"""OpenTelemetry distributed tracing for CrimeKit.

Provides:
- OTLP/Jaeger/Tempo trace export
- HTTP request tracing
- Database call tracing
- AI pipeline tracing
- Knowledge graph tracing
- Worker job tracing
- Nested span creation
- Context propagation
"""
import logging
import os
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# OpenTelemetry imports with graceful fallback
_OTEL_AVAILABLE = False
_tracer = None
_meter = None

try:
    from opentelemetry import trace, context
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    try:
        from opentelemetry.instrumentation.neo4j import Neo4jInstrumentor
    except ImportError:
        Neo4jInstrumentor = None
    from opentelemetry.trace import StatusCode, Status
    from opentelemetry.context import attach, detach
    from opentelemetry.propagate import set_global_textmap, extract, inject
    from opentelemetry.propagators.composite import CompositePropagator
    from opentelemetry.propagators.textmap import TextMapPropagator
    _OTEL_AVAILABLE = True
except ImportError:
    logger.info("OpenTelemetry not installed; tracing will use no-op implementation")


class NoOpTracer:
    """No-op tracer when OpenTelemetry is not available."""

    @contextmanager
    def start_as_current_span(self, name, **kwargs):
        yield NoOpSpan()


class NoOpSpan:
    """No-op span for fallback."""
    def set_attribute(self, key, value): pass
    def set_status(self, status): pass
    def add_event(self, name, attributes=None): pass
    def record_exception(self, exception): pass
    def end(self): pass
    def __enter__(self): return self
    def __exit__(self, *args): pass


class TelemetryConfig:
    """Configuration for OpenTelemetry telemetry."""

    def __init__(self):
        self.service_name = os.getenv("OTEL_SERVICE_NAME", "crimekit-backend")
        self.service_version = os.getenv("APP_VERSION", "1.0.0")
        self.environment = os.getenv("APP_ENV", "development")
        self.otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
        self.jaeger_endpoint = os.getenv("OTEL_JAEGER_ENDPOINT", "http://localhost:14268/api/traces")
        self.tempo_endpoint = os.getenv("OTEL_TEMPO_ENDPOINT", "")
        self.prometheus_port = int(os.getenv("OTEL_PROMETHEUS_PORT", "9464"))
        self.sample_rate = float(os.getenv("OTEL_SAMPLE_RATE", "1.0"))
        self.export_to_console = os.getenv("OTEL_EXPORT_CONSOLE", "false").lower() == "true"
        self.metrics_interval = int(os.getenv("OTEL_METRICS_INTERVAL", "30"))


_config = TelemetryConfig()


def init_telemetry(app=None):
    """Initialize OpenTelemetry tracing and metrics."""
    global _tracer, _meter

    if not _OTEL_AVAILABLE:
        _tracer = NoOpTracer()
        logger.info("OpenTelemetry not available; using no-op tracer")
        return

    # Create resource
    resource = Resource.create({
        "service.name": _config.service_name,
        "service.version": _config.service_version,
        "deployment.environment": _config.environment,
    })

    # Configure trace provider
    trace_provider = TracerProvider(resource=resource, sampler=None)

    # OTLP exporter (only if explicitly enabled via OTEL_ENABLED=true)
    if os.getenv("OTEL_ENABLED", "false").lower() == "true":
        try:
            otlp_exporter = OTLPSpanExporter(
                endpoint=_config.otlp_endpoint,
                insecure=True,
            )
            trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info("OTLP trace exporter configured: %s", _config.otlp_endpoint)
        except Exception as e:
            logger.warning("Failed to configure OTLP exporter: %s", e)

    # Console exporter (for debugging if enabled)
    if _config.export_to_console:
        console_exporter = ConsoleSpanExporter()
        trace_provider.add_span_processor(BatchSpanProcessor(console_exporter))

    trace.set_tracer_provider(trace_provider)
    _tracer = trace.get_tracer(_config.service_name, _config.service_version)

    # Configure metrics
    try:
        metric_reader = PeriodicExportingMetricReader(
            export_interval_millis=_config.metrics_interval * 1000,
        )
        metric_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader],
        )
        _meter = metric_provider.get_meter(_config.service_name, _config.service_version)
    except Exception as e:
        logger.warning("Failed to configure metrics: %s", e)

    # Instrument FastAPI
    if app is not None:
        FastAPIInstrumentor.instrument_app(app)

    # Instrument libraries
    try:
        SQLAlchemyInstrumentor().instrument()
    except Exception:
        pass

    try:
        RedisInstrumentor().instrument()
    except Exception:
        pass

    try:
        if Neo4jInstrumentor:
            Neo4jInstrumentor().instrument()
    except Exception:
        pass

    logger.info(
        "OpenTelemetry initialized: service=%s env=%s endpoint=%s",
        _config.service_name, _config.environment, _config.otlp_endpoint,
    )


def get_tracer():
    """Get the global tracer instance."""
    return _tracer or NoOpTracer()


def get_meter():
    """Get the global meter instance."""
    return _meter


@contextmanager
def trace_span(name: str, attributes: Optional[Dict[str, Any]] = None, kind=None):
    """Context manager for creating traced spans."""
    tracer = get_tracer()
    try:
        with tracer.start_as_current_span(name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            try:
                yield span
            except Exception as exc:
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                span.record_exception(exc)
                raise
    except AttributeError:
        # NoOpTracer fallback
        yield NoOpSpan()


@contextmanager
def trace_http_request(method: str, path: str, user_id: str = None, case_id: str = None):
    """Trace an HTTP request with standard attributes."""
    attrs = {
        "http.method": method,
        "http.url": path,
        "service.name": _config.service_name,
    }
    if user_id:
        attrs["user.id"] = user_id
    if case_id:
        attrs["case.id"] = case_id

    with trace_span(f"HTTP {method} {path}", attrs) as span:
        yield span


@contextmanager
def trace_forensic_processing(evidence_id: str, processor: str):
    """Trace forensic evidence processing."""
    attrs = {
        "evidence.id": evidence_id,
        "processor.name": processor,
        "processing.type": "forensic",
    }
    with trace_span(f"forensic.process.{processor}", attrs) as span:
        yield span


@contextmanager
def trace_ai_pipeline(operation: str, model: str = None):
    """Trace AI pipeline operations."""
    attrs = {
        "ai.operation": operation,
        "processing.type": "ai_pipeline",
    }
    if model:
        attrs["ai.model"] = model
    with trace_span(f"ai.{operation}", attrs) as span:
        yield span


@contextmanager
def trace_kg_operation(operation: str):
    """Trace knowledge graph operations."""
    attrs = {
        "kg.operation": operation,
        "processing.type": "knowledge_graph",
    }
    with trace_span(f"kg.{operation}", attrs) as span:
        yield span


@contextmanager
def trace_worker_job(job_id: str, processor: str):
    """Trace background worker job execution."""
    attrs = {
        "job.id": job_id,
        "processor.name": processor,
        "processing.type": "background_worker",
    }
    with trace_span(f"worker.job.{processor}", attrs) as span:
        yield span


def add_span_attribute(key: str, value: Any):
    """Add attribute to current span."""
    if _OTEL_AVAILABLE:
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute(key, value)


def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Add event to current span."""
    if _OTEL_AVAILABLE:
        span = trace.get_current_span()
        if span.is_recording():
            span.add_event(name, attributes)


def record_exception(exception: Exception):
    """Record exception on current span."""
    if _OTEL_AVAILABLE:
        span = trace.get_current_span()
        if span.is_recording():
            span.record_exception(exception)
            span.set_status(Status(StatusCode.ERROR, str(exception)))


def shutdown_telemetry():
    """Shutdown telemetry exporters."""
    if _OTEL_AVAILABLE:
        try:
            provider = trace.get_tracer_provider()
            if hasattr(provider, 'shutdown'):
                provider.shutdown()
        except Exception:
            pass
