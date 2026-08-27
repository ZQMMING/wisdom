"""Layer 2 — Embedding semantic similarity. **过渡 shim**。

Phase 2 / Step 8 产出：原 101 行均已迁出至
audit_validation/validators/layer2_similarity.py。本文件仅重导出公共符号
（含 THRESHOLD 以保持可能被外部引用）。

Migrated: 2026-08-20 (Phase 2 / Step 8)
"""

from __future__ import annotations

from tongshu.audit_validation.validators import Layer2Result, validate_layer2
from tongshu.audit_validation.validators.layer2_similarity import (
    THRESHOLD,
    _char_overlap_similarity,
)

__all__ = ["Layer2Result", "validate_layer2", "_char_overlap_similarity", "THRESHOLD"]
