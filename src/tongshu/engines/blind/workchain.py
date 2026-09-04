# -*- coding: utf-8 -*-
"""WorkChainResolver — 盲派做功鏈解析器。

從 WorkGraph 中找出完整的做功鏈（從體節點到用節點的有向路徑）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .workgraph import RelationType, WorkEdge, WorkGraph, WorkNode, NodeType


# ───  WorkChain ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class WorkChain:
    """一條完整的做功鏈。"""

    chain_id: str
    nodes: List[WorkNode]           # 鏈上所有節點
    edges: List[WorkEdge]           # 鏈上所有邊
    total_relations: List[str]      # 邊關係列表（["制", "生"]）
    start_node_id: str              # 起點
    end_node_id: str                # 終點

    @property
    def length(self) -> int:
        return len(self.edges)

    @property
    def relation_sequence(self) -> str:
        """可讀的關係序列，如「制→生→合」。"""
        return "→".join(self.total_relations) if self.total_relations else ""

    def __str__(self) -> str:
        node_labels = "→".join(n.label for n in self.nodes)
        rel_seq = self.relation_sequence
        return f"[{self.chain_id}] {node_labels}  ({rel_seq})"


# ───  WorkChainResolver ───────────────────────────────────────────────────────

class WorkChainResolver:
    """從 WorkGraph 中提取做功鏈。

    核心邏輯：
    - 從「體」節點出發，沿著有效邊做 DFS，直到遇到「用」節點。
    - 只保留有效邊（valid=True）。
    - 鏈長度不超过 max_depth。
    """

    def __init__(
        self,
        graph: WorkGraph,
        ti_node_ids: Optional[Set[str]] = None,
        yong_node_ids: Optional[Set[str]] = None,
        max_depth: int = 6,
    ) -> None:
        self.graph = graph
        self.max_depth = max_depth

        # 若未指定體/用集合，自動從節點类型推斷
        if ti_node_ids is None:
            ti_node_ids = self._infer_ti_nodes()
        if yong_node_ids is None:
            yong_node_ids = self._infer_yong_nodes()

        self.ti_node_ids = ti_node_ids
        self.yong_node_ids = yong_node_ids

    # ── 體/用推斷 ──────────────────────────────────────────────

    def _infer_ti_nodes(self) -> Set[str]:
        """從 TEN_GOD 類型節點推斷體節點（比肩/劫财/印/食神/伤官）。"""
        TI_TEN_GODS = {"比肩", "劫财", "偏印", "正印", "食神", "伤官"}
        return {
            n.id for n in self.graph.nodes
            if n.type == NodeType.TEN_GOD and n.value in TI_TEN_GODS
        }

    def _infer_yong_nodes(self) -> Set[str]:
        """從 TEN_GOD 類型節點推斷用節點（財/官杀）。"""
        YONG_TEN_GODS = {"正财", "偏财", "正官", "七杀"}
        return {
            n.id for n in self.graph.nodes
            if n.type == NodeType.TEN_GOD and n.value in YONG_TEN_GODS
        }

    # ── 主入口 ────────────────────────────────────────────────

    def resolve(self) -> List[WorkChain]:
        """找出所有從體到用的做功鏈。"""
        chains: List[WorkChain] = []
        chain_counter = 0

        for ti_id in sorted(self.ti_node_ids):
            visited: Set[str] = set()
            self._dfs_find_chains(
                ti_id, ti_id, visited, [], [], chains,
                chain_counter,
            )

        # 去重：相同 nodes 序列視為同一條鏈
        seen_keys: Set[Tuple[str, ...]] = set()
        unique: List[WorkChain] = []
        for c in chains:
            key = tuple(n.id for n in c.nodes)
            if key not in seen_keys:
                seen_keys.add(key)
                unique.append(c)
                chain_counter += 1

        return unique

    def _dfs_find_chains(
        self,
        start_id: str,
        cur_id: str,
        visited: Set[str],
        path_nodes: List[WorkNode],
        path_edges: List[WorkEdge],
        result: List[WorkChain],
        counter: int,
    ) -> int:
        """DFS 搜尋從 start 到用節點的所有路徑。返回新的 counter。"""
        if cur_id in visited:
            return counter
        if cur_id not in self.graph._node_map:
            return counter

        visited.add(cur_id)
        cur_node = self.graph._node_map[cur_id]
        path_nodes = path_nodes + [cur_node]

        # 終點：當前節點是用節點 → 記錄一條鏈
        if cur_id in self.yong_node_ids and len(path_edges) > 0:
            rels = [e.relation_str for e in path_edges]
            chain = WorkChain(
                chain_id=f"WCHAIN-{counter:04d}",
                nodes=path_nodes,
                edges=path_edges,
                total_relations=rels,
                start_node_id=start_id,
                end_node_id=cur_id,
            )
            result.append(chain)
            counter += 1
            # 繼續探索（可能有多條出路）
        else:
            # 沿有效出邊繼續
            for e in self.graph.get_valid_neighbors(cur_id):
                if e.target not in visited and len(path_edges) < self.max_depth:
                    counter = self._dfs_find_chains(
                        start_id, e.target, visited,
                        path_nodes, path_edges + [e],
                        result, counter,
                    )

        visited.discard(cur_id)
        return counter

    # ── 輔助查詢 ──────────────────────────────────────────────

    def get_chain_by_id(self, chain_id: str) -> Optional[WorkChain]:
        for c in self.resolve():
            if c.chain_id == chain_id:
                return c
        return None

    def get_chains_from(self, node_id: str) -> List[WorkChain]:
        """返回從指定節點出發的所有做功鏈。"""
        return [c for c in self.resolve() if c.start_node_id == node_id]

    def get_chains_to(self, node_id: str) -> List[WorkChain]:
        """返回終點為指定節點的所有做功鏈。"""
        return [c for c in self.resolve() if c.end_node_id == node_id]

    def find_direct_edges_between(
        self,
        source_id: str,
        target_id: str,
        relation: Optional[RelationType] = None,
    ) -> List[WorkEdge]:
        """查找兩節點之間直接相连的有效邊。"""
        result = []
        for e in self.graph.get_valid_neighbors(source_id):
            if e.target == target_id:
                if relation is None or e.relation == relation:
                    result.append(e)
        return result

    def summarize(self) -> dict:
        """返回做功鏈的摘要統計。"""
        chains = self.resolve()
        return {
            "total_chains": len(chains),
            "ti_nodes": sorted(self.ti_node_ids),
            "yong_nodes": sorted(self.yong_node_ids),
            "chain_lengths": [c.length for c in chains],
            "chains": [
                {
                    "id": c.chain_id,
                    "length": c.length,
                    "relations": c.relation_sequence,
                    "start": c.start_node_id,
                    "end": c.end_node_id,
                }
                for c in chains
            ],
        }
