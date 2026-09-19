# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build as l0build, WUXING
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.wuxing_power import build_wuxing_power
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.daymaster_power_network import build_power_network
from engines.common.wuxing_power import build_spectrum_topology
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.climate_structure import build_climate_structure
from engines.common.special_pattern import build_special_patterns
fp=[('辛','巳'),('丁','酉'),('丁','酉'),('辛','丑')]
p={'year':list(fp[0]),'month':list(fp[1]),'day':list(fp[2]),'hour':list(fp[3])}
f=l0build(p); ds=f['day_stem']; hst={p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
pa=build_power_structure(p); rc=build_root_classes(p,hst); tc=build_tou_cang(f)
wxo=build_wang_xiang(f,ds); rr=build_root_relations(rc,f['combination_facts'])
ts=build_two_side(rc,tc,rr); bt=build_branch_tiers(p,f); th=build_tian_he(p,f)
wp=build_wuxing_power(p,f,th)
net=build_power_network(pa,rc,tc,wxo,rr,ts,branch_tier=bt,tian_he=th,facts=f)
net.setdefault('facts',{})['daymaster_element']=WUXING[ds]
sp=build_spectrum_topology(net,wp)
clc=build_climate_candidates(f); cls=build_climate_structure(p,f,th)
spp=build_special_patterns(p,f,wp,th,cls)
print('daymaster',ds,WUXING[ds],'spectrum',sp['spectrum'])
print('comb sanhe',f['combination_facts'].get('sanhe'),'sanhui',f['combination_facts'].get('sanhui'))
for w in '木火土金水':
    d=wp['wuxing_power'][w]; print(w,'ben',d.get('ben_n'),'zhong',d.get('zhong_n'),'yu',d.get('yu_n'),'stem',d.get('stem_n'),'ju',d.get('ju_n'),'detail',d.get('root_detail'))
for k in ('cong_type','cong_state','zhuanwang','zhuanwang_state','hua_qi','hua_qi_state','mu_mie','mu_mie_state','liangqi','judgment_status'):
    print(k,'=',spp.get(k))
for pat in spp.get('patterns',[]):
    print('PAT',pat.get('pattern_id'),pat.get('state'),pat.get('boundary_note','')[:60])
