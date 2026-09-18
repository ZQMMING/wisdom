# -*- coding: utf-8 -*-
f = 'engines/common/daymaster_power_queries.py'
c = open(f, encoding='utf-8').read()
old = """def _root_combined_away(network: Dict[str, Any]) -> bool:
    \"\"\"检查重根是否被地支合化合走.
    结构: 根支参与六合 + 化神得令(月令五行=化神).
    只记结构, 不判合化真假.\"\"\"
    rr = network['dimensions'].get('ROOT_RELATION', {})
    comb_root = rr.get('combined_root_pillars', []) or []
    if not comb_root:
        return False
    facts = network.get('facts') or {}
    month_branch = facts.get('month_branch', '')
    month_wx = BRANCH_WX.get(month_branch, '')
    root_detail = rr.get('root_branch_relations', {})
    for pillar in comb_root:
        info = root_detail.get(pillar, {})
        for rel in (info.get('relations') or []):
            if rel.get('relation') == 'SIX_COMBINE':
                others = rel.get('with_branches', [])
                if others:
                    pair = frozenset([info.get('branch',''), others[0]])
                    huashen = LIUHE_HUASHEN.get(pair, '')
                    if huashen and month_wx == huashen:
                        return True
    return False"""
new = """def _root_combined_away(network: Dict[str, Any]) -> bool:
    \"\"\"检查重根是否被地支合化合走.
    结构: 根支参与六合 + 化神得令(月令五行=化神) + 化神≠日主五行.
    化神=日主五行时合化成功但根还在(如甲木寅亥合木), 不算合走.
    只记结构, 不判合化真假.\"\"\"
    rr = network['dimensions'].get('ROOT_RELATION', {})
    comb_root = rr.get('combined_root_pillars', []) or []
    if not comb_root:
        return False
    facts = network.get('facts') or {}
    month_branch = facts.get('month_branch', '')
    month_wx = BRANCH_WX.get(month_branch, '')
    day_stem = facts.get('day_stem', '')
    # 日主五行
    STEM_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
    dm_wx = STEM_WX.get(day_stem, '')
    root_detail = rr.get('root_branch_relations', {})
    for pillar in comb_root:
        info = root_detail.get(pillar, {})
        for rel in (info.get('relations') or []):
            if rel.get('relation') == 'SIX_COMBINE':
                others = rel.get('with_branches', [])
                if others:
                    pair = frozenset([info.get('branch',''), others[0]])
                    huashen = LIUHE_HUASHEN.get(pair, '')
                    if huashen and month_wx == huashen and huashen != dm_wx:
                        return True
    return False"""
c = c.replace(old, new)
open(f, 'w', encoding='utf-8').write(c)
print('done')
