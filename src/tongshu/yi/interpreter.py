"""
Phase 6 — Yi Interpretation Engine

职责:
  基于 YiStructure 生成关系式解释 (STATE → OPPORTUNITY/RISK/REMEDIATION/ACTION)
  严禁生成 fortune_score / luck_score

边界:
  - 输入必须是 YiStructure（已由 YiAdapter 从 Contract 数据适配）
  - 输出必须是 YiInterpretation（关系式结构）
  - 不参与计算，不参与验证
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import List, Optional

from tongshu.yi.schema import (
    YiStructure,
    YiInterpretation,
    DirectionLabel,
    YiStructureStatus,
)


# ─── 禁止术语表（用于 INTERPRETATION Dimension 校验）──────────────────────────

FORBIDDEN_TERMS = frozenset({
    "大凶", "凶兆", "化解", "必败", "定数", "宿命",
    "改运", "转运", "趋吉避凶", "命理", "风水",
    "五行缺", "冲煞", "刑克", "犯太岁",
})


class YiInterpretationEngine:
    """
    Yi 关系解释引擎

    输入: YiStructure (层 A/B/C/D 聚合结果)
    输出: YiInterpretation (关系式结构)

    约束:
      1. 不生成 fortune_score / luck_score
      2. 不修改输入 YiStructure
      3. 解释必须引用具体来源
      4. 状态描述基于体用关系
    """

    def interpret(self, structure: YiStructure) -> YiInterpretation:
        """
        基于 YiStructure 生成关系式解释。

        Args:
            structure: Yi 结构（来自 YiAdapter）

        Returns:
            YiInterpretation — 关系式解释输出
        """
        if structure.status == YiStructureStatus.NOT_APPLICABLE:
            return YiInterpretation(
                interpretation_id=str(uuid.uuid4()),
                yi_structure_ref="",
                state="当前 case 不适用 Yi 解释",
                directional_label=DirectionLabel.UNCERTAIN,
                phase=6,
            )

        if structure.status == YiStructureStatus.INCOMPLETE:
            return YiInterpretation(
                interpretation_id=str(uuid.uuid4()),
                yi_structure_ref=f"{structure.truth_hexagram}#{structure.true_line}",
                state=f"Yi 结构不完整（{structure.truth_hexagram}），需补充爻象或经典依据",
                directional_label=DirectionLabel.UNCERTAIN,
                phase=6,
            )

        # 基于体用关系确定方向
        directional_label = self._derive_direction(structure.ti_yong_relation)

        # 生成关系式解释
        state = self._generate_state(structure)
        opportunity = self._generate_opportunity(structure)
        risk = self._generate_risk(structure)
        remediation = self._generate_remediation(structure)
        action = self._generate_action(structure)

        # 构建来源引用
        source_refs = [
            f"周易·{structure.truth_hexagram}",
            structure.classical_source or "周易·卦辞",
        ]
        if structure.auxiliary_relations:
            source_refs.extend(structure.auxiliary_relations)

        return YiInterpretation(
            interpretation_id=str(uuid.uuid4()),
            yi_structure_ref=f"{structure.truth_hexagram}#{structure.true_line}",
            state=state,
            opportunity=opportunity,
            risk=risk,
            remediation=remediation,
            action=action,
            directional_label=directional_label,
            source_refs=source_refs,
            evidence_refs=[],
            confidence=self._compute_confidence(structure),
            phase=6,
        )

    def _derive_direction(self, ti_yong_relation: str) -> DirectionLabel:
        """基于体用关系推导方向标签。"""
        if "用生体" in ti_yong_relation:
            return DirectionLabel.POSITIVE
        elif "用克体" in ti_yong_relation:
            return DirectionLabel.NEGATIVE
        elif "体生用" in ti_yong_relation or "体克用" in ti_yong_relation:
            return DirectionLabel.CHANGE
        elif "比和" in ti_yong_relation:
            return DirectionLabel.NEUTRAL
        return DirectionLabel.UNCERTAIN

    def _generate_state(self, s: YiStructure) -> str:
        """生成当前状态描述。"""
        parts = [f"{s.truth_hexagram}卦"]
        if s.ti_trigram and s.yong_trigram:
            parts.append(f"体{s.ti_trigram}用{s.yong_trigram}")
        if s.ti_yong_relation:
            parts.append(s.ti_yong_relation)
        if s.true_line and s.position_name:
            parts.append(f"元堂{s.position_name}")
        return "，".join(parts) + "。"

    def _generate_opportunity(self, s: YiStructure) -> str:
        """生成机会/有利面向。"""
        if "用生体" in s.ti_yong_relation:
            return f"{s.truth_hexagram}卦，外部环境生助体卦，当前态势有利于顺势而为。"
        elif "比和" in s.ti_yong_relation:
            return f"{s.truth_hexagram}卦，体用比和，内外一致，可稳中求进。"
        return f"{s.truth_hexagram}卦，需结合具体人生领域评估有利面向。"

    def _generate_risk(self, s: YiStructure) -> str:
        """生成风险/不利面向。"""
        if "用克体" in s.ti_yong_relation:
            return f"{s.truth_hexagram}卦，外部克制体卦，需谨慎应对变化。"
        elif "体生用" in s.ti_yong_relation:
            return f"{s.truth_hexagram}卦，体泄于用，注意精力分配，避免过度消耗。"
        return f"{s.truth_hexagram}卦，需留意变化中的不确定因素。"

    def _generate_remediation(self, s: YiStructure) -> str:
        """生成化解/应对建议。"""
        if "用克体" in s.ti_yong_relation:
            return "关注外部环境变化，以静制动，等待时机。"
        elif "体生用" in s.ti_yong_relation:
            return "合理分配资源，避免单方面付出过度。"
        return "保持观察，根据实际发展调整策略。"

    def _generate_action(self, s: YiStructure) -> str:
        """生成行动建议。"""
        if s.true_line and s.position_name:
            return f"参考{s.truth_hexagram}卦{s.position_name}爻辞，结合当前情境判断。"
        return "建议咨询专业易学顾问，获取针对性指导。"

    def _compute_confidence(self, s: YiStructure) -> float:
        """
        计算解释置信度（仅用于记录，不参与决策）。

        基于:
          - 经典引用完整性
          - 象义推导链长度
          - 结构完整性
        """
        base = 0.5
        if s.classical_quote:
            base += 0.15
        if s.image_reasoning:
            base += min(0.1 * len(s.image_reasoning), 0.15)
        if s.status == YiStructureStatus.VALID:
            base += 0.1
        return round(min(base, 0.95), 2)

    def check_forbidden_terms(self, interpretation: YiInterpretation) -> List[str]:
        """检查解释中是否包含禁止术语。"""
        text = " ".join([
            interpretation.state,
            interpretation.opportunity,
            interpretation.risk,
            interpretation.remediation,
            interpretation.action,
        ])
        found = []
        for term in FORBIDDEN_TERMS:
            if term in text:
                found.append(term)
        return found
