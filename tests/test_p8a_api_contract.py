"""Phase 8-A: API Contract 测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.api.contract import (
    ApiContract,
    ErrorCode,
    RateLimiter,
    check_rate_limit,
    create_success_response,
    create_error_response
)


class TestApiContract(unittest.TestCase):
    """API Contract 测试。"""
    
    def test_success_response_structure(self):
        """成功响应结构。"""
        result = ApiContract.success({"key": "value"})
        
        self.assertTrue(result["success"])
        self.assertEqual(result["version"], "1.0.0")
        self.assertEqual(result["data"], {"key": "value"})
        self.assertIn("meta", result)
        self.assertIn("request_id", result["meta"])
        self.assertIn("timestamp", result["meta"])
    
    def test_error_response_structure(self):
        """错误响应结构。"""
        result = ApiContract.error(ErrorCode.TOKEN_INVALID, "Token无效")
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertEqual(result["error"]["code"], "E001")
        self.assertEqual(result["error"]["message"], "Token无效")
    
    def test_error_codes(self):
        """错误码定义。"""
        self.assertEqual(ErrorCode.TOKEN_INVALID.value, "E001")
        self.assertEqual(ErrorCode.PROFILE_MISSING.value, "E002")
        self.assertEqual(ErrorCode.CALCULATION_FAILED.value, "E003")
        self.assertEqual(ErrorCode.RELATIONSHIP_NOT_FOUND.value, "E004")
        self.assertEqual(ErrorCode.DEVICE_NOT_BOUND.value, "E005")
        self.assertEqual(ErrorCode.INVALID_INPUT.value, "E006")
        self.assertEqual(ErrorCode.SERVICE_UNAVAILABLE.value, "E007")
        self.assertEqual(ErrorCode.RATE_LIMITED.value, "E008")
    
    def test_page_response(self):
        """分页响应。"""
        items = [{"id": i} for i in range(5)]
        result = ApiContract.page(items, total=10, page=1, page_size=5)
        
        self.assertEqual(len(result["items"]), 5)
        self.assertEqual(result["total"], 10)
        self.assertEqual(result["page"], 1)
        self.assertEqual(result["pages"], 2)
    
    def test_paginated_response(self):
        """分页包装响应。"""
        items = [{"id": i} for i in range(3)]
        result = ApiContract.paginated_response(items, total=10, page=1)
        
        self.assertTrue(result["success"])
        self.assertIn("data", result)
        self.assertEqual(len(result["data"]["items"]), 3)


class TestRateLimiter(unittest.TestCase):
    """速率限制器测试。"""
    
    def test_allows_within_limit(self):
        """限制内允许。"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        for i in range(5):
            self.assertTrue(limiter.is_allowed("test"))
    
    def test_blocks_over_limit(self):
        """超限拒绝。"""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        
        limiter.is_allowed("test")
        limiter.is_allowed("test")
        limiter.is_allowed("test")
        
        self.assertFalse(limiter.is_allowed("test"))
    
    def test_different_keys(self):
        """不同key独立计数。"""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        limiter.is_allowed("key1")
        limiter.is_allowed("key1")
        
        self.assertFalse(limiter.is_allowed("key1"))
        self.assertTrue(limiter.is_allowed("key2"))


class TestConvenienceFunctions(unittest.TestCase):
    """便捷函数测试。"""
    
    def test_create_success(self):
        """create_success_response。"""
        result = create_success_response({"data": 123})
        self.assertTrue(result["success"])
        self.assertEqual(result["data"], {"data": 123})
    
    def test_create_error(self):
        """create_error_response。"""
        result = create_error_response(ErrorCode.TOKEN_INVALID, "测试错误")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["code"], "E001")


if __name__ == '__main__':
    unittest.main()