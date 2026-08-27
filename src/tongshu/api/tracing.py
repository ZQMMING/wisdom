"""Observability middleware for the OTC-G API (V3.6 §36).

Provides, for every HTTP request:

  - `trace_id`: read from `X-Trace-ID` header or generated as `TRACE-<hex8>`;
    stored in `scope["state"]["trace_id"]` (readable by route handlers and
    exception handlers via `request.state.trace_id`), and written back as an
    `X-Trace-ID` response header.
  - `request_id`: generated as `RR-<hex8>`, stored in
    `scope["state"]["request_id"]` for the §32 error envelope.
  - `X-Process-Time-Ms`: full request wall-clock (middleware → handler →
    response), giving the frontend/backoffice the network+middleware overhead
    on top of the renderer-only `X-Render-Time-Ms` set by the pipeline.
  - `X-Auth-Would-Deny`: B-09 STAGE-B flag-observation header. When the
    TONGSHU_AUTH_ENFORCED flag is OFF and a route's auth probe would have
    rejected the request, the dep tags ``request.state.auth_would_deny`` and
    the middleware propagates it as ``X-Auth-Would-Deny: 1``. This lets
    Hermes monitor migration readiness before flipping enforcement on
    (per B09_AUTH_PROPOSAL §Q9 and §12切流检查清单).

Deprecated-path telemetry (V3.6 §25-26): paths under `/api/` log a structured
`[Deprecated]` line per call and increment an in-memory per-path counter.
The counter is exposed at `/health` (`deprecated_calls`), NOT emitted as an
immediate alert — the team reads it periodically to find "钉子户" callers
before the 2027-08-18 sunset.
"""

from __future__ import annotations
import logging
import threading
import time
import uuid

log = logging.getLogger(__name__)

SUNSET_DATE = "2027-08-18"
DEPRECATED_PREFIX = "/api/"
_DEPRECATED_COUNTS: dict[str, int] = {}
_COUNTS_LOCK = threading.Lock()


def deprecated_counts() -> dict[str, int]:
    """Snapshot of deprecated-path call counts (path → count)."""
    with _COUNTS_LOCK:
        return dict(_DEPRECATED_COUNTS)


def reset_deprecated_counts() -> None:
    """Clear the deprecated-path counter (test isolation)."""
    with _COUNTS_LOCK:
        _DEPRECATED_COUNTS.clear()


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


class TraceMiddleware:
    """ASGI middleware: trace id, request id, timing, deprecated telemetry."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        path = scope.get("path", "")
        headers = dict(scope.get("headers") or [])

        raw_trace = headers.get(b"x-trace-id")
        trace_id = (
            raw_trace.decode("utf-8", "replace").strip() if raw_trace else _new_id("TRACE")
        )
        request_id = _new_id("RR")

        scope.setdefault("state", {})
        scope["state"]["trace_id"] = trace_id
        scope["state"]["request_id"] = request_id

        is_deprecated = path.startswith(DEPRECATED_PREFIX)
        if is_deprecated:
            with _COUNTS_LOCK:
                _DEPRECATED_COUNTS[path] = _DEPRECATED_COUNTS.get(path, 0) + 1
            ua = headers.get(b"user-agent", b"").decode("utf-8", "replace")
            client = headers.get(b"x-forwarded-for", headers.get(b"host", b"")).decode(
                "utf-8", "replace"
            )
            log.warning(
                "[Deprecated] path=%s ua=%s client=%s trace_id=%s",
                path, ua or "-", client or "-", trace_id,
            )

        start = time.monotonic()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                hdrs = list(message.get("headers", []))
                elapsed_ms = int(round((time.monotonic() - start) * 1000))
                hdrs.append((b"x-trace-id", trace_id.encode()))
                hdrs.append((b"x-process-time-ms", str(elapsed_ms).encode()))
                if is_deprecated:
                    hdrs.append((b"deprecation", b"true"))
                    hdrs.append((b"sunset", SUNSET_DATE.encode()))
                    hdrs.append(
                        (
                            b"x-deprecated-warning",
                            (
                                f"This API path is deprecated; migrate to /v1/* "
                                f"before {SUNSET_DATE}."
                            ).encode(),
                        )
                    )
                # B-09 STAGE-B: propagate the auth-would-deny flag (per B09_AUTH_PROPOSAL §Q9).
                # The dep set request.state.auth_would_deny = reason; we expose it as
                # a 1/0 header for log/curl observability.
                state = scope.get("state") or {}
                would_deny = state.get("auth_would_deny")
                if would_deny:
                    hdrs.append((b"x-auth-would-deny", b"1"))
                message["headers"] = hdrs
            await send(message)

        await self.app(scope, receive, send_wrapper)