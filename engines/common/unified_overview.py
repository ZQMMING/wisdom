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
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology
from engines.common.daymaster_power_network import build_power_network
from engines.common.daymaster_activity import build_activity_layer
from engines.common.yongshen_geju import build_yongshen_geju
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.qtbj_climate_presence import build_climate_presence
from engines.common.xiang_shen_candidates import build_xiang_shen_candidates
from engines.common.daymaster_power_queries import run_queries
from engines.common.special_pattern import build_special_patterns
from engines.common.climate_structure import build_climate_structure


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
    bt = build_branch_tiers(pillars, facts)           # 地支层级
    th = build_tian_he(pillars, facts)                # 天干五合/三合三会化神
    network = build_power_network(power_a, rc, tc, wx, rr, ts,
                                  branch_tier=bt, tian_he=th, facts=facts)  # 160-B 网络
    # 日主旺衰七档结构谱(连续力量打底+原典结构非对称修正; 多维网络上的单端结构度量)
    wpo = build_wuxing_power(pillars, facts, th)
    spectrum = build_spectrum_topology(network, wpo)
    network.setdefault('dimensions', {})['SPECTRUM'] = spectrum
    activity = build_activity_layer(tc, rr, facts)              # ACTIVITY 发动
    geshen = build_yongshen_geju(facts)               # PZZQ 格神
    climate = build_climate_candidates(facts)         # QTBJ 调候
    climate_presence = build_climate_presence(facts)  # QTBJ 调候干盘中位置投影
    xiang = build_xiang_shen_candidates(facts)        # PZZQ 相神角色
    queries = run_queries(network)                    # 160-C 原典命题结构查询
    climate_struct = build_climate_structure(pillars, facts, th)  # 寒暖燥湿客观结构
    special = build_special_patterns(pillars, facts, wpo, th, climate_struct)  # 特殊格局结构定性标签

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
        'daymaster_spectrum': spectrum,
        'activity_layer': activity,
        'pzzq_geshen': geshen,
        'pzzq_xiangshen': xiang,
        'qtbj_climate': climate,
        'qtbj_climate_presence': climate_presence,
        'daymaster_queries': queries,
        'special_pattern': special,
        'climate_structure': climate_struct,
        # 隔离声明: 各域独立, 不跨域综合
        'namespace_isolation': {
            'PZZQ.use_god': '格局用神候选, 不裁决身强弱/喜忌',
            'PZZQ.xiang_shen': '相神角色配对候选, 不判成相/破相/有情/成格',
            'QTBJ.climate_use': '调候干候选+次序, 不裁决格局/吉凶',
            'QTBJ.climate_presence': '调候干盘中位置(透干/藏支/全无), 不判调候得力/成败',
            'daymaster_network': '多维结构网络, 无总分器',
            'daymaster_spectrum': '日主单端七档旺衰结构谱(旺极/太旺/旺/中和/衰/太衰/衰极); 中和指日主单端无偏, 非全局五行流通之中和(全局中和属病药/流通层); 非STRONG/WEAK总裁决, 不出喜忌/用神/吉凶',
            'daymaster_queries': '原典命题各自结构查询, state恒UNKNOWN, 无STRONG/WEAK裁决',
            'special_pattern': '从格/专旺/日干化气/母灭结构定性标签(CONFIRMED/CANDIDATE), 只读七档与事实, 不改七档, 不判用神成败吉凶',
            'activity_layer': '发动前提候选, 无成败/有用无用',
            'climate.structure': '客观寒暖燥湿四性+虚湿/燥烈/金寒结构标签(离散枚举), 不判调候用神/身强弱/吉凶; 虚湿假从交special判CANDIDATE',
        },
        'judgment_status': 'PARALLEL_VIEW_NO_TOTALIZER',
        'boundary_note': (
            '只读并列罗列已封板孤岛; 各 namespace 互不裁决, 不跨域综合; '
            '无 STRONG/WEAK 总裁决, 无总用神, 无全局喜忌, 无吉凶; '
            'changsheng_direction 的 WEAK 为 176 授权十二长生方向标签, 非身弱 Judgment; '
            '不接 production_entry; 不改任何已封板模块'
        ),
    }
