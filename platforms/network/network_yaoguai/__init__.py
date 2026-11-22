"""Flask application and deployment-neutral paths."""
from pathlib import Path

from flask import Flask, render_template

from .course import Course
from .routes import site

ROOT = Path(__file__).resolve().parents[1]


def create_app(config=None):
    app = Flask(__name__, static_folder=None)
    app.config.from_mapping(CONTENT_ROOT=ROOT / "network-essentials",
                            PUBLIC_ROOT=ROOT / "public", MAX_CONTENT_LENGTH=4096)
    if config:
        app.config.update(config)
    # The central application and this preserved course share the same server-side
    # session store and secret, so a single Yaoguai sign-in is valid on this route.
    from app.extensions import csrf, db, login_manager
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get(
        "CENTRAL_DATABASE_URI", app.config.get("SQLALCHEMY_DATABASE_URI", "sqlite:///network-standalone.db")
    )
    app.config.update(
        SECRET_KEY=app.config.get("CENTRAL_SECRET_KEY") or "local-only-change-me",
        SESSION_COOKIE_NAME="yaoguai_session",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=app.config.get("CENTRAL_COOKIE_SECURE", False),
    )
    app.session_interface = app.config.get("CENTRAL_SESSION_INTERFACE", app.session_interface)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    app.extensions["course"] = Course(Path(app.config["CONTENT_ROOT"]))
    app.register_blueprint(site)

    @app.context_processor
    def shared():
        return {"course": app.extensions["course"]}

    @app.after_request
    def security_headers(response):
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' https:; "
            "font-src 'self'; connect-src 'self'; form-action 'self'; "
            "frame-ancestors 'none'; base-uri 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if response.mimetype == "application/json":
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(404)
    def not_found(error):
        return render_template("error.html", code=404, title="Page not found",
                               message="This route does not lead to a course page."), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("error.html", code=500, title="Something went wrong",
                               message="The course could not load this page. Try again in a moment."), 500

    return app
