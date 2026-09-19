# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_root_class import build_root_classes

pillars = {
    'year': ('癸', '卯'),
    'month': ('乙', '丑'),
    'day': ('己', '丑'),
    'hour': ('乙', '亥'),
}
facts = build(pillars)
hidden_stems_table = {pillars[k][1]: facts['hidden_stems'][k] for k in ('year','month','day','hour')}
rc = build_root_classes(pillars, hidden_stems_table)

print('root_weight_class_facts:')
for pillar, info in facts.get('root_weight_class_facts', {}).items():
    print(f"  {pillar}: {info}")
print()
print('rc keys:', list(rc.keys()))
if 'root_classes' in rc:
    print('root_classes:', rc['root_classes'])
if 'root_weight_class' in rc:
    print('root_weight_class:', rc['root_weight_class'])
