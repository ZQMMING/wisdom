"""P2.7-C: Calendar / Solar-Term Authority Closure Fix

Fix the month pillar calculation to properly handle solar term boundaries.

The bug was that sxtwl.getMonthGZ() only accepts date, not hour.
We need to manually check if birth time is before/after solar term
and adjust month pillar accordingly.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from src.tongshu.engines.bazi_engine import BaziEngine, BaziChart


class TestSolarTermBoundaryFix:
    """验证节气边界修复"""
    
    def test_立春前16时仍为丑月(self):
        """
        2024年立春时刻：16:26:53
        
        16:00 在立春前，月柱应为 CHOU（丑月）
        17:00 在立春后，月柱应为 YIN（寅月）
        """
        engine = BaziEngine()
        
        # 立春前
        before = engine.compute((2024, 2, 4, 16), gender="male")
        
        # 立春后
        after = engine.compute((2024, 2, 4, 17), gender="male")
        
        print(f"立春前 16:00 月柱: {before.month_pillar}")
        print(f"立春后 17:00 月柱: {after.month_pillar}")
        
        # 关键验证：立春前后月柱必须不同
        assert before.month_pillar.earthly_branch == "CHOU", \
            f"立春前 月柱应为 CHOU，实际为 {before.month_pillar.earthly_branch}"
        
        assert after.month_pillar.earthly_branch == "YIN", \
            f"立春后 月柱应为 YIN，实际为 {after.month_pillar.earthly_branch}"
        
        assert before.month_pillar != after.month_pillar, \
            f"立春前后月柱应不同"
    
    def test_惊蛰前后月柱切换(self):
        """验证惊蛰节气边界"""
        engine = BaziEngine()
        
        # 惊蛰时刻：2024-03-05 10:19
        # 惊蛰前（09:00）应为寅月
        before = engine.compute((2024, 3, 5, 9), gender="male")
        
        # 惊蛰后（11:00）应为卯月
        after = engine.compute((2024, 3, 5, 11), gender="male")
        
        print(f"惊蛰前 09:00 月柱: {before.month_pillar}")
        print(f"惊蛰后 11:00 月柱: {after.month_pillar}")
        
        assert before.month_pillar.earthly_branch == "YIN", \
            f"惊蛰前 月柱应为 YIN，实际为 {before.month_pillar.earthly_branch}"
        
        assert after.month_pillar.earthly_branch == "MAO", \
            f"惊蛰后 月柱应为 MAO，实际为 {after.month_pillar.earthly_branch}"
    
    def test_所有节气边界验证(self):
        """验证所有12个节气的月柱边界"""
        engine = BaziEngine()
        
        # 节气列表（月份，日期，期望的节气后月柱）
        solar_terms = [
            (2, 4, "YIN"),    # 立春
            (3, 5, "MAO"),    # 惊蛰
            (4, 4, "CHEN"),   # 清明
            (5, 5, "SI"),     # 立夏
            (6, 5, "WU"),     # 芒种
            (7, 6, "WEI"),    # 小暑
            (8, 7, "SHEN"),   # 立秋
            (9, 7, "YOU"),    # 白露
            (10, 8, "XU"),    # 寒露
            (11, 7, "HAI"),   # 立冬
            (12, 6, "ZI"),    # 大雪
            (1, 6, "CHOU"),   # 小寒（次年）
        ]
        
        for month, day, expected_branch in solar_terms:
            # 节气后1天（小时取中午12:00）
            chart = engine.compute((2024 if month >= 2 else 2025, month, day + 1, 12), gender="male")
            actual_branch = chart.month_pillar.earthly_branch
            
            # 节气后1天应为对应月柱
            assert actual_branch == expected_branch, \
                f"{month}月{day}日节气后，月柱应为 {expected_branch}，实际为 {actual_branch}"


class TestCanonicalCasesStillPass:
    """验证经典案例仍然通过"""
    
    def test_c001_jixiaolan(self):
        """C001: 纪晓岚案例验证"""
        engine = BaziEngine()
        chart = engine.compute((1724, 7, 16, 12), gender="male")
        
        assert chart.year_pillar.heavenly_stem == "JIA"
        assert chart.year_pillar.earthly_branch == "CHEN"
        assert chart.month_pillar.heavenly_stem == "XIN"
        assert chart.month_pillar.earthly_branch == "WEI"
        assert chart.day_pillar.heavenly_stem == "WU"
        assert chart.day_pillar.earthly_branch == "CHEN"
        assert chart.hour_pillar.heavenly_stem == "WU"
        assert chart.hour_pillar.earthly_branch == "WU"
    
    def test_c002_sushi(self):
        """C002: 苏轼案例验证"""
        engine = BaziEngine()
        chart = engine.compute((1037, 1, 8, 5), gender="male")
        
        assert chart.year_pillar.heavenly_stem == "BING"
        assert chart.year_pillar.earthly_branch == "ZI"
        assert chart.month_pillar.heavenly_stem == "XIN"
        assert chart.month_pillar.earthly_branch == "CHOU"
        assert chart.day_pillar.heavenly_stem == "GUI"
        assert chart.day_pillar.earthly_branch == "HAI"
        assert chart.hour_pillar.heavenly_stem == "YI"
        assert chart.hour_pillar.earthly_branch == "MAO"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
