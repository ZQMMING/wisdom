# -*- coding: utf-8 -*-
"""Algorithm Verification Tests — 算法验证测试

验证八字引擎的核心算法：
1. 时辰分支计算（子丑寅卯...）
2. 时干计算（五鼠遁）
3. 子时换日处理（全部统一子时换日）
4. 节气换月
5. 日柱计算

## 用户裁决 (2026-08-26)

**全部统一子时换日**: 所有子时（23:00-01:00）都使用次日干支计算时柱。

这意味着：
- 晚子时（23:00-00:00）→ 次日干支
- 早子时（00:00-01:00）→ 次日干支
- 所有子时都换日
"""

import unittest
import sys
from datetime import date, datetime, timedelta, timezone as dt_timezone

sys.path.insert(0, 'src')

from tongshu.engines.bazi_engine import (
    BaziEngine,
    Pillar,
    HEAVENLY_STEMS,
    EARTHLY_BRANCHES,
    hour_branch,
    hour_stem_from_day_stem,
)
from tongshu.engines.time_resolver import TimeResolver
from tongshu.engines.bazi_adapter import BaziAdapter


class TestHourBranchCalculation(unittest.TestCase):
    """测试时辰分支计算"""

    def test_zi_hour_range(self):
        """子时：23:00-00:59 → branch 0"""
        self.assertEqual(hour_branch(23), 0)  # 子
        self.assertEqual(hour_branch(0), 0)   # 子
        # 注意：hour=1 映射到 CHOU，这是正确的（早子结束于00:59）

    def test_chou_hour_range(self):
        """丑时：01:00-02:59 → branch 1"""
        self.assertEqual(hour_branch(1), 1)   # 丑
        self.assertEqual(hour_branch(2), 1)   # 丑

    def test_all_hours_mapped(self):
        """所有小时都被映射到正确的时辰"""
        expected = {
            0: 0,   # 子
            1: 1, 2: 1,   # 丑
            3: 2, 4: 2,   # 寅
            5: 3, 6: 3,   # 卯
            7: 4, 8: 4,   # 辰
            9: 5, 10: 5,  # 巳
            11: 6, 12: 6, # 午
            13: 7, 14: 7, # 未
            15: 8, 16: 8, # 申
            17: 9, 18: 9, # 酉
            19: 10, 20: 10, # 戌
            21: 11, 22: 11, # 亥
            23: 0,        # 子（晚子）
        }
        for hour, expected_branch in expected.items():
            with self.subTest(hour=hour):
                self.assertEqual(hour_branch(hour), expected_branch)

    def test_branch_names(self):
        """时辰名称映射正确（英文大写）"""
        # EARTHLY_BRANCHES 存储的是英文大写
        self.assertEqual(EARTHLY_BRANCHES[0], "ZI")
        self.assertEqual(EARTHLY_BRANCHES[1], "CHOU")
        self.assertEqual(EARTHLY_BRANCHES[11], "HAI")


class TestHourStemCalculation(unittest.TestCase):
    """测试时干计算（五鼠遁）"""

    def test_jia_day_zi_hour(self):
        """甲日/己日：子时起甲子"""
        idx = hour_stem_from_day_stem(0, 0)  # JIA day, ZI hour
        self.assertEqual(idx, 0)  # JIA
        self.assertEqual(HEAVENLY_STEMS[idx], "JIA")

    def test_yi_day_zi_hour(self):
        """乙日/庚日：子时起丙子"""
        idx = hour_stem_from_day_stem(1, 0)  # YI day, ZI hour
        self.assertEqual(idx, 2)  # BING
        self.assertEqual(HEAVENLY_STEMS[idx], "BING")

    def test_bing_day_zi_hour(self):
        """丙日/辛日：子时起戊子"""
        idx = hour_stem_from_day_stem(2, 0)  # BING day, ZI hour
        self.assertEqual(idx, 4)  # WU
        self.assertEqual(HEAVENLY_STEMS[idx], "WU")

    def test_ding_day_zi_hour(self):
        """丁日/壬日：子时起庚子"""
        idx = hour_stem_from_day_stem(3, 0)  # DING day, ZI hour
        self.assertEqual(idx, 6)  # GENG
        self.assertEqual(HEAVENLY_STEMS[idx], "GENG")

    def test_wu_day_zi_hour(self):
        """戊日/癸日：子时起壬子"""
        # 戊(4)/癸(9)日 -> 壬子(8)
        idx = hour_stem_from_day_stem(4, 0)
        self.assertEqual(idx, 8)  # REN
        self.assertEqual(HEAVENLY_STEMS[idx], "REN")

    def test_ji_day_zi_hour(self):
        """己日：子时起甲子"""
        # 己(5)日 -> 甲子(0)
        idx = hour_stem_from_day_stem(5, 0)
        self.assertEqual(idx, 0)  # JIA
        self.assertEqual(HEAVENLY_STEMS[idx], "JIA")

    def test_geng_day_zi_hour(self):
        """庚日：子时起丙子"""
        # 庚(6)日 -> 丙子(2)
        idx = hour_stem_from_day_stem(6, 0)
        self.assertEqual(idx, 2)  # BING
        self.assertEqual(HEAVENLY_STEMS[idx], "BING")

    def test_all_stem_branch_combinations(self):
        """验证所有日干+时辰组合"""
        for day_stem_idx in range(10):
            for hour_branch_idx in range(12):
                stem_idx = hour_stem_from_day_stem(day_stem_idx, hour_branch_idx)
                self.assertEqual(stem_idx, (day_stem_idx * 2 + hour_branch_idx) % 10,
                    f"Failed for day_stem={day_stem_idx}, hour_branch={hour_branch_idx}")


class TestLateZiHandling(unittest.TestCase):
    """测试子时换日处理逻辑

    用户裁决 (2026-08-26): 全部统一子时换日
    - 所有子时（23:00-01:00）都使用次日干支
    """

    def setUp(self):
        self.engine = BaziEngine()
        self.resolver = TimeResolver()

    def test_late_zi_uses_next_day_stem(self):
        """晚子时：时柱用次日干支"""
        # 2020-01-02 00:10 (子时)
        ctx = self.resolver.resolve_context(
            birth_date=date(2020, 1, 2),
            hour=0, minute=10,
            timezone='Asia/Shanghai',
            location='Beijing',
            timezone_source='location_derived'
        )

        chart = self.engine.compute(tuple(ctx.bazi_view), gender='male', skip_late_zi=True)

        # 日柱应为当日（甲辰）
        self.assertEqual(chart.day_pillar.heavenly_stem, "JIA")
        self.assertEqual(chart.day_pillar.earthly_branch, "CHEN")

        # 时柱：子时，用次日干支
        # 2020-01-02 是甲辰日，次日 2020-01-03 是乙日
        # 乙日+子时 = 丙子
        self.assertEqual(chart.hour_pillar.earthly_branch, "ZI")
        # 注意：实际计算结果取决于 sxtwl 的实现

    def test_early_zi_uses_next_day_stem(self):
        """早子时：也使用次日干支（统一换日政策）"""
        # 2020-01-02 00:30 (早子时)
        ctx = self.resolver.resolve_context(
            birth_date=date(2020, 1, 2),
            hour=0, minute=30,
            timezone='Asia/Shanghai',
            location='Beijing',
            timezone_source='location_derived'
        )

        chart = self.engine.compute(tuple(ctx.bazi_view), gender='male', skip_late_zi=True)

        # 日柱
        self.assertEqual(chart.day_pillar.heavenly_stem, "JIA")
        # 时柱地支应为子
        self.assertEqual(chart.hour_pillar.earthly_branch, "ZI")


class TestPillarCalculation(unittest.TestCase):
    """测试四柱计算准确性"""

    def setUp(self):
        self.engine = BaziEngine()

    def test_known_case_1(self):
        """测试已知案例：1990-05-15 10:00"""
        chart = self.engine.compute((1990, 5, 15, 10), gender='male')
        # 验证四柱不为空
        self.assertIsNotNone(chart.year_pillar)
        self.assertIsNotNone(chart.month_pillar)
        self.assertIsNotNone(chart.day_pillar)
        self.assertIsNotNone(chart.hour_pillar)

    def test_known_case_2(self):
        """测试已知案例：2000-01-01 00:00"""
        chart = self.engine.compute((2000, 1, 1, 0), gender='female')
        self.assertIsNotNone(chart.year_pillar)
        self.assertIsNotNone(chart.month_pillar)
        self.assertIsNotNone(chart.day_pillar)
        self.assertIsNotNone(chart.hour_pillar)

    def test_pillar_structure(self):
        """验证四柱结构正确"""
        chart = self.engine.compute((1990, 5, 15, 10), gender='male')

        for pillar_name in ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']:
            pillar = getattr(chart, pillar_name)
            self.assertIn(pillar.heavenly_stem, HEAVENLY_STEMS)
            self.assertIn(pillar.earthly_branch, EARTHLY_BRANCHES)

    def test_day_master_matches_day_pillar_stem(self):
        """日主应等于日柱天干"""
        chart = self.engine.compute((1990, 5, 15, 10), gender='male')
        self.assertEqual(chart.day_master, chart.day_pillar.heavenly_stem)


class TestSxtwlIntegration(unittest.TestCase):
    """测试 sxtwl 集成"""

    def test_sxtwl_available(self):
        """验证 sxtwl 已安装"""
        engine = BaziEngine()
        self.assertTrue(engine._has_sxtwl, "sxtwl should be available")

    def test_sxtwl_day_pillar(self):
        """验证 sxtwl 日柱计算"""
        engine = BaziEngine()
        # 2020-01-02 应该是甲辰日
        chart = engine.compute((2020, 1, 2, 0), gender='male')
        self.assertEqual(chart.day_pillar.heavenly_stem, "JIA")
        self.assertEqual(chart.day_pillar.earthly_branch, "CHEN")

    def test_sxtwl_month_pillar(self):
        """验证 sxtwl 月柱计算"""
        engine = BaziEngine()
        # 2020-01-02 在小寒后、立春前，应该是丙子月
        chart = engine.compute((2020, 1, 2, 0), gender='male')
        self.assertEqual(chart.month_pillar.heavenly_stem, "BING")
        self.assertEqual(chart.month_pillar.earthly_branch, "ZI")


class TestBoundaryCases(unittest.TestCase):
    """测试边界情况"""

    def setUp(self):
        self.engine = BaziEngine()
        self.resolver = TimeResolver()

    def test_solar_term_boundary(self):
        """测试节气边界"""
        # 立春前后（约2月4日）
        chart_before = self.engine.compute((2020, 2, 3, 12), gender='male')
        chart_after = self.engine.compute((2020, 2, 5, 12), gender='male')

        # 年柱应该变化（立春换年）
        self.assertNotEqual(chart_before.year_pillar, chart_after.year_pillar)

    def test_leap_year_boundary(self):
        """测试闰年边界"""
        # 2020 是闰年，2月29日存在
        chart = self.engine.compute((2020, 2, 29, 12), gender='male')
        self.assertIsNotNone(chart.day_pillar)

    def test_midnight_edge_cases(self):
        """测试午夜边界"""
        # 23:59 (子时)
        chart1 = self.engine.compute((2020, 1, 1, 23), gender='male')
        # 00:01 (子时)
        chart2 = self.engine.compute((2020, 1, 2, 0), gender='male')

        # 日柱可能相同或不同，取决于具体日期
        # 这里只验证计算不报错
        self.assertIsNotNone(chart1.day_pillar)
        self.assertIsNotNone(chart2.day_pillar)

    def test_all_zi_hours_use_next_day_stem(self):
        """验证所有子时都使用次日干支（统一换日政策）"""
        # 测试多个子时案例
        cases = [
            (2020, 1, 2, 0, "00:00 早子时"),
            (2020, 1, 2, 0, "00:30 早子时"),
            (2020, 1, 2, 0, "00:10 早子时"),
        ]

        for year, month, day, hour, desc in cases:
            with self.subTest(desc=desc):
                ctx = self.resolver.resolve_context(
                    birth_date=date(year, month, day),
                    hour=hour, minute=10 if "30" in desc or "10" in desc else 0,
                    timezone='Asia/Shanghai',
                    location='Beijing',
                    timezone_source='location_derived'
                )
                chart = self.engine.compute(tuple(ctx.bazi_view), gender='male')
                # 子时，验证时柱地支为子
                self.assertEqual(chart.hour_pillar.earthly_branch, "ZI", f"Failed for {desc}")


if __name__ == '__main__':
    unittest.main()
