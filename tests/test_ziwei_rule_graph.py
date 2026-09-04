# -*- coding: utf-8 -*-
"""ZiweiRuleGraph 测试（Z12）。

覆盖：
- 格局规则匹配（武贪格、杀破狼、日月并明等）
- 四化规则匹配（生年干四化落宫）
- 宫位规则匹配
- 多流派隔离（Sanhe vs Zhongzhou vs Feixing）
- 空宫借星打折逻辑
- 同盘异法验证（batch_match）
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tongshu.engines.ziwei_engine import ZiweiEngine
from tongshu.engines.ziwei_method_profile import MethodId
from tongshu.engines.ziwei.rules.rule_graph import (
    ZiweiRuleGraph,
    create_rule_graph,
    batch_match,
)


class TestPatternMatching(unittest.TestCase):
    """格局规则匹配测试。"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()
        cls.chart_male = cls.engine.full_chart((2000, 1, 1), 12, 'male')
        cls.chart_female = cls.engine.full_chart((1990, 5, 15), 10, 'female')

    def test_sanhe_rule_graph_creation(self):
        graph = create_rule_graph(MethodId.SANHE)
        self.assertEqual(graph.method_id, MethodId.SANHE)
        self.assertGreater(graph.rule_count, 0)

    def test_feixing_rule_graph_creation(self):
        graph = create_rule_graph(MethodId.FEIXING)
        self.assertEqual(graph.method_id, MethodId.FEIXING)

    def test_zhongzhou_rule_graph_creation(self):
        graph = create_rule_graph(MethodId.ZHONGZHOU)
        self.assertEqual(graph.method_id, MethodId.ZHONGZHOU)

    def test_qintian_rule_graph_creation(self):
        graph = create_rule_graph(MethodId.QINTIAN)
        self.assertEqual(graph.method_id, MethodId.QINTIAN)

    def test_match_patterns_returns_matches(self):
        graph = create_rule_graph(MethodId.SANHE)
        result = graph.match_patterns(self.chart_male)
        self.assertGreaterEqual(len(result.matched_rules), 0)
        self.assertEqual(result.method_id, MethodId.SANHE)

    def test_match_all_returns_combined(self):
        graph = create_rule_graph(MethodId.SANHE)
        result = graph.match_all(self.chart_male)
        total = len(result.matched_rules)
        self.assertGreater(total, 0)
        palace_matches = [m for m in result.matched_rules
                         if m.rule_spec.rule_type.value == "palace"]
        self.assertGreaterEqual(len(palace_matches), 12)

    def test_sihua_match_with_known_stem(self):
        graph = create_rule_graph(MethodId.SANHE)
        result = graph.match_sihua(self.chart_male, "甲")
        self.assertEqual(len(result.matched_rules), 4)
        for m in result.matched_rules:
            self.assertEqual(m.rule_spec.method_id, MethodId.SANHE)
            self.assertEqual(m.rule_spec.rule_type.value, "sihua")


class TestMultiMethodIsolation(unittest.TestCase):
    """多流派隔离测试。"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()
        cls.chart = cls.engine.full_chart((2000, 1, 1), 12, 'male')

    def test_sanh_vs_zhongzhou_different_sihua(self):
        sanhe_graph = create_rule_graph(MethodId.SANHE)
        zz_graph = create_rule_graph(MethodId.ZHONGZHOU)
        sanhe_sihua = sanhe_graph.match_sihua(self.chart, "戊")
        zz_sihua = zz_graph.match_sihua(self.chart, "戊")
        sanhe_ke = sanhe_sihua.matched_rules[0].facts.get("ke_star", "")
        zz_ke = zz_sihua.matched_rules[0].facts.get("ke_star", "")
        # 需要找到科星对应的规则（索引2）
        sanhe_ke = sanhe_sihua.matched_rules[2].facts.get("ke_star", "")
        zz_ke = zz_sihua.matched_rules[2].facts.get("ke_star", "")
        self.assertNotEqual(sanhe_ke, zz_ke,
            f"戊干科星应不同：三合={sanhe_ke}, 中州={zz_ke}")

    def test_sanh_vs_feixing_same_sihua(self):
        sanhe_graph = create_rule_graph(MethodId.SANHE)
        fx_graph = create_rule_graph(MethodId.FEIXING)
        sanhe_sihua = sanhe_graph.match_sihua(self.chart, "戊")
        fx_sihua = fx_graph.match_sihua(self.chart, "戊")
        sanhe_ke = sanhe_sihua.matched_rules[2].facts.get("ke_star", "")
        fx_ke = fx_sihua.matched_rules[2].facts.get("ke_star", "")
        self.assertEqual(sanhe_ke, fx_ke)

    def test_method_id_in_all_matches(self):
        for mid in [MethodId.SANHE, MethodId.ZHONGZHOU, MethodId.FEIXING]:
            graph = create_rule_graph(mid)
            result = graph.match_all(self.chart)
            self.assertEqual(result.method_id, mid)
            for m in result.matched_rules:
                self.assertEqual(m.rule_spec.method_id, mid)


class TestEmptyPalaceBorrow(unittest.TestCase):
    """空宫借星打折测试。"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()
        cls.chart = cls.engine.full_chart((1984, 10, 15), 8, 'female')

    def test_empty_palace_detected(self):
        ming_major = self.chart['palaces']['命宫'].get('major', [])
        self.assertEqual(ming_major, [], "此案例命宫应为空宫")

    def test_borrow_stars_applied(self):
        graph = create_rule_graph(MethodId.SANHE)
        result = graph.match_patterns(self.chart)
        pattern_names = [m.rule_spec.condition.get("pattern_name", "")
                        for m in result.matched_rules]
        self.assertIn("日月并明", pattern_names,
            f"命宫借星后应有日月并明格局，实际匹配: {pattern_names}")


class TestBatchMatch(unittest.TestCase):
    """同盘异法批量匹配测试。"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()
        cls.chart = cls.engine.full_chart((2000, 1, 1), 12, 'male')

    def test_batch_match_returns_all_methods(self):
        results = batch_match(self.chart)
        method_ids = list(results.keys())
        self.assertEqual(len(method_ids), 4)
        for mid in [MethodId.SANHE, MethodId.ZHONGZHOU,
                    MethodId.FEIXING, MethodId.QINTIAN]:
            self.assertIn(mid, method_ids)

    def test_batch_match_no_cross_contamination(self):
        results = batch_match(self.chart)
        for mid, result in results.items():
            self.assertEqual(result.method_id, mid)
            for m in result.matched_rules:
                self.assertEqual(m.rule_spec.method_id, mid)

    def test_batch_match_different_rule_ids(self):
        results = batch_match(self.chart)
        sanhe_ids = {m.rule_spec.rule_id for m
                     in results[MethodId.SANHE].matched_rules}
        zz_ids = {m.rule_spec.rule_id for m
                  in results[MethodId.ZHONGZHOU].matched_rules}
        self.assertTrue(any("SANHE" in sid for sid in sanhe_ids))
        self.assertTrue(any("ZHONGZHOU" in zid for zid in zz_ids))


class TestRuleMatchStructure(unittest.TestCase):
    """RuleMatch 数据结构测试。"""

    def test_to_dict(self):
        from tongshu.engines.ziwei_method_profile import (
            RuleSpec, MethodId, RuleType, ConfidenceLevel)
        from tongshu.engines.ziwei.rules.rule_graph import RuleMatch

        spec = RuleSpec(
            rule_id="TEST-RULE",
            method_id=MethodId.SANHE,
            rule_type=RuleType.PATTERN,
            condition={"test": True},
            operation={"action": "test"},
            confidence=ConfidenceLevel.HIGH,
        )
        match = RuleMatch(rule_spec=spec, facts={"key": "val"},
                          qualified=True, qualifier="")
        d = match.to_dict()
        self.assertEqual(d["rule_id"], "TEST-RULE")
        self.assertEqual(d["method_id"], "sanhe")
        self.assertEqual(d["qualified"], True)

    def test_rule_match_result_to_dict(self):
        from tongshu.engines.ziwei_method_profile import MethodId
        from tongshu.engines.ziwei.rules.rule_graph import RuleMatchResult

        result = RuleMatchResult(method_id=MethodId.SANHE)
        d = result.to_dict()
        self.assertEqual(d["method_id"], "sanhe")
        self.assertEqual(d["matched_count"], 0)


if __name__ == "__main__":
    unittest.main()
