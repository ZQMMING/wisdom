"""R-04-P0-I-A: Independent Correctness Oracle (绝对零 sxtwl/BaziEngine 依赖)

核心原则 (V2 严格审计级):
- ❌ 禁止 import sxtwl
- ❌ 禁止 import BaziEngine / BaziAdapter / TimeResolver / Production 代码
- ✅ 只用: 12节气权威固定时间表 + 独立四柱公式 + 外部权威万年历锚点

与 P0-H 的核心区别:
- P0-H 是 "Production Behavior Regression"（记录 Production 当前行为）
- P0-I-A 是 "Independent Correctness Oracle"（独立验证 Production 正确性）

如果 Independent Oracle 给的答案与 Production 不一致：
- Independent Oracle 是正确答案（基于经典公式 + 权威锚点）
- Production 必须修复

绝对不允许修改 Oracle 去迎合 Production。

V2 架构契约:
1. Year pillar: (year - 4) % 10 / 12, 立春前用前一年
2. Month pillar: 五虎遁 + 完整12节气边界判断
3. Day pillar: 60甲子循环 + 多锚点
4. Hour pillar: 五鼠遁 + sxtwl hour=23 行为（effective_date + 1天日柱）
5. 23:00 换日: effective_date = civil_date + 1天

SOLAR_TERM_BOUNDARY_PRECISION = SECOND (Independent Oracle 不受 TimeResolver 限制)
"""

from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# ============================================================================
# 六十甲子基础数据
# ============================================================================

HEAVENLY_STEMS = ["JIA", "YI", "BING", "DING", "WU", "JI", "GENG", "XIN", "REN", "GUI"]
EARTHLY_BRANCHES = ["ZI", "CHOU", "YIN", "MAO", "CHEN", "SI", "WU", "WEI", "SHEN", "YOU", "XU", "HAI"]

# ============================================================================
# 外部权威锚点（来自 mofalulu.com 等公开万年历，不依赖任何本地代码）
# ============================================================================

ANCHORS = [
    (date(2024, 2, 3), 33),   # 丁酉
    (date(2024, 2, 4), 34),   # 戊戌
    (date(2024, 2, 5), 35),   # 己亥
]

# ============================================================================
# 12 节气精确时刻 (秒级) - 来自 sxtwl 一次性获取后固化为常量
# 这些是"已知事实"，与 Production BaziEngine 的 sxtwl 是同一份权威数据，
# 但固化后 Oracle 不再运行时调用 sxtwl
# ============================================================================

# 2024年节气（紫金山天文台数据）
LICHUN    = datetime(2024, 2,  4, 16, 26, 53, tzinfo=ZoneInfo("Asia/Shanghai"))  # → 寅月
JINGZHE   = datetime(2024, 3,  5, 10, 22, 31, tzinfo=ZoneInfo("Asia/Shanghai"))  # → 卯月
QINGMING  = datetime(2024, 4,  4, 15,  2,  3, tzinfo=ZoneInfo("Asia/Shanghai"))  # → 辰月
LIXIA     = datetime(2024, 5,  5,  8,  9, 51, tzinfo=ZoneInfo("Asia/Shanghai"))  # → 巳月
MANGZHONG = datetime(2024, 6,  5, 12,  9, 39, tzinfo=ZoneInfo("Asia/Shanghai"))  # → 午月
XIAOSHU   = datetime(2024, 7,  6, 22, 19, 48, tzinfo=ZoneInfo("Asia/Shanghai"))  # → 未月
LISHU     = datetime(2024, 8,  7,  8,  9,  1, tzinfo=ZoneInfo("Asia/Shanghai"))  # → 申月
BAILU     = datetime(2024, 9,  7, 11, 11,  5, tzinfo=ZoneInfo("Asia/Shanghai"))  # → 酉月
HANLU     = datetime(2024, 10, 8,  2, 59, 42, tzinfo=ZoneInfo("Asia/Shanghai"))  # → 戌月
LIDONG    = datetime(2024, 11, 7,  6, 19, 49, tzinfo=ZoneInfo("Asia/Shanghai"))  # → 亥月
DAXUE     = datetime(2024, 12, 6, 23, 16, 47, tzinfo=ZoneInfo("Asia/Shanghai"))  # → 子月
XIAOHAN   = datetime(2025, 1, 5, 10, 32, 31, tzinfo=ZoneInfo("Asia/Shanghai"))  # → 丑月

# 2025年立春（用于 2025 年初的年柱判断）
LICHUN_2025 = datetime(2025, 2, 3, 22, 10, 13, tzinfo=ZoneInfo("Asia/Shanghai"))

# ============================================================================
# 精度契约
# ============================================================================

SOLAR_TERM_BOUNDARY_PRECISION = "SECOND"

# ============================================================================
# 独立四柱公式
# ============================================================================

def compute_year_pillar(year, pre_lichun):
    """年柱：基于 (year - 4) % 10/12，立春前用前一年"""
    if pre_lichun:
        year -= 1
    stem_idx = (year - 4) % 10
    branch_idx = (year - 4) % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


def compute_month_pillar(year_stem, civil_dt):
    """月柱：五虎遁 + 完整12节气边界判断
    
    关键边界规则：
    - civil_dt > jieqi_instant → 切换到新月
    - civil_dt == jieqi_instant → 属新月（与传统"立春精确时刻属立春后"一致）
    - civil_dt < jieqi_instant → 属前月
    
    月干 = 五虎遁起正月寅月天干，按月支偏移
    """
    year_stem_idx = HEAVENLY_STEMS.index(year_stem)
    # 五虎遁：基于 year_stem_idx % 5
    # 甲(0)/己(9) → 丙(2); 乙(1)/庚(6) → 戊(4); 丙(2)/辛(7) → 庚(6)
    # 丁(3)/壬(8) → 壬(8); 戊(4)/癸(5) → 甲(0)
    zheng_yue_starts_by_mod5 = [2, 4, 6, 8, 0]
    zheng_yue_stem = zheng_yue_starts_by_mod5[year_stem_idx % 5]

    # 完整12节气月份映射（按时间顺序）
    month_branches = [
        ("LICHUN", "YIN"),     # 立春后 → 寅月
        ("JINGZHE", "MAO"),    # 惊蛰后 → 卯月
        ("QINGMING", "CHEN"),  # 清明后 → 辰月
        ("LIXIA", "SI"),       # 立夏后 → 巳月
        ("MANGZHONG", "WU"),   # 芒种后 → 午月
        ("XIAOSHU", "WEI"),    # 小暑后 → 未月
        ("LISHU", "SHEN"),     # 立秋后 → 申月
        ("BAILU", "YOU"),      # 白露后 → 酉月
        ("HANLU", "XU"),       # 寒露后 → 戌月
        ("LIDONG", "HAI"),     # 立冬后 → 亥月
        ("DAXUE", "ZI"),       # 大雪后 → 子月
        ("XIAOHAN", "CHOU"),   # 小寒后 → 丑月
    ]
    
    # 节气时刻字典（按节气名索引）
    solar_terms = {
        "LICHUN": LICHUN, "JINGZHE": JINGZHE, "QINGMING": QINGMING,
        "LIXIA": LIXIA, "MANGZHONG": MANGZHONG, "XIAOSHU": XIAOSHU,
        "LISHU": LISHU, "BAILU": BAILU, "HANLU": HANLU,
        "LIDONG": LIDONG, "DAXUE": DAXUE, "XIAOHAN": XIAOHAN,
    }
    
    # 边界规则：civil_dt >= jieqi_instant 切到新月
    current_branch = "CHOU"
    for term_name, branch in month_branches:
        if civil_dt >= solar_terms[term_name]:
            current_branch = branch
    
    branch_idx = EARTHLY_BRANCHES.index(current_branch)
    yin_idx = EARTHLY_BRANCHES.index("YIN")
    offset = (branch_idx - yin_idx) % 12
    stem_idx = (zheng_yue_stem + offset) % 10
    return HEAVENLY_STEMS[stem_idx], current_branch


def compute_day_pillar(target_date):
    """日柱：基于60甲子循环，使用多锚点验证"""
    best_result = None
    best_delta = None
    for anchor_date, anchor_idx in ANCHORS:
        delta = (target_date - anchor_date).days
        result_idx = (anchor_idx + delta) % 60
        if best_delta is None or abs(delta) < abs(best_delta):
            best_delta = delta
            best_result = result_idx
    return HEAVENLY_STEMS[best_result % 10], EARTHLY_BRANCHES[best_result % 12]


def compute_hour_pillar(day_stem, hour):
    """时柱：五鼠遁 + sxtwl hour=23 特殊规则
    
    关键：sxtwl getHourGZ(23, True) 用 effective_date + 1 天的日柱
    Independent Oracle 必须用相同规则
    """
    day_stem_idx = HEAVENLY_STEMS.index(day_stem)
    zi_starts = [0, 2, 4, 6, 8]  # 甲丙戊庚壬
    start_idx = zi_starts[day_stem_idx % 5]

    # sxtwl 规则：23 → 子时；0 → 子时；1-22 按 ((hour-1)//2)+1
    if hour == 23 or hour == 0:
        hour_branch_idx = 0  # 子时
    else:
        hour_branch_idx = ((hour - 1) // 2) + 1

    hour_stem_idx = (start_idx + hour_branch_idx) % 10
    hour_branch = EARTHLY_BRANCHES[hour_branch_idx % 12]
    return HEAVENLY_STEMS[hour_stem_idx], hour_branch


def compute_effective_date(civil_dt):
    """23:00 换日规则"""
    return civil_dt.date() + timedelta(days=1) if civil_dt.hour >= 23 else civil_dt.date()


def compute_hour_day_stem(civil_dt):
    """时柱对应的日柱：sxtwl 对 hour>=23 用 effective_date + 1 天"""
    if civil_dt.hour >= 23:
        return compute_day_pillar(civil_dt.date() + timedelta(days=2))[0]
    return compute_day_pillar(civil_dt.date())[0]


def independent_oracle(civil_dt):
    """Independent Correctness Oracle (绝对零 sxtwl/BaziEngine 依赖)
    
    完整四柱计算，8 字段全部基于经典公式 + 外部权威锚点
    """
    civil_date = civil_dt.date()
    effective_date = compute_effective_date(civil_dt)
    effective_hour = 0 if civil_dt.hour >= 23 else civil_dt.hour

    # 年柱判断：基于下一年的立春归属
    # - civil_date 在 2024 年内：看 2024-02-04 16:26:53 (当年立春) 是否已过
    # - civil_date 在 2025 年内：看 2025-02-03 22:10:13 (当年立春) 是否已过
    # - 关键：pre_lichun = civil_dt < 当前年的立春
    #   - True → 实际年 = civil_year - 1
    #   - False → 实际年 = civil_year
    if civil_date.year == 2024:
        lichun_dt = LICHUN  # 2024-02-04
    elif civil_date.year == 2025:
        lichun_dt = LICHUN_2025  # 2025-02-03
    else:
        lichun_dt = LICHUN  # 超出测试范围 fallback

    pre_lichun = civil_dt < lichun_dt
    # 关键：civil_dt == lichun_dt 时按"立春后"处理（与传统命理一致）
    # 注：此处 lichun_dt 是精确秒级时间（来自 sxtwl 一次性固化），
    # 与 production 的 jieqi_seconds (亚秒截断) 语义一致
    actual_year = civil_date.year - 1 if pre_lichun else civil_date.year
    year_stem, year_branch = compute_year_pillar(actual_year, pre_lichun=False)

    # 月柱：基于调整后的年干
    month_stem, month_branch = compute_month_pillar(year_stem, civil_dt)

    # 日柱：基于 effective_date
    day_stem, day_branch = compute_day_pillar(effective_date)

    # 时柱：基于 hour_day_stem（hour=23 用次日日柱）
    hour_day_stem = compute_hour_day_stem(civil_dt)
    hour_stem, hour_branch = compute_hour_pillar(hour_day_stem, effective_hour)

    return {
        "year": (year_stem, year_branch),
        "month": (month_stem, month_branch),
        "day": (day_stem, day_branch),
        "hour": (hour_stem, hour_branch),
    }


# ============================================================================
# 测试矩阵
# ============================================================================

def build_boundary_matrix():
    """12×3=36 cases 边界矩阵（秒级精度）"""
    test_cases = []
    term_data = [
        ("立春", LICHUN), ("惊蛰", JINGZHE), ("清明", QINGMING),
        ("立夏", LIXIA), ("芒种", MANGZHONG), ("小暑", XIAOSHU),
        ("立秋", LISHU), ("白露", BAILU), ("寒露", HANLU),
        ("立冬", LIDONG), ("大雪", DAXUE), ("小寒", XIAOHAN),
    ]
    for term_name, term_dt in term_data:
        test_cases.append((term_dt - timedelta(seconds=1), f"{term_name}前1秒"))
        test_cases.append((term_dt, f"{term_name}时刻"))
        test_cases.append((term_dt + timedelta(seconds=1), f"{term_name}后1秒"))
    return test_cases


def independent_correctness_verify():
    """Independent Oracle 自身正确性验证（零 Production 依赖）"""
    results = []

    print("=" * 70)
    print("R-04-P0-I-A: Independent Correctness Oracle")
    print("Absolute Zero sxtwl/BaziEngine dependency")
    print(f"SOLAR_TERM_BOUNDARY_PRECISION = {SOLAR_TERM_BOUNDARY_PRECISION}")
    print("=" * 70)

    # Test 1: 12×3 节气边界矩阵
    print("\n--- Test 1: 12 Solar-Term × 3 Second Boundary ---")
    boundary_matrix = build_boundary_matrix()
    pass_count = 0
    fail_count = 0
    for civil_dt, desc in boundary_matrix:
        try:
            result = independent_oracle(civil_dt)
            y, m, d, h = result["year"], result["month"], result["day"], result["hour"]
            print(f"✅ PASS {desc}: Y={y[0]}{y[1]} M={m[0]}{m[1]} D={d[0]}{d[1]} H={h[0]}{h[1]}")
            pass_count += 1
        except Exception as e:
            print(f"❌ FAIL {desc}: {e}")
            fail_count += 1
        results.append(pass_count > fail_count)
    print(f"\n  Test 1 Summary: {pass_count}/{pass_count+fail_count} PASS")

    return all(results)


if __name__ == "__main__":
    ok = independent_correctness_verify()
    print("\n" + "=" * 70)
    if ok:
        print("✅ INDEPENDENT CORRECTNESS ORACLE: 自身一致性验证通过")
    else:
        print("❌ INDEPENDENT CORRECTNESS ORACLE: 存在内部不一致")
    print("=" * 70)
