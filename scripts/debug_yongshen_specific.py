# -*- coding: utf-8 -*-
"""调试特定案例的引擎输出详情"""
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

cases = [
    ("癸巳癸亥甲寅壬申", "DT-0011", "火"),
    ("丁亥壬子庚子辛巳", "DT-0465", "土"),
    ("戊戌甲子己巳戊辰", "PZ-0130", "火"),
]

for bazi, case_id, expected in cases:
    print(f"\n{'='*60}")
    print(f"案例: {case_id} 八字: {bazi} 期望用神: {expected}")
    print(f"{'='*60}")
    
    pillars = {'year': bazi[0:2], 'month': bazi[2:4], 'day': bazi[4:6], 'hour': bazi[6:8]}
    
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
    
    dm = f['day_stem']
    dm_wx = STEM_WX.get(dm, '')
    print(f"日主: {dm} ({dm_wx})")
    print(f"月令: {pillars['month']}")
    print(f"身强弱谱: {ye.get('spectrum_tier', 'N/A')}")
    print(f"理论来源: {ye.get('theory_source', 'N/A')}")
    print(f"用神primary: {ye.get('yongshen_primary', 'N/A')}")
    print(f"用神secondary: {ye.get('yongshen_secondary', [])}")
    print(f"忌神avoid: {ye.get('yongshen_avoid', [])}")
    
    # 调候候选
    if isinstance(clc, dict):
        for k, v in clc.items():
            if 'candidate' in k.lower() or 'qihou' in k.lower() or 'climate' in k.lower():
                print(f"\n{k}: {v}")
    
    # 气候结构
    if isinstance(cl, dict):
        for k, v in cl.items():
            if 'climate' in k.lower() or 'temp' in k.lower() or '寒' in str(v) or '暖' in str(v):
                print(f"气候-{k}: {v}")
    
    # 特殊格局
    if isinstance(spc, dict):
        sp_list = spc.get('special_patterns', [])
        if sp_list:
            print(f"\n特殊格局: {sp_list}")
    
    # 打印ye的所有keys和值
    print(f"\n引擎输出所有keys: {list(ye.keys())}")
    for k in ye.keys():
        if k not in ('yongshen_primary', 'yongshen_secondary', 'yongshen_avoid', 'theory_source', 'spectrum_tier'):
            v = ye[k]
            if isinstance(v, (str, int, float, bool)) or v is None:
                print(f"  {k}: {v}")
            elif isinstance(v, list) and len(v) < 5:
                print(f"  {k}: {v}")
            elif isinstance(v, dict) and len(v) < 5:
                print(f"  {k}: {v}")
