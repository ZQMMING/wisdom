# -*- coding: utf-8 -*-
"""向后兼容 shim：tongshu.assertion → legacy.assertion_v1.*

策略：直接导出所有测试需要的符号，同时保留 __getattr__ 处理子模块访问。
"""
from __future__ import annotations
import sys
from types import ModuleType

# 直接从 contract 导入（无循环风险）
from tongshu.assertion.contract import (  # noqa: F401
    Assertion,
    AssertionInput,
    AssertionType,
    Confidence,
    Direction,
    EvidenceRef,
    StateKind,
    insufficient_evidence,
    from_event_signal,
    FORBIDDEN_INPUT_FIELDS,
    InputBoundaryError,
)

# 从 engine 导入
try:
    from tongshu.legacy.assertion_v1.engine import (  # noqa: F401
        AssertionEngine,
        AssertionProducer,
    )
except ImportError:
    pass

# 从 systems 导入
try:
    from tongshu.legacy.assertion_v1.systems import (  # noqa: F401
        ZiweiAssertionProducer,
        BlindAssertionProducer,
        HeluoAssertionProducer,
        ZipingAssertionProducer,
    )
except ImportError:
    pass

# 从 topics 导入
try:
    from tongshu.legacy.assertion_v1.topics import (  # noqa: F401
        CareerAssertionProducer,
        WealthAssertionProducer,
        MarriageAssertionProducer,
        HealthAssertionProducer,
    )
except ImportError:
    pass

# 其他符号尝试导入
for _mod, _attrs in [
    ("tongshu.legacy.assertion_v1.flow_year", ["FlowYearAssertionProducer"]),
    ("tongshu.legacy.assertion_v1.environmental_fit", ["produce_environmental_fit"]),
    ("tongshu.legacy.assertion_v1.mizhu", ["MizhuProducer"]),
    ("tongshu.legacy.assertion_v1.advice_optimizer", ["AdviceOptimizer", "forbid_financial_terms"]),
    ("tongshu.legacy.assertion_v1.classical_citations", ["CLASSICS", "get_blind_citation"]),
    ("tongshu.legacy.assertion_v1.engine_adapters", ["produce_all_evidence"]),
    ("tongshu.legacy.assertion_v1.engine_evidence", ["EngineName"]),
    ("tongshu.legacy.assertion_v1.audit_report", ["build_audit_report"]),
    ("tongshu.legacy.assertion_v1.classical_validation", ["CitationValidationResult", "classical_validation"]),
]:
    try:
        _m = __import__(_mod, fromlist=_attrs)
        for _a in _attrs:
            globals()[_a] = getattr(_m, _a)
    except (ImportError, AttributeError):
        pass

# 子模块注册（供 from tongshu.assertion.X import Y 使用）
_submodules = {
    "contract": "tongshu.assertion.contract",
    "engine": "tongshu.legacy.assertion_v1.engine",
    "systems": "tongshu.legacy.assertion_v1.systems",
    "topics": "tongshu.legacy.assertion_v1.topics",
    "flow_year": "tongshu.legacy.assertion_v1.flow_year",
    "environmental_fit": "tongshu.legacy.assertion_v1.environmental_fit",
    "mizhu": "tongshu.legacy.assertion_v1.mizhu",
    "advice_optimizer": "tongshu.legacy.assertion_v1.advice_optimizer",
    "classical_citations": "tongshu.legacy.assertion_v1.classical_citations",
    "engine_adapters": "tongshu.legacy.assertion_v1.engine_adapters",
    "engine_evidence": "tongshu.legacy.assertion_v1.engine_evidence",
    "audit_report": "tongshu.legacy.assertion_v1.audit_report",
    "classical_validation": "tongshu.legacy.assertion_v1.classical_validation",
}


def __getattr__(name: str):
    if name in _submodules:
        import importlib
        mod = importlib.import_module(_submodules[name])
        sys.modules[f"tongshu.assertion.{name}"] = mod
        return mod
    raise AttributeError(f"module 'tongshu.assertion' has no attribute '{name}'")


def __dir__() -> list[str]:
    return list(globals().keys()) + list(_submodules.keys())
