# -*- coding: utf-8 -*-
"""向后兼容 shim：从 legacy.assertion_v1.advice_optimizer 重导出。"""
from tongshu.legacy.assertion_v1.advice_optimizer import (  # noqa: F401
    AdviceOptimizer,
    forbid_financial_terms,
)

__all__ = ["AdviceOptimizer", "forbid_financial_terms"]
