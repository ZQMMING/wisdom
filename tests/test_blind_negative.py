# -*- coding: utf-8 -*-
"""BLIND E4 负向测试（验收修改 M-03）。

规范 §55/E4：negative 必须 FAIL CLOSED。盲派应期引擎对越界目标
（负年龄 / 出生前年份 / 超设计范围 150 岁）必须拒绝计算并抛 ValueError，
不得静默返回结果。
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tongshu.engines.blind_yingqi import BlindYingqiEngine, analyze_yingqi


class TestBlindYingqiNegative(unittest.TestCase):
    BIRTH = (1990, 5, 12, 10)

    def setUp(self):
        self.engine = BlindYingqiEngine()

    # ── 越界 target_age（负 / 超 150）→ fail-closed ──────────────────────────
    def test_negative_target_age_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.engine.analyze(self.BIRTH, "male", target_age=-5)
        self.assertIn("fail-closed", str(ctx.exception))

    def test_target_age_above_design_range_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.engine.analyze(self.BIRTH, "male", target_age=150)
        self.assertIn("fail-closed", str(ctx.exception))

    def test_target_age_149_valid_boundary(self):
        # 设计范围上界 149（DAXIAN_SEGMENTS 末段 55-150 不含）仍合法
        r = self.engine.analyze(self.BIRTH, "male", target_age=149)
        self.assertEqual(r.age, 149)

    # ── 越界 target_year（出生前 / 超 150 岁）→ fail-closed ─────────────────
    def test_target_year_before_birth_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.engine.analyze(self.BIRTH, "male", target_year=1800)
        self.assertIn("fail-closed", str(ctx.exception))

    def test_target_year_too_far_ahead_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.engine.analyze(self.BIRTH, "male", target_year=3000)
        self.assertIn("fail-closed", str(ctx.exception))

    def test_target_year_boundary_valid(self):
        # 出生当年 age=0（大限年柱段 0-18）合法
        r = self.engine.analyze(self.BIRTH, "male", target_year=1990)
        self.assertEqual(r.age, 0)

    # ── 便捷入口 analyze_yingqi 继承同一守卫 ─────────────────────────────────
    def test_convenience_entry_fail_closed(self):
        with self.assertRaises(ValueError):
            analyze_yingqi(self.BIRTH, "male", target_age=-1)


if __name__ == "__main__":
    unittest.main()
