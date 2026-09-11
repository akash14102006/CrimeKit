"""
Health check endpoints for CrimeKit.

Provides:
- /health - Basic liveness check (always returns ok)
- /health/ready - Readiness check (verifies all dependencies)
- /health/live - Liveness check (process is alive)
- /health/detailed - Full status with dependency details
"""
import os
import time
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from .logging_config import get_logger

router = APIRouter(tags=['health'])
logger = get_logger('health')


async def check_postgres() -> dict:
    """Check PostgreSQL connectivity."""
    start = time.perf_counter()
    try:
        from . import database
        engine = database.get_engine()
        with engine.connect() as conn:
            conn.execute(__import__('sqlalchemy').text('SELECT 1'))
        latency_ms = (time.perf_counter() - start) * 1000
        return {
            "status": "healthy",
            "service": "postgres",
            "latency_ms": round(latency_ms, 2),
            "message": "PostgreSQL connection successful"
        }
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        logger.error(f"PostgreSQL health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "postgres",
            "latency_ms": round(latency_ms, 2),
            "message": str(e)
        }


async def check_redis() -> dict:
    """Check Redis connectivity."""
    start = time.perf_counter()
    try:
        import redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        client = redis.from_url(redis_url, socket_timeout=5)
        client.ping()
        latency_ms = (time.perf_counter() - start) * 1000
        client.close()
        return {
            "status": "healthy",
            "service": "redis",
            "latency_ms": round(latency_ms, 2),
            "message": "Redis connection successful"
        }
    except ImportError:
        return {
            "status": "degraded",
            "service": "redis",
            "latency_ms": 0,
            "message": "redis package not installed"
        }
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "redis",
            "latency_ms": round(latency_ms, 2),
            "message": str(e)
        }


async def check_neo4j() -> dict:
    """Check Neo4j connectivity."""
    start = time.perf_counter()
    try:
        from neo4j import GraphDatabase
        uri = os.getenv('NEO4J_URI')
        if not uri:
            return {
                "status": "degraded",
                "service": "neo4j",
                "latency_ms": 0,
                "message": "NEO4J_URI not configured"
            }
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD')
        if not password:
            return {
                "status": "degraded",
                "service": "neo4j",
                "latency_ms": 0,
                "message": "NEO4J_PASSWORD not configured"
            }
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
        latency_ms = (time.perf_counter() - start) * 1000
        return {
            "status": "healthy",
            "service": "neo4j",
            "latency_ms": round(latency_ms, 2),
            "message": "Neo4j connection successful"
        }
    except ImportError:
        return {
            "status": "degraded",
            "service": "neo4j",
            "latency_ms": 0,
            "message": "neo4j package not installed"
        }
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        logger.error(f"Neo4j health check failed: {e}")
        return {
            "status": "degraded",  # Neo4j is optional
            "service": "neo4j",
            "latency_ms": round(latency_ms, 2),
            "message": str(e)
        }


async def check_minio() -> dict:
    """Check MinIO connectivity."""
    start = time.perf_counter()
    try:
        import urllib.request
        endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
        use_ssl = os.getenv('MINIO_USE_SSL', 'false').lower() == 'true'
        protocol = 'https' if use_ssl else 'http'
        url = f"{protocol}://{endpoint}/minio/health/live"
        req = urllib.request.Request(url, method='GET')
        urllib.request.urlopen(req, timeout=5)
        latency_ms = (time.perf_counter() - start) * 1000
        return {
            "status": "healthy",
            "service": "minio",
            "latency_ms": round(latency_ms, 2),
            "message": "MinIO connection successful"
        }
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        logger.error(f"MinIO health check failed: {e}")
        return {
            "status": "degraded",  # MinIO is optional
            "service": "minio",
            "latency_ms": round(latency_ms, 2),
            "message": str(e)
        }


async def check_database_schema() -> dict:
    """Check that database tables exist."""
    start = time.perf_counter()
    try:
        from sqlalchemy import text
        from . import database
        engine = database.get_engine()
        with engine.connect() as conn:
            if str(engine.url).startswith('sqlite'):
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            else:
                result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
            tables = [row[0] for row in result]
        latency_ms = (time.perf_counter() - start) * 1000
        return {
            "status": "healthy",
            "service": "database_schema",
            "latency_ms": round(latency_ms, 2),
            "message": f"Found {len(tables)} tables",
            "tables": tables
        }
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        return {
            "status": "unhealthy",
            "service": "database_schema",
            "latency_ms": round(latency_ms, 2),
            "message": str(e)
        }


@router.get("/health")
async def health():
    """Basic liveness endpoint."""
    return {
        "status": "ok",
        "service": "crimekit-backend",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health/ready")
async def readiness():
    """Readiness check - verifies all critical dependencies."""
    checks = await asyncio.gather(
        check_postgres(),
        check_redis(),
        return_exceptions=True
    )
    
    all_healthy = all(
        c.get("status") == "healthy" 
        for c in checks if isinstance(c, dict)
    )
    
    return JSONResponse(
        status_code=200 if all_healthy else 503,
        content={
            "status": "ready" if all_healthy else "not_ready",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": [c for c in checks if isinstance(c, dict)]
        }
    )


@router.get("/health/live")
async def liveness():
    """Liveness check - process is alive and responsive."""
    return {
        "status": "alive",
        "service": "crimekit-backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": time.time() - _start_time
    }


@router.get("/health/detailed")
async def detailed_health():
    """Full health status with all dependency checks."""
    checks = await asyncio.gather(
        check_postgres(),
        check_redis(),
        check_neo4j(),
        check_minio(),
        check_database_schema(),
        return_exceptions=True
    )
    
    results = [c for c in checks if isinstance(c, dict)]
    
    # Determine overall status
    statuses = [c.get("status", "unknown") for c in results]
    if all(s == "healthy" for s in statuses):
        overall = "healthy"
    elif any(s == "unhealthy" for s in statuses):
        overall = "degraded"
    else:
        overall = "degraded"
    
    return {
        "status": overall,
        "service": "crimekit-backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("APP_ENV", "development"),
        "checks": results
    }


# Record startup time
_start_time = time.time()
