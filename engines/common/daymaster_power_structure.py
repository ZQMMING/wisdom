# -*- coding: utf-8 -*-
"""PATCH-160-A 日主力量结构发生器 (Daymaster Power Structure Generator)

只组织已有 L0 Fact, 不重算, 不评分, 不权重, 不阈值, 不比较两端。
输出 Daymaster Power Structure Fact (160-A)。160-B 强弱判定 NOT_AUTHORIZED, 不建。

边界(governance/ziping_160a_daymaster_power_structure.md):
- GUANSHA -> DAYMASTER (克日主方向, 非反向)
- seasonal_axis: in_season(月令本气同五行) 与 month_supports(同五行或生我) 分离
- BIJIE/SHISHANG 从 ten_god_members 现筛, 不新造搜索器
- 存在 != 有效; DIRECT 边关系可记, 但不授权"扶身方强"
- 传递链边 (食伤->财, 财->官杀, 官杀->印) = C, 记 UNAUTHORIZED
- 无法确定统一 UNKNOWN, 不压 FALSE
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from engines.common import l0_fact_builder as _l0

WUXING = _l0.WUXING

# 十神分组
SUPPORT_GROUPS = {
    'BIJIE': {'比肩', '劫财'},
    'YIN': {'正印', '偏印'},
}
DRAIN_GROUPS = {
    'SHISHANG': {'食神', '伤官'},
    'CAI': {'正财', '偏财'},
}
CONTROL_GROUPS = {
    'GUANSHA': {'正官', '七杀'},
}
# 传递链边 (五行生克结构, 但"有效力量传递"未授权)
TRANSFER_EDGES = [
    ('SHISHANG', 'CAI', '食伤生财'),
    ('CAI', 'GUANSHA', '财生官杀'),
    ('GUANSHA', 'YIN', '官杀生印'),
]


def _node_from_members(members, tg_set):
    """从 ten_god_members 筛某十神集合的 stem_present/root_present/root_type."""
    stem_present = False
    root_present = False
    root_types = set()
    for m in members:
        if m['ten_god'] not in tg_set:
            continue
        if m['type'] == 'stem':
            stem_present = True
        elif m['type'] == 'hidden':
            root_present = True
            root_types.add(m.get('qi_position', ''))
    return {
        'stem_present': stem_present,
        'root_present': root_present,
        'root_qi_positions': sorted(root_types),
    }


def build_power_structure(pillars):
    """pillars: {year,month,day,hour:[g,z]}。返回 Daymaster Power Structure Fact."""
    dg = pillars['day'][0]
    facts = _l0.build(pillars)
    members = facts.get('ten_god_members', [])
    month_branch = facts['month_branch']

    # --- seasonal_axis: in_season(纯得令) vs month_supports(生我) ---
    month_benqi = _l0.HIDDEN[month_branch][0]
    month_benqi_wx = WUXING[month_benqi]
    dm_wx = WUXING[dg]
    in_season = (month_benqi_wx == dm_wx)
    month_supports = bool(facts.get('month_supports_daymaster', False))

    # --- root_axis ---
    rwc = facts.get('root_weight_class_facts', {})
    heavy = any(v.get('class') == 'HEAVY' for v in rwc.values())
    light = any(v.get('class') == 'LIGHT' for v in rwc.values())
    if heavy:
        root_weight_class = 'HEAVY'
    elif light:
        root_weight_class = 'LIGHT'
    else:
        root_weight_class = 'NONE'

    # --- support/drain/control groups ---
    def _group(gdict):
        out = {}
        for gname, tg_set in gdict.items():
            out[gname] = _node_from_members(members, tg_set)
        return out

    support_group = _group(SUPPORT_GROUPS)
    drain_group = _group(DRAIN_GROUPS)
    control_group = _group(CONTROL_GROUPS)

    # --- DIRECT edges (关系结构可记, 不授权强弱 Judgment) ---
    def _present(node):
        return node['stem_present'] or node['root_present']

    direct_edges = [
        {'source': 'BIJIE', 'target': 'DAYMASTER', 'relation': '同类扶身',
         'active': _present(support_group['BIJIE'])},
        {'source': 'YIN', 'target': 'DAYMASTER', 'relation': '生我扶身',
         'active': _present(support_group['YIN'])},
        {'source': 'DAYMASTER', 'target': 'SHISHANG', 'relation': '日主泄气',
         'active': _present(drain_group['SHISHANG'])},
        {'source': 'DAYMASTER', 'target': 'CAI', 'relation': '日主耗身(克财)',
         'active': _present(drain_group['CAI'])},
        {'source': 'GUANSHA', 'target': 'DAYMASTER', 'relation': '官杀克身',
         'active': _present(control_group['GUANSHA'])},
    ]
    active_edges = [e for e in direct_edges if e['active']]
    inactive_edges = [e for e in direct_edges if not e['active']]

    # --- transfer edges: 结构存在可查, 有效传递未授权 -> UNAUTHORIZED ---
    unauthorized_edges = [
        {'source': s, 'target': t, 'relation': rel,
         'authorization': 'C',
         'note': '五行生克结构可查, 但"有效力量传递"未授权, 不参与强弱'}
        for s, t, rel in TRANSFER_EDGES
    ]

    return {
        'generator': 'DaymasterPowerStructureGenerator',
        'patch': 'PATCH-160-A',
        'daymaster': {'stem': dg, 'wuxing': dm_wx},
        'seasonal_axis': {
            'in_season': in_season,
            'month_supports': month_supports,
            'note': 'in_season=月令本气同五行(纯得令); month_supports=同五行或生我; 不判强弱',
        },
        'root_axis': {
            'root_weight_class': root_weight_class,
            'per_pillar': rwc,
        },
        'support_group': support_group,
        'drain_group': drain_group,
        'control_group': control_group,
        'active_edges': active_edges,
        'inactive_direct_edges': inactive_edges,
        'unauthorized_edges': unauthorized_edges,
        'unknown_edges': [],
        'judgment_status': 'NOT_AUTHORIZED',
        'note': '160-A 只组织结构事实, 不输出身强/身弱; 不评分不权重不比较两端',
    }
