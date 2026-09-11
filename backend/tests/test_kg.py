import os
from backend.app.database import init_db, SessionLocal
from backend.app import models
from backend.app.auth import create_access_token


def _make_investigator_token():
    db = SessionLocal()
    try:
        user = models.User(email=f"kg-test-{__import__('uuid').uuid4().hex[:6]}@example.com", password_hash="")
        db.add(user)
        db.flush()
        role = db.query(models.Role).filter(models.Role.name == "investigator").first()
        if role:
            user.roles.append(role)
        db.commit()
        return create_access_token({"sub": user.id, "roles": ["investigator"]})
    finally:
        db.close()


def test_extractors_simple():
    from backend.app.kg import extract_entities, extract_relationships, extract_timeline
    text = "John Doe met with Jane Smith on 2023-06-01. Contact: john@example.com. See https://example.com"
    ents = extract_entities(text)
    assert any(e['type'] == 'EMAIL' for e in ents)
    assert any(e['type'] == 'URL' for e in ents)
    assert any(e['type'] == 'DATE' for e in ents)
    rels = extract_relationships(text, ents)
    # John and Jane co-occur in first sentence
    assert isinstance(rels, list)
    timeline = extract_timeline(text)
    assert len(timeline) >= 1


def test_ingest_evidence_route(monkeypatch, client):
    token = _make_investigator_token()
    headers = {'Authorization': f'Bearer {token}'}

    # setup DB
    init_db()
    db = SessionLocal()
    try:
        c = models.Case(title='Test Case')
        db.add(c)
        db.commit()
        db.refresh(c)
        ev = models.Evidence(case_id=c.id, filename='sample.txt', storage_path='/tmp/sample', sha256='deadbeef', size=10, metadata_json={'ocr_text': 'Alice saw Bob on 2022-01-02'})
        db.add(ev)
        db.commit()
        db.refresh(ev)
        ev_id = ev.id
        # add a document too
        d = models.Document(evidence_id=ev_id, text='Alice saw Bob on 2022-01-02')
        db.add(d)
        db.commit()
    finally:
        db.close()

    # mock KG client
    class MockKG:
        def __init__(self):
            self.ingested = False

        def ingest(self, entities, relationships, timeline, evidence_id=None, case_id=None):
            self.ingested = True
            # basic assertions to ensure we got passed the right ids
            assert evidence_id is not None

        def query(self, cypher, params=None):
            return [{'name': 'Alice', 'type': 'proper_name'}]

        def close(self):
            pass

    monkeypatch.setattr('backend.app.kg.get_kg_client', lambda: MockKG())

    resp = client.post(f"/kg/ingest/evidence/{ev_id}", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert 'ingested_entities' in body


def test_query_route(monkeypatch, client):
    token = _make_investigator_token()
    headers = {'Authorization': f'Bearer {token}'}

    class MockKG2:
        def query(self, cypher, params=None):
            return [{'name': 'Alice', 'type': 'proper_name'}]

        def close(self):
            pass

    monkeypatch.setattr('backend.app.kg.get_kg_client', lambda: MockKG2())
    resp = client.post('/kg/query', json={'cypher': 'MATCH (n) RETURN n LIMIT 1'}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert 'results' in body and isinstance(body['results'], list)
