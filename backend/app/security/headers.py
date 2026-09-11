"""Security headers middleware for FastAPI.

Adds HSTS, CSP, X-Frame-Options, X-Content-Type-Options,
Referrer-Policy, Permissions-Policy, Cache-Control, and
X-XSS-Protection to every response.
"""
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that injects security headers into every HTTP response."""

    def __init__(self, app, strict_transport_security: bool = True):
        super().__init__(app)
        self.hsts_enabled = strict_transport_security

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), "
            "gyroscope=(), magnetometer=(), microphone=(), "
            "payment=(), usb=(), interest-cohort=()"
        )
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
        response.headers["Pragma"] = "no-cache"

        if self.hsts_enabled:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # CSP header
        # connect-src MUST allow the backend origin or the browser blocks all
        # fetch/XHR from the frontend to the API (this was the root cause of
        # "Network Error" / "CORS blocked" when frontend on :3000 calls :8002).
        csp = os.getenv(
            "CONTENT_SECURITY_POLICY",
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "font-src 'self' data:; "
            "connect-src 'self' "
            "http://localhost:3000 http://localhost:3001 http://localhost:8000 http://localhost:8002 "
            "http://127.0.0.1:3000 http://127.0.0.1:3001 http://127.0.0.1:8000 http://127.0.0.1:8002 "
            "ws://localhost:3000 ws://localhost:3001 "
            "wss://localhost:3000 wss://localhost:3001; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp

        return response
