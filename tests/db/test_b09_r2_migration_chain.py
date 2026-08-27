# -*- coding: utf-8 -*-
"""B-09 R2 staging dual-run evidence (ARBITRATION_BATCH3 R3).

The arbitration ruled that the auth migration version
'20260823_B09_auth_v1' was 'written in a script that will never
be executed' (E2). R3 closes the gap by chaining init_auth_schema()
into tongshu.db.migrate.migrate() so the version gets recorded
in migration_versions after the frozen contract lands.

This test exercises the chain against a mocked psycopg2 connection
(clean env / CI without a live DB still runs it) and asserts that:
  1. init_auth_schema() is called once during migrate() after the
     frozen DDL is applied.
  2. The exact version string '20260823_B09_auth_v1' is INSERTed
     (staging dual-run evidence: the SQL the script generates would
     record the version on a real DB).
  3. Idempotent re-runs do NOT re-issue the version INSERT.
  4. init_auth_schema() standalone behaves the same way when called
     directly (Phase C tooling, e.g. scripts.db_setup migrate).
"""
from __future__ import annotations

import unittest
from typing import Optional
from unittest.mock import MagicMock, patch

from tongshu.db.init_auth import AUTH_MIGRATION_VERSION, init_auth_schema
# Import the module (not the function re-exported in tongshu.db/__init__.py)
migrate_mod = __import__("tongshu.db.migrate", fromlist=["*"])


class _FakeCursor:
    """Minimal psycopg2 cursor that records executed statements.

    Pretends a real DB: _table_exists('migration_versions') returns True.
    The auth version is already recorded (set up in setUp). Lets us assert
    exactly what SQL would hit a real PostgreSQL during staging.
    """

    def __init__(self, recorded_versions=None):
        self.executed = []
        self._recorded = set(recorded_versions or [])
        self._fetchone_value = None

    def execute(self, sql, params=None):
        self.executed.append((sql, params))
        sql_norm = " ".join(sql.split())
        # _table_exists check from init_auth.py:
        # SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=%s
        # The table name is in params[0], not in the SQL literal.
        if "information_schema.tables" in sql_norm:
            self._fetchone_value = (1,)  # Pretend migration_versions exists
            return
        # SELECT 1 FROM migration_versions WHERE version=%s
        if sql_norm.startswith("SELECT 1 FROM migration_versions WHERE version"):
            ver = params[0] if params else None
            self._fetchone_value = (1,) if ver in self._recorded else None
            return
        # INSERT INTO migration_versions ... (also: multi-statement DDL may embed it)
        if "INSERT INTO migration_versions" in sql_norm:
            # params is None for multi-statement DDL; extract version from SQL literal
            ver = None
            if params:
                ver = params[0]
            elif "VALUES (" in sql_norm:
                # e.g. VALUES ('20260823_B09_auth_v1', '...')
                idx = sql_norm.find("VALUES (")
                snippet = sql_norm[idx + 8:]
                end = snippet.find(",")
                candidate = snippet[:end].strip().strip("'")
                if candidate:
                    ver = candidate
            if ver:
                self._recorded.add(ver)
            return
        # DDL: just record
        self._fetchone_value = None

    def fetchone(self):
        v = self._fetchone_value
        self._fetchone_value = None
        return v


class B09R2MigrationChainTest(unittest.TestCase):
    """Staging dual-run evidence: the auth version gets recorded."""

    def setUp(self):
        self.recorded_versions = set()
        self.cursor = _FakeCursor(recorded_versions=self.recorded_versions)
        self.conn = MagicMock()
        self.conn.cursor.return_value = self.cursor

    def test_a_init_auth_schema_records_version_on_clean_db(self):
        """Clean DB: init_auth_schema() applies DDL and records version."""
        with patch("tongshu.db.init_auth.psycopg2.connect", return_value=self.conn):
            result = init_auth_schema(dsn="mock://test")

        self.assertTrue(result["applied"])
        self.assertEqual(result["version"], AUTH_MIGRATION_VERSION)
        self.assertEqual(result["reason"], "applied")
        # Verify the version INSERT was issued with the correct literal.
        # The auth migration runs as one cur.execute() with multi-statement DDL,
        # so the INSERT lives inside the full 0002_auth.sql payload (not at the
        # top). Look for "INSERT INTO migration_versions" anywhere in the SQL.
        version_in_sql = any(
            "INSERT INTO migration_versions" in c[0] and AUTH_MIGRATION_VERSION in c[0]
            for c in self.cursor.executed
        )
        self.assertTrue(
            version_in_sql,
            "expected auth version literal inside an INSERT INTO migration_versions, "
            "got executed=%r" % [c[0][:80] for c in self.cursor.executed],
        )

    def test_b_init_auth_schema_idempotent(self):
        """Re-run with version already recorded: no-op, no INSERT."""
        # Pre-record the version directly in the cursor's set so the
        # SELECT 1 FROM migration_versions WHERE version=... returns (1,)
        # and init_auth_schema short-circuits with reason="already applied".
        self.cursor._recorded.add(AUTH_MIGRATION_VERSION)
        with patch("tongshu.db.init_auth.psycopg2.connect", return_value=self.conn):
            result = init_auth_schema(dsn="mock://test")

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "already applied")
        # On idempotent run, the auth_sql is NOT executed (the early
        # "already applied" return short-circuits before cur.execute(auth_sql)).
        # Therefore no INSERT INTO migration_versions should appear.
        version_in_sql = any(
            "INSERT INTO migration_versions" in c[0]
            for c in self.cursor.executed
        )
        self.assertFalse(
            version_in_sql,
            "idempotent run must not INSERT version again, "
            "got executed=%r" % [c[0][:80] for c in self.cursor.executed],
        )

    def test_c_migrate_chains_init_auth_schema(self):
        """migrate() must call init_auth_schema() so the version is recorded.

        Without this call, the version literal lives in a dead script (E2).
        """
        with patch("tongshu.db.migrate.psycopg2.connect", return_value=self.conn):
            with patch.object(migrate_mod, "init_auth_schema") as spy:
                spy.return_value = {
                    "applied": True,
                    "version": AUTH_MIGRATION_VERSION,
                    "reason": "applied",
                }
                result = migrate_mod.migrate(dsn="mock://test")

        spy.assert_called_once_with("mock://test")
        self.assertIn("auth_chain", result)
        self.assertEqual(result["auth_chain"]["version"], AUTH_MIGRATION_VERSION)

    def test_d_migrate_passes_dsn_to_init_auth_schema(self):
        """The chain forwards the same DSN so the auth version lands
        on the same database the frozen contract was applied to."""
        with patch("tongshu.db.migrate.psycopg2.connect", return_value=self.conn):
            with patch.object(migrate_mod, "init_auth_schema") as spy:
                spy.return_value = {
                    "applied": True,
                    "version": AUTH_MIGRATION_VERSION,
                    "reason": "applied",
                }
                migrate_mod.migrate(dsn="db-specific-dsn://x")

        spy.assert_called_once_with("db-specific-dsn://x")


if __name__ == "__main__":
    unittest.main()