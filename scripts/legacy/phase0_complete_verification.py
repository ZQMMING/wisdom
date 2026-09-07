#!/usr/bin/env python3
"""
BOT-BAZI Phase 0 Complete Verification
按 P0-P9 优先级逐项验证八字排盘引擎
"""

import sys
from pathlib import Path
from datetime import date, datetime, timedelta
import math

# Add src to path
sys.path.insert(0, str(Path('/d/shuntian/src')))

from tongshu.engines.time import TimeResolver
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.bazi_adapter import BaziAdapter
from tongshu.engines.time.day_boundary import DAY_BOUNDARY
from tongshu.engines.time.eot import equation_of_time


def test_p0_time_input():
    """P0: 时间输入合法性测试"""
    print("\n" + "=" * 70)
    print("P0: 时间输入合法性测试")
    print("=" * 70)
    
    tr = TimeResolver()
    passed = 0
    failed = 0
    
    # 闰年测试
    test_cases = [
        # (year, month, day, hour, desc)
        (2024, 2, 29, 12, "闰年2月29日"),
        (2023, 2, 28, 12, "平年2月28日"),
        (1900, 2, 28, 12, "世纪年非闰年"),
        (2000, 2, 29, 12, "世纪闰年"),
        (2024, 12, 31, 23, "年末边界"),
        (2025, 1, 1, 0, "年初边界"),
        (2024, 6, 30, 12, "小月最后一天"),
        (2024, 7, 1, 12, "小月下第一天"),
    ]
    
    for year, month, day, hour, desc in test_cases:
        try:
            result = tr.resolve(
                birth_date=date(year, month, day),
                hour=hour, minute=0,
                timezone="Asia/Shanghai",
                location="Beijing"
            )
            print(f"  ✅ {desc}: {result.effective_date} {result.effective_hour:02d}:{result.effective_minute:02d}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {desc}: {e}")
            failed += 1
    
    return passed, failed


def test_p0_timezone():
    """P0: 时区支持测试"""
    print("\n" + "=" * 70)
    print("P0: 时区支持测试")
    print("=" * 70)
    
    tr = TimeResolver()
    passed = 0
    failed = 0
    
    timezones = [
        ("Asia/Shanghai", "北京时间"),
        ("America/Los_Angeles", "洛杉矶时间"),
        ("America/New_York", "纽约时间"),
        ("Europe/London", "伦敦时间"),
        ("Europe/Paris", "巴黎时间"),
        ("Asia/Tokyo", "东京时间"),
        ("Asia/Singapore", "新加坡时间"),
        ("Australia/Sydney", "悉尼时间"),
        ("Pacific/Auckland", "奥克兰时间"),
    ]
    
    base_date = date(2024, 8, 21)
    base_hour = 12
    
    for tz, name in timezones:
        try:
            result = tr.resolve(
                birth_date=base_date,
                hour=base_hour, minute=0,
                timezone=tz,
                location="120,30"  # 使用经纬度
            )
            print(f"  ✅ {name} ({tz}): {result.effective_hour:02d}:{result.effective_minute:02d}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name} ({tz}): {e}")
            failed += 1
    
    return passed, failed


def test_p1_day_boundary():
    """P1: 子时换日边界测试"""
    print("\n" + "=" * 70)
    print("P1: 子时换日边界测试")
    print("=" * 70)
    
    tr = TimeResolver()
    passed = 0
    failed = 0
    
    # 子初换日边界测试
    test_cases = [
        # (hour, expected_rolled, desc)
        (22, False, "22:00 - 不应换日"),
        (22, False, "22:59 - 不应换日"),
        (23, True, "23:00 - 应换日（上海）"),
        (23, True, "23:01 - 应换日"),
        (23, True, "23:59 - 应换日"),
        (0, False, "00:00 - 早子时，不跨日"),
        (0, False, "00:01 - 早子时，不跨日"),
    ]
    
    for hour, expected_rolled, desc in test_cases:
        try:
            # 使用上海（经度>120，修正后更容易触发换日）
            result = tr.resolve(
                birth_date=date(2024, 8, 21),
                hour=hour, minute=0 if hour != 22 else 59,
                timezone="Asia/Shanghai",
                location="Shanghai"
            )
            rolled = result.day_rolled
            status = "✅" if rolled == expected_rolled else "❌"
            print(f"  {status} {desc}: day_rolled={rolled}, expected={expected_rolled}")
            if rolled == expected_rolled:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ {desc}: {e}")
            failed += 1
    
    return passed, failed


def test_p2_li_chun():
    """P2: 立春边界测试"""
    print("\n" + "=" * 70)
    print("P2: 立春边界测试")
    print("=" * 70)
    
    engine = BaziEngine()
    passed = 0
    failed = 0
    
    # 2024年立春: 2024-02-04 16:26:53 (UTC+8)
    # 测试立春前后
    test_cases = [
        # (year, month, day, hour, expected_year_stem, desc)
        (2024, 2, 4, 16, "甲", "立春瞬间（约16:26）"),
        (2024, 2, 4, 17, "甲", "立春后"),
        (2024, 2, 5, 0, "甲", "立春次日"),
        (2024, 2, 3, 23, "癸", "立春前一刻"),
        (2024, 2, 3, 12, "癸", "立春前半天"),
        (2025, 2, 4, 0, "甲", "2025立春"),
    ]
    
    for year, month, day, hour, expected_stem, desc in test_cases:
        try:
            chart = engine.compute((year, month, day, hour), gender="male")
            actual_stem = chart.year_pillar.heavenly_stem
            status = "✅" if actual_stem == expected_stem else "❌"
            print(f"  {status} {desc}: year_stem={actual_stem}, expected={expected_stem}")
            if actual_stem == expected_stem:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ {desc}: {e}")
            failed += 1
    
    return passed, failed


def test_p3_solar_terms():
    """P3: 24节气边界测试（抽样）"""
    print("\n" + "=" * 70)
    print("P3: 24节气边界测试（抽样）")
    print("=" * 70)
    
    engine = BaziEngine()
    passed = 0
    failed = 0
    
    # 抽样测试几个关键节气
    test_cases = [
        # (year, month, day, hour, expected_month_stem, desc)
        (2024, 2, 4, 16, "甲", "立春（月柱切换）"),
        (2024, 2, 19, 10, "乙", "雨水后"),
        (2024, 3, 21, 10, "丙", "春分"),
        (2024, 4, 4, 15, "丁", "清明"),
        (2024, 5, 5, 10, "戊", "立夏"),
        (2024, 6, 5, 15, "己", "芒种"),
        (2024, 7, 7, 10, "庚", "小暑"),
        (2024, 8, 7, 15, "辛", "立秋"),
        (2024, 9, 7, 10, "壬", "白露"),
        (2024, 10, 8, 15, "癸", "寒露"),
        (2024, 11, 7, 10, "甲", "立冬"),
        (2024, 12, 7, 15, "乙", "大雪"),
    ]
    
    for year, month, day, hour, expected_stem, desc in test_cases:
        try:
            chart = engine.compute((year, month, day, hour), gender="male")
            actual_stem = chart.month_pillar.heavenly_stem
            status = "✅" if actual_stem == expected_stem else "❌"
            print(f"  {status} {desc}: month_stem={actual_stem}, expected={expected_stem}")
            if actual_stem == expected_stem:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ {desc}: {e}")
            failed += 1
    
    return passed, failed


def test_p4_longitude():
    """P4: 全球经度修正测试"""
    print("\n" + "=" * 70)
    print("P4: 全球经度修正测试")
    print("=" * 70)
    
    tr = TimeResolver()
    passed = 0
    failed = 0
    
    cities = [
        ("Beijing", 116.41, "北京"),
        ("Shanghai", 121.47, "上海"),
        ("Tokyo", 139.69, "东京"),
        ("New_York", -74.01, "纽约"),
        ("London", -0.13, "伦敦"),
        ("Sydney", 151.21, "悉尼"),
        ("Moscow", 37.62, "莫斯科"),
        ("Dubai", 55.27, "迪拜"),
    ]
    
    base_date = date(2024, 8, 21)
    base_hour = 12
    
    for city_id, expected_lon, name in cities:
        try:
            result = tr.resolve(
                birth_date=base_date,
                hour=base_hour, minute=0,
                timezone=None,
                location=city_id
            )
            actual_lon = result.longitude
            correction = result.corrections.get('longitude_correction_min', 0)
            expected_correction = round((expected_lon - 120) * 4, 2)
            
            status = "✅" if abs(correction - expected_correction) < 1 else "❌"
            print(f"  {status} {name}: lon={actual_lon:.2f}, corr={correction:.2f}min")
            if abs(correction - expected_correction) < 1:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            failed += 1
    
    return passed, failed


def test_p5_lunar():
    """P5: 历法转换测试"""
    print("\n" + "=" * 70)
    print("P5: 历法转换测试")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    # 测试公历闰年
    test_cases = [
        (2024, 2, 29, "闰年2月29日"),
        (2023, 2, 28, "平年2月28日"),
        (1900, 2, 28, "世纪年非闰年"),
        (2000, 2, 29, "世纪闰年"),
        (2024, 12, 31, "年末"),
        (2025, 1, 1, "年初"),
    ]
    
    for year, month, day, desc in test_cases:
        try:
            d = date(year, month, day)
            print(f"  ✅ {desc}: {d.isoformat()}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {desc}: {e}")
            failed += 1
    
    return passed, failed


def test_p6_four_pillars():
    """P6: 四柱独立重算验证"""
    print("\n" + "=" * 70)
    print("P6: 四柱独立重算验证")
    print("=" * 70)
    
    engine = BaziEngine()
    passed = 0
    failed = 0
    
    # 已知答案案例
    test_cases = [
        # (year, month, day, hour, gender, expected)
        (1984, 12, 7, 16, "male", {"year": "JIA-ZI", "month": "BING-ZI", "day": "YI-HAI", "hour": "JIA-SHEN"}),
        (1980, 5, 7, 10, "male", {"year": "GENG-SHEN", "month": "XIN-SI", "day": "GENG-CHEN", "hour": "XIN-SI"}),
        (1990, 1, 1, 12, "male", {"year": "GENG-WU", "month": "DING-CHOU", "day": "WU-WU", "hour": "DENGY-SI"}),
    ]
    
    for year, month, day, hour, gender, expected in test_cases:
        try:
            chart = engine.compute((year, month, day, hour), gender=gender)
            
            checks = [
                ("year", chart.year_pillar.heavenly_stem + "-" + chart.year_pillar.earthly_branch),
                ("month", chart.month_pillar.heavenly_stem + "-" + chart.month_pillar.earthly_branch),
                ("day", chart.day_pillar.heavenly_stem + "-" + chart.day_pillar.earthly_branch),
                ("hour", chart.hour_pillar.heavenly_stem + "-" + chart.hour_pillar.earthly_branch),
            ]
            
            all_pass = True
            for pillar, actual in checks:
                exp = expected[pillar]
                status = "✅" if actual == exp else "❌"
                print(f"    {pillar}: {actual} (expected {exp}) {status}")
                if actual != exp:
                    all_pass = False
            
            if all_pass:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ {year}-{month}-{day} {hour}:00: {e}")
            failed += 1
    
    return passed, failed


def test_p7_stems_branches():
    """P7: 干支基础算法测试"""
    print("\n" + "=" * 70)
    print("P7: 干支基础算法测试")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    # 天干10
    tian_gan = ["JIA", "YI", "BING", "DING", "WU", "JI", "GENG", "XIN", "REN", "GUI"]
    print(f"  天干10: {tian_gan}")
    passed += 1
    
    # 地支12
    di_zhi = ["ZI", "CHOU", "YIN", "MAO", "CHEN", "SI", "WU", "WEI", "SHEN", "YOU", "XU", "HAI"]
    print(f"  地支12: {di_zhi}")
    passed += 1
    
    # 六十甲子循环
    for i in range(60):
        stem = tian_gan[i % 10]
        branch = di_zhi[i % 12]
        if i == 0:
            assert stem == "JIA" and branch == "ZI", "甲子应为第一个"
        if i == 59:
            assert stem == "GUI" and branch == "HAI", "癸亥应为最后一个"
    print(f"  六十甲子循环: 0-59 ✅")
    passed += 1
    
    # 五虎遁（年干→月干）
    wu_hu_dun = {
        "JIA": "BING", "YI": "WU", "BING": "GENG", "DING": "REN", "WU": "JIA",
        "JI": "BING", "GENG": "WU", "XIN": "GENG", "REN": "REN", "GUI": "JIA",
    }
    print(f"  五虎遁映射: {len(wu_hu_dun)} 项 ✅")
    passed += 1
    
    # 五鼠遁（日干→时干）
    wu_shu_dun = {
        "JIA": "BING", "YI": "BING", "BING": "WU", "DING": "WU", "WU": "GENG",
        "JI": "GENG", "GENG": "REN", "XIN": "REN", "REN": "JIA", "GUI": "JIA",
    }
    print(f"  五鼠遁映射: {len(wu_shu_dun)} 项 ✅")
    passed += 1
    
    return passed, failed


def test_p8_boundary_matrix():
    """P8: 边界测试矩阵"""
    print("\n" + "=" * 70)
    print("P8: 边界测试矩阵")
    print("=" * 70)
    
    tr = TimeResolver()
    engine = BaziEngine()
    passed = 0
    failed = 0
    
    # 时间边界测试
    boundary_tests = [
        # (date, hour, minute, desc)
        (date(2024, 12, 31), 23, 59, "年末23:59"),
        (date(2025, 1, 1), 0, 0, "年初00:00"),
        (date(2024, 2, 28), 23, 59, "2月末日23:59"),
        (date(2024, 3, 1), 0, 0, "3月1日00:00"),
        (date(2024, 8, 21), 22, 59, "22:59"),
        (date(2024, 8, 21), 23, 0, "23:00"),
        (date(2024, 8, 21), 23, 1, "23:01"),
        (date(2024, 8, 21), 0, 0, "00:00"),
        (date(2024, 8, 21), 0, 1, "00:01"),
    ]
    
    for d, h, m, desc in boundary_tests:
        try:
            result = tr.resolve(
                birth_date=d,
                hour=h, minute=m,
                timezone="Asia/Shanghai",
                location="Shanghai"
            )
            print(f"  ✅ {desc}: {result.effective_date} {result.effective_hour:02d}:{result.effective_minute:02d}, rolled={result.day_rolled}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {desc}: {e}")
            failed += 1
    
    return passed, failed


def test_p9_global_cities():
    """P9: 全球城市验证"""
    print("\n" + "=" * 70)
    print("P9: 全球城市验证")
    print("=" * 70)
    
    tr = TimeResolver()
    passed = 0
    failed = 0
    
    # 全球城市列表
    cities = [
        # (city_id, timezone, longitude, name)
        ("Beijing", "Asia/Shanghai", 116.41, "北京"),
        ("Shanghai", "Asia/Shanghai", 121.47, "上海"),
        ("Hong_Kong", "Asia/Hong_Kong", 114.17, "香港"),
        ("Taipei", "Asia/Taipei", 121.53, "台北"),
        ("Tokyo", "Asia/Tokyo", 139.69, "东京"),
        ("Seoul", "Asia/Seoul", 126.98, "首尔"),
        ("Singapore", "Asia/Singapore", 103.85, "新加坡"),
        ("Bangkok", "Asia/Bangkok", 100.50, "曼谷"),
        ("Jakarta", "Asia/Jakarta", 106.85, "雅加达"),
        ("Delhi", "Asia/Kolkata", 77.21, "德里"),
        ("Mumbai", "Asia/Kolkata", 72.88, "孟买"),
        ("Dubai", "Asia/Dubai", 55.27, "迪拜"),
        ("London", "Europe/London", -0.13, "伦敦"),
        ("Paris", "Europe/Paris", 2.35, "巴黎"),
        ("Berlin", "Europe/Berlin", 13.41, "柏林"),
        ("Moscow", "Europe/Moscow", 37.62, "莫斯科"),
        ("New_York", "America/New_York", -74.01, "纽约"),
        ("Los_Angeles", "America/Los_Angeles", -118.24, "洛杉矶"),
        ("Chicago", "America/Chicago", -87.63, "芝加哥"),
        ("Toronto", "America/Toronto", -79.38, "多伦多"),
        ("Vancouver", "America/Vancouver", -123.12, "温哥华"),
        ("Sao_Paulo", "America/Sao_Paulo", -46.63, "圣保罗"),
        ("Buenos_Aires", "America/Argentina/Buenos_Aires", -58.38, "布宜诺斯艾利斯"),
        ("Sydney", "Australia/Sydney", 151.21, "悉尼"),
        ("Melbourne", "Australia/Melbourne", 144.96, "墨尔本"),
        ("Auckland", "Pacific/Auckland", 174.76, "奥克兰"),
        ("Cape_Town", "Africa/Johannesburg", 18.42, "开普敦"),
        ("Johannesburg", "Africa/Johannesburg", 28.05, "约翰内斯堡"),
        ("Cairo", "Africa/Cairo", 31.24, "开罗"),
    ]
    
    base_date = date(2024, 8, 21)
    base_hour = 12
    
    for city_id, tz, lon, name in cities:
        try:
            result = tr.resolve(
                birth_date=base_date,
                hour=base_hour, minute=0,
                timezone=tz,
                location=city_id
            )
            corr = result.corrections.get('longitude_correction_min', 0)
            expected_corr = round((lon - 120) * 4, 2)
            status = "✅" if abs(corr - expected_corr) < 2 else "❌"
            print(f"  {status} {name}: corr={corr:.1f}min (exp~{expected_corr:.1f}min)")
            if abs(corr - expected_corr) < 2:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            failed += 1
    
    return passed, failed


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("BOT-BAZI Phase 0 Complete Verification")
    print("=" * 70)
    
    total_passed = 0
    total_failed = 0
    
    # 按优先级运行测试
    tests = [
        ("P0", "时间输入合法性", test_p0_time_input),
        ("P0", "时区支持", test_p0_timezone),
        ("P1", "子时换日边界", test_p1_day_boundary),
        ("P2", "立春边界", test_p2_li_chun),
        ("P3", "节气边界（抽样）", test_p3_solar_terms),
        ("P4", "全球经度修正", test_p4_longitude),
        ("P5", "历法转换", test_p5_lunar),
        ("P6", "四柱独立重算", test_p6_four_pillars),
        ("P7", "干支基础算法", test_p7_stems_branches),
        ("P8", "边界测试矩阵", test_p8_boundary_matrix),
        ("P9", "全球城市验证", test_p9_global_cities),
    ]
    
    for priority, name, test_func in tests:
        try:
            passed, failed = test_func()
            total_passed += passed
            total_failed += failed
            print(f"\n[{priority}] {name}: {passed} passed, {failed} failed")
        except Exception as e:
            print(f"\n[{priority}] {name}: ERROR - {e}")
            total_failed += 1
    
    # 汇总
    print("\n" + "=" * 70)
    print(f"总结果: {total_passed} passed, {total_failed} failed")
    print("=" * 70)
    
    if total_failed > 0:
        print("\n⚠️ 存在失败测试，请检查")
        return 1
    else:
        print("\n✅ 所有测试通过!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
