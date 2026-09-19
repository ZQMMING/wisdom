# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_power_network import build_power_network
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_power_queries import run_queries

pillars = {'year':('癸','亥'),'month':('壬','戌'),'day':('乙','未'),'hour':('壬','午')}
facts = build(pillars)
hst = {pillars[k][1]: facts['hidden_stems'][k] for k in ('year','month','day','hour')}
pa = build_power_structure(pillars)
rc = build_root_classes(pillars, hst)
tc = build_tou_cang(facts)
wx = build_wang_xiang(facts, facts['day_stem'])
rr = build_root_relations(rc, facts['combination_facts'])
ts = build_two_side(rc, tc, rr)
bt = build_branch_tiers(pillars, facts)
th = build_tian_he(pillars, facts)
network = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th, facts=facts)
queries = run_queries(network)

print('=== 关键query状态 ===')
for q in queries:
    qid = q['query_id']
    if any(k in qid for k in ['CAIDUO','SHAZHONG','XIEQI','JIRUO','HEAVY','LIGHT','YIN-PARTY','BIJIE']):
        print('  %s: %s - %s' % (qid, q['state'], q['name']))

print('\n=== root_weight_class ===')
for pillar, info in facts.get('root_weight_class_facts', {}).items():
    print('  %s: %s' % (pillar, info))

print('\n=== ten_god_members ===')
for m in facts.get('ten_god_members', []):
    print('  %s: %s (%s)' % (m.get('stem'), m.get('type'), m.get('position')))
