#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""av->ji 31例深度分析
分析大运判为忌(av)但原典判为吉(ji)的案例，找到可修正的模式
"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location("dayun_align_mod", "scripts/dayun_align.py")
mod = importlib.util.module_from_spec(spec)
import unittest.mock
with unittest.mock.patch('sys.argv', ['dayun_align.py']):
    try: spec.loader.exec_module(mod)
    except SystemExit: pass

cases = mod.cases
engine = mod.engine
cls_w = mod.cls_w
GAN_WX = mod.GAN_WX
BRANCH_WX = mod.BRANCH_WX
WUXING = mod.WUXING
luck_verdict = mod.luck_verdict
transit_clash_verdicts = mod.transit_clash_verdicts
build_transit_power = mod.build_transit_power

from engines.common.branch_role_matrix import build_branch_role_matrix

av_ji_cases = []

for li, fp, dy, txt in cases:
    if len(dy) < 4: continue
    try: p, f, ye, tp0 = engine(fp)
    except: continue
    prim = ye.get('yongshen_primary') or ''
    fav = set([prim]) | set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
    av = set(ye.get('yongshen_avoid') or [])
    dm = f['day_stem']
    tier = ye.get('spectrum_tier', 'N/A')
    paths = ye.get('yongshen_paths', [])
    
    for gz in dy:
        g, z = gz[0], gz[1]
        v, blob = luck_verdict(txt, g, z)
        if blob and blob.lstrip().startswith('【原注】'): v = None
        if not v or v in ('hun', 'lao'): continue
        gc = cls_w(GAN_WX[g], fav, av)
        zc = cls_w(BRANCH_WX[z], fav, av)
        ss = {gc, zc}
        
        # 判定lc
        lc = None
        if ss=={'xian'}: lc='xian'
        elif 'av' in ss and 'fav' not in ss: lc='av' if ss=={'av'} else 'av_l'
        elif 'fav' in ss and 'av' not in ss: lc='fav' if 'xian' not in ss else 'fav_l'
        else: lc='mix'
        
        if lc in ('mix','xian'): continue
        if lc.startswith('av') and v == 'ji':
            tp = build_transit_power(p, [gz])
            clash = [c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]
            matrix = build_branch_role_matrix(fp, ye, f)
            
            av_ji_cases.append({
                'case_id': f'L{li+1}',
                'chart': ''.join(a+b for a,b in fp),
                'daymaster': dm,
                'tier': tier,
                'paths': paths,
                'dayun': gz,
                'gc': gc,
                'zc': zc,
                'lc': lc,
                'fav': sorted(fav),
                'avoid': sorted(av),
                'primary': prim,
                'clash': clash,
                'blob': blob[:60] if blob else '',
                'matrix': matrix,
            })

print(f"av->ji 共 {len(av_ji_cases)} 例\n")
print("=" * 80)

# 按特征分类
from collections import Counter
tier_counter = Counter(c['tier'] for c in av_ji_cases)
path_counter = Counter(str(c['paths']) for c in av_ji_cases)
gc_counter = Counter(c['gc'] for c in av_ji_cases)
zc_counter = Counter(c['zc'] for c in av_ji_cases)
has_clash = sum(1 for c in av_ji_cases if c['clash'])

print(f"\n【身旺身弱分布】")
for tier, cnt in tier_counter.most_common():
    print(f"  {tier}: {cnt}例")

print(f"\n【路径分布】")
for path, cnt in path_counter.most_common():
    print(f"  {path}: {cnt}例")

print(f"\n【天干判断分布】")
for gc, cnt in gc_counter.most_common():
    print(f"  {gc}: {cnt}例")

print(f"\n【地支判断分布】")
for zc, cnt in zc_counter.most_common():
    print(f"  {zc}: {cnt}例")

print(f"\n【冲原局】{has_clash}例有冲")

print(f"\n【逐例详情】")
for i, c in enumerate(av_ji_cases, 1):
    print(f"\n{i}. {c['case_id']} {c['chart']} 日主{c['daymaster']} tier={c['tier']} paths={c['paths']}")
    print(f"   大运{c['dayun']} gc={c['gc']} zc={c['zc']} lc={c['lc']}")
    print(f"   primary={c['primary']} fav={c['fav']} avoid={c['avoid']}")
    print(f"   冲={c['clash']}")
    print(f"   原文={c['blob']}")
    # 地支角色矩阵简要
    for pos, info in c['matrix'].items():
        roles = []
        if info['is_heavy_root']: roles.append('重根')
        elif info['is_light_root']: roles.append('轻根')
        if info['has_primary_yongshen']: roles.append('用神根')
        if info['has_avoid']: roles.append('忌神根')
        if info['is_pattern_root']: roles.append('格局根')
        if roles:
            print(f"   [{info['palace']}{info['branch']}] {','.join(roles)}")

print("\n" + "=" * 80)
