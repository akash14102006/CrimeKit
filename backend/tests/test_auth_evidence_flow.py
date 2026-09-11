import io
import hashlib
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app import models
from backend.app.auth import create_access_token


def test_evidence_upload_and_verify(tmp_path):
    client = TestClient(app)

    import uuid
    email = f"tester-{uuid.uuid4().hex[:8]}@example.com"

    # Create user directly in DB
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

    # Evidence upload
    file_bytes = b"hello evidence"
    sha = hashlib.sha256(file_bytes).hexdigest()
    files = {'file': ('evidence.txt', io.BytesIO(file_bytes), 'text/plain')}
    headers = {'Authorization': f'Bearer {access}'}
    r = client.post('/evidence/upload', files=files, headers=headers)
    assert r.status_code == 200
    resp = r.json()
    assert resp['sha256'] == sha
    assert resp['size'] == len(file_bytes)

    # Verify DB record exists
    from sqlalchemy import text
    db = SessionLocal()
    try:
        ev = db.execute(text("SELECT id FROM evidence WHERE sha256 = :s"), {'s': sha}).fetchone()
        assert ev is not None
    finally:
        db.close()
