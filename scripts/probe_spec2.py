# -*- coding: utf-8 -*-
import io,sys
sys.path.insert(0,r'D:\shuntian-ziping-p0\scripts')
src=io.open(r'D:\shuntian-ziping-p0\scripts\dayun_align.py',encoding='utf-8').read()
g={'__name__':'__probe__'}
exec(compile(src,'dayun_align','exec'),g)
cases=g['cases']; dislist=g['dislist']
ept=g['element_power_tier']
seen=set()
for row in dislist:
    li,ch,gz,lc,gw,zw,ju,v,prim,fav,av,blob,clash=row
    if ch in seen: continue
    seen.add(ch)
    fp=None
    for l2,f2,dy2,t2 in cases:
        if ''.join(a+b for a,b in f2)==ch: fp=f2; break
    if not fp: continue
    try:
        p,f,ye,tp0=g['engine'](fp)
        spc=ye.get('special')
        def tinfo(wx):
            d=tp0['wuxing_power']['wuxing_power'][wx]
            t=ept(tp0['wuxing_power'],wx)['tier']
            return '%s:t%d b%d z%d y%d s%d j%d'%(wx,t,d.get('ben_n',0),d.get('zhong_n',0),d.get('yu_n',0),d.get('stem_n',0),d.get('ju_n',0))
        dmw=g['WUXING'][f['day_stem']]
        print('L%d %s dm=%s 七档%s'%(li+1,ch,dmw,ye.get('spectrum_tier')))
        print('   special=%s paths=%s'%(spc,'/'.join(ye.get('yongshen_paths') or [])))
        print('   P=%s fav=%s av=%s'%(prim,''.join(fav),''.join(av)))
        print('  '+' | '.join(tinfo(w) for w in '木火土金水'))
    except Exception as e:
        import traceback; print('L%d %s ERR'%(li+1,ch),e)
