"""audit_validation.gates — 审计 4 道 Gate 子包。

对齐 V3.6 §22-23 名称（G1/G2/G3/G4）：
    g1_evidence.py     — 证据链门（§22.1）
    g2_translation.py  — 词库标签链门（§22.2）
    g3_safety.py       — 安全门（§22.3）
    g4_output.py       — 输出聚合门（§22.4）
    runner.py          — run_gates() / gates_passed()
    result.py          — GateResult dataclass
    counters.py        — G*_block_rate 远测计数器（§63）

原 audit/gates.py 变为薄转发 shim（保持公共接口可用）。

调用方接口未变：
    from tongshu.audit.gates import run_gates, GateResult   # 仍可用
    from tongshu.audit_validation.gates import run_gates   # 新路径

Version: 1.0.0  Created: 2026-08-20 (Phase 2 / Step 8)
"""

from .counters import gate_block_counts, reset_gate_block_counts
from .g1_evidence import evidence_gate
from .g2_translation import translation_gate
from .g3_safety import safety_gate
from .g4_output import output_gate
from .result import GateResult
from .runner import gates_passed, run_gates


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
