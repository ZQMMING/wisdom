"""BZ-FNDR-15.2 (⑮-0 P1-2): stem_ten_god fail-closed + day_master_strength 生产顺序.

User 裁决 (2026-09-10):
  1. stem_ten_god 缺失必须 FAIL-CLOSED, 不允许 ten_god() fallback (P1-2 P0).
  2. day_master_strength 必须由 ZiPing Feature stage 产生, 不在 Bazi 不在 ZiPingCanonical
     (证明生产顺序: Bazi -> ZiPing Feature -> Context -> Judgment).

本测试锁死 ⑮-0 P1-2 的两条核心架构证据.
"""
from __future__ import annotations

import re
import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# BZ-FNDR-15.4 P0-2: repo-relative path resolver (替代 D:/shuntian/... 绝对路径)
_REPO_ROOT = Path(__file__).resolve().parents[1]
def _src_path(*parts):
    return _REPO_ROOT.joinpath("src", *parts)

_TEST_COMPUTE_STAGE = str(_src_path("tongshu", "pipeline_stages", "compute_stage.py"))
_TEST_BAZI_L1_FACTS = str(_src_path("tongshu", "engines", "bazi_l1_facts.py"))
_TEST_JUDGMENT_PY = str(_src_path("tongshu", "reasoning", "judgment.py"))

from zoneinfo import ZoneInfo

from tongshu.engines.bazi_engine import BaziEngine


def _make_bazi_chart():
    """真实生产路径: BaziEngine.compute() 产出 BaziChart (含 stem_ten_god)."""
    engine = BaziEngine()
    bd = datetime(1983, 11, 3, 12, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
    return engine.compute((1983, 11, 3, 12), gender="male", birth_datetime=bd)


def _extract_function_body(src, func_name):
    """从源码提取函数体 (从 def 行到下一个 def/class)."""
    pattern = rf"def {func_name}\b[\s\S]+?(?=\n    def |\nclass |\Z)"
    m = re.search(pattern, src)
    return m.group(0) if m else None


def _strip_comments(body):
    """移除注释行, 只保留可执行代码."""
    return "\n".join(ln for ln in body.split("\n") if not ln.strip().startswith("#"))


class TestStemTenGodFailClosed(unittest.TestCase):
    """P1-2 P0: stem_ten_god 缺失必须 fail-closed (RuntimeError), 不允 ten_god() fallback.

    User 裁决原文 (2026-09-10):
      "十神已经由 Bazi 计算完成, ZiPing 不得重新计算"
      "stem_ten_god 缺失 -> FAIL-CLOSED, 不允许 ten_god() fallback"
    """

    def test_real_bazi_chart_has_stem_ten_god_populated(self):
        """真实生产路径: BaziEngine 产出的 chart 应已填 stem_ten_god (4 柱 + 日主)."""
        chart = _make_bazi_chart()
        for pos, pillar in [
            ("year", chart.year_pillar),
            ("month", chart.month_pillar),
            ("day", chart.day_pillar),
            ("hour", chart.hour_pillar),
        ]:
            self.assertTrue(
                pillar.stem_ten_god,
                f"{pos} pillar 必须有 stem_ten_god (实际 = {pillar.stem_ten_god!r})",
            )

    def test_orchestrate_signals_no_ten_god_call_in_executable_lines(self):
        """P1-2: _orchestrate_signals 函数体内不能调用 bazi_ten_gods.ten_god.

        User 裁决: '不允许 ten_god() fallback'.
        文件顶层 import 可保留, 但函数体内**实际调用**禁止.
        检测方式: 扫描函数体内非注释行, 找 "ten_god(" 调用.
        """
        p = _TEST_COMPUTE_STAGE
        src = open(p, encoding='utf-8').read()
        body = _extract_function_body(src, "_orchestrate_signals")
        self.assertIsNotNone(body, "_orchestrate_signals 函数未找到")
        executable = _strip_comments(body)
        self.assertNotIn(
            "ten_god(", executable,
            "_orchestrate_signals 体内禁止调用 ten_god() (P1-2 fail-closed)"
        )

    def test_orchestrate_signals_fail_closed_branch_static(self):
        """P1-2: _orchestrate_signals 函数体内必须有 fail-closed RuntimeError 分支.

        静态验证 (不调用 _orchestrate_signals, 避免 orchestrator 初始化问题):
        - if not tg: 必须存在 (守门)
        - raise RuntimeError 必须存在 (触发 fail-closed)
        - BZ-FNDR-15.2 fail-closed 标识必须存在 (审计标记)
        """
        p = _TEST_COMPUTE_STAGE
        src = open(p, encoding='utf-8').read()
        body = _extract_function_body(src, "_orchestrate_signals")
        self.assertIsNotNone(body, "_orchestrate_signals 函数未找到")
        executable = _strip_comments(body)
        self.assertIn("if not tg:", executable,
                       "_orchestrate_signals 缺 'if not tg:' 守门 (P1-2)")
        self.assertIn("raise RuntimeError", executable,
                       "_orchestrate_signals 缺 'raise RuntimeError' (P1-2)")
        self.assertIn("BZ-FNDR-15.2 fail-closed", executable,
                       "_orchestrate_signals 缺 BZ-FNDR-15.2 标识 (P1-2 审计标记)")

    def test_real_bazi_chart_passes_orchestrate_signals_baseline(self):
        """P1-2 baseline: 真实 chart 满足 _orchestrate_signals 守门 (4 柱 stem_ten_god 非空).

        不调用 _orchestrate_signals (需 AssertionLibrary), 只静态验证守门.
        """
        chart = _make_bazi_chart()
        for pillar in [chart.year_pillar, chart.month_pillar,
                       chart.day_pillar, chart.hour_pillar]:
            self.assertTrue(pillar.stem_ten_god,
                            "Pillar.stem_ten_god 必须非空 (Bazi 引擎保证)")


class TestDayMasterStrengthProductionOrder(unittest.TestCase):
    """P1-2: day_master_strength 必须由 ZiPing Feature 阶段产生, Bazi 不算.

    User 裁决原文 (2026-09-10):
      "Bazi ❌ 不产生 day_master_strength
        ↓
       ZiPing Features ✅ 计算 day_master_strength
        ↓
       ContextAssembler ✅ 消费 ZiPing Feature
        ↓
       Judgment"
    """

    def test_bazi_l1_facts_neg07_blocks_day_master_strength(self):
        """Bazi L1 facts NEG-07 测试禁止 day_master_strength 字段."""
        p = _TEST_BAZI_L1_FACTS
        src = open(p, encoding='utf-8').read()
        self.assertIn(
            "'day_master_strength'", src,
            "bazi_l1_facts.py 必须含 day_master_strength NEG-07 守门",
        )
        self.assertIn(
            "NEG-07", src,
            "bazi_l1_facts.py 必须有 NEG-07 守门测试",
        )

    def test_bazi_chart_does_not_compute_day_master_strength(self):
        """BaziChart dataclass 不应有 day_master_strength 字段 (Bazi 不算)."""
        import dataclasses
        from tongshu.engines.bazi_engine import BaziChart
        field_names = {f.name for f in dataclasses.fields(BaziChart)}
        self.assertNotIn(
            "day_master_strength", field_names,
            "BaziChart 不应有 day_master_strength (属 ZiPing Feature, 不是 Bazi)",
        )

    def test_ziping_canonical_does_not_carry_day_master_strength(self):
        """ZiPingCanonicalBaziChart 也不携带 day_master_strength (P1-1 已确认)."""
        import dataclasses
        from tongshu.models.canonical_bazi import ZiPingCanonicalBaziChart
        field_names = {f.name for f in dataclasses.fields(ZiPingCanonicalBaziChart)}
        self.assertNotIn(
            "day_master_strength", field_names,
            "ZiPingCanonical 不携带 day_master_strength (P1-1 字段审计已锁)",
        )

    def test_context_assembler_falls_back_to_missing(self):
        """ContextAssembler 收到 chart 无 day_master_strength -> 填 'MISSING' (与 contract 一致)."""
        from tongshu.reasoning.context_assembler import ContextAssembler

        chart = _make_bazi_chart()
        self.assertFalse(
            hasattr(chart, "day_master_strength"),
            "BaziChart 不应携带 day_master_strength (前置条件)",
        )
        assembler = ContextAssembler()
        ctx = assembler.assemble_natal_context(chart, 1983, "male")
        self.assertEqual(
            ctx.day_master_strength, "MISSING",
            f"context_assembler 应 fallback 'MISSING', 实际 = {ctx.day_master_strength!r}",
        )

    def test_natal_context_default_is_missing(self):
        """NatalContext.day_master_strength 默认值 = 'MISSING' (contract 层面就预期未计算)."""
        from tongshu.reasoning.temporal_context_contract import NatalContext
        nc = NatalContext(
            day_master="YI", gender="male", birth_year=1983,
            pillars=[], branch_clashes=[],
        )
        self.assertEqual(
            nc.day_master_strength, "MISSING",
            "NatalContext 字段默认值应是 'MISSING' (契约一致性)",
        )

    def test_judgment_does_not_consume_day_master_strength(self):
        """Judgment 层不消费 day_master_strength (僵尸字段, 验证生产顺序)."""
        import os
        p = _TEST_JUDGMENT_PY
        if os.path.exists(p):
            src = open(p, encoding='utf-8').read()
            self.assertNotIn(
                "day_master_strength", src,
                "judgment.py 引用 day_master_strength (生产顺序违反, 应在 ZiPing Feature 计算)",
            )


if __name__ == "__main__":
    unittest.main()
