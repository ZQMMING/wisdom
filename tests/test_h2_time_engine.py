"""H2 时间引擎规格验证测试 (最终修正版)"""

from __future__ import annotations
import unittest
import psycopg2
import json

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"


class TestSolarTerms(unittest.TestCase):
    """验证24节气数据完整性。"""

    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(DB_URI)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_24_terms_exist(self):
        """24节气全部存在。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM solar_terms")
        count = cur.fetchone()[0]
        self.assertEqual(count, 24, f"Expected 24 solar terms, got {count}")

    def test_all_terms_have_source(self):
        """所有节气都有solar_ref。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM solar_terms WHERE solar_ref IS NULL OR solar_ref = ''")
        empty = cur.fetchone()[0]
        self.assertEqual(empty, 0, "All terms must have solar_ref")


class TestTimeCycles(unittest.TestCase):
    """验证time_cycles表结构。"""

    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(DB_URI)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_table_exists(self):
        """time_cycles表存在。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'time_cycles' AND table_schema = 'public'
        """)
        count = cur.fetchone()[0]
        self.assertEqual(count, 1, "time_cycles table must exist")

    def test_table_has_required_columns(self):
        """表有必需列。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'time_cycles' AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        columns = [r[0] for r in cur.fetchall()]
        required = ['cycle_id', 'cycle_type', 'cycle_start', 'status']
        for col in required:
            self.assertIn(col, columns, f"Missing column: {col}")


class TestAlgorithmRegistry(unittest.TestCase):
    """验证算法注册表。"""

    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(DB_URI)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_hl09_registered(self):
        """HL-ALG-009已注册。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM hl_algorithms WHERE algorithm_id = 'HL-ALG-009'")
        count = cur.fetchone()[0]
        self.assertEqual(count, 1, "HL-ALG-009 must be registered")

    def test_hl10_registered(self):
        """HL-ALG-010已注册。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM hl_algorithms WHERE algorithm_id = 'HL-ALG-010'")
        count = cur.fetchone()[0]
        self.assertEqual(count, 1, "HL-ALG-010 must be registered")

    def test_hl11_registered(self):
        """HL-ALG-011已注册。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM hl_algorithms WHERE algorithm_id = 'HL-ALG-011'")
        count = cur.fetchone()[0]
        self.assertEqual(count, 1, "HL-ALG-011 must be registered")

    def test_hl12_registered(self):
        """HL-ALG-012已注册。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM hl_algorithms WHERE algorithm_id = 'HL-ALG-012'")
        count = cur.fetchone()[0]
        self.assertEqual(count, 1, "HL-ALG-012 must be registered")


if __name__ == "__main__":
    unittest.main()
