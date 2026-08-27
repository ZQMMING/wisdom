"""Phase 8-E: Permission Service 测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.services.permission_service import (
    PermissionService,
    SubscriptionLevel,
    FeatureAccess,
    get_permission_service
)


class TestFeatureAccess(unittest.TestCase):
    """功能访问控制测试。"""
    
    def test_free_features(self):
        """Free等级功能。"""
        features = FeatureAccess.get_features(SubscriptionLevel.FREE)
        
        self.assertIn("daily_tongshu", features)
        self.assertIn("basic_model", features)
        self.assertIn("nfc_login", features)
        self.assertNotIn("relationship_space", features)
    
    def test_premium_features(self):
        """Premium等级功能。"""
        features = FeatureAccess.get_features(SubscriptionLevel.PREMIUM)
        
        # 包含所有Free功能
        self.assertIn("daily_tongshu", features)
        self.assertIn("basic_model", features)
        
        # 包含Premium独有功能
        self.assertIn("relationship_space", features)
        self.assertIn("advanced_reports", features)
        self.assertIn("priority_support", features)
    
    def test_has_access_free(self):
        """Free用户访问权限。"""
        self.assertTrue(FeatureAccess.has_access(SubscriptionLevel.FREE, "daily_tongshu"))
        self.assertFalse(FeatureAccess.has_access(SubscriptionLevel.FREE, "relationship_space"))
    
    def test_has_access_premium(self):
        """Premium用户访问权限。"""
        self.assertTrue(FeatureAccess.has_access(SubscriptionLevel.PREMIUM, "daily_tongshu"))
        self.assertTrue(FeatureAccess.has_access(SubscriptionLevel.PREMIUM, "relationship_space"))


class TestPermissionService(unittest.TestCase):
    """权限服务测试。"""
    
    def setUp(self):
        self.service = PermissionService()
    
    def test_register_user(self):
        """注册用户。"""
        profile = self.service.register_user("user_001", "测试用户")
        
        self.assertEqual(profile.user_id, "user_001")
        self.assertEqual(profile.nickname, "测试用户")
        self.assertEqual(profile.subscription_level, SubscriptionLevel.FREE)
    
    def test_check_feature_access(self):
        """检查功能访问。"""
        self.service.register_user("user_001", "测试")
        
        self.assertTrue(self.service.check_feature_access("user_001", "daily_tongshu"))
        self.assertFalse(self.service.check_feature_access("user_001", "relationship_space"))
    
    def test_upgrade_subscription(self):
        """升级订阅等级。"""
        self.service.register_user("user_001", "测试")
        self.service.set_subscription("user_001", SubscriptionLevel.PREMIUM)
        
        self.assertTrue(self.service.check_feature_access("user_001", "relationship_space"))
    
    def test_unknown_user_access(self):
        """未知用户返回False。"""
        self.assertFalse(self.service.check_feature_access("unknown", "daily_tongshu"))


class TestSingleton(unittest.TestCase):
    """单例测试。"""
    
    def test_singleton(self):
        """全局单例一致性。"""
        s1 = get_permission_service()
        s2 = get_permission_service()
        self.assertIs(s1, s2)


if __name__ == '__main__':
    unittest.main()