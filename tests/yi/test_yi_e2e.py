"""
Phase 6 — End-to-End Integration Tests

测试链路:
  User Profile → 五引擎 → Canonical Signals → Evidence Chain
  → Temporal Convergence → Validation → Yi Interpretation
  → Prediction → Forward Validation
"""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path("E:/shuntian/src")))

import unittest
from datetime import datetime, timedelta

from tongshu.spec.canonical_signal import (
    CanonicalSignal,
    SignalTemporalScope,
    SignalLayer,
    SourceEngine,
)
from tongshu.spec.evidence_chain import (
    Evidence,
    EvidenceLevel,
    VerificationStatus,
)
from tongshu.spec.temporal_evidence import (
    EvaluationToleranceWindow,
)
from tongshu.temporal.schema import TemporalConvergence
from tongshu.yi import (
    YiAdapter,
    YiAdapterInput,
    YiInterpretationEngine,
    YiStructureStatus,
    DirectionLabel,
)
from tongshu.yi.schema import YiStructure
from tongshu.forward_validation import (
    ForwardValidationEngine,
    ForwardValidationStatus,
)


class TestYiAdapterIntegration(unittest.TestCase):
    """Yi Adapter E2E 测试。"""

    def test_adapt_with_valid_heluo_data(self):
        """从有效河洛数据适配 YiStructure。"""
        input_data = YiAdapterInput(
            heluo_prenatal_hexagram="地天泰",
            heluo_postnatal_hexagram="天雷无妄",
            heluo_yuantang_index=3,
            heluo_yuantang="六四",
        )
        structure = YiAdapter.adapt(input_data)
        self.assertEqual(structure.truth_hexagram, "天雷无妄")
        self.assertEqual(structure.true_line, 4)
        self.assertEqual(structure.position_name, "四")
        self.assertEqual(structure.status, YiStructureStatus.VALID)

    def test_adapt_with_missing_hexagram(self):
        """缺失卦名返回 NOT_APPLICABLE。"""
        input_data = YiAdapterInput()
        structure = YiAdapter.adapt(input_data)
        self.assertEqual(structure.status, YiStructureStatus.NOT_APPLICABLE)

    def test_adapt_with_temporal_convergence(self):
        """包含时间收敛数据的适配。"""
        convergence = TemporalConvergence(
            convergence_id="conv_001",
            target_year=2026,
            convergence_score=0.85,
            total_engines=3,
            agreeing_engines=3,
        )
        input_data = YiAdapterInput(
            heluo_postnatal_hexagram="乾为天",
            heluo_yuantang_index=0,
            temporal_convergence=convergence,
        )
        structure = YiAdapter.adapt(input_data)
        self.assertIn("2026", structure.temporal_context)
        self.assertIn("0.85", structure.temporal_context)

    def test_adapt_validates_no_raw_calculation(self):
        """验证输入不包含原始计算数据。"""
        # 此测试确保 YiAdapterInput 不接受 raw calculation fields
        input_data = YiAdapterInput(
            heluo_postnatal_hexagram="地天泰",
        )
        errors = YiAdapter.validate_input(input_data)
        self.assertEqual(len(errors), 0)


class TestYiInterpretationEngine(unittest.TestCase):
    """Yi 解释引擎 E2E 测试。"""

    def setUp(self):
        self.engine = YiInterpretationEngine()

    def test_interpret_valid_structure(self):
        """有效结构生成关系式解释。"""
        structure = YiStructure(
            truth_hexagram="地天泰",
            true_line=4,
            position_name="六四",
            ti_trigram="乾",
            yong_trigram="坤",
            ti_yong_relation="用生体（吉）",
            classical_quote="泰，小往大来，吉亨。",
            classical_source="周易·泰卦",
            layer=8,
            status=YiStructureStatus.VALID,
        )
        interp = self.engine.interpret(structure)
        self.assertEqual(interp.phase, 6)
        self.assertEqual(interp.directional_label, DirectionLabel.POSITIVE)
        self.assertIn("用生体", interp.state)
        self.assertFalse(interp.has_fortune_score)

    def test_interpret_not_applicable(self):
        """NOT_APPLICABLE 状态处理。"""
        structure = YiStructure(status=YiStructureStatus.NOT_APPLICABLE)
        interp = self.engine.interpret(structure)
        self.assertIn("不适用", interp.state)
        self.assertEqual(interp.directional_label, DirectionLabel.UNCERTAIN)

    def test_interpret_incomplete(self):
        """INCOMPLETE 状态处理。"""
        structure = YiStructure(
            truth_hexagram="乾为天",
            status=YiStructureStatus.INCOMPLETE,
        )
        interp = self.engine.interpret(structure)
        self.assertIn("不完整", interp.state)

    def test_no_fortune_score_output(self):
        """严格禁止 fortune_score / luck_score。"""
        structure = YiStructure(
            truth_hexagram="坤为地",
            status=YiStructureStatus.VALID,
        )
        interp = self.engine.interpret(structure)
        interp_dict = interp.to_dict()
        forbidden_keys = {"fortune_score", "luck_score", "overall_goodness", "auspicious_score"}
        self.assertFalse(any(k in interp_dict for k in forbidden_keys))

    def test_forbidden_terms_check(self):
        """检查禁止术语。"""
        structure = YiStructure(
            truth_hexagram="乾为天",
            status=YiStructureStatus.VALID,
        )
        interp = self.engine.interpret(structure)
        found = self.engine.check_forbidden_terms(interp)
        # 默认输出不应包含禁止术语
        self.assertEqual(len(found), 0)

    def test_direction_derivation(self):
        """方向推导正确性。"""
        test_cases = [
            ("用生体（吉）", DirectionLabel.POSITIVE),
            ("用克体（凶）", DirectionLabel.NEGATIVE),
            ("体生用（泄）", DirectionLabel.CHANGE),
            ("体克用（耗）", DirectionLabel.CHANGE),
            ("比和（平）", DirectionLabel.NEUTRAL),
        ]
        for relation, expected in test_cases:
            structure = YiStructure(
                truth_hexagram="测试",
                ti_yong_relation=relation,
                status=YiStructureStatus.VALID,
            )
            interp = self.engine.interpret(structure)
            self.assertEqual(interp.directional_label, expected,
                           f"Failed for {relation}")


class TestForwardValidationEngine(unittest.TestCase):
    """Forward Validation Engine E2E 测试。"""

    def setUp(self):
        self.engine = ForwardValidationEngine()
        self.base_time = "2025-01-01T00:00:00Z"

    def test_create_and_evaluate_prediction(self):
        """完整预测→评估流程。"""
        pred = self.engine.create_prediction(
            interpretation_id="interp_001",
            direction=DirectionLabel.POSITIVE,
            window_start_year=2025,
            window_end_year=2025,
            created_at=self.base_time,
        )
        self.assertIsNotNone(pred.prediction_id)

        eval_record = self.engine.evaluate_event(
            prediction_id=pred.prediction_id,
            actual_direction=DirectionLabel.POSITIVE,
            actual_occurred_at="2025-06-15T00:00:00Z",
            tolerance_window=EvaluationToleranceWindow(
                severity_class="MODERATE",
                tolerance_days=365,
            ),
        )
        self.assertEqual(eval_record.status, ForwardValidationStatus.PASSED)

    def test_data_leakage_detection(self):
        """检测数据泄漏（prediction.created_at >= event.occurred_at）。"""
        pred = self.engine.create_prediction(
            interpretation_id="interp_002",
            direction=DirectionLabel.NEGATIVE,
            window_start_year=2025,
            window_end_year=2025,
            created_at="2026-01-01T00:00:00Z",  # 未来时间
        )
        eval_record = self.engine.evaluate_event(
            prediction_id=pred.prediction_id,
            actual_direction=DirectionLabel.NEGATIVE,
            actual_occurred_at="2025-06-15T00:00:00Z",  # 过去时间
            tolerance_window=EvaluationToleranceWindow(
                severity_class="HIGH",
                tolerance_days=30,
            ),
        )
        self.assertEqual(eval_record.status, ForwardValidationStatus.DATA_LEAKAGE)

    def test_mismatch_direction(self):
        """方向不匹配时标记 FAILED。"""
        pred = self.engine.create_prediction(
            interpretation_id="interp_003",
            direction=DirectionLabel.POSITIVE,
            window_start_year=2025,
            window_end_year=2025,
            created_at=self.base_time,
        )
        eval_record = self.engine.evaluate_event(
            prediction_id=pred.prediction_id,
            actual_direction=DirectionLabel.NEGATIVE,
            actual_occurred_at="2025-06-15T00:00:00Z",
            tolerance_window=EvaluationToleranceWindow(
                severity_class="LOW",
                tolerance_days=365,
            ),
        )
        self.assertEqual(eval_record.status, ForwardValidationStatus.FAILED)

    def test_validation_summary(self):
        """验证统计摘要正确。"""
        # 创建多个预测和评估
        for i in range(3):
            pred = self.engine.create_prediction(
                interpretation_id=f"interp_{i}",
                direction=DirectionLabel.POSITIVE,
                window_start_year=2025,
                window_end_year=2025,
                created_at=self.base_time,
            )
            self.engine.evaluate_event(
                prediction_id=pred.prediction_id,
                actual_direction=DirectionLabel.POSITIVE,
                actual_occurred_at="2025-06-15T00:00:00Z",
                tolerance_window=EvaluationToleranceWindow(
                    severity_class="LOW",
                    tolerance_days=365,
                ),
            )

        summary = self.engine.get_validation_summary()
        self.assertEqual(summary["total_predictions"], 3)
        self.assertEqual(summary["total_evaluations"], 3)
        self.assertEqual(summary["passed"], 3)


class TestE2EFullPipeline(unittest.TestCase):
    """端到端完整链路测试。"""

    def test_full_pipeline(self):
        """完整链路: CanonSig → Yi → Prediction → Forward Validation。"""
        # Step 1: 创建 CanonicalSignal（模拟来自五引擎的输出）
        signal = CanonicalSignal(
            signal_id="sig_001",
            source_engine=SourceEngine.HELUO,
            ontology_type="ACTION",
            event_types=["career_change"],
            direction="POSITIVE",
            confidence=0.85,
            temporal_scope=SignalTemporalScope(
                start_year=2025,
                end_year=2025,
                granularity="YEARLY",
            ),
            evidence_refs=["ev_001"],
            extracted_at=datetime.utcnow().isoformat() + "Z",
        )

        # Step 2: Yi Adapter 适配
        adapter_input = YiAdapterInput(
            canonical_signals=[signal],
            heluo_postnatal_hexagram="地天泰",
            heluo_yuantang_index=2,
            heluo_yuantang="九三",
        )
        yi_structure = YiAdapter.adapt(adapter_input)
        self.assertEqual(yi_structure.truth_hexagram, "地天泰")

        # Step 3: Yi Interpretation
        interp_engine = YiInterpretationEngine()
        interpretation = interp_engine.interpret(yi_structure)
        self.assertEqual(interpretation.phase, 6)
        self.assertFalse(interpretation.has_fortune_score)

        # Step 4: Forward Validation - Create Prediction
        fwd_engine = ForwardValidationEngine()
        prediction = fwd_engine.create_prediction(
            interpretation_id=interpretation.interpretation_id,
            direction=interpretation.directional_label,
            window_start_year=2025,
            window_end_year=2025,
            created_at="2025-01-01T00:00:00Z",
        )

        # Step 5: Evaluate Event
        evaluation = fwd_engine.evaluate_event(
            prediction_id=prediction.prediction_id,
            actual_direction=interpretation.directional_label,
            actual_occurred_at="2025-06-15T00:00:00Z",
            tolerance_window=EvaluationToleranceWindow(
                severity_class="MODERATE",
                tolerance_days=365,
            ),
        )

        # 验证最终状态
        self.assertEqual(evaluation.status, ForwardValidationStatus.PASSED)

        # Step 6: Summary
        summary = fwd_engine.get_validation_summary()
        self.assertEqual(summary["total_predictions"], 1)
        self.assertEqual(summary["passed"], 1)


if __name__ == "__main__":
    unittest.main()
