# -*- coding: utf-8 -*-
import sys
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

cases = {
    '甲申丙子癸亥癸亥': {'year':['甲','申'],'month':['丙','子'],'day':['癸','亥'],'hour':['癸','亥']},
    '庚申戊寅壬子甲辰': {'year':['庚','申'],'month':['戊','寅'],'day':['壬','子'],'hour':['甲','辰']},
    '乙亥庚辰丙申壬辰': {'year':['乙','亥'],'month':['庚','辰'],'day':['丙','申'],'hour':['壬','辰']},
    '辛未辛丑戊辰壬戌': {'year':['辛','未'],'month':['辛','丑'],'day':['戊','辰'],'hour':['壬','戌']},
    '丁巳癸丑丁卯丙午': {'year':['丁','巳'],'month':['癸','丑'],'day':['丁','卯'],'hour':['丙','午']},
}

for name, pillars in cases.items():
    f = build(pillars)
    pa = build_power_structure(pillars)
    hst = {pillars[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
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
    ys = build_yongshen_engine(pillars, f, wpo, spt, spc, clc)
    print(f'{name}: spectrum={spt.get("spectrum")}, tier={ys.get("spectrum_tier")}, primary={ys.get("yongshen_primary")}, paths={ys.get("yongshen_paths")}, special={spc.get("pattern_name")}')
