"""
M3+M4 规则引擎 + 输出服务测试
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages", "tongshu-calendar"))

import pytest
from datetime import date

from tongshu.calendar.rules import engine, get_daily_advice, DISCLAIMER_DE, HIGH_RISK_PATTERNS_ZH
from tongshu.calendar.output import build_daily_output, get_current_solar_term
from tongshu.calendar.almanac import get_day_info


class TestRuleEngine:
    """规则引擎"""

    def test_match_20260813(self):
        """2026-08-13 闭日 匹配规则"""
        info = get_day_info(date(2026, 8, 13))
        advice = get_daily_advice(info)
        assert len(advice["yi"]) > 0
        assert len(advice["ji"]) > 0
        assert "disclaimer" in advice

    def test_disclaimer_present(self):
        """免责声明必含"""
        info = get_day_info(date(2026, 8, 13))
        advice = get_daily_advice(info)
        assert advice["disclaimer"] == DISCLAIMER_DE

    def test_high_risk_filter(self):
        """高风险过滤"""
        filtered = engine.filter_high_risk("今天适合投资发财")
        assert "发财" not in filtered
        assert "***" in filtered


class TestOutputService:
    """输出服务"""

    def test_4_modules(self):
        """每日输出包含 5 个模块（含宜忌）"""
        out = build_daily_output(date(2026, 8, 13))
        assert len(out.moduls) == 5
        ids = [m["id"] for m in out.moduls]
        assert "hexagram" in ids
        assert "rhythm" in ids
        assert "seasonal" in ids
        assert "quote" in ids
        assert "yiji" in ids

    def test_ganzhi_in_output(self):
        """干支信息"""
        out = build_daily_output(date(2026, 8, 13))
        assert out.ganzhi["year"] == "丙午"
        assert out.ganzhi["day"] == "己未"

    def test_lunar_in_output(self):
        """农历信息"""
        out = build_daily_output(date(2026, 8, 13))
        assert "七月初一" in out.lunar

    def test_personalization(self):
        """个性化匹配"""
        out = build_daily_output(date(2026, 8, 13), yongshen={"favorable": ["水", "金"], "avoid": ["火"]})
        assert out.personal is not None
        assert out.personal["match"] in ("harmonious", "clashing", "neutral")

    def test_current_solar_term(self):
        """节气区间"""
        assert get_current_solar_term(date(2026, 8, 13)) == "立秋"
        assert get_current_solar_term(date(2026, 12, 25)) == "冬至"
        assert get_current_solar_term(date(2026, 2, 5)) == "立春"

    def test_seasonal_module_content(self):
        """养生模块内容"""
        out = build_daily_output(date(2026, 8, 13))
        seasonal = [m for m in out.moduls if m["id"] == "seasonal"][0]
        assert "Herbst" in seasonal["title_de"] or "Lunge" in seasonal["content_de"]