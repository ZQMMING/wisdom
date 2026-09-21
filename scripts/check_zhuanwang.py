#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查专旺格识别逻辑"""
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

# 检查L243稼穑格
for li, fp, dy, txt in cases:
    if li == 243:
        print(f"L243 戊子戊午戊戌戊午")
        try: p, f, ye, tp0 = engine(fp)
        except Exception as e:
            print(f"引擎错误: {e}")
            break
        
        print(f"  special: {ye.get('special')}")
        print(f"  zhuanwang: {f.get('zhuanwang')}")
        print(f"  zhuanwang_state: {f.get('zhuanwang_state')}")
        print(f"  cong: {f.get('cong')}")
        print(f"  cong_state: {f.get('cong_state')}")
        print(f"  cong_shun: {f.get('cong_shun')}")
        print(f"  paths: {ye.get('yongshen_paths')}")
        print(f"  primary: {ye.get('yongshen_primary')}")
        print(f"  secondary: {ye.get('yongshen_secondary')}")
        print(f"  avoid: {ye.get('yongshen_avoid')}")
        break

print()
print("=== 检查所有专旺格案例的paths ===")
zhuanwang_cases = []
for li, fp, dy, txt in cases:
    try: p, f, ye, tp0 = engine(fp)
    except Exception: continue
    zw = f.get('zhuanwang') or ''
    if zw:
        paths = ye.get('yongshen_paths') or []
        zhuanwang_cases.append({
            'li': li, 'zw': zw, 'paths': paths,
            'primary': ye.get('yongshen_primary'),
            'special': ye.get('special')
        })

print(f"专旺格案例总数: {len(zhuanwang_cases)}")
print()

# 统计paths分布
from collections import Counter
path_counter = Counter()
for c in zhuanwang_cases:
    path_str = '+'.join(c['paths']) if c['paths'] else '空'
    path_counter[path_str] += 1

print("paths分布:")
for path, cnt in path_counter.most_common():
    print(f"  {path}: {cnt}例")

print()
print("走调候轨(QIHOU)的专旺格案例:")
for c in zhuanwang_cases:
    if 'QIHOU' in c['paths']:
        print(f"  L{c['li']} {c['zw']} paths={c['paths']} primary={c['primary']} special={c['special']}")
