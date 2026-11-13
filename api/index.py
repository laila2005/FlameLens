"""Vercel serverless entry point: exposes the FlameLens FastAPI app.

Vercel's Python runtime looks for an ASGI app named `app` in this file. All routes live under /api,
so vercel.json rewrites /api/(.*) (and /docs, /openapi.json) here and the original path is kept.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.main import app  # noqa: E402,F401
