# -*- coding: utf-8 -*-
"""大运层: 原局+大运干支, 重算结构变化.
不评分不阈值, 只输出离散枚举变化."""
from typing import Any, Dict, List
from engines.common.l0_fact_builder import build, HIDDEN, WUXING
from engines.common.daymaster_root_class import classify_root_in_branches
from engines.common.daymaster_branch_tier import classify_branch_tier
from engines.common.chong_transit import chong_with_transit
from engines.common.daymaster_tian_he import HE_TO_HUASHEN


def dayun_summary(pillars: Dict[str, list], dayun: List[str]) -> Dict[str, Any]:
    """pillars: 原局四柱; dayun: 大运干支列表(如['甲子','乙丑'])."""
    facts = build(pillars)
    dm = pillars['day'][0]
    branches = [pillars[k][1] for k in ('year','month','day','hour')]
    mzi = facts['month_branch']
    mqi = WUXING[HIDDEN[mzi][0]]

    # 原局
    r0 = classify_root_in_branches(dm, branches, HIDDEN)
    t0 = classify_branch_tier(branches, mqi)

    # 大运支
    dy_branches = [g[1] for g in dayun]
    all_branches = branches + dy_branches
    r1 = classify_root_in_branches(dm, all_branches, HIDDEN)
    t1 = classify_branch_tier(all_branches, mqi)

    # 大运冲支
    chong = chong_with_transit(branches, mqi, dy_branches[0] if dy_branches else branches[0])

    # 大运天干合
    all_stems = [pillars[k][0] for k in ('year','month','day','hour')] + [g[0] for g in dayun]
    he_pairs = []
    for i in range(len(all_stems)):
        for j in range(i+1, len(all_stems)):
            hs = frozenset((all_stems[i], all_stems[j]))
            if hs in HE_TO_HUASHEN:
                he_pairs.append({'stems':[all_stems[i],all_stems[j]],'huashen':HE_TO_HUASHEN[hs]})

    return {
        'daymaster': dm,
        'month_qi': mqi,
        'original_root': {'has_root': r0['has_root'], 'heavy': r0['has_heavy_root']},
        'dayun_root': {'has_root': r1['has_root'], 'heavy': r1['has_heavy_root']},
        'root_changed': (r0['has_root'] != r1['has_root'] or r0['has_heavy_root'] != r1['has_heavy_root']),
        'chong': chong,
        'dayun_he_pairs': he_pairs,
        'judgment_status': 'DAYUN_SUMMARY_ONLY',
        'boundary_note': '大运层重算结构变化; 离散枚举不评分; 不输出吉凶',
    }
