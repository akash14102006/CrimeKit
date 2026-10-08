import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app import database, models
from backend.app.auth import create_access_token

client = TestClient(app)


@pytest.fixture
def auth_headers():
    db = database.SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == "test_investigator@crimekit.test").first()
        if not user:
            user = models.User(
                id="user-investigator-001",
                email="test_investigator@crimekit.test",
                name="Specialist Investigator",
                is_active=True,
            )
            role = db.query(models.Role).filter(models.Role.name == "investigator").first()
            if not role:
                role = models.Role(name="investigator")
                db.add(role)
                db.commit()
            user.roles.append(role)
            db.add(user)
            db.commit()
            db.refresh(user)
        token = create_access_token({"sub": user.id, "email": user.email, "roles": ["investigator"]})
        return {"Authorization": f"Bearer {token}"}
    finally:
        db.close()


@pytest.fixture
def sample_cases(auth_headers):
    db = database.SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == "test_investigator@crimekit.test").first()
        # Case A: Accessible to investigator
        case_a = db.query(models.Case).filter(models.Case.id == "CASE-TEST-A").first()
        if not case_a:
            case_a = models.Case(
                id="CASE-TEST-A",
                title="Operation Alpha",
                created_by=user.id,
                status="open",
            )
            db.add(case_a)

        # Case B: Belonging to another isolated user
        case_b = db.query(models.Case).filter(models.Case.id == "CASE-TEST-B").first()
        if not case_b:
            case_b = models.Case(
                id="CASE-TEST-B",
                title="Operation Omega",
                created_by="other-user-999",
                status="open",
            )
            db.add(case_b)

        db.commit()
        return {"case_a": "CASE-TEST-A", "case_b": "CASE-TEST-B"}
    finally:
        db.close()


def test_agent_registry_endpoint():
    """Verify GET /api/v1/ai/agents returns all 7 canonical agents."""
    resp = client.get("/api/v1/ai/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 7

    agent_ids = {a["id"] for a in data}
    expected_ids = {
        "case-orchestrator",
        "detective",
        "timeline",
        "geoscope",
        "testimony",
        "evidence-review",
        "report",
    }
    assert agent_ids == expected_ids

    detective = next(a for a in data if a["id"] == "detective")
    assert detective["name"] == "Detective Agent"
    assert "evidence-search" in detective["capabilities"]
    assert len(detective["tools"]) >= 4
    assert len(detective["suggested_questions"]) >= 3


def test_create_session_with_invalid_agent(auth_headers, sample_cases):
    """Verify HTTP 400 when attempting to create a session with an unrecognized agent ID."""
    resp = client.post(
        "/api/v1/ai/sessions",
        json={"case_id": sample_cases["case_a"], "agent_id": "non-existent-agent"},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert "Invalid agent ID" in resp.json()["detail"]


def test_create_session_with_invalid_case(auth_headers):
    """Verify HTTP 404 when case does not exist."""
    resp = client.post(
        "/api/v1/ai/sessions",
        json={"case_id": "CASE-NON-EXISTENT", "agent_id": "detective"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_create_and_list_sessions(auth_headers, sample_cases):
    """Verify session creation and listing filtered by case and agent."""
    case_id = sample_cases["case_a"]
    # Create session for Detective Agent
    resp = client.post(
        "/api/v1/ai/sessions",
        json={"case_id": case_id, "agent_id": "detective", "title": "Detective Alpha Lead"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    det_session = resp.json()
    assert det_session["case_id"] == case_id
    assert det_session["agent_id"] == "detective"
    assert det_session["title"] == "Detective Alpha Lead"
    det_session_id = det_session["id"]

    # Create session for Timeline Agent in same case
    resp_time = client.post(
        "/api/v1/ai/sessions",
        json={"case_id": case_id, "agent_id": "timeline"},
        headers=auth_headers,
    )
    assert resp_time.status_code == 201

    # List all sessions for Case A
    list_resp = client.get(f"/api/v1/ai/sessions?case_id={case_id}", headers=auth_headers)
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert data["total"] >= 2
    session_ids = [s["id"] for s in data["items"]]
    assert det_session_id in session_ids

    # List sessions filtered by agent_id=detective
    filtered_resp = client.get(
        f"/api/v1/ai/sessions?case_id={case_id}&agent_id=detective",
        headers=auth_headers,
    )
    assert filtered_resp.status_code == 200
    filt_data = filtered_resp.json()
    for s in filt_data["items"]:
        assert s["agent_id"] == "detective"


def test_chat_turn_execution_and_persistence(auth_headers, sample_cases):
    """Verify submitting a message returns structured tool executions, findings, and persists history."""
    case_id = sample_cases["case_a"]
    create_resp = client.post(
        "/api/v1/ai/sessions",
        json={"case_id": case_id, "agent_id": "detective"},
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    session_id = create_resp.json()["id"]

    # Post query
    msg_resp = client.post(
        f"/api/v1/ai/sessions/{session_id}/messages",
        json={"message": "Trace phone number connections to Rahul Kumar"},
        headers=auth_headers,
    )
    assert msg_resp.status_code == 200
    turn = msg_resp.json()

    assert turn["session_id"] == session_id
    assert turn["user_message"]["role"] == "user"
    assert turn["user_message"]["content"] == "Trace phone number connections to Rahul Kumar"
    assert turn["message"]["role"] == "assistant"
    assert "Rahul Kumar" in turn["message"]["content"]

    # Structured contracts
    assert len(turn["tool_executions"]) >= 3
    tool_names = [t["tool_name"] for t in turn["tool_executions"]]
    assert "evidence_search" in tool_names
    assert all(t["status"] == "completed" for t in turn["tool_executions"])

    # Findings contract
    assert len(turn["findings"]) >= 1
    finding = turn["findings"][0]
    assert finding["agent_id"] == "detective"
    assert finding["confidence"] > 0.8
    assert finding["status"] in ["supported", "needs_review", "contradicted"]

    # Handoff contract
    assert turn["handoff"] is not None
    assert turn["handoff"]["source_agent"] == "detective"
    assert turn["handoff"]["target_agent"] == "timeline"

    # Verify message persistence via GET messages
    hist_resp = client.get(f"/api/v1/ai/sessions/{session_id}/messages", headers=auth_headers)
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_case_isolation_and_unauthorized_access(sample_cases):
    """Verify unauthorized users or users without access to Case B cannot query or view Case B sessions."""
    # 1. Unauthenticated request should fail
    resp = client.get(f"/api/v1/ai/sessions?case_id={sample_cases['case_a']}")
    assert resp.status_code == 401

    # 2. Authenticate as a restricted viewer who has NO case access
    db = database.SessionLocal()
    try:
        restricted_user = db.query(models.User).filter(models.User.email == "restricted_viewer@crimekit.test").first()
        if not restricted_user:
            restricted_user = models.User(
                id="user-restricted-002",
                email="restricted_viewer@crimekit.test",
                name="Restricted Viewer",
                is_active=True,
            )
            role = db.query(models.Role).filter(models.Role.name == "viewer").first()
            if not role:
                role = models.Role(name="viewer")
                db.add(role)
                db.commit()
            restricted_user.roles.append(role)
            db.add(restricted_user)
            db.commit()
            db.refresh(restricted_user)
        token = create_access_token({"sub": restricted_user.id, "email": restricted_user.email, "roles": ["viewer"]})
        viewer_headers = {"Authorization": f"Bearer {token}"}
    finally:
        db.close()

    # Viewer attempts to list Case B sessions
    resp_restricted = client.get(
        f"/api/v1/ai/sessions?case_id={sample_cases['case_b']}",
        headers=viewer_headers,
    )
    assert resp_restricted.status_code == 403
    assert "Forbidden" in resp_restricted.json()["detail"]
