# -*- coding: utf-8 -*-
"""P3-002: 诊断正格C类冲突76例
逐例检查两轨是否确实同时成立
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

# 收集正格C类案例
zhengge_c = []

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
        
        # 只取正格
        if special != '正格':
            continue
        
        case_id = f"L{case.get('src_line', '?')}"
        
        for cand in csc:
            stem = cand.get('stem', '?')
            element = GAN_WX.get(stem, '?')
            priority = cand.get('priority', '?')
            applicability = cand.get('applicability', 'APPLICABLE')
            
            # 只取APPLICABLE的(真正的冲突)
            if applicability != 'APPLICABLE':
                continue
            
            # C类: 调候候选五行在av中
            if element in av:
                wang_shuai = sp.get('wang_shuai', {})
                if isinstance(wang_shuai, dict):
                    ws_result = wang_shuai.get('result', '未知')
                else:
                    ws_result = str(wang_shuai)
                
                zhengge_c.append({
                    'case_id': case_id,
                    'day_master': ds,
                    'month_branch': p['month'][1],
                    'stem': stem,
                    'element': element,
                    'priority': priority,
                    'fav': sorted(fav),
                    'av': sorted(av),
                    'wang_shuai': ws_result,
                    'primary': ye.get('yongshen_primary', ''),
                })
        
    except Exception as e:
        continue

print('=' * 70)
print(f'P3-002: 正格C类冲突案例 (共{len(zhengge_c)}例)')
print('=' * 70)
print()

# 按日主×月令分组
group_by_dm_month = defaultdict(list)
for entry in zhengge_c:
    key = entry['day_master'] + entry['month_branch'] + '月'
    group_by_dm_month[key].append(entry)

print('按日主×月令分组:')
for key, entries in sorted(group_by_dm_month.items(), key=lambda x: -len(x[1]))[:15]:
    stems = [e['stem'] for e in entries]
    print(f"  {key}: {len(entries)}例 (调候候选: {set(stems)})")
print()

# 按旺衰分组
group_by_ws = defaultdict(list)
for entry in zhengge_c:
    group_by_ws[entry['wang_shuai']].append(entry)

print('按旺衰分组:')
for key, entries in sorted(group_by_ws.items(), key=lambda x: -len(x[1])):
    print(f"  {key}: {len(entries)}例")
print()

# 典型案例详情
print('典型案例详情(前30例):')
for entry in zhengge_c[:30]:
    print(f"  {entry['case_id']}: {entry['day_master']}日主 {entry['month_branch']}月 | "
          f"调候:{entry['stem']}({entry['element']}) P{entry['priority']} | "
          f"旺衰:{entry['wang_shuai']} | "
          f"primary:{entry['primary']} | av:{entry['av']}")

print()
print('=' * 70)
print('初步分类:')
print('  C3: 两套体系各自成立(轨道冲突, 并列输出)')
print('  C2: 原典明确限制/条件化(调候需结合扶抑)')
print('  C4: 原典不足, 不能形成Assertion')
print('=' * 70)
