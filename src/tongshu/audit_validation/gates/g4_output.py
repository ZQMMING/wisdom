"""G4 — Output Gate (V3.6 §22.4)。

输出聚合门：schema + 追踪性 + 版本族 + 各子门全过（§22.4）。

检查项：
    1. SIR schema 有效
    2. meta 含 request_id/trace_id/document_id（追踪性）
    3. meta 含§17 个版本变量（§17 versioning）
    4. G1/G2/G3 全过

依赖：result.py。

Version: 1.0.0
Created: 2026-08-20 (Phase 2 / Step 8)
Migrated from: audit/gates.py:172-204
"""

from __future__ import annotations

from .result import GateResult


def output_gate(
    sir: dict,
    *,
    g1: GateResult,
    g2: GateResult,
    g3: GateResult,
    schema_valid: bool,
    schema_errors: list[str] | None = None,
) -> GateResult:
    """G4 输出聚合门。"""
    reasons: list[str] = []
    if not schema_valid:
        reasons.append(f"Schema: invalid ({schema_errors})")

    meta = sir.get("meta")
    if meta is None:
        reasons.append("Traceability: meta missing")
    else:
        for k in ("request_id", "trace_id", "document_id"):
            if not meta.get(k):
                reasons.append(f"Traceability: meta.{k} missing")
        for v in (
            "schema_version",
            "calculation_version",
            "knowledge_version",
            "mapping_version",
            "translation_version",
            "audit_version",
            "model_version",
        ):
            if not meta.get(v):
                reasons.append(f"Versions: meta.{v} missing")

    if not g1.passed:
        reasons.append(f"G1 blocked: {g1.reasons[:3]}")
    if not g2.passed:
        reasons.append(f"G2 blocked: {g2.reasons[:3]}")
    if not g3.passed:
        reasons.append(f"G3 blocked: {g3.reasons[:3]}")

    return GateResult("G4", not reasons, reasons)


__all__ = ["output_gate"]
