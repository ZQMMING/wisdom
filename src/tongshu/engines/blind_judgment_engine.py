# -*- coding: utf-8 -*-
"""盲派 Judgment Engine V1.1 — 只执行Registry已授权的Judgment，Clause真实执行+Exclusion真执行。

10条铁律锁死：
1. 只消费Assertion+Features，不直接读BaziChart
2. 只执行Registry中存在的Judgment_ID
3. Clause是逻辑条件，不是评分
4. Judgment Result必须是结构枚举，不是事件
5. Judgment ≠ Event（应期窗口≠事件坐实）
6. Exclusion必须实际执行（触发Exclusion=不产生Judgment）
7. Clause禁止偷偷形成评分
8. Judgment不反向修改Assertion
9. Provenance必须能反查
10. V1不碰Interpretation

输入：
  - assertions_present: 命中的Assertion_ID集合
  - features_present: 命中的特征集合（从Assertion细节提取）

输出：Judgment列表（结构化判断，带完整provenance）
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

from .blind_judgment_registry import (
    JudgmentRule, JUDGMENT_REGISTRY,
    get_production_judgments,
)
from .blind_clause_mapper import evaluate_clause, evaluate_exclusion


@dataclass(frozen=True)
class JudgmentResult:
    """单条Judgment执行结果"""
    judgment_id: str
    domain: str
    judgment_result: str
    triggered_clauses: Tuple[str, ...]
    matched_assertions: Tuple[str, ...]
    blocked_by_exclusion: bool
    exclusion_reason: str
    provenance: str
    evidence_id: str
    source: str
    source_location: str


@dataclass(frozen=True)
class JudgmentEngineResult:
    """Judgment Engine总输出"""
    triggered_judgments: Tuple[JudgmentResult, ...]
    skipped_judgments: Tuple[str, ...]
    total_registry: int
    total_triggered: int
    total_skipped: int


class BlindJudgmentEngine:
    """Judgment Engine V1.1：Clause真实执行+Exclusion真执行"""

    def __init__(self):
        self.registry = get_production_judgments()

    def judge(self, assertions_present: Set[str],
              features_present: Set[str] = None) -> JudgmentEngineResult:
        """
        执行Judgment Engine。

        Args:
            assertions_present: 当前命局+岁运中命中的Assertion_ID集合
            features_present: 当前命局+岁运中命中的特征集合（Clause条件）

        Returns:
            JudgmentEngineResult: 触发的Judgment列表
        """
        if features_present is None:
            features_present = set()

        triggered: List[JudgmentResult] = []
        skipped: List[str] = []

        for j_id, rule in self.registry.items():
            # Step 1: 检查所需Assertion是否全部存在
            required_assertions = set(rule.assertion_inputs)
            missing = required_assertions - assertions_present
            if missing:
                skipped.append(j_id)
                continue

            # Step 2: 逐条评估Clause
            triggered_clauses: List[str] = []
            unresolved_clauses: List[str] = []
            for clause in rule.clauses:
                clause_triggered, clause_status = evaluate_clause(j_id, clause.clause_id, features_present)
                if clause_triggered:
                    triggered_clauses.append(clause.clause_id)
                elif clause_status == "NOT_EVALUABLE":
                    unresolved_clauses.append(clause.clause_id)

            # Step 2b: 未映射Clause = fail-closed，不得生产Judgment
            if unresolved_clauses:
                skipped.append(j_id)
                continue

            # Step 2c: 至少1个Clause触发才生产Judgment
            if not triggered_clauses:
                skipped.append(j_id)
                continue

            # Step 3: 检查Exclusion是否触发
            excl_blocked, excl_reason = evaluate_exclusion(j_id, rule.exclusions, features_present)
            if excl_blocked:
                skipped.append(j_id)
                continue

            # Step 4: 构造provenance链
            prov = (
                f"{j_id} → "
                f"clauses={tuple(triggered_clauses)} → "
                f"assertions={tuple(sorted(required_assertions & assertions_present))} → "
                f"evidence={rule.evidence_id} → "
                f"{rule.source}"
            )

            result = JudgmentResult(
                judgment_id=j_id,
                domain=rule.domain.value,
                judgment_result=rule.judgment_result,
                triggered_clauses=tuple(triggered_clauses),
                matched_assertions=tuple(sorted(required_assertions & assertions_present)),
                blocked_by_exclusion=False,
                exclusion_reason="",
                provenance=prov,
                evidence_id=rule.evidence_id,
                source=rule.source,
                source_location=rule.source_location,
            )
            triggered.append(result)

        return JudgmentEngineResult(
            triggered_judgments=tuple(triggered),
            skipped_judgments=tuple(skipped),
            total_registry=len(self.registry),
            total_triggered=len(triggered),
            total_skipped=len(skipped),
        )


# ── Engine Gate 检查 ─────────────────────────────────────────────

def validate_engine() -> List[str]:
    """Judgment Engine V1.1 Gate检查"""
    errors = []
    engine = BlindJudgmentEngine()

    # G-E1: 空Assertion输入=0触发
    empty_result = engine.judge(set())
    if empty_result.total_triggered != 0:
        errors.append("空Assertion输入产生了Judgment")

    # G-E2: 伪造Assertion=0触发
    fake_result = engine.judge({"A-FAKE-XXX"})
    if fake_result.total_triggered != 0:
        errors.append("伪造Assertion产生了Judgment")

    # G-E3: 部分Assertion不全触发
    partial_result = engine.judge({"A-PJ-FAN"})
    if partial_result.total_triggered >= len(engine.registry):
        errors.append("部分Assertion触发了全部Judgment")

    # G-E4: 所有Assertion+所有Features=全部触发
    all_assertions = set()
    all_features = set()
    for rule in engine.registry.values():
        all_assertions.update(rule.assertion_inputs)
        # 从Clause Mapper收集所有特征
        from .blind_clause_mapper import CLAUSE_FEATURE_MAP
        for (j_id, c_id), feats in CLAUSE_FEATURE_MAP.items():
            if j_id in engine.registry:
                all_features.update(feats)

    all_result = engine.judge(all_assertions, all_features)
    if all_result.total_triggered != len(engine.registry):
        errors.append(f"全Assertion+全Features触发数={all_result.total_triggered}，应为{len(engine.registry)}")

    # G-E5: 每个触发的Judgment都有provenance
    for j in all_result.triggered_judgments:
        if not j.provenance:
            errors.append(f"{j.judgment_id} 缺provenance")
        if not j.evidence_id:
            errors.append(f"{j.judgment_id} 缺evidence_id")
        if not j.source:
            errors.append(f"{j.judgment_id} 缺source")

    # G-E6: 不允许出现WEALTH_LEVEL
    for j in all_result.triggered_judgments:
        if "WEALTH_LEVEL" in j.judgment_result or "财富等级" in j.judgment_result:
            errors.append(f"{j.judgment_id} 出现WEALTH_LEVEL")

    # G-E7: 不允许出现Event断言
    event_keywords = ["MARRIED", "DIVORCED", "PRISON_EVENT", "DISEASE", "DIED", "GETS_RICH"]
    for j in all_result.triggered_judgments:
        for kw in event_keywords:
            if kw in j.judgment_result:
                errors.append(f"{j.judgment_id} 出现Event断言: {kw}")

    # G-E8: Clause真实执行（不是全Assertion=全Clause）
    # 只喂Assertion不喂Features，应该触发0条或很少
    no_feature_result = engine.judge(all_assertions, set())
    if no_feature_result.total_triggered == len(engine.registry):
        errors.append("Clause未真实执行：无Features也全触发")

    # G-E9: Exclusion真执行
    # 喂入阻断特征，应该有Judgment被阻断
    from .blind_clause_mapper import EXCLUSION_FEATURE_MAP
    blocking_features = set()
    for feats in EXCLUSION_FEATURE_MAP.values():
        blocking_features.update(feats)
    exclusion_result = engine.judge(all_assertions, blocking_features)
    if exclusion_result.total_triggered == len(engine.registry):
        errors.append("Exclusion未真实执行：全阻断特征也全触发")

    return errors


if __name__ == "__main__":
    errors = validate_engine()
    print(f"Registry总Judgment: {len(get_production_judgments())}")
    if errors:
        print(f"❌ Engine Gate失败 {len(errors)}项:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✅ Judgment Engine V1.1 Gate PASS")

    # 演示
    engine = BlindJudgmentEngine()
    all_assertions = set()
    all_features = set()
    from .blind_clause_mapper import CLAUSE_FEATURE_MAP
    for rule in engine.registry.values():
        all_assertions.update(rule.assertion_inputs)
    for (j_id, c_id), feats in CLAUSE_FEATURE_MAP.items():
        all_features.update(feats)

    result = engine.judge(all_assertions, all_features)
    print(f"\n全Assertion+全Features演示:")
    print(f"  总Registry: {result.total_registry}")
    print(f"  触发: {result.total_triggered}")
    print(f"  跳过: {result.total_skipped}")
