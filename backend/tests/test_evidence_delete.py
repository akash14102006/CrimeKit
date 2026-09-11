import io
import hashlib
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app import models
from backend.app.auth import create_access_token

def test_evidence_delete_end_to_end():
    client = TestClient(app)

    # 1. Create admin user in DB
    email = f"admin-{__import__('uuid').uuid4().hex[:6]}@example.com"
    db = SessionLocal()
    user = models.User(email=email, password_hash="")
    db.add(user)
    role = db.query(models.Role).filter(models.Role.name == "admin").first()
    if role:
        user.roles.append(role)
    db.commit()
    db.refresh(user)
    access = create_access_token({"sub": user.id})
    user_id = user.id
    db.close()

    headers = {'Authorization': f'Bearer {access}'}

    # 2. Create case and upload evidence
    r = client.post('/cases/', json={'title': 'Delete Test Case'}, headers=headers)
    assert r.status_code == 200
    case_id = r.json()['id']

    file_bytes = b'file-content-to-be-deleted'
    sha = hashlib.sha256(file_bytes).hexdigest()
    files = {'file': ('test_delete.txt', io.BytesIO(file_bytes), 'text/plain')}
    r = client.post(f'/evidence/upload', data={'case_id': case_id}, files=files, headers=headers)
    assert r.status_code == 200
    ev_id = r.json()['id']

    # 3. Call DELETE /evidence/{ev_id}
    r = client.delete(f'/evidence/{ev_id}', headers=headers)
    assert r.status_code == 204

    # 4. Verify Evidence row is deleted
    db = SessionLocal()
    try:
        deleted = db.query(models.Evidence).filter(models.Evidence.id == ev_id).first()
        assert deleted is None, "Evidence DB row should be deleted"

        # 5. Verify Chain of Custody 'deleted' audit entry exists
        coc = db.query(models.ChainOfCustody).filter(
            models.ChainOfCustody.evidence_id == ev_id,
            models.ChainOfCustody.action == "deleted"
        ).first()
        assert coc is not None, "Chain of custody deleted entry should exist"
        assert coc.actor_id == user_id

        # 6. Verify AuditLog entry exists
        audit = db.query(models.AuditLog).filter(
            models.AuditLog.action == "evidence.delete",
            models.AuditLog.target_id == ev_id
        ).first()
        assert audit is not None, "AuditLog for evidence.delete should exist"
    finally:
        db.close()
