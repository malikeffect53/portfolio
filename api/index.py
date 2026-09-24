import os
import sys
import traceback

# Add project root directory to sys.path so app and seed can be imported
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

_import_error = None
try:
    from app import app as _flask_app
except Exception:
    _import_error = traceback.format_exc()
    print(f"[FATAL VERCEL STARTUP ERROR]\n{_import_error}", flush=True)

if _import_error:
    from flask import Flask, Response
    app = Flask(__name__)
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        return Response(
            f"Vercel Serverless Function Startup Error Traceback:\n\n{_import_error}",
            status=500,
            mimetype="text/plain; charset=utf-8"
        )
else:
    class VercelPathFix:
        """WSGI middleware to ensure Flask receives the true client request path from Vercel edge rewrites."""
        def __init__(self, wsgi_app):
            self.wsgi_app = wsgi_app

        def __call__(self, environ, start_response):
            req_uri = environ.get("REQUEST_URI") or environ.get("RAW_URI")
            matched = environ.get("HTTP_X_MATCHED_PATH")
            if req_uri:
                clean_path = req_uri.split("?")[0]
                if clean_path and clean_path not in ("/api/index", "/api/index.py"):
                    environ["PATH_INFO"] = clean_path
            elif matched and matched not in ("/api/index", "/api/index.py"):
                environ["PATH_INFO"] = matched
            elif environ.get("PATH_INFO") in ("/api/index", "/api/index.py"):
                environ["PATH_INFO"] = "/"
            return self.wsgi_app(environ, start_response)

    _flask_app.wsgi_app = VercelPathFix(_flask_app.wsgi_app)
    app = _flask_app

# Vercel Serverless WSGI callable
handler = app
