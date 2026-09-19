# -*- coding: utf-8 -*-
import io,sys
sys.path.insert(0,r'D:\shuntian-ziping-p0\scripts')
src=io.open(r'D:\shuntian-ziping-p0\scripts\dayun_align.py',encoding='utf-8').read()
g={'__name__':'__probe__'}
exec(compile(src,'dayun_align','exec'),g)
cases=g['cases']; dislist=g['dislist']; ept=g['element_power_tier']; btp=g['build_transit_power']
WX='木火土金水'
targets={180,190,228,244,250,300,516,605,620,623,632,647,695,752,852,933,965,1013,1016,
         1077,1265,1287,1322,1606,1618,1656,1781,1808,1814,1827,2161}
hdr=set()
for row in dislist:
    li,ch,gz,lc,gw,zw,ju,v,prim,fav,av,blob,clash=row
    if li not in targets: continue
    fp=None
    for l2,f2,dy2,t2 in cases:
        if ''.join(a+b for a,b in f2)==ch: fp=f2; break
    if not fp: continue
    p,f,ye,tp0=g['engine'](fp)
    if li not in hdr:
        hdr.add(li)
        def ti(wp,w):
            d=wp['wuxing_power']['wuxing_power'][w]; return 't%d(b%d z%d y%d s%d j%d)'%(ept(wp['wuxing_power'],w)['tier'],d.get('ben_n',0),d.get('zhong_n',0),d.get('yu_n',0),d.get('stem_n',0),d.get('ju_n',0))
        print('@@L%d %s 七档%s paths=%s'%(li,ch,ye.get('spectrum_tier'),'/'.join(ye.get('yongshen_paths') or [])))
        print('@@   P=%s fav=%s av=%s'%(prim,''.join(fav),''.join(av)))
        print('@@   '+' '.join(w+ti(tp0,w) for w in WX))
    tp=btp(p,[list(gz)])
    def t1(w):
        return ept(tp['wuxing_power'],w)['tier']
    print('@@    运%s 判%s 原%s | %s t%d->%d ; %s t%d->%d | %s'%(
        gz,lc,v,gw,ept(tp0['wuxing_power'],gw)['tier'],t1(gw),
        zw,ept(tp0['wuxing_power'],zw)['tier'],t1(zw),clash))
