"""Single-segment Vercel entry point for central and mounted WSGI routes."""
from urllib.parse import parse_qsl, urlencode

from backend.wsgi import app as wsgi_app


class PathDispatch:
    def __call__(self, environ, start_response):
        query = parse_qsl(environ.get("QUERY_STRING", ""), keep_blank_values=True)
        route = next((value for key, value in query if key == "route"), "")
        if not route.startswith(("/api/", "/network", "/linux", "/programming", "/crypto", "/admin", "/login", "/register", "/forgot-password", "/profile", "/reset-password")):
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return [b"Not found"]
        if route not in {"/network", "/linux", "/programming", "/crypto", "/admin", "/admin/login", "/login", "/register", "/forgot-password", "/profile", "/reset-password"} and not route.startswith(
            ("/api/", "/network/", "/linux/", "/programming/", "/crypto/")
        ):
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return [b"Not found"]
        environ = environ.copy()
        environ["PATH_INFO"] = route
        environ["QUERY_STRING"] = urlencode([(key, value) for key, value in query if key != "route"])
        return wsgi_app(environ, start_response)


app = PathDispatch()

