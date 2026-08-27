"""Ablation Runner — 消融实验引擎

验证每个模块的增量贡献：
- 完整模型 vs 去掉时
- vs 去掉爻
- vs 去掉元堂
- vs 去掉后天
- vs 去掉流月

使用方式：
    ablation = AblationRunner(case, pipeline_fn)
    results = ablation.run(variants=["full", "no_yuantang", "no_time"])
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Callable, Optional

from ..schema.case import Case
from ..schema.prediction import Prediction

logger = logging.getLogger(__name__)


@dataclass
class AblationVariant:
    """消融变体配置。"""
    variant_name: str
    description: str
    disabled_modules: list[str] = field(default_factory=list)


@dataclass
class AblationResult:
    """单次消融实验结果。"""
    case_id: str
    variant: str
    prediction: Prediction
    score: float
    delta_from_full: float = 0.0


class AblationRunner:
    """消融实验执行器。"""

    DEFAULT_VARIANTS = [
        AblationVariant("full", "完整模型"),
        AblationVariant("no_yuantang", "去掉元堂"),
        AblationVariant("no_time", "去掉时间维度"),
        AblationVariant("no_yao", "去掉爻"),
        AblationVariant("no_postnatal", "去掉后天"),
        AblationVariant("no_monthly", "去掉流月"),
    ]

    def __init__(self, case: Case, pipeline_fn: Optional[Callable] = None):
        self._case = case
        self._pipeline_fn = pipeline_fn
        self._results: dict[str, AblationResult] = {}

    def run(self, variants: Optional[list[AblationVariant]] = None) -> dict[str, AblationResult]:
        """执行消融实验。"""
        variant_list = variants or self.DEFAULT_VARIANTS
        for variant in variant_list:
            result = self._run_variant(variant)
            self._results[variant.variant_name] = result
            logger.info(f"Ablation {variant.variant_name}: score={result.score}")
        return self._results

    def _run_variant(self, variant: AblationVariant) -> AblationResult:
        """运行单个变体。"""
        # 获取完整模型分数作为基准
        full_result = self._results.get("full")
        full_score = full_result.score if full_result else 0.0

        # 运行变体（模拟，实际应传入disabled_modules给pipeline）
        prediction = self._predict(variant.disabled_modules)
        score = self._score(prediction)

        return AblationResult(
            case_id=self._case.case_id,
            variant=variant.variant_name,
            prediction=prediction,
            score=score,
            delta_from_full=score - full_score,
        )

    def _predict(self, disabled_modules: list[str]) -> Prediction:
        """生成预测（简化实现）。"""
        return Prediction(
            case_id=self._case.case_id,
            target_year=2026,
            signals=[],
            raw_calculation={"disabled_modules": disabled_modules},
        )

    def _score(self, prediction: Prediction) -> float:
        """评分（简化实现）。"""
        return 75.0  # 模拟分数

    def generate_report(self) -> dict:
        """生成消融实验报告。"""
        full_score = self._results.get("full", AblationResult("", "full", None, 0)).score
        return {
            "case_id": self._case.case_id,
            "full_score": full_score,
            "variants": {
                k: {
                    "score": v.score,
                    "delta": v.delta_from_full,
                }
                for k, v in self._results.items()
            },
            "contribution_summary": {
                var: self._results[var].delta_from_full
                for var in self._results
                if var != "full"
            },
        }
