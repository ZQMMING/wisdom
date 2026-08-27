"""B-09 C12: Real PostgreSQL integration test for PostgresAuthDB.create_user.

Validates the E8 fix against the frozen users table contract:

  - ``users.email TEXT NOT NULL UNIQUE`` is satisfied by the deterministic
    placeholder ``pending+{user_id}@anonymous.local``.
  - Insert via PostgresAuthDB.create_user against a real PG instance
    succeeds without IntegrityError.
  - The 5 STAGE-A auth columns (is_new_user / has_birth_info /
    has_heluo_model / token_version / last_login_at) layered by
    0002_auth.sql coexist with the frozen contract columns.
  - ``ON CONFLICT (id) DO NOTHING`` makes the call idempotent on retry.

This test uses real PostgreSQL (no mock / FakeDB). It is skipped if the
local PG instance is not reachable so the suite stays runnable in
environments without staging DB access.

Anti-mock rule per C1: mocks are forbidden as the SOLE evidence. This test
exercises the real psycopg2 adapter against a real DB.
"""
from __future__ import annotations
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure backend/src is on sys.path
BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_ROOT / "src"))
os.environ.setdefault("TONGSHU_AUTH_SECRET", "test-secret-" + "x" * 32)

import psycopg2  # noqa: E402

from tongshu.db.auth_db import PostgresAuthDB, _placeholder_email  # noqa: E402
from tongshu.db.config import db_available  # noqa: E402

# Default staging DSN: local PG 17 staging DB created by the B-09 C12 dual-run.
# Override via env var TEST_PG_DSN for CI.
DEFAULT_TEST_DSN = "postgresql://postgres:postgres@127.0.0.1:5432/otcg_staging_fresh"
TEST_DSN = os.environ.get("TEST_PG_DSN", DEFAULT_TEST_DSN)


@unittest.skipUnless(
    db_available(TEST_DSN, timeout=3)[0],
    f"PostgreSQL unavailable at {TEST_DSN}; B-09 C12 PG integration test skipped",
)
class TestPostgresAuthDBCreateUserAgainstFrozenContract(unittest.TestCase):
    """Real-PG integration test for the B-09 C12 E8 fix."""

    USER_IDS = (
        "11111111-1111-1111-1111-11111111c001",
        "11111111-1111-1111-1111-11111111c002",
        "22222222-2222-2222-2222-22222222c001",
        "22222222-2222-2222-2222-22222222c002",
        "33333333-3333-3333-3333-33333333c003",
    )

    @classmethod
    def setUpClass(cls):
        cls.dsn = TEST_DSN
        cls.db = PostgresAuthDB(dsn=cls.dsn)
        c = psycopg2.connect(cls.dsn, connect_timeout=5)
        cur = c.cursor()
        cur.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_schema='public' AND table_name='users'
            ORDER BY ordinal_position
            """
        )
        cls.user_cols = [r[0] for r in cur.fetchall()]
        c.close()

    def _cleanup(self):
        c = psycopg2.connect(self.dsn, connect_timeout=5)
        cur = c.cursor()
        cur.execute(
            "DELETE FROM refresh_tokens WHERE user_id = ANY(%s::uuid[])",
            (list(self.USER_IDS),),
        )
        cur.execute(
            "DELETE FROM users WHERE id = ANY(%s::uuid[])",
            (list(self.USER_IDS),),
        )
        c.commit()
        c.close()

    def setUp(self):
        self._cleanup()

    def tearDown(self):
        self._cleanup()

    def test_frozen_users_table_has_email_not_null(self):
        self.assertIn("email", self.user_cols)
        c = psycopg2.connect(self.dsn, connect_timeout=5)
        cur = c.cursor()
        cur.execute(
            """
            SELECT is_nullable FROM information_schema.columns
            WHERE table_schema='public' AND table_name='users'
              AND column_name='email'
            """
        )
        is_nullable = cur.fetchone()[0]
        c.close()
        self.assertEqual(is_nullable, "NO", "email must be NOT NULL")

    def test_frozen_users_table_has_5_auth_columns_from_0002(self):
        for col in (
            "is_new_user",
            "has_birth_info",
            "has_heluo_model",
            "token_version",
            "last_login_at",
        ):
            self.assertIn(col, self.user_cols, f"missing auth column: {col}")

    def test_placeholder_email_format(self):
        uid = "00000000-0000-0000-0000-000000000001"
        e = _placeholder_email(uid)
        self.assertEqual(e, f"pending+{uid}@anonymous.local")
        self.assertTrue(e.endswith("@anonymous.local"))
        self.assertTrue(e.startswith("pending+"))

    def test_placeholder_email_deterministic_and_unique(self):
        u1 = "00000000-0000-0000-0000-0000000000aa"
        u2 = "00000000-0000-0000-0000-0000000000bb"
        self.assertEqual(_placeholder_email(u1), _placeholder_email(u1))
        self.assertNotEqual(_placeholder_email(u1), _placeholder_email(u2))

    def test_create_user_against_frozen_table_succeeds(self):
        uid = self.USER_IDS[0]
        try:
            self.db.create_user(
                uid,
                is_new_user=True,
                has_birth_info=False,
                has_heluo_model=False,
                token_version=1,
            )
        except Exception as exc:  # noqa: BLE001
            self.fail(f"create_user raised {type(exc).__name__}: {exc}")

        row = self.db.get_user(uid)
        self.assertIsNotNone(row)
        self.assertEqual(row["id"], uid)
        self.assertTrue(row["is_new_user"])
        self.assertFalse(row["has_birth_info"])
        self.assertFalse(row["has_heluo_model"])
        self.assertEqual(row["token_version"], 1)

        c = psycopg2.connect(self.dsn, connect_timeout=5)
        cur = c.cursor()
        cur.execute("SELECT email FROM users WHERE id = %s", (uid,))
        email = cur.fetchone()[0]
        c.close()
        self.assertEqual(email, _placeholder_email(uid))

    def test_create_user_is_idempotent(self):
        uid = self.USER_IDS[1]
        self.db.create_user(uid, is_new_user=True, token_version=1)
        try:
            self.db.create_user(uid, is_new_user=False, token_version=5)
        except Exception as exc:  # noqa: BLE001
            self.fail(f"idempotent retry raised {type(exc).__name__}: {exc}")
        self.assertEqual(self.db.get_token_version(uid), 1)

    def test_create_user_unique_constraint_via_email_placeholder(self):
        u1 = self.USER_IDS[2]
        u2 = self.USER_IDS[3]
        e1 = _placeholder_email(u1)
        e2 = _placeholder_email(u2)
        self.assertNotEqual(e1, e2)

        self.db.create_user(u1, is_new_user=True)
        self.db.create_user(u2, is_new_user=True)

        c = psycopg2.connect(self.dsn, connect_timeout=5)
        cur = c.cursor()
        cur.execute(
            "SELECT id, email FROM users WHERE id IN (%s, %s) ORDER BY id",
            (u1, u2),
        )
        rows = cur.fetchall()
        c.close()
        self.assertEqual(len(rows), 2)
        ids = {r[0] for r in rows}
        emails = {r[1] for r in rows}
        self.assertSetEqual(ids, {u1, u2})
        self.assertSetEqual(emails, {e1, e2})

    def test_bump_and_get_token_version_after_create(self):
        uid = self.USER_IDS[4]
        self.db.create_user(uid, is_new_user=True, token_version=1)
        self.assertEqual(self.db.get_token_version(uid), 1)
        new_ver = self.db.bump_token_version(uid)
        self.assertEqual(new_ver, 2)
        self.assertEqual(self.db.get_token_version(uid), 2)


if __name__ == "__main__":
    unittest.main()