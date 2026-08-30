# -*- coding: utf-8 -*-
"""向后兼容 shim：直接从 legacy 重导出。"""
from tongshu.legacy.assertion_v1.advice_optimizer import (  # noqa: F401
    AdviceCategory,
    AdviceItem,
    AdviceSource,
    CONFLICT_PAIRS,
    SOURCE_BASE_WEIGHTS,
    cross_validate,
    deduplicate_advice,
    detect_conflicts,
    get_source_weight,
    make_advice,
    optimize_advice,
)

# 别名兼容
get_system_weight = get_source_weight  # noqa: F401

__all__ = [
    "AdviceCategory",
    "AdviceItem",
    "AdviceSource",
    "CONFLICT_PAIRS",
    "SOURCE_BASE_WEIGHTS",
    "cross_validate",
    "deduplicate_advice",
    "detect_conflicts",
    "get_source_weight",
    "get_system_weight",
    "make_advice",
    "optimize_advice",
]
