# -*- coding: utf-8 -*-
"""PATCH-173-A 食神生财 premise->成立 Relation Rule
原典: 月令食神, 四柱见财, 为食神生财; 且要求财有根。
成立=食神格入口+财同现+财有根; 位置/隔位/食神旺衰仍UNKNOWN。"""


def shisheng_shengcai_established(facts):
    """食神生财是否成立(三态); 不判格成。"""
    se = facts.get('shishen_entry', {})
    ah = facts.get('any_stem_has_ten_god', {})
    tr = facts.get('target_root_facts', {})
    # ①月令食神入口
    is_shishen = se.get('is_entry')
    # ②财同现
    has_cai = ah.get('财')
    # ③财有根(原典: 食神生财要求财有根)
    cai_root = tr.get('财')
    if is_shishen is not True:
        return {'relation': '食神生财', 'state': 'UNSATISFIED',
                'reason': '非食神格入口'}
    if has_cai is False or cai_root is False:
        return {'relation': '食神生财', 'state': 'UNSATISFIED',
                'reason': '无财或财无根'}
    if has_cai is True and cai_root is True:
        return {'relation': '食神生财', 'state': 'SATISFIED',
                'reason': '月令食神+见财+财有根',
                'note': '位置/隔位/食神旺衰仍UNKNOWN, 不等于格成'}
    return {'relation': '食神生财', 'state': 'UNKNOWN',
            'reason': '财同现或财根信息不全'}
