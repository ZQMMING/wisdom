"""
M1 历法引擎测试 — 与 lunar-python (MIT) 交叉验证
覆盖：农历转换、干支、纳音、黄历要素
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages", "tongshu-calendar"))

import pytest
from datetime import date
from lunar_python import Solar

from tongshu.calendar.lunar import solar_to_lunar, get_day_ganzhi, get_day_nayin
from tongshu.calendar.almanac import get_day_info, get_jianchu, get_nayin
from tongshu.calendar.types import GanZhi


# ============================================================
# 农历转换
# ============================================================

class TestLunarConversion:
    """农历转换与 lunar-python 交叉验证"""

    @pytest.mark.parametrize("y, m, day", [
        (2026, 8, 13), (2026, 8, 12), (2026, 2, 17), (2024, 2, 10),
        (2026, 1, 1), (2026, 12, 31), (2025, 1, 29), (2026, 6, 1),
        (2026, 11, 1), (2023, 3, 22), (2023, 4, 19), (2023, 4, 20),
        (1901, 1, 1), (2000, 1, 1), (2100, 12, 31),
    ])
    def test_known_dates(self, y, m, day):
        """已知日期农历转换"""
        d = date(y, m, day)
        ld = solar_to_lunar(d)
        s = Solar.fromYmd(y, m, day)
        l = s.getLunar()
        raw_m = l.getMonth()
        assert ld.year == l.getYear()
        assert ld.month == abs(raw_m)
        assert ld.day == l.getDay()
        assert ld.is_leap == (raw_m < 0)

    def test_spring_festival_2024(self):
        """2024春节 = 2024-02-10"""
        ld = solar_to_lunar(date(2024, 2, 10))
        assert (ld.year, ld.month, ld.day, ld.is_leap) == (2024, 1, 1, False)

    def test_leap_month_2023(self):
        """2023年闰二月"""
        ld = solar_to_lunar(date(2023, 3, 22))
        assert (ld.year, ld.month, ld.day, ld.is_leap) == (2023, 2, 1, True)


# ============================================================
# 干支
# ============================================================

class TestGanZhi:
    """干支计算"""

    def test_known_20260813(self):
        """2026-08-13 = 丙午年 丙申月 己未日"""
        gz = get_day_ganzhi(date(2026, 8, 13))
        assert gz["year"].full == "丙午"
        assert gz["month"].full == "丙申"
        assert gz["day"].full == "己未"

    def test_known_19830515(self):
        """1983-05-15 = 癸亥年 丁巳月 癸卯日"""
        gz = get_day_ganzhi(date(1983, 5, 15))
        assert gz["year"].full == "癸亥"
        assert gz["month"].full == "丁巳"
        assert gz["day"].full == "癸卯"

    @pytest.mark.parametrize("y, m, day", [
        (2026, 8, 13), (2024, 2, 10), (2026, 2, 17), (2000, 1, 1),
        (1983, 5, 15), (1901, 1, 1), (2100, 12, 31),
    ])
    def test_cross_validate(self, y, m, day):
        """与 lunar-python 交叉验证"""
        gz = get_day_ganzhi(date(y, m, day))
        s = Solar.fromYmd(y, m, day)
        bazi = s.getLunar().getBaZi()
        assert gz["year"].full == bazi[0]
        assert gz["month"].full == bazi[1]
        assert gz["day"].full == bazi[2]


# ============================================================
# 纳音
# ============================================================

class TestNaYin:
    """六十甲子纳音"""

    def test_known_20260813(self):
        """2026-08-13 己未日 = 天上火"""
        assert get_day_nayin(date(2026, 8, 13)) == "天上火"

    def test_known_20240210(self):
        """2024-02-10 甲辰日 = 覆灯火"""
        assert get_day_nayin(date(2024, 2, 10)) == "覆灯火"

    def test_known_20260217(self):
        """2026-02-17 壬戌日 = 大海水"""
        assert get_day_nayin(date(2026, 2, 17)) == "大海水"

    @pytest.mark.parametrize("y, m, day", [
        (2026, 8, 13), (2024, 2, 10), (2026, 2, 17), (2000, 1, 1),
        (1983, 5, 15), (1901, 1, 1), (2100, 12, 31),
    ])
    def test_cross_validate(self, y, m, day):
        """与 lunar-python 交叉验证"""
        our = get_day_nayin(date(y, m, day))
        s = Solar.fromYmd(y, m, day)
        lp = s.getLunar().getDayNaYin()
        assert our == lp


# ============================================================
# 黄历要素
# ============================================================

class TestAlmanac:
    """黄历要素"""

    def test_jianchu_20260813(self):
        """2026-08-13 农历七月(申月) 未日 = 闭"""
        assert get_jianchu(7, "未") == "闭"

    def test_jianchu_20240210(self):
        """2024-02-10 正月(寅月) 辰日 = 满"""
        assert get_jianchu(1, "辰") == "满"

    def test_jianchu_20260217(self):
        """2026-02-17 正月(寅月) 戌日 = 成"""
        assert get_jianchu(1, "戌") == "成"

    def test_peng_taboo_20260813(self):
        """己未日 彭祖百忌"""
        info = get_day_info(date(2026, 8, 13))
        assert "己不破券二比并亡" in info.peng_taboo
        assert "未不服药毒气入肠" in info.peng_taboo

    def test_day_info_complete(self):
        """完整 DayInfo 字段"""
        info = get_day_info(date(2026, 8, 13))
        assert info.lunar is not None
        assert info.day_ganzhi.full == "己未"
        assert info.jianchu != ""
        assert info.nayin != ""
        assert info.zodiac_clash != ""
        assert len(info.hour_lucky) == 12
        assert len(info.lucky_direction) > 0

    def test_hour_lucky_12(self):
        """每个时辰都有吉凶"""
        info = get_day_info(date(2026, 8, 13))
        assert len(info.hour_lucky) == 12
        lucky = [h for h in info.hour_lucky if h["lucky"]]
        unlucky = [h for h in info.hour_lucky if not h["lucky"]]
        assert len(lucky) >= 4
        assert len(unlucky) >= 4