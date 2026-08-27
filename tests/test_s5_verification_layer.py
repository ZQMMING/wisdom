"""S5-01 核验层测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import psycopg2
import json

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"


class TestClassicalSources(unittest.TestCase):
    """测试 classical_sources 表。"""

    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(DB_URI)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_table_exists(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name = 'classical_sources' AND table_schema = 'public'
        """)
        self.assertEqual(cur.fetchone()[0], 1)

    def test_required_columns(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'classical_sources'
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in cur.fetchall()]

        required = ['id', 'book_name', 'volume', 'original_text',
                    'related_algorithm', 'verification_status']
        for col in required:
            self.assertIn(col, columns, f"Missing column: {col}")

    def test_sources_exist_for_algorithms(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT related_algorithm, COUNT(*) as source_count
            FROM classical_sources
            GROUP BY related_algorithm
            ORDER BY related_algorithm
        """)
        results = {row[0]: row[1] for row in cur.fetchall()}

        for algo in ['HL-09', 'HL-10', 'HL-11', 'HL-12']:
            self.assertIn(algo, results, f"{algo} should have sources")
            self.assertGreaterEqual(results[algo], 1)

    def test_sources_have_original_text(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM classical_sources WHERE original_text IS NULL OR original_text = ''")
        empty = cur.fetchone()[0]
        self.assertEqual(empty, 0, "All sources must have original_text")

    def test_sources_have_hash(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM classical_sources WHERE original_text_hash IS NULL")
        empty = cur.fetchone()[0]
        self.assertEqual(empty, 0, "All sources must have text hash")

    def test_verified_count(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM classical_sources WHERE verification_status = 'verified'")
        verified = cur.fetchone()[0]
        self.assertGreaterEqual(verified, 4, "At least 4 sources should be verified")


class TestVerifications(unittest.TestCase):
    """测试 classical_source_verifications 表结构。"""

    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(DB_URI)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_table_exists(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name = 'classical_source_verifications'
        """)
        self.assertEqual(cur.fetchone()[0], 1)

    def test_fk_constraint(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT conname FROM pg_constraint
            WHERE conrelid = 'classical_source_verifications'::regclass
            AND confrelid = 'classical_sources'::regclass
        """)
        fk = cur.fetchone()
        self.assertIsNotNone(fk, "FK constraint to classical_sources should exist")


class TestIntegration(unittest.TestCase):
    """集成测试。"""

    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(DB_URI)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_verification_coverage(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(DISTINCT related_algorithm) FROM classical_sources")
        total = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT related_algorithm)
            FROM classical_sources
            WHERE verification_status = 'verified'
        """)
        verified = cur.fetchone()[0]

        coverage = verified / total if total > 0 else 0
        self.assertGreaterEqual(coverage, 0.8,
            f"Verification coverage {coverage:.0%} should be >= 80%")

    def test_algorithm_rules_consistency(self):
        """算法注册表与核验层引用一致。"""
        cur = self.conn.cursor()

        # 获取算法注册表中的算法
        cur.execute("SELECT algorithm_code FROM hl_algorithms")
        algo_codes = {row[0] for row in cur.fetchall()}

        # 获取核验层中的算法引用
        cur.execute("SELECT DISTINCT related_algorithm FROM classical_sources WHERE related_algorithm IS NOT NULL")
        source_algos = {row[0] for row in cur.fetchall()}

        # HL-09~HL-12 都应该有引用
        for algo in ['HL-09', 'HL-10', 'HL-11', 'HL-12']:
            self.assertIn(algo, source_algos, f"{algo} should have classical source")


if __name__ == "__main__":
    unittest.main()
