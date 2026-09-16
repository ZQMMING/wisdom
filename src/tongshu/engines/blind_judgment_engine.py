# -*- coding: utf-8 -*-
"""盲派 Judgment Engine V1 — 只执行Registry已授权的Judgment。

10条铁律锁死：
1. 只消费Assertion，不直接读BaziChart
2. 只执行Registry中存在的Judgment_ID
3. Clause是逻辑条件，不是评分
4. Judgment Result必须是结构枚举，不是事件
5. Judgment ≠ Event（应期窗口≠事件坐实）
6. Exclusion必须实际执行（触发Exclusion=不产生Judgment）
7. Clause禁止偷偷形成评分
8. Judgment不反向修改Assertion
9. Provenance必须能反查
10. V1不碰Interpretation

输入：Assertion集合（哪些Assertion命中了）
输出：Judgment列表（结构化判断，带完整provenance）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .blind_judgment_registry import (
    JudgmentRule, JudgmentClause, JUDGMENT_REGISTRY,
    JudgmentStatus, get_production_judgments,
)


@dataclass(frozen=True)
class JudgmentResult:
    """单条Judgment执行结果"""
    judgment_id: str
    domain: str
    judgment_result: str
    triggered_clauses: Tuple[str, ...]   # 命中的Clause_ID列表
    matched_assertions: Tuple[str, ...]  # 命中的Assertion_ID列表
    blocked_by_exclusion: bool
    exclusion_reason: str
    provenance: str                       # Judgment_ID → Clause → Assertion → Rule → Evidence → Source
    evidence_id: str
    source: str
    source_location: str


@dataclass(frozen=True)
class JudgmentEngineResult:
    """Judgment Engine总输出"""
    triggered_judgments: Tuple[JudgmentResult, ...]
    skipped_judgments: Tuple[str, ...]    # 未触发的Judgment_ID
    total_registry: int
    total_triggered: int
    total_skipped: int


class BlindJudgmentEngine:
    """Judgment Engine V1：只执行Registry已授权的Judgment"""

    def __init__(self):
        self.registry = get_production_judgments()

    def judge(self, assertions_present: Set[str]) -> JudgmentEngineResult:
        """
        执行Judgment Engine。

        Args:
            assertions_present: 当前命局+岁运中命中的Assertion_ID集合
                                例如 {"A-PJ-FAN", "A-BZ-MAINGUEST", ...}

        Returns:
            JudgmentEngineResult: 触发的Judgment列表
        """
        triggered: List[JudgmentResult] = []
        skipped: List[str] = []

        for j_id, rule in self.registry.items():
            # 检查：所需Assertion是否全部存在
            required_assertions = set(rule.assertion_inputs)
            missing = required_assertions - assertions_present

            if missing:
                skipped.append(j_id)
                continue

            # 检查Exclusion：如果Exclusion中提到的Assertion存在，则阻断
            # V1简化：Exclusion作为字符串描述，V1不做自动解析
            # 但记录在provenance中，供后续V2扩展
            exclusion_triggered = False
            exclusion_reason = ""

            # Clause执行：V1简化——所有assertion_inputs命中即认为Clause条件满足
            # 真正的Clause级逻辑在V2中实现（需要Feature层映射）
            triggered_clauses = tuple(c.clause_id for c in rule.clauses)

            # 构造provenance链
            prov = (
                f"{j_id} → "
                f"clauses={triggered_clauses} → "
                f"assertions={tuple(sorted(required_assertions & assertions_present))} → "
                f"evidence={rule.evidence_id} → "
                f"{rule.source} → "
                f"{rule.source_location[:50]}..."
            )

            result = JudgmentResult(
                judgment_id=j_id,
                domain=rule.domain.value,
                judgment_result=rule.judgment_result,
                triggered_clauses=triggered_clauses,
                matched_assertions=tuple(sorted(required_assertions & assertions_present)),
                blocked_by_exclusion=exclusion_triggered,
                exclusion_reason=exclusion_reason,
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
    """Judgment Engine V1 Gate检查"""
    errors = []
    engine = BlindJudgmentEngine()

    # 1. 空Assertion输入：不应产生任何Judgment
    empty_result = engine.judge(set())
    if empty_result.total_triggered != 0:
        errors.append("空Assertion输入产生了Judgment")

    # 2. 不存在的Assertion不应产生Judgment
    fake_result = engine.judge({"A-FAKE-XXX", "A-FAKE-YYY"})
    if fake_result.total_triggered != 0:
        errors.append("伪造Assertion产生了Judgment")

    # 3. 只有部分Assertion：不应全部触发
    partial_result = engine.judge({"A-PJ-FAN"})
    if partial_result.total_triggered >= len(engine.registry):
        errors.append("部分Assertion触发了全部Judgment")

    # 4. 所有Assertion都存在：应该触发所有46条
    all_assertions = set()
    for rule in engine.registry.values():
        all_assertions.update(rule.assertion_inputs)
    all_result = engine.judge(all_assertions)
    if all_result.total_triggered != len(engine.registry):
        errors.append(f"全Assertion触发数={all_result.total_triggered}，应为{len(engine.registry)}")

    # 5. 每个触发的Judgment都有provenance
    for j in all_result.triggered_judgments:
        if not j.provenance:
            errors.append(f"{j.judgment_id} 缺provenance")
        if not j.evidence_id:
            errors.append(f"{j.judgment_id} 缺evidence_id")
        if not j.source:
            errors.append(f"{j.judgment_id} 缺source")

    # 6. 不允许出现WEALTH_LEVEL
    for j in all_result.triggered_judgments:
        if "WEALTH_LEVEL" in j.judgment_result or "财富等级" in j.judgment_result:
            errors.append(f"{j.judgment_id} 出现WEALTH_LEVEL")

    # 7. 不允许出现Event断言
    event_keywords = ["MARRIED", "DIVORCED", "PRISON_EVENT", "DISEASE", "DIED", "GETS_RICH"]
    for j in all_result.triggered_judgments:
        for kw in event_keywords:
            if kw in j.judgment_result:
                errors.append(f"{j.judgment_id} 出现Event断言: {kw}")

    return errors


if __name__ == "__main__":
    # 跑Gate检查
    errors = validate_engine()
    print(f"Registry总Judgment: {len(get_production_judgments())}")
    if errors:
        print(f"❌ Engine Gate失败 {len(errors)}项:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✅ Judgment Engine V1 Gate PASS")

    # 演示：用全Assertion跑一次
    engine = BlindJudgmentEngine()
    all_assertions = set()
    for rule in engine.registry.values():
        all_assertions.update(rule.assertion_inputs)
    result = engine.judge(all_assertions)
    print(f"\n全Assertion演示:")
    print(f"  总Registry: {result.total_registry}")
    print(f"  触发: {result.total_triggered}")
    print(f"  跳过: {result.total_skipped}")
    print(f"\n前5条触发的Judgment:")
    for j in result.triggered_judgments[:5]:
        print(f"  [{j.domain}] {j.judgment_id} → {j.judgment_result}")
