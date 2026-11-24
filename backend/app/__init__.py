import os
from datetime import timedelta

from flask import Flask, jsonify, redirect, request, send_from_directory
from flask_login import current_user
from flask_wtf.csrf import CSRFError
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config
from .extensions import csrf, db, login_manager, migrate


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        if os.environ.get("VERCEL") or app.config.get("ENVIRONMENT") == "production":
            raise RuntimeError("SECRET_KEY must be set in production")
        app.config["SECRET_KEY"] = os.environ.get("DEV_SECRET_KEY", "local-only-change-me")
    if os.environ.get("VERCEL") or app.config.get("ENVIRONMENT") == "production":
        if not str(app.config.get("SQLALCHEMY_DATABASE_URI", "")).startswith(("postgres://", "postgresql://", "postgresql+psycopg://")):
            raise RuntimeError("DATABASE_URL must point to Neon PostgreSQL in production")
    if os.environ.get("VERCEL"):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    database_url = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if database_url.startswith("postgres://"):
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    app.config["SESSION_COOKIE_SECURE"] = bool(
        app.config.get("SESSION_COOKIE_SECURE") or os.environ.get("VERCEL")
        or app.config.get("ENVIRONMENT") == "production"
    )
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=14)
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        # Serverless: each instance serves one request at a time, so keep the pool small to spare Neon connections.
        **({"pool_size": int(os.environ.get("DB_POOL_SIZE", "2")), "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "1"))}
           if app.config["SQLALCHEMY_DATABASE_URI"].startswith(("postgresql://", "postgresql+psycopg://")) else {}),
    }
    db.init_app(app)
    migrate.init_app(app, db, directory=os.path.join(os.path.dirname(__file__), "..", "migrations"))
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = None

    from . import models  # noqa: F401
    from .routes.admin import admin_bp
    from .routes.assignments import assignments_bp
    from .routes.auth import auth_bp
    from .routes.catalog import catalog_bp
    from .routes.progress import progress_bp
    from .services.rate_limit import allow_auth_attempt
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(catalog_bp, url_prefix="/api")
    app.register_blueprint(progress_bp, url_prefix="/api")
    app.register_blueprint(assignments_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    @app.before_request
    def api_rate_limit():
        if (request.path.startswith("/api/") and request.method not in {"GET", "HEAD", "OPTIONS"}
                and not request.path.startswith("/api/auth/")
                and not allow_auth_attempt("api-write", 240, 60)):
            return jsonify(error={"code": "rate_limited", "message": "Too many requests. Try again shortly."}), 429

    @app.get("/admin")
    def admin_portal():
        if not current_user.is_authenticated or not current_user.is_admin or not current_user.is_active:
            return redirect("/admin/login")
        if current_user.must_change_password:
            return redirect("/profile?required=1&next=%2Fadmin")
        from pathlib import Path
        build = Path(__file__).resolve().parents[2] / "dist"
        return send_from_directory(build, "index.html")

    @app.get("/")
    @app.get("/<path:asset_path>")
    def portal(asset_path="index.html"):
        # Flask serves the root portal and keeps /admin and password-reset URLs refreshable.
        from pathlib import Path
        build = Path(__file__).resolve().parents[2] / "dist"
        candidate = (build / asset_path).resolve()
        if build.resolve() not in candidate.parents and candidate != build.resolve():
            return jsonify(error={"code": "not_found", "message": "Resource not found"}), 404
        if candidate.is_file():
            return send_from_directory(build, candidate.relative_to(build).as_posix())
        if not asset_path.startswith(("api/", "assets/", "src/")):
            return send_from_directory(build, "index.html")
        return jsonify(error={"code": "not_found", "message": "Resource not found"}), 404

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(models.User, user_id)

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if request.path.startswith("/api/"):
            response.headers.setdefault("Cache-Control", "no-store")
        return response

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith("/api/"):
            return jsonify(error={"code": "not_found", "message": "Resource not found"}), 404
        return _error

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()
        app.logger.exception("Unhandled application error")
        return jsonify(error={"code": "internal_error", "message": "The request could not be completed"}), 500

    @app.errorhandler(CSRFError)
    def csrf_error(_error):
        return jsonify(error={"code": "csrf_failed", "message": "Refresh the page and try again"}), 400

    return app

