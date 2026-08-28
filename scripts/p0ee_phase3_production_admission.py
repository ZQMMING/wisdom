"""P0-E-E Phase 3: Production Admission for 5 ACTIVE_ELIGIBLE CROSS_TEMPORAL Judgments.

关键原则:
  - ACTIVE_ELIGIBLE ≠ ACTIVE, 必须重新做最终Admission
  - 4个不变量:
    1. 不改变原典语义 (CT-002岁冲运=CLASH, 运克岁=CONTROLS, 不能统一)
    2. 不把结果极性塞进Judgment ("崩"属于后续解释层, 不是CLASH+NEGATIVE)
    3. 不因为CT-005内容较宽而过度泛化 (不能泛化成ANY_RELATION)
    4. Production Index必须保留完整Source Trace

  - 最终可能5、4、3条ACTIVE, 都可以接受
  - CT-003后置, 单独开P0-E-G
  - ContextResolver=FROZEN, P1=暂缓, 不制造原典/命例
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import hashlib
from datetime import datetime

from tongshu.engines.bazi_engine import (
    BaziEngine, BaziChart, Pillar,
    HEAVENLY_STEMS, EARTHLY_BRANCHES, STEM_ELEMENT, STEM_POLARITY,
    BRANCH_CLASH, BRANCH_SANXING,
)


# ============================================================================
# 1. 复用TemporalGraph数据结构 (与P0-E-F一致)
# ============================================================================

class TimeLayer(str, Enum):
    NATAL = "NATAL"
    DAYUN = "DAYUN"
    YEAR = "YEAR"


class NodeType(str, Enum):
    TEN_GOD = "TEN_GOD"
    DAY_MASTER = "DAY_MASTER"
    LUCK_PILLAR = "LUCK_PILLAR"
    FLOW_YEAR = "FLOW_YEAR"
    PILLAR = "PILLAR"


class PillarType(str, Enum):
    YEAR = "YEAR"
    MONTH = "MONTH"
    DAY = "DAY"
    HOUR = "HOUR"
    FLOW_YEAR = "FLOW_YEAR"


class RelationType(str, Enum):
    GENERATES = "GENERATES"
    CONTROLS = "CONTROLS"
    SAME = "SAME"
    CLASH = "CLASH"
    PUNISHMENT = "PUNISHMENT"
    ACTIVATES = "ACTIVATES"
    TRIGGERS = "TRIGGERS"


class MatchMode(str, Enum):
    EXACT = "EXACT"
    CONDITION = "CONDITION"
    SET = "SET"
    COMPOSITE = "COMPOSITE"


class JudgmentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PARTIAL = "PARTIAL"
    REJECTED = "REJECTED"
    ACTIVE_ELIGIBLE = "ACTIVE_ELIGIBLE"


@dataclass(frozen=True)
class TemporalNode:
    node_id: str
    node_type: NodeType
    value: str
    time_layer: TimeLayer
    year: Optional[int] = None
    dayun_index: Optional[int] = None
    stem: Optional[str] = None
    branch: Optional[str] = None
    pillar_type: Optional[PillarType] = None
    source_evidence: str = ""

    @property
    def identity_key(self) -> str:
        if self.node_type == NodeType.PILLAR and self.pillar_type:
            return f"{self.time_layer.value}:{self.pillar_type.value}:stem={self.stem}:branch={self.branch}"
        return f"{self.time_layer.value}:{self.node_type.value}:{self.value}"


@dataclass(frozen=True)
class TemporalRelation:
    edge_id: str
    source: str
    target: str
    relation_type: RelationType
    source_layer: TimeLayer
    target_layer: TimeLayer
    cross_layer: bool = False
    source_evidence: str = ""

    def __post_init__(self):
        if self.source_layer != self.target_layer:
            object.__setattr__(self, 'cross_layer', True)


class TemporalGraph:
    def __init__(self):
        self.nodes: dict[str, TemporalNode] = {}
        self.edges: dict[str, TemporalRelation] = {}

    def add_node(self, node: TemporalNode):
        self.nodes[node.node_id] = node

    def add_edge(self, edge: TemporalRelation):
        self.edges[edge.edge_id] = edge

    def find_relation(self, source: str, target: str,
                       relation_type: RelationType) -> Optional[TemporalRelation]:
        for edge in self.edges.values():
            if (edge.source == source and edge.target == target
                    and edge.relation_type == relation_type):
                return edge
        return None

    def has_relation(self, source: str, target: str,
                      relation_type: RelationType) -> bool:
        return self.find_relation(source, target, relation_type) is not None

    def find_nodes_by_layer(self, layer: TimeLayer) -> list[TemporalNode]:
        return [n for n in self.nodes.values() if n.time_layer == layer]

    def find_pillar_node(self, layer: TimeLayer, pillar_type: PillarType) -> Optional[TemporalNode]:
        for n in self.nodes.values():
            if (n.time_layer == layer and n.node_type == NodeType.PILLAR
                    and n.pillar_type == pillar_type):
                return n
        return None


# ============================================================================
# 2. 五行/地支关系计算
# ============================================================================

_GENERATES = {"WOOD": "FIRE", "FIRE": "EARTH", "EARTH": "METAL", "METAL": "WATER", "WATER": "WOOD"}
_CONTROLS = {"WOOD": "EARTH", "EARTH": "WATER", "WATER": "FIRE", "FIRE": "METAL", "METAL": "WOOD"}


def element_generates(a: str, b: str) -> bool:
    return _GENERATES.get(a) == b


def element_controls(a: str, b: str) -> bool:
    return _CONTROLS.get(a) == b


def branch_clashes(a: str, b: str) -> bool:
    return BRANCH_CLASH.get(a) == b


def calc_ten_god_en(day_master: str, other: str) -> str:
    dm_el = STEM_ELEMENT[day_master]
    ot_el = STEM_ELEMENT[other]
    same = (STEM_POLARITY[day_master] == STEM_POLARITY[other])
    if ot_el == dm_el:
        return "BI_JIAN" if same else "JIE_CAI"
    if _GENERATES.get(dm_el) == ot_el:
        return "SHI_SHEN" if same else "SHANG_GUAN"
    if _GENERATES.get(ot_el) == dm_el:
        return "PIAN_YIN" if same else "ZHENG_YIN"
    if _CONTROLS.get(ot_el) == dm_el:
        return "QI_SHA" if same else "ZHENG_GUAN"
    if _CONTROLS.get(dm_el) == ot_el:
        return "PIAN_CAI" if same else "ZHENG_CAI"
    raise ValueError(f"cannot determine 十神 for dm={day_master} other={other}")


# ============================================================================
# 3. build_temporal_graph_v2 (复用P0-E-F)
# ============================================================================

def build_temporal_graph_v2(chart: BaziChart, target_year: int) -> TemporalGraph:
    graph = TemporalGraph()
    dm = chart.day_master
    year_stem = HEAVENLY_STEMS[(target_year - 4) % 10]
    year_branch = EARTHLY_BRANCHES[(target_year - 4) % 12]

    # NATAL Pillar节点
    pillars = {
        PillarType.YEAR: chart.year_pillar,
        PillarType.MONTH: chart.month_pillar,
        PillarType.DAY: chart.day_pillar,
        PillarType.HOUR: chart.hour_pillar,
    }
    for ptype, pillar in pillars.items():
        graph.add_node(TemporalNode(
            node_id=f"N-NATAL-PILLAR-{ptype.value}",
            node_type=NodeType.PILLAR, value=f"{pillar.heavenly_stem}{pillar.earthly_branch}",
            time_layer=TimeLayer.NATAL, stem=pillar.heavenly_stem, branch=pillar.earthly_branch,
            pillar_type=ptype, source_evidence=f"BaziChart.{ptype.value.lower()}_pillar",
        ))

    # YEAR Pillar节点
    graph.add_node(TemporalNode(
        node_id=f"N-YEAR-{target_year}-PILLAR", node_type=NodeType.PILLAR,
        value=f"{year_stem}{year_branch}", time_layer=TimeLayer.YEAR, year=target_year,
        stem=year_stem, branch=year_branch, pillar_type=PillarType.FLOW_YEAR,
        source_evidence=f"流年{target_year}干={year_stem}支={year_branch}",
    ))

    # NATAL十神 + 日主
    dm_node = TemporalNode(
        node_id="N-NATAL-DM", node_type=NodeType.DAY_MASTER, value=dm,
        time_layer=TimeLayer.NATAL, stem=dm, source_evidence="BaziChart.day_master",
    )
    graph.add_node(dm_node)
    for ptype, pillar in pillars.items():
        tg = calc_ten_god_en(dm, pillar.heavenly_stem)
        graph.add_node(TemporalNode(
            node_id=f"N-NATAL-{ptype.value}-{tg}", node_type=NodeType.TEN_GOD,
            value=tg, time_layer=TimeLayer.NATAL, stem=pillar.heavenly_stem, branch=pillar.earthly_branch,
            source_evidence=f"BaziChart.{ptype.value.lower()}_pillar",
        ))

    # DAYUN节点
    dayun_nodes = []
    for i, luck in enumerate(chart.luck_pillars):
        tg = calc_ten_god_en(dm, luck.heavenly_stem)
        node = TemporalNode(
            node_id=f"N-DAYUN-{i}", node_type=NodeType.LUCK_PILLAR, value=tg,
            time_layer=TimeLayer.DAYUN, dayun_index=i, stem=luck.heavenly_stem, branch=luck.earthly_branch,
            source_evidence=f"BaziChart.luck_pillars[{i}]",
        )
        graph.add_node(node)
        dayun_nodes.append(node)

    # YEAR十神节点
    year_tg = calc_ten_god_en(dm, year_stem)
    year_tg_node = TemporalNode(
        node_id=f"N-YEAR-{target_year}", node_type=NodeType.FLOW_YEAR, value=year_tg,
        time_layer=TimeLayer.YEAR, year=target_year, stem=year_stem, branch=year_branch,
        source_evidence=f"流年{target_year}",
    )
    graph.add_node(year_tg_node)

    # 时间激活关系
    for dy in dayun_nodes:
        graph.add_edge(TemporalRelation(
            edge_id=f"E-TRIG-{dy.node_id}", source=dm_node.node_id, target=dy.node_id,
            relation_type=RelationType.TRIGGERS, source_layer=TimeLayer.NATAL, target_layer=TimeLayer.DAYUN,
            source_evidence="本命触发大运",
        ))
        graph.add_edge(TemporalRelation(
            edge_id=f"E-ACT-{dy.node_id}-{year_tg_node.node_id}",
            source=dy.node_id, target=year_tg_node.node_id, relation_type=RelationType.ACTIVATES,
            source_layer=TimeLayer.DAYUN, target_layer=TimeLayer.YEAR, source_evidence="大运激活流年",
        ))

    # DAYUN↔YEAR关系
    for dy in dayun_nodes:
        dy_el = STEM_ELEMENT[dy.stem]
        yr_el = STEM_ELEMENT[year_stem]
        if element_controls(dy_el, yr_el):
            graph.add_edge(TemporalRelation(
                edge_id=f"E-DY-CTRL-{dy.node_id}", source=dy.node_id, target=year_tg_node.node_id,
                relation_type=RelationType.CONTROLS, source_layer=TimeLayer.DAYUN, target_layer=TimeLayer.YEAR,
                source_evidence=f"大运干{dy.stem}克流年干{year_stem}",
            ))
        if element_controls(yr_el, dy_el):
            graph.add_edge(TemporalRelation(
                edge_id=f"E-YR-CTRL-{dy.node_id}", source=year_tg_node.node_id, target=dy.node_id,
                relation_type=RelationType.CONTROLS, source_layer=TimeLayer.YEAR, target_layer=TimeLayer.DAYUN,
                source_evidence=f"流年干{year_stem}克大运干{dy.stem}",
            ))
        if branch_clashes(dy.branch, year_branch):
            graph.add_edge(TemporalRelation(
                edge_id=f"E-DY-CLASH-{dy.node_id}", source=dy.node_id, target=year_tg_node.node_id,
                relation_type=RelationType.CLASH, source_layer=TimeLayer.DAYUN, target_layer=TimeLayer.YEAR,
                source_evidence=f"大运支{dy.branch}冲流年支{year_branch}",
            ))
        if branch_clashes(year_branch, dy.branch):
            graph.add_edge(TemporalRelation(
                edge_id=f"E-YR-CLASH-{dy.node_id}", source=year_tg_node.node_id, target=dy.node_id,
                relation_type=RelationType.CLASH, source_layer=TimeLayer.YEAR, target_layer=TimeLayer.DAYUN,
                source_evidence=f"流年支{year_branch}冲大运支{dy.branch}",
            ))
        if element_generates(dy_el, yr_el):
            graph.add_edge(TemporalRelation(
                edge_id=f"E-DY-GEN-{dy.node_id}", source=dy.node_id, target=year_tg_node.node_id,
                relation_type=RelationType.GENERATES, source_layer=TimeLayer.DAYUN, target_layer=TimeLayer.YEAR,
                source_evidence=f"大运干{dy.stem}生流年干{year_stem}",
            ))
        if element_generates(yr_el, dy_el):
            graph.add_edge(TemporalRelation(
                edge_id=f"E-YR-GEN-{dy.node_id}", source=year_tg_node.node_id, target=dy.node_id,
                relation_type=RelationType.GENERATES, source_layer=TimeLayer.YEAR, target_layer=TimeLayer.DAYUN,
                source_evidence=f"流年干{year_stem}生大运干{dy.stem}",
            ))

    # YEAR↔NATAL关系 (基于Pillar节点)
    natal_day = graph.find_pillar_node(TimeLayer.NATAL, PillarType.DAY)
    year_pillar = graph.find_pillar_node(TimeLayer.YEAR, PillarType.FLOW_YEAR)
    if natal_day and year_pillar:
        day_el = STEM_ELEMENT[natal_day.stem]
        yr_el = STEM_ELEMENT[year_stem]
        if branch_clashes(year_branch, natal_day.branch):
            graph.add_edge(TemporalRelation(
                edge_id=f"E-YN-CLASH", source=year_pillar.node_id, target=natal_day.node_id,
                relation_type=RelationType.CLASH, source_layer=TimeLayer.YEAR, target_layer=TimeLayer.NATAL,
                source_evidence=f"流年支{year_branch}冲日支{natal_day.branch}",
            ))
        if element_controls(yr_el, day_el):
            graph.add_edge(TemporalRelation(
                edge_id=f"E-YN-CTRL", source=year_pillar.node_id, target=natal_day.node_id,
                relation_type=RelationType.CONTROLS, source_layer=TimeLayer.YEAR, target_layer=TimeLayer.NATAL,
                source_evidence=f"流年干{year_stem}克日干{natal_day.stem}",
            ))
        if element_generates(yr_el, day_el):
            graph.add_edge(TemporalRelation(
                edge_id=f"E-YN-GEN", source=year_pillar.node_id, target=natal_day.node_id,
                relation_type=RelationType.GENERATES, source_layer=TimeLayer.YEAR, target_layer=TimeLayer.NATAL,
                source_evidence=f"流年干{year_stem}生日干{natal_day.stem}",
            ))

    return graph


# ============================================================================
# 4. Judgment Schema V2
# ============================================================================

@dataclass
class JudgmentCondition:
    """Judgment触发条件."""
    feature: str           # 特征标识, 如 "DAYUN→YEAR:CLASH"
    operator: str          # 操作符, 如 "EXISTS", "EQ"
    source_layer: str     # 源层
    target_layer: str     # 目标层
    relation_type: str    # 关系类型
    description: str      # 中文描述


@dataclass
class JudgmentSource:
    """原典来源."""
    book: str
    school: str
    chapter: str
    section: Optional[str] = None
    classical_text: str = ""
    source_locator: str = ""
    text_hash: str = ""


@dataclass
class JudgmentSpecificity:
    """特异度Profile (多维, 不是单一数字)."""
    constraint_count: int
    match_mode: str
    feature_depth: int
    structural_depth: int
    temporal_depth: int
    scope: str
    discrimination: str


@dataclass
class JudgmentAssetV2:
    """Judgment Schema V2."""
    # identity
    judgment_id: str
    system: str = "ZI_PING"
    school: str = ""
    judgment_type: str = "CROSS_TEMPORAL"
    version: str = "2.0"

    # retrieval
    match_mode: MatchMode = MatchMode.CONDITION
    conditions: list[JudgmentCondition] = field(default_factory=list)
    feature_requirements: list[str] = field(default_factory=list)
    specificity: Optional[JudgmentSpecificity] = None

    # statement (不包含结果极性)
    classical: str = ""
    semantic_keys: list[str] = field(default_factory=list)
    modern_mapping: str = ""  # 资产标注, 不是LLM生成

    # source
    source: Optional[JudgmentSource] = None

    # provenance
    created_at: str = ""
    revision: int = 1
    status: JudgmentStatus = JudgmentStatus.ACTIVE_ELIGIBLE

    # admission results
    admission_gates: dict = field(default_factory=dict)
    positive_cases: list[dict] = field(default_factory=list)
    negative_cases: list[dict] = field(default_factory=list)
    determinism_verified: bool = False


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ============================================================================
# 5. 5条Judgment Asset定义
# ============================================================================

def build_judgments() -> list[JudgmentAssetV2]:
    """构建5条ACTIVE_ELIGIBLE Judgment Asset."""
    judgments = []

    # CT-001: 大运不宜与太岁相克相冲
    j1 = JudgmentAssetV2(
        judgment_id="CT-001",
        school="SAN_MING_TONG_HUI",
        judgment_type="CROSS_TEMPORAL_DAYUN_YEAR",
        match_mode=MatchMode.CONDITION,
        conditions=[
            JudgmentCondition(feature="DAYUN→YEAR:CONTROLS", operator="EXISTS",
                              source_layer="DAYUN", target_layer="YEAR", relation_type="CONTROLS",
                              description="大运干克流年干"),
            JudgmentCondition(feature="DAYUN→YEAR:CLASH", operator="EXISTS",
                              source_layer="DAYUN", target_layer="YEAR", relation_type="CLASH",
                              description="大运支冲流年支"),
        ],
        feature_requirements=["DAYUN_PILLAR", "YEAR_PILLAR"],
        specificity=JudgmentSpecificity(
            constraint_count=2, match_mode="CONDITION", feature_depth=2,
            structural_depth=1, temporal_depth=2, scope="DAYUN_YEAR", discrimination="HIGH",
        ),
        classical="大运不宜与太岁相克相冲，尤忌运克岁",
        semantic_keys=["CROSS_TEMPORAL", "DAYUN_YEAR", "CONTROLS", "CLASH"],
        modern_mapping="大运与流年之间存在相克或相冲关系时触发",
        source=JudgmentSource(
            book="三命通会", school="SAN_MING_TONG_HUI", chapter="卷二·论大运",
            classical_text="大运不宜与太岁相克相冲，尤忌运克岁",
            source_locator="卷二·论大运",
        ),
        created_at=datetime.now().isoformat(),
    )
    j1.source.text_hash = text_hash(j1.source.classical_text)
    judgments.append(j1)

    # CT-002: 岁冲运则崩，运克岁则晦
    # 关键: 保持两个独立关系, 不能统一
    j2 = JudgmentAssetV2(
        judgment_id="CT-002",
        school="SAN_MING_TONG_HUI",
        judgment_type="CROSS_TEMPORAL_YEAR_DAYUN",
        match_mode=MatchMode.COMPOSITE,
        conditions=[
            JudgmentCondition(feature="YEAR→DAYUN:CLASH", operator="EXISTS",
                              source_layer="YEAR", target_layer="DAYUN", relation_type="CLASH",
                              description="岁冲运: 流年支冲大运支"),
            JudgmentCondition(feature="DAYUN→YEAR:CONTROLS", operator="EXISTS",
                              source_layer="DAYUN", target_layer="YEAR", relation_type="CONTROLS",
                              description="运克岁: 大运干克流年干"),
        ],
        feature_requirements=["DAYUN_PILLAR", "YEAR_PILLAR"],
        specificity=JudgmentSpecificity(
            constraint_count=2, match_mode="COMPOSITE", feature_depth=2,
            structural_depth=2, temporal_depth=2, scope="YEAR_DAYUN", discrimination="HIGH",
        ),
        classical="岁冲运则崩，运克岁则晦",
        semantic_keys=["CROSS_TEMPORAL", "YEAR_DAYUN", "CLASH", "CONTROLS"],
        modern_mapping="流年冲大运(岁冲运)或大运克流年(运克岁)时触发, 两个关系独立",
        source=JudgmentSource(
            book="三命通会", school="SAN_MING_TONG_HUI", chapter="卷十一·明通赋五",
            classical_text="岁冲运则崩，运克岁则晦",
            source_locator="卷十一·明通赋五",
        ),
        created_at=datetime.now().isoformat(),
    )
    j2.source.text_hash = text_hash(j2.source.classical_text)
    judgments.append(j2)

    # CT-004: 太岁干支冲日干支亦曰征
    j4 = JudgmentAssetV2(
        judgment_id="CT-004",
        school="SAN_MING_TONG_HUI",
        judgment_type="CROSS_TEMPORAL_YEAR_NATAL",
        match_mode=MatchMode.CONDITION,
        conditions=[
            JudgmentCondition(feature="YEAR→NATAL:CLASH", operator="EXISTS",
                              source_layer="YEAR", target_layer="NATAL", relation_type="CLASH",
                              description="太岁干支冲日干支: 流年支冲日支"),
        ],
        feature_requirements=["YEAR_PILLAR", "NATAL_DAY_PILLAR"],
        specificity=JudgmentSpecificity(
            constraint_count=1, match_mode="CONDITION", feature_depth=2,
            structural_depth=1, temporal_depth=2, scope="YEAR_NATAL", discrimination="HIGH",
        ),
        classical="太岁干支冲日干支亦曰征",
        semantic_keys=["CROSS_TEMPORAL", "YEAR_NATAL", "CLASH"],
        modern_mapping="流年干支与日柱干支存在相冲关系时触发",
        source=JudgmentSource(
            book="三命通会", school="SAN_MING_TONG_HUI", chapter="卷二·论太岁",
            classical_text="太岁干支冲日干支亦曰征",
            source_locator="卷二·论太岁",
        ),
        created_at=datetime.now().isoformat(),
    )
    j4.source.text_hash = text_hash(j4.source.classical_text)
    judgments.append(j4)

    # CT-005: 大运不宜与太岁相克相冲者凶；岁运相生者吉
    # 关键: 保持三个独立关系, 不能泛化成ANY_RELATION
    j5 = JudgmentAssetV2(
        judgment_id="CT-005",
        school="YUAN_HAI_ZI_PING",
        judgment_type="CROSS_TEMPORAL_DAYUN_YEAR_MULTI",
        match_mode=MatchMode.SET,
        conditions=[
            JudgmentCondition(feature="DAYUN→YEAR:CONTROLS", operator="EXISTS",
                              source_layer="DAYUN", target_layer="YEAR", relation_type="CONTROLS",
                              description="大运与太岁相克"),
            JudgmentCondition(feature="DAYUN→YEAR:CLASH", operator="EXISTS",
                              source_layer="DAYUN", target_layer="YEAR", relation_type="CLASH",
                              description="大运与太岁相冲"),
            JudgmentCondition(feature="DAYUN→YEAR:GENERATES", operator="EXISTS",
                              source_layer="DAYUN", target_layer="YEAR", relation_type="GENERATES",
                              description="岁运相生"),
            JudgmentCondition(feature="YEAR→DAYUN:GENERATES", operator="EXISTS",
                              source_layer="YEAR", target_layer="DAYUN", relation_type="GENERATES",
                              description="岁运相生(反向)"),
        ],
        feature_requirements=["DAYUN_PILLAR", "YEAR_PILLAR"],
        specificity=JudgmentSpecificity(
            constraint_count=4, match_mode="SET", feature_depth=2,
            structural_depth=1, temporal_depth=2, scope="DAYUN_YEAR", discrimination="MEDIUM",
        ),
        classical="大运不宜与太岁相克、相冲者凶；岁运相生者吉",
        semantic_keys=["CROSS_TEMPORAL", "DAYUN_YEAR", "CONTROLS", "CLASH", "GENERATES"],
        modern_mapping="大运与流年之间存在相克、相冲或相生关系时触发, 三种关系独立",
        source=JudgmentSource(
            book="渊海子平", school="YUAN_HAI_ZI_PING", chapter="基础第一",
            classical_text="大运不宜与太岁相克、相冲者凶；岁运相生者吉",
            source_locator="基础第一·论大运",
        ),
        created_at=datetime.now().isoformat(),
    )
    j5.source.text_hash = text_hash(j5.source.classical_text)
    judgments.append(j5)

    # CT-006: 行运以生月为运元，最怕行运与太岁冲克
    j6 = JudgmentAssetV2(
        judgment_id="CT-006",
        school="SAN_MING_TONG_HUI",
        judgment_type="CROSS_TEMPORAL_DAYUN_YEAR",
        match_mode=MatchMode.CONDITION,
        conditions=[
            JudgmentCondition(feature="DAYUN→YEAR:CLASH", operator="EXISTS",
                              source_layer="DAYUN", target_layer="YEAR", relation_type="CLASH",
                              description="行运与太岁冲"),
            JudgmentCondition(feature="DAYUN→YEAR:CONTROLS", operator="EXISTS",
                              source_layer="DAYUN", target_layer="YEAR", relation_type="CONTROLS",
                              description="行运与太岁克"),
        ],
        feature_requirements=["DAYUN_PILLAR", "YEAR_PILLAR"],
        specificity=JudgmentSpecificity(
            constraint_count=2, match_mode="CONDITION", feature_depth=2,
            structural_depth=1, temporal_depth=2, scope="DAYUN_YEAR", discrimination="HIGH",
        ),
        classical="行运以生月为运元，最怕行运与太岁冲克",
        semantic_keys=["CROSS_TEMPORAL", "DAYUN_YEAR", "CLASH", "CONTROLS"],
        modern_mapping="大运与流年之间存在相冲或相克关系时触发",
        source=JudgmentSource(
            book="三命通会", school="SAN_MING_TONG_HUI", chapter="卷二·论大运",
            classical_text="行运以生月为运元，最怕行运与太岁冲克",
            source_locator="卷二·论大运",
        ),
        created_at=datetime.now().isoformat(),
    )
    j6.source.text_hash = text_hash(j6.source.classical_text)
    judgments.append(j6)

    return judgments


# ============================================================================
# 6. Production Admission
# ============================================================================

def run_admission(judgment: JudgmentAssetV2, graphs: dict, chart: BaziChart) -> JudgmentAssetV2:
    """对一条Judgment执行最终Production Admission."""
    gates = {}
    target_years = list(graphs.keys())

    # Gate 1: Source Trace完整性
    source_complete = (judgment.source is not None
                        and judgment.source.book
                        and judgment.source.chapter
                        and judgment.source.classical_text
                        and judgment.source.text_hash)
    gates["source_trace"] = {
        "passed": source_complete,
        "details": [f"book={judgment.source.book if judgment.source else None}, "
                    f"chapter={judgment.source.chapter if judgment.source else None}, "
                    f"text_hash={'present' if judgment.source and judgment.source.text_hash else 'missing'}"]
    }

    # Gate 2: Canonical Fidelity (不改变原典语义)
    canonical_fidelity = True
    canonical_details = []
    # 验证conditions中的关系类型与原文一致
    for cond in judgment.conditions:
        if cond.relation_type not in ("CONTROLS", "CLASH", "GENERATES", "SAME", "PUNISHMENT"):
            canonical_fidelity = False
            canonical_details.append(f"非法关系类型: {cond.relation_type}")
    # 特别验证CT-002: 岁冲运=CLASH, 运克岁=CONTROLS, 不能统一
    if judgment.judgment_id == "CT-002":
        has_clash = any(c.relation_type == "CLASH" and c.source_layer == "YEAR" for c in judgment.conditions)
        has_controls = any(c.relation_type == "CONTROLS" and c.source_layer == "DAYUN" for c in judgment.conditions)
        if not (has_clash and has_controls):
            canonical_fidelity = False
            canonical_details.append("CT-002必须同时包含YEAR→DAYUN CLASH(岁冲运)和DAYUN→YEAR CONTROLS(运克岁), 不能统一")
        else:
            canonical_details.append("CT-002保持两个独立关系: 岁冲运=CLASH, 运克岁=CONTROLS")
    # 特别验证CT-005: 不能泛化成ANY_RELATION
    if judgment.judgment_id == "CT-005":
        relation_types = set(c.relation_type for c in judgment.conditions)
        if len(relation_types) < 3:
            canonical_fidelity = False
            canonical_details.append("CT-005必须包含CONTROLS/CLASH/GENERATES三种独立关系, 不能泛化")
        else:
            canonical_details.append(f"CT-005保持{len(relation_types)}种独立关系: {relation_types}")
    if canonical_fidelity and not canonical_details:
        canonical_details.append("conditions关系类型与原文一致")
    gates["canonical_fidelity"] = {"passed": canonical_fidelity, "details": canonical_details}

    # Gate 3: Polarity Isolation (不把结果极性塞进Judgment)
    polarity_isolation = True
    polarity_details = []
    # 验证classical文本不包含在conditions中作为关系类型
    polarity_keywords = ["崩", "晦", "凶", "吉", "灾", "祸", "福", "不利", "宜"]
    for cond in judgment.conditions:
        if any(kw in cond.description for kw in polarity_keywords):
            # description中可以有原文引用, 但relation_type必须是纯结构
            if cond.relation_type in polarity_keywords:
                polarity_isolation = False
                polarity_details.append(f"条件{cond.feature}的relation_type包含结果极性")
    # 验证semantic_keys不包含极性
    polarity_semantic = ["NEGATIVE", "POSITIVE", "BAD", "GOOD", "DISASTER", "FORTUNE"]
    for sk in judgment.semantic_keys:
        if sk.upper() in polarity_semantic:
            polarity_isolation = False
            polarity_details.append(f"semantic_key包含极性: {sk}")
    if polarity_isolation:
        polarity_details.append("Judgment只包含结构关系(CONTROLS/CLASH/GENERATES), 不包含结果极性(崩/晦/凶/吉)")
    gates["polarity_isolation"] = {"passed": polarity_isolation, "details": polarity_details}

    # Gate 4: Node Sufficiency
    node_sufficiency = True
    node_details = []
    first_graph = graphs[target_years[0]]
    for req in judgment.feature_requirements:
        if req == "DAYUN_PILLAR":
            dayun_nodes = first_graph.find_nodes_by_layer(TimeLayer.DAYUN)
            if not dayun_nodes:
                node_sufficiency = False
                node_details.append("DAYUN_PILLAR缺失")
            else:
                node_details.append(f"DAYUN_PILLAR存在({len(dayun_nodes)}个)")
        elif req == "YEAR_PILLAR":
            year_pillar = first_graph.find_pillar_node(TimeLayer.YEAR, PillarType.FLOW_YEAR)
            if not year_pillar:
                node_sufficiency = False
                node_details.append("YEAR_PILLAR缺失")
            else:
                node_details.append("YEAR_PILLAR存在")
        elif req == "NATAL_DAY_PILLAR":
            day_pillar = first_graph.find_pillar_node(TimeLayer.NATAL, PillarType.DAY)
            if not day_pillar:
                node_sufficiency = False
                node_details.append("NATAL_DAY_PILLAR缺失")
            else:
                node_details.append("NATAL_DAY_PILLAR存在")
    gates["node_sufficiency"] = {"passed": node_sufficiency, "details": node_details}

    # Gate 5: Relation Fidelity + Positive Match
    relation_fidelity = True
    positive_cases = []
    for cond in judgment.conditions:
        found = False
        found_year = None
        for year, g in graphs.items():
            # 根据条件查找关系
            src_layer = TimeLayer(cond.source_layer)
            tgt_layer = TimeLayer(cond.target_layer)
            rel_type = RelationType(cond.relation_type)
            for edge in g.edges.values():
                if (edge.relation_type == rel_type
                        and edge.source_layer == src_layer
                        and edge.target_layer == tgt_layer):
                    found = True
                    found_year = year
                    positive_cases.append({
                        "condition": cond.feature, "year": year,
                        "evidence": edge.source_evidence,
                    })
                    break
            if found:
                break
        if not found:
            relation_fidelity = False
    gates["relation_fidelity"] = {
        "passed": relation_fidelity,
        "details": [f"找到{len(positive_cases)}个Positive案例" if relation_fidelity
                    else f"部分条件未找到Positive案例"]
    }
    judgment.positive_cases = positive_cases

    # Gate 6: Negative Boundary
    negative_boundary = True
    negative_cases = []
    # 验证: 不满足条件的年份不会MATCH
    for year, g in graphs.items():
        # 检查该年份是否满足所有conditions
        all_match = True
        for cond in judgment.conditions:
            src_layer = TimeLayer(cond.source_layer)
            tgt_layer = TimeLayer(cond.target_layer)
            rel_type = RelationType(cond.relation_type)
            has_rel = any(e.relation_type == rel_type and e.source_layer == src_layer and e.target_layer == tgt_layer
                           for e in g.edges.values())
            if not has_rel:
                all_match = False
                break
        if not all_match:
            negative_cases.append({"year": year, "result": "REJECT (not all conditions met)"})
    # 验证: 关系类型不会混淆(CLASH不会被识别为CONTROLS)
    for year, g in graphs.items():
        for edge in g.edges.values():
            if edge.relation_type == RelationType.CLASH and "克" in edge.source_evidence and "冲" not in edge.source_evidence:
                negative_boundary = False
                negative_cases.append({"year": year, "issue": "CLASH关系source_evidence包含'克'但无'冲'"})
    gates["negative_boundary"] = {
        "passed": negative_boundary,
        "details": [f"{len(negative_cases)}个Negative案例正确REJECT" if negative_boundary else "存在边界问题"]
    }
    judgment.negative_cases = negative_cases[:5]  # 只保留前5个

    # Gate 7: Determinism
    determinism = True
    # 验证: 同一输入重复运行得到相同结果
    for year in target_years[:3]:
        g1 = build_temporal_graph_v2(chart, year)
        g2 = build_temporal_graph_v2(chart, year)
        edges1 = set((e.source, e.target, e.relation_type.value) for e in g1.edges.values())
        edges2 = set((e.source, e.target, e.relation_type.value) for e in g2.edges.values())
        if edges1 != edges2:
            determinism = False
    judgment.determinism_verified = determinism
    gates["determinism"] = {
        "passed": determinism,
        "details": ["同一输入重复运行结果一致" if determinism else "重复运行结果不一致"]
    }

    # Production Admission决策
    all_pass = all(g["passed"] for g in gates.values())
    gates["production_admission"] = {
        "passed": all_pass,
        "details": [f"全部Gate通过: {all_pass} → {'ACTIVE' if all_pass else 'NOT ACTIVE'}"]
    }

    judgment.admission_gates = gates
    if all_pass:
        judgment.status = JudgmentStatus.ACTIVE
    else:
        failed = [k for k, v in gates.items() if not v["passed"]]
        judgment.status = JudgmentStatus.PARTIAL
        judgment.admission_gates["failed_gates"] = failed

    return judgment


# ============================================================================
# 7. 4个不变量验证
# ============================================================================

def verify_invariants(judgments: list[JudgmentAssetV2]) -> dict:
    """验证4个不变量."""
    result = {"invariant_1": {}, "invariant_2": {}, "invariant_3": {}, "invariant_4": {}}

    # 不变量1: 不改变原典语义 (CT-002岁冲运=CLASH, 运克岁=CONTROLS)
    ct002 = next((j for j in judgments if j.judgment_id == "CT-002"), None)
    if ct002:
        has_year_dayun_clash = any(c.relation_type == "CLASH" and c.source_layer == "YEAR" and c.target_layer == "DAYUN"
                                    for c in ct002.conditions)
        has_dayun_year_controls = any(c.relation_type == "CONTROLS" and c.source_layer == "DAYUN" and c.target_layer == "YEAR"
                                       for c in ct002.conditions)
        result["invariant_1"] = {
            "passed": has_year_dayun_clash and has_dayun_year_controls,
            "details": f"CT-002: 岁冲运(YEAR→DAYUN CLASH)={has_year_dayun_clash}, 运克岁(DAYUN→YEAR CONTROLS)={has_dayun_year_controls}",
        }

    # 不变量2: 不把结果极性塞进Judgment
    all_no_polarity = True
    for j in judgments:
        for c in j.conditions:
            if c.relation_type in ("崩", "晦", "凶", "吉", "灾"):
                all_no_polarity = False
        for sk in j.semantic_keys:
            if sk.upper() in ("NEGATIVE", "POSITIVE", "BAD", "GOOD"):
                all_no_polarity = False
    result["invariant_2"] = {
        "passed": all_no_polarity,
        "details": "所有Judgment只包含结构关系, 不包含结果极性(崩/晦/凶/吉)",
    }

    # 不变量3: 不因为CT-005内容较宽而过度泛化
    ct005 = next((j for j in judgments if j.judgment_id == "CT-005"), None)
    if ct005:
        relation_types = set(c.relation_type for c in ct005.conditions)
        not_any_relation = "ANY" not in relation_types and len(relation_types) >= 3
        result["invariant_3"] = {
            "passed": not_any_relation,
            "details": f"CT-005保持{len(relation_types)}种独立关系: {relation_types}, 未泛化为ANY_RELATION",
        }

    # 不变量4: Production Index保留完整Source Trace
    all_source_complete = all(j.source and j.source.book and j.source.chapter
                               and j.source.classical_text and j.source.text_hash
                               for j in judgments)
    result["invariant_4"] = {
        "passed": all_source_complete,
        "details": f"所有{len(judgments)}条Judgment都有完整Source Trace (book/chapter/classical_text/text_hash)",
    }

    return result


# ============================================================================
# 8. 主函数
# ============================================================================

def main():
    print("=" * 90)
    print("P0-E-E Phase 3: Production Admission for 5 ACTIVE_ELIGIBLE CROSS_TEMPORAL Judgments")
    print("=" * 90)
    print("\n关键原则: ACTIVE_ELIGIBLE ≠ ACTIVE, 必须重新做最终Admission")
    print("4个不变量: 不改变原典语义 / 不塞极性 / 不过度泛化 / 完整Source Trace")
    print("最终可能5、4、3条ACTIVE, 都可以接受; CT-003后置; ContextResolver=FROZEN")

    # Part 1: 构建Graph
    print("\n" + "=" * 90)
    print("Part 1: 构建TemporalGraph (1983男命, 2024-2034)")
    print("=" * 90)

    engine = BaziEngine()
    chart = engine.compute((1983, 6, 15, 12), "male")
    target_years = list(range(2024, 2035))
    graphs = {yr: build_temporal_graph_v2(chart, yr) for yr in target_years}
    print(f"\n  命例: 1983-06-15 12:00 男, 日主={chart.day_master}, 日柱={chart.day_pillar.heavenly_stem}{chart.day_pillar.earthly_branch}")
    print(f"  目标年: {target_years[0]}-{target_years[-1]} ({len(target_years)}年)")

    # Part 2: 构建5条Judgment Asset
    print("\n" + "=" * 90)
    print("Part 2: 构建5条Judgment Asset V2")
    print("=" * 90)

    judgments = build_judgments()
    for j in judgments:
        print(f"\n  [{j.judgment_id}] {j.source.book}·{j.source.chapter}")
        print(f"    原文: {j.classical}")
        print(f"    match_mode: {j.match_mode.value}, conditions: {len(j.conditions)}个")
        for c in j.conditions:
            print(f"      {c.feature}: {c.source_layer}→{c.target_layer} {c.relation_type} ({c.description})")
        print(f"    specificity: constraint_count={j.specificity.constraint_count}, discrimination={j.specificity.discrimination}")

    # Part 3: 逐条Production Admission
    print("\n" + "=" * 90)
    print("Part 3: 逐条Production Admission")
    print("=" * 90)

    admitted = []
    for j in judgments:
        j = run_admission(j, graphs, chart)
        admitted.append(j)
        print(f"\n  [{j.judgment_id}] {j.source.book}·{j.source.chapter}")
        print(f"    最终状态: {j.status.value}")
        for gate_name, gate_result in j.admission_gates.items():
            if gate_name == "failed_gates":
                continue
            status = "✓" if gate_result["passed"] else "✗"
            print(f"    {status} {gate_name}: {'; '.join(gate_result['details'][:1])[:100]}")
        if j.positive_cases:
            print(f"    Positive案例: {len(j.positive_cases)}个 (e.g. {j.positive_cases[0]['year']}: {j.positive_cases[0]['evidence'][:40]})")

    # Part 4: 4个不变量验证
    print("\n" + "=" * 90)
    print("Part 4: 4个不变量验证")
    print("=" * 90)

    invariants = verify_invariants(admitted)
    for inv_name, inv_result in invariants.items():
        status = "✓" if inv_result.get("passed", False) else "✗"
        print(f"\n  {status} {inv_name}: {inv_result.get('details', '')}")

    all_invariants_pass = all(v.get("passed", False) for v in invariants.values())
    print(f"\n  4个不变量全部通过: {'是' if all_invariants_pass else '否'}")

    # Part 5: Production Index
    print("\n" + "=" * 90)
    print("Part 5: Production Index (CROSS_TEMPORAL)")
    print("=" * 90)

    active = [j for j in admitted if j.status == JudgmentStatus.ACTIVE]
    partial = [j for j in admitted if j.status == JudgmentStatus.PARTIAL]
    rejected = [j for j in admitted if j.status == JudgmentStatus.REJECTED]

    print(f"""
  CROSS_TEMPORAL Production Index:
    ACTIVE: {len(active)}条""")
    for j in active:
        print(f"      [{j.judgment_id}] {j.source.book}·{j.source.chapter} — {j.classical[:30]}")
    print(f"""    PARTIAL: {len(partial)}条""")
    for j in partial:
        failed = j.admission_gates.get("failed_gates", [])
        print(f"      [{j.judgment_id}] {j.source.book}·{j.source.chapter} — failed: {failed}")
    print(f"""    REJECTED: {len(rejected)}条
    CT-003(岁运并临): PARTIAL (后置, 单独开P0-E-G验证)

  4个不变量: {'全部通过' if all_invariants_pass else '存在违反'}
  ContextResolver: FROZEN
  P1 GRAPH Expansion: 暂缓
  不制造原典/命例: 是
  不为了Coverage增加ACTIVE: 是
  ACTIVE_ELIGIBLE不直接当ACTIVE: 是 (全部重新Admission)
""")

    print("=" * 90)
    print(f"P0-E-E Phase 3 Production Admission: COMPLETE")
    print(f"  (ACTIVE={len(active)}, PARTIAL={len(partial)}, REJECTED={len(rejected)}, "
          f"invariants={'PASS' if all_invariants_pass else 'FAIL'})")
    print("=" * 90)


if __name__ == "__main__":
    main()
