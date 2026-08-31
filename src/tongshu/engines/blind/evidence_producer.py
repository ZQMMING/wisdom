"""
P1.2-A — BlindEvidenceProducer（盲派八字证据生产者）

职责：
  - 从 blind_bazi_engine 输出提取纯事实
  - 输出 list[EngineEvidence]
  - 不产生 direction/polarity/strength/confidence

V13 §五硬约束：EngineEvidence 只保留事实/数值/结构/位置/时间
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from ..spec.canonical import EngineEvidence, EngineName, TemporalScope
from ..engines.blind_bazi_engine import BlindBaziResult


class BlindEvidenceProducer:
    """盲派八字证据生产者。

    从 BlindBaziResult 提取纯事实证据，输出 EngineEvidence 列表。
    """

    RULE_PREFIX = "BL"
    CALC_VERSION = "2026.09"
    CONTRACT_VERSION = "v13.0"

    def produce(
        self,
        result: BlindBaziResult,
        birth_year: Optional[int] = None,
    ) -> List[EngineEvidence]:
        """从 BlindBaziResult 提取纯事实证据。

        Args:
            result: BlindBaziResult 对象
            birth_year: 出生年份（可选）

        Returns:
            list[EngineEvidence]
        """
        evidences: List[EngineEvidence] = []

        # 1. 宾主判定（纯结构事实）
        evidences.append(
            EngineEvidence(
                evidence_id=f"{self.RULE_PREFIX}-MAIN-{uuid.uuid4().hex[:8]}",
                engine=EngineName.BLIND_SCHOOL,
                rule_id=f"{self.RULE_PREFIX}_MAIN_BRANCHES",
                value=list(result.main_branches),
                temporal_scope=TemporalScope.BIRTH,
                attributes={
                    "main_branches": list(result.main_branches),
                    "guest_branches": list(result.guest_branches),
                },
                source_rule_ref="rules/blind_main_guest.json",
                source_field="main_branches",
                calculation_version=self.CALC_VERSION,
                contract_version=self.CONTRACT_VERSION,
            )
        )

        # 2. 体用分析（纯结构事实）
        evidences.append(
            EngineEvidence(
                evidence_id=f"{self.RULE_PREFIX}-TI-{uuid.uuid4().hex[:8]}",
                engine=EngineName.BLIND_SCHOOL,
                rule_id=f"{self.RULE_PREFIX}_TI_YONG",
                value={
                    "ti_branches": list(result.ti_branches),
                    "yong_branches": list(result.yong_branches),
                    "ti_stems": result.ti_stems,
                    "yong_stems": result.yong_stems,
                },
                temporal_scope=TemporalScope.BIRTH,
                attributes={
                    "ti_branches": list(result.ti_branches),
                    "yong_branches": list(result.yong_branches),
                },
                source_rule_ref="rules/blind_ti_yong.json",
                source_field="ti_yong",
                calculation_version=self.CALC_VERSION,
                contract_version=self.CONTRACT_VERSION,
            )
        )

        # 3. 做功结构事实
        evidences.append(
            EngineEvidence(
                evidence_id=f"{self.RULE_PREFIX}-ZG-{uuid.uuid4().hex[:8]}",
                engine=EngineName.BLIND_SCHOOL,
                rule_id=f"{self.RULE_PREFIX}_ZUO_GONG",
                value=result.zuo_gong_type if result.zuo_gong else "",
                temporal_scope=TemporalScope.BIRTH,
                attributes={
                    "zuo_gong": result.zuo_gong,
                    "zuo_gong_type": result.zuo_gong_type,
                    "zuo_gong_methods": result.zuo_gong_methods,
                    "zuo_gong_strength": result.zuo_gong_strength,
                },
                source_rule_ref="rules/blind_zuogong.json",
                source_field="zuo_gong",
                calculation_version=self.CALC_VERSION,
                contract_version=self.CONTRACT_VERSION,
            )
        )

        # 4. 透干十神事实
        if result.transparent_ten_gods:
            evidences.append(
                EngineEvidence(
                    evidence_id=f"{self.RULE_PREFIX}-TGTG-{uuid.uuid4().hex[:8]}",
                    engine=EngineName.BLIND_SCHOOL,
                    rule_id=f"{self.RULE_PREFIX}_TRANSPARENT_TEN_GODS",
                    value=result.transparent_ten_gods,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={"transparent_ten_gods": result.transparent_ten_gods},
                    source_rule_ref="rules/blind_ten_gods.json",
                    source_field="transparent_ten_gods",
                    calculation_version=self.CALC_VERSION,
                    contract_version=self.CONTRACT_VERSION,
                )
            )

        return evidences
