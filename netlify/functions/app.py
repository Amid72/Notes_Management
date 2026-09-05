import os
import sys

# Ensure project root directory is in sys.path so app can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import serverless_wsgi
from app import app


def handler(event, context):
    """
    Netlify Serverless Function handler for the NotesVault Flask application.
    Handles AWS Lambda / Netlify Function events and converts them into WSGI requests.
    """
    # Defensive path fix: If Netlify preserves or prefixes the function path,
    # normalize it so Flask routes like '/', '/login', '/dashboard' match properly.
    path = event.get("path", "")
    prefix = "/.netlify/functions/app"

    if path.startswith(prefix):
        stripped = path[len(prefix):]
        event["path"] = stripped if stripped.startswith("/") else "/" + stripped

    # Ensure empty path defaults to "/"
    if not event.get("path"):
        event["path"] = "/"

    return serverless_wsgi.handle_request(app, event, context)
