# -*- coding: utf-8 -*-
"""P2-001: 统计EXACT_STEM匹配案例
不修改任何判断逻辑, 只统计输出
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
from engines.common.dayun_xiji import build_dayun_xiji

import json

K = ('year', 'month', 'day', 'hour')
GAN_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
BRANCH_WX = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}

# 读DTS案例
with open('scripts/dts_cases_extracted.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

# 读对齐结果(包含大运列表和原典断语)
# 先跑dayun_align获取数据, 这里简化处理: 直接跑引擎, 统计EXACT_STEM

exact_cases = []
element_cases = []
none_cases = []

stem_stats = {}  # {stem: count}
priority_stats = {}  # {priority: count}

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
        
        # 生成大运(简化: 从月柱顺排8个)
        # 实际大运需要计算, 这里先只统计climate_stem_candidates
        case_id = f"L{case.get('src_line', '?')}"
        
        for cand in csc:
            stem = cand.get('stem', '?')
            priority = cand.get('priority', '?')
            stem_stats[stem] = stem_stats.get(stem, 0) + 1
            priority_stats[priority] = priority_stats.get(priority, 0) + 1
        
        exact_cases.append({
            'case_id': case_id,
            'day_master': ds,
            'month_branch': p['month'][1],
            'csc': csc,
            'fav': sorted(ye.get('yongshen_secondary') or []),
            'av': sorted(ye.get('yongshen_avoid') or []),
            'primary': ye.get('yongshen_primary', ''),
        })
        
    except Exception as e:
        continue

print('=' * 60)
print('P2-001: EXACT_STEM案例统计')
print('=' * 60)
print(f'有QTBJ调候候选的案例数: {len(exact_cases)}')
print()

print('按天干分组:')
for stem, count in sorted(stem_stats.items()):
    print(f'  {stem}: {count}例')
print()

print('按优先级分组:')
for priority, count in sorted(priority_stats.items()):
    print(f'  P{priority}: {count}例')
print()

print('案例详情(前20例):')
for i, case in enumerate(exact_cases[:20]):
    csc_str = ', '.join([f"{c['stem']}(P{c['priority']})" for c in case['csc']])
    print(f"  {case['case_id']}: {case['day_master']}日主 {case['month_branch']}月 | 调候候选: {csc_str} | fav: {case['fav']} | av: {case['av']}")

print()
print('=' * 60)
print('说明: 以上统计基于climate_stem_candidates输出, 未跑大运对齐')
print('      EXACT_STEM匹配需要大运天干与候选天干精确匹配')
print('=' * 60)
