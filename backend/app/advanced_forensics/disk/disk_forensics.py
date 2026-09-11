import logging
import os
import struct
import subprocess
from datetime import datetime, timedelta
from typing import Any, Dict, FrozenSet, List, Optional, Set

from ...forensic_engine.base import BaseProcessor
from ...forensic_engine.schemas import (
    EvidenceSchema,
    EvidenceCategory,
    ForensicProcessorConfig,
    ProcessorPriority,
)

logger = logging.getLogger(__name__)

_MAGIC_SIGNATURES = {
    b"\xff\xd8\xff": "JPEG",
    b"%PDF": "PDF",
    b"\x50\x4b\x03\x04": "ZIP",
    b"\x89PNG\r\n\x1a\n": "PNG",
    b"GIF87a": "GIF",
    b"GIF89a": "GIF",
    b"Rar!\x1a\x07": "RAR",
    b"\x1f\x8b": "GZIP",
    b"PK\x03\x04": "ZIP",
    b"\x00\x00\x01\x00": "ICO",
    b"\x42\x4d": "BMP",
}

_FOOTER_SIGNATURES = {
    "JPEG": b"\xff\xd9",
    "PNG": b"IEND\xaeB`\x82",
    "GIF": b"\x00\x3b",
    "ZIP": b"PK\x05\x06",
    "PDF": b"%%EOF",
}


class DiskForensicsProcessor(BaseProcessor):
    """Deep disk image analysis with TSK integration and raw parsing fallbacks."""

    name = "disk_forensics"
    description = (
        "Deep disk image analysis: TSK integration, deleted file recovery, "
        "filesystem analysis, partition analysis, recovered artifacts"
    )
    supported_categories: FrozenSet[EvidenceCategory] = frozenset(
        {EvidenceCategory.DISK_IMAGE, EvidenceCategory.FORENSIC_DISK_IMAGE, EvidenceCategory.UNKNOWN}
    )
    priority = ProcessorPriority.DEEP_ANALYSIS

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        try:
            self._analyze_partitions(evidence)
            self._extract_file_system_info(evidence)
            self._list_filesystem(evidence)
            self._recover_deleted_files(evidence)
            self._build_file_timeline(evidence)
            self._carve_files(evidence)
            self._analyze_unallocated(evidence)
            evidence.add_tag("disk_forensics")
        except Exception as exc:
            evidence.add_error(self.name, f"Disk analysis failed: {exc}")
            logger.exception("DiskForensicsProcessor failed on %s", evidence.filename)
        return evidence

    # ------------------------------------------------------------------
    # Partition analysis
    # ------------------------------------------------------------------

    def _analyze_partitions(self, evidence: EvidenceSchema) -> None:
        partitions: List[Dict[str, Any]] = []

        # Attempt Sleuth Kit mmls first
        try:
            result = subprocess.run(
                ["mmls", evidence.storage_path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0 and result.stdout.strip():
                partitions = self._parse_mmls_output(result.stdout)
                evidence.metadata["partition_table_source"] = "mmls"
        except FileNotFoundError:
            logger.debug("mmls not available, falling back to raw header parsing")
        except subprocess.TimeoutExpired:
            evidence.add_error(self.name, "mmls timed out")
        except Exception as exc:
            evidence.add_error(self.name, f"mmls failed: {exc}")

        # Fallback: parse MBR / GPT headers manually
        if not partitions:
            partitions = self._parse_partition_headers(evidence)

        evidence.metadata["partitions"] = partitions
        for part in partitions:
            evidence.add_entity(
                name=part.get("name", f"Partition {part.get('index', '?')}"),
                entity_type="partition",
                properties=part,
            )
            evidence.add_tag("partition")

    def _parse_mmls_output(self, output: str) -> List[Dict[str, Any]]:
        partitions: List[Dict[str, Any]] = []
        for line in output.strip().splitlines():
            line = line.strip()
            if not line or line.startswith("Slot") or line.startswith("---"):
                continue
            parts = line.split()
            if len(parts) >= 6:
                partitions.append({
                    "index": parts[0],
                    "type": parts[1],
                    "start": parts[2],
                    "length": parts[3],
                    "size_sectors": parts[4],
                    "description": " ".join(parts[5:]),
                    "source": "mmls",
                })
        return partitions

    def _parse_partition_headers(self, evidence: EvidenceSchema) -> List[Dict[str, Any]]:
        partitions: List[Dict[str, Any]] = []
        try:
            with open(evidence.storage_path, "rb") as fh:
                # MBR at sector 0 (offset 446, 4 entries × 16 bytes)
                fh.seek(0)
                mbr = fh.read(512)
                if len(mbr) < 512:
                    return partitions

                if mbr[510:512] != b"\x55\xaa":
                    # Not a valid MBR; check for GPT at LBA 1
                    fh.seek(512)
                    gpt_header = fh.read(512)
                    if len(gpt_header) >= 512 and gpt_header[:8] == b"EFI PART":
                        partitions = self._parse_gpt(fh, gpt_header)
                        evidence.metadata["partition_table_source"] = "gpt_raw"
                    return partitions

                evidence.metadata["partition_table_source"] = "mbr_raw"
                for idx in range(4):
                    entry_offset = 446 + idx * 16
                    entry = mbr[entry_offset : entry_offset + 16]
                    ptype = entry[4]
                    if ptype == 0x00:
                        continue
                    lba_start = struct.unpack_from("<I", entry, 8)[0]
                    lba_count = struct.unpack_from("<I", entry, 12)[0]
                    partitions.append({
                        "index": idx,
                        "type": f"0x{ptype:02x}",
                        "lba_start": lba_start,
                        "lba_count": lba_count,
                        "active": bool(entry[0] & 0x80),
                        "source": "mbr_raw",
                    })
        except Exception as exc:
            evidence.add_error(self.name, f"Raw partition parsing failed: {exc}")
        return partitions

    def _parse_gpt(self, fh: Any, header: bytes) -> List[Dict[str, Any]]:
        partitions: List[Dict[str, Any]] = []
        try:
            part_entry_lba = struct.unpack_from("<Q", header, 72)[0]
            part_entry_count = struct.unpack_from("<I", header, 80)[0]
            part_entry_size = struct.unpack_from("<I", header, 84)[0]
            fh.seek(part_entry_lba * 512)
            for idx in range(part_entry_count):
                entry = fh.read(part_entry_size)
                if len(entry) < part_entry_size:
                    break
                type_guid = entry[:16]
                if type_guid == b"\x00" * 16:
                    continue
                unique_guid = entry[16:32]
                lba_start = struct.unpack_from("<Q", entry, 32)[0]
                lba_end = struct.unpack_from("<Q", entry, 40)[0]
                name_bytes = entry[56:128]
                try:
                    name = name_bytes.decode("utf-16-le").rstrip("\x00")
                except Exception:
                    name = f"GPT_Partition_{idx}"
                partitions.append({
                    "index": idx,
                    "name": name,
                    "lba_start": lba_start,
                    "lba_end": lba_end,
                    "source": "gpt_raw",
                })
        except Exception:
            pass
        return partitions

    # ------------------------------------------------------------------
    # Filesystem metadata
    # ------------------------------------------------------------------

    def _extract_file_system_info(self, evidence: EvidenceSchema) -> None:
        fs_info: Dict[str, Any] = {}
        try:
            result = subprocess.run(
                ["fstyp", evidence.storage_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                fs_info["fstyp_output"] = result.stdout.strip()
        except FileNotFoundError:
            pass
        except Exception as exc:
            evidence.add_error(self.name, f"fstyp failed: {exc}")

        # Try fls for inode info
        try:
            result = subprocess.run(
                ["fls", "-m", "/", evidence.storage_path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
                fs_info["file_count"] = len(lines)
                evidence.add_timeline_event(
                    datetime.utcnow().isoformat(),
                    f"Filesystem contains {len(lines)} entries",
                    self.name,
                )
        except FileNotFoundError:
            pass
        except Exception as exc:
            evidence.add_error(self.name, f"fls metadata failed: {exc}")

        # Manual FAT / NTFS / ext detection from boot sector
        try:
            with open(evidence.storage_path, "rb") as fh:
                boot = fh.read(512)
                if len(boot) >= 512:
                    fs_type = self._detect_filesystem_type(boot)
                    if fs_type:
                        fs_info["detected_type"] = fs_type
        except Exception:
            pass

        evidence.metadata["filesystem_info"] = fs_info

    def _detect_filesystem_type(self, boot_sector: bytes) -> Optional[str]:
        oem_id = boot_sector[3:11].decode("ascii", errors="ignore").strip()
        if boot_sector[0:3] in (b"\xeb\x3c\x90", b"\xe9"):
            if oem_id.upper().startswith("MSWIN") or oem_id.upper().startswith("NTFS"):
                return "NTFS"
            return "FAT"
        if boot_sector[0x38:0x40] == b"EXT2    " or boot_sector[0x438:0x438 + 2] == b"\x53\xef":
            return "ext2/ext3/ext4"
        if boot_sector[510:512] == b"\x55\xaa":
            return "FAT/Unknown"
        return None

    # ------------------------------------------------------------------
    # Filesystem listing
    # ------------------------------------------------------------------

    def _list_filesystem(self, evidence: EvidenceSchema) -> None:
        try:
            result = subprocess.run(
                ["fls", "-r", "-d", evidence.storage_path],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
                evidence.metadata["filesystem_entries"] = len(lines)
                evidence.metadata["deleted_entries"] = sum(
                    1 for l in lines if "(deleted)" in l.lower()
                )
                # Store first 1000 entries as extracted text sample (only if no text yet)
                if not evidence.extracted_text:
                    evidence.extracted_text = "\n".join(lines[:1000])
        except FileNotFoundError:
            logger.debug("fls not available")
        except Exception as exc:
            evidence.add_error(self.name, f"Filesystem listing failed: {exc}")

    # ------------------------------------------------------------------
    # Deleted file recovery
    # ------------------------------------------------------------------

    def _recover_deleted_files(self, evidence: EvidenceSchema) -> None:
        recovered: List[Dict[str, Any]] = []
        try:
            result = subprocess.run(
                ["fls", "-r", "-d", "-p", evidence.storage_path],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                return

            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if not line or "(deleted)" not in line.lower():
                    continue
                inode_part = line.split("*")[0].strip() if "*" in line else ""
                inode = inode_part.lstrip("d/d ")
                if not inode:
                    continue

                # Attempt to recover via icat
                file_data = self._icat_file(evidence, inode)
                if file_data:
                    recovered.append({
                        "inode": inode,
                        "path_hint": line,
                        "size_bytes": len(file_data),
                    })

        except FileNotFoundError:
            logger.debug("fls/icat not available for recovery")
        except Exception as exc:
            evidence.add_error(self.name, f"Deleted file recovery failed: {exc}")

        evidence.metadata["recovered_deleted_files"] = recovered
        if recovered:
            evidence.add_tag("deleted_files_found")
            evidence.add_timeline_event(
                datetime.utcnow().isoformat(),
                f"Recovered {len(recovered)} deleted file(s)",
                self.name,
            )

    def _icat_file(self, evidence: EvidenceSchema, inode: str) -> Optional[bytes]:
        try:
            result = subprocess.run(
                ["icat", evidence.storage_path, inode],
                capture_output=True,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    # File timeline from MACB timestamps
    # ------------------------------------------------------------------

    def _build_file_timeline(self, evidence: EvidenceSchema) -> None:
        try:
            result = subprocess.run(
                ["fls", "-r", "-m", "/", evidence.storage_path],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                return

            events_added = 0
            for line in result.stdout.strip().splitlines():
                if "|" not in line:
                    continue
                meta_part, name_part = line.split("|", 1)
                segments = meta_part.split(",")
                if len(segments) < 5:
                    continue

                name = name_part.strip() if name_part else ""
                # Try to extract timestamps from fields
                # Typical fls -m output: type|inode,uid,gid,size,mode,atime,mtime,ctime,crtime
                fields = meta_part.split(",")
                if len(fields) >= 9:
                    try:
                        for ts_field in fields[5:9]:
                            ts_val = int(ts_field)
                            if 946684800 < ts_val < 2524608000:  # 2000-2050 range
                                ts = datetime.utcfromtimestamp(ts_val).isoformat()
                                evidence.add_timeline_event(
                                    ts,
                                    f"File timestamp: {name}",
                                    self.name,
                                )
                                events_added += 1
                                if events_added >= 200:
                                    break
                    except (ValueError, OSError):
                        continue
                if events_added >= 200:
                    break
        except FileNotFoundError:
            pass
        except Exception as exc:
            evidence.add_error(self.name, f"Timeline building failed: {exc}")

    # ------------------------------------------------------------------
    # File carving by magic bytes
    # ------------------------------------------------------------------

    def _carve_files(self, evidence: EvidenceSchema) -> None:
        carved: List[Dict[str, Any]] = []
        chunk_size = 1024 * 1024  # 1 MB
        overlap = 8  # bytes to keep for header detection
        offset = 0

        try:
            file_size = os.path.getsize(evidence.storage_path)
            with open(evidence.storage_path, "rb") as fh:
                prev_tail = b""
                while offset < file_size:
                    chunk = fh.read(chunk_size)
                    if not chunk:
                        break
                    data = prev_tail + chunk
                    local_offset = offset - len(prev_tail)

                    for magic_bytes, fmt_name in _MAGIC_SIGNATURES.items():
                        search_start = 0
                        while True:
                            pos = data.find(magic_bytes, search_start)
                            if pos == -1:
                                break
                            abs_offset = local_offset + pos
                            footer = _FOOTER_SIGNATURES.get(fmt_name)
                            end_offset = file_size  # default to EOF
                            if footer:
                                footer_pos = data.find(footer, pos + len(magic_bytes))
                                if footer_pos != -1:
                                    end_offset = local_offset + footer_pos + len(footer)
                            carved.append({
                                "format": fmt_name,
                                "offset": abs_offset,
                                "size_estimate": end_offset - abs_offset,
                            })
                            evidence.add_tag(f"carved_{fmt_name.lower()}")
                            search_start = pos + 1
                            if len(carved) >= 500:
                                break
                        if len(carved) >= 500:
                            break

                    prev_tail = chunk[-overlap:] if len(chunk) >= overlap else chunk
                    offset += len(chunk)
        except Exception as exc:
            evidence.add_error(self.name, f"File carving failed: {exc}")

        evidence.metadata["carved_files"] = carved
        if carved:
            evidence.add_timeline_event(
                datetime.utcnow().isoformat(),
                f"Carved {len(carved)} file signature(s) from raw disk",
                self.name,
            )

    # ------------------------------------------------------------------
    # Unallocated space analysis
    # ------------------------------------------------------------------

    def _analyze_unallocated(self, evidence: EvidenceSchema) -> None:
        results: Dict[str, Any] = {}
        ascii_strings: List[str] = []
        unicode_strings: List[str] = []
        signature_hits: List[Dict[str, Any]] = []

        min_string_len = 6
        chunk_size = 1024 * 1024

        try:
            file_size = os.path.getsize(evidence.storage_path)
            with open(evidence.storage_path, "rb") as fh:
                offset = 0
                while offset < file_size:
                    chunk = fh.read(chunk_size)
                    if not chunk:
                        break

                    # ASCII strings
                    for match in self._extract_ascii_strings(chunk, min_string_len):
                        ascii_strings.append(match)
                        if len(ascii_strings) >= 5000:
                            break

                    # Unicode (UTF-16LE) strings
                    for match in self._extract_unicode_strings(chunk, min_string_len):
                        unicode_strings.append(match)
                        if len(unicode_strings) >= 5000:
                            break

                    # Magic byte scanning
                    for magic_bytes, fmt_name in _MAGIC_SIGNATURES.items():
                        pos = 0
                        while True:
                            pos = chunk.find(magic_bytes, pos)
                            if pos == -1:
                                break
                            signature_hits.append({
                                "format": fmt_name,
                                "offset": offset + pos,
                            })
                            pos += 1
                            if len(signature_hits) >= 1000:
                                break

                    offset += len(chunk)
                    if len(ascii_strings) >= 5000:
                        break
        except Exception as exc:
            evidence.add_error(self.name, f"Unallocated space analysis failed: {exc}")

        results["ascii_strings_count"] = len(ascii_strings)
        results["unicode_strings_count"] = len(unicode_strings)
        results["signature_hits_count"] = len(signature_hits)
        results["ascii_strings_sample"] = ascii_strings[:200]
        results["unicode_strings_sample"] = unicode_strings[:200]
        results["signature_hits_sample"] = signature_hits[:100]

        evidence.metadata["unallocated_analysis"] = results
        if signature_hits:
            evidence.add_tag("unallocated_signatures_found")

    # ------------------------------------------------------------------
    # String extraction helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_ascii_strings(data: bytes, min_len: int = 6) -> List[str]:
        strings: List[str] = []
        current: List[bytes] = []
        for byte in data:
            if 32 <= byte <= 126:
                current.append(bytes([byte]))
            else:
                if len(current) >= min_len:
                    strings.append(b"".join(current).decode("ascii", errors="ignore"))
                current = []
        if len(current) >= min_len:
            strings.append(b"".join(current).decode("ascii", errors="ignore"))
        return strings

    @staticmethod
    def _extract_unicode_strings(data: bytes, min_len: int = 6) -> List[str]:
        strings: List[str] = []
        if len(data) < 2:
            return strings
        current: List[str] = []
        for i in range(0, len(data) - 1, 2):
            code = struct.unpack_from("<H", data, i)[0]
            if 32 <= code <= 126 and code != 0:
                current.append(chr(code))
            else:
                if len(current) >= min_len:
                    strings.append("".join(current))
                current = []
        if len(current) >= min_len:
            strings.append("".join(current))
        return strings
