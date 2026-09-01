"""
P1.2-A: ZiweiEvidenceProducer（紫微斗数证据生产者）

职责:
  - 从 ziwei_engine 输出提取纯事实证据
  - 输出 list[dict] (EngineEvidence-like)
  - 不产生 direction/polarity/strength/confidence
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional


class EngineEvidence:
    """紫微斗数证据数据类（轻量版，不依赖 wisdom spec 模块）。"""
    __slots__ = (
        "evidence_id", "engine", "rule_id", "value", "temporal_scope",
        "attributes", "source_rule_ref", "source_field",
        "calculation_version", "contract_version",
    )

    def __init__(
        self,
        evidence_id: str,
        engine: str,
        rule_id: str,
        value: Any,
        temporal_scope: str,
        attributes: Optional[Dict[str, Any]] = None,
        source_rule_ref: str = "",
        source_field: str = "",
        calculation_version: str = "",
        contract_version: str = "",
    ) -> None:
        self.evidence_id = evidence_id
        self.engine = engine
        self.rule_id = rule_id
        self.value = value
        self.temporal_scope = temporal_scope
        self.attributes = attributes or {}
        self.source_rule_ref = source_rule_ref
        self.source_field = source_field
        self.calculation_version = calculation_version
        self.contract_version = contract_version

    def to_dict(self) -> dict:
        return {
            "evidence_id": self.evidence_id,
            "engine": self.engine,
            "rule_id": self.rule_id,
            "value": self.value,
            "temporal_scope": self.temporal_scope,
            "attributes": self.attributes,
            "source_rule_ref": self.source_rule_ref,
            "source_field": self.source_field,
            "calculation_version": self.calculation_version,
            "contract_version": self.contract_version,
        }


EngineName = type("EngineName", (), {"ZI_WEI": "ZI_WEI"})
TemporalScope = type("TemporalScope", (), {"BIRTH": "BIRTH"})


class ZiweiEvidenceProducer:
    """紫微斗数证据生产者。
    从 ZiweiChart 提取纯事实证据，输出 EngineEvidence 列表。
    """

    RULE_PREFIX = "ZW"
    CALC_VERSION = "2026.09"
    CONTRACT_VERSION = "v13.0"

    def produce(
        self,
        chart,
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
                    source_rule_ref="data/rules/ziwei_stars.json",
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
                    source_rule_ref="data/rules/ziwei_sihua.json",
                    source_field="soul_palace_sihua",
                    calculation_version=self.CALC_VERSION,
                    contract_version=self.CONTRACT_VERSION,
                )
            )

        # 3. 各宫位主星事实
        palace_data = getattr(chart, "palace_data", {}) or {}
        for palace_name, palace_info in palace_data.items():
            if not isinstance(palace_info, dict):
                continue
            stars = palace_info.get("stars", [])
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
                            "is_main": palace_info.get("is_main_star", False),
                        },
                        source_rule_ref="data/rules/ziwei_palaces.json",
                        source_field="palace_stars",
                        calculation_version=self.CALC_VERSION,
                        contract_version=self.CONTRACT_VERSION,
                    )
                )

            # 宫位四化事实
            pal_sihua = palace_info.get("sihua", [])
            for sihua in pal_sihua:
                evidences.append(
                    EngineEvidence(
                        evidence_id=f"{self.RULE_PREFIX}-PALACE-SIHUA-{palace_name}-{sihua}-{uuid.uuid4().hex[:6]}",
                        engine=EngineName.ZI_WEI,
                        rule_id=f"{self.RULE_PREFIX}_PALACE_SIHUA",
                        value=sihua,
                        temporal_scope=TemporalScope.BIRTH,
                        attributes={
                            "sihua": sihua,
                            "palace": palace_name,
                            "type": "palace",
                        },
                        source_rule_ref="data/rules/ziwei_sihua.json",
                        source_field="palace_sihua",
                        calculation_version=self.CALC_VERSION,
                        contract_version=self.CONTRACT_VERSION,
                    )
                )

        return evidences
