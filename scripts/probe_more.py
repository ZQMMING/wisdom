# -*- coding: utf-8 -*-
import sys,re; sys.path.insert(0,'.')
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
cases=[('L418','己巳辛未丙午丁酉'),('L899','戊申戊午丁巳乙巳'),('L886','壬戌己酉戊戌乙卯'),
       ('L905','壬辰壬子壬子癸卯'),('L244','戊子戊午戊戌戊午'),('L856','癸亥辛酉戊申己未'),
       ('L300','己丑丙子丁亥庚子'),('L228','己酉丁卯庚辰甲申'),
       ('L190','丁巳癸丑丁卯丙午'),('L267','癸巳丙辰丙午庚寅'),('L726','己酉丙寅庚申庚辰'),
       ('L554','丙寅甲午丙午癸巳'),('L323','甲寅庚午乙卯丙子'),('L484','癸卯丙辰甲辰丙寅')]
for tag,s in cases:
    g=re.findall(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])',s)
    p={'year':list(g[0]),'month':list(g[1]),'day':list(g[2]),'hour':list(g[3])}
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
    print('%s %s 日主%s%s 七档%s zw=%s/%s | 主%s 喜%s 忌%s %s'%(
        tag,s,ds,WUXING[ds],sp['spectrum'],spp.get('zhuanwang'),spp.get('zhuanwang_state'),
        ye.get('yongshen_primary'),ye.get('yongshen_secondary'),ye.get('yongshen_avoid'),ye.get('yongshen_paths')))
