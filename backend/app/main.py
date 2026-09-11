import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning, module='jose.jwt')
warnings.filterwarnings('ignore', category=DeprecationWarning, message='PyPDF2 is deprecated.*')

import os
from dotenv import load_dotenv
load_dotenv()

import time
import uuid
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from . import database
from .auth import router as auth_router
from .evidence import router as evidence_router
from . import models
from .logging_config import setup_logging, get_logger, generate_correlation_id, set_correlation_id, set_user_id
from .processing import start_worker

# Security middleware imports
from .security.headers import SecurityHeadersMiddleware
from .security.rate_limit import RateLimitMiddleware
from .security.audit_middleware import AuditMiddleware, set_audit_middleware

# Observability imports
from .observability import router as observability_router, MetricsMiddleware

# Telemetry imports (OpenTelemetry)
from .telemetry import init_telemetry
from .telemetry.middleware import TelemetryMiddleware

# Compliance models (need table creation)
from .compliance import (
    DataRetentionPolicy, LegalHold, ImmutableEvidenceLock,
    ComplianceAuditEntry, DataDeletionRequest, ComplianceReport,
    DataClassificationTag, RetentionScheduleRun, EvidenceExport, CaseExport,
)

# Multi-tenancy models (need table creation)
from .multitenancy import (
    Organization, Project, OrgMembership, ProjectMembership,
    TenantAuditLog, TenantUsageRecord, TenantProvisioningLog, TenantIsolationRule,
)

# Initialize logging
setup_logging()
logger = get_logger('main')

app = FastAPI(
    title="CrimeKit Backend",
    description="Enterprise-grade AI-powered Digital Forensics & Investigation Platform",
    version=os.getenv("APP_VERSION", "1.0.0"),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    redirect_slashes=False,
)

# CORS configuration for development & LAN access
_cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
if not _cors_origins or _cors_origins == [""] or "*" in _cors_origins:
    _cors_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://localhost:8002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8002",
        "http://192.168.29.240:3000",
        "http://192.168.29.240:3001",
        "http://192.168.29.240:8000",
        "http://192.168.29.240:8002",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=r"https?://([a-zA-Z0-9-]+\.)*(catalystserverless\.in|catalystappsail\.in|localhost|127\.0\.0\.1|192\.168\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Metrics middleware
app.add_middleware(MetricsMiddleware)

# Telemetry middleware (OpenTelemetry tracing + correlation)
app.add_middleware(TelemetryMiddleware)

# Audit middleware (singleton — must not add twice)
_audit = AuditMiddleware(app)
set_audit_middleware(_audit)
# Note: AuditMiddleware is added to the singleton registry but NOT added via
# app.add_middleware() because TelemetryMiddleware (which runs later in the
# middleware stack) already sets request.state.user_id. The AuditMiddleware
# reads that state, so it must run AFTER TelemetryMiddleware processes the
# request. The TelemetryMiddleware already handles user_id extraction.
# If you need AuditMiddleware as a standalone middleware, add it to the app
# and ensure TelemetryMiddleware runs first.


@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    """Add correlation ID to every request."""
    corr_id = request.headers.get("X-Correlation-ID", generate_correlation_id())
    set_correlation_id(corr_id)

    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000

    response.headers["X-Correlation-ID"] = corr_id
    response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

    # Log request
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.2f}ms)",
        extra={
            "extra_data": {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "correlation_id": corr_id,
                "client_ip": request.client.host if request.client else None,
            }
        }
    )
    return response


# Include routers
from . import auth, cases, evidence, ai_pipeline, kg_routes, search_routes, workspace, roles, processing, upload_routes
from . import storage_routes, advanced_forensics_routes, compliance_routes, multitenancy_routes, api_key_routes, timeline_routes, reports_routes

app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(evidence.router)
app.include_router(upload_routes.router)
app.include_router(ai_pipeline.router)
app.include_router(kg_routes.router)
app.include_router(search_routes.router)
app.include_router(workspace.router)
app.include_router(roles.router)
app.include_router(storage_routes.router)
app.include_router(advanced_forensics_routes.router)
app.include_router(compliance_routes.router)
app.include_router(multitenancy_routes.router)
app.include_router(api_key_routes.router)
app.include_router(timeline_routes.router)
app.include_router(reports_routes.router)
app.include_router(processing.router)

# WebSocket routes for real-time graph updates
from . import ws_routes
app.include_router(ws_routes.router)

# Health endpoints (no auth required)
from .health import router as health_router
app.include_router(health_router)

# Observability endpoints (no auth required)
app.include_router(observability_router)

# Enterprise platform routers
from .distributed_routes import router as distributed_router
app.include_router(distributed_router)

# Blockchain / Evidence Proof Fabric router
try:
    from .blockchain.routes import router as blockchain_router
    app.include_router(blockchain_router)
except ImportError:
    pass  # web3.py not installed — blockchain features disabled

# TSK Forensic Intelligence Engine. This is a required application surface;
# dependency failures must stop startup instead of silently removing /tsk/*.
from .tsk_engine.routes import router as tsk_router
app.include_router(tsk_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "correlation_id": generate_correlation_id(),
        }
    )


@app.on_event("startup")
def on_startup():
    logger.info("CrimeKit backend starting up", extra={
        "extra_data": {
            "environment": os.getenv("APP_ENV", "development"),
            "debug": os.getenv("APP_DEBUG", "false"),
            "workers": os.getenv("UVICORN_WORKERS", "2"),
        }
    })

    database.init_db()

    # Initialize OpenTelemetry
    init_telemetry(app)

    # Ensure all enterprise roles exist
    ENTERPRISE_ROLES = [
        ("admin",               "Full platform administrator"),
        ("investigator",        "Lead forensic investigator — default for new users"),
        ("analyst",             "Forensic data analyst"),
        ("viewer",              "Read-only access to evidence and cases"),
        ("evidence_officer",    "Manages evidence chain of custody"),
        ("compliance_officer",  "Compliance and audit access"),
        ("auditor",             "Audit log read access"),
        ("user",                "Basic authenticated user"),
    ]
    db = database.SessionLocal()
    try:
        for role_name, role_desc in ENTERPRISE_ROLES:
            if not db.query(models.Role).filter(models.Role.name == role_name).first():
                db.add(models.Role(name=role_name, description=role_desc))
        db.commit()
        logger.info("All enterprise roles initialized")

        # Migrate: any user whose ONLY role is the legacy 'user' role -> upgrade to 'investigator'
        user_role = db.query(models.Role).filter(models.Role.name == 'user').first()
        inv_role  = db.query(models.Role).filter(models.Role.name == 'investigator').first()
        if user_role and inv_role:
            users_with_only_user_role = [
                u for u in db.query(models.User).all()
                if u.roles and all(r.name == 'user' for r in u.roles)
            ]
            for u in users_with_only_user_role:
                if inv_role not in u.roles:
                    u.roles.append(inv_role)
            if users_with_only_user_role:
                db.commit()
                logger.info(f"Migrated {len(users_with_only_user_role)} user(s) from 'user' -> 'investigator' role")
    finally:
        db.close()

    # Start background processing worker (skip in test mode)
    if os.getenv('TESTING') != '1':
        start_worker()
        logger.info("Background processing worker started")

        # Start realtime event relay (Redis pub/sub -> WebSocket clients)
        try:
            from .realtime_relay import run_event_relay
            asyncio.ensure_future(run_event_relay())
            logger.info("Realtime event relay started")
        except Exception as e:
            logger.warning("Could not start realtime relay: %s", e)


@app.on_event("shutdown")
def on_shutdown():
    logger.info("CrimeKit backend shutting down")
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            from .distributed import shutdown_distributed_system
            loop.create_task(shutdown_distributed_system())
    except Exception:
        pass
    if database._engine:
        database._engine.dispose()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8002"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
