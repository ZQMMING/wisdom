# -*- coding: utf-8 -*-
"""P2-002-C: 诊断C类冲突案例(258例)
不修改主判断, 只输出结构分类
"""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0build, WUXING
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology, build_spectrum_from_power
from engines.common.daymaster_power_network import build_power_network
from engines.common.climate_structure import build_climate_structure
from engines.common.special_pattern import build_special_patterns
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.yongshen_engine import build_yongshen_engine
import json
from collections import defaultdict

K = ('year', 'month', 'day', 'hour')
GAN_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}

with open('scripts/dts_cases_extracted.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

# 收集C类案例
c_conflict = []

for idx, case in enumerate(cases):
    pillars = case.get('pillars', [])
    if len(pillars) < 4:
        continue
    
    p = {
        'year': pillars[0],
        'month': pillars[1],
        'day': pillars[2],
        'hour': pillars[3],
    }
    
    try:
        f = l0build(p)
        ds = f['day_stem']
        hst = {p[k][1]: f['hidden_stems'][k] for k in K}
        pa = build_power_structure(p)
        rc = build_root_classes(p, hst)
        tc = build_tou_cang(f)
        wxo = build_wang_xiang(f, ds)
        rr = build_root_relations(rc, f['combination_facts'])
        ts = build_two_side(rc, tc, rr)
        bt = build_branch_tiers(p, f)
        th = build_tian_he(p, f)
        wp = build_wuxing_power(p, f, th)
        net = build_power_network(pa, rc, tc, wxo, rr, ts, branch_tier=bt, tian_he=th, facts=f)
        net.setdefault('facts', {})['daymaster_element'] = WUXING[ds]
        sp = build_spectrum_topology(net, wp)
        _spd = build_spectrum_from_power(wp, p)
        sp['wang_shuai'] = _spd.get('wang_shuai')
        sp['qiang_ruo'] = _spd.get('qiang_ruo')
        clc = build_climate_candidates(f)
        cls = build_climate_structure(p, f, th)
        spp = build_special_patterns(p, f, wp, th, cls)
        ye = build_yongshen_engine(p, f, wp, sp, spp, clc)
        
        csc = ye.get('climate_stem_candidates', [])
        if not csc:
            continue
        
        fav = set(ye.get('yongshen_secondary') or [])
        av = set(ye.get('yongshen_avoid') or [])
        special = ye.get('special', '')
        tier = sp.get('wang_shuai', '')
        
        case_id = f"L{case.get('src_line', '?')}"
        
        for cand in csc:
            stem = cand.get('stem', '?')
            element = GAN_WX.get(stem, '?')
            priority = cand.get('priority', '?')
            
            # C类: 调候候选五行在av中
            if element in av:
                c_conflict.append({
                    'case_id': case_id,
                    'day_master': ds,
                    'month_branch': p['month'][1],
                    'stem': stem,
                    'element': element,
                    'priority': priority,
                    'fav': sorted(fav),
                    'av': sorted(av),
                    'special': special,
                    'tier': tier,
                })
        
    except Exception as e:
        continue

print('=' * 70)
print(f'P2-002-C: C类冲突案例诊断 (共{len(c_conflict)}例)')
print('=' * 70)
print()

# 按"日主×月令"分组统计
group_by_dm_month = defaultdict(list)
for entry in c_conflict:
    key = f"{entry['day_master']}{entry['month_branch']}月"
    group_by_dm_month[key].append(entry)

print('按日主×月令分组:')
for key, entries in sorted(group_by_dm_month.items(), key=lambda x: -len(x[1]))[:20]:
    stems = [e['stem'] for e in entries]
    print(f"  {key}: {len(entries)}例 (调候候选: {set(stems)})")
print()

# 按special(特殊格局)分组
group_by_special = defaultdict(list)
for entry in c_conflict:
    group_by_special[entry['special'] or '普通'].append(entry)

print('按特殊格局分组:')
for key, entries in sorted(group_by_special.items(), key=lambda x: -len(x[1])):
    print(f"  {key}: {len(entries)}例")
print()

# 按tier(旺衰)分组
group_by_tier = defaultdict(list)
for entry in c_conflict:
    tier_val = entry['tier']
    if isinstance(tier_val, dict):
        tier_key = tier_val.get('wang_shuai', '未知')
    else:
        tier_key = tier_val or '未知'
    group_by_tier[tier_key].append(entry)

print('按旺衰分组:')
for key, entries in sorted(group_by_tier.items(), key=lambda x: -len(x[1])):
    print(f"  {key}: {len(entries)}例")
print()

# 典型案例详情(前30例)
print('典型案例详情(前30例):')
for entry in c_conflict[:30]:
    print(f"  {entry['case_id']}: {entry['day_master']}日主 {entry['month_branch']}月 | "
          f"调候:{entry['stem']}({entry['element']}) P{entry['priority']} | "
          f"special:{entry['special'] or '普通'} | tier:{entry['tier']} | "
          f"av:{entry['av']}")

print()
print('=' * 70)
print('初步分类:')
print('  C1: 原典明确支持调候轨(调候为急)')
print('  C2: 原典明确限制/条件化(调候需结合扶抑)')
print('  C3: 两套经典体系各自成立(轨道冲突, 并列输出)')
print('  C4: 原典不足, 不能形成Assertion')
print('=' * 70)
