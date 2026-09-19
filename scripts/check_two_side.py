# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side

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
rr = build_root_relations(rc, facts['combination_facts'])
ts = build_two_side(rc, tc, rr)

print('TWO_SIDE:', ts)
print()
op = ts['sides'].get('OPPOSING_SIDE', {})
dm = ts['sides'].get('DAYMASTER_SIDE', {})
print('OPPOSING_SIDE members_present:', op.get('members_present'))
print('DAYMASTER_SIDE members_present:', dm.get('members_present'))
