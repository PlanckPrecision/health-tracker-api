from app import db
from app.models import Entry, User
from tests.conftest import login, signup

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
        signup(client)
        with app.app_context():
            assert User.query.filter_by(username="healthuser").first() is not None

    def test_duplicate_username_blocked(self, client):
        signup(client)
        resp = signup(client)
        assert b"already exists" in resp.data

    def test_weak_password_blocked(self, client):
        resp = client.post(
            "/signup",
            data={"username": "newuser", "password": "abc"},
            follow_redirects=True,
        )
        assert b"Password must be" in resp.data

    def test_password_not_stored_in_plaintext(self, client, app):
        signup(client, password="Secure1!")
        with app.app_context():
            user = User.query.filter_by(username="healthuser").first()
            assert user.password != "Secure1!"


class TestLogin:
    def test_wrong_password_rejected(self, client):
        signup(client)
        resp = login(client, password="WrongPass99!")
        assert b"Invalid" in resp.data

    def test_nonexistent_user_rejected(self, client):
        resp = login(client, username="ghost")
        assert b"Invalid" in resp.data

    def test_correct_credentials_accepted(self, client):
        signup(client)
        resp = login(client)
        assert resp.status_code == 200


class TestProtectedRoutes:
    def test_settings_redirects_when_not_logged_in(self, client):
        resp = client.get("/settings", follow_redirects=False)
        assert resp.status_code == 302


# ---------------------------------------------------------------------------
# Entry management
# ---------------------------------------------------------------------------

class TestDeleteEntry:
    def test_delete_removes_entry(self, client, app):
        signup(client)
        login(client)
        client.post("/register", data={"weight": "80.0", "date": ""}, follow_redirects=True)

        with app.app_context():
            entry = Entry.query.first()
            assert entry is not None
            entry_id = entry.id

        resp = client.post(f"/entries/{entry_id}/delete", follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            assert db.session.get(Entry, entry_id) is None

    def test_delete_other_users_entry_returns_404(self, client, app):
        signup(client, username="owner")
        login(client, username="owner")
        client.post("/register", data={"weight": "80.0", "date": ""}, follow_redirects=True)

        with app.app_context():
            entry_id = Entry.query.first().id

        signup(client, username="attacker", password="Attack1!")
        login(client, username="attacker", password="Attack1!")

        resp = client.post(f"/entries/{entry_id}/delete", follow_redirects=False)
        assert resp.status_code == 404

    def test_delete_requires_login(self, client, app):
        signup(client)
        login(client)
        client.post("/register", data={"weight": "80.0", "date": ""}, follow_redirects=True)

        with app.app_context():
            entry_id = Entry.query.first().id

        client.get("/logout")
        resp = client.post(f"/entries/{entry_id}/delete", follow_redirects=False)
        assert resp.status_code == 302
