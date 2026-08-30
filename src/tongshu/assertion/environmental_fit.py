# -*- coding: utf-8 -*-
"""向后兼容 shim：从 legacy.assertion_v1.environmental_fit 重导出。"""
from tongshu.legacy.assertion_v1.environmental_fit import produce_environmental_fit  # noqa: F401

__all__ = ["produce_environmental_fit"]
