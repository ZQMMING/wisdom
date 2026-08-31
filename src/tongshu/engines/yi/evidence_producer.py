"""
P1.2-A — YiEvidenceProducer（易经证据生产者）

职责：
  - 从 hexagram/yao 结果提取纯事实
  - 输出 list[EngineEvidence]
  - 不产生 direction/polarity/strength/confidence

V13 §五硬约束：EngineEvidence 只保留事实/数值/结构/位置/时间
"""
from __future__ import annotations

import uuid
from typing import Any, List, Optional

from ..spec.canonical import EngineEvidence, EngineName, TemporalScope


class YiEvidenceProducer:
    """易经证据生产者。

    从 Hexagram/Yao 结果提取纯事实证据，输出 EngineEvidence 列表。
    """

    RULE_PREFIX = "YI"
    CALC_VERSION = "2026.09"
    CONTRACT_VERSION = "v13.0"

    def produce(
        self,
        hexagram_result: dict,
        yao_result: Optional[dict] = None,
        birth_year: Optional[int] = None,
    ) -> List[EngineEvidence]:
        """从易经结果提取纯事实证据。

        Args:
            hexagram_result: 卦象结果字典（包含卦名、上下卦等）
            yao_result: 爻辞结果字典（包含爻位、爻辞等，可选）
            birth_year: 出生年份（可选）

        Returns:
            list[EngineEvidence]
        """
        evidences: List[EngineEvidence] = []

        # 1. 卦名事实
        gua_name = hexagram_result.get("name", "")
        if gua_name:
            evidences.append(
                EngineEvidence(
                    evidence_id=f"{self.RULE_PREFIX}-GUA-{uuid.uuid4().hex[:8]}",
                    engine=EngineName.YI_JING,
                    rule_id=f"{self.RULE_PREFIX}_HEXAGRAM_NAME",
                    value=gua_name,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={
                        "hexagram_name": gua_name,
                        "hexagram_number": hexagram_result.get("number", 0),
                        "upper_trigram": hexagram_result.get("upper_trigram", ""),
                        "lower_trigram": hexagram_result.get("lower_trigram", ""),
                    },
                    source_rule_ref="rules/yi_hexagrams.json",
                    source_field="hexagram_name",
                    calculation_version=self.CALC_VERSION,
                    contract_version=self.CONTRACT_VERSION,
                )
            )

        # 2. 卦辞事实
        gua_ci = hexagram_result.get("gua_ci", "")
        if gua_ci:
            evidences.append(
                EngineEvidence(
                    evidence_id=f"{self.RULE_PREFIX}-GUA-CI-{uuid.uuid4().hex[:8]}",
                    engine=EngineName.YI_JING,
                    rule_id=f"{self.RULE_PREFIX}_GUA_CI",
                    value=gua_ci,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={
                        "text": gua_ci,
                        "source": hexagram_result.get("gua_ci_source", ""),
                    },
                    source_rule_ref="rules/yi_gua_ci.json",
                    source_field="gua_ci",
                    calculation_version=self.CALC_VERSION,
                    contract_version=self.CONTRACT_VERSION,
                )
            )

        # 3. 爻位事实（如有）
        if yao_result:
            yao_position = yao_result.get("position", "")
            yao_text = yao_result.get("text", "")
            if yao_position:
                evidences.append(
                    EngineEvidence(
                        evidence_id=f"{self.RULE_PREFIX}-YAO-{yao_position}-{uuid.uuid4().hex[:6]}",
                        engine=EngineName.YI_JING,
                        rule_id=f"{self.RULE_PREFIX}_YAO_POSITION",
                        value=yao_position,
                        temporal_scope=TemporalScope.BIRTH,
                        attributes={
                            "yao_position": yao_position,
                            "yao_text": yao_text,
                            "yao_nature": yao_result.get("nature", ""),
                        },
                        source_rule_ref="rules/yi_yao.json",
                        source_field="yao_position",
                        calculation_version=self.CALC_VERSION,
                        contract_version=self.CONTRACT_VERSION,
                    )
                )

            # 爻辞事实
            if yao_text:
                evidences.append(
                    EngineEvidence(
                        evidence_id=f"{self.RULE_PREFIX}-YAO-CI-{yao_position}-{uuid.uuid4().hex[:6]}",
                        engine=EngineName.YI_JING,
                        rule_id=f"{self.RULE_PREFIX}_YAO_TEXT",
                        value=yao_text,
                        temporal_scope=TemporalScope.BIRTH,
                        attributes={
                            "yao_position": yao_position,
                            "text": yao_text,
                            "source": yao_result.get("source", ""),
                        },
                        source_rule_ref="rules/yi_yao_ci.json",
                        source_field="yao_text",
                        calculation_version=self.CALC_VERSION,
                        contract_version=self.CONTRACT_VERSION,
                    )
                )

        return evidences
