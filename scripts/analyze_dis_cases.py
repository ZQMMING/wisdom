#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析85个不一致案例的用神/avoid判断情况，确认四轨并行的潜在收益"""
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('dayun_align_mod', 'scripts/dayun_align.py')
mod = importlib.util.module_from_spec(spec)
import unittest.mock
with unittest.mock.patch('sys.argv', ['dayun_align.py']):
    try: spec.loader.exec_module(mod)
    except SystemExit: pass

engine = mod.engine
cls_w = mod.cls_w
GAN_WX = mod.GAN_WX
BRANCH_WX = mod.BRANCH_WX
WUXING = mod.WUXING
SHENG = mod.SHENG
KE = mod.KE
luck_verdict = mod.luck_verdict
cases = mod.cases

# 收集不一致案例
dis_cases = []
for li, fp, dy, txt in cases:
    if len(dy) < 4: continue
    try: p, f, ye, tp0 = engine(fp)
    except Exception: continue
    prim = ye.get('yongshen_primary') or ''
    fav = set([prim]) | set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
    av = set(ye.get('yongshen_avoid') or [])
    dm = f['day_stem']
    _spec = ye.get('spectrum_tier') or ''
    paths = ye.get('yongshen_paths') or []
    
    for gz in dy:
        g, z = gz[0], gz[1]
        v, blob = luck_verdict(txt, g, z)
        if blob and blob.lstrip().startswith('【原注】'): v = None
        if not v or v in ('hun', 'lao'): continue
        
        gc = cls_w(GAN_WX[g], fav, av)
        zc = cls_w(BRANCH_WX[z], fav, av)
        
        # V5.1修正版
        if _spec in ('衰极','太衰','衰'):
            _dmwW=WUXING[dm]; _SHENG_ME_W={v:k for k,v in SHENG.items()}
            _yinbi={_dmwW, _SHENG_ME_W.get(_dmwW)}
            _ppY='/'.join(paths)
            if not any(x in _ppY for x in ('CONG','ZHUANWANG','HUA_QI','LIANGQI')):
                _is_yinbi = (GAN_WX.get(g) in _yinbi) or (BRANCH_WX.get(z) in _yinbi)
                if _is_yinbi and (gc=='av' or zc=='av'):
                    gc = 'fav' if gc=='av' else gc
                    zc = 'fav' if zc=='av' else zc
        
        ss={gc,zc}
        if ss=={'xian'}: lc='xian'
        elif 'av' in ss and 'fav' not in ss: lc='av' if ss=={'av'} else 'av_l'
        elif 'fav' in ss and 'av' not in ss: lc='fav' if 'xian' not in ss else 'fav_l'
        else: lc='mix'
        
        if lc in ('mix','xian'): continue
        
        expect='ji' if lc.startswith('fav') else 'xiong'
        if expect != v:
            dis_cases.append({
                'li': li, 'fp': fp, 'gz': gz, 'lc': lc, 'expect': expect, 'v': v,
                'prim': prim, 'fav': sorted(fav), 'av': sorted(av),
                'spectrum': _spec, 'paths': paths, 'special': ye.get('special'),
                'g_wx': GAN_WX[g], 'z_wx': BRANCH_WX[z],
                'gc': gc, 'zc': zc,
            })

print(f"不一致案例总数: {len(dis_cases)}")
print()

# 分析：当前判断为fav但原文xiong的案例（引擎判喜，原文判凶）
fav_to_xiong = [c for c in dis_cases if c['expect']=='ji' and c['v']=='xiong']
av_to_ji = [c for c in dis_cases if c['expect']=='xiong' and c['v']=='ji']

print(f"【fav->xiong】引擎判喜，原文判凶: {len(fav_to_xiong)}例")
print(f"【av->ji】引擎判忌，原文判吉: {len(av_to_ji)}例")
print()

# 分析fav->xiong案例中，大运五行在fav中的情况
print("=== fav->xiong 案例分析 ===")
for c in fav_to_xiong[:20]:
    fp_str = ''.join([g+z for g,z in c['fp']])
    print(f"  L{c['li']} {fp_str} 运{c['gz'][0]}{c['gz'][1]}[{c['lc']}] 原文{c['v']} "
          f"主{c['prim']} 喜{c['fav']} 忌{c['av']} "
          f"干{c['g_wx']}({c['gc']}) 支{c['z_wx']}({c['zc']}) "
          f"谱={c['spectrum']} 路径={c['paths']} 特殊={c['special']}")

print()
print("=== av->ji 案例分析 ===")
for c in av_to_ji[:15]:
    fp_str = ''.join([g+z for g,z in c['fp']])
    print(f"  L{c['li']} {fp_str} 运{c['gz'][0]}{c['gz'][1]}[{c['lc']}] 原文{c['v']} "
          f"主{c['prim']} 喜{c['fav']} 忌{c['av']} "
          f"干{c['g_wx']}({c['gc']}) 支{c['z_wx']}({c['zc']}) "
          f"谱={c['spectrum']} 路径={c['paths']} 特殊={c['special']}")

# 统计：fav->xiong案例中，大运五行是否在avoid中（如果在avoid中，说明四轨并行可能有效）
print()
print("=== 四轨并行潜在收益分析 ===")
# 对于fav->xiong案例，如果大运五行在某个轨的avoid中，说明四轨并行可能有效
# 简化分析：看大运五行是否在当前avoid中（如果在，说明当前判断已经考虑了avoid，但因为fav优先所以判喜）
fav_in_av = sum(1 for c in fav_to_xiong if c['g_wx'] in c['av'] or c['z_wx'] in c['av'])
print(f"  fav->xiong中，大运五行在当前avoid中的案例数: {fav_in_av}/{len(fav_to_xiong)}")
print(f"  (这些案例中，当前fav优先于avoid，四轨并行可能改变裁决)")

# 统计spectrum分布
from collections import Counter
spec_counter = Counter(c['spectrum'] for c in dis_cases)
print()
print("=== 不一致案例spectrum分布 ===")
for spec, cnt in spec_counter.most_common():
    print(f"  {spec}: {cnt}例")

# 统计paths分布
paths_counter = Counter('/'.join(c['paths']) for c in dis_cases)
print()
print("=== 不一致案例paths分布 ===")
for paths, cnt in paths_counter.most_common():
    print(f"  {paths}: {cnt}例")
