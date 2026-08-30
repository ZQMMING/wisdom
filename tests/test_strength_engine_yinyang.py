"""P2-D1R1: D1 从格阴阳修正专项测试 — [DEPRECATED] stub 兼容性验证.

TASK-001: evaluate_strength 已退回 UNRESOLVED stub.
本文件验证 stub 的 API 契约(结构完整性 + UNRESOLVED 标记).
"""
from __future__ import annotations

import unittest

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.strength_engine import evaluate_strength  # [DEPRECATED] LEGACY/RESEARCH_ONLY — 测试兼容性


class TestYinYangCongGe(unittest.TestCase):
    def setUp(self):
        self.eng = BaziEngine()

    def _eval(self, y, m, d, h, gender):
        chart = self.eng.compute((y, m, d, h), gender=gender)
        return chart, evaluate_strength(chart)

    # ---- stub 兼容性测试 ----

    def test_stub_returns_valid_result(self):
        """stub 必须返回合法 D1StrengthResult, 字段完整."""
        _, r = self._eval(1914, 2, 17, 0, "male")
        self.assertIsNotNone(r.day_master_element)
        self.assertEqual(r.verdict, "")
        self.assertIn("DEPRECATED", r.verdict_condition)

    def test_all_cases_unresolved(self):
        """多命例验证: 所有调用均返回 UNRESOLVED."""
        cases = [
            (1914, 2, 17, 0, "male"),
            (1920, 12, 14, 12, "male"),
        ]
        for y, m, d, h, g in cases:
            _, r = self._eval(y, m, d, h, g)
            self.assertEqual(r.verdict, "", f"{y}-{m}-{d} {g} 应返回 UNRESOLVED")
