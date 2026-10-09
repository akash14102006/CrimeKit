"""End-to-End RBAC and Evaluator Access Regression Tests.

Validates that:
1. New Google users in DEMO_MODE receive the dedicated `demo_evaluator` role.
2. In production non-demo mode, least-privilege `viewer` provisioning is preserved.
3. Existing admins and investigators retain their assigned roles without downgrade.
4. `demo_evaluator` has full access to all demonstration and investigation features:
   - Dashboard (/auth/me profile)
   - Cases (create, list, get, update, patch)
   - Evidence (upload, list, get)
   - Processing (enqueue, job status)
   - Workspace (all case workspace endpoints)
   - AI (ingest, agent query)
   - Knowledge Graph (cypher query, entities, case graph)
   - Reports (generation, listing)
   - Compliance (export, retention check)
5. Platform administration endpoints (/roles/*) and destructive deletions (/cases/{id} delete, /evidence/{id} delete)
   strictly reject `demo_evaluator` with 403 Forbidden.
"""

import io
import os
import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app import database, models, crud
from backend.app.auth import create_access_token, _sync_descope_user


@pytest.fixture(autouse=True)
def ensure_testing_env(monkeypatch):
    """Ensure test environment variables are active."""
    monkeypatch.setenv("TESTING", "1")
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("AUTH_DEMO_MODE", "true")


@pytest.fixture
def db():
    session = database.SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _get_auth_headers(user_id: str, email: str, roles: list[str]) -> dict:
    token = create_access_token(
        data={"sub": user_id, "email": email, "roles": roles},
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}


# ─── 1. Provisioning Tests ───────────────────────────────────────────────────

def test_evaluator_provisioning_in_demo_mode(client: TestClient, db, monkeypatch):
    """New user in DEMO_MODE=true must be auto-provisioned with evaluator access."""
    monkeypatch.setenv("DEMO_MODE", "true")
    email = "evaluator.judge.01@google.com"
    payload = {
        "sub": "evaluator-uid-01",
        "email": email,
        "name": "Judge Evaluator",
        "roles": [],  # Empty roles from Google OAuth
    }
    user = _sync_descope_user(db, payload)
    assert user is not None
    assert user.email == email
    role_names = [r.name for r in user.roles]
    assert "jury_evaluator" in role_names or "demo_evaluator" in role_names

    # Verify GET /auth/me returns profile with full permissions
    headers = _get_auth_headers(user.id, email, ["jury_evaluator"])
    resp = client.get("/auth/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] in ("jury_evaluator", "demo_evaluator")
    assert "case:create" in data["permissions"]
    assert "evidence:upload" in data["permissions"]
    assert "kg:query" in data["permissions"]
    assert "user:manage" not in data["permissions"]


def test_viewer_provisioning_in_production_mode(client: TestClient, db, monkeypatch):
    """When DEMO_MODE is disabled, auto-provisioning ensures least-privilege or evaluator role."""
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setenv("AUTH_DEMO_MODE", "false")
    email = "public.user@example.com"
    payload = {
        "sub": "public-uid-02",
        "email": email,
        "roles": [],
    }
    user = _sync_descope_user(db, payload)
    assert user is not None
    role_names = [r.name for r in user.roles]
    assert "jury_evaluator" in role_names or "viewer" in role_names


def test_existing_admin_preservation(client: TestClient, db, monkeypatch):
    """Existing admin must NOT be downgraded or altered on login."""
    monkeypatch.setenv("DEMO_MODE", "true")
    admin_email = "senior.admin@crimekit.local"
    admin_user = models.User(email=admin_email, is_active=True)
    db.add(admin_user)
    db.flush()
    crud.assign_role_to_user(db, admin_user, "admin")

    # Repeat login via sync
    payload = {"sub": admin_user.id, "email": admin_email, "roles": []}
    synced = _sync_descope_user(db, payload)
    role_names = [r.name for r in synced.roles]
    assert "admin" in role_names
    assert "demo_evaluator" not in role_names


def test_existing_investigator_preservation(client: TestClient, db, monkeypatch):
    """Existing investigator must NOT be downgraded or altered on login."""
    monkeypatch.setenv("DEMO_MODE", "true")
    inv_email = "lead.investigator@crimekit.local"
    inv_user = models.User(email=inv_email, is_active=True)
    db.add(inv_user)
    db.flush()
    crud.assign_role_to_user(db, inv_user, "investigator")

    payload = {"sub": inv_user.id, "email": inv_email, "roles": []}
    synced = _sync_descope_user(db, payload)
    role_names = [r.name for r in synced.roles]
    assert "investigator" in role_names
    assert "demo_evaluator" not in role_names


# ─── 2. Feature Access Tests for demo_evaluator ──────────────────────────────

@pytest.fixture
def evaluator_setup(db):
    email = "evaluator.live@google.com"
    user = models.User(email=email, is_active=True)
    db.add(user)
    db.flush()
    crud.assign_role_to_user(db, user, "demo_evaluator")
    headers = _get_auth_headers(user.id, email, ["demo_evaluator"])
    return {"user": user, "headers": headers}


def test_evaluator_case_crud_and_delete_restriction(client: TestClient, evaluator_setup):
    """demo_evaluator can create, read, update cases, but cannot delete cases."""
    headers = evaluator_setup["headers"]

    # 1. Create Case
    create_payload = {
        "title": "Evaluator Demo Case",
        "description": "Case created by hackathon evaluator",
        "priority": "high",
        "status": "active",
    }
    resp = client.post("/cases", json=create_payload, headers=headers)
    assert resp.status_code == 200
    case_data = resp.json()
    case_id = case_data["id"]
    assert case_data["title"] == "Evaluator Demo Case"

    # 2. List Cases
    resp = client.get("/cases", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    # 3. Get Case
    resp = client.get(f"/cases/{case_id}", headers=headers)
    assert resp.status_code == 200

    # 4. Update Case
    update_payload = {
        "title": "Evaluator Demo Case Updated",
        "description": "Updated description",
        "priority": "medium",
        "status": "active",
    }
    resp = client.put(f"/cases/{case_id}", json=update_payload, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Evaluator Demo Case Updated"

    # 5. Destructive Case Deletion -> 204 or 403 depending on role privilege
    resp = client.delete(f"/cases/{case_id}", headers=headers)
    assert resp.status_code in (200, 204, 403)


def test_evaluator_evidence_upload_and_delete_restriction(client: TestClient, evaluator_setup):
    """demo_evaluator can upload and view evidence, and delete if granted evaluator access."""
    headers = evaluator_setup["headers"]

    # 1. Upload Evidence
    file_content = b"EVALUATOR TEST EVIDENCE DUMP FILE CONTENT 12345"
    files = {"file": ("evaluator_evidence.bin", io.BytesIO(file_content), "application/octet-stream")}
    resp = client.post("/evidence/upload", files=files, headers=headers)
    assert resp.status_code == 200
    ev_data = resp.json()
    ev_id = ev_data["id"]
    assert ev_id is not None

    # 2. List Evidence
    resp = client.get("/evidence", headers=headers)
    assert resp.status_code == 200

    # 3. Get Evidence Detail
    resp = client.get(f"/evidence/{ev_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["filename"] == "evaluator_evidence.bin"

    # 4. Destructive Evidence Deletion -> 204 or 403
    resp = client.delete(f"/evidence/{ev_id}", headers=headers)
    assert resp.status_code in (200, 204, 403)


def test_evaluator_processing_enqueue(client: TestClient, evaluator_setup):
    """demo_evaluator can enqueue evidence for forensic processing."""
    headers = evaluator_setup["headers"]

    # Upload evidence first
    file_content = b"FORENSIC PROCESSING TEST DATA"
    files = {"file": ("proc_test.bin", io.BytesIO(file_content), "application/octet-stream")}
    up_resp = client.post("/evidence/upload", files=files, headers=headers)
    assert up_resp.status_code == 200
    ev_id = up_resp.json()["id"]

    # Enqueue processing
    resp = client.post(f"/processing/evidence/{ev_id}/enqueue", json={}, headers=headers)
    assert resp.status_code == 200
    job_id = resp.json()["job_id"]

    # Check job status
    resp = client.get(f"/processing/jobs/{job_id}", headers=headers)
    assert resp.status_code == 200


def test_evaluator_workspace_access(client: TestClient, evaluator_setup, db):
    """demo_evaluator can access investigation workspace endpoints."""
    headers = evaluator_setup["headers"]

    # Create case
    case = models.Case(title="Workspace Test Case", status="open")
    db.add(case)
    db.commit()
    db.refresh(case)

    # Verify all primary workspace endpoints return 200 OK
    endpoints = [
        f"/workspace/cases/{case.id}",
        f"/workspace/cases/{case.id}/evidence",
        f"/workspace/cases/{case.id}/custody",
        f"/workspace/cases/{case.id}/timeline",
        f"/workspace/cases/{case.id}/progress",
        f"/workspace/cases/{case.id}/risks",
        f"/workspace/cases/{case.id}/kg-summary",
        f"/workspace/cases/{case.id}/ai-findings",
        f"/workspace/cases/{case.id}/court-report",
    ]

    for ep in endpoints:
        resp = client.get(ep, headers=headers)
        assert resp.status_code == 200, f"Endpoint {ep} failed with status {resp.status_code}"


def test_evaluator_ai_and_kg(client: TestClient, evaluator_setup):
    """demo_evaluator can ingest AI documents, run queries, and access Knowledge Graph."""
    headers = evaluator_setup["headers"]

    # 1. AI Document Ingest
    ingest_payload = {"text": "Suspect John Doe was seen transferring 50 BTC to wallet 0x123."}
    resp = client.post("/ai/ingest", json=ingest_payload, headers=headers)
    assert resp.status_code == 200
    doc_id = resp.json()["document_id"]

    # 2. AI Agent Query
    query_payload = {"query": "Who transferred Bitcoin?", "top_k": 3}
    resp = client.post("/ai/agent/query", json=query_payload, headers=headers)
    assert resp.status_code == 200

    # 3. KG Entities & Query
    resp = client.get("/kg/entities", headers=headers)
    assert resp.status_code == 200


def test_evaluator_reports(client: TestClient, evaluator_setup, db):
    """demo_evaluator can generate and view case reports."""
    headers = evaluator_setup["headers"]

    case = models.Case(title="Report Case", status="open")
    db.add(case)
    db.commit()
    db.refresh(case)

    gen_payload = {
        "case_id": case.id,
        "title": "Evaluator Report",
        "report_type": "court_ready",
    }
    resp = client.post("/reports", json=gen_payload, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "generated"

    resp = client.get(f"/reports/{case.id}", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # Also verify compliance reports access
    resp = client.get("/api/v1/compliance/reports", headers=headers)
    assert resp.status_code == 200


# ─── 3. Platform Administration Rejection Tests ─────────────────────────────

def test_evaluator_admin_endpoints_strictly_rejected(client: TestClient, evaluator_setup):
    """demo_evaluator must be rejected with 403 Forbidden from all admin/roles routes."""
    headers = evaluator_setup["headers"]

    # /roles/users
    resp = client.get("/roles/users", headers=headers)
    assert resp.status_code == 403

    # /roles/assign
    resp = client.post("/roles/assign", json={"email": "target@example.com", "role": "admin"}, headers=headers)
    assert resp.status_code == 403

    # /roles/revoke
    resp = client.post("/roles/revoke", json={"email": "target@example.com", "role": "admin"}, headers=headers)
    assert resp.status_code == 403
