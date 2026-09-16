# -*- coding: utf-8 -*-
"""PATCH-171 八格Entry->Candidate Contract
Entry只传候选身份, 绝不升级成Judgment/格成。"""

# 月令本气十神 -> 八格Entry (建禄月劫/食神/七煞/伤官/财/官/印)
_TG_TO_ENTRY = {
    '比肩': '建禄', '劫财': '月劫',
    '食神': '食神格', '七杀': '七煞格', '伤官': '伤官格',
    '正财': '财格', '偏财': '财格',
    '正官': '官格',
    '正印': '印格', '偏印': '印格',
}


def build_candidates(facts):
    """汇总八格Entry为Candidate; state=CANDIDATE, 不判成格/身强弱/用神。"""
    mqi_god = facts.get('month_qi_stem') and None  # placeholder
    # 月令本气十神: 由root/透明事实推; 直接从l0的month本气取
    from engines.common.l0_fact_builder import ten_god
    dg = facts.get('_daymaster')
    # 本批l0 entry字段已分好, 优先用专门entry
    cands = []
    # 建禄月劫
    jy = facts.get('jianlu_yuejie_entry', {})
    if jy.get('is_entry'):
        cands.append(_mk(jy['type'], 'jianlu_yuejie_entry'))
    # 食神/七煞/伤官/阳刃
    for key, etype in [('shishen_entry','食神格'),('qisha_entry','七煞格'),
                       ('shangguan_entry','伤官格'),('yangren_entry','阳刃格')]:
        e = facts.get(key, {})
        if e.get('is_entry'):
            cands.append(_mk(etype, key))
    return {
        'candidates': cands,
        'boundary': {
            'state_values': ['CANDIDATE', 'BLOCKED', 'UNKNOWN'],
            'forbidden_outputs': ['格成','格败','吉','凶','身强','身弱','旺','弱','用神已定'],
            'note': 'Entry仅候选身份; 配合前提≠成格; 成格条件后续Rule/Judgment',
        },
    }


def _mk(etype, src):
    return {
        'entry_type': etype,
        'state': 'CANDIDATE',
        'source_fact_ids': [src],
        'premise_refs': ['hezuo_relation_premise'],
        'boundary': f'{etype}=候选身份, 不判成格',
    }
