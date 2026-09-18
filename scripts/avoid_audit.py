# -*- coding: utf-8 -*-
"""忌神(avoid)自洽审计:
[致命] primary用神自己落入avoid, 必须0;
[污染] secondary喜神与avoid交集(撒网过宽/S-A未互斥), 列样例;
(参考)粗扶抑方向: 旺忌克泄耗/衰忌生扶多为相神保护(印化杀忌财坏印等), 仅计数。"""
import sys, csv
sys.path.insert(0,'.'); sys.path.insert(0,'scripts')
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
rows=list(csv.DictReader(open('scripts/dts_513_output.csv',encoding='utf-8-sig')))
SHENG={'木':'火','火':'土','土':'金','金':'水','水':'木'}; KE={'木':'土','土':'水','水':'火','火':'金','金':'木'}
def inv(d,v):
    for k,x in d.items():
        if x==v: return k
WANG={'旺','太旺','旺极'}; SHUAI={'衰','太衰','衰极'}
def gp(c):
    g=list(c.replace(' ',''));return {p:[g[i*2],g[i*2+1]] for i,p in enumerate(('year','month','day','hour'))}
_cache={}
def engine(ch):
    if ch in _cache: return _cache[ch]
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
    _cache[ch]=(ds,WUXING[ds],sp['spectrum'],spp,ye); return _cache[ch]
prim_bad=[]; inter=[]; dir_bad=[]; noavoid=0; n=0
for r in rows:
    ch=r['chart']
    try: ds,dmw,tier,spp,ye=engine(ch)
    except Exception: continue
    n+=1
    prim=ye.get('yongshen_primary') or ''
    sec=set(ye.get('yongshen_secondary') or [])
    av=set(ye.get('yongshen_avoid') or [])
    if not av: noavoid+=1
    if prim and prim in av: prim_bad.append((ch,tier,prim,sorted(av)))
    so=sec & av
    if so: inter.append((ch,tier,prim,sorted(sec),sorted(av),sorted(so)))
    special=bool(spp.get('cong_type') or spp.get('zhuanwang') or spp.get('hua_qi') or spp.get('liangqi'))
    if not special:
        yw=inv(SHENG,dmw); shengfu={yw,dmw}
        sxh={SHENG[dmw],KE[dmw],inv(KE,dmw)}
        if tier in WANG and (av & sxh): dir_bad.append((ch,tier,'旺忌克泄耗',sorted(av),prim,sorted(av&sxh)))
        if tier in SHUAI and (av & shengfu): dir_bad.append((ch,tier,'衰忌生扶',sorted(av),prim,sorted(av&shengfu)))
print(f'审计 {n} 例; 无忌神输出 {noavoid}')
print(f'[致命] primary落入avoid: {len(prim_bad)}')
for x in prim_bad: print('  ',x)
print(f'[污染] secondary与avoid交集: {len(inter)}')
for x in inter[:30]: print('  ',x)
print(f'(参考)粗扶抑方向疑似(多为相神保护): {len(dir_bad)}')
