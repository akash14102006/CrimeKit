import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal, init_db
from backend.app import models
from backend.app.auth import create_access_token


@pytest.fixture(autouse=True)
def setup_database():
    init_db()
    yield


def test_fresh_client_unauthenticated_requests():
    client = TestClient(app)
    
    # Fresh browser with no session/token: all protected routes return 401
    r_me = client.get("/auth/me")
    assert r_me.status_code == 401
    assert "detail" in r_me.json()

    r_cases = client.get("/cases/?page=1&limit=100")
    assert r_cases.status_code == 401

    r_evidence = client.get("/evidence/?page=1&limit=100")
    assert r_evidence.status_code == 401

    r_queue = client.get("/processing/queue/stats")
    assert r_queue.status_code == 401


def test_explicit_login_and_protected_access():
    client = TestClient(app)

    # Explicit login via /auth/login
    login_resp = client.post("/auth/login", json={"email": "officer@crimekit.local", "password": ""})
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "officer@crimekit.local"

    access_token = data["access_token"]
    refresh_token = data["refresh_token"]

    # Verify /auth/me with acquired token
    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "officer@crimekit.local"

    # Verify protected access to cases and evidence
    cases_resp = client.get("/cases/?page=1&limit=100", headers={"Authorization": f"Bearer {access_token}"})
    assert cases_resp.status_code == 200

    evidence_resp = client.get("/evidence/?page=1&limit=100", headers={"Authorization": f"Bearer {access_token}"})
    assert evidence_resp.status_code == 200


def test_session_refresh_flow():
    client = TestClient(app)

    login_resp = client.post("/auth/login", json={"email": "analyst@crimekit.local", "password": ""})
    assert login_resp.status_code == 200
    data = login_resp.json()
    refresh_token = data["refresh_token"]
    old_access = data["access_token"]

    # Refresh the session
    ref_resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_resp.status_code == 200
    ref_data = ref_resp.json()
    assert "access_token" in ref_data
    new_access = ref_data["access_token"]

    # Verify new access token works
    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {new_access}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "analyst@crimekit.local"


def test_refresh_token_rejection():
    client = TestClient(app)

    # 1. Missing refresh token
    r1 = client.post("/auth/refresh", json={})
    assert r1.status_code == 422

    # 2. Invalid/tampered refresh token
    r2 = client.post("/auth/refresh", json={"refresh_token": "invalid.jwt.token"})
    assert r2.status_code == 401

    # 3. Access token provided instead of refresh token
    access = create_access_token({"sub": "user-123", "email": "test@test.local"})
    r3 = client.post("/auth/refresh", json={"refresh_token": access})
    assert r3.status_code == 401
    assert "Invalid token type" in r3.json()["detail"]

    # 4. Expired token
    expired = create_access_token({"sub": "user-123", "type": "refresh"}, expires_delta=timedelta(seconds=-10))
    r4 = client.post("/auth/refresh", json={"refresh_token": expired})
    assert r4.status_code == 401


def test_multiple_simultaneous_401s():
    client = TestClient(app)
    bad_headers = {"Authorization": "Bearer totally-fake-token"}

    # Simulate multiple concurrent queries with an invalid token
    endpoints = [
        "/auth/me",
        "/cases/?page=1&limit=100",
        "/evidence/?page=1&limit=100",
        "/processing/queue/stats",
    ]
    for ep in endpoints:
        resp = client.get(ep, headers=bad_headers)
        assert resp.status_code == 401
