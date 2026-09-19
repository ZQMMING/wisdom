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

pillars = {
    'year': ('甲', '寅'),
    'month': ('癸', '酉'),
    'day': ('乙', '酉'),
    'hour': ('乙', '酉'),
}
facts = build(pillars)
hidden_stems_table = {pillars[k][1]: facts['hidden_stems'][k] for k in ('year','month','day','hour')}
rc = build_root_classes(pillars, hidden_stems_table)
tc = build_tou_cang(facts)
wx = build_wang_xiang(facts, facts['day_stem'])
rr = build_root_relations(rc, facts['combination_facts'])
ts = build_two_side(rc, tc, rr)
bt = build_branch_tiers(pillars, facts)
th = build_tian_he(pillars, facts)
pa = build_power_structure(pillars)
network = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th, facts=facts)

print('network keys:', list(network.keys()))
print('facts type:', type(network.get('facts')))
if isinstance(network.get('facts'), dict):
    print('facts keys:', list(network['facts'].keys())[:10])
    print('ten_god_members count:', len(network['facts'].get('ten_god_members', [])))
else:
    print('facts:', network.get('facts'))
