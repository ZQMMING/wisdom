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
    # 日主重根/轻根统一取 root_class(原典T4 长生禄旺=重根, T5 墓库余气=轻根, T42阴长生=明根约余气)
    _rcd = ((network.get('dimensions', {}).get('ROOT', {}) or {}).get('root_class_detail', {})) or {}
    dm_heavy = sum(1 for v in _rcd.values() if isinstance(v, str) and v.startswith('HEAVY'))
    dm_has_lu = any(isinstance(v, str) and v in ('HEAVY_LU','HEAVY_WANG','HEAVY_REN','HEAVY_BEN')
                    for v in _rcd.values())
    dm_light_n = sum(1 for v in _rcd.values() if isinstance(v, str) and (v.startswith('LIGHT') or v.startswith('SPECIAL')))

    L=1; R=1; A=0; multi=False; self_ju=False; yin_ju=False; yin_ben=0; yin_ling=False; dm_ben=0
    fin_rooted=0; fin_shi=0; fin_stem=0; ss_shi=False; gs_shi=False; opp_ling_fin=False; ss_ling=False
    yin_cheng=False; guan_hua=False; cai_ben=0; bj_stem=0; yin_stem=0; month_wx=None; lu_chong=False
    if pw:
        dm=pw[dm_wx]; yin=pw[yin_wx] if yin_wx else {}
        ss=pw[ss_wx]; cai=pw[cai_wx]; gs=pw[gs_wx]
        L = 2 if dm.get('ling_state')=='旺' else (1 if (dm.get('ling_state')=='相' or (yin and yin.get('ling_state')=='旺')) else 0)
        R = 2 if dm.get('ben_n',0)>=1 else (1 if (dm.get('zhong_n',0)+dm.get('yu_n',0))>=1 else 0)
        dm_ben=int(dm.get('ben_n',0)); multi=dm_ben>=2; self_ju=dm.get('ju_n',0)>=1
        dm_banhe=int(dm.get('banhe_n',0))
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
        # T30 禄刃/本气硬根支遭六冲、我非当令(月令囚死): 旺者冲衰衰者拔, 禄根被冲伤; 四库土冲反旺除外
        _cf0 = facts.get('combination_facts',{}) if isinstance(facts,dict) else {}
        _chong0 = {b for pr in (_cf0.get('liuchong') or []) for b in pr}
        _ku0=('辰','戌','丑','未')
        lu_chong = (L<2) and any(z in _chong0 and t=='BEN' and not (dm_wx=='土' and z in _ku0)
                             for z,t in (dm.get('root_detail',{}) or {}).items())
        # 印成势(化官杀/生身); ratio 过低则印被当令食伤财官隔耗, 抬不动身
        yin_cheng = yin_shi and (yin_ben>=2 or yin_ju or (yin_ling and yin_ben>=1)) and ratio>=0.35
        # 官印/杀印相生: 官杀成势而印能"化尽"(印>=2本气, 或印当令有根,
        # 或印本中气根处数比官杀多>=1, 或印成局); 单一印根化当令强官杀不算.
        gs_dangling = (gs is not None and month_wx == gs_wx)   # 官杀月令本气当旺(强杀)
        gs_ben = int(gs.get('ben_n',0)) if gs else 0
        ss_zhi = (int(ss.get('stem_n',0))>=1 and
                  (int(ss.get('ben_n',0))+int(ss.get('zhong_n',0)))>=1)   # 食伤透干有根, 可制杀折官杀
        ss_cheng_xie = int(ss.get('stem_n',0))>=2 and int(ss.get('ben_n',0))>=1   # 食伤多透坐本气根=过泄(非一神泄秀)
        yin_root_n = ((int(yin.get('ben_n',0))+int(yin.get('zhong_n',0))) if yin else 0)  # 本气+中气(含印长生/禄)
        gs_root_n = int(gs.get('ben_n',0))+int(gs.get('zhong_n',0))
        _bj_stem_n = int(dm.get('stem_n',0))
        if gs_dangling:
            # 当令强官杀: 须独立本气重印(>=2)/印当令/成局方化尽; 本位寄生中气印不反化本支, 化不尽则身杀两停
            yin_can_hua = int(yin.get('ben_n',0))>=1 and (
                int(yin.get('ben_n',0))>=2 or yin_ling or yin_ju)
        else:
            # 官杀不当令(长生/浅): 印本气或长生/禄中气根 + 日主有根/比劫即可化(身强杀浅)
            # 须独立本气印(辰戌丑未/印本气支); 官杀本位寄生中气印(午中己/巳中戊)不反化本支, 同 dangling 口径
            yin_can_hua = (int(yin.get('ben_n',0))>=1) and (R>=1 or _bj_stem_n>=1)
        # 印透干得中余气根(相令受官杀生)而日主多本气根, 亦可化官杀(通根身旺, 杀印相生)
        yin_tou_hua = (int(yin.get('stem_n',0))>=1 and
                       (int(yin.get('zhong_n',0))+int(yin.get('yu_n',0)))>=1 and dm_ben>=2)
        guan_hua = bool(gs_shi) and (yin_can_hua or yin_tou_hua)
        bj_stem = int(dm.get('stem_n',0))
        yin_stem = int(yin.get('stem_n',0))
        fin_rooted_eff = (1 if cai.get('ben_n',0)>=1 else 0) if guan_hua else fin_rooted
        fin_shi_eff = (1 if cai_shi else 0) if guan_hua else fin_shi
        # 印重成势生身(印>=2本气根/成局)且日主有根能受生: 杀印相生/印绶身旺
        yin_zhong_sheng = ((yin_ben>=2 or yin_ju) and R>=1
            and not (opp_ling_fin and fin_shi>=1))  # 财官当令成势则印被财坏/杀紧克, 交guan_hua/降级, 不直抬身旺
        # 比劫党/劫印重叠有根而财官不成势(食伤当令顺泄不制): 众寡"君盛臣衰"
        dang_you_gen = (R>=1 and fin_shi==0 and
                        (bj_stem>=2 or (bj_stem>=1 and yin_stem>=1) or (bj_stem>=1 and dm_ben>=1)))
        # 根虚: 地支多本气根而天干无比劫护、财官当令且多透坏印(木旺土虚/财多身弱), 印不重
        gen_xu = (dm_ben>=2 and bj_stem==0 and opp_ling_fin and fin_stem>=2
                  and ratio<0.40 and yin_ben<2)

        if self_ju:
            S=3
        elif (L==2 and R==2) or (R==2 and (bj_shi or yin_shi)):
            S=3
        elif (yin_cheng or yin_zhong_sheng or (guan_hua and (R>=2 or ((not gs_dangling) and R>=1 and bj_stem>=1 and yin_root_n>=1)))) and (R>=1 or yin_ben>=2 or yin_ling):
            S=3
        elif R==2 or (L>=1 and R>=1) or (L==2 and A>=1) or (yin_cheng):
            S=2
        elif R==0 and not (bj_shi or yin_shi):
            S=0
        else:
            S=1
    else:
        S=1; fin_rooted_eff=fin_rooted; fin_shi_eff=fin_shi

    # 禄刃硬根+独立本气印、官杀虚浮不当令不成势: 身旺任财官(虽ratio被死绝月令系数压低)
    lu_yin_ok = (dm_has_lu and yin_ben>=1 and (not gs_dangling) and (not gs_shi) and (not lu_chong))
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
    elif (ratio < 0.18 and not lu_yin_ok) or (R==0 and (fin_shi>=1 or (ss_shi and L==0))):
        spec='太衰'   # 禄刃+本气印+官杀虚者豁免(申禄辰印, 绝令系数压低ratio而实任财官)
    # ---- 根虚: 地支多本气根而天干无比劫护、财官当令多透坏印, 根被压制(木旺土虚/财坏印) ----
    elif gen_xu:
        spec='衰' if ratio<0.35 else '中和'
    # ---- 旺极: 三会本方(会方极强, 归化后三根, T33, 不受月令失令限制) ----
    elif S>=2 and L==2 and ss_cheng_xie and (not self_ju) and yin_ben>=1 and dm_heavy>=2:
        spec='中和'   # 当令而食伤多透本气根过泄, 印绶不伤精神旺足=纯粹中和(T14/T15得时不旺, 非一神泄秀)
    elif S==3 and self_ju and dm_ben>=3 and fin_rooted_eff<=1:
        spec='旺极'
    # ---- 旺极: 三根当令(孤财失令不制); 得令重根+印多根; 印成方生身 ----
    elif S==3 and dm_ben>=3 and L==2 and fin_rooted_eff<=1:
        spec='旺极'
    elif S==3 and fin_rooted_eff==0 and dm_ben>=2 and L==2 and yin_ben>=2:
        spec='旺极'   # 得令两本气根 + 印多根(两长生逢禄旺, 木火/水木成势)
    elif S==3 and fin_rooted_eff==0 and (yin_ju or yin_ben>=3) and ratio>=0.85 and dm_heavy>=1:
        spec='旺极'
    # ---- 拱局旺极: 半合本方局+禄刃重根+印成势生身, 财官虚透无根(戌午拱火日时逢印, T32半合) ----
    elif S==3 and fin_rooted_eff==0 and dm_banhe>=1 and dm_heavy>=1 and (yin_ben>=2 or yin_ju) and ratio>=0.40:
        spec='旺极'   # 印成方/三根生身(水旺木坚)
    # ---- 太旺: 两禄刃当令无制 / 本方局 / 成势无财官本气根 ----
    elif S==3 and fin_rooted_eff==0 and multi and L==2:
        spec='太旺'
    elif S==3 and fin_rooted_eff==0 and self_ju:
        spec='太旺'
    elif S==3 and fin_rooted_eff==0 and (self_ju or (dm_heavy>=2 and (L==2 or ratio>=0.80)) or (L==2 and dm_heavy>=1)):
        spec='太旺'  # 非当令重根须成局/纯众(相非旺, 木嫩火相未为旺)
    elif S==3 and fin_rooted_eff<=1 and ratio>=0.70 and (self_ju or (dm_heavy>=2 and (L==2 or ratio>=0.80)) or (L==2 and dm_heavy>=1)):
        spec='太旺'  # 非当令重根须成局/纯众
    # ---- 官印/杀印相生: 官杀被旺印化、日主有本气根(或印>=2本气且比劫透)受生, 财轻不当令则身旺 ----
    # ---- 食伤当令成势泄气太过(纵无财亦泄), 日主仅长生无禄刃, 印虚(ben<2)不能止泄: T14 ----
    elif S>=2 and ss_ling and int(ss.get('ben_n',0))>=2 and (not dm_has_lu) and (not self_ju) and yin_ben<2:
        spec='太衰' if ratio<0.26 else '衰'   # 己亥丙子庚子辛巳: 两子一亥水成势泄金, 己印虚, 虽时支巳长生亦泄气太过
    elif S==3 and guan_hua and (R>=2 or (yin_ben>=2 and bj_stem>=1) or ((not gs_dangling) and R>=1 and bj_stem>=1 and yin_root_n>=1)) and cai_ben<2 and month_wx!=cai_wx:
        spec='旺'
    # ---- 食伤当令成势泄身+财透根耗身, 日主仅长生无禄刃(死月印止泄不力): 泄气太重/财多身弱 ----
    elif (S>=2 and ss_ling and int(ss.get('ben_n',0))>=2 and (not dm_has_lu)
          and int(cai.get('stem_n',0))>=1
          and (int(cai.get('ben_n',0))+int(cai.get('zhong_n',0))+int(cai.get('yu_n',0)))>=1 and ratio<0.42):
        spec='衰'   # T14泄气太重 + T12财多身弱(火生土土生金, 气泄于财; 死月印难止当令泄)
    # ---- 印重成势生身 / 比劫党(劫印重叠)有根而财官不成势: 身旺(印绶身旺/君盛臣衰) ----
    elif S>=2 and (yin_zhong_sheng or dang_you_gen) and ratio>=0.25:
        spec='旺'
    # ---- 禄刃硬根+独立本气印、官杀虚浮不当令不成势: 身旺任财官(先于得时不旺降级; 日主健旺足以用官) ----
    elif lu_yin_ok and fin_rooted<=dm_ben+1 and ratio>=0.15:
        spec='旺'   # 己亥丁卯庚申庚辰(申禄辰本气戊印丁官虚, 足以用官科甲封疆); 己巳癸酉丙寅庚寅(巳禄寅印)
    # ---- 比劫成党得势: 比劫多透+长生禄旺重根, 财官仅单本气根(天干皆木君盛/群比争财), 党众不论失时 ----
    elif S>=2 and bj_stem>=2 and dm_heavy>=2 and fin_rooted<=1 and ratio>=0.30:
        spec='旺'
    # ---- 官杀当令: 日主重根数 vs 官杀本气根数 有序比较(离散结构计数, 非数值score) ----
    elif S==3 and gs_dangling and dm_heavy>=1 and yin_ben>=1 and fin_rooted>=1 and dm_heavy>=gs_ben+1 and ratio>=0.30:
        spec='旺'   # 身强杀浅: 身长生禄旺重根占优 + 本气印化杀生身
    elif S==3 and gs_dangling and dm_has_lu and gs_ben<=dm_heavy+1 and fin_rooted>=1 and (yin_ben>=1 or ss_zhi) and 0.30<=ratio<0.46:
        spec='中和'   # 身杀两停: 禄刃硬根+印化/食制折杀, 势均力敌(非单长生抵当令双官)
    # ---- 得时不旺(S3 而财官成势, 印不能化) ----
    elif S==3 and fin_shi_eff>=1 and fin_stem>=2 and dm_ben<2 and ratio<0.45:
        spec='太衰'   # 得令而财官两透成党、占比压身(财多身弱/虚弱极); 多本气重根任财官不降
    elif S==3 and fin_shi_eff>=1 and dm_ben<2 and ratio<0.45:
        spec='衰'   # 多本气重根任财官不降(丙申庚申用财滋杀/己亥戊辰任财官)
    elif S==3 and (fin_shi_eff>=2 or (fin_shi_eff>=1 and fin_stem>=2)) and not (dm_ben>=2 and bj_stem>=2 and not gs_dangling):
        spec='中和' if ratio<0.56 else '旺'   # 身双禄/本气根+双比劫党众而官杀不当令=身旺任财官(丙申庚申用财滋杀), 交B判旺
    elif S==3 and fin_shi_eff>=1 and dm_ben<2 and ratio<0.55:
        spec='中和'   # 当令多本气重根(dm_ben>=2)任财官, 不降(辛丑辛丑戊申壬子旺而逢生)
    # ---- 当令有本气根、财官虚浮无本气根、比劫/印透助: 身旺能任(身旺以财为子); 得时不旺降级已在前 ----
    elif S==3 and L==2 and dm_ben>=1 and fin_rooted_eff==0 and (bj_stem>=1 or yin_stem>=1) and ratio>=0.30:
        spec='旺'
    # ---- 身轻本气根(ben<=1)而食伤成势(ben>=2)/成局泄身、印弱不成势: 过泄衰(身弱食伤为泄气, T14) ----
    elif ((int(ss.get('ben_n',0))>=2 or int(ss.get('ju_n',0))>=1)
          and dm_ben<=1 and yin_ben<2 and (not gs_dangling) and ratio<0.45):
        spec='衰'   # 辛酉辛丑己酉丙寅: 酉酉丑金局泄土; 戊子戊午丙辰戊戌: 辰戌土泄午刃(弱可知)
    # ---- 身重本气根(ben>=2)/当令而官杀不当令重克、食伤非过泄: 身旺任财官、食伤泄秀(日元强/临旺/旺而逢生) ----
    elif ((dm_ben>=2 and (not gs_dangling) and fin_rooted<=dm_ben and (not ss_cheng_xie) and ratio>=0.25)
          or (dm_ben>=2 and int(gs.get('ben_n',0))==0 and int(gs.get('stem_n',0))==0
              and int(ss.get('ju_n',0))<1 and not (ss_ling and int(ss.get('ben_n',0))>=2) and ratio>=0.20)
          or (L==2 and dm_ben>=1 and fin_rooted<=1 and int(ss.get('ben_n',0))<2 and int(ss.get('ju_n',0))<1 and ratio>=0.30)):
        spec='旺'   # 特例: 禄刃重根而官杀全无、食伤仅泄秀非过泄(壬午癸丑甲寅丁卯寅卯气旺丁火秀)
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
