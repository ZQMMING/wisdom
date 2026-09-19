# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build as l0build, WUXING
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology
from engines.common.daymaster_power_network import build_power_network
from engines.common.climate_structure import build_climate_structure
from engines.common.special_pattern import build_special_patterns
from engines.common.qtbj_climate_candidates import build_climate_candidates
CASES=[('L1618','癸酉乙丑丙申丙申'),('L1436','丁酉癸卯丙辰丙申'),('L250','辛卯辛卯辛卯辛卯'),('L300','己丑丙子丁亥庚子')]
for tag,ch in CASES:
    fp=[ch[i:i+2] for i in range(0,8,2)]
    p={'year':list(fp[0]),'month':list(fp[1]),'day':list(fp[2]),'hour':list(fp[3])}
    f=l0build(p); ds=f['day_stem']; dmw=WUXING[ds]
    hst={p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
    pa=build_power_structure(p); rc=build_root_classes(p,hst); tc=build_tou_cang(f)
    wxo=build_wang_xiang(f,ds); rr=build_root_relations(rc,f['combination_facts'])
    ts=build_two_side(rc,tc,rr); bt=build_branch_tiers(p,f); th=build_tian_he(p,f)
    wp=build_wuxing_power(p,f,th)
    net=build_power_network(pa,rc,tc,wxo,rr,ts,branch_tier=bt,tian_he=th,facts=f)
    net.setdefault('facts',{})['daymaster_element']=dmw
    sp=build_spectrum_topology(net,wp)
    clc=build_climate_candidates(f); cls=build_climate_structure(p,f,th)
    spp=build_special_patterns(p,f,wp,th,cls)
    w=wp['wuxing_power']
    print(tag,ch,ds,dmw,'七档',sp['spectrum'])
    print('   cong=',spp.get('cong_type'),spp.get('cong_state'),' zhuanwang=',spp.get('zhuanwang'),spp.get('zhuanwang_state'))
    print('   各五行 ben/中余/stem:',{x:(w[x]['ben_n'],w[x]['zhong_n']+w[x]['yu_n'],w[x]['stem_n']) for x in '木火土金水'})
