"""DB runtime 平台层测试(task #57 落地)。

依赖本地 PostgreSQL(默认 postgres://postgres:postgres@127.0.0.1:5432/otcg)。
DB 不可达时整模块跳过 —— 不破坏 141 无 DB 基线。DAO 写测试用事务 + 回滚,
不在库里留持久行。migrate/seed 是幂等操作,反复执行安全。

运行(backend/):
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python -m unittest tests.test_db_runtime -v
"""

from __future__ import annotations

import unittest
from datetime import date

import psycopg2

from tongshu.db import config, dao
from tongshu.db.migrate import MIGRATION_VERSION, migrate
from tongshu.db.seed import seed

EXPECTED_TABLES = 28


@unittest.skipUnless(*config.db_available())
class DbRuntimeTest(unittest.TestCase):
    """全部用例要求目标库可达;DAO 写用例持事务并回滚。"""

    def setUp(self) -> None:
        self.dsn = config.get_dsn()
        self.conn = psycopg2.connect(self.dsn)
        self.tx = self.conn.cursor()
        self.tx.execute("BEGIN")
        self.addCleanup(self._rollback)

    def _rollback(self) -> None:
        try:
            self.conn.rollback()
        finally:
            self.conn.close()

    # ---------- migrate ----------

    def test_migrate_idempotent(self) -> None:
        # 状态无关断言:连跑两次,第二次恒返回 applied=False(已应用即幂等跳过)
        migrate(self.dsn)
        second = migrate(self.dsn)
        self.assertFalse(second["applied"])
        self.assertEqual(second["reason"], "already applied")
        cur = self.conn.cursor()
        cur.execute(
            "SELECT count(*) FROM migration_versions WHERE version=%s",
            (MIGRATION_VERSION,),
        )
        self.assertEqual(cur.fetchone()[0], 1)

    def test_schema_all_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"
        )
        self.assertGreaterEqual(cur.fetchone()[0], EXPECTED_TABLES)
        for t in (
            "users", "birth_profiles", "calculation_runs", "rule_results",
            "cross_analysis", "expressions", "expression_versions",
            "rules", "rule_versions", "books", "chapters", "passages",
            "classical_concepts", "principles", "evidence", "mappings",
            "mapping_versions", "semantic_objects", "audit_runs", "audit_findings",
            "golden_cases", "mapping_golden_cases", "semantic_golden_cases",
            "api_requests", "schema_versions", "migration_versions",
        ):
            cur.execute(
                "SELECT 1 FROM information_schema.tables WHERE table_schema='public'"
                " AND table_name=%s",
                (t,),
            )
            self.assertIsNotNone(cur.fetchone(), f"missing table {t}")

    # ---------- seed ----------

    def test_seed_idempotent_and_counts(self) -> None:
        first = seed(self.dsn)
        second = seed(self.dsn)
        self.assertEqual(first, second, "seed 必须幂等(两轮计数一致)")
        self.assertEqual(first["rules"], 136)   # 规则库增长至 120（原 88，含 T4 激活 + K2G 等新增）
        self.assertEqual(first["evidence"], 86)  # 证据库增长至 86（原 66，含 K2G 等新增）
        self.assertEqual(first["mappings"], 10)
        self.assertGreaterEqual(first["books"], 2)   # 子平真诠 + 紫微斗数
        cur = self.conn.cursor()
        cur.execute("SELECT count(*) FROM rules")
        self.assertEqual(cur.fetchone()[0], 136)
        cur.execute("SELECT count(*) FROM evidence WHERE evidence_id LIKE 'E-ZPZ%'")
        self.assertGreaterEqual(cur.fetchone()[0], 30)
        cur.execute("SELECT count(*) FROM rule_versions")
        self.assertGreaterEqual(cur.fetchone()[0], 88)  # 至少 88 (实际可能有历史数据)

    # ---------- dao ----------

    def test_dao_roundtrip(self) -> None:
        run_id = dao.record_calculation_run(
            self.conn,
            birth_profile_id=None,
            analysis_date=date(2026, 8, 18),
            theme="WORK",
            request_id="RR-DBTEST",
            trace_id="TRACE-DBTEST",
            canonical_id="CC-DBTEST",
            status="ok",
            source="engine",
            model_id="stub",
            prompt_version="prompt.1.0.0",
            versions={"calculation": "1.0.0", "knowledge": "1.0.0"},
        )
        dao.record_rule_results(
            self.conn,
            run_id,
            [
                {"rule_id": "ZPZ-001", "signal_id": "SIG-BA-JIA000", "matched": True,
                 "payload": {"type": "SUPPORT"}},
                {"rule_id": "ZPZ-999", "matched": False},
            ],
        )
        dao.record_expression(
            self.conn, run_id, source="template", text="测试文案",
            covered_claim_ids=["AC-SIG-BA-JIA000"], validation_passed=True,
        )
        audit_id = dao.record_audit(
            self.conn, run_id, request_id="RR-DBTEST", trace_id="TRACE-DBTEST",
            document_id="CC-DBTEST", validation_passed=True,
            gates={"g1": {"passed": True}, "g3": {"passed": True}},
            findings=[
                {"layer": "G1", "finding_code": "OK", "message": "全部证据可达"},
                {"layer": "G4", "finding_code": "OK", "message": "schema 校验通过"},
            ],
        )
        dao.record_api_request(
            self.conn, request_id="RR-DBTEST", trace_id="TRACE-DBTEST",
            method="POST", path="/v1/daily-guide", status_code=200,
            error_code=None, latency_ms=42,
        )
        runs = dao.recent_runs(self.conn, limit=5)
        self.assertTrue(any(r["request_id"] == "RR-DBTEST" for r in runs))
        self.assertTrue(any(r["run_id"] == run_id for r in runs))
        cur = self.conn.cursor()
        cur.execute("SELECT count(*) FROM rule_results WHERE run_id=%s", (run_id,))
        self.assertEqual(cur.fetchone()[0], 2)
        cur.execute("SELECT count(*) FROM expressions WHERE run_id=%s", (run_id,))
        self.assertEqual(cur.fetchone()[0], 1)
        cur.execute("SELECT count(*) FROM audit_findings WHERE audit_run_id=%s", (audit_id,))
        self.assertEqual(cur.fetchone()[0], 2)
        cur.execute("SELECT count(*) FROM api_requests WHERE request_id='RR-DBTEST'")
        self.assertEqual(cur.fetchone()[0], 1)


class KbDsnConfigTest(unittest.TestCase):
    """get_kb_dsn() must always point to shuntian_kb (no DB required)."""

    def test_default_kb_dsn_contains_shuntian_kb(self) -> None:
        import os
        # Ensure no env override interferes
        os.environ.pop("SHUNTIAN_KB_DATABASE_URL", None)
        dsn = config.get_kb_dsn()
        self.assertIn("shuntian_kb", dsn)
        self.assertNotIn("/otcg", dsn)

    def test_kb_dsn_env_override(self) -> None:
        import os
        os.environ["SHUNTIAN_KB_DATABASE_URL"] = "postgresql://u:p@h/db/shuntian_kb"
        try:
            self.assertEqual(
                config.get_kb_dsn(),
                "postgresql://u:p@h/db/shuntian_kb",
            )
        finally:
            os.environ.pop("SHUNTIAN_KB_DATABASE_URL", None)


if __name__ == "__main__":
    unittest.main()



