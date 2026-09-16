# -*- coding: utf-8 -*-
"""PATCH-172-B 官格Candidate->Rule条件契约
月令正官+财印配合+刑冲破害阻断; 官透+财印≠官格成。"""

GUANGE_BUCKET = {
    'required': ['官有根', '官透'],
    'blocked': ['官星受冲'],
    'supported': ['财印护官', '运之喜忌'],
    'unknown_pending': ['刑', '破', '害'],
}


def guange_rule_input(facts):
    tr = facts.get('target_root_facts', {})
    ah = facts.get('any_stem_has_ten_god', {})
    trel = facts.get('target_relation_facts', {})
    def st(v):
        return 'SATISFIED' if v is True else ('UNSATISFIED' if v is False else 'UNKNOWN')
    cond = {
        '官有根': st(tr.get('官')),
        '官透': st(ah.get('官')),
        '官星受冲': st(trel.get('官星受冲')),
        '见财(配合路径, 非阻断)': st(ah.get('财')),
    }
    return {
        'pattern': '官格',
        'bucket': GUANGE_BUCKET,
        'conditions': cond,
        'state': 'CANDIDATE',
        'boundary_note': '官逢财印为成格路径(见财≠blocked); 财/印存在≠财生官/印护官成立; 仍需无官星受冲; 刑/破/害未建UNKNOWN; 官透+财印≠官格成',
    }
