# -*- coding: utf-8 -*-
"""P0-4.5: Condition Graph 验证

目标：
- 验证 Condition Graph 能否忠实表达真实五经复杂条件
- 支持 PREREQUISITE/BLOCKING/ENHANCEMENT/ALTERNATIVE/PRIORITY
- 不进入 Composite Judgment
- 不扩大生产规则数量

Condition Graph 结构：
{
  nodes: [Condition],
  edges: [
    {from: C1, to: C2, type: "prerequisite"},
    {from: C1, to: C2, type: "blocking"},
    ...
  ]
}
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class EdgeType(Enum):
    """Condition 之间的关系类型"""
    PREREQUISITE = "prerequisite"  # C1 必须成立，C2 才有意义
    BLOCKING = "blocking"  # C1 成立时，C2 被阻断
    ENHANCEMENT = "enhancement"  # C1 成立时，C2 效果增强
    ALTERNATIVE = "alternative"  # C1 或 C2 成立均可
    PRIORITY = "priority"  # C1 优先级高于 C2


@dataclass
class Condition:
    """单个 Condition"""
    id: str
    text: str
    semantic_type: str  # FACT/NECESSARY/BLOCKING/PREFERENCE 等
    feature_ref: Optional[str] = None  # 对应的 Feature 引用
    evidence_ref: Optional[str] = None  # 对应的 Evidence 引用


@dataclass
class ConditionEdge:
    """Condition 之间的关系"""
    from_id: str
    to_id: str
    edge_type: EdgeType
    description: str  # 关系描述


@dataclass
class ConditionGraph:
    """Condition Graph"""
    id: str
    source_text: str
    classic: str
    conditions: List[Condition] = field(default_factory=list)
    edges: List[ConditionEdge] = field(default_factory=list)
    semantic_type: str = "COMPOUND"
    exec_state: str = "UNRESOLVED"
    exec_reason: str = ""


# 样本数据：需要多条件的真实五经原典
SAMPLES = [
    # ===== PREREQUISITE（必要条件链）=====
    {
        "id": "graph_001",
        "source_text": "生克制化，须制中有生，生中有制。太过者宜损之，不及者宜益之。",
        "classic": "滴天髓",
        "description": "制化必须同时存在，且根据旺衰调整",
        "conditions": [
            {"id": "c1", "text": "有生", "semantic_type": "NECESSARY", "feature_ref": "support_count"},
            {"id": "c2", "text": "有制", "semantic_type": "NECESSARY", "feature_ref": "drain_count"},
            {"id": "c3", "text": "太过", "semantic_type": "FACT", "feature_ref": "wang_score"},
            {"id": "c4", "text": "不及", "semantic_type": "FACT", "feature_ref": "shang_score"},
        ],
        "edges": [
            {"from": "c1", "to": "c2", "type": "PREREQUISITE", "desc": "生必须伴随制"},
            {"from": "c3", "to": "c1", "type": "BLOCKING", "desc": "太过时生被阻断"},
            {"from": "c4", "to": "c2", "type": "BLOCKING", "desc": "不及时节制被阻断"},
        ],
    },
    {
        "id": "graph_002",
        "source_text": "一行得二三人之气，则党众而专，须从其势。",
        "classic": "滴天髓",
        "description": "气势专旺时必须顺从",
        "conditions": [
            {"id": "c1", "text": "党众", "semantic_type": "FACT", "feature_ref": "support_count > 2"},
            {"id": "c2", "text": "气专", "semantic_type": "FACT", "feature_ref": "dominant_element"},
            {"id": "c3", "text": "从势", "semantic_type": "NECESSARY", "feature_ref": "follow_qi_shi"},
        ],
        "edges": [
            {"from": "c1", "to": "c2", "type": "PREREQUISITE", "desc": "党众是气专的前提"},
            {"from": "c2", "to": "c3", "type": "PREREQUISITE", "desc": "气专是从势的前提"},
        ],
    },
    {
        "id": "graph_003",
        "source_text": "大凡旺之极者，宜泄而不宜克，宜顺其气势，弗悖其性也。",
        "classic": "滴天髓",
        "description": "旺极时必须顺其势，不能克",
        "conditions": [
            {"id": "c1", "text": "旺极", "semantic_type": "FACT", "feature_ref": "wang_score > threshold"},
            {"id": "c2", "text": "宜泄", "semantic_type": "PREFERENCE", "feature_ref": "use_xie"},
            {"id": "c3", "text": "不宜克", "semantic_type": "BLOCKING", "feature_ref": "block_ke"},
            {"id": "c4", "text": "顺势", "semantic_type": "NECESSARY", "feature_ref": "follow_qi_shi"},
        ],
        "edges": [
            {"from": "c1", "to": "c2", "type": "PRIORITY", "desc": "旺极时泄优先于克"},
            {"from": "c1", "to": "c3", "type": "BLOCKING", "desc": "旺极时克被阻断"},
            {"from": "c1", "to": "c4", "type": "PREREQUISITE", "desc": "旺极时必须顺其势"},
        ],
    },

    # ===== BLOCKING + ENHANCEMENT（阻断+增强）=====
    {
        "id": "graph_004",
        "source_text": "辛金软弱，温润而清，畏土之埋，乐水之盈。",
        "classic": "滴天髓",
        "description": "辛金畏惧土埋，喜欢水旺",
        "conditions": [
            {"id": "c1", "text": "辛金日主", "semantic_type": "FACT", "feature_ref": "day_master == XIN"},
            {"id": "c2", "text": "土旺", "semantic_type": "FACT", "feature_ref": "wu_element_wang"},
            {"id": "c3", "text": "水旺", "semantic_type": "FACT", "feature_ref": "shui_element_wang"},
            {"id": "c4", "text": "畏土埋", "semantic_type": "BLOCKING", "feature_ref": "block_when_wu_wang"},
            {"id": "c5", "text": "乐水盈", "semantic_type": "ENHANCEMENT", "feature_ref": "enhance_when_shui_wang"},
        ],
        "edges": [
            {"from": "c1", "to": "c4", "type": "BLOCKING", "desc": "辛金日主时土埋被阻断"},
            {"from": "c1", "to": "c5", "type": "ENHANCEMENT", "desc": "辛金日主时水盈效果增强"},
            {"from": "c2", "to": "c4", "type": "PREREQUISITE", "desc": "土旺是土埋的前提"},
            {"from": "c3", "to": "c5", "type": "PREREQUISITE", "desc": "水旺是水盈的前提"},
        ],
    },
    {
        "id": "graph_005",
        "source_text": "戊己愁逢甲乙，干头须要庚辛。",
        "classic": "渊海子平",
        "description": "戊己土遇甲乙木时需要庚辛解救",
        "conditions": [
            {"id": "c1", "text": "戊己土旺", "semantic_type": "FACT", "feature_ref": "wu_wuji_wang"},
            {"id": "c2", "text": "甲乙木透", "semantic_type": "FACT", "feature_ref": "jia_yi_transparent"},
            {"id": "c3", "text": "庚辛透干", "semantic_type": "NECESSARY", "feature_ref": "geng_xin_transparent"},
            {"id": "c4", "text": "解救", "semantic_type": "ENHANCEMENT", "feature_ref": "rescue_effect"},
        ],
        "edges": [
            {"from": "c1", "to": "c2", "type": "BLOCKING", "desc": "戊己土旺时甲乙木透被阻断"},
            {"from": "c2", "to": "c3", "type": "PREREQUISITE", "desc": "甲乙木透时庚辛透是前提"},
            {"from": "c3", "to": "c4", "type": "ENHANCEMENT", "desc": "庚辛透时解救效果增强"},
        ],
    },

    # ===== ALTERNATIVE（替代关系）=====
    {
        "id": "graph_006",
        "source_text": "正月甲木，初春尚有余寒，得丙癸透，富贵双全。",
        "classic": "穷通宝鉴",
        "description": "正月甲木需要丙癸配合，但优先级不同",
        "conditions": [
            {"id": "c1", "text": "甲木日主", "semantic_type": "FACT", "feature_ref": "day_master == JIA"},
            {"id": "c2", "text": "寅月", "semantic_type": "FACT", "feature_ref": "month == YIN"},
            {"id": "c3", "text": "丙透", "semantic_type": "NECESSARY", "feature_ref": "bing_transparent"},
            {"id": "c4", "text": "癸透", "semantic_type": "NECESSARY", "feature_ref": "gui_transparent"},
            {"id": "c5", "text": "富贵", "semantic_type": "INFERENCE", "feature_ref": "fugui_judgment"},
        ],
        "edges": [
            {"from": "c1", "to": "c3", "type": "PRIORITY", "desc": "甲木日主时丙透优先级高"},
            {"from": "c2", "to": "c3", "type": "PREREQUISITE", "desc": "寅月时丙透是前提"},
            {"from": "c2", "to": "c4", "type": "ALTERNATIVE", "desc": "寅月时癸透可与丙透替代"},
            {"from": "c3", "to": "c5", "type": "ENHANCEMENT", "desc": "丙透时富贵效果增强"},
            {"from": "c4", "to": "c5", "type": "ENHANCEMENT", "desc": "癸透时富贵效果增强"},
        ],
    },
    {
        "id": "graph_007",
        "source_text": "五月甲木，木性虚焦。五月先癸后丁，庚金次之。",
        "classic": "穷通宝鉴",
        "description": "五月甲木用神优先级：癸 > 丁 > 庚",
        "conditions": [
            {"id": "c1", "text": "甲木日主", "semantic_type": "FACT", "feature_ref": "day_master == JIA"},
            {"id": "c2", "text": "午月", "semantic_type": "FACT", "feature_ref": "month == WU"},
            {"id": "c3", "text": "癸透", "semantic_type": "NECESSARY", "feature_ref": "gui_transparent"},
            {"id": "c4", "text": "丁透", "semantic_type": "NECESSARY", "feature_ref": "ding_transparent"},
            {"id": "c5", "text": "庚透", "semantic_type": "NECESSARY", "feature_ref": "geng_transparent"},
        ],
        "edges": [
            {"from": "c1", "to": "c3", "type": "PRIORITY", "desc": "甲木日主时癸优先"},
            {"from": "c2", "to": "c3", "type": "PREREQUISITE", "desc": "午月时癸透是前提"},
            {"from": "c2", "to": "c4", "type": "ALTERNATIVE", "desc": "午月时丁透可与癸透替代"},
            {"from": "c4", "to": "c5", "type": "PRIORITY", "desc": "丁透时庚透优先级低"},
        ],
    },

    # ===== PRIORITY（优先级）=====
    {
        "id": "graph_008",
        "source_text": "火炽乘龙，水荡骑虎。",
        "classic": "滴天髓",
        "description": "火旺需辰（龙）调候，水旺需寅（虎）疏导",
        "conditions": [
            {"id": "c1", "text": "火旺", "semantic_type": "FACT", "feature_ref": "huo_element_wang"},
            {"id": "c2", "text": "水旺", "semantic_type": "FACT", "feature_ref": "shui_element_wang"},
            {"id": "c3", "text": "辰土", "semantic_type": "NECESSARY", "feature_ref": "chen_earth_present"},
            {"id": "c4", "text": "寅木", "semantic_type": "NECESSARY", "feature_ref": "yin_wood_present"},
            {"id": "c5", "text": "调候", "semantic_type": "ENHANCEMENT", "feature_ref": "tiao_hou_effect"},
        ],
        "edges": [
            {"from": "c1", "to": "c3", "type": "PREREQUISITE", "desc": "火旺时辰土是前提"},
            {"from": "c2", "to": "c4", "type": "PREREQUISITE", "desc": "水旺时寅木是前提"},
            {"from": "c3", "to": "c5", "type": "ENHANCEMENT", "desc": "辰土时调候效果增强"},
            {"from": "c1", "to": "c4", "type": "BLOCKING", "desc": "火旺时寅木被阻断"},
            {"from": "c2", "to": "c3", "type": "BLOCKING", "desc": "水旺时辰土被阻断"},
        ],
    },
    {
        "id": "graph_009",
        "source_text": "戊土固重，既中且正。静翕动辟，万物司命。水润物生，火燥物病。",
        "classic": "滴天髓",
        "description": "戊土的特性及水的调节作用",
        "conditions": [
            {"id": "c1", "text": "戊土日主", "semantic_type": "FACT", "feature_ref": "day_master == WU"},
            {"id": "c2", "text": "土重", "semantic_type": "FACT", "feature_ref": "wu_element_heavy"},
            {"id": "c3", "text": "水润", "semantic_type": "NECESSARY", "feature_ref": "shui_moistening"},
            {"id": "c4", "text": "火燥", "semantic_type": "BLOCKING", "feature_ref": "huo_drying"},
            {"id": "c5", "text": "生", "semantic_type": "ENHANCEMENT", "feature_ref": "sheng_effect"},
            {"id": "c6", "text": "病", "semantic_type": "BLOCKING", "feature_ref": "bing_effect"},
        ],
        "edges": [
            {"from": "c1", "to": "c2", "type": "PREREQUISITE", "desc": "戊土日主时土重是前提"},
            {"from": "c2", "to": "c3", "type": "PREREQUISITE", "desc": "土重时水润是前提"},
            {"from": "c2", "to": "c4", "type": "BLOCKING", "desc": "土重时火燥被阻断"},
            {"from": "c3", "to": "c5", "type": "ENHANCEMENT", "desc": "水润时生机增强"},
            {"from": "c4", "to": "c6", "type": "ENHANCEMENT", "desc": "火燥时病害增强"},
        ],
    },

    # ===== 复杂混合 =====
    {
        "id": "graph_010",
        "source_text": "丁火柔中，内性昭融，抱乙而孝，合壬而忠。旺而不烈，衰而不穷，如有嫡母，可秋可冬。",
        "classic": "滴天髓",
        "description": "丁火的多重特性和条件组合",
        "conditions": [
            {"id": "c1", "text": "丁火日主", "semantic_type": "FACT", "feature_ref": "day_master == DING"},
            {"id": "c2", "text": "乙木透", "semantic_type": "NECESSARY", "feature_ref": "yi_transparent"},
            {"id": "c3", "text": "壬水透", "semantic_type": "NECESSARY", "feature_ref": "ren_transparent"},
            {"id": "c4", "text": "旺", "semantic_type": "FACT", "feature_ref": "wang_state"},
            {"id": "c5", "text": "衰", "semantic_type": "FACT", "feature_ref": "shuai_state"},
            {"id": "c6", "text": "嫡母（木）", "semantic_type": "NECESSARY", "feature_ref": "wood_support"},
            {"id": "c7", "text": "秋", "semantic_type": "FACT", "feature_ref": "month == YOU"},
            {"id": "c8", "text": "冬", "semantic_type": "FACT", "feature_ref": "month == ZI"},
        ],
        "edges": [
            {"from": "c1", "to": "c2", "type": "ALTERNATIVE", "desc": "丁火日主时乙透或壬透"},
            {"from": "c1", "to": "c3", "type": "ALTERNATIVE", "desc": "丁火日主时壬透或乙透"},
            {"from": "c4", "to": "c5", "type": "BLOCKING", "desc": "旺时不衰"},
            {"from": "c6", "to": "c7", "type": "PREREQUISITE", "desc": "有嫡母时秋可成立"},
            {"from": "c6", "to": "c8", "type": "PREREQUISITE", "desc": "有嫡母时冬可成立"},
        ],
    },
    {
        "id": "graph_011",
        "source_text": "庚金带杀，刚健为最，得水而清，得火而锐。土润则生，土干则脆。",
        "classic": "滴天髓",
        "description": "庚金的特性和土的影响",
        "conditions": [
            {"id": "c1", "text": "庚金日主", "semantic_type": "FACT", "feature_ref": "day_master == GENG"},
            {"id": "c2", "text": "带杀", "semantic_type": "FACT", "feature_ref": "seven_kong_present"},
            {"id": "c3", "text": "得水", "semantic_type": "NECESSARY", "feature_ref": "water_present"},
            {"id": "c4", "text": "得火", "semantic_type": "NECESSARY", "feature_ref": "fire_present"},
            {"id": "c5", "text": "土润", "semantic_type": "FACT", "feature_ref": "wu_moist"},
            {"id": "c6", "text": "土干", "semantic_type": "FACT", "feature_ref": "wu_dry"},
        ],
        "edges": [
            {"from": "c1", "to": "c2", "type": "PREREQUISITE", "desc": "庚金日主时带杀是前提"},
            {"from": "c2", "to": "c3", "type": "ALTERNATIVE", "desc": "带杀时得水或得火"},
            {"from": "c2", "to": "c4", "type": "ALTERNATIVE", "desc": "带杀时得火或得水"},
            {"from": "c5", "to": "c3", "type": "ENHANCEMENT", "desc": "土润时水效果增强"},
            {"from": "c6", "to": "c4", "type": "BLOCKING", "desc": "土干时火被阻断"},
        ],
    },
]


def build_condition_graph(sample: dict) -> ConditionGraph:
    """根据样本构建 Condition Graph"""
    # 构建 Condition 节点
    conditions = []
    for c in sample["conditions"]:
        conditions.append(Condition(
            id=c["id"],
            text=c["text"],
            semantic_type=c["semantic_type"],
            feature_ref=c.get("feature_ref"),
        ))

    # 构建 Edge
    edges = []
    for e in sample["edges"]:
        edges.append(ConditionEdge(
            from_id=e["from"],
            to_id=e["to"],
            edge_type=EdgeType(e["type"]),
            description=e["desc"],
        ))

    # 判断可执行性
    exec_state, exec_reason = evaluate_executability(conditions, edges)

    return ConditionGraph(
        id=sample["id"],
        source_text=sample["source_text"],
        classic=sample["classic"],
        conditions=conditions,
        edges=edges,
        semantic_type="COMPOUND",
        exec_state=exec_state,
        exec_reason=exec_reason,
    )


def evaluate_executability(conditions: List[Condition], edges: List[ConditionEdge]) -> tuple:
    """评估 Condition Graph 的可执行性"""
    # 规则：
    # 1. 如果所有节点都是 FACT 或 BLOCKING，且没有复杂的依赖关系 → EXECUTABLE
    # 2. 如果有 PREREQUISITE 链且都明确 → SEMANTIC_ONLY
    # 3. 如果有 PRIORITY 或 ALTERNATIVE → UNRESOLVED（需要更多原典验证）

    has_priority = any(e.edge_type == EdgeType.PRIORITY for e in edges)
    has_alternative = any(e.edge_type == EdgeType.ALTERNATIVE for e in edges)
    has_prerequisite_chain = any(e.edge_type == EdgeType.PREREQUISITE for e in edges)

    # 检查是否有不明确的条件
    unclear_conditions = [c for c in conditions if c.semantic_type in ["PREFERENCE", "INFERENCE"]]

    if has_priority or has_alternative:
        return "UNRESOLVED", "包含优先级或替代关系，需要更多原典验证"

    if unclear_conditions:
        return "SEMANTIC_ONLY", "包含倾向/宜忌或推论，不能直接执行"

    if has_prerequisite_chain:
        return "SEMANTIC_ONLY", "包含必要条件链，需要原典审核"

    # 只有 FACT 和 BLOCKING → EXECUTABLE
    all_fact_blocking = all(c.semantic_type in ["FACT", "BLOCKING"] for c in conditions)
    if all_fact_blocking:
        return "EXECUTABLE", "条件明确，可直接映射"

    return "UNRESOLVED", "语义类型不明确，保持保守"


def main():
    print("=== P0-4.5: Condition Graph 验证 ===\n")

    results = []
    state_counts = {"EXECUTABLE": 0, "SEMANTIC_ONLY": 0, "UNRESOLVED": 0}

    for sample in SAMPLES:
        graph = build_condition_graph(sample)
        results.append({
            "id": graph.id,
            "source_text": graph.source_text[:80],
            "classic": graph.classic,
            "condition_count": len(graph.conditions),
            "edge_count": len(graph.edges),
            "exec_state": graph.exec_state,
            "exec_reason": graph.exec_reason,
            "conditions": [{"id": c.id, "text": c.text, "type": c.semantic_type} for c in graph.conditions],
            "edges": [{"from": e.from_id, "to": e.to_id, "type": e.edge_type.value, "desc": e.description} for e in graph.edges],
        })
        state_counts[graph.exec_state] += 1

    # 输出统计
    print("=== 可执行性分布 ===")
    for s, count in sorted(state_counts.items(), key=lambda x: -x[1]):
        print(f"  {s}: {count}")

    # 输出详细结果
    print("\n=== 详细验证 ===")
    for r in results:
        print(f"\n[{r['id']}] {r['classic']}")
        print(f"  原文: {r['source_text']}...")
        print(f"  条件数: {r['condition_count']}, 边数: {r['edge_count']}")
        print(f"  可执行性: {r['exec_state']}")
        print(f"  原因: {r['exec_reason']}")

    # 输出报告
    report = {
        "generated": __import__('datetime').datetime.now().isoformat(),
        "summary": {
            "total_samples": len(results),
            "state_distribution": state_counts,
        },
        "results": results,
    }

    with open('data/p0_4_5_condition_graph_result.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 data/p0_4_5_condition_graph_result.json")


if __name__ == '__main__':
    main()
