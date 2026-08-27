"""审计 Gate 编排：顺序调用 G1→G2→G3→G4 + fail-closed 判断。

依赖：counters / g1-g4 / result。

Version: 1.0.0
Created: 2026-08-20 (Phase 2 / Step 8)
Migrated from: audit/gates.py:241-275 (run_gates + gates_passed)
"""

from __future__ import annotations

from .counters import _inc_block
from .g1_evidence import evidence_gate
from .g2_translation import translation_gate
from .g3_safety import safety_gate
from .g4_output import output_gate
from .result import GateResult


def run_gates(
    sir: dict,
    rendered_text: str,
    *,
    evidence_ids: set[str] | None = None,
    registry=None,
    schema_valid: bool = True,
    schema_errors: list[str] | None = None,
) -> list[GateResult]:
    """顺序调用四道 Gate（G1 → G2 → G3 → G4）。

    Fail-closed（§69）：任一门 BLOCK → 整体 BLOCK。block 计数随之累加
    （G*_block_rate 遥测）。
    """
    g1 = evidence_gate(sir, evidence_ids)
    g2 = translation_gate(sir, registry)
    g3 = safety_gate(rendered_text)
    g4 = output_gate(
        sir,
        g1=g1,
        g2=g2,
        g3=g3,
        schema_valid=schema_valid,
        schema_errors=schema_errors,
    )
    gates = [g1, g2, g3, g4]
    for g in gates:
        if not g.passed:
            _inc_block(g.gate)
    return gates


def gates_passed(gates: list[GateResult]) -> bool:
    return all(g.passed for g in gates)


__all__ = ["run_gates", "gates_passed"]
