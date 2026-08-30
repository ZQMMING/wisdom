# -*- coding: utf-8 -*-
"""断言层 contract 兼容层。

直接重导出 tongshu.assertion.contract，避免循环依赖。
"""
from tongshu.assertion.contract import (  # noqa: F401
    Assertion,
    AssertionInput,
    AssertionType,
    AuditFlag,
    Confidence,
    Direction,
    EvidenceRef,
    StateKind,
    insufficient_evidence,
    from_event_signal,
    FORBIDDEN_INPUT_FIELDS,
    InputBoundaryError,
)

__all__ = [
    "AssertionType", "Confidence", "Direction", "StateKind",
    "AssertionInput", "Assertion", "EvidenceRef", "AuditFlag",
    "InputBoundaryError", "FORBIDDEN_INPUT_FIELDS",
    "insufficient_evidence", "from_event_signal",
]
