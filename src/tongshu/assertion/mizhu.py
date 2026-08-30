# -*- coding: utf-8 -*-
"""向后兼容 shim：直接从 legacy 重导出。"""
from tongshu.legacy.assertion_v1.mizhu import MizhuProducer  # noqa: F401

__all__ = ["MizhuProducer"]
