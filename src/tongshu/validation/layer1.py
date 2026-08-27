"""Layer 1 — Deterministic validation. **过渡 shim**。

Phase 2 / Step 8 产出：原 138 行均已迁出至
audit_validation/validators/layer1_claim.py。本文件仅重导出公共符号。

Migrated: 2026-08-20 (Phase 2 / Step 8)
"""

from __future__ import annotations

from tongshu.audit_validation.validators import Layer1Result, validate_layer1

__all__ = ["Layer1Result", "validate_layer1"]
