"""JWT access token revocation via in-memory blocklist.

Stores revoked token JTI/claims for the duration of their expiry,
preventing reuse of invalidated tokens.
"""
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class TokenBlocklist:
    """In-memory blocklist for revoked JWT access tokens."""

    def __init__(self):
        self._blocked: dict[str, float] = {}  # token_id -> expiry_timestamp

    def add(self, token_id: str, expires_at: float) -> None:
        """Add a token to the blocklist."""
        self._blocked[token_id] = expires_at
        logger.info("Token %s added to blocklist (expires: %.0f)", token_id, expires_at)

    def is_blocked(self, token_id: str) -> bool:
        """Check if a token is revoked."""
        if token_id not in self._blocked:
            return False
        # Check if blocklist entry has expired
        if time.time() > self._blocked[token_id]:
            del self._blocked[token_id]
            return False
        return True

    def cleanup(self) -> int:
        """Remove expired entries. Returns number removed."""
        now = time.time()
        expired = [k for k, v in self._blocked.items() if now > v]
        for k in expired:
            del self._blocked[k]
        return len(expired)

    def size(self) -> int:
        """Return number of blocked tokens."""
        return len(self._blocked)


# Global singleton
_token_blocklist = TokenBlocklist()


def get_token_blocklist() -> TokenBlocklist:
    return _token_blocklist
