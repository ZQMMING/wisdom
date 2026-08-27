"""
Phase 8: 通知引擎模块

推送服务设计：
- 每日通书推送
- 节气提醒
- 重要时间节点
- 关系状态提醒
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """通知类型。"""
    DAILY_TONGSHU = "daily_tongshu"
    SOLAR_TERM = "solar_term"
    IMPORTANT_DATE = "important_date"
    RELATIONSHIP_CHANGE = "relationship_change"
    ANNUAL_CYCLE = "annual_cycle"


class NotificationStatus(str, Enum):
    """通知状态。"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


@dataclass
class NotificationPreference:
    """用户通知偏好。"""
    user_id: str
    daily_enabled: bool = True
    preferred_time: str = "08:00"
    language: str = "zh-CN"
    timezone: str = "Asia/Shanghai"


@dataclass
class NotificationLog:
    """通知日志。"""
    log_id: str
    user_id: str
    type: str
    content_version: str
    sent_time: datetime
    status: str


class NotificationEngine:
    """
    通知引擎服务。
    
    功能:
    - 管理用户通知偏好
    - 生成通知内容
    - 记录发送日志
    """
    
    def __init__(self):
        self._preferences: Dict[str, NotificationPreference] = {}
        self._logs: List[NotificationLog] = []
    
    def set_preference(self, pref: NotificationPreference) -> None:
        """设置用户通知偏好。"""
        self._preferences[pref.user_id] = pref
        logger.info(f'设置用户 {pref.user_id} 的通知偏好')
    
    def get_preference(self, user_id: str) -> Optional[NotificationPreference]:
        """获取用户通知偏好。"""
        return self._preferences.get(user_id)
    
    def should_notify(self, user_id: str, notif_type: NotificationType) -> bool:
        """检查是否应该发送通知。"""
        pref = self._preferences.get(user_id)
        if pref is None:
            return False
        
        if notif_type == NotificationType.DAILY_TONGSHU:
            return pref.daily_enabled
        
        return True  # 其他类型默认开启
    
    def log_notification(
        self,
        user_id: str,
        notif_type: NotificationType,
        content_version: str,
        status: NotificationStatus = NotificationStatus.SENT
    ) -> NotificationLog:
        """记录通知发送日志。"""
        log = NotificationLog(
            log_id=f"log_{len(self._logs)}",
            user_id=user_id,
            type=notif_type.value,
            content_version=content_version,
            sent_time=datetime.utcnow(),
            status=status.value
        )
        self._logs.append(log)
        return log
    
    def get_send_logs(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取发送日志。"""
        user_logs = [l for l in self._logs if l.user_id == user_id][-limit:]
        
        return [
            {
                "log_id": l.log_id,
                "type": l.type,
                "sent_time": str(l.sent_time),
                "status": l.status
            }
            for l in user_logs
        ]


# 全局实例
_engine: Optional[NotificationEngine] = None


def get_engine() -> NotificationEngine:
    """获取通知引擎实例。"""
    global _engine
    if _engine is None:
        _engine = NotificationEngine()
    return _engine