#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深入分析3个病药轨不准确案例"""
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

target_cases = [
    (269, '戊寅乙丑丙寅庚寅', '庚午'),
    (996, '辛酉丁酉乙未丁丑', '癸巳'),
    (1807, '壬申壬寅壬申辛丑', '丙午'),
]

for li, chart, dayun in target_cases:
    print(f"{'='*80}")
    print(f"L{li} {chart} 运{dayun}")
    print(f"{'='*80}")
    
    for case_li, fp, dy, txt in cases:
        if case_li == li:
            print(f"原典断语:")
            print(f"  {txt[:400]}")
            print()
            
            try: p, f, ye, tp0 = engine(fp)
            except Exception as e:
                print(f"引擎错误: {e}")
                continue
            
            print(f"引擎输出:")
            print(f"  日主: {f['day_stem']}")
            print(f"  special: {ye.get('special')}")
            print(f"  spectrum: {ye.get('spectrum_tier')}")
            print(f"  paths: {ye.get('yongshen_paths')}")
            print(f"  primary: {ye.get('yongshen_primary')}")
            print(f"  secondary: {ye.get('yongshen_secondary')}")
            print(f"  avoid: {ye.get('yongshen_avoid')}")
            
            # 病药信息
            bingyao = ye.get('bingyao') or {}
            if bingyao:
                print(f"  病药: {bingyao}")
            
            print()
            
            GAN_WX = mod.GAN_WX
            BRANCH_WX = mod.BRANCH_WX
            g, z = dayun[0], dayun[1]
            prim = ye.get('yongshen_primary') or ''
            fav = set([prim]) | set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
            av = set(ye.get('yongshen_avoid') or [])
            print(f"大运{dayun}判断:")
            print(f"  干{g}={GAN_WX[g]} (fav={GAN_WX[g] in fav}, av={GAN_WX[g] in av})")
            print(f"  支{z}={BRANCH_WX[z]} (fav={BRANCH_WX[z] in fav}, av={BRANCH_WX[z] in av})")
            print(f"  fav集合: {sorted(fav)}")
            print(f"  av集合: {sorted(av)}")
            print()
            break
    print()
