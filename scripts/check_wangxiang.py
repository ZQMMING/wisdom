# -*- coding: utf-8 -*-
"""鏍ANG-XIANG: 鏃ュ共鏃虹浉浼戝洑姝荤姸鎬?"""
import csv, sys
sys.path.insert(0, '.')
rows = list(csv.DictReader(open('scripts/dts_513_output.csv', encoding='utf-8-sig')))
# 鐪媙etwork dimensions閲學ANG_XIANG
from engines.common.l0_fact_builder import build
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.daymaster_power_network import build_power_network, run_queries

p={'year':['鐧?,'閰?],'month':['鐢?,'瀛?],'day':['鐧?,'浜?],'hour':['杈?,'閰?]}
f=build(p)
pa=build_power_structure(p)
hst={p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
rc=build_root_classes(p,hst)
tc=build_tou_cang(f)
wx=build_wang_xiang(f, f['day_stem'])
rr=build_root_relations(rc, f['combination_facts'])
ts=build_two_side(rc, tc, rr)
bt=build_branch_tiers(p, f)
th=build_tian_he(p, f)
net=build_power_network(pa,rc,tc,wx,rr,ts,branch_tier=bt,tian_he=th)
print('WANG_XIANG:', net['dimensions'].get('WANG_XIANG'))
