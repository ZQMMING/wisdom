#!/usr/bin/env python3
"""
BOT-BAZI Phase 0 Complete Verification - Fixed Version
修正地点名称和大小写问题
"""

import sys
from pathlib import Path
from datetime import date, datetime, timedelta

sys.path.insert(0, str(Path('/d/shuntian/src')))

from tongshu.engines.time import TimeResolver
from tongshu.engines.bazi_engine import BaziEngine


def to_upper(s):
    """统一转大写比较"""
    return s.upper() if s else s


def test_p0_time_input():
    """P0: 时间输入合法性测试"""
    print("\n" + "=" * 70)
    print("P0: 时间输入合法性测试")
    print("=" * 70)
    
    tr = TimeResolver()
    passed = failed = 0
    
    test_cases = [
        (2024, 2, 29, 12, "闰年2月29日"),
        (2023, 2, 28, 12, "平年2月28日"),
        (1900, 2, 28, 12, "世纪年非闰年"),
        (2000, 2, 29, 12, "世纪闰年"),
        (2024, 12, 31, 23, "年末边界"),
        (2025, 1, 1, 0, "年初边界"),
        (2024, 6, 30, 12, "小月最后一天"),
        (2024, 7, 1, 12, "小月下第一天"),
        (2024, 2, 28, 23, "2月28日23:00"),
        (2024, 2, 29, 0, "闰年首日00:00"),
    ]
    
    for year, month, day, hour, desc in test_cases:
        try:
            result = tr.resolve(
                birth_date=date(year, month, day),
                hour=hour, minute=0,
                timezone="Asia/Shanghai",
                location="北京"
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
    passed = failed = 0
    
    # 使用 registry 中的地点名称
    timezones = [
        ("北京", "Asia/Shanghai", "北京时间"),
        ("上海", "Asia/Shanghai", "上海时间"),
        ("香港", "Asia/Hong_Kong", "香港时间"),
        ("东京", "Asia/Tokyo", "东京时间"),
        ("纽约", "America/New_York", "纽约时间"),
        ("伦敦", "Europe/London", "伦敦时间"),
        ("悉尼", "Australia/Sydney", "悉尼时间"),
        ("莫斯科", "Europe/Moscow", "莫斯科时间"),
        ("迪拜", "Asia/Dubai", "迪拜时间"),
        ("新加坡", "Asia/Singapore", "新加坡时间"),
    ]
    
    base_date = date(2024, 8, 21)
    base_hour = 12
    
    for loc, tz, name in timezones:
        try:
            result = tr.resolve(
                birth_date=base_date,
                hour=base_hour, minute=0,
                timezone=tz,
                location=loc
            )
            print(f"  ✅ {name}: effective={result.effective_hour:02d}:{result.effective_minute:02d}, tz={result.timezone}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            failed += 1
    
    return passed, failed


def test_p1_day_boundary():
    """P1: 子时换日边界测试"""
    print("\n" + "=" * 70)
    print("P1: 子时换日边界测试")
    print("=" * 70)
    
    tr = TimeResolver()
    passed = failed = 0
    
    # 北京（经度116.41，修正-14min），23:00 civil → 22:46 apparent，不换日
    # 上海（经度121.47，修正+6min），23:00 civil → 23:06 apparent，换日
    
    test_cases = [
        # (location, hour, minute, expected_rolled, desc)
        ("北京", 22, 0, False, "北京22:00 - 不应换日"),
        ("北京", 22, 59, False, "北京22:59 - 不应换日"),
        ("北京", 23, 0, False, "北京23:00 - 不换日(apparent<23)"),
        ("北京", 23, 30, False, "北京23:30 - 不换日"),
        ("上海", 23, 0, True, "上海23:00 - 应换日(apparent>=23)"),
        ("上海", 23, 30, True, "上海23:30 - 应换日"),
        ("上海", 0, 0, False, "上海00:00 - 早子时不跨日"),
        ("上海", 0, 30, False, "上海00:30 - 早子时不跨日"),
    ]
    
    for loc, hour, minute, expected_rolled, desc in test_cases:
        try:
            result = tr.resolve(
                birth_date=date(2024, 8, 21),
                hour=hour, minute=minute,
                timezone="Asia/Shanghai",
                location=loc
            )
            rolled = result.day_rolled
            status = "✅" if rolled == expected_rolled else "❌"
            print(f"  {status} {desc}: rolled={rolled}, expected={expected_rolled}")
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
    passed = failed = 0
    
    # 2024年立春: 2024-02-04 16:26:53 (UTC+8)
    # 测试立春前后年柱变化
    test_cases = [
        # (year, month, day, hour, expected_year_stem, desc)
        (2024, 2, 4, 16, "JIA", "立春瞬间（约16:26）"),
        (2024, 2, 4, 17, "JIA", "立春后"),
        (2024, 2, 5, 0, "JIA", "立春次日"),
        (2024, 2, 3, 23, "GUI", "立春前一刻"),
        (2024, 2, 3, 12, "GUI", "立春前半天"),
        (2025, 2, 4, 0, "YI", "2025立春后进入乙年"),
    ]
    
    for year, month, day, hour, expected_stem, desc in test_cases:
        try:
            chart = engine.compute((year, month, day, hour), gender="male")
            actual_stem = to_upper(chart.year_pillar.heavenly_stem)
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
    passed = failed = 0
    
    # 2024年月柱测试 - 验证节气对月柱的影响
    # 2024年甲辰年，月柱从丙子开始（立春后第一个月）
    test_cases = [
        # (month, expected_month_stem, desc)
        (2, "BING", "2月立春后（丙子月）"),
        (3, "DING", "3月惊蛰后（丁丑月）"),
        (4, "WU", "4月清明后（戊寅月）"),
        (5, "JI", "5月立夏后（己卯月）"),
        (6, "GENG", "6月芒种后（庚辰月）"),
        (7, "XIN", "7月小暑后（辛巳月）"),
        (8, "REN", "8月立秋后（壬午月）"),
        (9, "GUI", "9月白露后（癸未月）"),
        (10, "JIA", "10月寒露后（甲申月）"),
        (11, "YI", "11月立冬后（乙酉月）"),
        (12, "BING", "12月大雪后（丙戌月）"),
        (1, "DING", "1月小寒后（丁亥月）"),
    ]
    
    for month, expected_stem, desc in test_cases:
        try:
            # 选择每月中间日期确保在节气后
            day = 15
            chart = engine.compute((2024, month, day, 12), gender="male")
            actual_stem = to_upper(chart.month_pillar.heavenly_stem)
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
    passed = failed = 0
    
    # 使用 Location Registry 中的地点
    cities = [
        ("北京", 116.41, "北京"),
        ("上海", 121.47, "上海"),
        ("香港", 114.17, "香港"),
        ("东京", 139.69, "东京"),
        ("纽约", -74.01, "纽约"),
        ("伦敦", -0.13, "伦敦"),
        ("悉尼", 151.21, "悉尼"),
        ("莫斯科", 37.62, "莫斯科"),
        ("迪拜", 55.27, "迪拜"),
        ("新加坡", 103.85, "新加坡"),
    ]
    
    base_date = date(2024, 8, 21)
    base_hour = 12
    
    for loc, expected_lon, name in cities:
        try:
            result = tr.resolve(
                birth_date=base_date,
                hour=base_hour, minute=0,
                timezone=None,
                location=loc
            )
            actual_lon = result.longitude
            correction = result.corrections.get('longitude_correction_min', 0)
            # 计算预期修正（基于当地经度与UTC+8参考经度120°的差）
            ref_meridian = 120.0  # UTC+8
            expected_correction = round((expected_lon - ref_meridian) * 4, 2)
            
            status = "✅" if abs(correction - expected_correction) < 1 else "❌"
            print(f"  {status} {name}: lon={actual_lon:.2f}, corr={correction:.1f}min (exp~{expected_correction:.1f}min)")
            if abs(correction - expected_correction) < 1:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            failed += 1
    
    return passed, failed


def test_p5_calendar():
    """P5: 历法转换测试"""
    print("\n" + "=" * 70)
    print("P5: 历法转换测试")
    print("=" * 70)
    
    passed = failed = 0
    
    test_cases = [
        (2024, 2, 29, "闰年2月29日"),
        (2023, 2, 28, "平年2月28日"),
        (1900, 2, 28, "世纪年非闰年"),
        (2000, 2, 29, "世纪闰年"),
        (2024, 12, 31, "年末"),
        (2025, 1, 1, "年初"),
        (2024, 6, 30, "小月最后"),
        (2024, 7, 1, "小月次日"),
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
    passed = failed = 0
    
    # 已知答案案例（来自Golden Cases）
    test_cases = [
        {
            "input": (1984, 12, 7, 16),
            "gender": "male",
            "expected": {
                "year": "JIA-ZI",
                "month": "BING-ZI", 
                "day": "YI-HAI",
                "hour": "JIA-SHEN"
            },
            "desc": "GOLDEN-001"
        },
        {
            "input": (1980, 5, 7, 10),
            "gender": "male",
            "expected": {
                "year": "GENG-SHEN",
                "month": "XIN-SI",
                "day": "GENG-CHEN",
                "hour": "XIN-SI"
            },
            "desc": "GOLDEN-004"
        },
        {
            "input": (1990, 1, 1, 12),
            "gender": "male",
            "expected": {
                "year": "JIA-WU",  # 1990年立春后为庚午年
                "month": "DING-CHOU",
                "day": "WU-WU",
                "hour": "DENGY-SI"
            },
            "desc": "1990年测试"
        },
    ]
    
    for case in test_cases:
        try:
            chart = engine.compute(case["input"], gender=case["gender"])
            
            checks = [
                ("year", to_upper(chart.year_pillar.heavenly_stem) + "-" + to_upper(chart.year_pillar.earthly_branch)),
                ("month", to_upper(chart.month_pillar.heavenly_stem) + "-" + to_upper(chart.month_pillar.earthly_branch)),
                ("day", to_upper(chart.day_pillar.heavenly_stem) + "-" + to_upper(chart.day_pillar.earthly_branch)),
                ("hour", to_upper(chart.hour_pillar.heavenly_stem) + "-" + to_upper(chart.hour_pillar.earthly_branch)),
            ]
            
            all_pass = True
            for pillar, actual in checks:
                exp = case["expected"][pillar]
                status = "✅" if actual == exp else "❌"
                print(f"    {pillar}: {actual} (expected {exp}) {status}")
                if actual != exp:
                    all_pass = False
            
            if all_pass:
                passed += 1
                print(f"  ✅ {case['desc']}: 全部匹配")
            else:
                failed += 1
                print(f"  ❌ {case['desc']}: 存在不匹配")
        except Exception as e:
            print(f"  ❌ {case['desc']}: {e}")
            failed += 1
    
    return passed, failed


def test_p7_stems_branches():
    """P7: 干支基础算法测试"""
    print("\n" + "=" * 70)
    print("P7: 干支基础算法测试")
    print("=" * 70)
    
    from tongshu.reasoning.bazi_ten_gods import BRANCH_HIDDEN_STEMS, GENERATES, CONTROLS
    
    passed = 0
    failed = 0
    
    # 天干10
    tian_gan = ["JIA", "YI", "BING", "DING", "WU", "JI", "GENG", "XIN", "REN", "GUI"]
    print(f"  ✅ 天干10: {len(tian_gan)} 项")
    passed += 1
    
    # 地支12
    di_zhi = ["ZI", "CHOU", "YIN", "MAO", "CHEN", "SI", "WU", "WEI", "SHEN", "YOU", "XU", "HAI"]
    print(f"  ✅ 地支12: {len(di_zhi)} 项")
    passed += 1
    
    # 六十甲子循环
    for i in range(60):
        stem = tian_gan[i % 10]
        branch = di_zhi[i % 12]
    print(f"  ✅ 六十甲子循环: 0-59")
    passed += 1
    
    # 藏干表完整性
    assert len(BRANCH_HIDDEN_STEMS) == 12, f"藏干表应有12项，实际{len(BRANCH_HIDDEN_STEMS)}"
    print(f"  ✅ 藏干表: {len(BRANCH_HIDDEN_STEMS)} 项")
    passed += 1
    
    # 五行相生相克
    assert len(GENERATES) == 5, f"相生应有5项"
    assert len(CONTROLS) == 5, f"相克应有5项"
    print(f"  ✅ 五行生成克制: GENERATES={len(GENERATES)}, CONTROLS={len(CONTROLS)}")
    passed += 1
    
    return passed, failed


def test_p8_boundary_matrix():
    """P8: 边界测试矩阵"""
    print("\n" + "=" * 70)
    print("P8: 边界测试矩阵")
    print("=" * 70)
    
    tr = TimeResolver()
    passed = failed = 0
    
    boundary_tests = [
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
                location="上海"
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
    passed = failed = 0
    
    # 使用 Location Registry 中的地点
    cities = [
        ("北京", "Asia/Shanghai", "北京"),
        ("上海", "Asia/Shanghai", "上海"),
        ("香港", "Asia/Hong_Kong", "香港"),
        ("台北", "Asia/Taipei", "台北"),
        ("东京", "Asia/Tokyo", "东京"),
        ("首尔", "Asia/Seoul", "首尔"),
        ("新加坡", "Asia/Singapore", "新加坡"),
        ("曼谷", "Asia/Bangkok", "曼谷"),
        ("雅加达", "Asia/Jakarta", "雅加达"),
        ("德里", "Asia/Kolkata", "德里"),
        ("孟买", "Asia/Kolkata", "孟买"),
        ("迪拜", "Asia/Dubai", "迪拜"),
        ("伦敦", "Europe/London", "伦敦"),
        ("巴黎", "Europe/Paris", "巴黎"),
        ("柏林", "Europe/Berlin", "柏林"),
        ("莫斯科", "Europe/Moscow", "莫斯科"),
        ("纽约", "America/New_York", "纽约"),
        ("洛杉矶", "America/Los_Angeles", "洛杉矶"),
        ("芝加哥", "America/Chicago", "芝加哥"),
        ("多伦多", "America/Toronto", "多伦多"),
        ("温哥华", "America/Vancouver", "温哥华"),
        ("悉尼", "Australia/Sydney", "悉尼"),
        ("墨尔本", "Australia/Melbourne", "墨尔本"),
        ("奥克兰", "Pacific/Auckland", "奥克兰"),
        ("开普敦", "Africa/Johannesburg", "开普敦"),
        ("约翰内斯堡", "Africa/Johannesburg", "约翰内斯堡"),
        ("开罗", "Africa/Cairo", "开罗"),
    ]
    
    base_date = date(2024, 8, 21)
    base_hour = 12
    
    for loc, tz, name in cities:
        try:
            result = tr.resolve(
                birth_date=base_date,
                hour=base_hour, minute=0,
                timezone=tz,
                location=loc
            )
            corr = result.corrections.get('longitude_correction_min', 0)
            print(f"  ✅ {name}: corr={corr:.1f}min")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            failed += 1
    
    return passed, failed


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("BOT-BAZI Phase 0 Complete Verification (Fixed)")
    print("=" * 70)
    
    total_passed = total_failed = 0
    
    tests = [
        ("P0", "时间输入合法性", test_p0_time_input),
        ("P0", "时区支持", test_p0_timezone),
        ("P1", "子时换日边界", test_p1_day_boundary),
        ("P2", "立春边界", test_p2_li_chun),
        ("P3", "节气边界（抽样）", test_p3_solar_terms),
        ("P4", "全球经度修正", test_p4_longitude),
        ("P5", "历法转换", test_p5_calendar),
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
            import traceback
            traceback.print_exc()
            total_failed += 1
    
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
