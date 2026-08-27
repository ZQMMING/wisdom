"""Phase 6: Daily Tongshu API 测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.services.daily_api import (
    DailyTongshuService,
    DailyTongshu,
    create_daily_tongshu
)


class TestDailyTongshuService(unittest.TestCase):
    """每日通书服务测试。"""
    
    def setUp(self):
        self.service = DailyTongshuService()
    
    def test_get_daily_tongshu_default_date(self):
        """默认日期为今天。"""
        result = self.service.get_daily_tongshu('test_token')
        self.assertEqual(result.date, date.today())
    
    def test_get_daily_tongshu_specific_date(self):
        """指定日期。"""
        target = date(2026, 12, 31)
        result = self.service.get_daily_tongshu('test_token', target)
        self.assertEqual(result.date, target)
    
    def test_output_structure(self):
        """输出结构完整性。"""
        result = self.service.get_daily_tongshu('test_token')
        
        self.assertIsInstance(result, DailyTongshu)
        self.assertTrue(hasattr(result, 'daily_hexagram'))
        self.assertTrue(hasattr(result, 'state'))
        self.assertTrue(hasattr(result, 'opportunity'))
        self.assertTrue(hasattr(result, 'attention'))
        self.assertTrue(hasattr(result, 'suggestion'))
        self.assertTrue(hasattr(result, 'element_balance'))
        self.assertTrue(hasattr(result, 'source_reference'))
    
    def test_element_balance_sum(self):
        """五行总和为1.0。"""
        result = self.service.get_daily_tongshu('test_token')
        total = sum(result.element_balance.values())
        self.assertAlmostEqual(total, 1.0, places=1)
    
    def test_all_elements_present(self):
        """五行元素齐全。"""
        result = self.service.get_daily_tongshu('test_token')
        elements = set(result.element_balance.keys())
        self.assertEqual(elements, {'金', '木', '水', '火', '土'})
    
    def test_source_references(self):
        """来源引用不为空。"""
        result = self.service.get_daily_tongshu('test_token')
        self.assertTrue(len(result.source_reference) > 0)
        self.assertIsInstance(result.source_reference, list)
    
    def test_non_empty_fields(self):
        """关键字段不为空。"""
        result = self.service.get_daily_tongshu('test_token')
        
        self.assertTrue(len(result.daily_hexagram) > 0)
        self.assertTrue(len(result.state) > 0)
        self.assertTrue(len(result.opportunity) > 0)
        self.assertTrue(len(result.attention) > 0)
        self.assertTrue(len(result.suggestion) > 0)
    
    def test_convenience_function(self):
        """便捷函数。"""
        result = create_daily_tongshu('test_token')
        
        self.assertIn('version', result)
        self.assertIn('date', result)
        self.assertIn('daily_hexagram', result)
        self.assertIn('state', result)
    
    def test_token_validation(self):
        """Token验证。"""
        self.assertTrue(self.service.validate_token('valid_token_123456'))
        self.assertFalse(self.service.validate_token(''))
        self.assertFalse(self.service.validate_token(None))
        self.assertFalse(self.service.validate_token('short'))


class TestDateHandling(unittest.TestCase):
    """日期处理测试。"""
    
    def setUp(self):
        self.service = DailyTongshuService()
    
    def test_future_date(self):
        """未来日期。"""
        future = date(2027, 1, 1)
        result = self.service.get_daily_tongshu('test_token', future)
        self.assertEqual(result.date, future)
    
    def test_past_date(self):
        """过去日期。"""
        past = date(2025, 1, 1)
        result = self.service.get_daily_tongshu('test_token', past)
        self.assertEqual(result.date, past)


if __name__ == '__main__':
    unittest.main()