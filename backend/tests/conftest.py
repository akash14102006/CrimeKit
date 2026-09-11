import sys
import os
import types

os.environ['TESTING'] = '1'

try:
    import backend.app as _app_pkg
except ModuleNotFoundError:
    try:
        import app as _app_pkg
    except ModuleNotFoundError:
        _app_pkg = None

if _app_pkg and hasattr(_app_pkg, "database"):
    _actual_app = _app_pkg
elif _app_pkg and hasattr(_app_pkg, "app") and hasattr(_app_pkg.app, "database"):
    _actual_app = _app_pkg.app
else:
    from app import app as _actual_app

backend_pkg = types.ModuleType("backend")
backend_pkg.app = _actual_app
sys.modules["backend"] = backend_pkg
sys.modules["backend.app"] = _actual_app
sys.modules["app"] = _actual_app

from backend.app import database

import warnings
import pytest
# suppress DeprecationWarning during tests (third-party libs may emit UTC-related deprecations)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Configure an in-memory SQLite engine at import time so imports during collection
# use the test DB. This engine will be reused for the test run but we recreate
# schema before each test to ensure isolation.
database.configure_database('sqlite:///:memory:')
database.init_db()


@pytest.fixture(autouse=True)
def clean_db():
    import importlib
    importlib.import_module('backend.app.models')
    importlib.import_module('backend.app.compliance')
    try:
        importlib.import_module('backend.app.blockchain.models')
    except (ImportError, ModuleNotFoundError):
        pass

    eng = database.get_engine()
    database.Base.metadata.drop_all(bind=eng)
    database.Base.metadata.create_all(bind=eng)

    # Seed enterprise roles so tests can assign them
    from backend.app import models
    db = database.SessionLocal()
    for role_name, role_desc in [
        ("admin",              "Full platform administrator"),
        ("investigator",       "Lead forensic investigator"),
        ("analyst",            "Forensic data analyst"),
        ("viewer",             "Read-only access"),
        ("evidence_officer",   "Manages evidence chain of custody"),
        ("compliance_officer", "Compliance and audit access"),
        ("auditor",            "Audit log read access"),
        ("user",               "Basic authenticated user"),
    ]:
        if not db.query(models.Role).filter(models.Role.name == role_name).first():
            db.add(models.Role(name=role_name, description=role_desc))
    db.commit()
    db.close()

    yield
    try:
        database.Base.metadata.drop_all(bind=eng)
    except Exception:
        pass


@pytest.fixture
def client():
    from backend.app.main import app
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c
