"""
P0-② CanonicalStateProducer — 从 BaziChart 生产 CanonicalState

【职责】将算层（BaziChart）的计算结果转换为 CanonicalState 中间状态容器
【原则】只做数据转换，不做辨证判断；所有 facts/relations 都是纯事实，不含价值判断
【迁移方向】health_signals.py / annual_event_evaluator.py 等从直接调用 strength_engine 改为消费 CanonicalState

数据转换链：
  BaziChart（算层输出）
      ↓
  Facts（L1原始事实：天干/地支/藏干/十神/五行/阴阳/十二长生）
      ↓
  Relations（L1关系：生/克/同/通根/刑冲合害）
      ↓
  CanonicalState（中间状态容器）
      ↓
  辨证层消费（五部经典各自 Primitive/Evidence/State）
"""

from __future__ import annotations

from typing import Optional

from tongshu.canonical.state import (
    CanonicalState,
    Fact,
    Relation,
    FactType,
    RelationType,
)
from tongshu.engines.bazi_engine import BaziChart, STEM_ELEMENT, STEM_POLARITY
from tongshu.reasoning.bazi_ten_gods import BRANCH_HIDDEN_STEMS, ten_god


class CanonicalStateProducer:
    """从 BaziChart 生产 CanonicalState。

    用法：
        producer = CanonicalStateProducer()
        state = producer.produce(chart)
    """

    def __init__(self):
        self._fact_counter = 0
        self._relation_counter = 0

    def _next_fact_id(self) -> str:
        self._fact_counter += 1
        return f"F-{self._fact_counter:04d}"

    def _next_relation_id(self) -> str:
        self._relation_counter += 1
        return f"R-{self._relation_counter:04d}"

    def produce(self, chart: BaziChart, state_id: Optional[str] = None) -> CanonicalState:
        """从 BaziChart 生产完整的 CanonicalState。

        Args:
            chart: BaziChart 算层输出
            state_id: 可选的状态ID，默认自动生成

        Returns:
            CanonicalState 包含 facts 和 relations 的中间状态容器
        """
        if state_id is None:
            state_id = f"CS-{chart.day_master}-{self._fact_counter:04d}"

        facts: list[Fact] = []
        relations: list[Relation] = []

        # 1. 四柱 facts
        facts.extend(self._produce_pillar_facts(chart))

        # 2. 藏干 facts
        facts.extend(self._produce_hidden_stem_facts(chart))

        # 3. 五行阴阳 facts
        facts.extend(self._produce_wuxing_yinyang_facts(chart))

        # 4. 十神 facts
        facts.extend(self._produce_ten_god_facts(chart))

        # 5. 通根 relations
        relations.extend(self._produce_gen_relations(chart, facts))

        # 6. 生克 relations
        relations.extend(self._produce_sheng_ke_relations(chart, facts))

        # 7. 刑冲合害 relations
        relations.extend(self._produce_xing_chong_he_hai_relations(chart))

        return CanonicalState(
            state_id=state_id,
            chart_id=f"CHART-{chart.day_master}",
            facts=facts,
            relations=relations,
            metadata={
                "producer": "CanonicalStateProducer",
                "day_master": chart.day_master,
                "gender": chart.gender,
                "facts_count": len(facts),
                "relations_count": len(relations),
            },
        )

    # ============================================================
    # Facts 生产
    # ============================================================

    def _produce_pillar_facts(self, chart: BaziChart) -> list[Fact]:
        """生产四柱天干地支 facts。"""
        facts = []
        pillars = [
            ("year", chart.year_pillar),
            ("month", chart.month_pillar),
            ("day", chart.day_pillar),
            ("hour", chart.hour_pillar),
        ]
        for position, pillar in pillars:
            # 天干 fact
            facts.append(Fact(
                fact_id=self._next_fact_id(),
                fact_type=FactType.HEAVENLY_STEM,
                subject=pillar.heavenly_stem,
                value=pillar.heavenly_stem,
                position=position,
                source="bazi_engine.pillar",
            ))
            # 地支 fact
            facts.append(Fact(
                fact_id=self._next_fact_id(),
                fact_type=FactType.EARTHLY_BRANCH,
                subject=pillar.earthly_branch,
                value=pillar.earthly_branch,
                position=position,
                source="bazi_engine.pillar",
            ))
        return facts

    def _produce_hidden_stem_facts(self, chart: BaziChart) -> list[Fact]:
        """生产藏干 facts。"""
        facts = []
        pillars = [
            ("year", chart.year_pillar.earthly_branch),
            ("month", chart.month_pillar.earthly_branch),
            ("day", chart.day_pillar.earthly_branch),
            ("hour", chart.hour_pillar.earthly_branch),
        ]
        for position, branch in pillars:
            hidden_stems = BRANCH_HIDDEN_STEMS.get(branch, [])
            for layer_idx, stem in enumerate(hidden_stems):
                layer = ["本气", "中气", "余气"][layer_idx] if layer_idx < 3 else f"第{layer_idx+1}层"
                facts.append(Fact(
                    fact_id=self._next_fact_id(),
                    fact_type=FactType.HIDDEN_STEM,
                    subject=branch,
                    value=stem,
                    position=position,
                    source="bazi_ten_gods.BRANCH_HIDDEN_STEMS",
                    metadata={"layer": layer, "layer_index": layer_idx},
                ))
        return facts

    def _produce_wuxing_yinyang_facts(self, chart: BaziChart) -> list[Fact]:
        """生产五行阴阳 facts。"""
        facts = []
        all_stems = [
            chart.year_pillar.heavenly_stem,
            chart.month_pillar.heavenly_stem,
            chart.day_pillar.heavenly_stem,
            chart.hour_pillar.heavenly_stem,
        ]
        for stem in all_stems:
            # 五行 fact
            facts.append(Fact(
                fact_id=self._next_fact_id(),
                fact_type=FactType.WUXING,
                subject=stem,
                value=STEM_ELEMENT.get(stem, "unknown"),
                source="bazi_engine.STEM_ELEMENT",
            ))
            # 阴阳 fact
            facts.append(Fact(
                fact_id=self._next_fact_id(),
                fact_type=FactType.YINYANG,
                subject=stem,
                value=STEM_POLARITY.get(stem, "unknown"),
                source="bazi_engine.STEM_POLARITY",
            ))
        return facts

    def _produce_ten_god_facts(self, chart: BaziChart) -> list[Fact]:
        """生产十神 facts。"""
        facts = []
        dm = chart.day_master
        positions = ["year", "month", "day", "hour"]
        stems = [
            chart.year_pillar.heavenly_stem,
            chart.month_pillar.heavenly_stem,
            chart.day_pillar.heavenly_stem,
            chart.hour_pillar.heavenly_stem,
        ]
        for pos, stem in zip(positions, stems):
            if stem == dm:
                tg = "日主"
            else:
                tg = ten_god(dm, stem)
            facts.append(Fact(
                fact_id=self._next_fact_id(),
                fact_type=FactType.TEN_GOD,
                subject=stem,
                value=tg,
                position=pos,
                source="bazi_ten_gods.ten_god",
                metadata={"day_master": dm},
            ))
        return facts

    # ============================================================
    # Relations 生产
    # ============================================================

    def _produce_gen_relations(self, chart: BaziChart, facts: list[Fact]) -> list[Relation]:
        """生产通根 relations（藏干与天干同干）。"""
        relations = []
        dm = chart.day_master

        # 找出所有天干 facts
        stem_facts = [f for f in facts if f.fact_type == FactType.HEAVENLY_STEM]
        hidden_stem_facts = [f for f in facts if f.fact_type == FactType.HIDDEN_STEM]

        for sf in stem_facts:
            for hsf in hidden_stem_facts:
                if sf.value == hsf.value:
                    # 同干 = 通根
                    relations.append(Relation(
                        relation_id=self._next_relation_id(),
                        relation_type=RelationType.GEN,
                        subject=f"{hsf.position}支{hsf.subject}中{hsf.value}",
                        object=sf.value,
                        relation=f"{hsf.value}通根（{hsf.position}支{hsf.subject}藏{hsf.value}）",
                        position=hsf.position,
                        source_facts=[sf.fact_id, hsf.fact_id],
                        metadata={"root_type": hsf.metadata.get("layer", "unknown")},
                    ))
        return relations

    def _produce_sheng_ke_relations(self, chart: BaziChart, facts: list[Fact]) -> list[Relation]:
        """生产五行生克 relations。"""
        relations = []
        # 五行生克表
        SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

        wuxing_facts = [f for f in facts if f.fact_type == FactType.WUXING]
        seen_pairs = set()

        for f1 in wuxing_facts:
            for f2 in wuxing_facts:
                if f1.subject == f2.subject:
                    continue
                w1, w2 = f1.value, f2.value
                pair = (f1.subject, f2.subject)
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)

                # 生
                if SHENG.get(w1) == w2:
                    relations.append(Relation(
                        relation_id=self._next_relation_id(),
                        relation_type=RelationType.SHENG,
                        subject=f1.subject,
                        object=f2.subject,
                        relation=f"{w1}生{w2}",
                        source_facts=[f1.fact_id, f2.fact_id],
                    ))
                # 克
                if KE.get(w1) == w2:
                    relations.append(Relation(
                        relation_id=self._next_relation_id(),
                        relation_type=RelationType.KE,
                        subject=f1.subject,
                        object=f2.subject,
                        relation=f"{w1}克{w2}",
                        source_facts=[f1.fact_id, f2.fact_id],
                    ))
        return relations

    def _produce_xing_chong_he_hai_relations(self, chart: BaziChart) -> list[Relation]:
        """生产刑冲合害 relations（从 BaziChart 预计算结果读取）。"""
        relations = []

        # 冲
        clash_map = getattr(chart, "branch_clash_map", {})
        for branch, clashed in clash_map.items():
            if clashed:
                relations.append(Relation(
                    relation_id=self._next_relation_id(),
                    relation_type=RelationType.CHONG,
                    subject=branch,
                    object=clashed if isinstance(clashed, str) else str(clashed),
                    relation=f"{branch}冲{clashed}",
                    metadata={"source": "bazi_engine.branch_clash_map"},
                ))

        # 合
        he_map = getattr(chart, "branch_he_map", {})
        for branch, he in he_map.items():
            if he:
                relations.append(Relation(
                    relation_id=self._next_relation_id(),
                    relation_type=RelationType.HE,
                    subject=branch,
                    object=he if isinstance(he, str) else str(he),
                    relation=f"{branch}合{he}",
                    metadata={"source": "bazi_engine.branch_he_map"},
                ))

        # 害
        hai_map = getattr(chart, "branch_harm_map", {})
        for branch, harmed in hai_map.items():
            if harmed:
                relations.append(Relation(
                    relation_id=self._next_relation_id(),
                    relation_type=RelationType.HAI,
                    subject=branch,
                    object=harmed if isinstance(harmed, str) else str(harmed),
                    relation=f"{branch}害{harmed}",
                    metadata={"source": "bazi_engine.branch_harm_map"},
                ))

        # 三刑
        sanxing_map = getattr(chart, "branch_sanxing_map", {})
        for key, value in sanxing_map.items():
            if value:
                relations.append(Relation(
                    relation_id=self._next_relation_id(),
                    relation_type=RelationType.XING,
                    subject=str(key),
                    object=str(value),
                    relation=f"三刑: {key} - {value}",
                    metadata={"source": "bazi_engine.branch_sanxing_map"},
                ))

        return relations
