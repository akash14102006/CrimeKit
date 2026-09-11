import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import init_db, engine
from backend.app import models
import bcrypt


@pytest.fixture(autouse=True)
def setup_db(tmp_path):
    # Use a temporary SQLite DB file for tests
    db_path = tmp_path / "test.db"
    url = f"sqlite:///{db_path}"
    # Patch engine URL indirectly by creating tables on the default engine
    init_db()
    yield


def test_health():
    client = TestClient(app)
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'
