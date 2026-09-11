from backend.app.database import SessionLocal, init_db
from backend.app import models
init_db()
db=SessionLocal()
rows=db.query(models.Embedding).all()
print('Found', len(rows), 'embeddings')
for r in rows:
    print(r.document_id, r.vector[:4] if r.vector else None)
db.close()
