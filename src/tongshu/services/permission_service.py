# -*- coding: utf-8 -*-
"""
Phase 8-E: 用户等级与权限模块

Free / Premium 分级设计。
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubscriptionLevel(str, Enum):
    """订阅等级。"""
    FREE = "free"
    PREMIUM = "premium"


class FeatureAccess:
    """功能访问控制。"""
    
    # Free 等级可用功能
    FREE_FEATURES = {
        "daily_tongshu",      # 今日通书
        "basic_model",        # 基础模型
        "nfc_login",          # NFC登录
    }
    
    # Premium 等级可用功能
    PREMIUM_FEATURES = {
        "full_model",         # 完整个人模型
        "monthly_tongshu",    # 月度通书
        "yearly_tongshu",     # 年度通书
        "relationship_space", # 关系空间
        "advanced_reports",   # 高级报告
        "priority_support",   # 优先支持
    }
    
    @classmethod
    def get_features(cls, level: SubscriptionLevel) -> set:
        """获取等级对应功能。"""
        if level == SubscriptionLevel.FREE:
            return cls.FREE_FEATURES.copy()
        elif level == SubscriptionLevel.PREMIUM:
            return cls.FREE_FEATURES.copy() | cls.PREMIUM_FEATURES
        return set()
    
    @classmethod
    def has_access(cls, level: SubscriptionLevel, feature: str) -> bool:
        """检查是否有功能访问权限。"""
        features = cls.get_features(level)
        return feature in features


@dataclass
class UserProfile:
    """用户档案（含订阅信息）。"""
    user_id: str
    nickname: str
    subscription_level: SubscriptionLevel
    devices: List[Dict[str, str]]
    
    def can_access(self, feature: str) -> bool:
        """检查功能访问权限。"""
        return FeatureAccess.has_access(self.subscription_level, feature)


class PermissionService:
    """
    权限服务。
    
    功能:
    - 检查功能访问权限
    - 管理用户订阅等级
    - 设备绑定策略
    """
    
    def __init__(self):
        self._users: Dict[str, UserProfile] = {}
    
    def set_subscription(self, user_id: str, level: SubscriptionLevel) -> None:
        """设置用户订阅等级。"""
        if user_id in self._users:
            self._users[user_id].subscription_level = level
            logger.info(f'用户 {user_id} 订阅等级: {level.value}')
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """获取用户档案。"""
        return self._users.get(user_id)
    
    def register_user(self, user_id: str, nickname: str) -> UserProfile:
        """注册新用户（默认为Free）。"""
        profile = UserProfile(
            user_id=user_id,
            nickname=nickname,
            subscription_level=SubscriptionLevel.FREE,
            devices=[]
        )
        self._users[user_id] = profile
        return profile
    
    def check_feature_access(self, user_id: str, feature: str) -> bool:
        """检查功能访问权限。"""
        profile = self._users.get(user_id)
        if profile is None:
            return False
        return profile.can_access(feature)


# 全局实例
_permission_service: Optional[PermissionService] = None


def get_permission_service() -> PermissionService:
    """获取权限服务实例。"""
    global _permission_service
    if _permission_service is None:
        _permission_service = PermissionService()
    return _permission_service