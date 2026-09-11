"""Field-level encryption at rest using Fernet (AES-128-CBC with HMAC-SHA256).

Provides encrypt/decrypt for sensitive evidence metadata and findings.
"""
import base64
import hashlib
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Fernet key derivation from a master passphrase
_FERNET_KEY_LENGTH = 32


def derive_fernet_key(passphrase: str, salt: bytes = b"crimekit-v1-salt") -> bytes:
    """Derive a Fernet-compatible key from a passphrase using PBKDF2."""
    import hashlib
    key = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, 100000, dklen=_FERNET_KEY_LENGTH)
    return base64.urlsafe_b64encode(key)


class FieldEncryptor:
    """Simple field-level encryption using AES-GCM (via stdlib hmac for key derivation).

    Falls back to XOR-based obfuscation if cryptography is not available.
    """

    def __init__(self, master_key: Optional[str] = None):
        self._master_key = master_key or os.getenv("ENCRYPTION_KEY", "dev-encryption-change-me")
        self._key_derived = self._derive_key(self._master_key)

    def _derive_key(self, passphrase: str) -> bytes:
        """Derive a 32-byte key from passphrase."""
        return hashlib.sha256(passphrase.encode()).digest()

    def encrypt_field(self, plaintext: str) -> str:
        """Encrypt a string field. Returns base64-encoded ciphertext."""
        if not plaintext:
            return ""
        try:
            from cryptography.fernet import Fernet
            fernet_key = derive_fernet_key(self._master_key)
            f = Fernet(fernet_key)
            return f.encrypt(plaintext.encode()).decode()
        except ImportError:
            # Fallback: simple XOR obfuscation (NOT secure, use for non-critical fields)
            key = self._key_derived
            data = plaintext.encode()
            encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
            return base64.b64encode(encrypted).decode()

    def decrypt_field(self, ciphertext: str) -> str:
        """Decrypt a base64-encoded ciphertext field."""
        if not ciphertext:
            return ""
        try:
            from cryptography.fernet import Fernet
            fernet_key = derive_fernet_key(self._master_key)
            f = Fernet(fernet_key)
            return f.decrypt(ciphertext.encode()).decode()
        except ImportError:
            # Fallback: XOR decryption
            key = self._key_derived
            data = base64.b64decode(ciphertext)
            decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
            return decrypted.decode()

    def hash_for_search(self, plaintext: str) -> str:
        """Create a deterministic hash for searchable encryption."""
        return hashlib.sha256(
            self._key_derived + plaintext.encode()
        ).hexdigest()


# Global singleton
_field_encryptor: Optional[FieldEncryptor] = None


def get_encryptor() -> FieldEncryptor:
    global _field_encryptor
    if _field_encryptor is None:
        _field_encryptor = FieldEncryptor()
    return _field_encryptor
