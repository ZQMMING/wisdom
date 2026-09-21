# -*- coding: utf-8 -*-
"""全面诊断未命中5例
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

# 未命中5例
TARGET_IDS = ['L270', 'L811', 'L1013', 'L1430', 'L1827']

with open('scripts/dts_cases_extracted.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

print('=' * 80)
print('未命中5例全面诊断')
print('=' * 80)
print()

for target_id in TARGET_IDS:
    line_num = target_id[1:]  # 去掉L前缀
    
    # 找案例
    target_case = None
    for case in cases:
        if str(case.get('src_line', '')) == line_num:
            target_case = case
            break
    
    if not target_case:
        print(f'--- {target_id}: 未找到案例 ---')
        print()
        continue
    
    pillars = target_case.get('pillars', [])
    p = {
        'year': pillars[0],
        'month': pillars[1],
        'day': pillars[2],
        'hour': pillars[3],
    }
    
    print(f'--- {target_id}: {p["year"]} {p["month"]} {p["day"]} {p["hour"]} ---')
    
    # 排盘
    f = l0build(p)
    ds = f['day_stem']
    hst = {p[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
    
    print(f'  日主: {ds}({WUXING[ds]}) | 月令: {p["month"][1]}')
    
    # 身强弱
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
    
    ws = sp.get('wang_shuai', {})
    ws_result = ws.get('result', '未知') if isinstance(ws, dict) else str(ws)
    print(f'  旺衰: {ws_result}')
    
    # 格局
    cls = build_climate_structure(p, f, th)
    spp = build_special_patterns(p, f, wp, th, cls)
    special = spp.get('special_name', '正格')
    print(f'  格局: {special}')
    
    # 用神
    clc = build_climate_candidates(f)
    ye = build_yongshen_engine(p, f, wp, sp, spp, clc)
    
    primary = ye.get('yongshen_primary', '')
    secondary = ye.get('yongshen_secondary', [])
    avoid = ye.get('yongshen_avoid', [])
    print(f'  用神: primary={primary}, secondary={secondary}, avoid={avoid}')
    
    # 大运
    dayun = target_case.get('dayun_list', [])
    verdict = target_case.get('verdict_text', '')
    print(f'  大运: {dayun}')
    print(f'  断语: {verdict[:100]}...' if len(verdict) > 100 else f'  断语: {verdict}')
    
    print()

print('=' * 80)
print('分类汇总:')
print('  A类: 用神五行错')
print('  B类: 大运喜忌逻辑错(合去用神/互动级等)')
print('  C类: 格局识别错')
print('  D类: 大运分看边界')
print('=' * 80)
