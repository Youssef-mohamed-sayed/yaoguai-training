import hashlib
import secrets
import smtplib
from datetime import timedelta
from email.message import EmailMessage

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_user, logout_user
from flask_wtf.csrf import generate_csrf
from sqlalchemy import func, select

from ..extensions import db
from ..models import PasswordResetToken, User, now_utc
from ..security import authenticated_required, error, json_object
from ..services.rate_limit import allow_auth_attempt

auth_bp = Blueprint("auth", __name__)
hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2, hash_len=32, salt_len=16)


def user_json(user):
    return {"id": user.id, "username": user.username, "email": user.email,
            "is_admin": user.is_admin, "must_change_password": user.must_change_password,
            "level": user.level.name if user.level else None}


@auth_bp.get("/csrf")
def csrf_token():
    return jsonify(data={"csrf_token": generate_csrf()})


@auth_bp.get("/me")
def me():
    return jsonify(data={"user": user_json(current_user._get_current_object()) if current_user.is_authenticated else None})


@auth_bp.get("/session")
def session_state():
    """CSRF token and current user in one request (replaces two calls on every page load)."""
    user = user_json(current_user._get_current_object()) if current_user.is_authenticated else None
    return jsonify(data={"csrf_token": generate_csrf(), "user": user})


@auth_bp.post("/register")
def register():
    if not allow_auth_attempt("register", 5, 3600):
        return error("rate_limited", "Too many registration attempts. Try again later", 429)
    data = json_object()
    if data is None:
        return error("invalid_request", "Send a JSON object", 400)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    if not all(isinstance(item, str) for item in (username, email, password)):
        return error("invalid_fields", "Username, email, and password are required", 400)
    username = username.strip()
    if not 3 <= len(username) <= 32 or not username.replace("_", "").replace("-", "").isalnum():
        return error("invalid_username", "Use 3 to 32 letters, numbers, hyphens, or underscores", 422)
    if len(password) < 10 or len(password.encode("utf-8")) > 128:
        return error("invalid_password", "Use a password between 10 and 128 bytes", 422)
    try:
        email = validate_email(email.strip(), check_deliverability=False).normalized
    except (EmailNotValidError, AttributeError):
        return error("invalid_email", "Enter a valid email address", 422)
    existing = db.session.execute(select(User.id).where(
        (func.lower(User.username) == username.lower()) | (func.lower(User.email) == email.lower())
    )).first()
    if existing:
        return error("account_exists", "An account already uses that username or email", 409)
    user = User(username=username, email=email, password_hash=hasher.hash(password))
    db.session.add(user)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error("account_exists", "An account already uses that username or email", 409)
    login_user(user, remember=False, fresh=True)
    return jsonify(data={"user": user_json(user)}), 201


@auth_bp.post("/login")
def login():
    return authenticate(admin_only=False)


@auth_bp.post("/admin-login")
def admin_login():
    return authenticate(admin_only=True)


def authenticate(admin_only):
    bucket = "admin-login" if admin_only else "login"
    if not allow_auth_attempt(bucket, 10, 900):
        return error("rate_limited", "Too many sign-in attempts. Try again later", 429)
    data = json_object()
    if data is None or not isinstance(data.get("username"), str) or not isinstance(data.get("password"), str):
        return error("invalid_fields", "Username or email and password are required", 400)
    identity = data["username"].strip().lower()
    user = db.session.execute(select(User).where(
        (func.lower(User.username) == identity) | (func.lower(User.email) == identity)
    )).scalar_one_or_none()
    valid = False
    if user and user.is_active:
        try:
            valid = hasher.verify(user.password_hash, data["password"])
        except (VerifyMismatchError, InvalidHashError):
            pass
    if not valid or user.is_admin != admin_only:
        return error("invalid_credentials", "Username or password is incorrect", 401)
    if hasher.check_needs_rehash(user.password_hash):
        user.password_hash = hasher.hash(data["password"])
    user.last_seen_at = now_utc()
    db.session.commit()
    from flask import session
    session.clear()
    login_user(user, remember=False, fresh=True)
    return jsonify(data={"user": user_json(user)})


@auth_bp.post("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    from flask import session
    session.clear()
    return jsonify(data={"logged_out": True})


@auth_bp.post("/password")
@authenticated_required
def change_password():
    data = json_object()
    current_password = data.get("current_password") if data else None
    new_password = data.get("new_password") if data else None
    if not isinstance(current_password, str) or not isinstance(new_password, str) or len(new_password) < 10 or len(new_password.encode("utf-8")) > 128:
        return error("invalid_password", "Provide your current password and a new password of 10 to 128 bytes", 422)
    try:
        if not hasher.verify(current_user.password_hash, current_password):
            return error("invalid_password", "Current password is incorrect", 401)
    except (VerifyMismatchError, InvalidHashError):
        return error("invalid_password", "Current password is incorrect", 401)
    current_user.password_hash = hasher.hash(new_password)
    current_user.must_change_password = False
    db.session.commit()
    return jsonify(data={"password_changed": True, "user": user_json(current_user._get_current_object())})


def send_reset_email(user, token):
    host = current_app.config.get("MAIL_HOST")
    sender = current_app.config.get("MAIL_FROM")
    if not host or not sender:
        return False
    origin = current_app.config["PUBLIC_ORIGIN"].rstrip("/")
    message = EmailMessage()
    message["Subject"] = "Reset your Yaoguai Training password"
    message["From"] = sender
    message["To"] = user.email
    message.set_content(f"Reset your password within 30 minutes: {origin}/reset-password?token={token}\n\nIf you did not request this, ignore this message.")
    with smtplib.SMTP(host, current_app.config["MAIL_PORT"], timeout=10) as smtp:
        smtp.starttls()
        username = current_app.config.get("MAIL_USERNAME")
        password = current_app.config.get("MAIL_PASSWORD")
        if username and password:
            smtp.login(username, password)
        smtp.send_message(message)
    return True


@auth_bp.post("/password-reset-requests")
def request_password_reset():
    if not allow_auth_attempt("password-reset", 4, 3600):
        return jsonify(data={"message": "If the account exists, password reset instructions will be sent"}), 202
    data = json_object()
    email = data.get("email", "") if data else ""
    if not isinstance(email, str):
        return error("invalid_email", "Enter a valid email address", 422)
    user = db.session.execute(select(User).where(func.lower(User.email) == email.strip().lower())).scalar_one_or_none()
    if user and user.is_active:
        token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(token.encode()).hexdigest()
        record = PasswordResetToken(user_id=user.id, token_digest=digest,
                                    expires_at=now_utc() + timedelta(minutes=current_app.config["PASSWORD_RESET_TTL_MINUTES"]))
        db.session.add(record)
        db.session.commit()
        try:
            send_reset_email(user, token)
        except (OSError, smtplib.SMTPException):
            current_app.logger.exception("Password reset email delivery failed")
    return jsonify(data={"message": "If the account exists, password reset instructions will be sent"}), 202


@auth_bp.post("/password-resets")
def reset_password():
    data = json_object()
    token = data.get("token") if data else None
    password = data.get("password") if data else None
    if not isinstance(token, str) or not isinstance(password, str) or len(password) < 10 or len(password.encode("utf-8")) > 128:
        return error("invalid_reset", "A valid reset token and a password of at least 10 characters are required", 422)
    digest = hashlib.sha256(token.encode()).hexdigest()
    record = db.session.execute(select(PasswordResetToken).where(
        PasswordResetToken.token_digest == digest,
        PasswordResetToken.used_at.is_(None),
        PasswordResetToken.expires_at > now_utc(),
    )).scalar_one_or_none()
    if not record:
        return error("invalid_reset", "This reset link is invalid or expired", 400)
    record.user.password_hash = hasher.hash(password)
    record.user.must_change_password = False
    record.used_at = now_utc()
    db.session.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == record.user_id,
        PasswordResetToken.id != record.id,
        PasswordResetToken.used_at.is_(None),
    ).update({PasswordResetToken.used_at: now_utc()}, synchronize_session=False)
    db.session.commit()
    return jsonify(data={"password_changed": True})

