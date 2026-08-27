"""Phase 7-B: Daily Tongshu ViewModel 测试"""
from __future__ import annotations
import unittest
import sys
import json
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.services.daily_viewmodel import (
    DailyTongshuViewModel,
    DailyTongshuBuilder,
    create_sample_tongshu
)


class TestDailyTongshuViewModel(unittest.TestCase):
    """ViewModel数据结构测试。"""
    
    def test_to_dict_structure(self):
        """字典结构完整性。"""
        viewmodel = create_sample_tongshu()
        d = viewmodel.to_dict()
        
        # 核心字段检查
        self.assertIn('date', d)
        self.assertIn('solar_term', d)
        self.assertIn('hexagram', d)
        self.assertIn('state', d)
        self.assertIn('guidance', d)
        self.assertIn('element_balance', d)
        self.assertIn('liu_nian', d)
        self.assertIn('liu_yue', d)
        self.assertIn('liu_ri', d)
        self.assertIn('source_reference', d)
    
    def test_hexagram_structure(self):
        """卦象数据结构。"""
        viewmodel = create_sample_tongshu()
        hexagram = viewmodel.hexagram
        
        self.assertEqual(hexagram.name, "火山旅")
        self.assertEqual(hexagram.upper, "离")
        self.assertEqual(hexagram.lower, "艮")
        self.assertEqual(hexagram.binary, "101001")
        self.assertTrue(len(hexagram.meaning) > 0)
    
    def test_state_structure(self):
        """状态数据结构。"""
        viewmodel = create_sample_tongshu()
        state = viewmodel.state
        
        self.assertEqual(state.title, "稳定期")
        self.assertEqual(state.energy_level, "middle")
        self.assertTrue(len(state.description) > 0)
    
    def test_guidance_structure(self):
        """指导数据结构。"""
        viewmodel = create_sample_tongshu()
        guidance = viewmodel.guidance
        
        self.assertTrue(len(guidance.opportunity) > 0)
        self.assertTrue(len(guidance.attention) > 0)
        self.assertTrue(len(guidance.suggestion) > 0)
    
    def test_element_balance_sum(self):
        """五行总和为1.0。"""
        viewmodel = create_sample_tongshu()
        balance = viewmodel.element_balance
        total = balance.gold + balance.wood + balance.water + balance.fire + balance.earth
        self.assertAlmostEqual(total, 1.0, places=1)
    
    def test_element_balance_dict(self):
        """五行字典转换。"""
        viewmodel = create_sample_tongshu()
        d = viewmodel.element_balance.to_dict()
        
        self.assertEqual(set(d.keys()), {'金', '木', '水', '火', '土'})
        for v in d.values():
            self.assertGreaterEqual(v, 0)
            self.assertLessEqual(v, 1)
    
    def test_time_sequence(self):
        """时间序列数据。"""
        viewmodel = create_sample_tongshu()
        
        self.assertEqual(viewmodel.liu_nian, "甲辰")
        self.assertEqual(viewmodel.liu_yue, "壬申")
        self.assertEqual(viewmodel.liu_ri, "丙午")
    
    def test_source_references(self):
        """来源引用。"""
        viewmodel = create_sample_tongshu()
        
        self.assertIsInstance(viewmodel.source_reference, list)
        self.assertTrue(len(viewmodel.source_reference) >= 2)
        self.assertIn("《河图》", viewmodel.source_reference)
    
    def test_json_serialization(self):
        """JSON序列化。"""
        viewmodel = create_sample_tongshu()
        json_str = viewmodel.to_json()
        
        parsed = json.loads(json_str)
        self.assertIn('date', parsed)
        self.assertIn('hexagram', parsed)
    
    def test_date_type(self):
        """日期类型。"""
        viewmodel = create_sample_tongshu()
        self.assertIsInstance(viewmodel.date, date)


class TestBuilder(unittest.TestCase):
    """构建器测试。"""
    
    def test_fluent_interface(self):
        """流畅接口。"""
        builder = DailyTongshuBuilder()
        
        result = (builder
            .set_date(date(2026, 1, 1))
            .set_solar_term("冬至")
            .set_hexagram("乾", "乾", "乾", "111111", "纯阳")
            .set_state("大吉", "纯阳之卦", "high")
            .set_guidance("进取", "把握时机", "乘势而上")
            .set_element_balance(0.3, 0.1, 0.1, 0.3, 0.2)
            .set_time_sequence("甲子", "乙丑", "丙寅")
            .add_source("测试源")
            .build()
        )
        
        self.assertEqual(result.date, date(2026, 1, 1))
        self.assertEqual(result.solar_term, "冬至")
        self.assertEqual(result.hexagram.name, "乾")
    
    def test_default_values(self):
        """默认值。"""
        builder = DailyTongshuBuilder()
        result = builder.build()
        
        self.assertEqual(result.date, date.today())
        self.assertEqual(result.state.energy_level, "middle")
    
    def test_overwrite_values(self):
        """覆盖值。"""
        builder = DailyTongshuBuilder()
        builder.set_date(date(2026, 1, 1))
        builder.set_date(date(2026, 12, 31))
        
        result = builder.build()
        self.assertEqual(result.date, date(2026, 12, 31))


class TestEdgeCases(unittest.TestCase):
    """边界情况测试。"""
    
    def test_empty_sources(self):
        """空来源列表。"""
        builder = DailyTongshuBuilder()
        result = builder.build()
        
        self.assertEqual(result.source_reference, [])
    
    def test_unbalanced_elements(self):
        """不平衡的五行（仍应通过）。"""
        builder = DailyTongshuBuilder()
        result = (builder
            .set_element_balance(0.5, 0.1, 0.1, 0.1, 0.1)
            .build()
        )
        
        balance = result.element_balance.to_dict()
        total = sum(balance.values())
        # 允许一定误差
        self.assertAlmostEqual(total, 0.9, places=1)


if __name__ == '__main__':
    unittest.main()