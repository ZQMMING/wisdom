# -*- coding: utf-8 -*-
"""P0-4.8: Semantic Feature → Primitive 映射验证

目标：
- 验证三类 Feature 如何安全进入 Primitive
- 特别保证 SEMANTIC_ONLY 不伪装成确定性计算

测试矩阵：
A. CANONICAL_FEATURE → Primitive
B. DERIVABLE_FEATURE → Primitive
C. SEMANTIC_ONLY → Primitive（禁止伪装）
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class FeatureType(Enum):
    """Feature 类型"""
    CANONICAL = "CANONICAL_FEATURE"
    DERIVABLE = "DERIVABLE_FEATURE"
    SEMANTIC_ONLY = "SEMANTIC_ONLY"


class MappingResult(Enum):
    """映射结果"""
    SAFE = "SAFE"  # 安全映射
    UNSAFE = "UNSAFE"  # 不安全映射
    BLOCKED = "BLOCKED"  # 被阻止（SEMANTIC_ONLY 被错误映射）


@dataclass
class FeatureDefinition:
    """Feature 定义"""
    name: str
    feature_type: FeatureType
    definition: str  # 明确定义
    source: str  # 来源（原典/计算）
    is_deterministic: bool  # 是否确定性计算


@dataclass
class PrimitiveTest:
    """Primitive 测试样本"""
    id: str
    source_text: str
    classic: str
    feature_definitions: List[FeatureDefinition]
    expected_result: MappingResult
    description: str


# 测试样本：基于 P0-4.7 审计结果
TEST_SAMPLES = [
    # ===== A. CANONICAL_FEATURE 测试 =====
    {
        "id": "canonical_001",
        "source_text": "得令者旺（月令支持日主）",
        "classic": "滴天髓",
        "feature_type": FeatureType.CANONICAL,
        "feature_name": "de_ling",
        "feature_definition": "月令五行支持日主五行",
        "is_deterministic": True,
        "expected_result": MappingResult.SAFE,
        "description": "得令是确定性计算，可以直接映射",
    },
    {
        "id": "canonical_002",
        "source_text": "得地者强（日支支持日主）",
        "classic": "滴天髓",
        "feature_type": FeatureType.CANONICAL,
        "feature_name": "de_di",
        "feature_definition": "日支五行支持日主五行",
        "is_deterministic": True,
        "expected_result": MappingResult.SAFE,
        "description": "得地是确定性计算，可以直接映射",
    },
    {
        "id": "canonical_003",
        "source_text": "得势者强（天干支持日主）",
        "classic": "滴天髓",
        "feature_type": FeatureType.CANONICAL,
        "feature_name": "de_shi",
        "feature_definition": "天干五行支持日主五行",
        "is_deterministic": True,
        "expected_result": MappingResult.SAFE,
        "description": "得势是确定性计算，可以直接映射",
    },

    # ===== B. DERIVABLE_FEATURE 测试 =====
    {
        "id": "derivable_001",
        "source_text": "一行得二三人之气",
        "classic": "滴天髓",
        "feature_type": FeatureType.DERIVABLE,
        "feature_name": "support_ratio",
        "feature_definition": "支持数量/总数量（待定义）",
        "is_deterministic": False,
        "expected_result": MappingResult.SAFE,
        "description": "需要新计算，但定义可证明",
    },
    {
        "id": "derivable_002",
        "source_text": "戊己愁逢甲乙，干头须要庚辛",
        "classic": "渊海子平",
        "feature_type": FeatureType.DERIVABLE,
        "feature_name": "wu_ji_pressure",
        "feature_definition": "戊己土受甲乙木压制的程度（待定义）",
        "is_deterministic": False,
        "expected_result": MappingResult.SAFE,
        "description": "需要新计算，但定义可证明",
    },

    # ===== C. SEMANTIC_ONLY 测试（关键：禁止伪装）=====
    {
        "id": "semantic_001",
        "source_text": "火炽乘龙，水荡骑虎",
        "classic": "滴天髓",
        "feature_type": FeatureType.SEMANTIC_ONLY,
        "feature_name": "huo_chizhi",
        "feature_definition": "火炽程度（无明确定义）",
        "is_deterministic": False,
        "expected_result": MappingResult.BLOCKED,
        "description": "原典为隐喻表达，不能伪装成确定性计算",
    },
    {
        "id": "semantic_002",
        "source_text": "畏土之埋，乐水之盈",
        "classic": "滴天髓",
        "feature_type": FeatureType.SEMANTIC_ONLY,
        "feature_name": "wu_zhi_mai",
        "feature_definition": "土埋程度（无明确定义）",
        "is_deterministic": False,
        "expected_result": MappingResult.BLOCKED,
        "description": "原典为定性描述，不能伪装成确定性计算",
    },
    {
        "id": "semantic_003",
        "source_text": "生克制化，须制中有生",
        "classic": "滴天髓",
        "feature_type": FeatureType.SEMANTIC_ONLY,
        "feature_name": "sheng_ke_balance",
        "feature_definition": "生克平衡程度（无明确定义）",
        "is_deterministic": False,
        "expected_result": MappingResult.BLOCKED,
        "description": "原典未明确阈值，不能伪装成确定性计算",
    },
]


def verify_mapping(sample: dict) -> dict:
    """验证单条映射"""
    feature_type = FeatureType(sample["feature_type"])
    expected = MappingResult(sample["expected_result"])

    # 安全检查
    issues = []
    is_safe = True

    # 规则 1: SEMANTIC_ONLY 不能是确定性计算
    if feature_type == FeatureType.SEMANTIC_ONLY and sample["is_deterministic"]:
        issues.append("SEMANTIC_ONLY 不能是确定性计算")
        is_safe = False

    # 规则 2: DERIVABLE_FEATURE 需要有明确定义
    if feature_type == FeatureType.DERIVABLE:
        if not sample["feature_definition"] or "待定义" in sample["feature_definition"]:
            issues.append("DERIVABLE_FEATURE 需要明确定义")
            is_safe = False

    # 规则 3: CANONICAL_FEATURE 必须是确定性计算
    if feature_type == FeatureType.CANONICAL and not sample["is_deterministic"]:
        issues.append("CANONICAL_FEATURE 必须是确定性计算")
        is_safe = False

    # 判断最终结果
    if not is_safe:
        actual_result = MappingResult.UNSAFE
    elif feature_type == FeatureType.SEMANTIC_ONLY:
        actual_result = MappingResult.BLOCKED
    else:
        actual_result = MappingResult.SAFE

    # 判断是否符合预期
    match = actual_result == expected

    return {
        "id": sample["id"],
        "source_text": sample["source_text"][:60],
        "classic": sample["classic"],
        "feature_type": feature_type.value,
        "feature_name": sample["feature_name"],
        "is_deterministic": sample["is_deterministic"],
        "expected_result": expected.value,
        "actual_result": actual_result.value,
        "match": match,
        "issues": issues,
        "description": sample["description"],
    }


def main():
    print("=== P0-4.8: Semantic Feature → Primitive 映射验证 ===\n")

    results = []
    result_counts = {r.value: 0 for r in MappingResult}
    type_counts = {t.value: 0 for t in FeatureType}
    match_count = 0

    for sample in TEST_SAMPLES:
        print(f"验证: {sample['id']} - {sample['classic']}")
        print(f"  原文: {sample['source_text'][:50]}...")
        print(f"  Feature类型: {sample['feature_type']}")

        result = verify_mapping(sample)
        results.append(result)
        result_counts[result["actual_result"]] += 1
        type_counts[result["feature_type"]] += 1

        if result["match"]:
            match_count += 1
            print(f"  ✅ 符合预期: {result['actual_result']}")
        else:
            print(f"  ❌ 不符合预期: 期望{result['expected_result']}, 实际{result['actual_result']}")

        if result["issues"]:
            print(f"  问题: {', '.join(result['issues'])}")
        print()

    # 输出统计
    print("=== 验证结果汇总 ===")
    print(f"总测试: {len(results)}")
    print(f"符合预期: {match_count}/{len(results)}")
    print()
    print("结果分布:")
    for r, count in sorted(result_counts.items(), key=lambda x: -x[1]):
        print(f"  {r}: {count}")
    print()
    print("Feature 类型分布:")
    for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {t}: {count}")

    # 输出详细报告
    print("\n=== 详细报告 ===")
    for r in results:
        status = "✅" if r["match"] else "❌"
        print(f"\n[{status}] {r['id']}")
        print(f"  原文: {r['source_text']}...")
        print(f"  Feature: {r['feature_name']} ({r['feature_type']})")
        print(f"  预期: {r['expected_result']}, 实际: {r['actual_result']}")
        if r["issues"]:
            print(f"  问题: {', '.join(r['issues'])}")

    # 保存结果
    report = {
        "generated": __import__('datetime').datetime.now().isoformat(),
        "summary": {
            "total_tests": len(results),
            "match_count": match_count,
            "match_rate": f"{match_count/len(results)*100:.1f}%",
            "result_distribution": result_counts,
            "type_distribution": type_counts,
        },
        "results": results,
    }

    with open('data/p0_4_8_mapping_result.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 data/p0_4_8_mapping_result.json")


if __name__ == '__main__':
    main()
