"""P2-d: 判定引擎方向性验证 — Golden 数据集对齐测试.

【DEPRECATED】evaluate_strength 已退回 UNRESOLVED stub (TASK-001).
本文件验证 stub 兼容性: judgment 引擎在空 verdict 时不崩溃.
Golden 数据集方向性验证移至新的 CanonicalState 驱动测试.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from tongshu.engines.bazi_engine import BaziEngine, STEM_ELEMENT
from tongshu.engines.strength_engine import evaluate_strength  # [DEPRECATED] LEGACY/RESEARCH_ONLY — 测试兼容性
from tongshu.engines.judgment_engine import judgment


class TestP2DirectionGolden(unittest.TestCase):
    """验证判定引擎在 stub 模式下的兜底行为."""

    def setUp(self):
        self.eng = BaziEngine()
        golden_path = Path(__file__).resolve().parent.parent / "dataset" / "golden_v1" / "golden_cases.json"
        self.golden_data = json.loads(golden_path.read_text(encoding="utf-8"))

    def _eval_with_judgment(self, birth_date: str, birth_hour: int, gender: str):
        """计算命盘并执行 P2 判定."""
        parts = birth_date.split("-")
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        chart = self.eng.compute((y, m, d, birth_hour), gender=gender)
        d1 = evaluate_strength(chart)
        return chart, d1, judgment(chart, d1)

    # ---- stub 兼容性测试 ----

    def test_stub_verdict_is_empty(self):
        """verify: evaluate_strength 已退回 UNRESOLVED."""
        _, d1, _ = self._eval_with_judgment("1724-08-03", 12, "male")
        self.assertEqual(d1.verdict, "")
        self.assertIn("DEPRECATED", d1.verdict_condition)

    def test_judgment_handles_empty_verdict(self):
        """judgment 应能处理 d1.verdict=="" 的情况, 不抛出异常."""
        cases = [
            ("1724-08-03", 12, "male"),
            ("1985-12-03", 8, "female"),
            ("2000-02-29", 14, "male"),
        ]
        for birth_date, birth_hour, gender in cases:
            _, d1, r = self._eval_with_judgment(birth_date, birth_hour, gender)
            self.assertEqual(d1.verdict, "", f"{birth_date} {gender} 应返回 UNRESOLVED")
            # judgment 不应崩溃
            self.assertIsNotNone(r)
