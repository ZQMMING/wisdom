"""tongshu.assertion backward compatibility shim.

Re-exports from legacy.assertion_v1 to preserve old import paths.
"""
from tongshu.legacy.assertion_v1.contract import (  # noqa: F401
    Assertion,
    AssertionInput,
    AssertionType,
    Confidence,
    Direction,
    EvidenceRef,
    StateKind,
    insufficient_evidence,
)
from tongshu.legacy.assertion_v1.classical_validation import (  # noqa: F401
    CitationValidationResult,
    _cited_classics,
    cross_validate_systems,
    validate_assertion_refs,
)
from tongshu.legacy.assertion_v1.audit_report import (  # noqa: F401
    build_audit_report,
)
from tongshu.legacy.assertion_v1.engine import (  # noqa: F401
    AssertionEngine,
    AssertionProducer,
)
from tongshu.legacy.assertion_v1.engine_adapters import (  # noqa: F401
    produce_all_evidence,
)
from tongshu.legacy.assertion_v1.engine_evidence import (  # noqa: F401
    EngineName,
)
from tongshu.legacy.assertion_v1.environmental_fit import (  # noqa: F401
    produce_environmental_fit,
)
from tongshu.legacy.assertion_v1.flow_year import (  # noqa: F401
    FlowYearAssertionProducer,
)
from tongshu.legacy.assertion_v1.systems import (  # noqa: F401
    BlindAssertionProducer,
    HeluoAssertionProducer,
    ZiweiAssertionProducer,
)
from tongshu.legacy.assertion_v1.topics import (  # noqa: F401
    aggregate_directions_weighted,
    _aggregate_directions_weighted,
    _detect_conflict,
    compute_topic_direction,
)
from tongshu.legacy.assertion_v1.classical_citations import (  # noqa: F401
    CLASSICS,
    get_blind_citation,
    get_heluo_citation,
    get_yijing_citation,
    get_ziwei_citation,
)
from tongshu.legacy.assertion_v1.advice_optimizer import (  # noqa: F401
    AdviceOptimizer,
    forbid_financial_terms,
)
from tongshu.legacy.assertion_v1.mizhu import (  # noqa: F401
    MizhuProducer,
)

__all__ = [
    "Assertion",
    "AssertionType",
    "Direction",
    "Confidence",
    "AssertionEngine",
    "AssertionProducer",
    "validate_assertion_refs",
    "cross_validate_systems",
    "build_audit_report",
    "produce_all_evidence",
    "EngineName",
    "produce_environmental_fit",
    "FlowYearAssertionProducer",
    "ZiweiAssertionProducer",
    "BlindAssertionProducer",
    "HeluoAssertionProducer",
    "CLASSICS",
    "get_ziwei_citation",
    "get_blind_citation",
    "get_heluo_citation",
    "get_yijing_citation",
    "AdviceOptimizer",
    "forbid_financial_terms",
    "MizhuProducer",
]
