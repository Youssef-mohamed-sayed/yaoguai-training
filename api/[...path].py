"""Catch-all Vercel Python runtime for the central Flask and mounted apps."""
from backend.wsgi import app as wsgi_app


class SiteAndApi:
    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path == "/api/site":
            environ = environ.copy()
            environ["PATH_INFO"] = "/"
        elif path.startswith("/api/site/"):
            environ = environ.copy()
            environ["PATH_INFO"] = path[len("/api/site"):]
        return wsgi_app(environ, start_response)


app = SiteAndApi()
