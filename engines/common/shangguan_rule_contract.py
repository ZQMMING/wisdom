# -*- coding: utf-8 -*-
"""PATCH-172-F 伤官格Candidate->Rule条件契约
required=伤官有根/伤官透; 生财/佩印仅读166 premise; 伤官旺/印有根/身强弱unknown。"""

SHANGGUAN_BUCKET = {
    'required': ['伤官有根', '伤官透'],
    'supported_premise': ['伤官生财', '伤官佩印'],  # 读166, 非成立
    'unknown_pending': ['伤官旺', '印有根', '身强', '身弱'],
}


def shangguan_rule_input(facts):
    tr = facts.get('target_root_facts', {})
    ah = facts.get('any_stem_has_ten_god', {})
    hz = facts.get('hezuo_relation_premise', {})
    def st(v):
        return 'SATISFIED' if v is True else ('UNSATISFIED' if v is False else 'UNKNOWN')
    cond = {
        '伤官有根': st(tr.get('伤官')),
        '伤官透': st(ah.get('伤官')),
        '伤官生财(premise, 非成立)': st(hz.get('伤官生财')),
        '伤官佩印(premise, 非成立)': st(hz.get('伤官佩印')),
    }
    return {
        'pattern': '伤官格',
        'bucket': SHANGGUAN_BUCKET,
        'conditions': cond,
        'state': 'CANDIDATE',
        'boundary_note': '伤官格入口不等于格成; 伤官+财不等于生财成立; 伤官+印不等于佩印成立; 伤官旺/印有根/身强弱unknown; 伤官有根透不等于伤官旺',
    }
