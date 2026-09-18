# -*- coding: utf-8 -*-
"""流年层: 原局+大运+流年, 重算结构变化."""
from typing import Any, Dict, List
from engines.common.dayun_summary import dayun_summary


def liunian_summary(pillars: Dict[str, list], dayun: List[str],
                    liunian: str) -> Dict[str, Any]:
    """pillars: 原局; dayun: 大运干支; liunian: 流年干支."""
    # 先算大运层
    base = dayun_summary(pillars, dayun)
    # 加大流年
    all_branches = [pillars[k][1] for k in ('year','month','day','hour')] + [g[1] for g in dayun] + [liunian[1]]
    all_stems = [pillars[k][0] for k in ('year','month','day','hour')] + [g[0] for g in dayun] + [liunian[0]]

    from engines.common.l0_fact_builder import build, ten_god, WUXING, HIDDEN
    facts = build(pillars)
    dm = pillars['day'][0]
    mqi = WUXING[HIDDEN[facts['month_branch']][0]]

    from engines.common.daymaster_branch_tier import classify_branch_tier
    from engines.common.daymaster_root_class import classify_root_in_branches
    t1 = classify_branch_tier(all_branches, mqi)
    r1 = classify_root_in_branches(dm, all_branches, HIDDEN)

    party_count = {}
    for s in all_stems:
        tg = ten_god(dm, s)
        party_count[tg] = party_count.get(tg, 0) + 1

    from engines.common.chong_transit import chong_with_transit
    from engines.common.daymaster_tian_he import HE_TO_HUASHEN
    he_pairs=[]
    for i in range(len(all_stems)):
        for j in range(i+1,len(all_stems)):
            hs=frozenset((all_stems[i],all_stems[j]))
            if hs in HE_TO_HUASHEN: he_pairs.append({'stems':[all_stems[i],all_stems[j]],'huashen':HE_TO_HUASHEN[hs]})
    he_huashen_deshi = any(p['huashen']==mqi for p in he_pairs)
    chong = chong_with_transit([pillars[k][1] for k in ('year','month','day','hour')], mqi, liunian[1])

    return {
        'daymaster': dm,
        'month_qi': mqi,
        'dayun_root': base['dayun_root'],
        'liunian_root': {'has_root': r1['has_root'], 'heavy': r1['has_heavy_root']},
        'root_changed': (base['dayun_root']['has_root'] != r1['has_root'] or
                         base['dayun_root']['heavy'] != r1['has_heavy_root']),
        'party_count': party_count,
        'chong': chong,
        'he_pairs': he_pairs,
        'he_huashen_deshi': he_huashen_deshi,
        'liunian': liunian,
        'judgment_status': 'LIUNIAN_SUMMARY_ONLY',
        'boundary_note': '流年层重算结构变化; 离散枚举不评分; 不输出吉凶',
    }
