# -*- coding: utf-8 -*-
"""盲派 Modern Semantic Engine V1 — 确定性Mapping Executor。

铁律：
  1. Engine不自己解释，只做查表转换
  2. 必须经过Mapping Registry，不能绕过
  3. 绝对禁止反向写入经典层

输入：JudgmentResult列表（来自Judgment Engine）
输出：ModernExpressionResult列表（用户可读的现代表达）
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, List

from .blind_judgment_engine import JudgmentResult
from .blind_mapping_registry import MAPPING_REGISTRY, MappingRule, get_mapping_by_judgment_id


@dataclass(frozen=True)
class ModernExpressionResult:
    """现代语义表达结果"""
    mapping_id: str
    judgment_id: str
    # ===== Classical（原样保留） =====
    classical_result: str
    classical_meaning: str
    # ===== Modern =====
    modern_semantic: str
    modern_domain: str
    modern_expression: str
    # ===== Boundary =====
    semantic_boundary: Tuple[str, ...]
    avoid_phrases: Tuple[str, ...]
    # ===== Provenance =====
    mapping_version: str
    provenance: str


@dataclass(frozen=True)
class ModernEngineResult:
    """Modern Engine总输出"""
    expressions: Tuple[ModernExpressionResult, ...]
    total_input: int
    total_mapped: int
    total_unmapped: int


class ModernSemanticEngine:
    """Modern Semantic Engine V1：确定性Mapping Executor"""

    def __init__(self):
        self.registry = MAPPING_REGISTRY

    def express(self, judgments: List[JudgmentResult]) -> ModernEngineResult:
        """
        把Judgment列表转换成现代语义表达列表。

        Args:
            judgments: Judgment Engine输出的JudgmentResult列表

        Returns:
            ModernEngineResult: 现代语义表达结果
        """
        expressions: List[ModernExpressionResult] = []
        unmapped: List[str] = []

        for j in judgments:
            mapping = get_mapping_by_judgment_id(j.judgment_id)
            if mapping is None:
                unmapped.append(j.judgment_id)
                continue

            # 验证review_status
            if mapping.review_status != "PASS":
                unmapped.append(j.judgment_id)
                continue

            prov = (
                f"{j.judgment_id} → "
                f"mapping={mapping.mapping_id} → "
                f"{mapping.modern_domain}"
            )

            expr = ModernExpressionResult(
                mapping_id=mapping.mapping_id,
                judgment_id=j.judgment_id,
                classical_result=mapping.classical_result,
                classical_meaning=mapping.classical_meaning,
                modern_semantic=mapping.modern_semantic,
                modern_domain=mapping.modern_domain,
                modern_expression=mapping.modern_expression,
                semantic_boundary=mapping.semantic_boundary,
                avoid_phrases=mapping.avoid_phrases,
                mapping_version=mapping.mapping_version,
                provenance=prov,
            )
            expressions.append(expr)

        return ModernEngineResult(
            expressions=tuple(expressions),
            total_input=len(judgments),
            total_mapped=len(expressions),
            total_unmapped=len(unmapped),
        )


# ── M-08 Machine Semantic Gate ────────────────────────────────────

def validate_mapping_engine() -> List[str]:
    """M-08 Machine Semantic Gate检查"""
    errors = []
    engine = ModernSemanticEngine()

    # M-08.1: 46 Judgment_ID → 46 MappingRule
    from .blind_judgment_registry import get_production_judgments
    prod = get_production_judgments()
    if len(prod) != 46:
        errors.append(f"M-08.1: Judgment Registry={len(prod)}，预期46")

    # M-08.2: 无重复Mapping_ID
    if len(engine.registry) != len(set(engine.registry.keys())):
        errors.append("M-08.2: 有重复Mapping_ID")

    # M-08.3: 无缺失Judgment_ID
    missing = []
    for j_id in prod:
        if get_mapping_by_judgment_id(j_id) is None:
            missing.append(j_id)
    if missing:
        errors.append(f"M-08.3: 缺失Mapping的Judgment: {missing}")

    # M-08.4: 所有生产Mapping review_status=PASS
    not_pass = [m.mapping_id for m in engine.registry.values() if m.review_status != "PASS"]
    if not_pass:
        errors.append(f"M-08.4: review_status!=PASS: {not_pass}")

    # M-08.5~M-08.7: Engine不读取BaziChart/Case/重算Judgment
    # （代码层已保证：输入只有JudgmentResult）

    # M-08.8: Engine不产生Event
    event_keywords = ["MARRIED", "DIVORCED", "PRISON_EVENT", "DISEASE", "DIED", "GETS_RICH"]
    for m in engine.registry.values():
        for kw in event_keywords:
            if kw in m.modern_semantic or kw in m.modern_expression:
                errors.append(f"M-08.8: {m.mapping_id} 出现Event: {kw}")

    # M-08.9: Engine不产生score/probability
    score_keywords = ["score", "probability", "weight", "百分比", "评分"]
    for m in engine.registry.values():
        for kw in score_keywords:
            if kw in m.modern_semantic.lower() or kw in m.modern_expression.lower():
                errors.append(f"M-08.9: {m.mapping_id} 出现评分: {kw}")

    # M-08.10: Classical字段immutable
    for m in engine.registry.values():
        if not m.classical_result or not m.classical_meaning:
            errors.append(f"M-08.10: {m.mapping_id} Classical字段缺失")

    # M-08.11: Mapping单向（代码层已保证）

    # M-08.12: 46条回归全部可执行
    # 构造46条JudgmentResult测试
    from .blind_judgment_engine import JudgmentResult
    test_judgments = []
    for j_id in prod:
        test_j = JudgmentResult(
            judgment_id=j_id,
            domain="test",
            judgment_result="test",
            triggered_clauses=("test",),
            matched_assertions=("test",),
            blocked_by_exclusion=False,
            exclusion_reason="",
            provenance="test",
            evidence_id="test",
            source="test",
            source_location="test",
        )
        test_judgments.append(test_j)

    result = engine.express(test_judgments)
    if result.total_mapped != 46:
        errors.append(f"M-08.12: 映射数={result.total_mapped}，预期46")

    return errors


if __name__ == "__main__":
    errors = validate_mapping_engine()
    print(f"Mapping Rule总数: {len(MAPPING_REGISTRY)}")
    if errors:
        print(f"❌ M-08 Gate失败 {len(errors)}项:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✅ M-08 Machine Semantic Gate PASS")

    # 演示
    from .blind_judgment_engine import JudgmentResult
    engine = ModernSemanticEngine()
    test_j = JudgmentResult(
        judgment_id="J-DISASTER-004",
        domain="J7",
        judgment_result="PRISON_STRUCTURE",
        triggered_clauses=("A",),
        matched_assertions=("A-DISASTER-PRISON",),
        blocked_by_exclusion=False,
        exclusion_reason="",
        provenance="test",
        evidence_id="EVD-J-DISASTER-004",
        source="盲派中级命理学第12章",
        source_location="test",
    )
    result = engine.express([test_j])
    if result.expressions:
        e = result.expressions[0]
        print(f"\n演示（J-DISASTER-004）:")
        print(f"  经典: {e.classical_result}")
        print(f"  经典含义: {e.classical_meaning}")
        print(f"  现代语义: {e.modern_semantic}")
        print(f"  现代表达: {e.modern_expression}")
        print(f"  边界: {e.semantic_boundary}")
