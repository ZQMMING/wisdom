#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深入分析5个从格/专旺格未命中案例的原典断语"""
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('dayun_align_mod', 'scripts/dayun_align.py')
mod = importlib.util.module_from_spec(spec)
import unittest.mock
with unittest.mock.patch('sys.argv', ['dayun_align.py']):
    try: spec.loader.exec_module(mod)
    except SystemExit: pass

engine = mod.engine
cases = mod.cases

# 5个问题案例
target_cases = [
    (249, '辛卯辛卯辛卯辛卯', '丁亥', '从财格'),
    (518, '辛卯丙申癸卯甲寅', '壬辰', '从儿格'),
    (751, '庚申庚辰甲戌丙寅', '壬午', '从财格'),
    (1121, '丙子丙申丙子丙申', '甲辰', '从财格'),
    (2085, '甲辰丙寅丙寅壬辰', '庚午', '炎上格'),
]

for li, chart, dayun, special in target_cases:
    print(f"{'='*80}")
    print(f"L{li} {chart} 运{dayun} [{special}]")
    print(f"{'='*80}")
    
    # 找到原典断语
    for case_li, fp, dy, txt in cases:
        if case_li == li:
            # 找到包含该大运的断语
            g, z = dayun[0], dayun[1]
            # 打印完整断语
            print(f"原典断语:")
            print(f"  {txt[:500]}")
            print()
            
            # 引擎判断
            try: p, f, ye, tp0 = engine(fp)
            except Exception as e:
                print(f"引擎错误: {e}")
                continue
            
            print(f"引擎输出:")
            print(f"  日主: {f['day_stem']}")
            print(f"  月令: {p['month'][1]}")
            print(f"  special: {ye.get('special')}")
            print(f"  spectrum: {ye.get('spectrum_tier')}")
            print(f"  paths: {ye.get('yongshen_paths')}")
            print(f"  primary: {ye.get('yongshen_primary')}")
            print(f"  secondary: {ye.get('yongshen_secondary')}")
            print(f"  avoid: {ye.get('yongshen_avoid')}")
            print()
            
            # 大运判断
            GAN_WX = mod.GAN_WX
            BRANCH_WX = mod.BRANCH_WX
            prim = ye.get('yongshen_primary') or ''
            fav = set([prim]) | set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
            av = set(ye.get('yongshen_avoid') or [])
            g_wx = GAN_WX[g]
            z_wx = BRANCH_WX[z]
            print(f"大运{dayun}判断:")
            print(f"  干{g}={g_wx} (fav={g_wx in fav}, av={g_wx in av})")
            print(f"  支{z}={z_wx} (fav={z_wx in fav}, av={z_wx in av})")
            print(f"  fav集合: {sorted(fav)}")
            print(f"  av集合: {sorted(av)}")
            print()
            break
    print()
