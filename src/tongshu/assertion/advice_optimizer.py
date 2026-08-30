# -*- coding: utf-8 -*-
"""向后兼容 shim：直接从 legacy 重导出。"""
from tongshu.legacy.assertion_v1.advice_optimizer import (  # noqa: F401
    AdviceCategory,
    AdviceItem,
    AdviceSource,
    cross_validate,
    detect_conflicts,
    deduplicate_advice,
    get_source_weight,
    make_advice,
    optimize_advice,
)

# get_system_weight 是 get_source_weight 的别名（来自 __all__）
get_system_weight = get_source_weight  # type: ignore[assignment]

__all__ = [
    "AdviceCategory",
    "AdviceItem",
    "AdviceSource",
    "cross_validate",
    "detect_conflicts",
    "deduplicate_advice",
    "get_source_weight",
    "get_system_weight",
    "make_advice",
    "optimize_advice",
]
