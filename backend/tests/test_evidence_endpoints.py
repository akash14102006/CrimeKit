import io
import hashlib
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app import models
from backend.app.auth import create_access_token


def test_evidence_get_and_list(tmp_path):
    client = TestClient(app)

    # create user directly in DB
    email = f"user-{__import__('uuid').uuid4().hex[:6]}@example.com"
    db = SessionLocal()
    user = models.User(email=email, password_hash="")
    db.add(user)
    role = db.query(models.Role).filter(models.Role.name == "investigator").first()
    if role:
        user.roles.append(role)
    db.commit()
    db.refresh(user)
    access = create_access_token({"sub": user.id})
    db.close()

    # create a case
    headers = {'Authorization': f'Bearer {access}'}
    r = client.post('/cases/', json={'title': 'Case A', 'description': 'desc'}, headers=headers)
    assert r.status_code == 200
    case = r.json()
    case_id = case['id']

    # upload evidence linked to case
    file_bytes = b'evidence-content'
    sha = hashlib.sha256(file_bytes).hexdigest()
    files = {'file': ('e.txt', io.BytesIO(file_bytes), 'text/plain')}
    r = client.post(f'/evidence/upload', data={'case_id': case_id}, files=files, headers=headers)
    assert r.status_code == 200
    ev = r.json()
    ev_id = ev['id']

    # get evidence by id
    r = client.get(f'/evidence/{ev_id}', headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data['sha256'] == sha
    assert data['case_id'] == case_id

    # list evidence for case
    r = client.get(f'/evidence/case/{case_id}', headers=headers)
    assert r.status_code == 200
    arr = r.json()
    assert any(item['id'] == ev_id for item in arr)

    # verify audit log entry exists
    from sqlalchemy import text
    db = SessionLocal()
    try:
        row = db.execute(text("SELECT id FROM audit_logs WHERE action = 'evidence.view' AND target_id = :tid"), {'tid': ev_id}).fetchone()
        assert row is not None
    finally:
        db.close()
