# -*- coding: utf-8 -*-
"""PATCH-172-D 食神格Candidate->Rule条件契约
required=食神有根/食神透; 食神生财/制杀仅读166 premise, 不等于成立。"""

SHISHEN_BUCKET = {
    'required': ['食神有根', '食神透'],
    'supported_premise': ['食神生财', '食神制杀'],  # 读166, 非成立
    'supported': ['食带煞而无财'],
    'blocked': ['食神逢枭'],
    'unknown_pending': ['弃食就煞而透印', '生财露煞', '枭神夺食'],
}


def shishen_rule_input(facts):
    tr = facts.get('target_root_facts', {})
    ah = facts.get('any_stem_has_ten_god', {})
    hz = facts.get('hezuo_relation_premise', {})
    tg = facts.get('ten_god_members', [])
    def st(v):
        return 'SATISFIED' if v is True else ('UNSATISFIED' if v is False else 'UNKNOWN')
    # PATCH-205 食带煞而无财 supported: 见七杀 + 天干藏干均无财
    has_qisha = any(m.get('ten_god') == '七杀' for m in tg)
    tian_no_cai = ah.get('财') is False
    cang_no_cai = tr.get('财') is False
    no_cai = tian_no_cai and cang_no_cai
    dai_sha = 'SATISFIED' if (has_qisha is True and no_cai is True) else (
        'UNSATISFIED' if (has_qisha is False or (ah.get('财') is True or tr.get('财') is True)) else 'UNKNOWN')
    # PATCH-205 食神逢枭 blocked: 见偏印(非正印, 天干+藏干)
    has_pianyin = any(m.get('ten_god') == '偏印' for m in tg)
    cond = {
        '食神有根': st(tr.get('食神')),
        '食神透': st(ah.get('食神')),
        '食神生财(premise, 非成立)': st(hz.get('食神生财')),
        '食神制杀(premise, 非成立)': st(hz.get('食神制杀')),
        '食带煞而无财': dai_sha,
        '食神逢枭': st(has_pianyin),
    }
    return {
        'pattern': '食神格',
        'bucket': SHISHEN_BUCKET,
        'conditions': cond,
        'state': 'CANDIDATE',
        'boundary_note': '食神格入口不等于格成; 食带煞而无财=见七杀+天干藏干均无财(205, supported非成格); 食神逢枭=见偏印(205, blocked非枭神夺食非FAILED); 偏印非正印; 无财=天干+藏干; 弃食就煞/生财露煞/身强食旺/调候例外HOLD',
    }
