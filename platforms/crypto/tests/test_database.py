import os
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import auth
import database
import migrate_sqlite


class DatabaseConfigurationTests(unittest.TestCase):
    def test_hosted_storage_never_falls_back_to_temporary_sqlite(self):
        with self.assertRaises(database.ConfigurationError):
            database.connect("", "unused.db", hosted=True)

    def test_invalid_url_is_rejected_without_echoing_credentials(self):
        with self.assertRaises(database.ConfigurationError) as error:
            database.connect("invalid://private-password", "unused.db")
        self.assertNotIn("private-password", str(error.exception))

    def test_vercel_connection_url_alias(self):
        with patch.dict(os.environ, {"DATABASE_URL": "", "POSTGRES_URL": "postgresql://example"}):
            self.assertEqual(database.configured_url(), "postgresql://example")

    def test_source_dry_run_does_not_create_missing_database(self):
        with tempfile.TemporaryDirectory() as temp:
            source = pathlib.Path(temp) / "missing.db"
            with self.assertRaises(FileNotFoundError):
                migrate_sqlite.read_source(source)
            self.assertFalse(source.exists())


@unittest.skipUnless(os.environ.get("TEST_POSTGRES_URL"), "Set TEST_POSTGRES_URL to an expendable PostgreSQL database")
class MigrationTests(unittest.TestCase):
    def test_sqlite_import_preserves_accounts_progress_sessions_and_avatars(self):
        with tempfile.TemporaryDirectory() as temp:
            source = pathlib.Path(temp) / "source.db"
            with patch.multiple(auth, DB_PATH=str(source), DATABASE_URL="", is_read_only=False, _db_initialized=False):
                user, token = auth.register_user("migrated_user", "password123", auth.PNG_MAGIC + b"image", "a.png")
                auth.save_progress(user["id"], {"aes": {"status": "done"}})
                secret = auth.get_jwt_secret()
            records = migrate_sqlite.read_source(source)
            url = os.environ["TEST_POSTGRES_URL"]
            with patch.multiple(auth, DATABASE_URL=url, _db_initialized=False):
                auth.init_db()
                with auth.get_db() as conn:
                    conn.execute("TRUNCATE users, progress, auth_settings, auth_sessions, avatars RESTART IDENTITY CASCADE")
                migrate_sqlite.import_records(records, url)
                self.assertEqual(auth.get_jwt_secret(), secret)
                self.assertEqual(auth.decode_token(token)["user_id"], user["id"])
                imported, _ = auth.login_user("MIGRATED_USER", "password123")
                self.assertEqual(imported["id"], user["id"])
                self.assertEqual(imported["progress"], {"aes": {"status": "done"}})
                avatar = auth.get_avatar(pathlib.Path(imported["avatar_url"]).name)
                self.assertEqual(bytes(avatar["data"]), auth.PNG_MAGIC + b"image")
                with self.assertRaises(ValueError):
                    migrate_sqlite.import_records(records, url)
                another, _ = auth.register_user("next_user", "password123")
                self.assertGreater(another["id"], user["id"])
                with auth.get_db() as conn:
                    conn.execute("TRUNCATE users, progress, auth_settings, auth_sessions, avatars RESTART IDENTITY CASCADE")
