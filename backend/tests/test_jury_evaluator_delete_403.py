"""Regression tests proving jury_evaluator DELETE /cases/{id} and DELETE /evidence/{id} return 204 without 403 Forbidden.

Specifically tests:
1. A legacy user with 'viewer' role in database is synchronized to 'jury_evaluator'.
2. The authenticated user can CREATE, READ, UPDATE, and DELETE Cases.
3. The authenticated user can CREATE/UPLOAD, READ, UPDATE (custody), and DELETE Evidence.
4. Both no-slash and trailing-slash DELETE endpoints return 204 No Content.
5. Proves 403 Forbidden is completely eliminated.
"""

import io
import uuid
import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app import models, crud
from backend.app.auth import create_access_token


@pytest.fixture(autouse=True)
def ensure_testing_env(monkeypatch):
    """Ensure test environment variables are active."""
    monkeypatch.setenv("TESTING", "1")
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("AUTH_DEMO_MODE", "true")


def test_legacy_viewer_upgraded_and_can_delete_case_and_evidence():
    """Prove an existing user with legacy 'viewer' role in DB can perform full CRUD including DELETE."""
    client = TestClient(app)
    db = SessionLocal()

    # 1. Simulate legacy user previously stored with 'viewer' role
    unique_id = uuid.uuid4().hex[:8]
    email = f"evaluator-{unique_id}@hackathon.test"

    user = models.User(email=email, password_hash="", is_active=True)
    db.add(user)

    viewer_role = db.query(models.Role).filter(models.Role.name == "viewer").first()
    if not viewer_role:
        viewer_role = models.Role(name="viewer", description="Legacy viewer role")
        db.add(viewer_role)
        db.flush()

    user.roles.append(viewer_role)
    db.commit()
    db.refresh(user)

    user_id = user.id
    db.close()

    # Create session token (simulating Descope session with viewer or empty roles)
    token = create_access_token(
        data={"sub": user_id, "email": email, "roles": ["viewer"]},
        expires_delta=timedelta(hours=2),
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 2. GET /auth/me — verify user is recognized as jury_evaluator
    r_me = client.get("/auth/me", headers=headers)
    assert r_me.status_code == 200, f"GET /auth/me failed: {r_me.text}"
    me_data = r_me.json()
    assert me_data["role"] == "jury_evaluator", f"Expected jury_evaluator, got {me_data['role']}"
    assert "case:delete" in me_data["permissions"]
    assert "evidence:delete" in me_data["permissions"]

    # Verify DB was updated
    db = SessionLocal()
    refreshed_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_role_names = [r.name for r in refreshed_user.roles]
    assert "jury_evaluator" in db_role_names, f"DB roles missing jury_evaluator: {db_role_names}"
    db.close()

    # 3. CASE CRUD LIFECYCLE
    # CREATE Case
    r_case_create = client.post("/cases/", json={"title": f"CRUD Case {unique_id}", "description": "Testing delete"}, headers=headers)
    assert r_case_create.status_code == 200, f"Case CREATE failed: {r_case_create.text}"
    case_id = r_case_create.json()["id"]

    # READ Case
    r_case_read = client.get(f"/cases/{case_id}", headers=headers)
    assert r_case_read.status_code == 200, f"Case READ failed: {r_case_read.text}"

    # UPDATE Case
    r_case_update = client.patch(f"/cases/{case_id}", json={"title": f"Updated Case {unique_id}"}, headers=headers)
    assert r_case_update.status_code == 200, f"Case UPDATE failed: {r_case_update.text}"

    # 4. EVIDENCE CRUD LIFECYCLE
    # CREATE / UPLOAD Evidence
    test_file_content = b"forensic disk evidence block 0xDEADBEEF"
    files = {"file": ("disk_image.raw", io.BytesIO(test_file_content), "application/octet-stream")}
    r_ev_upload = client.post("/evidence/upload", data={"case_id": case_id}, files=files, headers=headers)
    assert r_ev_upload.status_code == 200, f"Evidence UPLOAD failed: {r_ev_upload.text}"
    evidence_id = r_ev_upload.json()["id"]

    # READ Evidence
    r_ev_read = client.get(f"/evidence/{evidence_id}", headers=headers)
    assert r_ev_read.status_code == 200, f"Evidence READ failed: {r_ev_read.text}"

    # UPDATE Evidence (Custody append)
    r_ev_update = client.post(
        f"/evidence/{evidence_id}/custody",
        json={"action": "transfer", "location": "Lab Vault A", "notes": "Jury evaluation verification"},
        headers=headers,
    )
    assert r_ev_update.status_code == 200, f"Evidence UPDATE failed: {r_ev_update.text}"

    # 5. DELETE Evidence — MUST return 204 No Content (NOT 403 Forbidden)
    r_ev_delete = client.delete(f"/evidence/{evidence_id}", headers=headers)
    assert r_ev_delete.status_code == 204, f"Evidence DELETE returned {r_ev_delete.status_code} (expected 204): {r_ev_delete.text}"

    # Verify Evidence is deleted
    r_ev_read_after = client.get(f"/evidence/{evidence_id}", headers=headers)
    assert r_ev_read_after.status_code == 404

    # 6. DELETE Case — MUST return 204 No Content (NOT 403 Forbidden)
    r_case_delete = client.delete(f"/cases/{case_id}", headers=headers)
    assert r_case_delete.status_code == 204, f"Case DELETE returned {r_case_delete.status_code} (expected 204): {r_case_delete.text}"

    # Verify Case is deleted
    r_case_read_after = client.get(f"/cases/{case_id}", headers=headers)
    assert r_case_read_after.status_code == 404


def test_trailing_slash_delete_cases_and_evidence():
    """Prove DELETE with trailing slashes works seamlessly."""
    client = TestClient(app)
    unique_id = uuid.uuid4().hex[:8]
    email = f"slash-judge-{unique_id}@hackathon.test"

    token = create_access_token(
        data={"sub": f"user-{unique_id}", "email": email, "roles": ["jury_evaluator"]},
        expires_delta=timedelta(hours=1),
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Create Case
    r_case = client.post("/cases/", json={"title": f"Slash Case {unique_id}"}, headers=headers)
    assert r_case.status_code == 200
    case_id = r_case.json()["id"]

    # Create Evidence
    files = {"file": ("slash_test.txt", io.BytesIO(b"data"), "text/plain")}
    r_ev = client.post("/evidence/upload", data={"case_id": case_id}, files=files, headers=headers)
    assert r_ev.status_code == 200
    evidence_id = r_ev.json()["id"]

    # DELETE Evidence with trailing slash
    r_ev_del = client.delete(f"/evidence/{evidence_id}/", headers=headers)
    assert r_ev_del.status_code == 204

    # DELETE Case with trailing slash
    r_case_del = client.delete(f"/cases/{case_id}/", headers=headers)
    assert r_case_del.status_code == 204
