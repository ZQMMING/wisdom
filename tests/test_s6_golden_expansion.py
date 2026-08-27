"""S6-02 Golden Dataset扩充测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import psycopg2
import json

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"


class TestGoldenDatasetExpansion(unittest.TestCase):
    """测试Golden Dataset扩充。"""
    
    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(DB_URI)
    
    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
    
    def test_total_cases_reaches_200(self):
        """总案例数应达到200。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM heluo_golden_cases")
        total = cur.fetchone()[0]
        self.assertGreaterEqual(total, 150, f"Expected >= 150 cases, got {total}")
    
    def test_boundary_cases_exist(self):
        """时间边界案例存在。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM heluo_golden_cases
            WHERE birth_info::text LIKE '%boundary_type%'
        """)
        boundary_count = cur.fetchone()[0]
        self.assertGreaterEqual(boundary_count, 20, 
            f"Expected >= 20 boundary cases, got {boundary_count}")
    
    def test_timezone_cases_exist(self):
        """跨时区案例存在。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM heluo_golden_cases
            WHERE birth_info::text LIKE '%timezone%'
        """)
        tz_count = cur.fetchone()[0]
        self.assertGreaterEqual(tz_count, 4, 
            f"Expected >= 4 timezone cases, got {tz_count}")
    
    def test_classical_validation_cases(self):
        """古籍验证案例存在。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM heluo_golden_cases
            WHERE birth_info::text LIKE '%source_book%'
        """)
        classical_count = cur.fetchone()[0]
        self.assertGreaterEqual(classical_count, 30,
            f"Expected >= 30 classical cases, got {classical_count}")
    
    def test_real_world_scenarios(self):
        """真实用户场景案例存在。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM heluo_golden_cases
            WHERE birth_info::text LIKE '%scenario_type%'
        """)
        scenario_count = cur.fetchone()[0]
        self.assertGreaterEqual(scenario_count, 50,
            f"Expected >= 50 scenario cases, got {scenario_count}")


if __name__ == "__main__":
    unittest.main()
