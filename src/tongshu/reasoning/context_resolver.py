"""P4-C Context Resolver - 上下文评估器.

这是direction唯一产生的地方.
输入: SemanticSignal[] + SignalContext(本命+大运+流年+流月+流日+宫位+卦位+体用)
输出: CanonicalAssertion[] (direction=supportive/caution/neutral)

硬原则:
  1. ContextResolver不能凭空创造事实
  2. 只能基于SemanticSignal + Temporal Context + Structural Context产生Assertion
  3. 多Signal可以语义聚合为一个Assertion(P4第一次允许压缩)
  4. direction是上下文状态, 不是术语属性
  5. 禁止从旧的direction/polarity/confidence恢复direction

P4阶段: 先建立框架和基础评估逻辑, 具体规则逐步完善.
评估策略:
  - 基于signal_type和atom_id的语义聚合
  - 基于temporal_scope的时间维度分类
  - 基于context中的本命结构信息调整direction
  - intensity基于signal数量和上下文强度评估
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Optional

from .semantic_signal import SemanticSignal, SignalStatus
from .signal_context import SignalContext, AssertionDirection
from .assertion import (
    CanonicalAssertion,
    AssertionDomain,
    make_assertion_id,
    validate_assertion_contract,
)

log = logging.getLogger(__name__)


# 语义聚合规则: atom_id前缀 → (domain, semantic)
# 这是P4的基础聚合规则, 后续可以扩展为更复杂的规则引擎
SEMANTIC_AGGREGATION_RULES = {
    # OUTPUT类 → 事业/成长
    "OUTPUT": ("CAREER", "OUTPUT_ACTIVATION"),
    "EXPRESSION": ("CAREER", "EXPRESSION_ENHANCEMENT"),
    "CREATIVITY": ("GROWTH", "CREATIVITY_STIMULATION"),
    "VISIBILITY": ("CAREER", "VISIBILITY_INCREASE"),
    "AUTONOMY": ("GROWTH", "AUTONOMY_EXPANSION"),
    # SUPPORT类 → 资源/稳定
    "SUPPORT": ("FINANCE", "RESOURCE_SUPPORT"),
    "STABILITY": ("FAMILY", "STABILITY_STRENGTHEN"),
    "RESOURCE": ("FINANCE", "RESOURCE_AVAILABILITY"),
    "ENDURANCE": ("GROWTH", "ENDURANCE_BUILDUP"),
    "ABUNDANCE": ("FINANCE", "ABUNDANCE_POTENTIAL"),
    "WEALTH": ("FINANCE", "WEALTH_ACCUMULATION"),
    "ASSET": ("FINANCE", "ASSET_BUILDUP"),
    # CONSTRAINT类 → 决策/事业
    "CONSTRAINT": ("DECISION", "CONSTRAINT_AWARENESS"),
    "DISCIPLINE": ("GROWTH", "DISCIPLINE_REQUIRED"),
    "RULE": ("CAREER", "RULE_NAVIGATION"),
    "RESPONSIBILITY": ("CAREER", "RESPONSIBILITY_INCREASE"),
    # CHANGE类 → 迁移/事业
    "CHANGE": ("MIGRATION", "CHANGE_TRANSITION"),
    "TRANSFORMATION": ("CAREER", "TRANSFORMATION_PHASE"),
    "VOLATILITY": ("DECISION", "VOLATILITY_MANAGEMENT"),
    "DISRUPTION": ("MIGRATION", "DISRUPTION_EVENT"),
    # REFLECTION类 → 成长/决策
    "REFLECTION": ("GROWTH", "REFLECTION_PERIOD"),
    "AWARENESS": ("GROWTH", "AWARENESS_EXPANSION"),
    "INSIGHT": ("GROWTH", "INSIGHT_DEVELOPMENT"),
    "CONTEMPLATION": ("GROWTH", "CONTEMPLATION_PHASE"),
    # RELATION类 → 感情/家庭
    "RELATION": ("RELATIONSHIP", "RELATIONSHIP_DYNAMICS"),
    "SOCIAL": ("RELATIONSHIP", "SOCIAL_CONNECTION"),
    "CONNECTION": ("RELATIONSHIP", "CONNECTION_BUILDING"),
    "PARTNERSHIP": ("RELATIONSHIP", "PARTNERSHIP_DEVELOPMENT"),
    "HARMONY": ("RELATIONSHIP", "HARMONY_POTENTIAL"),
    "ATTRACT": ("RELATIONSHIP", "ATTRACT_OPPORTUNITY"),
    # ACTION类 → 事业/决策
    "ACTION": ("CAREER", "ACTION_INITIATIVE"),
    "EXECUTION": ("CAREER", "EXECUTION_FOCUS"),
    "INITIATIVE": ("GROWTH", "INITIATIVE_TAKING"),
    "MOVEMENT": ("MIGRATION", "MOVEMENT_OPPORTUNITY"),
    # HEALTH类 → 健康(仅生活节奏提醒)
    "HEALTH_RISK": ("HEALTH", "HEALTH_RISK_AWARENESS"),
    "CAUTION": ("HEALTH", "CAUTION_REQUIRED"),
    "PREVENTION": ("HEALTH", "PREVENTION_FOCUS"),
    "VULNERABILITY": ("HEALTH", "VULNERABILITY_NOTICE"),
    # RELATIONSHIP RISK类
    "RELATIONSHIP_RISK": ("RELATIONSHIP", "RELATIONSHIP_RISK"),
    "TENSION": ("RELATIONSHIP", "TENSION_MANAGEMENT"),
    "CONFLICT": ("RELATIONSHIP", "CONFLICT_NAVIGATION"),
}


class ContextResolver:
    """P4 Context Resolver - 上下文评估器.

    接收SemanticSignal[] + SignalContext, 产生CanonicalAssertion[].

    P4阶段: 基础评估逻辑, 基于语义聚合规则.
    后续: 更复杂的上下文评估(本命结构+大运+流年+流月+流日+宫位).
    """

    def __init__(self):
        self._aggregation_rules = SEMANTIC_AGGREGATION_RULES

    def resolve(
        self,
        signals: list[SemanticSignal],
        context: Optional[SignalContext] = None,
    ) -> list[CanonicalAssertion]:
        """将SemanticSignal[] + Context解析为CanonicalAssertion[].

        Args:
            signals: SemanticSignal列表(只处理READY状态的)
            context: SignalContext(本命+大运+流年+流月+流日+宫位)

        Returns:
            CanonicalAssertion列表
        """
        # 只处理READY信号
        ready_signals = [s for s in signals if s.status == SignalStatus.READY.value]
        log.info("ContextResolver: %d ready signals out of %d total", len(ready_signals), len(signals))

        if not ready_signals:
            return []

        # 步骤1: 语义聚合 - 按(domain, semantic, temporal_scope)分组
        grouped = self._aggregate_signals(ready_signals)

        # 步骤2: 对每组产生Assertion
        assertions = []
        for key, group_signals in grouped.items():
            domain, semantic, temporal_scope = key
            assertion = self._build_assertion(
                case_id=group_signals[0].case_id,
                domain=domain,
                semantic=semantic,
                temporal_scope=temporal_scope,
                signals=group_signals,
                context=context,
            )
            if assertion:
                assertions.append(assertion)

        # 验证契约
        errors = validate_assertion_contract(assertions)
        if errors:
            for e in errors:
                log.error("Assertion contract violation: %s", e)

        log.info("ContextResolver: produced %d assertions from %d signals", len(assertions), len(ready_signals))
        return assertions

    def _aggregate_signals(
        self,
        signals: list[SemanticSignal],
    ) -> dict[tuple, list[SemanticSignal]]:
        """语义聚合: 按(domain, semantic, temporal_scope)分组.

        这是P4第一次允许压缩: 多个Signal可以聚合为一个Assertion.
        聚合基于atom_id的语义聚合规则.
        """
        grouped: dict[tuple, list[SemanticSignal]] = defaultdict(list)

        for sig in signals:
            atom_id = sig.atom_id
            # 查找聚合规则
            if atom_id in self._aggregation_rules:
                domain, semantic = self._aggregation_rules[atom_id]
            else:
                # 未匹配的atom, 使用GROWTH作为默认domain
                domain = "GROWTH"
                semantic = f"{atom_id}_SIGNAL"

            key = (domain, semantic, sig.temporal_scope)
            grouped[key].append(sig)

        return dict(grouped)

    def _build_assertion(
        self,
        case_id: str,
        domain: str,
        semantic: str,
        temporal_scope: str,
        signals: list[SemanticSignal],
        context: Optional[SignalContext],
    ) -> Optional[CanonicalAssertion]:
        """从一组Signal构建一个Assertion.

        direction评估逻辑(P4基础版):
          - 默认neutral
          - 如果signal_type包含SUPPORT/RESOURCE/OUTPUT等正面语义 → supportive
          - 如果signal_type包含CONSTRAINT/HEALTH_RISK/RELATIONSHIP_RISK等 → caution
          - 混合 → 根据数量和强度评估

        intensity评估:
          - 基于signal数量(2-4个→50-70, 5+个→70-90)
          - 基于上下文强度(后续完善)
        """
        if not signals:
            return None

        # direction评估
        direction = self._evaluate_direction(signals, context)

        # intensity评估
        intensity = self._evaluate_intensity(signals, context)

        # 收集来源信息
        source_signal_ids = [s.signal_id for s in signals]
        source_engines = list(set(s.engine for s in signals))
        source_rules = list(set(s.rule_id for s in signals))
        evidence_refs = list(set(s.evidence_ref for s in signals if s.evidence_ref))

        # 上下文摘要
        context_summary = {
            "signal_count": len(signals),
            "signal_types": list(set(s.signal_type for s in signals if s.signal_type)),
            "atom_ids": list(set(s.atom_id for s in signals)),
            "evaluation_method": "P4_basic_semantic_aggregation",
        }

        assertion_id = make_assertion_id(case_id, domain, semantic, temporal_scope)

        return CanonicalAssertion(
            assertion_id=assertion_id,
            case_id=case_id,
            domain=domain,
            semantic=semantic,
            direction=direction,
            intensity=intensity,
            temporal_scope=temporal_scope,
            source_signal_ids=source_signal_ids,
            source_engines=source_engines,
            source_rules=source_rules,
            context_summary=context_summary,
            evidence_refs=evidence_refs,
            status="P4_BASIC",  # P4基础版, 后续完善
        )

    def _evaluate_direction(
        self,
        signals: list[SemanticSignal],
        context: Optional[SignalContext],
    ) -> str:
        """评估direction(P4基础版).

        基于signal_type和atom_id的语义倾向:
          - supportive类: SUPPORT, RESOURCE, OUTPUT, ACTION, REFLECTION, RELATION(机会)
          - caution类: CONSTRAINT, HEALTH_RISK, RELATIONSHIP_RISK, VOLATILITY, DISRUPTION
          - 混合: 根据数量评估
        """
        supportive_types = {"SUPPORT", "RESOURCE", "OUTPUT", "ACTION", "REFLECTION", "MARRIAGE_OPPORTUNITY"}
        caution_types = {"CONSTRAINT", "HEALTH_RISK", "MARRIAGE_RISK", "VOLATILITY", "DISRUPTION"}

        supportive_count = 0
        caution_count = 0

        for sig in signals:
            sig_type = sig.signal_type or ""
            atom_id = sig.atom_id or ""

            # 检查signal_type
            if sig_type in supportive_types or any(t in sig_type for t in supportive_types):
                supportive_count += 1
            elif sig_type in caution_types or any(t in sig_type for t in caution_types):
                caution_count += 1
            # 检查atom_id
            elif atom_id in supportive_types:
                supportive_count += 1
            elif atom_id in caution_types:
                caution_count += 1

        total = supportive_count + caution_count
        if total == 0:
            return AssertionDirection.NEUTRAL.value

        # 简单多数评估(不是投票, 是语义倾向统计)
        ratio = supportive_count / total
        if ratio >= 0.6:
            return AssertionDirection.SUPPORTIVE.value
        elif ratio <= 0.4:
            return AssertionDirection.CAUTION.value
        else:
            return AssertionDirection.NEUTRAL.value

    def _evaluate_intensity(
        self,
        signals: list[SemanticSignal],
        context: Optional[SignalContext],
    ) -> int:
        """评估intensity(P4基础版).

        基于signal数量:
          - 1个: 30-40
          - 2-3个: 50-65
          - 4-6个: 65-80
          - 7+个: 80-90
        """
        count = len(signals)
        if count <= 1:
            return 35
        elif count <= 3:
            return 55
        elif count <= 6:
            return 70
        else:
            return 82

    def get_stats(self, assertions: list[CanonicalAssertion]) -> dict:
        """统计Assertion信息."""
        from collections import Counter
        by_domain = Counter(a.domain for a in assertions)
        by_direction = Counter(a.direction for a in assertions)
        by_temporal = Counter(a.temporal_scope for a in assertions)
        by_engine_coverage = Counter()
        for a in assertions:
            for eng in a.source_engines:
                by_engine_coverage[eng] += 1

        return {
            "total": len(assertions),
            "by_domain": dict(by_domain),
            "by_direction": dict(by_direction),
            "by_temporal_scope": dict(by_temporal),
            "engine_coverage": dict(by_engine_coverage),
            "avg_intensity": sum(a.intensity for a in assertions) / len(assertions) if assertions else 0,
        }
