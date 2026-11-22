import io
import os
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import app
import auth


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.paths = patch.multiple(auth, DB_PATH=str(pathlib.Path(self.temp.name) / "test.db"),
                                    DATABASE_URL="", is_read_only=False,
                                    AVATARS_DIR=self.temp.name, _db_initialized=False)
        self.paths.start()
        self.client = app.app.test_client()

    def tearDown(self):
        self.paths.stop()
        self.temp.cleanup()

    def register(self, **changes):
        return self.client.post("/api/auth/register", json={
            "username": "test_user", "password": "password123", **changes})

    def test_registration_rules_and_all_missing_fields(self):
        response = self.register(username="", password="")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json["errors"]), {"username", "password"})
        for fields, message in [
            ({"password": "1234567"}, "at least 8"),
            ({"password": "x" * 73}, "72 UTF-8 bytes"),
            ({"password": "😀" * 19}, "72 UTF-8 bytes"),
            ({"username": "ab"}, "3 and 30"),
            ({"username": "a" * 31}, "3 and 30"),
            ({"username": "bad name"}, "only contain"),
            ({"username": ["test"]}, "must be text"),
            ({"password": 12345678}, "must be text"),
        ]:
            with self.subTest(fields=fields):
                response = self.register(**fields)
                self.assertEqual(response.status_code, 400)
                self.assertIn(message, response.json["error"])

    def test_registration_login_and_duplicate(self):
        response = self.register(password="12345678")
        self.assertEqual(response.status_code, 200)
        token = response.json["result"]["token"]
        self.assertEqual(self.client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}"}).status_code, 200)
        self.assertIn("already exists", self.register(username="TEST_USER").json["error"])
        response = self.client.post("/api/auth/login", json={
            "username": "test_user", "password": "12345678"})
        self.assertEqual(response.status_code, 200)

    def test_login_errors_and_legacy_short_password(self):
        response = self.client.post("/api/auth/login", json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json["errors"]), {"username", "password"})
        with auth.get_db() as conn:
            conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                         ("legacy", auth.hash_password("1234")))
        for username, password, status in [("legacy", "1234", 200),
                                            ("legacy", "wrong", 401),
                                            ("missing", "wrong", 401)]:
            response = self.client.post("/api/auth/login", json={
                "username": username, "password": password})
            self.assertEqual(response.status_code, status)
            if status == 401:
                self.assertEqual(response.json["error"], "Invalid username or password.")

    def test_bad_json_returns_json_error(self):
        for endpoint in ("register", "login", "avatar"):
            for body in ("[]", "null", "{", '"text"', "123"):
                response = self.client.post(f"/api/auth/{endpoint}", data=body,
                                            content_type="application/json")
                self.assertEqual(response.status_code, 400)
                self.assertIn("valid JSON object", response.json["error"])

    def test_avatar_validation_and_upload_limits(self):
        for content, filename, message in [(b"", "a.png", "Empty"),
                                            (b"fake", "a.png", "Invalid PNG"),
                                            (b"fake", "a.gif", ".png or .jpg")]:
            response = self.client.post("/api/auth/register", data={
                "username": "avatar_user", "password": "password123",
                "avatar": (io.BytesIO(content), filename)})
            self.assertEqual(response.status_code, 400)
            self.assertIn(message, response.json["error"])
        # Header validation is the existing avatar format policy.
        content = auth.PNG_MAGIC + b"x" * (2 * 1024 * 1024 - len(auth.PNG_MAGIC))
        response = self.client.post("/api/auth/register", data={
            "username": "avatar_user", "password": "password123",
            "avatar": (io.BytesIO(content), "a.png")})
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/api/auth/register", data={
            "username": "other_user", "password": "password123",
            "avatar": (io.BytesIO(content + b"x"), "a.png")})
        self.assertEqual(response.status_code, 400)
        self.assertIn("2 MB", response.json["error"])
        response = self.client.post("/api/auth/register", data=b"x" * (3 * 1024 * 1024 + 1),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 413)
        self.assertIn("2 MB", response.json["error"])
        response = self.client.post("/api/encoding/hex/encode", data=b"x" * (1024 * 1024 + 1))
        self.assertEqual(response.status_code, 413)

    def test_bad_base64_and_session(self):
        self.assertIn("Invalid base64", self.register(avatar_b64="!!!").json["error"])
        response = self.client.get("/api/auth/me", headers={"Authorization": "Bearer invalid"})
        self.assertEqual(response.status_code, 401)
        self.assertIn("log in again", response.json["error"])

    def test_service_errors_do_not_leak_internal_details(self):
        for endpoint, target in [("register", "register_user"), ("login", "login_user")]:
            with patch.object(auth, target, side_effect=sqlite3.OperationalError("private/path.db")), \
                    self.assertLogs(app.app.logger, level="ERROR"):
                response = self.client.post(f"/api/auth/{endpoint}", json={
                    "username": "test_user", "password": "password123"})
            self.assertEqual(response.status_code, 503)
            self.assertIn("try again later", response.json["error"])
            self.assertNotIn("private", response.json["error"])

    def test_progress_and_avatar_updates_are_scoped_to_authenticated_account(self):
        first = self.register().json["result"]
        second = self.register(username="second_user").json["result"]
        headers = {"Authorization": f"Bearer {first['token']}"}
        second_headers = {"Authorization": f"Bearer {second['token']}"}
        response = self.client.post(f"/api/user/progress?user_id={second['user']['id']}",
            headers=headers, json={"user_id": second["user"]["id"],
                                   "progress": {"aes": {"status": "done"}}})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/user/progress", headers=second_headers).json["result"]["progress"], {})
        self.client.post("/api/auth/avatar", headers=headers, data={
            "user_id": str(second["user"]["id"]), "avatar": (io.BytesIO(auth.PNG_MAGIC), "a.png")})
        first_user = self.client.get("/api/auth/me", headers=headers).json["result"]["user"]
        second_user = self.client.get("/api/auth/me", headers=second_headers).json["result"]["user"]
        self.assertTrue(first_user["avatar_url"])
        self.assertEqual(second_user["avatar_url"], "")
        self.assertEqual(second_user["progress"], {})
        self.assertEqual(first_user["progress"]["aes"]["status"], "done")

    def test_logout_revokes_only_current_session_and_preserves_saved_progress(self):
        first = self.register().json["result"]
        second = self.register(username="second_user").json["result"]
        headers = {"Authorization": f"Bearer {first['token']}"}
        self.client.post("/api/user/progress", headers=headers,
                         json={"progress": {"aes": {"status": "done"}}})
        response = self.client.post("/api/auth/logout", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        for endpoint in ("/api/auth/me", "/api/user/progress"):
            self.assertEqual(self.client.get(endpoint, headers=headers).status_code, 401)
        self.assertEqual(self.client.post("/api/user/progress", headers=headers,
                                         json={"progress": {}}).status_code, 401)
        self.assertEqual(self.client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {second['token']}"}).status_code, 200)
        login = self.client.post("/api/auth/login", json={
            "username": "test_user", "password": "password123"}).json["result"]
        self.assertNotEqual(first["token"], login["token"])
        self.assertEqual(login["user"]["progress"]["aes"]["status"], "done")

    def test_forged_or_expired_tokens_cannot_select_another_account(self):
        first = self.register().json["result"]
        second = self.register(username="second_user").json["result"]
        payload = auth.decode_token(first["token"])
        secret = auth.get_jwt_secret()
        self.assertNotEqual(secret, "yaoguai-crypto-secret-key-2024-secure-jwt")
        forged = dict(payload, sub=str(second["user"]["id"]), user_id=second["user"]["id"])
        missing_session = {key: value for key, value in payload.items() if key != "jti"}
        for claims, key in [(forged, secret), (missing_session, secret),
                            (dict(payload, exp=1), secret),
                            (payload, "yaoguai-crypto-secret-key-2024-secure-jwt")]:
            header = auth._b64url_encode(b'{"alg":"HS256","typ":"JWT"}')
            body = auth._b64url_encode(auth.json.dumps(claims).encode())
            signature = auth.hmac.new(key.encode(), f"{header}.{body}".encode(), auth.hashlib.sha256).digest()
            token = f"{header}.{body}.{auth._b64url_encode(signature)}"
            for fallback in (False, True):
                with patch.object(auth, "HAS_PYJWT", not fallback):
                    response = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
                self.assertEqual(response.status_code, 401)
        self.assertEqual(self.client.get(f"/api/auth/me?token={first['token']}").status_code, 401)

    def test_stdlib_session_creation_and_revocation(self):
        with patch.object(auth, "HAS_PYJWT", False):
            result = self.register().json["result"]
            payload = auth.decode_token(result["token"])
            self.assertEqual(payload["user_id"], result["user"]["id"])
            auth.revoke_token(result["token"])
            with self.assertRaises(ValueError):
                auth.decode_token(result["token"])

    def test_avatar_uploads_do_not_overwrite_each_other(self):
        result = self.register().json["result"]
        user_id = result["user"]["id"]
        first = auth.update_user_avatar(user_id, auth.PNG_MAGIC + b"first", "a.png")
        second = auth.update_user_avatar(user_id, auth.PNG_MAGIC + b"second", "a.png")
        self.assertNotEqual(first, second)
        self.assertEqual(bytes(auth.get_avatar(pathlib.Path(first).name)["data"]), auth.PNG_MAGIC + b"first")


@unittest.skipUnless(os.environ.get("TEST_POSTGRES_URL"), "Set TEST_POSTGRES_URL to an expendable PostgreSQL database")
class PostgresAuthenticationTests(AuthenticationTests):
    def setUp(self):
        super().setUp()
        auth.DATABASE_URL = os.environ["TEST_POSTGRES_URL"]
        auth.init_db()
        with auth.get_db() as conn:
            conn.execute("TRUNCATE users, progress, auth_settings, auth_sessions, avatars RESTART IDENTITY CASCADE")

    def tearDown(self):
        with auth.get_db() as conn:
            conn.execute("TRUNCATE users, progress, auth_settings, auth_sessions, avatars RESTART IDENTITY CASCADE")
        super().tearDown()


if __name__ == "__main__":
    unittest.main()
