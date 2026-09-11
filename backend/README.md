# Backend Scaffold (minimal)

This folder contains a minimal FastAPI service scaffold to validate the auth and DB pipeline.

Features:
- `POST /auth/login` — accepts `email` + `password`, returns a placeholder access token on success.
- SQLite dev DB with SQLAlchemy models for `users`.
- Password hashing using `passlib` (bcrypt).
- A small pytest test exercising the login flow.

Start (dev):

```bash
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
