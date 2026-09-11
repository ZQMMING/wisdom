# -*- coding: utf-8 -*-
"""BlindPaiEngine（V2 主引擎）测试。

生产路径：FrozenBaziState → 宾主 → 体用 → 做功图 → 做功链 → 做功强弱 → 功神 → 证据
案例：1980-06-22 10:00 男 广州 → 庚申 壬午 丙寅 癸巳
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import unittest

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.blind.engine import (
    BlindPaiEngine,
    GongShenRole,
    MethodScope,
    WorkEfficiency,
)
from tongshu.engines.blind.evidence_producer import Relevance


class TestBlindPaiEngineBasics(unittest.TestCase):
    """基础：输入、主入口、完整性。"""

    @classmethod
    def setUpClass(cls) -> None:
        chart = BaziEngine().compute((1980, 6, 22, 10), gender="male")
        cls.engine = BlindPaiEngine()
        cls.result = cls.engine.compute_from_chart(chart, (1980, 6, 22, 10), gender="male")

    def test_01_frozen_bazi_pillars(self) -> None:
        """对外输出四柱 = 庚申 壬午 丙寅 癸巳（中文可读层）。"""
        d = self.result.to_dict()
        self.assertEqual(d["frozen"]["pillars"], ["庚申", "壬午", "丙寅", "癸巳"])
        # 内部事实层保持拼音码（与 BaziChart 一致）
        self.assertEqual(self.result.frozen.pillars, ("GENGSHEN", "RENWU", "BINGYIN", "GUISI"))

    def test_02_day_master(self) -> None:
        self.assertEqual(self.result.to_dict()["frozen"]["day_master"], "丙")

    def test_03_method_scope(self) -> None:
        self.assertEqual(self.result.method_scope, MethodScope.DUAN_JIANYE.value)

    def test_04_host_guest_daypillar(self) -> None:
        """宾主：日支为主，年月时为宾（BG-001）。"""
        d = self.result.to_dict()
        self.assertIn("寅", d["host_guest"]["main_branches"])
        self.assertIn("申", d["host_guest"]["guest_branches"])

    def test_05_no_numeric_scores(self) -> None:
        """合规：输出中不得出现 strength/direction 数字或 score/weight 字段。"""
        d = self.result.to_dict()
        blob = repr(d)
        self.assertNotIn("strength", blob)
        self.assertNotIn("score", blob)
        self.assertNotIn("weight", blob)
        self.assertNotIn("efficiency=95", blob)
        self.assertNotIn("0.5", blob)

    def test_06_evidence_no_polarity(self) -> None:
        """证据项无 direction/polarity/strength（新契约）。"""
        for item in self.result.evidence:
            self.assertFalse(hasattr(item, "strength"))
            self.assertFalse(hasattr(item, "direction"))
            self.assertFalse(hasattr(item, "polarity"))

    def test_07_work_efficiency_enum(self) -> None:
        """做功强弱为枚举，且落在四档内。"""
        eff = self.result.work_efficiency.efficiency
        self.assertIn(eff, {WorkEfficiency.LARGE, WorkEfficiency.MEDIUM,
                            WorkEfficiency.SMALL, WorkEfficiency.NONE,
                            WorkEfficiency.UNDETERMINED})

    def test_08_rules_triggered(self) -> None:
        """规则触发记录非空。"""
        self.assertTrue(self.result.rules_triggered)
        self.assertIn("BG-001", self.result.rules_triggered)

    def test_09_to_dict_complete(self) -> None:
        """to_dict 含全部 10 段输出。"""
        d = self.result.to_dict()
        for key in ("method_scope", "frozen", "host_guest", "body_use",
                    "work_graph", "work_chains", "work_efficiency",
                    "gong_shen", "palace", "evidence", "rules_triggered"):
            self.assertIn(key, d)


class TestBlindPaiEngineNegative(unittest.TestCase):
    """负例：fail-closed。"""

    def test_10_no_chart_raises(self) -> None:
        """无 chart 时禁止引擎自行排盘（FrozenBaziState 只消费）。"""
        engine = BlindPaiEngine()
        with self.assertRaises(ValueError):
            engine.compute((1980, 6, 22, 10), gender="male")

    def test_11_evidence_relevance_enum(self) -> None:
        """证据相关性为枚举（高/中/低），非数字。"""
        chart = BaziEngine().compute((1980, 6, 22, 10), gender="male")
        result = BlindPaiEngine().compute_from_chart(chart, (1980, 6, 22, 10))
        for item in result.evidence:
            self.assertIn(item.relevance, Relevance.values())


if __name__ == "__main__":
    unittest.main()
