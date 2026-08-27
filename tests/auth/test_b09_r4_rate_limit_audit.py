# -*- coding: utf-8 -*-
"""B-09 R2 R4 closure: register/login IP rate limit + failed-attempt audit.

ARBITRATION_BATCH3 R4: register/login must each have an independent IP
rate-limit bucket (M3), and failed attempts must be written to the
auth_audit_log so abuse leaves a forensic trail. The wiring lives in
src/tongshu/api/auth.py (R1 commit); this file adds dedicated tests so
the R4 surface is independently verified and documented.

Coverage:
  - test_a_register_has_independent_register_ip_bucket: /v1/auth/register
    wired with RATE_LIMIT_REGISTER_IP (5/min/IP). Bursts of 6 should see
    one 429.
  - test_b_login_has_independent_login_ip_bucket: /v1/auth/login wired
    with RATE_LIMIT_LOGIN_IP (10/min/IP). The two buckets are
    independent: a saturated register bucket must NOT throttle login.
  - test_c_register_login_buckets_are_independent: a 6-burst on register
    returns 429 for the 6th call but a parallel /v1/auth/login call from
    the same IP still gets through (separate buckets).
  - test_d_register_audit_failure_writes_to_audit_log: a register failure
    (gateway raises AuthError) results in a AuthAuditEntry appended to
    FakeDB.audit_log with event_type=register_failed.
  - test_e_login_audit_failure_writes_to_audit_log: same for login with
    event_type=login_failed.

Hard rule honored: NO existing tests modified; this is a pure addition.
"""
from __future__ import annotations

import os
import unittest
from typing import Any, Optional

from fastapi.testclient import TestClient

from tongshu.api.app import create_app
from tongshu.api.auth import (
    RATE_LIMIT_LOGIN_IP,
    RATE_LIMIT_REGISTER_IP,
)
from tongshu.api.deps import reset_rate_limit_buckets
import tongshu.services.identity_gateway as identity_gateway_module

# f932650 落地时遗漏环境自给，违反同目录密闭惯例；357f233 启动门控后首次暴露
os.environ.setdefault("TONGSHU_AUTH_SECRET", "r4-test-secret-placeholder")


class _R4FakeDB:
    """Minimal db_ops adapter for R4 tests.

    Mirrors the FakeDB contract in test_b09_route_enforcement.py:
    provides the methods IdentityGatewayV2 actually calls when handling
    /register and /login + a list-based audit() recorder so we can assert
    the failed-attempt trail.
    """

    def __init__(self) -> None:
        self.users: dict[str, dict[str, Any]] = {}
        self.devices: dict[str, dict[str, Any]] = {}
        self.refresh_tokens: dict[str, dict[str, Any]] = {}
        self.device_tokens: dict[str, dict[str, Any]] = {}
        self.audit_log: list[Any] = []

    # ---- users ----
    def create_user(self, user_id, **flags):
        self.users[user_id] = {
            "token_version": 1,
            "is_new_user": True,
            "has_birth_info": False,
            "has_heluo_model": False,
        }

    def get_user(self, user_id):
        return self.users.get(user_id)

    # ---- token_version ----
    def get_token_version(self, user_id):
        u = self.users.get(user_id, {})
        return u.get("token_version", 0)

    def bump_token_version(self, user_id):
        u = self.users.setdefault(user_id, {"token_version": 0})
        u["token_version"] = u.get("token_version", 0) + 1
        return u["token_version"]

    # ---- refresh ----
    def insert_refresh_token(self, jti, user_id, device_id,
                              token_hash, expires_at):
        self.refresh_tokens[jti] = {
            "jti": jti, "user_id": user_id, "device_id": device_id,
            "token_hash": token_hash, "expires_at": expires_at,
            "revoked_at": None, "rotated_into": None,
        }

    def get_refresh_token(self, token_hash):
        for jti, row in self.refresh_tokens.items():
            if row["token_hash"] == token_hash:
                return row
        return None

    def revoke_refresh_token(self, jti, rotated_into=None):
        if jti in self.refresh_tokens:
            self.refresh_tokens[jti]["revoked_at"] = "now"
            self.refresh_tokens[jti]["rotated_into"] = rotated_into

    def revoke_all_refresh_tokens(self, user_id, device_id=None):
        return 0

    # ---- devices ----
    def create_device(self, device_id, user_id, **flags):
        self.devices[device_id] = {
            "id": device_id, "user_id": user_id,
            "device_type": "pendant", "status": "active",
        }

    def get_device(self, device_id):
        return self.devices.get(device_id)

    def list_user_devices(self, user_id):
        return [d for d in self.devices.values() if d["user_id"] == user_id]

    def update_device_last_used(self, device_id):
        pass

    # ---- audit ----
    def audit(self, entry):
        self.audit_log.append(entry)


def _wire_gateway() -> _R4FakeDB:
    """Build a fresh gateway with the R4 FakeDB adapter wired."""
    reset_rate_limit_buckets()
    identity_gateway_module._gateway_singleton = None
    db = _R4FakeDB()
    app = create_app(db_ops=db)
    return db, app


class B09R4RateLimitAndAuditTest(unittest.TestCase):
    """R4 closure: independent IP buckets + audit-failure wiring."""

    def setUp(self) -> None:
        # Each test gets a clean bucket and a fresh gateway.
        # Secret is set at module level; setUp only needs fresh gateway.
        self.db, self.app = _wire_gateway()
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        identity_gateway_module._gateway_singleton = None
        reset_rate_limit_buckets()

    # ---- IP rate limit buckets (M3) ----

    def test_a_register_has_independent_register_ip_bucket(self) -> None:
        """/v1/auth/register wired with RATE_LIMIT_REGISTER_IP (5/min/IP).
        The 6th request from the same IP within 60s must return 429.

        The bucket is captured inside the closure of RATE_LIMIT_REGISTER_IP
        (it's a FastAPI dep factory, not a config object), so we exercise
        the bucket by bursting requests and observing the 429.
        """
        # Inspect the closure to confirm the bucket name and limits match spec.
        # Closure order: bucket, key, max_requests, window_seconds
        closure = RATE_LIMIT_REGISTER_IP.__closure__
        bucket, key, max_req, window = (c.cell_contents for c in closure[:4])
        self.assertEqual(bucket, "auth-register-ip")
        self.assertEqual(key, "ip")
        self.assertEqual(max_req, 5)
        self.assertEqual(window, 60)

        statuses = []
        for _ in range(6):
            r = self.client.post("/v1/auth/register", json={})
            statuses.append(r.status_code)
        # First 5 register calls should pass the bucket (the response code
        # may be 200 OR a downstream failure -- what matters for R4 is that
        # the bucket admits the first 5 and rejects the 6th with 429).
        self.assertNotIn(429, statuses[:5],
                         "first 5 register calls must NOT be throttled")
        self.assertEqual(statuses[5], 429,
                         "6th register call within window must be 429")

    def test_b_login_has_independent_login_ip_bucket(self) -> None:
        """/v1/auth/login wired with RATE_LIMIT_LOGIN_IP (10/min/IP).
        The 11th login request from the same IP within 60s must be 429."""
        closure = RATE_LIMIT_LOGIN_IP.__closure__
        bucket, key, max_req, window = (c.cell_contents for c in closure[:4])
        self.assertEqual(bucket, "auth-login-ip")
        self.assertEqual(key, "ip")
        self.assertEqual(max_req, 10)
        self.assertEqual(window, 60)

        statuses = []
        for _ in range(11):
            r = self.client.post(
                "/v1/auth/login",
                json={"device_id": "dev-x", "pairing_code": "pair-x"},
            )
            statuses.append(r.status_code)
        self.assertNotIn(429, statuses[:10],
                         "first 10 login calls must NOT be throttled")
        self.assertEqual(statuses[10], 429,
                         "11th login call within window must be 429")

    def test_c_register_and_login_buckets_are_independent(self) -> None:
        """A saturated register bucket must NOT throttle login (separate buckets)."""
        # Saturate the register bucket (5 + 1 throttled = 6 calls)
        for _ in range(6):
            self.client.post("/v1/auth/register", json={})
        # Now hit login. Since the register bucket is full but the login
        # bucket is independent, login should NOT be 429.
        r = self.client.post(
            "/v1/auth/login",
            json={"device_id": "dev-y", "pairing_code": "pair-y"},
        )
        self.assertNotEqual(r.status_code, 429,
                            "login bucket must be independent of register")

    # ---- Failed attempts write to auth_audit_log ----

    def test_d_register_audit_failure_writes_to_audit_log(self) -> None:
        """A register failure must write AuthAuditEntry to audit_log.

        Triggers an AuthError via a payload the gateway refuses. The route
        catches AuthError, calls _audit_failure(register_failed), and the
        entry lands in FakeDB.audit_log.
        """
        before = len(self.db.audit_log)
        # Empty body is valid for register, but a malformed request can
        # also trigger downstream failure. To deterministically force a
        # known failure path, we monkeypatch the gateway to raise.
        gw = identity_gateway_module._gateway_singleton
        original_register = gw.register_user

        def boom(**kwargs):
            from tongshu.services.identity_gateway import AuthError
            raise AuthError(
                status_code=503,
                message="register boom (R4 test)",
                code="INTERNAL",
            )

        try:
            gw.register_user = boom
            r = self.client.post("/v1/auth/register", json={"x": "y"})
        finally:
            gw.register_user = original_register

        # The response is a 5xx (mapped from AuthError), and the audit log
        # should have grown by exactly one entry.
        self.assertEqual(r.status_code, 503)
        self.assertEqual(
            len(self.db.audit_log), before + 1,
            "register failure must append exactly 1 audit entry",
        )
        entry = self.db.audit_log[-1]
        # The entry exposes .event_type / .ip_address (R1 contract);
        # fall back to legacy aliases (.event / .ip) if R1 names not used.
        ev = getattr(entry, "event_type", None) or entry.event
        self.assertEqual(ev, "register_failed")

    def test_e_login_audit_failure_writes_to_audit_log(self) -> None:
        """A login failure must write AuthAuditEntry to audit_log."""
        before = len(self.db.audit_log)
        gw = identity_gateway_module._gateway_singleton
        original_login = gw.login_user

        def boom(**kwargs):
            from tongshu.services.identity_gateway import AuthError
            raise AuthError(
                status_code=503,
                message="login boom (R4 test)",
                code="INTERNAL",
            )

        try:
            gw.login_user = boom
            r = self.client.post(
                "/v1/auth/login",
                json={"device_id": "d", "pairing_code": "p"},
            )
        finally:
            gw.login_user = original_login

        self.assertEqual(r.status_code, 503)
        self.assertEqual(
            len(self.db.audit_log), before + 1,
            "login failure must append exactly 1 audit entry",
        )
        entry = self.db.audit_log[-1]
        ev = getattr(entry, "event_type", None) or entry.event
        self.assertEqual(ev, "login_failed")


if __name__ == "__main__":
    unittest.main()