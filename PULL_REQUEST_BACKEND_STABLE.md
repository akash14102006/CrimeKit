Concise PR: Stabilize backend tests and deprecations

- Knowledge Graph module: added `backend/app/kg.py` and routes to ingest/query entities, timeline and relationships; KG client wraps Neo4j driver and stores entity embeddings in the DB vector store.
- Backend package/import fixes: standardized imports to `backend.app.*`, added package `__init__.py` files, and ensured tests import correctly.
- In-memory SQLite test isolation: `backend/tests/conftest.py` configures an in-memory DB with `StaticPool`, recreates schema per-test, and sets `TESTING=1` to avoid background worker races.
- Timezone-aware datetime migration: replaced naive `datetime.utcnow()` with timezone-aware `datetime.now(timezone.utc)` across auth, evidence, and processing; JWT `exp` claims use numeric timestamps for compatibility.
- pypdf migration: prefer `pypdf` for PDF text extraction; removed runtime fallback to deprecated `PyPDF2`, updated `backend/requirements.txt`.
- Test results: all backend tests pass locally: 14/14 passing.

Notes: suppressed third-party DeprecationWarning in pytest output while upstream libraries are updated. The code changes are focused and backwards compatible; recommend bumping dependencies when upstream fixes are available.
