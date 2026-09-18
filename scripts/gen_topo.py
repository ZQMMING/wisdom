# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\wuxing_power.py'
s=io.open(p,encoding='utf-8').read()
idx=s.find('def build_spectrum_topology')
assert idx>0
head=s[:idx]

newfunc = '''def build_spectrum_topology(network, wp=None):
    """日主旺衰七档: 连续力量(ratio, 旺相休囚系数)打底 + 原典结构非对称修正.

    成势(shi): 某五行力量聚集, 任一即可(不唯"透干+本气根"):
      (a)透干且本气根 (b)地支>=2本气根(多根成势, 干多不如根重)
      (c)成三合/三会局 (d)当令(旺)且本气根(母旺子相)
    官印相生: 印成势而官杀亦成势, 官杀生印化身, 官杀不计压制(杀印相生/官印双全).
    衰端: 无根失令 ratio 趋零(锚点衰极<=0.14); ratio<0.10 而财官或食伤当令成势=弱极/从弱.
    旺端: 得令+本气重根+印比成势为本; 三会/三根当令为旺极(孤财失令不制, T33会方极强);
          两禄刃当令无财官本气根为太旺; 食伤(我生)顺泄不否定当令重根.
    得时不旺: S3 而财官成势(印不能化) -> 降; 财官两透成党 ratio 低 -> 太衰.
    印成势抬身须 ratio>=0.35, 否则印被当令食伤/财官隔耗(财多身弱/冬金身衰).
    纯结构度量, 不出喜忌/用神/吉凶, 非STRONG/WEAK总裁决; 阈值 # PCT-MARK 以锚点标定.
    """
    facts = network.get('facts', {}) or {}
    pw = wp.get('wuxing_power', {}) if wp else {}
    dm_wx = (wp or {}).get('daymaster_element') or facts.get('daymaster_element') or network.get('daymaster_element')
    yin_wx = SHENG_ME.get(dm_wx)
    ss_wx = SHENG.get(dm_wx); cai_wx = KE.get(dm_wx); gs_wx = KE_ME.get(dm_wx)
    ratio = build_spectrum_from_power(wp)['daymaster_ratio'] if pw else 0.5

    L=1; R=1; A=0; multi=False; self_ju=False; yin_ju=False; yin_ben=0; yin_ling=False; dm_ben=0
    fin_rooted=0; fin_shi=0; fin_stem=0; ss_shi=False; gs_shi=False; opp_ling_fin=False; ss_ling=False
    yin_cheng=False; guan_hua=False; cai_ben=0; bj_stem=0; yin_stem=0; month_wx=None
    if pw:
        dm=pw[dm_wx]; yin=pw[yin_wx] if yin_wx else {}
        ss=pw[ss_wx]; cai=pw[cai_wx]; gs=pw[gs_wx]
        L = 2 if dm.get('ling_state')=='旺' else (1 if (dm.get('ling_state')=='相' or (yin and yin.get('ling_state')=='旺')) else 0)
        R = 2 if dm.get('ben_n',0)>=1 else (1 if (dm.get('zhong_n',0)+dm.get('yu_n',0))>=1 else 0)
        dm_ben=int(dm.get('ben_n',0)); multi=dm_ben>=2; self_ju=dm.get('ju_n',0)>=1
        yin_ju=bool(yin) and yin.get('ju_n',0)>=1
        yin_ben=int(yin.get('ben_n',0)) if yin else 0
        yin_ling=bool(yin) and yin.get('ling_state')=='旺'

        def shi(e):
            if not e: return False
            b=e.get('ben_n',0); t=e.get('stem_n',0); j=e.get('ju_n',0)
            return (t>=1 and b>=1) or b>=2 or j>=1 or (e.get('ling_state')=='旺' and b>=1)
        bj_shi=shi(dm); yin_shi=shi(yin)
        ss_shi=shi(ss); gs_shi=shi(gs); cai_shi=shi(cai)
        A = 2 if (bj_shi or yin_shi) else (1 if (dm.get('stem_n',0)>=1 or (yin and yin.get('stem_n',0)>=1)) else 0)
        fin_rooted = sum(1 for e in (cai,gs) if e.get('ben_n',0)>=1)
        fin_shi = sum(1 for e in (cai,gs) if shi(e))
        fin_stem = int(cai.get('stem_n',0))+int(gs.get('stem_n',0))
        cai_ben = int(cai.get('ben_n',0))
        month_wx=(wp or {}).get('month_element')
        opp_ling_fin = month_wx in (cai_wx,gs_wx)
        ss_ling = (month_wx==ss_wx)
        # 印成势(化官杀/生身); ratio 过低则印被当令食伤财官隔耗, 抬不动身
        yin_cheng = yin_shi and (yin_ben>=2 or yin_ju or (yin_ling and yin_ben>=1)) and ratio>=0.35
        # 官印/杀印相生: 官杀成势而印能"化尽"(印>=2本气, 或印当令有根,
        # 或印本中气根处数比官杀多>=1, 或印成局); 单一印根化当令强官杀不算.
        yin_root_n = int(yin.get('ben_n',0))+int(yin.get('zhong_n',0)) if yin else 0
        gs_root_n = int(gs.get('ben_n',0))+int(gs.get('zhong_n',0))
        yin_can_hua = (int(yin.get('ben_n',0))>=1) and (
            int(yin.get('ben_n',0))>=2 or yin_ling or (yin_root_n >= gs_root_n+1) or yin_ju)
        # 印透干得中余气根(相令受官杀生)而日主多本气根, 亦可化官杀(通根身旺, 杀印相生)
        yin_tou_hua = (int(yin.get('stem_n',0))>=1 and
                       (int(yin.get('zhong_n',0))+int(yin.get('yu_n',0)))>=1 and dm_ben>=2)
        guan_hua = bool(gs_shi) and (yin_can_hua or yin_tou_hua)
        bj_stem = int(dm.get('stem_n',0))
        yin_stem = int(yin.get('stem_n',0))
        fin_rooted_eff = (1 if cai.get('ben_n',0)>=1 else 0) if guan_hua else fin_rooted
        fin_shi_eff = (1 if cai_shi else 0) if guan_hua else fin_shi

        if self_ju:
            S=3
        elif (L==2 and R==2) or (R==2 and (bj_shi or yin_shi)):
            S=3
        elif (yin_cheng or (guan_hua and R>=2)) and (R>=1 or yin_ben>=2 or yin_ling):
            S=3
        elif R==2 or (L>=1 and R>=1) or (L==2 and A>=1) or (yin_cheng):
            S=2
        elif R==0 and not (bj_shi or yin_shi):
            S=0
        else:
            S=1
    else:
        S=1; fin_rooted_eff=fin_rooted; fin_shi_eff=fin_shi

    # ---- 衰极(ratio 主轴 + 无根/当令成势结构) ----
    if ratio < 0.07:
        spec='衰极'
    elif ratio < 0.10 and ((opp_ling_fin and fin_shi>=1) or (ss_ling and ss_shi)):
        spec='衰极'   # 占比极低 + 财官当令成势(弱极) 或 食伤当令成势(从儿/从弱, 孤根被泄)
    elif R==0 and fin_shi>=2 and ratio<0.20:
        spec='衰极'   # 无根 + 财官成势两党
    elif R==0 and fin_rooted>=1 and opp_ling_fin and ratio<0.16:
        spec='衰极'   # 无根 + 财官当令得根
    elif R<=1 and opp_ling_fin and fin_shi>=1 and ratio<0.26:
        spec='太衰'   # 仅中余轻根 + 财官当令成势, 虚透比劫无力(干多不如根重)
    elif ratio < 0.18 or (R==0 and (fin_shi>=1 or (ss_shi and L==0))):
        spec='太衰'
    # ---- 旺极: 三会本方(会方极强, 归化后三根, T33, 不受月令失令限制) ----
    elif S==3 and self_ju and dm_ben>=3 and fin_rooted_eff<=1:
        spec='旺极'
    # ---- 旺极: 三根当令(孤财失令不制); 得令重根+印多根; 印成方生身 ----
    elif S==3 and dm_ben>=3 and L==2 and fin_rooted_eff<=1:
        spec='旺极'
    elif S==3 and fin_rooted_eff==0 and dm_ben>=2 and L==2 and yin_ben>=2:
        spec='旺极'   # 得令两本气根 + 印多根(两长生逢禄旺, 木火/水木成势)
    elif S==3 and fin_rooted_eff==0 and (yin_ju or yin_ben>=3) and ratio>=0.85:
        spec='旺极'   # 印成方/三根生身(水旺木坚)
    # ---- 太旺: 两禄刃当令无制 / 本方局 / 成势无财官本气根 ----
    elif S==3 and fin_rooted_eff==0 and multi and L==2:
        spec='太旺'
    elif S==3 and fin_rooted_eff==0 and self_ju:
        spec='太旺'
    elif S==3 and fin_rooted_eff==0 and (multi or ratio>=0.78 or yin_cheng):
        spec='太旺'
    elif S==3 and fin_rooted_eff<=1 and ratio>=0.70 and (multi or self_ju or yin_cheng or A==2):
        spec='太旺'
    # ---- 官印/杀印相生: 官杀被旺印化、日主有本气根(或印>=2本气且比劫透)受生, 财轻不当令则身旺 ----
    elif S==3 and guan_hua and (R>=2 or (yin_ben>=2 and bj_stem>=1)) and cai_ben<2 and month_wx!=cai_wx:
        spec='旺'
    # ---- 得时不旺(S3 而财官成势, 印不能化) ----
    elif S==3 and fin_shi_eff>=1 and fin_stem>=2 and ratio<0.45:
        spec='太衰'   # 得令而财官两透成党、占比压身(财多身弱/虚弱极)
    elif S==3 and fin_shi_eff>=1 and ratio<0.45:
        spec='衰'
    elif S==3 and (fin_shi_eff>=2 or (fin_shi_eff>=1 and fin_stem>=2)):
        spec='中和' if ratio<0.56 else '旺'
    elif S==3 and fin_shi_eff>=1 and ratio<0.55:
        spec='中和'
    # ---- 当令有本气根、财官虚浮无本气根、比劫/印透助: 身旺能任(身旺以财为子); 得时不旺降级已在前 ----
    elif S==3 and L==2 and dm_ben>=1 and fin_rooted_eff==0 and (bj_stem>=1 or yin_stem>=1) and ratio>=0.30:
        spec='旺'
    elif S==3:
        spec='旺' if ratio>=0.40 else '中和'
    elif S==2 and fin_rooted_eff<=1 and ratio>=0.55:
        spec='旺'
    elif S==2 and fin_shi_eff>=1 and ratio<0.40:
        spec='衰'
    # ---- 中段(ratio 分位; # PCT-MARK) ----
    elif ratio>=0.72:
        spec='旺'
    elif ratio>=0.53:
        spec='中和' if ratio<0.60 else '旺'
    elif ratio>=0.35:
        spec='中和' if ratio>=0.42 else '衰'
    elif ratio>=0.18:
        spec='衰'
    else:
        spec='太衰'
    if R==0 and spec in ('旺极','太旺'):
        spec='旺'

    return {
        'daymaster_element': dm_wx,
        'daymaster_ratio': round(ratio,3),
        'self_factors': {'月令':{2:'得令',1:'相令',0:'失令'}.get(L),'L':L,
                         '根':{2:'本气重根',1:'中余轻根',0:'无根'}.get(R),'R':R,
                         '党':{2:'印比成势',1:'透而根虚',0:'无印比'}.get(A),'A':A,
                         '本气根数':dm_ben,'多支本气根':multi,'本方局':self_ju,
                         '印成势':bool(pw) and yin_cheng,'官印相生':bool(pw) and guan_hua,
                         '支持档':'S%d'%S},
        'opposing_factors': {'财官有本气根类数':fin_rooted,'财官成势类数':fin_shi,
                             '有效压制类数(印化后)':fin_rooted_eff,'财官透干数':fin_stem,
                             '食伤成势(泄秀)':ss_shi,'财官当令':opp_ling_fin,'食伤当令':ss_ling},
        'spectrum': spec,
        'judgment_status': 'TOPOLOGY_STRUCTURE_ONLY',
        'boundary_note': 'ratio打底+原典结构非对称; 成势=透根/多根/成局/当令; 三会三根当令为旺极, 两刃当令无制为太旺; 官印相生官杀化印不压身; 印成势须ratio>=0.35; 食伤顺泄不否定重根; 得时不旺财官成党则降; 不出喜忌/用神/吉凶, 非STRONG/WEAK总裁决; # PCT-MARK 锚点标定',
    }
'''
io.open(p,'w',encoding='utf-8',newline='').write(head+newfunc)
print('rewritten v3, len=',len(head+newfunc))
