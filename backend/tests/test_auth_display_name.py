import pytest
from backend.app.auth import _extract_display_name, _sync_descope_user, get_me
from backend.app.database import init_db, SessionLocal
from backend.app import models


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    yield


def test_extract_display_name_google_full_name():
    payload = {
        "email": "akraguvaran66@gmail.com",
        "name": "Akash M",
    }
    assert _extract_display_name(payload) == "Akash M"


def test_extract_display_name_given_and_family_name():
    payload = {
        "email": "investigator@example.com",
        "given_name": "Jane",
        "family_name": "Doe",
    }
    assert _extract_display_name(payload) == "Jane Doe"


def test_extract_display_name_given_name_only():
    payload = {
        "email": "investigator@example.com",
        "givenName": "Akash",
    }
    assert _extract_display_name(payload) == "Akash"


def test_extract_display_name_custom_attributes():
    payload = {
        "email": "investigator@example.com",
        "customAttributes": {"name": "Detective Miller"},
    }
    assert _extract_display_name(payload) == "Detective Miller"


def test_extract_display_name_fallback_none_when_only_email():
    payload = {
        "email": "akraguvaran66@gmail.com",
    }
    # Returns None so caller can do proper safe fallback
    assert _extract_display_name(payload) is None


def test_sync_descope_user_stores_and_updates_name():
    db = SessionLocal()
    try:
        payload = {
            "sub": "google-oauth2|123456789",
            "email": "akraguvaran66@gmail.com",
            "name": "Akash M",
            "roles": ["jury_evaluator"],
        }
        user = _sync_descope_user(db, payload)
        assert user.name == "Akash M"
        assert user.email == "akraguvaran66@gmail.com"

        # Call get_me directly with user
        me = get_me(current_user=user)
        assert me["name"] == "Akash M"
        assert me["name"] != "akraguvaran66"
        assert me["email"] == "akraguvaran66@gmail.com"
    finally:
        db.close()
