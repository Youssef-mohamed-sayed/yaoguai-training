"""Validate a SQLite export, then optionally import it into an EMPTY Neon database.

Dry run: python scripts/migrate_sqlite.py --source backup.db --avatars public/assets/avatars
Import:  same command with --apply (DATABASE_URL must be set)
"""
import argparse
import json
import os
import pathlib
import sqlite3
import time
from contextlib import closing

import auth
import database


def read_source(source, avatars_dir=None, skip_missing_avatars=False):
    source = pathlib.Path(source).resolve(strict=True)
    with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "users" not in tables:
            raise ValueError("The source database does not contain a users table.")
        records = {}
        for table in ("users", "progress", "auth_settings", "auth_sessions", "avatars"):
            records[table] = [dict(row) for row in conn.execute(f"SELECT * FROM {table}")] if table in tables else []

    ids = {user["id"] for user in records["users"]}
    names = [user["username"].lower() for user in records["users"]]
    if len(names) != len(set(names)):
        raise ValueError("Source usernames conflict when compared without case.")
    for table in ("progress", "auth_sessions", "avatars"):
        if any(row["user_id"] not in ids for row in records[table]):
            raise ValueError(f"Source {table} contains an unknown account ID.")
    for progress in records["progress"]:
        if not isinstance(json.loads(progress["progress_json"]), dict):
            raise ValueError("Source progress must contain JSON objects.")
    records["auth_sessions"] = [row for row in records["auth_sessions"] if row["expires_at"] > int(time.time())]
    images = {row["filename"]: row for row in records["avatars"]}
    root = pathlib.Path(avatars_dir).resolve() if avatars_dir else None
    missing = 0
    for user in records["users"]:
        url = user.get("avatar_url") or ""
        if not url:
            continue
        prefix = "assets/avatars/"
        filename = url.removeprefix("/").removeprefix(prefix)
        if not url.removeprefix("/").startswith(prefix) or pathlib.PurePath(filename).name != filename or "\\" in filename:
            raise ValueError("A source avatar has an unsupported path.")
        if filename in images:
            if images[filename]["user_id"] != user["id"]:
                raise ValueError("A source avatar belongs to a different account.")
            continue
        image_path = root / filename if root else None
        if image_path and image_path.is_file() and image_path.resolve().is_relative_to(root):
            raw = image_path.read_bytes()
            raw, ext = auth.validate_avatar_file(raw, filename)
            images[filename] = {"filename": filename, "user_id": user["id"], "data": raw,
                                "content_type": "image/png" if ext == ".png" else "image/jpeg"}
        elif skip_missing_avatars:
            user["avatar_url"] = ""
            missing += 1
        else:
            raise ValueError("An avatar file is missing. Supply --avatars or explicitly use --skip-missing-avatars.")
    records["avatars"] = list(images.values())
    records["missing_avatars"] = missing
    return records


def import_records(records, url):
    if not url:
        raise ValueError("Set DATABASE_URL before importing into Neon.")
    conn = database.connect(url, None)
    try:
        database.init_schema(conn)
        conn.execute("LOCK TABLE users, progress, auth_settings, auth_sessions, avatars IN ACCESS EXCLUSIVE MODE")
        for table in ("users", "progress", "auth_settings", "auth_sessions", "avatars"):
            if conn.execute(f"SELECT 1 FROM {table} LIMIT 1").fetchone():
                raise ValueError("The target database already contains account data; import refused without changing it.")
        columns = {
            "users": ("id", "username", "password_hash", "avatar_url", "created_at"),
            "progress": ("user_id", "progress_json", "updated_at"),
            "auth_settings": ("name", "value"),
            "auth_sessions": ("token_id", "user_id", "expires_at"),
            "avatars": ("filename", "user_id", "data", "content_type"),
        }
        for table, fields in columns.items():
            query = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join('?' for _ in fields)})"
            for row in records[table]:
                conn.execute(query, tuple(row[field] for field in fields))
        conn.execute("""
            SELECT setval(pg_get_serial_sequence('users', 'id'),
                          COALESCE((SELECT MAX(id) FROM users), 1),
                          EXISTS (SELECT 1 FROM users))
        """)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--avatars")
    parser.add_argument("--skip-missing-avatars", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        records = read_source(args.source, args.avatars, args.skip_missing_avatars)
        counts = {table: len(records[table]) for table in ("users", "progress", "auth_settings", "auth_sessions", "avatars")}
        print(json.dumps({"mode": "import" if args.apply else "dry-run", **counts,
                          "missing_avatars": records["missing_avatars"]}))
        if args.apply:
            import_records(records, os.environ.get("DATABASE_URL_UNPOOLED") or database.configured_url())
            print("Import complete. Account IDs, password hashes, and progress were preserved.")
        else:
            print("Validation complete. No databases were changed. Add --apply to import into an empty target.")
    except (ValueError, OSError, sqlite3.Error) as exc:
        parser.exit(1, f"Migration stopped: {exc}\n")
    except database.DATABASE_ERRORS:
        parser.exit(1, "Migration stopped: database operation failed; target transaction was rolled back.\n")


if __name__ == "__main__":
    main()
