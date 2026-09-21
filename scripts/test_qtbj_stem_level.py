# -*- coding: utf-8 -*-
"""调候专项小样本验证: 筛选冬夏生人案例, 看EXACT_STEM匹配效果"""
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

K = ('year', 'month', 'day', 'hour')
WINTER = ('亥', '子', '丑')
SUMMER = ('巳', '午', '未')

import json
with open('scripts/dts_cases_extracted.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

# 筛选冬夏生人(月支在冬夏)
winter_summer_cases = []
for c in cases:
    pillars = c.get('pillars', [])
    if len(pillars) >= 2:
        month_branch = pillars[1][1]
        if month_branch in WINTER + SUMMER:
            winter_summer_cases.append(c)

print(f'冬夏生人案例总数: {len(winter_summer_cases)}')

exact_count = 0
element_count = 0
none_count = 0
total = 0

for case in winter_summer_cases[:20]:
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
        
        # 用前8个大运(假设标准大运)
        dayun_list = []
        # 从月柱顺排或逆排
        month_gan = p['month'][0]
        month_zhi = p['month'][1]
        # 简单生成8个大运
        for i in range(1, 9):
            # 这里简化, 实际大运需要计算, 先用占位
            pass
        
        # 先不跑大运, 只看climate_stem_candidates
        case_id = f"L{case.get('src_line', '?')}"
        print(f'{case_id} {p["year"]}{p["month"]}{p["day"]}{p["hour"]}: QTBJ候选={[c["stem"] for c in csc]}')
        
    except Exception as e:
        print(f'Error: {e}')
        continue

print()
print('=== 说明: 只验证climate_stem_candidates输出, 大运对齐需完整大运列表 ===')
