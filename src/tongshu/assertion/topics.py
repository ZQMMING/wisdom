# -*- coding: utf-8 -*-
"""核心主题断言Producer (P3 Topics Layer).

每个主题Producer整合多体系证据(紫微/盲派/河洛/八字), 输出主题断言.
- CareerAssertionProducer: 事业
- WealthAssertionProducer: 财运
- MarriageAssertionProducer: 婚姻
- HealthAssertionProducer: 健康

契约: 实现 AssertionProducer 协议.
多体系收敛时置信可达 SUPPORTED (>=2体系一致); 单体系最高 LIKELY.
"""
from __future__ import annotations

from tongshu.assertion.contract import (
    Assertion,
    AssertionInput,
    AssertionType,
    AuditFlag,
    Confidence,
    Direction,
    EvidenceRef,
    StateKind,
    insufficient_evidence,
)
from tongshu.assertion.systems import (
    ZiweiAssertionProducer,
    BlindAssertionProducer,
    HeluoAssertionProducer,
    ZipingAssertionProducer,
)
from tongshu.assertion.advice_optimizer import get_system_weight


def _aggregate_directions_weighted(assertions: list[Assertion], topic: str) -> tuple[Direction, float, float]:
    """V8: 加权聚合多体系方向.

    用SYSTEM_WEIGHTS对每个体系的direction加权, 替代简单多数投票.
    返回(综合方向, 加权吉分, 加权凶分).
    """
    pos_score = 0.0
    neg_score = 0.0
    for a in assertions:
        w = get_system_weight(a.subject, topic)
        if a.direction == Direction.POSITIVE:
            pos_score += w
        elif a.direction == Direction.NEGATIVE:
            neg_score += w
    if pos_score > neg_score:
        return Direction.POSITIVE, pos_score, neg_score
    if neg_score > pos_score:
        return Direction.NEGATIVE, pos_score, neg_score
    return Direction.NEUTRAL, pos_score, neg_score


def _detect_conflict(assertions: list[Assertion], topic: str) -> tuple[AuditFlag, ...]:
    """V11: 检测多体系方向相反 — 反方向=算法错误, 生成审计信号(不进结论).

    方法论: 互补不比较. 各体系同源, 对同一主题根本判断应内在一致.
    若出现正负方向同时存在, 非"冲突", 而是某个引擎算法/维度有误, 触发审计.
    """
    pos_systems = [
        f"{a.subject}: {a.direction.value}"
        for a in assertions if a.direction == Direction.POSITIVE
    ]
    neg_systems = [
        f"{a.subject}: {a.direction.value}"
        for a in assertions if a.direction == Direction.NEGATIVE
    ]
    if pos_systems and neg_systems:
        return (AuditFlag(
            topic=topic,
            conflicting_engines=tuple(pos_systems + neg_systems),
            hypothesis=(
                "多体系在同一主题方向相反(互补体系应内在一致), "
                "疑为其中一个引擎算法有误或维度未对齐"
            ),
            action="进入该引擎算法审计",
        ),)
    return ()


def _confidence_from_weighted(pos: float, neg: float, total: int, topic: str) -> Confidence:
    """V8/V11: 加权置信度.

    基于体系权重收敛度决定置信:
    - >=2体系权重且一致→SUPPORTED
    - 单体系权重主导→LIKELY
    - 正负均有→V11已废弃CONFLICTED, 由_detect_conflict拦截生成审计信号,
      此处仅防御性兜底为LIKELY(不确信), 避免反方向被当作正常置信消费.
    """
    if total < 2:
        return Confidence.LIKELY
    if pos > 0 and neg == 0 and pos >= 1.4:  # 权重和>=1.4 ≈ 至少2个中高权重体系一致
        return Confidence.SUPPORTED
    if neg > 0 and pos == 0 and neg >= 1.4:
        return Confidence.SUPPORTED
    return Confidence.LIKELY


class _BaseTopicProducer:
    """主题Producer基类. 子类指定subject和主题关键词."""

    subject: str = ""
    _topic_keywords: tuple[str, ...] = ()

    def __init__(self) -> None:
        self._ziwei = ZiweiAssertionProducer()
        self._blind = BlindAssertionProducer()
        self._heluo = HeluoAssertionProducer()
        self._ziping = ZipingAssertionProducer()

    def _run_systems(self, inp, chart, context) -> list[Assertion]:
        """V8: 运行四个体系Producer(子平/盲派/紫微/河洛), 收集非拒断断言."""
        results = []
        for producer in (self._ziping, self._ziwei, self._blind, self._heluo):
            try:
                a = producer.produce(inp, chart, context)
                if not a.abstain and a.assertion_type != AssertionType.INSUFFICIENT_EVIDENCE:
                    results.append(a)
            except Exception:
                pass
        return results

    def produce(self, inp: AssertionInput, chart, context: dict | None = None) -> Assertion:
        context = context or {}
        if chart is None:
            return insufficient_evidence(self.subject, "chart is None")

        assertions = self._run_systems(inp, chart, context)
        if not assertions:
            return insufficient_evidence(self.subject, "no system signals")

        topic = self.subject
        # V11: 反方向=算法错误, 生成审计信号, 不进结论
        audit_flags = _detect_conflict(assertions, topic)
        if audit_flags:
            # 互补不比较: 反方向时不靠权重投票硬决方向(那是"比较"),
            # 而是降级为待审计, 由审计流程定位算法错误后修复
            direction = Direction.NEUTRAL
            pos = neg = 0.0
            confidence = Confidence.LIKELY
        else:
            # 一致收敛: 多引擎方向一致, 加权聚合(反映体系本位权重) + 置信增强
            direction, pos, neg = _aggregate_directions_weighted(assertions, topic)
            confidence = _confidence_from_weighted(pos, neg, len(assertions), topic)

        # 主题特定机制描述
        mechanism = self._topic_mechanism(assertions, context)

        # V4: 画险趋吉建议 — 基于多体系方向和主题
        advice = self._topic_advice(direction, assertions, context)

        # 证据链
        evidence = tuple(
            EvidenceRef(
                system=a.subject,
                signal_ref=a.mechanism[:80],
                agrees=(a.direction == direction) if direction != Direction.NEUTRAL else None,
            )
            for a in assertions
        )

        # V10: 主题断言继承单体系古籍依据(交叉验证)
        classical_refs = []
        for a in assertions:
            for ref in (a.classical_refs or ()):
                if ref and ref not in classical_refs:
                    classical_refs.append(ref)
        classical_refs = classical_refs[:5]

        return Assertion(
            subject=self.subject,
            assertion_type=AssertionType.CONDITIONAL_EVENT,
            state=StateKind.EXPANSION if direction == Direction.POSITIVE else (
                StateKind.CONTRACTION if direction == Direction.NEGATIVE else StateKind.STABLE),
            direction=direction,
            mechanism=mechanism,
            time="; ".join(a.time for a in assertions if a.time)[:200],
            conditions=(f"多体系{len(assertions)}个信号聚合",),
            evidence=evidence,
            confidence=confidence,
            abstain=(confidence in (Confidence.WEAK, Confidence.INSUFFICIENT_EVIDENCE)),
            advice=advice,
            classical_refs=tuple(classical_refs),
            audit_flags=audit_flags,
        )

    def _topic_mechanism(self, assertions: list[Assertion], context: dict) -> str:
        """子类覆盖: 主题特定机制描述."""
        return f"{self.subject}主题: 多体系聚合(吉{sum(1 for a in assertions if a.direction==Direction.POSITIVE)}/凶{sum(1 for a in assertions if a.direction==Direction.NEGATIVE)})"

    def _topic_advice(self, direction: Direction, assertions: list[Assertion], context: dict) -> str:
        """V7: 聚合单体系生产者的advice内容, 用advice_optimizer优化.

        策略:
        1. 收集所有单体系生产者的advice(非空)
        2. 转换为AdviceItem, 按体系权重分配
        3. 用advice_optimizer优化(去重/冲突检测/交叉验证/排序)
        4. 输出优化后的文本
        5. 兜底: 模板化通用建议
        """
        from tongshu.assertion.advice_optimizer import (
            AdviceItem, AdviceSource, AdviceCategory, optimize_advice, make_advice,
        )

        # 体系→来源映射
        system_source_map = {
            "ziwei": AdviceSource.ZIWEI,
            "blind": AdviceSource.BLIND,
            "heluo": AdviceSource.HELUO,
            "ziping": AdviceSource.ZIPING,
        }
        # 主题→类别映射
        topic_category_map = {
            "career": AdviceCategory.CAREER,
            "wealth": AdviceCategory.WEALTH,
            "marriage": AdviceCategory.MARRIAGE,
            "health": AdviceCategory.HEALTH,
        }
        category = topic_category_map.get(self.subject, AdviceCategory.ACTION)

        # 1. 收集单体系advice
        advice_items: list[AdviceItem] = []
        for a in assertions:
            if a.advice:
                source = system_source_map.get(a.subject, AdviceSource.HELUO)
                # 体系方向决定建议方向
                item_direction = a.direction.value if a.direction else "neutral"
                advice_items.append(make_advice(
                    content=a.advice,
                    source=source,
                    category=category,
                    priority=4,
                    direction=item_direction,
                    confidence=0.6,
                ))

        # 2. 如果有单体系advice, 用optimizer优化
        if advice_items:
            optimized = optimize_advice(advice_items, topic=self.subject, max_items=4)
            if optimized["text"]:
                return optimized["text"]

        # 3. 兜底: 模板化通用建议
        if direction == Direction.POSITIVE:
            return f"{self.subject}方向偏吉, 可积极把握机遇"
        elif direction == Direction.NEGATIVE:
            return f"{self.subject}方向偏凶, 宜谨慎避险, 避免重大决策"
        return f"{self.subject}方向中性, 稳扎稳打为宜"


# ═══════════════════════════════════════════════════════════════════
# 事业断言Producer
# ═══════════════════════════════════════════════════════════════════

class CareerAssertionProducer(_BaseTopicProducer):
    """事业断言Producer. subject=career.

    整合紫微官禄宫/盲派官杀/河洛事业卦.
    """
    subject = "career"
    _topic_keywords = ("官", "职", "事业", "工作", "升迁")

    def _topic_mechanism(self, assertions, context) -> str:
        zw = next((a for a in assertions if a.subject == "ziwei"), None)
        blind = next((a for a in assertions if a.subject == "blind"), None)
        parts = []
        if zw:
            parts.append(f"紫微命宫/官禄方向: {zw.direction.value}")
        if blind:
            parts.append(f"盲派官杀引动: {blind.direction.value}")
        return f"事业主题: {'；'.join(parts) if parts else '多体系聚合'}"

    def _topic_advice(self, direction, assertions, context) -> str:
        """V4: 事业主题画险趋吉建议."""
        if direction == Direction.POSITIVE:
            return "事业方向偏吉, 可积极争取晋升/跳槽/创业机遇, 主动展现能力"
        elif direction == Direction.NEGATIVE:
            return "事业方向偏凶, 宜守成避险, 避免重大变动/创业/跳槽, 稳固现有职位"
        return "事业方向中性, 稳扎稳打积累实力, 不宜冒进也不宜消极"


# ═══════════════════════════════════════════════════════════════════
# 财运断言Producer
# ═══════════════════════════════════════════════════════════════════

class WealthAssertionProducer(_BaseTopicProducer):
    """财运断言Producer. subject=wealth.

    整合紫微财帛宫/盲派财星/河洛财运卦.
    """
    subject = "wealth"
    _topic_keywords = ("财", "钱", "富", "贫", "薪")

    def _topic_mechanism(self, assertions, context) -> str:
        zw = next((a for a in assertions if a.subject == "ziwei"), None)
        heluo = next((a for a in assertions if a.subject == "heluo"), None)
        parts = []
        if zw:
            parts.append(f"紫微财帛方向: {zw.direction.value}")
        if heluo:
            parts.append(f"河洛流年卦财运: {heluo.direction.value}")
        return f"财运主题: {'；'.join(parts) if parts else '多体系聚合'}"

    def _topic_advice(self, direction, assertions, context) -> str:
        """V4: 财运主题画险趋吉建议."""
        if direction == Direction.POSITIVE:
            return "财运方向偏吉, 可把握投资/增收机遇, 但仍需理性规划, 忌盲目跟风"
        elif direction == Direction.NEGATIVE:
            return "财运方向偏凶, 宜保守理财, 避免重大投资/借贷/担保, 守住现有财富"
        return "财运方向中性, 量入为出稳健理财, 不宜大额投资也不必过度保守"


# ═══════════════════════════════════════════════════════════════════
# 婚姻断言Producer
# ═══════════════════════════════════════════════════════════════════

class MarriageAssertionProducer(_BaseTopicProducer):
    """婚姻断言Producer. subject=marriage.

    整合紫微夫妻宫/盲派婚姻宫/河洛婚姻卦.
    """
    subject = "marriage"
    _topic_keywords = ("婚", "妻", "夫", "嫁", "娶", "感情")

    def _topic_mechanism(self, assertions, context) -> str:
        zw = next((a for a in assertions if a.subject == "ziwei"), None)
        blind = next((a for a in assertions if a.subject == "blind"), None)
        parts = []
        if zw:
            parts.append(f"紫微夫妻宫方向: {zw.direction.value}")
        if blind:
            parts.append(f"盲派婚姻引动: {blind.direction.value}")
        return f"婚姻主题: {'；'.join(parts) if parts else '多体系聚合'}"

    def _topic_advice(self, direction, assertions, context) -> str:
        """V4: 婚姻主题画险趋吉建议."""
        if direction == Direction.POSITIVE:
            return "婚姻方向偏吉, 利于婚恋/订婚/结婚, 主动经营感情, 把握良缘"
        elif direction == Direction.NEGATIVE:
            return "婚姻方向偏凶, 宜谨慎处理感情问题, 避免冲动决策/争吵, 多沟通包容"
        return "婚姻方向中性, 顺其自然经营感情, 不宜急于推进也不宜消极等待"


# ═══════════════════════════════════════════════════════════════════
# 健康断言Producer
# ═══════════════════════════════════════════════════════════════════

class HealthAssertionProducer(_BaseTopicProducer):
    """健康断言Producer. subject=health.

    整合紫微疾厄宫/盲派疾病/河洛健康卦.
    """
    subject = "health"
    _topic_keywords = ("病", "疾", "医", "健康", "伤")

    def _topic_mechanism(self, assertions, context) -> str:
        zw = next((a for a in assertions if a.subject == "ziwei"), None)
        blind = next((a for a in assertions if a.subject == "blind"), None)
        parts = []
        if zw:
            parts.append(f"紫微疾厄宫方向: {zw.direction.value}")
        if blind:
            parts.append(f"盲派疾病引动: {blind.direction.value}")
        # 健康主题方向反转: 体系凶=健康风险(negative), 体系吉=健康良好(positive)
        return f"健康主题: {'；'.join(parts) if parts else '多体系聚合'}"

    def _topic_advice(self, direction, assertions, context) -> str:
        """V4: 健康主题画险趋吉建议."""
        if direction == Direction.POSITIVE:
            return "健康方向良好, 保持规律作息/运动/饮食, 可积极锻炼提升体质"
        elif direction == Direction.NEGATIVE:
            return "健康方向偏凶, 需特别注意身体信号, 定期体检, 避免劳累/熬夜/不良习惯"
        return "健康方向中性, 维持良好生活习惯, 关注身体变化, 有不适及时就医"


__all__ = [
    "CareerAssertionProducer",
    "WealthAssertionProducer",
    "MarriageAssertionProducer",
    "HealthAssertionProducer",
]
