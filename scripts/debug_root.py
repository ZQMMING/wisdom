# -*- coding: utf-8 -*-
import sys;sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.daymaster_power_network import build_power_network

p={'year':['癸','亥'],'month':['壬','戌'],'day':['乙','卯'],'hour':['壬','午']}
f=build(p)
pa=build_power_structure(p)
hst={p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
rc=build_root_classes(p,hst);tc=build_tou_cang(f);wx=build_wang_xiang(f,f['day_stem'])
rr=build_root_relations(rc,f['combination_facts']);ts=build_two_side(rc,tc,rr)
bt=build_branch_tiers(p,f);th=build_tian_he(p,f)
net=build_power_network(pa,rc,tc,wx,rr,ts,branch_tier=bt,tian_he=th,facts=f)

rr2=net['dimensions']['ROOT_RELATION']
print('root_branch_relations:', rr2.get('root_branch_relations'))
print('combined_root_pillars:', rr2.get('combined_root_pillars'))
print('struck_root_pillars:', rr2.get('struck_root_pillars'))
print()
day_rel=rr2.get('root_branch_relations',{}).get('day',{})
print('day relations:', day_rel.get('relations'))
