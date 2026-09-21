#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('dayun_align_mod', 'scripts/dayun_align.py')
mod = importlib.util.module_from_spec(spec)
import unittest.mock
with unittest.mock.patch('sys.argv', ['dayun_align.py']):
    try: spec.loader.exec_module(mod)
    except SystemExit: pass
engine = mod.engine

test_cases = [
    ('冬月调候', [('癸','亥'),('壬','戌'),('乙','未'),('壬','午')]),
    ('专旺格', [('甲','寅'),('甲','寅'),('甲','寅'),('甲','子')]),
    ('身弱', [('辛','卯'),('丁','酉'),('庚','午'),('丙','子')]),
]
for name, fp in test_cases:
    p, f, ye, tp0 = engine(fp)
    print(f'=== {name} ===')
    print(f'  primary: {ye.get("yongshen_primary")}')
    print(f'  secondary: {ye.get("yongshen_secondary")}')
    print(f'  avoid: {ye.get("yongshen_avoid")}')
    print(f'  paths: {ye.get("yongshen_paths")}')
    print(f'  spectrum_tier: {ye.get("spectrum_tier")}')
    print(f'  special: {ye.get("special")}')
    print(f'  theory_source: {ye.get("theory_source")}')
    cands = ye.get('yongshen_candidates') or []
    print(f'  candidates ({len(cands)}):')
    for c in cands:
        print(f'    {c.get("wuxing")} | path={c.get("path")} | {str(c.get("note",""))[:50]}')
    print()
