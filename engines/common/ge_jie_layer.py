# -*- coding: utf-8 -*-
"""格局成格判定层.
PZZQ原文(255/258/241行): 八格成格/破格.
第一步已落地: 食神生财格成格+成格之神为喜.
第二步(第一步,可控): 伤官带煞无财格 -- 只标格体(伤官+煞), 不动病药层.
  PZZQ255: "伤官带煞而无财...伤官格成也". 杀是格体非破格; 身弱用印(第二步改).
双层属性: 格体(格局层) / 忌神(日主层) 并存, 第二步动病药层."""
from typing import Any, Dict

GAN_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
YINYANG = {'甲':1,'乙':0,'丙':1,'丁':0,'戊':1,'己':0,'庚':1,'辛':0,'壬':1,'癸':0}
DM_LU = {'甲':'寅','乙':'卯','丙':'巳','丁':'午','戊':'巳','己':'午','庚':'申','辛':'酉','壬':'亥','癸':'子'}
DM_WANG = {'甲':'卯','乙':'寅','丙':'午','丁':'巳','戊':'午','己':'巳','庚':'酉','辛':'申','壬':'子','癸':'亥'}
SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
CAI = {'正财','偏财'}
ZHI_WX = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}

# 阴干在阳令的借根剥离表(CASE_LEVEL才生效; 丁巳/辛申/癸亥 NO_EVIDENCE不启用)
# SFTK: 乙日寅月, 阳木得令阴木反弱. 寅是甲禄不是乙根.
_YIN_YANG_JIEGEN = {('乙','寅'): True}
# 地支本气干(禄=同阴阳日主根; 刃支本气=劫财, 异阴阳非日主根)
ZHI_BEN_GAN = {'子':'癸','丑':'己','寅':'甲','卯':'乙','辰':'戊','巳':'丙',
               '午':'丁','未':'己','申':'庚','酉':'辛','戌':'戊','亥':'壬'}

def dm_tier(wp, dg, month_zhi, pillars=None):
    """日主视角旺衰tier: 剥借根后再判element_power_tier.
    同阴阳判据(PZZQ"刃乃劫我正财之神, 不善之神须逆势驾驭"): 异阴阳本气支(刃/劫财禄)
    是比劫非日主根 -> 剥; 仅同阴阳本气支(禄)计日主根. 中余气维度待依赖.
    临时补丁一/二的切换点: 修复后财格过滤改用此函数."""
    import copy
    from engines.common.transit_power import element_power_tier
    wx = GAN_WX.get(dg, '')
    if not wx: return {'tier':0,'name':'衰'}
    wp2 = copy.deepcopy(wp)
    dm_e = wp2['wuxing_power'].get(wx, {})
    if pillars:
        _ben_self = sum(1 for _pos in ('year','month','day','hour')
                        if ZHI_BEN_GAN.get(pillars[_pos][1]) == dg)
        dm_e['ben_n'] = _ben_self
    elif (dg, month_zhi) in _YIN_YANG_JIEGEN:
        dm_e['ben_n'] = max(0, dm_e.get('ben_n',0) - 1)
    return element_power_tier(wp2, wx)

def ten_god(dg, stem):
    if dg not in GAN_WX or stem not in GAN_WX:
        return ''
    dwx, swx = GAN_WX[dg], GAN_WX[stem]
    same = YINYANG[dg] == YINYANG[stem]
    if swx == dwx:
        return '比肩' if same else '劫财'
    if SHENG[dwx] == swx:
        return '食神' if same else '伤官'
    if KE[dwx] == swx:
        return '偏财' if same else '正财'
    if SHENG[swx] == dwx:
        return '偏印' if same else '正印'
    if KE[swx] == dwx:
        return '七杀' if same else '正官'
    return ''

def _gans(pillars):
    return [pillars[k][0] for k in ('year','month','day','hour') if k in pillars]

def _zhis(pillars):
    return [pillars[k][1] for k in ('year','month','day','hour') if k in pillars]

def build_ge_cheng(facts: Dict[str, Any]) -> Dict[str, Any]:
    pillars = facts.get('pillars', {}) or {}
    dg = facts.get('day_stem', '') or ''
    gans = _gans(pillars)
    zhis = _zhis(pillars)

    # 从格CONFIRMED优先(覆盖正格): 日主无根+印比虚浮无根+临绝(子平真诠'四柱无可扶抑')
    # CANDIDATE不覆盖, 走正格判定(v1/v2误报=无差别覆盖, 已回退)
    try:
        from engines.common.special_pattern import build_special_patterns
        _wp0 = facts.get('wuxing_power', {}) or {}
        _sp0 = build_special_patterns(pillars, facts, _wp0)
        if _sp0.get('cong_type') and _sp0.get('cong_state') == 'CONFIRMED':
            _cwx_map = {'从杀格': None, '从官格': None, '从财格': None, '从儿格': None}
            _gs_wx = (facts.get('wuxing_power', {}) or {}).get('wuxing_power', {})
            _dm_wx = (facts.get('wuxing_power', {}) or {}).get('daymaster_element', '')
            _SH = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
            _KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
            _KE_M = {'木':'金','金':'火','火':'水','水':'土','土':'木'}
            _ss_wx = _SH.get(_dm_wx,''); _cai_wx = _KE.get(_dm_wx,''); _gs0 = _KE_M.get(_dm_wx,'')
            _ct = _sp0['cong_type']
            _side = {'从杀格': _gs0, '从官格': _gs0, '从财格': _cai_wx, '从儿格': _ss_wx}.get(_ct)
            # 从格破格检查(PZZQ4936/4941/4943/4944):
            #   从财格: 比劫透干争财(无食伤化)破格; 印通根生身破格
            #   从杀格: 食伤制杀破格; 印泄杀气破格
            # 排除day干按位置(索引2), 不能按值(四干同值时按值排除会全滤掉)
            _g3 = [g for i, g in enumerate(gans) if i != 2]
            _bijie = [g for g in _g3 if ten_god(dg, g) in ('比肩','劫财')]
            _shishang = [g for g in _g3 if ten_god(dg, g) in ('食神','伤官')]
            _yin_tou = [g for g in _g3 if ten_god(dg, g) in ('正印','偏印')]
            _po = []
            _not_cong = False
            if _ct == '从财格':
                # 比劫有根=帮身任财(正格财格身弱用比, QT-0057甲木辰中乙木中气根"财旺用比富贵"), 非破格
                # 比劫无根=虚浮逆势(从财格忌比劫, DT-0032辛金卯月临绝"四金临绝岂无成立乎"), 破格报病
                if _bijie and not _shishang:
                    _dm_rd = ((facts.get('wuxing_power',{}).get('wuxing_power',{}) or {}).get(_dm_wx,{}) or {}).get('root_detail',{}) or {}
                    _dm_bn = int((facts.get('wuxing_power',{}).get('wuxing_power',{}) or {}).get(_dm_wx,{}).get('ben_n',0) or 0)
                    if not (_dm_rd or _dm_bn >= 1):
                        _po = [{'type':'组合','required':['比肩','劫财']}]
                # 印透干+印原始本气根=不从(PZZQ4941"从财格而有印,须看印是否通根"): 不从->走正格(财格佩印), 非破格
                # 印虚透无根=假从仍从
                _YIN_WX = {v: k for k, v in _SH.items()}.get(_dm_wx, '')
                _yin_bn = int(((facts.get('wuxing_power',{}).get('wuxing_power',{}) or {}).get(_YIN_WX,{}) or {}).get('ben_n',0) or 0)
                if _yin_tou and _yin_bn >= 1:
                    _not_cong = True
            if _ct == '从杀格':
                # 从杀格破格(PZZQ"有弃命从煞者...若有伤食则煞受制而不从,有印则印以化煞而不从"):
                #   伤食透干+伤食有本气根(制煞有力)->破格报病; 伤食虚透无根=假从不破格(DT-0109己土伤官虚透无根)
                _hs0 = facts.get('hidden_stems', {}) or {}
                _ben_gans = [(_hs0.get(k) or [''])[0] for k in ('year','month','day','hour') if _hs0.get(k)]
                _ss_ben = any(g in _ben_gans for g in _shishang)
                if bool(_shishang) and _ss_ben:
                    _po = [{'type':'组合','required':['食神','伤官']}]
                # 印透化煞=不从(PZZQ"有印则印以化煞而不从"): 不从->走正格(杀印相生), 非破格
                if _yin_tou:
                    _not_cong = True
            if _not_cong:
                pass
            else:
                facts['ge_cheng'] = {
                    'ge': _ct if not _po else _ct + '(破格)',
                    'xi_wx': [],
                    'ti_wx': [] if _po else ([_side] if _side else []),
                    'overpower_combo': 6,
                    'zhi_wx': [], 'hua_wx': [],
                    'po_ge': _po,
                    'rule': ('从格破格: 从财格比劫透干无根争财/从杀格伤食有根制煞->破格; 破格后ti_wx不豁免, 病药层照跑'
                             if _po else
                             '从格CONFIRMED优先(覆盖正格): 日主无根+印比虚浮无根+临绝->从格; ti_wx=所从之神'),
                }
                return facts
    except Exception:
        pass

    # 1) 食神生财格: 月令食神entry + 食神透 + 财透 + 日主本气禄旺根
    entry = facts.get('shishen_entry', {}) or {}
    if entry.get('is_entry'):
        shishen_gans = [g for g in gans if ten_god(dg, g) == '食神']
        cai_gans = [g for g in gans if ten_god(dg, g) in CAI]
        self_root = (DM_LU.get(dg) in zhis) or (DM_WANG.get(dg) in zhis)
        if shishen_gans and cai_gans and self_root:
            facts['ge_cheng'] = {
                'ge': '食神格',
                'xi_wx': [GAN_WX[shishen_gans[0]]],
                'xi_gan': sorted(set(shishen_gans)),
                'ti_wx': [GAN_WX[shishen_gans[0]]],  # 食神是格体
                'overpower_combo': 6,   # UNVERIFIED
                'zhi_wx': [],  # 制神: 枭(印)
                'hua_wx': [],  # 化神: 无
                'po_ge': [{'type':'组合','required':['偏印']}, {'type':'组合','required':['正财','偏财','七杀']}],  # PZZQ258: 食神逢枭/生财露煞
                'rule': 'PZZQ255: 食神生财+身旺 -> 食格成; 成格之神(食神)为喜; 破格: 枭夺食/生财露煞',
            }
            return facts
        # 路径二: 食带煞无财弃食就煞透印. PZZQ255: "或食带煞而无财, 弃食就煞而透印, 食格成也"
        sha_gans = [g for g in gans if ten_god(dg, g) == '七杀']
        yin_gans = [g for g in gans if ten_god(dg, g) in ('正印', '偏印')]
        # "弃食"判据: 食神须虚透无根(四支本气无同干)才算弃食; 食神有本气根正在制杀=未弃, 不走此路径
        _shi_qishi = not any(ZHI_BEN_GAN.get(z) in shishen_gans for z in zhis)
        if shishen_gans and sha_gans and not cai_gans and yin_gans and _shi_qishi:
            facts['ge_cheng'] = {
                'ge': '食神格(带煞无财)',
                'xi_wx': sorted(set(GAN_WX[g] for g in yin_gans)),
                'ti_wx': sorted(set([GAN_WX[sha_gans[0]], GAN_WX[yin_gans[0]]])),
                'overpower_combo': 6,
                'zhi_wx': sorted(set(GAN_WX[g] for g in yin_gans)),  # 制神: 印(弃食就煞, 印制食伤为药)
                'hua_wx': [],
                'po_ge': [{'type':'组合','required':['正财','偏财']}],  # PZZQ258: 生财露煞
                'rule': 'PZZQ255: 食带煞无财弃食就煞透印 -> 食格成; 格体=煞+印; 喜神=印(弃食就煞); 破格: 生财露煞',
            }
            return facts

    # 1.5) 伤官佩印格: 月令伤官 + 印透. PZZQ255: "伤官佩印而伤官旺,印有根".
    # 伤官是格体, 不报泄气病(UNVERIFIED: 伤官旺/印有根判据).
    sg_entry0 = facts.get('shangguan_entry', {}) or {}
    if sg_entry0.get('is_entry'):
        yin_gans0 = [g for g in gans if ten_god(dg, g) in ('正印', '偏印')]
        shangguan_gans0 = [g for g in gans if ten_god(dg, g) == '伤官']
        if yin_gans0 and shangguan_gans0:
            sg_wx0 = facts.get('month_qi_element', '') or ''
            facts['ge_cheng'] = {
                'ge': '伤官格(佩印)', 'xi_wx': sorted(set(GAN_WX[g] for g in yin_gans0)),
                'ti_wx': [sg_wx0],
                'overpower_combo': 6,
                'zhi_wx': [], 'hua_wx': [],
                'po_ge': [{'type':'组合','required':['正财','偏财']}],  # PZZQ258: 伤官生财带煞
                'rule': 'PZZQ255: 伤官佩印伤旺印根->伤官格成; 伤官是格体不报泄气(UNVERIFIED: 伤官旺/印有根判据); 破格: 生财带煞',
            }
            return facts

    # 2) 伤官带煞无财格: 月令伤官entry + 七杀透 + 无财透. 只标格体, 不动病药层.
    sg_entry = facts.get('shangguan_entry', {}) or {}
    if sg_entry.get('is_entry'):
        qisha_gans = [g for g in gans if ten_god(dg, g) == '七杀']
        cai_gans = [g for g in gans if ten_god(dg, g) in CAI]
        yin_gans = [g for g in gans if ten_god(dg, g) in ('正印', '偏印')]
        if qisha_gans and not cai_gans:
            # 格体五行 = 伤官本气(月令) + 七杀透干
            sg_wx = facts.get('month_qi_element', '') or ''
            sha_wx = GAN_WX[qisha_gans[0]]
            facts['ge_cheng'] = {
                'ge': '伤官格(带煞无财)',
                'xi_wx': sorted(set(GAN_WX[g] for g in yin_gans)),
                'ti_wx': sorted(set([w for w in (sg_wx, sha_wx) if w])),
                'overpower_combo': 6,
                'zhi_wx': [], 'hua_wx': [GAN_WX[yin_gans[0]]] if yin_gans else [],
                'po_ge': [{'type':'组合','required':['正财','偏财']}],  # PZZQ258: 财露
                'rule': 'PZZQ255: 伤官带煞无财 -> 伤官格成; 杀是格体非破格; 身弱用印; 破格: 财露',
            }
            return facts

    # 3) 六格扩写: PZZQ255原文, 只定格体, 病药层不消费.
    #    纪律: ti_wx=[] 不触发格体过滤, 仅记录格名; 制化关系待格局层扩全后通用落.
    mqi_god = facts.get('month_qi_ten_god', '') or ''
    mqe = facts.get('month_qi_element', '') or ''

    def _has(g):
        return g in gans
    def _god_gans(god):
        return [g for g in gans if ten_god(dg, g) == god]

    # 正官格: 官逢财印又无刑冲破害. 官透 + 财印辅助 + 无伤官克
    if mqi_god == '正官':
        guan_gans = _god_gans('正官')
        if guan_gans:
            cai_gans = _god_gans('正财') + _god_gans('偏财')
            yin_gans = _god_gans('正印') + _god_gans('偏印')
            shangguan = _god_gans('伤官')
            # PZZQ258: 官逢刑冲破格. 官星受冲->不成格(破格).
            guan_chong = facts.get('target_relation_facts', {}).get('官星受冲', False)
            if (cai_gans or yin_gans) and not shangguan and not guan_chong:
                facts['ge_cheng'] = {
                    'ge': '正官格', 'xi_wx': sorted(set(GAN_WX[g] for g in cai_gans+yin_gans)),
                    'ti_wx': [GAN_WX[guan_gans[0]]],
                    'overpower_combo': 6,
                    'zhi_wx': [], 'hua_wx': [],
                    'po_ge': [{'type':'组合','required':['伤官']}, {'type':'地支','branch_cond':'刑冲'}],
                    'rule': 'PZZQ255: 官逢财印又无刑冲破害->官格成; 官是格体非杀病; 喜神=财印; 破格: 伤官克/刑冲',
                }
                return facts
            # 默认输出：月令正官+官透，但不满足成格条件（无财印辅助）
            # 败格条件：伤官克/刑冲——败格时不默认输出
            if not shangguan and not guan_chong:
                facts['ge_cheng'] = {
                    'ge': '正官格', 'xi_wx': [],
                    'ti_wx': [GAN_WX[guan_gans[0]]],
                    'overpower_combo': 6,
                    'zhi_wx': [], 'hua_wx': [],
                    'po_ge': [{'type':'组合','required':['伤官']}, {'type':'地支','branch_cond':'刑冲'}],
                    'rule': 'PZZQ255: 正官格; 官是格体; 破格: 伤官克/刑冲',
                }
                return facts
        # 食神制杀格：月令正官+无正官透+透干七杀+食伤透
        # PZZQ255: 身强七煞逢制(食制)->煞格成; 食伤是制杀格体
        sha_gans_zhi = _god_gans('七杀')
        shi_gans_zhi = _god_gans('食神') + _god_gans('伤官')
        if sha_gans_zhi and shi_gans_zhi:
            ti_list = sorted(set([GAN_WX[sha_gans_zhi[0]], GAN_WX[shi_gans_zhi[0]]]))
            facts['ge_cheng'] = {
                'ge': '食神制杀格', 'xi_wx': [],
                'ti_wx': ti_list,
                'overpower_combo': 6,
                'zhi_wx': [GAN_WX[shi_gans_zhi[0]]],
                'hua_wx': [],
                'po_ge': [{'type':'组合','required':['正财','偏财']}],
                'rule': 'PZZQ255: 月令官+透杀+食伤透->食神制杀格成; 食伤+煞是格体; 破格: 财透无制',
            }
            return facts

    # 财格: 财生官旺/财逢食生身强带比/财格透印. 财透 + (官透|食透+身旺|印透)
    # 格体过滤前提: 身强(日主禄旺根). 身弱财格不成, 财病照报.
    if mqi_god in ('正财', '偏财'):
        cai_gans = _god_gans('正财') + _god_gans('偏财')
        guan_gans = _god_gans('正官')
        shi_gans = _god_gans('食神')
        yin_gans = _god_gans('正印') + _god_gans('偏印')
        self_root = (DM_LU.get(dg) in zhis) or (DM_WANG.get(dg) in zhis)
        # PZZQ1113: "财生官旺...月令星旺,四柱有官" -- 财当令+官透即可, 不要求财透(UNVERIFIED: 官无根/官杀混杂)
        if guan_gans or cai_gans or (shi_gans and self_root) or yin_gans:
                # PZZQ1113: 财生官旺/财格透印不要求身旺. 财格成->财过滤, 不要求dm_tier>=2.
                # 财透->ti_wx=[财透干五行]; 财不透(月令财)->ti_wx=[月令本气五行]
                if cai_gans:
                    _ti = [GAN_WX[cai_gans[0]]]
                else:
                    _ti = [facts.get('month_qi_element', '')]
                # 喜神: 财逢食生(食伤)/财生官(官)/财格透印(印) 透干为喜(PZZQ1113)
                _sg_gans = _god_gans('食神') + _god_gans('伤官')
                _xi = sorted(set(GAN_WX[g] for g in _sg_gans+guan_gans+yin_gans))
                facts['ge_cheng'] = {
                    'ge': '财格', 'xi_wx': _xi, 'ti_wx': _ti,
                    'overpower_combo': 6,
                    'zhi_wx': [GAN_WX.get(guan_gans[0],'')] if guan_gans else [],  # 制神: 官(财生官)
                    'hua_wx': [],
                    'po_ge': [{'type':'力量','power_cond':'财轻比重'}, {'type':'组合','required':['正财','偏财','七杀']}],  # PZZQ258: 财轻比重/财透七煞
                    'rule': 'PZZQ1113: 财生官/财逢食生身强/财格透印->财格成; 财格成->财过滤不要求身旺; 破格: 比劫夺财/财透煞',
                }
                return facts
        # 默认输出：月令财，但不满足成格条件
        # 败格条件：财轻比重/财透七煞——败格时不默认输出
        sha_gans_def = _god_gans('七杀')
        if not sha_gans_def:
            _ti_def = [facts.get('month_qi_element', '')]
            _sg_gans_def = _god_gans('食神') + _god_gans('伤官')
            _xi_def = sorted(set(GAN_WX[g] for g in _sg_gans_def))
            facts['ge_cheng'] = {
                'ge': '财格', 'xi_wx': _xi_def, 'ti_wx': _ti_def,
                'overpower_combo': 6,
                'zhi_wx': [], 'hua_wx': [],
                'po_ge': [{'type':'力量','power_cond':'财轻比重'}, {'type':'组合','required':['正财','偏财','七杀']}],
                'rule': 'PZZQ255: 财格; 财是格体; 破格: 比劫夺财/财透煞',
            }
            return facts

    # 印格: 印轻逢煞/官印双全/身印两旺用食伤泄气/印多逢财财透根轻
    # 先落官印双全路径: 月令印+官透+印透+官有根+无杀透.
    # 官无根=官虚浮生印无力(UNVERIFIED); 杀透=官杀混杂破格(PZZQ258).
    if mqi_god in ('正印', '偏印'):
        yin_gans = _god_gans('正印') + _god_gans('偏印')
        cai_gans = _god_gans('正财') + _god_gans('偏财')
        guan_gans = _god_gans('正官')
        sha_gans = _god_gans('七杀')
        # PZZQ1113: 官印双全=月令印+官透+官有根+无杀透. 印是格体.
        if guan_gans and not sha_gans:
            guan_wx = GAN_WX[guan_gans[0]]
            guan_root = any(ZHI_WX.get(z,'')==guan_wx for z in zhis)
            if guan_root:
                yin_wx = GAN_WX[yin_gans[0]] if yin_gans else (facts.get('month_qi_element','') or '')
                facts['ge_cheng'] = {
                    'ge': '印格(官印双全)', 'xi_wx': [guan_wx],
                    'ti_wx': [yin_wx],
                    'overpower_combo': 6,
                    'zhi_wx': [], 'hua_wx': [],
                    'po_ge': [{'type':'组合','required':['正财','偏财']}],  # PZZQ258: 印轻逢财
                    'rule': 'PZZQ255: 官印双全+官有根+无杀透->印格成; 印是格体; 喜神=官; 破格: 财破印',
                }
                return facts
        # PZZQ1113: 印轻逢煞=月令印+煞透+印不透. 印是格体(UNVERIFIED: 印轻判据=印不透)
        if sha_gans and not yin_gans:
            yin_wx = facts.get('month_qi_element','') or ''
            facts['ge_cheng'] = {
                'ge': '印格(印轻逢煞)', 'xi_wx': [GAN_WX[sha_gans[0]]],
                'ti_wx': [yin_wx],
                'overpower_combo': 6,
                'zhi_wx': [], 'hua_wx': [],
                'po_ge': [{'type':'组合','required':['正财','偏财']}],  # PZZQ258: 印轻逢财
                'rule': 'PZZQ255: 印轻逢煞+印不透->印格成; 印是格体; 喜神=煞(煞生印); 破格: 财破印',
            }
            return facts
        # PZZQ1113: 印多逢财财透根轻=月令印+财透. 印是格体, 不报印多埋子(UNVERIFIED: 财透根轻判据)
        if cai_gans:
            yin_wx = GAN_WX[yin_gans[0]] if yin_gans else (facts.get('month_qi_element','') or '')
            facts['ge_cheng'] = {
                'ge': '印格(印多逢财)', 'xi_wx': sorted(set(GAN_WX[g] for g in cai_gans)),
                'ti_wx': [yin_wx],
                'overpower_combo': 6,
                'zhi_wx': [], 'hua_wx': [],
                'po_ge': [{'type':'组合','required':['正财','偏财']}],  # PZZQ258: 印轻逢财
                'rule': 'PZZQ255: 印多逢财财透根轻->印格成; 印是格体; 喜神=财(财损印); 破格: 财破印',
            }
            return facts
        yin_wx_default = GAN_WX[yin_gans[0]] if yin_gans else (facts.get('month_qi_element','') or '')
        _yin_xq = sorted(set(GAN_WX[g] for g in _god_gans('食神')+_god_gans('伤官')))
        facts['ge_cheng'] = {
            'ge': '印格', 'xi_wx': _yin_xq, 'ti_wx': [yin_wx_default] if yin_wx_default else [],
            'overpower_combo': 6,
            'zhi_wx': [], 'hua_wx': [],
            'po_ge': [{'type':'组合','required':['正财','偏财']}],
            'rule': 'PZZQ255: 印格成; 印是格体; 身印旺食伤泄秀为喜; 破格: 财破印',
        }
        return facts

    # 专旺/从格兜底(P0接线v3): 正格不成时才看专旺/从格
    if not facts.get('ge_cheng') or facts['ge_cheng'].get('ge','') == '无格':
        try:
            from engines.common.special_pattern import build_special_patterns
            wp = facts.get('wuxing_power', {}) or {}
            sp = build_special_patterns(pillars, facts, wp)
            if sp.get('zhuanwang'):
                dm_wx = GAN_WX.get(dg, '')
                facts['ge_cheng'] = {
                    'ge': sp['zhuanwang'], 'xi_wx': [],
                    'ti_wx': [dm_wx],
                    'overpower_combo': 6,
                    'zhi_wx': [], 'hua_wx': [],
                    'po_ge': [],
                    'rule': '专旺/从格兜底(P0): 正格不成->专旺格; ti_wx=[日主五行]',
                }
                return facts
            if sp.get('cong_type') and sp.get('cong_state') in ('CONFIRMED', 'CANDIDATE'):
                # 从格格体五行=所从之神
                _cong_wx_map = {'从杀格': 'gs_wx', '从官格': 'gs_wx',
                                '从财格': 'cai_wx', '从儿格': 'ss_wx'}
                _cong_key = _cong_wx_map.get(sp['cong_type'], '')
                _cong_wx = ''
                if _cong_key == 'gs_wx':
                    _cong_wx = facts.get('wuxing_power', {}).get('_gs_wx', '')
                elif _cong_key == 'cai_wx':
                    _cong_wx = facts.get('wuxing_power', {}).get('_cai_wx', '')
                elif _cong_key == 'ss_wx':
                    _cong_wx = facts.get('wuxing_power', {}).get('_ss_wx', '')
                # 从格所从五行从wp反推
                _wp = facts.get('wuxing_power', {}) or {}
                _dm_wx0 = GAN_WX.get(dg, '')
                _sh, _ke = {'木':'火','火':'土','土':'金','金':'水','水':'木'}, {'木':'土','土':'水','水':'火','火':'金','金':'木'}
                _sheng_me, _ke_me = {'木':'水','火':'木','土':'火','金':'土','水':'金'}, {'木':'金','金':'火','火':'水','水':'土','土':'木'}
                if sp['cong_type'] in ('从杀格','从官格'):
                    _cong_wx = _ke_me.get(_dm_wx0, '')
                    # PZZQ5000"从杀忌食伤"; 财生煞顺旺势为喜
                    _xi_cong = [_ke.get(_dm_wx0, '')]
                elif sp['cong_type'] == '从财格':
                    _cong_wx = _ke.get(_dm_wx0, '')
                    # PZZQ4943"原有食伤则能化比劫而生财": 食伤化劫生财为喜
                    _xi_cong = [_sh.get(_dm_wx0, '')]
                elif sp['cong_type'] == '从儿格':
                    _cong_wx = _sh.get(_dm_wx0, '')
                    # PZZQ4960"以见财为美": 财为喜
                    _xi_cong = [_ke.get(_dm_wx0, '')]
                else:
                    _xi_cong = []
                facts['ge_cheng'] = {
                    'ge': '从格(' + sp['cong_type'] + ')', 'xi_wx': sorted(set(w for w in _xi_cong if w)),
                    'ti_wx': [_cong_wx] if _cong_wx else [],
                    'overpower_combo': 6,
                    'zhi_wx': [], 'hua_wx': [],
                    'po_ge': [],
                    'rule': '专旺/从格兜底(P0): 正格不成->从格; ti_wx=所从之神五行; 喜神=从财食伤/从杀从官从儿财(PZZQ4943/4960)',
                }
                return facts
        except Exception:
            pass

    # 七煞格: 身强七煞逢制. 破格: 七煞逢财无制.
    # 制=食神制 OR 印化. 破格优先于成格.
    qisha_e = facts.get('qisha_entry', {}) or {}
    if qisha_e.get('is_entry'):
        sha_gans = _god_gans('七杀')
        if sha_gans:
            shi_gans = _god_gans('食神')
            yin_gans = _god_gans('正印') + _god_gans('偏印')
            cai_gans = _god_gans('正财') + _god_gans('偏财')
            has_zhi = bool(shi_gans or yin_gans)
            # 破格: 财透+无制
            if cai_gans and not has_zhi:
                facts['ge_cheng'] = {
                    'ge': '七煞格(破格)', 'xi_wx': [], 'ti_wx': [],
                    'overpower_combo': 6,
                    'zhi_wx': [], 'hua_wx': [],
                    'po_ge': [{'type':'组合','required':['正财','偏财']}],
                    'rule': 'PZZQ258: 七煞逢财无制->破格; 杀病照报',
                }
                return facts
            # 成格: 身强+制
            if has_zhi:
                _mz = pillars.get('month', ['',''])[1] if 'month' in pillars else ''
                _dt = dm_tier(facts.get('wuxing_power',{}), dg, _mz, pillars)
                if _dt['tier'] >= 2:
                    sha_wx = GAN_WX[sha_gans[0]]
                    facts['ge_cheng'] = {
                        'ge': '七煞格(逢制)', 'xi_wx': sorted(set(GAN_WX[g] for g in shi_gans+yin_gans)),
                        'ti_wx': [sha_wx],
                        'overpower_combo': 6,
                        'zhi_wx': [GAN_WX[shi_gans[0]]] if shi_gans else [],
                        'hua_wx': [GAN_WX[yin_gans[0]]] if yin_gans else [],
                        'po_ge': [{'type':'组合','required':['正财','偏财']}],
                        'rule': 'PZZQ255: 身强七煞逢制(食制/印化)->煞格成; 煞是格体不报杀重病; 破格: 财透无制',
                    }
                    return facts
            # 不成格: 哑巴标签
            facts['ge_cheng'] = {
                'ge': '七煞格', 'xi_wx': sorted(set(GAN_WX[g] for g in shi_gans+yin_gans)),
                'ti_wx': [GAN_WX[sha_gans[0]]] if sha_gans else [],
                'overpower_combo': 6,
                'zhi_wx': [], 'hua_wx': [],
                'po_ge': [{'type':'组合','required':['正财','偏财']}],
                'rule': 'PZZQ255: 七煞格; 煞是格体; 喜神=食伤(制)/印(化); 破格: 财透无制',
            }
            return facts

    # 阳刃格: 阳刃透官煞而露财印, 不见伤官. 刃entry + 官杀透
    # 配合神(官煞)入ti_wx: 官煞制刃是喜神不报杀重病. 比劫不入ti_wx, 比劫夺财病照报.
    yr_e = facts.get('yangren_entry', {}) or {}
    if yr_e.get('is_entry'):
        ks_gans = _god_gans('正官') + _god_gans('七杀')
        sg = _god_gans('伤官')
        if ks_gans and not sg:
            ks_wx = sorted(set([GAN_WX[g] for g in ks_gans]))
            _yr_cai = _god_gans('正财')+_god_gans('偏财')
            _yr_yin = _god_gans('正印')+_god_gans('偏印')
            facts['ge_cheng'] = {
                'ge': '阳刃格', 'xi_wx': sorted(set(GAN_WX[g] for g in ks_gans+_yr_cai+_yr_yin)),
                'ti_wx': ks_wx,
                'overpower_combo': 6,
                'zhi_wx': ks_wx,  # 制神: 官煞
                'hua_wx': [],
                'po_ge': [{'type':'缺失','forbidden':['正官','七杀']}],  # PZZQ258: 阳刃无官煞
                'rule': 'PZZQ255: 阳刃透官煞露财印不见伤官->刃格成; 官煞制刃是喜神; 破格: 无官煞',
            }
            return facts

    # 建禄月劫格: 透官逢财印/透财逢食伤/透煞遇制伏.
    # 配合神(官/财食伤/煞)入ti_wx: 配合神是喜神不报病. 比劫不入ti_wx.
    jl_e = facts.get('jianlu_yuejie_entry', {}) or {}
    if jl_e.get('is_entry'):
        guan = _god_gans('正官')
        cai = _god_gans('正财') + _god_gans('偏财')
        shi = _god_gans('食神') + _god_gans('伤官')
        sha = _god_gans('七杀')
        yin = _god_gans('正印') + _god_gans('偏印')
        ti_wx = []
        if guan and (cai or yin):
            ti_wx.append(GAN_WX[guan[0]])
        if cai and shi:
            for g in cai + shi:
                if GAN_WX[g] not in ti_wx:
                    ti_wx.append(GAN_WX[g])
        if sha and shi:
            if GAN_WX[sha[0]] not in ti_wx:
                ti_wx.append(GAN_WX[sha[0]])
        if ti_wx:
            facts['ge_cheng'] = {
                'ge': '建禄月劫格', 'xi_wx': sorted(set(ti_wx+[GAN_WX[g] for g in yin])),
                'ti_wx': sorted(set(ti_wx)),
                'overpower_combo': 6,
                'zhi_wx': [], 'hua_wx': [],
                'po_ge': [{'type':'缺失','forbidden':['正官','正财','偏财']}],  # PZZQ258: 无财官/透煞印
                'rule': 'PZZQ255: 建禄月劫透官逢财印/透财逢食伤/透煞遇制伏->成; 配合神入ti_wx; 破格: 无财官',
            }
            return facts

    # 食神格默认: 月令食神entry但没生财/没带煞 -> 食神格成, 食神是格体
    ss_entry_def = facts.get('shishen_entry', {}) or {}
    if ss_entry_def.get('is_entry'):
        ss_wx_def = facts.get('month_qi_element', '') or ''
        # 制杀太过检查(PZZQ4106"制煞过重同样成病"): 杀透 + 食伤当令(前提) + 杀无本气根/根被六冲 -> 格不成
        # 格不成则ti/xi清空, 由bingyao层判"制杀太过"(有印药则降级); 杀有根能任 -> 正常成格
        _LIUCHONG_PAIR = {'子':'午','午':'子','丑':'未','未':'丑','寅':'申','申':'寅',
                          '卯':'酉','酉':'卯','辰':'戌','戌':'辰','巳':'亥','亥':'巳'}
        _qs_def = _god_gans('七杀')
        _zhi_list = list(zhis)
        if _qs_def:
            _sha_ben_zhis = [z for z in _zhi_list
                             if ten_god(dg, ZHI_BEN_GAN.get(z, '')) == '七杀']
            _sha_root_chong = any(_LIUCHONG_PAIR.get(z) in _zhi_list for z in _sha_ben_zhis)
            # 仅"杀根被六冲(制尽)"判格不成; "杀无根"仍论格成(虚杀/中余气, 层次问题非原局病)
            if _sha_root_chong:
                facts['ge_cheng'] = None
                return facts
        _ss_xi = sorted(set(GAN_WX[g] for g in
            _god_gans('正财')+_god_gans('偏财')+_god_gans('七杀')+_god_gans('正印')+_god_gans('偏印')))
        facts['ge_cheng'] = {
            'ge': '食神格', 'xi_wx': _ss_xi,
            'ti_wx': [ss_wx_def] if ss_wx_def else [],
            'overpower_combo': 6,
            'zhi_wx': [], 'hua_wx': [],
            'po_ge': [{'type':'组合','required':['偏印']}],
            'rule': 'PZZQ255: 食神格成; 食神是格体; 喜神=财(生财)/煞印(带煞); 破格: 枭夺食',
        }
        return facts

    # 伤官格默认: 月令伤官entry但没佩印/没带煞 -> 伤官格成, 伤官是格体
    sg_entry_def = facts.get('shangguan_entry', {}) or {}
    if sg_entry_def.get('is_entry'):
        sg_wx_def = facts.get('month_qi_element', '') or ''
        _sg_xi = sorted(set(GAN_WX[g] for g in
            _god_gans('正财')+_god_gans('偏财')+_god_gans('正印')+_god_gans('偏印')+_god_gans('七杀')))
        facts['ge_cheng'] = {
            'ge': '伤官格', 'xi_wx': _sg_xi,
            'ti_wx': [sg_wx_def] if sg_wx_def else [],
            'overpower_combo': 6,
            'zhi_wx': [], 'hua_wx': [],
            'po_ge': [{'type':'组合','required':['正财','偏财']}],
            'rule': 'PZZQ255: 伤官格成; 伤官是格体; 喜神=财(生财)/印煞(身弱); 破格: 生财带煞',
        }
        return facts

    facts['ge_cheng'] = None
    return facts

def is_xix_shen(facts: Dict[str, Any], wx: str, combo: int) -> bool:
    """wx五行是否为成格喜神且未过旺. 是->泄气/克泄病应过滤(不报).
    过旺例外: combo>=overpower_combo 仍可报."""
    gc = facts.get('ge_cheng')
    if not gc:
        return False
    if wx not in (gc.get('xi_wx') or []):
        return False
    thr = int(gc.get('overpower_combo', 6))
    if combo >= thr:
        return False
    return True
