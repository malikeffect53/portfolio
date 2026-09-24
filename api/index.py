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
    app = _flask_app

# Vercel Serverless WSGI callable
handler = app

