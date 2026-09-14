"""B-02 Golden case: 晚子时 (23:00+) 日界政策锚定测试。

2026-09-14 子正换日裁决 (覆盖旧 2026-08-23"子初换日 23:00"与
2026-08-26"统一子时换日"): 日界 = 0:00 (子正)。
  23:00-23:59:59 夜子时 → 日柱 = 当天 (不换日); 时柱 = 子时, 天干按次日日干五鼠遁。
  0:00-0:59:59 早子时 → 日柱 = 新一天; 时柱 = 子时, 天干按当日日干。

Golden case (北京, 1990-11-10):
  22:30 civil → 22:31 solar → 当日 → 己卯 (JIMAO)
  23:30 civil → 23:31 solar → 夜子时 → 日柱仍己卯 (JIMAO), 时柱按次日日干

B-02 收尾 (2026-09-14) 边界对 (广州, 1990-11-10, 真太阳时校正约 -11 min):
  22:59 civil → 22:48 solar → 当日日柱 己卯
  23:30 civil → 23:19 solar → 夜子时 → 日柱仍己卯 (子正未到, 不换日)
  双引擎探针: Bazi 夜子时日柱当天 / Ziwei 按当日 iztro 晚子时约定。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Use current project src path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
os.environ.setdefault("TONGSHU_ALLOW_ZIWEI_STUB", "1")

import unittest
from datetime import date

from tongshu.engines.bazi_adapter import BaziAdapter
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.time.resolver import TimeResolver
from tongshu.signal.adapters import ZiweiAdapter
from tongshu.engines.ziwei_engine import ZiweiEngine


class TestLateZiGoldenCase(unittest.TestCase):
    """子正换日 Golden case — BaziAdapter 夜子时日柱=当天。"""

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

    def test_after_boundary_same_day(self):
        """23:30 出生 (夜子时) → 日柱仍当天 己卯 (子正换日, 不提前换日)。"""
        self.assertEqual(self._day_pillar(23), "JIMAO")

    def test_boundary_same_day_pillars(self):
        """22:30 与 23:30 日柱相同 (均当天 己卯, 子正未到不换日)。"""
        self.assertEqual(self._day_pillar(22), self._day_pillar(23))


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
        cls.ziwei_adapter = ZiweiAdapter()

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

    def test_2330_bazi_same_day(self):
        """23:30 出生 → 真太阳时 23:19 → 夜子时: 日柱仍当天 己卯 (子正换日)。

        day_rolled=True 现标记"夜子时" (时柱按次日日干), 不再表示换日。
        """
        ctx = self._ctx(23, 30)
        self.assertTrue(ctx.day_rolled)
        chart = self.bazi_adapter.compute(ctx, gender="male")
        self.assertEqual(
            f"{chart.day_pillar.heavenly_stem}{chart.day_pillar.earthly_branch}",
            "JIMAO",
        )

    # -- Ziwei 引擎探针 (P0-14-v1: late_zi_handling=same_day) -- #

    def _zw_chart(self, ctx):
        # Mock ziwei output for testing
        return {
            'soul_palace_main_star': 'Ziwei',
            'palace': 'Life',
            'stars': ['Ziwei', 'Tianfu'],
            'transformations': [],
            'strength': 0.8,
        }

    def test_2330_ziwei_uses_same_solar_day(self):
        """23:30 晚子时: 子正换日后 bazi 与 ziwei 视图均保留当日 (11-10)。

        bazi_view 不再 23:00 提前换日; ziwei_view 按当日 iztro 晚子时约定。
        """
        ctx = self._ctx(23, 30)
        # bazi 视图当日 (子正换日, 不提前)
        self.assertEqual(ctx.bazi_view[:3], (1990, 11, 10))
        # ziwei 视图保留当日
        self.assertEqual(ctx.ziwei_view[:3], (1990, 11, 10))

    def test_2259_and_2330_ziwei_same_solar_day(self):
        """22:59 与 23:30 的 Ziwei 视图均用当日 (11-10)。

        2026-09-14 子正换日: 晚子时不换日, ziwei 与 bazi 一致用当日。
        """
        ctx_early = self._ctx(22, 59)
        ctx_late = self._ctx(23, 30)
        self.assertEqual(ctx_early.ziwei_view[:3], (1990, 11, 10))
        self.assertEqual(ctx_late.ziwei_view[:3], (1990, 11, 10))


if __name__ == "__main__":
    unittest.main()
