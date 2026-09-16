# -*- coding: utf-8 -*-
"""PATCH-172-D 食神格Candidate->Rule条件契约
required=食神有根/食神透; 食神生财/制杀仅读166 premise, 不等于成立。"""

SHISHEN_BUCKET = {
    'required': ['食神有根', '食神透'],
    'supported_premise': ['食神生财', '食神制杀'],  # 读166, 非成立
    'unknown_pending': ['食带煞而无财', '弃食就煞而透印', '枭神夺食'],
}


def shishen_rule_input(facts):
    tr = facts.get('target_root_facts', {})
    ah = facts.get('any_stem_has_ten_god', {})
    hz = facts.get('hezuo_relation_premise', {})
    def st(v):
        return 'SATISFIED' if v is True else ('UNSATISFIED' if v is False else 'UNKNOWN')
    cond = {
        '食神有根': st(tr.get('食神')),
        '食神透': st(ah.get('食神')),
        '食神生财(premise, 非成立)': st(hz.get('食神生财')),
        '食神制杀(premise, 非成立)': st(hz.get('食神制杀')),
    }
    return {
        'pattern': '食神格',
        'bucket': SHISHEN_BUCKET,
        'conditions': cond,
        'state': 'CANDIDATE',
        'boundary_note': '食神格入口不等于格成; 食神+财不等于食神生财成立; 食神+杀不等于制杀成立; 食带煞而无财/弃食就煞/枭夺食UNKNOWN',
    }
