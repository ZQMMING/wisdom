# -*- coding: utf-8 -*-
import re
"""特殊格局结构识别（task#47）。

只做**结构定性标签**，不改变七档客观力量谱，不输出用神/吉凶/成败。
- 化气格：日干与【紧邻】(月干/时干)五合、化神得月令或成势(本气>=2/会局)；
  日主无根无印=真化(CONFIRMED)，带一微根/微印=假化(CANDIDATE)；隔位遥合、化神不当令不成势=合而不化(不判)。
  他干合化、地支合化、大运合化不在此列(交 ACTIVITY 合去 / task#50 归化)。
- 从格：日主无本气根、无有根印比、对立一方成势顺其势；虚透印比地支不载=假从(CANDIDATE)。
  **孤根被冲拔(T30)**: 身/印本气仅一支且被六冲、对立成势而日主不当令 -> 根拔, 冲拔之从为CANDIDATE(不作真从)。
  **财生杀**: 官杀透干而得本气财生(申金生壬杀)亦成杀势。
  食伤生财分界(#PCT-MARK): 财成局明透/当令党众主导->从财(丙寅庚寅「从财格真」);
    食伤当令本气压财、或叠透而财藏(儿会财局,吾儿又见儿)->从儿。
  **从儿不论身强弱**(甲午丁丑「格取从儿,虽逢禄比帮身,非身弱论」): 官杀无、食伤成势、无印逆局、
    日主非比劫当令即可, 允许日主带一禄根(CANDIDATE)。
- 专旺/一行得气(曲直/炎上/稼穡/从革/润下): 本方成局/本气重, 无官杀本气克、无财破;
  官杀虚透无根须被合化为本方(戊癸合火助刃)方不破局。
- 母多灭子/印势漂没(CANDIDATE): 印成势而日主无根不受生; pair反转(木火通明vs土重金埋)交气候/天干性情层。

方法论: 布尔 + 多态枚举 + 客观本气支数比较(#PCT-MARK, 非权重评分)。
原典: 《滴天髓·从象》《化象》《一行得气》; 「从儿不论身强弱」「干多不如根重」「旺者冲衰衰者拔」。
"""

ZHUANWANG_NAME = {'木': '曲直格', '火': '炎上格', '土': '稼穑格', '金': '从革格', '水': '润下格'}
WUHE_HUASHEN = {('甲', '己'): '土', ('己', '甲'): '土', ('乙', '庚'): '金', ('庚', '乙'): '金',
                ('丙', '辛'): '水', ('辛', '丙'): '水', ('丁', '壬'): '木', ('壬', '丁'): '木',
                ('戊', '癸'): '火', ('癸', '戊'): '火'}
# 本气级根标签(计 ben_n)
_BEN_TAGS = ('BEN', 'BEN_LU', 'BEN_CS')


def _shi(d):
    if not d:
        return False
    ben = int(d.get('ben_n', 0)); stem = int(d.get('stem_n', 0))
    ju = int(d.get('ju_n', 0)); ling = d.get('ling_state', '')
    return (stem >= 1 and ben >= 1) or ben >= 2 or ju >= 1 or (ling == '旺' and ben >= 1)


def _fkey(d):
    """#PCT-MARK: 成势归宿定性排序键(局 > 本气+半合支数 > 透干)。"""
    if not d:
        return (0, 0, 0)
    return (int(d.get('ju_n', 0)), int(d.get('ben_n', 0)) + int(d.get('banhe_n', 0)), int(d.get('stem_n', 0)))


def _pat(pid, name, state, side, note, facts=None):
    return {'pattern_id': pid, 'name': name, 'state': state, 'side': side,
            'boundary_note': note, 'source_fact_ids': list(facts or [])}


def _ben_branches(pw, wx):
    rd = (pw.get(wx, {}) or {}).get('root_detail', {}) or {}
    return {br for br, v in rd.items() if v in _BEN_TAGS}


def build_special_patterns(pillars, facts, wp, tian_he=None, climate=None):
    from engines.common.wuxing_power import SHENG, SHENG_ME, KE, KE_ME, BRANCH_WX
    pw = (wp or {}).get('wuxing_power', {})
    dm_wx = (wp or {}).get('daymaster_element')
    day_stem = (pillars.get('day') or [''])[0]
    out = {'patterns': [], 'cong_type': None, 'cong_state': None, 'zhuanwang': None,
           'hua_qi': None, 'mu_mie': None, 'judgment_status': 'STRUCTURE_ONLY'}
    if not dm_wx or dm_wx not in pw:
        out['judgment_status'] = 'INSUFFICIENT_INPUT'
        return out

    yin_wx, ss_wx, cai_wx, gs_wx = SHENG_ME[dm_wx], SHENG[dm_wx], KE[dm_wx], KE_ME[dm_wx]
    dm, yin = pw[dm_wx], pw.get(yin_wx, {})
    ss, cai, gs = pw.get(ss_wx, {}), pw.get(cai_wx, {}), pw.get(gs_wx, {})

    dm_ben = int(dm.get('ben_n', 0)); dm_stem = int(dm.get('stem_n', 0)); dm_ju = int(dm.get('ju_n', 0))
    yin_ben = int(yin.get('ben_n', 0)); yin_stem = int(yin.get('stem_n', 0)); yin_ju = int(yin.get('ju_n', 0))
    gs_ben = int(gs.get('ben_n', 0)); gs_stem = int(gs.get('stem_n', 0)); gs_ju = int(gs.get('ju_n', 0))
    cai_ben = int(cai.get('ben_n', 0)); cai_stem = int(cai.get('stem_n', 0))
    cai_ju = int(cai.get('ju_n', 0)); cai_banhe = int(cai.get('banhe_n', 0))
    ss_ben = int(ss.get('ben_n', 0)); ss_stem = int(ss.get('stem_n', 0)); ss_ju = int(ss.get('ju_n', 0))
    gs_ling = gs.get('ling_state') == '旺'; cai_ling = cai.get('ling_state') == '旺'; ss_ling = ss.get('ling_state') == '旺'
    dm_ling = dm.get('ling_state') == '旺'

    # ---- 孤根被冲拔(T30): 身/印本气仅一支、被六冲、对立成势而日主不当令 ----
    chong = (facts.get('combination_facts', {}) or {}).get('liuchong', [])
    chong_map = {}
    for pair in chong:
        if len(pair) == 2:
            chong_map[pair[0]] = pair[1]; chong_map[pair[1]] = pair[0]
    self_br = _ben_branches(pw, dm_wx) | _ben_branches(pw, yin_wx)
    struck = set()
    opp_ben = cai_ben + gs_ben + ss_ben
    if len(self_br) <= 1:
        for r in self_br:
            if r in chong_map:
                r2_wx = BRANCH_WX.get(chong_map[r])
                opp_dom = gs_ling or gs_ju >= 1 or cai_ju >= 1 or opp_ben >= 2 \
                    or int(pw.get(r2_wx, {}).get('ben_n', 0)) >= 1
                self_dom = dm_ling or dm_ju >= 1
                if opp_dom and not self_dom:
                    struck.add(r)
    dm_ben_eff = max(0, dm_ben - len(_ben_branches(pw, dm_wx) & struck))
    yin_ben_eff = max(0, yin_ben - len(_ben_branches(pw, yin_wx) & struck))
    root_struck = bool(struck)
    rootless = (dm_ben_eff == 0 and yin_ben_eff == 0)
    virtual_support = (dm_stem >= 1 or yin_stem >= 1)
    _light_tags = ('YU', 'MU_KU', 'SPECIAL', 'LONGSHENG_YIN')
    party = dm_ben_eff + yin_ben_eff + dm.get('banhe_n', 0)   # #PCT-MARK 专旺党众=日主本气+印本气+半合本方(印生身/半局助党)

    # 官杀成势(含财本气生透干杀) / 食伤成势(提前供救应判断)
    gs_pow_pre = _shi(gs)   # 食神制杀救应只认官杀本气真成势; 财生杀归从杀分类, 不在此封从财
    _dmrd = dm.get('root_detail', {}) or {}
    dm_light = any(any(t in str(v) for t in _light_tags) for v in _dmrd.values())
    _ss_gen = len((ss.get('root_detail', {}) or {})) > 0
    _ss_youli = (ss_ben >= 1) or (ss_stem >= 1 and _ss_gen) or (ss_stem >= 2)
    # 制杀救应(逆局): 食伤有力且财不透(无财通关, 食伤直克官杀), 或食伤叠透力足制杀;
    # 单透又有财透=伤官生财生官顺局(丙戌壬辰), 不救
    zhi_sha_save = (dm_ben_eff == 0 and dm_light and gs_pow_pre and _ss_youli
                    and (cai_stem == 0 or ss_stem >= 2))

    # E 孤根无冲而被当令成势官杀克拔(乙卯己卯): 日主仅一孤本气根、无印、官杀当令ben>=2成势、无食伤制杀
    ke_struck = (dm_ben_eff == 1 and yin_ben_eff == 0 and (gs_ling or gs_ju >= 1) and gs_ben >= 2
                 and ss_ben == 0 and ss_stem == 0)
    # F 日主真无根(含无轻根)、仅一孤印, 被当令成势之神反侮/克没(壬寅辛亥辰土孤印被当令旺水反侮, 辰为水库同化)
    _yin_ke = KE[yin_wx]
    _yk = pw.get(_yin_ke, {}) or {}
    yin_fanwu = (dm_ben_eff == 0 and not dm_light and yin_ben_eff == 1
                 and ((ss_ling and ss_ben >= 2)
                      or (_yk.get('ling_state') == '旺' and int(_yk.get('ben_n', 0)) >= 2)))
    yin_ke2 = (dm_ben_eff == 0 and yin_ben_eff == 1 and gs_ling and gs_ben >= 2 and cai_ben >= 1)
    # G 寄生宫/长生根而无同五行本气支根(土寄禄火宫: 戊禄巳旺午本气是火印、长生寅本气是甲杀),
    #   官杀当令本气成势且透干、印完全不透(化杀不力/虚不纳印)、食伤全不制 -> 假从杀, 寄宫根待运拔 CANDIDATE
    dm_true_ben = sum(1 for _v in _dmrd.values() if _v == 'BEN')
    jia_xu_sha = (dm_true_ben == 0 and dm_ben_eff >= 1
                  and gs_ling and (gs_ben + int(gs.get('banhe_n', 0))) >= 2 and gs_stem >= 1
                  and yin_stem == 0 and ss_ben == 0 and ss_stem == 0)
    rootless_entry = rootless or ke_struck or yin_fanwu or yin_ke2 or jia_xu_sha

    # ---------- 化气格(日干与紧邻月/时干合, 化神得令成势; 先判, 与从格互斥)----------
    hua_name = None; hua_state = None
    if tian_he and dm_ben_eff <= 1 and yin_ben_eff <= 1:
        for hp in tian_he.get('he_pairs', []):
            pls = hp.get('pillars', [])
            if 'day' not in pls:
                continue
            if not any(q in pls for q in ('month', 'hour')):
                continue   # 年干与日干隔月干=遥合, 不化
            stems = hp.get('stems', [])
            if day_stem not in stems:
                continue
            other = [s for s in stems if s != day_stem]
            if not other:
                continue
            hs = WUHE_HUASHEN.get((day_stem, other[0]))
            if not hs or hs not in pw:
                continue
            hd = pw[hs]
            on_qi = bool(hp.get('huashen_on_month_qi')) or (wp.get('month_element') == hs)
            hb, hju, hs_t = int(hd.get('ben_n', 0)), int(hd.get('ju_n', 0)), int(hd.get('stem_n', 0))
            chengshi = on_qi or hju >= 1 or hb >= 2     # 化神得令/成局/本气成势方论化
            if not chengshi:
                continue                                # 合而不化(冬令戊癸不化)
            if gs_stem >= 1 and gs_ben >= 1:
                continue   # 官杀有根透干克身=牵挂, 合而不真化(戊申甲寅戊土坐未实从财); 虚浮无根官杀被化神克伤不阻化
            hua_name = '化%s气格' % hs
            if on_qi and dm_ben_eff == 0 and yin_ben_eff == 0 and (hb >= 1 or hju >= 1 or hs_t >= 1):
                hua_state = 'CONFIRMED'
            else:
                hua_state = 'CANDIDATE'                 # 微根/微印=假化
            out['patterns'].append(_pat('ZP-SPECIAL-HUAQI', hua_name, hua_state, hs,
                '日干与紧邻(月/时)干五合、化神得令或成势；真化须日主无根无印，微根/微印为假化(CANDIDATE)；隔位合、化神不当令不成势为合而不化；成败取用交化气专审，不判吉凶',
                ['tian_he', 'wuxing_power']))
            out['hua_qi'] = hua_name
            break

    # 官杀成势(含财本气生透干杀)
    gs_pow = _shi(gs) or (gs_stem >= 1 and cai_ben >= 1)
    # 财明透成局主导(压食伤, 使从财而非从儿)
    cai_lead = ((cai_ju >= 1 and cai_stem >= 1)
                or (cai_banhe >= 2 and cai_stem >= 1 and ss_stem <= 1)
                or (cai_ling and _shi(cai) and cai_stem >= 1))
    ss_pow = _shi(ss)

    # ---------- 从格 ----------
    cong = None; side = None; cstate = None
    if rootless_entry and not hua_name and not zhi_sha_save:
        sides = {'食伤': (ss, ss_wx), '财': (cai, cai_wx), '官杀': (gs, gs_wx)}
        shi_sides = {k: (v, wx) for k, (v, wx) in sides.items()
                     if (k == '官杀' and gs_pow) or (k != '官杀' and _shi(v))}
        if shi_sides:
            if ss_ling and ss_pow and gs_stem >= 1 and gs_ben >= 1 and ss_ben > gs_ben and cai_stem >= 1:
                # 食伤当令成势、制去有根透干之孤官杀(制杀太过/去杀存财)、财透承接 -> 从财
                cong, side = '从财格', cai_wx
            elif gs_pow and gs_stem >= 1 and cai_ben >= 1 and not ss_ling and ss_stem == 0 and ss_ju == 0:
                # 财(有本气)生透干之杀、食伤不当令不逆局, 气归于杀 -> 从杀用财
                cong, side = '从杀格', gs_wx
            elif gs_ling and gs_pow:
                cong, side = '从杀格', gs_wx
            elif ss_ling and ss_pow and not gs_pow:
                if gs_stem >= 1 and gs_ben >= 1 and ss_ben > gs_ben and cai_stem >= 1:
                    # 食伤当令制去孤官杀、财透承接(去杀存财), 日主无根 -> 从财
                    cong, side = '从财格', cai_wx
                elif cai_lead or (cai_ling and _shi(cai)):
                    cong, side = '从财格', cai_wx
                elif ss_stem >= 2 and cai_stem == 0:
                    cong, side = '从儿格', ss_wx
                elif ss_ben > cai_ben:
                    cong, side = '从儿格', ss_wx
                elif ss_ben == cai_ben and cai_stem >= 1:
                    cong, side = '从财格', cai_wx
                elif ss_ben == cai_ben:
                    cong, side = '从儿格', ss_wx
                else:
                    cong, side = '从财格', cai_wx
            elif cai_ling and ss_stem >= 2 and ss_ben >= 1 and cai_stem == 0:
                # 财虽当令, 食伤叠透通根、财藏不透, 发泄在食伤 -> 顺局从儿
                cong, side = '从儿格', ss_wx
            elif cai_ling and _shi(cai):
                cong, side = '从财格', cai_wx
            elif gs_pow and gs_stem >= 1 and cai_ben >= 1 and not ss_ling and ss_stem == 0 and ss_ju == 0:
                # 丁丑壬寅: 壬杀透干、申金财生杀、丑辰湿土通关(食伤不当令不逆局), 气归于杀 -> 从杀用财
                cong, side = '从杀格', gs_wx
            else:
                order = sorted(shi_sides.items(),
                               key=lambda kv: (_fkey(kv[1][0]) if kv[0] != '官杀' else _fkey(gs)),
                               reverse=True)
                top_name, (top_d, top_wx) = order[0]
                if top_name == '官杀':
                    cong, side = ('从杀格' if (gs_ben >= 2 or gs_ju >= 1 or gs_ling or cai_ben >= 1) else '从官格'), gs_wx
                elif top_name == '财':
                    # 食伤叠透而财藏不透=从儿(儿会财局); 财明透成局=从财
                    if ss_pow and ss_stem >= 2 and cai_stem == 0 and not cai_lead:
                        cong, side = '从儿格', ss_wx
                    else:
                        cong, side = '从财格', cai_wx
                elif top_name == '食伤':
                    if cai_lead:
                        cong, side = '从财格', cai_wx
                    elif ss_stem >= 2 and cai_stem == 0 and ss_pow:
                        cong, side = '从儿格', ss_wx
                    elif (cai_ben >= 1 or cai_ju >= 1) and not (ss_stem >= 2 and cai_stem == 0):
                        cong, side = '从财格', cai_wx
                    else:
                        cong, side = '从儿格', ss_wx
                else:
                    cong, side = '从势格', top_wx
                if cong in ('从财格', '从杀格', '从官格', '从儿格') and len(shi_sides) >= 2:
                    keys = sorted(((9, 0, 0) if k == '官杀' else _fkey(v[0]) for k, v in shi_sides.items()),
                                  reverse=True)
                    if keys[0][0] == keys[1][0] and keys[0][1] == keys[1][1] and not (gs_ling or cai_ling or ss_ling):
                        cong, side = '从势格', None
            cstate = 'CANDIDATE' if (virtual_support or root_struck or ke_struck or yin_fanwu or yin_ke2 or jia_xu_sha) else 'CONFIRMED'

    # ---------- 从儿不论身强弱(日主非比劫当令、可带一禄根; 官杀无、食伤成势、无印逆局)----------
    if not cong and not hua_name:
        if (gs_ben == 0 and gs_stem == 0 and yin_ben_eff == 0 and ss_pow and not dm_ling
                and not cai_lead and dm_ben_eff <= 1):
            if cai_stem >= 2 and cai_ben >= 1 and ss_stem >= 1 and ss_ben <= cai_ben + 1:
                # 食伤透干泄身太过(干支同党)、财复透干成众有根, 食伤+财并旺顺克泄 -> 从势
                # (戊戌丁巳火旺木焚顺火土); 食伤当令而不透干(丁巳癸卯木在支)未焚身, 仍专从儿
                # 食伤与财两神并旺、财透干成众(食伤生财顺局), 衰极从其势 -> 从势(戊戌丁巳顺火土)
                cong, side = '从势格', None
            else:
                cong, side = '从儿格', ss_wx
            cstate = 'CONFIRMED' if dm_ben_eff == 0 else 'CANDIDATE'

    # ---------- 气候虚湿寒土假从(辰丑湿土寒冻、火印全无, 土虚不能用, 反顺旺水之财; 见火暖则土能任财而翻转, 故只CANDIDATE)----------
    if not cong and not hua_name and climate and 'XU_SHI_HAN_TU' in (climate.get('structure_flags') or []):
        if _shi(cai) or cai_ju >= 1 or (cai_ben >= 1 and cai_stem >= 1):
            cong, side = '从财格', cai_wx
            cstate = 'CANDIDATE'

    if cong == '从杀格':
        GAN_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
        _YG = set('甲丙戊庚壬'); _dm_y = day_stem in _YG
        def _sha(g):  # 与日主同阴阳=七杀, 异=正官
            return (g in _YG) == _dm_y
        _zg = _zs = _tg = _ts = 0
        _hs = facts.get('hidden_stems', {}) or {}
        for _k in ('year', 'month', 'day', 'hour'):
            _hg = (_hs.get(_k) or [''])[0]
            if _hg and GAN_WX.get(_hg) == gs_wx:
                if _sha(_hg): _zs += 1
                else: _zg += 1
            _tg0 = pillars[_k][0]
            if _k != 'day' and GAN_WX.get(_tg0) == gs_wx:
                if _sha(_tg0): _ts += 1
                else: _tg += 1
        if _zg > _zs or (_zg == _zs and _tg > _ts):
            cong = '从官格'   # 正官(异阴阳)本气支占优, 或支均而正官透干占优; 滴天髓官杀多混称, 否则仍从杀
    if cong:
        note = '日主无本气根、无有根印比，对立方成势顺其势；虚透印比地支不载/孤根被冲拔为假从(CANDIDATE)；从儿不论身强弱；虚湿寒土(辰丑寒冻、火印全无)虽带湿土本气根而寒冻不能用、反顺旺水之财为气候假从(CANDIDATE, 见火暖翻转)；只记结构定性，不判用神成败吉凶'
        out['patterns'].append(_pat('ZP-SPECIAL-CONG', cong, cstate, side, note,
            ['daymaster_root', 'wuxing_power', 'combination_facts']))
        out['cong_type'], out['cong_state'] = cong, cstate

    # ---------- 专旺/一行得气 ----------
    # 本方三合/三会成局: 局内支本气若为官杀/财, 被合化为本方(官杀化比劫), 专旺判定扣除(合局化破)
    gs_ben_zw, cai_ben_zw = gs_ben, cai_ben
    _cf = facts.get('combination_facts', {}) or {}
    for _items in (_cf.get('sanhe', []), _cf.get('sanhui', [])):
        for _it in _items:
            _m = re.match(r'^([子丑寅卯辰巳午未申酉戌亥])([子丑寅卯辰巳午未申酉戌亥])([子丑寅卯辰巳午未申酉戌亥]).*?([金木水火土])', str(_it))
            if not _m: continue
            _b1, _b2, _b3, _jwx = _m.groups()
            if _jwx != dm_wx: continue
            for _br in (_b1, _b2, _b3):
                _bw = BRANCH_WX.get(_br)
                if _bw == KE_ME[dm_wx] and str(gs.get('root_detail', {}).get(_br, '')).startswith(('BEN',)):
                    gs_ben_zw -= 1
                elif _bw == KE[dm_wx] and str(cai.get('root_detail', {}).get(_br, '')).startswith(('BEN',)):
                    cai_ben_zw -= 1
    gs_ben_zw = max(0, gs_ben_zw); cai_ben_zw = max(0, cai_ben_zw)
    guo_xie = (ss_stem >= 2 and ss_ben >= 1)   # #PCT-MARK 食伤透干有根成党=过泄/两气成象, 不判纯一行专旺

    if not hua_name and dm_ben_eff >= 1:
        no_guan = (gs_ben_zw == 0 and gs_stem == 0 and gs_ju == 0)
        no_cai = (cai_ben_zw == 0 and cai_stem == 0 and cai_ju == 0)
        gs_hehua = False
        if tian_he:
            for hp in tian_he.get('he_pairs', []):
                if hp.get('huashen_wuxing') == dm_wx:
                    gs_hehua = True
        # 成方(三会/三合本方, dm_ju>=1)力量最大: 官杀无本气不透、财仅孤一本气(<=1)且无财局,
        # 则财官伏而受当令本方所制(干多不如根重, 待运引发), 不真破成方 -> CONFIRMED(己巳辛未支类南方)
        # 克泄之神(食伤/财)叠透干>=2成党=泄气太过/伏神透干, 非纯一行(丁亥丁未食神用印正格);
        # 只1透或藏支伏制、顺泄不破(专旺本喜食伤顺泄, 如润下透一甲、炎上透一己)
        chengfang_gu = (dm_ju >= 1 and gs_ben_zw == 0 and gs_ju == 0 and gs_stem == 0
                        and cai_ben_zw <= 1 and cai_ju == 0 and ss_stem < 2 and cai_stem < 2)
        # 官杀有本气(真克)硬门槛排除; 虚浮无根(干多不如根重)不真破 -> CANDIDATE
        if (not guo_xie) and ((gs_ben_zw == 0 and gs_ju == 0 and no_cai and no_guan and (dm_ju >= 1 or party >= 4))
                              or chengfang_gu):
            zw = ZHUANWANG_NAME.get(dm_wx)
            out['patterns'].append(_pat('ZP-SPECIAL-ZHUANWANG', zw, 'CONFIRMED', dm_wx,
                '日主有根、得印比党众(party>=4)或会/合成方局，官杀财无本气不透，一行得气；只记专旺结构，不判贵贱吉凶',
                ['combination_facts', 'wuxing_power']))
            out['zhuanwang'] = zw
        elif (not guo_xie) and gs_ben_zw == 0 and gs_ju == 0 and cai_ben_zw <= 1 and party >= 3:
            zw = ZHUANWANG_NAME.get(dm_wx)
            out['patterns'].append(_pat('ZP-SPECIAL-ZHUANWANG', zw, 'CANDIDATE', dm_wx,
                '日主得印比党众成势(party>=3)，官杀/财仅虚透无根(或官杀被合化为本方如戊癸合火助刃)、财至多一余气；专旺待虚浮克泄被制化确认',
                ['wuxing_power', 'tian_he']))
            out['zhuanwang'] = zw

    # ---------- 母多灭子/印势漂没(CANDIDATE)----------
    # 印党余气/半合重重(本气不足3但余气/半合党众>=4)、日主无本气根、食伤全无泄路 -> 金多水浊/土重金埋
    yin_party_all = yin_ben + int(yin.get('zhong_n', 0)) + int(yin.get('yu_n', 0)) + int(yin.get('banhe_n', 0))
    # 财透干有本气根、印未成三合三会局 = 财能破印救应(壬戌壬子戊土砥柱制水); 印成局则虚财/湿土不制仍灭
    cai_zhi_yin = (cai_stem >= 1 and cai_ben >= 1 and yin_ju == 0)
    # 印本气+余气/半合党众、日主无本气根、食伤全无泄、官杀不透(非杀印相生)、无财破印 -> 金多水浊/土重金埋
    mumie_yu = (yin_ben >= 1 and yin_party_all >= 4 and ss_ben == 0 and ss_stem == 0 and ss_ju == 0
                and gs_stem == 0 and not cai_zhi_yin)
    if dm_ben_eff == 0 and (yin_ju >= 1 or yin_ben >= 3 or mumie_yu) and not out['cong_type'] and not hua_name:
        out['patterns'].append(_pat('ZP-SPECIAL-MUMIE', '母多灭子/印势漂没', 'CANDIDATE', yin_wx,
            '印绶成势而日主无本气根不受生(土重金埋/水多木漂)；木火通明(相令能受生)与印势漂没的pair反转须交气候/天干性情层细分，此处不据印多判身旺弱',
            ['wuxing_power']))
        out['mu_mie'] = '母多灭子/印势漂没'

    return out
