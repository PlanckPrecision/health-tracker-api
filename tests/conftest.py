import os

import pytest

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-prod")

from app import create_app, db  # noqa: E402


@pytest.fixture
def app():
    application = create_app()
    application.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
        RATELIMIT_ENABLED=False,
        DEBUG=False,
    )
    with application.app_context():
        db.create_all()
        yield application


@pytest.fixture
def client(app):
    return app.test_client()


def signup(client, username="healthuser", password="Secure1!"):
    return client.post(
        "/signup",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def login(client, username="healthuser", password="Secure1!"):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )
