"""
Phase 6 — Yi Engine Schema (Schema 9)

边界契约:
  1. Yi Engine 只能消费已通过 Contract 化的数据 (CanonicalSignal, TemporalEvidence, EvidenceChain)
  2. InterpInput 禁止包含任何 raw calculation fields
  3. Yi Engine 输出保持关系式结构 (STATE → OPPORTUNITY/RISK/REMEDIATION/ACTION)
  4. 严禁 fortune_score / luck_score / overall_goodness / auspicious_score
  5. Yi 不重新定义河洛链条: 本命→元堂→后天→流年→流月→流日→时刻→节候卦→卦气
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import List, Optional


class YiLayer(enum.Enum):
    """Yi 解释层。对应 V1.2 §9.1。"""
    HEXAGRAM = "HEXAGRAM"           # 层 A: 卦象
    LINE = "LINE"                    # 层 B: 爻象
    CLASSICAL = "CLASSICAL"          # 层 C: 经典
    IMAGE = "IMAGE"                  # 层 D: 象扩展
    RELATIONAL = "RELATIONAL"        # LLM 关系解释层


class YiStructureStatus(enum.Enum):
    """Yi 结构状态。"""
    VALID = "VALID"
    INCOMPLETE = "INCOMPLETE"        # 部分层缺失，仍可解释
    BLOCKED = "BLOCKED"              # 关键层缺失，无法解释
    NOT_APPLICABLE = "NOT_APPLICABLE"  # 当前 case 不适用 Yi 解释


class DirectionLabel(enum.Enum):
    """预测方向标签（不是分数，是定性描述）。"""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    CHANGE = "CHANGE"
    NEUTRAL = "NEUTRAL"
    UNCERTAIN = "UNCERTAIN"


@dataclass(frozen=True)
class YiStructure:
    """Yi Engine 结构化输出 — 由层 A/B/C/D 聚合。

    此结构只包含 Yi 可审计的解释依据:
      - 卦 (truth_hexagram)
      - 爻 (true_line)
      - 位 (position_name)
      - 时 (temporal_context)
      - 势 (ti_yong_relation)
      - 体 (ti_trigram)
      - 援 (auxiliary_relations)
      - 辞 (classical_quotes)
      - 理 (image_reasoning)
    """
    truth_hexagram: str = ""         # e.g. "地天泰"
    true_line: int = 0               # 1–6, 元堂爻
    position_name: str = ""          # e.g. "六四"
    temporal_context: str = ""       # 节候/卦气
    ti_trigram: str = ""             # 体卦
    yong_trigram: str = ""           # 用卦
    ti_yong_relation: str = ""       # 体用生克
    auxiliary_relations: List[str] = field(default_factory=list)  # 错卦/综卦/互卦
    classical_quote: str = ""        # 卦辞/爻辞原文
    classical_source: str = ""       # 出处
    image_reasoning: List[str] = field(default_factory=list)       # 象义推导链
    layer: YiLayer = YiLayer.HEXAGRAM
    status: YiStructureStatus = YiStructureStatus.INCOMPLETE

    def to_dict(self) -> dict:
        return {
            "truth_hexagram": self.truth_hexagram,
            "true_line": self.true_line,
            "position_name": self.position_name,
            "temporal_context": self.temporal_context,
            "ti_trigram": self.ti_trigram,
            "yong_trigram": self.yong_trigram,
            "ti_yong_relation": self.ti_yong_relation,
            "auxiliary_relations": self.auxiliary_relations,
            "classical_quote": self.classical_quote,
            "classical_source": self.classical_source,
            "image_reasoning": self.image_reasoning,
            "layer": self.layer.value,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class YiInterpretation:
    """Yi 解释输出 — 关系式结构，非分数。

    输出格式:
      STATE → OPPORTUNITY / RISK / REMEDIATION / ACTION
    """
    interpretation_id: str
    yi_structure_ref: str            # → YiStructure.truth_hexagram + true_line
    state: str                       # 当前状态描述
    opportunity: str = ""            # 机会/有利面向
    risk: str = ""                   # 风险/不利面向
    remediation: str = ""            # 化解/应对建议
    action: str = ""                 # 行动建议
    directional_label: DirectionLabel = DirectionLabel.UNCERTAIN
    source_refs: List[str] = field(default_factory=list)   # 可审计来源
    evidence_refs: List[str] = field(default_factory=list)  # → evidence_id
    confidence: float = 0.0          # 仅用于记录，不参与决策
    phase: int = 6                   # 必须 >= 6

    @property
    def has_fortune_score(self) -> bool:
        """严格禁止 fortune_score / luck_score 等字段。"""
        return False

    def to_dict(self) -> dict:
        return {
            "interpretation_id": self.interpretation_id,
            "yi_structure_ref": self.yi_structure_ref,
            "state": self.state,
            "opportunity": self.opportunity,
            "risk": self.risk,
            "remediation": self.remediation,
            "action": self.action,
            "directional_label": self.directional_label.value,
            "source_refs": self.source_refs,
            "evidence_refs": self.evidence_refs,
            "confidence": self.confidence,
            "phase": self.phase,
        }


# ─── Forward Validation Schema ────────────────────────────────────────────────

class ForwardValidationStatus(enum.Enum):
    """前瞻验证状态。"""
    PENDING = "PENDING"               # 预测已出，等待事件
    EVALUATABLE = "EVALUATABLE"       # 窗口期内可评估
    PASSED = "PASSED"                 # 验证通过
    FAILED = "FAILED"                 # 验证失败
    DATA_LEAKAGE = "DATA_LEAKAGE"     # 发现数据泄漏（prediction_created_at >= event_occurred_at）
    INSUFFICIENT = "INSUFFICIENT"     # 证据不足，无法评估
    SKIPPABLE = "SKIPPABLE"          # 可跳过（NOT_IMPLEMENTED/NOT_EVALUABLE）


@dataclass(frozen=True)
class PredictionRecord:
    """预测记录 — 预测时间冻结，不可修改。"""
    prediction_id: str
    interpretation_ref: str          # → YiInterpretation.interpretation_id
    prediction_direction: DirectionLabel
    prediction_window_start: int     # year
    prediction_window_end: int       # year
    created_at: str                  # ISO8601 — 预测产生时间（冻结）

    def validate_no_leakage(self, event_occurred_at: str) -> Optional[str]:
        """检查是否存在数据泄漏（预测时间 >= 事件时间）。"""
        if self.created_at >= event_occurred_at:
            return f"DATA_LEAKAGE: prediction.created_at({self.created_at}) >= event.occurred_at({event_occurred_at})"
        return None


@dataclass(frozen=True)
class EvaluationRecord:
    """事件评估记录 — 使用独立的 EvaluationToleranceWindow。"""
    evaluation_id: str
    prediction_ref: str              # → PredictionRecord.prediction_id
    actual_direction: DirectionLabel
    actual_occurred_at: str          # ISO8601
    tolerance_days: int              # 来自 severity_class
    match_result: bool = False       # 是否匹配预测窗口
    status: ForwardValidationStatus = ForwardValidationStatus.EVALUATABLE

    def to_dict(self) -> dict:
        return {
            "evaluation_id": self.evaluation_id,
            "prediction_ref": self.prediction_ref,
            "actual_direction": self.actual_direction.value,
            "actual_occurred_at": self.actual_occurred_at,
            "tolerance_days": self.tolerance_days,
            "match_result": self.match_result,
            "status": self.status.value,
        }
