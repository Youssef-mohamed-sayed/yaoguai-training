"""
auth.py — Resilient authentication, JWT session management, SQLite persistence,
avatar handling (.png, .jpg strictly enforced), and progress saving for YAOGUAI.
Compatible with both standard local runs and Vercel Serverless (read-only filesystem).
"""
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import tempfile
import time
from contextlib import contextmanager
from typing import Optional, Tuple, Dict, Any

import bcrypt
import database

# Attempt to load PyJWT; if not available, stdlib HS256 fallback will be used
try:
    import jwt
    HAS_PYJWT = True
except ImportError:
    HAS_PYJWT = False

DATABASE_URL = database.configured_url()
JWT_SECRET = os.environ.get("YAOGUAI_JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 14

# Allowed avatar extensions & magic byte signatures
ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"

# Environment detection for read-only serverless filesystems (e.g. Vercel)
scripts_dir = os.path.dirname(os.path.abspath(__file__))
is_read_only = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
if not is_read_only:
    try:
        test_file = os.path.join(scripts_dir, ".test_write")
        with open(test_file, "w") as f:
            f.write("1")
        os.remove(test_file)
    except Exception:
        is_read_only = True

if is_read_only:
    _temp_base = os.path.join(tempfile.gettempdir(), "yaoguai_data")
    os.makedirs(_temp_base, exist_ok=True)
    DB_PATH = os.path.join(_temp_base, "yaoguai.db")
    AVATARS_DIR = os.path.join(_temp_base, "avatars")
    os.makedirs(AVATARS_DIR, exist_ok=True)
else:
    DB_PATH = os.path.join(scripts_dir, "yaoguai.db")
    AVATARS_DIR = os.path.abspath(os.path.join(scripts_dir, "..", "public", "assets", "avatars"))
    try:
        os.makedirs(AVATARS_DIR, exist_ok=True)
    except Exception:
        _temp_base = os.path.join(tempfile.gettempdir(), "yaoguai_data")
        os.makedirs(_temp_base, exist_ok=True)
        DB_PATH = os.path.join(_temp_base, "yaoguai.db")
        AVATARS_DIR = os.path.join(_temp_base, "avatars")
        os.makedirs(AVATARS_DIR, exist_ok=True)


_db_initialized = False

@contextmanager
def get_db():
    global _db_initialized
    conn = database.connect(DATABASE_URL, DB_PATH, hosted=is_read_only)
    try:
        if not _db_initialized:
            init_db(conn)
            _db_initialized = True
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(conn=None):
    if conn is not None:
        database.init_schema(conn)
        conn.commit()
        return
    with get_db():
        pass


# ------------------------------------------------ JWT HELPERS (PyJWT + stdlib fallback)
def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    rem = len(s) % 4
    if rem:
        s += "=" * (4 - rem)
    return base64.urlsafe_b64decode(s.encode("ascii"))


def get_jwt_secret():
    if JWT_SECRET:
        return JWT_SECRET
    # Never sign sessions with a publicly known default key. Persist the local
    # fallback alongside the accounts so restarts and worker processes agree.
    with get_db() as conn:
        conn.execute("INSERT INTO auth_settings (name, value) VALUES (?, ?) ON CONFLICT(name) DO NOTHING",
                     ("jwt_secret", secrets.token_hex(32)))
        return conn.execute("SELECT value FROM auth_settings WHERE name = 'jwt_secret'").fetchone()["value"]


def create_token(user_id: int, username: str) -> str:
    now_ts = int(time.time())
    exp_ts = now_ts + (JWT_EXPIRATION_DAYS * 86400)
    token_id = secrets.token_urlsafe(32)
    payload = {"sub": str(user_id), "user_id": int(user_id), "username": username,
               "iat": now_ts, "exp": exp_ts, "jti": token_id}
    secret = get_jwt_secret()
    if HAS_PYJWT:
        token = jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)
    else:
        header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
        body = _b64url_encode(json.dumps(payload).encode())
        msg = f"{header}.{body}".encode("ascii")
        signature = hmac.new(secret.encode(), msg, hashlib.sha256).digest()
        token = f"{header}.{body}.{_b64url_encode(signature)}"
    with get_db() as conn:
        conn.execute("DELETE FROM auth_sessions WHERE expires_at <= ?", (now_ts,))
        conn.execute("INSERT INTO auth_sessions (token_id, user_id, expires_at) VALUES (?, ?, ?)",
                     (token_id, user_id, exp_ts))
    return token


def decode_token(token: str) -> Dict[str, Any]:
    if not isinstance(token, str) or not token.strip():
        raise ValueError("Invalid authentication token.")
    secret = get_jwt_secret()
    try:
        if HAS_PYJWT:
            payload = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM],
                                 options={"require": ["sub", "user_id", "iat", "exp", "jti"]})
        else:
            header, body, signature = token.split(".")
            if json.loads(_b64url_decode(header)).get("alg") != JWT_ALGORITHM:
                raise ValueError()
            expected = hmac.new(secret.encode(), f"{header}.{body}".encode("ascii"), hashlib.sha256).digest()
            if not hmac.compare_digest(expected, _b64url_decode(signature)):
                raise ValueError()
            payload = json.loads(_b64url_decode(body))
        if (not isinstance(payload, dict) or not isinstance(payload["user_id"], int)
                or isinstance(payload["user_id"], bool) or payload["user_id"] <= 0
                or payload["sub"] != str(payload["user_id"])
                or not isinstance(payload["jti"], str)
                or int(payload["iat"]) > int(time.time())
                or int(payload["exp"]) <= int(time.time())):
            raise ValueError()
    except Exception:
        raise ValueError("Your session is invalid or has expired. Please log in again.") from None
    with get_db() as conn:
        session = conn.execute(
            "SELECT user_id FROM auth_sessions WHERE token_id = ? AND user_id = ? AND expires_at > ?",
            (payload["jti"], payload["user_id"], int(time.time()))).fetchone()
    if not session:
        raise ValueError("Your session has ended. Please log in again.")
    return payload


def revoke_token(token: str):
    payload = decode_token(token)
    with get_db() as conn:
        conn.execute("DELETE FROM auth_sessions WHERE token_id = ? AND user_id = ?",
                     (payload["jti"], payload["user_id"]))


# ------------------------------------------------ PASSWORD HASHING
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ------------------------------------------------ AVATAR VALIDATION
def validate_avatar_file(raw_bytes: bytes, filename: str) -> Tuple[bytes, str]:
    """
    Strictly validates that uploaded avatar is .png or .jpg/.jpeg.
    Checks both file extension and image header magic bytes.
    Returns (raw_bytes, extension) on success, or raises ValueError.
    """
    if not raw_bytes:
        raise ValueError("Empty avatar file uploaded.")

    if len(raw_bytes) > 2 * 1024 * 1024:  # 2MB
        raise ValueError("Avatar file exceeds 2 MB limit.")

    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_IMAGE_EXTS:
        raise ValueError("Profile avatar must be a .png or .jpg file.")

    # Check magic bytes
    if ext == ".png":
        if not raw_bytes.startswith(PNG_MAGIC):
            raise ValueError("Invalid PNG image format (corrupted or fake file header).")
    elif ext in (".jpg", ".jpeg"):
        if not raw_bytes.startswith(JPEG_MAGIC):
            raise ValueError("Invalid JPG image format (corrupted or fake file header).")

    normalized_ext = ".jpg" if ext in (".jpg", ".jpeg") else ".png"
    return raw_bytes, normalized_ext


def save_avatar_file(user_id: int, raw_bytes: bytes, ext: str, conn) -> str:
    filename = f"avatar_{user_id}_{secrets.token_hex(16)}{ext}"
    content_type = "image/png" if ext == ".png" else "image/jpeg"
    conn.execute("INSERT INTO avatars (filename, user_id, data, content_type) VALUES (?, ?, ?, ?)",
                 (filename, user_id, raw_bytes, content_type))
    return f"assets/avatars/{filename}"


def get_avatar(filename):
    with get_db() as conn:
        return conn.execute("SELECT data, content_type FROM avatars WHERE filename = ?", (filename,)).fetchone()


# ------------------------------------------------ USER OPERATIONS
class ValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(" ".join(errors.values()))


def validate_credentials(username, password, registering=False):
    errors = {}
    if not isinstance(username, str) or not username.strip():
        errors["username"] = "Username is required and must be text."
    elif registering:
        username = username.strip()
        if not 3 <= len(username) <= 30:
            errors["username"] = "Username must be between 3 and 30 characters."
        elif not re.fullmatch(r"[a-zA-Z0-9_\-]+", username):
            errors["username"] = "Username can only contain letters, numbers, hyphens, and underscores."
    if not isinstance(password, str) or not password:
        errors["password"] = "Password is required and must be text."
    elif registering and len(password) < 8:
        errors["password"] = "Password must be at least 8 characters long."
    elif registering and len(password.encode("utf-8")) > 72:
        errors["password"] = "Password must be no more than 72 UTF-8 bytes."
    if errors:
        raise ValidationError(errors)


def register_user(username: str, password: str, avatar_bytes: Optional[bytes] = None,
                  avatar_filename: Optional[str] = None) -> Tuple[Dict[str, Any], str]:
    validate_credentials(username, password, registering=True)
    username = (username or "").strip()
    password = password or ""

    pw_hash = hash_password(password)

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        if cur.fetchone():
            raise ValueError("A user with that username already exists.")

        cur.execute(
            "INSERT INTO users (username, password_hash, avatar_url) VALUES (?, ?, ?) RETURNING id",
            (username, pw_hash, "")
        )
        user_id = cur.fetchone()["id"]

        avatar_url = ""
        if avatar_bytes is not None and avatar_filename:
            valid_bytes, ext = validate_avatar_file(avatar_bytes, avatar_filename)
            avatar_url = save_avatar_file(user_id, valid_bytes, ext, conn)
            cur.execute("UPDATE users SET avatar_url = ? WHERE id = ?", (avatar_url, user_id))

        conn.commit()

    token = create_token(user_id, username)
    user_info = {
        "id": user_id,
        "username": username,
        "avatar_url": avatar_url,
        "progress": {}
    }
    return user_info, token


def login_user(username: str, password: str) -> Tuple[Dict[str, Any], str]:
    validate_credentials(username, password)
    username = (username or "").strip()
    password = password or ""
    if not username or not password:
        raise ValueError("Username and password are required.")

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, password_hash, avatar_url FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        row = cur.fetchone()
        if not row:
            raise ValueError("Invalid username or password.")

        if not verify_password(password, row["password_hash"]):
            raise ValueError("Invalid username or password.")

        user_id = row["id"]
        avatar_url = row["avatar_url"] or ""

        cur.execute("SELECT progress_json FROM progress WHERE user_id = ?", (user_id,))
        prog_row = cur.fetchone()
        progress = {}
        if prog_row and prog_row["progress_json"]:
            try:
                progress = json.loads(prog_row["progress_json"])
            except Exception:
                progress = {}

    token = create_token(user_id, row["username"])
    user_info = {
        "id": user_id,
        "username": row["username"],
        "avatar_url": avatar_url,
        "progress": progress
    }
    return user_info, token


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, avatar_url FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            return None

        cur.execute("SELECT progress_json FROM progress WHERE user_id = ?", (user_id,))
        prog_row = cur.fetchone()
        progress = {}
        if prog_row and prog_row["progress_json"]:
            try:
                progress = json.loads(prog_row["progress_json"])
            except Exception:
                progress = {}

        return {
            "id": row["id"],
            "username": row["username"],
            "avatar_url": row["avatar_url"] or "",
            "progress": progress
        }


def update_user_avatar(user_id: int, raw_bytes: bytes, filename: str) -> str:
    valid_bytes, ext = validate_avatar_file(raw_bytes, filename)
    with get_db() as conn:
        avatar_url = save_avatar_file(user_id, valid_bytes, ext, conn)
        conn.execute("UPDATE users SET avatar_url = ? WHERE id = ?", (avatar_url, user_id))
        conn.commit()
    return avatar_url


def get_progress(user_id: int) -> Dict[str, Any]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT progress_json FROM progress WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row and row["progress_json"]:
            try:
                return json.loads(row["progress_json"])
            except Exception:
                return {}
        return {}


def save_progress(user_id: int, progress_data: Dict[str, Any]) -> None:
    progress_str = json.dumps(progress_data or {})
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO progress (user_id, progress_json, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                progress_json = excluded.progress_json,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, progress_str))
        conn.commit()
