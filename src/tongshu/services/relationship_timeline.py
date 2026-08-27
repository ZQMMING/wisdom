# -*- coding: utf-8 -*-
"""
Phase 8-B: Relationship Timeline 模块

保存关系历史，形成趋势分析。
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RelationshipRecord:
    """关系历史记录。"""
    record_id: str
    relationship_id: str
    date: date
    state_title: str
    interaction_pattern: str
    sync_phase: str
    strength_level: str
    summary: str


@dataclass
class DailyRelationshipState:
    """双人每日状态。"""
    date: date
    person_a_state: str
    person_b_state: str
    interaction: str
    suitable_actions: List[str]
    attention_points: List[str]


class RelationshipTimeline:
    """
    关系时间线服务。
    
    功能:
    - 保存关系历史
    - 查询历史趋势
    - 生成双人每日状态
    """
    
    def __init__(self):
        self._records: List[RelationshipRecord] = []
    
    def add_record(self, record: RelationshipRecord) -> None:
        """添加历史记录。"""
        self._records.append(record)
        logger.info(f'添加关系记录: {record.date}')
    
    def get_history(
        self,
        relationship_id: str,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """
        获取关系历史。
        
        Args:
            relationship_id: 关系ID
            limit: 返回数量
        
        Returns:
            List[Dict]: 历史记录列表
        """
        # 简化：返回所有记录（实际应按relationship_id过滤）
        records = self._records[-limit:] if limit > 0 else self._records
        
        return [
            {
                "date": str(r.date),
                "state": r.state_title,
                "pattern": r.interaction_pattern,
                "sync_phase": r.sync_phase,
                "strength": r.strength_level
            }
            for r in records
        ]
    
    def compute_daily_state(
        self,
        person_a_state: str,
        person_b_state: str,
        current_date: Optional[date] = None
    ) -> DailyRelationshipState:
        """
        计算双人每日状态。
        
        Args:
            person_a_state: A的当前状态
            person_b_state: B的当前状态
            current_date: 日期，默认今天
        
        Returns:
            DailyRelationshipState
        """
        if current_date is None:
            current_date = date.today()
        
        # 简化逻辑：基于状态组合生成建议
        suitable = []
        attention = []
        interaction = "neutral"
        
        if person_a_state == "stable" and person_b_state == "stable":
            interaction = "协同期"
            suitable = ["深入沟通", "规划未来", "共同决策"]
            attention = ["保持节奏", "不要过度解读"]
        elif person_a_state == "expanding" and person_b_state == "stable":
            interaction = "引领期"
            suitable = ["主动推进", "表达想法"]
            attention = ["给对方空间", "避免压力"]
        elif person_a_state == "adjusting" and person_b_state == "adjusting":
            interaction = "调整期"
            suitable = ["各自沉淀", "轻度互动"]
            attention = ["不要强求一致", "尊重差异"]
        else:
            suitable = ["保持沟通", "观察节奏"]
            attention = ["注意情绪变化"]
        
        return DailyRelationshipState(
            date=current_date,
            person_a_state=person_a_state,
            person_b_state=person_b_state,
            interaction=interaction,
            suitable_actions=suitable,
            attention_points=attention
        )


# 全局实例
_timeline: Optional[RelationshipTimeline] = None


def get_timeline() -> RelationshipTimeline:
    """获取时间线实例。"""
    global _timeline
    if _timeline is None:
        _timeline = RelationshipTimeline()
    return _timeline