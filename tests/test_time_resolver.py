"""TimeResolver / 真太阳时 tests (P0-2 Profile Gate).

Covers:
  - equation-of-time against published astronomical values (P0-14 re-check ok)
  - location registry lookup (id / name_zh / English alias, case-insensitive)
  - IANA timezone normalization, DST-aware ref meridian (Berlin summer 30°E)
  - 真太阳时经度校正 + EoT
  - 23:00 换日 at the apparent-solar boundary (roll / reclassify cases)
  - minute=None → 时辰中点 assumption + warning
"""

from __future__ import annotations
import unittest
from datetime import date

from tongshu.engines.time_resolver import (
    LocationError,
    TimeResolver,
    TimezoneError,
    equation_of_time,
)

_RESOLVER = TimeResolver()  # backend/data/locations.json (module-relative default)


class TestEquationOfTime(unittest.TestCase):
    """EoT = apparent − mean; verified against published values (delta ±1.5)."""

    def test_published_extrema(self):
        cases = {
            date(2026, 2, 11): -14.2,  # global min
            date(2026, 5, 14): 3.6,    # secondary max
            date(2026, 7, 26): -6.5,   # secondary min
            date(2026, 11, 3): 16.4,   # global max
        }
        for d, expected in cases.items():
            self.assertAlmostEqual(equation_of_time(d), expected, delta=1.5)

    def test_zero_crossings(self):
        for d in (date(2026, 4, 15), date(2026, 6, 13), date(2026, 9, 1), date(2026, 12, 25)):
            self.assertAlmostEqual(equation_of_time(d), 0.0, delta=1.0)

    def test_range(self):
        for m in range(1, 13):
            for day in (1, 10, 20, 28):
                v = equation_of_time(date(2026, m, day))
                self.assertLessEqual(abs(v), 16.5)


class TestLocationLookup(unittest.TestCase):
    def test_by_id(self):
        loc = _RESOLVER.lookup("CN_BEIJING")
        self.assertEqual(loc.timezone, "Asia/Shanghai")
        self.assertAlmostEqual(loc.longitude, 116.41)

    def test_localized_and_english_alias_case_insensitive(self):
        self.assertEqual(_RESOLVER.lookup("北京").id, "CN_BEIJING")
        self.assertEqual(_RESOLVER.lookup("beijing").id, "CN_BEIJING")
        self.assertEqual(_RESOLVER.lookup("Berlin").id, "DE_BERLIN")
        self.assertEqual(_RESOLVER.lookup("東京").id, "JP_TOKYO")
        self.assertEqual(_RESOLVER.lookup("New York").id, "US_NEW_YORK")

    def test_unknown_location_raises(self):
        with self.assertRaises(LocationError):
            _RESOLVER.lookup("Atlantis")

    def test_invalid_timezone_raises(self):
        with self.assertRaises(TimezoneError):
            _RESOLVER.resolve(
                birth_date=date(1984, 12, 7), hour=16, minute=None,
                timezone="Bad/Zone", location="CN_BEIJING",
            )


class TestTrueSolarResolution(unittest.TestCase):
    """真太阳时 + 经度校正 + 23:00 换日(EoT≈0 的 2026-09-01 便于干净断言)。

    北京经度校正 (116.41−120)×4 = −14.36 min;2026-09-01 EoT ≈ −0.41
    → total ≈ −14.77 min。
    """

    def test_beijing_midday_no_roll(self):
        r = _RESOLVER.resolve(birth_date=date(2026, 9, 1), hour=16, minute=0,
                              timezone=None, location="北京")
        self.assertEqual(r.effective_date, date(2026, 9, 1))
        self.assertEqual(r.effective_hour, 15)  # 16:00 − 14.77 ≈ 15:45,仍申时
        self.assertFalse(r.day_rolled)
        self.assertEqual(r.corrections["longitude_correction_min"], -14.36)
        self.assertAlmostEqual(r.corrections["total_correction_min"], -14.77, delta=0.5)

    def test_2330_rolls_to_next_day(self):
        # 23:30 − 14.77 ≈ 23:15 → hour 23 → 换日 → 次日 子时
        r = _RESOLVER.resolve(birth_date=date(2026, 9, 1), hour=23, minute=30,
                              timezone=None, location="北京")
        self.assertEqual(r.effective_date, date(2026, 9, 2))
        self.assertEqual(r.effective_hour, 23)
        self.assertTrue(r.day_rolled)

    def test_2305_reclassified_to_hai(self):
        # 23:05 − 14.77 ≈ 22:50 → <23 → 亥时(同日),不再跨日
        r = _RESOLVER.resolve(birth_date=date(2026, 9, 1), hour=23, minute=5,
                              timezone=None, location="北京")
        self.assertEqual(r.effective_date, date(2026, 9, 1))
        self.assertEqual(r.effective_hour, 22)
        self.assertFalse(r.day_rolled)

    def test_0010_becomes_previous_day_late_zi(self):
        # 00:10 − 14.77 ≈ 前一日 23:55 → hour 23 → 换日回当日 → 当日晚子时
        r = _RESOLVER.resolve(birth_date=date(2026, 9, 1), hour=0, minute=10,
                              timezone=None, location="北京")
        self.assertEqual(r.effective_date, date(2026, 9, 1))
        self.assertEqual(r.effective_hour, 23)
        self.assertTrue(r.day_rolled)

    def test_apparent_solar_off_keeps_wall_clock(self):
        r = _RESOLVER.resolve(birth_date=date(2026, 9, 1), hour=16, minute=0,
                              timezone=None, location="北京", apparent_solar=False)
        self.assertEqual(r.effective_hour, 16)
        self.assertFalse(r.day_rolled)
        self.assertFalse(r.corrections["applied"])

    def test_minute_none_midpoint_warning(self):
        # minute=None → 时辰中点 (16:30);校正后 ≈ 16:15 → minute 15
        r = _RESOLVER.resolve(birth_date=date(2026, 9, 1), hour=16, minute=None,
                              timezone=None, location="北京")
        self.assertEqual(r.effective_minute, 15)
        self.assertTrue(any("时辰中点" in w for w in r.warnings))

    def test_berlin_summer_dst_ref_meridian_30(self):
        # 欧洲/柏林 夏季 UTC+2 → ref 30°E;经度校正 (13.41−30)×4 = −66.36 min
        r = _RESOLVER.resolve(birth_date=date(2026, 7, 15), hour=12, minute=0,
                              timezone=None, location="Berlin")
        self.assertEqual(r.corrections["utc_offset_min"], 120)
        self.assertEqual(r.corrections["ref_meridian"], 30.0)
        self.assertAlmostEqual(r.corrections["longitude_correction_min"], -66.36, delta=0.01)
        # 12:00 − 66.36 − EoT(≈−5.5) ≈ 10:48 → 巳时
        self.assertEqual(r.effective_hour, 10)

    def test_berlin_winter_ref_meridian_15(self):
        r = _RESOLVER.resolve(birth_date=date(2026, 1, 15), hour=12, minute=0,
                              timezone=None, location="Berlin")
        self.assertEqual(r.corrections["utc_offset_min"], 60)
        self.assertEqual(r.corrections["ref_meridian"], 15.0)

    def test_timezone_derived_from_location(self):
        r = _RESOLVER.resolve(birth_date=date(1984, 12, 7), hour=16, minute=30,
                              timezone=None, location="Shanghai")
        self.assertEqual(r.timezone, "Asia/Shanghai")
        self.assertEqual(r.location_id, "CN_SHANGHAI")

    def test_explicit_timezone_overrides_location(self):
        r = _RESOLVER.resolve(birth_date=date(1984, 12, 7), hour=16, minute=30,
                              timezone="Asia/Tokyo", location="CN_BEIJING")
        self.assertEqual(r.timezone, "Asia/Tokyo")
        self.assertEqual(r.location_id, "CN_BEIJING")


if __name__ == "__main__":
    unittest.main()
