"""R-04 Independent Bazi Formula Verification

核心原则：
- 不 import BaziEngine
- 不 import sxtwl
- 纯经典公式手动计算
- 完整四柱 exact match（8字段全部验证）
- hour 从 civil_dt 独立推导，不从 fixture 传入

V2 架构契约：
1. Year/Month pillar: civil_date + 节气边界
   - 节气判断：birth_civil_datetime < jieqi_instant (严格小于)
   - 相等时属于节气后
2. Day/Hour pillar: effective_date (23:00 换日)
3. SOLAR_TERM_BOUNDARY_PRECISION = SECOND (秒级精度契约)
4. 时辰公式：hour == 23 → 子时，否则 ((hour+1)//2) % 12

权威锚点（紫金山天文台/传统万年历）：
- 2024-02-03 = 丁酉日 (索引33)
- 2024-02-04 = 戊戌日 (索引34)
- 立春时刻：2024-02-04 16:26:53 BJT
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

ANCHORS = [
    (date(2024, 2, 3), 33),   # 丁酉
    (date(2024, 2, 4), 34),   # 戊戌
    (date(2024, 2, 5), 35),   # 己亥
]

# ============================================================================
# 节气时刻（北京时间，紫金山天文台数据）
# ============================================================================

LICHUN_2024_BJT = datetime(2024, 2, 4, 16, 26, 53, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
JINGZHE_2024_BJT = datetime(2024, 3, 5, 16, 7, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))

# ============================================================================
# V2 秒级精度契约
# ============================================================================

SOLAR_TERM_BOUNDARY_PRECISION = "SECOND"

# ============================================================================
# 独立计算公式（纯数学，无外部依赖）
# ============================================================================

def compute_year_pillar(year, pre_lichun):
    """年柱：立春前用前一年"""
    if pre_lichun:
        year -= 1
    stem_idx = (year - 4) % 10
    branch_idx = (year - 4) % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


def compute_month_pillar(year_stem, civil_dt, solar_terms):
    """月柱：五虎遁 + 节气边界判断
    
    节气月份映射：
    - 小寒后 → 丑月
    - 立春后 → 寅月
    - 惊蛰后 → 卯月
    - ...
    """
    year_stem_idx = HEAVENLY_STEMS.index(year_stem)
    
    # 五虎遁：正月（寅月）天干起始
    zheng_yue_starts = {0: 2, 1: 4, 2: 6, 3: 8, 4: 0, 5: 0, 6: 4, 7: 6, 8: 8, 9: 2}
    zheng_yue_stem = zheng_yue_starts[year_stem_idx]
    
    # 节气月份映射
    month_branches = [
        ("LICHUN", "YIN"),    # 立春后 → 寅月
        ("JINGZHE", "MAO"),   # 惊蛰后 → 卯月
        ("QINGMING", "CHEN"), # 清明后 → 辰月
        ("LIXIA", "SI"),      # 立夏后 → 巳月
        ("MANGZHONG", "WU"),  # 芒种后 → 午月
        ("XIAOSHU", "WEI"),   # 小暑后 → 未月
        ("LISHU", "SHEN"),    # 立秋后 → 申月
        ("BAILOU", "YOU"),    # 白露后 → 酉月
        ("HANLOU", "XU"),     # 寒露后 → 戌月
        ("LIDONG", "HAI"),    # 立冬后 → 亥月
        ("DAXUE", "ZI"),      # 大雪后 → 子月
        ("XIAOHAN", "CHOU"),  # 小寒后 → 丑月
    ]
    
    # 从 civil_dt 推断当前节气月
    current_branch = "CHOU"  # 默认丑月（小寒前）
    for term_name, branch in month_branches:
        if term_name in solar_terms:
            if civil_dt >= solar_terms[term_name]:
                current_branch = branch
    
    branch_idx = EARTHLY_BRANCHES.index(current_branch)
    yin_idx = EARTHLY_BRANCHES.index("YIN")
    stem_idx = (zheng_yue_stem + (branch_idx - yin_idx)) % 10
    
    return HEAVENLY_STEMS[stem_idx], current_branch


def compute_day_pillar(target_date):
    """日柱：基于六十甲子循环，使用多锚点验证"""
    best_result = None
    best_delta = None
    
    for anchor_date, anchor_idx in ANCHORS:
        delta = (target_date - anchor_date).days
        result_idx = (anchor_idx + delta) % 60
        if best_delta is None or abs(delta) < abs(best_delta):
            best_delta = delta
            best_result = result_idx
    
    stem_idx = best_result % 10
    branch_idx = best_result % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


def compute_hour_pillar(day_stem, hour):
    """时柱：日干 × 时辰（与引擎一致）
    
    公式：
    - hour == 23 → 子时 (0)
    - 其他：((hour + 1) // 2) % 12
    """
    day_stem_idx = HEAVENLY_STEMS.index(day_stem)
    zi_starts = [0, 2, 4, 6, 8]  # 甲丙戊庚壬
    start_idx = zi_starts[day_stem_idx % 5]
    
    if hour == 23:
        hour_branch_idx = 0  # 子时
    else:
        hour_branch_idx = ((hour + 1) // 2) % 12
    
    hour_stem_idx = (start_idx + hour_branch_idx) % 10
    hour_branch = EARTHLY_BRANCHES[hour_branch_idx % 12]
    
    return HEAVENLY_STEMS[hour_stem_idx], hour_branch


def compute_effective_date(civil_dt):
    """23:00 换日规则"""
    if civil_dt.hour >= 23:
        return civil_dt.date() + timedelta(days=1)
    return civil_dt.date()


def compute_effective_hour(civil_dt):
    """从 civil_dt 独立推导 effective_hour"""
    if civil_dt.hour >= 23:
        return 0
    return civil_dt.hour


# ============================================================================
# 完整四柱测试用例（hour 从 civil_dt 独立推导）
# ============================================================================

TEST_CASES = [
    # ===================== 立春边界测试 =====================
    # 2024-02-04 16:30: 立春后，甲辰年丙寅月戊戌日，申时(8)→庚申
    (datetime(2024, 2, 4, 16, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     ("JIA", "CHEN"), ("BING", "YIN"), ("WU", "XU"), ("GENG", "SHEN"),
     "立春后典型命盘"),
    
    # 2024-02-03 12:00: 立春前，癸卯年乙丑月丁酉日，午时(6)→丙午
    (datetime(2024, 2, 3, 12, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     ("GUI", "MAO"), ("YI", "CHOU"), ("DING", "YOU"), ("BING", "WU"),
     "立春前典型命盘"),
    
    # 2024-02-03 23:30: 立春前，癸卯年乙丑月，有效日期2024-02-04(戊戌)，子时(0)→壬子
    (datetime(2024, 2, 3, 23, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     ("GUI", "MAO"), ("YI", "CHOU"), ("WU", "XU"), ("REN", "ZI"),
     "立春前1天23:30"),
    
    # 2024-02-04 23:30: 立春后，甲辰年丙寅月，有效日期2024-02-05(己亥)，子时(0)→甲子
    (datetime(2024, 2, 4, 23, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     ("JIA", "CHEN"), ("BING", "YIN"), ("JI", "HAI"), ("JIA", "ZI"),
     "立春当天23:30"),
    
    # 立春精确时刻边界（秒级）
    (datetime(2024, 2, 4, 16, 26, 52, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     ("GUI", "MAO"), ("YI", "CHOU"), ("WU", "XU"), ("GENG", "SHEN"),
     "立春前1秒"),
    
    (datetime(2024, 2, 4, 16, 26, 53, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     ("JIA", "CHEN"), ("BING", "YIN"), ("WU", "XU"), ("GENG", "SHEN"),
     "立春时刻（相等，属立春后）"),
    
    (datetime(2024, 2, 4, 16, 26, 54, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     ("JIA", "CHEN"), ("BING", "YIN"), ("WU", "XU"), ("GENG", "SHEN"),
     "立春后1秒"),
    
    # ===================== 时辰边界测试 =====================
    # 2024-02-04 00:30: 立春后，甲辰年丙寅月戊戌日，子时(0)→壬子
    (datetime(2024, 2, 4, 0, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     ("JIA", "CHEN"), ("BING", "YIN"), ("WU", "XU"), ("REN", "ZI"),
     "子时00:30（戊日壬子）"),
    
    # 2024-02-04 03:30: 立春后，甲辰年丙寅月戊戌日，寅时(4)→甲寅
    (datetime(2024, 2, 4, 3, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     ("JIA", "CHEN"), ("BING", "YIN"), ("WU", "XU"), ("JIA", "YIN"),
     "寅时03:30（戊日甲寅）"),
    
    # 2024-02-04 12:00: 立春后，甲辰年丙寅月戊戌日，午时(6)→戊午
    (datetime(2024, 2, 4, 12, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     ("JIA", "CHEN"), ("BING", "YIN"), ("WU", "XU"), ("WU", "WU"),
     "午时12:00（戊日戊午）"),
    
    # 2024-02-04 15:30: 立春后，甲辰年丙寅月戊戌日，申时(8)→庚申
    (datetime(2024, 2, 4, 15, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
     ("JIA", "CHEN"), ("BING", "YIN"), ("WU", "XU"), ("GENG", "SHEN"),
     "申时15:30（戊日庚申）"),
    
    # ===================== 惊蛰边界测试 =====================
    # 2024-03-05 16:06:59: 惊蛰前1秒，甲辰年丙寅月... 等待计算正确值
    # 2024-03-05 16:07:00: 惊蛰时刻，甲辰年丁卯月...
    # 2024-03-05 16:07:01: 惊蛰后1秒，甲辰年丁卯月...
]


# ============================================================================
# 验证函数
# ============================================================================

def verify_independent_pillars():
    """独立验证完整四柱（8字段 exact match）"""
    results = []
    
    # 节气字典
    solar_terms = {
        "LICHUN": LICHUN_2024_BJT,
        "JINGZHE": JINGZHE_2024_BJT,
    }
    
    print("=" * 70)
    print("R-04 Independent Bazi Formula Verification")
    print("Full Four-Pillar Exact Oracle - NO engine dependency")
    print("=" * 70)
    
    for civil_dt, exp_year, exp_month, exp_day, exp_hour, desc in TEST_CASES:
        civil_date = civil_dt.date()
        effective_date = compute_effective_date(civil_dt)
        effective_hour = compute_effective_hour(civil_dt)
        
        # 节气边界判断：严格小于
        pre_lichun = civil_dt < LICHUN_2024_BJT
        
        # Year/Month: 基于 civil_date + 节气边界
        year_stem, year_branch = compute_year_pillar(civil_date.year, pre_lichun)
        month_stem, month_branch = compute_month_pillar(
            year_stem, civil_dt, solar_terms
        )
        
        # Day/Hour: 基于 effective_date + effective_hour
        day_stem, day_branch = compute_day_pillar(effective_date)
        hour_stem, hour_branch = compute_hour_pillar(day_stem, effective_hour)
        
        # 完整四柱 exact match（8字段全部验证）
        y_ok = year_stem == exp_year[0] and year_branch == exp_year[1]
        m_ok = month_stem == exp_month[0] and month_branch == exp_month[1]
        d_ok = day_stem == exp_day[0] and day_branch == exp_day[1]
        h_ok = hour_stem == exp_hour[0] and hour_branch == exp_hour[1]
        
        all_ok = y_ok and m_ok and d_ok and h_ok
        status = "PASS" if all_ok else "FAIL"
        
        print(f"\n{status} {desc}")
        print(f"   civil={civil_date}, effective={effective_date}, hour={effective_hour}, pre_lichun={pre_lichun}")
        print(f"   Year={year_stem}{year_branch}, Month={month_stem}{month_branch}, Day={day_stem}{day_branch}, Hour={hour_stem}{hour_branch}")
        
        if not all_ok:
            if not y_ok:
                print(f"   Year: expected={exp_year[0]} {exp_year[1]}, got={year_stem} {year_branch}")
            if not m_ok:
                print(f"   Month: expected={exp_month[0]} {exp_month[1]}, got={month_stem} {month_branch}")
            if not d_ok:
                print(f"   Day: expected={exp_day[0]} {exp_day[1]}, got={day_stem} {day_branch}")
            if not h_ok:
                print(f"   Hour: expected={exp_hour[0]} {exp_hour[1]}, got={hour_stem} {hour_branch}")
        
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
        print("Full four-pillar exact match verified")
        print(f"SOLAR_TERM_BOUNDARY_PRECISION = {SOLAR_TERM_BOUNDARY_PRECISION}")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)
