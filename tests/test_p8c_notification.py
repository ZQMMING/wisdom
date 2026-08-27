"""Phase 8-C: Notification Engine 测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.services.notification_engine import (
    NotificationEngine,
    NotificationPreference,
    NotificationType,
    NotificationStatus,
    get_engine
)


class TestNotificationEngine(unittest.TestCase):
    """通知引擎测试。"""
    
    def setUp(self):
        self.engine = NotificationEngine()
        self.user_id = "user_001"
    
    def test_set_and_get_preference(self):
        """设置和获取偏好。"""
        pref = NotificationPreference(
            user_id=self.user_id,
            daily_enabled=True,
            preferred_time="08:00",
            language="zh-CN",
            timezone="Asia/Shanghai"
        )
        
        self.engine.set_preference(pref)
        result = self.engine.get_preference(self.user_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.user_id, self.user_id)
        self.assertTrue(result.daily_enabled)
    
    def test_default_preference(self):
        """默认偏好值。"""
        pref = NotificationPreference(user_id=self.user_id)
        self.engine.set_preference(pref)
        
        result = self.engine.get_preference(self.user_id)
        self.assertTrue(result.daily_enabled)
        self.assertEqual(result.preferred_time, "08:00")
    
    def test_missing_preference_returns_none(self):
        """不存在的用户返回None。"""
        result = self.engine.get_preference("unknown_user")
        self.assertIsNone(result)
    
    def test_daily_notification_enabled(self):
        """每日通知启用。"""
        pref = NotificationPreference(user_id=self.user_id, daily_enabled=True)
        self.engine.set_preference(pref)
        
        self.assertTrue(self.engine.should_notify(self.user_id, NotificationType.DAILY_TONGSHU))
    
    def test_daily_notification_disabled(self):
        """每日通知禁用。"""
        pref = NotificationPreference(user_id=self.user_id, daily_enabled=False)
        self.engine.set_preference(pref)
        
        self.assertFalse(self.engine.should_notify(self.user_id, NotificationType.DAILY_TONGSHU))
    
    def test_log_notification(self):
        """记录通知日志。"""
        log = self.engine.log_notification(
            self.user_id,
            NotificationType.DAILY_TONGSHU,
            "v1.0",
            NotificationStatus.SENT
        )
        
        self.assertEqual(log.user_id, self.user_id)
        self.assertEqual(log.type, NotificationType.DAILY_TONGSHU.value)
        self.assertEqual(log.status, NotificationStatus.SENT.value)
    
    def test_get_send_logs(self):
        """获取发送日志。"""
        for i in range(5):
            self.engine.log_notification(
                self.user_id,
                NotificationType.DAILY_TONGSHU,
                f"v1.{i}"
            )
        
        logs = self.engine.get_send_logs(self.user_id, limit=3)
        self.assertEqual(len(logs), 3)
    
    def test_get_send_logs_empty(self):
        """空日志列表。"""
        logs = self.engine.get_send_logs("unknown_user")
        self.assertEqual(len(logs), 0)


class TestSingleton(unittest.TestCase):
    """单例测试。"""
    
    def test_singleton(self):
        """全局单例一致性。"""
        e1 = get_engine()
        e2 = get_engine()
        self.assertIs(e1, e2)


if __name__ == '__main__':
    unittest.main()