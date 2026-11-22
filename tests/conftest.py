import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app(tmp_path):
    application = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-session-secret-with-enough-entropy-1234",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        "WTF_CSRF_ENABLED": False,
        "SESSION_COOKIE_SECURE": False,
    })
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
