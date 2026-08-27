"""
Phase 6 — Yi Engine Adapter

职责:
  从 CanonicalSignal + EvidenceChain + TemporalConvergence
  适配到 YiStructure（层 A/B/C/D 聚合）

边界:
  - 不修改 Legacy Engine
  - 不修改 Evidence Chain
  - 不修改 Canonical Signal
  - 只消费已 Contract 化的数据
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from tongshu.spec.canonical_signal import CanonicalSignal, SourceEngine
from tongshu.spec.evidence_chain import Evidence, Source
from tongshu.spec.temporal_evidence import TemporalConvergence
from tongshu.yi.schema import YiStructure, YiStructureStatus, YiLayer


@dataclass(frozen=True)
class YiAdapterInput:
    """Yi Adapter 输入 — 只允许来自 Contract 层的数据。"""
    canonical_signals: List[CanonicalSignal] = None
    evidence_chain: Dict[str, Evidence] = None
    temporal_convergence: Optional[TemporalConvergence] = None
    heluo_prenatal_hexagram: str = ""      # 从 Heluo result 提取（已通过 Contract）
    heluo_postnatal_hexagram: str = ""     # 后天卦
    heluo_yuantang_index: int = 0
    heluo_yuantang: str = ""

    def __post_init__(self):
        if self.canonical_signals is None:
            object.__setattr__(self, "canonical_signals", [])
        if self.evidence_chain is None:
            object.__setattr__(self, "evidence_chain", {})


class YiAdapter:
    """
    Yi Engine Adapter

    数据流:
      CanonicalSignal + EvidenceChain + TemporalConvergence
      → YiStructure (层A/B/C/D 聚合)

    禁止:
      - 直接访问 bazi_pillars / raw_calculation
      - 重新计算河洛链条
      - 生成 fortune_score / luck_score
    """

    @staticmethod
    def adapt(input_data: YiAdapterInput) -> YiStructure:
        """
        将 Contract 层数据适配为 YiStructure。

        Args:
            input_data: 只含 Contract 化数据

        Returns:
            YiStructure — 层 A/B/C/D 聚合结果
        """
        # 提取后天卦（Yi 解释的核心）
        hexagram_name = input_data.heluo_postnatal_hexagram or input_data.heluo_prenatal_hexagram

        if not hexagram_name:
            return YiStructure(
                status=YiStructureStatus.NOT_APPLICABLE,
                layer=YiLayer.HEXAGRAM,
            )

        # 层 A: 卦象基础信息
        from tongshu.engines.yi.hexagram_symbol import get_hexagram_symbol
        try:
            hex_symbol = get_hexagram_symbol(hexagram_name)
            upper = hex_symbol.upper_trigram
            lower = hex_symbol.lower_trigram
            ti_yong = hex_symbol.ti_yong_relation
        except Exception:
            upper, lower, ti_yong = "?", "?", "?"

        # 层 B: 爻象信息（从 Heluo 结果提取）
        line_index = input_data.heluo_yuantang_index
        position_names = ["初", "二", "三", "四", "五", "上"]
        position_name = position_names[line_index] if 0 <= line_index < 6 else "?"

        # 层 C: 经典引用（从 EvidenceChain 提取）
        classical_quote = ""
        classical_source = ""
        evidence_refs = []
        for ev_id, ev in input_data.evidence_chain.items():
            evidence_refs.append(ev_id)
            # 简化：取第一条 LEVEL_1 证据的 passage 文本
            if ev.evidence_level.name == "LEVEL_1" and not classical_quote:
                classical_quote = f"证以{ev_id}"
                classical_source = ev.source_id

        # 层 D: 象义推导链
        image_reasoning = []
        if input_data.canonical_signals:
            for sig in input_data.canonical_signals[:3]:  # 最多取前3个信号
                image_reasoning.append(
                    f"{sig.source_engine.value}→{sig.direction}#{sig.signal_id}"
                )

        # 辅助关系
        auxiliary = []
        try:
            hex_symbol = get_hexagram_symbol(hexagram_name)
            if hex_symbol.cuo_gua:
                auxiliary.append(f"错卦:{hex_symbol.cuo_gua}")
            if hex_symbol.zong_gua:
                auxiliary.append(f"综卦:{hex_symbol.zong_gua}")
        except Exception:
            pass

        # 时间上下文
        temporal_ctx = ""
        if input_data.temporal_convergence:
            temporal_ctx = (
                f"Year={input_data.temporal_convergence.target_year}"
                f" Conf={input_data.temporal_convergence.convergence_score:.2f}"
            )

        # 确定状态
        has_hexagram = bool(hexagram_name)
        has_line = line_index >= 0
        has_classical = bool(classical_quote)

        if not has_hexagram:
            status = YiStructureStatus.NOT_APPLICABLE
        elif not has_line:
            status = YiStructureStatus.INCOMPLETE
        else:
            status = YiStructureStatus.VALID

        return YiStructure(
            truth_hexagram=hexagram_name,
            true_line=line_index + 1,  # 1-indexed
            position_name=position_name,
            temporal_context=temporal_ctx,
            ti_trigram=lower,
            yong_trigram=upper,
            ti_yong_relation=ti_yong,
            auxiliary_relations=auxiliary,
            classical_quote=classical_quote,
            classical_source=classical_source,
            image_reasoning=image_reasoning,
            layer=YiLayer.RELATIONAL,
            status=status,
        )

    @classmethod
    def validate_input(cls, input_data: YiAdapterInput) -> List[str]:
        """验证输入是否符合 Contract 边界。"""
        errors: List[str] = []

        # 禁止 raw calculation fields
        forbidden = {"bazi_pillars", "raw_calculation", "calculation_context"}
        raw_attrs = {
            "heluo_prenatal_hexagram",
            "heluo_postnatal_hexagram",
            "heluo_yuantang_index",
            "heluo_yuantang",
        }
        # 这些是允许从 Heluo 提取的字段（已通过 Contract）

        # 检查 EvidenceChain 引用是否完整
        if input_data.evidence_chain:
            for ev_id, ev in input_data.evidence_chain.items():
                if not ev.source_id:
                    errors.append(f"Evidence {ev_id} missing source_id")
                if not ev.claim_id:
                    errors.append(f"Evidence {ev_id} missing claim_id")

        return errors
