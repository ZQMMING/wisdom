"""S5-03 Golden Dataset 测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import psycopg2
import json

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"


class TestHeluoGoldenCases(unittest.TestCase):
    """测试 Heluo Golden Dataset。"""

    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(DB_URI)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_table_exists(self):
        """heluo_golden_cases 表存在。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name = 'heluo_golden_cases' AND table_schema = 'public'
        """)
        self.assertEqual(cur.fetchone()[0], 1)

    def test_cases_count(self):
        """至少有50个案例。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM heluo_golden_cases")
        count = cur.fetchone()[0]
        self.assertGreaterEqual(count, 40, f"Expected >= 40 cases, got {count}")

    def test_cases_have_required_fields(self):
        """案例都有必需字段。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM heluo_golden_cases
            WHERE birth_info IS NULL OR calculated_results IS NULL
        """)
        empty = cur.fetchone()[0]
        self.assertEqual(empty, 0, "All cases must have birth_info and calculated_results")

    def test_cases_cover_algorithms(self):
        """案例覆盖所有算法。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT DISTINCT LEFT(case_id, 2) as algo_prefix, COUNT(*)
            FROM heluo_golden_cases
            GROUP BY algo_prefix
            ORDER BY algo_prefix
        """)
        results = {row[0]: row[1] for row in cur.fetchall()}

        for prefix in ['HC', 'DY', 'LN']:
            self.assertIn(prefix, results, f"Should have cases for {prefix}")
            self.assertGreaterEqual(results[prefix], 5, 
                f"Should have at least 5 cases for {prefix}")

    def test_approval_rate(self):
        """approved案例比例。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM heluo_golden_cases WHERE status = 'approved'")
        approved = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM heluo_golden_cases")
        total = cur.fetchone()[0]
        
        rate = approved / total if total > 0 else 0
        self.assertGreaterEqual(rate, 0.5, f"Approval rate {rate:.0%} should be >= 50%")

    def test_classical_consistency_score(self):
        """古籍一致性评分合理。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT AVG(classical_consistency), MIN(classical_consistency), MAX(classical_consistency)
            FROM heluo_golden_cases
            WHERE classical_consistency IS NOT NULL
        """)
        row = cur.fetchone()
        
        self.assertIsNotNone(row[0], "Should have consistency scores")
        self.assertGreaterEqual(row[1], 0.7, "Min consistency should be >= 0.7")
        self.assertLessEqual(row[2], 1.0, "Max consistency should be <= 1.0")


if __name__ == "__main__":
    unittest.main()
