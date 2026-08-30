# -*- coding: utf-8 -*-
"""向后兼容 shim：从 legacy.assertion_v1.systems 重导出。"""
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
