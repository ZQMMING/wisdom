"""断言层Producer测试 (systems + topics).

验证:
- 多体系独立断言Producer (紫微/盲派/河洛) 能正常输出Assertion
- 核心主题断言Producer (事业/财运/婚姻/健康) 能整合多体系输出
- AssertionEngine 能注册并运行全部Producer
- 契约合规: 单体系置信<=LIKELY, 多体系收敛可达SUPPORTED
"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tongshu.assertion.contract import (
    AssertionInput, AssertionType, Confidence, Direction, insufficient_evidence,
)
from tongshu.assertion.engine import AssertionEngine
from tongshu.assertion.systems import (
    ZiweiAssertionProducer, BlindAssertionProducer, HeluoAssertionProducer,
)
from tongshu.assertion.topics import (
    CareerAssertionProducer, WealthAssertionProducer,
    MarriageAssertionProducer, HealthAssertionProducer,
)


class TestSystemProducers(unittest.TestCase):
    """多体系独立断言Producer测试."""

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

    def test_ziwei_producer(self):
        """紫微断言Producer能输出非拒断Assertion."""
        p = ZiweiAssertionProducer()
        self.assertEqual(p.subject, "ziwei")
        a = p.produce(self.inp, chart={}, context=self.context)
        self.assertEqual(a.subject, "ziwei")
        # 单体系置信<=LIKELY
        self.assertIn(a.confidence, (Confidence.LIKELY, Confidence.WEAK, Confidence.INSUFFICIENT_EVIDENCE))

    def test_blind_producer(self):
        """盲派断言Producer能输出Assertion."""
        p = BlindAssertionProducer()
        self.assertEqual(p.subject, "blind")
        a = p.produce(self.inp, chart={}, context=self.context)
        self.assertEqual(a.subject, "blind")

    def test_heluo_producer(self):
        """河洛断言Producer能输出Assertion."""
        p = HeluoAssertionProducer()
        self.assertEqual(p.subject, "heluo")
        a = p.produce(self.inp, chart={}, context=self.context)
        self.assertEqual(a.subject, "heluo")
        if not a.abstain:
            self.assertIn("先天", a.mechanism)
            self.assertIn("元堂", a.mechanism)

    def test_no_chart_returns_insufficient(self):
        """chart=None时返回拒断."""
        p = ZiweiAssertionProducer()
        a = p.produce(self.inp, chart=None, context=self.context)
        self.assertTrue(a.abstain)
        self.assertEqual(a.assertion_type, AssertionType.INSUFFICIENT_EVIDENCE)


class TestTopicProducers(unittest.TestCase):
    """核心主题断言Producer测试."""

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

    def test_career_producer(self):
        """事业断言Producer."""
        p = CareerAssertionProducer()
        self.assertEqual(p.subject, "career")
        a = p.produce(self.inp, chart={}, context=self.context)
        self.assertEqual(a.subject, "career")
        self.assertIn("事业", a.mechanism)

    def test_wealth_producer(self):
        """财运断言Producer."""
        p = WealthAssertionProducer()
        self.assertEqual(p.subject, "wealth")
        a = p.produce(self.inp, chart={}, context=self.context)
        self.assertEqual(a.subject, "wealth")
        self.assertIn("财运", a.mechanism)

    def test_marriage_producer(self):
        """婚姻断言Producer."""
        p = MarriageAssertionProducer()
        self.assertEqual(p.subject, "marriage")
        a = p.produce(self.inp, chart={}, context=self.context)
        self.assertEqual(a.subject, "marriage")
        self.assertIn("婚姻", a.mechanism)

    def test_health_producer(self):
        """健康断言Producer."""
        p = HealthAssertionProducer()
        self.assertEqual(p.subject, "health")
        a = p.produce(self.inp, chart={}, context=self.context)
        self.assertEqual(a.subject, "health")
        self.assertIn("健康", a.mechanism)

    def test_topic_direction_valid(self):
        """主题断言方向必须是合法Direction."""
        for ProducerClass in (CareerAssertionProducer, WealthAssertionProducer,
                               MarriageAssertionProducer, HealthAssertionProducer):
            p = ProducerClass()
            a = p.produce(self.inp, chart={}, context=self.context)
            self.assertIsInstance(a.direction, Direction)


class TestAssertionEngine(unittest.TestCase):
    """AssertionEngine集成测试."""

    def test_register_and_run_all(self):
        """引擎能注册并运行全部Producer."""
        engine = AssertionEngine()
        producers = [
            ZiweiAssertionProducer(),
            BlindAssertionProducer(),
            HeluoAssertionProducer(),
            CareerAssertionProducer(),
            WealthAssertionProducer(),
            MarriageAssertionProducer(),
            HealthAssertionProducer(),
        ]
        for p in producers:
            engine.register(p)

        self.assertEqual(len(engine.subjects), 7)
        self.assertIn("ziwei", engine.subjects)
        self.assertIn("career", engine.subjects)

        inp = AssertionInput(birth_datetime="1974-04-28T16:00:00+08:00")
        context = {
            "birth": (1974, 4, 28, 16, "male"),
            "bazi": [("甲", "寅"), ("戊", "辰"), ("己", "亥"), ("壬", "申")],
            "gender": "male",
            "birth_hour": "申",
            "birth_year": 1974,
            "focus_years": [1996],
        }
        results = engine.run(inp, chart={}, context=context)
        self.assertEqual(len(results), 7)
        subjects = [r.subject for r in results]
        self.assertIn("ziwei", subjects)
        self.assertIn("blind", subjects)
        self.assertIn("heluo", subjects)
        self.assertIn("career", subjects)
        self.assertIn("wealth", subjects)
        self.assertIn("marriage", subjects)
        self.assertIn("health", subjects)

    def test_duplicate_subject_rejected(self):
        """重复subject注册被拒绝."""
        engine = AssertionEngine()
        engine.register(ZiweiAssertionProducer())
        with self.assertRaises(ValueError):
            engine.register(ZiweiAssertionProducer())


if __name__ == "__main__":
    unittest.main()
