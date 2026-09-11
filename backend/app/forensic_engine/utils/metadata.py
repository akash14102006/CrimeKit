import mimetypes
import os
from pathlib import Path
from typing import Any, Dict, Optional

from ..schemas import EvidenceCategory

_MIME_CATEGORY_MAP = {
    "image/": EvidenceCategory.IMAGE,
    "video/": EvidenceCategory.VIDEO,
    "audio/": EvidenceCategory.VIDEO,
    "application/pdf": EvidenceCategory.PDF,
    "application/epub": EvidenceCategory.PDF,
    "application/msword": EvidenceCategory.OFFICE,
    "application/vnd.openxmlformats-officedocument": EvidenceCategory.OFFICE,
    "application/vnd.ms-": EvidenceCategory.OFFICE,
    "application/vnd.oasis.opendocument": EvidenceCategory.OFFICE,
    "application/zip": EvidenceCategory.ARCHIVE,
    "application/x-rar": EvidenceCategory.ARCHIVE,
    "application/x-7z": EvidenceCategory.ARCHIVE,
    "application/x-tar": EvidenceCategory.ARCHIVE,
    "application/gzip": EvidenceCategory.ARCHIVE,
    "message/rfc822": EvidenceCategory.EMAIL,
    "multipart/mixed": EvidenceCategory.EMAIL,
}

_EXTENSION_CATEGORY_MAP = {
    "jpg": EvidenceCategory.IMAGE, "jpeg": EvidenceCategory.IMAGE,
    "png": EvidenceCategory.IMAGE, "gif": EvidenceCategory.IMAGE,
    "bmp": EvidenceCategory.IMAGE, "tiff": EvidenceCategory.IMAGE,
    "tif": EvidenceCategory.IMAGE, "webp": EvidenceCategory.IMAGE,
    "heic": EvidenceCategory.IMAGE, "heif": EvidenceCategory.IMAGE,
    "svg": EvidenceCategory.IMAGE, "raw": EvidenceCategory.IMAGE,
    "cr2": EvidenceCategory.IMAGE, "nef": EvidenceCategory.IMAGE,
    "arw": EvidenceCategory.IMAGE, "dng": EvidenceCategory.IMAGE,
    "mp4": EvidenceCategory.VIDEO, "avi": EvidenceCategory.VIDEO,
    "mkv": EvidenceCategory.VIDEO, "mov": EvidenceCategory.VIDEO,
    "wmv": EvidenceCategory.VIDEO, "flv": EvidenceCategory.VIDEO,
    "webm": EvidenceCategory.VIDEO, "m4v": EvidenceCategory.VIDEO,
    "mp3": EvidenceCategory.VIDEO, "wav": EvidenceCategory.VIDEO,
    "ogg": EvidenceCategory.VIDEO, "flac": EvidenceCategory.VIDEO,
    "pdf": EvidenceCategory.PDF,
    "doc": EvidenceCategory.OFFICE, "docx": EvidenceCategory.OFFICE,
    "xls": EvidenceCategory.OFFICE, "xlsx": EvidenceCategory.OFFICE,
    "ppt": EvidenceCategory.OFFICE, "pptx": EvidenceCategory.OFFICE,
    "odt": EvidenceCategory.OFFICE, "ods": EvidenceCategory.OFFICE,
    "odp": EvidenceCategory.OFFICE, "rtf": EvidenceCategory.OFFICE,
    "eml": EvidenceCategory.EMAIL, "msg": EvidenceCategory.EMAIL,
    "mbox": EvidenceCategory.EMAIL,
    "zip": EvidenceCategory.ARCHIVE, "rar": EvidenceCategory.ARCHIVE,
    "7z": EvidenceCategory.ARCHIVE, "tar": EvidenceCategory.ARCHIVE,
    "gz": EvidenceCategory.ARCHIVE, "bz2": EvidenceCategory.ARCHIVE,
    "iso": EvidenceCategory.DISK_IMAGE, "img": EvidenceCategory.DISK_IMAGE,
    "dd": EvidenceCategory.DISK_IMAGE, "raw": EvidenceCategory.DISK_IMAGE,
    "e01": EvidenceCategory.DISK_IMAGE, "ex01": EvidenceCategory.DISK_IMAGE,
    "vmdk": EvidenceCategory.DISK_IMAGE, "vhd": EvidenceCategory.DISK_IMAGE,
    "aff": EvidenceCategory.DISK_IMAGE,
    "ab": EvidenceCategory.MOBILE_ARTIFACT, "tar.gz": EvidenceCategory.MOBILE_ARTIFACT,
    "plist": EvidenceCategory.MOBILE_ARTIFACT, "db": EvidenceCategory.MOBILE_ARTIFACT,
    "sqlite": EvidenceCategory.MOBILE_ARTIFACT, "mbdb": EvidenceCategory.MOBILE_ARTIFACT,
}

_FORENSIC_IMAGE_EXTENSIONS = frozenset({"e01", "ex01", "ewf", "raw", "dd", "img", "iso", "vmdk", "vhd", "vhdx", "aff", "afd", "afm", "qcow", "qcow2"})


def extract_file_metadata(file_path: str) -> Dict:
    """Extract basic file metadata."""
    stat = os.stat(file_path)
    mime_type = mimetypes.guess_type(file_path)[0]
    return {
        "size": stat.st_size,
        "created_at": stat.st_ctime,
        "modified_at": stat.st_mtime,
        "accessed_at": stat.st_atime,
        "mime_type": mime_type,
        "extension": file_path.rsplit(".", 1)[-1].lower() if "." in file_path else "",
    }


def classify_evidence(filename: str, mime_type: Optional[str] = None) -> EvidenceCategory:
    """Classify evidence by file extension and MIME type."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    cat = _EXTENSION_CATEGORY_MAP.get(ext)
    if cat:
        return cat
    if mime_type:
        for prefix, category in _MIME_CATEGORY_MAP.items():
            if mime_type.startswith(prefix) or mime_type == prefix:
                return category
    return EvidenceCategory.UNKNOWN


def classify_forensic_image(file_path: str, filename: str, mime_type: Optional[str] = None) -> Dict[str, Any]:
    """Classify disk images using filename, bytes, and the installed TSK bindings.

    The client MIME type is only a signal. EWF files remain forensic images when
    browsers report application/octet-stream, but support is true only when TSK
    can open EWF in this environment.
    """
    extension = Path(filename).suffix.lower().lstrip(".")
    if extension not in _FORENSIC_IMAGE_EXTENSIONS:
        return {"is_forensic_image": False}

    image_format = "unknown"
    signature = ""
    try:
        with open(file_path, "rb") as handle:
            header = handle.read(16)
        if header.startswith(b"EVF"):
            image_format = "E01/EWF"
            signature = "EWF signature"
    except OSError as exc:
        return {
            "is_forensic_image": True,
            "evidence_type": "forensic_disk_image",
            "image_format": "E01/EWF" if extension in {"e01", "ex01", "ewf"} else "unknown",
            "processor": "TSK",
            "capability": "unsupported",
            "reason": f"Unable to inspect uploaded bytes: {exc}",
        }

    if image_format == "unknown":
        image_format = {"e01": "E01/EWF", "ex01": "E01/EWF", "ewf": "E01/EWF"}.get(extension, extension.upper())

    try:
        from ...tsk_engine.bindings import TSKBindings
        tsk_available = TSKBindings.is_available()
        supported_formats = TSKBindings.supported_image_formats()
        ewf_supported = any(fmt.value == "ewf_e01" for fmt in supported_formats)
    except Exception:
        tsk_available = False
        ewf_supported = False

    is_ewf = image_format == "E01/EWF"
    capability = "supported" if tsk_available and (not is_ewf or ewf_supported) else "unsupported"
    reason = "TSK/libewf capability verified" if capability == "supported" else (
        "E01/EWF analysis unavailable: libewf support is not installed."
        if is_ewf else "TSK native bindings are not installed."
    )
    return {
        "is_forensic_image": True,
        "evidence_type": "forensic_disk_image",
        "image_format": image_format,
        "processor": "TSK",
        "capability": capability,
        "reason": reason,
        "detected_by": ["filename_extension", "detected_signature" if signature else "filename_extension", "tsk_capability"],
        "mime_type_signal": mime_type or "application/octet-stream",
    }
