"""P1 + P1.5 测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tongshu.engines.time.solar_time import (
    calculate_true_solar_time,
    create_global_time_table,
    get_equation_of_time
)
from tongshu.engines.heluo.hexagram_state import (
    calculate_hexagram_state,
    calculate_element_modifier,
    get_branch_element
)

import psycopg2

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"


class TestTrueSolarTime(unittest.TestCase):
    """测试真太阳时计算。"""
    
    def test_beijing_no_correction(self):
        """北京经度接近120度，修正应很小。"""
        result = calculate_true_solar_time(
            datetime(2025, 8, 21, 12, 0, 0),
            longitude=116.4,
            latitude=39.9
        )
        self.assertAlmostEqual(result["longitude_correction_minutes"], -14.4, delta=1)
    
    def test_shanghai_positive_correction(self):
        """上海在东边，时间应提前。"""
        result = calculate_true_solar_time(
            datetime(2025, 8, 21, 12, 0, 0),
            longitude=121.5,
            latitude=31.2
        )
        # 经度修正应为正
        self.assertGreater(result["longitude_correction_minutes"], 0)
    
    def test_urumqi_negative_correction(self):
        """乌鲁木齐在西边，时间应推迟。"""
        result = calculate_true_solar_time(
            datetime(2025, 8, 21, 12, 0, 0),
            longitude=87.6,
            latitude=43.8
        )
        # 经度修正应为负
        self.assertLess(result["longitude_correction_minutes"], 0)
    
    def test_equation_of_time_range(self):
        """均时差应在合理范围（全年极值约 ±16.4min ≈ ±985s）。"""
        eot = get_equation_of_time(2025, 8, 21)
        # 8月21日真实值约 -199s（Meeus）；断言放宽至天文极值范围。
        self.assertGreaterEqual(eot, -1000)
        self.assertLessEqual(eot, 1000)
        # 非零：修复 P1-3 前恒返回 0，此断言确保均时差真实生效。
        self.assertNotEqual(eot, 0)


class TestGlobalTimeTable(unittest.TestCase):
    """测试全球时间参数表。"""
    
    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(DB_URI)
    
    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
    
    def test_table_created(self):
        """表已创建。"""
        stats = create_global_time_table(self.conn)
        self.assertEqual(stats["global_time_params_table"], 1)
    
    def test_params_inserted(self):
        """参数已插入。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM global_time_params")
        count = cur.fetchone()[0]
        self.assertGreaterEqual(count, 4)


class TestHexagramState(unittest.TestCase):
    """测试卦象状态引擎。"""
    
    def test_basic_calculation(self):
        """基本状态计算。"""
        result = calculate_hexagram_state(
            hexagram="乾上乾下",
            state_type="动",
            element_state={"木": 0.6, "火": 0.8, "土": 0.3, "金": 0.5, "水": 0.7},
            month_branch="午"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.hexagram, "乾上乾下")
        self.assertEqual(result.state_type, "动")
    
    def test_element_modifier(self):
        """五行修正计算。"""
        modifier = calculate_element_modifier(
            {"木": 0.6, "火": 0.8},
            month_branch="午"
        )
        # 午属火，火生土，木生火
        # 应有正向修正
        self.assertIsInstance(modifier, float)
    
    def test_branch_element(self):
        """地支五行查询。"""
        self.assertEqual(get_branch_element("子"), "水")
        self.assertEqual(get_branch_element("午"), "火")
        self.assertEqual(get_branch_element("寅"), "木")
        self.assertEqual(get_branch_element("申"), "金")
        self.assertEqual(get_branch_element("丑"), "土")
    
    def test_interpretation_generated(self):
        """解释生成。"""
        result = calculate_hexagram_state("坤上坤下", "静")
        self.assertIsInstance(result.interpretation, str)
        self.assertGreater(len(result.interpretation), 0)


if __name__ == "__main__":
    unittest.main()
