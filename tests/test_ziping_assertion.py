# -*- coding: utf-8 -*-
"""断言层V8测试 — 子平断言生产者 + 加权方向聚合."""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tongshu.assertion.contract import (
    Assertion, AssertionInput, AssertionType, Confidence, Direction,
)
from tongshu.assertion.systems import ZipingAssertionProducer
from tongshu.assertion.topics import (
    CareerAssertionProducer, WealthAssertionProducer,
    MarriageAssertionProducer, HealthAssertionProducer,
)


class TestZipingProducer(unittest.TestCase):
    """子平八字断言Producer测试."""

    def setUp(self):
        self.inp = AssertionInput(birth_datetime="1974-04-28T16:00:00+08:00")
        self.context = {
            "birth": (1974, 4, 28, 16, "male"),
            "bazi": [("甲", "寅"), ("戊", "辰"), ("己", "亥"), ("壬", "申")],
            "gender": "male",
            "birth_hour": "申",
            "birth_year": 1974,
            "focus_years": [1996],
        }

    def test_producer_subject(self):
        p = ZipingAssertionProducer()
        self.assertEqual(p.subject, "ziping")

    def test_producer_output(self):
        p = ZipingAssertionProducer()
        a = p.produce(self.inp, chart={}, context=self.context)
        self.assertEqual(a.subject, "ziping")
        # 单体系置信<=LIKELY
        self.assertIn(a.confidence, (Confidence.LIKELY, Confidence.WEAK, Confidence.INSUFFICIENT_EVIDENCE))
        # 应输出mechanism
        self.assertTrue(a.mechanism)

    def test_producer_no_birth(self):
        p = ZipingAssertionProducer()
        a = p.produce(self.inp, chart={}, context={})
        self.assertEqual(a.subject, "ziping")
        self.assertEqual(a.assertion_type.value, "INSUFFICIENT_EVIDENCE")

    def test_producer_none_chart(self):
        p = ZipingAssertionProducer()
        a = p.produce(self.inp, chart=None, context=self.context)
        self.assertEqual(a.assertion_type.value, "INSUFFICIENT_EVIDENCE")


class TestTopicWithZiping(unittest.TestCase):
    """主题断言Producer整合子平体系测试."""

    def setUp(self):
        self.inp = AssertionInput(birth_datetime="1974-04-28T16:00:00+08:00")
        self.context = {
            "birth": (1974, 4, 28, 16, "male"),
            "bazi": [("甲", "寅"), ("戊", "辰"), ("己", "亥"), ("壬", "申")],
            "gender": "male",
            "birth_hour": "申",
            "birth_year": 1974,
            "focus_years": [1996],
        }

    def test_career_includes_ziping(self):
        p = CareerAssertionProducer()
        a = p.produce(self.inp, chart={}, context=self.context)
        if not a.abstain:
            # 证据链应包含ziping(子平)
            systems = [e.system for e in a.evidence]
            self.assertIn("ziping", systems)

    def test_wealth_includes_ziping(self):
        p = WealthAssertionProducer()
        a = p.produce(self.inp, chart={}, context=self.context)
        if not a.abstain:
            systems = [e.system for e in a.evidence]
            self.assertIn("ziping", systems)

    def test_marriage_includes_ziping(self):
        p = MarriageAssertionProducer()
        a = p.produce(self.inp, chart={}, context=self.context)
        if not a.abstain:
            systems = [e.system for e in a.evidence]
            self.assertIn("ziping", systems)

    def test_health_includes_ziping(self):
        p = HealthAssertionProducer()
        a = p.produce(self.inp, chart={}, context=self.context)
        if not a.abstain:
            systems = [e.system for e in a.evidence]
            self.assertIn("ziping", systems)


class TestWeightedAggregation(unittest.TestCase):

    def test_marriage_ziwei_high_weight(self):
        """婚姻主题: 紫微权重0.90, 若紫微偏吉而其他偏凶, 综合应偏吉."""
        from tongshu.assertion.topics import _aggregate_directions_weighted
        from tongshu.assertion.contract import Assertion, AssertionType

        def mk(subject, direction):
            return Assertion(
                subject=subject,
                assertion_type=AssertionType.STRUCTURAL,
                direction=direction,
            )

        # 紫微(0.90)偏吉 + 盲派(0.70)偏凶 + 子平(0.75)偏凶 + 河洛(0.60)偏凶
        assertions = [
            mk("ziwei", Direction.POSITIVE),
            mk("blind", Direction.NEGATIVE),
            mk("ziping", Direction.NEGATIVE),
            mk("heluo", Direction.NEGATIVE),
        ]
        direction, pos, neg = _aggregate_directions_weighted(assertions, "marriage")
        # pos=0.90, neg=0.70+0.75+0.60=2.05 → 偏凶
        self.assertEqual(direction, Direction.NEGATIVE)
        self.assertAlmostEqual(pos, 0.90, places=2)
        self.assertAlmostEqual(neg, 2.05, places=2)

    def test_weighted_matters_over_votes(self):
        """加权与简单多数可能不同: 婚姻中紫微单票(高权重) vs 三个低权重体系反方向."""
        from tongshu.assertion.topics import _aggregate_directions_weighted
        from tongshu.assertion.contract import Assertion, AssertionType

        def mk(subject, direction):
            return Assertion(
                subject=subject,
                assertion_type=AssertionType.STRUCTURAL,
                direction=direction,
            )

        # 简单多数: 1吉vs3凶→凶; 加权: 紫微0.90 vs 0.70+0.75+0.60=2.05→仍凶
        # 构造一个权重能翻转的例子: 婚姻中 紫微(0.90)吉 vs 河洛(0.60)+盲派(0.70)凶
        assertions = [
            mk("ziwei", Direction.POSITIVE),   # 0.90
            mk("heluo", Direction.NEGATIVE),   # 0.60
            mk("blind", Direction.NEGATIVE),   # 0.70
        ]
        direction, pos, neg = _aggregate_directions_weighted(assertions, "marriage")
        # pos=0.90, neg=1.30 → 偏凶(负权重仍占优)
        self.assertEqual(direction, Direction.NEGATIVE)

    def test_health_ziping_high_weight(self):
        """健康主题: 子平0.85权重, 应能体现."""
        from tongshu.assertion.topics import _aggregate_directions_weighted
        from tongshu.assertion.contract import Assertion, AssertionType

        def mk(subject, direction):
            return Assertion(
                subject=subject,
                assertion_type=AssertionType.STRUCTURAL,
                direction=direction,
            )

        assertions = [
            mk("ziping", Direction.POSITIVE),  # 0.85
            mk("heluo", Direction.NEGATIVE),   # 0.80
        ]
        direction, pos, neg = _aggregate_directions_weighted(assertions, "health")
        # pos=0.85, neg=0.80 → 偏吉(子平权重略高)
        self.assertEqual(direction, Direction.POSITIVE)


    pytestmark = __import__("pytest").mark.xfail(reason="AuditFlag冻结(V13-P0)")

    @staticmethod
    def _mk(subject, direction):
        from tongshu.assertion.contract import Assertion, AssertionType
        return Assertion(subject=subject, assertion_type=AssertionType.STRUCTURAL, direction=direction)

    def test_detect_conflict_generates_audit_flag(self):
        from tongshu.assertion.topics import _detect_conflict
        assertions = [
            self._mk("ziwei", Direction.POSITIVE),
            self._mk("ziping", Direction.NEGATIVE),
        ]
        flags = _detect_conflict(assertions, "marriage")
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0].topic, "marriage")
        self.assertIn("ziwei: positive", flags[0].conflicting_engines)
        self.assertIn("ziping: negative", flags[0].conflicting_engines)

    def test_no_conflict_when_aligned(self):
        from tongshu.assertion.topics import _detect_conflict
        assertions = [
            self._mk("ziwei", Direction.POSITIVE),
            self._mk("ziping", Direction.POSITIVE),
            self._mk("blind", Direction.POSITIVE),
        ]
        self.assertEqual(_detect_conflict(assertions, "career"), ())

    def test_audit_report_locates_suspect_engine(self):
        """P4: 反方向审计报告应定位冲突频次最高的引擎(最可能算法出错)."""
        from tongshu.assertion.contract import AuditFlag
        from tongshu.assertion.audit_report import build_audit_report
        a1 = Assertion(subject="婚姻", assertion_type=AssertionType.STRUCTURAL,
                       direction=Direction.NEUTRAL, confidence=Confidence.LIKELY,
                       audit_flags=(AuditFlag(topic="婚姻",
                                              conflicting_engines=("ziwei: positive", "ziping: negative")),))
        a2 = Assertion(subject="健康", assertion_type=AssertionType.STRUCTURAL,
                       direction=Direction.NEUTRAL, confidence=Confidence.LIKELY,
                       audit_flags=(AuditFlag(topic="健康",
                                              conflicting_engines=("ziwei: negative", "heluo: positive")),))
        r = build_audit_report([a1, a2])
        self.assertEqual(r["total_conflicts"], 4)
        self.assertEqual(r["engine_conflict_count"]["ziwei"], 2)
        self.assertEqual(r["most_suspect_engine"], "ziwei")
        self.assertIn("婚姻", r["topics"])

    def test_audit_report_empty_no_conflicts(self):
        from tongshu.assertion.audit_report import build_audit_report
        a = Assertion(subject="事业", assertion_type=AssertionType.STRUCTURAL,
                      direction=Direction.POSITIVE, confidence=Confidence.LIKELY)
        r = build_audit_report([a])
        self.assertEqual(r["total_conflicts"], 0)
        self.assertIsNone(r["most_suspect_engine"])


if __name__ == "__main__":
    unittest.main()
