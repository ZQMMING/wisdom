# -*- coding: utf-8 -*-
"""P0-RULE-GRAPH 测试：规则图系统支持 requires + invalidates。"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.engines.blind.rules import Rule, MatchContext, RuleMatcher, RuleGraph


class TestRule(unittest.TestCase):
    """Rule 数据类基本测试。"""

    def test_frozen(self):
        r = Rule(rule_id="TEST-001", school="BLIND_SCHOOL", requires=["stem:JIA"],
                 invalidates=["TEST-002"], judgment="test")
        self.assertEqual(r.id, "TEST-001")
        with self.assertRaises(AttributeError):
            r.rule_id = "x"  # frozen

    def test_is_invalidated_by(self):
        r = Rule(rule_id="A", school="BLIND_SCHOOL", requires=[],
                 invalidates=["B"])
        self.assertTrue(r.is_invalidated_by({"B"}))
        self.assertFalse(r.is_invalidated_by({"C"}))
        self.assertFalse(r.is_invalidated_by(set()))


class TestRuleMatcher(unittest.TestCase):
    """RuleMatcher 匹配与反例排除测试。"""

    def setUp(self):
        self.rules = [
            Rule(rule_id="A", school="BLIND_SCHOOL", requires=["stem:JIA"],
                 invalidates=["B"], judgment="A命中"),
            Rule(rule_id="B", school="BLIND_SCHOOL", requires=["stem:JIA"],
                 invalidates=[], judgment="B被A排除"),
            Rule(rule_id="C", school="BLIND_SCHOOL", requires=["tg:正财"],
                 invalidates=["A"], judgment="C排除A"),
        ]
        self.matcher = RuleMatcher(self.rules)

    def test_match_basic(self):
        ctx = MatchContext(
            stems={"year": "JIA", "month": "YI", "day": "BING", "hour": "WU"},
            branches={"year": "ZI", "month": "CHOU", "day": "YIN", "hour": "MAO"},
            hidden_stems={"year": [], "month": [], "day": [], "hour": []},
            ten_gods={"JIA": "比肩", "YI": "劫财", "BING": "比肩", "WU": "比肩"},
            ti_stems=["JIA", "BING", "WU"], yong_stems=[],
        )
        matched = self.matcher.match(ctx)
        ids = {r.rule_id for r in matched}
        # A 和 B 都需要 stem:JIA，都应该命中（未经 invalidate）
        self.assertIn("A", ids)
        self.assertIn("B", ids)

    def test_invalidate_removes_b(self):
        ctx = MatchContext(
            stems={"year": "JIA", "month": "YI", "day": "BING", "hour": "WU"},
            branches={"year": "ZI", "month": "CHOU", "day": "YIN", "hour": "MAO"},
            hidden_stems={"year": [], "month": [], "day": [], "hour": []},
            ten_gods={"JIA": "比肩", "YI": "劫财", "BING": "比肩", "WU": "比肩"},
            ti_stems=["JIA", "BING", "WU"], yong_stems=[],
        )
        matched = self.matcher.match(ctx)
        result = self.matcher.invalidate(matched, self.rules)
        ids = {r.rule_id for r in result}
        # A invalidates B，所以 B 应被移除
        self.assertIn("A", ids)
        self.assertNotIn("B", ids)

    def test_mutual_invalidation_only_one_kept(self):
        """C 排除 A，A 排除 B；最终保留 C（A 也被 C 排除）。"""
        ctx = MatchContext(
            stems={"year": "JIA", "month": "YI", "day": "BING", "hour": "WU"},
            branches={"year": "ZI", "month": "CHOU", "day": "YIN", "hour": "MAO"},
            hidden_stems={"year": [], "month": [], "day": [], "hour": []},
            ten_gods={"JIA": "比肩", "YI": "劫财", "BING": "正财", "WU": "比肩"},
            ti_stems=["JIA", "BING", "WU"], yong_stems=["BING"],
        )
        matched = self.matcher.match(ctx)
        result = self.matcher.invalidate(matched, self.rules)
        ids = {r.rule_id for r in result}
        # C 排除 A；A 排除 B；所以只有 C 保留
        self.assertIn("C", ids)
        self.assertNotIn("A", ids)
        self.assertNotIn("B", ids)

    def test_no_match_when_required_stem_missing(self):
        ctx = MatchContext(
            stems={"year": "YI", "month": "BING", "day": "WU", "hour": "JI"},
            branches={"year": "ZI", "month": "CHOU", "day": "YIN", "hour": "MAO"},
            hidden_stems={"year": [], "month": [], "day": [], "hour": []},
            ten_gods={"YI": "劫财", "BING": "比肩", "WU": "比肩", "JI": "正印"},
            ti_stems=["YI", "BING", "WU"], yong_stems=[],
        )
        matched = self.matcher.match(ctx)
        self.assertEqual(len(matched), 0)


class TestRuleGraph(unittest.TestCase):
    """RuleGraph 加载与匹配集成测试。"""

    def test_load_and_match(self):
        graph = RuleGraph(rules_dir=Path("backend/data/rules"))
        n = graph.load("BL-sample.json")
        self.assertGreater(n, 0)

        ctx = MatchContext(
            stems={"year": "JIA", "month": "YI", "day": "BING", "hour": "WU"},
            branches={"year": "ZI", "month": "CHOU", "day": "WU", "hour": "MAO"},
            hidden_stems={"year": [], "month": [], "day": [], "hour": []},
            ten_gods={"JIA": "比肩", "YI": "劫财", "BING": "比肩", "WU": "比肩"},
            ti_stems=["JIA", "BING", "WU"], yong_stems=[],
        )
        result = graph.match(ctx)
        ids = [r.rule_id for r in result]
        # BL-ZG-001 和 BL-ZG-002 条件相同(stem:JIA, branch:WU)，都应命中
        # BL-CAI-001 条件不同(stem:正财)，不应命中
        self.assertIn("BL-ZG-001", ids)
        self.assertIn("BL-ZG-002", ids)
        self.assertNotIn("BL-CAI-001", ids)

    def test_get_rule(self):
        graph = RuleGraph(rules_dir=Path("backend/data/rules"))
        graph.load("BL-sample.json")
        r = graph.get_rule("BL-ZG-001")
        self.assertIsNotNone(r)
        self.assertEqual(r.judgment, "甲日坐午火为羊刃，主性格刚烈、事业心强")


if __name__ == "__main__":
    unittest.main()
