# -*- coding: utf-8 -*-
"""P0-5.4: 寻找不依赖 strength_engine 的 Authorized Primitive

目标：
- 分析 P0-3.7 的 4 条 EXPLICIT 授权
- 识别哪些可以不用 strength_engine 实现
- 选择 1-2 个候选 Primitive 进行验证
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '.')

from tongshu.canonical.state import (
    StateAuthorizationLevel,
    ClassicalState,
    Provenance,
    Fact,
    Relation,
    FactType,
    RelationType,
)
from tongshu.engines.bazi_engine import BaziEngine


def analyze_classical_authorization():
    """分析 P0-3.7 的 4 条 EXPLICIT 授权"""
    print("=" * 60)
    print("P0-5.4: 分析 P0-3.7 的 4 条 EXPLICIT 授权")
    print("=" * 60)

    # P0-3.7 的 4 条 EXPLICIT 授权
    explicit_primitives = [
        {
            "id": "DTS-SZ-HZ-ZL",
            "source": "滴天髓·生克制化·总论",
            "text": "生克制化，须制中有生，生中有制。太过者宜损之，不及者宜益之。",
            "authorization": StateAuthorizationLevel.CLASSICAL_EXPLICIT,
            "status": "verified",
            "depends_on_strength_engine": False,  # 可能可以独立实现
        },
        {
            "id": "DTS-LF-QS",
            "source": "滴天髓·理法·气势",
            "text": "一行得二三人之气，则党众而专，须从其势",
            "authorization": StateAuthorizationLevel.CLASSICAL_EXPLICIT,
            "status": "verified",
            "depends_on_strength_engine": True,  # 需要"得气"判断，可能需要 strength
        },
        {
            "id": "DTS-LF-SZKH",
            "source": "滴天髓·理法·生扶克泄耗",
            "text": "生克制化，须制中有生，生中有制",
            "authorization": StateAuthorizationLevel.CLASSICAL_EXPLICIT,
            "status": "verified",
            "depends_on_strength_engine": False,  # 可能可以独立实现
        },
        {
            "id": "YHZP-LF-TSJX-5",
            "source": "渊海子平·论法·论太岁吉凶",
            "text": "日犯岁君，灾殃必重；五行有救，其年反必招财",
            "authorization": StateAuthorizationLevel.CLASSICAL_EXPLICIT,
            "status": "verified",
            "depends_on_strength_engine": False,  # 只需要日干和年干关系
        },
    ]

    print("\n【P0-3.7 EXPLICIT 授权列表】")
    for p in explicit_primitives:
        print(f"\n{p['id']}: {p['source']}")
        print(f"  原文: {p['text']}")
        print(f"  授权: {p['authorization'].value}")
        print(f"  依赖 strength_engine: {'是' if p['depends_on_strength_engine'] else '否'}")

    return explicit_primitives


def find_non_strength_dependent_primitives(explicit_primitives):
    """找出可以不依赖 strength_engine 的 Primitive"""
    print("\n" + "=" * 60)
    print("P0-5.4: 找出可以不依赖 strength_engine 的 Primitive")
    print("=" * 60)

    candidates = []
    for p in explicit_primitives:
        if not p["depends_on_strength_engine"]:
            candidates.append(p)
            print(f"\n✅ {p['id']}: 可独立实现")
            print(f"   理由: 只涉及 L1 事实/关系，不需要旺衰评分")
        else:
            print(f"\n⚠️ {p['id']}: 需要进一步审计")
            print(f"   理由: 可能涉及'得气'等判断，需要确认")

    return candidates


def test_candidate_primitive(candidate, chart):
    """测试候选 Primitive（示例实现）"""
    print(f"\n{'='*60}")
    print(f"测试: {candidate['id']}")
    print(f"{'='*60}")

    # 示例：检查五行生克关系（制中有生，生中有制）
    # 这需要实现具体的计算逻辑

    return {
        "primitive_id": candidate["id"],
        "source": candidate["source"],
        "condition_met": None,  # 待实现
        "evidence": "需要实现具体计算逻辑",
        "authorization": candidate["authorization"].value,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("P0-5.4: 寻找不依赖 strength_engine 的 Authorized Primitive")
    print("=" * 60)

    # Step 1: 分析 4 条 EXPLICIT 授权
    explicit_primitives = analyze_classical_authorization()

    # Step 2: 找出可不依赖 strength_engine 的
    candidates = find_non_strength_dependent_primitives(explicit_primitives)

    # Step 3: 测试候选 Primitive（示例）
    print("\n" + "=" * 60)
    print("P0-5.4: 测试候选 Primitive")
    print("=" * 60)

    # 使用一个简单命例测试
    engine = BaziEngine()
    chart = engine.compute((1990, 5, 15, 10), gender='male')

    test_results = []
    for candidate in candidates:
        result = test_candidate_primitive(candidate, chart)
        test_results.append(result)

    # 汇总
    print("\n" + "=" * 60)
    print("P0-5.4 验证结果汇总")
    print("=" * 60)
    print(f"总候选: {len(candidates)}")
    print(f"可独立实现: {len([c for c in candidates if not c['depends_on_strength_engine']])}")
    print(f"需要进一步审计: {len([c for c in candidates if c['depends_on_strength_engine']])}")

    # 保存
    output_path = Path(__file__).parent.parent / "data" / "p0_5_4_candidate_analysis.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "analysis_date": datetime.now().isoformat(),
            "total_explicit": len(explicit_primitives),
            "candidates": candidates,
            "test_results": test_results,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 {output_path}")

    # 关键结论
    print("\n" + "=" * 60)
    print("关键结论")
    print("=" * 60)
    print("- P0-3.7 有 4 条 EXPLICIT 授权")
    print("- 其中 3 条可能可以不依赖 strength_engine")
    print("- 下一步：实现这 3 条的具体计算逻辑")
    print("- 避免：把 strength_engine 接回生产链")
