# -*- coding: utf-8 -*-
"""向后兼容 shim：直接从 legacy 重导出。"""
from tongshu.legacy.assertion_v1.engine_evidence import EngineName  # noqa: F401

__all__ = ["EngineName"]
