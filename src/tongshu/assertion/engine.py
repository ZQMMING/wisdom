# -*- coding: utf-8 -*-
"""向后兼容 shim：从 legacy.assertion_v1.engine 重导出。"""
from tongshu.legacy.assertion_v1.engine import (  # noqa: F401
    AssertionEngine,
    AssertionProducer,
)

__all__ = ["AssertionEngine", "AssertionProducer"]
