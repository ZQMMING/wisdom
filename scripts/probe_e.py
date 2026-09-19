# -*- coding: utf-8 -*-
# e类方向反造: 批量dump命局状态, 判系统性偏差(不动gen_topo)
import io,sys
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
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology, BRANCH_WX
from engines.common.daymaster_power_network import build_power_network
from engines.common.climate_structure import build_climate_structure
from engines.common.special_pattern import build_special_patterns
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.yongshen_engine import build_yongshen_engine

CASES=[
 ('L862','癸亥甲寅癸亥甲寅'),('L889','庚午己卯壬申己酉'),('L1080','戊午壬戌丁卯癸卯'),
 ('L1265','甲午丙寅辛酉己丑'),('L1436','丁酉癸卯丙辰丙申'),('L1553','庚寅戊子甲寅丙寅'),
 ('L1606','癸卯乙卯甲寅乙亥'),('L1618','癸酉乙丑丙申丙申'),('L1678','甲寅丁丑甲戌己巳'),
 ('L1744','甲申丙寅甲申庚午'),('L1763','戊戌丙辰辛丑戊戌'),('L2251','己亥癸酉壬申戊申'),
]
def engine(ch):
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
    return p,f,ds,wp,sp,spp,ye
for tag,ch in CASES:
    p,f,ds,wp,sp,spp,ye=engine(ch)
    dmw=WUXING[ds]; mz=p['month'][1]
    w=wp['wuxing_power']
    bs=' '.join('%s:b%d z%d s%d ling%s'%(x,w[x]['ben_n'],w[x]['zhong_n']+w[x]['yu_n'],w[x]['stem_n'],w[x]['ling_state']) for x in '木火土金水')
    print('%s %s 日主%s(%s) 月支%s'%(tag,ch,ds,dmw,mz))
    print('   七档=%s ratio=%.2f special=%s/%s lq=%s'%(sp['spectrum'],sp['daymaster_ratio'],spp.get('zhuanwang'),spp.get('zhuanwang_state'),(spp.get('liangqi') or {}).get('relation')))
    print('   ',bs)
    print('   primary=%s sec=%s avoid=%s paths=%s'%(ye.get('yongshen_primary'),ye.get('yongshen_secondary'),ye.get('yongshen_avoid'),ye.get('yongshen_paths')))
