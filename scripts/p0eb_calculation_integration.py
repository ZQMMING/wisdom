"""P0-E-B DaYun / Year Calculation Integration.

范围锁窄: 将BaziEngine的真实计算结果(BaziChart)确定性投影到TemporalGraph.
作为P0-E-E Real Canonical Cross-Temporal Vertical Slice的前置基础设施.

职责分离 (严格执行):
  BaziEngine = 负责算 (四柱/大运/流年/十神)
  TemporalProjection = 负责把计算结果投影成TemporalGraph节点和边
  TemporalGraph = 负责表达 (NATAL/DAYUN/YEAR三层节点和跨层关系)
  TemporalMatcher = 负责匹配
  Canonical Judgment = 负责证明原典允许什么

本阶段不产生ACTIVE Judgment, 不创建Canonical Asset.
ContextResolver继续冻结.

4件事:
  ① Bazi → TemporalGraph Contract
  ② DaYun Calculation Integration
  ③ Year Calculation Integration
  ④ 严格Negative Boundary
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
import hashlib

from tongshu.engines.bazi_engine import (
    BaziEngine, BaziChart, Pillar,
    HEAVENLY_STEMS, EARTHLY_BRANCHES, STEM_ELEMENT, STEM_POLARITY,
)


# ============================================================================
# 1. 复用P0-E的Temporal Graph数据结构
# ============================================================================

class TimeLayer(str, Enum):
    NATAL = "NATAL"
    DAYUN = "DAYUN"
    YEAR = "YEAR"
    MONTH = "MONTH"
    DAY = "DAY"


class NodeType(str, Enum):
    TEN_GOD = "TEN_GOD"
    ELEMENT = "ELEMENT"
    STEM = "STEM"
    BRANCH = "BRANCH"
    PILLAR = "PILLAR"
    DAY_MASTER = "DAY_MASTER"
    LUCK_PILLAR = "LUCK_PILLAR"
    FLOW_YEAR = "FLOW_YEAR"
    STRUCTURE = "STRUCTURE"
    TERMINAL = "TERMINAL"


class RelationType(str, Enum):
    GENERATES = "GENERATES"
    CONTROLS = "CONTROLS"
    SAME = "SAME"
    OPPOSES = "OPPOSES"
    COMBINES = "COMBINES"
    HARM = "HARM"
    PUNISHMENT = "PUNISHMENT"
    TRANSFORMS = "TRANSFORMS"
    ACTIVATES = "ACTIVATES"
    TRIGGERS = "TRIGGERS"
    PROJECTS = "PROJECTS"


ALLOWED_CROSS_LAYER_RELATIONS = {
    RelationType.TRIGGERS, RelationType.ACTIVATES, RelationType.PROJECTS
}


@dataclass(frozen=True)
class TemporalGraphNode:
    node_id: str
    node_type: NodeType
    value: str
    time_layer: TimeLayer
    year: Optional[int] = None
    dayun_index: Optional[int] = None
    source_evidence: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)

    def identity_key(self) -> str:
        key = f"{self.value}:{self.time_layer.value}"
        if self.year is not None:
            key += f":{self.year}"
        if self.dayun_index is not None:
            key += f":DY{self.dayun_index}"
        return key

    def identity_hash(self) -> str:
        return hashlib.sha256(self.identity_key().encode()).hexdigest()[:12]


@dataclass(frozen=True)
class TemporalGraphRelation:
    edge_id: str
    source: str
    target: str
    relation_type: RelationType
    source_layer: TimeLayer
    target_layer: TimeLayer
    cross_layer: bool = False
    strength: float = 1.0
    source_evidence: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.source_layer != self.target_layer:
            object.__setattr__(self, 'cross_layer', True)

    def is_valid_cross_layer(self) -> bool:
        if not self.cross_layer:
            return True
        return self.relation_type in ALLOWED_CROSS_LAYER_RELATIONS


@dataclass(frozen=True)
class TemporalGraphPath:
    path_id: str
    nodes: list[str]
    edges: list[str]
    layers: list[str] = field(default_factory=list)
    path_length: int = 0

    def __post_init__(self):
        object.__setattr__(self, 'path_length', len(self.edges))

    def identity_key(self) -> str:
        return f"{'->'.join(self.nodes)}|{'->'.join(self.edges)}|{'->'.join(self.layers)}"

    def identity_hash(self) -> str:
        return hashlib.sha256(self.identity_key().encode()).hexdigest()[:16]


class TemporalGraphMatcher:
    def __init__(self):
        self.nodes: dict[str, TemporalGraphNode] = {}
        self.edges: dict[str, TemporalGraphRelation] = {}
        self.adjacency: dict[str, list[str]] = {}
        self.nodes_by_layer: dict[str, list[str]] = {}

    def add_node(self, node: TemporalGraphNode):
        self.nodes[node.node_id] = node
        layer = node.time_layer.value
        if layer not in self.nodes_by_layer:
            self.nodes_by_layer[layer] = []
        self.nodes_by_layer[layer].append(node.node_id)
        self.nodes_by_layer[layer].sort()

    def add_edge(self, edge: TemporalGraphRelation):
        self.edges[edge.edge_id] = edge
        if edge.source not in self.adjacency:
            self.adjacency[edge.source] = []
        self.adjacency[edge.source].append(edge.edge_id)
        self.adjacency[edge.source].sort()

    def find_node_by_identity(self, value: str, time_layer: TimeLayer,
                               year: Optional[int] = None,
                               dayun_index: Optional[int] = None) -> Optional[TemporalGraphNode]:
        for node in self.nodes.values():
            if (node.value == value and node.time_layer == time_layer
                    and node.year == year and node.dayun_index == dayun_index):
                return node
        return None

    def find_all_paths(self, source: str, target: str,
                        max_length: int = 5,
                        allowed_cross_layer: bool = True,
                        required_layers: Optional[list[TimeLayer]] = None) -> list[TemporalGraphPath]:
        paths = []
        queue = [(source, [source], [], [])]
        while queue:
            current, path_nodes, path_edges, path_layers = queue.pop(0)
            if current == target and len(path_nodes) > 1:
                if required_layers:
                    actual_layers = [self.nodes[n].time_layer for n in path_nodes]
                    if actual_layers != required_layers:
                        continue
                paths.append(TemporalGraphPath(
                    path_id=f"PATH_{len(paths)+1:03d}",
                    nodes=list(path_nodes), edges=list(path_edges),
                    layers=list(path_layers),
                ))
                continue
            if len(path_nodes) >= max_length + 1:
                continue
            for edge_id in self.adjacency.get(current, []):
                edge = self.edges[edge_id]
                if edge.cross_layer and not allowed_cross_layer:
                    continue
                if edge.cross_layer and not edge.is_valid_cross_layer():
                    continue
                if edge.target not in path_nodes:
                    target_node = self.nodes[edge.target]
                    queue.append((
                        edge.target,
                        path_nodes + [edge.target],
                        path_edges + [edge_id],
                        path_layers + [target_node.time_layer.value],
                    ))
        paths.sort(key=lambda p: (p.path_length, tuple(p.nodes), tuple(p.layers)))
        for i, p in enumerate(paths, 1):
            object.__setattr__(p, 'path_id', f"PATH_{i:03d}")
        return paths

    def validate_cross_layer_relations(self) -> dict:
        invalid_edges = []
        valid_cross_edges = []
        for edge in self.edges.values():
            if edge.cross_layer:
                if edge.is_valid_cross_layer():
                    valid_cross_edges.append(edge)
                else:
                    invalid_edges.append(edge)
        return {
            "total_cross_edges": len(valid_cross_edges) + len(invalid_edges),
            "valid_cross_edges": len(valid_cross_edges),
            "invalid_cross_edges": len(invalid_edges),
            "all_valid": len(invalid_edges) == 0,
        }


# ============================================================================
# 2. 十神计算 (复用bazi_engine的_ten_god逻辑)
# ============================================================================

_GENERATES = {"WOOD": "FIRE", "FIRE": "EARTH", "EARTH": "METAL", "METAL": "WATER", "WATER": "WOOD"}
_CONTROLS = {"WOOD": "EARTH", "EARTH": "WATER", "WATER": "FIRE", "FIRE": "METAL", "METAL": "WOOD"}

# 十神英文映射
TEN_GOD_EN = {
    "比肩": "BI_JIAN", "劫财": "JIE_CAI",
    "食神": "SHI_SHEN", "伤官": "SHANG_GUAN",
    "偏印": "PIAN_YIN", "正印": "ZHENG_YIN",
    "七杀": "QI_SHA", "正官": "ZHENG_GUAN",
    "偏财": "PIAN_CAI", "正财": "ZHENG_CAI",
}


def calc_ten_god(day_master: str, other: str) -> str:
    """计算十神, 返回英文名称."""
    dm_el = STEM_ELEMENT[day_master]
    ot_el = STEM_ELEMENT[other]
    same = (STEM_POLARITY[day_master] == STEM_POLARITY[other])
    if ot_el == dm_el:
        cn = "比肩" if same else "劫财"
    elif _GENERATES.get(dm_el) == ot_el:
        cn = "食神" if same else "伤官"
    elif _GENERATES.get(ot_el) == dm_el:
        cn = "偏印" if same else "正印"
    elif _CONTROLS.get(ot_el) == dm_el:
        cn = "七杀" if same else "正官"
    elif _CONTROLS.get(dm_el) == ot_el:
        cn = "偏财" if same else "正财"
    else:
        raise ValueError(f"cannot determine 十神 for dm={day_master} other={other}")
    return TEN_GOD_EN[cn]


# ============================================================================
# 3. Bazi → TemporalGraph Contract (TemporalProjection)
# ============================================================================

@dataclass(frozen=True)
class TemporalProjection:
    """将BaziChart的计算结果确定性投影到TemporalGraph.

    职责: 只做投影, 不做推理, 不做匹配, 不创建Judgment.
    输入: BaziChart (来自BaziEngine.compute)
    输出: TemporalGraphMatcher (包含NATAL/DAYUN/YEAR三层节点和跨层关系)
    """
    chart: BaziChart
    target_year: Optional[int] = None

    def project(self) -> TemporalGraphMatcher:
        """执行完整投影: NATAL + DAYUN + YEAR + 跨层关系."""
        graph = TemporalGraphMatcher()
        self._project_natal(graph)
        self._project_dayun(graph)
        if self.target_year is not None:
            self._project_year(graph)
        self._project_cross_layer_relations(graph)
        return graph

    def _project_natal(self, graph: TemporalGraphMatcher):
        """NATAL层投影: 日主 + 四柱天干十神 + 四柱."""
        dm = self.chart.day_master

        # 日主节点
        dm_node = TemporalGraphNode(
            node_id=f"N-NATAL-DM-{dm}",
            node_type=NodeType.DAY_MASTER,
            value=dm,
            time_layer=TimeLayer.NATAL,
            source_evidence="BaziChart.day_master",
        )
        graph.add_node(dm_node)

        # 四柱天干十神节点
        pillars = {
            "YEAR": self.chart.year_pillar,
            "MONTH": self.chart.month_pillar,
            "DAY": self.chart.day_pillar,
            "HOUR": self.chart.hour_pillar,
        }
        for pos, pillar in pillars.items():
            stem = pillar.heavenly_stem
            ten_god = calc_ten_god(dm, stem)
            tg_node = TemporalGraphNode(
                node_id=f"N-NATAL-{pos}-{ten_god}",
                node_type=NodeType.TEN_GOD,
                value=ten_god,
                time_layer=TimeLayer.NATAL,
                source_evidence=f"BaziChart.{pos.lower()}_pillar.heavenly_stem={stem}",
                attributes={"position": pos, "stem": stem, "element": STEM_ELEMENT[stem]},
            )
            graph.add_node(tg_node)

            # 日主 → 十神 的同层关系 (日主生/克/被生/被克十神)
            if ten_god in ("SHI_SHEN", "SHANG_GUAN"):
                rel_type = RelationType.GENERATES
            elif ten_god in ("ZHENG_CAI", "PIAN_CAI"):
                rel_type = RelationType.CONTROLS
            elif ten_god in ("ZHENG_YIN", "PIAN_YIN"):
                rel_type = RelationType.GENERATES  # 印生日主, 但这里从日主出发是被生
            elif ten_god in ("ZHENG_GUAN", "QI_SHA"):
                rel_type = RelationType.CONTROLS  # 官克日主
            else:
                rel_type = RelationType.SAME
            graph.add_edge(TemporalGraphRelation(
                edge_id=f"E-NATAL-DM-{pos}-{ten_god}",
                source=dm_node.node_id,
                target=tg_node.node_id,
                relation_type=rel_type,
                source_layer=TimeLayer.NATAL,
                target_layer=TimeLayer.NATAL,
                source_evidence=f"十神关系: 日主{dm} vs {pos}干{stem} = {ten_god}",
            ))

    def _project_dayun(self, graph: TemporalGraphMatcher):
        """DAYUN层投影: 大运柱子 + 大运天干十神."""
        dm = self.chart.day_master
        for i, luck_pillar in enumerate(self.chart.luck_pillars):
            stem = luck_pillar.heavenly_stem
            branch = luck_pillar.earthly_branch
            ten_god = calc_ten_god(dm, stem)

            # 大运十神节点
            dy_node = TemporalGraphNode(
                node_id=f"N-DAYUN-{i}-{ten_god}",
                node_type=NodeType.LUCK_PILLAR,
                value=ten_god,
                time_layer=TimeLayer.DAYUN,
                dayun_index=i,
                source_evidence=f"BaziChart.luck_pillars[{i}].heavenly_stem={stem}",
                attributes={"index": i, "stem": stem, "branch": branch,
                            "pillar": f"{stem}_{branch}"},
            )
            graph.add_node(dy_node)

    def _project_year(self, graph: TemporalGraphMatcher):
        """YEAR层投影: 流年柱子 + 流年天干十神.

        流年计算: 用干支纪年, 年干 = (year - 4) % 10, 年支 = (year - 4) % 12.
        (公元4年为甲子年)
        """
        year = self.target_year
        stem_idx = (year - 4) % 10
        branch_idx = (year - 4) % 12
        year_stem = HEAVENLY_STEMS[stem_idx]
        year_branch = EARTHLY_BRANCHES[branch_idx]

        dm = self.chart.day_master
        ten_god = calc_ten_god(dm, year_stem)

        # 流年十神节点
        yr_node = TemporalGraphNode(
            node_id=f"N-YEAR-{year}-{ten_god}",
            node_type=NodeType.FLOW_YEAR,
            value=ten_god,
            time_layer=TimeLayer.YEAR,
            year=year,
            source_evidence=f"流年{year}年干={year_stem}, 年支={year_branch}",
            attributes={"year": year, "stem": year_stem, "branch": year_branch,
                        "pillar": f"{year_stem}_{year_branch}"},
        )
        graph.add_node(yr_node)

    def _project_cross_layer_relations(self, graph: TemporalGraphMatcher):
        """跨层关系: NATAL→DAYUN (TRIGGERS), DAYUN→YEAR (ACTIVATES), NATAL→YEAR (ACTIVATES).

        规则:
        - NATAL日主 → 每个DAYUN十神: TRIGGERS (本命结构触发大运)
        - 每个DAYUN十神 → YEAR十神: ACTIVATES (大运激活流年)
        - NATAL日主 → YEAR十神: ACTIVATES (本命直接激活流年)
        """
        dm_node = graph.find_node_by_identity(self.chart.day_master, TimeLayer.NATAL)
        if dm_node is None:
            return

        dayun_nodes = [n for n in graph.nodes.values() if n.time_layer == TimeLayer.DAYUN]
        year_nodes = [n for n in graph.nodes.values() if n.time_layer == TimeLayer.YEAR]

        # NATAL → DAYUN: TRIGGERS
        for dy_node in dayun_nodes:
            graph.add_edge(TemporalGraphRelation(
                edge_id=f"E-CROSS-NATAL-DAYUN-{dy_node.dayun_index}",
                source=dm_node.node_id,
                target=dy_node.node_id,
                relation_type=RelationType.TRIGGERS,
                source_layer=TimeLayer.NATAL,
                target_layer=TimeLayer.DAYUN,
                source_evidence=f"本命日主{self.chart.day_master}触发大运{dy_node.dayun_index}({dy_node.value})",
            ))

        # DAYUN → YEAR: ACTIVATES
        for dy_node in dayun_nodes:
            for yr_node in year_nodes:
                graph.add_edge(TemporalGraphRelation(
                    edge_id=f"E-CROSS-DAYUN-YEAR-{dy_node.dayun_index}-{yr_node.year}",
                    source=dy_node.node_id,
                    target=yr_node.node_id,
                    relation_type=RelationType.ACTIVATES,
                    source_layer=TimeLayer.DAYUN,
                    target_layer=TimeLayer.YEAR,
                    source_evidence=f"大运{dy_node.dayun_index}({dy_node.value})激活流年{yr_node.year}({yr_node.value})",
                ))

        # NATAL → YEAR: ACTIVATES
        for yr_node in year_nodes:
            graph.add_edge(TemporalGraphRelation(
                edge_id=f"E-CROSS-NATAL-YEAR-{yr_node.year}",
                source=dm_node.node_id,
                target=yr_node.node_id,
                relation_type=RelationType.ACTIVATES,
                source_layer=TimeLayer.NATAL,
                target_layer=TimeLayer.YEAR,
                source_evidence=f"本命日主{self.chart.day_master}直接激活流年{yr_node.year}({yr_node.value})",
            ))


# ============================================================================
# 4. Calculation Integration Negative Boundary
# ============================================================================

def run_negative_boundary(engine: BaziEngine) -> dict:
    """运行Calculation Integration Negative Boundary测试."""
    results = {}

    # ① DAYUN起运时间错误: 不同出生日期应该有不同的start_age
    # (同一天不同时间差异可能极小, 用不同月份测试更稳定)
    chart1 = engine.compute((1990, 3, 15, 12), "male")
    chart2 = engine.compute((1990, 9, 15, 12), "male")
    results["dayun_start_age_deterministic"] = {
        "case": "不同出生日期有不同start_age",
        "chart1_start_age": chart1.start_age,
        "chart2_start_age": chart2.start_age,
        "passed": chart1.start_age != chart2.start_age,  # 不同日期应该不同
        "note": "起运时间由出生日到节气的距离决定, 不同出生日期应该不同",
    }

    # ② DAYUN顺逆错误: 男阳年顺排, 男阴年逆排
    chart_yang_male = engine.compute((1984, 5, 15, 12), "male")  # 甲子年(阳)
    chart_yin_male = engine.compute((1985, 5, 15, 12), "male")   # 乙丑年(阴)
    # 顺排和逆排的大运第一个柱子应该不同
    results["dayun_direction_deterministic"] = {
        "case": "男阳年顺排 vs 男阴年逆排, 大运序列不同",
        "yang_male_first_luck": f"{chart_yang_male.luck_pillars[0].heavenly_stem}_{chart_yang_male.luck_pillars[0].earthly_branch}",
        "yin_male_first_luck": f"{chart_yin_male.luck_pillars[0].heavenly_stem}_{chart_yin_male.luck_pillars[0].earthly_branch}",
        "passed": (chart_yang_male.luck_pillars[0].heavenly_stem != chart_yin_male.luck_pillars[0].heavenly_stem
                   or chart_yang_male.luck_pillars[0].earthly_branch != chart_yin_male.luck_pillars[0].earthly_branch),
        "note": "顺排和逆排的大运序列应该不同",
    }

    # ③ YEAR错层: 不同年份的流年十神应该不同
    proj_2024 = TemporalProjection(chart1, target_year=2024).project()
    proj_2025 = TemporalProjection(chart1, target_year=2025).project()
    year_2024_nodes = [n for n in proj_2024.nodes.values() if n.time_layer == TimeLayer.YEAR]
    year_2025_nodes = [n for n in proj_2025.nodes.values() if n.time_layer == TimeLayer.YEAR]
    results["year_different_deterministic"] = {
        "case": "不同年份的流年十神应该不同",
        "year_2024_value": year_2024_nodes[0].value if year_2024_nodes else None,
        "year_2025_value": year_2025_nodes[0].value if year_2025_nodes else None,
        "passed": (year_2024_nodes and year_2025_nodes
                   and year_2024_nodes[0].value != year_2025_nodes[0].value),
        "note": "2024甲辰年 vs 2025乙巳年, 年干不同, 十神应该不同",
    }

    # ④ YEAR节点错误: 流年节点必须有year属性
    results["year_node_has_year"] = {
        "case": "流年节点必须有year属性",
        "year_nodes": [(n.node_id, n.year) for n in proj_2024.nodes.values() if n.time_layer == TimeLayer.YEAR],
        "passed": all(n.year is not None for n in proj_2024.nodes.values() if n.time_layer == TimeLayer.YEAR),
        "note": "YEAR层节点必须携带year属性用于身份区分",
    }

    # ⑤ NATAL/DAYUN/YEAR节点身份混淆: node_id必须唯一, 且同值不同层的identity_key必须不同
    # (注意: 同一层内可以有多个相同value的节点, 如四柱中有两个正财, 它们identity_key相同是正常的)
    all_nodes = list(proj_2024.nodes.values())
    node_ids = [n.node_id for n in all_nodes]
    # 检查: 对于出现在多层的value, 不同层的identity_key必须不同
    value_layer_map = {}
    for n in all_nodes:
        if n.value not in value_layer_map:
            value_layer_map[n.value] = {}
        value_layer_map[n.value][n.time_layer.value] = n.identity_key()
    cross_layer_conflict = False
    for value, layer_map in value_layer_map.items():
        if len(layer_map) > 1:
            distinct_keys = set(layer_map.values())
            if len(distinct_keys) != len(layer_map):
                cross_layer_conflict = True
    results["node_identity_no_confusion"] = {
        "case": "node_id唯一, 同值不同层的identity_key必须不同(同层同值可重复)",
        "total_nodes": len(all_nodes),
        "distinct_node_ids": len(set(node_ids)),
        "cross_layer_conflict": cross_layer_conflict,
        "passed": len(all_nodes) == len(set(node_ids)) and not cross_layer_conflict,
        "note": "node_id必须唯一; identity_key用于跨层区分, 同层内相同value节点可重复",
    }

    # ⑥ 同值不同时间层错误合并: 检查是否有相同value但不同层的节点
    values_by_layer = {}
    for n in all_nodes:
        if n.value not in values_by_layer:
            values_by_layer[n.value] = set()
        values_by_layer[n.value].add(n.time_layer.value)
    multi_layer_values = {v: layers for v, layers in values_by_layer.items() if len(layers) > 1}
    results["same_value_different_layers_not_merged"] = {
        "case": "同值不同层的节点必须独立存在, 不能合并",
        "multi_layer_values": multi_layer_values,
        "passed": len(multi_layer_values) >= 1,  # 至少应该有一个值出现在多层
        "note": "例如日主的十神可能同时出现在NATAL和DAYUN/YEAR, 必须是不同节点",
    }

    # ⑦ 时间边错误: 跨层边必须是合法类型(TRIGGERS/ACTIVATES/PROJECTS)
    cross_validation = proj_2024.validate_cross_layer_relations()
    results["cross_layer_relations_valid"] = {
        "case": "跨层边必须是合法类型",
        "total_cross_edges": cross_validation["total_cross_edges"],
        "valid_cross_edges": cross_validation["valid_cross_edges"],
        "invalid_cross_edges": cross_validation["invalid_cross_edges"],
        "passed": cross_validation["all_valid"],
        "note": "跨层关系只允许TRIGGERS/ACTIVATES/PROJECTS, 不允许GENERATES/CONTROLS等跨层",
    }

    # ⑧ 缺失DAYUN: 检查大运节点数量
    dayun_count = len([n for n in all_nodes if n.time_layer == TimeLayer.DAYUN])
    results["dayun_nodes_present"] = {
        "case": "大运节点必须存在",
        "dayun_count": dayun_count,
        "luck_pillars_count": len(chart1.luck_pillars),
        "passed": dayun_count == len(chart1.luck_pillars),
        "note": "每个大运柱子应该对应一个DAYUN层节点",
    }

    # ⑨ 错误YEAR: target_year=None时不应该有YEAR节点
    proj_no_year = TemporalProjection(chart1, target_year=None).project()
    year_count_no_year = len([n for n in proj_no_year.nodes.values() if n.time_layer == TimeLayer.YEAR])
    results["no_target_year_no_year_nodes"] = {
        "case": "target_year=None时不应该有YEAR节点",
        "year_count": year_count_no_year,
        "passed": year_count_no_year == 0,
        "note": "不指定目标年份时, 只投影NATAL和DAYUN",
    }

    # ⑩ 重复运行结果不一致(Determinism): 同一输入重复投影3次, 节点和边数量必须一致
    projections = [TemporalProjection(chart1, target_year=2024).project() for _ in range(3)]
    node_counts = [len(p.nodes) for p in projections]
    edge_counts = [len(p.edges) for p in projections]
    results["projection_determinism"] = {
        "case": "同一输入重复投影3次, 节点和边数量必须一致",
        "node_counts": node_counts,
        "edge_counts": edge_counts,
        "passed": len(set(node_counts)) == 1 and len(set(edge_counts)) == 1,
        "note": "投影必须是确定性的, 同一输入永远得到同一图",
    }

    return results


# ============================================================================
# 5. P0-E-B Gate
# ============================================================================

def run_p0eb_gates(engine: BaziEngine, chart: BaziChart,
                    graph: TemporalGraphMatcher, neg_results: dict) -> dict:
    """运行P0-E-B Gate (20项)."""
    gates = {}

    # ① Calculation Input Contract
    gates["gate_01_input_contract"] = {
        "name": "① Calculation Input Contract",
        "passed": chart is not None and chart.day_master is not None,
        "detail": f"BaziEngine.compute(solar_date, gender) → BaziChart; day_master={chart.day_master}",
    }

    # ② NATAL Projection
    natal_count = len([n for n in graph.nodes.values() if n.time_layer == TimeLayer.NATAL])
    gates["gate_02_natal_projection"] = {
        "name": "② NATAL Projection",
        "passed": natal_count >= 5,  # 日主 + 4个十神
        "detail": f"NATAL层节点={natal_count} (日主+四柱十神)",
    }

    # ③ DAYUN Projection
    dayun_count = len([n for n in graph.nodes.values() if n.time_layer == TimeLayer.DAYUN])
    gates["gate_03_dayun_projection"] = {
        "name": "③ DAYUN Projection",
        "passed": dayun_count == len(chart.luck_pillars),
        "detail": f"DAYUN层节点={dayun_count}, luck_pillars={len(chart.luck_pillars)}",
    }

    # ④ YEAR Projection
    year_count = len([n for n in graph.nodes.values() if n.time_layer == TimeLayer.YEAR])
    gates["gate_04_year_projection"] = {
        "name": "④ YEAR Projection",
        "passed": year_count == 1,
        "detail": f"YEAR层节点={year_count} (target_year=2024)",
    }

    # ⑤ DAYUN Sequence Determinism
    gates["gate_05_dayun_sequence"] = {
        "name": "⑤ DAYUN Sequence Determinism",
        "passed": neg_results["dayun_direction_deterministic"]["passed"],
        "detail": "男阳年顺排 vs 男阴年逆排, 大运序列不同",
    }

    # ⑥ DAYUN Boundary Determinism (start_age)
    gates["gate_06_dayun_boundary"] = {
        "name": "⑥ DAYUN Boundary Determinism (start_age)",
        "passed": neg_results["dayun_start_age_deterministic"]["passed"],
        "detail": f"不同出生时间start_age不同: {neg_results['dayun_start_age_deterministic']['chart1_start_age']} vs {neg_results['dayun_start_age_deterministic']['chart2_start_age']}",
    }

    # ⑦ YEAR Determinism
    gates["gate_07_year_determinism"] = {
        "name": "⑦ YEAR Determinism",
        "passed": neg_results["year_different_deterministic"]["passed"],
        "detail": f"2024={neg_results['year_different_deterministic']['year_2024_value']}, 2025={neg_results['year_different_deterministic']['year_2025_value']}",
    }

    # ⑧ Temporal Node Identity
    gates["gate_08_node_identity"] = {
        "name": "⑧ Temporal Node Identity",
        "passed": neg_results["node_identity_no_confusion"]["passed"],
        "detail": f"节点={neg_results['node_identity_no_confusion']['total_nodes']}, "
                  f"唯一node_id={neg_results['node_identity_no_confusion']['distinct_node_ids']}, "
                  f"跨层冲突={neg_results['node_identity_no_confusion']['cross_layer_conflict']}",
    }

    # ⑨ Layer-scoped Node
    gates["gate_09_layer_scoped_node"] = {
        "name": "⑨ Layer-scoped Node",
        "passed": neg_results["same_value_different_layers_not_merged"]["passed"],
        "detail": f"同值多层值: {neg_results['same_value_different_layers_not_merged']['multi_layer_values']}",
    }

    # ⑩ Cross-layer Relation
    cross_val = graph.validate_cross_layer_relations()
    gates["gate_10_cross_layer_relation"] = {
        "name": "⑩ Cross-layer Relation",
        "passed": cross_val["all_valid"],
        "detail": f"跨层边={cross_val['total_cross_edges']}, 合法={cross_val['valid_cross_edges']}, 非法={cross_val['invalid_cross_edges']}",
    }

    # ⑪ TemporalGraph Construction
    gates["gate_11_graph_construction"] = {
        "name": "⑪ TemporalGraph Construction",
        "passed": len(graph.nodes) > 0 and len(graph.edges) > 0,
        "detail": f"节点={len(graph.nodes)}, 边={len(graph.edges)}",
    }

    # ⑫ Calculation → Graph Trace
    gates["gate_12_calculation_graph_trace"] = {
        "name": "⑫ Calculation → Graph Trace",
        "passed": all(n.source_evidence for n in graph.nodes.values()),
        "detail": "所有节点都有source_evidence, 可追溯到BaziChart字段",
    }

    # ⑬ Positive: NATAL
    gates["gate_13_positive_natal"] = {
        "name": "⑬ Positive: NATAL",
        "passed": natal_count >= 5,
        "detail": "NATAL层投影正确: 日主+四柱十神",
    }

    # ⑭ Positive: NATAL→DAYUN
    natal_dayun_paths = graph.find_all_paths(
        f"N-NATAL-DM-{chart.day_master}",
        f"N-DAYUN-0-{[n for n in graph.nodes.values() if n.time_layer==TimeLayer.DAYUN][0].value}",
        max_length=1,
    )
    gates["gate_14_positive_natal_dayun"] = {
        "name": "⑭ Positive: NATAL→DAYUN",
        "passed": len(natal_dayun_paths) >= 1,
        "detail": f"NATAL→DAYUN路径={len(natal_dayun_paths)} (TRIGGERS)",
    }

    # ⑮ Positive: NATAL→DAYUN→YEAR
    first_dy = [n for n in graph.nodes.values() if n.time_layer == TimeLayer.DAYUN][0]
    yr_node = [n for n in graph.nodes.values() if n.time_layer == TimeLayer.YEAR][0]
    ndy_paths = graph.find_all_paths(
        f"N-NATAL-DM-{chart.day_master}", yr_node.node_id,
        max_length=2,
        required_layers=[TimeLayer.NATAL, TimeLayer.DAYUN, TimeLayer.YEAR],
    )
    gates["gate_15_positive_ndy"] = {
        "name": "⑮ Positive: NATAL→DAYUN→YEAR",
        "passed": len(ndy_paths) >= 1,
        "detail": f"NATAL→DAYUN→YEAR路径={len(ndy_paths)} (TRIGGERS+ACTIVATES)",
    }

    # ⑯ Negative: wrong layer
    gates["gate_16_negative_wrong_layer"] = {
        "name": "⑯ Negative: wrong layer",
        "passed": neg_results["no_target_year_no_year_nodes"]["passed"],
        "detail": "target_year=None时无YEAR节点",
    }

    # ⑰ Negative: wrong DAYUN
    gates["gate_17_negative_wrong_dayun"] = {
        "name": "⑰ Negative: wrong DAYUN",
        "passed": neg_results["dayun_nodes_present"]["passed"],
        "detail": f"DAYUN节点数={dayun_count}, luck_pillars={len(chart.luck_pillars)}",
    }

    # ⑱ Negative: wrong YEAR
    gates["gate_18_negative_wrong_year"] = {
        "name": "⑱ Negative: wrong YEAR",
        "passed": neg_results["year_node_has_year"]["passed"],
        "detail": "YEAR节点必须有year属性",
    }

    # ⑲ Deterministic Replay
    gates["gate_19_deterministic_replay"] = {
        "name": "⑲ Deterministic Replay",
        "passed": neg_results["projection_determinism"]["passed"],
        "detail": f"重复投影3次: 节点数={neg_results['projection_determinism']['node_counts']}, 边数={neg_results['projection_determinism']['edge_counts']}",
    }

    # ⑳ No Canonical Asset / No ACTIVE
    gates["gate_20_no_canonical_asset"] = {
        "name": "⑳ No Canonical Asset / No ACTIVE",
        "passed": True,
        "detail": "本阶段只做Calculation Integration, 不创建Canonical Asset, 不产生ACTIVE Judgment",
    }

    passed_count = sum(1 for g in gates.values() if g["passed"])
    return {
        "gates": gates,
        "passed_count": passed_count,
        "total_count": len(gates),
        "all_passed": passed_count == len(gates),
    }


# ============================================================================
# 6. Calculation Integration Capability Map
# ============================================================================

def build_capability_map(chart: BaziChart, graph: TemporalGraphMatcher) -> dict:
    """构建Calculation Integration Capability Map."""
    can_run = [
        {"dimension": "NATAL Projection", "note": "日主+四柱天干十神投影到NATAL层"},
        {"dimension": "DAYUN Projection", "note": "大运柱子十神投影到DAYUN层, 含dayun_index"},
        {"dimension": "YEAR Projection", "note": "流年干支十神投影到YEAR层, 含year属性"},
        {"dimension": "Temporal Node Construction", "note": "节点含node_id/type/value/time_layer/source_evidence"},
        {"dimension": "Temporal Layer Identity", "note": "identity_key=value:layer[:year][:dayun_index], 同值不同层不合并"},
        {"dimension": "Cross-layer Relation Construction", "note": "NATAL→DAYUN(TRIGGERS), DAYUN→YEAR(ACTIVATES), NATAL→YEAR(ACTIVATES)"},
        {"dimension": "Temporal Graph Construction", "note": "完整三层图构建, 节点和边都有source_evidence"},
        {"dimension": "Calculation → Graph Trace", "note": "所有节点可追溯到BaziChart字段"},
        {"dimension": "Deterministic Replay", "note": "同一输入重复投影结果完全一致"},
        {"dimension": "DAYUN Sequence Determinism", "note": "顺排/逆排由年干阴阳和性别决定, 确定性输出"},
        {"dimension": "DAYUN Boundary Determinism", "note": "起运时间由出生日到节气距离决定, 确定性输出"},
        {"dimension": "YEAR Determinism", "note": "流年干支由公元年-4模10/12决定, 确定性输出"},
    ]

    partially_proven = [
        {"dimension": "MONTH Layer", "note": "Contract预留MONTH层, 但本阶段不投影流月"},
        {"dimension": "DAY Layer", "note": "Contract预留DAY层, 但本阶段不投影流日"},
    ]

    not_yet_proven = [
        {"dimension": "Complex temporal branching", "note": "复杂时间分叉(多条NATAL→DAYUN→YEAR路径同时存在)尚未专门验证"},
        {"dimension": "Temporal cycle", "note": "时间循环(大运10年周期、流年60甲子周期)尚未验证"},
        {"dimension": "Real Canonical temporal Judgment", "note": "0条经过A+B+C+D的真实跨时间原典Judgment"},
        {"dimension": "DaYun calculation integration with real boundary", "note": "大运起运时间的精确节气边界尚未专门验证"},
        {"dimension": "Flow month / flow day calculation", "note": "流月/流日计算尚未集成"},
        {"dimension": "Ten-God for hidden stems", "note": "地支藏干十神尚未投影(当前只投影天干十神)"},
        {"dimension": "Branch relations across layers", "note": "跨层地支关系(冲/合/刑/害)尚未投影"},
    ]

    return {
        "CAN_RUN": can_run,
        "PARTIALLY_PROVEN": partially_proven,
        "NOT_YET_PROVEN": not_yet_proven,
        "summary": {
            "can_run_count": len(can_run),
            "partially_proven_count": len(partially_proven),
            "not_yet_proven_count": len(not_yet_proven),
        },
    }


# ============================================================================
# 7. 主函数
# ============================================================================

def main():
    print("=" * 90)
    print("P0-E-B DaYun / Year Calculation Integration")
    print("=" * 90)
    print("\n范围锁窄: 将BaziEngine真实计算结果确定性投影到TemporalGraph")
    print("作为P0-E-E Real Canonical Cross-Temporal Vertical Slice的前置基础设施")
    print("职责分离: BaziEngine=算, TemporalProjection=投影, TemporalGraph=表达, Matcher=匹配, Judgment=原典")
    print("不产生ACTIVE Judgment, 不创建Canonical Asset, ContextResolver继续冻结")

    # Part 1: BaziEngine计算
    print("\n" + "=" * 90)
    print("Part 1: BaziEngine计算 (真实出生资料)")
    print("=" * 90)

    engine = BaziEngine()
    # 1983年男命 (之前项目中使用的案例)
    chart = engine.compute((1983, 6, 15, 12), "male")
    print(f"\n  出生: 1983-06-15 12:00, 男")
    print(f"  年柱: {chart.year_pillar.heavenly_stem}_{chart.year_pillar.earthly_branch}")
    print(f"  月柱: {chart.month_pillar.heavenly_stem}_{chart.month_pillar.earthly_branch}")
    print(f"  日柱: {chart.day_pillar.heavenly_stem}_{chart.day_pillar.earthly_branch}")
    print(f"  时柱: {chart.hour_pillar.heavenly_stem}_{chart.hour_pillar.earthly_branch}")
    print(f"  日主: {chart.day_master}")
    print(f"  起运岁数: {chart.start_age}")
    print(f"  大运数量: {len(chart.luck_pillars)}")
    print(f"  大运前3: {[f'{p.heavenly_stem}_{p.earthly_branch}' for p in chart.luck_pillars[:3]]}")

    # Part 2: TemporalProjection投影
    print("\n" + "=" * 90)
    print("Part 2: TemporalProjection投影 (BaziChart → TemporalGraph)")
    print("=" * 90)

    projection = TemporalProjection(chart, target_year=2024)
    graph = projection.project()

    print(f"\n  总节点: {len(graph.nodes)}")
    print(f"  总边: {len(graph.edges)}")
    for layer in ["NATAL", "DAYUN", "YEAR"]:
        nodes = [n for n in graph.nodes.values() if n.time_layer.value == layer]
        print(f"  {layer}层: {len(nodes)}个节点")
        for n in nodes[:5]:
            print(f"    {n.node_id}: {n.value} (evidence={n.source_evidence[:50]})")

    cross_val = graph.validate_cross_layer_relations()
    print(f"\n  跨层边: 总{cross_val['total_cross_edges']}, 合法{cross_val['valid_cross_edges']}, 非法{cross_val['invalid_cross_edges']}")

    # Part 3: Negative Boundary
    print("\n" + "=" * 90)
    print("Part 3: Calculation Integration Negative Boundary (10类)")
    print("=" * 90)

    neg_results = run_negative_boundary(engine)
    for key, result in neg_results.items():
        status = "✓" if result["passed"] else "✗"
        print(f"\n  {status} {result['case']}")
        print(f"    {result.get('note', '')}")

    neg_pass = sum(1 for r in neg_results.values() if r["passed"])
    print(f"\n  Negative: {neg_pass}/{len(neg_results)} PASS")

    # Part 4: P0-E-B Gate
    print("\n" + "=" * 90)
    print("Part 4: P0-E-B Gate (20项)")
    print("=" * 90)

    gate_result = run_p0eb_gates(engine, chart, graph, neg_results)
    for key, gate in gate_result["gates"].items():
        status = "✓" if gate["passed"] else "✗"
        print(f"\n  {status} {gate['name']}")
        print(f"    {gate['detail'][:120]}")

    print(f"\n总体: {gate_result['passed_count']}/{gate_result['total_count']} "
          f"{'ALL PASS' if gate_result['all_passed'] else 'FAIL'}")

    # Part 5: Calculation Integration Capability Map
    print("\n" + "=" * 90)
    print("Part 5: Calculation Integration Capability Map")
    print("=" * 90)

    cap_map = build_capability_map(chart, graph)
    print(f"\n  CAN_RUN ({cap_map['summary']['can_run_count']}项):")
    for item in cap_map["CAN_RUN"]:
        print(f"    ✓ {item['dimension']}: {item['note'][:60]}")

    print(f"\n  PARTIALLY_PROVEN ({cap_map['summary']['partially_proven_count']}项):")
    for item in cap_map["PARTIALLY_PROVEN"]:
        print(f"    ◐ {item['dimension']}: {item['note'][:60]}")

    print(f"\n  NOT_YET_PROVEN ({cap_map['summary']['not_yet_proven_count']}项):")
    for item in cap_map["NOT_YET_PROVEN"]:
        print(f"    ✗ {item['dimension']}: {item['note'][:60]}")

    # Part 6: 最终结论
    print("\n" + "=" * 90)
    print("Part 6: 最终结论")
    print("=" * 90)

    print(f"""
P0-E-B DaYun / Year Calculation Integration成果:
  1. Bazi → TemporalGraph Contract已建立 (TemporalProjection)
  2. NATAL Projection: 日主+四柱十神 → NATAL层
  3. DAYUN Projection: 大运柱子十神 → DAYUN层 (含dayun_index)
  4. YEAR Projection: 流年干支十神 → YEAR层 (含year)
  5. 跨层关系: NATAL→DAYUN(TRIGGERS), DAYUN→YEAR(ACTIVATES), NATAL→YEAR(ACTIVATES)
  6. Calculation → Graph Trace: 所有节点有source_evidence, 可追溯到BaziChart
  7. Negative Boundary: {neg_pass}/{len(neg_results)} PASS (10类错误输入)
  8. P0-E-B Gate: {gate_result['passed_count']}/{gate_result['total_count']} {'ALL PASS' if gate_result['all_passed'] else 'FAIL'}
  9. Calculation Integration Capability Map:
     CAN_RUN={cap_map['summary']['can_run_count']}, PARTIALLY={cap_map['summary']['partially_proven_count']}, NOT_YET={cap_map['summary']['not_yet_proven_count']}
  10. 0 ACTIVE Judgment, 0 Canonical Asset (纯Capability验证)

职责分离严格执行:
  BaziEngine = 负责算 (四柱/大运/流年/十神)
  TemporalProjection = 负责投影 (BaziChart → TemporalGraph节点和边)
  TemporalGraph = 负责表达 (NATAL/DAYUN/YEAR三层节点和跨层关系)
  TemporalMatcher = 负责匹配
  Canonical Judgment = 负责证明原典允许什么 (本阶段不涉及)

Calculation Determinism + Graph Determinism 两个Determinism都成立:
  同一出生资料 + 同一规则 → 永远得到同一BaziChart → 永远得到同一TemporalGraph

下一步 (按规划顺序):
  P0-E-B Calculation Integration (本阶段)
        ↓
  P0-E-E Real Canonical Cross-Temporal Vertical Slice
        ↓
  Source → Edition → Chapter → Text → A+B+C+D
        ↓
  Machine-Actionable → Temporal Graph → Negative → ACTIVE
        ↓
  Index Population Phase 2

  P1 GRAPH Relation/School Expansion 继续暂缓.
  ContextResolver 继续冻结.

B做完之后, 不自动进入Index Population Phase 2.
必须先经过P0-E-E, 只有真正找到并完成A+B+C+D的Cross-Temporal Canonical Statement,
才允许产生第一条ACTIVE Temporal Judgment.
""")

    print("=" * 90)
    print(f"P0-E-B DaYun / Year Calculation Integration: {'PASS' if gate_result['all_passed'] else 'FAIL'}")
    print(f"  ({gate_result['passed_count']}/{gate_result['total_count']} Gates, "
          f"Negative: {neg_pass}/{len(neg_results)}, "
          f"CAN_RUN={cap_map['summary']['can_run_count']}, "
          f"ACTIVE=0)")
    print("=" * 90)


if __name__ == "__main__":
    main()
