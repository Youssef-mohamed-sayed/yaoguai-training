"""Create or verify the first Yaoguai Training administrator."""
import os
import sys
from pathlib import Path

from argon2 import PasswordHasher
from sqlalchemy import func, select

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app import create_app
from app.extensions import db
from app.models import User


def main():
    username = os.environ.get("INITIAL_ADMIN_USERNAME", "YaoAdmin").strip()
    email = os.environ.get("INITIAL_ADMIN_EMAIL", "0xsoundwav3@gmail.com").strip().lower()
    password = os.environ.get("INITIAL_ADMIN_PASSWORD")
    if not password or len(password) < 12:
        print("Set INITIAL_ADMIN_PASSWORD to a unique password of at least 12 characters.", file=sys.stderr)
        return 2
    app = create_app()
    with app.app_context():
        user = db.session.execute(select(User).where(func.lower(User.username) == username.lower())).scalar_one_or_none()
        if user:
            duplicate = db.session.execute(select(User).where(func.lower(User.email) == email, User.id != user.id)).scalar_one_or_none()
            if duplicate:
                print("The configured administrator email belongs to another account.", file=sys.stderr)
                return 1
            user.is_admin = True
            user.email = email
            user.must_change_password = True
            db.session.commit()
            print("Administrator role verified. Password was not changed.")
            return 0
        user = User(username=username, email=email,
                    password_hash=PasswordHasher().hash(password), is_admin=True, must_change_password=True)
        db.session.add(user)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            print("Unable to create the administrator; check that the database is migrated and the username/email is unused.", file=sys.stderr)
            return 1
        print("Initial administrator created. A password change is required at first login.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

