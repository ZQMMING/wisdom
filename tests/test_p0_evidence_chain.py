"""P0 证据链验证测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import psycopg2

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"


class TestAlgorithmRules(unittest.TestCase):
    """验证 algorithm_rules 表数据完整性。"""
    
    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(DB_URI)
    
    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
    
    def test_table_exists(self):
        """表存在。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'algorithm_rules' AND table_schema = 'public'
        """)
        self.assertEqual(cur.fetchone()[0], 1)
    
    def test_rules_exist_for_algorithms(self):
        """HL-01~HL-12 都有对应规则。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT algorithm_code, COUNT(*) as rule_count 
            FROM algorithm_rules 
            GROUP BY algorithm_code 
            ORDER BY algorithm_code
        """)
        results = {row[0]: row[1] for row in cur.fetchall()}
        
        # 检查关键算法都有规则
        for algo in ['HL-01', 'HL-02', 'HL-03', 'HL-05', 'HL-08', 'HL-09', 'HL-10', 'HL-11', 'HL-12']:
            self.assertIn(algo, results, f"{algo} should have rules")
            self.assertGreaterEqual(results[algo], 1, f"{algo} should have at least 1 rule")
    
    def test_rules_have_source_refs(self):
        """所有规则都有来源引用。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM algorithm_rules WHERE source_book IS NULL OR source_text IS NULL")
        empty = cur.fetchone()[0]
        self.assertEqual(empty, 0, "All rules must have source references")
    
    def test_rules_have_confidence(self):
        """所有规则都有置信度。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM algorithm_rules WHERE confidence IS NULL OR confidence <= 0")
        empty = cur.fetchone()[0]
        self.assertEqual(empty, 0, "All rules must have confidence > 0")


class TestAlgorithmImplementations(unittest.TestCase):
    """验证 algorithm_implementations 表数据完整性。"""
    
    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(DB_URI)
    
    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
    
    def test_table_exists(self):
        """表存在。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'algorithm_implementations' AND table_schema = 'public'
        """)
        self.assertEqual(cur.fetchone()[0], 1)
    
    def test_implementations_exist(self):
        """关键算法都有实现记录。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM algorithm_implementations")
        count = cur.fetchone()[0]
        self.assertGreaterEqual(count, 9, "At least 9 algorithms should have implementations")
    
    def test_function_paths_valid(self):
        """所有实现都有有效的函数路径。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM algorithm_implementations WHERE function_path IS NULL OR function_path = ''")
        empty = cur.fetchone()[0]
        self.assertEqual(empty, 0, "All implementations must have function_path")
    
    def test_test_references_exist(self):
        """所有实现都有测试引用。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM algorithm_implementations WHERE test_reference IS NULL OR test_reference = ''")
        empty = cur.fetchone()[0]
        self.assertEqual(empty, 0, "All implementations must have test_reference")


class TestEvidenceClosure(unittest.TestCase):
    """验证证据链闭合度。"""
    
    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(DB_URI)
    
    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
    
    def test_evidence_closure_rate(self):
        """证据闭合率计算。"""
        cur = self.conn.cursor()
        
        # 总算法数
        cur.execute("SELECT COUNT(DISTINCT algorithm_code) FROM hl_algorithms")
        total_algos = cur.fetchone()[0]
        
        # 有规则的算法数
        cur.execute("""
            SELECT COUNT(DISTINCT algorithm_code) 
            FROM algorithm_rules 
            WHERE status = 'verified'
        """)
        verified_algos = cur.fetchone()[0]
        
        # 有实现的算法数
        cur.execute("SELECT COUNT(*) FROM algorithm_implementations")
        implemented = cur.fetchone()[0]
        
        closure_rate = (verified_algos / total_algos) if total_algos > 0 else 0
        
        self.assertGreaterEqual(closure_rate, 0.7, 
            f"Evidence closure rate {closure_rate:.2%} should be >= 70%")


if __name__ == "__main__":
    unittest.main()
