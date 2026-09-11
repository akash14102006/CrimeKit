"""Enterprise Observability: Prometheus metrics, enhanced health checks, metrics middleware.

Provides:
- /metrics endpoint for Prometheus scraping
- Request duration histograms, request counters, error rate tracking
- Forensic processing metrics
- Database connection pool metrics
- System health indicators
"""
import logging
import os
import time
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

router = APIRouter(tags=["observability"])


class MetricsCollector:
    """In-memory metrics collector for Prometheus exposition."""

    def __init__(self):
        self._request_count: dict[str, int] = defaultdict(int)
        self._request_duration: dict[str, list[float]] = defaultdict(list)
        self._error_count: dict[str, int] = defaultdict(int)
        self._forensic_jobs: dict[str, int] = defaultdict(int)
        self._forensic_duration: list[float] = []
        self._active_connections: int = 0
        self._start_time = time.time()

    def record_request(self, method: str, path: str, status_code: int, duration_ms: float):
        key = f"{method}:{path}"
        self._request_count[key] += 1
        self._request_duration[key].append(duration_ms)
        if status_code >= 400:
            self._error_count[f"{method}:{path}:{status_code}"] += 1

    def record_forensic_job(self, processor: str, status: str, duration_ms: float):
        self._forensic_jobs[f"{processor}:{status}"] += 1
        self._forensic_duration.append(duration_ms)

    def get_prometheus_metrics(self) -> str:
        """Generate Prometheus text format metrics."""
        lines = []
        lines.append("# HELP crimekit_http_requests_total Total HTTP requests")
        lines.append("# TYPE crimekit_http_requests_total counter")
        for key, count in self._request_count.items():
            method, path = key.split(":", 1)
            lines.append(f'crimekit_http_requests_total{{method="{method}",path="{path}"}} {count}')

        lines.append("# HELP crimekit_http_request_duration_seconds Request duration histogram")
        lines.append("# TYPE crimekit_http_request_duration_seconds histogram")
        for key, durations in self._request_duration.items():
            method, path = key.split(":", 1)
            if durations:
                avg = sum(durations) / len(durations)
                p99 = sorted(durations)[int(len(durations) * 0.99)] if len(durations) > 1 else durations[0]
                lines.append(f'crimekit_http_request_duration_seconds{{method="{method}",path="{path}",quantile="0.5"}} {avg/1000:.4f}')
                lines.append(f'crimekit_http_request_duration_seconds{{method="{method}",path="{path}",quantile="0.99"}} {p99/1000:.4f}')

        lines.append("# HELP crimekit_http_errors_total Total HTTP errors")
        lines.append("# TYPE crimekit_http_errors_total counter")
        for key, count in self._error_count.items():
            parts = key.rsplit(":", 2)
            if len(parts) == 3:
                method, path, status = parts
                lines.append(f'crimekit_http_errors_total{{method="{method}",path="{path}",status="{status}"}} {count}')

        lines.append("# HELP crimekit_forensic_jobs_total Total forensic processing jobs")
        lines.append("# TYPE crimekit_forensic_jobs_total counter")
        for key, count in self._forensic_jobs.items():
            processor, status = key.split(":", 1)
            lines.append(f'crimekit_forensic_jobs_total{{processor="{processor}",status="{status}"}} {count}')

        uptime = time.time() - self._start_time
        lines.append(f"# HELP crimekit_uptime_seconds Application uptime")
        lines.append(f"# TYPE crimekit_uptime_seconds gauge")
        lines.append(f"crimekit_uptime_seconds {uptime:.0f}")

        return "\n".join(lines) + "\n"


# Global metrics collector
_metrics = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    return _metrics


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware that records request metrics for Prometheus."""

    SKIP_PATHS = {"/health", "/health/ready", "/health/live", "/metrics"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        _metrics.record_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        return response


@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    content = _metrics.get_prometheus_metrics()
    return Response(content=content, media_type="text/plain; charset=utf-8")


@router.get("/metrics/json")
async def json_metrics():
    """JSON metrics endpoint for dashboards."""
    return {
        "request_count": dict(_metrics._request_count),
        "error_count": dict(_metrics._error_count),
        "forensic_jobs": dict(_metrics._forensic_jobs),
        "uptime_seconds": time.time() - _metrics._start_time,
    }
