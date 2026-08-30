# -*- coding: utf-8 -*-
"""P1 Assertion Contract (DISPATCH_HERMES_ASSERTION_CONTRACT.md §4/§5/§9).

断言系统统一契约 — 顺天"灵魂接口"。
- 排盘负责算对, 断言系统负责说对, 词库负责怎么说。
- 原有 EVENT_SIGNAL 协议升级合并进本契约, 不再维护两套。

铁律(Rule 01-05)内建:
- Rule 01 输入边界: 只接受 birth_datetime/birth_location/current_living_location
- Rule 02 禁止隐式用户依赖
- Rule 03 条件式判断优先
- Rule 04 Abstention: INSUFFICIENT_EVIDENCE 合法且优先于错误硬断
- Rule 05 人/事为隐变量: 只能出现在 conditions, 不得伪装成已知事实
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class AssertionType(str, Enum):
    """§3 断言类型(冻结, 至少 7 种)。"""
    STRUCTURAL = "STRUCTURAL"
    ACTIVATION = "ACTIVATION"
    ENVIRONMENT_FIT = "ENVIRONMENT_FIT"
    DIRECTION = "DIRECTION"
    TIMING_WINDOW = "TIMING_WINDOW"
    CONDITIONAL_EVENT = "CONDITIONAL_EVENT"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class Confidence(str, Enum):
    """§5 置信分级(冻结)。"""
    SUPPORTED = "SUPPORTED"
    LIKELY = "LIKELY"
    WEAK = "WEAK"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class Direction(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class StateKind(str, Enum):
    """结构状态。"""
    EXPANSION = "扩张"
    CONTRACTION = "收缩"
    ACTIVATION = "激活"
    SUPPRESSION = "抑制"
    STABLE = "稳定"
    UNDEFINED = "未定"


_CONDITIONAL_TYPES = frozenset({
    AssertionType.CONDITIONAL_EVENT,
    AssertionType.DIRECTION,
    AssertionType.TIMING_WINDOW,
})


class InputBoundaryError(ValueError):
    """Rule 01/02 违规: 断言输入携带了禁止的用户隐式依赖。"""
    pass


FORBIDDEN_INPUT_FIELDS = frozenset({
    "event", "events", "occupation", "industry", "job",
    "relationship", "relationships", "person", "people",
    "plan", "plans", "question", "topic_question",
})


@dataclass(frozen=True)
class AssertionInput:
    """§2 断言系统唯一合法输入边界(Rule 01)。

    用户只能提供三个输入; 时间变量由系统计算。
    extra 字段若触碰 FORBIDDEN_INPUT_FIELDS → 构造时即抛错(Rule 02)。
    """
    birth_datetime: str = ""
    birth_location: str | None = None
    current_living_location: str | None = None

    def __post_init__(self):
        for f in FORBIDDEN_INPUT_FIELDS:
            if hasattr(self, f):
                raise InputBoundaryError(
                    f"Rule 02 violation: '{f}' is a forbidden user input "
                    "(No Hidden User Dependency)"
                )

    def validate(self) -> list[str]:
        errs = []
        if not self.birth_datetime:
            errs.append("birth_datetime is required (Rule 01)")
        return errs

    @classmethod
    def from_user_dict(cls, d: dict) -> "AssertionInput":
        """从用户提交的原始 dict 构造; 触碰禁止字段即抛 Rule 02 错误。"""
        forbidden = FORBIDDEN_INPUT_FIELDS & set(d)
        if forbidden:
            raise InputBoundaryError(
                f"Rule 02 violation: forbidden user input fields {sorted(forbidden)} "
                "(No Hidden User Dependency)"
            )
        return cls(
            birth_datetime=d.get("birth_datetime", ""),
            birth_location=d.get("birth_location"),
            current_living_location=d.get("current_living_location"),
        )


@dataclass(frozen=True)
class EvidenceRef:
    """单体系证据信号(§4 evidence 字段的结构化形态)。"""
    system: str
    signal_ref: str
    agrees: bool | None = None


@dataclass(frozen=True)
class AuditFlag:
    """V11: 审计信号 — 反方向=算法错误, 触发审计而非"冲突"。

    当主题层发现多体系在同一主题方向相反时, 生成 AuditFlag:
    - 不进最终断言结论(不输出"冲突"状态)
    - 独立输出, 驱动该引擎算法审计修复
    """
    topic: str
    conflicting_engines: tuple[str, ...]
    hypothesis: str = ""
    action: str = "audit"

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "conflicting_engines": list(self.conflicting_engines),
            "hypothesis": self.hypothesis,
            "action": self.action,
        }


@dataclass(frozen=True)
class Assertion:
    """§4 统一断言结构(冻结)。

    所有 Producer 输出同一格式; EVENT_SIGNAL 字段映射:
      system→subject(主题), rule_id→mechanism.rule_refs,
      theme→subject, direction→direction,
      strength→并入 confidence 判定, time_scope→time,
      evidence→evidence。
    """
    subject: str = ""
    assertion_type: AssertionType = AssertionType.INSUFFICIENT_EVIDENCE
    state: StateKind = StateKind.UNDEFINED
    direction: Direction = Direction.NEUTRAL
    mechanism: str = ""
    time: str = ""
    conditions: tuple[str, ...] = ()
    evidence: tuple[EvidenceRef, ...] = ()
    confidence: Confidence = Confidence.INSUFFICIENT_EVIDENCE
    abstain: bool = True
    dayun_direction: Direction = Direction.NEUTRAL
    liunian_direction: Direction = Direction.NEUTRAL
    dayun_weight: float = 0.6
    liunian_weight: float = 0.4
    advice: str = ""
    classical_refs: tuple[str, ...] = ()
    audit_flags: tuple[AuditFlag, ...] = ()

    def __post_init__(self):
        # Rule 05: 人/事只能进 conditions, 且不得伪装成已知事实
        if self.assertion_type not in _CONDITIONAL_TYPES and self.conditions:
            raise ValueError(
                f"Rule 05 violation: {self.assertion_type} may not carry "
                "conditions; human/event variables only allowed in "
                "conditional assertion types"
            )
        # Rule 04: 拒断时不得同时给出具体事件断言
        if self.abstain and self.assertion_type == AssertionType.CONDITIONAL_EVENT:
            raise ValueError(
                "Rule 04 violation: abstaining assertion cannot be "
                "CONDITIONAL_EVENT; downgrade to INSUFFICIENT_EVIDENCE"
            )
        # SUPPORTED 需多体系收敛
        if self.confidence == Confidence.SUPPORTED:
            agreeing_systems = {
                e.system for e in self.evidence if e.agrees is True
            }
            if len(agreeing_systems) < 2:
                raise ValueError(
                    "SUPPORTED requires >=2 systems in agreement "
                    "(single-system signals are downgraded per contract §9)"
                )

    def to_dict(self) -> dict:
        return {
            "subject": self.subject,
            "assertion_type": self.assertion_type.value,
            "state": self.state.value,
            "direction": self.direction.value,
            "mechanism": self.mechanism,
            "time": self.time,
            "conditions": list(self.conditions),
            "evidence": [
                {"system": e.system, "signal_ref": e.signal_ref,
                 "agrees": e.agrees}
                for e in self.evidence
            ],
            "confidence": self.confidence.value,
            "abstain": self.abstain,
            "dayun_direction": self.dayun_direction.value,
            "liunian_direction": self.liunian_direction.value,
            "dayun_weight": self.dayun_weight,
            "liunian_weight": self.liunian_weight,
            "advice": self.advice,
            "classical_refs": list(self.classical_refs),
            "audit_flags": [af.to_dict() for af in self.audit_flags],
        }


def insufficient_evidence(subject: str, reason: str) -> Assertion:
    """Rule 04 工厂: 标准拒断断言。"""
    return Assertion(
        subject=subject,
        assertion_type=AssertionType.INSUFFICIENT_EVIDENCE,
        mechanism=reason,
        confidence=Confidence.INSUFFICIENT_EVIDENCE,
        abstain=True,
    )


def from_event_signal(es: dict) -> Assertion:
    """EVENT_SIGNAL → Assertion 迁移映射(§4: 不保留两套)。

    es 需含: system/rule_id/theme/direction/strength/time_scope/confidence/evidence。
    strength 映射: >=0.66 提升一级置信, <=0.33 降低一级。
    """
    theme = es.get("theme") or es.get("system") or "unknown"
    strength = float(es.get("strength", 0.0))
    conf = es.get("confidence", "WEAK")
    order = [Confidence.INSUFFICIENT_EVIDENCE, Confidence.WEAK,
             Confidence.LIKELY, Confidence.SUPPORTED]
    try:
        idx = order.index(Confidence(conf))
    except ValueError:
        idx = 1
    if strength >= 0.66:
        idx = min(idx + 1, len(order) - 1)
    elif strength <= 0.33:
        idx = max(idx - 1, 0)
    # 单体系信号不得 SUPPORTED(契约 §9): 迁移路径保守封顶 LIKELY
    if order[idx] == Confidence.SUPPORTED:
        idx = order.index(Confidence.LIKELY)

    ev = es.get("evidence") or []
    if isinstance(ev, str):
        ev = [ev]
    refs = tuple(
        e if isinstance(e, EvidenceRef) else EvidenceRef(system="legacy", signal_ref=str(e))
        for e in ev
    )

    direction_map = {
        "INCREASE": Direction.POSITIVE, "DECREASE": Direction.NEGATIVE,
        "positive": Direction.POSITIVE, "negative": Direction.NEGATIVE,
        "neutral": Direction.NEUTRAL, "STABLE": Direction.NEUTRAL,
    }
    return Assertion(
        subject=theme,
        assertion_type=AssertionType.ACTIVATION,
        direction=direction_map.get(str(es.get("direction", "neutral")), Direction.NEUTRAL),
        mechanism=f"migrated rule: {es.get('rule_id', 'unknown')}",
        time=str(es.get("time_scope", "")),
        evidence=refs,
        confidence=order[idx],
        abstain=(order[idx] in (Confidence.WEAK, Confidence.INSUFFICIENT_EVIDENCE)),
    )


__all__ = [
    "AssertionType", "Confidence", "Direction", "StateKind",
    "AssertionInput", "Assertion", "EvidenceRef", "AuditFlag",
    "InputBoundaryError", "FORBIDDEN_INPUT_FIELDS",
    "insufficient_evidence", "from_event_signal",
]
