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
from engines.common.yongshen_engine import build_yongshen_engine

cases=[
 ('L905','壬辰壬子壬子癸卯'),
 ('L1016','壬子辛亥乙亥丙子'),
 ('L244','戊子戊午戊戌戊午'),
 ('L1781','乙亥辛巳丁巳庚戌'),
 ('L1045','丙辰辛丑庚辰丙子'),
 ('L250','辛卯辛卯辛卯辛卯'),
 ('L300','己丑丙子丁亥庚子'),
 ('L366','丙午戊戌丙午戊戌'),
 ('L1520','甲申丙子癸亥癸亥'),
 ('L1287','辛丑丙申癸巳庚申'),
 ('L695','庚寅壬午戊午丁巳'),
 ('L852','壬申辛亥辛酉庚寅'),
 ('L1808','壬申壬寅壬申辛丑'),
 ('L862','癸亥甲寅癸亥甲寅'),
 ('L385','戊寅乙卯甲辰辛未'),
 ('L620','戊寅丁巳丙寅甲午'),
]
for tag,ch in cases:
    fp=[ch[i:i+2] for i in range(0,8,2)]
    p={'year':list(fp[0]),'month':list(fp[1]),'day':list(fp[2]),'hour':list(fp[3])}
    f=l0build(p); ds=f['day_stem']
    hst={p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
    pa=build_power_structure(p); rc=build_root_classes(p,hst); tc=build_tou_cang(f)
    wxo=build_wang_xiang(f,ds); rr=build_root_relations(rc,f['combination_facts'])
    ts=build_two_side(rc,tc,rr); bt=build_branch_tiers(p,f); th=build_tian_he(p,f)
    wp=build_wuxing_power(p,f,th)
    net=build_power_network(pa,rc,tc,wxo,rr,ts,branch_tier=bt,tian_he=th,facts=f)
    net.setdefault('facts',{})['daymaster_element']=WUXING[ds]
    sp=build_spectrum_topology(net,wp)
    clc=build_climate_candidates(f); cls=build_climate_structure(p,f,th)
    spp=build_special_patterns(p,f,wp,th,cls)
    ye=build_yongshen_engine(p,f,wp,sp,spp,clc)
    print('%s %s %s 档%s r%.2f | cong=%s/%s zw=%s/%s lq=%s | 主%s 喜%s 忌%s %s'%(
        tag,ch,ds,sp['spectrum'],sp['daymaster_ratio'],
        spp.get('cong_type'),spp.get('cong_state'),spp.get('zhuanwang'),spp.get('zhuanwang_state'),
        (spp.get('liangqi') or {}).get('relation'),
        ye.get('yongshen_primary'),ye.get('yongshen_secondary'),ye.get('yongshen_avoid'),ye.get('yongshen_paths')))
