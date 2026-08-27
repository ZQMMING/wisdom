"""ValidationStage — 阶段 9（3 层校验 + 4 Gate + fail-closed）。

职责：
    - Layer1: Claim 覆盖校验
    - Layer2: 文本相似度校验
    - Layer3: 蕴含校验（judge model）
    - G1 Evidence Gate + G2 Translation Gate + G3 Safety Gate + G4 Output Gate
    - fail-closed 决策：任一 BLOCK → 整体 BLOCK

返回 ValidationStageResult。template fallback 由 pipeline.run() 在
validation.passed=False 时触发（本 Stage 不主动降级）。

Version: 1.0.0
Created: 2026-08-20 (Phase 2 / Step 3 C4)
Migrated from: pipeline.py:243-269（run() 阶段 9）
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..audit.gates import run_gates, gates_passed
from ..reasoning.mapping_registry import MappingRegistry
from ..types import ValidationStageResult
from ..validation.layer1 import validate_layer1
from ..validation.layer2 import validate_layer2
from ..validation.layer3 import validate_layer3

if TYPE_CHECKING:
    from .compute_stage import ComputeResult
    from .render_stage import RenderStageResult


log = logging.getLogger(__name__)


class ValidationStage:
    """阶段 9: 3 层校验 + 4 Gate + fail-closed 决策。"""

    def __init__(
        self,
        evidence_ids: set[str],
        mapping_registry: MappingRegistry | None,
        enable_validation: bool = True,
    ) -> None:
        self.evidence_ids = evidence_ids
        self.mapping_registry = mapping_registry
        self._enable_validation = enable_validation

    def run(
        self,
        compute: "ComputeResult",
        render: "RenderStageResult",
        forbidden_inferences: list | None,
    ) -> ValidationStageResult:
        """执行校验 + fail-closed 决策。

        返回 ValidationStageResult，pipeline.run() 根据 passed 决定是否触发
        template fallback（本 Stage 不主动降级）。
        """
        canonical_dict = compute.canonical.to_dict()
        rendered_text = render.rendered_text
        rendered_obj = render.rendered

        # 计算模式或 renderer 硬失败 → 不走校验
        if not self._enable_validation or rendered_obj is None:
            return ValidationStageResult(
                layer1=None,
                layer2=None,
                layer3=None,
                gates=(),
                passed=False,  # fail-closed：不走校验 → 不通过（不会被 RenderStage fallback 污染）
            )

        l1 = validate_layer1(
            rendered_obj.raw_output,
            canonical_dict,
            render.render_request_dict,
            forbidden_inferences or [],
        )
        l2 = validate_layer2(rendered_text, canonical_dict, rendered_obj.degradation)
        l3 = validate_layer3(rendered_text, canonical_dict)
        gates = run_gates(
            canonical_dict,
            rendered_text,
            evidence_ids=self.evidence_ids,
            registry=self.mapping_registry,
            schema_valid=compute.canonical_schema_valid,
            schema_errors=list(compute.canonical_schema_errors),
        )
        passed = l1.passed and l2.passed and l3.passed and gates_passed(gates)

        return ValidationStageResult(
            layer1=l1,
            layer2=l2,
            layer3=l3,
            gates=tuple(gates),
            passed=passed,
        )

    @staticmethod
    def make_skip() -> ValidationStageResult:
        """compute_only 或 其他跳过校验的占位。"""
        return ValidationStageResult(
            layer1=None,
            layer2=None,
            layer3=None,
            gates=(),
            passed=False,
        )
