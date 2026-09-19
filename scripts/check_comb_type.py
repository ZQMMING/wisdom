# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build

pillars = {
    'year': ('戊', '辰'),
    'month': ('己', '巳'),
    'day': ('庚', '午'),
    'hour': ('辛', '未'),
}
facts = build(pillars)
cf = facts.get('combination_facts', [])
print('combination_facts:')
for c in cf:
    print(f"  {c}")
print(f"\ntype values: {set(c.get('type') for c in cf)}")
