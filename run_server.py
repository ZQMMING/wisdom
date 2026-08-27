"""TONGSHU API dev server.

Usage (from backend/):
    PYTHONPATH=src python run_server.py
    # -> http://127.0.0.1:8000/docs

Env:
    TONGSHU_HOST      (default 0.0.0.0)
    TONGSHU_PORT      (default 8000)
    TONGSHU_CORS_ORIGINS  comma-separated (default *)
    DEEPSEEK_API_KEY  set → real LLM renderer; unset → deterministic Stub
"""

from __future__ import annotations
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import uvicorn

from tongshu.api.app import create_app

if __name__ == "__main__":
    import os
    host = os.environ.get("TONGSHU_HOST", "127.0.0.1")  # B3: 仅本地，禁止公网
    port = int(os.environ.get("TONGSHU_PORT", "8000"))
    # Factory mode: create_app() without db_ops → auth routes return 503
    # For production, pass db_ops=PostgresAuthDB(...)
    app = create_app()
    uvicorn.run(app, host=host, port=port, log_level="info")
