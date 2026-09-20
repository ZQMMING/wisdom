# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build
from engines.common.pzzq_producer_v1 import produce_pattern_candidates

# 案例8: 辛酉日生于戌月
print('=== 案例8: 壬辰 庚戌 辛酉 辛卯 ===')
pillars = {'year': '壬辰', 'month': '庚戌', 'day': '辛酉', 'hour': '辛卯'}
f = build(pillars)
pzzq = produce_pattern_candidates(f)
print('day_stem:', f['day_stem'])
print('month_branch:', f['month_branch'])
print('hidden_stems month:', f['hidden_stems']['month'])
print('pzzq candidates:')
for c in pzzq.get('pattern_candidates', []):
    print('  ', c.get('pattern_type'), c.get('ten_god'), c.get('basis'), c.get('status'))

print()
print('=== 案例9: 壬寅 乙巳 癸亥 庚申 ===')
pillars = {'year': '壬寅', 'month': '乙巳', 'day': '癸亥', 'hour': '庚申'}
f = build(pillars)
pzzq = produce_pattern_candidates(f)
print('day_stem:', f['day_stem'])
print('month_branch:', f['month_branch'])
print('hidden_stems month:', f['hidden_stems']['month'])
print('pzzq candidates:')
for c in pzzq.get('pattern_candidates', []):
    print('  ', c.get('pattern_type'), c.get('ten_god'), c.get('basis'), c.get('status'))
