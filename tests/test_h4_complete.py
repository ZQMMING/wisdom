"""H4 + P0 + P1 + P1.5 完整验证测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import psycopg2
from tongshu.engines.heluo.interpretation import interpret, HeluoInput

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"


class TestH4Complete(unittest.TestCase):
    """H4 完整流程测试。"""
    
    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(DB_URI)
    
    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
    
    def test_algorithm_rules_exist(self):
        """HL-01~12 算法规则存在。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(DISTINCT algorithm_code) FROM algorithm_rules WHERE status='verified'")
        count = cur.fetchone()[0]
        self.assertGreaterEqual(count, 9, f"至少9个算法应有验证规则，实际: {count}")
    
    def test_algorithm_implementations_exist(self):
        """HL-09~12 算法实现存在。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM algorithm_implementations")
        count = cur.fetchone()[0]
        self.assertGreaterEqual(count, 9, f"至少9个算法应有实现记录，实际: {count}")
    
    def test_solar_terms_complete(self):
        """24节气完整。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM solar_terms")
        count = cur.fetchone()[0]
        self.assertEqual(count, 24, f"应有24个节气，实际: {count}")
    
    def test_interpretation_output_structure(self):
        """解释引擎输出结构正确。"""
        inp = HeluoInput(
            prenatal_hexagram="乾上乾下",
            yuan_tang="五爻",
            postnatal_hexagram="乾上坤下",
            day_hexagram="屯上蒙下",
            year_cycle="乙巳",
            month_cycle="甲申",
            day_cycle="丙午",
            element_state={"木": 0.6, "火": 0.8, "土": 0.3, "金": 0.5, "水": 0.7},
            line_position={"active_line": 5, "position_type": "尊位", "yinyang": "阳"},
            time_state={"solar_term": "立秋", "hour": 14}
        )
        
        result = interpret(inp)
        
        # 核心字段
        self.assertIsInstance(result.current_state, str)
        self.assertGreater(len(result.current_state), 10)
        
        # 机会因子
        self.assertIsInstance(result.opportunity.type, str)
        self.assertIsInstance(result.opportunity.strength, float)
        self.assertGreater(result.opportunity.strength, 0)
        self.assertLessEqual(result.opportunity.strength, 1)
        
        # 风险因子
        self.assertIsInstance(result.risk.type, str)
        self.assertIsInstance(result.risk.severity, float)
        self.assertGreater(result.risk.severity, 0)
        self.assertLessEqual(result.risk.severity, 1)
        
        # 建议行动
        self.assertIsInstance(result.recommended_action.primary, str)
        self.assertIsInstance(result.recommended_action.confidence, float)
        
        # 解释链
        self.assertEqual(len(result.interpretation_chain), 5)
        for step in result.interpretation_chain:
            self.assertIsInstance(step.logic, str)
            self.assertIsInstance(step.source, str)
        
        # 元数据
        self.assertEqual(result.meta["algorithm_version"], "H4-V1.0")
        self.assertIsInstance(result.meta["confidence_score"], float)
        self.assertEqual(result.meta["interpretation_type"], "relational")
    
    def test_time_reference_table(self):
        """时间参考表存在且数据完整。"""
        cur = self.conn.cursor()
        
        # time_reference
        cur.execute("SELECT COUNT(*) FROM time_reference")
        tr_count = cur.fetchone()[0]
        self.assertGreaterEqual(tr_count, 3)
        
        # ganzhi_base
        cur.execute("SELECT COUNT(*) FROM ganzhi_base")
        gb_count = cur.fetchone()[0]
        self.assertGreaterEqual(gb_count, 10)
    
    def test_global_time_params(self):
        """全球时间参数表存在。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM global_time_params")
        count = cur.fetchone()[0]
        self.assertGreaterEqual(count, 4)


if __name__ == "__main__":
    unittest.main()
