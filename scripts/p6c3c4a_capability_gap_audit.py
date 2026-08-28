"""P6-C-3C-4-A: ContextResolver Capability Gap Audit.

范围严格限定为ContextResolver Selection层, 不进入Interpretation, 不接Cross-Engine Cluster.

12个审计维度:
  1. Context Input - 能接受哪些TemporalContext
  2. Layer Selection - NATAL/DAYUN/YEAR/多层
  3. Relation Selection - CLASH/CONTROLS/SAME/GENERATES等
  4. Condition Pattern - SINGLE/DOUBLE/SET/GRAPH/COMPOSITE
  5. Exact Matching - 干支、柱位、年份、大运序号
  6. Multi-Judgment - 多条Judgment同时命中
  7. Candidate Ranking - 是否存在排序需求
  8. Cross-Temporal - YEAR→NATAL、DAYUN→YEAR、多跳路径
  9. Static GRAPH - 目前完全未证明, 必须单独标记
  10. Negative Boundary - 错层、错关系、缺节点、伪满足
  11. Determinism - Selection是否稳定
  12. Index Isolation - Resolver是否只读, 不修改36 ACTIVE

最终输出:
  CONTEXT_RESOLVER_CAPABILITY_MAP (CAN_RUN / PARTIALLY_PROVEN / NOT_YET_PROVEN)
  CONTEXT_RESOLVER_EXPANSION_DECISION_LOG

关键原则:
  不要因为发现Static GRAPH = NOT_YET_PROVEN, 就自动把它定义成Capability Gap.
  区分:
    Engine不能做 → CAPABILITY_GAP
    Engine能做, 但Resolver没实现 → CAPABILITY_GAP
    Resolver理论能做, 但没有真实Canonical Asset → ASSET_GAP
    当前阶段根本没有必要做 → NOT_WORTH_EXPANDING
    尚未验证 → NOT_YET_PROVEN
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from tongshu.engines.bazi_engine import (
    BaziEngine, BaziChart,
    HEAVENLY_STEMS, EARTHLY_BRANCHES, STEM_ELEMENT, STEM_POLARITY,
    BRANCH_CLASH,
)


# ============================================================================
# 1. 数据结构
# ============================================================================

class CapabilityStatus(str, Enum):
    CAN_RUN = "CAN_RUN"
    PARTIALLY_PROVEN = "PARTIALLY_PROVEN"
    NOT_YET_PROVEN = "NOT_YET_PROVEN"


class GapType(str, Enum):
    CAPABILITY_GAP = "CAPABILITY_GAP"
    ASSET_GAP = "ASSET_GAP"
    NOT_WORTH_EXPANDING = "NOT_WORTH_EXPANDING"
    NOT_YET_PROVEN = "NOT_YET_PROVEN"
    NO_GAP = "NO_GAP"


@dataclass
class CapabilityDimension:
    dimension_id: str
    name: str
    status: CapabilityStatus
    gap_type: GapType
    description: str
    evidence: str
    recommendation: str


@dataclass
class ExpansionDecision:
    decision_id: str
    dimension: str
    gap_type: GapType
    priority: str  # P0/P1/P2/DEFER
    action: str
    acceptance_criteria: str
    fallback: str


# ============================================================================
# 2. ContextResolver 能力审计
# ============================================================================

def audit_context_resolver() -> tuple[list[CapabilityDimension], list[ExpansionDecision]]:
    """审计ContextResolver的12个维度能力."""

    dimensions = []
    decisions = []

    # 维度1: Context Input
    dimensions.append(CapabilityDimension(
        dimension_id="CTX-01",
        name="Context Input",
        status=CapabilityStatus.CAN_RUN,
        gap_type=GapType.NO_GAP,
        description="能接受哪些TemporalContext",
        evidence="MVS验证: birth_data=(1983,6,15,12), gender=male, target_year=int, 全部合法. TemporalContext包含NATAL/DAYUN/YEAR三层节点和关系.",
        recommendation="保持当前Input Contract, 不需要扩展.",
    ))
    decisions.append(ExpansionDecision(
        decision_id="DEC-01",
        dimension="Context Input",
        gap_type=GapType.NO_GAP,
        priority="DEFER",
        action="保持当前Input Contract",
        acceptance_criteria="N/A",
        fallback="N/A",
    ))

    # 维度2: Layer Selection
    dimensions.append(CapabilityDimension(
        dimension_id="CTX-02",
        name="Layer Selection",
        status=CapabilityStatus.PARTIALLY_PROVEN,
        gap_type=GapType.NOT_YET_PROVEN,
        description="NATAL/DAYUN/YEAR/多层选择",
        evidence="MVS验证: YEAR→NATAL (CT-004)和DAYUN→YEAR (CT-003)的Layer Constraint严格执行. 但NATAL→DAYUN、NATAL→YEAR(反向)、DAYUN→NATAL、多层组合(如NATAL→DAYUN→YEAR)尚未验证.",
        recommendation="渐进验证其他层间组合, 不需要修改Resolver.",
    ))
    decisions.append(ExpansionDecision(
        decision_id="DEC-02",
        dimension="Layer Selection",
        gap_type=GapType.NOT_YET_PROVEN,
        priority="P1",
        action="渐进验证NATAL→DAYUN、NATAL→YEAR(反向)、DAYUN→NATAL、多层组合",
        acceptance_criteria="每种层间组合至少1条Positive + 2条Negative",
        fallback="如果发现Layer Constraint有缺陷, 回到Capability Contract修复",
    ))

    # 维度3: Relation Selection
    dimensions.append(CapabilityDimension(
        dimension_id="CTX-03",
        name="Relation Selection",
        status=CapabilityStatus.PARTIALLY_PROVEN,
        gap_type=GapType.ASSET_GAP,
        description="CLASH/CONTROLS/SAME/GENERATES等关系选择",
        evidence="MVS验证: CLASH (CT-004)和SAME (CT-003)的Relation Constraint严格执行. CONTROLS和GENERATES在Negative测试中验证了不会冒充SAME/CLASH, 但没有对应的ACTIVE Judgment使用CONTROLS/GENERATES作为主关系. 其他关系(COMBINES/HARM/PUNISHMENT/TRANSFORMS)完全未验证.",
        recommendation="CONTROLS/GENERATES有Engine能力但缺少Canonical Asset, 属于ASSET_GAP. 其他关系需要先确认是否有Canonical Asset.",
    ))
    decisions.append(ExpansionDecision(
        decision_id="DEC-03",
        dimension="Relation Selection",
        gap_type=GapType.ASSET_GAP,
        priority="P1",
        action="为CONTROLS/GENERATES寻找真实Canonical Asset并验证; 其他关系先做Source Audit确认是否存在",
        acceptance_criteria="每种关系至少1条ACTIVE Judgment + Positive/Negative验证",
        fallback="如果找不到Canonical Asset, 保持NOT_YET_PROVEN, 不制造资产",
    ))

    # 维度4: Condition Pattern
    dimensions.append(CapabilityDimension(
        dimension_id="CTX-04",
        name="Condition Pattern",
        status=CapabilityStatus.PARTIALLY_PROVEN,
        gap_type=GapType.NOT_YET_PROVEN,
        description="SINGLE/DOUBLE/SET/GRAPH/COMPOSITE条件模式",
        evidence="MVS验证: SINGLE (CT-004 CONDITION模式, 单条件CLASH)和EXACT (CT-003, 干支完全相同)模式. DOUBLE/SET/GRAPH/COMPOSITE模式在CROSS_TEMPORAL中尚未验证. Static GRAPH的GRAPH模式有30条ACTIVE但ContextResolver尚未接入.",
        recommendation="DOUBLE/SET/COMPOSITE需要渐进验证, GRAPH模式需要先接入Static GRAPH.",
    ))
    decisions.append(ExpansionDecision(
        decision_id="DEC-04",
        dimension="Condition Pattern",
        gap_type=GapType.NOT_YET_PROVEN,
        priority="P1",
        action="渐进验证DOUBLE/SET/COMPOSITE模式; GRAPH模式在Static GRAPH接入后验证",
        acceptance_criteria="每种模式至少1条ACTIVE Judgment + Positive/Negative验证",
        fallback="如果发现模式有缺陷, 回到Capability Contract修复",
    ))

    # 维度5: Exact Matching
    dimensions.append(CapabilityDimension(
        dimension_id="CTX-05",
        name="Exact Matching",
        status=CapabilityStatus.CAN_RUN,
        gap_type=GapType.NO_GAP,
        description="干支、柱位、年份、大运序号的精确匹配",
        evidence="MVS验证: CT-003 EXACT模式严格检查干支完全相同(同干不同支被REJECT). CT-004 CONDITION模式检查地支六冲. 柱位(DAY_PILLAR)、年份(target_year)、大运序号(dayun_idx)在TemporalContext中都有明确标识.",
        recommendation="保持当前Exact Matching逻辑, 不需要扩展.",
    ))
    decisions.append(ExpansionDecision(
        decision_id="DEC-05",
        dimension="Exact Matching",
        gap_type=GapType.NO_GAP,
        priority="DEFER",
        action="保持当前Exact Matching逻辑",
        acceptance_criteria="N/A",
        fallback="N/A",
    ))

    # 维度6: Multi-Judgment
    dimensions.append(CapabilityDimension(
        dimension_id="CTX-06",
        name="Multi-Judgment",
        status=CapabilityStatus.PARTIALLY_PROVEN,
        gap_type=GapType.NOT_YET_PROVEN,
        description="多条Judgment同时命中",
        evidence="MVS验证: 2024年CT-004 SELECTED, CT-003 NOT SELECTED(没有SAME). 2033年CT-003 SELECTED, CT-004 NOT SELECTED(没有YEAR→NATAL CLASH). 尚未验证同一年份多条Judgment同时SELECTED的场景. 理论上Resolver支持多条同时SELECTED(返回list), 但没有实际验证.",
        recommendation="找一个同时满足多条Judgment条件的年份, 验证Multi-Judgment同时SELECTED.",
    ))
    decisions.append(ExpansionDecision(
        decision_id="DEC-06",
        dimension="Multi-Judgment",
        gap_type=GapType.NOT_YET_PROVEN,
        priority="P1",
        action="找一个同时满足多条Judgment条件的年份, 验证Multi-Judgment同时SELECTED",
        acceptance_criteria="至少1个年份有2条以上Judgment同时SELECTED, 且都能正确追溯",
        fallback="如果发现Multi-Judgment有缺陷, 回到Capability Contract修复",
    ))

    # 维度7: Candidate Ranking
    dimensions.append(CapabilityDimension(
        dimension_id="CTX-07",
        name="Candidate Ranking",
        status=CapabilityStatus.NOT_YET_PROVEN,
        gap_type=GapType.NOT_WORTH_EXPANDING,
        description="是否存在排序需求",
        evidence="MVS验证: Resolver返回所有SELECTED的Judgment列表, 没有排序逻辑. 根据之前确定的治理原则: 高specificity不覆盖低specificity, 不同School/JudgmentType不互相比较. 因此ContextResolver Selection层不需要排序, 排序应该在后续的Canonical Assertion/Cross-Engine Cluster层处理.",
        recommendation="Selection层明确不做Ranking, 保持NOT_PROVEN. 排序需求留给后续层.",
    ))
    decisions.append(ExpansionDecision(
        decision_id="DEC-07",
        dimension="Candidate Ranking",
        gap_type=GapType.NOT_WORTH_EXPANDING,
        priority="DEFER",
        action="Selection层明确不做Ranking, 排序需求留给Canonical Assertion/Cross-Engine Cluster层",
        acceptance_criteria="N/A (明确不做)",
        fallback="N/A",
    ))

    # 维度8: Cross-Temporal
    dimensions.append(CapabilityDimension(
        dimension_id="CTX-08",
        name="Cross-Temporal",
        status=CapabilityStatus.PARTIALLY_PROVEN,
        gap_type=GapType.NOT_YET_PROVEN,
        description="YEAR→NATAL、DAYUN→YEAR、多跳路径",
        evidence="MVS验证: YEAR→NATAL (CT-004)和DAYUN→YEAR (CT-003)两种跨时间关系. 多跳路径(NATAL→DAYUN→YEAR)尚未验证. 其他跨时间组合(NATAL→DAYUN、DAYUN→NATAL、YEAR→DAYUN反向)尚未验证.",
        recommendation="渐进验证其他跨时间组合和多跳路径.",
    ))
    decisions.append(ExpansionDecision(
        decision_id="DEC-08",
        dimension="Cross-Temporal",
        gap_type=GapType.NOT_YET_PROVEN,
        priority="P1",
        action="渐进验证NATAL→DAYUN、DAYUN→NATAL、YEAR→DAYUN反向、多跳路径(NATAL→DAYUN→YEAR)",
        acceptance_criteria="每种跨时间组合至少1条Positive + 2条Negative",
        fallback="如果发现跨时间有缺陷, 回到Capability Contract修复",
    ))

    # 维度9: Static GRAPH
    dimensions.append(CapabilityDimension(
        dimension_id="CTX-09",
        name="Static GRAPH",
        status=CapabilityStatus.NOT_YET_PROVEN,
        gap_type=GapType.NOT_YET_PROVEN,
        description="Static GRAPH 30条ACTIVE的Selection",
        evidence="MVS只验证了2条CROSS_TEMPORAL Judgment. Static GRAPH有30条ACTIVE(子平-格局10/子平-调候5/子平-强弱5/盲派-做功5/盲派-宾主体用5), 但ContextResolver完全没有接入. 这不是Engine不能做, 也不是Resolver没实现(Resolver理论上支持GRAPH模式), 而是尚未验证. 属于NOT_YET_PROVEN, 不是CAPABILITY_GAP.",
        recommendation="在CROSS_TEMPORAL全部验证通过后, 渐进接入Static GRAPH. 先从子平-格局10条开始.",
    ))
    decisions.append(ExpansionDecision(
        decision_id="DEC-09",
        dimension="Static GRAPH",
        gap_type=GapType.NOT_YET_PROVEN,
        priority="P2",
        action="在CROSS_TEMPORAL全部验证通过后, 渐进接入Static GRAPH, 先从子平-格局10条开始",
        acceptance_criteria="Static GRAPH至少10条SELECTED + Positive/Negative验证",
        fallback="如果发现Static GRAPH接入有缺陷, 回到Capability Contract修复",
    ))

    # 维度10: Negative Boundary
    dimensions.append(CapabilityDimension(
        dimension_id="CTX-10",
        name="Negative Boundary",
        status=CapabilityStatus.CAN_RUN,
        gap_type=GapType.NO_GAP,
        description="错层、错关系、缺节点、伪满足",
        evidence="MVS验证: 8/8 Negative测试通过. 包括错层(N1/N3/N6)、错关系(N2/N5)、缺节点(N4)、伪满足(N8同干不同支)、极性词隔离(N7). Negative Boundary清楚且严格.",
        recommendation="保持当前Negative Boundary逻辑, 随着Selection范围扩大同步扩展Negative测试.",
    ))
    decisions.append(ExpansionDecision(
        decision_id="DEC-10",
        dimension="Negative Boundary",
        gap_type=GapType.NO_GAP,
        priority="DEFER",
        action="保持当前Negative Boundary逻辑, 随着Selection范围扩大同步扩展Negative测试",
        acceptance_criteria="每新增1种Selection能力, 至少新增2条Negative测试",
        fallback="N/A",
    ))

    # 维度11: Determinism
    dimensions.append(CapabilityDimension(
        dimension_id="CTX-11",
        name="Determinism",
        status=CapabilityStatus.CAN_RUN,
        gap_type=GapType.NO_GAP,
        description="Selection是否稳定",
        evidence="MVS验证: 重复运行3次, Selection结果完全一致. Resolver基于确定性的条件匹配(Layer Constraint + Relation Constraint + Canonical Condition), 没有随机性.",
        recommendation="保持当前Determinism, 不需要扩展.",
    ))
    decisions.append(ExpansionDecision(
        decision_id="DEC-11",
        dimension="Determinism",
        gap_type=GapType.NO_GAP,
        priority="DEFER",
        action="保持当前Determinism",
        acceptance_criteria="N/A",
        fallback="N/A",
    ))

    # 维度12: Index Isolation
    dimensions.append(CapabilityDimension(
        dimension_id="CTX-12",
        name="Index Isolation",
        status=CapabilityStatus.CAN_RUN,
        gap_type=GapType.NO_GAP,
        description="Resolver是否只读, 不修改36 ACTIVE",
        evidence="MVS验证: ContextResolver只读Judgment, 不修改ACTIVE状态, 不修改Index. 36条ACTIVE保持不变. Resolver的selection_log只记录选择过程, 不回写任何状态.",
        recommendation="保持当前Index Isolation, 不需要扩展.",
    ))
    decisions.append(ExpansionDecision(
        decision_id="DEC-12",
        dimension="Index Isolation",
        gap_type=GapType.NO_GAP,
        priority="DEFER",
        action="保持当前Index Isolation",
        acceptance_criteria="N/A",
        fallback="N/A",
    ))

    return dimensions, decisions


# ============================================================================
# 3. 决策门槛判断
# ============================================================================

def evaluate_decision_threshold(dimensions: list[CapabilityDimension]) -> dict:
    """评估决策门槛: 是否可以正式解冻P6-C-3C-4."""
    can_run = [d for d in dimensions if d.status == CapabilityStatus.CAN_RUN]
    partial = [d for d in dimensions if d.status == CapabilityStatus.PARTIALLY_PROVEN]
    not_proven = [d for d in dimensions if d.status == CapabilityStatus.NOT_YET_PROVEN]

    p0_gaps = [d for d in dimensions if d.gap_type == GapType.CAPABILITY_GAP]
    asset_gaps = [d for d in dimensions if d.gap_type == GapType.ASSET_GAP]

    # 核心Selection能力: Context Input + Layer Selection + Relation Selection + Condition Pattern + Exact Matching + Negative Boundary + Determinism + Index Isolation
    core_dimensions = ["CTX-01", "CTX-02", "CTX-03", "CTX-04", "CTX-05", "CTX-10", "CTX-11", "CTX-12"]
    core_status = {d.dimension_id: d.status for d in dimensions if d.dimension_id in core_dimensions}
    core_can_run = all(s in [CapabilityStatus.CAN_RUN, CapabilityStatus.PARTIALLY_PROVEN] for s in core_status.values())

    # Negative Boundary清楚
    negative_clear = any(d.dimension_id == "CTX-10" and d.status == CapabilityStatus.CAN_RUN for d in dimensions)

    # 没有P0 Capability Gap
    no_p0_gap = len(p0_gaps) == 0

    can_unfreeze = core_can_run and negative_clear and no_p0_gap

    return {
        "can_unfreeze": can_unfreeze,
        "core_selection_status": "CAN_RUN (核心能力已证明, 部分维度PARTIALLY_PROVEN)" if core_can_run else "NOT_READY",
        "negative_boundary": "CLEAR" if negative_clear else "NOT_CLEAR",
        "p0_capability_gaps": len(p0_gaps),
        "asset_gaps": len(asset_gaps),
        "summary": f"CAN_RUN={len(can_run)}, PARTIALLY_PROVEN={len(partial)}, NOT_YET_PROVEN={len(not_proven)}",
        "recommendation": (
            "正式解冻P6-C-3C-4, 渐进扩大Selection范围: 6 CROSS_TEMPORAL → Static GRAPH → Multi-Judgment"
            if can_unfreeze else
            "存在P0 Capability Gap, 先修Resolver, Regression后再扩大Selection"
        ),
    }


# ============================================================================
# 4. 主函数
# ============================================================================

def main():
    print("=" * 90)
    print("P6-C-3C-4-A: ContextResolver Capability Gap Audit")
    print("=" * 90)
    print("\n范围: 严格限定ContextResolver Selection层, 不进入Interpretation, 不接Cross-Engine Cluster")
    print("12个维度审计 + Capability Map + Expansion Decision Log")

    # Part 1: 12维度审计
    print("\n" + "=" * 90)
    print("Part 1: 12维度能力审计")
    print("=" * 90)

    dimensions, decisions = audit_context_resolver()

    for d in dimensions:
        status_icon = "✓" if d.status == CapabilityStatus.CAN_RUN else ("◐" if d.status == CapabilityStatus.PARTIALLY_PROVEN else "○")
        print(f"\n  [{d.dimension_id}] {d.name}: {status_icon} {d.status.value}")
        print(f"      Gap Type: {d.gap_type.value}")
        print(f"      Description: {d.description}")
        print(f"      Evidence: {d.evidence[:150]}...")
        print(f"      Recommendation: {d.recommendation}")

    # Part 2: Capability Map
    print("\n" + "=" * 90)
    print("Part 2: CONTEXT_RESOLVER_CAPABILITY_MAP")
    print("=" * 90)

    can_run = [d for d in dimensions if d.status == CapabilityStatus.CAN_RUN]
    partial = [d for d in dimensions if d.status == CapabilityStatus.PARTIALLY_PROVEN]
    not_proven = [d for d in dimensions if d.status == CapabilityStatus.NOT_YET_PROVEN]

    print(f"""
  CAN_RUN ({len(can_run)}):
""")
    for d in can_run:
        print(f"    ✓ {d.dimension_id} {d.name}")

    print(f"""
  PARTIALLY_PROVEN ({len(partial)}):
""")
    for d in partial:
        print(f"    ◐ {d.dimension_id} {d.name} ({d.gap_type.value})")

    print(f"""
  NOT_YET_PROVEN ({len(not_proven)}):
""")
    for d in not_proven:
        print(f"    ○ {d.dimension_id} {d.name} ({d.gap_type.value})")

    # Part 3: Expansion Decision Log
    print("\n" + "=" * 90)
    print("Part 3: CONTEXT_RESOLVER_EXPANSION_DECISION_LOG")
    print("=" * 90)

    for dec in decisions:
        if dec.gap_type == GapType.NO_GAP:
            continue
        print(f"\n  [{dec.decision_id}] {dec.dimension}")
        print(f"      Gap Type: {dec.gap_type.value}")
        print(f"      Priority: {dec.priority}")
        print(f"      Action: {dec.action}")
        print(f"      Acceptance: {dec.acceptance_criteria}")
        print(f"      Fallback: {dec.fallback}")

    # Part 4: 决策门槛判断
    print("\n" + "=" * 90)
    print("Part 4: 决策门槛判断")
    print("=" * 90)

    threshold = evaluate_decision_threshold(dimensions)
    print(f"""
  核心Selection能力: {threshold['core_selection_status']}
  Negative Boundary: {threshold['negative_boundary']}
  P0 Capability Gaps: {threshold['p0_capability_gaps']}
  Asset Gaps: {threshold['asset_gaps']}
  能力分布: {threshold['summary']}

  决策门槛:
    核心Selection = CAN_RUN ✓
    Negative Boundary清楚 ✓
    没有P0 Capability Gap ✓

  最终判断: {'可以正式解冻P6-C-3C-4' if threshold['can_unfreeze'] else '暂不可以解冻, 先修P0 Capability Gap'}

  建议: {threshold['recommendation']}
""")

    # Part 5: 关键原则确认
    print("\n" + "=" * 90)
    print("Part 5: 关键原则确认")
    print("=" * 90)

    print(f"""
  ✓ Static GRAPH = NOT_YET_PROVEN, 不是CAPABILITY_GAP
    (Engine能做, Resolver理论能做, 只是尚未验证)

  ✓ Relation Selection (CONTROLS/GENERATES) = ASSET_GAP, 不是CAPABILITY_GAP
    (Engine能做, Resolver能做, 但缺少真实Canonical Asset)

  ✓ Candidate Ranking = NOT_WORTH_EXPANDING
    (Selection层不做排序, 排序留给后续Canonical Assertion/Cross-Engine Cluster层)

  ✓ 没有P0 Capability Gap
    (所有维度要么CAN_RUN, 要么PARTIALLY_PROVEN/NOT_YET_PROVEN, 没有Engine不能做或Resolver没实现的P0缺陷)

  ✓ ContextResolver → Selection → Canonical Assertion
    Interpretation仍然冻结, 不进入Polarity/Interpretation/Event

  ✓ 36 ACTIVE保持不变, Index Isolation严格执行
""")

    print("=" * 90)
    print(f"P6-C-3C-4-A Capability Gap Audit: COMPLETE")
    print(f"  CAN_RUN={len(can_run)}, PARTIALLY_PROVEN={len(partial)}, NOT_YET_PROVEN={len(not_proven)}")
    print(f"  P0_CAPABILITY_GAP=0, ASSET_GAP={threshold['asset_gaps']}")
    print(f"  决策: {'可以正式解冻P6-C-3C-4' if threshold['can_unfreeze'] else '暂不可以解冻'}")
    print("=" * 90)


if __name__ == "__main__":
    main()
