"""G1 — Evidence Gate (V3.6 §22.1)。

SIR 证据链完整性：每条 claim 必须能沿 rule → evidence 链路追溯。

检查项（均为§22.1）：
    - rule_refs 非空（Rule linkage）
    - evidence_refs 非空（Evidence existence）且（提供 evidence_ids 时）全部解析
    - source_layers 非空（Derivation linkage）
    - claim_id 为 AC-* （Traceability）

依赖：result.py。

Version: 1.0.0
Created: 2026-08-20 (Phase 2 / Step 8)
Migrated from: audit/gates.py:75-99
"""

from __future__ import annotations

from .result import GateResult


def evidence_gate(sir: dict, evidence_ids: set[str] | None = None) -> GateResult:
    """G1 证据链完整性检查。"""
    reasons: list[str] = []
    claims = sir.get("atomic_claims", []) or []
    if not claims:
        reasons.append("no atomic_claims to evidence")
    for c in claims:
        cid = c.get("claim_id", "") or "?"
        if not c.get("rule_refs"):
            reasons.append(f"{cid}: empty rule_refs (Rule linkage)")
        refs = c.get("evidence_refs") or []
        if not refs:
            reasons.append(f"{cid}: empty evidence_refs (Evidence existence)")
        elif evidence_ids is not None:
            missing = [e for e in refs if e not in evidence_ids]
            if missing:
                reasons.append(f"{cid}: unresolved evidence_refs {sorted(missing)}")
        if not c.get("source_layers"):
            reasons.append(f"{cid}: empty source_layers (Derivation linkage)")
        if not str(cid).startswith("AC-"):
            reasons.append(f"{cid}: claim_id not AC-* (Traceability)")
    return GateResult("G1", not reasons, reasons)


__all__ = ["evidence_gate"]
