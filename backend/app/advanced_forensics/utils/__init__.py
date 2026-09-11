"""Shared utilities for advanced forensic processors."""
import hashlib
import logging
import math
import os
import struct
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

MAGIC_BYTES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
    b"GIF87a": "image/gif",
    b"GIF89a": "image/gif",
    b"%PDF": "application/pdf",
    b"PK\x03\x04": "application/zip",
    b"PK\x05\x06": "application/zip",
    b"\x1f\x8b": "application/gzip",
    b"Rar!\x1a\x07": "application/x-rar",
    b"7z\xbc\xaf\x27\x1c": "application/x-7z-compressed",
    b"MZ": "application/x-dosexec",
    b"\x7fELF": "application/x-elf",
    b"BM": "image/bmp",
    b"RIFF": "audio/x-wav",
    b"\x00\x00\x01\x00": "image/x-icon",
    b"\x00\x00\x02\x00": "image/x-icon",
    b"ID3": "audio/mpeg",
    b"\xff\xfb": "audio/mpeg",
    b"\xff\xf3": "audio/mpeg",
    b"\xff\xf2": "audio/mpeg",
    b"\x00\x00\x00\x18ftypmp4": "video/mp4",
    b"\x00\x00\x00\x1cftyp": "video/mp4",
    b"\x00\x00\x00\x20ftyp": "video/mp4",
    b"\x00\x00\x00\x14ftypqt": "video/quicktime",
    b"OggS": "audio/ogg",
    b"fLaC": "audio/flac",
    b"\x04\x22\x4d\x18": "application/octet-stream",
    b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1": "application/ms-office",
    b"SQLite format 3": "application/x-sqlite3",
    b"\xef\xbb\xbf": "text/plain",
    b"\xff\xfe": "text/plain",
    b"\xfe\xff": "text/plain",
}

FILE_EXTENSION_MIME = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".gif": "image/gif", ".bmp": "image/bmp", ".tiff": "image/tiff",
    ".tif": "image/tiff", ".webp": "image/webp", ".svg": "image/svg+xml",
    ".pdf": "application/pdf", ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".zip": "application/zip", ".rar": "application/x-rar",
    ".7z": "application/x-7z-compressed", ".tar": "application/x-tar",
    ".gz": "application/gzip", ".bz2": "application/x-bzip2",
    ".exe": "application/x-dosexec", ".dll": "application/x-dosexec",
    ".sys": "application/x-dosexec", ".msi": "application/x-msi",
    ".eml": "message/rfc822", ".msg": "application/vnd.ms-outlook",
    ".mp3": "audio/mpeg", ".wav": "audio/wav", ".ogg": "audio/ogg",
    ".flac": "audio/flac", ".aac": "audio/aac",
    ".mp4": "video/mp4", ".avi": "video/x-msvideo", ".mkv": "video/x-matroska",
    ".mov": "video/quicktime", ".wmv": "video/x-ms-wmv",
    ".iso": "application/x-iso9660-image", ".img": "application/octet-stream",
    ".dd": "application/octet-stream", ".raw": "application/octet-stream",
    ".e01": "application/x-ewf", ".vmdk": "application/x-vmdk",
    ".vhd": "application/x-vhd", ".qcow2": "application/x-qcow2",
    ".pcap": "application/vnd.tcpdump.pcap",
    ".pcapng": "application/vnd.tcpdump.pcap",
    ".evtx": "application/x-evtx", ".pf": "application/x-prefetch",
    ".lnk": "application/x-ms-shortcut",
    ".sqlite": "application/x-sqlite3", ".db": "application/x-sqlite3",
    ".plist": "application/x-plist",
}


def compute_hashes(file_path: str, algorithms: tuple = ("sha256", "sha1", "md5")) -> Dict[str, str]:
    hashes = {alg: hashlib.new(alg) for alg in algorithms}
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            for h in hashes.values():
                h.update(chunk)
    return {alg: h.hexdigest() for alg, h in hashes.items()}


def read_file_header(file_path: str, num_bytes: int = 32) -> bytes:
    try:
        with open(file_path, "rb") as f:
            return f.read(num_bytes)
    except Exception:
        return b""


def detect_mime_by_magic(file_path: str) -> Optional[str]:
    header = read_file_header(file_path, 32)
    if not header:
        return None
    for magic, mime in MAGIC_BYTES.items():
        if header[:len(magic)] == magic:
            return mime
    return None


def detect_mime_by_extension(filename: str) -> Optional[str]:
    _, ext = os.path.splitext(filename.lower())
    return FILE_EXTENSION_MIME.get(ext)


def calculate_shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    freq = [0] * 256
    for byte in data:
        freq[byte] += 1
    length = len(data)
    entropy = 0.0
    for count in freq:
        if count > 0:
            p = count / length
            entropy -= p * math.log2(p)
    return entropy


def extract_strings(data: bytes, min_length: int = 4, encoding: str = "ascii") -> List[str]:
    strings = []
    current = []
    for byte in data:
        if 32 <= byte <= 126:
            current.append(chr(byte))
        else:
            if len(current) >= min_length:
                strings.append("".join(current))
            current = []
    if len(current) >= min_length:
        strings.append("".join(current))
    return strings


def extract_unicode_strings(data: bytes, min_length: int = 4) -> List[str]:
    strings = []
    i = 0
    while i < len(data) - 1:
        if data[i] != 0 and data[i + 1] == 0 and 32 <= data[i] <= 126:
            start = i
            while i < len(data) - 1 and data[i] != 0 and data[i + 1] == 0 and 32 <= data[i] <= 126:
                i += 2
            s = data[start:i:2].decode("ascii", errors="ignore")
            if len(s) >= min_length:
                strings.append(s)
        else:
            i += 1
    return strings


def check_file_signature(file_path: str, expected_type: str) -> bool:
    detected = detect_mime_by_magic(file_path)
    if detected is None:
        return True
    type_groups = {
        "image": ["image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff", "image/webp", "image/svg+xml", "image/x-icon"],
        "pdf": ["application/pdf"],
        "zip": ["application/zip"],
        "office": ["application/ms-office", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.openxmlformats-officedocument.presentationml.presentation", "application/msword", "application/vnd.ms-excel", "application/vnd.ms-powerpoint"],
        "executable": ["application/x-dosexec", "application/x-elf"],
        "email": ["message/rfc822", "application/vnd.ms-outlook"],
        "archive": ["application/zip", "application/x-rar", "application/x-7z-compressed", "application/x-tar", "application/gzip", "application/x-bzip2"],
        "database": ["application/x-sqlite3"],
    }
    expected_group = type_groups.get(expected_type, [expected_type])
    return detected in expected_group
