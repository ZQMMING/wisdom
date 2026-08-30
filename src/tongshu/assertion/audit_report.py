# -*- coding: utf-8 -*-
"""向后兼容 shim：从 legacy.assertion_v1.audit_report 重导出。"""
from tongshu.legacy.assertion_v1.audit_report import build_audit_report  # noqa: F401

__all__ = ["build_audit_report"]
