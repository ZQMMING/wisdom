"""OTC-G V3.6 §22-23 审计四道 Gate — **过渡 shim**。

Phase 2 / Step 8 产出：原 275 行均已迁出至 audit_validation/gates/ 子包（一个
Gate / counters / result / runner 一个文件）。本文件仅重导出公共符号以保持向后兼容。
新代码请直接 import 自 tongshu.audit_validation.gates。

原始实现已迁出（保持原始行为）：
    audit_validation/gates/result.py          GateResult dataclass
    audit_validation/gates/counters.py        G*_block_rate 计数器（§63）
    audit_validation/gates/g1_evidence.py     G1 证据链门（§22.1）
    audit_validation/gates/g2_translation.py  G2 词库标签链门（§22.2）
    audit_validation/gates/g3_safety.py       G3 安全门（§22.3）
    audit_validation/gates/g4_output.py       G4 输出聚合门（§22.4）
    audit_validation/gates/runner.py          run_gates + gates_passed

Migrated: 2026-08-20 (Phase 2 / Step 8)
"""

from __future__ import annotations

from tongshu.audit_validation.gates import (
    GateResult,
    evidence_gate,
    gate_block_counts,
    gates_passed,
    output_gate,
    reset_gate_block_counts,
    run_gates,
    safety_gate,
    translation_gate,
)

__all__ = [
    "GateResult",
    "evidence_gate",
    "translation_gate",
    "safety_gate",
    "output_gate",
    "run_gates",
    "gates_passed",
    "gate_block_counts",
    "reset_gate_block_counts",
]
