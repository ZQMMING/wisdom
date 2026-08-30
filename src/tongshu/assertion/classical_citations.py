# -*- coding: utf-8 -*-
"""向后兼容 shim：从 legacy.assertion_v1.classical_citations 重导出。"""
from tongshu.legacy.assertion_v1.classical_citations import (  # noqa: F401
    CLASSICS,
    get_blind_citation,
    get_heluo_citation,
    get_yijing_citation,
    get_ziwei_citation,
)

__all__ = [
    "CLASSICS",
    "get_blind_citation",
    "get_heluo_citation",
    "get_yijing_citation",
    "get_ziwei_citation",
]
