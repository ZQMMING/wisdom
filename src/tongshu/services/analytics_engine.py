"""
Phase 8-D: Analytics Layer 模块

用户行为分析和产品运营数据。
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserEventType(str):
    """用户事件类型。"""
    NFC_OPEN = "nfc_open"
    DAILY_VIEW = "daily_view"
    RELATIONSHIP_VIEW = "relationship_view"
    SHARE = "share"
    BIND_COMPLETE = "bind_complete"
    MODEL_CREATED = "model_created"
    PROFILE_UPDATED = "profile_updated"


@dataclass
class UserEvent:
    """用户事件记录。"""
    event_id: str
    user_id: str
    event_type: str
    timestamp: datetime
    metadata: Dict[str, Any]


class AnalyticsEngine:
    """
    分析引擎服务。
    
    功能:
    - 记录用户事件
    - 计算核心指标
    - 生成运营报告
    """
    
    def __init__(self):
        self._events: List[UserEvent] = []
    
    def record_event(self, event: UserEvent) -> None:
        """记录用户事件。"""
        self._events.append(event)
        logger.info(f'记录事件: {event.event_type} by {event.user_id}')
    
    def get_daily_active_users(self, target_date: date) -> int:
        """获取日活跃用户数(按 UTC 日界聚合,与 record_event 的 utcnow 口径一致)。

        说明: target_date 保留以维持 API 兼容;实际按当前 UTC 日期(day_start = utcnow()
        对齐的 UTC 午夜)聚合,以保证与 record_event 写入的 datetime.utcnow() 时间戳同口径,
        避免 UTC+8 凌晨窗口(00:00-08:00 本地)下本地 date.today() 与 UTC utcnow() 错位。
        """
        now_utc = datetime.utcnow()
        utc_today = now_utc.date()
        day_start = datetime.combine(utc_today, datetime.min.time())
        day_end = day_start + timedelta(days=1)

        count = sum(
            1 for e in self._events
            if day_start <= e.timestamp < day_end
        )
        return count
    
    def get_nfc_conversion_rate(self) -> float:
        """获取NFC转化率。"""
        nfc_opens = sum(
            1 for e in self._events if e.event_type == UserEventType.NFC_OPEN
        )
        bind_completes = sum(
            1 for e in self._events if e.event_type == UserEventType.BIND_COMPLETE
        )
        
        if nfc_opens == 0:
            return 0.0
        
        return bind_completes / nfc_opens
    
    def get_retention_rate(self, period_days: int = 7) -> float:
        """获取留存率。"""
        # 简化计算
        recent = datetime.utcnow() - timedelta(days=period_days)
        retained = sum(
            1 for e in self._events
            if e.timestamp >= recent
        )
        
        total = len(self._events)
        if total == 0:
            return 0.0
        
        return retained / total
    
    def get_metric_report(self) -> Dict[str, Any]:
        """获取指标报告。"""
        return {
            "daily_active_users": self.get_daily_active_users(date.today()),
            "nfc_conversion_rate": self.get_nfc_conversion_rate(),
            "retention_7d": self.get_retention_rate(7),
            "retention_30d": self.get_retention_rate(30),
            "total_events": len(self._events)
        }
    
    def get_event_counts_by_type(self) -> Dict[str, int]:
        """按类型统计事件数。"""
        counts: Dict[str, int] = {}
        for e in self._events:
            counts[e.event_type] = counts.get(e.event_type, 0) + 1
        return counts


# 全局实例
_analytics: Optional[AnalyticsEngine] = None


def get_analytics() -> AnalyticsEngine:
    """获取分析引擎实例。"""
    global _analytics
    if _analytics is None:
        _analytics = AnalyticsEngine()
    return _analytics