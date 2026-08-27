"""Unit tests for the rule condition DSL (T201) and conflict resolution (T205).

Run from backend/:
    PYTHONPATH=src python -m unittest tests.test_matcher -v
"""

from __future__ import annotations
import json
import os
import tempfile
import unittest
from pathlib import Path

from tongshu.reasoning.matcher import (
    RuleContext,
    RuleMatcher,
    UnknownFieldError,
    UnknownOperatorError,
    count_conditions,
    evaluate_conditions,
    resolve_conflicts,
    rule_precedence,
    rule_specificity,
)
from tongshu.reasoning.rule_loader import RuleLoader, RuleLoadError
from tongshu.reasoning.knowledge_base import KbLoader
from tongshu.reasoning.signal_engine import build_rule_context
from tongshu.reasoning.bazi_ten_gods import (
    hidden_main_stem_is_transparent,
    month_hidden_main_ten_god,
    transparent_ten_gods,
)
from tongshu.engines.bazi_engine import BaziEngine


def ctx(**kw):
    defaults = dict(
        day_master="YI",
        day_master_element="WOOD",
        day_branch="HAI",
        month_stem="GUI",
        month_branch="ZI",
        layer="BASELINE",
    )
    defaults.update(kw)
    return RuleContext(**defaults)


class TestDSLCombinators(unittest.TestCase):
    def test_empty_matches_unconditionally(self):
        self.assertTrue(evaluate_conditions(None, ctx()))
        self.assertTrue(evaluate_conditions({}, ctx()))

    def test_all(self):
        cond = {"all": [
            {"field": "day_master_element", "op": "eq", "value": "WOOD"},
            {"field": "month_branch", "op": "eq", "value": "ZI"},
        ]}
        self.assertTrue(evaluate_conditions(cond, ctx()))
        self.assertFalse(
            evaluate_conditions(cond, ctx(month_branch="WU"))
        )

    def test_any(self):
        cond = {"any": [
            {"field": "day_master_element", "op": "eq", "value": "FIRE"},
            {"field": "month_branch", "op": "eq", "value": "ZI"},
        ]}
        self.assertTrue(evaluate_conditions(cond, ctx()))
        self.assertFalse(
            evaluate_conditions(cond, ctx(month_branch="WU", day_master_element="WATER"))
        )

    def test_not(self):
        cond = {"not": {"field": "day_master_element", "op": "eq", "value": "WOOD"}}
        self.assertFalse(evaluate_conditions(cond, ctx()))
        self.assertTrue(evaluate_conditions(cond, ctx(day_master_element="FIRE")))

    def test_nested(self):
        cond = {
            "all": [
                {"not": {"field": "gender", "op": "eq", "value": "female"}},
                {"any": [
                    {"field": "month_branch", "op": "eq", "value": "ZI"},
                    {"field": "month_branch", "op": "eq", "value": "CHOU"},
                ]},
            ]
        }
        self.assertTrue(evaluate_conditions(cond, ctx()))
        self.assertFalse(evaluate_conditions(cond, ctx(gender="female")))


class TestDSLOperators(unittest.TestCase):
    def test_in_and_nin(self):
        self.assertTrue(evaluate_conditions(
            {"field": "month_hidden_main_ten_god", "op": "in", "value": ["正印", "偏印"]},
            ctx(month_hidden_main_ten_god="正印")))
        self.assertFalse(evaluate_conditions(
            {"field": "month_hidden_main_ten_god", "op": "in", "value": ["正印"]},
            ctx(month_hidden_main_ten_god="七杀")))
        self.assertTrue(evaluate_conditions(
            {"field": "month_hidden_main_ten_god", "op": "nin", "value": ["正印"]},
            ctx(month_hidden_main_ten_god="七杀")))

    def test_contains_list(self):
        self.assertTrue(evaluate_conditions(
            {"field": "daily_sihua_roles", "op": "contains", "value": "化禄"},
            ctx(daily_sihua_roles=["化禄", "化忌"])))
        self.assertFalse(evaluate_conditions(
            {"field": "daily_sihua_roles", "op": "contains", "value": "化权"},
            ctx(daily_sihua_roles=["化禄", "化忌"])))

    def test_exists(self):
        self.assertTrue(evaluate_conditions(
            {"field": "soul_palace_main_star_key", "op": "exists", "value": True},
            ctx(soul_palace_main_star_key="TIANFU")))
        self.assertFalse(evaluate_conditions(
            {"field": "soul_palace_main_star_key", "op": "exists", "value": True},
            ctx(soul_palace_main_star_key=None)))
        self.assertTrue(evaluate_conditions(
            {"field": "soul_palace_main_star_key", "op": "exists", "value": False},
            ctx(soul_palace_main_star_key=None)))

    def test_regex(self):
        self.assertTrue(evaluate_conditions(
            {"field": "month_hidden_main_ten_god", "op": "regex", "value": "印"},
            ctx(month_hidden_main_ten_god="正印")))

    def test_missing_field_is_false_for_comparison(self):
        # field present in registry but value is None -> comparison fails
        self.assertFalse(evaluate_conditions(
            {"field": "soul_palace_main_star_key", "op": "eq", "value": "TIANFU"},
            ctx(soul_palace_main_star_key=None)))


class TestHardErrors(unittest.TestCase):
    def test_unknown_field_raises(self):
        with self.assertRaises(UnknownFieldError):
            evaluate_conditions(
                {"field": "day_master_elmnt", "op": "eq", "value": "WOOD"}, ctx())

    def test_unknown_operator_raises(self):
        with self.assertRaises(UnknownOperatorError):
            evaluate_conditions(
                {"field": "day_master_element", "op": "like", "value": "WOOD"}, ctx())


class TestSpecificity(unittest.TestCase):
    def test_leaf_count(self):
        self.assertEqual(count_conditions(None), 0)
        self.assertEqual(
            count_conditions({"field": "day_master_element", "op": "eq", "value": "WOOD"}),
            1,
        )
        self.assertEqual(
            count_conditions({"all": [
                {"field": "a", "op": "eq", "value": 1},
                {"any": [{"field": "b", "op": "eq", "value": 2}, {"field": "c", "op": "eq", "value": 3}]},
            ]}),
            3,
        )


def _rule(rule_id, stype, direction, polarity, conditions=None, precedence=0, spec_hint=None):
    return {
        "rule_id": rule_id,
        "produces_signal_type": stype,
        "applies_to_layers": ["BASELINE"],
        "evidence_refs": [f"E-{rule_id}-001"],
        "precedence": precedence,
        "specificity_hint": spec_hint,
        "conditions": conditions or {},
        "conclusion": {"produces_layer_output_template": {"direction": direction, "polarity": polarity}},
    }


class TestConflictResolution(unittest.TestCase):
    def test_unanimous_merges_refs(self):
        rules = [
            _rule("R-001", "SUPPORT", "STABLE", "active"),
            _rule("R-002", "SUPPORT", "STABLE", "active"),
        ]
        out = resolve_conflicts(rules)
        self.assertEqual(len(out), 1)
        self.assertEqual(sorted(out[0]["_rule_refs"]), ["R-001", "R-002"])
        self.assertEqual(sorted(out[0]["evidence_refs"]), ["E-R-001-001", "E-R-002-001"])

    def test_precedence_wins(self):
        rules = [
            _rule("R-001", "SUPPORT", "STABLE", "active", precedence=0),
            _rule("R-002", "SUPPORT", "INCREASE", "active", precedence=5),
        ]
        out = resolve_conflicts(rules)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["rule_id"], "R-002")

    def test_specificity_tiebreak_when_precedence_equal(self):
        cond_generic = {"all": [{"field": "day_master_element", "op": "eq", "value": "WOOD"}]}
        cond_specific = {"all": [
            {"field": "day_master_element", "op": "eq", "value": "WOOD"},
            {"field": "month_branch", "op": "eq", "value": "ZI"},
        ]}
        rules = [
            _rule("R-001", "SUPPORT", "STABLE", "active", conditions=cond_specific),
            _rule("R-002", "SUPPORT", "INCREASE", "active", conditions=cond_generic),
        ]
        out = resolve_conflicts(rules)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["rule_id"], "R-001")

    def test_tie_conflicting_is_dropped(self):
        rules = [
            _rule("R-001", "SUPPORT", "STABLE", "active"),
            _rule("R-002", "SUPPORT", "INCREASE", "active"),
        ]
        out = resolve_conflicts(rules)
        self.assertEqual(out, [])

    def test_different_types_coexist(self):
        rules = [
            _rule("R-001", "SUPPORT", "STABLE", "active"),
            _rule("R-002", "RESOURCE", "STABLE", "active"),
        ]
        out = resolve_conflicts(rules)
        self.assertEqual(len(out), 2)


class TestZWSihuaRules(unittest.TestCase):
    """ZW-405~408: §5.2 四化→USO mapping as rules (Block 2).

    Evaluated against a synthetic daily_sihua_roles context. These rules are
    NOT yet wired into DAILY_ACTIVATION (UR-012 records why); this test proves
    the matcher evaluates the mapping correctly.
    """

    @classmethod
    def setUpClass(cls):
        repo = Path(__file__).resolve().parents[2]
        loader = RuleLoader(repo / "backend" / "data", repo / "docs")
        cls.matcher = RuleMatcher(loader.rules)

    def test_sihua_subset_matches_only_present_roles(self):
        c = RuleContext(daily_sihua_roles=["化禄", "化忌"], layer="DAILY_ACTIVATION")
        matched = self.matcher.match_all(c, layer="DAILY_ACTIVATION")
        ids = {r["rule_id"] for r in matched}
        self.assertIn("ZW-405", ids)   # 化禄 present -> RESOURCE
        self.assertIn("ZW-408", ids)   # 化忌 present -> CONSTRAINT
        self.assertNotIn("ZW-406", ids)  # 化权 absent
        self.assertNotIn("ZW-407", ids)  # 化科 absent

    def test_sihua_resolution_produces_two_types(self):
        c = RuleContext(daily_sihua_roles=["化禄", "化忌"], layer="DAILY_ACTIVATION")
        matched = self.matcher.match_all(c, layer="DAILY_ACTIVATION")
        resolved = resolve_conflicts(matched)
        by_type = {r["produces_signal_type"] for r in resolved}
        self.assertEqual(by_type, {"RESOURCE", "CONSTRAINT"})

    def test_no_sihua_matches_nothing(self):
        c = RuleContext(daily_sihua_roles=[], layer="DAILY_ACTIVATION")
        matched = self.matcher.match_all(c, layer="DAILY_ACTIVATION")
        zw_ids = [r["rule_id"] for r in matched if r["rule_id"].startswith("ZW-")]
        self.assertEqual(zw_ids, [])


class TestZagiTransparencyGate(unittest.TestCase):
    """T301 杂气透干门槛:《论杂气如何取用》——辰戌丑未杂气月主气不透干不成格.

    非杂气月当令主气天然司权,无需透干;杂气月必须主气透干(本实现只做
    透干这一确定性判据,不实现会支)。
    """

    GATE = {
        "all": [
            {"field": "month_hidden_main_ten_god", "op": "eq", "value": "七杀"},
            {
                "any": [
                    {"field": "month_branch", "op": "nin",
                     "value": ["CHEN", "XU", "CHOU", "WEI"]},
                    {"field": "month_hidden_main_ten_god_transparent",
                     "op": "eq", "value": True},
                ]
            },
        ]
    }

    def test_zagi_month_blocked_when_not_transparent(self):
        # 戌月(杂气)主气戊土未透 -> 七杀格不取(GOLDEN-002 语义)
        c = ctx(month_hidden_main_ten_god="七杀", month_branch="XU",
                month_hidden_main_ten_god_transparent=False)
        self.assertFalse(evaluate_conditions(self.GATE, c))

    def test_zagi_month_fires_when_transparent(self):
        c = ctx(month_hidden_main_ten_god="七杀", month_branch="XU",
                month_hidden_main_ten_god_transparent=True)
        self.assertTrue(evaluate_conditions(self.GATE, c))

    def test_non_zagi_month_unconditional(self):
        # 巳月(非杂气)主气丙火当令司权,不受透干门槛限制(GOLDEN-004 语义)
        c = ctx(month_hidden_main_ten_god="七杀", month_branch="SI",
                month_hidden_main_ten_god_transparent=False)
        self.assertTrue(evaluate_conditions(self.GATE, c))

    def test_transparency_computation_real_charts(self):
        # GOLDEN-002 壬水/戌月:四柱 乙丙壬丙,主气戊未透 -> transparent=False
        be = BaziEngine()
        chart = be.compute((1955, 10, 28, 12), gender="male")
        rctx = build_rule_context(chart, None, None)
        self.assertEqual(month_hidden_main_ten_god("REN", "XU"), "七杀")
        self.assertIs(rctx.month_hidden_main_ten_god_transparent, False)

    def test_hidden_main_transparency_helper(self):
        self.assertTrue(hidden_main_stem_is_transparent("XU", ["YI", "WU", "REN", "BING"]))
        self.assertFalse(hidden_main_stem_is_transparent("XU", ["YI", "BING", "REN", "BING"]))
        self.assertTrue(hidden_main_stem_is_transparent("CHOU", ["DING", "JI", "GUI", "JIA"]))


class TestTier1TransparencyConfirmation(unittest.TestCase):
    """梯一「当令主气透干 → 格显性确认」ZPZ-111~120(实时接入,precedence 2).

    条件:month_hidden_main_ten_god eq X AND transparent eq true。主气透出时
    与当令司权/格局规则同型合并(rule_refs 取并集);不透出不触发。
    """

    REPO = Path(__file__).resolve().parents[2]

    @classmethod
    def setUpClass(cls):
        loader = RuleLoader(cls.REPO / "backend" / "data", cls.REPO / "docs")
        cls.matcher = RuleMatcher(loader.rules)

    def test_fires_only_when_main_qi_transparent(self):
        c = RuleContext(layer="BASELINE", month_hidden_main_ten_god="正印",
                        month_hidden_main_ten_god_transparent=True)
        ids = {r["rule_id"] for r in self.matcher.match_all(c, layer="BASELINE")}
        self.assertIn("ZPZ-111", ids)

        c2 = RuleContext(layer="BASELINE", month_hidden_main_ten_god="正印",
                         month_hidden_main_ten_god_transparent=False)
        ids2 = {r["rule_id"] for r in self.matcher.match_all(c2, layer="BASELINE")}
        self.assertNotIn("ZPZ-111", ids2)

    def test_ten_god_specific(self):
        c = RuleContext(layer="BASELINE", month_hidden_main_ten_god="七杀",
                        month_hidden_main_ten_god_transparent=True)
        ids = {r["rule_id"] for r in self.matcher.match_all(c, layer="BASELINE")}
        self.assertIn("ZPZ-120", ids)          # 七杀当令透出
        self.assertNotIn("ZPZ-111", ids)       # 正印不透出

    def test_merge_with_commanding_rules(self):
        # 甲日主/子月/正印当令且主气透出:ZPZ-001 + ZPZ-101 + ZPZ-108 + ZPZ-111
        # 全部 SUPPORT STABLE active -> T205 同结论合并为单条 signal
        c = RuleContext(
            layer="BASELINE",
            day_master="JIA", day_master_element="WOOD", month_branch="ZI",
            month_hidden_main_ten_god="正印",
            month_hidden_main_ten_god_transparent=True,
        )
        resolved = resolve_conflicts(self.matcher.match_all(c, layer="BASELINE"))
        support = [r for r in resolved if r["produces_signal_type"] == "SUPPORT"]
        self.assertEqual(len(support), 1)
        refs = support[0].get("_rule_refs")
        for rid in ("ZPZ-001", "ZPZ-101", "ZPZ-108", "ZPZ-111"):
            self.assertIn(rid, refs, f"missing {rid} in merged refs {refs}")


class TestTransparentTenGodsRules(unittest.TestCase):
    """梯二「非当令十神透干显性」ZPZ-121~130(透则显).

    T501 后接入(2026-08-17):build_rule_context 已填充 transparent_ten_gods,
    实时上下文梯二规则触发(非当令十神透干显性)。规则以
    month_hidden_main_ten_god ne X 排除当令情形(当令交给梯一/司权/格局)。
    """

    REPO = Path(__file__).resolve().parents[2]

    @classmethod
    def setUpClass(cls):
        loader = RuleLoader(cls.REPO / "backend" / "data", cls.REPO / "docs")
        cls.matcher = RuleMatcher(loader.rules)

    def test_helper_computes_three_stems(self):
        # 日主不参与透干:只算年月时三干
        self.assertEqual(
            transparent_ten_gods("JIA", "GUI", "BING", "GENG"),
            ["正印", "食神", "七杀"],
        )
        self.assertEqual(
            transparent_ten_gods("JIA", "JIA", "BING", "WU"),
            ["比肩", "食神", "偏财"],
        )

    def test_live_context_populates_and_fires(self):
        # 实时 build_rule_context 已填充 transparent_ten_gods -> 梯二在真实管道触发
        eng = BaziEngine()
        chart = eng.compute((1984, 12, 7, 16), gender="male")  # GOLDEN-001 甲子/丙子/乙亥/甲申
        ctx = build_rule_context(chart, None, None, layer="BASELINE")
        self.assertIsNotNone(ctx.transparent_ten_gods)
        self.assertIn("劫财", ctx.transparent_ten_gods)  # 年月时三干对乙木
        ids = {r["rule_id"] for r in self.matcher.match_all(ctx, layer="BASELINE")}
        t2 = {rid for rid in ids if rid.startswith("ZPZ-12")}
        # 当令主气为偏印(子藏癸);劫财/伤官非当令且透出 -> ZPZ-124/126 触发
        self.assertIn("ZPZ-124", t2, f"劫财透未触发: {sorted(t2)}")
        self.assertIn("ZPZ-126", t2, f"伤官透未触发: {sorted(t2)}")

    def test_non_commanding_transparent_ten_god_fires(self):
        c = RuleContext(layer="BASELINE",
                        transparent_ten_gods=["正印", "食神"],
                        month_hidden_main_ten_god="七杀")
        ids = {r["rule_id"] for r in self.matcher.match_all(c, layer="BASELINE")}
        self.assertIn("ZPZ-121", ids)   # 正印透(非当令)
        self.assertIn("ZPZ-125", ids)   # 食神透
        self.assertNotIn("ZPZ-129", ids)  # 正官未透
        self.assertNotIn("ZPZ-123", ids)  # 比肩未透

    def test_commanding_same_ten_god_excluded(self):
        # 当令者与透出者同为 X -> 梯二用 ne 排除,交给梯一/司权/格局
        c = RuleContext(layer="BASELINE",
                        transparent_ten_gods=["正印"],
                        month_hidden_main_ten_god="正印")
        ids = {r["rule_id"] for r in self.matcher.match_all(c, layer="BASELINE")}
        self.assertNotIn("ZPZ-121", ids)


class TestT301RulesLoad(unittest.TestCase):
    """T301《子平真诠》规则(ZPZ-101~130)经 RuleLoader 装载并通过 schema 校验。

    含梯一透干规则(ZPZ-111~120,实时)与梯二透干规则(ZPZ-121~130,draft 缓接)。
    """

    REPO = Path(__file__).resolve().parents[2]

    def test_t301_rules_present_and_validate(self):
        loader = RuleLoader(self.REPO / "backend" / "data", self.REPO / "docs")
        ids = {r["rule_id"] for r in loader.rules}
        expected = {f"ZPZ-{n:03d}" for n in range(101, 131)}
        self.assertTrue(expected.issubset(ids), f"missing T301 rules: {expected - ids}")
        # 全部规则(6 种子 + 30 T301)证据闭合
        missing = loader.verify_evidence_refs()
        self.assertEqual(missing, [], f"unresolved evidence refs: {missing}")


class TestRuleLoader(unittest.TestCase):
    # project root = 通书-claude (parents[2] of backend/tests/test_matcher.py)
    REPO = Path(__file__).resolve().parents[2]
    SCHEMA_DIR = REPO / "docs"

    def test_seed_rules_validate_and_evidence_closes(self):
        # Real repo data dir: every rule validates against rule.schema.json 1.1
        # and every evidence_ref resolves (DoD #4 for the seed set).
        loader = RuleLoader(self.REPO / "backend" / "data", self.SCHEMA_DIR)
        self.assertGreaterEqual(len(loader.rules), 6)
        missing = loader.verify_evidence_refs()
        self.assertEqual(missing, [], f"unresolved evidence refs: {missing}")

    def test_invalid_rule_rejected(self):
        # A malformed rule must fail at load time (加载即校验).
        with tempfile.TemporaryDirectory() as tmp:
            rules_dir = Path(tmp) / "rules"
            evidence_dir = Path(tmp) / "evidence"
            rules_dir.mkdir()
            evidence_dir.mkdir()
            (rules_dir / "BAD-001.json").write_text(
                json.dumps({"rule_id": "BAD-001"}), encoding="utf-8"
            )
            with self.assertRaises(RuleLoadError):
                RuleLoader(Path(tmp), self.SCHEMA_DIR)


class TestLifecycleStatusFilter(unittest.TestCase):
    """手册 §8.7 / DECISION-010:仅 validated+active 参与生产推理,draft/review 惰性。

    P1-01 D3:matcher.match_all 只匹配 EXECUTABLE_STATUSES;15 条新
    DTS/SMTH/YHZP 规则全部 draft,不得在任何命局下产出信号。
    """

    REPO = Path(__file__).resolve().parents[2]

    def _matcher(self):
        loader = RuleLoader(self.REPO / "backend" / "data", self.REPO / "docs")
        return RuleMatcher(loader.rules), loader.rules

    def _ctx(self, day_master="JIA", month_branch="YIN", hour_branch="WU"):
        # 构造最小 RuleContext:甲日、寅月(比肩司权→DTS-101 得令命中)、午时。
        return RuleContext(
            day_master=day_master,
            day_master_element="WOOD",
            day_branch="YIN",
            month_stem="BING",
            month_branch=month_branch,
            year_stem="JIA",
            year_branch="YIN",
            hour_stem="WU",
            hour_branch=hour_branch,
            month_hidden_main_ten_god="比肩",
            day_master_stage_month="临官",
            day_master_road_month=True,
            day_master_absolute_month=True,
            day_branch_main_ten_god="比肩",
            tianyi_guiren_branches=["YIN", "WU"],
            layer="BASELINE",
            theme="WORK",
        )

    def test_draft_rules_excluded_from_match(self):
        matcher, rules = self._matcher()
        ctx = self._ctx()
        hits = {m["rule_id"] for m in matcher.match_all(ctx, layer="BASELINE")}
        # 15 条新规则全部 draft,不得命中(其条件对本 ctx 大多为真)。
        for rid in ("DTS-101", "SMTH-101", "SMTH-103", "SMTH-104", "YHZP-101"):
            self.assertNotIn(rid, hits, f"draft rule {rid} leaked into production match")
        # active 规则仍正常匹配(如 ZPZ-101 印绶当令——本 ctx 主气比肩,不命中,但 ZPZ-101 是 active)
        self.assertTrue(
            all(
                rules_by_id(rules, h)["status"] in ("validated", "active")
                for h in hits
            ),
            "matched rules must be executable (validated/active)",
        )

    def test_all_new_rules_are_draft(self):
        loader = RuleLoader(self.REPO / "backend" / "data", self.REPO / "docs")
        new = {
            r["rule_id"]: r["status"]
            for r in loader.rules
            if r["rule_id"].startswith(("DTS-", "SMTH-", "YHZP-"))
        }
        self.assertEqual(len(new), 17, f"expect 17 new rules, got {sorted(new)}")
        self.assertTrue(
            all(s == "draft" for s in new.values()),
            f"all new classical rules must be draft(§8.7 禁止 AI 自动 Active): {new}",
        )

    def test_new_field_rules_link_closure(self):
        # D2b:15 条新规则 schema 校验 + book_id/passage_id/concept_id 链接闭合。
        loader = RuleLoader(self.REPO / "backend" / "data", self.REPO / "docs")
        kb = KbLoader(self.REPO / "backend" / "data", self.REPO / "docs")
        viol = kb.verify_link_closure(loader.rules)
        self.assertEqual(viol, [], f"KB link closure broken: {viol}")
        for r in loader.rules:
            if r["rule_id"].startswith(("DTS-", "SMTH-", "YHZP-")):
                self.assertTrue(r.get("book_id"), f"{r['rule_id']} missing book_id")
                self.assertTrue(r.get("passage_id"), f"{r['rule_id']} missing passage_id")

    def test_tianyi_field_derives_guiren_branches(self):
        # 天乙贵人字段:甲日查支(甲戊庚见丑未)→ 命局含 CHOU/WEI 则填充。
        bazi = BaziEngine().compute((1984, 12, 7, 16), gender="male")  # 甲子日
        ctx = build_rule_context(bazi, None, None, layer="BASELINE", theme="WORK")
        self.assertIsInstance(ctx.tianyi_guiren_branches, list)


def rules_by_id(rules, rid):
    return next(r for r in rules if r["rule_id"] == rid)


if __name__ == "__main__":
    unittest.main()
