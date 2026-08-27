"""P3 Signal Context - 语义信号上下文评估框架.

P3阶段: 建立框架和接口, 不做实际的direction判断.
P4阶段: 实现Contextual Assertion Resolver, direction在这里产生.

硬契约:
  direction 只能由 ContextResolver.evaluate() 产生,
  不能在 SemanticSignal 中预先设定.

  评估输入:
    - 本命结构(日主/旺衰/格局/调候/扶抑)
    - 当前大运
    - 当前流年
    - 当前流月
    - 当前流日
    - 宫位/卦位/体用
    - 其他相关 SemanticSignals

  评估输出:
    CanonicalAssertion(domain, semantic, direction, intensity, ...)

  direction值:
    supportive / caution / neutral
    (不是 positive/negative, 不是吉凶)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .semantic_signal import SemanticSignal


class AssertionDirection(str, Enum):
    """Contextual Assertion的direction.

    这是P4/P5才会产生的值, P3只定义枚举.
    注意: 不是 positive/negative, 不是吉凶.
    """
    SUPPORTIVE = "supportive"    # 顺势, 有利
    CAUTION = "caution"          # 需注意, 有风险
    NEUTRAL = "neutral"          # 中性, 无明显倾向


@dataclass
class SignalContext:
    """SemanticSignal的上下文数据.

    P3阶段: 只收集和存储上下文, 不做direction判断.
    P4阶段: ContextResolver使用这些数据产生direction.
    """
    case_id: str
    birth_chart: dict[str, Any] = field(default_factory=dict)      # 本命结构
    current_dayun: Optional[dict] = None                             # 当前大运
    current_liunian: Optional[dict] = None                           # 当前流年
    current_liuyue: Optional[dict] = None                            # 当前流月
    current_liuri: Optional[dict] = None                             # 当前流日
    palace_positions: dict[str, Any] = field(default_factory=dict)  # 宫位/卦位
    ti_yong: Optional[dict] = None                                   # 体用
    other_signals: list[SemanticSignal] = field(default_factory=list)  # 其他相关信号
    extra: dict[str, Any] = field(default_factory=dict)             # 额外上下文

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "birth_chart": self.birth_chart,
            "current_dayun": self.current_dayun,
            "current_liunian": self.current_liunian,
            "current_liuyue": self.current_liuyue,
            "current_liuri": self.current_liuri,
            "palace_positions": self.palace_positions,
            "ti_yong": self.ti_yong,
            "other_signals_count": len(self.other_signals),
            "extra": self.extra,
        }


class ContextResolver:
    """上下文评估器 - P4实现, P3只定义接口.

    硬契约:
      direction 只能在这里产生.
      输入: SemanticSignal + SignalContext
      输出: CanonicalAssertion(direction=supportive/caution/neutral)

    P3阶段: 所有evaluate()调用返回direction=neutral,
    并标记"P4_PENDING", 明确表示direction尚未实现.
    """

    def __init__(self):
        self._p4_pending = True  # P3阶段标记

    def evaluate(
        self,
        signal: SemanticSignal,
        context: SignalContext,
    ) -> dict:
        """评估一个SemanticSignal的上下文, 产生CanonicalAssertion.

        P3阶段: 返回direction=neutral, 标记P4_PENDING.
        P4阶段: 实现真正的上下文评估逻辑.
        """
        return {
            "assertion_id": f"AST-{signal.signal_id}",
            "case_id": signal.case_id,
            "domain": "GENERAL",  # P4: 根据atom_id和context推断domain
            "semantic": signal.atom_id,
            "direction": AssertionDirection.NEUTRAL.value,
            "intensity": 50,  # P4: 根据上下文强度评估
            "temporal_scope": signal.temporal_scope,
            "source_engine": signal.engine,
            "source_rule": signal.rule_id,
            "signal_id": signal.signal_id,
            "status": "P4_PENDING" if self._p4_pending else "READY",
            "note": "P3: direction评估待P4实现, 当前固定neutral",
        }

    def evaluate_batch(
        self,
        signals: list[SemanticSignal],
        context: SignalContext,
    ) -> list[dict]:
        """批量评估."""
        return [self.evaluate(s, context) for s in signals]
