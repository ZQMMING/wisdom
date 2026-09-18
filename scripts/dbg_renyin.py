# -*- coding: utf-8 -*-
import sys;sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes,WUXING
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.daymaster_power_network import build_power_network
from engines.common.wuxing_power import build_wuxing_power,build_spectrum_topology
import json
def run(ch):
    p={'year':list(ch[0:2]),'month':list(ch[2:4]),'day':list(ch[4:6]),'hour':list(ch[6:8])}
    f=build(p);pa=build_power_structure(p)
    hst={p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
    rc=build_root_classes(p,hst);tc=build_tou_cang(f);wx=build_wang_xiang(f,f['day_stem'])
    rr=build_root_relations(rc,f['combination_facts']);ts=build_two_side(rc,tc,rr)
    bt=build_branch_tiers(p,f);th=build_tian_he(p,f)
    net=build_power_network(pa,rc,tc,wx,rr,ts,branch_tier=bt,tian_he=th,facts=f)
    net.setdefault('facts',{})['daymaster_element']=WUXING[f['day_stem']]
    wpo=build_wuxing_power(p,f,th);sp=build_spectrum_topology(net,wpo)
    we=wpo['wuxing_power']
    print(ch,'日主五行',wpo['daymaster_element'],'月令',wpo['month_element'])
    for wxname in ['水','火','土','木','金']:
        e=we[wxname]
        print(f'  {wxname}: ling={e["ling_state"]} ben={e["ben_n"]} zhong={e["zhong_n"]} yu={e["yu_n"]} stem={e["stem_n"]} ju={e["ju_n"]}')
    print('  sanhui_ju=',th.get('sanhui_ju'),'sanhe_ju=',th.get('sanhe_ju'))
    print('  ratio=',sp['daymaster_ratio'],'spectrum=',sp['spectrum'])
    print('  self=',sp['self_factors'])
    print('  opp=',sp['opposing_factors'])
run('壬寅辛亥壬子辛丑')
