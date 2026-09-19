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

pillars = {'year':('甲','子'),'month':('丙','寅'),'day':('戊','午'),'hour':('庚','申')}
facts = build(pillars)
hst = {pillars[k][1]: facts['hidden_stems'][k] for k in ('year','month','day','hour')}
rc = build_root_classes(pillars, hst)
tc = build_tou_cang(facts)
wx = build_wang_xiang(facts, facts['day_stem'])
rr = build_root_relations(rc, facts['combination_facts'])
ts = build_two_side(rc, tc, rr)
bt = build_branch_tiers(pillars, facts)
th = build_tian_he(pillars, facts)
pa = build_power_structure(pillars)
network = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th, facts=facts)
results = run_queries(network)

print(f'=== 160-C Query 总数: {len(results)} ===')
supported = sum(1 for r in results if r['state']=='SUPPORTED')
not_supported = sum(1 for r in results if r['state']=='NOT_SUPPORTED')
unknown = sum(1 for r in results if r['state']=='UNKNOWN')
print(f'SUPPORTED: {supported}, NOT_SUPPORTED: {not_supported}, UNKNOWN: {unknown}')
print()
print('=== Query 清单 ===')
for r in results:
    print(f"  {r['query_id']:40s} {r['state']:15s} {r['name']}")
