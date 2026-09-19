# -*- coding: utf-8 -*-
import io,sys
sys.path.insert(0,r'D:\shuntian-ziping-p0\scripts')
src=io.open(r'D:\shuntian-ziping-p0\scripts\dayun_align.py',encoding='utf-8').read()
g={'__name__':'__probe__'}
exec(compile(src,'dayun_align','exec'),g)
cases=g['cases']; dislist=g['dislist']
# 复用 dayun_align 的 import 与孤岛链
import engines.common.special_pattern as _spm
from engines.common.special_pattern import build_special_patterns
from engines.common.wuxing_power import build_spectrum_topology
from engines.common.climate_structure import build_climate_structure
seen=set()
for row in dislist:
    li,ch,gz,lc,gw,zw,ju,v,prim,fav,av,blob,clash=row
    if ch in seen: continue
    seen.add(ch)
    fp=None
    for l2,f2,dy2,t2 in cases:
        if ''.join(a+b for a,b in f2)==ch: fp=f2; break
    if not fp: continue
    p={'year':list(fp[0]),'month':list(fp[1]),'day':list(fp[2]),'hour':list(fp[3])}
    try:
        pc,f,ye,tp0=g['engine'](fp)
        th=g['build_tian_he'](p,f)
        cls=build_climate_structure(p,f,th)
        spp=build_special_patterns(p,f,tp0,th,cls)
        net=g['build_power_network'](g['build_power_structure'](p),g['build_root_classes'](p,{p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}),g['build_tou_cang'](f),g['build_wang_xiang'](f,f['day_stem']),g['build_root_relations'](g['build_root_classes'](p,{p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}),f['combination_facts']),g['build_two_side'](g['build_root_classes'](p,{p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}),g['build_tou_cang'](f),g['build_root_relations'](g['build_root_classes'](p,{p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}),f['combination_facts'])),branch_tier=g['build_branch_tiers'](p,f),tian_he=th,facts=f)
        net.setdefault('facts',{})['daymaster_element']=g['WUXING'][f['day_stem']]
        sp=build_spectrum_topology(net,tp0)
        ct=spp.get('cong_type'); cs=spp.get('cong_state'); zw=spp.get('zhuanwang'); zs=spp.get('zhuanwang_state')
        print('L%d %s | 七档%s | cong=%s/%s zw=%s/%s | paths=%s | P=%s fav=%s av=%s'%(
            li+1,ch,sp['spectrum'],ct,cs,zw,zs,'/'.join(ye.get('yongshen_paths') or []),prim,''.join(fav),''.join(av)))
    except Exception as e:
        print('L%d %s ERR %s'%(li+1,ch,e))
