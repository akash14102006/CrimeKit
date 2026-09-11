# CRIMEKIT DATABASE DEPLOYMENT CHECKLIST
**Document Version:** 1.0.0  
**Target Engine:** PostgreSQL 16  
**ORM / Migration Framework:** SQLAlchemy 2.0.22 / Alembic 1.11.1  

---

## 1. Engine & Extension Requirements

* **PostgreSQL Version:** 16.x (recommended 16.2+)
* **Mandatory Extensions (executed as superuser/rds_superuser):**
  ```sql
  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
  CREATE EXTENSION IF NOT EXISTS "pgcrypto";
  CREATE EXTENSION IF NOT EXISTS "pg_trgm";
  CREATE EXTENSION IF NOT EXISTS "btree_gist";
  CREATE EXTENSION IF NOT EXISTS "vector";
  ```
* **pgvector Specifications:**
  - Used by `models.Embedding` for semantic search and `Face Trace` face embedding matching.
  - Dimension for Document Embeddings: 32-dim (DeterministicProvider) or 1536-dim (OpenAI `text-embedding-3-small`).
  - Dimension for Face Trace Embeddings: 512-dim (InsightFace ArcFace `buffalo_l`).
  - Index Type: HNSW (`vector_cosine_ops`) for sub-millisecond nearest-neighbor search.

---

## 2. Permissions & Role Architecture

* Run from `infrastructure/postgres/init.sql`:
  ```sql
  CREATE ROLE crimekit_app WITH LOGIN PASSWORD 'STRONG_PRODUCTION_PASSWORD';
  GRANT CONNECT ON DATABASE crimekit TO crimekit_app;
  GRANT USAGE ON SCHEMA public TO crimekit_app;
  GRANT CREATE ON SCHEMA public TO crimekit_app;
  GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO crimekit_app;
  GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO crimekit_app;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO crimekit_app;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO crimekit_app;
  ```

---

## 3. Migration Commands & Sequence

1. **Alembic Database Head Migration:**
   ```bash
   cd backend
   alembic upgrade head
   ```
2. **Runtime Verification:**
   - On application startup, `database.init_db()` invokes `Base.metadata.create_all(bind=engine)`, creating any unmigrated compliance, multitenancy, or blockchain tables.
   - Initial enterprise roles (`admin`, `investigator`, `analyst`, `viewer`, `evidence_officer`, `compliance_officer`, `auditor`, `user`) are automatically seeded by `app.main:on_startup`.

---

## 4. Production Connection Configuration

* **Connection String:**
  `postgresql://crimekit_app:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DB}?sslmode=require`
* **Connection Pooling:**
  - Pool Class: `QueuePool` with health checks (`pool_pre_ping=True`)
  - Pool Size: `DB_POOL_SIZE=10`
  - Max Overflow: `DB_MAX_OVERFLOW=20`
  - Pool Timeout: `DB_POOL_TIMEOUT=30`
  - Recycle Time: `DB_POOL_RECYCLE=1800` (prevents stale socket disconnections)

---

## 5. Backup & Recovery Policy

* **Automated Daily Backups:** 35-day retention with AWS RDS automated snapshots.
* **Point-in-Time Recovery (PITR):** Transaction log (WAL) archiving enabled with 5-minute RPO.
* **Multi-AZ Replication:** Synchronous standby replica across separate Availability Zones for automatic failover.
