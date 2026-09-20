# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.daymaster_power_network import build_power_network
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology
from engines.common.special_pattern import build_special_patterns
from engines.common.climate_structure import build_climate_structure
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.yongshen_engine import build_yongshen_engine

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    details = json.load(f)

bazi_set = list(set(d['chart'] for d in details))[:15]

for chart in bazi_set:
    if len(chart) != 8:
        continue
    pillars = {'year': chart[0:2], 'month': chart[2:4], 'day': chart[4:6], 'hour': chart[6:8]}
    try:
        f = build(pillars)
        pa = build_power_structure(pillars)
        hst = {pillars[k][1]: f['hidden_stems'][k] for k in ('year', 'month', 'day', 'hour')}
        rc = build_root_classes(pillars, hst)
        tc = build_tou_cang(f)
        wx = build_wang_xiang(f, f['day_stem'])
        rr = build_root_relations(rc, f['combination_facts'])
        ts = build_two_side(rc, tc, rr)
        bt = build_branch_tiers(pillars, f)
        th = build_tian_he(pillars, f)
        net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th, facts=f)
        wpo = build_wuxing_power(pillars, f, th)
        spt = build_spectrum_topology(net, wpo)
        cl = build_climate_structure(pillars, f, th)
        spc = build_special_patterns(pillars, f, wpo, th, cl)
        clc = build_climate_candidates(f)
        ye = build_yongshen_engine(pillars, f, wpo, spt, spc, clc)

        theory = ye.get('theory_source', 'UNKNOWN')
        spectrum = ye.get('spectrum_tier', 'UNKNOWN')
        primary = ye.get('yongshen_primary', 'NONE')

        if theory == 'THEORY_QIONGTONG' and spectrum in ('旺', '旺极', '太旺'):
            # 输出调候候选
            hou = clc.get('climate_candidates', [])
            hou_stems = [c.get('stem') for c in hou if c.get('stem')]
            dm = f['day_stem']
            dmw = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}[dm]
            print(f'{chart}: 日主={dm}({dmw}), 月令={pillars["month"][1]}, spectrum={spectrum}')
            print(f'  用神={primary}, 调候候选={hou_stems[:5]}')
            print(f'  调候候选是否生扶: {hou_stems[0] if hou_stems else "NONE"} (印={dmw in "木火土金水" and hou_stems and hou_stems[0] == {"木":"水","火":"木","土":"火","金":"土","水":"金"}.get(dmw)})')
            print()
    except Exception as e:
        print(f'  错误 {chart}: {e}')
