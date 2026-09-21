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
cases = mod.cases
from collections import Counter

special_counter = Counter()
for li, fp, dy, txt in cases:
    if len(dy) < 4: continue
    try: p, f, ye, tp0 = engine(fp)
    except Exception: continue
    special = ye.get('special') or '正格'
    special_counter[special] += 1

print('=== special分布 ===')
for special, cnt in special_counter.most_common():
    print(f'  {special}: {cnt}例')
total = sum(special_counter.values())
print(f'  总计: {total}例')
print()
zhengge = special_counter.get('正格', 0)
print(f'  正格: {zhengge}例 ({100*zhengge/total:.1f}%)')
print(f'  非正格: {total-zhengge}例 ({100*(total-zhengge)/total:.1f}%)')
