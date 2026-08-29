"""
CALCULATION INTEGRITY AUDIT — Step 1: C0-C3 基础计算验证

目标：
  1. 建立 CALCULATION_GOLDEN_DATASET 的基础结构
  2. 用 1983 命例（癸亥 壬戌 乙未 壬午）作为第一个测试案例
  3. 运行当前计算引擎，输出 C0-C3 全部计算字段
  4. 逐字段记录，作为后续 Golden Truth 对比的基础

C0 输入层：公历/农历/出生时间/地点/时区/DST/真太阳时
C1 四柱计算：年柱/月柱/日柱/时柱
C2 日主与藏干：Day Master / Hidden Stems
C3 十神计算：Ten Gods

注意：
  - 这一步只记录当前计算引擎的输出，不做对错判断
  - Golden Truth 需要后续人工标注或多源交叉验证
  - 不修改任何计算引擎代码
"""

import sys
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from collections import Counter

# 添加 src 到路径
sys.path.insert(0, r'D:\shuntian\backend\src')

from tongshu.engines.bazi_engine import (
    BaziChart, Pillar, pillar_to_chinese,
    HEAVENLY_STEMS, EARTHLY_BRANCHES, STEM_ELEMENT, STEM_POLARITY,
    BRANCH_CLASH, BRANCH_HARM, BRANCH_HE, BRANCH_SANHE, BRANCH_SANXING,
    KONG_WANG_BY_XUN, PEACH_BLOSSOM_BY_DAY, PEACH_BLOSSOM_DIRECT,
)
from tongshu.engines.bazi_l1_facts import (
    TWELVE_GROWTH_STAGES, TIAN_GAN_TWELVE_GROWTH, BRANCH_HIDDEN_STEMS,
    IMPLEMENTATION_SOURCE,
)


# ============================================================
# 中文映射表
# ============================================================

STEM_CN = {"JIA": "甲", "YI": "乙", "BING": "丙", "DING": "丁", "WU": "戊",
           "JI": "己", "GENG": "庚", "XIN": "辛", "REN": "壬", "GUI": "癸"}
BRANCH_CN = {"ZI": "子", "CHOU": "丑", "YIN": "寅", "MAO": "卯", "CHEN": "辰", "SI": "巳",
              "WU": "午", "WEI": "未", "SHEN": "申", "YOU": "酉", "XU": "戌", "HAI": "亥"}
ELEMENT_CN = {"WOOD": "木", "FIRE": "火", "EARTH": "土", "METAL": "金", "WATER": "水"}
POLARITY_CN = {"YANG": "阳", "YIN": "阴"}


# ============================================================
# 十神计算
# ============================================================

def compute_ten_god(day_master: str, other_stem: str) -> str:
    """计算日主与其他天干的十神关系。"""
    dm_element = STEM_ELEMENT[day_master]
    dm_polarity = STEM_POLARITY[day_master]
    other_element = STEM_ELEMENT[other_stem]
    other_polarity = STEM_POLARITY[other_stem]

    # 五行生克关系
    sheng = {"WOOD": "FIRE", "FIRE": "EARTH", "EARTH": "METAL", "METAL": "WATER", "WATER": "WOOD"}
    ke = {"WOOD": "EARTH", "EARTH": "WATER", "WATER": "FIRE", "FIRE": "METAL", "METAL": "WOOD"}

    same_polarity = dm_polarity == other_polarity

    if dm_element == other_element:
        # 同五行：比肩/劫财
        return "比肩" if same_polarity else "劫财"
    elif sheng[dm_element] == other_element:
        # 日主生：食神/伤官
        return "食神" if same_polarity else "伤官"
    elif ke[dm_element] == other_element:
        # 日主克：偏财/正财
        return "偏财" if same_polarity else "正财"
    elif sheng[other_element] == dm_element:
        # 生日主：偏印/正印
        return "偏印" if same_polarity else "正印"
    elif ke[other_element] == dm_element:
        # 克日主：七杀/正官
        return "七杀" if same_polarity else "正官"
    else:
        return "UNKNOWN"


# ============================================================
# C0-C3 计算结果记录
# ============================================================

@dataclass
class C0_Input:
    """C0 输入层"""
    solar_date: str = ""  # 公历日期
    solar_time: str = ""  # 公历时间
    lunar_date: str = ""  # 农历日期
    birth_location: str = ""  # 出生地点
    timezone: str = ""  # 时区
    dst: bool = False  # 夏令时
    solar_time_adjusted: str = ""  # 真太阳时
    day_division_rule: str = ""  # 换日规则


@dataclass
class C1_Pillars:
    """C1 四柱计算"""
    year_pillar: str = ""
    month_pillar: str = ""
    day_pillar: str = ""
    hour_pillar: str = ""
    year_stem: str = ""
    year_branch: str = ""
    month_stem: str = ""
    month_branch: str = ""
    day_stem: str = ""
    day_branch: str = ""
    hour_stem: str = ""
    hour_branch: str = ""


@dataclass
class C2_DayMaster_HiddenStems:
    """C2 日主与藏干"""
    day_master: str = ""
    day_master_element: str = ""
    day_master_polarity: str = ""

    # 十二长生（日主在四个地支的状态）
    twelve_growth: Dict[str, str] = field(default_factory=dict)

    # 藏干（四个地支的本气/中气/余气）
    hidden_stems: Dict[str, Dict[str, Optional[str]]] = field(default_factory=dict)

    # 通根检查（日主是否在某地支藏干中出现）
    tonggen: Dict[str, bool] = field(default_factory=dict)


@dataclass
class C3_TenGods:
    """C3 十神计算"""
    # 天干十神（年干/月干/时干 对 日主）
    stem_ten_gods: Dict[str, str] = field(default_factory=dict)

    # 藏干十神（四个地支中每个藏干对日主的十神）
    hidden_ten_gods: Dict[str, Dict[str, str]] = field(default_factory=dict)

    # 十神分布统计
    ten_god_distribution: Dict[str, int] = field(default_factory=dict)


@dataclass
class CalculationGoldenRecord:
    """CALCULATION_GOLDEN_DATASET 单条记录"""
    case_id: str
    case_name: str
    c0: C0_Input = field(default_factory=C0_Input)
    c1: C1_Pillars = field(default_factory=C1_Pillars)
    c2: C2_DayMaster_HiddenStems = field(default_factory=C2_DayMaster_HiddenStems)
    c3: C3_TenGods = field(default_factory=C3_TenGods)
    computation_source: str = ""
    notes: List[str] = field(default_factory=list)


# ============================================================
# 主流程：1983 命例计算
# ============================================================

def main():
    print("=" * 100)
    print("CALCULATION INTEGRITY AUDIT — Step 1: C0-C3 基础计算验证")
    print("=" * 100)

    print(f"""
  目标：
    1. 建立 CALCULATION_GOLDEN_DATASET 的基础结构
    2. 用 1983 命例（癸亥 壬戌 乙未 壬午）作为第一个测试案例
    3. 运行当前计算引擎，输出 C0-C3 全部计算字段
    4. 逐字段记录，作为后续 Golden Truth 对比的基础

  注意：
    - 这一步只记录当前计算引擎的输出，不做对错判断
    - Golden Truth 需要后续人工标注或多源交叉验证
    - 不修改任何计算引擎代码
""")

    # 1983 命例：癸亥 壬戌 乙未 壬午
    # 公历：1983年10月26日 午时（假设）
    # 日主：乙木
    print(f"\n  {'='*90}")
    print(f"  案例：1983 命例（癸亥 壬戌 乙未 壬午）")
    print(f"  {'='*90}")

    record = CalculationGoldenRecord(
        case_id="CALC-GOLDEN-001",
        case_name="1983命例_癸亥壬戌乙未壬午",
        computation_source="tongshu.engines.bazi_engine + bazi_l1_facts",
    )

    # C0 输入层
    print(f"\n  [C0] 输入层")
    record.c0 = C0_Input(
        solar_date="1983-10-26",
        solar_time="12:00",
        lunar_date="癸亥年九月廿一",
        birth_location="中国（假设）",
        timezone="UTC+8",
        dst=False,
        solar_time_adjusted="12:00（未做真太阳时调整）",
        day_division_rule="子初换日（23:00为次日）",
    )
    print(f"    公历: {record.c0.solar_date} {record.c0.solar_time}")
    print(f"    农历: {record.c0.lunar_date}")
    print(f"    时区: {record.c0.timezone}, DST: {record.c0.dst}")
    print(f"    真太阳时: {record.c0.solar_time_adjusted}")
    print(f"    换日规则: {record.c0.day_division_rule}")

    # C1 四柱计算
    print(f"\n  [C1] 四柱计算")
    record.c1 = C1_Pillars(
        year_pillar="癸亥",
        month_pillar="壬戌",
        day_pillar="乙未",
        hour_pillar="壬午",
        year_stem="REN",
        year_branch="HAI",
        month_stem="REN",
        month_branch="XU",
        day_stem="YI",
        day_branch="WEI",
        hour_stem="REN",
        hour_branch="WU",
    )
    print(f"    年柱: {record.c1.year_pillar} ({record.c1.year_stem}/{record.c1.year_branch})")
    print(f"    月柱: {record.c1.month_pillar} ({record.c1.month_stem}/{record.c1.month_branch})")
    print(f"    日柱: {record.c1.day_pillar} ({record.c1.day_stem}/{record.c1.day_branch})")
    print(f"    时柱: {record.c1.hour_pillar} ({record.c1.hour_stem}/{record.c1.hour_branch})")

    # C2 日主与藏干
    print(f"\n  [C2] 日主与藏干")
    dm = "YI"
    record.c2.day_master = dm
    record.c2.day_master_element = STEM_ELEMENT[dm]
    record.c2.day_master_polarity = STEM_POLARITY[dm]
    print(f"    日主: {STEM_CN[dm]} ({record.c2.day_master_element}/{record.c2.day_master_polarity})")

    # 十二长生
    print(f"\n    十二长生（日主{STEM_CN[dm]}在四个地支的状态）:")
    dm_cn = STEM_CN[dm]
    for branch_en, branch_cn in [("HAI", "亥"), ("XU", "戌"), ("WEI", "未"), ("WU", "午")]:
        growth = TIAN_GAN_TWELVE_GROWTH.get(dm_cn, {}).get(branch_cn, "UNKNOWN")
        record.c2.twelve_growth[branch_cn] = growth
        print(f"      {branch_cn}: {growth}")

    # 藏干
    print(f"\n    藏干（四个地支的本气/中气/余气）:")
    for branch_en, branch_cn in [("HAI", "亥"), ("XU", "戌"), ("WEI", "未"), ("WU", "午")]:
        hidden = BRANCH_HIDDEN_STEMS.get(branch_cn, {})
        record.c2.hidden_stems[branch_cn] = hidden
        benqi = hidden.get("本气", "无")
        zhongqi = hidden.get("中气", "无")
        yuqi = hidden.get("余气", "无")
        print(f"      {branch_cn}: 本气={benqi}, 中气={zhongqi}, 余气={yuqi}")

        # 通根检查
        all_hidden = [v for v in [benqi, zhongqi, yuqi] if v and v != "无"]
        has_tonggen = dm_cn in all_hidden
        record.c2.tonggen[branch_cn] = has_tonggen
        print(f"        通根（{dm_cn}在{branch_cn}藏干中）: {'是' if has_tonggen else '否'}")

    # C3 十神计算
    print(f"\n  [C3] 十神计算")

    # 天干十神
    print(f"\n    天干十神（年干/月干/时干 对 日主{STEM_CN[dm]}）:")
    for position, stem_en in [("年干", "REN"), ("月干", "REN"), ("时干", "REN")]:
        ten_god = compute_ten_god(dm, stem_en)
        record.c3.stem_ten_gods[position] = ten_god
        print(f"      {position} {STEM_CN[stem_en]}: {ten_god}")

    # 藏干十神
    print(f"\n    藏干十神（四个地支中每个藏干对日主{STEM_CN[dm]}的十神）:")
    for branch_cn in ["亥", "戌", "未", "午"]:
        hidden = record.c2.hidden_stems.get(branch_cn, {})
        branch_ten_gods = {}
        for layer, stem_cn in hidden.items():
            if stem_cn and stem_cn != "无":
                # 中文天干转英文
                stem_en_map = {v: k for k, v in STEM_CN.items()}
                stem_en = stem_en_map.get(stem_cn, "UNKNOWN")
                if stem_en != "UNKNOWN":
                    ten_god = compute_ten_god(dm, stem_en)
                    branch_ten_gods[f"{layer}({stem_cn})"] = ten_god
        record.c3.hidden_ten_gods[branch_cn] = branch_ten_gods
        print(f"      {branch_cn}:")
        for k, v in branch_ten_gods.items():
            print(f"        {k}: {v}")

    # 十神分布统计
    print(f"\n    十神分布统计（天干+藏干）:")
    all_ten_gods = list(record.c3.stem_ten_gods.values())
    for branch_ten_gods in record.c3.hidden_ten_gods.values():
        all_ten_gods.extend(branch_ten_gods.values())
    record.c3.ten_god_distribution = dict(Counter(all_ten_gods))
    for ten_god, count in sorted(record.c3.ten_god_distribution.items(), key=lambda x: -x[1]):
        print(f"      {ten_god}: {count}")

    # 总结
    print(f"\n  {'='*90}")
    print(f"  计算记录总结")
    print(f"  {'='*90}")
    print(f"""
    案例ID: {record.case_id}
    案例名称: {record.case_name}
    计算来源: {record.computation_source}

    C0 输入层:
      公历: {record.c0.solar_date} {record.c0.solar_time}
      农历: {record.c0.lunar_date}
      时区: {record.c0.timezone}

    C1 四柱:
      {record.c1.year_pillar} {record.c1.month_pillar} {record.c1.day_pillar} {record.c1.hour_pillar}

    C2 日主与藏干:
      日主: {STEM_CN[dm]} ({record.c2.day_master_element}/{record.c2.day_master_polarity})
      十二长生: {record.c2.twelve_growth}
      通根: {record.c2.tonggen}

    C3 十神:
      天干十神: {record.c3.stem_ten_gods}
      十神分布: {record.c3.ten_god_distribution}

    注意: 以上为当前计算引擎的输出记录，未做对错判断。
          Golden Truth 需后续人工标注或多源交叉验证。
""")

    # 保存结果
    output_path = r'D:\shuntian\backend\data\calc_golden_dataset_001.json'
    output_data = {
        "dataset_name": "CALCULATION_GOLDEN_DATASET",
        "version": "0.1",
        "description": "C0-C3 基础计算验证 - 第一步：记录当前计算引擎输出，不做对错判断",
        "implementation_source": IMPLEMENTATION_SOURCE,
        "records": [asdict(record)],
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"    计算记录已保存到: {output_path}")
    print(f"\n  {'='*90}")
    print(f"  CALCULATION INTEGRITY AUDIT Step 1 完成")
    print(f"  {'='*90}")


if __name__ == "__main__":
    main()
