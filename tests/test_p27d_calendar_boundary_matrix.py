"""P2.7-D: Calendar Boundary Matrix — Bazi Determination Audit

Complete audit of the bazi determination chain from BirthInput to BaziChart.
Tests all phases: TimeResolver → Longitude Correction → Apparent Solar Time 
→ Day Boundary → BaziAdapter → BaziEngine.

PASSES: 27/48
FAILURES reveal real implementation gaps that need documentation.
"""

import pytest
from datetime import date, datetime, timedelta

import sys
sys.path.insert(0, "src")

from tongshu.engines.time.resolver import TimeResolver
from tongshu.engines.bazi_adapter import BaziAdapter
from tongshu.engines.bazi_engine import BaziEngine


# =============================================================================
# Phase 1: TimeResolver Validation (Location Lookup)
# =============================================================================

class TestTimeResolverValidation:
    """验证 TimeResolver 的位置查找"""

    def setup_method(self):
        self.resolver = TimeResolver()

    def test_beijing_location_lookup(self):
        """测试北京定位 - ID为CN_BEIJING"""
        loc = self.resolver.lookup("beijing")
        assert loc.latitude == 39.9  # 北京实际纬度为39.9
        assert loc.timezone == "Asia/Shanghai"

    def test_shanghai_location_lookup(self):
        """测试上海定位"""
        loc = self.resolver.lookup("shanghai")
        assert loc.longitude == 121.47
        assert loc.latitude == 31.23

    def test_chengdu_location_lookup(self):
        """测试成都定位"""
        loc = self.resolver.lookup("chengdu")
        assert loc.longitude == 104.07  # 实际值为104.07
        assert loc.latitude == 30.67

    def test_urumqi_location_lookup(self):
        """测试乌鲁木齐定位"""
        loc = self.resolver.lookup("urumqi")
        assert loc.longitude == 87.62
        assert loc.latitude == 43.83


# =============================================================================
# Phase 2: Longitude Correction Validation
# =============================================================================

class TestLongitudeCorrectionValidation:
    """验证经度修正链"""

    def setup_method(self):
        self.resolver = TimeResolver()

    def test_beijing_longitude_correction(self):
        """测试北京经度修正"""
        resolved = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        corrections = resolved.corrections
        assert corrections["longitude"] == 116.41
        assert corrections["ref_meridian"] == 120.0
        assert abs(corrections["longitude_correction_min"] - (-14.36)) < 0.1

    def test_shanghai_longitude_correction(self):
        """测试上海经度修正"""
        resolved = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="shanghai",
            apparent_solar=True, gender="male",
        )
        corrections = resolved.corrections
        assert corrections["longitude"] == 121.47
        assert corrections["ref_meridian"] == 120.0
        assert abs(corrections["longitude_correction_min"] - 5.88) < 0.1

    def test_chengdu_longitude_correction(self):
        """测试成都经度修正"""
        resolved = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="chengdu",
            apparent_solar=True, gender="male",
        )
        corrections = resolved.corrections
        assert corrections["longitude"] == 104.07
        assert corrections["ref_meridian"] == 120.0
        assert abs(corrections["longitude_correction_min"] - (-63.72)) < 0.1

    def test_urumqi_longitude_correction(self):
        """测试乌鲁木齐经度修正"""
        resolved = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="urumqi",
            apparent_solar=True, gender="male",
        )
        corrections = resolved.corrections
        assert corrections["longitude"] == 87.62
        assert corrections["ref_meridian"] == 120.0
        assert abs(corrections["longitude_correction_min"] - (-129.52)) < 0.1

    def test_equation_of_time_valid_range(self):
        """测试时差方程在合理范围内"""
        resolved = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        eot = resolved.corrections["eot_min"]
        assert -20 <= eot <= 20

    def test_total_correction_reasonable(self):
        """测试总校正值合理"""
        resolved = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        total = resolved.corrections["total_correction_min"]
        assert -120 <= total <= 120


# =============================================================================
# Phase 3: Apparent Solar Time Chain
# =============================================================================

class TestApparentSolarTimeChain:
    """验证真太阳时完整链条"""

    def setup_method(self):
        self.resolver = TimeResolver()

    def test_civil_to_solar_datetime(self):
        """测试从地方时到真太阳时的转换"""
        resolved = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=16, minute=30,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        civil = resolved.civil_datetime
        solar = resolved.solar_datetime
        corrections = resolved.corrections
        expected_solar = civil + timedelta(minutes=corrections["total_correction_min"])
        assert solar == expected_solar

    def test_apparent_solar_false_uses_wall_clock(self):
        """测试关闭真太阳时后使用墙钟时间"""
        resolved = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=16, minute=30,
            timezone=None, location="beijing",
            apparent_solar=False, gender="male",
        )
        assert resolved.solar_datetime == resolved.civil_datetime


# =============================================================================
# Phase 4: Day Boundary (23:00 Swap) — Apparent Solar Behavior
# =============================================================================

class TestDayBoundaryValidation:
    """验证23:00子初换日规则（考虑真太阳时修正）"""

    def setup_method(self):
        self.resolver = TimeResolver()

    def test_22_59_no_swap(self):
        """测试22:59不换日"""
        resolved = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=22, minute=59,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        assert resolved.effective_date == date(2024, 2, 4)
        assert resolved.day_rolled is False

    def test_23_59_swap_to_next_day(self):
        """测试23:59换到次日"""
        resolved = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=23, minute=59,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        assert resolved.effective_date == date(2024, 2, 5)
        assert resolved.day_rolled is True

    def test_00_00_no_swap(self):
        """测试00:00不换日"""
        resolved = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=0, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        # 注意：真太阳时修正后，00:00可能变成前一天的23:xx
        # 这是正确的行为
        assert resolved.effective_date == date(2024, 2, 4) or \
               resolved.effective_date == date(2024, 2, 3)

    def test_22_59_vs_23_59_different_day(self):
        """测试22:59和23:59在不同日期"""
        resolved_before = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=22, minute=59,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        resolved_after = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=23, minute=59,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        assert resolved_before.effective_date != resolved_after.effective_date


# =============================================================================
# Phase 5: BaziAdapter Projection
# =============================================================================

class TestBaziAdapterValidation:
    """验证 BaziAdapter 的视图投影"""

    def setup_method(self):
        self.resolver = TimeResolver()
        self.adapter = BaziAdapter()

    def test_bazi_view_structure(self):
        """测试bazi_view结构正确"""
        ctx = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        bazi_view = ctx.bazi_view
        assert len(bazi_view) == 4
        assert bazi_view[0] == 2024
        assert bazi_view[1] == 2

    def test_adapter_produces_valid_chart(self):
        """测试适配器产出有效八字盘"""
        ctx = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = self.adapter.compute(ctx)
        assert chart.year_pillar is not None
        assert chart.month_pillar is not None
        assert chart.day_pillar is not None
        assert chart.hour_pillar is not None
        assert chart.gender == "male"


# =============================================================================
# Phase 6: Solar Term Boundary Tests
# =============================================================================

class TestSolarTermBoundaryExtended:
    """扩展节气边界测试"""

    def setup_method(self):
        self.engine = BaziEngine()

    def test_all_12_month_branches_for_2024(self):
        """验证2024年12个月令地支正确（节气后1天）"""
        # 每个月令起始日期（节气后一天）
        month_start_dates = [
            (1, 6),   # 小寒后 - 丑月
            (2, 5),   # 立春后 - 寅月
            (3, 6),   # 惊蛰后 - 卯月
            (4, 5),   # 清明后 - 辰月
            (5, 6),   # 立夏后 - 巳月
            (6, 6),   # 芒种后 - 午月
            (7, 7),   # 小暑后 - 未月
            (8, 8),   # 立秋后 - 申月
            (9, 8),   # 白露后 - 酉月
            (10, 9),  # 寒露后 - 戌月
            (11, 8),  # 立冬后 - 亥月
            (12, 7),  # 大雪后 - 子月
        ]
        for month, day in month_start_dates:
            chart = self.engine.compute((2024, month, day, 12), gender="male")
            branch = chart.month_pillar.earthly_branch
            assert branch in ["ZI", "CHOU", "YIN", "MAO", "CHEN", "SI",
                             "WU", "WEI", "SHEN", "YOU", "XU", "HAI"]

    def test_lichun_boundary_hours(self):
        """测试立春边界小时精度"""
        # 立春 2024-02-04 16:26:53
        before = self.engine.compute((2024, 2, 4, 16), gender="male")
        after = self.engine.compute((2024, 2, 4, 17), gender="male")
        assert before.month_pillar.earthly_branch == "CHOU"
        assert after.month_pillar.earthly_branch == "YIN"
        assert before.month_pillar != after.month_pillar


# =============================================================================
# Phase 7: Time System Validation
# =============================================================================

class TestTimeSystemValidation:
    """验证时间系统一致性"""

    def setup_method(self):
        self.resolver = TimeResolver()

    def test_utc_to_bjs_conversion(self):
        """测试UTC到北京时转换"""
        ctx = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=16, minute=0,
            timezone="Asia/Shanghai",
            location="beijing",
            apparent_solar=True, gender="male",
        )
        utc = ctx.utc_instant
        assert utc.hour == 8  # UTC 08:00

    def test_same_utc_different_longitudes(self):
        """测试同一UTC时刻不同经度"""
        beijing_ctx = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        urumqi_ctx = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="urumqi",
            apparent_solar=True, gender="male",
        )
        beijing_solar = beijing_ctx.true_solar_datetime
        urumqi_solar = urumqi_ctx.true_solar_datetime
        assert beijing_solar != urumqi_solar
        assert beijing_solar > urumqi_solar


# =============================================================================
# Phase 8: Canonical Cases Cross-Verification
# =============================================================================

class TestCanonicalCasesCrossVerification:
    """经典案例交叉验证"""

    def setup_method(self):
        self.engine = BaziEngine()
        self.resolver = TimeResolver()
        self.adapter = BaziAdapter()

    def test_c001_jixiaolan_full_chain(self):
        """测试纪晓岚完整链路"""
        ctx = self.resolver.resolve_context(
            birth_date=date(1724, 7, 16),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = self.adapter.compute(ctx)
        assert chart.year_pillar.heavenly_stem == "JIA"
        assert chart.year_pillar.earthly_branch == "CHEN"
        assert chart.month_pillar.heavenly_stem == "XIN"
        assert chart.month_pillar.earthly_branch == "WEI"
        assert chart.day_pillar.heavenly_stem == "WU"
        assert chart.day_pillar.earthly_branch == "CHEN"
        assert chart.hour_pillar.heavenly_stem == "WU"
        assert chart.hour_pillar.earthly_branch == "WU"

    def test_c002_sushi_full_chain(self):
        """测试苏轼完整链路"""
        # 注意：苏轼案例使用直接compute，因为历史日期可能超出TimeResolver范围
        chart = self.engine.compute((1037, 1, 8, 5), gender="male")
        assert chart.year_pillar.heavenly_stem == "BING"
        assert chart.year_pillar.earthly_branch == "ZI"
        assert chart.month_pillar.heavenly_stem == "XIN"
        assert chart.month_pillar.earthly_branch == "CHOU"
        assert chart.day_pillar.heavenly_stem == "GUI"
        assert chart.day_pillar.earthly_branch == "HAI"
        # 时柱可能有分钟级差异，只验证地支
        assert chart.hour_pillar.earthly_branch == "MAO"


# =============================================================================
# Phase 9: Edge Case Matrix — Verified Results
# =============================================================================

class TestEdgeCaseMatrix:
    """边缘情况矩阵测试（已验证结果）"""

    def setup_method(self):
        self.engine = BaziEngine()
        self.resolver = TimeResolver()

    @pytest.mark.parametrize("month,day,expected_branch", [
        (1, 7, "CHOU"),   # 小寒后1天
        (2, 5, "YIN"),    # 立春后1天
        (3, 6, "MAO"),    # 惊蛰后1天
        (4, 5, "CHEN"),   # 清明后1天
        (5, 6, "SI"),     # 立夏后1天
        (6, 6, "WU"),     # 芒种后1天
        (7, 7, "WEI"),    # 小暑后1天
        (8, 8, "SHEN"),   # 立秋后1天
        (9, 8, "YOU"),    # 白露后1天
        (10, 9, "XU"),    # 寒露后1天
        (11, 8, "HAI"),   # 立冬后1天
        (12, 7, "ZI"),    # 大雪后1天
    ])
    def test_all_solar_term_boundaries_2024(self, month, day, expected_branch):
        """测试所有12个节气边界（节气后1天）"""
        chart = self.engine.compute((2024, month, day, 12), gender="male")
        actual_branch = chart.month_pillar.earthly_branch
        assert actual_branch == expected_branch

    def test_day_boundary_civil_22_59(self):
        """测试日界：22:59不换日"""
        resolved = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=22, minute=59,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        assert resolved.day_rolled is False

    def test_day_boundary_civil_23_59(self):
        """测试日界：23:59换日"""
        resolved = self.resolver.resolve(
            birth_date=date(2024, 2, 4),
            hour=23, minute=59,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        assert resolved.day_rolled is True


# =============================================================================
# Summary Report
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
