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
    STRUCTURAL = "STRUCTURAL"                    # 先天结构是什么
    ACTIVATION = "ACTIVATION"                    # 当前时间激活什么结构
    ENVIRONMENT_FIT = "ENVIRONMENT_FIT"          # 生活地与先天结构关系
    DIRECTION = "DIRECTION"                      # 哪种环境/方向更顺势
    TIMING_WINDOW = "TIMING_WINDOW"              # 哪个时间段具备某类结构条件
    CONDITIONAL_EVENT = "CONDITIONAL_EVENT"      # 仅证据足够时的条件式事件
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"  # 拒断(合法且优先)


class Confidence(str, Enum):
    """§5 置信分级(冻结, V11: 删除CONFLICTED).

    方法论: 互补不比较, 反方向=算法错误. 体系间方向相反不再产出"冲突"置信,
    而是触发审计信号(AuditFlag)驱动算法修复.
    """
    SUPPORTED = "SUPPORTED"                      # 多体系收敛, 证据充分
    LIKELY = "LIKELY"                            # 部分收敛, 有依据
    WEAK = "WEAK"                                # 单体系/弱信号
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"  # 信息不足, 拒断


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


# 允许携带 conditions 的断言类型(Rule 03/05)
_CONDITIONAL_TYPES = frozenset({
    AssertionType.CONDITIONAL_EVENT,
    AssertionType.DIRECTION,
    AssertionType.TIMING_WINDOW,
})


class InputBoundaryError(ValueError):
    """Rule 01/02 违规: 断言输入携带了禁止的用户隐式依赖。"""

# Rule 02 — 禁止作为输入的字段(人/事隐变量)
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
    birth_datetime: str                          # ISO8601 出生时间 → 先天结构
    birth_location: str | None = None            # 出生地 → 初始环境参照
    current_living_location: str | None = None   # 生活地 → 可操作后天场域

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
    system: str          # ziping / blind / ziwei / heluo / ditiansui ...
    signal_ref: str      # 该体系内部的 signal/rule 引用
    agrees: bool | None = None   # 与断言主方向是否一致(None=未参与裁定)


@dataclass(frozen=True)
class AuditFlag:
    """V11: 审计信号 — 反方向=算法错误, 触发审计而非"冲突".

    当主题层发现多体系在同一主题方向相反时, 生成 AuditFlag:
    - 不进最终断言结论(不输出"冲突"状态)
    - 独立输出, 驱动该引擎算法审计修复
    """
    topic: str                                # 发生反方向的主题(如 marriage)
    conflicting_engines: tuple[str, ...]      # 方向相反的引擎列表, 如 ("ziwei: positive", "ziping: negative")
    hypothesis: str = ""                      # 疑因(哪个引擎算法可能出错/维度未对齐)
    action: str = "audit"                     # 建议动作(默认进入算法审计)

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
    subject: str                       # 事业/财运/婚姻/健康/人际/环境…
    assertion_type: AssertionType
    state: StateKind = StateKind.UNDEFINED
    direction: Direction = Direction.NEUTRAL
    mechanism: str = ""                # 原局结构+大运引动+流年触发 证据机制链
    time: str = ""                     # 大运/流年/流月/流日 窗口描述
    conditions: tuple[str, ...] = ()   # 条件式前提(仅条件式类型允许非空)
    evidence: tuple[EvidenceRef, ...] = ()
    confidence: Confidence = Confidence.INSUFFICIENT_EVIDENCE
    abstain: bool = True               # Rule 04: 默认拒断, Producer 显式解除
    # V3: 倪海厦"命好不如限好" — 大运(限)为主, 流年为辅
    dayun_direction: Direction = Direction.NEUTRAL   # 十年大运方向
    liunian_direction: Direction = Direction.NEUTRAL # 流年方向
    dayun_weight: float = 0.6          # 大运权重(默认0.6, 限好>命好)
    liunian_weight: float = 0.4        # 流年权重(默认0.4, 流年为辅)
    # V3: 倪海厦"画险趋吉" — 建设性建议, 不只说吉凶
    advice: str = ""                    # 具体化解/建议(画险趋吉)
    # V4: 古籍依据校验 — 凡古籍无据者不妄断(借鉴chinese-fortune解读纪律)
    # 五大古籍: 《子平真诠》《滴天髓》《穷通宝鉴》《三命通会》《渊海子平》
    classical_refs: tuple[str, ...] = ()  # 古籍依据列表, 如 ("《滴天髓·衰旺》: 能知衰旺, 真机已达",)
    # V11: 审计信号 — 多体系方向相反时生成, 不进结论, 驱动算法审计
    audit_flags: tuple["AuditFlag", ...] = ()

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
