# -*- coding: utf-8 -*-
"""
L3-3 格局成败规则表
出处: 子平真诠·论用神成败
"""

# 善神格(顺用): 成格=无恶神破
GOOD_SPIRIT_RULES = {
    '正官': {
        '顺用': '生扶',
        '成格条件': '无伤官见官+无七杀混官',
        '破格物': ['伤官', '七杀'],
        'source': '子平真诠: 官星不可被伤官所伤',
    },
    '正印': {
        '顺用': '生扶',
        '成格条件': '无财星破印',
        '破格物': ['正财', '偏财'],
        'source': '子平真诠: 印逢财而被破',
    },
    '偏财': {
        '顺用': '生扶',
        '成格条件': '无比劫夺财',
        '破格物': ['比肩', '劫财'],
        'source': '子平真诠: 财逢劫而被夺',
    },
    '食神': {
        '顺用': '生扶',
        '成格条件': '无枭神夺食',
        '破格物': ['偏印'],
        'source': '子平真诠: 食逢枭而被夺',
    },
}

# 恶神格(逆用): 成格=有制化
BAD_SPIRIT_RULES = {
    '七杀': {
        '逆用': '制化',
        '成格条件': '有食神制杀 或 有印星化杀',
        '救应物': ['食神', '偏印'],
        'source': '子平真诠: 杀无制则为鬼, 有制则为权',
    },
    '伤官': {
        '逆用': '制化',
        '成格条件': '有财星泄伤 或 有印星制伤',
        '救应物': ['正财', '偏财', '偏印'],
        'source': '子平真诠: 伤官伤尽见财官',
    },
    '劫财': {
        '逆用': '制化',
        '成格条件': '有官杀制劫',
        '救应物': ['正官', '七杀'],
        'source': '子平真诠: 劫财需官杀制',
    },
    '羊刃': {
        '逆用': '制化',
        '成格条件': '有官杀制刃',
        '救应物': ['正官', '七杀'],
        'source': '子平真诠: 羊刃喜官杀制',
    },
}


def check_pattern_success(pattern, four_stems, four_branches):
    """
    格局成败检查
    返回: (成格/败格/待定, 原因)
    """
    # 善神格: 查破格物
    if pattern in GOOD_SPIRIT_RULES:
        rule = GOOD_SPIRIT_RULES[pattern]
        po_ge = [p for p in rule['破格物'] if _stem_has_ge(p, four_stems)]
        if po_ge:
            return '败格', f'破格物: {po_ge}'
        return '成格', rule['成格条件']

    # 恶神格: 查救应物
    if pattern in BAD_SPIRIT_RULES:
        rule = BAD_SPIRIT_RULES[pattern]
        jiu_ying = [p for p in rule['救应物'] if _stem_has_ge(p, four_stems)]
        if jiu_ying:
            return '成格', f'救应: {jiu_ying}'
        return '败格', '无制化'

    return '待定', '非八格'


def _stem_has_ge(pattern_name, four_stems):
    """检查天干是否有该十神"""
    # TODO: 查四柱天干是否含该十神
    # 暂简化: 查天干五行
    return False


if __name__ == '__main__':
    print('=== L3-3格局成败规则表 ===')
    print()
    print('善神格(顺用):')
    for k, v in GOOD_SPIRIT_RULES.items():
        print(f'  {k}: 破格={v["破格物"]}')
    print()
    print('恶神格(逆用):')
    for k, v in BAD_SPIRIT_RULES.items():
        print(f'  {k}: 救应={v["救应物"]}')
