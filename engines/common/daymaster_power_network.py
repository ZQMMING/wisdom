# -*- coding: utf-8 -*-
"""PATCH-160-B V2 Daymaster Strength Multi-Dimensional Network
不做总裁决器, 不压缩成 STRONG/WEAK.
把 160-A 五轴转成 节点+边+关系类型+方向+来源 的结构网络.
经典规则未来通过 Query Interface 各自查询网络, 不汇总成总分.
不改 dbadfedc 主链, 不接生产.
"""
from typing import Any, Dict, List


# ---- Dimension Types（原著明确的独立轴）----
DIMENSIONS = (
    'SEASONAL',    # 得令/失令
    'ROOT',        # 通根/根重
    'SUPPORT',     # 党众/助寡（印比）
    'DRAIN',       # 泄耗（食伤/财）
    'CONTROL',     # 克制（官杀）
    'TWO_SIDE',    # 两端成势
)

# ---- Edge Types（关系语义）----
EDGE_TYPES = (
    'ROOT_RELATION',       # 日主 ← 根
    'SEASONAL_RELATION',   # 月令 ↔ 日主
    'SUPPORT_RELATION',    # 印/比劫 → 日主
    'DRAIN_RELATION',      # 日主 → 食伤/财
    'CONTROL_RELATION',    # 官杀 → 日主
    'PRODUCE_RELATION',    # 财→官, 食伤→财, 官杀→印 (传递, C级)
    'COMBINATION',         # 合冲刑害破
)

# ---- Node Types ----
NODE_TYPES = (
    'DAYMASTER',
    'ROOT_BRANCH',
    'SUPPORT_GROUP',
    'DRAIN_GROUP',
    'CONTROL_GROUP',
    'SEASON',
)

# ---- Authorization 级别 ----
# A = 可独立结构 Fact
# C = 五行生克可查, 但"有效力量传递"未授权, 不参与任何强弱判断
AUTH = {
    'DIRECT_STRUCTURE': 'A',   # 直接日主关系
    'TRANSFER': 'C',           # 传递链（食伤→财→官→印）
}


def _node(node_type: str, label: str, attrs: Dict[str, Any]) -> Dict[str, Any]:
    return {'node_type': node_type, 'label': label, 'attrs': attrs}


def _edge(src: str, dst: str, edge_type: str, auth: str, note: str = '') -> Dict[str, Any]:
    return {'source': src, 'target': dst, 'edge_type': edge_type,
            'authorization': auth, 'note': note}


def build_power_network(a: Dict[str, Any], root_classes: Dict[str, Any] = None,
                        tou_cang: Dict[str, Any] = None,
                        wang_xiang: Dict[str, Any] = None,
                        root_relations: Dict[str, Any] = None,
                        two_side: Dict[str, Any] = None,
                        branch_tier: Dict[str, Any] = None) -> Dict[str, Any]:
    """输入 = 160-A build_power_structure 输出;
    可选 root_classes = daymaster_root_class.build_root_classes 输出(D2 细分);
    可选 tou_cang = daymaster_tou_cang.build_tou_cang 输出(D13 透藏四态);
    可选 wang_xiang = daymaster_wang_xiang.build_wang_xiang 输出(D11 旺相休囚死);
    可选 root_relations = daymaster_root_relations.build_root_relations 输出(D8 根支关系);
    可选 two_side = daymaster_two_side.build_two_side 输出(D6 两端构成投影).
    输出 = 多维网络 (nodes + edges + dimensions + queries 占位).
    不计算总分, 不输出 STRONG/WEAK."""
    dm = a['daymaster']
    dm_label = f"日主({dm['stem']}/{dm['wuxing']})"

    nodes: List[Dict] = []
    edges: List[Dict] = []

    # --- Node: DAYMASTER ---
    nodes.append(_node('DAYMASTER', dm_label, {'stem': dm['stem'], 'wuxing': dm['wuxing']}))

    # --- seasonal dimension ---
    sa = a['seasonal_axis']
    nodes.append(_node('SEASON', '月令', {'in_season': sa['in_season'], 'month_supports': sa['month_supports']}))
    edges.append(_edge('SEASON', dm_label, 'SEASONAL_RELATION', 'A',
                        '得令/失令轴, 不并入总分'))

    # --- root dimension ---
    ra = a['root_axis']
    root_node_attrs = {
        'root_weight_class': ra['root_weight_class'],
        'per_pillar': ra['per_pillar'],
    }
    if root_classes is not None:
        # D2 细分: 离散原典 root_class(长生/禄/旺刃/墓库/余气/阴长生), 无数值
        root_node_attrs['root_class_detail'] = {
            k: v['root_class'] for k, v in root_classes['per_pillar'].items()
        }
        root_node_attrs['root_class_basis'] = {
            k: v['basis'] for k, v in root_classes['per_pillar'].items()
        }
    nodes.append(_node('ROOT_BRANCH', '根气', root_node_attrs))
    edges.append(_node_edge(edges, dm_label, 'ROOT_RELATION', ra))

    # --- support dimension ---
    sg = a['support_group']
    for grp_name, grp in sg.items():
        nodes.append(_node('SUPPORT_GROUP', grp_name, grp))
        edges.append(_edge(grp_name, dm_label, 'SUPPORT_RELATION', 'A',
                           '印/比劫扶身, 党众/助寡轴'))

    # --- drain dimension ---
    dg = a['drain_group']
    for grp_name, grp in dg.items():
        nodes.append(_node('DRAIN_GROUP', grp_name, grp))
        edges.append(_edge(dm_label, grp_name, 'DRAIN_RELATION', 'A',
                           '日主泄耗, 不判断"太重"'))

    # --- control dimension ---
    cg = a['control_group']
    for grp_name, grp in cg.items():
        nodes.append(_node('CONTROL_GROUP', grp_name, grp))
        edges.append(_edge(grp_name, dm_label, 'CONTROL_RELATION', 'A',
                           '官杀克身, 不判断"有效制化"'))

    # --- transfer edges (C 级, 不参与强弱) ---
    for e in a.get('unauthorized_edges', []):
        edges.append(_edge(e['source'], e['target'], 'PRODUCE_RELATION', 'C', e.get('note', '')))

    # --- dimensions 总览（纯结构, 不汇总）---
    dimensions = {
        'SEASONAL': {
            'in_season': sa['in_season'],
            'month_supports': sa['month_supports'],
            'state': 'IN_SEASON' if sa['in_season'] else ('SUPPORTS' if sa['month_supports'] else 'OUT_OF_SEASON'),
        },
        'ROOT': {
            'root_weight_class': ra['root_weight_class'],
            'has_root': ra['root_weight_class'] in ('HEAVY', 'LIGHT'),
            **({
                'root_class_detail': {
                    k: v['root_class'] for k, v in root_classes['per_pillar'].items()
                },
                'root_pillars': root_classes['root_pillars'],
            } if root_classes is not None else {}),
        },
        **({
            'JUECHU': {
                'month_jue': a['juechu_axis']['month_jue'],
                'month_hidden_yin': a['juechu_axis']['month_hidden_yin'],
            },
        } if 'juechu_axis' in a else {}),
        'SUPPORT': {
            grp: {'stem_present': v['stem_present'], 'stem_count': v.get('stem_count', 0),
                  'root_present': v['root_present']}
            for grp, v in sg.items()
        },
        'DRAIN': {
            grp: {'stem_present': v['stem_present'], 'stem_count': v.get('stem_count', 0),
                  'root_present': v['root_present']}
            for grp, v in dg.items()
        },
        'CONTROL': {
            grp: {'stem_present': v['stem_present'], 'stem_count': v.get('stem_count', 0),
                  'root_present': v['root_present']}
            for grp, v in cg.items()
        },
        **({
            'TOU_CANG': {
                grp: {'state': v['state'], 'tou': v['tou'], 'cang': v['cang']}
                for grp, v in tou_cang['groups'].items()
            },
        } if tou_cang is not None else {}),
        **({
            'WANG_XIANG': {
                'state': wang_xiang['state'],
                'state_cn': wang_xiang['state_cn'],
            },
        } if wang_xiang is not None else {}),
        **({
            'ROOT_RELATION': {
                'struck_root_pillars': root_relations['struck_root_pillars'],
                'combined_root_pillars': root_relations['combined_root_pillars'],
            },
        } if root_relations is not None else {}),
        **({
            'TWO_SIDE': {
                side: {
                    'members_present': {m['member']: m['present'] for m in block['members']},
                    **({'root_present': block['root']['present'],
                        'struck_root_pillars': block['root']['struck_root_pillars'],
                        'combined_root_pillars': block['root']['combined_root_pillars']}
                       if 'root' in block else {}),
                }
                for side, block in two_side['sides'].items()
            },
        } if two_side is not None else {}),
        **({
            'BRANCH_TIER': {
                'clash_results': branch_tier['clash_results'],
            },
        } if branch_tier is not None else {}),
    }

    return {
        'generator': 'DaymasterPowerMultiDimensionalNetwork',
        'patch': 'PATCH-160-B-V2',
        'nodes': nodes,
        'edges': edges,
        'dimensions': dimensions,
        'two_side_structure': {
            'note': '两端成势未授权, 保留节点不裁, 经典规则未来各自查询',
            'daymaster_side': f'{dm_label} + SUPPORT + ROOT',
            'opposing_side': 'DRAIN + CONTROL',
        },
        'classical_queries': [],  # 未来 Rule 查询接口, 当前为空
        'judgment_status': 'NETWORK_ONLY_NO_TOTALIZER',
        'boundary_note': (
            '多维网络, 不做总裁决器, 不输出 STRONG/WEAK; '
            '矛盾共存(得令+泄成势/失令+扶成势)不强行裁; '
            '传递链C级不参与; 经典规则未来各自查询网络'
        ),
    }


def _node_edge(edges, dst, edge_type, ra):
    return _edge('ROOT_BRANCH', dst, edge_type, 'A',
                 f"根气class={ra['root_weight_class']}")
