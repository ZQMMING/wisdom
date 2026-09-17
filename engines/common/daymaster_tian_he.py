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


def build_tian_he(pillars: Dict[str, Any], facts: Dict[str, Any]) -> Dict[str, Any]:
    from engines.common.l0_fact_builder import WUXING
    month_benqi_stem = facts['hidden_stems']['month'][0]
    month_qi_wx = WUXING[month_benqi_stem]

    stems = {k: pillars[k][0] for k in ('year', 'month', 'day', 'hour')}
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

    has_chen = any(pillars[k][1] == '辰' for k in keys)

    return {
        'generator': 'TianHeAnalyzer',
        'month_qi_wuxing': month_qi_wx,
        'he_pairs': pairs,
        'huashen_on_month_qi': any(p['huashen_on_month_qi'] for p in pairs),
        'has_long_chen': has_chen,
        'judgment_status': 'STRUCTURE_ONLY',
        'boundary_note': (
            '仅记天干合对/化神/化神得月令/逢辰结构; '
            '不判真化假化, 不判化气格, 太过不及未量化'
        ),
    }
