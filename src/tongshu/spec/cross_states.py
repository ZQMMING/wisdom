"""Cross Analysis states (DECISION-003)."""

CROSS_STATES = frozenset({"ALIGNED", "PARTIAL", "CONFLICTED", "INSUFFICIENT"})

# Reason codes from canonical_content.schema.json
REASON_CODES = frozenset({
    "CROSS_TYPE_PARTIAL",
    "SHARED_SUPERTYPE",
    "OPPOSITE_DIRECTION",
    "SAME_SIGNAL_AGREE",
    "EVIDENCE_MISSING",
    "FORBIDDEN_EXCLUDED",
    "INSUFFICIENT_RULES",
    "RULE_DEPRECATED",
})
