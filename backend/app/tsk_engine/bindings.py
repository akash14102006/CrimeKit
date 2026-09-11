"""Native pytsk3 bindings wrapper — low-level TSK library access for CrimeKit.

Provides a clean Pythonic interface over pytsk3's C library, handling:
- Image format detection and opening (RAW, EWF, AFF, VMDK, VHD)
- Volume system / partition discovery
- Filesystem detection and opening
- Directory traversal and file enumeration
- Metadata extraction (timestamps, allocation state, file types)
- File content reading with streaming/bounded reads
- Deleted/orphan file detection
"""

from __future__ import annotations

import io
import logging
import os
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Callable, Dict, Iterator, List, Optional, Tuple

from .schemas import (
    AllocationState,
    FilesystemType,
    ImageFormat,
    ObjectType,
    TSKFilesystemInfo,
    TSKFileInfo,
    TSKImageInfo,
    TSKPartitionInfo,
    TSKVolumeInfo,
)

logger = logging.getLogger(__name__)

try:
    import pytsk3

    _HAS_PYTSK3 = True
except ImportError:
    _HAS_PYTSK3 = False
    logger.warning("pytsk3 not installed — TSK native bindings unavailable")

try:
    import libewf

    _HAS_LIBEWF = True
except ImportError:
    _HAS_LIBEWF = False

try:
    import pyewf

    _HAS_PYEWF = True
except ImportError:
    _HAS_PYEWF = False

# Cached result of the functional native-EWF probe (None = not probed yet).
_NATIVE_EWF_WORKS: Optional[bool] = None


def _native_ewf_open_works() -> bool:
    """Functional probe: can this pytsk3 build actually open EWF containers?

    Constant presence (TSK_IMG_TYPE_EWF_EWF) does NOT imply runtime libewf
    linkage — a bundled-libtsk wheel may lack it. Probing an explicit EWF
    open distinguishes "unsupported image type" (no libewf) from a normal
    missing-file error (libewf present).
    """
    global _NATIVE_EWF_WORKS
    if _NATIVE_EWF_WORKS is not None:
        return _NATIVE_EWF_WORKS
    works = False
    if _HAS_PYTSK3 and hasattr(pytsk3, "TSK_IMG_TYPE_EWF_EWF"):
        try:
            pytsk3.Img_Info("/definitely/not/here/no-such.E01", pytsk3.TSK_IMG_TYPE_EWF_EWF)
            works = True
        except Exception as exc:
            works = "Unsupported image type" not in str(exc)
    _NATIVE_EWF_WORKS = works
    return works

_PYTSK3_FS_TYPE_MAP: Dict[int, FilesystemType] = {}
_PYTSK3_IMG_TYPE_MAP: Dict[int, ImageFormat] = {}
_PYTSK3_META_TYPE_MAP: Dict[int, ObjectType] = {}

if _HAS_PYTSK3:
    _PYTSK3_FS_TYPE_MAP = {
        pytsk3.TSK_FS_TYPE_NTFS: FilesystemType.NTFS,
        pytsk3.TSK_FS_TYPE_FAT12: FilesystemType.FAT12,
        pytsk3.TSK_FS_TYPE_FAT16: FilesystemType.FAT16,
        pytsk3.TSK_FS_TYPE_FAT32: FilesystemType.FAT32,
        pytsk3.TSK_FS_TYPE_EXFAT: FilesystemType.EXFAT,
        pytsk3.TSK_FS_TYPE_EXT2: FilesystemType.EXT2,
        pytsk3.TSK_FS_TYPE_EXT3: FilesystemType.EXT3,
        pytsk3.TSK_FS_TYPE_EXT4: FilesystemType.EXT4,
        pytsk3.TSK_FS_TYPE_HFS: FilesystemType.HFS,
        pytsk3.TSK_FS_TYPE_APFS: FilesystemType.APFS,
        pytsk3.TSK_FS_TYPE_ISO9660: FilesystemType.ISO9660,
        pytsk3.TSK_FS_TYPE_FFS1: FilesystemType.UFS,
        pytsk3.TSK_FS_TYPE_FFS2: FilesystemType.UFS,
        pytsk3.TSK_FS_TYPE_YAFFS2: FilesystemType.YAFFS2,
        pytsk3.TSK_FS_TYPE_RAW: FilesystemType.RAW,
        pytsk3.TSK_FS_TYPE_SWAP: FilesystemType.SWAP,
    }
    _PYTSK3_IMG_TYPE_MAP = {
        pytsk3.TSK_IMG_TYPE_RAW_SING: ImageFormat.RAW,
        pytsk3.TSK_IMG_TYPE_RAW_SPLIT: ImageFormat.RAW_SPLIT,
        pytsk3.TSK_IMG_TYPE_EWF_EWF: ImageFormat.EWF_E01,
        pytsk3.TSK_IMG_TYPE_AFF_ANY: ImageFormat.AFF,
        pytsk3.TSK_IMG_TYPE_VMDK_VMDK: ImageFormat.VMDK,
        pytsk3.TSK_IMG_TYPE_VHD_VHD: ImageFormat.VHD,
    }
    _PYTSK3_META_TYPE_MAP = {
        pytsk3.TSK_FS_META_TYPE_REG: ObjectType.FILE,
        pytsk3.TSK_FS_META_TYPE_DIR: ObjectType.DIRECTORY,
        pytsk3.TSK_FS_META_TYPE_LNK: ObjectType.LINK,
        pytsk3.TSK_FS_META_TYPE_BLK: ObjectType.BLOCK,
        pytsk3.TSK_FS_META_TYPE_CHR: ObjectType.CHARACTER,
        pytsk3.TSK_FS_META_TYPE_FIFO: ObjectType.FIFO,
        pytsk3.TSK_FS_META_TYPE_SOCK: ObjectType.SOCKET,
    }


def _tsk_timestamp_to_datetime(ts: int) -> Optional[datetime]:
    """Convert a TSK Unix timestamp to a UTC datetime."""
    if ts <= 0:
        return None
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    except (OSError, ValueError, OverflowError):
        return None


def _classify_allocation(meta_flags: int, name_flags: int) -> AllocationState:
    """Determine allocation state from TSK meta/name flags."""
    if _HAS_PYTSK3:
        if meta_flags & pytsk3.TSK_FS_META_FLAG_ORPHAN:
            return AllocationState.ORPHAN
        if meta_flags & pytsk3.TSK_FS_META_FLAG_UNALLOC:
            return AllocationState.UNALLOCATED
        if meta_flags & pytsk3.TSK_FS_META_FLAG_ALLOC:
            return AllocationState.ALLOCATED
        if name_flags & pytsk3.TSK_FS_NAME_FLAG_UNALLOC:
            return AllocationState.UNALLOCATED
        if name_flags & pytsk3.TSK_FS_NAME_FLAG_ALLOC:
            return AllocationState.ALLOCATED
    return AllocationState.UNKNOWN


class TSKBindings:
    """High-level wrapper around pytsk3 for disk image forensic analysis.

    Provides methods for image opening, partition/volume discovery,
    filesystem traversal, metadata extraction, and content reading.
    All methods are designed to be called from the processing pipeline
    with proper error handling and resource cleanup.
    """

    def __init__(self) -> None:
        self._img: Any = None
        self._img_path: Optional[str] = None
        self._vs: Any = None
        self._fs_list: List[Tuple[int, Any]] = []
        if not _HAS_PYTSK3:
            raise RuntimeError(
                "pytsk3 is required for TSK native bindings. "
                "Install with: pip install pytsk3"
            )

    def close(self) -> None:
        """Release all TSK resources."""
        self._fs_list.clear()
        self._vs = None
        self._img = None
        self._img_path = None

    def __enter__(self) -> "TSKBindings":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    @staticmethod
    def is_available() -> bool:
        return _HAS_PYTSK3

    @staticmethod
    def supported_image_formats() -> List[ImageFormat]:
        fmts = [ImageFormat.RAW, ImageFormat.RAW_SPLIT]
        if _HAS_PYTSK3:
            if hasattr(pytsk3, "TSK_IMG_TYPE_EWF_EWF"):
                fmts.append(ImageFormat.EWF_E01)
            if hasattr(pytsk3, "TSK_IMG_TYPE_AFF_ANY"):
                fmts.append(ImageFormat.AFF)
            if hasattr(pytsk3, "TSK_IMG_TYPE_VMDK_VMDK"):
                fmts.append(ImageFormat.VMDK)
            if hasattr(pytsk3, "TSK_IMG_TYPE_VHD_VHD"):
                fmts.append(ImageFormat.VHD)
        return fmts

    @staticmethod
    def ewf_capability() -> Dict[str, Any]:
        """Report whether this environment can open EWF/E01 containers."""
        if _native_ewf_open_works():
            return {
                "supported": True,
                "mode": "native",
                "reason": "TSK/libewf capability verified",
            }
        if _HAS_PYEWF:
            return {
                "supported": True,
                "mode": "pyewf-bridge",
                "reason": (
                    "E01/EWF analysis via pyewf raw-export bridge "
                    "(this pytsk3 build has no native libewf linkage)."
                ),
            }
        return {
            "supported": False,
            "mode": "unavailable",
            "reason": "E01/EWF analysis unavailable: libewf support is not installed.",
        }

    @staticmethod
    def detect_format(path: str) -> ImageFormat:
        if not os.path.isfile(path):
            return ImageFormat.UNKNOWN
        try:
            with open(path, "rb") as f:
                header = f.read(16)
            if header[:4] == b"\xdd\xcf\x11\xe0":
                return ImageFormat.VHD
            if header[:3] == b"VMDK" or header[:4] == b"KDMV":
                return ImageFormat.VMDK
            if header[:6] == b"Play" or header[:4] == b"\x47\x4b\x44\x4d":
                return ImageFormat.VMDK
            if header[:4] == b"EVF\x00" or header[:3] == b"EVF":
                return ImageFormat.EWF_E01
            if header[:4] == b"23456789":
                return ImageFormat.AFF
            if header[:8] == b"CAFEBOOBA":
                return ImageFormat.QCOW
        except (OSError, IOError):
            pass
        ext = Path(path).suffix.lower()
        ext_map = {
            ".raw": ImageFormat.RAW, ".dd": ImageFormat.RAW,
            ".img": ImageFormat.RAW, ".iso": ImageFormat.RAW,
            ".e01": ImageFormat.EWF_E01, ".ex01": ImageFormat.EWF_EX01,
            ".ewf": ImageFormat.EWF_E01,
            ".vmdk": ImageFormat.VMDK,
            ".vhd": ImageFormat.VHD, ".vhdx": ImageFormat.VHD,
            ".aff": ImageFormat.AFF, ".afd": ImageFormat.AFF, ".afm": ImageFormat.AFF,
            ".qcow2": ImageFormat.QCOW, ".qcow": ImageFormat.QCOW,
        }
        return ext_map.get(ext, ImageFormat.UNKNOWN)

    def open_image(self, path: str) -> TSKImageInfo:
        if self._img is not None:
            self.close()
        fmt = self.detect_format(path)
        file_size = 0
        try:
            file_size = os.path.getsize(path)
        except OSError:
            pass
        if fmt in (ImageFormat.EWF_E01, ImageFormat.EWF_EX01) and not _native_ewf_open_works():
            # This pytsk3 build cannot open EWF natively (DETECT would
            # silently fall back to RAW and scan compressed container bytes).
            # Never fall back silently: use the pyewf bridge or fail loudly.
            if not _HAS_PYEWF:
                logger.error("EWF image %s refused: no EWF reader available", path)
                return TSKImageInfo(
                    image_path=path,
                    image_format=fmt,
                    image_size=file_size,
                    error="E01/EWF analysis unavailable: libewf support is not installed.",
                )
            try:
                raw_path = self._export_ewf_to_raw(path)
            except Exception as exc:
                logger.error("EWF export failed for %s: %s", path, exc)
                return TSKImageInfo(
                    image_path=path,
                    image_format=fmt,
                    image_size=file_size,
                    error=f"E01/EWF export failed: {exc}",
                )
            try:
                self._img = pytsk3.Img_Info(raw_path, pytsk3.TSK_IMG_TYPE_RAW_SING)
                self._img_path = raw_path
                try:
                    raw_size = os.path.getsize(raw_path)
                except OSError:
                    raw_size = 0
                return TSKImageInfo(
                    image_path=path,
                    image_format=fmt,
                    image_size=raw_size,
                    sector_size=512,
                )
            except Exception as exc:
                logger.error("Failed to open exported image %s: %s", raw_path, exc)
                return TSKImageInfo(
                    image_path=path,
                    image_format=fmt,
                    image_size=file_size,
                    error=str(exc),
                )
        try:
            img_type = pytsk3.TSK_IMG_TYPE_DETECT
            self._img = pytsk3.Img_Info(path, img_type)
            self._img_path = path
            return TSKImageInfo(
                image_path=path,
                image_format=fmt,
                image_size=file_size,
                sector_size=512,
            )
        except Exception as exc:
            logger.error("Failed to open image %s: %s", path, exc)
            return TSKImageInfo(
                image_path=path,
                image_format=fmt,
                image_size=file_size,
                error=str(exc),
            )

    @staticmethod
    def _ewf_segment_paths(path: str) -> List[str]:
        """Resolve all EWF segment files (.E01, .E02, ...)."""
        directory = os.path.dirname(path) or "."
        base = os.path.basename(path)
        stem, _, ext = base.rpartition(".")
        segments: List[str] = []
        if stem and ext and len(ext) == 3 and ext[0].upper() == "E" and ext[1:].isdigit():
            prefix = stem.upper()
            try:
                for entry in sorted(os.listdir(directory)):
                    name_up = entry.upper()
                    if name_up.startswith(prefix + ".E") and name_up[-2:].isdigit():
                        segments.append(os.path.join(directory, entry))
            except OSError:
                pass
        if path not in segments:
            segments = [path] + [s for s in segments if s != path]
        return segments

    @staticmethod
    def _export_ewf_to_raw(path: str, chunk_size: int = 8 * 1024 * 1024) -> str:
        """Export an EWF container to a cached RAW image via pyewf.

        Never modifies the source evidence. Uses sparse file handling to
        minimize disk usage by skipping zero regions.
        """
        segments = TSKBindings._ewf_segment_paths(path)
        handle = pyewf.handle()
        try:
            handle.open(segments)
            try:
                media_size = int(handle.get_media_size())
            except Exception:
                media_size = 0
            if media_size <= 0:
                raise RuntimeError("pyewf reported an empty media size")
            cache_dir = os.path.join(os.path.dirname(path) or ".", ".tsk_raw_cache")
            os.makedirs(cache_dir, exist_ok=True)
            cache_path = os.path.join(cache_dir, os.path.basename(path) + ".raw")
            try:
                if os.path.getsize(cache_path) == media_size:
                    logger.info("Reusing cached RAW export %s (%d bytes)", cache_path, media_size)
                    return cache_path
            except OSError:
                pass
            exported = 0
            non_zero_count = 0
            zero_count = 0
            with open(cache_path, "wb") as output:
                while exported < media_size:
                    try:
                        handle.seek_offset(exported)
                    except Exception:
                        pass
                    data = handle.read_buffer(min(chunk_size, media_size - exported))
                    if not data:
                        break
                    is_non_zero = any(b != 0 for b in data[:4096])
                    if is_non_zero:
                        output.write(data)
                        non_zero_count += len(data)
                    else:
                        output.seek(len(data), 1)
                        zero_count += len(data)
                    exported += len(data)
            if exported != media_size:
                try:
                    os.remove(cache_path)
                except OSError:
                    pass
                raise RuntimeError(f"short export: {exported} of {media_size} bytes")
            logger.info(
                "Exported EWF %s to RAW %s (%d bytes, %d non-zero, %d sparse)",
                path, cache_path, exported, non_zero_count, zero_count,
            )
            return cache_path
        finally:
            try:
                handle.close()
            except Exception:
                pass

    def detect_volume_system(self) -> TSKVolumeInfo:
        if self._img is None:
            return TSKVolumeInfo(vs_type="none", error="No image opened")
        try:
            self._vs = pytsk3.Volume_Info(self._img, pytsk3.TSK_VS_TYPE_DETECT)
            partitions: List[TSKPartitionInfo] = []
            for part in self._vs:
                partitions.append(TSKPartitionInfo(
                    index=part.addr,
                    start_offset=part.start,
                    length=part.len,
                    description=str(part.desc) if hasattr(part, "desc") else "",
                    flags=str(part.flags) if hasattr(part, "flags") else "",
                    type_code=str(part.vstype) if hasattr(part, "vstype") else "",
                    source_image=self._img_path or "",
                ))
            vs_type_name = type(self._vs).__name__ if self._vs else "unknown"
            return TSKVolumeInfo(vs_type=vs_type_name, partitions=partitions)
        except Exception as exc:
            logger.warning("Volume system detection failed: %s", exc)
            return TSKVolumeInfo(vs_type="none", error=str(exc))

    def open_filesystem(self, partition: TSKPartitionInfo) -> TSKFilesystemInfo:
        if self._img is None:
            return TSKFilesystemInfo(
                fs_type=FilesystemType.UNKNOWN,
                offset=0, block_size=0,
                error="No image opened",
            )
        try:
            fs = pytsk3.FS_Info(self._img, offset=partition.start_offset)
            fs_type_raw = fs.info.ftype if hasattr(fs.info, "ftype") else 0
            fs_type = _PYTSK3_FS_TYPE_MAP.get(fs_type_raw, FilesystemType.UNKNOWN)
            info = TSKFilesystemInfo(
                fs_type=fs_type,
                offset=partition.start_offset,
                block_size=fs.info.block_size if hasattr(fs.info, "block_size") else 512,
                block_count=fs.info.block_count if hasattr(fs.info, "block_count") else 0,
                inode_count=fs.info.inum_count if hasattr(fs.info, "inum_count") else 0,
                root_inum=fs.info.root_addr if hasattr(fs.info, "root_addr") else 2,
                first_inum=fs.info.first_addr if hasattr(fs.info, "first_addr") else 0,
                last_inum=fs.info.last_addr if hasattr(fs.info, "last_addr") else 0,
                source_partition=partition.index,
            )
            self._fs_list.append((partition.index, fs))
            return info
        except Exception as exc:
            logger.warning(
                "Filesystem open failed at offset %d: %s",
                partition.start_offset, exc,
            )
            return TSKFilesystemInfo(
                fs_type=FilesystemType.UNKNOWN,
                offset=partition.start_offset,
                block_size=0,
                error=str(exc),
            )

    def _get_fs(self, partition_index: Optional[int] = None) -> Any:
        if not self._fs_list:
            raise RuntimeError("No filesystem opened")
        if partition_index is not None:
            for idx, fs in self._fs_list:
                if idx == partition_index:
                    return fs
            raise RuntimeError(f"Filesystem for partition {partition_index} not found")
        return self._fs_list[-1][1]

    def _build_path(self, fs: Any, name: Any, parent_path: str = "") -> str:
        name_str = ""
        try:
            name_str = name.name.decode("utf-8", errors="replace") if isinstance(name.name, bytes) else str(name.name)
        except Exception:
            name_str = str(name.name) if hasattr(name, "name") else ""
        if parent_path:
            return f"{parent_path}/{name_str}" if name_str else parent_path
        return f"/{name_str}" if name_str else "/"

    def _convert_meta(self, meta: Any, fs_type: FilesystemType) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        if meta is None:
            return result
        try:
            result["addr"] = meta.addr
            result["size"] = meta.size
            result["uid"] = meta.uid
            result["gid"] = meta.gid
            result["mode"] = meta.mode
            result["nlink"] = meta.nlink
            result["atime"] = meta.atime
            result["mtime"] = meta.mtime
            result["ctime"] = meta.ctime
            if hasattr(meta, "crtime"):
                result["crtime"] = meta.crtime
        except Exception:
            pass
        return result

    def enumerate_files(
        self,
        partition_index: Optional[int] = None,
        max_files: int = 100000,
        include_deleted: bool = True,
        callback: Optional[Callable[[TSKFileInfo], None]] = None,
    ) -> List[TSKFileInfo]:
        fs = self._get_fs(partition_index)
        files: List[TSKFileInfo] = []
        root_inum = fs.info.root_addr if hasattr(fs.info, "root_addr") else 2

        walk_flags = pytsk3.TSK_FS_DIR_WALK_FLAG_RECURSE
        if not include_deleted:
            walk_flags |= pytsk3.TSK_FS_DIR_WALK_FLAG_NOORPHAN

        def _walk_cb(name: Any) -> int:
            if len(files) >= max_files:
                return pytsk3.TSK_WALK_STOP
            try:
                meta = None
                if hasattr(name, "meta") and name.meta:
                    meta = name.meta
                fs_type_raw = fs.info.ftype if hasattr(fs.info, "ftype") else 0
                fs_type = _PYTSK3_FS_TYPE_MAP.get(fs_type_raw, FilesystemType.UNKNOWN)

                meta_flags = meta.flags if meta and hasattr(meta, "flags") else 0
                name_flags = name.flags if hasattr(name, "flags") else 0
                alloc_state = _classify_allocation(meta_flags, name_flags)

                meta_type = meta.type if meta and hasattr(meta, "type") else 0
                obj_type = _PYTSK3_META_TYPE_MAP.get(meta_type, ObjectType.UNKNOWN)

                atime = _tsk_timestamp_to_datetime(meta.atime) if meta and hasattr(meta, "atime") else None
                mtime = _tsk_timestamp_to_datetime(meta.mtime) if meta and hasattr(meta, "mtime") else None
                ctime = _tsk_timestamp_to_datetime(meta.ctime) if meta and hasattr(meta, "ctime") else None
                crtime = None
                if meta and hasattr(meta, "crtime"):
                    crtime = _tsk_timestamp_to_datetime(meta.crtime)

                name_str = ""
                try:
                    name_str = name.name.decode("utf-8", errors="replace") if isinstance(name.name, bytes) else str(name.name)
                except Exception:
                    name_str = str(getattr(name, "name", ""))

                path_str = self._build_path(fs, name)

                is_deleted = (alloc_state == AllocationState.UNALLOCATED) or (
                    name_flags & (pytsk3.TSK_FS_NAME_FLAG_UNALLOC if _HAS_PYTSK3 else 0)
                )

                content_accessible = True
                if meta and hasattr(meta, "type"):
                    if meta.type not in (pytsk3.TSK_FS_META_TYPE_REG, pytsk3.TSK_FS_META_TYPE_DIR):
                        content_accessible = False

                fi = TSKFileInfo(
                    name=name_str,
                    path=path_str,
                    metadata_addr=meta.addr if meta else 0,
                    object_type=obj_type,
                    allocation_state=alloc_state,
                    size=meta.size if meta else 0,
                    uid=meta.uid if meta else 0,
                    gid=meta.gid if meta else 0,
                    mode=meta.mode if meta else 0,
                    atime=atime,
                    mtime=mtime,
                    ctime=ctime,
                    crtime=crtime,
                    nlink=meta.nlink if meta else 0,
                    fs_type=fs_type,
                    partition_index=partition_index,
                    is_deleted=is_deleted,
                    content_accessible=content_accessible,
                )
                files.append(fi)
                if callback:
                    callback(fi)
            except Exception as exc:
                logger.debug("Error walking entry: %s", exc)
            return pytsk3.TSK_WALK_CONT

        try:
            fs.dir_walk(root_inum, walk_flags, _walk_cb)
        except Exception as exc:
            logger.error("Directory walk failed: %s", exc)

        return files

    def read_file_content(
        self,
        metadata_addr: int,
        max_bytes: int = 10 * 1024 * 1024,
        partition_index: Optional[int] = None,
    ) -> Optional[bytes]:
        fs = self._get_fs(partition_index)
        try:
            f = fs.open_meta(metadata_addr)
            data = b""
            remaining = max_bytes
            while remaining > 0:
                chunk_size = min(65536, remaining)
                buf = f.read_random(0, chunk_size)
                if not buf:
                    break
                data += bytes(buf)
                remaining -= len(buf)
            return data
        except Exception as exc:
            logger.debug("Content read failed for inum %d: %s", metadata_addr, exc)
            return None

    def get_filesystem_stats(self, partition_index: Optional[int] = None) -> Dict[str, Any]:
        fs = self._get_fs(partition_index)
        return {
            "block_size": fs.info.block_size if hasattr(fs.info, "block_size") else 0,
            "block_count": fs.info.block_count if hasattr(fs.info, "block_count") else 0,
            "inode_count": fs.info.inum_count if hasattr(fs.info, "inum_count") else 0,
            "first_inum": fs.info.first_addr if hasattr(fs.info, "first_addr") else 0,
            "last_inum": fs.info.last_addr if hasattr(fs.info, "last_addr") else 0,
            "root_inum": fs.info.root_addr if hasattr(fs.info, "root_addr") else 2,
        }
