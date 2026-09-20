# -*- coding: utf-8 -*-
"""分析剩余17个avoid但原文判喜案例的身强弱+十神组合"""
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

STEM_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
BRANCH_WX = {'子':'水','亥':'水','寅':'木','卯':'木','巳':'火','午':'火','申':'金','酉':'金','辰':'土','戌':'土','丑':'土','未':'土'}
SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}  # 我生
KE = {'木':'土','火':'金','土':'水','金':'木','水':'火'}  # 我克
KE_ME = {'木':'金','火':'水','土':'木','金':'火','水':'土'}  # 克我
SHENG_ME = {'木':'水','火':'木','土':'火','金':'土','水':'金'}  # 生我

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    mismatches = json.load(f)

results = []

for m in mismatches:
    chart = m.get('chart', '')
    dayun_str = m.get('dayun', '')
    text = m.get('text', '')
    
    if len(chart) != 8 or not dayun_str or len(dayun_str) != 2:
        continue
    if text != 'XI':
        continue
    
    dm = chart[4]
    dm_wx = STEM_WX.get(dm, '')
    gan = dayun_str[0]
    zhi = dayun_str[1]
    gan_wx = STEM_WX.get(gan, '')
    zhi_wx = BRANCH_WX.get(zhi, '')
    
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
        
        avoid = ye.get('yongshen_avoid', [])
        if gan_wx not in avoid and zhi_wx not in avoid:
            continue
        
        tier = ye.get('spectrum_tier', '')
        
        # 十神
        gan_tg = '比劫' if gan_wx == dm_wx else ('印' if gan_wx == SHENG_ME.get(dm_wx) else ('食伤' if gan_wx == SHENG.get(dm_wx) else ('财' if gan_wx == KE.get(dm_wx) else '官杀')))
        zhi_tg = '比劫' if zhi_wx == dm_wx else ('印' if zhi_wx == SHENG_ME.get(dm_wx) else ('食伤' if zhi_wx == SHENG.get(dm_wx) else ('财' if zhi_wx == KE.get(dm_wx) else '官杀')))
        
        results.append({
            'chart': chart, 'dayun': dayun_str, 'tier': tier,
            'gan_tg': gan_tg, 'zhi_tg': zhi_tg,
            'combo': gan_tg + '+' + zhi_tg
        })
        
    except Exception as e:
        pass

print(f'avoid但原文判喜案例总数: {len(results)}')
print(f'\n=== 按十神组合统计 ===')
from collections import Counter
combo_count = Counter(r['combo'] for r in results)
for combo, count in combo_count.most_common():
    print(f'  {combo}: {count}个')

print(f'\n=== 按身强弱统计 ===')
tier_count = Counter(r['tier'] for r in results)
for tier, count in tier_count.most_common():
    print(f'  {tier}: {count}个')

print(f'\n=== 详细列表 ===')
for r in results:
    print(f"  {r['chart']} {r['dayun']}: tier={r['tier']}, {r['combo']}")
