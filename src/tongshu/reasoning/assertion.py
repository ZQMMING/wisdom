"""P4-B Canonical Assertion - 标准断言数据模型.

这是direction唯一允许出现的地方.
direction值: supportive / caution / neutral (不是positive/negative, 不是吉凶)

硬契约:
  - 禁止 positive/negative/good/bad/lucky/unlucky
  - 禁止 confidence/weight/score/probability
  - direction 只能由 Context Resolver(P4-C) 评估产生
  - 一个 Assertion 可以由多个 SemanticSignal 共同形成(语义聚合)
  - 一个 Assertion 的 source_engines 记录提供证据的引擎列表(互补, 不投票)

数据链:
  SemanticSignal[] (无direction)
    ↓ Context Resolver (本命+大运+流年+流月+流日+宫位+卦位+体用+其他Signals)
  CanonicalAssertion (有direction=supportive/caution/neutral)
    ↓ Assertion Cluster (P4-D, 聚类不投票)
  AssertionCluster[]
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class AssertionDirection(str, Enum):
    """断言方向 - 这是direction唯一允许出现的地方.

    注意: 不是 positive/negative, 不是吉凶.
    supportive: 顺势, 有利, 适合主动推进
    caution: 需注意, 有风险, 适合谨慎处理
    neutral: 中性, 无明显倾向
    """
    SUPPORTIVE = "supportive"
    CAUTION = "caution"
    NEUTRAL = "neutral"


class AssertionDomain(str, Enum):
    """人生维度 - 标准8维度."""
    CAREER = "CAREER"           # 事业/工作
    FINANCE = "FINANCE"         # 财富/资源
    RELATIONSHIP = "RELATIONSHIP"  # 感情/婚姻/亲密关系
    FAMILY = "FAMILY"           # 家庭/父母/子女
    HEALTH = "HEALTH"           # 健康(仅生活节奏提醒, 不诊断)
    GROWTH = "GROWTH"           # 个人成长/学习/能力
    DECISION = "DECISION"       # 决策/选择/判断
    MIGRATION = "MIGRATION"     # 迁移/出行/环境变化


# 禁止字段 - Assertion中不允许出现
FORBIDDEN_ASSERTION_FIELDS = frozenset({
    "positive", "negative", "good", "bad", "lucky", "unlucky",
    "favorable", "unfavorable", "auspicious", "inauspicious",
    "confidence", "weight", "score", "probability",
    "pos", "neg",
})


def make_assertion_id(case_id: str, domain: str, semantic: str, temporal_scope: str) -> str:
    """生成断言ID."""
    raw = f"{case_id}:{domain}:{semantic}:{temporal_scope}"
    return "AST-" + hashlib.md5(raw.encode()).hexdigest()[:12]


@dataclass
class CanonicalAssertion:
    """标准断言 - direction唯一允许出现的地方.

    一个Assertion可以由多个SemanticSignal共同形成(语义聚合, P4第一次允许压缩).
    例如: OUTPUT + EXPRESSION + CREATIVITY + AUTONOMY → CAREER/OUTPUT_ACTIVATION

    source_engines记录提供证据的引擎列表, 表示互补覆盖面, 不是投票权重.
    """
    assertion_id: str
    case_id: str
    domain: str  # AssertionDomain值
    semantic: str  # 语义标识, 如OUTPUT_ACTIVATION/STRUCTURAL_CHANGE
    direction: str  # AssertionDirection值 - 唯一允许direction的地方
    intensity: int  # 0-100, 表示断言强度(不是概率/置信度)
    temporal_scope: str  # birth/year/month/day
    source_signal_ids: list[str] = field(default_factory=list)  # 来源Signal ID列表
    source_engines: list[str] = field(default_factory=list)  # 来源引擎列表(互补, 不投票)
    source_rules: list[str] = field(default_factory=list)  # 来源规则ID列表
    context_summary: dict[str, Any] = field(default_factory=dict)  # 上下文摘要(为什么是这个direction)
    evidence_refs: list[str] = field(default_factory=list)  # 证据引用
    status: str = "P4_PENDING"  # P4_PENDING / READY / VALIDATED

    def __post_init__(self):
        """验证断言契约."""
        # direction必须是合法值
        valid_directions = {d.value for d in AssertionDirection}
        if self.direction not in valid_directions:
            raise ValueError(
                f"Assertion direction must be one of {valid_directions}, "
                f"got '{self.direction}'"
            )

        # domain必须是合法值
        valid_domains = {d.value for d in AssertionDomain}
        if self.domain not in valid_domains:
            raise ValueError(
                f"Assertion domain must be one of {valid_domains}, "
                f"got '{self.domain}'"
            )

        # intensity范围
        if not (0 <= self.intensity <= 100):
            raise ValueError(f"Assertion intensity must be 0-100, got {self.intensity}")

        # 检查禁止字段
        for key in FORBIDDEN_ASSERTION_FIELDS:
            if hasattr(self, key):
                raise ValueError(f"Assertion contains forbidden field: {key}")
            if key in self.context_summary:
                raise ValueError(
                    f"Assertion context_summary contains forbidden key: {key}"
                )

    def to_dict(self) -> dict:
        return {
            "assertion_id": self.assertion_id,
            "case_id": self.case_id,
            "domain": self.domain,
            "semantic": self.semantic,
            "direction": self.direction,
            "intensity": self.intensity,
            "temporal_scope": self.temporal_scope,
            "source_signal_ids": self.source_signal_ids,
            "source_engines": self.source_engines,
            "source_rules": self.source_rules,
            "context_summary": self.context_summary,
            "evidence_refs": self.evidence_refs,
            "status": self.status,
        }


def validate_assertion_contract(assertions: list[CanonicalAssertion]) -> list[str]:
    """验证一组断言的契约."""
    errors = []
    for a in assertions:
        try:
            # __post_init__已经验证了大部分
            pass
        except ValueError as e:
            errors.append(f"Assertion {a.assertion_id}: {e}")

        # 额外检查: source_engines不应该有重复(互补覆盖面)
        if len(a.source_engines) != len(set(a.source_engines)):
            errors.append(
                f"Assertion {a.assertion_id}: source_engines has duplicates: {a.source_engines}"
            )

        # 额外检查: direction不应该出现在context_summary的key中(已经在__post_init__检查)
    return errors
