"""
P0-1 Calculation Source Reconciliation
三套数据源逐项 diff：
  1. bazi_l1_facts.py (TIAN_GAN_TWELVE_GROWTH, BRANCH_HIDDEN_STEMS)
  2. reasoning/bazi_fixed_tables.py (LONGHU_STAGE)
  3. reasoning/bazi_ten_gods.py (BRANCH_HIDDEN_STEMS, ten_god)

只审计，不重构。
输出：SOURCE_DIFF_REPORT
"""

import sys
sys.path.insert(0, r'D:\shuntian\backend\src')

from tongshu.engines.bazi_l1_facts import TIAN_GAN_TWELVE_GROWTH, BRANCH_HIDDEN_STEMS as HIDDEN_L1
from tongshu.reasoning.bazi_fixed_tables import LONGHU_STAGE
from tongshu.reasoning.bazi_ten_gods import BRANCH_HIDDEN_STEMS as HIDDEN_TG, ten_god

# 天干映射：英文 -> 中文
STEM_EN_TO_CN = {
    "JIA": "甲", "YI": "乙", "BING": "丙", "DING": "丁", "WU": "戊",
    "JI": "己", "GENG": "庚", "XIN": "辛", "REN": "壬", "GUI": "癸"
}
STEM_CN_TO_EN = {v: k for k, v in STEM_EN_TO_CN.items()}

# 地支映射：英文 -> 中文
BRANCH_EN_TO_CN = {
    "ZI": "子", "CHOU": "丑", "YIN": "寅", "MAO": "卯", "CHEN": "辰", "SI": "巳",
    "WU": "午", "WEI": "未", "SHEN": "申", "YOU": "酉", "XU": "戌", "HAI": "亥"
}
BRANCH_CN_TO_EN = {v: k for k, v in BRANCH_EN_TO_CN.items()}


def compare_twelve_growth():
    """对比十二长生表：bazi_l1_facts vs bazi_fixed_tables"""
    print("=" * 80)
    print("一、十二长生表对比")
    print("=" * 80)
    print(f"  来源1: bazi_l1_facts.py TIAN_GAN_TWELVE_GROWTH (中文天干地支)")
    print(f"  来源2: reasoning/bazi_fixed_tables.py LONGHU_STAGE (英文天干地支)")
    print()

    diffs = []
    total = 0
    match = 0

    for stem_en in STEM_EN_TO_CN:
        stem_cn = STEM_EN_TO_CN[stem_en]
        for branch_en in BRANCH_EN_TO_CN:
            branch_cn = BRANCH_EN_TO_CN[branch_en]
            total += 1

            # 来源1：bazi_l1_facts (中文key)
            stage1 = TIAN_GAN_TWELVE_GROWTH.get(stem_cn, {}).get(branch_cn, "MISSING")

            # 来源2：bazi_fixed_tables (英文key)
            stage2 = LONGHU_STAGE.get(stem_en, {}).get(branch_en, "MISSING")

            if stage1 == stage2:
                match += 1
            else:
                diffs.append({
                    "stem": f"{stem_cn}({stem_en})",
                    "branch": f"{branch_cn}({branch_en})",
                    "bazi_l1_facts": stage1,
                    "bazi_fixed_tables": stage2
                })

    print(f"  总对比数: {total} (10天干 × 12地支)")
    print(f"  一致数: {match}")
    print(f"  差异数: {len(diffs)}")
    print()

    if diffs:
        print("  差异详情:")
        print(f"  {'天干':<12} {'地支':<12} {'bazi_l1_facts':<10} {'bazi_fixed_tables':<10}")
        print("  " + "-" * 50)
        for d in diffs:
            print(f"  {d['stem']:<12} {d['branch']:<12} {d['bazi_l1_facts']:<10} {d['bazi_fixed_tables']:<10}")
    else:
        print("  ✅ 两套十二长生表完全一致")

    print()
    return len(diffs) == 0


def compare_hidden_stems():
    """对比藏干表：bazi_l1_facts vs bazi_ten_gods"""
    print("=" * 80)
    print("二、藏干表对比")
    print("=" * 80)
    print(f"  来源1: bazi_l1_facts.py BRANCH_HIDDEN_STEMS (本气/中气/余气, 中文)")
    print(f"  来源2: reasoning/bazi_ten_gods.py BRANCH_HIDDEN_STEMS (结构可能不同)")
    print()

    diffs = []
    total = 0
    match = 0

    for branch_cn in ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]:
        branch_en = BRANCH_CN_TO_EN[branch_cn]
        total += 1

        # 来源1：bazi_l1_facts (中文key, 本气/中气/余气)
        hidden1 = HIDDEN_L1.get(branch_cn, {})
        benqi1 = hidden1.get("本气")
        zhongqi1 = hidden1.get("中气")
        yuqi1 = hidden1.get("余气")

        # 来源2：bazi_ten_gods (英文key, 结构待确认)
        hidden2 = HIDDEN_TG.get(branch_en, {})

        # 尝试提取 bazi_ten_gods 的藏干结构
        if isinstance(hidden2, dict):
            # 可能的结构：{"main": "GUI", "middle": None, "residual": None}
            benqi2_en = hidden2.get("main") or hidden2.get("benqi") or hidden2.get("本气")
            zhongqi2_en = hidden2.get("middle") or hidden2.get("zhongqi") or hidden2.get("中气")
            yuqi2_en = hidden2.get("residual") or hidden2.get("yuqi") or hidden2.get("余气")
            benqi2 = STEM_EN_TO_CN.get(benqi2_en, benqi2_en) if benqi2_en else None
            zhongqi2 = STEM_EN_TO_CN.get(zhongqi2_en, zhongqi2_en) if zhongqi2_en else None
            yuqi2 = STEM_EN_TO_CN.get(yuqi2_en, yuqi2_en) if yuqi2_en else None
        elif isinstance(hidden2, list):
            # 可能是列表结构
            stems2 = [STEM_EN_TO_CN.get(s, s) for s in hidden2]
            benqi2 = stems2[0] if len(stems2) > 0 else None
            zhongqi2 = stems2[1] if len(stems2) > 1 else None
            yuqi2 = stems2[2] if len(stems2) > 2 else None
        else:
            benqi2 = zhongqi2 = yuqi2 = "UNKNOWN_STRUCTURE"

        # 对比
        same = (benqi1 == benqi2 and zhongqi1 == zhongqi2 and yuqi1 == yuqi2)
        if same:
            match += 1
        else:
            diffs.append({
                "branch": f"{branch_cn}({branch_en})",
                "l1": f"本气={benqi1}, 中气={zhongqi1}, 余气={yuqi1}",
                "tg": f"本气={benqi2}, 中气={zhongqi2}, 余气={yuqi2}",
                "raw_tg": str(hidden2)
            })

    print(f"  总对比数: {total} (12地支)")
    print(f"  一致数: {match}")
    print(f"  差异数: {len(diffs)}")
    print()

    if diffs:
        print("  差异详情:")
        for d in diffs:
            print(f"  {d['branch']}:")
            print(f"    bazi_l1_facts: {d['l1']}")
            print(f"    bazi_ten_gods: {d['tg']}")
            print(f"    raw: {d['raw_tg']}")
    else:
        print("  ✅ 两套藏干表完全一致")

    print()
    return len(diffs) == 0


def inspect_ten_god():
    """检查十神计算：bazi_engine._ten_god vs bazi_ten_gods.ten_god"""
    print("=" * 80)
    print("三、十神计算对比")
    print("=" * 80)
    print(f"  来源1: bazi_engine.py _ten_god (本地副本)")
    print(f"  来源2: reasoning/bazi_ten_gods.py ten_god (canonical)")
    print()

    # 导入 bazi_engine 的 _ten_god
    from tongshu.engines.bazi_engine import _ten_god

    diffs = []
    total = 0
    match = 0

    stems = list(STEM_EN_TO_CN.keys())
    for dm in stems:
        for other in stems:
            total += 1
            result1 = _ten_god(dm, other)
            result2 = ten_god(dm, other)
            if result1 == result2:
                match += 1
            else:
                diffs.append({
                    "dm": STEM_EN_TO_CN[dm],
                    "other": STEM_EN_TO_CN[other],
                    "bazi_engine": result1,
                    "bazi_ten_gods": result2
                })

    print(f"  总对比数: {total} (10×10)")
    print(f"  一致数: {match}")
    print(f"  差异数: {len(diffs)}")
    print()

    if diffs:
        print("  差异详情(前10条):")
        for d in diffs[:10]:
            print(f"    日主={d['dm']}, 他干={d['other']}: bazi_engine={d['bazi_engine']}, bazi_ten_gods={d['bazi_ten_gods']}")
    else:
        print("  ✅ 两套十神计算完全一致")

    print()
    return len(diffs) == 0


def main():
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + "P0-1 Calculation Source Reconciliation — 三套数据源逐项 diff".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    print("  原则：只审计，不重构。")
    print("  目标：确认三套数据源是否一致，差异在哪里。")
    print()

    r1 = compare_twelve_growth()
    r2 = compare_hidden_stems()
    r3 = inspect_ten_god()

    print("=" * 80)
    print("总结")
    print("=" * 80)
    print(f"  十二长生表一致性: {'✅ 一致' if r1 else '❌ 有差异'}")
    print(f"  藏干表一致性:     {'✅ 一致' if r2 else '❌ 有差异'}")
    print(f"  十神计算一致性:   {'✅ 一致' if r3 else '❌ 有差异'}")
    print()

    if r1 and r2 and r3:
        print("  ✅ 三套数据源在已对比的范围内完全一致")
        print("  ⚠️  但'一致'不等于'已经完成权威认证'，仍需原典验证。")
    else:
        print("  ❌ 存在差异，需要进一步分析差异原因")
        print("  差异可能来自：体系不同、命名不同、结构不同、或真正的数据错误")

    print()
    print("  下一步：")
    print("    1. 如有差异，分析差异原因（体系差异 vs 数据错误）")
    print("    2. 对一致的数据，标记为'工程一致，待原典认证'")
    print("    3. 建立 Canonical Source Registry 候选")
    print()


if __name__ == "__main__":
    main()
