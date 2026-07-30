from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from typing import Optional
import threading

# Globals configured at import-time but replaceable via configure_database()
_engine = None
SessionLocal = None
engine = None
Base = declarative_base()


def configure_database(database_url: Optional[str] = None):
    """Configure the module-level engine and SessionLocal.

    Supports SQLite (development/testing) and PostgreSQL (production).
    For PostgreSQL, uses connection pooling with health checks.
    """
    global _engine, SessionLocal, engine

    database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///./dev.db')

    connect_args = {}
    engine_kwargs = {}

    if database_url.startswith('sqlite'):
        # SQLite configuration (dev/test)
        connect_args = {"check_same_thread": False}
        if ':memory:' in database_url:
            engine_kwargs['poolclass'] = StaticPool
    else:
        # PostgreSQL configuration (production)
        engine_kwargs = {
            'poolclass': QueuePool,
            'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
            'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20')),
            'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30')),
            'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '1800')),
            'pool_pre_ping': True,  # Verify connections before use
        }

    _engine = create_engine(database_url, connect_args=connect_args, **engine_kwargs)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    engine = _engine

# Global lock for serializing DB writes when multiple threads access the same SQLite connection.
DB_LOCK = threading.Lock()


# Global lock for serializing DB writes when multiple threads access the same SQLite connection.
DB_LOCK = threading.RLock()


def acquire_db_lock():
    """Acquire the database write lock. Safe to call multiple times (reentrant)."""
    DB_LOCK.acquire()


def release_db_lock():
    """Release the database write lock."""
    try:
        DB_LOCK.release()
    except RuntimeError:
        pass  # Lock not held by this thread


def _migrate_add_columns(engine):
    """Add missing columns to existing SQLite tables (safe no-ops if column exists)."""
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        migrations = [
            ("cases", "ALTER TABLE cases ADD COLUMN priority TEXT DEFAULT 'medium'"),
            ("cases", "ALTER TABLE cases ADD COLUMN assigned_to TEXT"),
            ("cases", "ALTER TABLE cases ADD COLUMN updated_at TIMESTAMP"),
            ("evidence", "ALTER TABLE evidence ADD COLUMN bucket TEXT"),
            ("evidence", "ALTER TABLE evidence ADD COLUMN object_key TEXT"),
        ]
        for table, sql in migrations:
            if table in tables:
                existing_cols = {c['name'] for c in inspector.get_columns(table)}
                col_name = sql.split("ADD COLUMN ")[1].split(" ")[0]
                if col_name not in existing_cols:
                    with engine.connect() as conn:
                        conn.execute(text(sql))
                        conn.commit()
    except Exception:
        pass  # best-effort migration


def init_db():
    if _engine is None:
        configure_database()
    # ensure all model modules are imported so Base.metadata is populated
    try:
        import importlib
        importlib.import_module('backend.app.models')
        importlib.import_module('backend.app.compliance')
        importlib.import_module('backend.app.multitenancy')
        importlib.import_module('backend.app.blockchain.models')
    except Exception:
        pass
    Base.metadata.create_all(bind=_engine)
    _migrate_add_columns(_engine)


def get_engine():
    if _engine is None:
        configure_database()
    return _engine


def get_db_session():
    """Get a database session with automatic cleanup."""
    if SessionLocal is None:
        configure_database()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict:
    """Check database connectivity and return status."""
    try:
        eng = get_engine()
        with eng.connect() as conn:
            conn.execute(text('SELECT 1'))
        return {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


# configure at import time using environment variable
configure_database()
