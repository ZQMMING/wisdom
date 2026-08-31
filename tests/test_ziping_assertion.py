# -*- coding: utf-8 -*-
"""断言层V8测试 — 子平断言生产者."""
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
        self.assertIn(a.confidence, (Confidence.LIKELY, Confidence.WEAK, Confidence.INSUFFICIENT_EVIDENCE))
        self.assertTrue(a.mechanism)

    def test_producer_no_birth(self):
        p = ZipingAssertionProducer()
        a = p.produce(self.inp, chart={}, context={})
        self.assertEqual(a.subject, "ziping")
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


if __name__ == "__main__":
    unittest.main()
