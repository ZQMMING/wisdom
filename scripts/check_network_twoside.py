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
    'year': ('戊', '辰'),
    'month': ('己', '巳'),
    'day': ('庚', '午'),
    'hour': ('辛', '未'),
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

two_side = network['dimensions'].get('TWO_SIDE', {})
print('TWO_SIDE keys:', list(two_side.keys()))
op = two_side.get('OPPOSING_SIDE', {})
print('OPPOSING_SIDE:', op)
print('members_present:', op.get('members_present'))
