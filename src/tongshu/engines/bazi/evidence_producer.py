"""
P1.2-A — ZiPingEvidenceProducer（子平八字证据生产者）

职责：
  - 从 BaziChart（四柱）提取纯事实
  - 输出 list[EngineEvidence]
  - 不产生 direction/polarity/strength/confidence

V13 §五硬约束：EngineEvidence 只保留事实/数值/结构/位置/时间
"""
from __future__ import annotations

import uuid
from typing import Any, List, Optional

from ...spec.canonical import EngineEvidence, EngineName, TemporalScope
from ..bazi_engine import BaziChart


class BaziEvidenceProducer:
    """子平八字证据生产者。

    从 BaziChart 提取纯事实证据，输出 EngineEvidence 列表。
    """

    RULE_PREFIX = "ZP"
    CALC_VERSION = "2026.09"
    CONTRACT_VERSION = "v13.0"

    def produce(
        self,
        chart: BaziChart,
        birth_year: Optional[int] = None,
    ) -> List[EngineEvidence]:
        """从 BaziChart 提取纯事实证据。

        Args:
            chart: BaziChart 对象（四柱 + 衍生字段）
            birth_year: 出生年份（用于流年证据，可选）

        Returns:
            list[EngineEvidence]，每条为纯事实，无方向/极性/强度
        """
        evidences: List[EngineEvidence] = []

        # 1. 四柱天干地支（本命层）
        pillars = [
            ("year", chart.year_pillar, TemporalScope.BIRTH),
            ("month", chart.month_pillar, TemporalScope.BIRTH),
            ("day", chart.day_pillar, TemporalScope.BIRTH),
            ("hour", chart.hour_pillar, TemporalScope.BIRTH),
        ]

        for pillar_name, pillar, scope in pillars:
            # 天干事实
            evidences.append(
                EngineEvidence(
                    evidence_id=f"{self.RULE_PREFIX}-STEM-{pillar_name}-{uuid.uuid4().hex[:8]}",
                    engine=EngineName.ZI_PING,
                    rule_id=f"{self.RULE_PREFIX}_STEM_{pillar_name.upper()}",
                    value=pillar.heavenly_stem,
                    temporal_scope=scope,
                    attributes={
                        "stem": pillar.heavenly_stem,
                        "element": pillar.stem_element,
                        "pillar": pillar_name,
                    },
                    source_rule_ref="rules/bazi_stems.json",
                    source_field="heavenly_stem",
                    calculation_version=self.CALC_VERSION,
                    contract_version=self.CONTRACT_VERSION,
                )
            )

            # 地支事实
            evidences.append(
                EngineEvidence(
                    evidence_id=f"{self.RULE_PREFIX}-BRANCH-{pillar_name}-{uuid.uuid4().hex[:8]}",
                    engine=EngineName.ZI_PING,
                    rule_id=f"{self.RULE_PREFIX}_BRANCH_{pillar_name.upper()}",
                    value=pillar.earthly_branch,
                    temporal_scope=scope,
                    attributes={
                        "branch": pillar.earthly_branch,
                        "element": pillar.branch_element,
                        "pillar": pillar_name,
                    },
                    source_rule_ref="rules/bazi_branches.json",
                    source_field="earthly_branch",
                    calculation_version=self.CALC_VERSION,
                    contract_version=self.CONTRACT_VERSION,
                )
            )

        # 2. 十神事实（透干十神）
        from ...reasoning.bazi_ten_gods import ten_god
        day_master = chart.day_master
        stem_positions = {
            "year": chart.year_pillar.heavenly_stem,
            "month": chart.month_pillar.heavenly_stem,
            "day": day_master,
            "hour": chart.hour_pillar.heavenly_stem,
        }
        for pos, stem in stem_positions.items():
            tg = ten_god(day_master, stem)
            evidences.append(
                EngineEvidence(
                    evidence_id=f"{self.RULE_PREFIX}-TG-{pos}-{uuid.uuid4().hex[:8]}",
                    engine=EngineName.ZI_PING,
                    rule_id=f"{self.RULE_PREFIX}_TEN_GOD_{pos.upper()}",
                    value=tg,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={
                        "ten_god": tg,
                        "stem": stem,
                        "day_master": day_master,
                        "pillar": pos,
                    },
                    source_rule_ref="rules/bazi_ten_gods.json",
                    source_field="ten_god",
                    calculation_version=self.CALC_VERSION,
                    contract_version=self.CONTRACT_VERSION,
                )
            )

        # 3. 地支关系事实（冲/合/刑/害）
        if chart.branch_clash_map:
            for key, vals in chart.branch_clash_map.items():
                evidences.append(
                    EngineEvidence(
                        evidence_id=f"{self.RULE_PREFIX}-CLASH-{key.replace('-', '_')}-{uuid.uuid4().hex[:6]}",
                        engine=EngineName.ZI_PING,
                        rule_id=f"{self.RULE_PREFIX}_BRANCH_CLASH",
                        value=key,
                        temporal_scope=TemporalScope.BIRTH,
                        attributes={"branches": vals, "type": "clash"},
                        source_rule_ref="rules/bazi_branch_relations.json",
                        source_field="branch_clash_map",
                        calculation_version=self.CALC_VERSION,
                        contract_version=self.CONTRACT_VERSION,
                    )
                )

        # 4. 桃花事实
        if chart.peach_blossom:
            evidences.append(
                EngineEvidence(
                    evidence_id=f"{self.RULE_PREFIX}-PEACH-{uuid.uuid4().hex[:8]}",
                    engine=EngineName.ZI_PING,
                    rule_id=f"{self.RULE_PREFIX}_PEACH_BLOSSOM",
                    value=chart.day_pillar.earthly_branch,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={
                        "day_branch": chart.day_pillar.earthly_branch,
                        "peach_blossom": True,
                    },
                    source_rule_ref="rules/bazi_peach_blossom.json",
                    source_field="peach_blossom",
                    calculation_version=self.CALC_VERSION,
                    contract_version=self.CONTRACT_VERSION,
                )
            )

        # 5. 五行失衡事实
        if chart.five_element_imbalance:
            evidences.append(
                EngineEvidence(
                    evidence_id=f"{self.RULE_PREFIX}-FE_IMBAL-{uuid.uuid4().hex[:8]}",
                    engine=EngineName.ZI_PING,
                    rule_id=f"{self.RULE_PREFIX}_FIVE_ELEMENT_IMBALANCE",
                    value=chart.five_element_balance,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={"balance": chart.five_element_balance},
                    source_rule_ref="rules/bazi_five_elements.json",
                    source_field="five_element_imbalance",
                    calculation_version=self.CALC_VERSION,
                    contract_version=self.CONTRACT_VERSION,
                )
            )

        return evidences
