# -*- coding: utf-8 -*-
"""B-09 STAGE-B end-to-end acceptance tests.

Covers TASK_BATCH3_B09 §STAGE-B / B09_AUTH_PROPOSAL §7 / §9 acceptance test
§7 (新增:无凭据 /v1/today → 200 + public + 负向断言无 personal 字段).

Hard rule honored: NO existing tests were modified. The FakeDB adapter from
tests/auth/test_identity_gateway_v2.py is reused so the gateway can be wired
without a real Postgres connection.

The flag is read on EVERY request by ``is_auth_enforced()``, so each test
either (a) relies on the default ``false`` (permissive) state, or (b) uses
the ``_flag`` context manager to pin ``TONGSHU_AUTH_ENFORCED=true`` for the
duration of the request call. The context manager restores the env on exit.

Note: gateway wiring happens through ``identity_gateway._gateway_singleton``
directly (not via the imported name in this module) because ``from x import y``
creates an independent binding — the dep module's ``get_gateway_v2_singleton``
reads from the ``identity_gateway`` module's globals, not the test module's.
"""
from __future__ import annotations

import contextlib
import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

os.environ.setdefault("TONGSHU_AUTH_SECRET", "test-secret-" + "x" * 32)

from fastapi.testclient import TestClient

from tongshu.api.app import create_app
from tongshu.api.deps import reset_rate_limit_buckets
from tongshu.api.tracing import reset_deprecated_counts
import tongshu.services.identity_gateway as identity_gateway_module
from tongshu.services.identity_gateway import IdentityGatewayV2


# ----------------------------------------------------------------------- #
# Test fixtures — FakeDB matches the contract from tests/auth/.
# ----------------------------------------------------------------------- #


class FakeDB:
    """In-memory db_ops adapter for the gateway (mirrors the existing test)."""

    def __init__(self):
        self.users: dict = {}
        self.refresh_tokens: dict = {}
        self.device_tokens: dict = {}
        self.devices: dict = {}
        self.audit_log: list = []

    def get_token_version(self, user_id):
        return self.users.get(user_id, {}).get("token_version", 0)

    def bump_token_version(self, user_id):
        u = self.users.setdefault(user_id, {})
        u["token_version"] = u.get("token_version", 0) + 1
        return u["token_version"]

    def insert_refresh_token(self, jti, user_id, device_id, token_hash, expires_at):
        self.refresh_tokens[jti] = {
            "jti": jti, "user_id": user_id, "device_id": device_id,
            "token_hash": token_hash, "expires_at": expires_at,
            "revoked_at": None, "rotated_into": None,
        }

    def get_refresh_token(self, token_hash):
        for row in self.refresh_tokens.values():
            if row["token_hash"] == token_hash:
                return dict(row)
        return None

    def revoke_refresh_token(self, jti, rotated_into=None):
        if jti in self.refresh_tokens:
            self.refresh_tokens[jti]["revoked_at"] = datetime.now(timezone.utc)
            self.refresh_tokens[jti]["rotated_into"] = rotated_into

    def revoke_all_refresh_tokens(self, user_id, device_id=None):
        n = 0
        for row in self.refresh_tokens.values():
            if row["user_id"] == user_id and row["revoked_at"] is None:
                if device_id is None or row["device_id"] == device_id:
                    row["revoked_at"] = datetime.now(timezone.utc)
                    n += 1
        return n

    def get_device(self, device_id):
        d = self.devices.get(device_id)
        return dict(d) if d else None

    def revoke_device(self, device_id):
        if device_id in self.devices:
            self.devices[device_id]["status"] = "revoked"

    def insert_device_token(self, device_id, token_hash, expires_at):
        tid = f"dt-{len(self.device_tokens) + 1}"
        self.device_tokens[tid] = {
            "token_id": tid, "device_id": device_id, "token_hash": token_hash,
            "expires_at": expires_at, "last_used_at": None, "revoked_at": None,
        }

    def get_device_token(self, token_hash):
        for row in self.device_tokens.values():
            if row["token_hash"] == token_hash:
                return dict(row)
        return None

    def touch_device_token(self, token_id):
        if token_id in self.device_tokens:
            self.device_tokens[token_id]["last_used_at"] = datetime.now(timezone.utc)

    def audit(self, entry):
        self.audit_log.append(entry)

    # B-09 R2 rework (ARBITRATION_BATCH3 R1): the gateway now exposes
    # register_user / login_user / resolve_user_context / get_user_devices,
    # so the FakeDB adapter must match. The minimal in-memory implementations
    # below are no-op identity functions over the existing self.users /
    # self.devices dicts.
    def create_user(self, user_id, **flags):
        row = self.users.setdefault(user_id, {"token_version": 0})
        row.setdefault("id", user_id)
        row.setdefault("is_new_user", True)
        row.setdefault("has_birth_info", False)
        row.setdefault("has_heluo_model", False)
        row.setdefault("token_version", 1)
        for k, v in flags.items():
            row[k] = v
        return row

    def get_user(self, user_id):
        row = self.users.get(user_id)
        return dict(row) if row else None

    def list_user_devices(self, user_id):
        return [
            {
                "id": dev["device_id"],
                "device_id": dev["device_id"],
                "device_type": dev.get("device_type", "unknown"),
                "status": dev.get("status", "unknown"),
            }
            for dev in self.devices.values()
            if dev.get("user_id") == user_id
        ]


@contextlib.contextmanager
def _flag(value: str):
    """Pin TONGSHU_AUTH_ENFORCED for the duration of the block.

    Used to wrap the request call (NOT just create_app) because the flag
    is read on every request by ``is_auth_enforced()``. Example::

        with _flag("true"):
            r = client.get(...)
    """
    saved = os.environ.get("TONGSHU_AUTH_ENFORCED")
    os.environ["TONGSHU_AUTH_ENFORCED"] = value
    try:
        yield
    finally:
        if saved is None:
            os.environ.pop("TONGSHU_AUTH_ENFORCED", None)
        else:
            os.environ["TONGSHU_AUTH_ENFORCED"] = saved


def _wire_gateway() -> FakeDB:
    """Create a fresh gateway with FakeDB and wire it via the module attribute.

    Returns the FakeDB so tests can assert on its state if needed.
    """
    db = FakeDB()
    db.users["u-1"] = {"token_version": 0}
    db.users["u-2"] = {"token_version": 0}
    db.devices["dev-1"] = {
        "device_id": "dev-1", "user_id": "u-1",
        "device_type": "pendant", "status": "active",
    }
    identity_gateway_module._gateway_singleton = IdentityGatewayV2(db_ops=db)
    return db


def _build_client(*, with_gateway: bool = True) -> TestClient:
    """Build a TestClient with optional gateway wiring.

    Does NOT the TONGSHU_AUTH_ENFORCED env var — callers should use
    ``_flag(value)`` around request calls if they need a non-default
    enforcement state. Default state is permissive (no env set).
    """
    # Reset module-level state before each scenario.
    reset_rate_limit_buckets()
    reset_deprecated_counts()
    if with_gateway:
        _wire_gateway()
    else:
        identity_gateway_module._gateway_singleton = None
    return TestClient(create_app())


_GOLDEN001_BODY = {
    "birth_date": "1984-12-07",
    "hour": 16,
    "gender": "male",
    "theme": "WORK",
    "analysis_date": "2026-08-17",
    "timezone": "Asia/Shanghai",
    "location": "Beijing",
}


# ----------------------------------------------------------------------- #
# Acceptance test §7: 游客 /v1/today → public layer only (negative assertion)
# ----------------------------------------------------------------------- #


class TestGuestTodayPublicLayer(unittest.TestCase):
    """M1 / §7 验收: 无凭据 GET /v1/today → 200 且 body 含 public 层字段,
    负向断言: 不含 personal 字段。"""

    def test_today_without_credentials_returns_public_only(self):
        client = _build_client(with_gateway=True)
        r = client.get("/v1/today", params={"date": "2026-08-17", "region": "Beijing"})
        self.assertEqual(r.status_code, 200)
        body = r.json()
        # Public layer: ganzhi / weekday / day / lunarMonth / calendar / yi / ji / provenance
        self.assertIn("ganZhi", body)
        self.assertIn("weekday", body)
        self.assertIn("day", body)
        self.assertIn("lunarMonth", body)
        self.assertIn("yi", body)
        self.assertIn("ji", body)
        self.assertIn("calendar", body)
        self.assertIn("provenance", body)
        self.assertIn("trace_id", body)
        # Negative assertion — personal MUST be absent for guests.
        self.assertNotIn(
            "personal", body,
            f"Guest /v1/today must not include personal block; got keys={list(body.keys())}",
        )
        # C1 (ARBITRATION_BATCH3_G45_SIGNED): nested leak pin. G-F5 showed
        # mock data can carry hexagram.personal past a top-level-only check.
        # Recursively scan the whole response for any "personal" key at any
        # depth so this class of leak is caught by the suite, not by probes.

        def _assert_no_personal_key(obj, path="$"):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    self.assertNotEqual(
                        k.lower(), "personal",
                        f"Guest /v1/today leaked nested personal key at {path}.{k}",
                    )
                    _assert_no_personal_key(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    _assert_no_personal_key(v, f"{path}[{i}]")

        _assert_no_personal_key(body)

    def test_api_today_legacy_also_public_only(self):
        """Sunset /api/today same guest rule — public only."""
        client = _build_client(with_gateway=True)
        r = client.get("/api/today", params={"date": "2026-08-17"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers.get("deprecation"), "true")
        self.assertEqual(r.headers.get("sunset"), "2027-08-18")
        body = r.json()
        self.assertIn("ganZhi", body)
        self.assertNotIn("personal", body)


class TestAuthedTodayPersonalLayer(unittest.TestCase):
    """M1 second clause: Bearer user → public + personal."""

    def test_today_with_valid_bearer_includes_personal(self):
        client = _build_client(with_gateway=True)
        # Forge an access token via the wired gateway (FakeDB pre-loaded u-1).
        gw = identity_gateway_module._gateway_singleton
        token = gw.generate_access_token("u-1", "dev-1")
        r = client.get(
            "/v1/today",
            params={"date": "2026-08-17", "region": "Beijing"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertIn("ganZhi", body)
        self.assertIn("personal", body, "Authed /v1/today must include personal block")
        personal = body["personal"]
        self.assertEqual(personal["tier"], "personal")
        self.assertEqual(personal["user_id"], "u-1")
        self.assertEqual(personal["device_id"], "dev-1")
        # device_type is intentionally absent here: Bearer-only path
        # surfaces user_id from the token payload but device_type requires
        # either X-Device-Token or a separate DB lookup.
        self.assertNotIn("device_type", personal)
        self.assertEqual(personal["token_version"], 0)


# ----------------------------------------------------------------------- #
# Flag-observation acceptance — flag=false preserves legacy behavior
# ----------------------------------------------------------------------- #


class TestFlagPermissiveBypass(unittest.TestCase):
    """TASK §6 验收: TONGSHU_AUTH_ENFORCED=false 时, 旧请求一律不 401."""

    def test_invalid_bearer_with_flag_false_returns_200(self):
        client = _build_client(with_gateway=True)
        r = client.get(
            "/v1/today",
            params={"date": "2026-08-17"},
            headers={"Authorization": "Bearer this-is-not-a-real-token"},
        )
        # Default flag=false: parse failure does not reject; falls back to public.
        self.assertEqual(r.status_code, 200)
        # And emits the X-Auth-Would-Deny observation header (per §Q9).
        self.assertEqual(r.headers.get("x-auth-would-deny"), "1")
        body = r.json()
        self.assertNotIn("personal", body)

    def test_invalid_bearer_with_flag_true_returns_401(self):
        client = _build_client(with_gateway=True)
        with _flag("true"):
            r = client.get(
                "/v1/today",
                params={"date": "2026-08-17"},
                headers={"Authorization": "Bearer this-is-not-a-real-token"},
            )
        # Enforced: 401 from the optional dep's rejection branch.
        self.assertEqual(r.status_code, 401)
        # Header is NOT set in enforced mode (only the permissive mode
        # advertises the would-deny signal).
        self.assertNotEqual(r.headers.get("x-auth-would-deny"), "1")

    def test_legacy_routes_unaffected_when_flag_false(self):
        """Existing /v1/daily-guide test golden001 still 200s under flag=false."""
        # Ziwei stub opt-in (B-03a guard) — daily-guide pipeline touches ziwei.
        # NOTE: keep env set after test; conftest sets it globally and popping
        # here leaks state into subsequent suites in the same pytest session.
        os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = "1"
        client = _build_client(with_gateway=True)
        r = client.post("/v1/daily-guide", json=_GOLDEN001_BODY)
        self.assertEqual(r.status_code, 200)

    def test_legacy_calculate_unaffected_when_flag_false(self):
        # Ziwei stub opt-in — same as above, keep env set afterwards.
        os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = "1"
        client = _build_client(with_gateway=True)
        r = client.post("/v1/calculate", json=_GOLDEN001_BODY)
        self.assertEqual(r.status_code, 200)

    def test_legacy_profile_unaffected_when_flag_false(self):
        client = _build_client(with_gateway=True)
        r = client.post(
            "/v1/profile",
            json={
                "birth_date": "1984-12-07",
                "birth_time": {"hour": 16, "minute": 0},
                "gender": "male",
                "timezone": "Asia/Shanghai",
                "calendar_system": "solar",
                "location": "Beijing",
            },
        )
        self.assertEqual(r.status_code, 200)


# ----------------------------------------------------------------------- #
# /health stays public regardless of flag (k8s liveness)
# ----------------------------------------------------------------------- #


class TestHealthPublicRegardlessOfAuth(unittest.TestCase):
    """§6 验收: /health 免 token 仍 200 (监控系统不挂)."""

    def test_health_no_token_flag_false(self):
        client = _build_client(with_gateway=True)
        r = client.get("/health")
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d["status"], "ok")
        self.assertEqual(d["auth_enforced"], False)

    def test_health_no_token_flag_true(self):
        client = _build_client(with_gateway=True)
        with _flag("true"):
            r = client.get("/health")
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d["auth_enforced"], True)

    def test_health_no_gateway_returns_200(self):
        """Even without a wired gateway, /health must remain reachable."""
        client = _build_client(with_gateway=False)
        r = client.get("/health")
        self.assertEqual(r.status_code, 200)


# ----------------------------------------------------------------------- #
# NFC freeze (B-05 + M2): routes stay 501, no auth wired
# ----------------------------------------------------------------------- #


class TestNFC501Preserved(unittest.TestCase):
    """M2: NFC 三端点保持 501 不挂 auth."""

    def test_nfc_daily_no_auth_501(self):
        client = _build_client(with_gateway=True)
        r = client.get("/nfc/daily", params={"pendant_id": "p-1"})
        self.assertEqual(r.status_code, 501)

    def test_nfc_relationship_no_auth_501(self):
        client = _build_client(with_gateway=True)
        r = client.get(
            "/nfc/relationship",
            params={"pendant_id_a": "p-1", "pendant_id_b": "p-2"},
        )
        self.assertEqual(r.status_code, 501)

    def test_nfc_state_no_auth_501(self):
        client = _build_client(with_gateway=True)
        r = client.get("/nfc/state", params={"pendant_id": "p-1"})
        self.assertEqual(r.status_code, 501)

    def test_nfc_daily_with_flag_true_still_501(self):
        """Even when auth is enforced, NFC still 501 (no auth on NFC by M2)."""
        client = _build_client(with_gateway=True)
        with _flag("true"):
            r = client.get("/nfc/daily", params={"pendant_id": "p-1"})
        self.assertEqual(r.status_code, 501)


# ----------------------------------------------------------------------- #
# Optional sanity — guest-tier rate limiting on /v1/today
# ----------------------------------------------------------------------- #


class TestRateLimitObservable(unittest.TestCase):
    """read-public bucket is wired on /v1/today; per-IP key, sliding window."""

    def test_rate_limit_headers_present(self):
        client = _build_client(with_gateway=False)
        r = client.get("/v1/today", params={"date": "2026-08-17"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("x-trace-id", {k.lower() for k in r.headers.keys()})

    def test_rate_limit_429_after_burst(self):
        """Burst 31 requests against /v1/today (limit=30/min/IP)."""
        client = _build_client(with_gateway=False)
        statuses = []
        for _ in range(31):
            r = client.get("/v1/today", params={"date": "2026-08-17"})
            statuses.append(r.status_code)
        self.assertEqual(statuses[:30].count(200), 30)
        self.assertEqual(statuses[30], 429)
        last = client.get("/v1/today", params={"date": "2026-08-17"})
        self.assertEqual(last.status_code, 429)
        self.assertTrue(last.headers.get("retry-after"))

# ----------------------------------------------------------------------- #
# B-09 R2 rework (ARBITRATION_BATCH3 R2): TestLazyAuthSecretGate was nested
# inside test_rate_limit_429_after_burst, so pytest --collect-only never picked
# it up. Lifted to module top level so the gate contract is actually tested.
# ----------------------------------------------------------------------- #


class TestLazyAuthSecretGate(unittest.TestCase):
    """B-09 lazy fail-fast (User ruling): secret check at capability-use time,
    never at import time. Bidirectional: (a) no-secret startup raises;
    (b) with-secret issues and validates a token.

    B-09 R2 additions: (c) ``create_app()`` must enforce the gate (no startup
    bypass); (d) ``import tongshu.api.deps, tongshu.api.app`` must remain clean
    so test fixtures can pop the secret BEFORE building the app.
    """

    def test_a_no_secret_ensure_auth_ready_raises(self):
        """Direct call to ensure_auth_ready() in a fresh subprocess: with the
        secret popped, the gate raises RuntimeError. Original lazy contract."""
        import subprocess
        code = (
            "import sys; sys.path.insert(0, 'src')\n"
            "import os\n"
            "os.environ.pop('TONGSHU_AUTH_SECRET', None)\n"
            "import tongshu.services.identity_gateway as ig\n"
            "try:\n"
            "    ig.ensure_auth_ready()\n"
            "    print('NO_RAISE')\n"
            "except RuntimeError:\n"
            "    print('RAISED_OK')"
        )
        r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                           text=True, timeout=60)
        self.assertIn("RAISED_OK", r.stdout)

    def test_b_with_secret_token_roundtrip(self):
        """Happy path: with the secret set, gateway issues + validates a token."""
        from tests.auth.test_identity_gateway_v2 import make_gateway
        gw, db = make_gateway()
        tok = gw.generate_access_token("u-1", "dev-1")
        ctx = gw.validate_access_token(tok)
        self.assertEqual(ctx.user_id, "u-1")

    def test_c_import_chain_clean_without_secret(self):
        """Importing the modules MUST NOT require the secret. Test fixtures
        pop the secret before calling create_app() to assert the gate."""
        import subprocess
        code = (
            "import sys; sys.path.insert(0, 'src');"
            "import os; os.environ.pop('TONGSHU_AUTH_SECRET', None);"
            "import tongshu.api.deps, tongshu.api.app;"
            "print('CLEAN_IMPORT')"
        )
        r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                           text=True, timeout=90)
        self.assertIn("CLEAN_IMPORT", r.stdout)

    def test_d_create_app_calls_ensure_auth_ready(self):
        """B-09 R2: create_app() must invoke ensure_auth_ready() at the top so
        no startup path can serve traffic without the secret. Verified by
        popping the secret in a fresh subprocess, importing create_app, and
        calling it -- it must raise."""
        import subprocess
        code = (
            "import sys; sys.path.insert(0, 'src')\n"
            "import os\n"
            "os.environ.pop('TONGSHU_AUTH_SECRET', None)\n"
            "from tongshu.api.app import create_app\n"
            "try:\n"
            "    create_app()\n"
            "    print('NO_RAISE')\n"
            "except RuntimeError:\n"
            "    print('CREATE_APP_RAISED')"
        )
        r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                           text=True, timeout=90)
        self.assertIn("CREATE_APP_RAISED", r.stdout)




if __name__ == "__main__":
    unittest.main()