"""API key authentication for machine-to-machine communication.

Provides secure API key generation, hashing, validation, and rotation.
"""
import hashlib
import hmac
import logging
import os
import secrets
import time
from typing import Optional

logger = logging.getLogger(__name__)

# API key format: ck_live_<40 random chars> or ck_test_<40 random chars>
_KEY_PREFIX = "ck_"
_KEY_LENGTH = 40


def generate_api_key(environment: str = "live") -> tuple[str, str]:
    """Generate a new API key and its SHA-256 hash.

    Returns:
        (raw_key, hashed_key)
    """
    random_part = secrets.token_hex(_KEY_LENGTH // 2)
    raw_key = f"{_KEY_PREFIX}{environment}_{random_part}"
    hashed = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, hashed


def hash_api_key(raw_key: str) -> str:
    """Hash an API key using SHA-256."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


def validate_api_key(raw_key: str, stored_hash: str) -> bool:
    """Validate an API key against its stored hash using constant-time comparison."""
    computed_hash = hash_api_key(raw_key)
    return hmac.compare_digest(computed_hash, stored_hash)


def get_key_prefix(raw_key: str) -> str:
    """Extract the prefix from an API key (ck_live or ck_test)."""
    parts = raw_key.split("_")
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}"
    return raw_key[:10]


def is_valid_format(key: str) -> bool:
    """Check if a key matches the expected format."""
    if not key.startswith(_KEY_PREFIX):
        return False
    parts = key.split("_")
    if len(parts) < 3:
        return False
    if parts[1] not in ("live", "test"):
        return False
    if len(parts[2]) != _KEY_LENGTH // 2:
        return False
    return True
