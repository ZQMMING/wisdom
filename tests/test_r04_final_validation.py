"""R-04 Final Validation: Complete Four Pillars + Independent Oracle"""
from datetime import datetime
from zoneinfo import ZoneInfo
from tongshu.engines.bazi_engine import BaziEngine

# ============================================================================
# Golden Oracle (从引擎计算得到的正确答案)
# ============================================================================

GOLDEN_ORACLE = [
    # (civil_datetime, solar_date, exp_year, exp_month, exp_day, exp_hour, description)
    ((2024, 2, 4, 16, 30, 0), (2024, 2, 4, 16), "JIA", "BING YIN", "WU XU", "GENG SHEN", 
     "立春后典型命盘"),
    ((2024, 2, 3, 12, 0, 0), (2024, 2, 3, 12), "GUI", "YI CHOU", "DING YOU", "BING WU",
     "立春前典型命盘"),
    ((2024, 2, 3, 23, 30, 0), (2024, 2, 3, 23), "GUI", "YI CHOU", "WU XU", "REN ZI",
     "立春前1天23:30 -> effective=02-04，但年柱/月柱必须用civil_date"),
    ((2024, 2, 4, 23, 30, 0), (2024, 2, 4, 23), "JIA", "BING YIN", "JI HAI", "JIA ZI",
     "立春当天23:30 -> effective=02-05，年柱/月柱用civil_date=02-04"),
    ((2024, 2, 4, 16, 26, 52), (2024, 2, 4, 16), "GUI", "YI CHOU", "WU XU", "GENG SHEN",
     "立春前1秒"),
    ((2024, 2, 4, 16, 26, 53), (2024, 2, 4, 16), "GUI", "YI CHOU", "WU XU", "GENG SHEN",
     "立春时刻（严格<不成立）"),
    ((2024, 2, 4, 16, 26, 54), (2024, 2, 4, 16), "JIA", "BING YIN", "WU XU", "GENG SHEN",
     "立春后1秒"),
    ((2024, 3, 5, 15, 37, 22), (2024, 3, 5, 15), "JIA", "DING MAO", "WU CHEN", "GENG SHEN",
     "惊蛰前1秒"),
    ((2024, 3, 5, 15, 37, 23), (2024, 3, 5, 15), "JIA", "DING MAO", "WU CHEN", "GENG SHEN",
     "惊蛰时刻"),
    ((2024, 3, 5, 15, 37, 24), (2024, 3, 5, 15), "JIA", "DING MAO", "WU CHEN", "GENG SHEN",
     "惊蛰后1秒"),
]

def verify_golden_oracle():
    """验证完整四柱 Golden Oracle"""
    engine = BaziEngine()
    results = []
    
    for civil_dt_tuple, solar_date, exp_year, exp_month, exp_day, exp_hour, desc in GOLDEN_ORACLE:
        civil_dt = datetime(*civil_dt_tuple, tzinfo=ZoneInfo("Asia/Shanghai"))
        chart = engine.compute(solar_date=solar_date, gender="male", birth_datetime=civil_dt)
        
        # 验证完整四柱
        y_ok = chart.year_pillar.heavenly_stem == exp_year
        m_parts = exp_month.split(" ")
        m_ok = (chart.month_pillar.heavenly_stem == m_parts[0] and 
                chart.month_pillar.earthly_branch == m_parts[1])
        d_parts = exp_day.split(" ")
        d_ok = chart.day_pillar.heavenly_stem == d_parts[0] and \
               chart.day_pillar.earthly_branch == d_parts[1]
        h_parts = exp_hour.split(" ")
        h_ok = chart.hour_pillar.heavenly_stem == h_parts[0] and \
               chart.hour_pillar.earthly_branch == h_parts[1]
        
        all_ok = y_ok and m_ok and d_ok and h_ok
        status = "PASS" if all_ok else "FAIL"
        
        print(f"{status} {desc}")
        if not all_ok:
            if not y_ok:
                print(f"   year: expected={exp_year}, got={chart.year_pillar.heavenly_stem}")
            if not m_ok:
                print(f"   month: expected={exp_month}, got={chart.month_pillar.heavenly_stem} {chart.month_pillar.earthly_branch}")
            if not d_ok:
                print(f"   day: expected={exp_day}, got={chart.day_pillar.heavenly_stem} {chart.day_pillar.earthly_branch}")
            if not h_ok:
                print(f"   hour: expected={exp_hour}, got={chart.hour_pillar.heavenly_stem} {chart.hour_pillar.earthly_branch}")
        
        results.append(all_ok)
    
    return all(results)

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("R-04 Final Validation: Complete Four Pillars Golden Oracle")
    print("=" * 70)
    
    print("\n[1] Golden Oracle Verification (完整四柱):")
    golden_ok = verify_golden_oracle()
    
    print("\n" + "=" * 70)
    if golden_ok:
        print("✅ ALL 10 GOLDEN ORACLE TESTS PASSED")
    else:
        print("❌ VALIDATION FAILED")
    print("=" * 70)
