# -*- coding: utf-8 -*-
# 刀: 应期合冲子层之一 —— 喜用被天干五合/地支六合合夺 -> av(凶)
# 原典: 《滴天髓·合局第五十四》"羁绊喜神之合...喜神合而化不来,反羁绊贪恋而无用";
#       合去喜用凶; 六合紧贴(日/月支)优先于隔位三会/三合(L1815子丑合闭子水,亥子丑三会不成)。
# 保守单向: 只把"喜用被合化夺走"翻 av; 合去忌神吉/化喜成势待命局喜忌修正后另做。
# 化气格(special含'化')不走普通合夺(化气格喜忌另算)。
import io
fp=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(fp,encoding='utf-8').read()

# 1) 在 LH 表后加 WUHE 表 + transit_hequ 函数
anchor="""LH={frozenset(('子','丑')):'土',frozenset(('寅','亥')):'木',frozenset(('卯','戌')):'火',
    frozenset(('辰','酉')):'金',frozenset(('巳','申')):'水',frozenset(('午','未')):'土'}"""
assert s.count(anchor)==1, s.count(anchor)
func=anchor+"""
WUHE={frozenset(('甲','己')):'土',frozenset(('乙','庚')):'金',frozenset(('丙','辛')):'水',
      frozenset(('丁','壬')):'木',frozenset(('戊','癸')):'火'}
def transit_hequ(p,g,z,tp,tp0,fav,av,special):
    # 喜用被合夺 -> 'av'; 不成立 None。化气格跳过。
    if special and '化' in str(special): return None
    wpt=tp['wuxing_power']; wp0=tp0['wuxing_power']['wuxing_power']
    def tier(H):
        try: return element_power_tier(wpt,H)['tier']
        except Exception: return 0
    def ben0(wx): return wp0[wx].get('ben_n',0) or 0
    def ling(wx):
        return wp0[wx].get('ling_state','')
    pgans=[p[k][0] for k in ('year','month','day','hour')]
    pzhis=[p[k][1] for k in ('year','month','day','hour')]
    GW=GAN_WX[g]; ZW=BRANCH_WX[z]
    SHILING=('囚','死','休')
    # (C) 天干五合: 运干 g 合命局干
    for b in pgans:
        H=WUHE.get(frozenset((g,b)))
        if not H: continue
        BW=GAN_WX[b]
        hit=False
        if BW in fav and H!=BW and ben0(BW)==0 and tier(H)>=1:
            hit=True   # 命局喜用干虚透无根被合去(L696 丁壬合去壬财)
        elif GW in fav and H!=GW and tier(H)>=1 and (tier(GW)<=1 or ling(GW) in SHILING):
            hit=True   # 运喜用干被命局合化,立不住
        if hit: return 'av'
    # (A)(B) 地支六合: 运支 z 合命局支
    for idx,b in enumerate(pzhis):
        H=LH.get(frozenset((z,b)))
        if not H: continue
        BW=BRANCH_WX[b]
        tight=idx in (1,2)
        heshen=sum(1 for q in pzhis if LH.get(frozenset((z,q)))==H)  # 命局能与运支合化同神的支数(争合/合势)
        # (A) 命局紧贴(日/月)喜用支被运合去,化神有气、喜用复合孤弱
        if tight and BW in fav and H!=BW and tier(H)>=1 and tier(BW)<=1:
            return 'av'
        # (B) 运喜用支被命局合化夺: 争合(合神>=2)或化神成势,且运支五行失令/复合立不住
        if ZW in fav and H!=ZW and (heshen>=2 or tier(H)>=2) and (ling(ZW) in SHILING or tier(ZW)<=1):
            return 'av'
    return None"""
s=s.replace(anchor,func)

# 2) 在 lc 组合判定块之后、clash 行之前插入合夺覆盖(合夺喜用优先级最高,可覆盖 new_hs 的 fav)
anchor2="""        clash=[c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]"""
assert s.count(anchor2)==1, s.count(anchor2)
ins="""        _hq=transit_hequ(p,g,z,tp,tp0,fav,av,ye.get('special'))
        if _hq: lc=_hq
        clash=[c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]"""
s=s.replace(anchor2,ins)

io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched transit_hequ')
