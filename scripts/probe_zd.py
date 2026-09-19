# -*- coding: utf-8 -*-
# 列出命中"身衰支财官成势主导"规则的全部步: 运干十神角色/干tier/支tier/原文v, 定收窄判据。
import io,sys
sys.path.insert(0,r'D:\shuntian-ziping-p0\scripts')
src=io.open(r'D:\shuntian-ziping-p0\scripts\dayun_align.py',encoding='utf-8').read()
g={'__name__':'__probe__'}; exec(compile(src,'dayun_align','exec'),g)
cases=g['cases']; ept=g['element_power_tier']; btp=g['build_transit_power']
SHENG=g['SHENG']; KE=g['KE']; GAN_WX=g['GAN_WX']; BRANCH_WX=g['BRANCH_WX']
SME={v:k for k,v in SHENG.items()}; KME={v:k for k,v in KE.items()}
def cls_w(w,fav,av): return 'fav' if w in fav else ('av' if w in av else 'xian')
for li,fp,dy,txt in cases:
    if len(dy)<4: continue
    try: p,f,ye,tp0=g['engine'](fp)
    except Exception: continue
    dm=f['day_stem']; dmw=GAN_WX[dm]; _spec=ye.get('spectrum_tier') or ''
    prim=ye.get('yongshen_primary') or ''
    fav=set([prim])|set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
    av=set(ye.get('yongshen_avoid') or [])
    pp='/'.join(ye.get('yongshen_paths') or [])
    for gz in dy:
        g0,z=gz[0],gz[1]; v,blob=g['luck_verdict'](txt,g0,z)
        if blob and blob.lstrip().startswith('【原注】'): v=None
        if not v or v in ('hun','lao'): continue
        gw,zw=GAN_WX[g0],BRANCH_WX[z]; gc,zc=cls_w(gw,fav,av),cls_w(zw,fav,av)
        if not (_spec in ('衰极','太衰','衰') and gc=='fav' and zc!='fav'): continue
        tp=btp(p,[list(gz)])
        if not (zw in (KE.get(dmw),KME.get(dmw)) and not any(x in pp for x in ('CONG','ZHUANWANG','HUA_QI','LIANGQI'))
                and ept(tp['wuxing_power'],zw)['tier']>=2 and ept(tp['wuxing_power'],gw)['tier']<=1): continue
        role={dmw:'比劫',SME[dmw]:'印',SHENG[dmw]:'食伤',KE[dmw]:'财',KME[dmw]:'官杀'}.get(gw,'?')
        print('L%-5d %s 七档%s v=%s | 干%s(%s)t%d 支%s(%s)t%d | %s'%(
            li,gz,_spec,v,g0,role,ept(tp['wuxing_power'],gw)['tier'],z,
            {KE[dmw]:'财',KME[dmw]:'官杀'}.get(zw,'?'),ept(tp['wuxing_power'],zw)['tier'],
            (blob or '')[:34]))
