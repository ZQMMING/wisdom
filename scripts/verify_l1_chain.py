# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
from engines.production_entry import production_entry, FrozenCanonicalBaziChart

pillars = {'year':('甲','子'),'month':('丙','寅'),'day':('戊','午'),'hour':('庚','申')}
chart = FrozenCanonicalBaziChart(pillars=pillars)
r = production_entry(chart)

print('gate_passed:', r['gate_passed'])
print('engine_result keys:', len(r['engine_result']))
print('l1_result keys:', list(r['l1_result'].keys()))
print('query_summary:', r['l1_result']['query_summary'])
print('queries count:', len(r['l1_result']['queries']))
print('前3个query:')
for q in r['l1_result']['queries'][:3]:
    print('  %s: %s - %s' % (q['query_id'], q['state'], q['name']))
