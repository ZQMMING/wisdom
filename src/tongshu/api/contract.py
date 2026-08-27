# -*- coding: utf-8 -*-
"""
Phase 8-A: API Contract 实现

统一响应格式、错误处理、路由注册。
"""
from __future__ import annotations
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_VERSION = "1.0.0"


class ErrorCode(str, Enum):
    """错误码枚举。"""
    TOKEN_INVALID = "E001"
    PROFILE_MISSING = "E002"
    CALCULATION_FAILED = "E003"
    RELATIONSHIP_NOT_FOUND = "E004"
    DEVICE_NOT_BOUND = "E005"
    INVALID_INPUT = "E006"
    SERVICE_UNAVAILABLE = "E007"
    RATE_LIMITED = "E008"


@dataclass
class ErrorResponse:
    """错误响应。"""
    code: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SuccessResponse:
    """成功响应。"""
    data: Dict[str, Any]
    meta: Dict[str, str] = field(default_factory=dict)


class ApiContract:
    """
    API 响应构建器。
    
    示例:
        result = ApiContract.success(data={"hello": "world"})
        error = ApiContract.error(ErrorCode.TOKEN_INVALID, "Token已过期")
    """
    
    @staticmethod
    def success(data: Dict[str, Any], meta: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """构建成功响应。"""
        return {
            "success": True,
            "version": API_VERSION,
            "data": data,
            "meta": meta or {
                "request_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    
    @staticmethod
    def error(code: ErrorCode, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """构建错误响应。"""
        return {
            "success": False,
            "error": {
                "code": code.value,
                "message": message,
                "details": details or {}
            },
            "meta": {
                "request_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    
    @staticmethod
    def page(data: List[Any], total: int, page: int, page_size: int) -> Dict[str, Any]:
        """分页响应。"""
        return {
            "items": data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
    
    @staticmethod
    def paginated_response(
        items: List[Any],
        total: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """分页包装响应。"""
        return ApiContract.success(ApiContract.page(items, total, page, page_size))


# 全局常量
SUPPORTED_VERSIONS = ["1.0"]
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """便捷函数：创建成功响应。"""
    return ApiContract.success(data)


def create_error_response(code: ErrorCode, message: str) -> Dict[str, Any]:
    """便捷函数：创建错误响应。"""
    return ApiContract.error(code, message)


class RateLimiter:
    """简单的内存速率限制器。"""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, key: str) -> bool:
        """检查是否允许请求。"""
        now = datetime.utcnow().timestamp()
        window_start = now - self.window_seconds
        
        if key not in self._requests:
            self._requests[key] = []
        
        # 清理过期记录
        self._requests[key] = [t for t in self._requests[key] if t > window_start]
        
        if len(self._requests[key]) >= self.max_requests:
            return False
        
        self._requests[key].append(now)
        return True


# 全局速率限制器
_rate_limiters: Dict[str, RateLimiter] = {
    "auth": RateLimiter(max_requests=10, window_seconds=60),
    "tongshu": RateLimiter(max_requests=60, window_seconds=60),
    "relationship": RateLimiter(max_requests=30, window_seconds=60),
    "profile": RateLimiter(max_requests=20, window_seconds=60),
}


def check_rate_limit(category: str, client_key: str) -> bool:
    """检查速率限制。"""
    limiter = _rate_limiters.get(category)
    if limiter is None:
        return True
    return limiter.is_allowed(f"{category}:{client_key}")