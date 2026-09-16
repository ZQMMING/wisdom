# -*- coding: utf-8 -*-
"""PATCH-160.11 Structure Comparison Readiness Rule
只判: 日主方↔目标十神方 比较所需已授权结构输入是否齐备。
SATISFIED=输入齐备, 非比较结果成立。不判强弱。"""

_TARGET_CAT = {
    '财': {'正财', '偏财'}, '官': {'正官', '七杀'}, '印': {'正印', '偏印'},
}


def readiness_readiness(facts, target):
    """facts: L0 build输出; target: '财'/'官'/'印'
    返回三态readiness, 缺什么UNKNOWN."""
    needs = []
    # 日主方结构
    has_root = any(facts.get('root_facts', {}).values())
    has_month = 'month_supports_daymaster' in facts
    dm_members = [m for m in facts.get('ten_god_members', [])
                  if m['ten_god'] in {'比肩', '劫财', '正印', '偏印'}]
    # 目标方结构
    cat = _TARGET_CAT.get(target)
    if not cat:
        return {'state': 'UNKNOWN', 'reason': f'未知target:{target}',
                'direction': None, 'missing': ['unknown_target']}
    has_target_root = facts.get('target_root_facts', {}).get(target)
    target_members = [m for m in facts.get('ten_god_members', [])
                      if m['ten_god'] in cat]

    missing = []
    if not dm_members: missing.append('日主方成员不可追溯')
    if not has_root: missing.append('根气信息缺失')
    if not has_month: missing.append('月令信息缺失')
    if not target_members: missing.append(f'{target}方成员不可追溯')
    if has_target_root is None: missing.append(f'{target}根气信息缺失')

    if missing:
        return {'state': 'UNKNOWN', 'reason': '比较输入不齐备',
                'direction': None, 'missing': missing}
    return {'state': 'SATISFIED', 'reason': '比较所需已授权结构输入齐备',
            'direction': f'日主↔{target}结构可比较(仅输入齐备, 非强弱结论)',
            'missing': [],
            'dm_members': len(dm_members), 'target_members': len(target_members)}
