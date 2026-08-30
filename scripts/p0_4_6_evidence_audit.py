# -*- coding: utf-8 -*-
"""P0-4.6: SEMANTIC_ONLY 逐条证据审计

目标：
- 对 6 条 SEMANTIC_ONLY 做逐条原典上下文审计
- 检查 Feature 映射是否准确
- 检查关系类型是否原典明确表达
- 判断是否可以授权为 EXECUTABLE

审计框架：
1. 原典完整上下文
2. Feature 映射依据
3. 关系类型是否明确
4. 最终授权判断
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple


# 6 条待审计的 SEMANTIC_ONLY 样本
TARGET_SAMPLES = [
    {
        "id": "graph_001",
        "source_text": "生克制化，须制中有生，生中有制。太过者宜损之，不及者宜益之。",
        "classic": "滴天髓",
        "current_state": "SEMANTIC_ONLY",
        "current_reason": "包含必要条件链，需要原典审核",
        "questions": [
            "Feature映射是否正确？",
            "生克制化是否明确表达了prerequisite关系？",
            "原典是否有明确授权？",
        ],
    },
    {
        "id": "graph_002",
        "source_text": "一行得二三人之气，则党众而专，须从其势。",
        "classic": "滴天髓",
        "current_state": "SEMANTIC_ONLY",
        "current_reason": "包含必要条件链，需要原典审核",
        "questions": [
            "Feature映射是否正确？",
            "党众→气专→从势是否是明确的条件链？",
            "原典是否有明确授权？",
        ],
    },
    {
        "id": "graph_004",
        "source_text": "辛金软弱，温润而清，畏土之埋，乐水之盈。",
        "classic": "滴天髓",
        "current_state": "SEMANTIC_ONLY",
        "current_reason": "包含必要条件链，需要原典审核",
        "questions": [
            "Feature映射是否正确？",
            "畏土之埋是否明确表达blocking关系？",
            "原典是否有明确授权？",
        ],
    },
    {
        "id": "graph_005",
        "source_text": "戊己愁逢甲乙，干头须要庚辛。",
        "classic": "渊海子平",
        "current_state": "SEMANTIC_ONLY",
        "current_reason": "包含必要条件链，需要原典审核",
        "questions": [
            "Feature映射是否正确？",
            "愁逢甲乙是否明确表达blocking关系？",
            "原典是否有明确授权？",
        ],
    },
    {
        "id": "graph_008",
        "source_text": "火炽乘龙，水荡骑虎。",
        "classic": "滴天髓",
        "current_state": "SEMANTIC_ONLY",
        "current_reason": "包含必要条件链，需要原典审核",
        "questions": [
            "Feature映射是否正确？",
            "乘龙骑虎是否明确表达prerequisite关系？",
            "原典是否有明确授权？",
        ],
    },
    {
        "id": "graph_009",
        "source_text": "戊土固重，既中且正。静翕动辟，万物司命。水润物生，火燥物病。",
        "classic": "滴天髓",
        "current_state": "SEMANTIC_ONLY",
        "current_reason": "包含必要条件链，需要原典审核",
        "questions": [
            "Feature映射是否正确？",
            "水润/火燥是否明确表达enhancement/blocking关系？",
            "原典是否有明确授权？",
        ],
    },
]


def load_classic_context(classic_name: str, keyword: str, context_size: int = 500) -> Optional[str]:
    """加载经典原文并查找上下文"""
    corpus_path = Path("D:/today/Canonical-Mining/五部经典完整数据")

    file_map = {
        "滴天髓": "DTS_滴天髓_完整全文.md",
        "渊海子平": "YHZP_渊海子平_完整全文.md",
        "三命通会": "SMTH_三命通会_完整全文.md",
        "穷通宝鉴": "QTBJ_穷通宝鉴_完整全文.md",
        "子平真诠": "PZZQ_子平真诠_完整全文.md",
    }

    if classic_name not in file_map:
        return None

    file_path = corpus_path / file_map[classic_name]
    if not file_path.exists():
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 查找关键词
    if keyword not in text:
        return None

    idx = text.find(keyword)
    start = max(0, idx - context_size)
    end = min(len(text), idx + len(keyword) + context_size)

    return text[start:end]


def audit_sample(sample: dict) -> dict:
    """审计单条样本"""
    result = {
        "id": sample["id"],
        "source_text": sample["source_text"],
        "classic": sample["classic"],
        "context_found": False,
        "full_context": "",
        "feature_mapping_audit": {},
        "relation_type_audit": {},
        "authorization_decision": "",
        "authorization_reason": "",
        "final_state": sample["current_state"],
        "questions_answered": [],
    }

    # Phase 1: 原典上下文审计
    context = load_classic_context(sample["classic"], sample["source_text"][:20], context_size=800)
    if context:
        result["context_found"] = True
        result["full_context"] = context

    # Phase 2: Feature 映射审计
    feature_audit = analyze_feature_mapping(sample)
    result["feature_mapping_audit"] = feature_audit

    # Phase 3: 关系类型审计
    relation_audit = analyze_relation_types(sample)
    result["relation_type_audit"] = relation_audit

    # Phase 4: 授权判断
    decision, reason = make_authorization_decision(result)
    result["authorization_decision"] = decision
    result["authorization_reason"] = reason

    return result


def analyze_feature_mapping(sample: dict) -> dict:
    """分析 Feature 映射"""
    audit = {
        "questions": sample.get("questions", []),
        "answers": [],
        "issues": [],
    }

    # 根据原典特征判断
    source = sample["source_text"]

    if "生克制化" in source:
        audit["answers"].append("Feature映射：支持/抑制计数可能不准确")
        audit["issues"].append("原典未明确指定 Feature 来源")

    elif "一行得二三人" in source:
        audit["answers"].append("Feature映射：support_count > drain_count 可能不准确")
        audit["issues"].append("原典未明确'二三人'的数量阈值")

    elif "畏土之埋" in source:
        audit["answers"].append("Feature映射：wu_element_wang 可能不准确")
        audit["issues"].append("原典未明确'埋'的程度标准")

    elif "愁逢甲乙" in source:
        audit["answers"].append("Feature映射：jia_yi_transparent 可能不准确")
        audit["issues"].append("原典未明确'愁逢'的具体条件")

    elif "火炽乘龙" in source:
        audit["answers"].append("Feature映射：chen_earth_present 可能不准确")
        audit["issues"].append("原典未明确'乘龙'的条件")

    elif "水润物生" in source:
        audit["answers"].append("Feature映射：shui_moistening 可能不准确")
        audit["issues"].append("原典未明确'润'的程度标准")

    audit["questions_answered"] = len(audit["answers"])

    return audit


def analyze_relation_types(sample: dict) -> dict:
    """分析关系类型"""
    audit = {
        "explicit_relations": [],
        "inferred_relations": [],
        "issues": [],
    }

    source = sample["source_text"]

    if "须" in source:
        audit["explicit_relations"].append("prerequisite（须...）")

    if "不可" in source or "畏" in source or "愁" in source:
        audit["explicit_relations"].append("blocking（不可.../畏...）")

    if "得" in source and "则" in source:
        audit["explicit_relations"].append("enhancement（得...则...）")

    if "或" in source:
        audit["explicit_relations"].append("alternative（或...）")

    if "先" in source or "后" in source or "优先" in source:
        audit["explicit_relations"].append("priority（先...后...）")

    # 检查推断的关系
    if "太岁" in source and "犯" in source:
        audit["inferred_relations"].append("blocking（推论）")

    if "党众" in source and "从势" in source:
        audit["inferred_relations"].append("prerequisite（推论）")

    audit["issues"] = [
        "部分关系可能是工程师推断而非原典明确表达"
    ]

    return audit


def make_authorization_decision(audit_result: dict) -> Tuple[str, str]:
    """做出授权判断"""
    # 规则：
    # 1. 如果所有关系都是原典明确表达（explicit_relations）→ EXECUTABLE
    # 2. 如果有任何推断关系 → SEMANTIC_ONLY
    # 3. 如果 Feature 映射不明确 → SEMANTIC_ONLY

    explicit_count = len(audit_result["relation_type_audit"]["explicit_relations"])
    inferred_count = len(audit_result["relation_type_audit"]["inferred_relations"])
    feature_issues = len(audit_result["feature_mapping_audit"]["issues"])

    if inferred_count > 0:
        return "SEMANTIC_ONLY", "包含推断关系，不得自动授权"

    if feature_issues > 0:
        return "SEMANTIC_ONLY", "Feature映射不明确，需要原典审核"

    if explicit_count > 0:
        return "EXECUTABLE", "原典明确授权所有关系"

    return "UNRESOLVED", "无法确定关系类型"


def main():
    print("=== P0-4.6: SEMANTIC_ONLY 逐条证据审计 ===\n")

    results = []
    state_counts = {"EXECUTABLE": 0, "SEMANTIC_ONLY": 0, "UNRESOLVED": 0}

    for sample in TARGET_SAMPLES:
        print(f"审计: {sample['id']} - {sample['classic']}")
        print(f"  原文: {sample['source_text'][:60]}...")

        result = audit_sample(sample)
        results.append(result)
        state_counts[result["final_state"]] += 1

        print(f"  上下文: {'找到' if result['context_found'] else '未找到'}")
        print(f"  授权判断: {result['authorization_decision']}")
        print(f"  原因: {result['authorization_reason']}")
        print()

    # 输出统计
    print("=== 审计结果汇总 ===")
    for s, count in sorted(state_counts.items(), key=lambda x: -x[1]):
        print(f"  {s}: {count}")

    # 输出详细报告
    print("\n=== 详细报告 ===")
    for r in results:
        print(f"\n[{r['id']}] {r['classic']}")
        print(f"  原文: {r['source_text'][:80]}...")
        print(f"  授权判断: {r['authorization_decision']}")
        print(f"  原因: {r['authorization_reason']}")
        if r['relation_type_audit']['explicit_relations']:
            print(f"  明确关系: {', '.join(r['relation_type_audit']['explicit_relations'])}")
        if r['relation_type_audit']['inferred_relations']:
            print(f"  推断关系: {', '.join(r['relation_type_audit']['inferred_relations'])}")

    # 保存结果
    report = {
        "generated": __import__('datetime').datetime.now().isoformat(),
        "summary": {
            "total_samples": len(results),
            "state_distribution": state_counts,
        },
        "results": results,
    }

    with open('data/p0_4_6_audit_result.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 data/p0_4_6_audit_result.json")


if __name__ == '__main__':
    main()
