# -*- coding: utf-8 -*-
"""身旺衰多维判断层: 综合月令+有效根+生扶+克泄, 输出多态枚举.
不评分不加权, 布尔+多态枚举+多维拓扑.
输出: 月令维度/根气维度/生扶维度/克泄维度/综合旺衰(七档)."""
from typing import Dict, List, Any

WUXING = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火',
    '戊': '土', '己': '土', '庚': '金', '辛': '金',
    '壬': '水', '癸': '水',
}

# 十神分类
SUPPORT_TG = {'正印', '偏印', '比肩', '劫财'}  # 生扶
DRAIN_TG = {'食神', '伤官'}  # 泄
CONTROL_TG = {'正官', '七杀', '正财', '偏财'}  # 克耗


def judge_wangshuai(
    facts: Dict[str, Any],
    root_effectiveness: Dict[str, Any],
) -> Dict[str, Any]:
    """身旺衰多维判断.
    输入: facts(l0_fact_builder输出), root_effectiveness(根有效性过滤输出)
    输出: 多维旺衰状态 + 综合七档
    """
    dm = facts.get('day_stem', '')
    dm_wx = WUXING.get(dm, '')

    # 1. 月令维度
    month_supports = facts.get('month_supports_daymaster', False)
    month_qi_ten_god = facts.get('month_qi_ten_god', '')
    in_season = month_supports or month_qi_ten_god in ('比肩', '劫财', '正印', '偏印')
    if in_season:
        season_state = '得令'
    elif month_qi_ten_god in ('正官', '七杀', '正财', '偏财', '食神', '伤官'):
        season_state = '失令'
    else:
        season_state = '未知'

    # 2. 根气维度(有效根)
    effective_rwc = root_effectiveness.get('effective_root_weight_class', 'NONE')
    if effective_rwc == 'HEAVY':
        root_state = '有效重根'
    elif effective_rwc == 'LIGHT':
        root_state = '有效轻根'
    else:
        root_state = '无有效根'

    # 3. 生扶/克泄维度(天干+地支藏干)
    stem_relations = facts.get('stem_relations', {}) or {}
    ten_god_members = facts.get('ten_god_members', []) or []

    support_count = 0
    drain_count = 0
    control_count = 0

    # 天干
    for v in stem_relations.values():
        tg = v.get('ten_god', '')
        if tg in SUPPORT_TG:
            support_count += 1
        elif tg in DRAIN_TG:
            drain_count += 1
        elif tg in CONTROL_TG:
            control_count += 1

    # 地支藏干(只算本气)
    hidden_stems = facts.get('hidden_stems', {}) or {}
    for pillar, stems in hidden_stems.items():
        if stems and len(stems) > 0:
            benqi = stems[0]  # 本气
            # 本气对应的十神
            benqi_wx = WUXING.get(benqi, '')
            if benqi_wx == dm_wx:
                support_count += 1  # 比肩/劫财
            elif benqi_wx == _sheng_wo(dm_wx):
                support_count += 1  # 印
            elif benqi_wx == _wo_sheng(dm_wx):
                drain_count += 1  # 食伤
            else:
                control_count += 1  # 财官

    # 生扶/克泄比较
    total_support = support_count
    total_drain_control = drain_count + control_count
    if total_support > total_drain_control + 1:
        support_state = '生扶成势'
    elif total_support > total_drain_control:
        support_state = '生扶稍强'
    elif total_support == total_drain_control:
        support_state = '生克平衡'
    elif total_support + 1 == total_drain_control:
        support_state = '克泄稍强'
    else:
        support_state = '克泄成势'

    # 4. 综合旺衰(七档: 极旺/旺/偏旺/中和/偏衰/衰/极衰)
    score = 0
    # 月令
    if season_state == '得令':
        score += 2
    elif season_state == '失令':
        score -= 2
    # 根气
    if root_state == '有效重根':
        score += 2
    elif root_state == '有效轻根':
        score += 1
    elif root_state == '无有效根':
        score -= 1
    # 生扶克泄
    if support_state == '生扶成势':
        score += 2
    elif support_state == '生扶稍强':
        score += 1
    elif support_state == '克泄稍强':
        score -= 1
    elif support_state == '克泄成势':
        score -= 2

    # 七档映射
    if score >= 5:
        comprehensive = '极旺'
    elif score >= 3:
        comprehensive = '旺'
    elif score >= 1:
        comprehensive = '偏旺'
    elif score == 0:
        comprehensive = '中和'
    elif score >= -2:
        comprehensive = '偏衰'
    elif score >= -4:
        comprehensive = '衰'
    else:
        comprehensive = '极衰'

    return {
        'daymaster': dm,
        'season': {'state': season_state, 'month_supports': month_supports, 'month_qi_ten_god': month_qi_ten_god},
        'root': {'state': root_state, 'effective_rwc': effective_rwc},
        'support': {
            'state': support_state,
            'support_count': support_count,
            'drain_count': drain_count,
            'control_count': control_count,
            'total_support': total_support,
            'total_drain_control': total_drain_control,
        },
        'comprehensive': comprehensive,
        'score': score,  # PCT-MARK: 仅用于七档映射, 非最终评分
        'boundary_note': '身旺衰多维判断: 月令+有效根+生扶克泄; 七档枚举不评分; score仅用于七档映射(PCT-MARK)',
    }


def _sheng_wo(wx):
    """生我者(印)"""
    m = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}
    return m.get(wx, '')


def _wo_sheng(wx):
    """我生者(食伤)"""
    m = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
    return m.get(wx, '')
