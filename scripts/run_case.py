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
from engines.common.daymaster_power_queries import run_queries

p={'year':['癸','亥'],'month':['壬','戌'],'day':['乙','卯'],'hour':['壬','午']}
f=build(p)
pa=build_power_structure(p)
hst={p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
rc=build_root_classes(p,hst);tc=build_tou_cang(f);wx=build_wang_xiang(f,f['day_stem'])
rr=build_root_relations(rc,f['combination_facts']);ts=build_two_side(rc,tc,rr)
bt=build_branch_tiers(p,f);th=build_tian_he(p,f)
net=build_power_network(pa,rc,tc,wx,rr,ts,branch_tier=bt,tian_he=th,facts=f)
qs=run_queries(net)

print('=== 1983-11-03 11:30 男 广东中山 ===')
print('四柱: 癸亥 壬戌 乙卯 壬午')
print('日主: 乙木')
print()
print('【算层】')
print('  月令十神:', f.get('month_qi_ten_god',''))
print('  月令藏干:', f['month_hidden_stems'])
print('  透干:', f['month_transparent'])
print()
print('【辩层】')
print('  根:', net['dimensions']['ROOT'])
print('  月令:', net['dimensions']['SEASONAL'])
print('  生扶:', net['dimensions']['SUPPORT'])
print('  泄耗:', net['dimensions']['DRAIN'])
print('  克制:', net['dimensions']['CONTROL'])
print('  天干合:', net['dimensions']['TIAN_HE'])
print()
print('【断言层 SUPPORTED】')
for q in qs:
    if q['state']=='SUPPORTED':
        print('  ✓', q['query_id'].split('QUERY-')[-1])
