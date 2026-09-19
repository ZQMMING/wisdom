# -*- coding: utf-8 -*-
# 众寡量化(只读): 对全部有断语运步, 运干/支落fav者, 记录该喜用复合total/本气/生源/本方total/tier,
# 对比 fav实凶(虚神犯旺) vs fav实吉(真用神) 的众寡比值分布, 找可分阈值(#PCT-MARK), 不case拟合。
import io,sys,statistics
sys.path.insert(0,r'D:\shuntian-ziping-p0\scripts')
src=io.open(r'D:\shuntian-ziping-p0\scripts\dayun_align.py',encoding='utf-8').read()
g={'__name__':'__probe__'}
exec(compile(src,'dayun_align','exec'),g)
cases=g['cases']; ept=g['element_power_tier']; btp=g['build_transit_power']
SHENG=g['SHENG']; KE=g['KE']; GAN_WX=g['GAN_WX']; BRANCH_WX=g['BRANCH_WX']; WX=g.get('WUXING','木火土金水')
SME={v:k for k,v in SHENG.items()}; KME={v:k for k,v in KE.items()}
def cls_w(w,fav,av): return 'fav' if w in fav else ('av' if w in av else 'xian')
def tot(wp,w): return float((wp['wuxing_power']['wuxing_power'][w] or {}).get('total',0) or 0)
def ben(wp,w): return int((wp['wuxing_power']['wuxing_power'][w] or {}).get('ben_n',0) or 0)
rows=[]
for li,fp,dy,txt in cases:
    if len(dy)<4: continue
    try: p,f,ye,tp0=g['engine'](fp)
    except Exception: continue
    dmw=f['day_stem']
    dmwx=GAN_WX[f['day_stem']]
    prim=ye.get('yongshen_primary') or ''
    fav=set([prim])|set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
    av=set(ye.get('yongshen_avoid') or [])
    paths='/'.join(ye.get('yongshen_paths') or [])
    for gz in dy:
        g0,z=gz[0],gz[1]; v,blob=g['luck_verdict'](txt,g0,z)
        if blob and blob.lstrip().startswith('【原注】'): v=None
        if not v or v in ('hun','lao'): continue
        gw,zw=GAN_WX[g0],BRANCH_WX[z]
        gc,zc=cls_w(gw,fav,av),cls_w(zw,fav,av)
        tp=btp(p,[list(gz)])
        benfang=dmwx+'+'+SME[dmwx]
        bf=tot(tp,dmwx)+tot(tp,SME[dmwx])   # 本方=比劫+印(复合)
        for role,w in (('干',gw),('支',zw)):
            if cls_w(w,fav,av)!='fav': continue
            wt=tot(tp,w); wb=ben(tp,w); src=tot(tp,SME[w]); ke_w=tot(tp,KME[w])
            tier=ept(tp['wuxing_power'],w)['tier']
            rows.append((v,role,paths,w,round(wt,1),wb,round(src,1),round(bf,1),round(ke_w,1),tier,
                         round(wt/max(bf,0.1),2),li,gz))
def summ(sub,name):
    if not sub: print(name,'n=0'); return
    r=[x[10] for x in sub]; tt=[x[4] for x in sub]; bb=[x[5] for x in sub]
    print('%s n=%d 比值(w/本方) min%.2f 中位%.2f max%.2f | w_total中位%.1f | w有本气根占比%.2f'%(
        name,len(sub),min(r),statistics.median(r),max(r),statistics.median(tt),
        sum(1 for x in sub if x[5]>=1)/len(sub)))
fx=[x for x in rows if x[0]=='xiong']; fj=[x for x in rows if x[0]=='ji']
summ(fx,'FAV实凶(虚犯旺?)')
summ(fj,'FAV实吉(真用神)')
print('\n--- FAV实凶明细(比值升序前30) ---')
for x in sorted(fx,key=lambda a:a[10])[:30]:
    print('L%-5d %s %s%s P%s %s w=%s wt%.1f b%d 生源%.1f 本方%.1f 克w%.1f t%d 比%.2f'%(
        x[11],x[12],x[1],x[0],x[2][:14],'',x[3],x[4],x[5],x[6],x[7],x[8],x[9],x[10]))
