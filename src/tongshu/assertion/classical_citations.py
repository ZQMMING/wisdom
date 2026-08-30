# -*- coding: utf-8 -*-
"""向后兼容 shim：直接从 legacy 重导出。"""
from tongshu.legacy.assertion_v1.classical_citations import (  # noqa: F401
    CLASSICS,
    get_blind_citation,
    get_ziwei_citation,
    get_heluo_citation,
    get_strength_citation,
    get_ten_god_citation,
    get_tiaohou_citation,
    get_yijing_citation,
    get_citation,
)

__all__ = [
    "CLASSICS",
    "get_blind_citation",
    "get_ziwei_citation",
    "get_heluo_citation",
    "get_strength_citation",
    "get_ten_god_citation",
    "get_tiaohou_citation",
    "get_yijing_citation",
    "get_citation",
]
