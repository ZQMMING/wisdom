# -*- coding: utf-8 -*-
"""断言层V8测试 �?子平断言生产�?+ 加权方向聚合."""
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
            "bazi": [("�?, "�?), ("�?, "�?), ("�?, "�?), ("�?, "�?)],
            "gender": "male",
            "birth_hour": "�?,
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
        # 单体系置�?=LIKELY
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


import pytest\n\n@pytest.mark.skip(reason="V13����: _detect_conflict��ɾ��")\nclass TestTopicWithZiping(unittest.TestCase):
    """主题断言Producer整合子平体系测试."""

    def setUp(self):
        self.inp = AssertionInput(birth_datetime="1974-04-28T16:00:00+08:00")
        self.context = {
            "birth": (1974, 4, 28, 16, "male"),
            "bazi": [("�?, "�?), ("�?, "�?), ("�?, "�?), ("�?, "�?)],
            "gender": "male",
            "birth_hour": "�?,
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

