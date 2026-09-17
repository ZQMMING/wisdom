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


def shishen_zhisha_established(facts):
    """食神制杀结构成立(三态); 有效性/身强/制化足量仍UNKNOWN, 不判美格。"""
    se = facts.get('shishen_entry', {})
    members = facts.get('ten_god_members', [])
    is_shishen = se.get('is_entry')
    has_sha = any(m.get('ten_god') == '七杀' for m in members)
    if is_shishen is not True:
        return {'relation': '食神制杀', 'state': 'UNSATISFIED',
                'reason': '非食神格入口'}
    if has_sha is False:
        return {'relation': '食神制杀', 'state': 'UNSATISFIED',
                'reason': '四柱不见七杀'}
    if has_sha is True:
        return {'relation': '食神制杀', 'state': 'SATISFIED',
                'reason': '月令食神+见七杀(结构前提)',
                'note': '仅结构前提具备; 身强(160未授权)/制化足量/财党杀/枭夺食仍UNKNOWN, 不等于制杀有效或美格'}
    return {'relation': '食神制杀', 'state': 'UNKNOWN',
            'reason': '七杀信息不全'}


def shangguan_shengcai_established(facts):
    """伤官生财结构成立(三态); 财有根/伤官旺/身强仍后续, 不判格成。
    原典(沈): 伤官生财=月令伤官+见财; "有根"指日主, 财有根为徐注质量条件非硬成立条件。"""
    sg = facts.get('shangguan_entry', {})
    ah = facts.get('any_stem_has_ten_god', {})
    is_sg = sg.get('is_entry')
    has_cai = ah.get('财')
    if is_sg is not True:
        return {'relation': '伤官生财', 'state': 'UNSATISFIED',
                'reason': '非伤官格入口'}
    if has_cai is False:
        return {'relation': '伤官生财', 'state': 'UNSATISFIED',
                'reason': '四柱不见财'}
    if has_cai is True:
        return {'relation': '伤官生财', 'state': 'SATISFIED',
                'reason': '月令伤官+见财',
                'note': '财有根(质量evidence)/日主有根身强/伤官旺/财旺/位置隔位仍后续UNKNOWN; 财无根不等于关系不存在; 不等于格成'}
    return {'relation': '伤官生财', 'state': 'UNKNOWN',
            'reason': '财信息不全'}
