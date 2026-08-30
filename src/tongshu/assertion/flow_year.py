# -*- coding: utf-8 -*-
"""向后兼容 shim：从 legacy.assertion_v1.flow_year 重导出。"""
from tongshu.legacy.assertion_v1.flow_year import FlowYearAssertionProducer  # noqa: F401

__all__ = ["FlowYearAssertionProducer"]
