import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app import create_app

app = create_app()

if __name__ == "__main__":
    from werkzeug.serving import run_simple
    from backend.wsgi import app as full_application
    run_simple("127.0.0.1", 5000, full_application, use_reloader=True, use_debugger=True)

