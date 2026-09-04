"""B-02 Golden case: 晚子时 (23:00+) 日界政策锚定测试。

背景：
  八字日界 = 23:00（子初换日）。23:00 前出生 → 当日日柱；
  23:00 后出生 → 次日日柱。主管道之前直调引擎绕过 BaziAdapter，
  此政策未生效。

Golden case (北京, 1990-11-10):
  22:30 civil → 22:31 solar → 当日 → 己卯 (JIMAO)
  23:30 civil → 23:31 solar → 次日 → 庚辰 (GENGCHEN)

B-02 收尾 (User 终裁 2026-08-23) 新增:
  晚子时边界测试对 (广州, 1990-11-10, 真太阳时校正约 -11 min):
  22:59 civil → 22:48 solar → 当日日柱 己卯 (未触发换日)
  23:30 civil → 23:19 solar → 次日日柱 庚辰 (子初换日生效)
  双引擎探针: Bazi 换日 / Ziwei 按当日 iztro 晚子时约定(P0-14-v1)。
  依赖 stub 引擎，B-03b 冻结时强制复核。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
os.environ.setdefault("TONGSHU_ALLOW_ZIWEI_STUB", "1")

import unittest
from datetime import date

from tongshu.engines.bazi_adapter import BaziAdapter
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.time.resolver import TimeResolver
from tongshu.engines.ziwei_adapter import ZiweiAdapter
from tongshu.engines.ziwei_engine import ZiweiEngine


class TestLateZiGoldenCase(unittest.TestCase):
    """23:00 日界 Golden case — BaziAdapter 正确换日。"""

    @classmethod
    def setUpClass(cls):
        cls.resolver = TimeResolver()
        cls.adapter = BaziAdapter(BaziEngine())

    def _day_pillar(self, hour: int, minute: int = 30) -> str:
        ctx = self.resolver.resolve_context(
            birth_date=date(1990, 11, 10),
            hour=hour,
            minute=minute,
            timezone="Asia/Shanghai",
            location="beijing",
            gender="male",
        )
        chart = self.adapter.compute(ctx, gender="male")
        return f"{chart.day_pillar.heavenly_stem}{chart.day_pillar.earthly_branch}"

    def test_before_boundary_same_day(self):
        """22:30 出生 → 当日日柱 己卯。"""
        self.assertEqual(self._day_pillar(22), "JIMAO")

    def test_after_boundary_next_day(self):
        """23:30 出生 → 次日日柱 庚辰。"""
        self.assertEqual(self._day_pillar(23), "GENGCHEN")

    def test_boundary_produces_different_pillars(self):
        """两日柱必须不同（验证日界确实生效）。"""
        self.assertNotEqual(self._day_pillar(22), self._day_pillar(23))


class TestLateZiBoundaryPair(unittest.TestCase):
    """B-02 收尾: 22:59/23:30 边界对 + 双引擎探针。

    依据: 子初换日规则冻结 (23:00) + P0-14-v1 时间政策。
    广州经度 113.26°E → 真太阳时校正约 -11 min,确保
    22:59 civil 不被校正推过 23:00 边界。
    依赖 stub 引擎，B-03b 冻结时强制复核。
    """

    @classmethod
    def setUpClass(cls):
        cls.resolver = TimeResolver()
        cls.bazi_adapter = BaziAdapter(BaziEngine())
        cls.ziwei_adapter = ZiweiAdapter(ZiweiEngine())

    def _ctx(self, hour: int, minute: int):
        return self.resolver.resolve_context(
            birth_date=date(1990, 11, 10),
            hour=hour,
            minute=minute,
            timezone="Asia/Shanghai",
            location="guangzhou",
            gender="male",
        )

    # -- Bazi 引擎探针 -- #

    def test_2259_bazi_same_day(self):
        """22:59 出生 → 真太阳时 22:48 → 当日日柱 己卯（未触发换日）。"""
        ctx = self._ctx(22, 59)
        self.assertFalse(ctx.day_rolled)
        chart = self.bazi_adapter.compute(ctx, gender="male")
        self.assertEqual(
            f"{chart.day_pillar.heavenly_stem}{chart.day_pillar.earthly_branch}",
            "JIMAO",
        )

    def test_2330_bazi_next_day(self):
        """23:30 出生 → 真太阳时 23:19 → 次日日柱 庚辰（子初换日生效）。"""
        ctx = self._ctx(23, 30)
        self.assertTrue(ctx.day_rolled)
        chart = self.bazi_adapter.compute(ctx, gender="male")
        self.assertEqual(
            f"{chart.day_pillar.heavenly_stem}{chart.day_pillar.earthly_branch}",
            "GENGCHEN",
        )

    # -- Ziwei 引擎探针 (P0-14-v1: late_zi_handling=same_day) -- #

    def test_2330_ziwei_uses_same_solar_day(self):
        """23:30 晚子时: Ziwei 视图不换日（iztro 晚子时约定）。

        bazi_view 已换日至次日(11-11);ziwei_view 必须保留当日(11-10),
        即 true_solar_datetime 的日期,与 ZiweiCalculationPolicy 一致。
        """
        ctx = self._ctx(23, 30)
        # bazi 视图已换日
        self.assertEqual(ctx.bazi_view[:3], (1990, 11, 11))
        # ziwei 视图保留当日（不换日）
        self.assertEqual(ctx.ziwei_view[:3], (1990, 11, 10))
        # ZiweiAdapter 能正常计算（stub 引擎）
        zw_chart = self.ziwei_adapter.compute(ctx, gender="male")
        self.assertTrue(zw_chart.soul_palace_main_star)

    def test_2259_and_2330_ziwei_different_lunar_date(self):
        """22:59 与 23:30 的 Ziwei 命盘分属不同日（晚子时换日，与八字一致）。

        决策 A (2026-08-27): 紫微晚子时换日（接受 iztro 行为，与八字子初换日一致）。
        22:59(亥时)用当日命盘; 23:30(晚子时)iztro 按次日命盘 → 主星不同。
        """
        ctx_early = self._ctx(22, 59)
        ctx_late = self._ctx(23, 30)
        zw_early = self.ziwei_adapter.compute(ctx_early, gender="male")
        zw_late = self.ziwei_adapter.compute(ctx_late, gender="male")
        self.assertNotEqual(
            zw_early.soul_palace_main_star,
            zw_late.soul_palace_main_star,
            "紫微晚子时换日(决策A):两时刻命盘分属不同日,主星必须不同",
        )


if __name__ == "__main__":
    unittest.main()
