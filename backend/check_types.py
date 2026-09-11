import sys
sys.path.insert(0, '.')
from app import database, models
db = database.SessionLocal()
ev = db.query(models.Evidence).order_by(models.Evidence.id.desc()).first()
results = db.query(models.ForensicResult).filter(models.ForensicResult.evidence_id == ev.id).all()
for r in results:
    rt = type(r.result).__name__
    print(f"processor={r.processor}, type={rt}")
db.close()
