# -*- coding: utf-8 -*-
"""P0-4.7: 五经 Semantic Feature Ontology 审计

目标：
- 建立"原典语言"与"工程 Feature"的语义桥梁
- 逐条分析 6 条 SEMANTIC_ONLY 的 Feature 映射
- 分类为 CANONICAL_FEATURE / DERIVABLE_FEATURE / SEMANTIC_ONLY

三种状态定义：
- CANONICAL_FEATURE: 已有确定性计算可以表达
- DERIVABLE_FEATURE: 需要增加确定性计算，但定义可证明
- SEMANTIC_ONLY: 目前只能保留经典语义，不能硬算
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple


# 三种状态定义
STATE_CANONICAL = "CANONICAL_FEATURE"
STATE_DERIVABLE = "DERIVABLE_FEATURE"
STATE_SEMANTIC = "SEMANTIC_ONLY"


# 6 条待审计样本
TARGET_SAMPLES = [
    {
        "id": "graph_001",
        "source_text": "生克制化，须制中有生，生中有制。太过者宜损之，不及者宜益之。",
        "classic": "滴天髓",
        "current_features": {
            "support_count": "支持数量（生）",
            "drain_count": "抑制数量（制）",
            "wang_score": "旺度分数（太过）",
            "shang_score": "衰度分数（不及）",
        },
        "analysis": {
            "language_analysis": "生克制化是命理核心概念，'须'表示必要条件，'太过/不及'表示程度描述",
            "feature_mapping_issues": [
                "'生'可能不单纯对应 support_count",
                "'制'可能不单纯对应 drain_count",
                "'太过/不及'缺乏明确阈值",
            ],
            "classification": STATE_SEMANTIC,
            "reason": "原典未明确指定 Feature 定义和阈值",
        },
    },
    {
        "id": "graph_002",
        "source_text": "一行得二三人之气，则党众而专，须从其势。",
        "classic": "滴天髓",
        "current_features": {
            "support_count": "支持数量",
            "drain_count": "抑制数量",
            "dominant_element": "主导五行",
        },
        "analysis": {
            "language_analysis": "'二三人'可能是约数（多数）而非确数（≥2），'一行'指单一五行",
            "feature_mapping_issues": [
                "'二三人'是约数还是确数？",
                "'党众而专'缺乏明确定义",
                "'从势'是否对应 follow_qi_shi？",
            ],
            "classification": STATE_SEMANTIC,
            "reason": "'二三人'语义不确定，可能是约数表达",
        },
    },
    {
        "id": "graph_004",
        "source_text": "辛金软弱，温润而清，畏土之埋，乐水之盈。",
        "classic": "滴天髓",
        "current_features": {
            "wu_element_wang": "土旺程度",
            "shui_element_wang": "水旺程度",
        },
        "analysis": {
            "language_analysis": "'畏土之埋'是程度概念还是存在概念？'乐水之盈'的'盈'如何量化？",
            "feature_mapping_issues": [
                "'埋'的程度标准未明确",
                "'盈'的程度标准未明确",
                "原典可能是定性描述而非定量",
            ],
            "classification": STATE_SEMANTIC,
            "reason": "原典为定性描述，缺乏定量标准",
        },
    },
    {
        "id": "graph_005",
        "source_text": "戊己愁逢甲乙，干头须要庚辛。",
        "classic": "渊海子平",
        "current_features": {
            "jia_yi_transparent": "甲乙透干",
            "geng_xin_transparent": "庚辛透干",
        },
        "analysis": {
            "language_analysis": "'愁逢'可能表示不利影响，'须要'表示必要条件",
            "feature_mapping_issues": [
                "'愁逢'是否明确条件关系？",
                "'须要'是否对应 prerequisite？",
                "原典是否有其他相关论述？",
            ],
            "classification": STATE_DERIVABLE,
            "reason": "可能有明确的条件关系，但需要更多原典验证",
        },
    },
    {
        "id": "graph_008",
        "source_text": "火炽乘龙，水荡骑虎。",
        "classic": "滴天髓",
        "current_features": {
            "huo_element_wang": "火旺程度",
            "shui_element_wang": "水旺程度",
            "chen_earth_present": "辰土存在",
            "yin_wood_present": "寅木存在",
        },
        "analysis": {
            "language_analysis": "'火炽''水荡'是程度描述，'乘龙''骑虎'是隐喻表达",
            "feature_mapping_issues": [
                "'火炽'的程度标准？",
                "'水荡'的程度标准？",
                "'乘龙''骑虎'是否明确条件？",
            ],
            "classification": STATE_SEMANTIC,
            "reason": "原典为隐喻表达，缺乏明确程度标准",
        },
    },
    {
        "id": "graph_009",
        "source_text": "戊土固重，既中且正。静翕动辟，万物司命。水润物生，火燥物病。",
        "classic": "滴天髓",
        "current_features": {
            "wu_element_heavy": "土重程度",
            "shui_moistening": "水润程度",
            "huo_drying": "火燥程度",
        },
        "analysis": {
            "language_analysis": "'固重''水润''火燥'都是程度描述",
            "feature_mapping_issues": [
                "'固重'的程度标准？",
                "'水润'的程度标准？",
                "'火燥'的程度标准？",
            ],
            "classification": STATE_SEMANTIC,
            "reason": "原典为定性描述，缺乏定量标准",
        },
    },
]


def audit_sample(sample: dict) -> dict:
    """审计单条样本"""
    analysis = sample["analysis"]

    return {
        "id": sample["id"],
        "source_text": sample["source_text"],
        "classic": sample["classic"],
        "current_features": sample["current_features"],
        "language_analysis": analysis["language_analysis"],
        "feature_mapping_issues": analysis["feature_mapping_issues"],
        "classification": analysis["classification"],
        "classification_reason": analysis["reason"],
    }


def main():
    print("=== P0-4.7: 五经 Semantic Feature Ontology 审计 ===\n")

    results = []
    state_counts = {
        STATE_CANONICAL: 0,
        STATE_DERIVABLE: 0,
        STATE_SEMANTIC: 0,
    }

    for sample in TARGET_SAMPLES:
        print(f"审计: {sample['id']} - {sample['classic']}")
        print(f"  原文: {sample['source_text'][:60]}...")

        result = audit_sample(sample)
        results.append(result)
        state_counts[result["classification"]] += 1

        print(f"  分类: {result['classification']}")
        print(f"  原因: {result['classification_reason']}")
        print()

    # 输出统计
    print("=== 分类结果汇总 ===")
    print(f"  CANONICAL_FEATURE: {state_counts[STATE_CANONICAL]}")
    print(f"  DERIVABLE_FEATURE: {state_counts[STATE_DERIVABLE]}")
    print(f"  SEMANTIC_ONLY: {state_counts[STATE_SEMANTIC]}")

    # 输出详细报告
    print("\n=== 详细报告 ===")
    for r in results:
        print(f"\n[{r['id']}] {r['classic']}")
        print(f"  原文: {r['source_text'][:80]}...")
        print(f"  分类: {r['classification']}")
        print(f"  原因: {r['classification_reason']}")
        if r['feature_mapping_issues']:
            print(f"  问题:")
            for issue in r['feature_mapping_issues']:
                print(f"    - {issue}")

    # 保存结果
    report = {
        "generated": __import__('datetime').datetime.now().isoformat(),
        "summary": {
            "total_samples": len(results),
            "state_distribution": state_counts,
        },
        "results": results,
    }

    with open('data/p0_4_7_feature_audit_result.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 data/p0_4_7_feature_audit_result.json")


if __name__ == '__main__':
    main()
