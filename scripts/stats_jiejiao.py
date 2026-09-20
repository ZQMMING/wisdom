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
from engines.common.dayun_xiji import build_dayun_xiji

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    details = json.load(f)

WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}

jiejiao_count = 0
gaitou_count = 0
jiejiao_avoid = 0
gaitou_avoid = 0

for d in details[:50]:
    chart = d['chart']
    dayun = d['dayun']
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
        dx = build_dayun_xiji(pillars, ye, [dayun], wpo)
        
        step = dx['per_step'][0]
        relations = step.get('relations', [])
        gan = dayun[0]
        zhi = dayun[1]
        gan_wx = WX[gan]
        zhi_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(zhi, '')
        
        is_jiejiao = KE.get(zhi_wx, '') == gan_wx
        is_gaitou = KE.get(gan_wx, '') == zhi_wx
        
        if is_jiejiao:
            jiejiao_count += 1
            if 'GAN_AVOID' in relations:
                jiejiao_avoid += 1
                print(f'截脚+忌神: {chart} {dayun}, 引擎={d["engine"]}, 原文={d["text"]}, relations={relations[:8]}')
        if is_gaitou:
            gaitou_count += 1
            if 'ZHI_AVOID' in relations:
                gaitou_avoid += 1
                print(f'盖头+忌神: {chart} {dayun}, 引擎={d["engine"]}, 原文={d["text"]}, relations={relations[:8]}')
    except Exception as e:
        pass

print(f'\n统计: 截脚={jiejiao_count}, 截脚+忌神={jiejiao_avoid}, 盖头={gaitou_count}, 盖头+忌神={gaitou_avoid}')
