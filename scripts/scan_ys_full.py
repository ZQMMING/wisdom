# -*- coding: utf-8 -*-
import sys, csv; sys.path.insert(0,'.'); sys.path.insert(0,'scripts')
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
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.special_pattern import build_special_patterns
from engines.common.yongshen_engine import build_yongshen_engine
rows=list(csv.DictReader(open('scripts/dts_513_output.csv',encoding='utf-8-sig')))
def gp(c):
    g=list(c.replace(' ',''));return {p:[g[i*2],g[i*2+1]] for i,p in enumerate(('year','month','day','hour'))}
lq=[]; empty=[]; err=0; n=0
for r in rows:
    ch=r['chart']; n+=1
    try:
        p=gp(ch); f=l0build(p); ds=ch[4]
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
        if spp.get('liangqi'): lq.append((ch,spp['liangqi']['name'],spp['liangqi'].get('xiu'),sp.get('spectrum'),ye['candidate_wuxing']))
        if not ye['candidate_wuxing']: empty.append((ch,sp.get('spectrum'),spp.get('zhuanwang'),spp.get('cong_type')))
    except Exception as e:
        err+=1; print('ERR',ch,repr(e)[:80])
print(f'全量 {n} 异常 {err}; 两气成象 {len(lq)} 例; 用神候选为空 {len(empty)} 例')
print('--- 两气成象名单 ---')
for x in lq: print(' ',x)
print('--- 候选为空 ---')
for x in empty[:30]: print(' ',x)
