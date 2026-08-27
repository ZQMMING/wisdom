"""G*_block_rate 远测计数器。

按 V3.6 §63：G1-G4 各自的 block 计数（内存计数器）由 /health 对外暴露。
线程安全：threading.Lock 保护 dict 读写。

依赖：threading 仅。

Version: 1.0.0
Created: 2026-08-20 (Phase 2 / Step 8)
Migrated from: audit/gates.py:18-43 (_GATE_BLOCK_COUNTS / gate_block_counts / reset_gate_block_counts / _inc_block)
"""

from __future__ import annotations

import threading


_GATE_BLOCK_COUNTS: dict[str, int] = {"G1": 0, "G2": 0, "G3": 0, "G4": 0}
_COUNTS_LOCK = threading.Lock()


def gate_block_counts() -> dict[str, int]:
    """返图计数器快照（不可变）。"""
    with _COUNTS_LOCK:
        return dict(_GATE_BLOCK_COUNTS)


def reset_gate_block_counts() -> None:
    """重置计数器（仅限测试 / reset 调用）。"""
    with _COUNTS_LOCK:
        for k in _GATE_BLOCK_COUNTS:
            _GATE_BLOCK_COUNTS[k] = 0


def _inc_block(gate: str) -> None:
    """内部接口：给定 Gate 加 1。仅 run_gates 调用。"""
    with _COUNTS_LOCK:
        _GATE_BLOCK_COUNTS[gate] = _GATE_BLOCK_COUNTS.get(gate, 0) + 1


__all__ = ["gate_block_counts", "reset_gate_block_counts", "_inc_block"]
