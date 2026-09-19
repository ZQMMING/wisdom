# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build

pillars = {
    'year': ('甲', '子'),
    'month': ('丙', '寅'),
    'day': ('戊', '午'),
    'hour': ('庚', '申'),
}
facts = build(pillars)
print('=== L0 Fact 字段清单 ===')
for k in sorted(facts.keys()):
    v = facts[k]
    if isinstance(v, list):
        print(f'  {k}: list[{len(v)}]')
    elif isinstance(v, dict):
        print(f'  {k}: dict[{len(v)}]')
    else:
        print(f'  {k}: {type(v).__name__} = {v}')

print('\n=== 关键Fact内容 ===')
print(f'  day_stem: {facts.get("day_stem")}')
print(f'  month_branch: {facts.get("month_branch")}')
print(f'  combination_facts types: {list(facts.get("combination_facts", {}).keys()) if isinstance(facts.get("combination_facts"), dict) else facts.get("combination_facts")}')
print(f'  ten_god_members count: {len(facts.get("ten_god_members", []))}')
print(f'  hidden_stems pillars: {list(facts.get("hidden_stems", {}).keys())}')
print(f'  root_facts: {facts.get("root_facts")}')
print(f'  root_weight_class_facts: {facts.get("root_weight_class_facts")}')
print(f'  changsheng_direction: {facts.get("changsheng_direction")}')
