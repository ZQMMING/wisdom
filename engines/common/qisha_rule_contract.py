# -*- coding: utf-8 -*-
"""PATCH-172-E 七煞格Candidate->Rule条件契约
required=杀有根/杀透; 制杀/化杀仅读166 premise; 身强/逢制NOT_AUTHORIZED。"""

QISHA_BUCKET = {
    'required': ['七杀有根', '七杀透'],
    'supported_premise': ['食神制杀', '印化杀'],  # 读166, 非成立
    'unknown_pending': ['身强', '逢制', '七杀逢财无制'],
}


def qisha_rule_input(facts):
    tr = facts.get('target_root_facts', {})
    ah = facts.get('any_stem_has_ten_god', {})
    hz = facts.get('hezuo_relation_premise', {})
    def st(v):
        return 'SATISFIED' if v is True else ('UNSATISFIED' if v is False else 'UNKNOWN')
    cond = {
        '七杀有根': st(tr.get('七杀')),
        '七杀透': st(ah.get('七杀')),
        '食神制杀(premise, 非成立)': st(hz.get('食神制杀')),
        '印化杀(premise, 非成立)': st(hz.get('印化杀')),
    }
    return {
        'pattern': '七煞格',
        'bucket': QISHA_BUCKET,
        'conditions': cond,
        'state': 'CANDIDATE',
        'boundary_note': '七煞格入口不等于格成; 七杀+食神不等于制杀成立; 七杀+印不等于化杀成立; 身强/逢制NOT_AUTHORIZED(160); 杀有根/透不等于杀旺',
    }
