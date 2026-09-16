# -*- coding: utf-8 -*-
"""PATCH-172-A 财格Candidate->Rule条件契约
财格入口≠财格成; 逐条挂原典已授权条件, 三态, 不产Judgment。"""

# 财格三桶(早期Assertion已封): required/blocked/supported
CAIGE_BUCKET = {
    'required': ['财有根', '财透'],
    'blocked': ['财太露'],
    'supported': ['格清', '配合', '运之喜忌'],
}


def caige_rule_input(facts):
    """财格各condition三态; 不判成格, 不出is_success。"""
    # 财有根 = target_root_facts['财']
    has_cai_root = facts.get('target_root_facts', {}).get('财')
    # 财透 = 月令透干含财(month_transparent)
    # month_transparent 是月令藏干透出; 财透条件读transparent evaluator已判
    cai_root_state = 'SATISFIED' if has_cai_root is True else (
        'UNSATISFIED' if has_cai_root is False else 'UNKNOWN')
    # 财透 = 已授权"天干透财"Fact(any_stem_has_ten_god['财'], 四柱任一天干透财), 非month_transparent
    cai_tou = facts.get('any_stem_has_ten_god', {}).get('财')
    cai_tou_state = 'SATISFIED' if cai_tou is True else (
        'UNSATISFIED' if cai_tou is False else 'UNKNOWN')
    # 财太露: 保持UNKNOWN(161封板, 禁count)
    cond = {
        '财有根': cai_root_state,
        '财透': cai_tou_state,
        '财太露': 'UNKNOWN',  # 161: 无机器充分条件
    }
    return {
        'pattern': '财格',
        'bucket': CAIGE_BUCKET,
        'conditions': cond,
        'state': 'CANDIDATE',  # 仍候选, 不判成格
        'boundary_note': '财格入口≠财格成; 财透≠财旺; 财有根≠财旺; 财太露UNKNOWN; 无财透/无财有根≠财格必败(财格多路径, 后续逐路径Rule)',
    }
