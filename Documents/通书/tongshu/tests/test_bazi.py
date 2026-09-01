"""
M2 八字分析器测试 — 与 bazi-tool 已知命盘 + lunar-python 交叉验证
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages", "tongshu-calendar"))

import pytest
from datetime import date
from lunar_python import Solar

from tongshu.calendar.bazi import calculate_bazi, BirthInfo, analyze_five_elements, judge_day_master_strength, calculate_yongshen_v1
from tongshu.calendar.lunar import get_day_ganzhi
from tongshu.calendar.types import GanZhi


class TestBaZiChart:
    """八字排盘"""

    def test_1983_0515_1430_shanghai_male(self):
        """1983-05-15 14:30 上海 男 — bazi-tool 已知命盘"""
        birth = BirthInfo(date=date(1983, 5, 15), time="14:30", gender="male", city="上海")
        chart = calculate_bazi(birth)
        assert chart.pillars["year"].full == "癸亥"
        assert chart.pillars["month"].full == "丁巳"
        assert chart.pillars["day"].full == "癸卯"
        assert chart.pillars["hour"].full == "己未"
        assert chart.day_master["stem"] == "癸"
        assert chart.day_master["element"] == "水"

    def test_2000_0101_0000_beijing_female(self):
        """2000-01-01 00:00 北京 女 — bazi-tool 已知命盘"""
        birth = BirthInfo(date=date(2000, 1, 1), time="00:00", gender="female", city="北京")
        chart = calculate_bazi(birth)
        assert chart.pillars["year"].full == "己卯"
        assert chart.pillars["month"].full == "丙子"
        assert chart.pillars["day"].full == "戊午"
        assert chart.pillars["hour"].full == "壬子"

    def test_2024_0204_1700_beijing_female(self):
        """
        2024-02-04 17:00 北京 女 — 立春边界
        期望值 = 真太阳时修正后 (北京 116.4E, 修正约-28min → 16:31 申时)
        注: lunar-python 独立验证 2024-02-04 日柱=戊戌 (bazi-tool fixture 写的壬辰有误)
        """
        birth = BirthInfo(date=date(2024, 2, 4), time="17:00", gender="female", city="北京")
        chart = calculate_bazi(birth)
        assert chart.pillars["year"].full == "甲辰"   # 立春后
        assert chart.pillars["month"].full == "丙寅"  # 立春后
        assert chart.pillars["day"].full == "戊戌"    # lunar-python 验证
        # 修正后 16:31 → 申时 → 庚申 (flyingstar/meen 等工具确认辛酉为未修正值)
        assert chart.pillars["hour"].full == "庚申"

    def test_hour_ganzhi_accuracy(self):
        """时辰测试：不同时辰不同时柱"""
        # 2026-08-13 07:00 辰时
        gz1 = get_day_ganzhi(date(2026, 8, 13), 7, 0)
        # 2026-08-13 15:00 申时
        gz2 = get_day_ganzhi(date(2026, 8, 13), 15, 0)
        assert gz1["hour"] != gz2["hour"], "不同时辰应不同时柱"

    # ========== 国际版本 (M7) ==========
    def test_newyork_intl_timezone(self):
        """纽约 1990-06-15 14:00 EST (UTC-5) — 时区迁移 + 真太阳时"""
        birth = BirthInfo(date=date(1990, 6, 15), time="14:00", gender="male", city="纽约")
        chart = calculate_bazi(birth)
        assert chart.input["tz_offset"] == -5.0
        assert chart.input["solar_correction"] is True
        # 纽约 → UTC 19:00 → 北京 06-16 03:00; 经度 -74 (75W标准) → +4min → 03:04 寅时
        assert chart.pillars["year"].full == "庚午"
        assert chart.pillars["month"].full == "壬午"
        assert chart.pillars["day"].full == "壬子"
        assert chart.pillars["hour"].full == "壬寅"  # 寅时

    def test_london_intl_timezone(self):
        """伦敦 1985-03-20 10:30 GMT (UTC+0) — 经度约0 → 无修正"""
        birth = BirthInfo(date=date(1985, 3, 20), time="10:30", gender="female", city="伦敦")
        chart = calculate_bazi(birth)
        assert chart.pillars["year"].full == "乙丑"
        assert chart.pillars["month"].full == "己卯"
        assert chart.pillars["day"].full == "戊午"
        assert chart.pillars["hour"].full == "辛酉"

    def test_paris_dst_summer(self):
        """巴黎 1995-07-01 20:30 CEST (夏令时 UTC+2) — DST 处理"""
        birth = BirthInfo(date=date(1995, 7, 1), time="20:30", gender="female", city="巴黎",
                          daylight_saving=True)
        chart = calculate_bazi(birth)
        assert chart.pillars["year"].full == "乙亥"
        assert chart.pillars["month"].full == "壬午"
        assert chart.pillars["day"].full == "甲午"
        # 20:30 CEST = UTC 18:30 → 北京 07-02 02:30 丑时
        assert chart.pillars["hour"].full == "乙丑"

    def test_paris_no_dst_winter(self):
        """巴黎 1995-01-15 10:00 CET (标准时间 UTC+1) — 冬季无夏令时"""
        birth = BirthInfo(date=date(1995, 1, 15), time="10:00", gender="male", city="巴黎",
                          daylight_saving=False)
        chart = calculate_bazi(birth)
        assert chart.pillars["year"].full == "甲戌"
        assert chart.pillars["month"].full == "丁丑"
        assert chart.pillars["day"].full == "丙午"
        assert chart.pillars["hour"].full == "丙申"

    def test_tokyo_intl_timezone(self):
        """东京 2001-09-11 09:00 JST (UTC+9) — 亚洲时区"""
        birth = BirthInfo(date=date(2001, 9, 11), time="09:00", gender="female", city="东京")
        chart = calculate_bazi(birth)
        assert chart.pillars["year"].full == "辛巳"
        assert chart.pillars["month"].full == "丁酉"
        assert chart.pillars["day"].full == "丁丑"
        assert chart.pillars["hour"].full == "甲辰"

    def test_sydney_dst_summer(self):
        """悉尼 1978-12-25 15:00 AEDT (夏令时 UTC+11) — 南半球夏令时"""
        birth = BirthInfo(date=date(1978, 12, 25), time="15:00", gender="male", city="悉尼",
                          daylight_saving=True)
        chart = calculate_bazi(birth)
        assert chart.pillars["year"].full == "戊午"
        assert chart.pillars["month"].full == "甲子"
        assert chart.pillars["day"].full == "辛酉"
        # 15:00 AEDT = UTC 04:00 → 北京 12:00 (~午时, 经度+5min → 12:05 甲午)
        assert chart.pillars["hour"].full == "甲午"

    def test_sydney_no_dst_winter(self):
        """悉尼 1978-06-25 15:00 AEST (标准时间 UTC+10) — 冬季无夏令时"""
        birth = BirthInfo(date=date(1978, 6, 25), time="15:00", gender="female", city="悉尼",
                          daylight_saving=False)
        chart = calculate_bazi(birth)
        assert chart.pillars["year"].full == "戊午"
        assert chart.pillars["month"].full == "戊午"
        assert chart.pillars["day"].full == "戊午"
        assert chart.pillars["hour"].full == "己未"


class TestFiveElements:
    """五行力量分析"""

    def test_1983_0515(self):
        """1983-05-15 癸水日主，水偏强"""
        gz = get_day_ganzhi(date(1983, 5, 15), 14, 30)
        fe = analyze_five_elements(gz)
        water = float(fe["water"]["score"])
        assert water >= 1.0

    def test_2000_0101(self):
        """2000-01-01 戊土日主"""
        gz = get_day_ganzhi(date(2000, 1, 1), 0, 0)
        fe = analyze_five_elements(gz)
        assert fe["earth"]["chinese"] == "土"


class TestDayMasterStrength:
    """日主强弱"""

    def test_1983_0515_weak(self):
        """癸水日主，巳月失令，偏弱"""
        gz = get_day_ganzhi(date(1983, 5, 15), 14, 30)
        strength = judge_day_master_strength("癸", gz["month"].branch, gz)
        assert strength == "偏弱"


class TestYongShen:
    """喜用神"""

    def test_1983_0515_water_needs_gold(self):
        """癸水偏弱 → 喜金水"""
        gz = get_day_ganzhi(date(1983, 5, 15), 14, 30)
        fe = analyze_five_elements(gz)
        ys = calculate_yongshen_v1("癸", "偏弱", fe)
        # 喜用神必须包含中文五行
        for f in ys["favorable"]:
            assert f in ["木", "火", "土", "金", "水"]
        for a in ys["avoid"]:
            assert a in ["木", "火", "土", "金", "水"]
        assert "水" in ys["favorable"]  # 同我
        assert "金" in ys["favorable"]  # 生我

    def test_yongshen_method_label(self):
        """喜用神标注方法版本"""
        gz = get_day_ganzhi(date(1983, 5, 15), 14, 30)
        fe = analyze_five_elements(gz)
        ys = calculate_yongshen_v1("癸", "偏弱", fe)
        assert ys["method"] == "wuxing-support-v1"