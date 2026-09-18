# -*- coding: utf-8 -*-
"""天干五合→化神 结构分析.
原典(渊海子平121-003):
  甲己化土 乙庚化金 丙辛化水 丁壬化木 戊癸化火
  月令生旺养库临官之地方化, 逢龙(辰)即化, 太过不及皆不能化.
本层只记录结构事实: 合对/化神五行/化神得月令否/逢龙否.
不判真化假化, 不判化气格, 不判吉凶."""
from typing import Any, Dict

HE_TO_HUASHEN = {
    frozenset(('甲', '己')): '土',
    frozenset(('乙', '庚')): '金',
    frozenset(('丙', '辛')): '水',
    frozenset(('丁', '壬')): '木',
    frozenset(('戊', '癸')): '火',
}


def build_tian_he(pillars: Dict[str, Any], facts: Dict[str, Any], extra_pillars=None) -> Dict[str, Any]:
    from engines.common.l0_fact_builder import WUXING
    month_benqi_stem = facts['hidden_stems']['month'][0]
    month_qi_wx = WUXING[month_benqi_stem]

    extra_pillars = extra_pillars or []
    stems = {k: pillars[k][0] for k in ('year', 'month', 'day', 'hour')}
    for _i, _gz in enumerate(extra_pillars):
        stems['t%d' % _i] = _gz[0]
    pairs = []
    keys = list(stems.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = stems[keys[i]], stems[keys[j]]
            hs = frozenset((a, b))
            if hs in HE_TO_HUASHEN:
                pairs.append({
                    'pillars': [keys[i], keys[j]],
                    'stems': [a, b],
                    'huashen_wuxing': HE_TO_HUASHEN[hs],
                    'huashen_on_month_qi': HE_TO_HUASHEN[hs] == month_qi_wx,
                })

    _cf = facts.get('combination_facts', {}) or {}
    sanhe_ju = list(_cf.get('sanhe', []))
    sanhui_ju = list(_cf.get('sanhui', []))
    _all_zhi = [pillars[k][1] for k in ('year', 'month', 'day', 'hour')] + [g[1] for g in extra_pillars]
    has_chen = '辰' in _all_zhi
    if extra_pillars:
        SANHE3 = {frozenset(('申', '子', '辰')): ('申子辰', '水'), frozenset(('寅', '午', '戌')): ('寅午戌', '火'),
                  frozenset(('巳', '酉', '丑')): ('巳酉丑', '金'), frozenset(('亥', '卯', '未')): ('亥卯未', '木')}
        SANHUI3 = {frozenset(('寅', '卯', '辰')): ('寅卯辰', '木'), frozenset(('巳', '午', '未')): ('巳午未', '火'),
                   frozenset(('申', '酉', '戌')): ('申酉戌', '金'), frozenset(('亥', '子', '丑')): ('亥子丑', '水')}
        _zset = set(_all_zhi)
        def _seen(lst):
            out = set()
            for it in lst:
                out.add(frozenset(c for c in str(it) if c in
                                  '子丑寅卯辰巳午未申酉戌亥'))
            return out
        _sh, _sh3 = _seen(sanhe_ju), _seen(sanhui_ju)
        for br, (nm, wx) in SANHE3.items():
            if br.issubset(_zset) and br not in _sh:
                sanhe_ju.append('%s合%s' % (nm, wx)); _sh.add(br)
        for br, (nm, wx) in SANHUI3.items():
            if br.issubset(_zset) and br not in _sh3:
                sanhui_ju.append('%s三会%s' % (nm, wx)); _sh3.add(br)

    return {
        'generator': 'TianHeAnalyzer',
        'month_qi_wuxing': month_qi_wx,
        'he_pairs': pairs,
        'huashen_on_month_qi': any(p['huashen_on_month_qi'] for p in pairs),
        'has_long_chen': has_chen,
        'sanhe_ju': sanhe_ju,
        'sanhui_ju': sanhui_ju,
        'judgment_status': 'STRUCTURE_ONLY',
        'boundary_note': (
            '仅记天干合对/化神/化神得月令/逢辰结构; '
            '不判真化假化, 不判化气格, 太过不及未量化'
        ),
    }
