# -*- coding: utf-8 -*-
"""向后兼容 shim：直接从 legacy 重导出。"""
from tongshu.legacy.assertion_v1.environmental_fit import (  # noqa: F401
    GENERATES,
    OVERCOMES,
    SECTOR_CHINESE,
    SECTOR_ELEMENT,
    produce_environmental_fit,
)

__all__ = [
    "GENERATES",
    "OVERCOMES",
    "SECTOR_CHINESE",
    "SECTOR_ELEMENT",
    "produce_environmental_fit",
]
