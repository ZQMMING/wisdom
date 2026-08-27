"""Phase 8-D: Analytics Engine 测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path
from datetime import date, datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.services.analytics_engine import (
    AnalyticsEngine,
    UserEvent,
    UserEventType,
    get_analytics
)


class TestAnalyticsEngine(unittest.TestCase):
    """分析引擎测试。"""
    
    def setUp(self):
        self.analytics = AnalyticsEngine()
        self.user_id = "user_001"
        self.now = datetime.utcnow()
    
    def test_record_and_count_events(self):
        """记录和统计事件。"""
        event = UserEvent(
            event_id="e1",
            user_id=self.user_id,
            event_type=UserEventType.NFC_OPEN,
            timestamp=self.now,
            metadata={}
        )
        self.analytics.record_event(event)
        
        counts = self.analytics.get_event_counts_by_type()
        self.assertEqual(counts.get(UserEventType.NFC_OPEN, 0), 1)
    
    def test_nfc_conversion_rate(self):
        """NFC转化率计算。"""
        # 模拟3次NFC打开，1次绑定完成
        for i in range(3):
            self.analytics.record_event(UserEvent(
                event_id=f"open_{i}",
                user_id=self.user_id,
                event_type=UserEventType.NFC_OPEN,
                timestamp=self.now,
                metadata={}
            ))
        
        self.analytics.record_event(UserEvent(
            event_id="bind_1",
            user_id=self.user_id,
            event_type=UserEventType.BIND_COMPLETE,
            timestamp=self.now,
            metadata={}
        ))
        
        rate = self.analytics.get_nfc_conversion_rate()
        self.assertAlmostEqual(rate, 1/3, places=2)
    
    def test_nfc_conversion_zero(self):
        """无NFC打开时转化率为0。"""
        rate = self.analytics.get_nfc_conversion_rate()
        self.assertEqual(rate, 0.0)
    
    def test_daily_active_users(self):
        """日活跃用户计算。"""
        today = date.today()
        
        # 今天的事件
        self.analytics.record_event(UserEvent(
            event_id="e1",
            user_id=self.user_id,
            event_type=UserEventType.DAILY_VIEW,
            timestamp=self.now,
            metadata={}
        ))
        
        count = self.analytics.get_daily_active_users(today)
        self.assertGreaterEqual(count, 1)
    
    def test_retention_rate(self):
        """留存率计算。"""
        # 记录近期事件
        recent = datetime.utcnow() - timedelta(days=3)
        self.analytics.record_event(UserEvent(
            event_id="e1",
            user_id=self.user_id,
            event_type=UserEventType.DAILY_VIEW,
            timestamp=recent,
            metadata={}
        ))
        
        retention = self.analytics.get_retention_rate(period_days=7)
        self.assertGreater(retention, 0.0)
    
    def test_metric_report(self):
        """指标报告。"""
        report = self.analytics.get_metric_report()
        
        self.assertIn("daily_active_users", report)
        self.assertIn("nfc_conversion_rate", report)
        self.assertIn("retention_7d", report)
        self.assertIn("retention_30d", report)
        self.assertIn("total_events", report)


class TestSingleton(unittest.TestCase):
    """单例测试。"""
    
    def test_singleton(self):
        """全局单例一致性。"""
        a1 = get_analytics()
        a2 = get_analytics()
        self.assertIs(a1, a2)


if __name__ == '__main__':
    unittest.main()