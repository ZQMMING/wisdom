"""
Phase 6 — Forward Validation Engine

职责:
  管理 Prediction → Event → Evaluation 的前瞻验证链路

边界:
  1. PredictionWindow 一旦创建不可修改
  2. EvaluationToleranceWindow 独立于 PredictionWindow
  3. 禁止使用未来事件反向修改 prediction
  4. 禁止 post-hoc information 修改 interpretation
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from tongshu.yi.schema import (
    PredictionRecord,
    EvaluationRecord,
    ForwardValidationStatus,
    DirectionLabel,
)
from tongshu.spec.temporal_evidence import EvaluationToleranceWindow


class ForwardValidationEngine:
    """
    前瞻验证引擎

    数据流:
      YiInterpretation → PredictionRecord (冻结)
                        ↓
                  Real-world Event (未来发生)
                        ↓
                  EvaluationRecord (使用独立 Tolerance Window)
                        ↓
                  ForwardValidationStatus

    严格保证:
      prediction.created_at < event.occurred_at
    """

    def __init__(self):
        self._predictions: Dict[str, PredictionRecord] = {}
        self._evaluations: Dict[str, EvaluationRecord] = {}

    # ─── Prediction Management ────────────────────────────────────────────────

    def create_prediction(
        self,
        interpretation_id: str,
        direction: DirectionLabel,
        window_start_year: int,
        window_end_year: int,
        created_at: Optional[str] = None,
    ) -> PredictionRecord:
        """
        创建预测记录。

        Args:
            interpretation_id: → YiInterpretation.interpretation_id
            direction: 预测方向
            window_start_year: 预测窗口起始年
            window_end_year: 预测窗口结束年
            created_at: ISO8601 时间戳（默认现在）

        Returns:
            PredictionRecord（冻结，不可修改）
        """
        if created_at is None:
            created_at = datetime.utcnow().isoformat() + "Z"

        prediction = PredictionRecord(
            prediction_id=str(uuid.uuid4()),
            interpretation_ref=interpretation_id,
            prediction_direction=direction,
            prediction_window_start=window_start_year,
            prediction_window_end=window_end_year,
            created_at=created_at,
        )
        self._predictions[prediction.prediction_id] = prediction
        return prediction

    # ─── Evaluation Management ────────────────────────────────────────────────

    def evaluate_event(
        self,
        prediction_id: str,
        actual_direction: DirectionLabel,
        actual_occurred_at: str,
        tolerance_window: EvaluationToleranceWindow,
    ) -> EvaluationRecord:
        """
        评估实际事件。

        检查:
          1. prediction.created_at < event.occurred_at（防泄漏）
          2. actual_direction 是否在 prediction 窗口内

        Args:
            prediction_id: → PredictionRecord.prediction_id
            actual_direction: 实际发生的方向
            actual_occurred_at: 事件发生时间（ISO8601）
            tolerance_window: 评估容差窗口

        Returns:
            EvaluationRecord
        """
        prediction = self._predictions.get(prediction_id)
        if prediction is None:
            raise ValueError(f"Prediction {prediction_id} not found")

        # 检查数据泄漏
        leakage = prediction.validate_no_leakage(actual_occurred_at)
        if leakage:
            status = ForwardValidationStatus.DATA_LEAKAGE
            match = False
        else:
            # 检查时间窗口和方向匹配
            event_year = datetime.fromisoformat(actual_occurred_at.replace("Z", "+00:00")).year
            in_window = (
                prediction.prediction_window_start
                <= event_year
                <= prediction.prediction_window_end
            )
            direction_match = (
                prediction.prediction_direction == actual_direction
            )
            match = in_window and direction_match
            status = ForwardValidationStatus.PASSED if match else ForwardValidationStatus.FAILED

        evaluation = EvaluationRecord(
            evaluation_id=str(uuid.uuid4()),
            prediction_ref=prediction_id,
            actual_direction=actual_direction,
            actual_occurred_at=actual_occurred_at,
            tolerance_days=tolerance_window.tolerance_days,
            match_result=match,
            status=status,
        )
        self._evaluations[evaluation.evaluation_id] = evaluation
        return evaluation

    # ─── Query ────────────────────────────────────────────────────────────────

    def get_prediction(self, prediction_id: str) -> Optional[PredictionRecord]:
        return self._predictions.get(prediction_id)

    def get_evaluation(self, evaluation_id: str) -> Optional[EvaluationRecord]:
        return self._evaluations.get(evaluation_id)

    def list_all_predictions(self) -> List[PredictionRecord]:
        return list(self._predictions.values())

    def list_all_evaluations(self) -> List[EvaluationRecord]:
        return list(self._evaluations.values())

    def get_validation_summary(self) -> Dict[str, int]:
        """返回验证统计摘要。"""
        summary = {
            "total_predictions": len(self._predictions),
            "total_evaluations": len(self._evaluations),
            "passed": 0,
            "failed": 0,
            "data_leakage": 0,
            "insufficient": 0,
            "pending": 0,
        }
        for ev in self._evaluations.values():
            if ev.status == ForwardValidationStatus.PASSED:
                summary["passed"] += 1
            elif ev.status == ForwardValidationStatus.FAILED:
                summary["failed"] += 1
            elif ev.status == ForwardValidationStatus.DATA_LEAKAGE:
                summary["data_leakage"] += 1
            elif ev.status == ForwardValidationStatus.INSUFFICIENT:
                summary["insufficient"] += 1
            else:
                summary["pending"] += 1
        return summary
