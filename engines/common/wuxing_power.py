# -*- coding: utf-8 -*-
"""PATCH-160-B 五行力量对称计算 + 日主旺衰结构谱 (含月令旺相休囚死)

对五个五行做完全对称的客观结构计分, 再按月令状态(旺相休囚死)加权, 归并:
  日主端 = 比劫(同五行) + 印(生我)
  对方端 = 食伤(我生) + 财(我克) + 官杀(克我)
输出日主端占比 + 有序七档枚举(旺极/太旺/旺/中和/衰/太衰/衰极).

月令为提纲: 当令者旺, 令所生者相, 生令者休, 克令者囚, 令所克者死;
各五行(根+透+局)力量按其月令状态系数加权 —— 此即"得时/失令"的结构本质.

只做结构度量, 不输出喜忌/用神/吉凶, 非 STRONG/WEAK 总裁决; 不抹销各维度独立事实.
纯函数可重入, 应期层(原局+岁运)可复用.

# PCT-MARK: 权重/月令系数/档位阈值为工程估计, 源自《子平真诠》干根力量序
#   ("得一比肩不如支中一墓库, 得二比肩不如一余气, 得三比肩不如一长生禄刃")
#   与《渊海子平》"得时俱为旺论, 失时便作衰看"的旺相休囚死位阶;
#   非古籍直接数值, 允许在案例回归中修正.
"""
from typing import Any, Dict, List

from engines.common.daymaster_root_class import WUXING
from engines.common.l0_fact_builder import HIDDEN

WX_LIST = ['木', '火', '土', '金', '水']
# 十干阴阳映射: 每个五行对应阳干和阴干
GAN_YANG = {'木': '甲', '火': '丙', '土': '戊', '金': '庚', '水': '壬'}
GAN_YIN = {'木': '乙', '火': '丁', '土': '己', '金': '辛', '水': '癸'}
YANG_GAN_SET = set(GAN_YANG.values())  # 甲丙戊庚壬
YIN_GAN_SET = set(GAN_YIN.values())    # 乙丁己辛癸
SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}   # 我生
KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}      # 我克
SHENG_ME = {v: k for k, v in SHENG.items()}                            # 生我(印)
KE_ME = {v: k for k, v in KE.items()}                                  # 克我(官杀)
BRANCH_WX = {'子': '水', '亥': '水', '寅': '木', '卯': '木', '巳': '火', '午': '火',
             '申': '金', '酉': '金', '辰': '土', '戌': '土', '丑': '土', '未': '土'}

# ---- # PCT-MARK: 藏干层级客观权重(源自子平真诠干根序, 可调) ----
W_BENQI = 6.0     # 本气藏干(重根, 原典得三比肩不如得一长生禄刃) # PCT-MARK 经DTS513例校准
W_ZHONGQI = 2.0   # 中气藏干(轻根, 约墓库余气)
W_YUQI = 1.0      # 余气藏干
W_STEM = 1.0      # 天干透出一位
W_JU = 3.0        # 三合/三会成方局
W_BANHE = 1.5     # 半三合两支拱局(力约全合之半)  # PCT-MARK 半合权重
_DM_HEAVY_BRANCH = {  # 日主十二长生重根位(长生/禄/帝旺刃)
    '甲': ('亥','寅','卯'), '乙': ('午','卯','寅'),
    '丙': ('寅','巳','午'), '丁': ('酉','午','巳'),
    '戊': ('寅','巳','午'), '己': ('酉','午','巳'),
    '庚': ('巳','申','酉'), '辛': ('子','酉','申'),
    '壬': ('申','亥','子'), '癸': ('卯','子','亥')}

# ---- # PCT-MARK: 月令旺相休囚死状态系数(可调) ----
LING_COEF = {'旺': 1.00, '相': 0.72, '休': 0.52, '囚': 0.34, '死': 0.20}
# ---- # PCT-MARK: 天干透干月令系数(比地支平缓, 因天干为明见之力, 月令影响较小) ----
# 原典: 子平真诠"得时不旺失时不弱"; 天垂象地成形, 月令主地支, 天干受影响较小
STEM_LING_COEF = {'旺': 1.00, '相': 0.90, '休': 0.80, '囚': 0.70, '死': 0.60}

# ---- # PCT-MARK: 七档占比阈值(下界), 按513 ratio分位+原文极端案例标定, 可调 ----
T_WANG_JI = 0.78
T_TAI_WANG = 0.64
T_WANG = 0.45  # PCT-MARK 经DTS513例校准, 体现得时不旺失时不弱
T_ZHONG_HE_LO = 0.45
T_TAI_SHUAI = 0.32
T_SHUAI_JI = 0.18

PILLAR_KEYS = ('year', 'month', 'day', 'hour')


def ling_state(month_wx: str, wx: str) -> str:
    """五行 wx 在 month_wx 当令下的旺相休囚死状态."""
    if not month_wx:
        return '休'
    if wx == month_wx:
        return '旺'
    if SHENG[month_wx] == wx:      # 令所生
        return '相'
    if SHENG_ME[month_wx] == wx:   # 生令者(令之母)
        return '休'
    if KE_ME[month_wx] == wx:      # 克令者
        return '囚'
    if KE[month_wx] == wx:         # 令所克
        return '死'
    return '休'


def _root_raw_for_wx(wx: str, pillars, hidden_by_pillar: Dict[str, List[str]],
                     branch_convert: Dict[str, str] = None, day_stem: str = None,
                     he_convert: Dict[str, str] = None, all_keys=None) -> Dict[str, Any]:
    """某五行在四支按本气/中气/余气层级的原始根分(未乘月令系数).

    branch_convert: 三会方/三合局成局后四季土(辰戌丑未)本气归化会神五行,
    如 亥子丑三会水 -> 丑本气己土不再计土, 归化计水(T32/T33 会局改变根气归属).
    """
    branch_convert = branch_convert or {}
    he_convert = he_convert or {}
    # 通用归化: 三合三会墓库=BEN_JU; 紧贴六合化神/从旺=BEN_HE(不覆盖局归化, 一支一化)
    conv = dict(branch_convert)
    for _z0, _w0 in he_convert.items():
        conv.setdefault(_z0, _w0)
    ben_n = zhong_n = yu_n = 0
    detail = {}
    for k in (all_keys or PILLAR_KEYS):
        z = pillars[k][1]
        stems = hidden_by_pillar.get(k, [])
        if z in conv:
            cwx = conv[z]
            ctag = 'BEN_JU' if z in branch_convert else 'BEN_HE'
            if wx == cwx:
                ben_n += 1; detail[z] = ctag
            for idx, h in enumerate(stems[1:], start=1):
                if WUXING.get(h) == wx:
                    if idx == 1:
                        zhong_n += 1; detail.setdefault(z, 'ZHONG')
                    elif idx == 2:
                        yu_n += 1; detail.setdefault(z, 'YU')
            continue
        hit = None
        for idx, h in enumerate(stems):
            if WUXING.get(h) == wx:
                if idx == 0:
                    hit = 'BEN'; break
                elif idx == 1:
                    hit = 'ZHONG'
                elif idx == 2 and hit is None:
                    hit = 'YU'
        # 土寄禄火宫(原典十干禄: 戊禄巳刃午/己禄午刃巳): 巳午本气火(印)而土居禄刃位,
        # 仅日主戊己时按本气级重根; 他神土不提级(禄为日干概念). # PCT-MARK 提级用本气权重
        is_lu = (wx == '土' and day_stem in ('戊', '己') and z in ('巳', '午')
                 and any(WUXING.get(h) == '土' for h in stems))
        if is_lu:
            hit = 'BEN'
        # 日主长生/禄/帝旺(刃)位: 原典"长生禄旺根之重者", 藏干虽余气(庚长生巳, 巳中庚余气)亦按本气重根;
        # 阴长生支(午酉子卯)藏干不含本五行自动不提(为 SPECIAL 明根, 非重根). # PCT-MARK 提级用本气权重
        is_cs = False
        if not is_lu and day_stem and wx == WUXING.get(day_stem) and hit != 'BEN':
            if z in _DM_HEAVY_BRANCH.get(day_stem, ()) and any(WUXING.get(h) == wx for h in stems):
                is_cs = True; hit = 'BEN'
        if hit == 'BEN':
            ben_n += 1; detail[z] = ('BEN_LU' if is_lu else ('BEN_CS' if is_cs else 'BEN'))
        elif hit == 'ZHONG':
            zhong_n += 1; detail[z] = 'ZHONG'
        elif hit == 'YU':
            yu_n += 1; detail[z] = 'YU'
    raw = W_BENQI * ben_n + W_ZHONGQI * zhong_n + W_YUQI * yu_n
    return {'raw': raw, 'ben_n': ben_n, 'zhong_n': zhong_n, 'yu_n': yu_n, 'detail': detail}


def build_wuxing_power(pillars: Dict[str, list], facts: Dict[str, Any],
                       tian_he: Dict[str, Any] = None, extra_pillars=None) -> Dict[str, Any]:
    """对称计算五行动力(含月令旺相休囚死加权). extra_pillars=岁运柱[(gan,zhi),...]可重入."""
    hidden_by_pillar = {}
    hs = facts.get('hidden_stems', {})
    for k in PILLAR_KEYS:
        z = pillars[k][1]
        v = hs.get(k) if isinstance(hs, dict) and k in hs else hs.get(z)
        if v is None:
            v = facts.get('hidden_stems_table', {}).get(z, [])
        hidden_by_pillar[k] = v or []

    dm = facts.get('day_stem') or pillars['day'][0]
    dm_wx = WUXING[dm]
    month_wx = BRANCH_WX.get(pillars['month'][1])

    # 应期可重入: 岁运柱(大运/流年)作为额外柱位; 不改变月令与日干
    extra_pillars = extra_pillars or []
    _ext = [('t%d' % i, list(gz)) for i, gz in enumerate(extra_pillars)]
    all_keys = PILLAR_KEYS + tuple(k for k, _ in _ext)
    epillars = dict(pillars)
    for _k, _gz in _ext:
        epillars[_k] = _gz
    _htab = facts.get('hidden_stems_table', {}) or {}
    for _k, _gz in _ext:
        hidden_by_pillar[_k] = list(_htab.get(_gz[1]) or HIDDEN.get(_gz[1], []))

    ju_wx = []
    branch_convert = {}
    TU_BRANCHES = {'辰', '戌', '丑', '未'}
    def _absorb_ju(ju):
        wx = None; brs = []
        if isinstance(ju, dict):
            wx = ju.get('wuxing') or ju.get('huashen') or ju.get('element')
            brs = ju.get('branches') or ju.get('branches_char') or []
            nm = ju.get('name') or ''
            if not brs:
                brs = [c for c in nm if c in BRANCH_WX]
            if not wx:
                for c in reversed(nm):
                    if c in WX_LIST:
                        wx = c; break
        elif isinstance(ju, (list, tuple)) and ju:
            wx = ju[-1]; brs = list(ju[:-1])
        elif isinstance(ju, str):
            brs = [c for c in ju if c in BRANCH_WX]
            for c in reversed(ju):
                if c in WX_LIST:
                    wx = c; break
        if wx in WX_LIST:
            ju_wx.append(wx)
            for z in brs:
                if z in TU_BRANCHES:
                    branch_convert[z] = wx   # 四季土本气归化会神
    if tian_he:
        for ju in (tian_he.get('sanhe_ju', []) or []) + (tian_he.get('sanhui_ju', []) or []):
            _absorb_ju(ju)

    # 半三合(两支拱局, T32延伸; L0不记半合Fact, 力量层从轻计; 全合已计同化神则不重复)
    BANHE = {frozenset(('申','子')): '水', frozenset(('子','辰')): '水',
             frozenset(('寅','午')): '火', frozenset(('午','戌')): '火',
             frozenset(('巳','酉')): '金', frozenset(('酉','丑')): '金',
             frozenset(('亥','卯')): '木', frozenset(('卯','未')): '木'}
    _brs = [epillars[k][1] for k in all_keys]
    banhe_wx = []
    for _i in range(len(_brs)):
        for _j in range(_i + 1, len(_brs)):
            _hw = BANHE.get(frozenset((_brs[_i], _brs[_j])))
            if _hw and ju_wx.count(_hw) == 0:
                banhe_wx.append(_hw)

    # ---- task#50 紧贴六合化神归化(从严; # PCT-MARK 合化条件) ----
    LIUHE_HUASHEN = {frozenset(('子', '丑')): '土', frozenset(('寅', '亥')): '木', frozenset(('卯', '戌')): '火',
                     frozenset(('辰', '酉')): '金', frozenset(('巳', '申')): '水', frozenset(('午', '未')): '土'}
    _pre_root = {wx: _root_raw_for_wx(wx, epillars, hidden_by_pillar, branch_convert,
                                       day_stem=dm, all_keys=all_keys)
                 for wx in WX_LIST}
    _pre_ben = {wx: _pre_root[wx]['ben_n'] for wx in WX_LIST}
    he_convert = {}
    _seq = [(k, pillars[k][1]) for k in PILLAR_KEYS]
    for _i in range(3):  # 仅紧贴: 年月/月日/日时
        _z1, _z2 = _seq[_i][1], _seq[_i + 1][1]
        _hwx = LIUHE_HUASHEN.get(frozenset((_z1, _z2)))
        if not _hwx:
            continue
        _hling = ling_state(month_wx, _hwx)
        _hju = ju_wx.count(_hwx) >= 1
        _hstem = sum(1 for k in ('year', 'month', 'hour') if WUXING.get(pillars[k][0]) == _hwx)
        _hsheng_ju = (SHENG.get(_hwx) in ju_wx and ling_state(month_wx, SHENG[_hwx]) in ('旺', '相'))
        _hua = (_hling == '旺' or _hju or _pre_ben.get(_hwx, 0) >= 2
                or (_pre_ben.get(_hwx, 0) >= 1 and _hling == '相' and _hstem >= 1) or _hsheng_ju)
        # 从旺合化: 化神不得势, 而合中一支五行已成三合三会局且当令 -> 另一支从旺神(湿土从水局)
        _cong = None
        for _zz in (_z1, _z2):
            _w = BRANCH_WX.get(_zz)
            if _w in ju_wx and ling_state(month_wx, _w) == '旺':
                _cong = _w
        _target = _hwx if _hua else _cong
        if _target:
            for _zz in (_z1, _z2):
                if _zz in branch_convert or _zz in he_convert:
                    continue
                # 日主本气/禄刃根(支本气=日主五行)不因地支六合化走; 日干化气归天干五合化气格另案
                if BRANCH_WX.get(_zz) != _target and BRANCH_WX.get(_zz) != dm_wx:
                    he_convert[_zz] = _target

    # 岁运焦点六合(不限紧邻): 岁运支与原局任一支、岁运支之间论合化; 化神条件同原局(透干含岁运干)
    def _liuhe_target(_z1, _z2):
        _hwx = LIUHE_HUASHEN.get(frozenset((_z1, _z2)))
        if not _hwx:
            return None
        _hling = ling_state(month_wx, _hwx)
        _hju = ju_wx.count(_hwx) >= 1
        _hstem = sum(1 for _k in all_keys if _k != 'day' and WUXING.get(epillars[_k][0]) == _hwx)
        _hsheng_ju = (SHENG.get(_hwx) in ju_wx and ling_state(month_wx, SHENG[_hwx]) in ('旺', '相'))
        _hua = (_hling == '旺' or _hju or _pre_ben.get(_hwx, 0) >= 2
                or (_pre_ben.get(_hwx, 0) >= 1 and _hling == '相' and _hstem >= 1) or _hsheng_ju)
        _cong = None
        for _zz in (_z1, _z2):
            _w = BRANCH_WX.get(_zz)
            if _w in ju_wx and ling_state(month_wx, _w) == '旺':
                _cong = _w
        return _hwx if _hua else _cong
    _focal = [(k, epillars[k][1]) for k, _ in _ext]
    for _fi, (_fk, _fz) in enumerate(_focal):
        _cands = [(_fz, epillars[_ok][1]) for _ok in PILLAR_KEYS]
        _cands += [(_fz, _fz2) for _fk2, _fz2 in _focal[_fi + 1:]]
        for _z1, _z2 in _cands:
            _target = _liuhe_target(_z1, _z2)
            if not _target:
                continue
            for _zz in (_z1, _z2):
                if _zz in branch_convert or _zz in he_convert:
                    continue
                if BRANCH_WX.get(_zz) != _target and BRANCH_WX.get(_zz) != dm_wx:
                    he_convert[_zz] = _target

    power = {}
    for wx in WX_LIST:
        root = _root_raw_for_wx(wx, epillars, hidden_by_pillar, branch_convert, day_stem=dm,
                                 he_convert=he_convert, all_keys=all_keys)
        stem_n = sum(1 for k in all_keys if k != 'day' and WUXING.get(epillars[k][0]) == wx)
        ju_n = ju_wx.count(wx)
        banhe_n = banhe_wx.count(wx)
        # 分离计算: 地支藏干(含局/半合)用地支月令系数, 天干透干用天干月令系数
        # 原典: 天垂象地成形, 月令主地支之气, 天干透干为明见之力受月令影响较小
        root_raw = root['raw'] + W_JU * ju_n + W_BANHE * banhe_n  # 地支部分(藏干+局+半合)
        stem_raw = W_STEM * stem_n  # 天干透干部分
        state = ling_state(month_wx, wx)
        coef = LING_COEF[state]  # 地支月令系数
        stem_coef = STEM_LING_COEF[state]  # 天干月令系数(平缓)
        raw = root_raw + stem_raw
        total = root_raw * coef + stem_raw * stem_coef  # 分别加权后求和
        # 十干级独立力量: 阳干和阴干分别计算透干和藏干
        # 原典: 六部经典全部以十干为论述单位, 同一五行阴阳干作用机制完全不同
        # 如壬水冲奔泛滥=病, 癸水渗透滋润=药
        yang_gan = GAN_YANG[wx]
        yin_gan = GAN_YIN[wx]
        # 阳干透干数(不含日主)
        yang_stem_n = sum(1 for k in all_keys if k != 'day' and epillars[k][0] == yang_gan)
        yin_stem_n = sum(1 for k in all_keys if k != 'day' and epillars[k][0] == yin_gan)
        # 阳干/阴干藏干数(遍历地支藏干)
        yang_ben = yang_zhong = yang_yu = 0
        yin_ben = yin_zhong = yin_yu = 0
        for k in all_keys:
            z = epillars[k][1]
            stems = hidden_by_pillar.get(k, [])
            # 处理六合化神: 如果该支被化神, 则化神五行的本气+1
            if z in he_convert and he_convert[z] == wx:
                # 化神本气归到阳干(化神为五行, 默认归阳干)
                yang_ben += 1
                continue
            if z in branch_convert and branch_convert[z] == wx:
                yang_ben += 1
                continue
            for idx, h in enumerate(stems):
                if h == yang_gan:
                    if idx == 0: yang_ben += 1
                    elif idx == 1: yang_zhong += 1
                    else: yang_yu += 1
                elif h == yin_gan:
                    if idx == 0: yin_ben += 1
                    elif idx == 1: yin_zhong += 1
                    else: yin_yu += 1
        # 阳干/阴干独立力量(使用与五行相同的系数)
        yang_root_raw = W_BENQI * yang_ben + W_ZHONGQI * yang_zhong + W_YUQI * yang_yu
        yin_root_raw = W_BENQI * yin_ben + W_ZHONGQI * yin_zhong + W_YUQI * yin_yu
        yang_stem_raw = W_STEM * yang_stem_n
        yin_stem_raw = W_STEM * yin_stem_n
        yang_total = yang_root_raw * coef + yang_stem_raw * stem_coef
        yin_total = yin_root_raw * coef + yin_stem_raw * stem_coef

        stem_detail = {
            'yang': {
                'stem': yang_gan, 'stem_n': yang_stem_n,
                'ben_n': yang_ben, 'zhong_n': yang_zhong, 'yu_n': yang_yu,
                'root_raw': round(yang_root_raw, 2), 'stem_raw': round(yang_stem_raw, 2),
                'total': round(yang_total, 2),
            },
            'yin': {
                'stem': yin_gan, 'stem_n': yin_stem_n,
                'ben_n': yin_ben, 'zhong_n': yin_zhong, 'yu_n': yin_yu,
                'root_raw': round(yin_root_raw, 2), 'stem_raw': round(yin_stem_raw, 2),
                'total': round(yin_total, 2),
            },
        }

        power[wx] = {
            'ling_state': state,
            'ling_coef': coef,
            'stem_ling_coef': stem_coef,
            'raw': round(raw, 2),
            'root_raw': round(root_raw, 2),
            'stem_raw': round(stem_raw, 2),
            'root_detail': root['detail'],
            'ben_n': root['ben_n'], 'zhong_n': root['zhong_n'], 'yu_n': root['yu_n'],
            'stem_n': stem_n, 'ju_n': ju_n, 'banhe_n': banhe_n,
            'total': round(total, 2),
            'stem_detail': stem_detail,  # 十干级独立力量(阳干/阴干)
        }

    return {'daymaster': dm, 'daymaster_element': dm_wx, 'month_element': month_wx,
            'wuxing_power': power, 'judgment_status': 'WUXING_POWER_STRUCTURE_ONLY'}


def build_spectrum_from_power(wp: Dict[str, Any]) -> Dict[str, Any]:
    """由五行动力归并日主端/对方端, 输出占比与有序七档."""
    dm_wx = wp['daymaster_element']
    p = wp['wuxing_power']
    yin_wx = SHENG_ME.get(dm_wx)
    shishang_wx = SHENG.get(dm_wx)
    cai_wx = KE.get(dm_wx)
    guansha_wx = KE_ME.get(dm_wx)

    self_bijie = p[dm_wx]['total']
    self_yin = p[yin_wx]['total'] if yin_wx else 0
    self_score = self_bijie + self_yin
    opp_ss = p[shishang_wx]['total']
    opp_cai = p[cai_wx]['total']
    opp_gs = p[guansha_wx]['total']
    opp_score = opp_ss + opp_cai + opp_gs

    total = self_score + opp_score
    ratio = self_score / total if total > 0 else 0.5

    has_heavy = p[dm_wx]['ben_n'] > 0
    if ratio >= T_WANG_JI and has_heavy:
        spec = '旺极'
    elif ratio >= T_TAI_WANG and has_heavy:
        spec = '太旺'
    elif ratio >= T_WANG:
        spec = '旺'
    elif ratio >= T_ZHONG_HE_LO:
        spec = '中和'
    elif ratio >= T_TAI_SHUAI:
        spec = '衰'
    elif ratio >= T_SHUAI_JI:
        spec = '太衰'
    else:
        spec = '衰极' if p[dm_wx]['ben_n'] == 0 else '太衰'

    return {
        'daymaster_element': dm_wx,
        'self_group': {'比劫': dm_wx, '印': yin_wx, 'score': round(self_score, 2),
                       'detail': {'比劫': self_bijie, '印': self_yin},
                       'ling_state': {'比劫': p[dm_wx]['ling_state'],
                                      '印': p[yin_wx]['ling_state'] if yin_wx else None}},
        'opposing_group': {'食伤': shishang_wx, '财': cai_wx, '官杀': guansha_wx,
                           'score': round(opp_score, 2),
                           'detail': {'食伤': opp_ss, '财': opp_cai, '官杀': opp_gs}},
        'daymaster_ratio': round(ratio, 3),
        'spectrum': spec,
        'judgment_status': 'SPECTRUM_STRUCTURE_ONLY',
        'boundary_note': '对称五行(月令旺相休囚死加权)结构度量+有序枚举; # PCT-MARK 权重系数阈值待回归校准; 不输出喜忌/用神/吉凶, 非STRONG/WEAK总裁决',
    }


def _party(g):
    """成党 = 透干 且 通根(原典: 有根无透其力不彰)."""
    return bool(g.get('stem_present') and g.get('root_present'))


def build_spectrum_topology(network, wp=None):
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
    yin_cheng=False; guan_hua=False; cai_ben=0; gs_ben=0; bj_stem=0; yin_stem=0; month_wx=None; lu_chong=False
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
        cai_ben = int(cai.get('ben_n',0)); gs_ben = int(gs.get('ben_n',0))
        month_wx=(wp or {}).get('month_element')
        opp_ling_fin = month_wx in (cai_wx,gs_wx)
        ss_ling = (month_wx==ss_wx)
        # T30 禄刃/本气硬根支遭六冲、我非当令(月令囚死): 旺者冲衰衰者拔, 禄根被冲伤; 四库土冲反旺除外
        _cf0 = facts.get('combination_facts',{}) if isinstance(facts,dict) else {}
        _chong0 = {b for pr in (_cf0.get('liuchong') or []) for b in pr}
        _ku0=('辰','戌','丑','未')
        _chong_ben = [z for z,t in (dm.get('root_detail',{}) or {}).items()
                     if z in _chong0 and t=='BEN' and not (dm_wx=='土' and z in _ku0)]
        # 禄刃本气根遭六冲: 我非当令(旺者冲衰衰者拔), 或财官党众冲克寡根(两卯冲酉+午克)
        # 当令根被单冲属衰神冲旺旺神发(不伤); 唯财官本气党众悬殊(>=身根+2, 两卯+寅+午)方拔
        # 衰者拔须财官党众压身; 失令逢冲若日主比劫本气根反占优(>=财官, 衰神冲旺旺神发/两停)不拔
        _chong_pull_dang = (cai_ben+gs_ben >= dm_ben+2)
        _chong_pull_ling = (L<2 and dm_ben<=1 and (cai_ben+gs_ben) >= dm_ben)
        lu_chong = bool(_chong_ben) and (_chong_pull_dang or _chong_pull_ling)
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
    elif S==3 and self_ju and dm_ben>=3 and fin_rooted_eff<=1 and L>=1:
        spec='旺极'   # 三合局旺极须得令/相令(失令三合局不判旺极, 如庚申戊寅壬子甲辰寅月食神当令); 三会方才不受月令限制
    # ---- 旺极: 三根当令(孤财失令不制); 得令重根+印多根; 印成方生身 ----
    elif S==3 and dm_ben>=3 and L==2 and fin_rooted_eff<=1:
        spec='旺极'
    elif S==3 and fin_rooted_eff==0 and dm_ben>=2 and L==2 and yin_ben>=2:
        spec='旺极'   # 得令两本气根 + 印多根(两长生逢禄旺, 木火/水木成势)
    elif S==3 and fin_rooted_eff==0 and (yin_ju or yin_ben>=3) and ratio>=0.85 and dm_heavy>=1:
        spec='旺极'
    # ---- 拱局旺极: 半合本方局+禄刃重根+印成势生身, 财官虚透无根(戌午拱火日时逢印, T32半合) ----
    elif S==3 and fin_rooted_eff==0 and dm_banhe>=1 and dm_heavy>=1 and (yin_ben>=2 or yin_ju) and ratio>=0.40 and L>=1:
        spec='旺极'   # 得令/相令+半合本方局+印重(失令印重不判旺极, 如己丑丙子辛酉壬辰子月伤官当令+丙火官杀)
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
    elif (S>=3 and guan_hua and dm_has_lu and yin_ben>=1 and yin_stem>=1
          and fin_rooted_eff<=1 and ratio>=0.20
          and not (L==0 and month_wx==cai_wx and gs_ben>=1 and gs is not None and int(gs.get('stem_n',0))>=1)):
        spec='旺'   # 财当令而财->官->印->身流通, 禄刃+本气印双透: 日元临旺逢生官印双清(乙卯丁亥戊午丙辰);
        # PCT-MARK 例外: 日主囚死月令(L=0)+财当令+官杀本气根且透干=财官连环成党压失令之身(春金虽弱/杀重身轻, L1265甲午丙寅辛酉己丑), 不落流通判旺, 交后line204太衰身弱喜印比
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
    # ---- 禄刃本气根遭六冲被拔(我非当令, 或财官党众冲克寡根): 根拔不任财官(T30 旺者冲衰衰者拔) ----
    elif lu_chong and ratio<0.62:
        spec='衰'   # 乙卯乙酉庚寅壬午(酉刃当令被两卯冲+午火克, 财官党4>身1, 反弱不任财官)
    # ---- 比劫成党得势: 比劫多透+长生禄旺重根, 财官仅单本气根(天干皆木君盛/群比争财), 党众不论失时 ----
    elif S>=2 and fin_rooted<=1 and ((bj_stem>=2 and dm_heavy>=2 and ratio>=0.30)
                                      or (dm_ben>=3 and dm_heavy>=2 and ratio>=0.24)):
        spec='旺'   # 比劫成党得势; 三真根(禄刃+合化)成党失令亦托底(干多不如根重, #225辛酉刃运)
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
