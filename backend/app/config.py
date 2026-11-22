import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env.local")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///yaoguai-training.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}
    SESSION_TYPE = "sqlalchemy"
    SESSION_SQLALCHEMY_TABLE = "server_sessions"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "").lower() in {"1", "true", "yes"}
    SESSION_COOKIE_NAME = "yaoguai_session"
    WTF_CSRF_TIME_LIMIT = 3600
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    MAIL_HOST = os.environ.get("MAIL_HOST")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_FROM = os.environ.get("MAIL_FROM")
    PUBLIC_ORIGIN = os.environ.get("PUBLIC_ORIGIN", "http://localhost:5173")
    PASSWORD_RESET_TTL_MINUTES = 30

