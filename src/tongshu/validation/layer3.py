"""Layer 3 — Entailment judge. **过渡 shim**。

Phase 2 / Step 8 产出：原 78 行均已迁出至
audit_validation/validators/layer3_entailment.py。本文件仅重导出公共符号。

Migrated: 2026-08-20 (Phase 2 / Step 8)
"""

from __future__ import annotations

from tongshu.audit_validation.validators import Layer3Result, validate_layer3

__all__ = ["Layer3Result", "validate_layer3"]
