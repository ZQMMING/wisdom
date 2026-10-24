"""契约层子模块转发（单一来源 = ``heluo_engine.spec.canonical.engine_evidence``）。

⚠ 2026-10-24 河洛回灌：本文件原先**独立定义** EngineName / TemporalScope /
   EngineEvidence，与 ``heluo_engine/spec/canonical/engine_evidence.py``
   字节相同但**类身份不同** ⇒ 跨包 isinstance 恒为 False。
   现改为纯转发，实体定义只在 vendor 侧存在一份。

保留本子模块路径仅为兼容既有直接 import
（如 ``from tongshu.spec.canonical.engine_evidence import EngineEvidence``）。
"""
from __future__ import annotations

from heluo_engine.spec.canonical.engine_evidence import (
    EngineEvidence,
    EngineName,
    TemporalScope,
)

__all__ = ["EngineEvidence", "EngineName", "TemporalScope"]
