import io
import time
import hashlib
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app import models, crud
from backend.app.auth import create_access_token


def test_processing_queue_and_results():
    client = TestClient(app)

    # create user directly in DB and upload evidence
    email = f"user-{__import__('uuid').uuid4().hex[:6]}@example.com"
    db = SessionLocal()
    user = models.User(email=email, password_hash="")
    db.add(user)
    role = db.query(models.Role).filter(models.Role.name == "investigator").first()
    if role:
        user.roles.append(role)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.id})
    db.close()
    headers = {'Authorization': f'Bearer {token}'}

    r = client.post('/cases/', json={'title': 'ProcCase', 'description': 'proc'}, headers=headers)
    assert r.status_code == 200
    case_id = r.json()['id']

    data = b'proc-sample'
    files = {'file': ('sample.bin', io.BytesIO(data), 'application/octet-stream')}
    r = client.post(f'/evidence/upload', data={'case_id': case_id}, files=files, headers=headers)
    assert r.status_code == 200
    ev_id = r.json()['id']

    # enqueue processing for hashes and mime
    r = client.post(f'/processing/evidence/{ev_id}/enqueue', json={'processors': ['hashes', 'mime']}, headers=headers)
    assert r.status_code == 200
    job_id = r.json()['job_id']

    # poll for completion
    completed = False
    for _ in range(20):
        r = client.get(f'/processing/jobs/{job_id}', headers=headers)
        assert r.status_code == 200
        status = r.json()['status']
        if status == 'completed':
            completed = True
            break
        time.sleep(0.2)
    assert completed

    # verify forensic results in DB
    db = SessionLocal()
    try:
        rows = db.query(models.ForensicResult).filter(models.ForensicResult.evidence_id == ev_id).all()
        assert any(r.processor == 'hashes' for r in rows)
        assert any(r.processor == 'mime' for r in rows)
    finally:
        db.close()
