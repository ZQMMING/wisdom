# -*- coding: utf-8 -*-
"""P1-WORK-GRAPH 測試：WorkGraph 關係圖結構 + WorkChainResolver。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.engines.blind.workgraph import (
    RelationType,
    WorkEdge,
    WorkGraph,
    WorkNode,
    NodeType,
)
from tongshu.engines.blind.workchain import WorkChain, WorkChainResolver


# ─── 輔助工廠 ─────────────────────────────────────────────────────────────────

def _make_stem_node(node_id: str, value: str, position: str) -> WorkNode:
    return WorkNode(id=node_id, type=NodeType.STEM, value=value, position=position)


def _make_branch_node(node_id: str, value: str, position: str) -> WorkNode:
    return WorkNode(id=node_id, type=NodeType.BRANCH, value=value, position=position)


def _make_tengod_node(node_id: str, value: str, position: str) -> WorkNode:
    return WorkNode(id=node_id, type=NodeType.TEN_GOD, value=value, position=position)


def _make_palace_node(node_id: str, value: str, position: str) -> WorkNode:
    return WorkNode(id=node_id, type=NodeType.PALACE, value=value, position=position)


def _make_edge(src: str, tgt: str, rel: RelationType, valid: bool = True) -> WorkEdge:
    return WorkEdge(source=src, target=tgt, relation=rel, valid=valid)


# ─── 測試用例 ─────────────────────────────────────────────────────────────────

class TestWorkNode(unittest.TestCase):
    """WorkNode 數據類測試。"""

    def test_create_stem_node(self):
        n = _make_stem_node("s1", "甲", "年干")
        self.assertEqual(n.id, "s1")
        self.assertEqual(n.type, NodeType.STEM)
        self.assertEqual(n.value, "甲")
        self.assertEqual(n.position, "年干")
        self.assertEqual(n.label, "年干[甲]")

    def test_create_branch_node(self):
        n = _make_branch_node("b1", "子", "年支")
        self.assertEqual(n.type, NodeType.BRANCH)
        self.assertEqual(n.value, "子")

    def test_create_tengod_node(self):
        n = _make_tengod_node("tg1", "正财", "月干")
        self.assertEqual(n.type, NodeType.TEN_GOD)
        self.assertEqual(n.value, "正财")

    def test_create_palace_node(self):
        n = _make_palace_node("p1", "日柱", "日柱")
        self.assertEqual(n.type, NodeType.PALACE)

    def test_frozen(self):
        n = _make_stem_node("s1", "甲", "年干")
        with self.assertRaises(AttributeError):
            n.id = "x"


class TestWorkEdge(unittest.TestCase):
    """WorkEdge 數據類測試。"""

    def test_zhi_relation(self):
        e = _make_edge("s1", "s2", RelationType.ZHI)
        self.assertEqual(e.source, "s1")
        self.assertEqual(e.target, "s2")
        self.assertEqual(e.relation, RelationType.ZHI)
        self.assertTrue(e.valid)

    def test_str_valid(self):
        e = _make_edge("a", "b", RelationType.HE, valid=True)
        self.assertIn("-->", str(e))

    def test_str_invalid(self):
        e = _make_edge("a", "b", RelationType.CHONG, valid=False)
        self.assertIn("--X->", str(e))

    def test_frozen(self):
        e = _make_edge("a", "b", RelationType.SHENG)
        with self.assertRaises(AttributeError):
            e.source = "x"


class TestWorkGraph(unittest.TestCase):
    """WorkGraph 結構與遍歷算法測試。"""

    def setUp(self):
        """構建測試圖：

        甲(年干) --制--> 戊(月干)
        乙(日干) --生--> 戊(月干)
        戊(月干) --合--> 癸(時干)
        子(年支) --冲--> 午(日支)
        未效 edge: 甲 --> 癸(无效)
        """
        nodes = [
            _make_stem_node("s_jia", "甲", "年干"),
            _make_stem_node("s_yi",  "乙", "日干"),
            _make_stem_node("s_wu",  "戊", "月干"),
            _make_stem_node("s_gui", "癸", "時干"),
            _make_branch_node("b_zi", "子", "年支"),
            _make_branch_node("b_wu", "午", "日支"),
            _make_tengod_node("tg_cai", "正财", "月干"),
            _make_tengod_node("tg_bi", "比肩", "日干"),
        ]
        edges = [
            _make_edge("s_jia", "s_wu",  RelationType.ZHI, True),
            _make_edge("s_yi",  "s_wu",  RelationType.SHENG, True),
            _make_edge("s_wu",  "s_gui", RelationType.HE, True),
            _make_edge("b_zi",  "b_wu",  RelationType.CHONG, True),
            _make_edge("s_jia", "s_gui", RelationType.ZHI, False),  # 無效邊
        ]
        self.graph = WorkGraph(nodes=nodes, edges=edges)

    def test_node_count(self):
        self.assertEqual(self.graph.node_count(), 8)

    def test_edge_count(self):
        self.assertEqual(self.graph.edge_count(), 5)

    def test_valid_edge_count(self):
        self.assertEqual(self.graph.valid_edge_count(), 4)

    def test_get_node(self):
        n = self.graph.get_node("s_jia")
        self.assertIsNotNone(n)
        self.assertEqual(n.value, "甲")

    def test_get_node_not_found(self):
        self.assertIsNone(self.graph.get_node("nonexist"))

    def test_get_neighbors(self):
        nbrs = self.graph.get_neighbors("s_jia")
        self.assertEqual(len(nbrs), 2)  # 含無效邊
        targets = {e.target for e in nbrs}
        self.assertIn("s_wu", targets)
        self.assertIn("s_gui", targets)

    def test_get_valid_neighbors(self):
        nbrs = self.graph.get_valid_neighbors("s_jia")
        self.assertEqual(len(nbrs), 1)
        self.assertEqual(nbrs[0].target, "s_wu")

    def test_nodes_by_type(self):
        stems = self.graph.nodes_by_type(NodeType.STEM)
        self.assertEqual(len(stems), 4)
        for n in stems:
            self.assertEqual(n.type, NodeType.STEM)

    def test_nodes_at_position(self):
        year = self.graph.nodes_at_position("年干")
        self.assertEqual(len(year), 1)
        self.assertEqual(year[0].value, "甲")

    def test_add_node(self):
        before = self.graph.node_count()
        new_node = _make_stem_node("s_new", "丙", "時干")
        self.graph.add_node(new_node)
        self.assertEqual(self.graph.node_count(), before + 1)
        self.assertEqual(self.graph.get_node("s_new").value, "丙")

    def test_add_duplicate_node_ignored(self):
        before = self.graph.node_count()
        dup = _make_stem_node("s_jia", "甲", "年干")  # 同 ID
        self.graph.add_node(dup)
        self.assertEqual(self.graph.node_count(), before)

    def test_add_edge(self):
        before = self.graph.edge_count()
        self.graph.add_edge(_make_edge("s_jia", "s_yi", RelationType.SHENG))
        self.assertEqual(self.graph.edge_count(), before + 1)

    def test_dfs(self):
        path = self.graph.dfs("s_jia")
        # 從甲出發，有效邊只有甲→戊
        self.assertIn(("s_jia", "s_wu"), path)

    def test_dfs_max_depth_limit(self):
        path = self.graph.dfs("s_jia", max_depth=1)
        # max_depth=1 表示最多 1 條邊：甲→戊（s_gui 是無效邊被跳過）
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], ("s_jia", "s_wu"))

    def test_bfs(self):
        path = self.graph.bfs("s_jia")
        self.assertIn(("s_jia", "s_wu"), path)

    def test_find_connected_components(self):
        comps = self.graph.find_connected_components()
        # 應該至少有一個分量包含 s_jia 和 s_wu
        found = False
        for comp in comps:
            if "s_jia" in comp and "s_wu" in comp:
                found = True
                break
        self.assertTrue(found, "s_jia 和 s_wu 應在同一連通分量")

    def test_get_degree(self):
        # s_jia 有 1 條有效出邊，0 條入邊 → 度 = 1
        self.assertEqual(self.graph.get_degree("s_jia"), 1)
        # s_wu 有 1 條有效出邊（戊→癸），2 條有效入邊（甲制戊、乙生戊）→ 度 = 3
        self.assertEqual(self.graph.get_degree("s_wu"), 3)

    def test_to_dict(self):
        d = self.graph.to_dict()
        self.assertIn("nodes", d)
        self.assertIn("edges", d)
        self.assertEqual(len(d["nodes"]), 8)
        self.assertEqual(len(d["edges"]), 5)
        # 驗證節點結構
        jia = next(n for n in d["nodes"] if n["id"] == "s_jia")
        self.assertEqual(jia["type"], "STEM")
        self.assertEqual(jia["value"], "甲")

    def test_repr(self):
        r = repr(self.graph)
        self.assertIn("WorkGraph", r)
        self.assertIn("nodes=8", r)


class TestWorkChainResolver(unittest.TestCase):
    """WorkChainResolver 做功鏈解析測試。"""

    def setUp(self):
        """構建測試圖：

        tg_bi(比肩/日干) --生--> tg_cai(正财/月干)
        s_jia(甲/年干)   --制--> tg_cai(正财/月干)

        體節點：tg_bi（比肩）、s_jia（甲，推斷為體）
        用節點：tg_cai（正财）
        """
        nodes = [
            _make_tengod_node("tg_bi", "比肩", "日干"),
            _make_tengod_node("tg_cai", "正财", "月干"),
            _make_stem_node("s_jia", "甲", "年干"),
            _make_stem_node("s_wu", "戊", "月干"),
            _make_tengod_node("tg_shi", "食神", "時干"),
            _make_tengod_node("tg_guan", "正官", "年干"),
        ]
        edges = [
            # 比肩生正财 → 一條直接做功鏈
            _make_edge("tg_bi", "tg_cai", RelationType.SHENG, True),
            # 甲制正财 → 另一條直接做功鏈
            _make_edge("s_jia", "tg_cai", RelationType.ZHI, True),
            # 食神制正官 → 另一條做功鏈
            _make_edge("tg_shi", "tg_guan", RelationType.ZHI, True),
            # 無效邊：不應被解析
            _make_edge("tg_bi", "tg_shi", RelationType.HE, False),
        ]
        self.graph = WorkGraph(nodes=nodes, edges=edges)

    def test_resolve_returns_chains(self):
        resolver = WorkChainResolver(self.graph)
        chains = resolver.resolve()
        self.assertGreater(len(chains), 0, "應至少找到一條做功鏈")

    def test_chain_structure(self):
        resolver = WorkChainResolver(self.graph)
        chains = resolver.resolve()
        for c in chains:
            self.assertIsInstance(c, WorkChain)
            self.assertGreaterEqual(c.length, 1)
            self.assertEqual(len(c.nodes), c.length + 1)
            self.assertEqual(len(c.edges), c.length)

    def test_chain_relations(self):
        resolver = WorkChainResolver(self.graph)
        chains = resolver.resolve()
        # 檢查所有鏈的 relations 都是合法字符串
        for c in chains:
            for rel in c.total_relations:
                self.assertIn(rel, {"制", "生", "合", "冲"})

    def test_chain_relation_sequence(self):
        resolver = WorkChainResolver(self.graph)
        chains = resolver.resolve()
        for c in chains:
            seq = c.relation_sequence
            if c.length > 1:
                self.assertIn("→", seq)
            else:
                self.assertEqual(seq, c.total_relations[0])

    def test_chain_starts_from_ti(self):
        """所有鏈的起點應是體節點。"""
        resolver = WorkChainResolver(self.graph)
        chains = resolver.resolve()
        for c in chains:
            self.assertIn(c.start_node_id, resolver.ti_node_ids)

    def test_chain_ends_at_yong(self):
        """所有鏈的終點應是用節點。"""
        resolver = WorkChainResolver(self.graph)
        chains = resolver.resolve()
        for c in chains:
            self.assertIn(c.end_node_id, resolver.yong_node_ids)

    def test_no_chains_when_no_valid_edges(self):
        """無有效邊時應返回空鏈列表。"""
        empty_graph = WorkGraph(
            nodes=[
                _make_tengod_node("tg1", "比肩", "日干"),
                _make_tengod_node("tg2", "正财", "月干"),
            ],
            edges=[],
        )
        resolver = WorkChainResolver(empty_graph)
        chains = resolver.resolve()
        self.assertEqual(len(chains), 0)

    def test_str_representation(self):
        resolver = WorkChainResolver(self.graph)
        chains = resolver.resolve()
        for c in chains:
            s = str(c)
            self.assertIn(c.chain_id, s)
            self.assertIn("→", s)

    def test_get_chains_from(self):
        resolver = WorkChainResolver(self.graph)
        tg_bi_chains = resolver.get_chains_from("tg_bi")
        self.assertEqual(len(tg_bi_chains), 1)
        self.assertEqual(tg_bi_chains[0].end_node_id, "tg_cai")

    def test_get_chains_to(self):
        resolver = WorkChainResolver(self.graph)
        cai_chains = resolver.get_chains_to("tg_cai")
        self.assertGreaterEqual(len(cai_chains), 1)

    def test_summarize(self):
        resolver = WorkChainResolver(self.graph)
        summary = resolver.summarize()
        self.assertIn("total_chains", summary)
        self.assertGreater(summary["total_chains"], 0)
        self.assertIn("chain_lengths", summary)
        self.assertIn("chains", summary)

    def test_direct_edges_between(self):
        resolver = WorkChainResolver(self.graph)
        edges = resolver.find_direct_edges_between("tg_bi", "tg_cai")
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].relation, RelationType.SHENG)

    def test_direct_edges_not_exist(self):
        resolver = WorkChainResolver(self.graph)
        edges = resolver.find_direct_edges_between("tg_bi", "tg_guan")
        self.assertEqual(len(edges), 0)

    def test_direct_edges_filtered_by_relation(self):
        resolver = WorkChainResolver(self.graph)
        # 篩選制關係
        zhi_edges = resolver.find_direct_edges_between(
            "s_jia", "tg_cai", RelationType.ZHI
        )
        self.assertEqual(len(zhi_edges), 1)
        self.assertEqual(zhi_edges[0].relation, RelationType.ZHI)

    def test_chain_with_longer_path(self):
        """測試多步鏈：a→b→c"""
        nodes = [
            _make_tengod_node("t1", "比肩", "日干"),
            _make_tengod_node("t2", "食神", "月干"),
            _make_tengod_node("t3", "正财", "時干"),
        ]
        edges = [
            _make_edge("t1", "t2", RelationType.SHENG, True),
            _make_edge("t2", "t3", RelationType.SHENG, True),
        ]
        g = WorkGraph(nodes=nodes, edges=edges)
        resolver = WorkChainResolver(g)
        chains = resolver.resolve()
        # 比肩→食神→正财 是一條長度為 2 的鏈
        long_chains = [c for c in chains if c.length == 2]
        self.assertEqual(len(long_chains), 1)
        self.assertEqual(long_chains[0].relation_sequence, "生→生")

    def test_no_false_chains_via_invalid_edges(self):
        """無效邊不應對做功鏈產生病態影響。"""
        nodes = [
            _make_tengod_node("tg_ti", "比肩", "日干"),
            _make_tengod_node("tg_yong", "正财", "月干"),
        ]
        edges = [
            _make_edge("tg_ti", "tg_yong", RelationType.ZHI, False),  # 無效
        ]
        g = WorkGraph(nodes=nodes, edges=edges)
        resolver = WorkChainResolver(g)
        chains = resolver.resolve()
        self.assertEqual(len(chains), 0)

    def test_deduplication(self):
        """相同節點序列不應重複計入。"""
        nodes = [
            _make_tengod_node("tg_ti", "比肩", "日干"),
            _make_tengod_node("tg_yong", "正财", "月干"),
        ]
        edges = [
            _make_edge("tg_ti", "tg_yong", RelationType.SHENG, True),
            _make_edge("tg_ti", "tg_yong", RelationType.ZHI, True),  # 多重邊
        ]
        g = WorkGraph(nodes=nodes, edges=edges)
        resolver = WorkChainResolver(g)
        chains = resolver.resolve()
        # 去重後只應有 1 條（以第一條有效邊為準）
        self.assertLessEqual(len(chains), 1)


if __name__ == "__main__":
    unittest.main()
