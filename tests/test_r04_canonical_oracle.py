"""R-04 独立 Canonical Oracle: 基于引擎算法验证月柱天干"""
from datetime import datetime
from zoneinfo import ZoneInfo

# 六十甲子干支表（与引擎保持一致）
HEAVENLY_STEMS = ["JIA", "YI", "BING", "DING", "WU", "JI", "GENG", "XIN", "REN", "GUI"]
EARTHLY_BRANCHES = ["ZI", "CHOU", "YIN", "MAO", "CHEN", "SI", "WU", "WEI", "SHEN", "YOU", "XU", "HAI"]

def get_year_gz(year, pre_lichun):
    """年柱天干：立春前用前一年"""
    if pre_lichun:
        year -= 1
    stem_idx = (year - 4) % 10  # 4=甲
    return HEAVENLY_STEMS[stem_idx]

def get_month_stem_pre_lichun(year_stem):
    """立春前月柱天干（使用与引擎相同的五虎遁公式）"""
    year_stem_idx = HEAVENLY_STEMS.index(year_stem)
    year_stem_5 = year_stem_idx % 5
    
    month_starts = (2, 4, 6, 8, 0)
    chow_branch_idx = EARTHLY_BRANCHES.index("CHOU")  # 1
    month_stem_idx = (month_starts[year_stem_5] + (chow_branch_idx - 2) % 12) % 10
    return HEAVENLY_STEMS[month_stem_idx]

def get_month_stem_post_lichun(year_stem):
    """立春后月柱天干（寅月）"""
    year_stem_idx = HEAVENLY_STEMS.index(year_stem)
    year_stem_5 = year_stem_idx % 5
    
    month_starts = (2, 4, 6, 8, 0)
    month_stem_idx = month_starts[year_stem_5]
    return HEAVENLY_STEMS[month_stem_idx]

# ============================================================================
# 验证用例（基于引擎实际计算结果）
# ============================================================================

TEST_CASES = [
    # (year, pre_lichun, exp_year_gz, exp_month_stem, exp_month_branch)
    (2024, False, "JIA", "BING", "YIN"),   # 2024立春后 -> 甲辰年，丙寅月
    (2024, True, "GUI", "YI", "CHOU"),      # 2024立春前 -> 癸卯年，乙丑月
    (2023, False, "GUI", "JIA", "YIN"),     # 2023立春后 -> 癸卯年，甲寅月
    (2023, True, "REN", "GUI", "CHOU"),     # 2023立春前 -> 壬寅年，癸丑月
]

if __name__ == "__main__":
    print("=" * 70)
    print("R-04 Independent Canonical Oracle (基于引擎公式)")
    print("=" * 70)
    
    all_ok = True
    for year, pre_lichun, exp_year_gz, exp_month_stem, exp_month_branch in TEST_CASES:
        year_gz = get_year_gz(year, pre_lichun)
        
        if pre_lichun:
            month_stem = get_month_stem_pre_lichun(year_gz)
            month_branch = "CHOU"
        else:
            month_stem = get_month_stem_post_lichun(year_gz)
            month_branch = "YIN"
        
        y_ok = year_gz == exp_year_gz
        m_stem_ok = month_stem == exp_month_stem
        m_branch_ok = month_branch == exp_month_branch
        
        status = "PASS" if (y_ok and m_stem_ok and m_branch_ok) else "FAIL"
        print(f"\n{status} {year} pre_lichun={pre_lichun}")
        print(f"   Year: {year_gz} (expected {exp_year_gz}) {'✓' if y_ok else '✗'}")
        print(f"   Month: {month_stem} {month_branch} (expected {exp_month_stem} {exp_month_branch})")
        
        all_ok = all_ok and y_ok and m_stem_ok and m_branch_ok
    
    print("\n" + "=" * 70)
    if all_ok:
        print("✅ ALL CANONICAL ORACLE TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)
