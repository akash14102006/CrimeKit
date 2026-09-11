import hashlib
import os
from typing import Dict


def compute_hashes(file_path: str, algorithms: tuple = ("sha256", "sha1", "md5")) -> Dict[str, str]:
    """Compute cryptographic hashes for a file."""
    hashes = {alg: hashlib.new(alg) for alg in algorithms}
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            for h in hashes.values():
                h.update(chunk)
    return {alg: h.hexdigest() for alg, h in hashes.items()}


def verify_integrity(file_path: str, expected_sha256: str) -> bool:
    """Verify file integrity against expected SHA-256 hash."""
    hashes = compute_hashes(file_path, ("sha256",))
    return hashes["sha256"] == expected_sha256.lower()
