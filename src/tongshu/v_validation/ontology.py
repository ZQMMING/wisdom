"""Event Ontology V1 — 事件本体论

使用 schema.case.py 中的 EventCategory, EventSeverity, EvidenceGrade
提供匹配规则、验证规则和本体工具类。
"""
from __future__ import annotations
import re
from datetime import date, timedelta
from typing import Optional, List, Tuple

from .schema.case import Event, EventCategory, EventSeverity, EvidenceGrade


# ─── 事件类别层级 ─────────────────────────────────────────────────────────

class EventHierarchy:
    """事件类别层级关系。"""
    
    # 人生大事
    LIFE_EVENTS = {
        EventCategory.CHILD_BIRTH,
        EventCategory.PARENT_DEATH,
        EventCategory.MARRIAGE,
        EventCategory.DIVORCE,
    }
    
    # 事业事件
    CAREER_EVENTS = {
        EventCategory.JOB_CHANGE,
        EventCategory.PROMOTION,
        EventCategory.RESIGNATION,
        EventCategory.ENTREPRENEURSHIP,
        EventCategory.BUSINESS_FAILURE,
        EventCategory.BUSINESS_EXPANSION,
        EventCategory.CAREER_TRANSITION,
    }
    
    # 财务事件
    FINANCE_EVENTS = {
        EventCategory.MAJOR_INCOME,
        EventCategory.MAJOR_EXPENSE,
        EventCategory.PROPERTY_PURCHASE,
        EventCategory.PROPERTY_SALE,
        EventCategory.INVESTMENT,
        EventCategory.DEBT,
        EventCategory.FINANCIAL_LOSS,
    }
    
    # 家庭事件
    FAMILY_EVENTS = {
        EventCategory.CHILD_BIRTH,  # 生子
        EventCategory.NEW_RELATIONSHIP,
        EventCategory.FAMILY_CHANGE,
        EventCategory.RELOCATION,
    }
    
    # 教育事件
    EDUCATION_EVENTS = {
        EventCategory.EXAM,
        EventCategory.GRADUATION,
        EventCategory.ADMISSION,
        EventCategory.DEGREE,
    }
    
    # 健康事件（谨慎使用）
    HEALTH_EVENTS = {
        EventCategory.HOSPITALIZATION,
        EventCategory.SURGERY,
        EventCategory.MAJOR_HEALTH_EVENT,
        EventCategory.ACCIDENT,
    }
    
    @classmethod
    def get_category_group(cls, category: EventCategory) -> str:
        """获取事件类别分组。"""
        if category in cls.LIFE_EVENTS:
            return "life"
        elif category in cls.CAREER_EVENTS:
            return "career"
        elif category in cls.FINANCE_EVENTS:
            return "finance"
        elif category in cls.FAMILY_EVENTS:
            return "family"
        elif category in cls.EDUCATION_EVENTS:
            return "education"
        elif category in cls.HEALTH_EVENTS:
            return "health"
        return "other"
    
    @classmethod
    def get_primary_domains(cls, events: List[Event]) -> List[str]:
        """获取命主的主要关注领域。"""
        domain_count = {}
        for e in events:
            group = cls.get_category_group(e.category)
            domain_count[group] = domain_count.get(group, 0) + 1
        return sorted(domain_count.keys(), key=lambda x: domain_count[x], reverse=True)


# ─── 严重程度权重 ─────────────────────────────────────────────────────────

class SeverityScoring:
    """严重程度评分标准。"""
    
    # 权重映射
    WEIGHTS = {
        EventSeverity.TRIVIAL: 0.1,
        EventSeverity.SLIGHT: 0.3,
        EventSeverity.MODERATE: 0.5,
        EventSeverity.MAJOR: 0.8,
        EventSeverity.CRITICAL: 1.0,
    }
    
    # 时间容忍度（预测与实际的时间差允许范围）
    TIME_TOLERANCE = {
        EventSeverity.TRIVIAL: timedelta(days=365),     # 1年
        EventSeverity.SLIGHT: timedelta(days=180),      # 6个月
        EventSeverity.MODERATE: timedelta(days=90),     # 3个月
        EventSeverity.MAJOR: timedelta(days=30),        # 1个月
        EventSeverity.CRITICAL: timedelta(days=7),      # 1周
    }
    
    @classmethod
    def get_weight(cls, severity: EventSeverity) -> float:
        """获取严重程度权重。"""
        return cls.WEIGHTS.get(severity, 0.5)
    
    @classmethod
    def get_tolerance(cls, severity: EventSeverity) -> timedelta:
        """获取时间容忍度。"""
        return cls.TIME_TOLERANCE.get(severity, timedelta(days=90))


# ─── 事件匹配器 ────────────────────────────────────────────────────────────

class EventMatcher:
    """事件匹配规则引擎。"""
    
    @classmethod
    def matches(
        cls,
        predicted: Event,
        actual: Event,
        tolerance: Optional[timedelta] = None
    ) -> bool:
        """检查预测事件与实际事件是否匹配。"""
        # 类别必须完全匹配
        if predicted.category != actual.category:
            return False
        
        # 计算时间差
        date_diff = abs((predicted.date - actual.date).days)
        
        # 使用严重程度决定的容忍度
        time_tol = tolerance or SeverityScoring.get_tolerance(actual.severity)
        
        return date_diff <= time_tol.days
    
    @classmethod
    def partial_match(
        cls,
        predicted: Event,
        actual: Event,
        min_severity: EventSeverity = EventSeverity.MODERATE
    ) -> bool:
        """部分匹配：类别相同，严重程度不低于最小值。"""
        if predicted.category != actual.category:
            return False
        if actual.severity.value < min_severity.value:
            return False
        return True
    
    @classmethod
    def fuzzy_match(
        cls,
        predicted: Event,
        actual: Event,
        category_tolerance: Optional[EventCategory] = None
    ) -> bool:
        """模糊匹配：允许类别在容忍范围内匹配。"""
        # 严格匹配
        if predicted.category == actual.category:
            return cls.matches(predicted, actual)
        
        # 模糊匹配：同一分组内的类别可以互相匹配
        predicted_group = EventHierarchy.get_category_group(predicted.category)
        actual_group = EventHierarchy.get_category_group(actual.category)
        
        return (predicted_group == actual_group and 
                SeverityScoring.get_tolerance(max(predicted.severity, actual.severity)).days >= 
                abs((predicted.date - actual.date).days))


# ─── 事件验证器 ────────────────────────────────────────────────────────────

class EventValidator:
    """事件验证规则。"""
    
    # 必填字段
    REQUIRED_FIELDS = ["date", "category", "severity", "description"]
    
    # 禁止的逻辑组合
    LOGIC_CONFLICTS = [
        # 同一天既出生又去世
        (EventCategory.CHILD_BIRTH, EventCategory.PARENT_DEATH),
        # 同一天结婚又离婚
        (EventCategory.MARRIAGE, EventCategory.DIVORCE),
    ]
    
    @classmethod
    def validate(cls, event: Event) -> Tuple[bool, List[str]]:
        """验证事件是否有效。"""
        errors = []
        
        # 检查必填字段
        for field in cls.REQUIRED_FIELDS:
            if not hasattr(event, field) or getattr(event, field) is None:
                errors.append(f"Missing required field: {field}")
        
        # 检查日期合法性
        if event.date and event.date > date(2026, 8, 22):
            errors.append("Date cannot be in the future")
        
        # 检查严重程度范围
        if event.severity.value < 1 or event.severity.value > 5:
            errors.append("Severity must be between 1 and 5")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_case(cls, case: 'Case') -> Tuple[bool, List[str]]:
        """验证整个命例。"""
        errors = []
        
        # 检查出生年份
        if case.birth_year <= 0:
            errors.append(f"Invalid birth year: {case.birth_year}")
        
        # 检查事件序列
        for i, e in enumerate(case.events):
            valid, event_errors = cls.validate(e)
            if not valid:
                errors.extend([f"Event {i}: {err}" for err in event_errors])
        
        # 检查时间顺序
        for i in range(len(case.events) - 1):
            if case.events[i].date > case.events[i+1].date:
                errors.append(f"Events not in chronological order at index {i}")
        
        # 检查逻辑冲突
        for i, e1 in enumerate(case.events):
            for j, e2 in enumerate(case.events[i+1:], i+1):
                if e1.date == e2.date:
                    for conf_pair in cls.LOGIC_CONFLICTS:
                        if e1.category in conf_pair and e2.category in conf_pair:
                            errors.append(f"Logic conflict: {e1.category} and {e2.category} on {e1.date}")
        
        return len(errors) == 0, errors


# ─── 事件本体主类 ──────────────────────────────────────────────────────────

class EventOntology:
    """事件本体主类，整合所有规则。"""
    
    def __init__(self):
        self.hierarchy = EventHierarchy()
        self.scoring = SeverityScoring()
        self.matcher = EventMatcher()
        self.validator = EventValidator()
    
    def classify_event(self, description: str) -> EventCategory:
        """根据描述自动分类事件。"""
        keywords = {
            EventCategory.CHILD_BIRTH: ["出生", "诞生", "降生"],
            EventCategory.PARENT_DEATH: ["去世", "逝世", "死亡", "卒", "终"],
            EventCategory.MARRIAGE: ["娶", "嫁", "婚", "配", "结缡"],
            EventCategory.EXAM: ["中举", "中进士", "科举", "及第", "登科"],
            EventCategory.JOB_CHANGE: ["任", "迁", "调", "入", "出"],
            EventCategory.PROMOTION: ["擢", "升", "晋", "进"],
            EventCategory.RELOCATION: ["迁", "谪", "贬", "流放", "徙", "移"],
            EventCategory.FAMILY_CHANGE: ["乱", "变", "难", "灾", "祸"],
        }
        
        for category, kws in keywords.items():
            for kw in kws:
                if kw in description:
                    return category
        
        return EventCategory.FAMILY_CHANGE  # 默认类别
    
    def get_default_severity(self, category: EventCategory, description: str) -> EventSeverity:
        """根据类别和描述获取默认严重程度。"""
        critical_keywords = ["去世", "逝世", "死亡", "战死", "赐死", "自杀", "殉国"]
        major_keywords = ["中举", "中进士", "擢", "升", "贬", "流放", "谪"]
        
        for kw in critical_keywords:
            if kw in description:
                return EventSeverity.CRITICAL
        
        for kw in major_keywords:
            if kw in description:
                return EventSeverity.MAJOR
        
        return EventSeverity.MODERATE
    
    def generate_event(
        self, 
        description: str, 
        date_val: date,
        source_grade: EvidenceGrade = EvidenceGrade.B
    ) -> Event:
        """生成标准化事件。"""
        category = self.classify_event(description)
        severity = self.get_default_severity(category, description)
        
        return Event(
            date=date_val,
            category=category,
            severity=severity,
            description=description,
            evidence_grade=source_grade,
        )


# ─── 导出 ──────────────────────────────────────────────────────────────────

__all__ = [
    "EventOntology",
    "EventHierarchy",
    "SeverityScoring",
    "EventMatcher",
    "EventValidator",
    "Event",
    "EventCategory",
    "EventSeverity",
    "EvidenceGrade",
]
