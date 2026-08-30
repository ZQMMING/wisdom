# -*- coding: utf-8 -*-
"""向后兼容 shim：直接从 legacy 重导出。"""
from tongshu.legacy.assertion_v1.engine_adapters import produce_all_evidence  # noqa: F401

__all__ = ["produce_all_evidence"]
