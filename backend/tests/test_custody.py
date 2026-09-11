import io
import hashlib
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app import models, crud
from backend.app.auth import create_access_token


def test_custody_append_and_read():
    client = TestClient(app)

    # create uploader directly in DB with viewer role (cannot append custody)
    email_u = f"uploader-{__import__('uuid').uuid4().hex[:6]}@example.com"
    db = SessionLocal()
    user_u = models.User(email=email_u, password_hash="")
    db.add(user_u)
    db.flush()
    role_viewer = db.query(models.Role).filter(models.Role.name == "viewer").first()
    if role_viewer:
        user_u.roles.append(role_viewer)
    db.commit()
    db.refresh(user_u)
    tok_u = create_access_token({"sub": user_u.id})
    db.close()

    headers_u = {'Authorization': f'Bearer {tok_u}'}

    # create case & upload evidence
    r = client.post('/cases/', json={'title': 'Case C', 'description': 'desc'}, headers=headers_u)
    assert r.status_code == 200
    case_id = r.json()['id']

    file_bytes = b'forensic-data'
    sha = hashlib.sha256(file_bytes).hexdigest()
    files = {'file': ('f.bin', io.BytesIO(file_bytes), 'application/octet-stream')}
    r = client.post(f'/evidence/upload', data={'case_id': case_id}, files=files, headers=headers_u)
    assert r.status_code == 200
    ev_id = r.json()['id']

    # create investigator directly in DB with investigator role
    email_i = f"invest-{__import__('uuid').uuid4().hex[:6]}@example.com"
    db = SessionLocal()
    inv_user = models.User(email=email_i, password_hash="")
    db.add(inv_user)
    role_inv = db.query(models.Role).filter(models.Role.name == "investigator").first()
    if role_inv:
        inv_user.roles.append(role_inv)
    db.commit()
    db.refresh(inv_user)
    tok_i = create_access_token({"sub": inv_user.id})
    db.close()
    headers_i = {'Authorization': f'Bearer {tok_i}'}

    # investigator appends custody entry
    payload = {
        'action': 'transfer',
        'previous_owner': None,
        'new_owner': inv_user.id,
        'location': 'Lab1',
        'notes': 'Transferred to lab for analysis',
        'signature': 'sig-xyz',
    }
    r = client.post(f'/evidence/{ev_id}/custody', json=payload, headers=headers_i)
    assert r.status_code == 200
    res = r.json()
    assert res['integrity_ok'] is True
    custody_id = res['custody_id']

    # normal user without role cannot append custody
    r = client.post(f'/evidence/{ev_id}/custody', json=payload, headers=headers_u)
    assert r.status_code == 403

    # get custody as investigator
    r = client.get(f'/evidence/{ev_id}/custody', headers=headers_i)
    assert r.status_code == 200
    data = r.json()
    assert data['integrity_ok'] is True
    assert any(h['id'] == custody_id and h['action'] == 'transfer' for h in data['history'])

    # tamper file to test integrity failure
    db = SessionLocal()
    try:
        ev = db.query(models.Evidence).filter(models.Evidence.id == ev_id).first()
        with open(ev.storage_path, 'wb') as f:
            f.write(b'corrupted')
    finally:
        db.close()

    r = client.get(f'/evidence/{ev_id}/custody', headers=headers_i)
    assert r.status_code == 200
    assert r.json()['integrity_ok'] is False
