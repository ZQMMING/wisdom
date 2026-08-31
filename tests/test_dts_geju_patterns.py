# -*- coding: utf-8 -*-
"""滴天髓格局断言测试 - M3 Phase 3.1 第一批（5条）

【测试要求】
- 验证Primitive拆分是否正确
- 验证Composite规则是否有原典授权
- 验证Condition能从Canonical State得出
- 验证无Legacy调用
- 验证无wang_score阈值使用
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tongshu.assertion.classics.ditian_sui.patterns import (
    DtsGejuAssertionProducer,
    DtsGejuPrimitive,
    DtsGejuConditionId,
    DtsGejuEvidence,
    DtsGejuPrimitiveAssertion,
    DtsGejuCompositeRule,
)
from tongshu.assertion.contract import (
    Assertion, AssertionInput, AssertionType, Confidence, Direction,
    EvidenceRef,
)


class TestDtsGejuPrimitives(unittest.TestCase):
    """测试滴天髓格局Primitive拆分"""

    def setUp(self):
        self.producer = DtsGejuAssertionProducer()
        self.input_data = AssertionInput(birth_datetime="1974-04-28T16:00:00+08:00")
        self.canonical_state = {
            "month_branch": "辰",
            "day_master": "甲",
            "day_branch": "寅",
            "heavenly_stems": ["甲", "戊", "己", "壬"],
            "earthly_branches": ["寅", "辰", "亥", "申"],
        }

    def test_primitive_count_per_assertion(self):
        """验证每条断言有3个Primitive"""
        for assertion_id in ["DTS-GEJU-001", "DTS-GEJU-002", "DTS-GEJU-003", "DTS-GEJU-004", "DTS-GEJU-005"]:
            primitives = self.producer.primitives.get(assertion_id, [])
            self.assertEqual(len(primitives), 3, f"{assertion_id}应该有3个Primitive")

    def test_primitive_structure(self):
        """验证Primitive结构完整性"""
        for assertion_id, primitives in self.producer.primitives.items():
            for primitive in primitives:
                self.assertIsNotNone(primitive.primitive_id)
                self.assertIsInstance(primitive.primitive, DtsGejuPrimitive)
                self.assertIsInstance(primitive.condition_id, DtsGejuConditionId)
                self.assertIsInstance(primitive.evidence, DtsGejuEvidence)
                self.assertTrue(primitive.canonical_state_requirement)

    def test_evidence_layer_distribution(self):
        """验证Evidence分层（原文层/注释层/后世层）"""
        original_text_count = 0
        commentary_count = 0

        for assertion_id, primitives in self.producer.primitives.items():
            for primitive in primitives:
                if primitive.evidence.text_layer == "ORIGINAL_TEXT":
                    original_text_count += 1
                elif primitive.evidence.text_layer == "ORIGINAL_COMMENTARY":
                    commentary_count += 1

        # 应该至少有原文层Evidence
        self.assertGreater(original_text_count, 0)


class TestDtsGejuCompositeRules(unittest.TestCase):
    """测试滴天髓格局Composite规则（必须有原典授权）"""

    def setUp(self):
        self.producer = DtsGejuAssertionProducer()

    def test_all_composite_rules_have_authorization(self):
        """验证所有Composite规则都有原典授权"""
        for assertion_id, rule in self.producer.composite_rules.items():
            self.assertTrue(rule.classical_authorization,
                f"{assertion_id}的Composite规则缺少原典授权")

    def test_composite_logic_is_and(self):
        """验证Composite逻辑为AND（用户裁决：不能工程推断A+B+C⇒成格）"""
        for assertion_id, rule in self.producer.composite_rules.items():
            self.assertEqual(rule.logic, "AND",
                f"{assertion_id}的Composite逻辑应该是AND")

    def test_composite_has_classical_source(self):
        """验证Composite规则有原典来源定位"""
        for assertion_id, rule in self.producer.composite_rules.items():
            self.assertTrue(rule.source_locator,
                f"{assertion_id}的Composite规则缺少来源定位")


class TestDtsGejuAssertionProduction(unittest.TestCase):
    """测试滴天髓格局断言生产"""

    def setUp(self):
        self.producer = DtsGejuAssertionProducer()
        self.input_data = AssertionInput(birth_datetime="1974-04-28T16:00:00+08:00")
        self.canonical_state = {
            "month_branch": "辰",
            "day_master": "甲",
            "day_branch": "寅",
            "heavenly_stems": ["甲", "戊", "己", "壬"],
            "earthly_branches": ["寅", "辰", "亥", "申"],
        }

    def test_produce_returns_5_assertions(self):
        """验证生产返回5条断言"""
        assertions = self.producer.produce(self.input_data, self.canonical_state)
        self.assertEqual(len(assertions), 5)

    def test_assertions_have_classical_refs(self):
        """验证断言有经典引用"""
        assertions = self.producer.produce(self.input_data, self.canonical_state)
        for assertion in assertions:
            self.assertTrue(assertion.classical_refs,
                f"断言{assertion.subject}缺少经典引用")

    def test_assertions_have_evidence(self):
        """验证断言有Evidence引用"""
        assertions = self.producer.produce(self.input_data, self.canonical_state)
        for assertion in assertions:
            self.assertTrue(assertion.evidence,
                f"断言{assertion.subject}缺少Evidence")

    def test_assertions_no_legacy_strength_call(self):
        """验证断言不使用Legacy Strength调用"""
        assertions = self.producer.produce(self.input_data, self.canonical_state)
        for assertion in assertions:
            # 检查mechanism中不包含evaluate_strength或wang_score
            self.assertNotIn("evaluate_strength", assertion.mechanism.lower())
            self.assertNotIn("wang_score", assertion.mechanism.lower())

    def test_assertions_no_wang_score_threshold(self):
        """验证断言不使用wang_score阈值判定"""
        assertions = self.producer.produce(self.input_data, self.canonical_state)
        for assertion in assertions:
            # 检查confidence不是基于wang_score阈值
            self.assertNotIn("threshold", assertion.mechanism.lower())


class TestDtsGejuEvidenceVerification(unittest.TestCase):
    """测试滴天髓格局Evidence验证状态"""

    def setUp(self):
        self.producer = DtsGejuAssertionProducer()

    def test_evidence_verification_status_tracking(self):
        """验证Evidence验证状态被跟踪"""
        for assertion_id, primitives in self.producer.primitives.items():
            for primitive in primitives:
                valid_statuses = {"UNVERIFIED", "EXACT_MATCH", "PARTIAL_MATCH", "NOT_FOUND", "CONFLICT", "pending_verification"}
                self.assertIn(primitive.evidence.verification_status, valid_statuses,
                    f"{primitive.primitive_id}的验证状态无效: {status}")

    def test_evidence_has_source_locator(self):
        """验证Evidence有来源定位"""
        for assertion_id, primitives in self.producer.primitives.items():
            for primitive in primitives:
                self.assertTrue(primitive.evidence.source_locator,
                    f"{primitive.primitive_id}缺少来源定位")


class TestDtsGejuNoLegacyCalls(unittest.TestCase):
    """验证无Legacy调用"""

    def test_no_evaluate_strength_call(self):
        """验证不调用evaluate_strength"""
        from tongshu.assertion.classics.ditian_sui.patterns import DtsGejuAssertionProducer
        import inspect

        source = inspect.getsource(DtsGejuAssertionProducer)
        self.assertNotIn("evaluate_strength", source,
            "DtsGejuAssertionProducer不应调用evaluate_strength")

    def test_no_wang_score_usage(self):
        """验证不使用wang_score"""
        from tongshu.assertion.classics.ditian_sui.patterns import DtsGejuAssertionProducer
        import inspect

        source = inspect.getsource(DtsGejuAssertionProducer)
        self.assertNotIn("wang_score", source,
            "DtsGejuAssertionProducer不应使用wang_score")


if __name__ == "__main__":
    unittest.main()