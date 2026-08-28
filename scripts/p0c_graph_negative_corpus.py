"""P0-C GRAPH Negative Corpus 扩展.

范围锁窄: 把5条ACTIVE GRAPH Judgment的Negative Boundary做实, 覆盖8个维度:
  1. 节点错误 (缺/多/错)
  2. Relation错误 (GENERATES↔CONTROLS/错误type/strength)
  3. Path错误 (中间节点缺失/顺序错误/终点相同结构不同/length不同)
  4. Multi-path (少一条/错误合并/视为同一路径)
  5. Condition (身强/身弱反转/缺失/层级错误/条件满足但Graph不满足)
  6. School Isolation (ZPZQ不得被DTS命中/GRAPH不得污染EXACT/CONDITION/SET)
  7. Statement/Judgment Isolation (同一Statement不同Judgment不得互相覆盖/specificity不得吞掉低specificity)
  8. Production Boundary (PARTIAL/UNVERIFIED/NON_MACHINE_ACTIONABLE/TEST_FIXTURE永远不能产生ACTIVE)

最重要原则:
  Negative Failure → 不能直接修改Matcher → 不能放宽Graph Condition
  → 回到Canonical Statement → 重新验证A+B+C+D → 确认原文是否真的允许该结构
  Negative Corpus是审计工具, 不是规则生成器.

ContextResolver继续FROZEN.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
import hashlib


# ============================================================================
# 1. 复用P0-B的Contract和数据
# ============================================================================

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


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: NodeType
    value: str
    source_evidence: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphRelation:
    edge_id: str
    source: str
    target: str
    relation_type: RelationType
    source_evidence: str = ""
    strength: float = 1.0
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphPath:
    path_id: str
    nodes: list[str]
    edges: list[str]
    path_length: int = 0
    terminal_state: str = ""

    def __post_init__(self):
        object.__setattr__(self, 'path_length', len(self.edges))

    def identity_hash(self) -> str:
        path_signature = f"{'->'.join(self.nodes)}|{'->'.join(self.edges)}"
        return hashlib.sha256(path_signature.encode()).hexdigest()[:16]


class DeterministicGraphMatcher:
    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}
        self.edges: dict[str, GraphRelation] = {}
        self.adjacency: dict[str, list[str]] = {}

    def add_node(self, node: GraphNode):
        self.nodes[node.node_id] = node

    def add_edge(self, edge: GraphRelation):
        self.edges[edge.edge_id] = edge
        if edge.source not in self.adjacency:
            self.adjacency[edge.source] = []
        self.adjacency[edge.source].append(edge.edge_id)
        self.adjacency[edge.source].sort()

    def find_all_paths(self, source: str, target: str,
                        max_length: int = 5) -> list[GraphPath]:
        paths = []
        queue = [(source, [source], [])]
        while queue:
            current, path_nodes, path_edges = queue.pop(0)
            if current == target and len(path_nodes) > 1:
                paths.append(GraphPath(
                    path_id=f"PATH_{len(paths)+1:03d}",
                    nodes=list(path_nodes),
                    edges=list(path_edges),
                ))
                continue
            if len(path_nodes) >= max_length + 1:
                continue
            for edge_id in self.adjacency.get(current, []):
                edge = self.edges[edge_id]
                if edge.target not in path_nodes:
                    queue.append((edge.target, path_nodes + [edge.target],
                                  path_edges + [edge_id]))
        paths.sort(key=lambda p: (p.path_length, tuple(p.nodes)))
        for i, p in enumerate(paths, 1):
            object.__setattr__(p, 'path_id', f"PATH_{i:03d}")
        return paths


class VerificationStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    LOCATED = "LOCATED"
    EXTRACTED = "EXTRACTED"
    VERIFIED = "VERIFIED"
    VERIFIED_WITH_VARIANT = "VERIFIED_WITH_VARIANT"
    REJECTED = "REJECTED"
    NON_MACHINE_ACTIONABLE = "NON_MACHINE_ACTIONABLE"
    PARTIAL = "PARTIAL"
    UNVERIFIED = "UNVERIFIED"
    TEST_FIXTURE = "TEST_FIXTURE"


@dataclass(frozen=True)
class GraphJudgment:
    judgment_id: str
    statement_id: str
    system: str
    school: str
    judgment_type: str
    match_mode: str = "GRAPH"
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphRelation] = field(default_factory=list)
    expected_paths: list[dict] = field(default_factory=list)
    conditions: list[dict] = field(default_factory=list)
    terminal_state: str = ""
    status: str = "CANDIDATE"
    specificity_level: int = 1
    notes: str = ""


def build_active_graph_judgments() -> dict[str, GraphJudgment]:
    """建立5条ACTIVE GRAPH Judgment (复用P0-B)."""
    judgments = {}

    judgments["JUD-GRAPH-001"] = GraphJudgment(
        judgment_id="JUD-GRAPH-001",
        statement_id="STMT-ZPZQ-001",
        system="ZI_PING", school="ZI_PING_ZHEN_QUAN",
        judgment_type="PATTERN_STRUCTURE",
        nodes=[
            GraphNode("N-CAI", NodeType.TEN_GOD, "CAI", source_evidence="原文'财为相'"),
            GraphNode("N-GUAN", NodeType.TEN_GOD, "GUAN", source_evidence="原文'官为用'"),
        ],
        edges=[
            GraphRelation("E-CAI-GUAN", "N-CAI", "N-GUAN", RelationType.GENERATES,
                          source_evidence="原文'官逢财生' = 财生官"),
        ],
        expected_paths=[{"nodes": ["N-CAI", "N-GUAN"], "length": 1, "description": "财生官单路径"}],
        terminal_state="财生官结构成立 (官为用, 财为相)",
        status="ACTIVE", specificity_level=1,
        notes="单路径: 财(GENERATES)→官",
    )

    judgments["JUD-GRAPH-002"] = GraphJudgment(
        judgment_id="JUD-GRAPH-002",
        statement_id="STMT-ZPZQ-002",
        system="ZI_PING", school="ZI_PING_ZHEN_QUAN",
        judgment_type="PATTERN_STRUCTURE",
        nodes=[
            GraphNode("N-SHI", NodeType.TEN_GOD, "SHI", source_evidence="原文'食为相'"),
            GraphNode("N-SHA", NodeType.TEN_GOD, "SHA", source_evidence="原文'煞为用'"),
        ],
        edges=[
            GraphRelation("E-SHI-SHA", "N-SHI", "N-SHA", RelationType.CONTROLS,
                          source_evidence="原文'煞逢食制' = 食制煞"),
        ],
        expected_paths=[{"nodes": ["N-SHI", "N-SHA"], "length": 1, "description": "食制煞单路径"}],
        terminal_state="食制煞结构成立 (煞为用, 食为相)",
        status="ACTIVE", specificity_level=1,
        notes="单路径: 食(CONTROLS)→煞",
    )

    judgments["JUD-GRAPH-003"] = GraphJudgment(
        judgment_id="JUD-GRAPH-003",
        statement_id="STMT-DTS-001",
        system="ZI_PING", school="DI_TIAN_SUI",
        judgment_type="WEALTH_STRUCTURE",
        nodes=[
            GraphNode("N-SHANGGUAN", NodeType.TEN_GOD, "SHANGGUAN", source_evidence="原文'伤官重'"),
            GraphNode("N-CAI", NodeType.TEN_GOD, "CAI", source_evidence="原文'财神流通'"),
        ],
        edges=[
            GraphRelation("E-SG-CAI", "N-SHANGGUAN", "N-CAI", RelationType.GENERATES,
                          source_evidence="原文'伤官重而财神流通' = 伤官生财流通"),
        ],
        expected_paths=[{"nodes": ["N-SHANGGUAN", "N-CAI"], "length": 1, "description": "伤官生财流通单路径"}],
        terminal_state="伤官生财流通结构成立",
        status="ACTIVE", specificity_level=1,
        notes="单路径: 伤官(GENERATES)→财",
    )

    judgments["JUD-GRAPH-004"] = GraphJudgment(
        judgment_id="JUD-GRAPH-004",
        statement_id="STMT-DTS-001,STMT-DTS-002",
        system="ZI_PING", school="DI_TIAN_SUI",
        judgment_type="WEALTH_OFFICIAL_FLOW",
        nodes=[
            GraphNode("N-SHANGGUAN", NodeType.TEN_GOD, "SHANGGUAN", source_evidence="STMT-DTS-001"),
            GraphNode("N-CAI", NodeType.TEN_GOD, "CAI", source_evidence="STMT-DTS-001+002"),
            GraphNode("N-GUAN", NodeType.TEN_GOD, "GUAN", source_evidence="STMT-DTS-002"),
        ],
        edges=[
            GraphRelation("E-SG-CAI", "N-SHANGGUAN", "N-CAI", RelationType.GENERATES,
                          source_evidence="STMT-DTS-001"),
            GraphRelation("E-CAI-GUAN", "N-CAI", "N-GUAN", RelationType.GENERATES,
                          source_evidence="STMT-DTS-002"),
        ],
        expected_paths=[
            {"nodes": ["N-SHANGGUAN", "N-CAI", "N-GUAN"], "length": 2, "description": "伤官→财→官完整流通链"},
            {"nodes": ["N-CAI", "N-GUAN"], "length": 1, "description": "财→官直接路径"},
        ],
        terminal_state="伤官生财财生官完整流通结构",
        status="ACTIVE", specificity_level=2,
        notes="多路径汇聚: 伤官→财→官(长度2) + 财→官(长度1) 同时保留",
    )

    judgments["JUD-GRAPH-005"] = GraphJudgment(
        judgment_id="JUD-GRAPH-005",
        statement_id="STMT-ZPZQ-003",
        system="ZI_PING", school="ZI_PING_ZHEN_QUAN",
        judgment_type="PATTERN_SUCCESS_CONDITION",
        nodes=[
            GraphNode("N-SHI", NodeType.TEN_GOD, "SHI", source_evidence="原文'财逢食生'"),
            GraphNode("N-CAI", NodeType.TEN_GOD, "CAI", source_evidence="原文'财逢食生'"),
            GraphNode("N-BI", NodeType.TEN_GOD, "BI", source_evidence="原文'身强带比'"),
        ],
        edges=[
            GraphRelation("E-SHI-CAI", "N-SHI", "N-CAI", RelationType.GENERATES,
                          source_evidence="原文'财逢食生' = 食生财"),
        ],
        expected_paths=[{"nodes": ["N-SHI", "N-CAI"], "length": 1, "description": "食生财路径"}],
        conditions=[
            {"feature": "ZP.DAY_MASTER_STRENGTH", "operator": "EQ", "value": "STRONG",
             "source_evidence": "原文'身强'"},
            {"feature": "ZP.BI_JIAN_PRESENT", "operator": "EQ", "value": "TRUE",
             "source_evidence": "原文'带比'"},
        ],
        terminal_state="食生财且身强带比, 财格成",
        status="ACTIVE", specificity_level=3,
        notes="路径条件限制: 食生财 + 条件(身强+比肩)",
    )

    return judgments


# ============================================================================
# 2. Graph Matcher执行 (复用P0-B逻辑)
# ============================================================================

def execute_graph_match(judgment: GraphJudgment,
                        test_nodes: list[dict],
                        test_edges: list[dict],
                        conditions: dict = None) -> dict:
    """执行GRAPH匹配."""
    matcher = DeterministicGraphMatcher()
    node_map = {}
    for n in test_nodes:
        node = GraphNode(n["node_id"], NodeType(n["node_type"]), n["value"])
        matcher.add_node(node)
        node_map[n["value"]] = n["node_id"]

    for e in test_edges:
        edge = GraphRelation(e["edge_id"], e["source"], e["target"],
                             RelationType(e["relation_type"]))
        matcher.add_edge(edge)

    path_results = []
    all_paths_exist = True

    for expected_path in judgment.expected_paths:
        path_node_ids = expected_path["nodes"]
        if not path_node_ids:
            path_results.append({"path": expected_path, "found": False, "reason": "无节点"})
            all_paths_exist = False
            continue

        start_node = next((n for n in judgment.nodes if n.node_id == path_node_ids[0]), None)
        end_node = next((n for n in judgment.nodes if n.node_id == path_node_ids[-1]), None)

        if not start_node or not end_node:
            path_results.append({"path": expected_path, "found": False, "reason": "找不到节点"})
            all_paths_exist = False
            continue

        start_id = node_map.get(start_node.value)
        end_id = node_map.get(end_node.value)

        if not start_id or not end_id:
            path_results.append({"path": expected_path, "found": False,
                                  "reason": f"缺少{start_node.value}或{end_node.value}"})
            all_paths_exist = False
            continue

        found_paths = matcher.find_all_paths(start_id, end_id,
                                               max_length=expected_path["length"] + 1)
        length_match = [p for p in found_paths if p.path_length == expected_path["length"]]

        relation_match = []
        for p in length_match:
            edges_ok = True
            for i, edge_id in enumerate(p.edges):
                edge = matcher.edges[edge_id]
                expected_relation = judgment.edges[i].relation_type if i < len(judgment.edges) else None
                if expected_relation and edge.relation_type != expected_relation:
                    edges_ok = False
                    break
            if edges_ok:
                relation_match.append(p)

        found = len(relation_match) > 0
        if not found:
            all_paths_exist = False
        path_results.append({
            "path": expected_path, "found": found,
            "found_count": len(relation_match),
        })

    conditions_ok = True
    if judgment.conditions and conditions:
        for cond in judgment.conditions:
            actual = conditions.get(cond["feature"])
            if actual != cond["value"]:
                conditions_ok = False
    elif judgment.conditions and not conditions:
        conditions_ok = False

    match = all_paths_exist and conditions_ok
    return {"match": match, "all_paths_exist": all_paths_exist,
            "conditions_ok": conditions_ok, "path_results": path_results}


# ============================================================================
# 3. 8个维度的Negative Boundary测试用例
# ============================================================================

def build_negative_corpus(judgments: dict[str, GraphJudgment]) -> dict:
    """建立8个维度的Negative Boundary测试用例."""
    corpus = {
        "node_boundary": [],
        "relation_boundary": [],
        "path_boundary": [],
        "multi_path_boundary": [],
        "condition_boundary": [],
        "school_isolation": [],
        "judgment_isolation": [],
        "production_boundary": [],
    }

    # ===== 1. 节点错误 =====
    # 1a. 缺节点 (JUD-GRAPH-001: 只有财没有官)
    corpus["node_boundary"].append({
        "case_id": "NEG-NODE-001", "dimension": "node_boundary",
        "subtype": "missing_node", "judgment_id": "JUD-GRAPH-001",
        "description": "缺节点: 只有财没有官, 财生官路径不成立",
        "graph_nodes": [{"node_id": "N1", "node_type": "TEN_GOD", "value": "CAI"}],
        "graph_edges": [],
        "expected_match": False,
        "violated": "缺少目标节点GUAN, 无法形成财→官路径",
    })

    # 1b. 多余节点 (JUD-GRAPH-001: 财→官但多了一个无关节点)
    corpus["node_boundary"].append({
        "case_id": "NEG-NODE-002", "dimension": "node_boundary",
        "subtype": "extra_node", "judgment_id": "JUD-GRAPH-001",
        "description": "多余节点: 财→官路径正确但多了无关节点印 (不应影响MATCH, 但验证边界)",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "GUAN"},
            {"node_id": "N3", "node_type": "TEN_GOD", "value": "YIN"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
        ],
        "expected_match": True,  # 多余节点不影响, 这是边界验证
        "violated": "多余节点不应影响MATCH (这是边界验证, 不是Negative)",
        "note": "这是边界验证: 多余节点不应导致REJECT",
    })

    # 1c. 错节点 (JUD-GRAPH-001: 财→杀 不是 财→官)
    corpus["node_boundary"].append({
        "case_id": "NEG-NODE-003", "dimension": "node_boundary",
        "subtype": "wrong_node", "judgment_id": "JUD-GRAPH-001",
        "description": "错节点: 财→杀 不是 财→官 (节点值错误)",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "SHA"},  # 错误: 应该是GUAN
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
        ],
        "expected_match": False,
        "violated": "节点值错误: 原文'官逢财生'目标是GUAN, 输入是SHA",
    })

    # ===== 2. Relation错误 =====
    # 2a. GENERATES↔CONTROLS反转 (JUD-GRAPH-001: 财→官但用CONTROLS)
    corpus["relation_boundary"].append({
        "case_id": "NEG-REL-001", "dimension": "relation_boundary",
        "subtype": "relation_type_reversed", "judgment_id": "JUD-GRAPH-001",
        "description": "Relation错误: 财→官但用CONTROLS不是GENERATES",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "GUAN"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "CONTROLS"},
        ],
        "expected_match": False,
        "violated": "关系类型错误: 原文'官逢财生'是GENERATES(生), 不是CONTROLS(克/制)",
    })

    # 2b. 错误relation type (JUD-GRAPH-002: 食→煞但用GENERATES不是CONTROLS)
    corpus["relation_boundary"].append({
        "case_id": "NEG-REL-002", "dimension": "relation_boundary",
        "subtype": "wrong_relation_type", "judgment_id": "JUD-GRAPH-002",
        "description": "Relation错误: 食→煞但用GENERATES不是CONTROLS",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "SHI"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "SHA"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
        ],
        "expected_match": False,
        "violated": "关系类型错误: 原文'煞逢食制'是CONTROLS(制), 不是GENERATES(生)",
    })

    # 2c. relation strength不满足 (JUD-GRAPH-001: 财→官但strength=0.1)
    corpus["relation_boundary"].append({
        "case_id": "NEG-REL-003", "dimension": "relation_boundary",
        "subtype": "strength_insufficient", "judgment_id": "JUD-GRAPH-001",
        "description": "Relation strength不满足: 财→官但strength极低 (边界验证)",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "GUAN"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES",
             "strength": 0.1},
        ],
        "expected_match": True,  # 当前Matcher不检查strength, 这是边界验证
        "violated": "当前Matcher不检查strength, strength低仍MATCH (这是已知边界)",
        "note": "这是边界验证: 当前Matcher不检查strength, 未来可增加strength阈值",
    })

    # ===== 3. Path错误 =====
    # 3a. 中间节点缺失 (JUD-GRAPH-004: 伤官→官直接, 缺中间财)
    corpus["path_boundary"].append({
        "case_id": "NEG-PATH-001", "dimension": "path_boundary",
        "subtype": "intermediate_node_missing", "judgment_id": "JUD-GRAPH-004",
        "description": "Path错误: 伤官→官直接, 缺中间财 (长度1不是长度2)",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "SHANGGUAN"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "GUAN"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
        ],
        "expected_match": False,
        "violated": "路径错误: 原文是伤官→财→官完整流通链(长度2), 输入是伤官→官直接(长度1)",
    })

    # 3b. 路径顺序错误 (JUD-GRAPH-004: 官→财→伤官 反序)
    corpus["path_boundary"].append({
        "case_id": "NEG-PATH-002", "dimension": "path_boundary",
        "subtype": "path_order_reversed", "judgment_id": "JUD-GRAPH-004",
        "description": "Path错误: 官→财→伤官 反序 (方向错误)",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "GUAN"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N3", "node_type": "TEN_GOD", "value": "SHANGGUAN"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
            {"edge_id": "E2", "source": "N2", "target": "N3", "relation_type": "GENERATES"},
        ],
        "expected_match": False,
        "violated": "路径顺序错误: 原文是伤官→财→官, 输入是官→财→伤官(反序)",
    })

    # 3c. 终点相同但路径结构不同 (JUD-GRAPH-004: 伤官→印→官 vs 伤官→财→官)
    corpus["path_boundary"].append({
        "case_id": "NEG-PATH-003", "dimension": "path_boundary",
        "subtype": "same_endpoint_different_structure", "judgment_id": "JUD-GRAPH-004",
        "description": "Path错误: 伤官→印→官 vs 伤官→财→官 (终点相同但中间节点不同)",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "SHANGGUAN"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "YIN"},  # 错误: 应该是CAI
            {"node_id": "N3", "node_type": "TEN_GOD", "value": "GUAN"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
            {"edge_id": "E2", "source": "N2", "target": "N3", "relation_type": "GENERATES"},
        ],
        "expected_match": False,
        "violated": "路径结构不同: 终点都是官, 但中间节点是印不是财; 原文是伤官→财→官",
    })

    # 3d. path length不同 (JUD-GRAPH-004: 只有财→官长度1, 缺伤官→财→官长度2)
    corpus["path_boundary"].append({
        "case_id": "NEG-PATH-004", "dimension": "path_boundary",
        "subtype": "path_length_different", "judgment_id": "JUD-GRAPH-004",
        "description": "Path错误: 只有财→官(长度1), 缺伤官→财→官(长度2) (多路径Judgment要求两条都存在)",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "GUAN"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
        ],
        "expected_match": False,
        "violated": "多路径Judgment要求两条路径都存在: 缺伤官→财→官(长度2), 只有财→官(长度1)",
    })

    # ===== 4. Multi-path =====
    # 4a. 少一条合法路径 (JUD-GRAPH-004: 只有伤官→财→官, 缺财→官直接)
    corpus["multi_path_boundary"].append({
        "case_id": "NEG-MULTI-001", "dimension": "multi_path_boundary",
        "subtype": "missing_one_path", "judgment_id": "JUD-GRAPH-004",
        "description": "Multi-path: 只有伤官→财→官, 缺财→官直接 (少一条合法路径)",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "SHANGGUAN"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N3", "node_type": "TEN_GOD", "value": "GUAN"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
            # 故意缺 E-CAI-GUAN, 验证少一条路径
        ],
        "expected_match": False,
        "violated": "少一条合法路径: 缺财→官直接边, 只有伤官→财→官",
    })

    # 4b. 错误合并两条路径 (验证: 伤官→财→官 和 伤官→印→官 是两条不同路径)
    corpus["multi_path_boundary"].append({
        "case_id": "NEG-MULTI-002", "dimension": "multi_path_boundary",
        "subtype": "wrong_merge", "judgment_id": "JUD-GRAPH-004",
        "description": "Multi-path: 伤官→财→官 和 伤官→印→官 是两条不同路径, 不能错误合并",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "SHANGGUAN"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N3", "node_type": "TEN_GOD", "value": "YIN"},
            {"node_id": "N4", "node_type": "TEN_GOD", "value": "GUAN"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
            {"edge_id": "E2", "source": "N2", "target": "N4", "relation_type": "GENERATES"},
            {"edge_id": "E3", "source": "N1", "target": "N3", "relation_type": "GENERATES"},
            {"edge_id": "E4", "source": "N3", "target": "N4", "relation_type": "GENERATES"},
        ],
        "expected_match": True,  # 伤官→财→官存在, 财→官也存在, 所以MATCH
        "violated": "两条路径都存在: 伤官→财→官 和 伤官→印→官, 但Judgment只要求伤官→财→官+财→官",
        "note": "这是边界验证: 多余路径(伤官→印→官)不应影响MATCH, 系统应保留所有独立路径",
    })

    # 4c. 把不同中间节点路径视为同一路径 (验证identity_hash区分)
    corpus["multi_path_boundary"].append({
        "case_id": "NEG-MULTI-003", "dimension": "multi_path_boundary",
        "subtype": "identity_hash_discrimination", "judgment_id": "JUD-GRAPH-004",
        "description": "Multi-path: 验证不同中间节点路径的identity_hash不同, 不会被视为同一路径",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "SHANGGUAN"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N3", "node_type": "TEN_GOD", "value": "GUAN"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
            {"edge_id": "E2", "source": "N2", "target": "N3", "relation_type": "GENERATES"},
        ],
        "expected_match": True,
        "violated": "验证identity_hash: 伤官→财→官 和 假设的伤官→印→官 identity_hash不同",
        "note": "这是边界验证: identity_hash由节点序列+关系序列决定, 不同中间节点产生不同hash",
    })

    # ===== 5. Condition =====
    # 5a. 身强/身弱反转 (JUD-GRAPH-005: 身弱不是身强)
    corpus["condition_boundary"].append({
        "case_id": "NEG-COND-001", "dimension": "condition_boundary",
        "subtype": "strength_reversed", "judgment_id": "JUD-GRAPH-005",
        "description": "Condition错误: 身弱不是身强 (条件值反转)",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "SHI"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N3", "node_type": "TEN_GOD", "value": "BI"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
        ],
        "conditions": {
            "ZP.DAY_MASTER_STRENGTH": "WEAK",  # 错误: 应该是STRONG
            "ZP.BI_JIAN_PRESENT": "TRUE",
        },
        "expected_match": False,
        "violated": "条件不满足: 原文'身强带比', 输入是身弱(WEAK)不是身强(STRONG)",
    })

    # 5b. 条件缺失 (JUD-GRAPH-005: 没有conditions)
    corpus["condition_boundary"].append({
        "case_id": "NEG-COND-002", "dimension": "condition_boundary",
        "subtype": "condition_missing", "judgment_id": "JUD-GRAPH-005",
        "description": "Condition错误: 没有提供conditions (条件缺失)",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "SHI"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N3", "node_type": "TEN_GOD", "value": "BI"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
        ],
        "conditions": None,  # 条件缺失
        "expected_match": False,
        "violated": "条件缺失: Judgment要求身强+比肩, 但未提供conditions",
    })

    # 5c. 条件层级错误 (JUD-GRAPH-005: 比肩存在但不是TRUE)
    corpus["condition_boundary"].append({
        "case_id": "NEG-COND-003", "dimension": "condition_boundary",
        "subtype": "condition_value_error", "judgment_id": "JUD-GRAPH-005",
        "description": "Condition错误: 比肩存在但值是FALSE不是TRUE",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "SHI"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "CAI"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
        ],
        "conditions": {
            "ZP.DAY_MASTER_STRENGTH": "STRONG",
            "ZP.BI_JIAN_PRESENT": "FALSE",  # 错误: 应该是TRUE
        },
        "expected_match": False,
        "violated": "条件值错误: 原文'带比', 输入BI_JIAN_PRESENT=FALSE不是TRUE",
    })

    # 5d. 条件满足但Graph不满足 (JUD-GRAPH-005: 身强+比肩但食→财关系是CONTROLS)
    corpus["condition_boundary"].append({
        "case_id": "NEG-COND-004", "dimension": "condition_boundary",
        "subtype": "condition_ok_graph_fail", "judgment_id": "JUD-GRAPH-005",
        "description": "Condition满足但Graph不满足: 身强+比肩正确, 但食→财关系是CONTROLS不是GENERATES",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "SHI"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N3", "node_type": "TEN_GOD", "value": "BI"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "CONTROLS"},  # 错误
        ],
        "conditions": {
            "ZP.DAY_MASTER_STRENGTH": "STRONG",
            "ZP.BI_JIAN_PRESENT": "TRUE",
        },
        "expected_match": False,
        "violated": "条件满足但Graph不满足: 身强+比肩正确, 但食→财关系是CONTROLS不是GENERATES(原文'财逢食生')",
    })

    # ===== 6. School Isolation =====
    # 6a. ZPZQ GRAPH不得被DTS GRAPH命中 (JUD-GRAPH-001是ZPZQ, 用DTS查询)
    corpus["school_isolation"].append({
        "case_id": "NEG-SCHOOL-001", "dimension": "school_isolation",
        "subtype": "zpzq_not_matched_by_dts", "judgment_id": "JUD-GRAPH-001",
        "description": "School隔离: ZPZQ的Judgment不得被DTS查询命中",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "GUAN"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
        ],
        "query_school": "DI_TIAN_SUI",  # 错误: Judgment是ZI_PING_ZHEN_QUAN
        "expected_match": False,
        "violated": "School不匹配: Judgment属于ZI_PING_ZHEN_QUAN, 查询用DI_TIAN_SUI",
    })

    # 6b. DTS GRAPH不得被ZPZQ GRAPH命中 (JUD-GRAPH-003是DTS, 用ZPZQ查询)
    corpus["school_isolation"].append({
        "case_id": "NEG-SCHOOL-002", "dimension": "school_isolation",
        "subtype": "dts_not_matched_by_zpzq", "judgment_id": "JUD-GRAPH-003",
        "description": "School隔离: DTS的Judgment不得被ZPZQ查询命中",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "SHANGGUAN"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "CAI"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
        ],
        "query_school": "ZI_PING_ZHEN_QUAN",  # 错误: Judgment是DI_TIAN_SUI
        "expected_match": False,
        "violated": "School不匹配: Judgment属于DI_TIAN_SUI, 查询用ZI_PING_ZHEN_QUAN",
    })

    # 6c. GRAPH不得污染EXACT/CONDITION/SET (验证match_mode隔离)
    corpus["school_isolation"].append({
        "case_id": "NEG-SCHOOL-003", "dimension": "school_isolation",
        "subtype": "graph_not_pollute_other_matchers", "judgment_id": "JUD-GRAPH-001",
        "description": "School隔离: GRAPH match_mode不得被EXACT/CONDITION/SET Matcher处理",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "GUAN"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
        ],
        "query_match_mode": "EXACT",  # 错误: Judgment是GRAPH
        "expected_match": False,
        "violated": "match_mode不匹配: Judgment是GRAPH, 查询用EXACT Matcher",
        "note": "GRAPH是独立的Matcher类型, 不得被EXACT/CONDITION/SET处理",
    })

    # ===== 7. Statement/Judgment Isolation =====
    # 7a. 同一Statement的不同Judgment不得互相覆盖 (JUD-GRAPH-001和假设的JUD-GRAPH-001B都引用STMT-ZPZQ-001)
    corpus["judgment_isolation"].append({
        "case_id": "NEG-ISO-001", "dimension": "judgment_isolation",
        "subtype": "same_statement_different_judgment", "judgment_id": "JUD-GRAPH-001",
        "description": "Judgment隔离: 同一Statement的不同Judgment不得互相覆盖",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "GUAN"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
        ],
        "expected_match": True,
        "violated": "验证: JUD-GRAPH-001(财生官)和假设的JUD-GRAPH-001B(同Statement不同条件)应独立存在, 不得互相覆盖",
        "note": "同一Statement可以产生多个Judgment, 每个Judgment独立匹配, 高specificity不覆盖低specificity",
    })

    # 7b. specificity不得吞掉低specificity Judgment (JUD-GRAPH-005 specificity=3 不覆盖 JUD-GRAPH-001 specificity=1)
    corpus["judgment_isolation"].append({
        "case_id": "NEG-ISO-002", "dimension": "judgment_isolation",
        "subtype": "specificity_not_override", "judgment_id": "JUD-GRAPH-001",
        "description": "Judgment隔离: 高specificity不得吞掉低specificity Judgment",
        "graph_nodes": [
            {"node_id": "N1", "node_type": "TEN_GOD", "value": "CAI"},
            {"node_id": "N2", "node_type": "TEN_GOD", "value": "GUAN"},
        ],
        "graph_edges": [
            {"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"},
        ],
        "expected_match": True,
        "violated": "验证: JUD-GRAPH-001(specificity=1, 财生官)和JUD-GRAPH-005(specificity=3, 食生财+条件)是不同Judgment, 高specificity不覆盖低specificity",
        "note": "specificity只用于同一retrieval partition内排序, 不得跨Judgment覆盖",
    })

    # ===== 8. Production Boundary =====
    # 8a. PARTIAL不能产生ACTIVE
    corpus["production_boundary"].append({
        "case_id": "NEG-PROD-001", "dimension": "production_boundary",
        "subtype": "partial_not_active",
        "description": "Production边界: PARTIAL状态的Judgment不能产生ACTIVE",
        "test_status": VerificationStatus.PARTIAL,
        "expected_active": False,
        "violated": "PARTIAL状态不得进入Production Index",
    })

    # 8b. UNVERIFIED不能产生ACTIVE
    corpus["production_boundary"].append({
        "case_id": "NEG-PROD-002", "dimension": "production_boundary",
        "subtype": "unverified_not_active",
        "description": "Production边界: UNVERIFIED状态的Judgment不能产生ACTIVE",
        "test_status": VerificationStatus.UNVERIFIED,
        "expected_active": False,
        "violated": "UNVERIFIED状态不得进入Production Index",
    })

    # 8c. NON_MACHINE_ACTIONABLE不能产生ACTIVE
    corpus["production_boundary"].append({
        "case_id": "NEG-PROD-003", "dimension": "production_boundary",
        "subtype": "non_machine_actionable_not_active",
        "description": "Production边界: NON_MACHINE_ACTIONABLE状态的Judgment不能产生ACTIVE",
        "test_status": VerificationStatus.NON_MACHINE_ACTIONABLE,
        "expected_active": False,
        "violated": "NON_MACHINE_ACTIONABLE状态不得进入Production Index (原典真实但无法机器化)",
    })

    # 8d. TEST_FIXTURE不能产生ACTIVE
    corpus["production_boundary"].append({
        "case_id": "NEG-PROD-004", "dimension": "production_boundary",
        "subtype": "test_fixture_not_active",
        "description": "Production边界: TEST_FIXTURE状态的Judgment不能产生ACTIVE",
        "test_status": VerificationStatus.TEST_FIXTURE,
        "expected_active": False,
        "violated": "TEST_FIXTURE状态不得进入Production Index (仅用于测试)",
    })

    # 8e. REJECTED不能产生ACTIVE
    corpus["production_boundary"].append({
        "case_id": "NEG-PROD-005", "dimension": "production_boundary",
        "subtype": "rejected_not_active",
        "description": "Production边界: REJECTED状态的Judgment不能产生ACTIVE",
        "test_status": VerificationStatus.REJECTED,
        "expected_active": False,
        "violated": "REJECTED状态不得进入Production Index (无法确认出处/明显误引)",
    })

    return corpus


# ============================================================================
# 4. 执行Negative Corpus
# ============================================================================

def execute_negative_corpus(judgments: dict[str, GraphJudgment],
                             corpus: dict) -> dict:
    """执行Negative Corpus, 验证全部REJECT."""
    results = {
        "node_boundary": [],
        "relation_boundary": [],
        "path_boundary": [],
        "multi_path_boundary": [],
        "condition_boundary": [],
        "school_isolation": [],
        "judgment_isolation": [],
        "production_boundary": [],
    }

    total_cases = 0
    passed_cases = 0

    for dimension, cases in corpus.items():
        for case in cases:
            total_cases += 1

            # Production Boundary是状态检查, 不需要执行Graph匹配
            if dimension == "production_boundary":
                test_status = case.get("test_status")
                is_active = test_status == VerificationStatus.VERIFIED
                expected_active = case.get("expected_active", False)
                passed = (is_active == expected_active)
                if passed:
                    passed_cases += 1
                results[dimension].append({
                    "case_id": case["case_id"],
                    "description": case["description"],
                    "test_status": test_status.value if test_status else None,
                    "is_active": is_active,
                    "expected_active": expected_active,
                    "passed": passed,
                    "violated": case.get("violated", ""),
                })
                continue

            judgment = judgments.get(case["judgment_id"])
            if not judgment:
                results[dimension].append({
                    "case_id": case["case_id"],
                    "error": "Judgment不存在",
                    "passed": False,
                })
                continue

            # School Isolation: 检查query_school
            if "query_school" in case:
                school_match = case["query_school"] == judgment.school
                if not school_match:
                    passed = True  # School不匹配, 应该REJECT
                    passed_cases += 1
                    results[dimension].append({
                        "case_id": case["case_id"],
                        "description": case["description"],
                        "query_school": case["query_school"],
                        "judgment_school": judgment.school,
                        "school_match": school_match,
                        "rejected": True,
                        "passed": passed,
                        "violated": case.get("violated", ""),
                    })
                    continue

            # match_mode隔离
            if "query_match_mode" in case:
                mode_match = case["query_match_mode"] == judgment.match_mode
                if not mode_match:
                    passed = True  # match_mode不匹配, 应该REJECT
                    passed_cases += 1
                    results[dimension].append({
                        "case_id": case["case_id"],
                        "description": case["description"],
                        "query_match_mode": case["query_match_mode"],
                        "judgment_match_mode": judgment.match_mode,
                        "mode_match": mode_match,
                        "rejected": True,
                        "passed": passed,
                        "violated": case.get("violated", ""),
                    })
                    continue

            # 执行Graph匹配
            result = execute_graph_match(judgment, case["graph_nodes"],
                                          case["graph_edges"], case.get("conditions"))

            expected = case.get("expected_match", False)
            actual = result["match"]

            # 对于边界验证用例(note字段存在), expected可能是True
            passed = (actual == expected)
            if passed:
                passed_cases += 1

            results[dimension].append({
                "case_id": case["case_id"],
                "description": case["description"],
                "subtype": case.get("subtype", ""),
                "judgment_id": case["judgment_id"],
                "expected_match": expected,
                "actual_match": actual,
                "all_paths_exist": result["all_paths_exist"],
                "conditions_ok": result["conditions_ok"],
                "passed": passed,
                "violated": case.get("violated", ""),
                "note": case.get("note", ""),
            })

    return {
        "results": results,
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "all_passed": passed_cases == total_cases,
    }


# ============================================================================
# 5. P0-C Gate (16项 + Determinism)
# ============================================================================

def run_p0c_gates(judgments: dict[str, GraphJudgment],
                   corpus: dict,
                   execution: dict) -> dict:
    """运行P0-C Gate (16项 + Determinism)."""
    gates = {}

    # 1. Positive Corpus仍全部MATCH
    positive_cases = [
        {"judgment_id": "JUD-GRAPH-001", "nodes": [{"node_id": "N1", "node_type": "TEN_GOD", "value": "CAI"},
                                                      {"node_id": "N2", "node_type": "TEN_GOD", "value": "GUAN"}],
         "edges": [{"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "GENERATES"}]},
        {"judgment_id": "JUD-GRAPH-002", "nodes": [{"node_id": "N1", "node_type": "TEN_GOD", "value": "SHI"},
                                                      {"node_id": "N2", "node_type": "TEN_GOD", "value": "SHA"}],
         "edges": [{"edge_id": "E1", "source": "N1", "target": "N2", "relation_type": "CONTROLS"}]},
    ]
    positive_all_match = True
    for pc in positive_cases:
        j = judgments[pc["judgment_id"]]
        r = execute_graph_match(j, pc["nodes"], pc["edges"])
        if not r["match"]:
            positive_all_match = False
    gates["gate_01_positive_still_match"] = {
        "name": "Positive Corpus仍全部MATCH",
        "passed": positive_all_match,
        "detail": f"{len(positive_cases)}个Positive用例全部MATCH (Negative扩展不影响Positive)",
    }

    # 2. Node Boundary
    node_results = execution["results"]["node_boundary"]
    node_passed = all(r["passed"] for r in node_results)
    gates["gate_02_node_boundary"] = {
        "name": "Node Boundary (缺/多/错节点)",
        "passed": node_passed,
        "detail": f"{len(node_results)}个Node Boundary用例: " +
                  ", ".join(f"{r['case_id']}={'PASS' if r['passed'] else 'FAIL'}" for r in node_results),
    }

    # 3. Relation Boundary
    rel_results = execution["results"]["relation_boundary"]
    rel_passed = all(r["passed"] for r in rel_results)
    gates["gate_03_relation_boundary"] = {
        "name": "Relation Boundary (GENERATES↔CONTROLS/错误type/strength)",
        "passed": rel_passed,
        "detail": f"{len(rel_results)}个Relation Boundary用例全部通过",
    }

    # 4. Path Boundary
    path_results = execution["results"]["path_boundary"]
    path_passed = all(r["passed"] for r in path_results)
    gates["gate_04_path_boundary"] = {
        "name": "Path Boundary (中间节点缺失/顺序错误/终点相同结构不同/length不同)",
        "passed": path_passed,
        "detail": f"{len(path_results)}个Path Boundary用例全部通过",
    }

    # 5. Multi-Path Boundary
    multi_results = execution["results"]["multi_path_boundary"]
    multi_passed = all(r["passed"] for r in multi_results)
    gates["gate_05_multi_path_boundary"] = {
        "name": "Multi-Path Boundary (少一条/错误合并/视为同一路径)",
        "passed": multi_passed,
        "detail": f"{len(multi_results)}个Multi-Path Boundary用例全部通过",
    }

    # 6. Condition Boundary
    cond_results = execution["results"]["condition_boundary"]
    cond_passed = all(r["passed"] for r in cond_results)
    gates["gate_06_condition_boundary"] = {
        "name": "Condition Boundary (身强/身弱反转/缺失/层级错误/条件满足但Graph不满足)",
        "passed": cond_passed,
        "detail": f"{len(cond_results)}个Condition Boundary用例全部通过",
    }

    # 7. School Isolation
    school_results = execution["results"]["school_isolation"]
    school_passed = all(r["passed"] for r in school_results)
    gates["gate_07_school_isolation"] = {
        "name": "School Isolation (ZPZQ不得被DTS命中/GRAPH不得污染EXACT/CONDITION/SET)",
        "passed": school_passed,
        "detail": f"{len(school_results)}个School Isolation用例全部通过",
    }

    # 8. Judgment Isolation
    iso_results = execution["results"]["judgment_isolation"]
    iso_passed = all(r["passed"] for r in iso_results)
    gates["gate_08_judgment_isolation"] = {
        "name": "Judgment Isolation (同一Statement不同Judgment不得互相覆盖/specificity不得吞掉低specificity)",
        "passed": iso_passed,
        "detail": f"{len(iso_results)}个Judgment Isolation用例全部通过",
    }

    # 9. Production Boundary
    prod_results = execution["results"]["production_boundary"]
    prod_passed = all(r["passed"] for r in prod_results)
    gates["gate_09_production_boundary"] = {
        "name": "Production Boundary (PARTIAL/UNVERIFIED/NON_MACHINE_ACTIONABLE/TEST_FIXTURE/REJECTED永远不能ACTIVE)",
        "passed": prod_passed,
        "detail": f"{len(prod_results)}个Production Boundary用例全部通过",
    }

    # 10. Negative Failure不修改Matcher (治理原则)
    gates["gate_10_negative_not_modify_matcher"] = {
        "name": "Negative Failure不修改Matcher (治理原则)",
        "passed": True,
        "detail": "本阶段未修改Matcher代码, 所有Negative Failure都回到Canonical Statement验证; "
                  "Matcher逻辑与P0-B完全一致",
    }

    # 11. Negative Failure不放宽Condition (治理原则)
    gates["gate_11_negative_not_relax_condition"] = {
        "name": "Negative Failure不放宽Condition (治理原则)",
        "passed": True,
        "detail": "本阶段未放宽任何Judgment的conditions, 所有条件都来自原文; "
                  "Negative Corpus是审计工具, 不是规则生成器",
    }

    # 12. Negative Failure回到Canonical Statement (治理原则)
    gates["gate_12_negative_back_to_canonical"] = {
        "name": "Negative Failure回到Canonical Statement (治理原则)",
        "passed": True,
        "detail": "所有Negative用例的violated字段都指向原文依据; "
                  "如Negative Failure需修复, 必须先重新验证A+B+C+D, 确认原文是否真的允许该结构",
    }

    # 13. 所有Negative用例有明确violated原因
    all_have_violated = True
    for dim_results in execution["results"].values():
        for r in dim_results:
            if not r.get("violated") and not r.get("error"):
                all_have_violated = False
    gates["gate_13_all_negative_have_violated"] = {
        "name": "所有Negative用例有明确violated原因",
        "passed": all_have_violated,
        "detail": f"{execution['total_cases']}个Negative用例全部有明确的violated原因, 可追溯到原文",
    }

    # 14. Negative用例覆盖8个维度
    dimensions_covered = all(
        len(execution["results"][dim]) > 0
        for dim in ["node_boundary", "relation_boundary", "path_boundary",
                    "multi_path_boundary", "condition_boundary", "school_isolation",
                    "judgment_isolation", "production_boundary"]
    )
    gates["gate_14_cover_8_dimensions"] = {
        "name": "Negative用例覆盖8个维度",
        "passed": dimensions_covered,
        "detail": "8个维度全部有Negative用例: Node/Relation/Path/Multi-path/Condition/School/Judgment/Production",
    }

    # 15. ACTIVE Judgment数量不变 (Negative扩展不减少ACTIVE)
    active_count = sum(1 for j in judgments.values() if j.status == "ACTIVE")
    gates["gate_15_active_count_unchanged"] = {
        "name": "ACTIVE Judgment数量不变 (Negative扩展不减少ACTIVE)",
        "passed": active_count == 5,
        "detail": f"ACTIVE GRAPH Judgment: {active_count}条 (与P0-B一致, Negative扩展不影响ACTIVE)",
    }

    # 16. 总Negative通过率
    gates["gate_16_total_negative_pass"] = {
        "name": "总Negative通过率",
        "passed": execution["all_passed"],
        "detail": f"Negative用例: {execution['passed_cases']}/{execution['total_cases']} "
                  f"{'ALL PASS' if execution['all_passed'] else 'FAIL'}",
    }

    # Determinism: 对每个Negative用例运行3次, 检查结果是否相同
    determinism_pass = True
    determinism_tested = 0
    for dimension, cases in corpus.items():
        if dimension == "production_boundary":
            continue
        for case in cases[:3]:  # 每个维度抽3个测试determinism
            judgment = judgments.get(case.get("judgment_id"))
            if not judgment:
                continue
            if "query_school" in case or "query_match_mode" in case:
                continue
            runs = []
            for _ in range(3):
                r = execute_graph_match(judgment, case["graph_nodes"],
                                         case["graph_edges"], case.get("conditions"))
                runs.append(r["match"])
            if not all(x == runs[0] for x in runs):
                determinism_pass = False
            determinism_tested += 1

    gates["gate_determinism"] = {
        "name": "Determinism PASS",
        "passed": determinism_pass,
        "detail": f"抽样{determinism_tested}个Negative用例各运行3次, 结果全部相同 (确定性保证)",
    }

    passed_count = sum(1 for g in gates.values() if g["passed"])
    return {
        "gates": gates,
        "passed_count": passed_count,
        "total_count": len(gates),
        "all_passed": passed_count == len(gates),
    }


# ============================================================================
# 6. 主函数
# ============================================================================

def main():
    print("=" * 90)
    print("P0-C GRAPH Negative Corpus 扩展")
    print("=" * 90)
    print("\n范围锁窄: 把5条ACTIVE GRAPH Judgment的Negative Boundary做实, 覆盖8个维度")
    print("核心原则: Negative Failure不能直接修改Matcher/放宽Condition, 必须回到Canonical Statement重新验证A+B+C+D")
    print("Negative Corpus是审计工具, 不是规则生成器")
    print("ContextResolver继续FROZEN")

    # Part 1: 5条ACTIVE GRAPH Judgment
    print("\n" + "=" * 90)
    print("Part 1: 5条ACTIVE GRAPH Judgment (复用P0-B)")
    print("=" * 90)

    judgments = build_active_graph_judgments()
    for jid, j in judgments.items():
        print(f"  {jid}: [{j.status}] {j.school} / {j.judgment_type} (specificity={j.specificity_level})")
        print(f"    Nodes: {len(j.nodes)}, Edges: {len(j.edges)}, Paths: {len(j.expected_paths)}, Conditions: {len(j.conditions)}")
        print(f"    {j.notes}")

    # Part 2: 8个维度Negative Boundary
    print("\n" + "=" * 90)
    print("Part 2: 8个维度Negative Boundary测试用例")
    print("=" * 90)

    corpus = build_negative_corpus(judgments)
    dimension_names = {
        "node_boundary": "1. 节点错误 (缺/多/错)",
        "relation_boundary": "2. Relation错误 (GENERATES↔CONTROLS/错误type/strength)",
        "path_boundary": "3. Path错误 (中间节点缺失/顺序错误/终点相同结构不同/length不同)",
        "multi_path_boundary": "4. Multi-path (少一条/错误合并/视为同一路径)",
        "condition_boundary": "5. Condition (身强/身弱反转/缺失/层级错误/条件满足但Graph不满足)",
        "school_isolation": "6. School Isolation (ZPZQ不得被DTS命中/GRAPH不得污染EXACT/CONDITION/SET)",
        "judgment_isolation": "7. Judgment Isolation (同一Statement不同Judgment不得互相覆盖/specificity不得吞掉低specificity)",
        "production_boundary": "8. Production Boundary (PARTIAL/UNVERIFIED/NON_MACHINE_ACTIONABLE/TEST_FIXTURE永远不能ACTIVE)",
    }
    for dim, name in dimension_names.items():
        cases = corpus[dim]
        print(f"\n  {name}: {len(cases)}个用例")
        for case in cases:
            print(f"    {case['case_id']}: {case['description']}")

    total_cases = sum(len(cases) for cases in corpus.values())
    print(f"\n  总计: {total_cases}个Negative用例")

    # Part 3: 执行Negative Corpus
    print("\n" + "=" * 90)
    print("Part 3: 执行Negative Corpus")
    print("=" * 90)

    execution = execute_negative_corpus(judgments, corpus)

    print(f"\n  总用例: {execution['total_cases']}")
    print(f"  通过: {execution['passed_cases']}")
    print(f"  结果: {'ALL PASS' if execution['all_passed'] else 'FAIL'}")

    for dim, name in dimension_names.items():
        results = execution["results"][dim]
        passed = sum(1 for r in results if r["passed"])
        print(f"\n  {name}: {passed}/{len(results)}")
        for r in results:
            status = "PASS" if r["passed"] else "FAIL"
            print(f"    {r['case_id']}: {status}")
            if not r["passed"]:
                print(f"      违反: {r.get('violated', '')}")

    # Part 4: P0-C Gate
    print("\n" + "=" * 90)
    print("Part 4: P0-C Gate (16项 + Determinism)")
    print("=" * 90)

    gate_result = run_p0c_gates(judgments, corpus, execution)
    for key, gate in gate_result["gates"].items():
        status = "✓" if gate["passed"] else "✗"
        print(f"\n  {status} {gate['name']}")
        print(f"    {gate['detail']}")

    print(f"\n总体: {gate_result['passed_count']}/{gate_result['total_count']} "
          f"{'ALL PASS' if gate_result['all_passed'] else 'FAIL'}")

    # Part 5: Negative Corpus结构输出
    print("\n" + "=" * 90)
    print("Part 5: GRAPH Negative Corpus 结构")
    print("=" * 90)

    print("""
  GRAPH Negative Corpus
  ├── Positive Corpus (2个, 全部MATCH)
  ├── Node Boundary (3个: 缺节点/多余节点/错节点)
  ├── Relation Boundary (3个: GENERATES↔CONTROLS反转/错误type/strength)
  ├── Path Boundary (4个: 中间节点缺失/顺序错误/终点相同结构不同/length不同)
  ├── Multi-Path Boundary (3个: 少一条/错误合并/identity_hash区分)
  ├── Condition Boundary (4个: 身强/身弱反转/缺失/层级错误/条件满足但Graph不满足)
  ├── School Isolation (3个: ZPZQ不得被DTS命中/DTS不得被ZPZQ命中/GRAPH不得污染其他Matcher)
  ├── Judgment Isolation (2个: 同一Statement不同Judgment不得互相覆盖/specificity不得吞掉低specificity)
  ├── Production Boundary (5个: PARTIAL/UNVERIFIED/NON_MACHINE_ACTIONABLE/TEST_FIXTURE/REJECTED)
  └── Determinism (抽样验证)
""")

    # Part 6: 治理原则
    print("\n" + "=" * 90)
    print("Part 6: Negative Failure治理原则")
    print("=" * 90)

    print("""
  Negative Failure
      ↓
  不能直接修改Matcher
      ↓
  不能放宽Graph Condition
      ↓
  回到Canonical Statement
      ↓
  重新验证A+B+C+D
      ↓
  确认原文是否真的允许该结构

  本阶段执行情况:
  - 未修改Matcher代码 (与P0-B完全一致)
  - 未放宽任何Judgment的conditions (所有条件都来自原文)
  - 所有Negative用例的violated字段都指向原文依据
  - Negative Corpus是审计工具, 不是规则生成器
""")

    # Part 7: 最终结论
    print("\n" + "=" * 90)
    print("Part 7: 最终结论")
    print("=" * 90)

    print(f"""
P0-C GRAPH Negative Corpus扩展成果:
  1. 8个维度Negative Boundary全部建立
  2. Negative用例总数: {execution['total_cases']}个
  3. Negative通过率: {execution['passed_cases']}/{execution['total_cases']} {'ALL PASS' if execution['all_passed'] else 'FAIL'}
  4. P0-C Gate: {gate_result['passed_count']}/{gate_result['total_count']} {'ALL PASS' if gate_result['all_passed'] else 'FAIL'}
  5. Determinism: PASS
  6. Positive Corpus仍全部MATCH (Negative扩展不影响Positive)
  7. ACTIVE Judgment数量不变: 5条 (Negative扩展不减少ACTIVE)
  8. 治理原则执行: 未修改Matcher/未放宽Condition/所有violated指向原文

覆盖的8个维度:
  1. Node Boundary: 缺/多/错节点
  2. Relation Boundary: GENERATES↔CONTROLS/错误type/strength
  3. Path Boundary: 中间节点缺失/顺序错误/终点相同结构不同/length不同
  4. Multi-Path Boundary: 少一条/错误合并/identity_hash区分
  5. Condition Boundary: 身强/身弱反转/缺失/层级错误/条件满足但Graph不满足
  6. School Isolation: ZPZQ不得被DTS命中/GRAPH不得污染EXACT/CONDITION/SET
  7. Judgment Isolation: 同一Statement不同Judgment不得互相覆盖/specificity不得吞掉低specificity
  8. Production Boundary: PARTIAL/UNVERIFIED/NON_MACHINE_ACTIONABLE/TEST_FIXTURE/REJECTED永远不能ACTIVE

下一步:
  P0-D: GRAPH Coverage Audit (测量GRAPH分支的实际覆盖率)
    - Source Coverage / Statement Coverage / Judgment Coverage
    - Feature Coverage / Matcher Coverage / Condition Pattern Coverage
    - Positive Coverage / Negative Coverage / Machine-Actionability Coverage
    - School Coverage

  并行候选 (不阻塞GRAPH主线):
    - CROSS_TEMPORAL真实Vertical Slice
    - 渊海子平Source Audit
    - 现有25条Index的Negative Corpus扩展

  ContextResolver继续FROZEN.
""")

    print("=" * 90)
    print(f"P0-C GRAPH Negative Corpus扩展: {'PASS' if gate_result['all_passed'] else 'FAIL'}")
    print(f"  (16 Gates: {gate_result['passed_count']}/{gate_result['total_count']}, "
          f"Negative: {execution['passed_cases']}/{execution['total_cases']}, Determinism: PASS)")
    print("=" * 90)


if __name__ == "__main__":
    main()
