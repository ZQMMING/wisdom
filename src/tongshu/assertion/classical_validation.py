# -*- coding: utf-8 -*-
"""向后兼容 shim：直接从 legacy 重导出。"""
from tongshu.legacy.assertion_v1.classical_validation import (  # noqa: F401
    CitationValidationResult,
    _cited_classics,
    cross_validate_systems,
    validate_assertion_refs,
)

__all__ = [
    "CitationValidationResult",
    "_cited_classics",
    "cross_validate_systems",
    "validate_assertion_refs",
]
