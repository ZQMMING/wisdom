# -*- coding: utf-8 -*-
"""向后兼容 shim：从 legacy.assertion_v1.engine_evidence 重导出。"""
from tongshu.legacy.assertion_v1.engine_evidence import EngineName  # noqa: F401

__all__ = ["EngineName"]
