from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from . import database
from . import models
from .auth import get_current_user
from .database import init_db
import hashlib
import math
import json

router = APIRouter(prefix='/ai', tags=['ai'])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _text_to_embedding(text: str, dim: int = 32):
    # deterministic pseudo-embedding from sha256
    h = hashlib.sha256(text.encode('utf-8')).hexdigest()
    # take hex pairs into numbers
    nums = [int(h[i:i+2], 16) for i in range(0, len(h), 2)]
    vec = [((n % 256) / 255.0) for n in nums]
    # repeat/truncate to dim
    if len(vec) < dim:
        vec = (vec * ((dim // len(vec)) + 1))[:dim]
    else:
        vec = vec[:dim]
    return vec


@router.post('/ingest')
def ingest(payload: dict = Body(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # ensure DB exists
    database.init_db()
    evidence_id = payload.get('evidence_id')
    text = payload.get('text')
    if not text and not evidence_id:
        raise HTTPException(status_code=400, detail='provide text or evidence_id')
    if evidence_id:
        ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
        if not ev:
            raise HTTPException(status_code=404, detail='evidence not found')
        # derive text from metadata if available, otherwise use filename
        text = (ev.metadata_json or {}).get('ocr_text') or ev.filename or ''
    doc = models.Document(evidence_id=evidence_id, text=text, metadata_json={})
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # create embedding immediately (simple adapter)
    vec = _text_to_embedding(text or '')
    emb = models.Embedding(document_id=doc.id, vector=vec)
    db.add(emb)
    db.commit()

    audit = models.AuditLog(actor_id=current_user.id, action='ai.ingest', target_type='document', target_id=doc.id, detail={'evidence_id': evidence_id})
    db.add(audit)
    db.commit()

    return {'document_id': doc.id, 'embedding_id': emb.id}


@router.get('/documents/{doc_id}')
def get_document(doc_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    d = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not d:
        raise HTTPException(status_code=404, detail='document not found')
    return {'id': d.id, 'evidence_id': d.evidence_id, 'text': d.text, 'metadata': d.metadata_json}


def _cosine(a, b):
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


@router.post('/agent/query')
def agent_query(payload: dict = Body(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = payload.get('query')
    top_k = int(payload.get('top_k', 3))
    vec = _text_to_embedding(query)
    # load all embeddings
    rows = db.query(models.Embedding).all()
    scores = []
    for r in rows:
        v = r.vector or []
        score = _cosine(vec, v)
        scores.append((score, r))
    scores.sort(key=lambda x: x[0], reverse=True)
    hits = []
    for score, r in scores[:top_k]:
        doc = db.query(models.Document).filter(models.Document.id == r.document_id).first()
        hits.append({'document_id': r.document_id, 'score': score, 'text': (doc.text[:200] if doc else None)})
    audit = models.AuditLog(actor_id=current_user.id, action='ai.agent.query', target_type='query', target_id=None, detail={'query': query, 'hits': [h['document_id'] for h in hits]})
    db.add(audit)
    db.commit()
    return {'query': query, 'hits': hits}