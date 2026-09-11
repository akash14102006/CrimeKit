from . import database
from . import models
import math
from typing import List, Tuple


def _cosine(a: List[float], b: List[float]) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


class DBVectorStore:
    """Simple DB-backed vector store using models.Embedding."""

    def upsert(self, document_id: str, vector: List[float]):
        db = database.SessionLocal()
        try:
            emb = db.query(models.Embedding).filter(models.Embedding.document_id == document_id).first()
            if emb:
                emb.vector = vector
                db.add(emb)
            else:
                emb = models.Embedding(document_id=document_id, vector=vector)
                db.add(emb)
            db.commit()
        finally:
            db.close()

    def query(self, vector: List[float], top_k: int = 5) -> List[Tuple[float, str]]:
        db = database.SessionLocal()
        try:
            rows = db.query(models.Embedding).all()
            scored = []
            for r in rows:
                v = r.vector or []
                score = _cosine(vector, v)
                scored.append((score, r.document_id))
            scored.sort(key=lambda x: x[0], reverse=True)
            return scored[:top_k]
        finally:
            db.close()
