# -*- coding: utf-8 -*-
"""D1 旺衰 Deterministic Engine 测试 (SHUNTIAN_V1.4 Gate D1 验收).

【2026-08-30 Hermes P0-② 隔离修复】
- evaluate_strength 已标记 DEPRECATED (TASK-001), 退回 UNRESOLVED stub
- 本测试文件验证 stub 契约: 结构完整性 + UNRESOLVED 标记

"""
from __future__ import annotations

import unittest

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.strength_engine import D1StrengthResult, evaluate_strength  # [DEPRECATED] LEGACY/RESEARCH_ONLY — 测试兼容性


class TestD1StrengthEngine(unittest.TestCase):
    def setUp(self):
        self.eng = BaziEngine()

    def _eval(self, y, m, d, h, gender):
        chart = self.eng.compute((y, m, d, h), gender=gender)
        return chart, evaluate_strength(chart)

    # ---------- 契约: 全部中间项必须存在 ----------

    def test_stub_returns_valid_result(self):
        """evaluate_strength 是 DEPRECATED stub, 必须返回合法 D1StrengthResult."""
        _, r = self._eval(1990, 5, 15, 22, "male")
        self.assertIsInstance(r, D1StrengthResult)
        # 字段完整性: 所有 dataclass 字段必须存在
        _ = r.month_command
        _ = r.day_master_element
        _ = r.de_ling
        _ = r.verdict
        _ = r.verdict_condition
        _ = r.climate
        _ = r.tiaohou_primary
        _ = r.tiaohou_secondary

    def test_verdict_is_unresolved(self):
        """verify: evaluate_strength 已退回 UNRESOLVED."""
        _, r = self._eval(1990, 5, 15, 22, "male")
        self.assertEqual(r.verdict, "")
        self.assertIn("DEPRECATED", r.verdict_condition)
        self.assertEqual(r.climate, "neutral")
        # wang_score 为 RESEARCH_ONLY 中间特征，stub 返回 0.0
        self.assertEqual(r.wang_score, 0.0)

    def test_evidence_has_deprecated_marker(self):
        """evidence 字典保留原始条目, 但 verdict 为空."""
        _, r = self._eval(1985, 12, 3, 8, "female")
        # evidence dict 保留, 但 verdict 项应为空
        self.assertIn("verdict", r.evidence)
        self.assertEqual(r.verdict, "")

    def test_all_call_sites_get_unresolved(self):
        """多命例验证: 所有调用均返回 UNRESOLVED stub."""
        cases = [
            (1990, 5, 15, 22, "male"),
            (1985, 12, 3, 8, "female"),
            (2000, 2, 29, 14, "male"),
        ]
        for y, m, d, h, g in cases:
            _, r = self._eval(y, m, d, h, g)
            self.assertEqual(r.verdict, "", f"{y}-{m}-{d} {g} 应返回 UNRESOLVED")
            self.assertEqual(r.climate, "neutral", f"{y}-{m}-{d} {g} 气候应为 neutral")


if __name__ == "__main__":
    unittest.main()
