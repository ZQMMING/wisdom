# -*- coding: utf-8 -*-
"""向后兼容 shim：直接从 legacy 重导出。"""
from tongshu.legacy.assertion_v1.systems import (  # noqa: F401
    ZiweiAssertionProducer,
    BlindAssertionProducer,
    HeluoAssertionProducer,
    ZipingAssertionProducer,
)

__all__ = [
    "ZiweiAssertionProducer",
    "BlindAssertionProducer",
    "HeluoAssertionProducer",
    "ZipingAssertionProducer",
]
