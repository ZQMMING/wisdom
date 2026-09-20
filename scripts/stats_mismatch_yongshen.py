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
from collections import Counter

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    details = json.load(f)

# 按命局去重
bazi_set = set(d['chart'] for d in details)
print(f'不匹配大运: {len(details)}, 不匹配命局: {len(bazi_set)}')
print()

theory_counter = Counter()
spectrum_counter = Counter()
primary_counter = Counter()
avoid_empty = 0
shenwang_qihou = 0
errors = 0

for chart in bazi_set:
    # chart格式: 庚寅壬午丁卯癸卯 (8字符, 每柱2字符)
    if len(chart) != 8:
        print(f'  格式错误: {chart}')
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
        avoid = ye.get('yongshen_avoid', [])

        theory_counter[theory] += 1
        spectrum_counter[spectrum] += 1
        primary_counter[primary] += 1
        if not avoid:
            avoid_empty += 1
        if theory == 'THEORY_QIONGTONG' and spectrum in ('旺', '旺极', '太旺'):
            shenwang_qihou += 1
    except Exception as e:
        errors += 1
        print(f'  错误 {chart}: {e}')

print(f'成功解析: {len(bazi_set)-errors}/{len(bazi_set)}')
print()
print('theory_source分布:')
for k, v in theory_counter.most_common():
    print(f'  {k}: {v}')
print()
print('spectrum_tier分布:')
for k, v in spectrum_counter.most_common():
    print(f'  {k}: {v}')
print()
print('用神分布(前10):')
for k, v in primary_counter.most_common(10):
    print(f'  {k}: {v}')
print()
print(f'忌神为空的命局: {avoid_empty}/{len(bazi_set)-errors}')
print(f'调候路径+身旺的命局: {shenwang_qihou}/{len(bazi_set)-errors}')
