"""R-04 独立验证: 四者组合测试

验证 civil/effective date + 节气边界 + timezone + 23:00 换日 的组合
"""
from datetime import datetime, date
from zoneinfo import ZoneInfo
from tongshu.engines.bazi_engine import BaziEngine

# ============================================================================
# Test Matrix: civil vs effective divergence at solar term boundaries
# ============================================================================

def run_test(civil_dt, solar_date, expected_year, expected_month_branch, desc):
    engine = BaziEngine()
    chart = engine.compute(
        solar_date=solar_date,
        gender="male",
        birth_datetime=civil_dt,
    )
    y_ok = chart.year_pillar.heavenly_stem == expected_year
    m_ok = chart.month_pillar.earthly_branch == expected_month_branch
    status = "PASS" if y_ok and m_ok else "FAIL"
    print(f"{status} {desc}")
    if not y_ok:
        print(f"   year: expected={expected_year}, got={chart.year_pillar.heavenly_stem}")
    if not m_ok:
        print(f"   month: expected={expected_month_branch}, got={chart.month_pillar.earthly_branch}")
    return y_ok and m_ok

TZ = ZoneInfo("Asia/Shanghai")

print("=" * 70)
print("R-04 Independent Verification: Civil/Effective × Solar Term × Timezone")
print("=" * 70)

# 1. 立春边界 + 23:00 换日
print("\n[1] Lichun boundary + 23:00 day change:")
results = []
results.append(run_test(
    datetime(2024, 2, 3, 23, 30, 0, tzinfo=TZ),
    (2024, 2, 3, 23),
    "GUI", "CHOU",
    "civil=02-03 23:30 -> effective=02-04, pre-lichun"
))
results.append(run_test(
    datetime(2024, 2, 4, 23, 30, 0, tzinfo=TZ),
    (2024, 2, 4, 23),
    "JIA", "YIN",
    "civil=02-04 23:30 -> effective=02-05, post-lichun"
))

# 2. 立春精确时刻
print("\n[2] Lichun exact moment:")
results.append(run_test(
    datetime(2024, 2, 4, 16, 26, 52, tzinfo=TZ),
    (2024, 2, 4, 16),
    "GUI", "CHOU",
    "civil=16:26:52 (1s before lichun)"
))
results.append(run_test(
    datetime(2024, 2, 4, 16, 26, 53, tzinfo=TZ),
    (2024, 2, 4, 16),
    "GUI", "CHOU",
    "civil=16:26:53 (exact lichun)"
))
results.append(run_test(
    datetime(2024, 2, 4, 16, 26, 54, tzinfo=TZ),
    (2024, 2, 4, 16),
    "JIA", "YIN",
    "civil=16:26:54 (1s after lichun)"
))

# 3. 全球时区 + 立春边界
print("\n[3] Global timezone x Lichun boundary:")
tz_ny = ZoneInfo("America/New_York")
tz_sydney = ZoneInfo("Australia/Sydney")

# New York: 02-04 16:26 BJT = 02-04 03:26 EST (still pre-lichun in NY)
results.append(run_test(
    datetime(2024, 2, 4, 3, 26, 52, tzinfo=tz_ny),
    (2024, 2, 4, 3),
    "GUI", "CHOU",
    "NY=03:26:52 (pre-lichun in NY)"
))

# Sydney: 02-04 19:27 AEDT = 02-04 16:27 BJT (post-lichun)
results.append(run_test(
    datetime(2024, 2, 4, 19, 27, 0, tzinfo=tz_sydney),
    (2024, 2, 4, 19),
    "JIA", "YIN",
    "Sydney=19:27:00 (post-lichun in Sydney, BJT=16:27)"
))

# 4. 其他节气边界
print("\n[4] Other solar term boundaries:")
# 惊蛰: 2024-03-05 15:37:23
results.append(run_test(
    datetime(2024, 3, 4, 23, 30, 0, tzinfo=TZ),
    (2024, 3, 4, 23),
    "JIA", "YIN",
    "Pre-jingzhe (03-04 23:30)"
))
results.append(run_test(
    datetime(2024, 3, 5, 15, 37, 24, tzinfo=TZ),
    (2024, 3, 5, 15),
    "JIA", "MAO",
    "Post-jingzhe (03-05 15:37:24)"
))

# 5. 23:00 换日但无节气变化
print("\n[5] 23:00 day change without solar term:")
results.append(run_test(
    datetime(2024, 2, 10, 23, 30, 0, tzinfo=TZ),
    (2024, 2, 10, 23),
    "JIA", "YIN",
    "No term change (02-10 23:30)"
))

print("\n" + "=" * 70)
if all(results):
    print("All independent verification tests PASSED")
else:
    print("Some tests FAILED")
    failed_count = sum(1 for r in results if not r)
    print(f"Failed: {failed_count}/{len(results)}")
print("=" * 70)
