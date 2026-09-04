"""
P1.2-A — ZiweiEvidenceProducer（紫微斗数证据生产者）

职责：
  - 从 ziwei_engine 输出提取纯事实
  - 输出 list[EngineEvidence]
  - 不产生 direction/polarity/strength/confidence

V13 §五硬约束：EngineEvidence 只保留事实/数值/结构/位置/时间
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from ...spec.canonical import EngineEvidence, EngineName, TemporalScope
from ..ziwei_engine import ZiweiChart


class ZiweiEvidenceProducer:
    """紫微斗数证据生产者。

    从 ZiweiChart 提取纯事实证据，输出 EngineEvidence 列表。
    """

    RULE_PREFIX = "ZW"
    CALC_VERSION = "2026.09"
    CONTRACT_VERSION = "v13.0"

    def produce(
        self,
        chart: ZiweiChart,
        birth_year: Optional[int] = None,
    ) -> List[EngineEvidence]:
        """从 ZiweiChart 提取纯事实证据。

        Args:
            chart: ZiweiChart 对象
            birth_year: 出生年份（可选）

        Returns:
            list[EngineEvidence]
        """
        evidences: List[EngineEvidence] = []

        # 1. 命宫主星事实
        for idx, star in enumerate(chart.soul_palace_main_stars):
            evidences.append(
                EngineEvidence(
                    evidence_id=f"{self.RULE_PREFIX}-STAR-{star}-{uuid.uuid4().hex[:6]}",
                    engine=EngineName.ZI_WEI,
                    rule_id=f"{self.RULE_PREFIX}_MAIN_STAR_{star.upper()}",
                    value=star,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={
                        "star": star,
                        "palace": "命宫",
                        "position": "soul",
                        "star_index": idx,
                    },
                    source_rule_ref="data/rules_index/ziwei_stars.json",
                    source_field="soul_palace_main_stars",
                    calculation_version=self.CALC_VERSION,
                    contract_version=self.CONTRACT_VERSION,
                )
            )

        # 2. 命宫四化事实
        for sihua in chart.soul_palace_sihua:
            evidences.append(
                EngineEvidence(
                    evidence_id=f"{self.RULE_PREFIX}-SIHUA-{sihua}-{uuid.uuid4().hex[:6]}",
                    engine=EngineName.ZI_WEI,
                    rule_id=f"{self.RULE_PREFIX}_SIHUA_{sihua}",
                    value=sihua,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={
                        "sihua": sihua,
                        "palace": "命宫",
                        "type": "natal",
                    },
                    source_rule_ref="data/rules_index/ziwei_stars.json",
                    source_field="soul_palace_sihua",
                    calculation_version=self.CALC_VERSION,
                    contract_version=self.CONTRACT_VERSION,
                )
            )

        # 3. 各宫位主星事实（消费 ZiweiChart.palaces 字典，key=宫名，value={"major":[], "minor":[], ...}）
        for palace_name, palace_info in chart.palaces.items():
            if not isinstance(palace_info, dict):
                continue
            stars = palace_info.get("major", [])
            for star in stars:
                evidences.append(
                    EngineEvidence(
                        evidence_id=f"{self.RULE_PREFIX}-PALACE-{palace_name}-{star}-{uuid.uuid4().hex[:6]}",
                        engine=EngineName.ZI_WEI,
                        rule_id=f"{self.RULE_PREFIX}_PALACE_STAR",
                        value=star,
                        temporal_scope=TemporalScope.BIRTH,
                        attributes={
                            "star": star,
                            "palace": palace_name,
                        },
                        source_rule_ref="data/rules_index/ziwei_stars.json",
                        source_field="palace_stars",
                        calculation_version=self.CALC_VERSION,
                        contract_version=self.CONTRACT_VERSION,
                    )
                )

            # 宫位四化事实（注：当前 ZiweiChart.palaces 不含 sihua，此项暂跳过，待 MethodProfile 接入）

        return evidences
