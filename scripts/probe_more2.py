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
cases=[('L752','庚申庚辰甲戌丙寅'),('L1265','甲午丙寅辛酉己丑'),('L1275','壬子戊申戊戌辛酉'),
       ('L1080','戊午壬戌丁卯癸卯'),('L1278','癸卯甲寅丁巳己酉'),('L692','辛卯辛卯丙子甲午'),
       ('L889','庚午己卯壬申己酉'),('L435','戊申壬戌庚申乙酉'),('L1010','庚辰庚辰庚申庚辰'),
       ('L852','壬申辛亥辛酉庚寅'),('L231','庚申壬午辛酉癸巳'),('L647','己卯庚午辛卯甲午')]
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
    wpx=wp['wuxing_power']
    print('%s %s %s%s 档%s r%.2f | cong=%s/%s zw=%s/%s lq=%s | 主%s 喜%s 忌%s %s'%(
        tag,s,ds,WUXING[ds],sp['spectrum'],sp['daymaster_ratio'],spp.get('cong_type'),spp.get('cong_state'),
        spp.get('zhuanwang'),spp.get('zhuanwang_state'),spp.get('liangqi'),
        ye.get('yongshen_primary'),ye.get('yongshen_secondary'),ye.get('yongshen_avoid'),ye.get('yongshen_paths')))
