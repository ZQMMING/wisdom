# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\wuxing_power.py'
s=io.open(p,encoding='utf-8').read()
idx=s.find('def build_spectrum_topology')
assert idx>0
head=s[:idx]

newfunc = '''def build_spectrum_topology(network, wp=None):
    """日主旺衰七档: 连续力量(ratio, 旺相休囚系数)打底 + 原典结构非对称修正.

    衰端: 日主无根失令则 ratio 趋零, 以 ratio 为主(锚点衰极 ratio<=0.14).
    旺端: 以 得令+本气重根+印比真党(S档)为本; 压制只算 财+官杀(克耗我者),
          食伤(我生)为泄秀, 不否定当令重根(午月两刃虽食伤重仍太旺).
    得时不旺: S3 而财官杀成党 -> 降为旺/中和.
    纯结构度量, 不输出喜忌/用神/吉凶, 非STRONG/WEAK总裁决; 阈值 # PCT-MARK 以干净锚点标定.
    """
    facts = network.get('facts', {}) or {}
    pw = wp.get('wuxing_power', {}) if wp else {}
    dm_wx = (wp or {}).get('daymaster_element') or facts.get('daymaster_element') or network.get('daymaster_element')
    yin_wx = SHENG_ME.get(dm_wx)
    ss_wx = SHENG.get(dm_wx); cai_wx = KE.get(dm_wx); gs_wx = KE_ME.get(dm_wx)
    ratio = build_spectrum_from_power(wp)['daymaster_ratio'] if pw else 0.5

    # ---- 要素(默认中性, wp缺失时) ----
    L=1; R=1; A=0; multi_heavy=False; self_ju=False
    fin_parties=0; fin_rooted=0; fin_present=0; fin_stem=0; fin_heavy=False; ss_party=False; ss_stem=0; opp_ling_fin=False
    if pw:
        dm_e=pw[dm_wx]; yin_e=pw[yin_wx] if yin_wx else {}
        ss_e=pw[ss_wx]; cai_e=pw[cai_wx]; gs_e=pw[gs_wx]
        L = 2 if dm_e.get('ling_state')=='旺' else (1 if (dm_e.get('ling_state')=='相' or (yin_e and yin_e.get('ling_state')=='旺')) else 0)
        R = 2 if dm_e.get('ben_n',0)>=1 else (1 if (dm_e.get('zhong_n',0)+dm_e.get('yu_n',0))>=1 else 0)
        multi_heavy = dm_e.get('ben_n',0)>=2
        self_ju = dm_e.get('ju_n',0)>=1
        def _tp(e): return bool(e and e.get('stem_n',0)>=1 and e.get('ben_n',0)>=1)
        bj_party=_tp(dm_e); yin_party=_tp(yin_e)
        bj_stem=dm_e.get('stem_n',0)>=1; yin_stem=bool(yin_e and yin_e.get('stem_n',0)>=1)
        A = 2 if (bj_party or yin_party) else (1 if (bj_stem or yin_stem) else 0)
        fin=[cai_e,gs_e]   # 主压力: 财(我克)+官杀(克我); 食伤泄秀另计
        fin_parties=sum(1 for e in fin if _tp(e))                 # 真党: 透干且本气根(有力)
        fin_rooted=sum(1 for e in fin if e.get('ben_n',0)>=1)     # 有本气根(干多不如根重; 制化以根为重)
        fin_present=sum(1 for e in fin if e.get('stem_n',0)>=1 or e.get('ben_n',0)>=1)  # 显现: 透或本气根
        fin_stem=sum(int(e.get('stem_n',0)) for e in fin)
        fin_heavy=any(_tp(e) and e.get('stem_n',0)>=2 for e in fin)
        ss_party=_tp(ss_e); ss_stem=int(ss_e.get('stem_n',0))
        month_wx=(wp or {}).get('month_element')
        opp_ling_fin = month_wx in (cai_wx,gs_wx)

    # 日主支持档
    if (L==2 and R==2) or (R==2 and A==2 and (L>=1 or multi_heavy or self_ju)):
        S=3
    elif R==2 or (L>=1 and R>=1 and A>=1) or (L==2 and A>=1):
        S=2
    elif R==0 and A==0:
        S=0
    else:
        S=1

    # ---- 衰端(ratio 分位主轴, 无根财官成党结构兜底) ----
    if ratio < 0.07:
        spec='衰极'
    elif R==0 and fin_parties>=2 and ratio<0.20:
        spec='衰极'   # 无根 + 财官成党(如辛亥火 申辰官杀财两党)
    elif ratio < 0.18 or (R==0 and (fin_parties>=1 or (ss_party and L==0))):
        spec='太衰'
    # ---- 旺端(结构 S档 × 财官杀压力; 食伤泄秀不否定重根) ----
    elif S==3 and fin_rooted==0 and (multi_heavy or self_ju) and ratio>=0.86 and not ss_party:
        spec='旺极'
    elif S==3 and fin_rooted==0 and (multi_heavy or self_ju or ratio>=0.78):
        spec='太旺'   # 财官无本气根(虚浮/藏余气无力制化) + 当令重根成势; 食伤泄秀不否定
    elif S==3 and fin_rooted<=1 and ratio>=0.82 and (multi_heavy or self_ju or A==2):
        spec='太旺'   # 财官仅一本气根而日主占比压倒(卯刃水印而财坐库)
    elif S==3 and fin_parties>=2:
        spec='中和' if ratio<0.56 else '旺'   # 得时不旺: 财官透根成党
    elif S==3:
        spec='旺' if ratio>=0.40 else '中和'
    elif S==2 and fin_parties<=1 and ratio>=0.56:
        spec='旺'
    elif S==2 and fin_parties>=2 and ratio<0.40:
        spec='衰'
    # ---- 中段(ratio 分位主轴; # PCT-MARK 阈值=p5/p20/p40/p60/p80/p95) ----
    elif ratio>=0.73:
        spec='旺'
    elif ratio>=0.56:
        spec='中和' if ratio<0.60 else '旺'
    elif ratio>=0.33:
        spec='中和' if ratio>=0.40 else '衰'
    elif ratio>=0.18:
        spec='衰'
    else:
        spec='太衰'
    # 无本气根不得判旺极/太旺
    if R==0 and spec in ('旺极','太旺'):
        spec='旺'

    return {
        'daymaster_element': dm_wx,
        'daymaster_ratio': round(ratio,3),
        'self_factors': {'月令':{2:'得令',1:'相令',0:'失令'}.get(L),'L':L,
                         '根':{2:'本气重根',1:'中余轻根',0:'无根'}.get(R),'R':R,
                         '党':{2:'印比真党',1:'印比透无本气根',0:'无印比透'}.get(A),'A':A,
                         '多支本气根':multi_heavy,'本方局':self_ju,'支持档':'S%d'%S},
        'opposing_factors': {'财官杀真党类数':fin_parties,'财官杀透干数':fin_stem,
                             '财官一党多透':fin_heavy,'食伤真党(泄秀)':ss_party,
                             '财官当令':opp_ling_fin},
        'spectrum': spec,
        'judgment_status': 'TOPOLOGY_STRUCTURE_ONLY',
        'boundary_note': 'ratio(旺相休囚系数)打底+原典结构非对称修正; 旺端看令/本气根/印比党且唯财官杀为压制, 食伤泄秀不否定重根; 衰端无根失令ratio趋零; 不输出喜忌/用神/吉凶, 非STRONG/WEAK总裁决; # PCT-MARK 阈值以干净锚点标定',
    }
'''
io.open(p,'w',encoding='utf-8',newline='').write(head+newfunc)
print('rewritten len=',len(head+newfunc))
