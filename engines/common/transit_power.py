# -*- coding: utf-8 -*-
"""应期层(大运/流年)复合旺衰可重入模块.

链路(复用已封板辩层, 不重新排盘、不另造强弱裁决器):
  原局 pillars + 岁运柱 extra_pillars
      -> L0 facts / build_tian_he(含岁运合局) / 纯规则计数(含岁运根与六合半合归化)
      -> 四档旺衰枚举(强/旺/平/衰, 布尔谓词非浮点)
      -> 冲支五行旺衰有序枚举比较 -> 衰者拔/旺神发/两停

原典依据:
  《滴天髓·冲合》"旺者冲衰衰者拔, 衰神冲旺旺神发";
  《滴天髓·岁运》"冲战视其孰降, 和好视其孰切"。
边界: 只输出结构枚举与变化; 五行旺衰序为布尔优先级多态枚举(非连续分数);
  不输出喜忌/用神/吉凶, 非 STRONG/WEAK 总裁决; 岁运不改变原局月令与日干。
"""
from typing import Any, Dict, List

from engines.common.l0_fact_builder import build as l0build, WUXING, HIDDEN
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.daymaster_root_class import classify_root_in_branches
from spec.root_qi import BRANCH_CANGGAN, STEM_WUXING

LIU_CHONG = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
_CHONG_SET = {frozenset(p) for p in LIU_CHONG}
_BASE_KEYS = ('year', 'month', 'day', 'hour')

# 地支→五行映射（纯常量，替代已删wuxing_power.BRANCH_WX）
BRANCH_WX = {'子': '水', '亥': '水', '寅': '木', '卯': '木',
             '巳': '火', '午': '火', '申': '金', '酉': '金',
             '辰': '土', '戌': '土', '丑': '土', '未': '土'}

# 月令旺相休囚死（《渊海子平》"得时俱为旺论，失时便作衰看"）
# 当令者旺，令所生者相，生令者休，克令者囚，令所克者死
WX_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}  # 我生
WX_KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}      # 我克


def _ling_state(month_wx: str, wx: str) -> str:
    """月令旺相休囚死纯规则查表。"""
    if wx == month_wx:
        return '旺'
    if WX_SHENG[month_wx] == wx:
        return '相'
    if WX_SHENG[wx] == month_wx:
        return '休'
    if WX_KE[month_wx] == wx:
        return '囚'
    return '死'  # 令所克者死


def _build_pure_power(pillars: Dict[str, list], facts: Dict[str, Any],
                       cfc: Dict[str, Any], extra: list) -> Dict[str, Any]:
    """纯规则五行动力计数——替代已删build_wuxing_power。

    只做结构计数（根数/透干/局数/半合/月令状态），不做浮点加权。
    输出格式与旧wuxing_power.wuxing_power字典对齐，供element_power_tier消费。
    """
    all_stems = [pillars[k][0] for k in _BASE_KEYS] + [g[0] for g in extra]
    all_branches = [pillars[k][1] for k in _BASE_KEYS] + [g[1] for g in extra]
    month_branch = pillars['month'][1]
    month_wx = BRANCH_WX[month_branch]

    # 三合三会局数（从cfc拿）
    ju_count = {wx: 0 for wx in ('木', '火', '土', '金', '水')}
    for rel_list in (cfc.get('sanhui', []), cfc.get('sanhe', [])):
        for rel in rel_list:
            if isinstance(rel, dict):
                wx = rel.get('wx') or rel.get('huashen')
                if wx in ju_count:
                    ju_count[wx] += 1
            elif isinstance(rel, str):
                # 字符串格式如"亥子丑三会水" → 解析结尾五行
                for wx in ('木', '火', '土', '金', '水'):
                    if rel.endswith(wx):
                        ju_count[wx] += 1
                        break
            elif isinstance(rel, (list, tuple)) and len(rel) >= 2:
                # 尝试从支反推五行局
                for wx, branches_set in [
                    ('木', {'寅', '卯', '辰', '亥', '卯', '未'}),
                    ('火', {'巳', '午', '未', '寅', '午', '戌'}),
                    ('金', {'申', '酉', '戌', '巳', '酉', '丑'}),
                    ('水', {'亥', '子', '丑', '申', '子', '辰'}),
                ]:
                    if set(rel).issubset(branches_set) and len(set(rel)) >= 3:
                        ju_count[wx] += 1
                        break

    # 半合数（从cfc拿）
    banhe_count = {wx: 0 for wx in ('木', '火', '土', '金', '水')}
    for rel in cfc.get('banhe', []):
        if isinstance(rel, dict):
            wx = rel.get('wx')
            if wx in banhe_count:
                banhe_count[wx] += 1

    # 逐五行计数
    wuxing_power = {}
    for wx in ('木', '火', '土', '金', '水'):
        ben_n = zhong_n = yu_n = 0
        for b in all_branches:
            cg = BRANCH_CANGGAN.get(b, ('', '', ''))
            if cg[0] and STEM_WUXING.get(cg[0]) == wx:
                ben_n += 1
            if cg[1] and STEM_WUXING.get(cg[1]) == wx:
                zhong_n += 1
            if cg[2] and STEM_WUXING.get(cg[2]) == wx:
                yu_n += 1
        stem_n = sum(1 for s in all_stems if STEM_WUXING.get(s) == wx)
        wuxing_power[wx] = {
            'ling_state': _ling_state(month_wx, wx),
            'ben_n': ben_n,
            'zhong_n': zhong_n,
            'yu_n': yu_n,
            'ju_n': ju_count.get(wx, 0),
            'banhe_n': banhe_count.get(wx, 0),
            'stem_n': stem_n,
        }

    return {'wuxing_power': wuxing_power, 'month_element': month_wx}


def _norm_extra(extra):
    out = []
    for g in extra or []:
        if isinstance(g, str):
            g = [g[0], g[1]]
        out.append([g[0], g[1]])
    return out


def build_transit_power(pillars: Dict[str, list], extra_pillars=None) -> Dict[str, Any]:
    """原局 pillars + 岁运柱 extra_pillars([(gan, zhi), ...]) -> 复合五行动力/根/合冲."""
    extra = _norm_extra(extra_pillars)
    facts = l0build(pillars)
    dm = pillars['day'][0]
    dm_wx = WUXING[dm]

    th = build_tian_he(pillars, facts, extra_pillars=extra)

    base_zhi = [pillars[k][1] for k in _BASE_KEYS]
    extra_zhi = [g[1] for g in extra]
    all_zhi = base_zhi + extra_zhi

    # 复合 root_class_detail(支->class), 口径同 build_root_classes(按藏干, 不做合化归化)
    rcd = classify_root_in_branches(dm, all_zhi, HIDDEN)['per_branch']

    # 复合六冲: 原局内部沿用 L0; 追加岁运支与原局/岁运支之间新引发的冲
    cf = dict(facts.get('combination_facts', {}) or {})
    chong = [list(p) for p in (cf.get('liuchong') or [])
             if isinstance(p, (list, tuple)) and len(p) == 2]
    seen = {frozenset(p) for p in chong}
    for i in range(len(all_zhi)):
        for j in range(i + 1, len(all_zhi)):
            a, b = all_zhi[i], all_zhi[j]
            key = frozenset((a, b))
            if key in _CHONG_SET and key not in seen and (a in extra_zhi or b in extra_zhi):
                chong.append([a, b])
                seen.add(key)
    cfc = dict(cf)
    cfc['liuchong'] = chong

    # V7.25 D1: 追加岁运支与原局/岁运支之间的六合
    from engines.common.daymaster_branch_relations import LIUHE_PAIRS
    liuhe = [list(p) for p in (cf.get('liuhe') or [])
             if isinstance(p, (list, tuple)) and len(p) == 2]
    seen_he = {frozenset(p) for p in liuhe}
    for i in range(len(all_zhi)):
        for j in range(i + 1, len(all_zhi)):
            a, b = all_zhi[i], all_zhi[j]
            key = frozenset((a, b))
            if key in LIUHE_PAIRS and key not in seen_he and (a in extra_zhi or b in extra_zhi):
                liuhe.append([a, b])
                seen_he.add(key)
    cfc['liuhe'] = liuhe

    # V7.25 D1: 追加岁运支与原局/岁运支之间的暗会
    from engines.common.daymaster_branch_relations import ANHUI_PAIRS
    anhui = []
    seen_anhui = set()
    for i in range(len(all_zhi)):
        for j in range(i + 1, len(all_zhi)):
            a, b = all_zhi[i], all_zhi[j]
            key = frozenset((a, b))
            if key in ANHUI_PAIRS and key not in seen_anhui and (a in extra_zhi or b in extra_zhi):
                anhui.append({'pair': [a, b], 'anhui_shen': ANHUI_PAIRS[key]})
                seen_anhui.add(key)
    cfc['anhui'] = anhui

    # V7.25 D1: 追加岁运支与原局/岁运支之间的半合
    # 生地半合: 申子/亥卯/寅午/巳酉
    # 墓地半合: 子辰/卯未/午戌/酉丑
    BANHE_PAIRS = {
        frozenset(('申', '子')): ('水', '生地'),
        frozenset(('亥', '卯')): ('木', '生地'),
        frozenset(('寅', '午')): ('火', '生地'),
        frozenset(('巳', '酉')): ('金', '生地'),
        frozenset(('子', '辰')): ('水', '墓地'),
        frozenset(('卯', '未')): ('木', '墓地'),
        frozenset(('午', '戌')): ('火', '墓地'),
        frozenset(('酉', '丑')): ('金', '墓地'),
    }
    banhe = []
    seen_banhe = set()
    for i in range(len(all_zhi)):
        for j in range(i + 1, len(all_zhi)):
            a, b = all_zhi[i], all_zhi[j]
            key = frozenset((a, b))
            if key in BANHE_PAIRS and key not in seen_banhe and (a in extra_zhi or b in extra_zhi):
                wx, type_ = BANHE_PAIRS[key]
                banhe.append({'pair': [a, b], 'wx': wx, 'type': type_ + '半合'})
                seen_banhe.add(key)
    cfc['banhe'] = banhe

    # V7.25 融合层: 地支关系优先级裁决规则
    # 原著依据: 三会>三合>半合>六合>冲>刑>害>破 (《四柱预测学入门》+《子平真诠》)
    # 规则: 多个关系同时存在时, 按类型优先级取最高; 同类型按位置距离取最高; 并列输出冲突保留
    RELATION_PRIORITY = {
        'sanhui': 7,
        'sanhe': 6,
        'banhe': 5,
        'liuhe': 4,
        'liuchong': 3,
        'sanxing': 2,
        'liuhai': 1,
        'liupo': 0,
    }
    # 收集所有关系
    all_relations = []
    for rel_type, rel_list in [('sanhui', cfc.get('sanhui', [])),
                                 ('sanhe', cfc.get('sanhe', [])),
                                 ('banhe', cfc.get('banhe', [])),
                                 ('liuhe', cfc.get('liuhe', [])),
                                 ('liuchong', cfc.get('liuchong', [])),
                                 ('sanxing', cfc.get('sanxing', [])),
                                 ('liuhai', cfc.get('liuhai', [])),
                                 ('liupo', cfc.get('liupo', []))]:
        for rel in rel_list:
            if isinstance(rel, dict):
                rel_type_val = rel.get('type', rel_type)
                rel['relation_type'] = rel_type
                rel['priority'] = RELATION_PRIORITY.get(rel_type, 0)
            else:
                all_relations.append({'relation_type': rel_type, 'priority': RELATION_PRIORITY.get(rel_type, 0), 'detail': rel})
    # 按优先级排序
    all_relations.sort(key=lambda x: -x['priority'])
    # 取最高优先级的关系
    dominant_relation = all_relations[0] if all_relations else None

    # 纯规则五行动力计数（替代已删build_wuxing_power）
    wp = _build_pure_power(pillars, facts, cfc, extra)

    # 七档spectrum: 浮点阈值产物已废弃, 用纯规则日主四档替代
    # 输出格式对齐下游期望: {'spectrum': '强'/'旺'/'平'/'衰'}
    dm_tier = element_power_tier(wp, dm_wx)
    spec = {'spectrum': dm_tier['name']}

    return {
        'daymaster': dm,
        'daymaster_element': dm_wx,
        'extra_pillars': extra,
        'wuxing_power': wp,
        'spectrum': spec,
        'root_class_detail': rcd,
        'combination_facts': cfc,
        'base_branches': base_zhi,
        'all_branches': all_zhi,
        'judgment_status': 'TRANSIT_POWER_PURE_RULE',
        'boundary_note': ('原局+岁运复合结构; 纯规则计数(根数/透干/局数/月令状态), 无浮点加权; '
                          '五行旺衰序为布尔四档枚举(强/旺/平/衰); '
                          '不输出喜忌/用神/吉凶, 非STRONG/WEAK总裁决'),
    }


def element_power_tier(wp: Dict[str, Any], wx: str) -> Dict[str, Any]:
    """某五行在复合局下的旺衰有序枚举(供冲/合作用比较).

    布尔条件优先级(不做连续总分; 序位边界 # PCT-MARK, 以DTS岁运命例回归校准):
      强(3): 成三合三会局 / 当令且有本气根 / 本气根>=3
      旺(2): 本气根>=2 / 当令而透干或半合 / 当令相令有本气根
      平(1): 有本气根 / 有中余气根 / 半合 / 相令透干
      衰(0): 仅虚透或失令无本气根
    """
    e = (wp.get('wuxing_power', {}) or {}).get(wx) or {}
    ling = e.get('ling_state', '休')
    ben = int(e.get('ben_n', 0))
    zy = int(e.get('zhong_n', 0)) + int(e.get('yu_n', 0))
    ju = int(e.get('ju_n', 0))
    banhe = int(e.get('banhe_n', 0))
    stem = int(e.get('stem_n', 0))
    if ju >= 1 or (ling == '旺' and ben >= 1) or ben >= 3:
        tier, name = 3, '强'
    elif ben >= 2 or (ling == '旺' and (stem >= 1 or banhe >= 1)) or (ling in ('旺', '相') and ben >= 1):
        tier, name = 2, '旺'
    elif ben >= 1 or zy >= 1 or banhe >= 1 or (ling == '相' and stem >= 1):
        tier, name = 1, '平'
    else:
        tier, name = 0, '衰'
    return {'wuxing': wx, 'tier': tier, 'name': name, 'ling_state': ling,
            'ben_n': ben, 'zhong_yu_n': zy, 'ju_n': ju, 'banhe_n': banhe, 'stem_n': stem}


def transit_clash_verdicts(tp: Dict[str, Any]) -> List[Dict[str, Any]]:
    """复合局下所有六冲, 比两边五行旺衰序位 -> 衰者拔/旺神发/两停(《滴天髓》冲合)."""
    wp = tp['wuxing_power']
    out = []
    for a, b in tp.get('combination_facts', {}).get('liuchong', []):
        wa, wb = BRANCH_WX.get(a), BRANCH_WX.get(b)
        ta, tb = element_power_tier(wp, wa), element_power_tier(wp, wb)
        if ta['tier'] > tb['tier']:
            verdict = f'{a}({wa}{ta["name"]})旺冲{b}({wb}{tb["name"]})衰: {b}衰者拔, {a}旺神发'
        elif tb['tier'] > ta['tier']:
            verdict = f'{b}({wb}{tb["name"]})旺冲{a}({wa}{ta["name"]})衰: {a}衰者拔, {b}旺神发'
        else:
            verdict = f'{a}{b}同阶({ta["name"]}/{tb["name"]}): 两停不拔不发'
        out.append({'pair': [a, b], 'a_tier': ta, 'b_tier': tb, 'verdict': verdict})
    return out





