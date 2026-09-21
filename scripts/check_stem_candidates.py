#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查用神引擎中是否有天干级候选信息"""
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('dayun_align_mod', 'scripts/dayun_align.py')
mod = importlib.util.module_from_spec(spec)
import unittest.mock
with unittest.mock.patch('sys.argv', ['dayun_align.py']):
    try: spec.loader.exec_module(mod)
    except SystemExit: pass
engine = mod.engine

# 测试几个命例
test_cases = [
    ('冬月调候', [('癸','亥'),('壬','戌'),('乙','未'),('壬','午')]),
    ('身旺', [('甲','寅'),('甲','寅'),('甲','寅'),('甲','子')]),
    ('身弱', [('辛','卯'),('丁','酉'),('庚','午'),('丙','子')]),
]
for name, fp in test_cases:
    p, f, ye, tp0 = engine(fp)
    print(f'=== {name} ===')
    print(f'  day_stem: {f["day_stem"]}')
    print(f'  month_branch: {p["month"][1]}')
    
    # 检查climate_candidates
    clc = ye.get('climate_candidates') or []
    print(f'  climate_candidates ({len(clc)}):')
    for c in clc[:5]:
        print(f'    {c}')
    
    # 检查yongshen_candidates
    cands = ye.get('yongshen_candidates') or []
    print(f'  yongshen_candidates ({len(cands)}):')
    for c in cands:
        print(f'    {c}')
    
    # 检查所有包含stem/gan/tian的key
    print(f'  包含天干信息的keys:')
    for k, v in ye.items():
        if any(x in k.lower() for x in ['stem', 'gan', 'tian', '干']):
            print(f'    {k}: {v}')
    print()
