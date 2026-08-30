# -*- coding: utf-8 -*-
"""向后兼容 shim：直接从 legacy 重导出。"""
from tongshu.legacy.assertion_v1.topics import (  # noqa: F401
    CareerAssertionProducer,
    WealthAssertionProducer,
    MarriageAssertionProducer,
    HealthAssertionProducer,
)

__all__ = [
    "CareerAssertionProducer",
    "WealthAssertionProducer",
    "MarriageAssertionProducer",
    "HealthAssertionProducer",
]
