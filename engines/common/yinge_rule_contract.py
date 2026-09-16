# -*- coding: utf-8 -*-
"""PATCH-172-C 印格Candidate->Rule条件契约
required=印有根/印透; 贪财破印不做布尔blocked(后续Rule)。"""

YINGE_BUCKET = {
    'required': ['印有根', '印透'],
    'blocked': [],  # 贪财破印是作用关系+条件, 不直接布尔
    'supported': ['官印双全', '印轻逢煞', '印多逢财'],
    'unknown_pending': ['贪财破印'],
}


def yinge_rule_input(facts):
    tr = facts.get('target_root_facts', {})
    ah = facts.get('any_stem_has_ten_god', {})
    def st(v):
        return 'SATISFIED' if v is True else ('UNSATISFIED' if v is False else 'UNKNOWN')
    cond = {
        '印有根': st(tr.get('印')),
        '印透': st(ah.get('印')),
        '财印同现(结构, 非贪财破印)': st(ah.get('财')),
    }
    return {
        'pattern': '印格',
        'bucket': YINGE_BUCKET,
        'conditions': cond,
        'state': 'CANDIDATE',
        'boundary_note': '印格入口≠印格成; 财+印同现≠贪财破印(作用关系后续Rule); 贪财破印保持UNKNOWN',
    }
