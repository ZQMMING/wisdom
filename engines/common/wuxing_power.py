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

WX_LIST = ['木', '火', '土', '金', '水']
SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}   # 我生
KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}      # 我克
SHENG_ME = {v: k for k, v in SHENG.items()}                            # 生我(印)
KE_ME = {v: k for k, v in KE.items()}                                  # 克我(官杀)
BRANCH_WX = {'子': '水', '亥': '水', '寅': '木', '卯': '木', '巳': '火', '午': '火',
             '申': '金', '酉': '金', '辰': '土', '戌': '土', '丑': '土', '未': '土'}

# ---- # PCT-MARK: 藏干层级客观权重(源自子平真诠干根序, 可调) ----
W_BENQI = 4.0     # 本气藏干(重根, 约长生禄刃, >三比肩)
W_ZHONGQI = 2.0   # 中气藏干(轻根, 约墓库余气)
W_YUQI = 1.0      # 余气藏干
W_STEM = 1.0      # 天干透出一位
W_JU = 3.0        # 三合/三会成方局

# ---- # PCT-MARK: 月令旺相休囚死状态系数(可调) ----
LING_COEF = {'旺': 1.00, '相': 0.72, '休': 0.52, '囚': 0.34, '死': 0.20}

# ---- # PCT-MARK: 七档占比阈值(下界), 按513 ratio分位+原文极端案例标定, 可调 ----
T_WANG_JI = 0.78
T_TAI_WANG = 0.64
T_WANG = 0.55
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
                     branch_convert: Dict[str, str] = None) -> Dict[str, Any]:
    """某五行在四支按本气/中气/余气层级的原始根分(未乘月令系数).

    branch_convert: 三会方/三合局成局后四季土(辰戌丑未)本气归化会神五行,
    如 亥子丑三会水 -> 丑本气己土不再计土, 归化计水(T32/T33 会局改变根气归属).
    """
    branch_convert = branch_convert or {}
    ben_n = zhong_n = yu_n = 0
    detail = {}
    for k in PILLAR_KEYS:
        z = pillars[k][1]
        stems = hidden_by_pillar.get(k, [])
        if z in branch_convert:
            cwx = branch_convert[z]
            if wx == cwx:
                ben_n += 1; detail[z] = 'BEN_JU'
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
        if hit == 'BEN':
            ben_n += 1; detail[z] = 'BEN'
        elif hit == 'ZHONG':
            zhong_n += 1; detail[z] = 'ZHONG'
        elif hit == 'YU':
            yu_n += 1; detail[z] = 'YU'
    raw = W_BENQI * ben_n + W_ZHONGQI * zhong_n + W_YUQI * yu_n
    return {'raw': raw, 'ben_n': ben_n, 'zhong_n': zhong_n, 'yu_n': yu_n, 'detail': detail}


def build_wuxing_power(pillars: Dict[str, list], facts: Dict[str, Any],
                       tian_he: Dict[str, Any] = None) -> Dict[str, Any]:
    """对称计算五行动力(含月令旺相休囚死加权)."""
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

    power = {}
    for wx in WX_LIST:
        root = _root_raw_for_wx(wx, pillars, hidden_by_pillar, branch_convert)
        stem_n = sum(1 for k in ('year', 'month', 'hour') if WUXING.get(pillars[k][0]) == wx)
        ju_n = ju_wx.count(wx)
        raw = root['raw'] + W_STEM * stem_n + W_JU * ju_n
        state = ling_state(month_wx, wx)
        coef = LING_COEF[state]
        power[wx] = {
            'ling_state': state,
            'ling_coef': coef,
            'raw': round(raw, 2),
            'root_detail': root['detail'],
            'ben_n': root['ben_n'], 'zhong_n': root['zhong_n'], 'yu_n': root['yu_n'],
            'stem_n': stem_n, 'ju_n': ju_n,
            'total': round(raw * coef, 2),
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
