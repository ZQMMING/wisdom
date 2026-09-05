# -*- coding: utf-8 -*-
"""WorkGraph — 盲派做功關係圖結構。

將原本的能量強度計算改為結構化關係圖，用節點+邊表示做功關係。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


# ─── 節點類型 ─────────────────────────────────────────────────────────────────

class NodeType(str, Enum):
    STEM = "STEM"
    BRANCH = "BRANCH"
    TEN_GOD = "TEN_GOD"
    PALACE = "PALACE"


# ─── 關係類型 ─────────────────────────────────────────────────────────────────

class RelationType(str, Enum):
    ZHI = "制"      # 克/控制
    SHENG = "生"    # 生/順生
    HE = "合"       # 合/六合或天干五合
    CHONG = "冲"    # 沖/六沖


# ───  WorkNode ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class WorkNode:
    """做功圖中的單個節點。"""

    id: str
    type: NodeType
    value: str           # 甲 / 子 / 正財 / 日柱 等
    position: str = ""   # 年干 / 月支 / 日柱 / 時干 等

    def __post_init__(self) -> None:
        # 防止修改 frozen dataclass（用 object.__setattr__ 绕过）
        pass

    @property
    def label(self) -> str:
        """可讀標籤：位置 + 值。"""
        return f"{self.position}[{self.value}]" if self.position else self.value


# ───  WorkEdge ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class WorkEdge:
    """做功圖中的一條邊（有向）。"""

    source: str      # 源節點 ID
    target: str      # 目標節點 ID
    relation: RelationType
    valid: bool = True

    @property
    def relation_str(self) -> str:
        return self.relation.value

    def __str__(self) -> str:
        arrow = "-->" if self.valid else "--X->"
        return f"[{self.source}] {arrow} [{self.target}] ({self.relation_str})"


# ───  WorkGraph ───────────────────────────────────────────────────────────────

@dataclass
class WorkGraph:
    """盲派做功關係圖。"""

    nodes: List[WorkNode] = field(default_factory=list)
    edges: List[WorkEdge] = field(default_factory=list)

    # 內部索引
    _node_map: Dict[str, WorkNode] = field(default_factory=dict, repr=False)
    _adj: Dict[str, List[WorkEdge]] = field(default_factory=lambda: {}, repr=False)

    def __post_init__(self) -> None:
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        """根據 nodes / edges 重建內部索引。"""
        self._node_map = {n.id: n for n in self.nodes}
        self._adj = {n.id: [] for n in self.nodes}
        for e in self.edges:
            if e.source in self._adj:
                self._adj[e.source].append(e)

    # ── 查詢 API ──────────────────────────────────────────────

    def get_node(self, node_id: str) -> Optional[WorkNode]:
        return self._node_map.get(node_id)

    def get_neighbors(self, node_id: str) -> List[WorkEdge]:
        """返回從 node_id 出發的所有邊（含無效邊）。"""
        return self._adj.get(node_id, [])

    def get_valid_neighbors(self, node_id: str) -> List[WorkEdge]:
        """返回從 node_id 出發的有效邊。"""
        return [e for e in self._adj.get(node_id, []) if e.valid]

    def get_edges_for_node(self, node_id: str) -> List[WorkEdge]:
        """所有以 node_id 為 source 或 target 的邊。"""
        out = []
        for e in self.edges:
            if e.source == node_id or e.target == node_id:
                out.append(e)
        return out

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        return len(self.edges)

    def valid_edge_count(self) -> int:
        return sum(1 for e in self.edges if e.valid)

    def nodes_by_type(self, ntype: NodeType) -> List[WorkNode]:
        return [n for n in self.nodes if n.type == ntype]

    def nodes_at_position(self, position: str) -> List[WorkNode]:
        return [n for n in self.nodes if n.position == position]

    # ── 添加 ──────────────────────────────────────────────────

    def add_node(self, node: WorkNode) -> None:
        if node.id not in self._node_map:
            self.nodes.append(node)
            self._node_map[node.id] = node
            self._adj[node.id] = []

    def add_edge(self, edge: WorkEdge) -> None:
        self.edges.append(edge)
        if edge.source in self._adj:
            self._adj[edge.source].append(edge)

    # ── 遍歷算法 ──────────────────────────────────────────────

    def dfs(
        self,
        start_id: str,
        valid_only: bool = True,
        max_depth: int = 10,
    ) -> List[Tuple[str, str]]:
        """DFS 遍歷，返回 (從, 到) 邊序對列表。

        max_depth 限制從起點出發的最長跳數（邊數）。
        """
        visited: Set[str] = set()
        result: List[Tuple[str, str]] = []

        def _dfs(cur: str, depth: int) -> None:
            # depth == max_depth 表示已走 max_depth 步，不能再延伸
            if depth >= max_depth:
                return
            visited.add(cur)
            neighbors = (
                self.get_valid_neighbors(cur)
                if valid_only
                else self.get_neighbors(cur)
            )
            for e in neighbors:
                if e.target not in visited:
                    result.append((cur, e.target))
                    _dfs(e.target, depth + 1)

        _dfs(start_id, 0)
        return result

    def bfs(
        self,
        start_id: str,
        valid_only: bool = True,
        max_depth: int = 10,
    ) -> List[Tuple[str, str]]:
        """BFS 遍歷，返回 (從, 到) 邊序對列表。

        max_depth 限制從起點出發的最長跳數（邊數）。
        """
        from collections import deque
        visited: Set[str] = set()
        result: List[Tuple[str, str]] = []
        queue: deque = deque([(start_id, 0)])
        visited.add(start_id)

        while queue:
            cur, depth = queue.popleft()
            # depth == max_depth 表示已走 max_depth 步，不再延伸
            if depth >= max_depth:
                continue
            neighbors = (
                self.get_valid_neighbors(cur)
                if valid_only
                else self.get_neighbors(cur)
            )
            for e in neighbors:
                if e.target not in visited:
                    visited.add(e.target)
                    result.append((cur, e.target))
                    queue.append((e.target, depth + 1))

        return result

    def find_connected_components(self) -> List[Set[str]]:
        """找出所有連通分量（忽略方向）。"""
        visited: Set[str] = set()
        components: List[Set[str]] = []

        all_ids = list(self._node_map.keys())
        # 構建無向鄰接表
        undir: Dict[str, Set[str]] = {nid: set() for nid in all_ids}
        for e in self.edges:
            if e.source in undir and e.target in undir:
                undir[e.source].add(e.target)
                undir[e.target].add(e.source)

        for start in all_ids:
            if start in visited:
                continue
            component: Set[str] = set()
            stack = [start]
            while stack:
                cur = stack.pop()
                if cur in visited:
                    continue
                visited.add(cur)
                component.add(cur)
                for nb in undir.get(cur, []):
                    if nb not in visited:
                        stack.append(nb)
            components.append(component)

        return components

    def get_degree(self, node_id: str) -> int:
        """返回節點的度（入度 + 出度，只看有效邊）。"""
        out_deg = len(self.get_valid_neighbors(node_id))
        in_deg = sum(
            1 for e in self.edges if e.target == node_id and e.valid
        )
        return out_deg + in_deg

    def to_dict(self) -> dict:
        return {
            "nodes": [
                {
                    "id": n.id,
                    "type": n.type.value,
                    "value": n.value,
                    "position": n.position,
                }
                for n in self.nodes
            ],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "relation": e.relation.value,
                    "valid": e.valid,
                }
                for e in self.edges
            ],
        }

    def __repr__(self) -> str:
        return (
            f"WorkGraph(nodes={self.node_count()}, "
            f"edges={self.edge_count()}, valid={self.valid_edge_count()})"
        )
