"""P2 判定引擎专项测试 — [DEPRECATED] evaluate_strength stub 兼容性验证.

TASK-001: evaluate_strength 已退回 UNRESOLVED stub.
本文件验证 judgment 引擎在 d1.verdict=="" 时的兜底行为.
"""
from __future__ import annotations

import unittest

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.strength_engine import evaluate_strength  # [DEPRECATED] LEGACY/RESEARCH_ONLY — 测试兼容性
from tongshu.engines.judgment_engine import judgment, P2JudgmentResult


class TestP2Judgment(unittest.TestCase):
    def setUp(self):
        self.eng = BaziEngine()

    def _eval(self, y, m, d, h, gender):
        chart = self.eng.compute((y, m, d, h), gender=gender)
        d1 = evaluate_strength(chart)
        return chart, d1, judgment(chart, d1)

    # ---- 契约: 输出结构完整 ----

    def test_result_has_all_fields(self):
        """P2JudgmentResult 必须包含全部字段."""
        _, _, r = self._eval(1990, 5, 15, 22, "male")
        self.assertIsInstance(r, P2JudgmentResult)
        self.assertTrue(hasattr(r, 'climate'))
        self.assertTrue(hasattr(r, 'tiao_hou_element'))
        self.assertTrue(hasattr(r, 'tiao_hou_present'))
        self.assertTrue(hasattr(r, 'tiao_hou_is_yong'))
        self.assertTrue(hasattr(r, 'evidence_tiaohou'))
        self.assertTrue(hasattr(r, 'bing'))
        self.assertTrue(hasattr(r, 'yao'))
        self.assertTrue(hasattr(r, 'you_bing_you_yao'))
        self.assertTrue(hasattr(r, 'verdict_from_d1'))

    # ---- DEPRECATED stub 兼容性 ----

    def test_stub_verdict_is_empty(self):
        """evaluate_strength 已退回 UNRESOLVED, verdict 为空."""
        _, d1, _ = self._eval(1990, 5, 15, 22, "male")
        self.assertEqual(d1.verdict, "")
        self.assertIn("DEPRECATED", d1.verdict_condition)

    def test_judgment_handles_empty_verdict(self):
        """judgment 应能处理 d1.verdict=="" 的情况, 不抛出异常."""
        _, d1, r = self._eval(1985, 12, 3, 8, "female")
        self.assertIsInstance(r, P2JudgmentResult)
        # climate 来自 d1, 但 stub 返回 neutral
        self.assertEqual(d1.climate, "neutral")
