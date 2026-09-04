# -*- coding: utf-8 -*-
"""P1-PALACE-LAYER 測試：PalaceFeatureCalculator 與宮位語義加載。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.engines.blind.palace import (
    PalaceState,
    PalaceRule,
    PalaceFeatureCalculator,
)


class TestPalaceState(unittest.TestCase):
    """PalaceState 數據類基本測試。"""

    def test_create_default(self):
        """測試默認構造。"""
        ps = PalaceState()
        self.assertEqual(ps.year_pillar, "年柱")
        self.assertEqual(ps.month_pillar, "月柱")
        self.assertEqual(ps.day_pillar, "日柱")
        self.assertEqual(ps.hour_pillar, "時柱")
        self.assertEqual(ps.semantics, {})

    def test_create_with_values(self):
        """測試帶參數構造。"""
        ps = PalaceState(
            year_stem="甲",
            year_branch="子",
            month_stem="乙",
            month_branch="丑",
            day_stem="丙",
            day_branch="寅",
            hour_stem="丁",
            hour_branch="卯",
        )
        self.assertEqual(ps.year_stem, "甲")
        self.assertEqual(ps.day_branch, "寅")
        self.assertEqual(ps.hour_stem, "丁")

    def test_frozen(self):
        """測試 frozen 屬性。"""
        ps = PalaceState()
        with self.assertRaises(AttributeError):
            ps.year_stem = "新值"  # type: ignore


class TestPalaceRule(unittest.TestCase):
    """PalaceRule 數據類測試。"""

    def test_create_rule(self):
        """測試宮位規則創建。"""
        rule = PalaceRule(
            palace="年柱",
            semantics=["父母宮", "祖上宮"],
            source="《盲派命理》第1章",
            confidence=0.9,
        )
        self.assertEqual(rule.palace, "年柱")
        self.assertEqual(rule.semantics, ["父母宮", "祖上宮"])
        self.assertEqual(rule.source, "《盲派命理》第1章")
        self.assertEqual(rule.confidence, 0.9)

    def test_frozen(self):
        """測試 Rule frozen 屬性。"""
        rule = PalaceRule(
            palace="年柱",
            semantics=["父母宮"],
            source="test",
        )
        with self.assertRaises(AttributeError):
            rule.palace = "新值"  # type: ignore


class TestPalaceFeatureCalculator(unittest.TestCase):
    """PalaceFeatureCalculator 功能測試。"""

    def setUp(self):
        """準備測試環境。"""
        self.calc = PalaceFeatureCalculator()

    def test_load_rules_from_file(self):
        """測試從 JSON 文件加載規則。"""
        rules = self.calc.list_all_rules()
        self.assertGreater(len(rules), 0)
        # 檢查至少有年柱規則
        palaces = [r["palace"] for r in rules]
        self.assertIn("年柱", palaces)
        self.assertIn("月柱", palaces)
        self.assertIn("日柱", palaces)
        self.assertIn("時柱", palaces)

    def test_calculate_palace_state(self):
        """測試宮位狀態計算。"""
        ps = self.calc.calculate(
            year_stem="甲",
            year_branch="子",
            month_stem="乙",
            month_branch="丑",
            day_stem="丙",
            day_branch="寅",
            hour_stem="丁",
            hour_branch="卯",
        )
        self.assertEqual(ps.year_stem, "甲")
        self.assertEqual(ps.day_branch, "寅")
        self.assertEqual(ps.hour_stem, "丁")
        self.assertIn("年柱", ps.semantics)
        self.assertIn("父母宮", ps.semantics["年柱"])

    def test_get_palace_semantics(self):
        """測試獲取宮位語義。"""
        semantics = self.calc.get_palace_semantics("年柱")
        self.assertIsInstance(semantics, list)
        self.assertGreater(len(semantics), 0)
        # 應該包含父母宮
        self.assertTrue(any("父母" in s for s in semantics))

    def test_get_palace_source(self):
        """測試獲取宮位來源。"""
        source = self.calc.get_palace_source("年柱")
        self.assertIsInstance(source, str)
        self.assertGreater(len(source), 0)
        # 應該包含《盲派命理》
        self.assertIn("盲派", source)

    def test_semantics_loaded_from_file(self):
        """測試語義從文件加載而非硬編碼。"""
        # 檢查 semantics 字典不為空
        ps = self.calc.calculate(
            year_stem="甲", year_branch="子",
            month_stem="乙", month_branch="丑",
            day_stem="丙", day_branch="寅",
            hour_stem="丁", hour_branch="卯",
        )
        self.assertGreater(len(ps.semantics), 0)
        # 檢查語義包含「宮」字
        self.assertTrue(any("宮" in s for s in ps.semantics.get("年柱", [])))

    def test_all_four_palaces_have_semantics(self):
        """測試四柱都有語義。"""
        for palace in ["年柱", "月柱", "日柱", "時柱"]:
            semantics = self.calc.get_palace_semantics(palace)
            self.assertGreater(len(semantics), 0, f"{palace} 應有語義")

    def test_rule_confidence_range(self):
        """測試規則置信度範圍。"""
        rules = self.calc.list_all_rules()
        for rule in rules:
            self.assertGreaterEqual(rule["confidence"], 0.0)
            self.assertLessEqual(rule["confidence"], 1.0)


if __name__ == "__main__":
    unittest.main()
