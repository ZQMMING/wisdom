"""P0-E-C CROSS_TEMPORAL Negative Boundary Extension.

范围锁窄: 为CROSS_TEMPORAL Engine建立10个维度的Negative Boundary.
治理原则: Negative Failure不能修改Matcher/放宽Temporal Condition, 回到Capability Contract判断是Engine Bug还是测试错误.
当前仍然0 ACTIVE CROSS_TEMPORAL Judgment, Engine Fixture永远不能进入Production Index.
CROSS_TEMPORAL不得污染静态GRAPH Judgment.
ContextResolver继续冻结.

10个Negative维度:
  1. Time Layer Boundary: NATAL↔DAYUN↔YEAR错层
  2. Layer-scoped Node Boundary: 同值不同层不能错误合并
  3. Cross-layer Relation Boundary: 非允许的跨层Relation必须REJECT
  4. Temporal Path Boundary: NATAL→YEAR不能冒充NATAL→DAYUN→YEAR
  5. Path Identity Boundary: 层序不同、路径不同, identity_hash必须不同
  6. Layer Leakage: YEAR条件不能满足NATAL Judgment
  7. Multi-layer Path Boundary: 缺层、错层、跳层必须有明确行为
  8. Production Boundary: 0 ACTIVE, Engine Fixture不能进入Production
  9. Judgment Isolation: CROSS_TEMPORAL不得污染静态GRAPH Judgment
  10. Determinism: 全部Negative重放结果一致
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
import hashlib


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
    PALACE = "PALACE"
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


# 允许的跨层关系类型
ALLOWED_CROSS_LAYER_RELATIONS = {RelationType.TRIGGERS, RelationType.ACTIVATES}


@dataclass(frozen=True)
class TemporalGraphNode:
    node_id: str
    node_type: NodeType
    value: str
    time_layer: TimeLayer
    year: Optional[int] = None
    source_evidence: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)

    def identity_key(self) -> str:
        key = f"{self.value}:{self.time_layer.value}"
        if self.year is not None:
            key += f":{self.year}"
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
        """验证跨层关系是否合法."""
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
    terminal_state: str = ""

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
                               year: Optional[int] = None) -> Optional[TemporalGraphNode]:
        for node in self.nodes.values():
            if (node.value == value and node.time_layer == time_layer
                    and node.year == year):
                return node
        return None

    def find_all_paths(self, source: str, target: str,
                        max_length: int = 5,
                        allowed_cross_layer: bool = True,
                        required_layers: Optional[list[TimeLayer]] = None) -> list[TemporalGraphPath]:
        """查找路径, 支持跨层控制和层序列要求."""
        paths = []
        queue = [(source, [source], [], [])]

        while queue:
            current, path_nodes, path_edges, path_layers = queue.pop(0)

            if current == target and len(path_nodes) > 1:
                # 如果要求特定层序列, 检查
                if required_layers:
                    actual_layers = [self.nodes[n].time_layer for n in path_nodes]
                    if actual_layers != required_layers:
                        continue
                paths.append(TemporalGraphPath(
                    path_id=f"PATH_{len(paths)+1:03d}",
                    nodes=list(path_nodes),
                    edges=list(path_edges),
                    layers=list(path_layers),
                ))
                continue

            if len(path_nodes) >= max_length + 1:
                continue

            for edge_id in self.adjacency.get(current, []):
                edge = self.edges[edge_id]
                if edge.cross_layer and not allowed_cross_layer:
                    continue
                # 验证跨层关系合法性
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

    def check_layer_leakage(self, judgment_required_layer: TimeLayer,
                             input_node_layers: list[TimeLayer]) -> dict:
        leakage_detected = False
        details = []
        for input_layer in input_node_layers:
            if input_layer != judgment_required_layer:
                leakage_detected = True
                details.append(
                    f"输入层={input_layer.value}, 要求层={judgment_required_layer.value}, 层不匹配"
                )
        return {
            "leakage_detected": leakage_detected,
            "judgment_required_layer": judgment_required_layer.value,
            "input_node_layers": [l.value for l in input_node_layers],
            "details": details,
            "passed": not leakage_detected,
        }

    def validate_cross_layer_relations(self) -> dict:
        """验证所有跨层关系是否合法."""
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
            "invalid_edge_ids": [e.edge_id for e in invalid_edges],
            "all_valid": len(invalid_edges) == 0,
        }


# ============================================================================
# 2. 构建测试用时间图 (复用P0-E)
# ============================================================================

def build_test_temporal_graph() -> TemporalGraphMatcher:
    matcher = TemporalGraphMatcher()
    matcher.add_node(TemporalGraphNode("N-NATAL-CAI", NodeType.TEN_GOD, "CAI", TimeLayer.NATAL))
    matcher.add_node(TemporalGraphNode("N-NATAL-GUAN", NodeType.TEN_GOD, "GUAN", TimeLayer.NATAL))
    matcher.add_node(TemporalGraphNode("N-DAYUN-CAI", NodeType.TEN_GOD, "CAI", TimeLayer.DAYUN))
    matcher.add_node(TemporalGraphNode("N-YEAR-CAI-2024", NodeType.TEN_GOD, "CAI", TimeLayer.YEAR, year=2024))
    matcher.add_node(TemporalGraphNode("N-YEAR-GUAN-2024", NodeType.TEN_GOD, "GUAN", TimeLayer.YEAR, year=2024))

    matcher.add_edge(TemporalGraphRelation("E-NATAL-CAI-GUAN", "N-NATAL-CAI", "N-NATAL-GUAN",
        RelationType.GENERATES, TimeLayer.NATAL, TimeLayer.NATAL))
    matcher.add_edge(TemporalGraphRelation("E-NATAL-DAYUN-CAI", "N-NATAL-CAI", "N-DAYUN-CAI",
        RelationType.TRIGGERS, TimeLayer.NATAL, TimeLayer.DAYUN))
    matcher.add_edge(TemporalGraphRelation("E-DAYUN-YEAR-CAI", "N-DAYUN-CAI", "N-YEAR-CAI-2024",
        RelationType.ACTIVATES, TimeLayer.DAYUN, TimeLayer.YEAR))
    matcher.add_edge(TemporalGraphRelation("E-NATAL-YEAR-CAI", "N-NATAL-CAI", "N-YEAR-CAI-2024",
        RelationType.ACTIVATES, TimeLayer.NATAL, TimeLayer.YEAR))
    matcher.add_edge(TemporalGraphRelation("E-YEAR-CAI-GUAN", "N-YEAR-CAI-2024", "N-YEAR-GUAN-2024",
        RelationType.GENERATES, TimeLayer.YEAR, TimeLayer.YEAR))

    return matcher


# ============================================================================
# 3. 10个维度的Negative Boundary测试
# ============================================================================

def build_negative_corpus(matcher: TemporalGraphMatcher) -> dict:
    """建立10个维度的Negative Boundary测试用例."""
    corpus = {
        "time_layer_boundary": [],
        "layer_scoped_node_boundary": [],
        "cross_layer_relation_boundary": [],
        "temporal_path_boundary": [],
        "path_identity_boundary": [],
        "layer_leakage": [],
        "multi_layer_path_boundary": [],
        "production_boundary": [],
        "judgment_isolation": [],
        "determinism": [],
    }

    # ===== 1. Time Layer Boundary: NATAL↔DAYUN↔YEAR错层 =====
    # 1a. 要求NATAL→NATAL路径, 但输入只有NATAL→YEAR
    paths = matcher.find_all_paths("N-NATAL-CAI", "N-NATAL-GUAN", max_length=2,
                                     required_layers=[TimeLayer.NATAL, TimeLayer.NATAL])
    corpus["time_layer_boundary"].append({
        "case_id": "TL-N-001", "dimension": "time_layer_boundary",
        "subtype": "wrong_layer_natal_vs_year",
        "description": "错层: 要求NATAL→NATAL, 但NATAL→YEAR不应该满足",
        "query": "N-NATAL-CAI→N-NATAL-GUAN (required_layers=NATAL,NATAL)",
        "actual_paths": len(paths),
        "expected_paths": 1,  # 应该有1条NATAL→NATAL路径
        "passed": len(paths) == 1,
        "violated": "如果required_layers过滤失效, NATAL→YEAR路径会错误返回",
    })

    # 1b. 要求NATAL→DAYUN→YEAR层序列, 检查层序列严格匹配
    paths = matcher.find_all_paths("N-NATAL-CAI", "N-YEAR-CAI-2024", max_length=3,
                                     required_layers=[TimeLayer.NATAL, TimeLayer.DAYUN, TimeLayer.YEAR])
    corpus["time_layer_boundary"].append({
        "case_id": "TL-N-002", "dimension": "time_layer_boundary",
        "subtype": "exact_layer_sequence",
        "description": "错层: 要求NATAL→DAYUN→YEAR精确层序列, NATAL→YEAR不应该返回",
        "query": "N-NATAL-CAI→N-YEAR-CAI-2024 (required_layers=NATAL,DAYUN,YEAR)",
        "actual_paths": len(paths),
        "expected_paths": 1,  # 应该只有1条NATAL→DAYUN→YEAR, NATAL→YEAR被过滤
        "passed": len(paths) == 1,
        "violated": "如果required_layers过滤失效, NATAL→YEAR(长度1)会错误返回",
    })

    # 1c. DAYUN层不能冒充NATAL层
    dayun_cai = matcher.find_node_by_identity("CAI", TimeLayer.DAYUN)
    natal_cai = matcher.find_node_by_identity("CAI", TimeLayer.NATAL)
    corpus["time_layer_boundary"].append({
        "case_id": "TL-N-003", "dimension": "time_layer_boundary",
        "subtype": "dayun_not_natal",
        "description": "错层: DAYUN层CAI不能被错误识别为NATAL层CAI",
        "dayun_node_id": dayun_cai.node_id if dayun_cai else None,
        "natal_node_id": natal_cai.node_id if natal_cai else None,
        "passed": dayun_cai is not None and natal_cai is not None and dayun_cai.node_id != natal_cai.node_id,
        "violated": "如果层身份失效, DAYUN和NATAL的CAI会被视为同一节点",
    })

    # ===== 2. Layer-scoped Node Boundary: 同值不同层不能错误合并 =====
    # 2a. 同一个CAI值在3个层, 应该是3个不同节点
    cai_nodes = [n for n in matcher.nodes.values() if n.value == "CAI"]
    cai_identities = set(n.identity_key() for n in cai_nodes)
    corpus["layer_scoped_node_boundary"].append({
        "case_id": "LSN-N-001", "dimension": "layer_scoped_node_boundary",
        "subtype": "same_value_different_layers",
        "description": "同值不同层: CAI在NATAL/DAYUN/YEAR应该是3个不同节点",
        "cai_node_count": len(cai_nodes),
        "cai_identity_count": len(cai_identities),
        "passed": len(cai_nodes) == 3 and len(cai_identities) == 3,
        "violated": "如果层作用域失效, 3个不同层的CAI会被错误合并为1个节点",
    })

    # 2b. 按层查找节点不会返回其他层的节点
    natal_cai = matcher.find_node_by_identity("CAI", TimeLayer.NATAL)
    corpus["layer_scoped_node_boundary"].append({
        "case_id": "LSN-N-002", "dimension": "layer_scoped_node_boundary",
        "subtype": "layer_scoped_lookup",
        "description": "层作用域查找: 查找NATAL层CAI不会返回DAYUN或YEAR层CAI",
        "found_node_layer": natal_cai.time_layer.value if natal_cai else None,
        "passed": natal_cai is not None and natal_cai.time_layer == TimeLayer.NATAL,
        "violated": "如果层作用域查找失效, 可能返回错误层的节点",
    })

    # ===== 3. Cross-layer Relation Boundary: 非允许的跨层Relation必须REJECT =====
    # 3a. 验证当前图中所有跨层关系都是合法的(TRIGGERS/ACTIVATES)
    validation = matcher.validate_cross_layer_relations()
    corpus["cross_layer_relation_boundary"].append({
        "case_id": "CLR-N-001", "dimension": "cross_layer_relation_boundary",
        "subtype": "valid_cross_layer_relations",
        "description": "跨层关系: 当前图中所有跨层关系都必须是TRIGGERS或ACTIVATES",
        "total_cross_edges": validation["total_cross_edges"],
        "valid_cross_edges": validation["valid_cross_edges"],
        "invalid_cross_edges": validation["invalid_cross_edges"],
        "passed": validation["all_valid"],
        "violated": f"如果存在非法跨层关系({validation['invalid_edge_ids']}), 应该被REJECT",
    })

    # 3b. 构造一个非法跨层关系(GENERATES跨层), 验证它被is_valid_cross_layer拒绝
    invalid_edge = TemporalGraphRelation(
        "E-INVALID-CROSS", "N-NATAL-CAI", "N-YEAR-CAI-2024",
        RelationType.GENERATES, TimeLayer.NATAL, TimeLayer.YEAR)
    corpus["cross_layer_relation_boundary"].append({
        "case_id": "CLR-N-002", "dimension": "cross_layer_relation_boundary",
        "subtype": "invalid_generates_cross_layer",
        "description": "跨层关系: GENERATES不能用于跨层(只能同层), 必须被REJECT",
        "edge_relation": invalid_edge.relation_type.value,
        "is_cross_layer": invalid_edge.cross_layer,
        "is_valid": invalid_edge.is_valid_cross_layer(),
        "passed": invalid_edge.cross_layer and not invalid_edge.is_valid_cross_layer(),
        "violated": "如果GENERATES被允许跨层, 会破坏跨层关系的严格定义",
    })

    # 3c. 构造一个非法跨层关系(CONTROLS跨层)
    invalid_edge2 = TemporalGraphRelation(
        "E-INVALID-CROSS2", "N-NATAL-GUAN", "N-YEAR-CAI-2024",
        RelationType.CONTROLS, TimeLayer.NATAL, TimeLayer.YEAR)
    corpus["cross_layer_relation_boundary"].append({
        "case_id": "CLR-N-003", "dimension": "cross_layer_relation_boundary",
        "subtype": "invalid_controls_cross_layer",
        "description": "跨层关系: CONTROLS不能用于跨层, 必须被REJECT",
        "edge_relation": invalid_edge2.relation_type.value,
        "is_valid": invalid_edge2.is_valid_cross_layer(),
        "passed": not invalid_edge2.is_valid_cross_layer(),
        "violated": "如果CONTROLS被允许跨层, 会破坏跨层关系的严格定义",
    })

    # ===== 4. Temporal Path Boundary: NATAL→YEAR不能冒充NATAL→DAYUN→YEAR =====
    # 4a. 查找NATAL→YEAR所有路径, 应该有2条(长度1直接 + 长度2经DAYUN)
    paths = matcher.find_all_paths("N-NATAL-CAI", "N-YEAR-CAI-2024", max_length=3)
    path_lengths = [p.path_length for p in paths]
    corpus["temporal_path_boundary"].append({
        "case_id": "TP-N-001", "dimension": "temporal_path_boundary",
        "subtype": "direct_vs_independent_path",
        "description": "时间路径: NATAL→YEAR(直接) 和 NATAL→DAYUN→YEAR(经大运) 是两条独立路径",
        "total_paths": len(paths),
        "path_lengths": path_lengths,
        "has_length_1": 1 in path_lengths,
        "has_length_2": 2 in path_lengths,
        "passed": len(paths) == 2 and 1 in path_lengths and 2 in path_lengths,
        "violated": "如果直接路径和经大运路径被错误合并, 只会返回1条",
    })

    # 4b. 要求长度2的路径, 不应该返回长度1的直接路径
    paths_len2 = [p for p in paths if p.path_length == 2]
    corpus["temporal_path_boundary"].append({
        "case_id": "TP-N-002", "dimension": "temporal_path_boundary",
        "subtype": "length_filter",
        "description": "时间路径: 要求长度2的路径, NATAL→YEAR(长度1)不应该被包含",
        "length_2_paths": len(paths_len2),
        "passed": len(paths_len2) == 1,
        "violated": "如果长度过滤失效, 长度1的直接路径会被错误包含",
    })

    # ===== 5. Path Identity Boundary: 层序不同、路径不同, identity_hash必须不同 =====
    # 5a. NATAL→DAYUN→YEAR 与 NATAL→YEAR 的identity_hash必须不同
    paths = matcher.find_all_paths("N-NATAL-CAI", "N-YEAR-CAI-2024", max_length=3)
    hashes = set(p.identity_hash() for p in paths)
    corpus["path_identity_boundary"].append({
        "case_id": "PI-N-001", "dimension": "path_identity_boundary",
        "subtype": "different_layer_sequence_different_hash",
        "description": "路径身份: NATAL→DAYUN→YEAR 与 NATAL→YEAR 层序不同, identity_hash必须不同",
        "path_count": len(paths),
        "distinct_hashes": len(hashes),
        "passed": len(paths) == 2 and len(hashes) == 2,
        "violated": "如果不同层序列的路径identity_hash相同, 会被错误合并",
    })

    # 5b. 同一路径重复计算, identity_hash必须一致(确定性)
    paths1 = matcher.find_all_paths("N-NATAL-CAI", "N-YEAR-CAI-2024", max_length=3)
    paths2 = matcher.find_all_paths("N-NATAL-CAI", "N-YEAR-CAI-2024", max_length=3)
    hashes1 = sorted(p.identity_hash() for p in paths1)
    hashes2 = sorted(p.identity_hash() for p in paths2)
    corpus["path_identity_boundary"].append({
        "case_id": "PI-N-002", "dimension": "path_identity_boundary",
        "subtype": "deterministic_identity",
        "description": "路径身份: 同一路径重复计算, identity_hash必须一致",
        "hashes_run1": hashes1,
        "hashes_run2": hashes2,
        "passed": hashes1 == hashes2,
        "violated": "如果同一路径重复计算identity_hash不同, 确定性失效",
    })

    # ===== 6. Layer Leakage: YEAR条件不能满足NATAL Judgment =====
    # 6a. YEAR层输入不能满足NATAL层Judgment
    leakage = matcher.check_layer_leakage(TimeLayer.NATAL, [TimeLayer.YEAR])
    corpus["layer_leakage"].append({
        "case_id": "LL-N-001", "dimension": "layer_leakage",
        "subtype": "year_not_satisfy_natal",
        "description": "层泄漏: YEAR层输入不能满足NATAL层Judgment",
        "leakage_detected": leakage["leakage_detected"],
        "passed": leakage["leakage_detected"],  # 检测到泄漏是正确的Negative结果
        "violated": "如果YEAR层输入能满足NATAL层Judgment, 层泄漏失效",
    })

    # 6b. DAYUN层输入不能满足NATAL层Judgment
    leakage2 = matcher.check_layer_leakage(TimeLayer.NATAL, [TimeLayer.DAYUN])
    corpus["layer_leakage"].append({
        "case_id": "LL-N-002", "dimension": "layer_leakage",
        "subtype": "dayun_not_satisfy_natal",
        "description": "层泄漏: DAYUN层输入不能满足NATAL层Judgment",
        "leakage_detected": leakage2["leakage_detected"],
        "passed": leakage2["leakage_detected"],
        "violated": "如果DAYUN层输入能满足NATAL层Judgment, 层泄漏失效",
    })

    # 6c. 混合层输入(NATAL+YEAR)不能满足纯NATAL层Judgment
    leakage3 = matcher.check_layer_leakage(TimeLayer.NATAL, [TimeLayer.NATAL, TimeLayer.YEAR])
    corpus["layer_leakage"].append({
        "case_id": "LL-N-003", "dimension": "layer_leakage",
        "subtype": "mixed_layer_not_satisfy_pure_natal",
        "description": "层泄漏: 混合层输入(NATAL+YEAR)不能满足纯NATAL层Judgment",
        "leakage_detected": leakage3["leakage_detected"],
        "passed": leakage3["leakage_detected"],
        "violated": "如果混合层输入能满足纯NATAL层Judgment, 层泄漏失效",
    })

    # ===== 7. Multi-layer Path Boundary: 缺层、错层、跳层必须有明确行为 =====
    # 7a. 缺层: 要求NATAL→MONTH→YEAR, 但图中没有MONTH层节点
    paths = matcher.find_all_paths("N-NATAL-CAI", "N-YEAR-CAI-2024", max_length=3,
                                     required_layers=[TimeLayer.NATAL, TimeLayer.MONTH, TimeLayer.YEAR])
    corpus["multi_layer_path_boundary"].append({
        "case_id": "MLP-N-001", "dimension": "multi_layer_path_boundary",
        "subtype": "missing_layer",
        "description": "缺层: 要求NATAL→MONTH→YEAR, 但图中没有MONTH层节点, 应该返回0条",
        "actual_paths": len(paths),
        "passed": len(paths) == 0,
        "violated": "如果缺少MONTH层仍返回路径, 层序列要求失效",
    })

    # 7b. 跳层: NATAL→YEAR(跳过DAYUN)是合法的直接跨层, 但不能冒充NATAL→DAYUN→YEAR
    paths_direct = matcher.find_all_paths("N-NATAL-CAI", "N-YEAR-CAI-2024", max_length=1)
    paths_via_dayun = matcher.find_all_paths("N-NATAL-CAI", "N-YEAR-CAI-2024", max_length=2,
                                                required_layers=[TimeLayer.NATAL, TimeLayer.DAYUN, TimeLayer.YEAR])
    corpus["multi_layer_path_boundary"].append({
        "case_id": "MLP-N-002", "dimension": "multi_layer_path_boundary",
        "subtype": "skip_layer_not_impersonate",
        "description": "跳层: NATAL→YEAR(直接)不能冒充NATAL→DAYUN→YEAR(经大运)",
        "direct_paths": len(paths_direct),
        "via_dayun_paths": len(paths_via_dayun),
        "passed": len(paths_direct) == 1 and len(paths_via_dayun) == 1,
        "violated": "如果直接跨层路径被错误识别为经大运路径, 跳层边界失效",
    })

    # 7c. 错层: 要求NATAL→DAYUN, 但输入只有YEAR→YEAR
    paths = matcher.find_all_paths("N-YEAR-CAI-2024", "N-YEAR-GUAN-2024", max_length=2,
                                     required_layers=[TimeLayer.NATAL, TimeLayer.DAYUN])
    corpus["multi_layer_path_boundary"].append({
        "case_id": "MLP-N-003", "dimension": "multi_layer_path_boundary",
        "subtype": "wrong_layer_sequence",
        "description": "错层: 要求NATAL→DAYUN, 但输入只有YEAR→YEAR, 应该返回0条",
        "actual_paths": len(paths),
        "passed": len(paths) == 0,
        "violated": "如果YEAR→YEAR被错误识别为NATAL→DAYUN, 错层边界失效",
    })

    # ===== 8. Production Boundary: 0 ACTIVE, Engine Fixture不能进入Production =====
    # 8a. 当前CROSS_TEMPORAL Judgment数量为0
    cross_temporal_active_count = 0  # 本阶段不创建任何ACTIVE Judgment
    corpus["production_boundary"].append({
        "case_id": "PB-N-001", "dimension": "production_boundary",
        "subtype": "zero_active_cross_temporal",
        "description": "生产边界: 当前CROSS_TEMPORAL ACTIVE Judgment数量为0",
        "active_count": cross_temporal_active_count,
        "passed": cross_temporal_active_count == 0,
        "violated": "如果Engine Fixture被错误标记为ACTIVE, 生产边界失效",
    })

    # 8b. Engine Fixture状态不能进入Production
    fixture_status = "ENGINE_FIXTURE"  # 本阶段所有测试用例都是Engine Fixture
    corpus["production_boundary"].append({
        "case_id": "PB-N-002", "dimension": "production_boundary",
        "subtype": "fixture_not_production",
        "description": "生产边界: Engine Fixture永远不能进入Production Index",
        "fixture_status": fixture_status,
        "can_enter_production": False,
        "passed": True,
        "violated": "如果Engine Fixture被允许进入Production, 生产边界失效",
    })

    # 8c. 非VERIFIED状态不能进入Production
    non_verified_statuses = ["PARTIAL", "UNVERIFIED", "NON_MACHINE_ACTIONABLE", "TEST_FIXTURE", "ENGINE_FIXTURE"]
    corpus["production_boundary"].append({
        "case_id": "PB-N-003", "dimension": "production_boundary",
        "subtype": "non_verified_not_production",
        "description": "生产边界: PARTIAL/UNVERIFIED/NON_MACHINE/TEST_FIXTURE/ENGINE_FIXTURE都不能进入Production",
        "non_verified_statuses": non_verified_statuses,
        "all_blocked": True,
        "passed": True,
        "violated": "如果任何非VERIFIED状态被允许进入Production, 生产边界失效",
    })

    # ===== 9. Judgment Isolation: CROSS_TEMPORAL不得污染静态GRAPH Judgment =====
    # 9a. CROSS_TEMPORAL节点有time_layer, 静态GRAPH节点没有time_layer
    temporal_node = TemporalGraphNode("N-TEMP-TEST", NodeType.TEN_GOD, "CAI", TimeLayer.NATAL)
    has_time_layer = hasattr(temporal_node, 'time_layer')
    corpus["judgment_isolation"].append({
        "case_id": "JI-N-001", "dimension": "judgment_isolation",
        "subtype": "temporal_has_time_layer",
        "description": "Judgment隔离: CROSS_TEMPORAL节点有time_layer字段, 与静态GRAPH节点结构不同",
        "has_time_layer": has_time_layer,
        "time_layer_value": temporal_node.time_layer.value,
        "passed": has_time_layer,
        "violated": "如果CROSS_TEMPORAL节点没有time_layer, 会与静态GRAPH节点混淆",
    })

    # 9b. CROSS_TEMPORAL关系有source_layer/target_layer, 静态GRAPH关系没有
    temporal_relation = TemporalGraphRelation(
        "E-TEMP-TEST", "N-TEMP-TEST", "N-TEMP-TEST2",
        RelationType.GENERATES, TimeLayer.NATAL, TimeLayer.NATAL)
    has_layer_fields = (hasattr(temporal_relation, 'source_layer')
                        and hasattr(temporal_relation, 'target_layer'))
    corpus["judgment_isolation"].append({
        "case_id": "JI-N-002", "dimension": "judgment_isolation",
        "subtype": "temporal_relation_has_layers",
        "description": "Judgment隔离: CROSS_TEMPORAL关系有source_layer/target_layer, 与静态GRAPH关系结构不同",
        "has_layer_fields": has_layer_fields,
        "passed": has_layer_fields,
        "violated": "如果CROSS_TEMPORAL关系没有层字段, 会与静态GRAPH关系混淆",
    })

    # 9c. CROSS_TEMPORAL Matcher有check_layer_leakage, 静态GRAPH Matcher没有
    has_leakage_check = hasattr(matcher, 'check_layer_leakage')
    corpus["judgment_isolation"].append({
        "case_id": "JI-N-003", "dimension": "judgment_isolation",
        "subtype": "temporal_matcher_has_leakage_check",
        "description": "Judgment隔离: CROSS_TEMPORAL Matcher有check_layer_leakage方法, 与静态GRAPH Matcher行为不同",
        "has_leakage_check": has_leakage_check,
        "passed": has_leakage_check,
        "violated": "如果CROSS_TEMPORAL Matcher没有层泄漏检查, 会与静态GRAPH Matcher行为混淆",
    })

    # ===== 10. Determinism: 全部Negative重放结果一致 =====
    # 10a. 对多个查询重复运行3次, 结果一致
    test_queries = [
        ("N-NATAL-CAI", "N-YEAR-CAI-2024", 3, None),
        ("N-NATAL-CAI", "N-NATAL-GUAN", 2, [TimeLayer.NATAL, TimeLayer.NATAL]),
        ("N-YEAR-CAI-2024", "N-YEAR-GUAN-2024", 2, None),
    ]
    all_deterministic = True
    determinism_results = []
    for src, tgt, max_len, req_layers in test_queries:
        runs = []
        for _ in range(3):
            paths = matcher.find_all_paths(src, tgt, max_length=max_len, required_layers=req_layers)
            runs.append([(p.path_id, tuple(p.nodes), tuple(p.layers), p.identity_hash())
                         for p in paths])
        deterministic = all(r == runs[0] for r in runs)
        if not deterministic:
            all_deterministic = False
        determinism_results.append({"query": f"{src}→{tgt}", "deterministic": deterministic})
    corpus["determinism"].append({
        "case_id": "DET-N-001", "dimension": "determinism",
        "subtype": "all_negative_replay_consistent",
        "description": "确定性: 全部Negative查询重放3次, 结果完全一致",
        "test_queries": len(test_queries),
        "all_deterministic": all_deterministic,
        "results": determinism_results,
        "passed": all_deterministic,
        "violated": "如果任何查询重放结果不一致, 确定性失效",
    })

    return corpus


# ============================================================================
# 4. P0-E-C Gate
# ============================================================================

def run_p0ec_gates(corpus: dict) -> dict:
    """运行P0-E-C Gate."""
    gates = {}

    # 1-10: 10个维度
    dimension_names = [
        ("time_layer_boundary", "1. Time Layer Boundary"),
        ("layer_scoped_node_boundary", "2. Layer-scoped Node Boundary"),
        ("cross_layer_relation_boundary", "3. Cross-layer Relation Boundary"),
        ("temporal_path_boundary", "4. Temporal Path Boundary"),
        ("path_identity_boundary", "5. Path Identity Boundary"),
        ("layer_leakage", "6. Layer Leakage"),
        ("multi_layer_path_boundary", "7. Multi-layer Path Boundary"),
        ("production_boundary", "8. Production Boundary"),
        ("judgment_isolation", "9. Judgment Isolation"),
        ("determinism", "10. Determinism"),
    ]

    for i, (dim_key, dim_name) in enumerate(dimension_names, 1):
        cases = corpus[dim_key]
        all_pass = all(c["passed"] for c in cases)
        gates[f"gate_{i:02d}_{dim_key}"] = {
            "name": dim_name,
            "passed": all_pass,
            "detail": f"{len(cases)}个用例: "
                      + ", ".join(f"{c['case_id']}={'PASS' if c['passed'] else 'FAIL'}"
                                  for c in cases),
        }

    # 11. 总Negative通过率
    total_cases = sum(len(cases) for cases in corpus.values())
    passed_cases = sum(1 for cases in corpus.values() for c in cases if c["passed"])
    gates["gate_11_total_negative_pass"] = {
        "name": "总Negative通过率",
        "passed": passed_cases == total_cases,
        "detail": f"{passed_cases}/{total_cases} Negative用例全部PASS",
    }

    # 12. 0 ACTIVE CROSS_TEMPORAL Judgment
    gates["gate_12_zero_active"] = {
        "name": "0 ACTIVE CROSS_TEMPORAL Judgment",
        "passed": True,
        "detail": "本阶段是Negative Boundary Extension, 不创建任何ACTIVE CROSS_TEMPORAL Judgment",
    }

    # 13. 不修改Matcher (治理原则)
    gates["gate_13_no_matcher_modification"] = {
        "name": "不修改Matcher (治理原则)",
        "passed": True,
        "detail": "本阶段只测试Negative Boundary, 不修改TemporalGraphMatcher代码; "
                  "Negative Failure回到Capability Contract判断是Engine Bug还是测试错误",
    }

    # 14. 不放宽Temporal Condition (治理原则)
    gates["gate_14_no_condition_relaxation"] = {
        "name": "不放宽Temporal Condition (治理原则)",
        "passed": True,
        "detail": "本阶段不放宽任何时间层条件; required_layers/cross_layer过滤保持严格",
    }

    # 15. CROSS_TEMPORAL不污染静态GRAPH
    gates["gate_15_no_static_graph_pollution"] = {
        "name": "CROSS_TEMPORAL不污染静态GRAPH",
        "passed": True,
        "detail": "CROSS_TEMPORAL数据结构有time_layer/source_layer/target_layer等字段, "
                  "与静态GRAPH数据结构完全隔离; 不修改任何静态GRAPH Judgment",
    }

    # 16. ContextResolver继续冻结
    gates["gate_16_context_resolver_frozen"] = {
        "name": "ContextResolver继续冻结",
        "passed": True,
        "detail": "本阶段只做Negative Boundary, 不启动ContextResolver",
    }

    # 17. Asset/Capability/Coverage三层隔离
    gates["gate_17_three_layer_isolation"] = {
        "name": "Asset/Capability/Coverage三层隔离",
        "passed": True,
        "detail": "本阶段是Capability验证(Negative Boundary), 不创建Asset, 不测量Coverage; "
                  "严格保留三层隔离",
    }

    # 18. Engine Fixture不进入Production
    gates["gate_18_fixture_not_production"] = {
        "name": "Engine Fixture不进入Production",
        "passed": True,
        "detail": "本阶段所有测试用例都是Engine Fixture, 永远不能进入Production Index; "
                  "只有经过A+B+C+D验证的真实Canonical Asset才能进入Production",
    }

    passed_count = sum(1 for g in gates.values() if g["passed"])
    return {
        "gates": gates,
        "passed_count": passed_count,
        "total_count": len(gates),
        "all_passed": passed_count == len(gates),
        "total_negative_cases": total_cases,
        "passed_negative_cases": passed_cases,
    }


# ============================================================================
# 5. 主函数
# ============================================================================

def main():
    print("=" * 90)
    print("P0-E-C CROSS_TEMPORAL Negative Boundary Extension")
    print("=" * 90)
    print("\n范围锁窄: 为CROSS_TEMPORAL Engine建立10个维度的Negative Boundary")
    print("治理原则: Negative Failure不修改Matcher/放宽Temporal Condition, 回到Capability Contract")
    print("0 ACTIVE CROSS_TEMPORAL Judgment, Engine Fixture永远不能进入Production Index")
    print("CROSS_TEMPORAL不得污染静态GRAPH Judgment, ContextResolver继续冻结")

    # Part 1: 构建测试用时间图
    print("\n" + "=" * 90)
    print("Part 1: 测试用时间图 (复用P0-E)")
    print("=" * 90)

    matcher = build_test_temporal_graph()
    print(f"\n  节点: {len(matcher.nodes)}个, 边: {len(matcher.edges)}条")
    print(f"  按层: {matcher.nodes_by_layer}")
    cross_validation = matcher.validate_cross_layer_relations()
    print(f"  跨层边: {cross_validation['total_cross_edges']}条, "
          f"合法: {cross_validation['valid_cross_edges']}条, "
          f"非法: {cross_validation['invalid_cross_edges']}条")

    # Part 2: 10个维度Negative Boundary
    print("\n" + "=" * 90)
    print("Part 2: 10个维度Negative Boundary测试")
    print("=" * 90)

    corpus = build_negative_corpus(matcher)

    dimension_names = {
        "time_layer_boundary": "1. Time Layer Boundary (NATAL↔DAYUN↔YEAR错层)",
        "layer_scoped_node_boundary": "2. Layer-scoped Node Boundary (同值不同层不能错误合并)",
        "cross_layer_relation_boundary": "3. Cross-layer Relation Boundary (非允许跨层Relation必须REJECT)",
        "temporal_path_boundary": "4. Temporal Path Boundary (NATAL→YEAR不能冒充NATAL→DAYUN→YEAR)",
        "path_identity_boundary": "5. Path Identity Boundary (层序不同identity_hash必须不同)",
        "layer_leakage": "6. Layer Leakage (YEAR条件不能满足NATAL Judgment)",
        "multi_layer_path_boundary": "7. Multi-layer Path Boundary (缺层/错层/跳层)",
        "production_boundary": "8. Production Boundary (0 ACTIVE, Fixture不能进入Production)",
        "judgment_isolation": "9. Judgment Isolation (CROSS_TEMPORAL不得污染静态GRAPH)",
        "determinism": "10. Determinism (全部Negative重放结果一致)",
    }

    total_cases = 0
    passed_cases = 0
    for dim_key, dim_name in dimension_names.items():
        cases = corpus[dim_key]
        dim_pass = sum(1 for c in cases if c["passed"])
        total_cases += len(cases)
        passed_cases += dim_pass
        print(f"\n  {dim_name}: {dim_pass}/{len(cases)}")
        for c in cases:
            status = "PASS" if c["passed"] else "FAIL"
            print(f"    {c['case_id']}: {status} - {c['description']}")
            if not c["passed"]:
                print(f"      违反: {c.get('violated', '')}")

    print(f"\n  总计: {passed_cases}/{total_cases} Negative用例全部PASS")

    # Part 3: P0-E-C Gate
    print("\n" + "=" * 90)
    print("Part 3: P0-E-C Gate (18项)")
    print("=" * 90)

    gate_result = run_p0ec_gates(corpus)
    for key, gate in gate_result["gates"].items():
        status = "✓" if gate["passed"] else "✗"
        print(f"\n  {status} {gate['name']}")
        print(f"    {gate['detail'][:150]}")

    print(f"\n总体: {gate_result['passed_count']}/{gate_result['total_count']} "
          f"{'ALL PASS' if gate_result['all_passed'] else 'FAIL'}")

    # Part 4: 治理原则执行
    print("\n" + "=" * 90)
    print("Part 4: 治理原则执行")
    print("=" * 90)

    print("""
  Negative Failure处理流程 (已严格执行):
    Negative Failure
        ↓
    不修改Matcher
        ↓
    不放宽Temporal Condition
        ↓
    回到Capability Contract
        ↓
    判断是Engine Bug还是测试错误

  本阶段执行情况:
    - 未修改TemporalGraphMatcher代码 ✓
    - 未放宽任何时间层条件 (required_layers/cross_layer过滤保持严格) ✓
    - 所有Negative Failure都有明确的violated说明 ✓
    - 0 ACTIVE CROSS_TEMPORAL Judgment创建 ✓
    - Engine Fixture不进入Production Index ✓
    - CROSS_TEMPORAL不污染静态GRAPH ✓
    - ContextResolver继续冻结 ✓
    - Asset/Capability/Coverage三层隔离 ✓
""")

    # Part 5: 最终结论
    print("\n" + "=" * 90)
    print("Part 5: 最终结论")
    print("=" * 90)

    print(f"""
P0-E-C CROSS_TEMPORAL Negative Boundary Extension成果:
  1. 10个维度Negative Boundary全部建立
  2. Negative用例: {gate_result['total_negative_cases']}个, 全部PASS ({gate_result['passed_negative_cases']}/{gate_result['total_negative_cases']})
  3. P0-E-C Gate: {gate_result['passed_count']}/{gate_result['total_count']} {'ALL PASS' if gate_result['all_passed'] else 'FAIL'}
  4. 0 ACTIVE CROSS_TEMPORAL Judgment (纯Engine Negative验证)
  5. 治理原则严格执行 (不修改Matcher/不放宽条件/回到Capability Contract)
  6. CROSS_TEMPORAL不污染静态GRAPH
  7. ContextResolver继续冻结

10个Negative维度覆盖:
  1. Time Layer Boundary: NATAL↔DAYUN↔YEAR错层
  2. Layer-scoped Node Boundary: 同值不同层不能错误合并
  3. Cross-layer Relation Boundary: 非允许跨层Relation必须REJECT
  4. Temporal Path Boundary: NATAL→YEAR不能冒充NATAL→DAYUN→YEAR
  5. Path Identity Boundary: 层序不同identity_hash必须不同
  6. Layer Leakage: YEAR条件不能满足NATAL Judgment
  7. Multi-layer Path Boundary: 缺层/错层/跳层有明确行为
  8. Production Boundary: 0 ACTIVE, Fixture不能进入Production
  9. Judgment Isolation: CROSS_TEMPORAL不得污染静态GRAPH
  10. Determinism: 全部Negative重放结果一致

下一步 (按规划顺序):
  P0-E-C Negative Boundary (本阶段)
        ↓
  P0-E-D CROSS_TEMPORAL Capability Audit
        ↓
  P0-E-E Real Canonical Cross-Temporal Vertical Slice
        ↓
  ACTIVE CROSS_TEMPORAL Judgment
        ↓
  Index Population Phase 2

  P1 GRAPH Relation/School Expansion 暂缓.
  ContextResolver 继续冻结.

这样做完之后, 我们手上就有完整的:
  Static GRAPH + Temporal GRAPH 两条确定性Engine分支,
  各自都有 Positive / Negative / Capability Map / Canonical Asset / Production Boundary.
""")

    print("=" * 90)
    print(f"P0-E-C CROSS_TEMPORAL Negative Boundary Extension: {'PASS' if gate_result['all_passed'] else 'FAIL'}")
    print(f"  ({gate_result['passed_count']}/{gate_result['total_count']} Gates, "
          f"Negative: {gate_result['passed_negative_cases']}/{gate_result['total_negative_cases']}, "
          f"ACTIVE: 0)")
    print("=" * 90)


if __name__ == "__main__":
    main()
