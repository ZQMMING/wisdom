"""Schema: Case — 命例数据模型

支持多层级验证：
- L0: 出生数据正确性
- L1: 算法正确性（八字/河洛/紫微计算）
- L2: 结构推断（本命/元堂/流年/流月/流日）
- L3: 历史事件回测（盲测）
- L4: 泛化能力（换案例/年代/来源）
- L5: 前瞻预测（冻结后预测未来）
"""
from __future__ import annotations
import enum
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


class EvidenceGrade(enum.Enum):
    """证据等级。Golden Dataset只允许A/B级。"""
    A = "A"           # 明确原始记录
    B = "B"           # 多来源交叉验证
    C = "C"           # 命理文章声称
    D = "D"           # 论坛匿名案例
    E = "E"           # 无法验证

    @property
    def is_golden(self) -> bool:
        return self in (EvidenceGrade.A, EvidenceGrade.B)


class EventSeverity(enum.IntEnum):
    """事件严重程度。"""
    TRIVIAL = 1       # 普通
    SLIGHT = 2        # 轻微变化
    MODERATE = 3      # 明显变化
    MAJOR = 4         # 重大人生事件
    CRITICAL = 5      # 极重大人生事件


class EventCategory(enum.Enum):
    """事件分类。"""
    # 婚姻
    MARRIAGE = "MARRIAGE"
    ENGAGEMENT = "ENGAGEMENT"
    DIVORCE = "DIVORCE"
    SEPARATION = "SEPARATION"
    NEW_RELATIONSHIP = "NEW_RELATIONSHIP"
    RELATIONSHIP_CRISIS = "RELATIONSHIP_CRISIS"
    # 事业
    JOB_CHANGE = "JOB_CHANGE"
    PROMOTION = "PROMOTION"
    RESIGNATION = "RESIGNATION"
    ENTREPRENEURSHIP = "ENTREPRENEURSHIP"
    BUSINESS_FAILURE = "BUSINESS_FAILURE"
    BUSINESS_EXPANSION = "BUSINESS_EXPANSION"
    CAREER_TRANSITION = "CAREER_TRANSITION"
    # 财务
    MAJOR_INCOME = "MAJOR_INCOME"
    MAJOR_EXPENSE = "MAJOR_EXPENSE"
    PROPERTY_PURCHASE = "PROPERTY_PURCHASE"
    PROPERTY_SALE = "PROPERTY_SALE"
    INVESTMENT = "INVESTMENT"
    DEBT = "DEBT"
    FINANCIAL_LOSS = "FINANCIAL_LOSS"
    # 家庭
    CHILD_BIRTH = "CHILD_BIRTH"
    PARENT_DEATH = "PARENT_DEATH"
    PARENT_ILLNESS = "PARENT_ILLNESS"
    FAMILY_CHANGE = "FAMILY_CHANGE"
    RELOCATION = "RELOCATION"
    # 教育
    GRADUATION = "GRADUATION"
    EXAM = "EXAM"
    ADMISSION = "ADMISSION"
    DEGREE = "DEGREE"
    # 健康（谨慎使用）
    HOSPITALIZATION = "HOSPITALIZATION"
    SURGERY = "SURGERY"
    MAJOR_HEALTH_EVENT = "MAJOR_HEALTH_EVENT"
    ACCIDENT = "ACCIDENT"


@dataclass
class Event:
    """单个历史事件。"""
    date: date
    category: EventCategory
    severity: EventSeverity
    description: str
    evidence_grade: EvidenceGrade = EvidenceGrade.C
    source_url: Optional[str] = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "category": self.category.value,
            "severity": int(self.severity),
            "description": self.description,
            "evidence_grade": self.evidence_grade.value,
            "source_url": self.source_url,
            "tags": self.tags,
        }


@dataclass
class Case:
    """命例：出生信息 + 历史事件序列。"""
    case_id: str
    gender: str                          # "male" / "female"
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int                      # 24h format, 0-23
    birth_location: Optional[str] = None # 出生地点（时区校正用）
    timezone: str = "Asia/Shanghai"
    calendar_system: str = "solar"       # solar / lunar

    # 历史事件（按时间排序）
    events: list[Event] = field(default_factory=list)

    # 元数据
    source_url: Optional[str] = None
    source_type: str = "unknown"         # manual / mingli_bench / fate_bench / iztro
    notes: str = ""

    @property
    def birth_date_tuple(self) -> tuple[int, int, int, int]:
        return (self.birth_year, self.birth_month, self.birth_day, self.birth_hour)

    @property
    def min_event_year(self) -> Optional[int]:
        return min((e.date.year for e in self.events), default=None)

    @property
    def max_event_year(self) -> Optional[int]:
        return max((e.date.year for e in self.events), default=None)

    @property
    def golden_events(self) -> list[Event]:
        return [e for e in self.events if e.evidence_grade.is_golden]

    @property
    def major_events(self) -> list[Event]:
        return [e for e in self.events if e.severity >= EventSeverity.MAJOR]

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "gender": self.gender,
            "birth_date": f"{self.birth_year}-{self.birth_month:02d}-{self.birth_day:02d}",
            "birth_hour": self.birth_hour,
            "timezone": self.timezone,
            "event_count": len(self.events),
            "golden_event_count": len(self.golden_events),
            "major_event_count": len(self.major_events),
            "source_type": self.source_type,
        }
