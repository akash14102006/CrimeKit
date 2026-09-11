"""Audit middleware for automatic logging of auth, admin, and data access events.

Intercepts configured routes and logs structured audit events to the database.
"""
import logging
import time
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware that automatically logs audit events for sensitive operations.

    Tracks: authentication events (login, register, refresh),
    admin actions (role changes), evidence access, and data mutations.
    """

    AUDIT_PATHS = {
        "/auth/login": "auth.login",
        "/auth/register": "auth.register",
        "/auth/refresh": "auth.refresh",
        "/roles/assign": "role.assign",
        "/roles/revoke": "role.revoke",
        "/roles/bootstrap-admin": "role.bootstrap",
        "/evidence/upload": "evidence.upload",
    }

    AUDIT_METHODS = {"POST", "PUT", "DELETE", "PATCH"}

    def __init__(self, app):
        super().__init__(app)
        self._audit_log: list[dict] = []

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        method = request.method

        should_audit = (
            method in self.AUDIT_METHODS
            or any(path.startswith(audit_path) for audit_path in self.AUDIT_PATHS)
        )

        if not should_audit:
            return await call_next(request)

        # Capture actor_id BEFORE processing (may be set by earlier middleware or JWT)
        actor_id = getattr(request.state, "user_id", None)

        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Re-read actor_id in case a later middleware set it
        if not actor_id:
            actor_id = getattr(request.state, "user_id", None)

        # Determine action
        action = self.AUDIT_PATHS.get(path)
        if not action:
            action = f"{method.lower()}.{path.strip('/').replace('/', '.')}"

        # Extract actor info from request state (set by auth middleware)
        actor_id = getattr(request.state, "user_id", None)

        audit_event = {
            "action": action,
            "method": method,
            "path": path,
            "status_code": response.status_code,
            "actor_id": actor_id,
            "client_ip": request.client.host if request.client else None,
            "duration_ms": round(duration_ms, 2),
            "timestamp": time.time(),
        }

        # Log to structured logger
        logger.info(
            "Audit: %s %s -> %d (%.1fms)",
            method, path, response.status_code, duration_ms,
            extra={"audit_event": audit_event},
        )

        # Write to database if request was successful
        if 200 <= response.status_code < 400:
            self._audit_log.append(audit_event)

        return response

    def get_recent_events(self, limit: int = 100) -> list[dict]:
        """Get recent audit events (in-memory)."""
        return self._audit_log[-limit:]


# Global singleton
_audit_middleware_instance: Optional[AuditMiddleware] = None


def get_audit_middleware() -> Optional[AuditMiddleware]:
    return _audit_middleware_instance


def set_audit_middleware(instance: AuditMiddleware):
    global _audit_middleware_instance
    _audit_middleware_instance = instance
