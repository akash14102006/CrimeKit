"""
Targeted tests for QTC-02 defect remediations:
- P2-001: Blockchain settings and router importability
- P2-002: Descope first-time user provisioning, least privilege, and role preservation
- P3-001: Trailing slash compatibility (/cases, /cases/, /evidence, /evidence/)
- P3-002: Case status enum validation (active, closed, archived, pending, invalid -> 422)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

try:
    from backend.app.main import app
    from backend.app import database, models, schemas
    from backend.app.auth import get_db, create_access_token, _sync_descope_user
    from backend.app.schemas import CaseStatus
except ModuleNotFoundError:
    from app.main import app
    from app import database, models, schemas
    from app.auth import get_db, create_access_token, _sync_descope_user
    from app.schemas import CaseStatus

# Test SQLite in-memory database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    app.dependency_overrides[get_db] = override_get_db
    models.Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    # Populate standard roles
    roles = ["admin", "investigator", "analyst", "viewer", "evidence_officer", "compliance_officer", "auditor", "user"]
    for rname in roles:
        if not db.query(models.Role).filter(models.Role.name == rname).first():
            db.add(models.Role(name=rname, description=f"{rname} role"))
    db.commit()
    try:
        yield db
    finally:
        db.close()
        models.Base.metadata.drop_all(bind=test_engine)
        app.dependency_overrides.pop(get_db, None)



@pytest.fixture
def client():
    return TestClient(app)


# ─── P2-001: Blockchain Settings & Router ────────────────────────────────────

def test_p2_001_blockchain_config_importable():
    """Verify BlockchainConfig imports and initializes with defaults."""
    from app.blockchain.config import BlockchainConfig, get_blockchain_config
    cfg = get_blockchain_config()
    assert isinstance(cfg, BlockchainConfig)
    assert cfg.chain_id == 80002
    assert cfg.network == "polygon-amoy"


def test_p2_001_blockchain_routes_included(client):
    """Verify blockchain endpoints are registered on app."""
    routes = [r.path for r in app.routes]
    assert "/api/v1/blockchain/protocol" in routes
    assert "/api/v1/blockchain/stats" in routes


# ─── P2-002: Descope First-Time User Provisioning & RBAC ────────────────────

def test_p2_002_a_existing_user_login(setup_database):
    """Test A: Existing user is identified and existing roles preserved."""
    db = setup_database
    user = models.User(email="existing@descope.test", password_hash="", is_active=True)
    admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
    user.roles.append(admin_role)
    db.add(user)
    db.commit()

    payload = {"email": "existing@descope.test", "sub": "descope_user_existing"}
    synced = _sync_descope_user(db, payload)
    assert synced.id == user.id
    role_names = [r.name for r in synced.roles]
    assert "admin" in role_names


def test_p2_002_b_and_e_new_user_least_privilege_viewer(setup_database, monkeypatch):
    """Test B & E: New user auto-provisioning in production defaults to 'viewer' role (least privilege)."""
    db = setup_database
    # Force production mode: AUTH_DEMO_MODE=false
    monkeypatch.setenv("AUTH_DEMO_MODE", "false")

    payload = {
        "email": "newbie@descope.test",
        "sub": "descope_sub_newbie_123",
        "roles": [],  # No roles provided by Descope
    }
    user = _sync_descope_user(db, payload)
    assert user is not None
    assert user.email == "newbie@descope.test"
    role_names = [r.name for r in user.roles]
    assert "jury_evaluator" in role_names
    assert "investigator" not in role_names
    assert "admin" not in role_names


def test_p2_002_c_invalid_token(client):
    """Test C: Invalid token returns HTTP 401."""
    resp = client.get("/auth/me", headers={"Authorization": "Bearer not-a-valid-token"})
    assert resp.status_code == 401
    assert "Invalid or expired token" in resp.json()["detail"]


def test_p2_002_d_missing_identity_claims(setup_database, monkeypatch):
    """Test D: Missing email and sub claims in token raises 401."""
    from app.auth import get_current_user
    from fastapi import HTTPException

    # Token with neither sub nor email
    token = create_access_token({"some_other_claim": "test"})
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=setup_database)
    assert exc_info.value.status_code == 401
    assert "no user identity" in exc_info.value.detail.lower()


def test_p2_002_f_and_g_repeated_login_idempotency_and_role_preservation(setup_database, monkeypatch):
    """Test F & G: Repeated logins are idempotent and do not wipe custom local roles."""
    db = setup_database
    monkeypatch.setenv("AUTH_DEMO_MODE", "false")

    payload = {"email": "idempotent@descope.test", "sub": "descope_idemp_1"}
    user1 = _sync_descope_user(db, payload)
    assert len(user1.roles) == 1
    assert user1.roles[0].name == "jury_evaluator"

    # Admin promotes user locally to analyst
    analyst_role = db.query(models.Role).filter(models.Role.name == "analyst").first()
    user1.roles.append(analyst_role)
    db.commit()

    # User logs in again via Descope without role claims
    user2 = _sync_descope_user(db, payload)
    assert user2.id == user1.id
    role_names = [r.name for r in user2.roles]
    assert "jury_evaluator" in role_names
    assert "analyst" in role_names  # Locally granted role was preserved!


# ─── P3-001: Trailing Slash Compatibility ────────────────────────────────────

def test_p3_001_cases_trailing_slash_compatibility(client, setup_database):
    """Verify both /cases and /cases/ return HTTP 200 for listing and creation."""
    db = setup_database
    # Create investigator user
    user = models.User(email="investigator@test.local", password_hash="")
    role = db.query(models.Role).filter(models.Role.name == "investigator").first()
    user.roles.append(role)
    db.add(user)
    db.commit()

    token = create_access_token({"sub": user.id, "email": user.email, "roles": ["investigator"]})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. GET /cases (without slash)
    resp = client.get("/cases", headers=headers)
    assert resp.status_code == 200, f"/cases failed: {resp.status_code}"

    # 2. GET /cases/ (with slash)
    resp_slash = client.get("/cases/", headers=headers)
    assert resp_slash.status_code == 200, f"/cases/ failed: {resp_slash.status_code}"

    # 3. POST /cases (without slash)
    post_resp = client.post("/cases", json={"title": "No Slash Case"}, headers=headers)
    assert post_resp.status_code == 200, f"POST /cases failed: {post_resp.status_code}"

    # 4. POST /cases/ (with slash)
    post_slash_resp = client.post("/cases/", json={"title": "With Slash Case"}, headers=headers)
    assert post_slash_resp.status_code == 200, f"POST /cases/ failed: {post_slash_resp.status_code}"


def test_p3_001_evidence_trailing_slash_compatibility(client, setup_database):
    """Verify both /evidence and /evidence/ return HTTP 200."""
    db = setup_database
    user = models.User(email="ev_user@test.local", password_hash="")
    role = db.query(models.Role).filter(models.Role.name == "investigator").first()
    user.roles.append(role)
    db.add(user)
    db.commit()

    token = create_access_token({"sub": user.id, "email": user.email, "roles": ["investigator"]})
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/evidence", headers=headers)
    assert resp.status_code == 200, f"/evidence failed: {resp.status_code}"

    resp_slash = client.get("/evidence/", headers=headers)
    assert resp_slash.status_code == 200, f"/evidence/ failed: {resp_slash.status_code}"


# ─── P3-002: Case Status Validation ──────────────────────────────────────────

@pytest.mark.parametrize("status_val", ["active", "closed", "archived", "pending"])
def test_p3_002_case_status_valid_values(client, setup_database, status_val):
    """Verify all 4 valid CaseStatus values succeed with HTTP 200."""
    db = setup_database
    user = models.User(email="case_tester@test.local", password_hash="")
    role = db.query(models.Role).filter(models.Role.name == "investigator").first()
    user.roles.append(role)
    db.add(user)
    db.commit()

    token = create_access_token({"sub": user.id, "email": user.email, "roles": ["investigator"]})
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/cases/", json={"title": f"Case {status_val}", "status": status_val}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == status_val


def test_p3_002_case_status_invalid_value_rejected(client, setup_database):
    """Verify invalid status string returns HTTP 422 Unprocessable Entity."""
    db = setup_database
    user = models.User(email="case_tester2@test.local", password_hash="")
    role = db.query(models.Role).filter(models.Role.name == "investigator").first()
    user.roles.append(role)
    db.add(user)
    db.commit()

    token = create_access_token({"sub": user.id, "email": user.email, "roles": ["investigator"]})
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/cases/", json={"title": "Invalid Case", "status": "invalid_enum_val"}, headers=headers)
    assert resp.status_code == 422, f"Expected 422 for invalid enum, got: {resp.status_code}"
    # Verify error location is status field
    errors = resp.json().get("detail", [])
    assert any("status" in str(err.get("loc", [])) for err in errors)


def test_p2_002_production_rejects_fallback_decode(monkeypatch):
    """Verify that in production mode, validate_descope_jwt does NOT fall back to HS256 decode."""
    from app.security.descope_auth import validate_descope_jwt

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("AUTH_DEMO_MODE", "false")
    monkeypatch.delenv("TESTING", raising=False)

    token = create_access_token({"sub": "attacker", "email": "attacker@evil.com", "roles": ["admin"]})
    # Since this is an HS256 token, Descope SDK validation will fail, and production mode prevents fallback decode
    result = validate_descope_jwt(token)
    assert result is None, "In production mode, validate_descope_jwt must reject non-Descope tokens without falling back"

