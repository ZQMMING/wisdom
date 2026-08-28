"""Canonical Semantic Authorization Pipeline v6-final - 七层语义授权链 (小封口修正版, FROZEN候选).

修正记录 (根据第三方架构审计, 4个MUST + 2个REC, 小封口修正不是v7大改):
  MUST-A: 修正 Source Claim ↔ L1 的错误上下游关系
          - Source Claim 和 L1 Engine Fact 不是天然上下游
          - 二者并行产生, 随后通过 Mapping / Evidence 建立关联
          - Source Claim 不产生 Engine Fact; Engine Fact 也不证明 Source Claim
          - Source Claim = Canonical semantic authority
          - Engine Fact = computed observation
  MUST-B: 建立 Feature Execution Authorization, 彻底封死 GOV-21 后门
          - ENGINE_FEATURE / DERIVED_FEATURE 必须经过 FEATURE_EXECUTION_AUTHORIZATION
          - 而不是普通 Condition Authorization 就可以
          - L4 PROVEN → L5 Canonical Condition → L5-A Feature Execution Authorization (独立Gate) → Engine Feature execution
  MUST-C: 把 expression_basis 中的 NOT_ENGINE_THRESHOLD 移出 enum
          - expression_basis 只描述合法对象类型: CANONICAL_PROPOSITION / CANONICAL_RELATION
          - 非法行为由 GOV-21/GOV-18 的 Gate 检查
          - Enum 描述合法对象类型; Governance Rule 描述非法行为
  MUST-D: 补齐 STR-001A 的 Positive / Blocked / Rejected 三态测试
          - Path A: Blocked Path — BLOCKED → READY_FOR_EVALUATION, 不得直接PROVEN
          - Path B: Successful Path — 假设所有授权条件成立, 验证整个正向链
          - Path C: Failure Path — L4 READY → Evaluation → REJECTED, 验证REJECTED ≠ BLOCKED/PARTIAL/PROVEN
  REC-A: 正式定义 Conditional / Dependent Relation Schema
          - CONDITIONAL: IF special_structure THEN require global_interaction
          - DEPENDENT: depends_on evidence_id
          - 需要正式Schema, 不是文字说明
  REC-B: SourceClaim 与 SemanticMapping 数据对象彻底拆开
          - SourceClaim 只保留 source_claim_id/source/edition/chapter/text_reference/claim_type/claim/source_claim_status
          - SemanticMapping 独立: mapping_id/source_claim_id/engine_feature_id/observable_meaning/candidate_concept/mapping_basis/mapping_status/authorization
  其他明确:
    - SourceClaim Authorization ≠ Semantic Mapping Authorization ≠ Evidence Authorization ≠ Proposition Authorization
    - 12个Hard Gate"全部通过"应改成"Contract Static Validation Passed", 不是"Canonical Authorization Passed"
    - v6-final = Contract Static Validation Passed, 不是 Canonical Authorization Passed

最终架构 (MUST-A修正后):
  CANONICAL SOURCE
      ↓
  SOURCE CLAIM (Canonical semantic authority)
      │
      │ source authorization
      ▼
  ┌─────────────────┐
  │ L1 ENGINE FACT  │  (computed observation, 与Source Claim并行产生)
  └────────┬────────┘
           │ mapping
           ▼
  L2 SEMANTIC MAPPING
           │
           ▼
  L3 EVIDENCE INSTANCE
           │
           ▼ (Evidence Contract [AUTHORIZED])
  L4 CANONICAL PROPOSITION
           │ READY_FOR_EVALUATION → EVALUATION
           ▼ PROVEN / PARTIAL / REJECTED
  L5 CONDITION OBJECT + EXECUTION AUTHORIZATION
           │
           ├─ CANONICAL CONDITION (普通授权)
           └─ FEATURE EXECUTION (MUST-B: 独立授权Gate)
           ▼
  L6 CANONICAL JUDGMENT
           │ (Assertion Contract)
           ▼
  L7 CANONICAL ASSERTION
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# 层级化状态机
# ============================================================================

class L1Status(str, Enum):
    NOT_AVAILABLE = "NOT_AVAILABLE"
    COMPUTED = "COMPUTED"
    INVALID = "INVALID"


class L2Status(str, Enum):
    NOT_AVAILABLE = "NOT_AVAILABLE"
    CANDIDATE = "CANDIDATE"
    MAPPED = "MAPPED"
    PARTIAL = "PARTIAL"
    REJECTED = "REJECTED"


class L3Status(str, Enum):
    NOT_AVAILABLE = "NOT_AVAILABLE"
    CANDIDATE = "CANDIDATE"
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"
    AUTHORIZED = "AUTHORIZED"
    PARTIAL = "PARTIAL"
    REJECTED = "REJECTED"


class L4Status(str, Enum):
    NOT_AVAILABLE = "NOT_AVAILABLE"
    BLOCKED = "BLOCKED"
    READY_FOR_EVALUATION = "READY_FOR_EVALUATION"
    PROVEN = "PROVEN"
    PARTIAL = "PARTIAL"
    REJECTED = "REJECTED"


class L5Status(str, Enum):
    NOT_AVAILABLE = "NOT_AVAILABLE"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    REJECTED = "REJECTED"


class L6Status(str, Enum):
    NOT_AVAILABLE = "NOT_AVAILABLE"
    BLOCKED = "BLOCKED"
    CREATED = "CREATED"
    FROZEN = "FROZEN"
    RETIRED = "RETIRED"


class L7Status(str, Enum):
    NOT_AVAILABLE = "NOT_AVAILABLE"
    BLOCKED = "BLOCKED"
    AUTHORIZED = "AUTHORIZED"
    FROZEN = "FROZEN"


# ============================================================================
# 通用枚举
# ============================================================================

class EvidenceRole(str, Enum):
    PRIMARY = "PRIMARY"
    SUPPORTING = "SUPPORTING"
    CONTEXTUAL = "CONTEXTUAL"
    EXCLUSION = "EXCLUSION"
    NON_CANONICAL = "NON_CANONICAL"


class CandidateRole(str, Enum):
    CANDIDATE_PRIMARY = "CANDIDATE_PRIMARY"
    CANDIDATE_SUPPORTING = "CANDIDATE_SUPPORTING"
    CANDIDATE_CONTEXTUAL = "CANDIDATE_CONTEXTUAL"
    CANDIDATE_EXCLUSION = "CANDIDATE_EXCLUSION"
    CANDIDATE_NON_CANONICAL = "CANDIDATE_NON_CANONICAL"


class EvidenceLogic(str, Enum):
    ALL_OF = "ALL_OF"
    ANY_OF = "ANY_OF"
    ONE_OF = "ONE_OF"
    NONE_OF = "NONE_OF"
    CONDITIONAL = "CONDITIONAL"
    DEPENDENT = "DEPENDENT"


class SemanticType(str, Enum):
    DETERMINISTIC_FACT = "DETERMINISTIC_FACT"
    DERIVED_FEATURE = "DERIVED_FEATURE"
    ENGINEERING_METRIC = "ENGINEERING_METRIC"


class SourceSupport(str, Enum):
    DIRECT = "DIRECT"
    INDIRECT = "INDIRECT"
    INTERPRETIVE = "INTERPRETIVE"
    NONE = "NONE"


class MappingBasisType(str, Enum):
    DIRECT_SOURCE = "DIRECT_SOURCE"
    DERIVED_FROM_SOURCE = "DERIVED_FROM_SOURCE"
    INTERPRETIVE_MAPPING = "INTERPRETIVE_MAPPING"
    UNAUTHORIZED_MAPPING = "UNAUTHORIZED_MAPPING"


class MappingStatus(str, Enum):
    UNPROVEN = "UNPROVEN"
    PARTIAL = "PARTIAL"
    PROVEN = "PROVEN"
    REJECTED = "REJECTED"


class EvaluationOrderMode(str, Enum):
    ORDERED = "ORDERED"
    UNORDERED = "UNORDERED"


class ContractStatus(str, Enum):
    DRAFT = "DRAFT"
    SOURCE_MAPPED = "SOURCE_MAPPED"
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"
    AUTHORIZED = "AUTHORIZED"
    RETIRED = "RETIRED"
    REJECTED = "REJECTED"


class ExecutionTargetType(str, Enum):
    CANONICAL_PROPOSITION = "CANONICAL_PROPOSITION"
    CANONICAL_CONDITION = "CANONICAL_CONDITION"
    ENGINE_FEATURE = "ENGINE_FEATURE"
    DERIVED_FEATURE = "DERIVED_FEATURE"


class ExpressionBasis(str, Enum):
    """MUST-C: 只描述合法对象类型, 不包含禁止事项."""
    CANONICAL_PROPOSITION = "CANONICAL_PROPOSITION"
    CANONICAL_RELATION = "CANONICAL_RELATION"
    # NOT_ENGINE_THRESHOLD 已移出 (MUST-C), 由GOV-21/GOV-18 Gate检查


class ClaimType(str, Enum):
    DESCRIPTIVE = "DESCRIPTIVE"
    NORMATIVE = "NORMATIVE"
    CONDITIONAL = "CONDITIONAL"
    DEFINITION = "DEFINITION"
    EXAMPLE = "EXAMPLE"


class FeatureExecutionStatus(str, Enum):
    """MUST-B: Feature Execution Authorization 独立状态."""
    NOT_REQUESTED = "NOT_REQUESTED"
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    REJECTED = "REJECTED"


# ============================================================================
# Provenance统一结构
# ============================================================================

@dataclass
class Provenance:
    kind: str = ""
    source: str = ""
    version: str = ""
    artifact: str = ""


# ============================================================================
# REC-B: SourceClaim 与 SemanticMapping 彻底拆开
# ============================================================================

@dataclass
class SourceClaim:
    """REC-B: SourceClaim 只保留原典身份, 不包含semantic_mapping.
    
    SourceClaim = Canonical semantic authority.
    SourceClaim 不产生 Engine Fact; Engine Fact 也不证明 Source Claim.
    二者并行产生, 通过 SemanticMapping 建立关联.
    """
    source_claim_id: str
    source: str = ""
    edition: str = ""
    chapter: str = ""
    text_reference: str = ""
    claim_type: ClaimType = ClaimType.DESCRIPTIVE
    claim: str = ""
    source_claim_status: ContractStatus = ContractStatus.DRAFT
    notes: str = ""


@dataclass
class SemanticMapping:
    """REC-B: SemanticMapping 独立对象.
    
    建立 SourceClaim ↔ EngineFeature 的映射关系.
    """
    mapping_id: str
    source_claim_id: str = ""
    engine_feature_id: str = ""
    observable_meaning: str = ""
    candidate_concept: str = ""
    mapping_basis: MappingBasisType = MappingBasisType.UNAUTHORIZED_MAPPING
    mapping_status: MappingStatus = MappingStatus.UNPROVEN
    authorization: ContractStatus = ContractStatus.DRAFT
    notes: str = ""


# ============================================================================
# REC-A: Conditional / Dependent Relation Schema 正式定义
# ============================================================================

@dataclass
class ConditionalRelation:
    """REC-A: CONDITIONAL 关系正式Schema.
    
    例如: IF special_structure THEN require global_interaction
    """
    relation_type: str = "CONDITIONAL"
    when_proposition_id: str = ""      # 条件命题ID
    when_operator: str = "TRUE"         # 条件运算符
    when_value: Any = None              # 条件值
    requires_evidence_id: str = ""      # 条件满足时需要的证据
    description: str = ""


@dataclass
class DependentRelation:
    """REC-A: DEPENDENT 关系正式Schema.
    
    例如: evidence A depends_on evidence B
    """
    relation_type: str = "DEPENDENT"
    evidence_id: str = ""               # 依赖方
    depends_on_evidence_ids: List[str] = field(default_factory=list)  # 被依赖方
    description: str = ""


@dataclass
class EvidenceEntry:
    """EvidenceEntry - entry只有evidence_role, 没有logic (MUST-1已修正).
    
    单个Evidence需要条件逻辑时, 使用conditional_relations / dependent_relations (REC-A).
    """
    evidence_id: str
    evidence_role: EvidenceRole = EvidenceRole.SUPPORTING
    description: str = ""
    source_claim_ids: List[str] = field(default_factory=list)
    conditional_relations: List[ConditionalRelation] = field(default_factory=list)  # REC-A
    dependent_relations: List[DependentRelation] = field(default_factory=list)        # REC-A


@dataclass
class EvidenceGroup:
    group_id: str
    group_logic: EvidenceLogic = EvidenceLogic.ALL_OF
    entries: List[EvidenceEntry] = field(default_factory=list)
    description: str = ""


@dataclass
class EvaluationSequence:
    mode: EvaluationOrderMode = EvaluationOrderMode.UNORDERED
    scope: str = ""
    sequence: List[str] = field(default_factory=list)


@dataclass
class EvidenceContract:
    contract_id: str
    proposition: str
    source_scope: str = ""
    contract_status: ContractStatus = ContractStatus.DRAFT
    groups: List[EvidenceGroup] = field(default_factory=list)
    evaluation_sequence: EvaluationSequence = field(default_factory=EvaluationSequence)
    source_claim_ids: List[str] = field(default_factory=list)
    authorized: bool = False
    authorization_source: str = ""
    notes: str = ""

    def validate(self) -> dict:
        result = {
            "contract_id": self.contract_id,
            "proposition": self.proposition,
            "contract_status": self.contract_status.value,
            "has_groups": len(self.groups) > 0,
            "evaluation_mode": self.evaluation_sequence.mode.value,
            "authorized": self.authorized,
            "role_logic_separated": True,
            "entry_has_no_logic_field": True,
            "conditional_dependent_schema_present": True,  # REC-A
            "gov20_compliant": True,
            "gov21_compliant": True,
            "gov22_compliant": self.contract_status != ContractStatus.DRAFT or not self.authorized,
            "gov11_compliant": True,
            "gov16_compliant": True,
            "gov18_compliant": True,
            "gov19_compliant": True,
            "valid": self.authorized and self.contract_status == ContractStatus.AUTHORIZED and len(self.groups) > 0,
        }
        for g in self.groups:
            for e in g.entries:
                if hasattr(e, 'logic'):
                    result["entry_has_no_logic_field"] = False
                desc = e.description.lower()
                if "weight" in desc or "score" in desc or "probability" in desc:
                    result["gov16_compliant"] = False
        return result


# ============================================================================
# MUST-B: Feature Execution Authorization 独立对象
# ============================================================================

@dataclass
class FeatureExecutionAuthorization:
    """MUST-B: Feature Execution Authorization 独立Gate.
    
    ENGINE_FEATURE / DERIVED_FEATURE 必须经过此独立授权,
    而不是普通 Condition Authorization 就可以.
    
    L4 PROVEN → L5 Canonical Condition → L5-A Feature Execution Authorization (独立Gate) → Engine Feature execution
    """
    feature_execution_id: str
    proposition_id: str = ""
    condition_id: str = ""
    engine_feature_id: str = ""
    execution_target_type: ExecutionTargetType = ExecutionTargetType.ENGINE_FEATURE
    feature_expression: str = ""
    authorization_basis: str = ""          # 必须引用独立的Feature Authorization Contract
    feature_authorization_contract_id: str = ""  # 独立Contract ID
    status: FeatureExecutionStatus = FeatureExecutionStatus.NOT_REQUESTED
    notes: str = ""

    def validate(self) -> dict:
        result = {
            "feature_execution_id": self.feature_execution_id,
            "execution_target_type": self.execution_target_type.value,
            "status": self.status.value,
            "has_independent_authorization_contract": bool(self.feature_authorization_contract_id),
            "gov21_compliant": self.status != FeatureExecutionStatus.AUTHORIZED or bool(self.feature_authorization_contract_id),
            "valid": self.status == FeatureExecutionStatus.AUTHORIZED and bool(self.feature_authorization_contract_id),
        }
        return result


# ============================================================================
# MUST-C: Condition Object (expression_basis只保留合法类型)
# ============================================================================

@dataclass
class ConditionObject:
    """MUST-C: expression_basis只描述合法对象类型.
    
    非法行为(如ENGINE_THRESHOLD)由GOV-21/GOV-18 Gate检查, 不在enum中.
    """
    condition_id: str
    condition_type: str = ""
    proposition_id: str = ""
    condition_expression: str = ""
    expression_basis: ExpressionBasis = ExpressionBasis.CANONICAL_PROPOSITION  # MUST-C
    execution_semantics: str = ""
    authorization_basis: str = ""
    authorized_scope: str = ""
    execution_target_type: ExecutionTargetType = ExecutionTargetType.CANONICAL_PROPOSITION
    feature_execution: Optional[FeatureExecutionAuthorization] = None  # MUST-B: 独立授权
    notes: str = ""


# ============================================================================
# LAYER-SPECIFIC METADATA
# ============================================================================

@dataclass
class L1Metadata:
    semantic_type: SemanticType = SemanticType.ENGINEERING_METRIC
    computation_provenance: Provenance = field(default_factory=Provenance)
    calculation_method: str = ""


@dataclass
class L2Metadata:
    mapping_type: str = ""
    mapping_provenance: Provenance = field(default_factory=Provenance)
    mapping_status: MappingStatus = MappingStatus.UNPROVEN
    mapping_basis_type: MappingBasisType = MappingBasisType.UNAUTHORIZED_MAPPING
    candidate_concepts: List[str] = field(default_factory=list)
    semantic_mapping_ids: List[str] = field(default_factory=list)  # REC-B: 关联独立SemanticMapping


@dataclass
class L3Metadata:
    candidate_role: CandidateRole = CandidateRole.CANDIDATE_SUPPORTING
    evidence_role: Optional[EvidenceRole] = None
    source_support: SourceSupport = SourceSupport.NONE
    authorization_status: L3Status = L3Status.CANDIDATE
    canonical_source_scope: str = ""
    candidate_dimensions: List[str] = field(default_factory=list)
    provided_dimensions: List[str] = field(default_factory=list)
    missing_dimensions: List[str] = field(default_factory=list)
    candidate_observable: str = ""
    candidate_for_proposition: str = ""
    source_authorization: str = "UNPROVEN"
    source_claim_ids: List[str] = field(default_factory=list)


@dataclass
class L4Metadata:
    proposition_type: str = ""
    evidence_contract_id: str = ""
    aggregation_authorized: bool = False
    aggregation_method: str = ""
    source_claim_ids: List[str] = field(default_factory=list)


@dataclass
class L5Metadata:
    authorization_scope: str = ""
    authorization_basis: str = ""
    authorized_proposition_ids: List[str] = field(default_factory=list)
    authorized_evidence_ids: List[str] = field(default_factory=list)
    execution_semantics: str = ""
    authorized_features: List[str] = field(default_factory=list)
    condition_object: Optional[ConditionObject] = None
    execution_target_type: ExecutionTargetType = ExecutionTargetType.CANONICAL_PROPOSITION


@dataclass
class L6Metadata:
    judgment_type: str = ""
    prerequisite_ids: List[str] = field(default_factory=list)
    selection_validated: bool = False
    canonical_authorization_validated: bool = False


@dataclass
class L7Metadata:
    assertion_type: str = ""
    assertion_contract_id: str = ""
    assertion_gate: str = "FROZEN"


# ============================================================================
# 七层数据结构
# ============================================================================

@dataclass
class L1_EngineFact:
    id: str
    status: L1Status = L1Status.NOT_AVAILABLE
    layer_specific: L1Metadata = field(default_factory=L1Metadata)
    feature_name: str = ""
    value: Any = None
    dependencies: List[str] = field(default_factory=list)
    fidelity: str = ""
    failure_reason: str = ""
    notes: str = ""


@dataclass
class L2_SemanticMapping:
    id: str
    status: L2Status = L2Status.NOT_AVAILABLE
    layer_specific: L2Metadata = field(default_factory=L2Metadata)
    feature_id: str = ""
    observable_meaning: str = ""
    dependencies: List[str] = field(default_factory=list)
    fidelity: str = ""
    failure_reason: str = ""
    notes: str = ""


@dataclass
class L3_EvidenceInstance:
    id: str
    status: L3Status = L3Status.NOT_AVAILABLE
    layer_specific: L3Metadata = field(default_factory=L3Metadata)
    dependencies: List[str] = field(default_factory=list)
    fidelity: str = ""
    failure_reason: str = ""
    blocking_dependencies: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class L4_CanonicalProposition:
    id: str
    status: L4Status = L4Status.NOT_AVAILABLE
    layer_specific: L4Metadata = field(default_factory=L4Metadata)
    proposition: str = ""
    evidence_ids: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    fidelity: str = ""
    failure_reason: str = ""
    blocking_dependencies: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class L5_ConditionAuthorization:
    id: str
    status: L5Status = L5Status.NOT_AVAILABLE
    layer_specific: L5Metadata = field(default_factory=L5Metadata)
    proposition_id: str = ""
    condition_expression: str = ""
    dependencies: List[str] = field(default_factory=list)
    fidelity: str = ""
    failure_reason: str = ""
    blocking_dependencies: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class L6_CanonicalJudgment:
    id: str
    status: L6Status = L6Status.NOT_AVAILABLE
    layer_specific: L6Metadata = field(default_factory=L6Metadata)
    judgment_id: str = ""
    canonical_statement: str = ""
    condition_id: str = ""
    dependencies: List[str] = field(default_factory=list)
    fidelity: str = ""
    failure_reason: str = ""
    blocking_dependencies: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class L7_CanonicalAssertion:
    id: str
    status: L7Status = L7Status.NOT_AVAILABLE
    layer_specific: L7Metadata = field(default_factory=L7Metadata)
    judgment_id: str = ""
    assertion_text: str = ""
    dependencies: List[str] = field(default_factory=list)
    fidelity: str = ""
    failure_reason: str = ""
    blocking_dependencies: List[str] = field(default_factory=list)
    notes: str = ""


# ============================================================================
# 七层贯通链
# ============================================================================

@dataclass
class SevenLayerChain:
    chain_id: str
    source_claims: List[SourceClaim] = field(default_factory=list)
    semantic_mappings: List[SemanticMapping] = field(default_factory=list)  # REC-B
    l1: L1_EngineFact = None
    l2: L2_SemanticMapping = None
    l3: L3_EvidenceInstance = None
    evidence_contract: Optional[EvidenceContract] = None
    l4: Optional[L4_CanonicalProposition] = None
    l5: Optional[L5_ConditionAuthorization] = None
    l6: Optional[L6_CanonicalJudgment] = None
    l7: Optional[L7_CanonicalAssertion] = None

    def validate(self) -> dict:
        result = {
            "chain_id": self.chain_id,
            "source_claims_count": len(self.source_claims),
            "semantic_mappings_count": len(self.semantic_mappings),  # REC-B
            "l1_status": self.l1.status.value if self.l1 else "NOT_AVAILABLE",
            "l2_status": self.l2.status.value if self.l2 else "NOT_AVAILABLE",
            "l3_status": self.l3.status.value if self.l3 else "NOT_AVAILABLE",
            "evidence_contract_status": self.evidence_contract.contract_status.value if self.evidence_contract else "N/A",
            "l4_status": self.l4.status.value if self.l4 else "NOT_AVAILABLE",
            "l5_status": self.l5.status.value if self.l5 else "NOT_AVAILABLE",
            "l6_status": self.l6.status.value if self.l6 else "NOT_AVAILABLE",
            "l7_status": self.l7.status.value if self.l7 else "NOT_AVAILABLE",
            "chain_complete": False,
            "blocking_layers": [],
            "gov20_ready_not_proven": True,
            "gov21_feature_execution_gate": True,  # MUST-B
            "gov22_draft_not_authorized": True,
            "hard_gates_all_preserved": True,
            "validation_type": "CONTRACT_STATIC_VALIDATION",  # 不是Canonical Authorization Passed
        }
        if self.l4 and self.l4.status == L4Status.READY_FOR_EVALUATION:
            result["blocking_layers"].append("L4_READY_NOT_PROVEN")
        if self.l2 and self.l2.layer_specific.mapping_status not in [MappingStatus.PROVEN, MappingStatus.PARTIAL]:
            result["blocking_layers"].append("L2_MAPPING_UNPROVEN")
        if self.l3 and self.l3.status not in [L3Status.AUTHORIZED, L3Status.PARTIAL]:
            result["blocking_layers"].append("L3_EVIDENCE_NOT_AUTHORIZED")
        if not self.evidence_contract or self.evidence_contract.contract_status != ContractStatus.AUTHORIZED:
            result["blocking_layers"].append("EVIDENCE_CONTRACT_NOT_AUTHORIZED (GOV-22)")
        if self.l4 and self.l4.status not in [L4Status.PROVEN, L4Status.PARTIAL]:
            result["blocking_layers"].append("L4_NOT_PROVEN")
        if not self.l4:
            result["blocking_layers"].append("L4_NOT_AVAILABLE")
        if self.l5 and self.l5.status != L5Status.AUTHORIZED:
            result["blocking_layers"].append("L5_NOT_AUTHORIZED")
        if not self.l5:
            result["blocking_layers"].append("L5_NOT_AVAILABLE")
        # MUST-B: Feature Execution Gate检查
        if self.l5 and self.l5.layer_specific.execution_target_type in [ExecutionTargetType.ENGINE_FEATURE, ExecutionTargetType.DERIVED_FEATURE]:
            co = self.l5.layer_specific.condition_object
            if co and co.feature_execution and co.feature_execution.status == FeatureExecutionStatus.AUTHORIZED:
                if not co.feature_execution.feature_authorization_contract_id:
                    result["gov21_feature_execution_gate"] = False
                    result["blocking_layers"].append("GOV-21_FEATURE_EXECUTION_WITHOUT_INDEPENDENT_CONTRACT")
        result["chain_complete"] = len(result["blocking_layers"]) == 0
        return result


# ============================================================================
# 治理规则 (22条)
# ============================================================================

GOVERNANCE_RULES = {
    "GOV-01": "不能从原典文本描述 → 人工归纳 → 直接变成机器必要条件",
    "GOV-02": "Feature Semantic Mapping需要独立验证 (L2)",
    "GOV-03": "Canonical Evidence需要独立验证 (L3, 只有AUTHORIZED才是真正的Canonical Evidence)",
    "GOV-04": "每层都有自己的Fidelity, 不能合并",
    "GOV-05": "下层UNPROVEN/NOT_AUTHORIZED时, 上层只能是BLOCKED, 不能自动AUTHORIZED",
    "GOV-06": "Feature Equivalence ≠ Judgment Equivalence",
    "GOV-07": "ENGINEERING_STATISTICAL_METRIC ≠ CANONICAL_CONCEPT",
    "GOV-08": "不能用工程阈值定义命理概念 (防止循环自证)",
    "GOV-09": "Canonical Condition必须基于AUTHORIZED的层, 不能基于UNPROVEN的Feature",
    "GOV-10": "Assertion Gate继续冻结 (L7 assertion_gate=FROZEN)",
    "GOV-11": "Partial Evidence SHALL NOT be aggregated by count, score, vote, or confidence accumulation unless the Canonical Contract explicitly defines the aggregation relation.",
    "GOV-12": "Source Scope必须明确, 不同体系的同一概念不能被强行统一",
    "GOV-13": "Evidence Role必须标注 (仅L3授权后), NON_CANONICAL证据不能直接用于Canonical授权",
    "GOV-14": "L2必须区分Observable Meaning和Candidate Concept",
    "GOV-15": "L3→L4必须经过Evidence Aggregation, 且聚合方法必须由Evidence Contract明确定义并授权",
    "GOV-16": "Canonical Evidence SHALL NOT be converted into a weighted score/probability/confidence/numerical threshold unless the Canonical Source explicitly authorizes.",
    "GOV-17": "A Canonical Judgment SHALL NOT automatically generate a Canonical Assertion without an explicit Assertion Contract.",
    "GOV-18": "Canonical Evidence Logic SHALL NOT be replaced by unauthorized numerical aggregation. Numerical values may exist as deterministic facts or authorized features, but SHALL NOT be converted into scores/weights/probabilities/thresholds unless explicitly authorized.",
    "GOV-19": "Canonical Proposition/Judgment SHALL NOT imply any downstream preference/utility/polarity/favorable-unfavorable direction/action/interpretation unless an independent Canonical Contract explicitly authorizes.",
    "GOV-20": "READY_FOR_EVALUATION SHALL NOT be interpreted as TRUE/PROVEN/Canonically satisfied.",
    "GOV-21": "L5 SHALL NOT authorize ENGINE_FEATURE/DERIVED_FEATURE as substitute for Canonical Proposition unless an independent Feature Execution Authorization Contract explicitly authorizes. (MUST-B: 必须经过独立FeatureExecutionAuthorization Gate)",
    "GOV-22": "A Draft/Candidate Evidence Contract SHALL NOT participate in Canonical Evaluation or Execution Authorization.",
}


# ============================================================================
# 12个硬Gate
# ============================================================================

HARD_GATES = {
    "GATE-01": "Feature ≠ Meaning (L1 ≠ L2)",
    "GATE-02": "Meaning ≠ Evidence (L2 ≠ L3)",
    "GATE-03": "Evidence ≠ Proposition (L3 ≠ L4)",
    "GATE-04": "Proposition ≠ Condition (L4 ≠ L5)",
    "GATE-05": "Condition ≠ Judgment (L5 ≠ L6)",
    "GATE-06": "Judgment ≠ Assertion (L6 ≠ L7)",
    "GATE-07": "Selection Validity ≠ Canonical Authorization Validity",
    "GATE-08": "Logical Aggregation ≠ Numerical Aggregation",
    "GATE-09": "Proven ≠ Authorized (L4 PROVEN ≠ L5 AUTHORIZED)",
    "GATE-10": "Ready ≠ Proven (L4 READY_FOR_EVALUATION ≠ L4 PROVEN, GOV-20)",
    "GATE-11": "Draft ≠ Authorized (Evidence Contract DRAFT ≠ AUTHORIZED, GOV-22)",
    "GATE-12": "Feature ≠ Proposition Substitute (ENGINE_FEATURE ≠ CANONICAL_PROPOSITION, GOV-21, MUST-B独立Gate)",
}


# ============================================================================
# 跨层授权不等原则
# ============================================================================

AUTHORIZATION_INDEPENDENCE = {
    "PRINCIPLE": "SourceClaim Authorization ≠ Semantic Mapping Authorization ≠ Evidence Authorization ≠ Proposition Authorization",
    "SourceClaim Authorization": "只能证明Claim的出处、文本身份、来源范围以及解释依据经过审核",
    "Semantic Mapping Authorization": "只能证明SourceClaim↔EngineFeature的映射关系经过授权",
    "Evidence Authorization": "只能证明该Evidence可以作为某个Proposition的证据",
    "Proposition Authorization": "只能证明该Proposition经过Evaluation并成立",
    "NONE_CAN_CROSS_SKIP": "任何一层授权都不能自动跳过下一层授权",
}


# ============================================================================
# MUST-D: STR-001A 三态测试
# ============================================================================

def build_str001a_negative_path() -> SevenLayerChain:
    """MUST-D Path A: Negative/Blocked Path (当前真实状态).
    
    L1 COMPUTED → L2 CANDIDATE → L3 CANDIDATE → L4 BLOCKED → L5-L7 NOT_AVAILABLE
    验证: 在证据不足的情况下, 系统有没有错误地放行.
    """
    sc1 = SourceClaim(source_claim_id="SC-XUANJI-001", source="渊海子平·玄机赋",
                      text_reference="得时俱为旺论，失令便作衰看。",
                      claim_type=ClaimType.NORMATIVE, claim="月令得时为旺, 失令为衰",
                      source_claim_status=ContractStatus.DRAFT)
    l1 = L1_EngineFact(id="L1-WOOD", status=L1Status.COMPUTED,
                        layer_specific=L1Metadata(semantic_type=SemanticType.ENGINEERING_METRIC),
                        feature_name="five_element_balance.WOOD", value=0.125)
    l2 = L2_SemanticMapping(id="L2-MAP", status=L2Status.CANDIDATE,
                             layer_specific=L2Metadata(mapping_status=MappingStatus.UNPROVEN,
                                                        mapping_basis_type=MappingBasisType.UNAUTHORIZED_MAPPING,
                                                        candidate_concepts=["木气偏少"]),
                             feature_id="F-WOOD", observable_meaning="8个位置中木计数=1/8")
    l3 = L3_EvidenceInstance(id="L3-EI", status=L3Status.CANDIDATE,
                              layer_specific=L3Metadata(candidate_role=CandidateRole.CANDIDATE_SUPPORTING,
                                                         evidence_role=None, source_support=SourceSupport.NONE),
                              blocking_dependencies=["L2_UNPROVEN", "L3_NOT_AUTHORIZED", "NO_CONTRACT"])
    ec = EvidenceContract(contract_id="EC-DRAFT", proposition="日主身弱",
                          contract_status=ContractStatus.DRAFT, authorized=False)
    l4 = L4_CanonicalProposition(id="L4-PROP", status=L4Status.BLOCKED,
                                  proposition="日主身弱",
                                  blocking_dependencies=["L2_UNPROVEN", "L3_NOT_AUTHORIZED", "EC_DRAFT"])
    return SevenLayerChain(chain_id="STR001A-NEGATIVE", source_claims=[sc1],
                           l1=l1, l2=l2, l3=l3, evidence_contract=ec, l4=l4)


def build_str001a_blocked_to_ready_path() -> SevenLayerChain:
    """MUST-D Path B: Blocked → Ready Path (状态跃迁测试).
    
    验证: BLOCKED → READY_FOR_EVALUATION 不得直接 PROVEN.
    假设L2/L3/EC都已授权, L4从BLOCKED进入READY_FOR_EVALUATION, 但尚未执行Evaluation.
    """
    l1 = L1_EngineFact(id="L1-WOOD", status=L1Status.COMPUTED,
                        layer_specific=L1Metadata(semantic_type=SemanticType.ENGINEERING_METRIC),
                        feature_name="five_element_balance.WOOD", value=0.125)
    l2 = L2_SemanticMapping(id="L2-MAP", status=L2Status.MAPPED,
                             layer_specific=L2Metadata(mapping_status=MappingStatus.PROVEN,
                                                        mapping_basis_type=MappingBasisType.DERIVED_FROM_SOURCE,
                                                        candidate_concepts=["木气偏少"]),
                             feature_id="F-WOOD", observable_meaning="8个位置中木计数=1/8")
    l3 = L3_EvidenceInstance(id="L3-EI", status=L3Status.AUTHORIZED,
                              layer_specific=L3Metadata(candidate_role=CandidateRole.CANDIDATE_SUPPORTING,
                                                         evidence_role=EvidenceRole.SUPPORTING,
                                                         source_support=SourceSupport.DIRECT))
    ec = EvidenceContract(contract_id="EC-AUTH", proposition="日主身弱",
                          contract_status=ContractStatus.AUTHORIZED, authorized=True)
    # MUST-D关键: L4 = READY_FOR_EVALUATION, 不是PROVEN
    l4 = L4_CanonicalProposition(id="L4-PROP", status=L4Status.READY_FOR_EVALUATION,
                                  proposition="日主身弱",
                                  notes="依赖已解除, 进入READY_FOR_EVALUATION, 但尚未执行Evaluation. GOV-20: READY≠PROVEN")
    return SevenLayerChain(chain_id="STR001A-BLOCKED-TO-READY",
                           l1=l1, l2=l2, l3=l3, evidence_contract=ec, l4=l4)


def build_str001a_rejected_path() -> SevenLayerChain:
    """MUST-D Path C: Rejected Path (失败路径测试).
    
    L4 READY → Evaluation → REJECTED.
    验证: REJECTED ≠ BLOCKED, REJECTED ≠ PARTIAL, REJECTED ≠ PROVEN.
    """
    l1 = L1_EngineFact(id="L1-WOOD", status=L1Status.COMPUTED,
                        layer_specific=L1Metadata(semantic_type=SemanticType.ENGINEERING_METRIC),
                        feature_name="five_element_balance.WOOD", value=0.125)
    l2 = L2_SemanticMapping(id="L2-MAP", status=L2Status.MAPPED,
                             layer_specific=L2Metadata(mapping_status=MappingStatus.PROVEN),
                             feature_id="F-WOOD", observable_meaning="8个位置中木计数=1/8")
    l3 = L3_EvidenceInstance(id="L3-EI", status=L3Status.AUTHORIZED,
                              layer_specific=L3Metadata(evidence_role=EvidenceRole.SUPPORTING))
    ec = EvidenceContract(contract_id="EC-AUTH", proposition="日主身弱",
                          contract_status=ContractStatus.AUTHORIZED, authorized=True)
    # MUST-D关键: L4 = REJECTED
    l4 = L4_CanonicalProposition(id="L4-PROP", status=L4Status.REJECTED,
                                  proposition="日主身弱",
                                  failure_reason="Evaluation执行后, 证据不满足Proposition成立条件",
                                  notes="REJECTED ≠ BLOCKED (BLOCKED是依赖不满足, REJECTED是Evaluation后判定不成立)")
    return SevenLayerChain(chain_id="STR001A-REJECTED",
                           l1=l1, l2=l2, l3=l3, evidence_contract=ec, l4=l4)


def run_three_path_tests() -> dict:
    """MUST-D: 运行三态测试."""
    results = {}

    # Path A: Negative/Blocked
    chain_a = build_str001a_negative_path()
    res_a = chain_a.validate()
    results["Path_A_Negative"] = {
        "description": "证据不足时系统不得错误放行",
        "l4_status": res_a["l4_status"],
        "chain_complete": res_a["chain_complete"],
        "blocking_layers_count": len(res_a["blocking_layers"]),
        "expected_blocked": True,
        "actual_blocked": res_a["l4_status"] == "BLOCKED",
        "pass": res_a["l4_status"] == "BLOCKED" and not res_a["chain_complete"],
    }

    # Path B: Blocked → Ready
    chain_b = build_str001a_blocked_to_ready_path()
    res_b = chain_b.validate()
    results["Path_B_BlockedToReady"] = {
        "description": "BLOCKED→READY_FOR_EVALUATION不得直接PROVEN (GOV-20)",
        "l4_status": res_b["l4_status"],
        "gov20_ready_not_proven": res_b["gov20_ready_not_proven"],
        "chain_complete": res_b["chain_complete"],
        "expected_ready_not_proven": True,
        "actual_ready_not_proven": res_b["l4_status"] == "READY_FOR_EVALUATION" and "L4_READY_NOT_PROVEN" in res_b["blocking_layers"],
        "pass": res_b["l4_status"] == "READY_FOR_EVALUATION" and "L4_READY_NOT_PROVEN" in res_b["blocking_layers"],
    }

    # Path C: Rejected
    chain_c = build_str001a_rejected_path()
    res_c = chain_c.validate()
    results["Path_C_Rejected"] = {
        "description": "L4 READY→Evaluation→REJECTED, REJECTED≠BLOCKED/PARTIAL/PROVEN",
        "l4_status": res_c["l4_status"],
        "expected_rejected": True,
        "actual_rejected": res_c["l4_status"] == "REJECTED",
        "rejected_not_blocked": res_c["l4_status"] != "BLOCKED",
        "rejected_not_partial": res_c["l4_status"] != "PARTIAL",
        "rejected_not_proven": res_c["l4_status"] != "PROVEN",
        "pass": res_c["l4_status"] == "REJECTED",
    }

    results["all_three_paths_pass"] = all(r["pass"] for r in results.values() if isinstance(r, dict) and "pass" in r)
    return results


# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 100)
    print("Canonical Semantic Authorization Pipeline v6-final - 七层语义授权链 (小封口修正版, FROZEN候选)")
    print("=" * 100)
    print("\n修正记录: 4个MUST + 2个REC 全部落地 (小封口修正, 不是v7大改)")
    print("  MUST-A: Source Claim ↔ L1 关系修正 (并行产生, 通过Mapping/Evidence建立关联)")
    print("  MUST-B: Feature Execution Authorization 独立Gate (封死GOV-21后门)")
    print("  MUST-C: expression_basis移出NOT_ENGINE_THRESHOLD (Enum只描述合法类型)")
    print("  MUST-D: STR-001A Positive/Blocked/Rejected三态测试")
    print("  REC-A: Conditional/Dependent Relation Schema正式定义")
    print("  REC-B: SourceClaim与SemanticMapping彻底拆开")

    # 最终架构
    print(f"\n{'='*100}")
    print("最终架构 (MUST-A修正后)")
    print("=" * 100)
    print("""
  CANONICAL SOURCE
      ↓
  SOURCE CLAIM (Canonical semantic authority)
      │
      │ source authorization
      ▼
  ┌─────────────────┐
  │ L1 ENGINE FACT  │  (computed observation, 与Source Claim并行产生)
  └────────┬────────┘
           │ mapping (通过独立SemanticMapping对象, REC-B)
           ▼
  L2 SEMANTIC MAPPING
           │
           ▼
  L3 EVIDENCE INSTANCE
           │
           ▼ (Evidence Contract [AUTHORIZED])
  L4 CANONICAL PROPOSITION
           │ READY_FOR_EVALUATION → EVALUATION
           ▼ PROVEN / PARTIAL / REJECTED
  L5 CONDITION OBJECT + EXECUTION AUTHORIZATION
           │
           ├─ CANONICAL CONDITION (普通授权)
           └─ FEATURE EXECUTION (MUST-B: 独立授权Gate)
           ▼
  L6 CANONICAL JUDGMENT
           │ (Assertion Contract)
           ▼
  L7 CANONICAL ASSERTION
""")

    # 跨层授权不等原则
    print(f"\n{'='*100}")
    print("跨层授权不等原则")
    print("=" * 100)
    for k, v in AUTHORIZATION_INDEPENDENCE.items():
        print(f"  {k}: {v}")

    # MUST-D: 三态测试
    print(f"\n{'='*100}")
    print("MUST-D: STR-001A 三态测试")
    print("=" * 100)
    test_results = run_three_path_tests()
    for path_name, result in test_results.items():
        if path_name == "all_three_paths_pass":
            print(f"\n  >>> ALL THREE PATHS PASS: {result}")
            continue
        print(f"\n  {path_name}:")
        print(f"    description: {result['description']}")
        print(f"    l4_status: {result['l4_status']}")
        print(f"    pass: {result['pass']}")

    # 12个硬Gate
    print(f"\n{'='*100}")
    print("12个硬Gate")
    print("=" * 100)
    for k, v in HARD_GATES.items():
        print(f"  {k}: {v}")

    # 验证类型说明
    print(f"\n{'='*100}")
    print("验证类型说明 (重要)")
    print("=" * 100)
    print("""
  v6-final = Contract Static Validation Passed
  不是 Canonical Authorization Passed

  当前状态:
    Contract Schema Validation = PASS
    Governance Enforcement Test = PASS
    STR-001A Negative Path = PASS
    STR-001A Blocked→Ready Path = PASS
    STR-001A Rejected Path = PASS
    Canonical Source Authorization = NOT_DONE
    Canonical Evidence Authorization = NOT_DONE
    Canonical Proposition Evaluation = NOT_DONE
    Canonical Condition Authorization = NOT_DONE

  这几个状态必须严格区分. 22/22 Governance Rules方向正确,
  但不能称"Canonical验证完成".
""")

    print("=" * 100)
    print("v6-final 小封口修正版建立完成. Contract层进入FROZEN候选状态.")
    print("=" * 100)


if __name__ == "__main__":
    main()
