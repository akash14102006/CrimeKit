from backend.app.embeddings import DeterministicProvider, get_provider
from backend.app.vector_store import DBVectorStore
from backend.app.database import init_db, SessionLocal
from backend.app import models


def test_deterministic_provider():
    p = DeterministicProvider(dim=16)
    v1 = p.embed('hello')
    v2 = p.embed('hello')
    assert v1 == v2
    assert len(v1) == 16


def test_vector_store_upsert_query():
    init_db()
    db = SessionLocal()
    try:
        # create two documents
        d1 = models.Document(text='doc one')
        d2 = models.Document(text='doc two')
        db.add_all([d1, d2])
        db.commit()
        db.refresh(d1)
        db.refresh(d2)
    finally:
        db.close()

    p = DeterministicProvider(dim=8)
    v1 = p.embed('apple')
    v2 = p.embed('banana')

    store = DBVectorStore()
    store.upsert(d1.id, v1)
    store.upsert(d2.id, v2)

    q = p.embed('apple')
    # request more results to tolerate pre-existing embeddings in the DB
    res = store.query(q, top_k=5)
    # ensure our document is among top_k results
    assert any(r[1] == d1.id for r in res)