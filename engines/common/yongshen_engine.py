# -*- coding: utf-8 -*-
"""160-D 用神病机收敛引擎 V2.4(布尔+多态枚举决策树, 非 score/非黑盒裁决)。

primary 主用神(1行)+secondary 喜神/相神+avoid 忌神。
特殊格局顺逆分流 / CANDIDATE 真假从(印叠透或得载留正格, 无根从顺; 从儿归财、火财吐秀、水财寒湿顺财)
> 仲冬仲夏调候(制杀调候合一; 夏水透看印源/库根, 水涸培金) > 官杀制化(中和杀印相生/身根足食制)
> 通关(成势×成势, 财印战放宽到透根) > 专旺日支归垣用财 > 印重财破(官杀不透)
> 衰极印绝食伤财成势顺生(类从儿) > 财重分财/食伤泄过 > 扶抑(财当令滋弱杀、官透用官、虚杀食制)。
cs 成势=当令旺/本气>=2/成局/透干>=2且有气; 专旺食伤顺泄须得比劫成势之生。
吉凶前端拦截, 本层只给真实取用结构; 不接 production_entry。
"""
WUXING='木火土金水'
SHENG={'木':'火','火':'土','土':'金','金':'水','水':'木'}
KE={'木':'土','土':'水','水':'火','火':'金','金':'木'}
WX={'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
WANG_TIER=('旺极','太旺','旺'); SHUAI_TIER=('衰极','太衰','衰')
WINTER=('亥','子','丑'); SUMMER=('巳','午','未'); DRY_BRANCH=('午','未','戌'); MIDWINTER=('亥','子'); MIDSUMMER=('巳','午')
BRANCH_WX={'子':'水','亥':'水','寅':'木','卯':'木','巳':'火','午':'火','申':'金','酉':'金','辰':'土','戌':'土','丑':'土','未':'土'}

def _ten_wx(dmw):
    return {'bi': dmw,
            'yin': [x for x in WUXING if SHENG[x]==dmw][0],
            'shi': SHENG[dmw], 'cai': KE[dmw],
            'guan': [x for x in WUXING if KE[x]==dmw][0]}

def build_yongshen_engine(pillars, facts, wuxing_power, spectrum, special, climate):
    dm=facts['day_stem']; dmw=WX[dm]; t=_ten_wx(dmw)
    tier=spectrum.get('spectrum') if isinstance(spectrum,dict) else spectrum
    wpd=(wuxing_power or {}).get('wuxing_power',{})
    def d(w): return wpd.get(w) or {}
    def ben(w): return d(w).get('ben_n',0)
    def stem(w): return d(w).get('stem_n',0)
    def ling(w): return d(w).get('ling_state')
    def cs(w):
        return ling(w)=='旺' or ben(w)>=2 or d(w).get('ju_n',0)>=1 or (stem(w)>=2 and (ling(w) in ('旺','相') or ben(w)>=1))
    def qi(w):
        return ben(w)>=1 or stem(w)>=1 or ling(w) in ('旺','相')

    cong=(special.get('cong_type') or '').strip(); cong_state=(special.get('cong_state') or '').strip()
    zw=(special.get('zhuanwang') or '').strip(); hua=(special.get('hua_qi') or '').strip()
    lq=special.get('liangqi') or None
    conf_cong=bool(cong) and 'CONFIRMED' in cong_state
    cand_cong=bool(cong) and not conf_cong
    spec_name=cong or zw or hua or (lq.get('name') if lq else '正格')

    primary=None; secondary=[]; avoid=[]; paths=[]; notes={}
    def P(w,path,note):
        nonlocal primary
        if w and w in WUXING and primary is None:
            primary=w; paths.append(path); notes[w]=note
    def S(w,note=''):
        if w and w in WUXING and w!=primary and w not in secondary:
            secondary.append(w); notes.setdefault(w,note)
    def A(*ws):
        for w in ws:
            if w and w in WUXING and w not in avoid: avoid.append(w)
    hou={WX[c.get('stem')] for c in (climate.get('climate_candidates') or []) if c.get('stem') in WX}
    mz=pillars['month'][1]; dz=pillars['day'][1]
    brs=[pillars[k][1] for k in ('year','month','day','hour')]
    cold=(mz in WINTER) or (ling('水')=='旺' and not qi('火'))
    hot=(mz in SUMMER) or (ling('火')=='旺' and not qi('水'))
    fire_branches=sum(1 for b in brs if b in ('巳','午','未','戌'))
    dry=(dmw=='土' and fire_branches>=2 and ben('水')==0 and mz not in ('亥','子','丑'))
    chong_branches=set()
    for pr in (facts.get('combination_facts',{}) or {}).get('liuchong',[]):
        if len(pr)==2: chong_branches.update(pr)

    yin_load = stem(t['yin'])>=2 or (stem(t['yin'])>=1 and (ben(t['yin'])>=1 or ben(t['guan'])>=1)) \
               or (stem(t['yin'])>=1 and stem(t['guan'])>=2)
    gen_zheng = yin_load or (ben(dmw)>=1 and ben(t['yin'])>=1)
    cong_shun = (conf_cong or (cand_cong and not gen_zheng)) and stem(t['yin'])<2 \
        and not (stem(t['yin'])>=1 and stem(t['bi'])>=1)
    zheng=(not zw) and (not lq) and (not hua) and (not cong_shun)

    # ---------- A 化气 / 从顺 / 专旺 / 成象 ----------
    if hua:
        hwx=next((w for w in WUXING if ('化'+w) in hua or w in hua), None)
        if hwx:
            P(hwx,'HUA_QI','化气格以化神为用'); S(SHENG[hwx],'生扶化神'); A(t['guan'],t['cai'])
    if cong_shun:
        if '从财' in cong:
            if t['cai']=='水' and (mz in ('亥','子','丑','辰') or cold):
                P(t['cai'],'CONG_SHUN','寒湿虚身从水财，顺其寒湿水势'); S(t['shi'],'金食伤生水')
            elif qi(t['shi']):
                P(t['shi'],'CONG_SHUN','从财喜食伤吐秀生财(从财必要食伤)'); S(t['cai'],'顺财')
            else:
                P(t['cai'],'CONG_SHUN','从财无食伤，顺财'); S(t['shi'],'食伤生财')
        elif '从官' in cong or '从杀' in cong or '从煞' in cong:
            P(t['guan'],'CONG_SHUN','从官杀顺官杀'); S(t['cai'],'财生官杀')
        elif '从儿' in cong:
            P(t['cai'],'CONG_SHUN','从儿儿又见儿，食伤生财，以财为用'); S(t['shi'],'顺食伤格神')
        elif '从势' in cong or '从强' in cong:
            P(t['cai'],'CONG_SHUN','从势顺势')
        A(t['yin'],t['bi'])
    if zw:
        gw=t['guan']; cw=t['cai']; sw=t['shi']; yw=t['yin']
        og=[pillars[k][0] for k in ('year','month','hour')]
        gan_yang = dm in '甲丙戊庚壬'
        _yang='甲丙戊庚壬'; _yin='乙丁己辛癸'; _seq='木火土金水'
        sha_gan = _yang[_seq.index(gw)] if gan_yang else _yin[_seq.index(gw)]
        has_sha = sha_gan in og
        guan_rooted = ben(gw)>=1 or cs(gw) or ling(gw) in ('旺','相')
        cai_zai = has_sha and stem(gw)>=1 and (ben(cw)>=1 or any(BRANCH_WX.get(b)==cw for b in brs))   # 阳杀得财方支归垣之载(曲直庚得辰载, 辰会木方仍载)
        if '曲直' in zw:
            if cai_zai:
                P(gw,'WANG_KE','曲直春木，阳杀(庚)得财星本气之载，力足以修旺木，用杀')
            elif not guan_rooted and stem(gw)>=1 and stem(sw)>=1:
                P(sw,'WANG_KE','曲直官杀虚透临绝(木旺金缺)，食伤火透泄秀兼制虚杀，寒木向阳')
            elif not guan_rooted and stem(gw)>=1 and stem(sw)==0 and stem(yw)>=1:
                P(yw,'ZHUANWANG','曲直官杀虚、食伤不透，印星透干顺性滋木(存君之子)')
            elif stem(gw)==0 and sum(1 for b in brs if BRANCH_WX.get(b)==cw)>=2 and stem(sw)>=1:
                P(cw,'ZHUANWANG','曲直无官杀、财方支叠见归垣而食伤透以生财，身旺任财'); S(sw,'食伤生财')
            else:
                P(sw,'ZHUANWANG','曲直格顺食伤火泄秀(木火通明)')
        elif '炎上' in zw:
            if stem(gw)>=1:
                if stem(gw)==1 and mz in ('巳','午') and d(dmw).get('ju_n',0)>=1 and stem(cw)>=1 and ben(gw)==0:
                    P(cw,'WANG_KE','炎上仲夏火局成、官杀独透根绝，弱杀难制旺火，财滋弱杀(金生水)为用'); S(gw)
                else:
                    P(gw,'WANG_KE','炎上火旺，官杀水透以济炎(火炎水制)，根弱待运/财金滋'); S(cw,'财金滋水')
            elif stem(sw)>=2 or cs(sw):
                P(sw,'ZHUANWANG','炎上水绝而食伤土成势透干，火土伤官泄秀为用'); S(cw,'财星得用')
            else:
                P(gw,'QIHOU','炎上火炎水绝，取水(官杀)调候济火待运')
        elif '稼' in zw:
            if ling(sw)=='旺':
                P(cw,'QIHOU','稼穑食伤金当令泄秀已足，取水(财)润燥养金'); S(sw)
            elif ben(sw)>=1 or stem(sw)>=1:
                P(sw,'ZHUANWANG','稼穑食伤金透干或见本气根(申酉)，金泄土秀为用(非官印论)')
            else:
                P(cw,'QIHOU','稼穑火土燥烈，取水(财)润燥养金为急'); S(sw)
        elif '从革' in zw:
            if stem(sw)>=2:
                P(sw,'ZHUANWANG','从革金旺而食伤并透，金白水清/泄其精英为用'); S(cw,'食伤生财')
            elif mz in ('申','酉') and stem(gw)>=1:
                P(gw,'WANG_KE','从革秋金当令旺极，官杀火透炼金成器(金旺喜火)，根弱待运'); S(cw,'财木生火')
            elif stem(gw)>=1 and ben(gw)==0 and ben(cw)>=1:
                P(cw,'WANG_KE','从革官杀火透无根，财星本气生杀(木火两字)，用财滋杀'); S(gw)
            elif cold and not qi(gw):
                P(gw,'QIHOU','从革金寒水冷无火，火暖局调候为急')
            else:
                P(gw,'WANG_KE','从革金旺喜火炼，取官杀火'); S(cw)
        elif '润下' in zw:
            if stem(sw)>=1:
                P(sw,'ZHUANWANG','润下水旺极，食伤木透泄秀(水生木)为奋发之机'); S(cw,'木生火暖局')
            elif stem(cw)>=1:
                P(cw,'QIHOU','润下冬水寒凝，财火透干敌寒解冻/暖局为急'); S(sw)
            else:
                P(sw,'ZHUANWANG','润下顺食伤木泄秀，喜火暖'); S(cw)
        else:
            if dmw=='土' and dry:
                P(cw,'QIHOU','专旺燥烈，财润燥为急')
            elif stem(gw)>=2 and guan_rooted:
                P(gw,'WANG_KE','专旺官杀叠透有气，太旺可克以修旺')
            elif BRANCH_WX.get(dz)==cw and dz not in chong_branches and stem(gw)==0:
                P(cw,'ZHUANWANG','专旺日支财星归垣不被冲，身旺用财'); S(sw,'食伤生财')
            elif stem(sw)>=1 and (ben(sw)>=1 or cs(sw) or cs(dmw)):
                P(sw,'ZHUANWANG','专旺食伤透干得比劫成势之生，顺泄为用')
            elif ben(cw)>=1 or cs(cw):
                P(cw,'ZHUANWANG','专旺财有根，用财(滋杀/润燥)')
            else:
                P(sw,'ZHUANWANG','格纯专旺，食伤泄秀导其气势')
        S(yw,'顺性喜印'); S(t['bi'],'顺性喜比劫')
        if primary!=gw: A(gw)
        if primary!=cw: A(cw)
    if lq:
        if lq.get('xiu'): P(lq['xiu'],'LIANGQI','两气成象顺食伤秀神'); S(t['bi'],'成象顺本方')

    # ---------- B 正格 ----------
    if zheng:
        # 财星破印可用性: 透干有藏干根(本气/中气/余气), 且不被阳日干五合合走而失令
        YANG_HE={'甲':'己','丙':'辛','戊':'癸','庚':'乙','壬':'丁'}
        other_gan=[pillars[k][0] for k in ('year','month','hour')]
        cai_gan_he=(dm in YANG_HE) and (YANG_HE[dm] in other_gan)
        cai_root=ben(t['cai'])>=1 or (stem(t['cai'])>=1 and any(BRANCH_WX.get(b)==t['cai'] for b in brs))  # 本气根; 或财透干坐财方支(己透坐丑虽会水方仍通根位)
        cai_usable=bool(cai_root) and stem(t['cai'])>=1 and not (cai_gan_he and ling(t['cai']) in ('囚','死'))
        # B1 仲冬调候(火透: 杀重则制杀调候合一, 否则身有气寒木向阳; 印重破印让位)
        if primary is None and mz in MIDWINTER and stem('火')>=1 \
                and not (cs(t['yin']) and not cs(t['guan']) and stem(t['guan'])==0 and cai_usable) \
                and ('火' in (t['shi'],t['yin']) or tier in WANG_TIER or cs(dmw) or cs(t['guan'])):
            P('火','QIHOU','仲冬火透为我生/生我之候神，制杀调候/寒木向阳为急(印重无杀财破印除外)')
        # B1b 仲夏调候(水透: 有根/多透/水库/金印源则用水, 单透涸绝培金生水)
        if primary is None and mz in MIDSUMMER and stem('水')>=1:
            if ben('水')>=1 or stem('水')>=2 or ('辰' in brs or '丑' in brs) or ben('金')>=1:
                P('水','QIHOU','仲夏火炎，水透有根/库/金生，水制火调候')
            else:
                P('金','QIHOU','仲夏水单透根涸金无根，培金印生水为源')
        # B2 官杀制化
        if primary is None:
            gs_rooted = cs(t['guan']) or (stem(t['guan'])>=1 and ben(t['guan'])>=1)
            yin_cheng = cs(t['yin']) or ben(t['yin'])>=2
            cai_yin_chong=False
            for _pr in ((facts.get('combination_facts',{}) or {}).get('liuchong',[]) or []):
                if len(_pr)==2 and {BRANCH_WX.get(_pr[0]),BRANCH_WX.get(_pr[1])}=={t['cai'],t['yin']}:
                    cai_yin_chong=True   # 财成势冲克印支(如申金冲寅木), 官杀是泄财生印通关枢纽, 非攻身
            gs_bing = gs_rooted or (stem(t['guan'])>=1
                       and (ling(t['yin'])=='旺' or cs(t['yin']) or ben(t['yin'])>=1 or stem(t['yin'])>=1)
                       and not (tier in WANG_TIER and not gs_rooted and yin_cheng)
                       and not (cs(t['cai']) and cai_yin_chong and stem(t['yin'])>=1 and ben(t['yin'])>=1))
            if gs_bing:
                zhi_ok=stem(t['shi'])>=1 and qi(t['shi'])
                yin_he = d(t['yin']).get('banhe_n',0)>=1 or BRANCH_WX.get(dz)==t['yin']
                hua_ok=stem(t['yin'])>=1 or ling(t['yin'])=='旺' or ben(t['yin'])>=2 or (ben(t['yin'])>=1 and yin_he)
                if tier in WANG_TIER:
                    if zhi_ok:
                        P(t['shi'],'BINGYAO','官杀成势身旺，食伤制杀')
                    elif gs_rooted and hua_ok and (cs(t['guan']) or stem(t['guan'])>=2):
                        P(t['yin'],'BINGYAO','身旺而官杀成势有根、印透有气，杀印相生权自我操'); S(t['guan'])
                    elif stem(t['guan'])==1 and cs(t['cai']) and stem(t['bi'])>=2:
                        P(t['cai'],'FUYI','身旺比劫成众、官杀独透根浅而财星当令，财滋弱杀'); S(t['guan'])
                    else:
                        P(t['guan'],'BINGYAO','身旺官杀透，任官杀克身成权(待根/财滋)'); S(t['cai'],'财滋官杀')
                elif ben(dmw)>=2 and not hua_ok:
                    P(t['shi'],'BINGYAO','官杀重而身有重根、印无气，食伤制杀为美(生局须食)'); S(t['yin'])
                elif hua_ok:
                    P(t['yin'],'BINGYAO','官杀重身弱/中和，印化杀生身(杀印相生)'); S(t['bi'])
                elif zhi_ok:
                    P(t['shi'],'BINGYAO','印无力而食伤透根，食伤制杀'); S(t['yin'])
                else:
                    P(t['yin'],'BINGYAO','官杀重，取印化杀待运'); S(t['bi'])
                A(t['cai'])
        # B4 印重成病(官杀不透)→财破印(优先于通关: 印重为病, 通关官杀生印反助病)
        if primary is None and cs(t['yin']) and stem(t['guan'])==0 and cai_usable:
            P(t['cai'],'BINGYAO','印重成势官杀不透而财有本气根，财破印去壅塞'); S(t['shi']); A(t['yin'])
        # 印重无官杀、财不透而食伤有本气根: 食伤生财、就财破印(财待运透), 同党顺泄
        if primary is None and cs(t['yin']) and stem(t['guan'])==0 and not cai_usable \
                and stem(t['cai'])==0 and ben(t['shi'])>=1:
            P(t['cai'],'BINGYAO','印重成势无官杀、财不透而食伤有本气根，食伤生财就财破印(财待透)'); S(t['shi'],'食伤泄秀生财'); A(t['yin'])
        # B3 通关
        if primary is None and cs(t['guan']) and cs(t['bi']):
            P(t['yin'],'TONGGUAN','官杀与比劫两神成势相战，印通关')
        if primary is None and cs(t['cai']) and (cs(t['yin']) or (stem(t['yin'])>=1 and ben(t['yin'])>=1)):
            P(t['guan'],'TONGGUAN','财印成势相战(或印透根被财克)，官杀通关(财生官生印)')
        if primary is None and cs(t['shi']) and cs(t['guan']):
            P(t['cai'],'TONGGUAN','食伤与官杀两神成势相战，财通关')
        # B4b 衰极印绝、食伤+财成势顺生(日支根被合化, 类从儿)→顺财
        if primary is None and tier=='衰极' and ben(t['yin'])==0 and stem(t['yin'])==0 \
                and cs(t['shi']) and cs(t['cai']):
            P(t['cai'],'CONG_SHUN','衰极印绝、食伤生财成势顺生(类从儿)，顺财'); S(t['shi'],'食伤吐秀')
        # B5 财重身弱 / 食伤泄过
        if primary is None and cs(t['cai']) and tier in SHUAI_TIER:
            if ben(t['bi'])>=1:
                P(t['bi'],'BINGYAO','财重身弱、比劫有根，比劫分财'); S(t['yin'])
            elif qi(t['yin']):
                P(t['yin'],'BINGYAO','财重身弱而比劫虚透无根(干多不如根重)，印化财生身'); S(t['bi'])
            elif qi(t['bi']):
                P(t['bi'],'BINGYAO','财重身弱，比劫分财'); S(t['yin'])
            else:
                P(t['yin'],'BINGYAO','财重身弱无比劫，印扶身泄财'); S(t['bi'])
            A(t['cai'],t['guan'])
        if primary is None and cs(t['shi']) and tier in SHUAI_TIER:
            P(t['yin'],'BINGYAO','食伤泄气太过，印制食伤扶身'); S(t['bi']); A(t['shi'])
        # B6 调候兜底 / 扶抑
        if primary is None and mz in MIDWINTER:
            P('火','QIHOU','仲冬寒凝无制化，取火调候待运')
        if primary is None and mz in MIDSUMMER:
            P('水','QIHOU','仲夏炎燥无制化，取水调候待运')
        if primary is None and tier in WANG_TIER:
            if stem(t['guan'])>=2 and stem(t['shi'])>=1: P(t['shi'],'BINGYAO','身旺官杀众透，食伤制杀兼泄秀')
            elif cs(t['cai']) and qi(t['guan']) and stem(t['guan'])<2: P(t['cai'],'FUYI','身旺财当令而官杀浅，财滋弱杀/用财')
            elif stem(t['guan'])==1 and ben(t['guan'])==0 and ling(t['guan']) in ('休','囚','死') \
                    and stem(t['cai'])>=1 and ben(t['cai'])>=1:
                P(t['cai'],'FUYI','身旺官杀独透无根失令不足任，财星透干有根(财来就我)，用财'); S(t['shi'],'食伤生财')
            elif stem(t['guan'])>=1: P(t['guan'],'FUYI','身旺官杀透干，用官杀克身成权(待根)')
            elif ben(t['guan'])==0 and stem(t['shi'])>=1: P(t['shi'],'FUYI','身旺官杀虚透无根，食伤制杀兼泄秀')
            elif qi(t['cai']): P(t['cai'],'FUYI','身旺用财，我克为财')
            else: P(t['shi'],'FUYI','身旺无官杀财，食伤吐秀')
            S(t['cai'] if primary==t['guan'] else t['shi'],''); A(t['yin'],t['bi'])
        if primary is None and tier in SHUAI_TIER:
            if qi(t['yin']): P(t['yin'],'FUYI','身弱用印，生我扶身')
            elif qi(t['bi']): P(t['bi'],'FUYI','身弱用比劫帮身')
            else: P(t['yin'],'FUYI','身弱印比微，取印待运扶身')
            S(t['bi'] if primary==t['yin'] else t['yin'],''); A(t['cai'],t['guan'],t['shi'])
        if primary is None and tier=='中和':
            if stem(t['guan'])>=1 and ben(t['guan'])>=1 and (ling(t['yin'])=='旺' or cs(t['yin'])):
                P(t['yin'],'BINGYAO','中和官杀透根、印当令，杀印相生用印')
            elif hou: P(sorted(hou)[0],'QIHOU','中和取调候/相神，扶抑不强')
        for w in hou:
            if w!=primary: S(w,'调候候神(《穷通宝鉴》次序)')

    cand=[w for w in ([primary]+secondary) if w]
    return {'module':'YONGSHEN_ENGINE_V2','namespace':'daymaster_yongshen_engine',
            'day_master':dm,'daymaster_wuxing':dmw,'spectrum_tier':tier,'special':spec_name,
            'yongshen_primary':primary,'yongshen_secondary':secondary,'yongshen_avoid':avoid,
            'yongshen_paths':paths,
            'yongshen_candidates':[{'wuxing':w,'path':(paths[0] if w==primary else 'SECONDARY'),
                                    'note':notes.get(w,'')} for w in cand],
            'candidate_wuxing':sorted(set(cand)),
            'judgment_status':'YONGSHEN_PRIMARY_STRUCTURE' if primary else 'YONGSHEN_PENDING',
            'boundary_note':'病机决策树收敛主用神(布尔+多态枚举, 无score/winner); primary为结构取用推演非富贵吉凶裁决, '
                           '假从/湿土/会方归垣等边界保留secondary; 吉凶前端拦截; 成败有力待作用层; 不接production_entry'}
