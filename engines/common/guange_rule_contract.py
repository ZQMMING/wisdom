# -*- coding: utf-8 -*-
"""PATCH-172-B 官格Candidate->Rule条件契约
月令正官+财印配合+刑冲破害阻断; 官透+财印≠官格成。"""

GUANGE_BUCKET = {
    'required': ['官有根', '官透'],
    'blocked': ['官星受冲', '伤官克官'],
    'supported': ['财印护官', '运之喜忌'],
    'blocked_unknown': ['刑', '破', '害'],  # 175: 接163结构Fact, 存在=UNKNOWN, 无=CLEAR
}


def _struct_state(lst):
    """有结构=UNKNOWN(动不动未授权); 无结构=CLEAR; 缺数据=UNKNOWN。"""
    if lst is None:
        return 'UNKNOWN'
    return 'UNKNOWN' if len(lst) > 0 else 'CLEAR'


def guange_rule_input(facts):
    tr = facts.get('target_root_facts', {})
    ah = facts.get('any_stem_has_ten_god', {})
    trel = facts.get('target_relation_facts', {})
    comb = facts.get('combination_facts', {})
    def st(v):
        return 'SATISFIED' if v is True else ('UNSATISFIED' if v is False else 'UNKNOWN')
    # PATCH-198 伤官克官 blocked结构: 天干见伤官(复用ten_god_members, 非直接FAILED)
    # 原典"官逢伤克刑冲官格败"; 财印救应后续Rule, 此仅blocked结构
    tg = facts.get('ten_god_members', [])
    shangguan_on_stem = any(m.get('type') == 'stem' and m.get('ten_god') == '伤官' for m in tg)
    cond = {
        '官有根': st(tr.get('官')),
        '官透': st(ah.get('官')),
        '官星受冲': st(trel.get('官星受冲')),
        '伤官克官': st(shangguan_on_stem),
        '刑': _struct_state(comb.get('sanxing')),
        '破': _struct_state(comb.get('liupo')),
        '害': _struct_state(comb.get('liuhai')),
        '见财(配合路径, 非阻断)': st(ah.get('财')),
    }
    return {
        'pattern': '官格',
        'bucket': GUANGE_BUCKET,
        'conditions': cond,
        'state': 'CANDIDATE',
        'boundary_note': '官逢财印为成格路径(见财≠blocked); 官星受冲=BLOCKED(155); 伤官克官=blocked结构(198, 非直接FAILED, 财印救应后续Rule); 刑/破/害结构存在=UNKNOWN(动不动未授权)不升级BLOCKED, 无结构=CLEAR; CLEAR≠官格无问题; 官透+财印+无伤官≠官格成',
    }
