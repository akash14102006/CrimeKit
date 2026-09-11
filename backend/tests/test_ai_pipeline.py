import io
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app import models
from backend.app.auth import create_access_token


def test_ai_ingest_and_query():
    client = TestClient(app)
    # create user directly in DB
    email = f"ai-{__import__('uuid').uuid4().hex[:6]}@example.com"
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

    # create case
    r = client.post('/cases/', json={'title': 'AI Case', 'description': 'ai'}, headers=headers)
    assert r.status_code == 200
    case_id = r.json()['id']
    data = b'some document content for AI'
    files = {'file': ('doc.txt', io.BytesIO(data), 'text/plain')}
    r = client.post(f'/evidence/upload', data={'case_id': case_id}, files=files, headers=headers)
    assert r.status_code == 200
    ev_id = r.json()['id']

    # ingest evidence into AI pipeline
    r = client.post('/ai/ingest', json={'evidence_id': ev_id}, headers=headers)
    assert r.status_code == 200
    ids = r.json()
    assert 'document_id' in ids

    # query the agent
    r = client.post('/ai/agent/query', json={'query': 'document content', 'top_k': 1}, headers=headers)
    assert r.status_code == 200
    hits = r.json()['hits']
    assert isinstance(hits, list)
