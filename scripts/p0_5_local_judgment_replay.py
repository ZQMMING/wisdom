# -*- coding: utf-8 -*-
"""P0-5: 五经 Local Judgment 第一批真实生产规则

目标：
- 使用已验证的 Authorized Primitive 做第一批真实 Local Judgment
- 只做局部、可验证、低歧义的问题
- 验证：原典 → Canonical Feature → Authorized Primitive → Condition → Local Judgment

测试 Primitive：
1. 得令 (de_ling) - CANONICAL_FEATURE
2. 得地 (de_di) - CANONICAL_FEATURE
3. 得势 (de_shi) - CANONICAL_FEATURE

排除：
- 身强/身弱综合判断（Composite Judgment）
- support_ratio（CURRENTLY_NON_PRODUCTION）
- wu_ji_pressure（CURRENTLY_NON_PRODUCTION）
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class JudgmentStatus(Enum):
    """Judgment 状态"""
    PASS = "PASS"  # 条件满足
    FAIL = "FAIL"  # 条件不满足
    BLOCKED = "BLOCKED"  # 被阻断


@dataclass
class PrimitiveCondition:
    """Primitive 条件"""
    name: str
    feature_name: str
    operator: str
    threshold: float
    source_text: str
    classic: str


@dataclass
class LocalJudgment:
    """Local Judgment"""
    primitive_name: str
    condition_met: bool
    status: JudgmentStatus
    evidence_trace: str
    auth_gate_passed: bool
    uses_legacy_strength: bool


# 第一批可生产 Primitive 定义
PRODUCTION_PRIMITIVES = [
    {
        "id": "de_ling",
        "name": "得令",
        "feature_name": "de_ling",
        "operator": "==",
        "threshold": True,
        "source_text": "得令者旺（月令支持日主）",
        "classic": "滴天髓",
        "condition": PrimitiveCondition(
            name="得令",
            feature_name="de_ling",
            operator=="==",
            threshold=True,
            source_text="得令者旺（月令支持日主）",
            classic="滴天髓",
        ),
    },
    {
        "id": "de_di",
        "name": "得地",
        "feature_name": "de_di",
        "operator": "==",
        "threshold": True,
        "source_text": "得地者强（日支支持日主）",
        "classic": "滴天髓",
        "condition": PrimitiveCondition(
            name="得地",
            feature_name="de_di",
            operator=="==",
            threshold=True,
            source_text="得地者强（日支支持日主）",
            classic="滴天髓",
        ),
    },
    {
        "id": "de_shi",
        "name": "得势",
        "feature_name": "de_shi",
        "operator": "==",
        "threshold": True,
        "source_text": "得势者强（天干支持日主）",
        "classic": "滴天髓",
        "condition": PrimitiveCondition(
            name="得势",
            feature_name="de_shi",
            operator=="==",
            threshold=True,
            source_text="得势者强（天干支持日主）",
            classic="滴天髓",
        ),
    },
]


# 真实命例测试数据（来自 P0-3.9 已验证命例）
TEST_CHARTS = [
    {
        "id": "chart_001",
        "birth": "1990-5-15 10:00 male",
        "de_ling": False,
        "de_di": 2,
        "de_shi": 2,
        "support": 4.4,
        "drain": 2.5,
        "description": "身偏强命例",
    },
    {
        "id": "chart_002",
        "birth": "1985-3-21 6:00 male",
        "de_ling": False,
        "de_di": 3,
        "de_shi": 1,
        "support": 1.9,
        "drain": 3.5,
        "description": "身偏弱命例",
    },
    {
        "id": "chart_003",
        "birth": "1992-8-8 14:00 female",
        "de_ling": False,
        "de_di": 3,
        "de_shi": 1,
        "support": 2.5,
        "drain": 6.5,
        "description": "身弱命例",
    },
    {
        "id": "chart_004",
        "birth": "1995-1-1 12:00 male",
        "de_ling": True,
        "de_di": 2,
        "de_shi": 0,
        "support": 1.5,
        "drain": 6.0,
        "description": "得令命例",
    },
]


def evaluate_primitive(primitive: dict, chart: dict) -> LocalJudgment:
    """评估单条 Primitive"""
    feature_name = primitive["feature_name"]
    operator = primitive["condition"].operator
    threshold = primitive["condition"].threshold

    # 获取 Feature 值
    feature_value = chart.get(feature_name)

    # 评估条件
    condition_met = False
    if operator == "==":
        condition_met = (feature_value == threshold)
    elif operator == ">=":
        condition_met = (feature_value >= threshold)
    elif operator == ">":
        condition_met = (feature_value > threshold)

    # 判断状态
    if condition_met:
        status = JudgmentStatus.PASS
    else:
        status = JudgmentStatus.FAIL

    # 生成证据追踪
    evidence_trace = f"{primitive['classic']}::{primitive['condition'].source_text}"

    return LocalJudgment(
        primitive_name=primitive["name"],
        condition_met=condition_met,
        status=status,
        evidence_trace=evidence_trace,
        auth_gate_passed=True,  # 已授权
        uses_legacy_strength=False,  # 不使用旧 strength_engine
    )


def main():
    print("=== P0-5: 五经 Local Judgment 第一批真实生产规则 ===\n")

    all_results = []
    pass_count = 0
    fail_count = 0

    for chart in TEST_CHARTS:
        print(f"命例: {chart['id']} - {chart['description']}")
        print(f"  de_ling={chart['de_ling']}, de_di={chart['de_di']}, de_shi={chart['de_shi']}")

        chart_results = []
        for primitive in PRODUCTION_PRIMITIVES:
            judgment = evaluate_primitive(primitive, chart)
            chart_results.append({
                "primitive": primitive["name"],
                "condition_met": judgment.condition_met,
                "status": judgment.status.value,
                "evidence_trace": judgment.evidence_trace,
                "auth_gate_passed": judgment.auth_gate_passed,
                "uses_legacy_strength": judgment.uses_legacy_strength,
            })

            if judgment.status == JudgmentStatus.PASS:
                pass_count += 1
                print(f"  ✅ {primitive['name']}: PASS")
            else:
                fail_count += 1
                print(f"  ❌ {primitive['name']}: FAIL")

        all_results.append({
            "chart_id": chart["id"],
            "description": chart["description"],
            "features": {
                "de_ling": chart["de_ling"],
                "de_di": chart["de_di"],
                "de_shi": chart["de_shi"],
            },
            "judgments": chart_results,
        })

    # 输出统计
    print("\n=== 验证结果汇总 ===")
    print(f"总测试: {len(TEST_CHARTS)} 命例 × {len(PRODUCTION_PRIMITIVES)} Primitive = {len(TEST_CHARTS) * len(PRODUCTION_PRIMITIVES)} 条")
    print(f"PASS: {pass_count}")
    print(f"FAIL: {fail_count}")
    print(f"成功率: {pass_count/(pass_count+fail_count)*100:.1f}%")

    # 输出详细报告
    print("\n=== 详细报告 ===")
    for r in all_results:
        print(f"\n[{r['chart_id']}] {r['description']}")
        for j in r['judgments']:
            status = "✅" if j['status'] == 'PASS' else "❌"
            print(f"  {status} {j['primitive']}: {j['status']}")
            print(f"     证据: {j['evidence_trace'][:50]}...")

    # 保存结果
    report = {
        "generated": __import__('datetime').datetime.now().isoformat(),
        "summary": {
            "total_tests": len(TEST_CHARTS) * len(PRODUCTION_PRIMITIVES),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": f"{pass_count/(pass_count+fail_count)*100:.1f}%",
        },
        "results": all_results,
    }

    with open('data/p0_5_judgment_result.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 data/p0_5_judgment_result.json")


if __name__ == '__main__':
    main()
