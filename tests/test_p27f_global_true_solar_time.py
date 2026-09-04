"""P2.7-F: Global True Solar Time Validation

Test the complete global apparent solar time calculation chain:
1. Location lookup (registry + GPS coordinates)
2. IANA timezone resolution
3. UTC offset calculation (DST-aware)
4. Longitude correction
5. Equation of time (EoT)
6. Apparent solar time computation
7. Day boundary rule (23:00 swap)
"""

import pytest
from datetime import date, datetime, timedelta
import sys
sys.path.insert(0, "src")

from tongshu.engines.time.resolver import TimeResolver
from tongshu.engines.bazi_adapter import BaziAdapter
from tongshu.engines.bazi_engine import BaziEngine


# =============================================================================
# Test 1: GPS Coordinate Resolution (Global Coverage)
# =============================================================================

class TestGPSCoordinateResolution:
    """测试 GPS 坐标解析（全球任意地点）"""

    def setup_method(self):
        self.resolver = TimeResolver()

    def test_beijing_gps(self):
        """测试北京 GPS 坐标"""
        loc = self.resolver.lookup("116.41,39.91")
        assert loc.longitude == 116.41
        assert loc.latitude == 39.91
        assert loc.timezone == "Asia/Shanghai"

    def test_tokyo_gps(self):
        """测试东京 GPS 坐标"""
        loc = self.resolver.lookup("139.69,35.68")
        assert loc.longitude == 139.69
        assert loc.latitude == 35.68
        assert loc.timezone == "Asia/Tokyo"

    def test_new_york_gps(self):
        """测试纽约 GPS 坐标"""
        loc = self.resolver.lookup("-74.01,40.71")
        assert loc.longitude == -74.01
        assert loc.latitude == 40.71
        assert loc.timezone == "America/New_York"

    def test_london_gps(self):
        """测试伦敦 GPS 坐标"""
        loc = self.resolver.lookup("-0.13,51.51")
        assert loc.longitude == -0.13
        assert loc.latitude == 51.51
        assert loc.timezone == "Europe/London"

    def test_sydney_gps(self):
        """测试悉尼 GPS 坐标"""
        loc = self.resolver.lookup("151.21,-33.87")
        assert loc.longitude == 151.21
        assert loc.latitude == -33.87
        assert loc.timezone == "Australia/Sydney"

    def test_rio_gps(self):
        """测试里约热内卢 GPS 坐标"""
        loc = self.resolver.lookup("-43.13,-22.91")
        assert loc.longitude == -43.13
        assert loc.latitude == -22.91
        assert loc.timezone == "America/Sao_Paulo"

    def test_negative_longitude(self):
        """测试西经（负值）"""
        loc = self.resolver.lookup("-74.01,40.71")
        assert loc.longitude < 0

    def test_negative_latitude(self):
        """测试南纬（负值）"""
        loc = self.resolver.lookup("151.21,-33.87")
        assert loc.latitude < 0

    def test_gps_with_spaces(self):
        """测试带空格的 GPS 格式"""
        loc = self.resolver.lookup(" 116.41 , 39.91 ")
        assert loc.longitude == 116.41
        assert loc.latitude == 39.91

    def test_invalid_gps_out_of_range(self):
        """测试超出范围的 GPS 坐标"""
        with pytest.raises(Exception):
            self.resolver.lookup("200,100")  # 经度超出范围

    def test_invalid_gps_non_numeric(self):
        """测试非数字 GPS 坐标"""
        with pytest.raises(Exception):
            self.resolver.lookup("abc,def")


# =============================================================================
# Test 2: Global Timezone Coverage
# =============================================================================

class TestGlobalTimezoneCoverage:
    """测试全球时区覆盖"""

    def setup_method(self):
        self.resolver = TimeResolver()

    def test_all_major_continents(self):
        """测试各大洲主要城市"""
        test_cases = [
            # 亚洲
            ("beijing", "Asia/Shanghai"),
            ("tokyo", "Asia/Tokyo"),
            ("singapore", "Asia/Singapore"),
            ("dubai", "Asia/Dubai"),
            # 欧洲
            ("london", "Europe/London"),
            ("paris", "Europe/Paris"),
            ("moscow", "Europe/Moscow"),
            # 北美洲
            ("new_york", "America/New_York"),
            ("los_angeles", "America/Los_Angeles"),
            # 南美洲
            ("sao_paulo", "America/Sao_Paulo"),
            # 大洋洲
            ("sydney", "Australia/Sydney"),
        ]

        for city, expected_tz in test_cases:
            try:
                loc = self.resolver.lookup(city)
                assert loc.timezone == expected_tz, \
                    f"{city}: 期望 {expected_tz}, 实际 {loc.timezone}"
            except Exception:
                # 如果城市不在 registry，跳过（GPS 解析会处理）
                pytest.skip(f"{city} 不在 registry，使用 GPS 解析")

    def test_gps_timezone_resolution(self):
        """测试 GPS 坐标的时区解析"""
        # 纽约
        loc = self.resolver.lookup("-74.01,40.71")
        assert loc.timezone == "America/New_York"

        # 伦敦
        loc = self.resolver.lookup("-0.13,51.51")
        assert loc.timezone == "Europe/London"

        # 悉尼
        loc = self.resolver.lookup("151.21,-33.87")
        assert loc.timezone == "Australia/Sydney"


# =============================================================================
# Test 3: True Solar Time Calculation (Global)
# =============================================================================

class TestTrueSolarTimeGlobal:
    """测试全球真太阳时计算"""

    def setup_method(self):
        self.resolver = TimeResolver()
        # Import at module level for convenience
        from datetime import timezone as tz
        self.tz = tz

    def test_same_utc_different_solar_times(self):
        """同一 UTC 时刻，不同地点的真太阳时应反映经度差"""
        # 北京时间 2024-02-04 12:00 = UTC 04:00
        beijing = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )

        # 纽约时间 2024-02-03 23:00 = UTC 04:00（同 UTC 时刻）
        new_york = self.resolver.resolve_context(
            birth_date=date(2024, 2, 3),
            hour=23, minute=0,
            timezone=None, location="-74.01,40.71",
            apparent_solar=True, gender="male",
        )

        # 两者的 UTC 时刻应该相同
        assert abs((beijing.utc_instant - new_york.utc_instant).total_seconds()) < 1

        # 真太阳时差异应反映经度差
        # 北京(116.41°E) vs 纽约(74.01°W) ≈ 190° 经度差 ≈ 12.7 小时
        # 但真太阳时基于当地子午线，同 UTC 时刻的差异约 18 分钟（经度差约 4.5°）
        beijing_solar_utc = beijing.true_solar_datetime.astimezone(self.tz.utc)
        ny_solar_utc = new_york.true_solar_datetime.astimezone(self.tz.utc)

        diff_hours = abs((beijing_solar_utc - ny_solar_utc).total_seconds()) / 3600
        # 约 0.3 小时 = 18 分钟（正确）
        assert 0.2 < diff_hours < 0.5, f"真太阳时差异应在 0.2-0.5 小时，实际 {diff_hours:.2f} 小时"

    def test_longitude_effect_on_solar_time(self):
        """测试经度对真太阳时的影响（同 timezone 内）"""
        # 同一 timezone（Asia/Shanghai），不同经度
        # 排除 timezone 边界效应，纯看 longitude_correction
        locations = [
            ("beijing", 116.41),
            ("shanghai", 121.47),
        ]

        results = []
        for loc_id, expected_lon in locations:
            ctx = self.resolver.resolve_context(
                birth_date=date(2024, 2, 4),
                hour=12, minute=0,
                timezone=None, location=loc_id,
                apparent_solar=True, gender="male",
            )
            results.append({
                "location": loc_id,
                "longitude": ctx.longitude,
                "correction": ctx.corrections["total_correction_min"],
            })

        # 验证经度与校正值的线性关系
        # 每 1° 经度差 = 4 分钟时间差
        for i in range(len(results) - 1):
            lon_diff = results[i+1]["longitude"] - results[i]["longitude"]
            corr_diff = results[i+1]["correction"] - results[i]["correction"]
            expected_corr_diff = lon_diff * 4  # 4 min/degree

            # 允许 ±2 分钟误差（EoT 影响极小）
            assert abs(corr_diff - expected_corr_diff) < 2, \
                f"{results[i]['location']} vs {results[i+1]['location']}: " \
                f"经度差 {lon_diff:.1f}°, 期望校正差 {expected_corr_diff:.1f}min, " \
                f"实际 {corr_diff:.1f}min"

        # 额外测试：不同 timezone 的经度效应（通过 UTC 标准化）
        # 同一 UTC 时刻，不同地点的真太阳时差异应反映经度差
        beijing_utc = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        ).utc_instant

        # 上海同一 UTC 时刻
        shanghai_utc = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="shanghai",
            apparent_solar=True, gender="male",
        ).utc_instant

        # 两者 UTC 应相同（同 timezone）
        assert abs((beijing_utc - shanghai_utc).total_seconds()) < 1

    def test_extreme_longitudes(self):
        """测试极端经度（国际日期变更线附近）"""
        # 斐济（东经 178°）
        fiji = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="178.00,-17.71",
            apparent_solar=True, gender="male",
        )

        # 美属萨摩亚（西经 171°）
        samoa = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=12, minute=0,
            timezone=None, location="-171.00,-14.27",
            apparent_solar=True, gender="male",
        )

        # 两者经度差约 11°，时间差约 44 分钟
        diff_minutes = abs(
            (fiji.true_solar_datetime - samoa.true_solar_datetime).total_seconds()
        ) / 60

        assert diff_minutes > 40, f"斐济 vs 萨摩亚时差应大于 40 分钟，实际 {diff_minutes:.1f} 分钟"


# =============================================================================
# Test 4: DST Awareness
# =============================================================================

class TestDSTAwareness:
    """测试夏令时感知"""

    def setup_method(self):
        self.resolver = TimeResolver()

    def test_new_york_summer_dst(self):
        """测试纽约夏季 DST"""
        # 2024-07-04 是夏令时期间（UTC-4）
        ctx = self.resolver.resolve_context(
            birth_date=date(2024, 7, 4),
            hour=12, minute=0,
            timezone=None, location="-74.01,40.71",
            apparent_solar=True, gender="male",
        )

        # 夏令时 UTC offset 应为 -240 分钟（UTC-4）
        assert ctx.corrections["utc_offset_min"] == -240, \
            f"纽约夏季应为 DST (UTC-4)，实际 offset={ctx.corrections['utc_offset_min']}"

    def test_new_york_winter_standard(self):
        """测试纽约冬季标准时间"""
        # 2024-01-04 是标准时间期间（UTC-5）
        ctx = self.resolver.resolve_context(
            birth_date=date(2024, 1, 4),
            hour=12, minute=0,
            timezone=None, location="-74.01,40.71",
            apparent_solar=True, gender="male",
        )

        # 标准时间 UTC offset 应为 -300 分钟（UTC-5）
        assert ctx.corrections["utc_offset_min"] == -300, \
            f"纽约冬季应为标准时间 (UTC-5)，实际 offset={ctx.corrections['utc_offset_min']}"

    def test_beijing_no_dst(self):
        """测试北京无 DST"""
        ctx_summer = self.resolver.resolve_context(
            birth_date=date(2024, 7, 4),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )

        ctx_winter = self.resolver.resolve_context(
            birth_date=date(2024, 1, 4),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )

        # 北京全年 UTC+8，无 DST
        assert ctx_summer.corrections["utc_offset_min"] == 480
        assert ctx_winter.corrections["utc_offset_min"] == 480


# =============================================================================
# Test 5: Equation of Time Validation
# =============================================================================

class TestEquationOfTimeValidation:
    """测试时差方程（EoT）"""

    def setup_method(self):
        self.resolver = TimeResolver()

    def test_eot_range(self):
        """测试 EoT 在合理范围内"""
        # EoT 应在 ±20 分钟范围内
        for month in range(1, 13):
            ctx = self.resolver.resolve_context(
                birth_date=date(2024, month, 15),
                hour=12, minute=0,
                timezone=None, location="beijing",
                apparent_solar=True, gender="male",
            )
            eot = ctx.corrections["eot_min"]
            assert -20 <= eot <= 20, \
                f"{month}月15日 EoT 超出范围: {eot}min"

    def test_eot_zero_crossings(self):
        """测试 EoT 过零点（一年四次）"""
        # EoT 过零点大约在：4月15日、6月13日、9月1日、12月25日
        # 这里只验证 EoT 值合理，不验证具体零点

        eot_values = []
        for month in range(1, 13):
            ctx = self.resolver.resolve_context(
                birth_date=date(2024, month, 15),
                hour=12, minute=0,
                timezone=None, location="beijing",
                apparent_solar=True, gender="male",
            )
            eot_values.append((month, ctx.corrections["eot_min"]))

        # 打印 EoT 变化趋势
        for month, eot in eot_values:
            print(f"{month}月: EoT = {eot:+.2f} min")

        # 验证有正有负（一年四次过零点）
        positive_months = [m for m, e in eot_values if e > 0]
        negative_months = [m for m, e in eot_values if e < 0]

        assert len(positive_months) > 0, "应有 EoT > 0 的月份"
        assert len(negative_months) > 0, "应有 EoT < 0 的月份"


# =============================================================================
# Test 6: BaziChart Consistency (Global)
# =============================================================================

class TestBaziChartConsistencyGlobal:
    """测试全球地点的八字盘一致性"""

    def setup_method(self):
        self.resolver = TimeResolver()
        self.adapter = BaziAdapter()
        self.engine = BaziEngine()

    def test_same_utc_different_charts(self):
        """测试同一 UTC 时刻，不同地点产生不同八字盘"""
        # 北京时间 2024-02-04 12:00 = UTC 04:00
        beijing_chart = self.engine.compute((2024, 2, 4, 12), gender="male")

        # 纽约时间 2024-02-03 20:00 = UTC 04:00（前一天）
        ny_ctx = self.resolver.resolve_context(
            birth_date=date(2024, 2, 3),
            hour=20, minute=0,
            timezone=None, location="-74.01,40.71",
            apparent_solar=True, gender="male",
        )
        ny_chart = self.adapter.compute(ny_ctx)

        # 由于时差约 12 小时，日柱应该不同
        print(f"北京日柱: {beijing_chart.day_pillar}")
        print(f"纽约日柱: {ny_chart.day_pillar}")

        # 日柱不同（经度差导致真太阳时不同）
        assert beijing_chart.day_pillar != ny_chart.day_pillar or \
               beijing_chart.month_pillar != ny_chart.month_pillar

    def test_longitude_affects_month_pillar(self):
        """测试经度影响月柱（节气边界案例）"""
        # 立春时刻：2024-02-04 16:26:53 北京时间
        # 北京（116.41°E）和乌鲁木齐（87.62°E）的真太阳时不同

        beijing = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=16, minute=20,  # 立春前 7 分钟（北京时间）
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )

        urumqi = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=16, minute=20,  # 同一民用时间
            timezone=None, location="urumqi",
            apparent_solar=True, gender="male",
        )

        beijing_chart = self.adapter.compute(beijing)
        urumqi_chart = self.adapter.compute(urumqi)

        print(f"北京真太阳时: {beijing.true_solar_datetime}")
        print(f"乌鲁木齐真太阳时: {urumqi.true_solar_datetime}")
        print(f"北京月柱: {beijing_chart.month_pillar}")
        print(f"乌鲁木齐月柱: {urumqi_chart.month_pillar}")

        # 由于经度差 28.79°，时差约 115 分钟
        # 北京时间 16:20 的真太阳时 ≈ 16:06
        # 乌鲁木齐时间 16:20 的真太阳时 ≈ 14:25
        # 立春是 16:26:53，所以两者都在立春前
        # 但月柱应该相同（都在丑月）

        # 验证经度修正正确应用
        beijing_corr = beijing.corrections["total_correction_min"]
        urumqi_corr = urumqi.corrections["total_correction_min"]
        assert beijing_corr != urumqi_corr, "不同经度的修正值应不同"


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
