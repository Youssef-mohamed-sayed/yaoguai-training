import hashlib
from datetime import timedelta

from flask import request
from sqlalchemy import case, delete, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from ..extensions import db
from ..models import LoginThrottle, now_utc


def allow_auth_attempt(scope, limit, window_seconds):
    """A shared fixed-window limit persisted in PostgreSQL, including across Vercel instances."""
    now = now_utc()
    window = timedelta(seconds=window_seconds)
    identity = f"{scope}:{request.remote_addr or 'unknown'}"
    key_hash = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    dialect = db.engine.dialect.name
    if dialect == "postgresql":
        insert = pg_insert
    elif dialect == "sqlite":
        insert = sqlite_insert
    else:
        return False
    expired = LoginThrottle.window_started_at <= now - window
    statement = insert(LoginThrottle).values(key_hash=key_hash, window_started_at=now, attempts=1)
    statement = statement.on_conflict_do_update(
        index_elements=[LoginThrottle.key_hash],
        set_={
            "window_started_at": case((expired, now), else_=LoginThrottle.window_started_at),
            "attempts": case((expired, 1), else_=LoginThrottle.attempts + 1),
        },
    ).returning(LoginThrottle.attempts)
    attempts = db.session.execute(statement).scalar_one()
    db.session.execute(delete(LoginThrottle).where(LoginThrottle.window_started_at < now - timedelta(days=2)))
    db.session.commit()
    return attempts <= limit

