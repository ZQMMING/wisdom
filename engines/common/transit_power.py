# -*- coding: utf-8 -*-
"""应期层(大运/流年)复合旺衰可重入模块.

链路(复用已封板辩层, 不重新排盘、不另造强弱裁决器):
  原局 pillars + 岁运柱 extra_pillars
      -> L0 facts / build_tian_he(含岁运合局) / build_wuxing_power(含岁运根与六合半合归化)
      -> build_spectrum_topology 七档结构谱(同一套非对称定档, 输入扩展为原局+岁运)
      -> 冲支五行旺衰有序枚举比较 -> 衰者拔/旺神发/两停

原典依据:
  《滴天髓·冲合》"旺者冲衰衰者拔, 衰神冲旺旺神发";
  《滴天髓·岁运》"冲战视其孰降, 和好视其孰切"。
边界: 只输出结构枚举与变化; 五行旺衰序为布尔优先级多态枚举(非连续分数, # PCT-MARK);
  不输出喜忌/用神/吉凶, 非 STRONG/WEAK 总裁决; 岁运不改变原局月令与日干。
"""
from typing import Any, Dict, List

from engines.common.l0_fact_builder import build as l0build, WUXING, HIDDEN
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology, BRANCH_WX
from engines.common.daymaster_root_class import classify_root_in_branches

LIU_CHONG = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
_CHONG_SET = {frozenset(p) for p in LIU_CHONG}
_BASE_KEYS = ('year', 'month', 'day', 'hour')


def _norm_extra(extra):
    out = []
    for g in extra or []:
        if isinstance(g, str):
            g = [g[0], g[1]]
        out.append([g[0], g[1]])
    return out


def build_transit_power(pillars: Dict[str, list], extra_pillars=None) -> Dict[str, Any]:
    """原局 pillars + 岁运柱 extra_pillars([(gan, zhi), ...]) -> 复合五行动力/七档/根/合冲."""
    extra = _norm_extra(extra_pillars)
    facts = l0build(pillars)
    dm = pillars['day'][0]
    dm_wx = WUXING[dm]

    th = build_tian_he(pillars, facts, extra_pillars=extra)
    wp = build_wuxing_power(pillars, facts, th, extra_pillars=extra)

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

    network = {
        'facts': {'daymaster_element': dm_wx, 'combination_facts': cfc},
        'dimensions': {'ROOT': {'root_class_detail': rcd}},
    }
    spec = build_spectrum_topology(network, wp)

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
        'judgment_status': 'TRANSIT_POWER_STRUCTURE_ONLY',
        'boundary_note': ('原局+岁运复合结构; 复用七档定档不另造强弱; 五行旺衰序为布尔枚举非分数; '
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




