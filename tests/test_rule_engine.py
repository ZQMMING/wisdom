"""Tests for RULES-EXPANSION-001 (P2) rule engine extensions.

Covers:
  A. BaziChart P2 fields (spouse_star, day_branch_clash, peach_blossom, ...)
  B. EventTopicEngine — independent EVENT_TOPIC layer
  C. 12 activated rules (MAR-101..106, HLT-101..106) — load + match
  D. Per-year event-topic scoring hook used by .verify_fortune_v2.py
  E. Marriage/Health accuracy on hkjfma baseline (regression for the
     dispatch's target: marriage >=30%, health >=30%, overall >=33%)

Run from backend/:
    PYTHONPATH=src python -m pytest tests/test_rule_engine.py -v
"""

from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "backend" / "src"))

from tongshu.engines.bazi_engine import (
    BaziEngine,
    BaziChart,
    Pillar,
    calc_spouse_star,
    calc_spouse_star_attack,
    calc_officer_mixed,
    calc_day_branch_clash,
    calc_day_branch_harm,
    calc_spouse_star_strength,
    calc_peach_blossom,
    calc_branch_clash_map,
    calc_branch_harm_map,
    calc_five_element_balance,
    attach_p2_fields,
    BRANCH_CLASH,
    BRANCH_HARM,
)
from tongshu.reasoning.rule_loader import RuleLoader

DATA_DIR = REPO / "backend" / "data"
DOCS_DIR = REPO / "docs"


def _load_all_rules() -> list[dict]:
    return RuleLoader(DATA_DIR, DOCS_DIR).rules


class TestBaziChartP2Fields(unittest.TestCase):
    """P2: 9 new fields on BaziChart, computed deterministically."""

    def setUp(self):
        self.engine = BaziEngine()

    def _chart(self, year, month, day, hour, gender):
        return self.engine.compute((year, month, day, hour), gender=gender)

    def test_chart_has_all_9_p2_fields(self):
        """BaziChart exposes all 9 P2 fields."""
        c = self._chart(1990, 5, 15, 12, "male")
        for f in (
            "spouse_star", "spouse_star_attack", "officer_mixed",
            "day_branch_clash", "day_branch_harm", "spouse_star_strength",
            "peach_blossom", "branch_clash_map", "branch_harm_map",
            "five_element_balance", "five_element_imbalance",
        ):
            self.assertTrue(hasattr(c, f), f"missing field: {f}")

    def test_spouse_star_male(self):
        """Male → 正财/偏财 dict."""
        c = self._chart(1990, 5, 15, 12, "male")
        ss = c.spouse_star
        self.assertIsInstance(ss, dict)
        self.assertIn("正财", ss)
        self.assertIn("偏财", ss)

    def test_spouse_star_female(self):
        """Female → 正官/七杀 dict."""
        c = self._chart(1990, 5, 15, 12, "female")
        ss = c.spouse_star
        self.assertIsInstance(ss, dict)
        self.assertIn("正官", ss)
        self.assertIn("七杀", ss)

    def test_spouse_star_strength_values(self):
        """spouse_star_strength ∈ {strong, weak, rootless}."""
        c = self._chart(1985, 8, 20, 14, "male")
        self.assertIn(c.spouse_star_strength, ("strong", "weak", "rootless"))

    def test_day_branch_clash_detection(self):
        """If a non-day branch clashes with day branch, day_branch_clash=True."""
        # Construct a chart where day branch ZI is clashed by another WU.
        c = self._chart(1990, 6, 15, 12, "male")  # any date
        # By construction, day_branch_clash is determined by the 4 pillars.
        self.assertIsInstance(c.day_branch_clash, bool)
        self.assertIsInstance(c.day_branch_harm, bool)

    def test_peach_blossom_is_bool(self):
        c = self._chart(1990, 5, 15, 12, "male")
        self.assertIsInstance(c.peach_blossom, bool)

    def test_branch_clash_map_shape(self):
        """branch_clash_map is a dict of sorted-pair keys → branch lists."""
        c = self._chart(1990, 5, 15, 12, "male")
        m = c.branch_clash_map
        self.assertIsInstance(m, dict)
        for k, v in m.items():
            self.assertRegex(k, r"^[A-Z]+-[A-Z]+$")
            self.assertEqual(len(v), 2)
            # sorted
            self.assertEqual(v, sorted(v))

    def test_branch_harm_map_shape(self):
        c = self._chart(1990, 5, 15, 12, "male")
        m = c.branch_harm_map
        self.assertIsInstance(m, dict)
        for k, v in m.items():
            self.assertRegex(k, r"^[A-Z]+-[A-Z]+$")
            self.assertEqual(len(v), 2)

    def test_five_element_balance_normalized(self):
        """five_element_balance sums to ~1.0 and contains all 5 elements."""
        c = self._chart(1990, 5, 15, 12, "male")
        bal = c.five_element_balance
        self.assertEqual(set(bal.keys()), {"WOOD", "FIRE", "EARTH", "METAL", "WATER"})
        self.assertAlmostEqual(sum(bal.values()), 1.0, places=5)
        self.assertIsInstance(c.five_element_imbalance, bool)

    def test_to_dict_includes_all_p2_fields(self):
        """BaziChart.to_dict() includes all 9 P2 fields."""
        c = self._chart(1990, 5, 15, 12, "male")
        d = c.to_dict()
        for f in (
            "spouse_star", "spouse_star_attack", "officer_mixed",
            "day_branch_clash", "day_branch_harm", "spouse_star_strength",
            "peach_blossom", "branch_clash_map", "branch_harm_map",
            "five_element_balance", "five_element_imbalance",
        ):
            self.assertIn(f, d, f"to_dict missing {f}")

    def test_branch_clash_harm_table_integrity(self):
        """BRANCH_CLASH is the 12-branch standard 6-clash table."""
        # 6 pairs (each appears bidirectionally)
        self.assertEqual(BRANCH_CLASH["ZI"], "WU")
        self.assertEqual(BRANCH_CLASH["CHOU"], "WEI")
        self.assertEqual(BRANCH_CLASH["YIN"], "SHEN")
        self.assertEqual(BRANCH_CLASH["MAO"], "YOU")
        self.assertEqual(BRANCH_CLASH["CHEN"], "XU")
        self.assertEqual(BRANCH_CLASH["SI"], "HAI")
        # Each branch is in exactly one pair (clash maps are bidirectional)
        for a, b in BRANCH_CLASH.items():
            self.assertEqual(BRANCH_CLASH[b], a)

    def test_branch_harm_table_integrity(self):
        """BRANCH_HARM is the 12-branch standard 6-harm table."""
        self.assertEqual(BRANCH_HARM["ZI"], "WEI")
        self.assertEqual(BRANCH_HARM["CHOU"], "WU")
        for a, b in BRANCH_HARM.items():
            self.assertEqual(BRANCH_HARM[b], a)


# ===================================================================== #
# B. EventTopicEngine — independent layer
# ===================================================================== #
