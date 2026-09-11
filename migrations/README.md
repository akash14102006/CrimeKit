# Migrations — Guidance (Alembic/Flyway)

This folder contains guidance for setting up database migrations for CrimeKit.

Recommended tools
-----------------
- Python: Alembic (for SQLAlchemy-based apps)
- Java/SQL: Flyway or Liquibase

Alembic quickstart (Python)
----------------------------
1. Create a virtualenv and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install alembic psycopg2-binary
```

2. Initialize Alembic (run from repo root):

```bash
alembic init migrations
```

3. Edit `alembic.ini` and `migrations/env.py` to use your DB URL from a secret manager.

4. Create migration:

```bash
alembic revision --autogenerate -m "create users/roles/evidence schema"
alembic upgrade head
```

Notes
-----
- Never commit production DB credentials. Use environment variables or a secrets manager.  
- Run migrations from CI with a dedicated service account that has limited privileges.
