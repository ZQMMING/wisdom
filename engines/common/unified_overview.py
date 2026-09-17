# -*- coding: utf-8 -*-
"""P160 只读联合全景视图 · 第三刀（把已建孤岛并列罗列, 不裁不评分不接生产）

一个命盘进来, 把下列已封板孤岛按依赖串起来并列输出:
  L0 facts
   ├─ 160-A 日主力量五轴结构
   ├─ D2/D13/D11/D8/D6 纯结构派生
   ├─ 160-B 多维力量网络
   ├─ ACTIVITY 发动层
   ├─ PZZQ 格神视图 (PZZQ.use_god)
   └─ QTBJ 调候候选 (QTBJ.climate_use)

铁律:
  - 各 namespace 并列罗列, 互不裁决; 禁止跨域综合出 STRONG/WEAK/总用神/喜忌/吉凶;
  - 不新增任何评分/权重/阈值/比较器;
  - 不接 production_entry; 只读消费已封板模块, 不改它们;
  - changsheng_direction 的 WEAK 是 176 授权十二长生方向标签, 非身弱 Judgment, 豁免。
"""
from typing import Any, Dict
from engines.common.l0_fact_builder import build
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_power_network import build_power_network
from engines.common.daymaster_activity import build_activity_layer
from engines.common.yongshen_geju import build_yongshen_geju
from engines.common.qtbj_climate_candidates import build_climate_candidates


def build_unified_overview(pillars: Dict[str, list]) -> Dict[str, Any]:
    """只读串联已封板孤岛, 并列输出。不做任何跨域裁决。"""
    facts = build(pillars)

    # 160-A 五轴结构
    power_a = build_power_structure(pillars)
    # hidden_stems_table: {地支: [藏干]}
    hst = {pillars[k][1]: facts['hidden_stems'][k] for k in ('year', 'month', 'day', 'hour')}
    rc = build_root_classes(pillars, hst)            # D2 根层级
    tc = build_tou_cang(facts)                        # D13 透藏
    wx = build_wang_xiang(facts, facts['day_stem'])  # D11 旺相休囚
    rr = build_root_relations(rc, facts['combination_facts'])  # D8 根支关系
    ts = build_two_side(rc, tc, rr)                   # D6 两端投影
    network = build_power_network(power_a, rc, tc, wx, rr, ts)  # 160-B 网络
    activity = build_activity_layer(tc, rr, facts)              # ACTIVITY 发动
    geshen = build_yongshen_geju(facts)               # PZZQ 格神
    climate = build_climate_candidates(facts)         # QTBJ 调候

    return {
        'module': 'ZIPING_UNIFIED_OVERVIEW',
        'patch': 'P160-UNIFIED-3',
        'panxi': {
            'day_stem': facts['day_stem'],
            'daymaster_element': facts.get('daymaster_element'),
            'month_branch': facts['month_branch'],
        },
        # 各 namespace 并列罗列, 互不裁决
        'daymaster_power_network': network,
        'activity_layer': activity,
        'pzzq_geshen': geshen,
        'qtbj_climate': climate,
        # 隔离声明: 各域独立, 不跨域综合
        'namespace_isolation': {
            'PZZQ.use_god': '格局用神候选, 不裁决身强弱/喜忌',
            'QTBJ.climate_use': '调候干候选+次序, 不裁决格局/吉凶',
            'daymaster_network': '多维结构网络, 无总分器',
            'activity_layer': '发动前提候选, 无成败/有用无用',
        },
        'judgment_status': 'PARALLEL_VIEW_NO_TOTALIZER',
        'boundary_note': (
            '只读并列罗列已封板孤岛; 各 namespace 互不裁决, 不跨域综合; '
            '无 STRONG/WEAK 总裁决, 无总用神, 无全局喜忌, 无吉凶; '
            'changsheng_direction 的 WEAK 为 176 授权十二长生方向标签, 非身弱 Judgment; '
            '不接 production_entry; 不改任何已封板模块'
        ),
    }
