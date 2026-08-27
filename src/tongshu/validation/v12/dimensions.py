"""9 Validation Dimensions — per V1.2 Contract.

Exactly 9 Dimensions, no #10. DIRECTIONALITY is OPTIONAL.
All others are REQUIRED.
Read-only: validators never write to upstream data.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class DimensionRequirement(enum.Enum):
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"
    FUTURE = "FUTURE"


@dataclass
class ValidationDimension:
    """Definition of a single Validation Dimension."""

    dimension_id: str
    name: str
    description: str
    requirement: DimensionRequirement = DimensionRequirement.REQUIRED
    target_status: str = "PARTIAL"
    phase: int = 1
    reads_from: List[str] = field(default_factory=list)
    output_fields: List[str] = field(default_factory=list)


# ─── V1.2 9 Dimensions (strict order, no #10) ────────────────────────────────

VALIDATION_DIMENSION_DEFS: List[ValidationDimension] = [
    ValidationDimension(
        dimension_id="CALCULATION",
        name="计算层正确性",
        description="八字/河洛/紫微/黄历计算是否与参考实现一致",
        requirement=DimensionRequirement.REQUIRED,
        target_status="PASS",
        phase=1,
        reads_from=["schema_1"],
        output_fields=["status", "score", "failures"],
    ),
    ValidationDimension(
        dimension_id="SIGNAL",
        name="信号生成覆盖度",
        description="五大引擎信号是否完整生成并标准化",
        requirement=DimensionRequirement.REQUIRED,
        target_status="PARTIAL",
        phase=3,
        reads_from=["schema_4"],
        output_fields=["status", "coverage_ratio", "missing_signals"],
    ),
    ValidationDimension(
        dimension_id="ONTOLOGY",
        name="事件本体映射精度",
        description="预测Event Type是否与Golden Dataset一致",
        requirement=DimensionRequirement.REQUIRED,
        target_status="PARTIAL",
        phase=3,
        reads_from=["schema_3", "schema_7"],
        output_fields=["status", "match_rate", "mismatches"],
    ),
    ValidationDimension(
        dimension_id="TEMPORAL",
        name="时间预测精度",
        description="预测时间是否在Evaluation Tolerance Window内",
        requirement=DimensionRequirement.REQUIRED,
        target_status="PARTIAL",
        phase=4,
        reads_from=["schema_5"],
        output_fields=["status", "convergence_score", "window_match"],
    ),
    ValidationDimension(
        dimension_id="SEVERITY",
        name="严重度评估质量",
        description="预测severity_class是否与actual_severity_class匹配",
        requirement=DimensionRequirement.REQUIRED,
        target_status="PARTIAL",
        phase=5,
        reads_from=["schema_6"],
        output_fields=["status", "severity_match_rate"],
    ),
    ValidationDimension(
        dimension_id="EVIDENCE",
        name="证据链完整性",
        description="CLAIM/SOURCE/PASSAGE/EVIDENCE五级结构是否完整",
        requirement=DimensionRequirement.REQUIRED,
        target_status="PARTIAL",
        phase=2,
        reads_from=["schema_7"],
        output_fields=["status", "completeness_score", "chain_breaks"],
    ),
    ValidationDimension(
        dimension_id="INTERPRETATION",
        name="关系解释质量",
        description="Yi Engine解释是否符合证据链，有无禁止术语",
        requirement=DimensionRequirement.REQUIRED,
        target_status="NOT_IMPLEMENTED",
        phase=6,
        reads_from=["schema_8"],
        output_fields=["status", "quality_score", "forbidden_terms"],
    ),
    ValidationDimension(
        dimension_id="CROSS_ENGINE_AGREE",
        name="多引擎一致性",
        description="五大引擎信号是否一致，冲突是否有裁决",
        requirement=DimensionRequirement.REQUIRED,
        target_status="PARTIAL",
        phase=5,
        reads_from=["schema_4", "schema_6"],
        output_fields=["status", "agreement_rate", "conflicts"],
    ),
    ValidationDimension(
        dimension_id="DIRECTIONALITY",
        name="方向性正确性",
        description="预测方向(POSITIVE/NEGATIVE/CHANGE)是否正确",
        requirement=DimensionRequirement.OPTIONAL,
        target_status="NOT_EVALUABLE",
        phase=5,
        reads_from=["schema_3", "schema_4"],
        output_fields=["status", "direction_match_rate"],
    ),
]

# O(1) lookup
DIMENSION_BY_ID: Dict[str, ValidationDimension] = {
    d.dimension_id: d for d in VALIDATION_DIMENSION_DEFS
}

# Strict count invariant
assert len(VALIDATION_DIMENSION_DEFS) == 9, \
    f"V1.2 mandates exactly 9 Dimensions, got {len(VALIDATION_DIMENSION_DEFS)}"

# REQUIRED count
REQUIRED_DIMENSIONS = [d for d in VALIDATION_DIMENSION_DEFS if d.requirement == DimensionRequirement.REQUIRED]
OPTIONAL_DIMENSIONS = [d for d in VALIDATION_DIMENSION_DEFS if d.requirement == DimensionRequirement.OPTIONAL]

assert len(REQUIRED_DIMENSIONS) == 8, f"Expected 8 REQUIRED dimensions, got {len(REQUIRED_DIMENSIONS)}"
assert len(OPTIONAL_DIMENSIONS) == 1, f"Expected 1 OPTIONAL dimension (DIRECTIONALITY), got {len(OPTIONAL_DIMENSIONS)}"
