"""Single-domain WSGI composition for the four preserved learning products."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Callable

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.utils import send_from_directory

ROOT = Path(__file__).resolve().parents[1]
PLATFORMS = ROOT / "platforms"
sys.path.insert(0, str(ROOT / "backend"))

from app import create_app  # noqa: E402


class PrefixedApplication:
    """Mount a WSGI app while retaining SCRIPT_NAME and stripping its URL prefix."""
    def __init__(self, application: Callable, prefix: str, preserve_path: bool = False):
        self.application, self.prefix, self.preserve_path = application, prefix, preserve_path

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "/")
        original_uri = environ.get("RAW_URI", environ.get("REQUEST_URI", ""))
        if self.prefix == "/crypto" and original_uri.split("?", 1)[0] == "/crypto":
            from werkzeug.wrappers import Response
            return Response(status=308, headers={"Location": f"{self.prefix}/"})(environ, start_response)
        environ = environ.copy()
        environ["SCRIPT_NAME"] = self.prefix
        if self.preserve_path:
            # Network's course URLs include /network; its asset endpoint remains app-relative.
            environ["PATH_INFO"] = path if path.startswith("/assets/") else ("/network" if path == "/" else "/network" + path)
        return self.application(environ, start_response)


class StaticCourse:
    def __init__(self, directory: Path, prefix: str, fallback: str = "index.html"):
        self.directory, self.prefix, self.fallback = directory.resolve(), prefix, fallback

    def __call__(self, environ, start_response):
        from werkzeug.wrappers import Request
        request = Request(environ)
        relative = request.path.lstrip("/")
        if relative == "training-bridge.js":
            return send_from_directory(ROOT / "public", relative)(environ, start_response)
        if not relative or relative == self.prefix.lstrip("/"):
            relative = self.fallback
        candidate = (self.directory / relative).resolve()
        if self.directory not in candidate.parents and candidate != self.directory:
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return [b"Not found"]
        if not candidate.is_file():
            candidate = self.directory / self.fallback
        response = send_from_directory(self.directory, candidate.relative_to(self.directory).as_posix(), environ)
        return response(environ, start_response)


def network_application(central_app):
    sys.path.insert(0, str(PLATFORMS / "network"))
    from network_yaoguai import create_app as create_network_app
    base = PLATFORMS / "network"
    app = create_network_app({
        "CONTENT_ROOT": base / "network-essentials",
        "PUBLIC_ROOT": base / "public",
        "CENTRAL_SECRET_KEY": central_app.secret_key,
        "CENTRAL_COOKIE_SECURE": central_app.config["SESSION_COOKIE_SECURE"],
        "CENTRAL_DATABASE_URI": central_app.config["SQLALCHEMY_DATABASE_URI"],
        "CENTRAL_SESSION_INTERFACE": central_app.session_interface,
        "TESTING": False,
    })
    return PrefixedApplication(app, "/network", preserve_path=True)


def crypto_application():
    scripts = PLATFORMS / "crypto" / "scripts"
    sys.path.insert(0, str(scripts))
    spec = importlib.util.spec_from_file_location("yaoguai_crypto_wsgi", scripts / "app.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    app = module.app

    @app.before_request
    def centralize_crypto_identity():
        from flask import jsonify, request
        if request.path.startswith(("/api/auth/", "/api/user/progress")):
            return jsonify(success=False, error="Sign in through Yaoguai Training to synchronize account activity."), 410

    return PrefixedApplication(app, "/crypto")


central = create_app()
network = network_application(central)
crypto = crypto_application()
linux = StaticCourse(PLATFORMS / "linux" / "dist", "/linux")
programming = StaticCourse(PLATFORMS / "programming" / "public", "/programming")

# Vercel and local Gunicorn both invoke this WSGI object. API routes stay in Flask;
# each preserved course keeps its original application and is mounted by path.
app = DispatcherMiddleware(central, {
    "/network": network,
    "/linux": linux,
    "/programming": programming,
    "/crypto": crypto,
})
