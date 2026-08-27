# [ARCHIVED 2026-08-23] Tests for the v1 stub removed by B-09 (P0). Kept per User ruling option A.
# The 11 stub-behavior tests documented the vulnerability; superseded by tests/auth/test_identity_gateway_v2.py
"""Phase 6: Identity Gateway 测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.services.identity_gateway import (
    IdentityGateway,
    NFCToken,
    UserContext,
    DeviceType,
    DeviceStatus,
    create_device_token,
    get_gateway
)


class TestTokenGeneration(unittest.TestCase):
    """Token生成测试。"""
    
    def setUp(self):
        self.gateway = IdentityGateway()
    
    def test_token_length(self):
        """Token长度64位。"""
        token = self.gateway.generate_token('user_001')
        self.assertEqual(len(token), 64)
    
    def test_token_uniqueness(self):
        """Token唯一性。"""
        token1 = self.gateway.generate_token('user_001')
        token2 = self.gateway.generate_token('user_002')
        self.assertNotEqual(token1, token2)
    
    def test_token_format(self):
        """Token格式为hex。"""
        token = self.gateway.generate_token('user_001')
        self.assertEqual(token, token.lower())
        self.assertEqual(len(token), 64)


class TestTokenValidation(unittest.TestCase):
    """Token验证测试。"""
    
    def setUp(self):
        self.gateway = IdentityGateway()
    
    def test_valid_token(self):
        """有效Token验证。"""
        token = self.gateway.generate_token('user_001')
        result = self.gateway.validate_token(token)
        self.assertIsNotNone(result)
        self.assertEqual(result.device_token, token)
    
    def test_invalid_token_length(self):
        """无效长度Token。"""
        result = self.gateway.validate_token('short')
        self.assertIsNone(result)
    
    def test_empty_token(self):
        """空Token。"""
        result = self.gateway.validate_token('')
        self.assertIsNone(result)
    
    def test_none_token(self):
        """None Token。"""
        result = self.gateway.validate_token(None)
        self.assertIsNone(result)


class TestUserContext(unittest.TestCase):
    """用户上下文测试。"""
    
    def setUp(self):
        self.gateway = IdentityGateway()
    
    def test_new_user_context(self):
        """新用户上下文。"""
        context = self.gateway.resolve_user_context('test_token')
        self.assertTrue(context.is_new_user)
        self.assertFalse(context.has_birth_info)
        self.assertFalse(context.has_heluo_model)
    
    def test_user_id_type(self):
        """用户ID类型。"""
        context = self.gateway.resolve_user_context('test_token')
        self.assertIsInstance(context.user_id, str)


class TestDeviceBinding(unittest.TestCase):
    """设备绑定测试。"""
    
    def setUp(self):
        self.gateway = IdentityGateway()
    
    def test_bind_device(self):
        """绑定设备。"""
        result = self.gateway.bind_device('user_001', 'token_001')
        self.assertTrue(result)
    
    def test_unbind_device(self):
        """解绑设备。"""
        result = self.gateway.unbind_device('user_001', 'token_001')
        self.assertTrue(result)


class TestSingleton(unittest.TestCase):
    """单例模式测试。"""
    
    def test_singleton(self):
        """全局单例一致性。"""
        gw1 = get_gateway()
        gw2 = get_gateway()
        self.assertIs(gw1, gw2)
    
    def test_convenience_function(self):
        """便捷函数。"""
        token = create_device_token('user_001')
        self.assertEqual(len(token), 64)


class TestDeviceTypes(unittest.TestCase):
    """设备类型测试。"""
    
    def test_device_types(self):
        """设备类型枚举。"""
        self.assertEqual(DeviceType.PENDANT.value, 'pendant')
        self.assertEqual(DeviceType.TAG.value, 'tag')
        self.assertEqual(DeviceType.PHONE.value, 'phone')
    
    def test_device_status(self):
        """设备状态枚举。"""
        self.assertEqual(DeviceStatus.ACTIVE.value, 'active')
        self.assertEqual(DeviceStatus.INACTIVE.value, 'inactive')
        self.assertEqual(DeviceStatus.REVOKED.value, 'revoked')


if __name__ == '__main__':
    unittest.main()