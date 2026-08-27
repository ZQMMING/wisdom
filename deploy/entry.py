# -*- coding: utf-8 -*-
"""C2 production ASGI entry (Plan A: deploy-layer, zero src changes).

This module wires the production ``PostgresAuthDB`` into the existing
``create_app(db_ops=...)`` seam (``backend/src/tongshu/api/app.py:583-585``)
so that ``/v1/auth/*`` endpoints become end-to-end reachable in production.

Design contract (see ``docs/audit/stage_c/C2_PROD_WIRE_PLAN.md`` §2.3.1 and
``C2_PROD_WIRE_SIGNED.md`` acceptance ruling):

  1. ``src/`` MUST stay untouched -- this is a HARD RED LINE.
  2. ``build_app()`` is the only function that touches the DB at import time.
     It runs a ``db_available()`` fail-closed probe FIRST, then constructs
     ``PostgresAuthDB(dsn)`` and passes it to ``create_app(db_ops=...)``.
  3. Module-level ``app = build_app()`` -- ``uvicorn deploy.entry:app`` boots
     straight into a wired, fail-fast-checked production ASGI instance.
  4. ``create_app()`` itself calls ``ensure_auth_ready()`` (B-09 R2 rework)
     so ``TONGSHU_AUTH_SECRET`` is enforced by the framework; we do NOT
     duplicate that check here.

Out of scope for this entry (deferred change orders per
``C2_PROD_WIRE_SIGNED.md``):

  - C2.1: runtime OperationalError wrapping (-> 503) on identity gateway.
  - C2.2: monitoring / alerting hooks.
  - C2.3: gradual rollout SOP (G0 permissive -> G1 small -> G2 full).
"""
from __future__ import annotations

import logging
import os
import sys

# Ensure ``src`` is on sys.path so this entry works both as
# ``uvicorn deploy.entry:app`` (package layout) and ``python deploy/entry.py``.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC_PATH = os.path.join(_REPO_ROOT, "src")
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

from tongshu.api.app import create_app  # noqa: E402
from tongshu.db.auth_db import PostgresAuthDB  # noqa: E402
from tongshu.db.config import db_available, get_dsn  # noqa: E402

log = logging.getLogger("deploy.entry")


def build_app():
    """Build the production ASGI app with db_ops wired.

    Returns:
        FastAPI: a ``create_app(db_ops=PostgresAuthDB(dsn))`` instance.

    Raises:
        RuntimeError: if ``db_available()`` probe fails (fail-closed at
            startup so process manager / orchestrator can restart cleanly).
    """
    dsn = get_dsn()
    ok, err = db_available(dsn, timeout=3)
    if not ok:
        # Truncate err to keep log line bounded; do NOT leak full DSN.
        msg = f"[C2] DB unreachable at startup: {err[:120]}"
        log.error(msg)
        raise RuntimeError(msg)
    log.info("[C2] DB probe OK; wiring PostgresAuthDB into create_app(db_ops=...)")
    return create_app(db_ops=PostgresAuthDB(dsn=dsn))


# Module-level ASGI app -- ``uvicorn deploy.entry:app`` boots directly into
# the production-wired FastAPI instance.
app = build_app()
