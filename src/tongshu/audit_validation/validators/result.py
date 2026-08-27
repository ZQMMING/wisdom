"""渲染输出 3 层校验结果数据类。

依赖：无。

Version: 1.0.0
Created: 2026-08-20 (Phase 2 / Step 8)
Migrated from: validation/layer1.py:18-28 (Layer1Result)
              validation/layer2.py:20-29 (Layer2Result)
              validation/layer3.py:14-22 (Layer3Result)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Layer1Result:
    passed: bool
    errors: list[str]
    details: dict

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "errors": list(self.errors),
            "details": self.details,
        }


@dataclass
class Layer2Result:
    passed: bool
    min_similarity: float
    threshold: float
    details: dict

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "min_similarity": self.min_similarity,
            "threshold": self.threshold,
            "details": self.details,
        }


@dataclass
class Layer3Result:
    passed: bool
    entailment_verdict: str
    judge_model_id: str
    details: dict

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "entailment_verdict": self.entailment_verdict,
            "judge_model_id": self.judge_model_id,
            "details": self.details,
        }


__all__ = ["Layer1Result", "Layer2Result", "Layer3Result"]
