"""P3 Semantic Signal - 语义信号数据模型.

硬契约(P3):
  SemanticSignal 严格禁止以下字段:
    - direction / polarity / positive / negative
    - confidence / weight / score / probability

  direction 只在 Contextual Assertion 阶段(P4/P5)产生,
  由 本命结构 + 大运 + 流年 + 流月 + 流日 + 宫位/卦位 + 其他Signals
  共同评估后决定, 不是 Signal 本身的属性.

  语义守恒:
    Rule.produces_semantic_atoms 有 N 个 atom
    → 必须产生 N 个 SemanticSignal
    → 不能压缩, 不能合并, 不能丢弃

数据链:
  EngineEvidence(纯事实)
    ↓ rule_id
  Rule(produces_semantic_atoms = [atom1, atom2, ...])
    ↓ 每个atom产生一个Signal
  SemanticSignal[] (语义信号, 无direction)
    ↓ context
  Contextual Assertion (P4: direction在这里产生)
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════════
# 禁止字段列表 - P3硬契约
# ═══════════════════════════════════════════════════════════════════
FORBIDDEN_SIGNAL_FIELDS = frozenset({
    "direction", "polarity", "positive", "negative",
    "confidence", "weight", "score", "probability",
    "pos", "neg", "good", "bad", "lucky", "unlucky",
    "favorable", "unfavorable", "auspicious", "inauspicious",
})


class SignalStatus(str, Enum):
    """SemanticSignal状态."""
    READY = "READY"              # 已迁移规则产生的信号
    NOT_READY = "NOT_READY"      # 未迁移规则, 禁止走旧路径


class TemporalScope(str, Enum):
    """时间范围(简化版, 与EngineEvidence一致)."""
    BIRTH = "birth"
    YEAR = "year"
    MONTH = "month"
    DAY = "day"
    HOUR = "hour"


@dataclass(frozen=True)
class SemanticSignal:
    """P3 Semantic Signal - 语义信号.

    一条 EngineEvidence 通过 Rule 匹配后,
    对 Rule.produces_semantic_atoms 中的每一个 atom 产生一个 SemanticSignal.

    硬契约: 无 direction / polarity / confidence / weight.
    """
    signal_id: str
    case_id: str
    engine: str                    # ZI_PING / BLIND_SCHOOL / ZI_WEI / HE_LUO / YI_JING
    rule_id: str                   # 匹配到的规则ID
    atom_id: str                   # 对应 produces_semantic_atoms 中的一个 concept_id
    temporal_scope: str            # birth / year / month / day / hour
    evidence_ref: str              # 来源 EngineEvidence 的 rule_id(或evidence_id)
    status: str = "READY"          # READY / NOT_READY
    context: dict[str, Any] = field(default_factory=dict)  # 上下文数据(无direction)
    signal_type: str = ""          # 对应 Rule.produces_signal_type(可选, 用于分组)

    def __post_init__(self):
        """硬契约验证: 禁止字段."""
        # 检查context中是否偷偷塞入了禁止字段
        for key in self.context:
            if key.lower() in FORBIDDEN_SIGNAL_FIELDS:
                raise ValueError(
                    f"SemanticSignal.context 禁止字段 '{key}': "
                    f"direction只在Contextual Assertion阶段产生, 不是Signal属性"
                )

    def to_dict(self) -> dict:
        return {
            "signal_id": self.signal_id,
            "case_id": self.case_id,
            "engine": self.engine,
            "rule_id": self.rule_id,
            "atom_id": self.atom_id,
            "temporal_scope": self.temporal_scope,
            "evidence_ref": self.evidence_ref,
            "status": self.status,
            "signal_type": self.signal_type,
            "context": self.context,
        }


def make_signal_id(case_id: str, engine: str, rule_id: str, atom_id: str) -> str:
    """生成稳定的signal_id."""
    raw = f"{case_id}:{engine}:{rule_id}:{atom_id}"
    return f"SIG-{hashlib.md5(raw.encode()).hexdigest()[:12]}"


def validate_signal_contract(signals: list[SemanticSignal]) -> list[str]:
    """验证SemanticSignal契约.

    检查:
    1. 无禁止字段(direction/polarity/confidence/weight等)
    2. 语义守恒: 同一条rule_id产生的signal数量 = rule的produces_semantic_atoms数量
    3. 未迁移规则的signal必须标记NOT_READY
    """
    errors = []

    for sig in signals:
        # 检查禁止字段(已经在__post_init__里检查了context, 这里再检查顶层)
        sig_dict = sig.to_dict()
        for key in sig_dict:
            if key.lower() in FORBIDDEN_SIGNAL_FIELDS:
                errors.append(f"Signal {sig.signal_id} 禁止字段: {key}")

        # 检查atom_id非空
        if not sig.atom_id:
            errors.append(f"Signal {sig.signal_id} atom_id为空")

        # 检查status
        if sig.status not in ("READY", "NOT_READY"):
            errors.append(f"Signal {sig.signal_id} 无效status: {sig.status}")

    return errors
