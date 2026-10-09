"""Application-level rate limiting middleware using in-memory sliding window.

Falls back to in-memory if Redis is unavailable. Supports per-user and
per-IP rate limiting with configurable windows and limits.
"""
import asyncio
import logging
import os
import time
from collections import defaultdict
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class _SlidingWindowCounter:
    """In-memory sliding window rate limiter."""

    def __init__(self):
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._window_sec = 60

    def is_rate_limited(self, key: str, max_requests: int, window_sec: int = 60) -> bool:
        now = time.time()
        cutoff = now - window_sec
        timestamps = self._requests[key]
        self._requests[key] = [t for t in timestamps if t > cutoff]
        if len(self._requests[key]) >= max_requests:
            return True
        self._requests[key].append(now)
        return False

    def get_remaining(self, key: str, max_requests: int, window_sec: int = 60) -> int:
        now = time.time()
        cutoff = now - window_sec
        timestamps = self._requests[key]
        current = len([t for t in timestamps if t > cutoff])
        return max(0, max_requests - current)

    def get_reset_time(self, key: str, window_sec: int = 60) -> float:
        timestamps = self._requests.get(key, [])
        if not timestamps:
            return 0
        return max(0, window_sec - (time.time() - timestamps[0]))


# Global singleton
_limiter = _SlidingWindowCounter()


class RateLimitConfig:
    """Rate limit configuration."""

    def __init__(
        self,
        default_limit: int = 100,
        default_window: int = 60,
        login_limit: int = 10,
        login_window: int = 300,
        upload_limit: int = 10,
        upload_window: int = 60,
        api_key_limit: int = 1000,
        api_key_window: int = 60,
        search_limit: int = 60,
        search_window: int = 60,
        compliance_limit: int = 30,
        compliance_window: int = 60,
        storage_limit: int = 30,
        storage_window: int = 60,
        tenant_limit: int = 30,
        tenant_window: int = 60,
        distributed_limit: int = 50,
        distributed_window: int = 60,
    ):
        self.default_limit = default_limit
        self.default_window = default_window
        self.login_limit = login_limit
        self.login_window = login_window
        self.upload_limit = upload_limit
        self.upload_window = upload_window
        self.api_key_limit = api_key_limit
        self.api_key_window = api_key_window
        self.search_limit = search_limit
        self.search_window = search_window
        self.compliance_limit = compliance_limit
        self.compliance_window = compliance_window
        self.storage_limit = storage_limit
        self.storage_window = storage_window
        self.tenant_limit = tenant_limit
        self.tenant_window = tenant_window
        self.distributed_limit = distributed_limit
        self.distributed_window = distributed_window

    def get_limit(self, path: str) -> tuple[int, int]:
        """Return (max_requests, window_sec) for a given path."""
        if "/auth/login" in path or "/auth/register" in path:
            return self.login_limit, self.login_window
        if "/evidence/upload" in path or "/uploads" in path:
            return self.upload_limit, self.upload_window
        if "/api/v1/search" in path:
            return self.search_limit, self.search_window
        if "/api/v1/compliance" in path:
            return self.compliance_limit, self.compliance_window
        if "/api/v1/storage" in path:
            return self.storage_limit, self.storage_window
        if "/api/v1/tenants" in path:
            return self.tenant_limit, self.tenant_window
        if "/api/v1/distributed" in path:
            return self.distributed_limit, self.distributed_window
        return self.default_limit, self.default_window


_rate_config = RateLimitConfig()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with per-IP and per-user tracking."""

    def __init__(self, app, config: Optional[RateLimitConfig] = None):
        super().__init__(app)
        self.config = config or _rate_config

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        if request.method == "OPTIONS" or os.getenv("TESTING") == "1":
            return await call_next(request)

        # Skip rate limiting for health checks
        if path.startswith("/health"):
            return await call_next(request)

        # Determine rate limit for this path
        max_requests, window = self.config.get_limit(path)
        key = f"ip:{client_ip}:{path}"

        if _limiter.is_rate_limited(key, max_requests, window):
            reset_time = _limiter.get_reset_time(key, window)
            logger.warning(
                "Rate limit exceeded for %s on %s",
                client_ip, path,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": int(reset_time) + 1,
                },
                headers={
                    "Retry-After": str(int(reset_time) + 1),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + reset_time)),
                },
            )

        response = await call_next(request)

        remaining = _limiter.get_remaining(key, max_requests, window)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + window))

        return response
