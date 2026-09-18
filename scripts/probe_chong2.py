# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build as build_l0, WUXING
from engines.common.wuxing_power import build_wuxing_power
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.daymaster_power_network import build_power_network
def gp(s):
    keys=('year','month','day','hour'); return {keys[i//2]:[s[i],s[i+1]] for i in range(0,8,2)}
for chart in ['戊辰乙卯辛丑丁酉','己亥丁卯庚申庚辰']:
    p=gp(chart); f=build_l0(p); ds=f['day_stem']; wx=WUXING[ds]
    pa=build_power_structure(p)
    rc=build_root_classes(p,{p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')})
    tc=build_tou_cang(f); wxo=build_wang_xiang(f,ds)
    rr=build_root_relations(rc,f['combination_facts']); ts=build_two_side(rc,tc,rr)
    bt=build_branch_tiers(p,f); th=build_tian_he(p,f)
    net=build_power_network(pa,rc,tc,wxo,rr,ts,branch_tier=bt,tian_he=th,facts=f)
    net.setdefault('facts',{})['daymaster_element']=wx
    wpo=build_wuxing_power(p,f,th)
    print('==',chart,ds,wx,'liuchong',f['combination_facts'].get('liuchong'))
    print('  pillar zhi:', {k:p[k][1] for k in ('year','month','day','hour')})
    print('  wp root_detail:', wpo['wuxing_power'][wx].get('root_detail'))
    print('  ROOT detail:', net['dimensions']['ROOT'].get('root_class_detail'))
