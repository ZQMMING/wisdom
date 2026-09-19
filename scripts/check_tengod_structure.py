# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build

pillars = {'year':('癸','亥'),'month':('壬','戌'),'day':('乙','未'),'hour':('壬','午')}
facts = build(pillars)

print('=== ten_god_members 结构 ===')
for i, m in enumerate(facts.get('ten_god_members', [])):
    print('  [%d] keys=%s' % (i, list(m.keys())))
    print('       %s' % m)
    if i >= 3:
        break

print('\n=== any_stem_has_ten_god ===')
print(facts.get('any_stem_has_ten_god'))
