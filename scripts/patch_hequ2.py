# -*- coding: utf-8 -*-
# 应期合冲子层之一(严格版): 喜用被天干五合/地支六合合夺 -> av
# 合化真硬条件(滴天髓·合局"来与不来即化与不化"; 子平真诠论合化):
#   紧贴(运干合月/日/时干; 运支合月/日支) + 化神有气(月令旺相/原局本气根/成局)
#   + 被合喜用孤虚(天干虚透无根 ben=0; 地支被双支争合且失令; 日月支孤根 ben<=1 且失令)
# 化气格(special含'化')跳过。只翻 fav->av, 不做合去忌神吉(待命局喜忌修正)。
import io
fp=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(fp,encoding='utf-8').read()
anchor="""LH={frozenset(('子','丑')):'土',frozenset(('寅','亥')):'木',frozenset(('卯','戌')):'火',
    frozenset(('辰','酉')):'金',frozenset(('巳','申')):'水',frozenset(('午','未')):'土'}"""
assert s.count(anchor)==1
func=anchor+"""
WUHE={frozenset(('甲','己')):'土',frozenset(('乙','庚')):'金',frozenset(('丙','辛')):'水',
      frozenset(('丁','壬')):'木',frozenset(('戊','癸')):'火'}
def transit_hequ(p,g,z,tp,tp0,fav,av,special):
    if special and '化' in str(special): return None
    wp0=tp0['wuxing_power']['wuxing_power']
    def ben0(wx): return wp0[wx].get('ben_n',0) or 0
    def ju0(wx): return wp0[wx].get('ju_n',0) or 0
    def ling(wx): return wp0[wx].get('ling_state','')
    def huaqi(H):
        return ling(H) in ('旺','相') or ben0(H)>=1 or ju0(H)>=1
    pgans=[p[k][0] for k in ('year','month','day','hour')]
    pzhis=[p[k][1] for k in ('year','month','day','hour')]
    ZW=BRANCH_WX[z]; SHILING=('囚','死','休')
    # (C) 天干五合: 运干合命局月/日/时干(紧邻,年干远不合化), 喜用干虚透无根被合化
    for idx,b in enumerate(pgans):
        if idx==0: continue
        H=WUHE.get(frozenset((g,b)))
        if not H: continue
        BW=GAN_WX[b]
        if BW in fav and H!=BW and ben0(BW)==0 and huaqi(H):
            return 'av'
    # 地支六合分组
    groups={}
    for idx,b in enumerate(pzhis):
        H=LH.get(frozenset((z,b)))
        if H: groups.setdefault(H,[]).append((idx,b))
    for H,lst in groups.items():
        # (B) 运喜用支被>=2命支争合化, 化神当令旺相, 运支五行失令
        if ZW in fav and H!=ZW and len(lst)>=2 and ling(H) in ('旺','相') and ling(ZW) in SHILING:
            return 'av'
        for idx,b in lst:
            BW=BRANCH_WX[b]
            # (A) 命局日/月紧贴喜用孤根(ben<=1)失令被合化
            if idx in (1,2) and BW in fav and H!=BW and ben0(BW)<=1 and ling(BW) in SHILING and huaqi(H):
                return 'av'
    return None"""
s=s.replace(anchor,func)
anchor2="""        clash=[c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]"""
assert s.count(anchor2)==1
ins="""        _hq=transit_hequ(p,g,z,tp,tp0,fav,av,ye.get('special'))
        if _hq: lc=_hq
        clash=[c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]"""
s=s.replace(anchor2,ins)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched transit_hequ strict')
