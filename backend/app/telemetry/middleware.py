"""OpenTelemetry FastAPI middleware for CrimeKit enterprise platform."""

from __future__ import annotations

import logging
import re
import time
import uuid
from typing import Any, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

try:
    from opentelemetry import trace
    from opentelemetry.trace import SpanKind, StatusCode
except ImportError:
    trace = None  # type: ignore[assignment]
    SpanKind = None  # type: ignore[assignment,misc]
    StatusCode = None  # type: ignore[assignment,misc]

try:
    import jwt
except ImportError:
    jwt = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

CORRELATION_ID_HEADER = "X-Correlation-ID"
TRACE_ID_HEADER = "X-Trace-ID"
SPAN_ID_HEADER = "X-Span-ID"
USER_ID_HEADER = "X-User-ID"

_PATH_CASE_RE = re.compile(r"/cases/([0-9a-f-]+)", re.IGNORECASE)
_PATH_EVIDENCE_RE = re.compile(r"/evidence/([0-9a-f-]+)", re.IGNORECASE)

_SENSITIVE_HEADERS = frozenset({
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-auth-token",
})
_SENSITIVE_BODY_FIELDS = frozenset({
    "password",
    "secret",
    "token",
    "api_key",
    "access_token",
    "refresh_token",
})

_request_counter = None
_request_duration = None
_error_counter = None


def _init_metrics() -> None:
    global _request_counter, _request_duration, _error_counter
    if trace is None:
        return
    try:
        from opentelemetry.metrics import get_meter_provider

        meter = get_meter_provider().get_meter("crimekit.telemetry", "1.0.0")
        _request_counter = meter.create_counter(
            "http.server.request.total",
            description="Total number of HTTP requests",
            unit="1",
        )
        _request_duration = meter.create_histogram(
            "http.server.request.duration",
            description="HTTP request duration in milliseconds",
            unit="ms",
        )
        _error_counter = meter.create_counter(
            "http.server.request.errors",
            description="Total number of HTTP error responses",
            unit="1",
        )
    except Exception:
        logger.debug("Failed to initialize OpenTelemetry metrics", exc_info=True)


def _extract_user_id_from_jwt(request: Request) -> str | None:
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:]
    if jwt is None:
        try:
            import base64
            parts = token.split(".")
            if len(parts) == 3:
                payload = parts[1]
                padding = 4 - len(payload) % 4
                payload += "=" * padding
                decoded = base64.urlsafe_b64decode(payload)
                import json
                claims = json.loads(decoded)
                return claims.get("sub") or claims.get("user_id") or claims.get("id")
        except Exception:
            return None

    try:
        # Decode without verification for correlation purposes only;
        # real auth happens in the auth middleware/service.
        unverified = jwt.decode(
            token,
            options={"verify_signature": False, "verify_exp": False},
        )
        return unverified.get("sub") or unverified.get("user_id") or unverified.get("id")
    except Exception:
        return None


def _extract_case_id(request: Request) -> str | None:
    match = _PATH_CASE_RE.search(str(request.url.path))
    if match:
        return match.group(1)
    case_id = request.query_params.get("case_id")
    return case_id


def _extract_evidence_id(request: Request) -> str | None:
    match = _PATH_EVIDENCE_RE.search(str(request.url.path))
    if match:
        return match.group(1)
    evidence_id = request.query_params.get("evidence_id")
    return evidence_id


def _mask_sensitive_headers(headers: dict[str, str]) -> dict[str, str]:
    masked: dict[str, str] = {}
    for k, v in headers.items():
        if k.lower() in _SENSITIVE_HEADERS:
            masked[k] = "***REDACTED***"
        else:
            masked[k] = v
    return masked


class TelemetryMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that injects correlation/trace identifiers and records metrics."""

    def __init__(self, app: ASGIApp, expose_trace_headers: bool = False) -> None:
        super().__init__(app)
        self._expose_trace_headers = expose_trace_headers

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        correlation_id = request.headers.get(CORRELATION_ID_HEADER) or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        request.state.start_time = time.perf_counter()

        user_id = _extract_user_id_from_jwt(request)
        case_id = _extract_case_id(request)
        evidence_id = _extract_evidence_id(request)
        request.state.user_id = user_id
        request.state.case_id = case_id
        request.state.evidence_id = evidence_id

        # ---------- span ----------
        span = None
        trace_id = ""
        span_id = ""
        tracer = trace.get_tracer("crimekit.api", "1.0.0") if trace else None

        if tracer:
            attributes: dict[str, Any] = {
                "http.method": request.method,
                "http.url": str(request.url),
                "http.scheme": request.url.scheme,
                "http.host": request.headers.get("host", ""),
                "http.user_agent": request.headers.get("user-agent", ""),
                "http.client_ip": request.headers.get(
                    "x-forwarded-for", request.client.host if request.client else ""
                ),
                "correlation.id": correlation_id,
            }
            if user_id:
                attributes["user.id"] = user_id
            if case_id:
                attributes["case.id"] = case_id
            if evidence_id:
                attributes["evidence.id"] = evidence_id

            with tracer.start_as_current_span(
                f"{request.method} {request.url.path}",
                kind=SpanKind.SERVER,
                attributes=attributes,
            ) as current_span:
                span = current_span
                try:
                    otel_ctx = current_span.get_span_context()
                    trace_id = format(otel_ctx.trace_id, "032x") if otel_ctx else ""
                    span_id = format(otel_ctx.span_id, "016x") if otel_ctx else ""
                except (AttributeError, Exception):
                    trace_id = ""
                    span_id = ""
                response = await self._process_request(
                    request, call_next, correlation_id, trace_id, span_id
                )
                if span and StatusCode:
                    if response.status_code >= 500:
                        span.set_status(StatusCode.ERROR, f"HTTP {response.status_code}")
                    else:
                        span.set_status(StatusCode.OK)
        else:
            response = await self._process_request(
                request, call_next, correlation_id, trace_id, span_id
            )

        return response

    async def _process_request(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
        correlation_id: str,
        trace_id: str,
        span_id: str,
    ) -> Response:
        start = request.state.start_time
        response: Response
        status_code = 500
        error_detail: str | None = None

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            logger.exception("Unhandled exception in request %s", correlation_id)
            status_code = 500
            error_detail = str(exc)
            response = JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "correlation_id": correlation_id,
                },
            )
            # Ensure CORS headers are present on unhandled-error responses so the
            # browser does not treat a server 500 as a network failure. This
            # middleware is outermost and bypasses the inner CORSMiddleware.
            origin = request.headers.get("origin")
            if origin and re.match(
                r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+):(3000|3001|8000|8002)$",
                origin,
            ):
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Vary"] = "Origin"

        duration_ms = (time.perf_counter() - start) * 1000

        response.headers[CORRELATION_ID_HEADER] = correlation_id
        if self._expose_trace_headers:
            if trace_id:
                response.headers[TRACE_ID_HEADER] = trace_id
            if span_id:
                response.headers[SPAN_ID_HEADER] = span_id

        if hasattr(request.state, "user_id") and request.state.user_id:
            response.headers[USER_ID_HEADER] = request.state.user_id

        # ---------- metrics ----------
        method = request.method
        path = request.url.path
        route = self._normalise_path(path)
        labels = {
            "method": method,
            "route": route,
            "status_code": str(status_code),
        }
        if _request_counter:
            _request_counter.add(1, labels)
        if _request_duration:
            _request_duration.record(duration_ms, labels)
        if _error_counter and status_code >= 400:
            _error_counter.add(1, labels)

        # ---------- structured log ----------
        log_data = {
            "correlation_id": correlation_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
            "user_id": getattr(request.state, "user_id", None),
            "case_id": getattr(request.state, "case_id", None),
            "evidence_id": getattr(request.state, "evidence_id", None),
            "client_ip": request.headers.get(
                "x-forwarded-for", request.client.host if request.client else ""
            ),
        }
        if trace_id:
            log_data["trace_id"] = trace_id
        if span_id:
            log_data["span_id"] = span_id
        if error_detail:
            log_data["error"] = error_detail

        if status_code >= 500:
            logger.error("request completed", extra=log_data)
        elif status_code >= 400:
            logger.warning("request completed", extra=log_data)
        else:
            logger.info("request completed", extra=log_data)

        return response

    @staticmethod
    def _normalise_path(path: str) -> str:
        parts = path.strip("/").split("/")
        normalised: list[str] = []
        for part in parts:
            if re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", part, re.IGNORECASE):
                normalised.append("{id}")
            elif re.match(r"^\d+$", part):
                normalised.append("{id}")
            else:
                normalised.append(part)
        return "/" + "/".join(normalised)


class DependencyTrackingMiddleware(BaseHTTPMiddleware):
    """Tracks downstream HTTP dependency calls."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request.state.dependencies: list[dict[str, Any]] = []
        request.state._dep_start = time.perf_counter()
        response = await call_next(request)
        return response


def setup_telemetry(app: FastAPI, expose_trace_headers: bool = False) -> None:
    """Register telemetry middleware on a FastAPI application."""
    _init_metrics()
    app.add_middleware(
        TelemetryMiddleware,
        expose_trace_headers=expose_trace_headers,
    )
    app.add_middleware(DependencyTrackingMiddleware)
    logger.info("Telemetry middleware registered")
