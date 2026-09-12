# -*- coding: utf-8 -*-
"""子平 V3.1 端到端案例 - 完整链路:
   八字排盘 (sxtwl + BaziEngine)
   → 子平 (ziping_v3 全部已实现域)
   → §28 统一输出

5 案例覆盖: 得令/失令/夏木/秋金/冬水/湿土/燥土
"""
import sys
sys.path.insert(0, "D:/shuntian")

from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.reasoning.ziping_v3 import chart_to_context
from src.tongshu.reasoning.ziping_v3.reference import build_derived_facts
from src.tongshu.reasoning.ziping_v3.engine import EngineContext
from src.tongshu.reasoning.ziping_v3.judgment import (
    judge_ling, judge_growth, derive_effective_root, derive_party_structure,
    judge_strength, run_strength_chain,
)
from src.tongshu.reasoning.ziping_v3.judgment_ext import (
    judge_qing, judge_tongguan, judge_disease, judge_qi,
    judge_yong, judge_climate,
)
from src.tongshu.reasoning.ziping_v3.runner import run_ziping

# 天干地支 -> 中文 (BaziEngine 返回拼音, 需转汉字)
STEM_PINYIN_TO_CN = {
    "JIA":"甲","YI":"乙","BING":"丙","DING":"丁","WU":"戊","JI":"己",
    "GENG":"庚","XIN":"辛","REN":"壬","GUI":"癸"
}
BRANCH_PINYIN_TO_CN = {
    "ZI":"子","CHOU":"丑","YIN":"寅","MAO":"卯","CHEN":"辰","SI":"巳",
    "WU":"午","WEI":"未","SHEN":"申","YOU":"酉","XU":"戌","HAI":"亥"
}

STEMS_CN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
BRANCHES_CN = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
STEM_IDX = {s: i for i, s in enumerate(STEMS_CN)}
BRANCH_IDX = {b: i for i, b in enumerate(BRANCHES_CN)}


def pillar_to_chinese(stem, branch):
    """支持 int 索引 或 中文 或 拼音 (BaziEngine)."""
    if isinstance(stem, int):
        stem_cn = STEMS_CN[stem]
    elif stem in STEMS_CN:
        stem_cn = stem
    else:
        stem_cn = STEM_PINYIN_TO_CN[stem]
    if isinstance(branch, int):
        branch_cn = BRANCHES_CN[branch]
    elif branch in BRANCHES_CN:
        branch_cn = branch
    else:
        branch_cn = BRANCH_PINYIN_TO_CN[branch]
    return f"{stem_cn}{branch_cn}"

CASES = [
    # (年, 月, 日, 时, 性别, 备注)
    (1980, 6, 22, 10, "male",   "丙火午月-夏季火旺"),
    (1985, 1, 1, 0, "male",     "庚金子月-冬季水寒金泄"),
    (1990, 5, 15, 12, "female", "庚金巳月-夏季金死"),
    (1995, 11, 8, 18, "female", "癸水亥月-冬季水旺"),
    (2000, 8, 8, 8, "male",     "戊土申月-秋季土养"),
]


def run_case(year, month, day, hour, gender, note):
    print(f"\n{'='*72}")
    print(f"【案例】{year}-{month:02d}-{day:02d} {hour:02d}:00 {gender}  ({note})")
    print('='*72)

    # ===== Step 1: 八字排盘 =====
    chart = BaziEngine().compute((year, month, day, hour), gender=gender)
    # sxtwl 独立验证
    import sxtwl
    day_obj = sxtwl.fromSolar(year, month, day)
    gz_year = day_obj.getYearGZ()
    gz_month = day_obj.getMonthGZ()
    gz_day = day_obj.getDayGZ()
    gz_hour = day_obj.getHourGZ(hour)
    sxtwl_pillars = [
        pillar_to_chinese(gz_year.tg, gz_year.dz),
        pillar_to_chinese(gz_month.tg, gz_month.dz),
        pillar_to_chinese(gz_day.tg, gz_day.dz),
        pillar_to_chinese(gz_hour.tg, gz_hour.dz),
    ]

    # BaziEngine 排盘 (用 pillar_to_chinese 自动处理 string/index)
    bazi_pillars = [
        pillar_to_chinese(p.heavenly_stem, p.earthly_branch)
        for p in [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]
    ]
    print(f"  ┌─ Step 1: 八字排盘")
    print(f"  │ 年柱: {bazi_pillars[0]}  月柱: {bazi_pillars[1]}  日柱: {bazi_pillars[2]}  时柱: {bazi_pillars[3]}")
    print(f"  │ sxtwl 校验: {sxtwl_pillars}")
    match = bazi_pillars == sxtwl_pillars
    print(f"  │ sxtwl一致: {'✓' if match else '✗'}")

    # ===== Step 2: 子平 V3 引擎 =====
    fact, avail, ti = chart_to_context(chart)
    derived = build_derived_facts(fact, {"commanded_stem": ti.get("commanded_stem","") if isinstance(ti,dict) else ""})
    cmd = ti.get("commanded_stem","") if isinstance(ti,dict) else ""
    ctx = EngineContext(fact, avail, ti)

    # 各域判断
    chain = run_strength_chain(ctx, derived, special_valid=False)
    ling = chain["LING"]
    growth = chain["GROWTH"]
    strength = chain["STRENGTH"]

    # P4 扩展域
    eff_root = derive_effective_root(ctx, derived)
    party = derive_party_structure(ctx, derived, de_ling=(ling.state=="DE_LING"))
    qing = judge_qing(ctx, derived)
    tongguan = judge_tongguan(ctx, derived)
    disease = judge_disease(ctx, derived, pattern_judgment=None)
    qi = judge_qi(ctx, derived, ling=ling, party=party)
    climate = judge_climate(ctx, derived, climate_table=None)
    yong = judge_yong(ctx, derived, pattern=None, climate=climate,
                      disease=disease, tongguan=tongguan, climate_table=None)

    print(f"  │")
    print(f"  ├─ Step 2: 子平 V3.1 各域判断")
    print(f"  │  LING(得令)   = {ling.state:<25} rule={ling.matched_rule_ids}")
    print(f"  │  GROWTH(长生) = {growth.state:<25} rule={growth.matched_rule_ids}")
    print(f"  │  ROOT(有效根) = {eff_root['EFFECTIVE_ROOT']:<25} kind={eff_root['ROOT_KIND']} avail={eff_root['ROOT_IS_AVAILABLE']}")
    print(f"  │  PARTY(党众)  = 帮身:{party['SUPPORT_STRUCTURE']}  对立:{party['OPPOSITION_STRUCTURE']}")
    print(f"  │  STRENGTH     = {strength.state:<25} rule={strength.matched_rule_ids}")
    print(f"  │  QING(清浊)   = {qing.state:<25} rule={qing.matched_rule_ids}")
    print(f"  │  CLIMATE      = {climate.state:<25} rule={climate.matched_rule_ids}")
    print(f"  │  TONGGUAN     = {tongguan.state:<25} rule={tongguan.matched_rule_ids}")
    print(f"  │  DISEASE      = {disease.state:<25} rule={disease.matched_rule_ids}")
    print(f"  │  QI(气势)     = {qi.state:<25} rule={qi.matched_rule_ids}")
    print(f"  │  YONG(用神)   = pattern={yong['pattern'].state} climate={yong['climate'].state} disease={yong['disease'].state} bridge={yong['bridge'].state}")

    # ===== Step 3: §28 统一输出 (run_ziping 顶层入口) =====
    print(f"  │")
    print(f"  └─ Step 3: §28 统一输出 (run_ziping)")
    s28 = run_ziping(chart, month_command={"commanded_stem": cmd} if cmd else None,
                     climate_table=None)
    print(f"     engine: {s28['engine']} v{s28['version']} status={s28['status']}")
    print(f"     已判断: {len(s28['judgments'])} 项")
    for j in s28['judgments']:
        if j.get('state') not in ('UNDETERMINED','NOT_APPLICABLE'):
            print(f"       {j['domain']:<10} = {j['state']:<25} rule={j.get('matched_rule_ids',[])}")
    print(f"     未实现域 (fail-closed): {len(s28['undetermined'])} 项")
    for u in s28['undetermined'][:8]:
        print(f"       {u['domain']:<20} ({u['reason']})")
    print(f"     日主: {chart.day_master} ({fact.day_master})")
    print(f"     月令: {fact.month_branch} ({ling.state})")
    print(f"     综合: {strength.state}, 气势:{qi.state}, 清浊:{qing.state}, 调候:{climate.state}")
    return match


if __name__ == "__main__":
    print("\n子平 V3.1 端到端 - 5 案例完整链路")
    print("Step 1: 八字排盘 → Step 2: 子平 → Step 3: §28 输出\n")
    results = []
    for case in CASES:
        results.append(run_case(*case))

    print(f"\n{'='*72}")
    print(f"汇总: {sum(results)}/{len(results)} 案例 sxtwl 校验一致")
    print('='*72)
