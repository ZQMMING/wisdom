"""审计 Gate 返回结果数据类。

依赖：无。

Version: 1.0.0
Created: 2026-08-20 (Phase 2 / Step 8)
Migrated from: audit/gates.py:38-49 (GateResult)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GateResult:
    gate: str
    passed: bool
    reasons: list[str]

    def to_dict(self) -> dict:
        return {
            "gate": self.gate,
            "passed": self.passed,
            "reasons": list(self.reasons),
        }


__all__ = ["GateResult"]
