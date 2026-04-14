import os
import pytest

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-prod")

from app import create_app, db
from app.models import User


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    application = create_app()
    application.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
        DEBUG=False,
    )
    with application.app_context():
        db.create_all()
        yield application
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _signup(client, username="healthuser", password="Secure1!"):
    return client.post(
        "/signup",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def _login(client, username="healthuser", password="Secure1!"):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


# ---------------------------------------------------------------------------
# Password validation (pure function — no DB needed)
# ---------------------------------------------------------------------------

class TestPasswordValidation:
    def test_too_short_rejected(self):
        from app.validate import is_valid_password
        assert not is_valid_password("Ab1!")

    def test_no_special_char_rejected(self):
        from app.validate import is_valid_password
        assert not is_valid_password("Password1")

    def test_no_letter_rejected(self):
        from app.validate import is_valid_password
        assert not is_valid_password("123456!")

    def test_valid_password_accepted(self):
        from app.validate import is_valid_password
        assert is_valid_password("Secure1!")


# ---------------------------------------------------------------------------
# Weight validation (pure function — no DB needed)
# ---------------------------------------------------------------------------

class TestWeightValidation:
    def test_empty_string_rejected(self):
        from app.validate import check_weight
        valid, _ = check_weight("")
        assert not valid

    def test_above_500_rejected(self):
        from app.validate import check_weight
        valid, _ = check_weight("501")
        assert not valid

    def test_text_input_rejected(self):
        from app.validate import check_weight
        valid, _ = check_weight("heavy")
        assert not valid

    def test_valid_weight_accepted(self):
        from app.validate import check_weight
        valid, val = check_weight("75.5")
        assert valid and val == 75.5


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

class TestSignup:
    def test_signup_success(self, client, app):
        _signup(client)
        with app.app_context():
            assert User.query.filter_by(username="healthuser").first() is not None

    def test_duplicate_username_blocked(self, client):
        _signup(client)
        resp = _signup(client)
        assert b"already exists" in resp.data

    def test_weak_password_blocked(self, client):
        resp = client.post(
            "/signup",
            data={"username": "newuser", "password": "abc"},
            follow_redirects=True,
        )
        assert b"Password must be" in resp.data

    def test_password_not_stored_in_plaintext(self, client, app):
        _signup(client, password="Secure1!")
        with app.app_context():
            user = User.query.filter_by(username="healthuser").first()
            assert user.password != "Secure1!"


class TestLogin:
    def test_wrong_password_rejected(self, client):
        _signup(client)
        resp = _login(client, password="WrongPass99!")
        assert b"Invalid" in resp.data

    def test_nonexistent_user_rejected(self, client):
        resp = _login(client, username="ghost")
        assert b"Invalid" in resp.data

    def test_correct_credentials_accepted(self, client):
        _signup(client)
        resp = _login(client)
        assert resp.status_code == 200


class TestProtectedRoutes:
    def test_settings_redirects_when_not_logged_in(self, client):
        resp = client.get("/settings", follow_redirects=False)
        assert resp.status_code == 302
