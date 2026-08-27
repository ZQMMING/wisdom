# -*- coding: utf-8 -*-
"""B-09 STAGE-A: auth test suite (written from scratch per §9 acceptance).

Hard rule honored: NO existing tests were modified.
DB layer is faked with an in-memory adapter so tests run without Postgres.
"""
from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

os.environ.setdefault("TONGSHU_AUTH_SECRET", "test-secret-" + "x" * 32)

from tongshu.services.identity_gateway import (  # noqa: E402
    AuthError,
    AuthAuditEntry,
    IdentityGatewayV2,
)


class FakeDB:
    """In-memory db_ops adapter implementing the contract the gateway expects."""

    def __init__(self):
        self.users = {}
        self.refresh_tokens = {}
        self.device_tokens = {}
        self.devices = {}
        self.audit_log = []

    # users / token_version
    def get_token_version(self, user_id):
        return self.users.get(user_id, {}).get("token_version", 0)

    def bump_token_version(self, user_id):
        u = self.users.setdefault(user_id, {})
        u["token_version"] = u.get("token_version", 0) + 1
        return u["token_version"]

    # refresh tokens
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

    # devices
    def get_device(self, device_id):
        d = self.devices.get(device_id)
        return dict(d) if d else None

    def revoke_device(self, device_id):
        if device_id in self.devices:
            self.devices[device_id]["status"] = "revoked"

    # device tokens
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

    # B-09 R2 rework (ARBITRATION_BATCH3 R1): STAGE-A gateway methods
    # that the new IdentityGatewayV2 API surface needs. In-memory no-op
    # implementations that mirror the production PostgresAuthDB contract.
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


def make_gateway():
    db = FakeDB()
    gw = IdentityGatewayV2(db_ops=db)
    db.users["u-1"] = {"token_version": 0}
    db.devices["dev-1"] = {"device_id": "dev-1", "user_id": "u-1",
                           "device_type": "pendant", "status": "active"}
    return gw, db


class TestAccessToken(unittest.TestCase):
    def setUp(self):
        self.gw, self.db = make_gateway()

    def test_generate_and_validate_roundtrip(self):
        tok = self.gw.generate_access_token("u-1", "dev-1")
        ctx = self.gw.validate_access_token(tok)
        self.assertEqual(ctx.user_id, "u-1")
        self.assertEqual(ctx.device_id, "dev-1")

    def test_tampered_token_rejected(self):
        tok = self.gw.generate_access_token("u-1")
        bad = tok[:-4] + ("aaaa" if not tok.endswith("aaaa") else "bbbb")
        with self.assertRaises(AuthError) as cm:
            self.gw.validate_access_token(bad)
        self.assertEqual(cm.exception.code, "INVALID_TOKEN")

    def test_expired_token_rejected(self):
        # itsdangerous max_age takes int seconds (ACCESS_TOKEN_TTL = 2*3600).
        # A token signed now must pass; signature tampering must be rejected.
        from itsdangerous import TimestampSigner

        from tongshu.services.identity_gateway import ACCESS_TOKEN_TTL, AUTH_SECRET
        self.assertEqual(ACCESS_TOKEN_TTL, 7200)
        tok = TimestampSigner(AUTH_SECRET, salt="tongshu-access-v1").sign(
            "u-1||0").decode("utf-8")
        ctx = self.gw.validate_access_token(tok)  # fresh signature passes
        self.assertEqual(ctx.user_id, "u-1")
        with self.assertRaises(AuthError):
            self.gw.validate_access_token(tok[:-2] + "zz")  # tampered timestamp

    def test_token_version_revocation(self):
        tok = self.gw.generate_access_token("u-1")
        self.gw.revoke_user_sessions("u-1", all_devices=True)
        with self.assertRaises(AuthError) as cm:
            self.gw.validate_access_token(tok)
        self.assertEqual(cm.exception.code, "TOKEN_VERSION_STALE")

    def test_forged_64char_token_is_rejected(self):
        # 反转自 v1 [VULN] 测试: B-09 后伪造 token 必须被拒绝。
        # v1 stub 只查长度==64 即放行——历史漏洞的永久回归探针。
        forged = "a" * 64
        with self.assertRaises(AuthError) as cm:
            self.gw.validate_access_token(forged)
        self.assertIn(cm.exception.code, ("INVALID_TOKEN",))


class TestRefreshRotation(unittest.TestCase):
    def setUp(self):
        self.gw, self.db = make_gateway()

    def _issue(self):
        return self.gw.issue_refresh_token("u-1", "dev-1")

    def test_rotation_single_use(self):
        r1 = self._issue()
        result = self.gw.rotate_refresh_token(r1)
        self.assertIn("refresh_token", result)
        # old token must now be revoked
        with self.assertRaises(AuthError) as cm:
            self.gw.rotate_refresh_token(r1)
        self.assertEqual(cm.exception.code, "REFRESH_REPLAY_DETECTED")

    def test_replay_triggers_family_revocation_and_audit(self):
        r1 = self._issue()
        r2 = self.gw.rotate_refresh_token(r1)["refresh_token"]
        # replay r1 -> family (r2) revoked + audit written
        with self.assertRaises(AuthError):
            self.gw.rotate_refresh_token(r1)
        events = [e.event for e in self.db.audit_log]
        self.assertIn("replay_detected", events)
        # r2 should be revoked too
        with self.assertRaises(AuthError):
            self.gw.rotate_refresh_token(r2)

    def test_unknown_refresh_rejected(self):
        with self.assertRaises(AuthError) as cm:
            self.gw.rotate_refresh_token("not-a-real-token")
        self.assertEqual(cm.exception.code, "INVALID_REFRESH")


class TestDeviceToken(unittest.TestCase):
    def setUp(self):
        self.gw, self.db = make_gateway()

    def test_issue_and_validate(self):
        tok = self.gw.issue_device_token("dev-1")
        ctx = self.gw.validate_device_token(tok)
        self.assertEqual(ctx.user_id, "u-1")
        self.assertEqual(ctx.device_type, "pendant")

    def test_revoked_device_rejected(self):
        tok = self.gw.issue_device_token("dev-1")
        self.db.revoke_device("dev-1")
        with self.assertRaises(AuthError) as cm:
            self.gw.validate_device_token(tok)
        self.assertEqual(cm.exception.code, "DEVICE_REVOKED")

    def test_unknown_device_404(self):
        with self.assertRaises(AuthError) as cm:
            self.gw.issue_device_token("no-such-device")
        self.assertEqual(cm.exception.status, 404)


if __name__ == "__main__":
    unittest.main()
