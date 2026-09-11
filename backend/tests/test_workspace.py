import io
import hashlib
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app import models, crud
from backend.app.auth import create_access_token


def _create_user(email, role_name=None):
    """Helper to create a user in DB and return (user, token)."""
    db = SessionLocal()
    user = models.User(email=email, password_hash="")
    db.add(user)
    db.flush()
    if role_name:
        role = db.query(models.Role).filter(models.Role.name == role_name).first()
        if role:
            user.roles.append(role)
    else:
        # Default to viewer role (required after RC-4 fix: no-role users get 403)
        role = db.query(models.Role).filter(models.Role.name == "viewer").first()
        if role:
            user.roles.append(role)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.id})
    db.close()
    return user, token


def test_workspace_full(tmp_path):
    client = TestClient(app)

    # Create investigator directly in DB
    email_i = f"inv-{__import__('uuid').uuid4().hex[:6]}@example.com"
    inv_user, tok_i = _create_user(email_i, "investigator")
    headers_i = {'Authorization': f'Bearer {tok_i}'}

    # Create case
    r = client.post('/cases/', json={'title': 'Workspace Case', 'description': 'ws'}, headers=headers_i)
    assert r.status_code == 200
    case_id = r.json()['id']

    # Upload multiple evidence files
    ev_ids = []
    for i in range(3):
        data = f'evidence content {i}'.encode()
        sha = hashlib.sha256(data).hexdigest()
        files = {'file': (f'ev{i}.txt', io.BytesIO(data), 'text/plain')}
        r = client.post(f'/evidence/upload', data={'case_id': case_id}, files=files, headers=headers_i)
        assert r.status_code == 200
        ev_ids.append(r.json()['id'])

    # Add custody entry for one evidence
    payload = {
        'action': 'transfer',
        'previous_owner': None,
        'new_owner': inv_user.id,
        'location': 'Lab A',
        'notes': 'Initial intake',
        'signature': 'sig-1'
    }
    r = client.post(f'/evidence/{ev_ids[0]}/custody', json=payload, headers=headers_i)
    assert r.status_code == 200

    # Enqueue processing for one evidence
    r = client.post(f'/processing/evidence/{ev_ids[0]}/enqueue', json={'processors': ['hashes', 'mime']}, headers=headers_i)
    assert r.status_code == 200
    job_id = r.json()['job_id']

    # Wait for processing
    import time
    for _ in range(20):
        r = client.get(f'/processing/jobs/{job_id}', headers=headers_i)
        if r.json()['status'] == 'completed':
            break
        time.sleep(0.2)

    # Ingest into AI pipeline
    r = client.post('/ai/ingest', json={'evidence_id': ev_ids[0]}, headers=headers_i)
    assert r.status_code == 200

    # Ingest into KG
    r = client.post(f'/kg/ingest/evidence/{ev_ids[0]}', headers=headers_i)
    # Neo4j not available in tests, accept 503
    assert r.status_code in (200, 503)

    # Get full workspace
    r = client.get(f'/workspace/cases/{case_id}', headers=headers_i)
    assert r.status_code == 200
    ws = r.json()

    # Verify structure
    assert ws['case']['id'] == case_id
    assert len(ws['evidence']) == 3
    assert ws['progress']['evidence_total'] == 3
    assert ws['progress']['forensic_jobs_total'] >= 1
    assert ws['progress']['forensic_jobs_completed'] >= 1
    assert 'risk_indicators' in ws
    assert 'court_report' in ws

    # Test sub-endpoints
    for endpoint, key in [
        ('evidence', 'evidence'),
        ('custody', 'custody'),
        ('timeline', 'timeline'),
        ('progress', 'progress'),
        ('risks', 'risk_indicators'),
        ('kg-summary', 'knowledge_graph'),
        ('ai-findings', 'ai_findings'),
        ('court-report', 'court_report'),
    ]:
        r = client.get(f'/workspace/cases/{case_id}/{endpoint}', headers=headers_i)
        assert r.status_code == 200, f"Failed on {endpoint}: {r.text}"


def test_workspace_unauthorized_workspace(tmp_path):
    """Test that non-investigator/non-owner cannot access workspace."""
    client = TestClient(app)

    # Owner creates case (no special role)
    email_o = f"owner-{__import__('uuid').uuid4().hex[:6]}@example.com"
    owner_user, tok_o = _create_user(email_o)
    headers_o = {'Authorization': f'Bearer {tok_o}'}

    r = client.post('/cases/', json={'title': 'Private', 'description': 'p'}, headers=headers_o)
    case_id = r.json()['id']

    # Upload evidence
    files = {'file': ('e.txt', io.BytesIO(b'data'), 'text/plain')}
    r = client.post(f'/evidence/upload', data={'case_id': case_id}, files=files, headers=headers_o)
    ev_id = r.json()['id']

    # Another user tries to access
    email_u = f"user-{__import__('uuid').uuid4().hex[:6]}@example.com"
    _, tok_u = _create_user(email_u)
    headers_u = {'Authorization': f'Bearer {tok_u}'}

    # Should be forbidden (not owner, not investigator, not admin)
    r = client.get(f'/workspace/cases/{case_id}', headers=headers_u)
    assert r.status_code == 403
