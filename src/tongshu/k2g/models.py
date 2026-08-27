# K2G Python 数据模型 V1.0

"""
K2G (Knowledge to Guidance) 核心数据模型。
对应数据库 schema: backend/src/tongshu/k2g/schema/k2g_schema.sql
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# 枚举定义
# ============================================================

class Domain(Enum):
    BAZI = "BAZI"
    BLIND = "BLIND"
    ZIWEI = "ZIWEI"
    YIJING = "YIJING"
    HELUO = "HELUO"
    TONGSHU = "TONGSHU"


class ConceptType(Enum):
    TEN_GOD = "TEN_GOD"
    FIVE_ELEMENTS = "FIVE_ELEMENTS"
    DAY_MASTER = "DAY_MASTER"
    STRENGTH = "STRENGTH"
    STRUCTURE = "STRUCTURE"
    COMBINATIONS = "COMBINATIONS"
    RELATIONAL = "RELATIONAL"
    SHEN_SHA = "SHEN_SHA"
    DA_YUN = "DA_YUN"
    LIU_NIAN = "LIU_NIAN"


class RelationType(Enum):
    SUPPORT = "SUPPORT"
    CONTRADICT = "CONTRADICT"
    QUALIFY = "QUALIFY"
    AMPLIFY = "AMPLIFY"
    REDUCE = "REDUCE"
    COMPLEMENT = "COMPLEMENT"
    CONFLICT = "CONFLICT"
    SEQUENCE = "SEQUENCE"
    CONDITION = "CONDITION"


class ParentTheme(Enum):
    XING = "XING"    # 行
    SHI = "SHI"      # 事
    REN = "REN"      # 人
    JU = "JU"        # 居
    YANG = "YANG"    # 养
    SHI_T = "SHI_T"  # 时


class ActionTypeEnum(Enum):
    EXECUTION = "execution"
    REFLECTION = "reflection"
    COMMUNICATION = "communication"
    ADJUSTMENT = "adjustment"
    REST = "rest"


class SafetySeverity(Enum):
    BLOCK = "BLOCK"
    WARN = "WARN"
    INFO = "INFO"


class VerificationStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"


# ============================================================
# 基础数据类
# ============================================================

@dataclass
class SourceRef:
    """传统文献引用"""
    canonical: str          # 如 "子平真诠·十神篇"
    passage_id: str         # 如 "ZPZ_TG_001"


@dataclass
class SemanticLevel:
    """信号强度级别"""
    level: str              # "low" | "medium" | "high"
    confidence: float       # 0.0 - 1.0


# ============================================================
# 1. Concept Registry
# ============================================================

@dataclass
class Concept:
    concept_id: str
    domain: Domain
    school: Optional[str]
    concept_type: ConceptType
    traditional_term: str
    alternative_terms: List[str] = field(default_factory=list)
    canonical_definition: Optional[Dict[str, str]] = None
    source_refs: List[SourceRef] = field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.PENDING
    evidence_refs: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def is_approved(self) -> bool:
        return self.verification_status == VerificationStatus.APPROVED


# ============================================================
# 2. Semantic Registry
# ============================================================

@dataclass
class Semantic:
    semantic_id: str
    canonical_label: str
    short_label: Optional[str]
    keywords: Dict[str, List[str]] = field(
        default_factory=lambda: {"positive": [], "negative": []}
    )
    dimensions: List[str] = field(default_factory=list)
    allowed_context: List[str] = field(default_factory=list)
    forbidden_claims: List[str] = field(default_factory=list)
    related_semantics: List[str] = field(default_factory=list)
    parent_theme: ParentTheme = ParentTheme.SHI
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


# ============================================================
# 3. Mapping Registry
# ============================================================

@dataclass
class TargetSemantic:
    semantic_id: str
    weight: float = 1.0


@dataclass
class Mapping:
    mapping_id: str
    source_domain: Domain
    source_school: Optional[str]
    source_concept: str
    trigger: Dict[str, Any]
    target_semantics: List[TargetSemantic]
    mapping_type: str = "semantic"
    allowed_context: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    rule_refs: List[str] = field(default_factory=list)
    conflict_resolution: Optional[Dict[str, str]] = None


# ============================================================
# 4. Relation Registry
# ============================================================

@dataclass
class RelationInput:
    semantic_id: str
    direction: str = "positive"  # "positive" | "negative"


@dataclass
class Relation:
    relation_id: str
    inputs: List[RelationInput]
    relation_type: RelationType
    output: Dict[str, Any]
    conditions: List[str] = field(default_factory=list)
    fallback: Optional[Dict[str, Any]] = None


# ============================================================
# 5. Context Registry
# ============================================================

@dataclass
class Context:
    context_id: str
    parent_theme: ParentTheme
    product_label: str
    aliases: List[str] = field(default_factory=list)
    allowed_semantics: List[str] = field(default_factory=list)
    forbidden_semantics: List[str] = field(default_factory=list)
    usage_rules: List[str] = field(default_factory=list)
    related_contexts: List[str] = field(default_factory=list)


# ============================================================
# 6. State Registry
# ============================================================

@dataclass
class SupportingSignal:
    domain: Domain
    semantic: str
    relation: str
    evidence_refs: List[str] = field(default_factory=list)


@dataclass
class State:
    state_id: str
    signals: Dict[str, SemanticLevel]
    supporting_signals: List[SupportingSignal] = field(default_factory=list)
    transition_rules: List[Dict[str, Any]] = field(default_factory=list)
    evidence_provenance: Optional[Dict[str, Any]] = None


# ============================================================
# 7. Daily Guidance Registry (DGR)
# ============================================================

@dataclass
class GuidanceComponent:
    semantic_id: str
    priority: int = 50


@dataclass
class DailyGuidance:
    guidance_id: str
    state_conditions: List[Dict[str, Any]]
    context: List[Dict[str, str]]
    theme: Optional[GuidanceComponent] = None
    opportunity: Optional[GuidanceComponent] = None
    risk: Optional[GuidanceComponent] = None
    action: Optional[GuidanceComponent] = None
    rhythm: Optional[GuidanceComponent] = None
    priority: int = 50
    evidence_refs: List[str] = field(default_factory=list)
    mapping_refs: List[str] = field(default_factory=list)
    relation_refs: List[str] = field(default_factory=list)


# ============================================================
# 8. Action Registry
# ============================================================

@dataclass
class ActionTemplate:
    locale: str
    text: str
    length: str = "medium"  # "short" | "medium" | "long"


@dataclass
class Action:
    action_id: str
    semantic_id: str
    context: str
    action_type: ActionTypeEnum
    templates: List[ActionTemplate] = field(default_factory=list)
    forbidden_phrases: List[str] = field(default_factory=list)
    constraints: Dict[str, str] = field(default_factory=dict)
    related_semantics: List[str] = field(default_factory=list)


# ============================================================
# 9. Expression Registry
# ============================================================

@dataclass
class ExpressionVariant:
    id: str
    tone: str
    length: str
    text: str


@dataclass
class Expression:
    expression_id: str
    semantic_id: str
    action_ref: Optional[str]
    style: Dict[str, Any] = field(default_factory=dict)
    text: Dict[str, List[str]] = field(
        default_factory=lambda: {"zh": [], "en": []}
    )
    variants: List[ExpressionVariant] = field(default_factory=list)
    forbidden_patterns: List[str] = field(default_factory=list)
    locale: str = "zh-CN"


# ============================================================
# 10. Safety Registry
# ============================================================

@dataclass
class SafetyRule:
    safety_rule_id: str
    rule_type: str
    severity: SafetySeverity
    description: str
    patterns: List[str]
    applies_to: List[str]
    check_level: str = "pre_output"

    def matches(self, text: str) -> bool:
        import re
        for pattern in self.patterns:
            if re.search(pattern, text):
                return True
        return False


# ============================================================
# 横表模型
# ============================================================

@dataclass
class EvidenceBinding:
    binding_id: str
    concept_id: Optional[str]
    mapping_id: Optional[str]
    evidence_id: str
    source_layer: str
    binding_type: str  # "supports" | "conflicts" | "qualifies"


@dataclass
class GoldenCase:
    case_id: str
    domain: Domain
    case_type: str
    input_profile: Dict[str, Any]
    expected_state: str
    expected_guidance: str
    expected_action: str
    expected_expression: Optional[str]
    source_ref: Optional[str]
    verification_status: str = "pending"


@dataclass
class K2gVersion:
    version: str
    change_type: str  # "MAJOR" | "MINOR" | "PATCH"
    description: str
    changed_by: str
    affected_tables: List[str] = field(default_factory=list)
    backward_compatible: bool = True


# ============================================================
# 引擎输出模型
# ============================================================

@dataclass
class DeterministicGuidance:
    state: State
    theme: GuidanceComponent
    opportunity: GuidanceComponent
    risk: GuidanceComponent
    action: GuidanceComponent
    rhythm: GuidanceComponent


@dataclass
class PresentationOutput:
    text: str
    locale: str
    tone: str
    ai_enhanced: bool
    ai_model: Optional[str] = None


@dataclass
class ProvenanceChain:
    calculation_refs: List[str]
    rule_refs: List[str]
    mapping_refs: List[str]
    relation_refs: List[str]
    state_ref: str
    guidance_ref: str
    action_refs: List[str]
    expression_ref: str
    evidence_refs: List[str]
    ai_enhanced: bool
    ai_generated: bool
    ai_inference: bool

    @classmethod
    def empty(cls) -> "ProvenanceChain":
        return cls(
            calculation_refs=[],
            rule_refs=[],
            mapping_refs=[],
            relation_refs=[],
            state_ref="",
            guidance_ref="",
            action_refs=[],
            expression_ref="",
            evidence_refs=[],
            ai_enhanced=False,
            ai_generated=False,
            ai_inference=False,
        )


@dataclass
class SafetyCheckResult:
    passed: bool
    violations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class K2gOutput:
    deterministic_guidance: DeterministicGuidance
    presentation_output: PresentationOutput
    provenance: ProvenanceChain
    safety_check: SafetyCheckResult
    ai_enhanced: bool = False
    ai_model: Optional[str] = None
    fallback_reason: Optional[str] = None
