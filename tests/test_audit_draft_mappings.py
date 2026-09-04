"""DRAFT Mapping 批量审核工具测试(2026-08-21,M-LC-01 前置)。

覆盖:
  1. 十神本体表: 10 十神 → 期望 ontology_type(印=SUPPORT/比劫=RELATION/食伤=OUTPUT/财=RESOURCE/官杀=CONSTRAINT)。
  2. scan_rule_ten_gods: 递归提取 conditions 中 ten_god 取值。
  3. run_audit(): 10 mapping 全过 schema、35 条 rule_ref 全解析、ZPZ-101..130 全覆盖、
     单神规则零双引、每 mapping 结论 PASS、跨映射发现含 M-LC-01(BLOCK)。
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

_SPEC = importlib.util.spec_from_file_location(
    "audit_draft_mappings", REPO / "backend" / "scripts" / "audit_draft_mappings.py"
)
AUDIT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(AUDIT)


class TestOntologyTable(unittest.TestCase):
    def test_god_ontology(self):
        # 生我=SUPPORT / 同我=RELATION / 我生=OUTPUT / 我克=RESOURCE / 克我=CONSTRAINT
        self.assertEqual(AUDIT.GOD_ONTOLOGY["正印"], "SUPPORT")
        self.assertEqual(AUDIT.GOD_ONTOLOGY["偏印"], "SUPPORT")
        self.assertEqual(AUDIT.GOD_ONTOLOGY["比肩"], "RELATION")
        self.assertEqual(AUDIT.GOD_ONTOLOGY["劫财"], "RELATION")
        self.assertEqual(AUDIT.GOD_ONTOLOGY["食神"], "OUTPUT")
        self.assertEqual(AUDIT.GOD_ONTOLOGY["伤官"], "OUTPUT")
        self.assertEqual(AUDIT.GOD_ONTOLOGY["正财"], "RESOURCE")
        self.assertEqual(AUDIT.GOD_ONTOLOGY["偏财"], "RESOURCE")
        self.assertEqual(AUDIT.GOD_ONTOLOGY["正官"], "CONSTRAINT")
        self.assertEqual(AUDIT.GOD_ONTOLOGY["七杀"], "CONSTRAINT")
        self.assertEqual(set(AUDIT.GOD_ONTOLOGY), AUDIT.EXPECTED_GODS, "十神表必须覆盖恰好 10 个")

    def test_families_include_aliases(self):
        self.assertEqual(AUDIT.GOD_FAMILIES["正印"], {"正印", "偏印", "印绶", "印"})
        self.assertEqual(AUDIT.GOD_FAMILIES["偏印"], {"偏印", "枭神"})
        self.assertEqual(AUDIT.GOD_FAMILIES["七杀"], {"七杀", "偏官"})


class TestScanRuleTenGods(unittest.TestCase):
    def test_extracts_gods_from_all_any(self):
        rule = {"conditions": {"all": [
            {"field": "month_hidden_main_ten_god", "op": "in", "value": ["正印", "偏印"]},
            {"any": [{"field": "x", "op": "eq", "value": 1}]},
        ]}}
        self.assertEqual(AUDIT.scan_rule_ten_gods(rule), {"正印", "偏印"})

    def test_ignores_non_ten_god_fields(self):
        rule = {"conditions": {"all": [{"field": "month_branch", "op": "in", "value": ["CHEN", "XU"]}]}}
        self.assertEqual(AUDIT.scan_rule_ten_gods(rule), set())

    def test_nested_scan(self):
        rule = {"conditions": {"all": [
            {"field": "month_hidden_main_ten_god", "op": "eq", "value": "七杀"},
            {"any": [{"field": "transparent", "op": "eq", "value": True}]},
        ]}}
        self.assertEqual(AUDIT.scan_rule_ten_gods(rule), {"七杀"})


class TestRunAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries, cls.per_mapping, cls.all_findings, cls.cross, cls.rules, cls.decisions = AUDIT.run_audit()

    def test_ten_mappings_all_pass(self):
        self.assertEqual(len(self.entries), 10)
        self.assertEqual(set(self.per_mapping), {f"MAP-{i}" for i in range(1001, 1011)})
        for mid, v in self.per_mapping.items():
            self.assertEqual(v, "PASS", f"{mid} 应 PASS: {self.all_findings[mid]}")

    def test_rule_refs_all_resolved(self):
        # 35 条 rule_ref 全解析(B-01 PASS);ZPZ-101..130 全覆盖(B-03 PASS)
        for mid, f in self.all_findings.items():
            self.assertTrue(any(x.check == "B-01" and x.severity == "PASS" for x in f), mid)
        self.assertTrue(any(x.check == "B-03" and x.severity == "PASS" for x in self.cross))

    def test_ontology_consistency_per_rule(self):
        # C-02(逐 rule_ref signal==mapping ontology)全 PASS
        for mid, f in self.all_findings.items():
            self.assertTrue(any(x.check == "C-02" and x.severity == "PASS" for x in f),
                            f"{mid} 应有 C-02 PASS: {[x.text for x in f]}")

    def test_shared_rules_are_family_rules(self):
        # ZPZ-101..105(当令族规则)双引合法;B-02 无 REVIEW(单神规则零双引)
        self.assertFalse(any(x.check == "B-02" and x.severity == "REVIEW" for x in self.cross))

    def test_mlc01_blocked_by_status_gate(self):
        # M-LC-01: 已加 status 门控，检测应 PASS 而非 BLOCK
        blocks = [x for x in self.cross if x.severity == "BLOCK"]
        self.assertFalse(any("M-LC-01" in x.text for x in blocks), "M-LC-01 应已修复")
        self.assertTrue(any(x.check == "F-01" and x.severity == "PASS" for x in self.cross))

    def test_source_term_and_theme_unique(self):
        terms = [e["source_term"] for e in self.entries]
        themes = [e["modern_theme"] for e in self.entries]
        self.assertEqual(len(set(terms)), 10)
        self.assertEqual(len(set(themes)), 10)

    def test_ten_god_coverage_complete(self):
        self.assertTrue(any(x.check == "A-04" and x.severity == "PASS" for x in self.cross))


if __name__ == "__main__":
    unittest.main()
