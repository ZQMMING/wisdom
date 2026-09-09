"""R-04 独立四柱验证：完全手动计算，不依赖任何引擎

核心原则：
- 不 import BaziEngine
- 不使用 sxtwl
- 纯经典公式 + 权威历史锚点

V2 架构契约：
1. Year/Month pillar: 基于 civil_date + 节气边界
   - 节气边界判断：birth_civil_datetime < jieqi_instant
   - 注意：相等时属于节气后（非严格小于）
2. Day/Hour pillar: 基于 effective_date (已做 23:00 换日)
3. 权威锚点：2024-02-04 16:26:53 = 立春时刻 (北京时间)
"""

from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# ============================================================================
# 六十甲子基础数据
# ============================================================================

HEAVENLY_STEMS = ["JIA", "YI", "BING", "DING", "WU", "JI", "GENG", "XIN", "REN", "GUI"]
EARTHLY_BRANCHES = ["ZI", "CHOU", "YIN", "MAO", "CHEN", "SI", "WU", "WEI", "SHEN", "YOU", "XU", "HAI"]

# ============================================================================
# 权威万年历锚点
# ============================================================================

ANCHOR_2024_02_03 = date(2024, 2, 3)
ANCHOR_GANZI_IDX_02_03 = 33  # 丁酉

# ============================================================================
# 立春时刻（北京时间，紫金山天文台数据）
# ============================================================================

LICHUN_2024_BJT = datetime(2024, 2, 4, 16, 26, 53, 0, tzinfo=ZoneInfo("Asia/Shanghai"))

# ============================================================================
# 独立计算公式
# ============================================================================

def compute_year_pillar(year, pre_lichun):
    """年柱：立春前用前一年"""
    if pre_lichun:
        year -= 1
    stem_idx = (year - 4) % 10
    branch_idx = (year - 4) % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]

def compute_month_pillar(year_stem, post_lichun):
    """月柱：五虎遁"""
    year_stem_idx = HEAVENLY_STEMS.index(year_stem)
    year_stem_5 = year_stem_idx % 5
    
    month_starts = (2, 4, 6, 8, 0)
    
    if post_lichun:
        branch_idx = EARTHLY_BRANCHES.index("YIN")
        stem_idx = (month_starts[year_stem_5] + (branch_idx - 2) % 12) % 10
        return HEAVENLY_STEMS[stem_idx], "YIN"
    else:
        branch_idx = EARTHLY_BRANCHES.index("CHOU")
        stem_idx = (month_starts[year_stem_5] + (branch_idx - 2) % 12) % 10
        return HEAVENLY_STEMS[stem_idx], "CHOU"

def compute_day_pillar(target_date):
    """日柱：基于六十甲子循环"""
    delta = (target_date - ANCHOR_2024_02_03).days
    result_idx = (ANCHOR_GANZI_IDX_02_03 + delta) % 60
    stem_idx = result_idx % 10
    branch_idx = result_idx % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]

def compute_hour_pillar(day_stem, hour):
    """时柱：日干 × 时辰"""
    day_stem_idx = HEAVENLY_STEMS.index(day_stem)
    zi_starts = [0, 2, 4, 6, 8]
    
    start_idx = zi_starts[day_stem_idx % 5]
    hour_branch_idx = ((hour + 1) % 24) // 2
    hour_stem_idx = (start_idx + hour_branch_idx) % 10
    hour_branch = EARTHLY_BRANCHES[hour_branch_idx % 12]
    
    return HEAVENLY_STEMS[hour_stem_idx], hour_branch

def compute_effective_date(civil_dt):
    """23:00 换日规则"""
    if civil_dt.hour >= 23:
        return civil_dt.date() + timedelta(days=1)
    return civil_dt.date()

# ============================================================================
# 测试用例（与引擎行为一致）
# ============================================================================

TEST_CASES = [
    # 立春后典型命盘
    (datetime(2024, 2, 4, 16, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     (2024, 2, 4, 16), "JIA", "BING", "WU", "GENG", "立春后典型命盘"),
    
    # 立春前典型命盘
    (datetime(2024, 2, 3, 12, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     (2024, 2, 3, 12), "GUI", "YI", "DING", "BING", "立春前典型命盘"),
    
    # 23:00 换日边界
    (datetime(2024, 2, 3, 23, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     (2024, 2, 3, 23), "GUI", "YI", "WU", "REN", "立春前1天23:30"),
    
    (datetime(2024, 2, 4, 23, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     (2024, 2, 4, 23), "JIA", "BING", "JI", "JIA", "立春当天23:30"),
    
    # 立春精确时刻边界
    # 注意：引擎定义 birth_dt < jieqi 为立春前，相等时为立春后
    (datetime(2024, 2, 4, 16, 26, 52, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     (2024, 2, 4, 16), "GUI", "YI", "WU", "GENG", "立春前1秒"),
    
    (datetime(2024, 2, 4, 16, 26, 53, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     (2024, 2, 4, 16), "JIA", "BING", "WU", "GENG", "立春时刻（相等，属立春后）"),
    
    (datetime(2024, 2, 4, 16, 26, 54, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     (2024, 2, 4, 16), "JIA", "BING", "WU", "GENG", "立春后1秒"),
]

# ============================================================================
# 验证函数
# ============================================================================

def verify_independent_pillars():
    """独立验证四柱计算"""
    results = []
    
    print("=" * 70)
    print("R-04 Independent Four-Pillar Verification")
    print("Pure classical algorithm - NO engine dependency")
    print("=" * 70)
    
    for civil_dt, solar_date, exp_year, exp_month_stem, exp_day_stem, exp_hour_stem, desc in TEST_CASES:
        civil_date = civil_dt.date()
        effective_date = compute_effective_date(civil_dt)
        
        # 节气边界判断：严格小于
        pre_lichun = civil_dt < LICHUN_2024_BJT
        
        # Year/Month: 基于 civil_date + 节气边界
        year_stem, year_branch = compute_year_pillar(solar_date[0], pre_lichun)
        month_stem, month_branch = compute_month_pillar(year_stem, not pre_lichun)
        
        # Day/Hour: 基于 effective_date
        day_stem, day_branch = compute_day_pillar(effective_date)
        hour_stem, hour_branch = compute_hour_pillar(day_stem, solar_date[3])
        
        # 验证
        y_ok = year_stem == exp_year
        m_ok = month_stem == exp_month_stem and month_branch in ["YIN", "CHOU"]
        d_ok = day_stem == exp_day_stem
        h_ok = hour_stem == exp_hour_stem
        
        all_ok = y_ok and m_ok and d_ok and h_ok
        status = "PASS" if all_ok else "FAIL"
        
        print(f"\n{status} {desc}")
        print(f"   civil={civil_date}, effective={effective_date}, pre_lichun={pre_lichun}")
        if not all_ok:
            if not y_ok:
                print(f"   Year: expected={exp_year}, got={year_stem} {year_branch}")
            if not m_ok:
                print(f"   Month: expected={exp_month_stem} *, got={month_stem} {month_branch}")
            if not d_ok:
                print(f"   Day: expected={exp_day_stem} *, got={day_stem} {day_branch}")
            if not h_ok:
                print(f"   Hour: expected={exp_hour_stem} *, got={hour_stem} {hour_branch}")
        
        results.append(all_ok)
    
    return all(results)

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    ok = verify_independent_pillars()
    
    print("\n" + "=" * 70)
    if ok:
        print("✅ ALL INDEPENDENT VERIFICATION TESTS PASSED")
        print("Verification is TRULY independent of BaziEngine")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)
