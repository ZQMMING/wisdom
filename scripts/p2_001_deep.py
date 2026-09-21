# -*- coding: utf-8 -*-
"""P2-001: 深入分析EXACT_STEM案例
分析调候候选五行与fav/av的关系
不修改任何判断逻辑
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

K = ('year', 'month', 'day', 'hour')
GAN_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}

with open('scripts/dts_cases_extracted.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

# 分类统计
A_consistent = []  # 调候轨与主轨一致
B_supplement = []   # 调候轨补充
C_conflict = []    # 调候轨与主轨冲突
D_unauthorized = [] # 未授权

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
        
        case_id = f"L{case.get('src_line', '?')}"
        
        # 分析每个调候候选
        for cand in csc:
            stem = cand.get('stem', '?')
            element = GAN_WX.get(stem, '?')
            priority = cand.get('priority', '?')
            
            entry = {
                'case_id': case_id,
                'day_master': ds,
                'month_branch': p['month'][1],
                'stem': stem,
                'element': element,
                'priority': priority,
                'fav': sorted(fav),
                'av': sorted(av),
            }
            
            # 分类
            if element in fav:
                # 调候候选五行在fav中 → 一致
                A_consistent.append(entry)
            elif element in av:
                # 调候候选五行在av中 → 冲突
                C_conflict.append(entry)
            else:
                # 不在fav也不在av → 补充或未授权
                B_supplement.append(entry)
        
    except Exception as e:
        continue

print('=' * 70)
print('P2-001: EXACT_STEM案例深入分析')
print('=' * 70)
print(f'A类(调候候选在fav中-一致): {len(A_consistent)}例')
print(f'B类(调候候选不在fav/av中-补充/未授权): {len(B_supplement)}例')
print(f'C类(调候候选在av中-冲突): {len(C_conflict)}例')
print()

print('=' * 70)
print('C类(冲突)案例详情: 调候候选在av中')
print('=' * 70)
for entry in C_conflict[:30]:
    print(f"  {entry['case_id']}: {entry['day_master']}日主 {entry['month_branch']}月 | "
          f"调候:{entry['stem']}({entry['element']}) P{entry['priority']} | "
          f"av:{entry['av']}")
print(f'  ... 共{len(C_conflict)}例')
print()

print('=' * 70)
print('B类(补充/未授权)案例详情: 调候候选不在fav/av中')
print('=' * 70)
for entry in B_supplement[:30]:
    print(f"  {entry['case_id']}: {entry['day_master']}日主 {entry['month_branch']}月 | "
          f"调候:{entry['stem']}({entry['element']}) P{entry['priority']} | "
          f"fav:{entry['fav']} av:{entry['av']}")
print(f'  ... 共{len(B_supplement)}例')
print()

print('=' * 70)
print('A类(一致)案例: 调候候选在fav中')
print('=' * 70)
print(f'  共{len(A_consistent)}例')
print()

print('=' * 70)
print('关键发现:')
print(f'  C类冲突占比: {len(C_conflict)/(len(A_consistent)+len(B_supplement)+len(C_conflict))*100:.1f}%')
print(f'  B类补充占比: {len(B_supplement)/(len(A_consistent)+len(B_supplement)+len(C_conflict))*100:.1f}%')
print(f'  A类一致占比: {len(A_consistent)/(len(A_consistent)+len(B_supplement)+len(C_conflict))*100:.1f}%')
print('=' * 70)
