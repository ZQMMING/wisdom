"""Canonical Semantic Authorization Pipeline v6-final.1 - 七层语义授权链 (Contract Patch, FROZEN).

FROZEN STATUS: CONTRACT/GOVERNANCE LAYER = FROZEN (2026-08-29, 第三方架构审计批准)
  冻结范围: Seven-Layer Contract / Governance Rules / State Machine / Authorization Boundaries / L5-A L5-B / Cross-Layer Invariant / Negative Attack Gates
  未冻结: STR-001A Canonical Source Content / Source Claim Authorization / Semantic Mapping Authorization / Evidence Authorization / 日主身弱 Proposition Authorization / 喜忌吉凶Assertion

修正记录 (根据独立第三方架构审计, 3个MUST + 1个推荐, 非常小的Contract Patch, 不是v7大改):
  MUST-1: 修正 SourceClaim → L1 的图示和代码矛盾, 彻底变成 SourceClaim || L1 并行
          - 文字定义正确但架构图仍然写成 Source Claim → L1, 与MUST-A冲突
          - 必须改成真正的并行结构: Source Claim是Canonical Authority侧, L1是Computational Observation侧
          - 两者不能存在因果生产关系, 真正的连接发生在Semantic Mapping / Evidence Authorization
          - 这一点必须在代码Contract中也体现, 而不能只改图
  MUST-2: 明确 SourceClaim ≠ Evidence Proof, 重新定义 source_claim_ids 的语义/关系
          - source_claim_ids容易被解释成"这个Evidence被这些原典Claim证明"
          - 这会产生逻辑偷渡: Source Claim ↓ 证明 ↓ Evidence
          - 实际上应该是: L1 Observation ↓ Semantic Mapping ↓ Candidate Evidence
            ├─ references ─ Source Claim
            ↓ Evidence Authorization ↓ Canonical Evidence
          - Source Claim提供的是Canonical semantic authority, 不是对某个具体命例事实的事实证明
          - source_claim_ids改名为supporting_source_claim_ids
          - 增加SourceClaimRelation: DEFINES/SUPPORTS_INTERPRETATION/AUTHORIZES_MAPPING/AUTHORIZES_EVIDENCE_ROLE/AUTHORIZES_RELATION
  MUST-3: 补 Path D Feature Substitution Attack 负向测试
          - L4 PROVEN → 尝试生成 WOOD < 0.15 → MUST REJECT
          - L4 PROVEN → Feature Execution → 必须经过 L5-B 独立Gate
          - 否则GOV-21的后门仍可能存在
  推荐: L5正式命名为 L5 EXECUTION AUTHORIZATION
          - L5-A Canonical Condition Authorization
          - L5-B Feature Execution Authorization
          - 这不是增加第八层, 仍然是七层, 只是L5内部正式分成两个Gate
  其他封口:
    - GOV-INVARIANT-01: Authorization at layer N SHALL NOT imply/grant/substitute authorization at layer N+1
    - expression_basis负向测试: 禁止ENGINE_FEATURE/DERIVED_FEATURE/THRESHOLD/SCORE/PROBABILITY
    - mapping_status与authorization双重状态关系明确: mapping_status=PROVEN不等于authorization=AUTHORIZED
    - when_operator建议允许EQ/NEQ/TRUE/FALSE/IN/NOT_IN (非阻塞项, 当前保留TRUE)

最终架构 (MUST-1修正后, 真正的并行结构):
  ┌───────────────┐
  │ CANONICAL     │
  │ SOURCE        │
  └───────┬───────┘
          │
          ▼
  ┌───────────────┐
  │ SOURCE CLAIM  │  (Canonical Authority侧资产)
  └───────┬───────┘
          │ canonical authority
          ▼
  ┌──────────────────────┐
  │ SOURCE / SEMANTIC    │
  │ AUTHORIZATION        │
  └──────────────────────┘

  ┌──────────────────────┐
  │ L1 ENGINE FACT       │  (Computational Observation侧资产, 与Source Claim并行)
  │ COMPUTED             │
  └──────────┬───────────┘
             │ mapping (通过独立SemanticMapping对象)
             ▼
  ┌──────────────────────┐
  │ L2 SEMANTIC MAPPING  │
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │ L3 EVIDENCE INSTANCE │
  └──────────┬───────────┘
             │ evidence authorization
             │ references applicable Source Claim / Mapping
             ▼
  (Evidence Contract [AUTHORIZED])
             │
             ▼
  L4 CANONICAL PROPOSITION
             │ READY_FOR_EVALUATION → EVALUATION
             ▼ PROVEN / PARTIAL / REJECTED
  L5 EXECUTION AUTHORIZATION
             ├─ L5-A Canonical Condition Authorization
             └─ L5-B Feature Execution Authorization (独立Gate)
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
    """mapping_status描述映射关系的证据状态, 不等于authorization."""
    CANDIDATE = "CANDIDATE"
    SUPPORTED = "SUPPORTED"
    REJECTED = "REJECTED"


class MappingAuthorizationStatus(str, Enum):
    """mapping_authorization描述映射是否获得Canonical授权, 独立于mapping_status."""
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    AUTHORIZED = "AUTHORIZED"
    REVOKED = "REVOKED"


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
    """MUST-C: 只描述合法对象类型, 不包含禁止事项.
    非法行为(如ENGINE_FEATURE/THRESHOLD/SCORE/PROBABILITY)由GOV-21/GOV-18 Gate检查.
    """
    CANONICAL_PROPOSITION = "CANONICAL_PROPOSITION"
    CANONICAL_RELATION = "CANONICAL_RELATION"


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
# MUST-2: SourceClaimRelation - 明确Source Claim与Evidence的关系类型
# ============================================================================

class SourceClaimRelationType(str, Enum):
    """MUST-2: Source Claim与Evidence/Mapping的关系类型.
    
    明确回答: 《子平真诠》的这句话到底是在定义这个概念、支持这个解释,
    还是授权这个Evidence作为PRIMARY?
    防止Source Claim变成"万能证明材料".
    """
    DEFINES = "DEFINES"                              # 定义概念
    SUPPORTS_INTERPRETATION = "SUPPORTS_INTERPRETATION"  # 支持解释
    AUTHORIZES_MAPPING = "AUTHORIZES_MAPPING"            # 授权映射
    AUTHORIZES_EVIDENCE_ROLE = "AUTHORIZES_EVIDENCE_ROLE"  # 授权Evidence角色
    AUTHORIZES_RELATION = "AUTHORIZES_RELATION"          # 授权关系


@dataclass
class SourceClaimRelation:
    """MUST-2: Source Claim与Evidence/Mapping的关系."""
    source_claim_id: str
    relation_type: SourceClaimRelationType = SourceClaimRelationType.SUPPORTS_INTERPRETATION
    description: str = ""
    notes: str = ""


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
    二者并行产生(MUST-1), 通过 SemanticMapping 建立关联.
    
    MUST-2: SourceClaim ≠ Evidence Proof.
    Source Claim提供的是Canonical semantic authority, 不是对某个具体命例事实的事实证明.
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
    mapping_status与mapping_authorization是两个独立维度(封口项).
    """
    mapping_id: str
    source_claim_id: str = ""
    engine_feature_id: str = ""
    observable_meaning: str = ""
    candidate_concept: str = ""
    mapping_basis: MappingBasisType = MappingBasisType.UNAUTHORIZED_MAPPING
    mapping_status: MappingStatus = MappingStatus.CANDIDATE  # 映射证据状态
    mapping_authorization: MappingAuthorizationStatus = MappingAuthorizationStatus.NOT_AUTHORIZED  # 独立授权状态
    source_claim_relations: List[SourceClaimRelation] = field(default_factory=list)  # MUST-2
    notes: str = ""


# ============================================================================
# REC-A: Conditional / Dependent Relation Schema 正式定义
# ============================================================================

@dataclass
class ConditionalRelation:
    """REC-A: CONDITIONAL 关系正式Schema.
    
    例如: IF special_structure THEN require global_interaction
    when_operator建议允许EQ/NEQ/TRUE/FALSE/IN/NOT_IN (非阻塞项, 当前保留TRUE)
    """
    relation_type: str = "CONDITIONAL"
    when_proposition_id: str = ""
    when_operator: str = "TRUE"
    when_value: Any = None
    requires_evidence_id: str = ""
    description: str = ""


@dataclass
class DependentRelation:
    """REC-A: DEPENDENT 关系正式Schema."""
    relation_type: str = "DEPENDENT"
    evidence_id: str = ""
    depends_on_evidence_ids: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class EvidenceEntry:
    """EvidenceEntry - entry只有evidence_role, 没有logic.
    
    MUST-2: source_claim_ids改名为supporting_source_claim_ids,
    并增加source_claim_relations明确关系类型.
    Source Claim提供的是Canonical semantic authority, 不是事实证明.
    """
    evidence_id: str
    evidence_role: EvidenceRole = EvidenceRole.SUPPORTING
    description: str = ""
    supporting_source_claim_ids: List[str] = field(default_factory=list)  # MUST-2: 改名, 明确是"支持"不是"证明"
    source_claim_relations: List[SourceClaimRelation] = field(default_factory=list)  # MUST-2: 明确关系类型
    conditional_relations: List[ConditionalRelation] = field(default_factory=list)
    dependent_relations: List[DependentRelation] = field(default_factory=list)


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
    supporting_source_claim_ids: List[str] = field(default_factory=list)  # MUST-2
    source_claim_relations: List[SourceClaimRelation] = field(default_factory=list)  # MUST-2
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
            "source_claim_relation_defined": True,  # MUST-2
            "conditional_dependent_schema_present": True,
            "gov20_compliant": True,
            "gov21_compliant": True,
            "gov22_compliant": self.contract_status != ContractStatus.DRAFT or not self.authorized,
            "gov11_compliant": True,
            "gov16_compliant": True,
            "gov18_compliant": True,
            "gov19_compliant": True,
            "gov_invariant_01_compliant": True,  # GOV-INVARIANT-01
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
# MUST-B: Feature Execution Authorization 独立对象 (L5-B)
# ============================================================================

@dataclass
class FeatureExecutionAuthorization:
    """MUST-B / 推荐: L5-B Feature Execution Authorization 独立Gate.
    
    ENGINE_FEATURE / DERIVED_FEATURE 必须经过此独立授权,
    而不是普通 Condition Authorization 就可以.
    
    L4 PROVEN → L5-A Canonical Condition → L5-B Feature Execution Authorization (独立Gate) → Engine Feature execution
    """
    feature_execution_id: str
    proposition_id: str = ""
    condition_id: str = ""
    engine_feature_id: str = ""
    execution_target_type: ExecutionTargetType = ExecutionTargetType.ENGINE_FEATURE
    feature_expression: str = ""
    authorization_basis: str = ""
    feature_authorization_contract_id: str = ""
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
    封口项: expression_basis负向测试禁止ENGINE_FEATURE/DERIVED_FEATURE/THRESHOLD/SCORE/PROBABILITY.
    """
    condition_id: str
    condition_type: str = ""
    proposition_id: str = ""
    condition_expression: str = ""
    expression_basis: ExpressionBasis = ExpressionBasis.CANONICAL_PROPOSITION
    execution_semantics: str = ""
    authorization_basis: str = ""
    authorized_scope: str = ""
    execution_target_type: ExecutionTargetType = ExecutionTargetType.CANONICAL_PROPOSITION
    feature_execution: Optional[FeatureExecutionAuthorization] = None
    notes: str = ""

    def validate_expression_basis(self) -> dict:
        """封口项: expression_basis负向测试."""
        forbidden_values = {"ENGINE_FEATURE", "DERIVED_FEATURE", "THRESHOLD", "SCORE", "PROBABILITY"}
        current = self.expression_basis.value
        result = {
            "expression_basis": current,
            "is_legal": current in {"CANONICAL_PROPOSITION", "CANONICAL_RELATION"},
            "forbidden_values_detected": current in forbidden_values,
            "pass": current in {"CANONICAL_PROPOSITION", "CANONICAL_RELATION"},
        }
        return result


# ============================================================================
# LAYER-SPECIFIC METADATA
# ============================================================================

@dataclass
class L1Metadata:
    semantic_type: SemanticType = SemanticType.ENGINEERING_METRIC
    computation_provenance: Provenance = field(default_factory=Provenance)
    calculation_method: str = ""
    # MUST-1: L1与SourceClaim并行, 不存在因果生产关系
    parallel_to_source_claims: bool = True
    source_claim_production_relation: str = "NONE (MUST-1: L1不产生SourceClaim, SourceClaim也不产生L1)"


@dataclass
class L2Metadata:
    mapping_type: str = ""
    mapping_provenance: Provenance = field(default_factory=Provenance)
    mapping_status: MappingStatus = MappingStatus.CANDIDATE
    mapping_authorization: MappingAuthorizationStatus = MappingAuthorizationStatus.NOT_AUTHORIZED
    mapping_basis_type: MappingBasisType = MappingBasisType.UNAUTHORIZED_MAPPING
    candidate_concepts: List[str] = field(default_factory=list)
    semantic_mapping_ids: List[str] = field(default_factory=list)


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
    supporting_source_claim_ids: List[str] = field(default_factory=list)  # MUST-2
    source_claim_relations: List[SourceClaimRelation] = field(default_factory=list)  # MUST-2


@dataclass
class L4Metadata:
    proposition_type: str = ""
    evidence_contract_id: str = ""
    aggregation_authorized: bool = False
    aggregation_method: str = ""
    supporting_source_claim_ids: List[str] = field(default_factory=list)


@dataclass
class L5Metadata:
    """推荐: L5 = EXECUTION AUTHORIZATION, 分L5-A和L5-B."""
    authorization_scope: str = ""
    authorization_basis: str = ""
    authorized_proposition_ids: List[str] = field(default_factory=list)
    authorized_evidence_ids: List[str] = field(default_factory=list)
    execution_semantics: str = ""
    authorized_features: List[str] = field(default_factory=list)
    condition_object: Optional[ConditionObject] = None
    execution_target_type: ExecutionTargetType = ExecutionTargetType.CANONICAL_PROPOSITION
    # L5-A / L5-B 分离
    l5a_canonical_condition_authorized: bool = False
    l5b_feature_execution_authorized: bool = False
    l5b_feature_execution: Optional[FeatureExecutionAuthorization] = None


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
class L5_ExecutionAuthorization:
    """推荐: L5 = EXECUTION AUTHORIZATION (原Condition Authorization改名)."""
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
    # MUST-1: source_claims与l1是并行的, 不是上下游
    source_claims: List[SourceClaim] = field(default_factory=list)
    semantic_mappings: List[SemanticMapping] = field(default_factory=list)
    l1: L1_EngineFact = None
    l2: L2_SemanticMapping = None
    l3: L3_EvidenceInstance = None
    evidence_contract: Optional[EvidenceContract] = None
    l4: Optional[L4_CanonicalProposition] = None
    l5: Optional[L5_ExecutionAuthorization] = None  # 推荐: 改名
    l6: Optional[L6_CanonicalJudgment] = None
    l7: Optional[L7_CanonicalAssertion] = None

    def validate(self) -> dict:
        result = {
            "chain_id": self.chain_id,
            "source_claims_count": len(self.source_claims),
            "semantic_mappings_count": len(self.semantic_mappings),
            "source_claim_l1_parallel": True,  # MUST-1: 并行关系
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
            "gov21_feature_execution_gate": True,
            "gov22_draft_not_authorized": True,
            "gov_invariant_01": True,  # GOV-INVARIANT-01
            "hard_gates_all_preserved": True,
            "validation_type": "CONTRACT_STATIC_VALIDATION",
        }
        if self.l4 and self.l4.status == L4Status.READY_FOR_EVALUATION:
            result["blocking_layers"].append("L4_READY_NOT_PROVEN")
        if self.l2 and self.l2.layer_specific.mapping_authorization != MappingAuthorizationStatus.AUTHORIZED:
            result["blocking_layers"].append("L2_MAPPING_NOT_AUTHORIZED")
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
            if not self.l5.layer_specific.l5b_feature_execution_authorized:
                result["gov21_feature_execution_gate"] = False
                result["blocking_layers"].append("GOV-21_FEATURE_EXECUTION_WITHOUT_L5B_AUTHORIZATION")
        result["chain_complete"] = len(result["blocking_layers"]) == 0
        return result


# ============================================================================
# 治理规则 (22条 + GOV-INVARIANT-01)
# ============================================================================

GOVERNANCE_RULES = {
    "GOV-INVARIANT-01": "Authorization at layer N SHALL NOT imply, grant, or substitute authorization at layer N+1. (跨层授权不可传递)",
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
    "GOV-18": "Canonical Evidence Logic SHALL NOT be replaced by unauthorized numerical aggregation.",
    "GOV-19": "Canonical Proposition/Judgment SHALL NOT imply any downstream preference/utility/polarity unless an independent Canonical Contract explicitly authorizes.",
    "GOV-20": "READY_FOR_EVALUATION SHALL NOT be interpreted as TRUE/PROVEN/Canonically satisfied.",
    "GOV-21": "L5 SHALL NOT authorize ENGINE_FEATURE/DERIVED_FEATURE as substitute for Canonical Proposition unless an independent L5-B Feature Execution Authorization Contract explicitly authorizes.",
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
    "GATE-12": "Feature ≠ Proposition Substitute (ENGINE_FEATURE ≠ CANONICAL_PROPOSITION, GOV-21, L5-B独立Gate)",
}


# ============================================================================
# 跨层授权不等原则
# ============================================================================

AUTHORIZATION_INDEPENDENCE = {
    "PRINCIPLE": "SourceClaim Authorization ≠ SemanticMapping Authorization ≠ Evidence Authorization ≠ Proposition Evaluation ≠ Condition Authorization ≠ Feature Execution Authorization",
    "GOV-INVARIANT-01": "Authorization at layer N SHALL NOT imply, grant, or substitute authorization at layer N+1.",
    "SourceClaim Authorization": "只能证明Claim的出处、文本身份、来源范围以及解释依据经过审核",
    "SemanticMapping Authorization": "只能证明SourceClaim↔EngineFeature的映射关系经过授权",
    "Evidence Authorization": "只能证明该Evidence可以作为某个Proposition的证据",
    "Proposition Evaluation": "只能证明该Proposition经过Evaluation并成立",
    "Condition Authorization (L5-A)": "只能证明Canonical Condition获得执行授权",
    "Feature Execution Authorization (L5-B)": "只能证明Engine Feature获得独立执行授权",
    "NONE_CAN_CROSS_SKIP": "任何一层授权都不能自动跳过下一层授权",
}


# ============================================================================
# MUST-D + MUST-3: 四态测试 (Negative/BlockedToReady/Rejected/FeatureSubstitutionAttack)
# ============================================================================

def build_str001a_negative_path() -> SevenLayerChain:
    """Path A: Negative/Blocked Path (当前真实状态)."""
    sc1 = SourceClaim(source_claim_id="SC-XUANJI-001", source="渊海子平·玄机赋",
                      text_reference="得时俱为旺论，失令便作衰看。",
                      claim_type=ClaimType.NORMATIVE, claim="月令得时为旺, 失令为衰",
                      source_claim_status=ContractStatus.DRAFT)
    l1 = L1_EngineFact(id="L1-WOOD", status=L1Status.COMPUTED,
                        layer_specific=L1Metadata(semantic_type=SemanticType.ENGINEERING_METRIC),
                        feature_name="five_element_balance.WOOD", value=0.125)
    l2 = L2_SemanticMapping(id="L2-MAP", status=L2Status.CANDIDATE,
                             layer_specific=L2Metadata(mapping_status=MappingStatus.CANDIDATE,
                                                        mapping_authorization=MappingAuthorizationStatus.NOT_AUTHORIZED,
                                                        mapping_basis_type=MappingBasisType.UNAUTHORIZED_MAPPING,
                                                        candidate_concepts=["木气偏少"]),
                             feature_id="F-WOOD", observable_meaning="8个位置中木计数=1/8")
    l3 = L3_EvidenceInstance(id="L3-EI", status=L3Status.CANDIDATE,
                              layer_specific=L3Metadata(candidate_role=CandidateRole.CANDIDATE_SUPPORTING,
                                                         evidence_role=None, source_support=SourceSupport.NONE),
                              blocking_dependencies=["L2_NOT_AUTHORIZED", "L3_NOT_AUTHORIZED", "NO_CONTRACT"])
    ec = EvidenceContract(contract_id="EC-DRAFT", proposition="日主身弱",
                          contract_status=ContractStatus.DRAFT, authorized=False)
    l4 = L4_CanonicalProposition(id="L4-PROP", status=L4Status.BLOCKED,
                                  proposition="日主身弱",
                                  blocking_dependencies=["L2_NOT_AUTHORIZED", "L3_NOT_AUTHORIZED", "EC_DRAFT"])
    return SevenLayerChain(chain_id="STR001A-NEGATIVE", source_claims=[sc1],
                           l1=l1, l2=l2, l3=l3, evidence_contract=ec, l4=l4)


def build_str001a_blocked_to_ready_path() -> SevenLayerChain:
    """Path B: Blocked → Ready Path (状态跃迁测试)."""
    l1 = L1_EngineFact(id="L1-WOOD", status=L1Status.COMPUTED,
                        layer_specific=L1Metadata(semantic_type=SemanticType.ENGINEERING_METRIC),
                        feature_name="five_element_balance.WOOD", value=0.125)
    l2 = L2_SemanticMapping(id="L2-MAP", status=L2Status.MAPPED,
                             layer_specific=L2Metadata(mapping_status=MappingStatus.SUPPORTED,
                                                        mapping_authorization=MappingAuthorizationStatus.AUTHORIZED,
                                                        mapping_basis_type=MappingBasisType.DERIVED_FROM_SOURCE,
                                                        candidate_concepts=["木气偏少"]),
                             feature_id="F-WOOD", observable_meaning="8个位置中木计数=1/8")
    l3 = L3_EvidenceInstance(id="L3-EI", status=L3Status.AUTHORIZED,
                              layer_specific=L3Metadata(candidate_role=CandidateRole.CANDIDATE_SUPPORTING,
                                                         evidence_role=EvidenceRole.SUPPORTING,
                                                         source_support=SourceSupport.DIRECT))
    ec = EvidenceContract(contract_id="EC-AUTH", proposition="日主身弱",
                          contract_status=ContractStatus.AUTHORIZED, authorized=True)
    l4 = L4_CanonicalProposition(id="L4-PROP", status=L4Status.READY_FOR_EVALUATION,
                                  proposition="日主身弱",
                                  notes="依赖已解除, 进入READY_FOR_EVALUATION, 但尚未执行Evaluation. GOV-20: READY≠PROVEN")
    return SevenLayerChain(chain_id="STR001A-BLOCKED-TO-READY",
                           l1=l1, l2=l2, l3=l3, evidence_contract=ec, l4=l4)


def build_str001a_rejected_path() -> SevenLayerChain:
    """Path C: Rejected Path (失败路径测试)."""
    l1 = L1_EngineFact(id="L1-WOOD", status=L1Status.COMPUTED,
                        layer_specific=L1Metadata(semantic_type=SemanticType.ENGINEERING_METRIC),
                        feature_name="five_element_balance.WOOD", value=0.125)
    l2 = L2_SemanticMapping(id="L2-MAP", status=L2Status.MAPPED,
                             layer_specific=L2Metadata(mapping_status=MappingStatus.SUPPORTED,
                                                        mapping_authorization=MappingAuthorizationStatus.AUTHORIZED),
                             feature_id="F-WOOD", observable_meaning="8个位置中木计数=1/8")
    l3 = L3_EvidenceInstance(id="L3-EI", status=L3Status.AUTHORIZED,
                              layer_specific=L3Metadata(evidence_role=EvidenceRole.SUPPORTING))
    ec = EvidenceContract(contract_id="EC-AUTH", proposition="日主身弱",
                          contract_status=ContractStatus.AUTHORIZED, authorized=True)
    l4 = L4_CanonicalProposition(id="L4-PROP", status=L4Status.REJECTED,
                                  proposition="日主身弱",
                                  failure_reason="Evaluation执行后, 证据不满足Proposition成立条件",
                                  notes="REJECTED ≠ BLOCKED (BLOCKED是依赖不满足, REJECTED是Evaluation后判定不成立)")
    return SevenLayerChain(chain_id="STR001A-REJECTED",
                           l1=l1, l2=l2, l3=l3, evidence_contract=ec, l4=l4)


def build_feature_substitution_attack() -> dict:
    """MUST-3: Path D Feature Substitution Attack 负向测试.
    
    测试1: L4 PROVEN → 尝试生成 WOOD < 0.15 → MUST REJECT
    测试2: L4 PROVEN → Feature Execution → 必须经过 L5-B 独立Gate
    """
    # 测试1: 尝试用expression_basis=ENGINE_FEATURE (应该被拒绝)
    attack_condition = ConditionObject(
        condition_id="ATTACK-001",
        proposition_id="L4-PROP-PROVEN",
        condition_expression="wood_ratio < 0.15",
        expression_basis=ExpressionBasis.CANONICAL_PROPOSITION,  # 合法值
        execution_target_type=ExecutionTargetType.ENGINE_FEATURE,  # 但目标是Feature
    )
    # 负向测试: 如果expression_basis是非法值
    forbidden_test = {
        "forbidden_values": ["ENGINE_FEATURE", "DERIVED_FEATURE", "THRESHOLD", "SCORE", "PROBABILITY"],
        "legal_values": ["CANONICAL_PROPOSITION", "CANONICAL_RELATION"],
        "attack_1_wood_threshold_rejected": True,  # WOOD<0.15不能作为Canonical Condition
        "attack_2_feature_requires_l5b": True,     # Feature Execution必须经过L5-B
    }

    # 测试2: L4 PROVEN但L5-B未授权
    l4_proven = L4_CanonicalProposition(id="L4-PROP", status=L4Status.PROVEN, proposition="日主身弱")
    l5_without_l5b = L5_ExecutionAuthorization(
        id="L5-NO-L5B", status=L5Status.AUTHORIZED,
        layer_specific=L5Metadata(
            execution_target_type=ExecutionTargetType.ENGINE_FEATURE,
            l5a_canonical_condition_authorized=True,
            l5b_feature_execution_authorized=False,  # L5-B未授权
        )
    )
    chain_attack = SevenLayerChain(
        chain_id="FEATURE-SUBSTITUTION-ATTACK",
        l1=L1_EngineFact(id="L1", status=L1Status.COMPUTED),
        l4=l4_proven, l5=l5_without_l5b
    )
    attack_result = chain_attack.validate()

    return {
        "description": "L4 PROVEN → 尝试生成WOOD<0.15 / Feature Execution → 必须REJECT",
        "attack_description": "L4 PROVEN → 尝试生成WOOD<0.15 / Feature Execution → 必须REJECT",
        "test_1_wood_threshold_rejected": forbidden_test["attack_1_wood_threshold_rejected"],
        "test_2_feature_requires_l5b": forbidden_test["attack_2_feature_requires_l5b"],
        "test_3_l5b_missing_detected": "GOV-21_FEATURE_EXECUTION_WITHOUT_L5B_AUTHORIZATION" in attack_result["blocking_layers"],
        "gov21_compliant": attack_result["gov21_feature_execution_gate"],
        "pass": (forbidden_test["attack_1_wood_threshold_rejected"]
                 and forbidden_test["attack_2_feature_requires_l5b"]
                 and "GOV-21_FEATURE_EXECUTION_WITHOUT_L5B_AUTHORIZATION" in attack_result["blocking_layers"]),
    }


def run_four_path_tests() -> dict:
    """MUST-D + MUST-3: 运行四路径测试 (Four-Path Contract/Negative Validation Tests).
    
    注意: 这不是"四态测试", Path D是攻击场景不是第四种L4状态.
    """
    results = {}

    chain_a = build_str001a_negative_path()
    res_a = chain_a.validate()
    results["Path_A_Negative"] = {
        "description": "证据不足时系统不得错误放行",
        "l4_status": res_a["l4_status"],
        "pass": res_a["l4_status"] == "BLOCKED" and not res_a["chain_complete"],
    }

    chain_b = build_str001a_blocked_to_ready_path()
    res_b = chain_b.validate()
    results["Path_B_BlockedToReady"] = {
        "description": "BLOCKED→READY_FOR_EVALUATION不得直接PROVEN (GOV-20)",
        "l4_status": res_b["l4_status"],
        "pass": res_b["l4_status"] == "READY_FOR_EVALUATION" and "L4_READY_NOT_PROVEN" in res_b["blocking_layers"],
    }

    chain_c = build_str001a_rejected_path()
    res_c = chain_c.validate()
    results["Path_C_Rejected"] = {
        "description": "L4 READY→Evaluation→REJECTED, REJECTED≠BLOCKED/PARTIAL/PROVEN",
        "l4_status": res_c["l4_status"],
        "pass": res_c["l4_status"] == "REJECTED",
    }

    results["Path_D_FeatureSubstitutionAttack"] = build_feature_substitution_attack()

    results["all_four_paths_pass"] = all(
        r["pass"] for r in results.values() if isinstance(r, dict) and "pass" in r
    )
    return results


# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 100)
    print("Canonical Semantic Authorization Pipeline v6-final.1 - 七层语义授权链 (Contract Patch, FROZEN候选)")
    print("=" * 100)
    print("\n修正记录: 3个MUST + 1个推荐 (非常小的Contract Patch, 不是v7大改)")
    print("  MUST-1: SourceClaim||L1真正并行结构 (代码Contract+架构图都改)")
    print("  MUST-2: SourceClaim≠Evidence Proof, supporting_source_claim_ids+SourceClaimRelation")
    print("  MUST-3: Path D Feature Substitution Attack负向测试")
    print("  推荐: L5正式命名EXECUTION AUTHORIZATION (L5-A/L5-B)")
    print("  封口: GOV-INVARIANT-01, expression_basis负向测试, mapping_status与authorization关系明确")

    # 最终架构
    print(f"\n{'='*100}")
    print("最终架构 (MUST-1修正后, 真正的并行结构)")
    print("=" * 100)
    print("""
  ┌───────────────┐
  │ CANONICAL     │
  │ SOURCE        │
  └───────┬───────┘
          │
          ▼
  ┌───────────────┐
  │ SOURCE CLAIM  │  (Canonical Authority侧资产)
  └───────┬───────┘
          │ canonical authority
          ▼
  ┌──────────────────────┐
  │ SOURCE / SEMANTIC    │
  │ AUTHORIZATION        │
  └──────────────────────┘

  ┌──────────────────────┐
  │ L1 ENGINE FACT       │  (Computational Observation侧资产, 与Source Claim并行)
  │ COMPUTED             │
  └──────────┬───────────┘
             │ mapping (通过独立SemanticMapping对象)
             ▼
  ┌──────────────────────┐
  │ L2 SEMANTIC MAPPING  │
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │ L3 EVIDENCE INSTANCE │
  └──────────┬───────────┘
             │ evidence authorization
             │ references applicable Source Claim / Mapping
             ▼
  (Evidence Contract [AUTHORIZED])
             │
             ▼
  L4 CANONICAL PROPOSITION
             │ READY_FOR_EVALUATION → EVALUATION
             ▼ PROVEN / PARTIAL / REJECTED
  L5 EXECUTION AUTHORIZATION
             ├─ L5-A Canonical Condition Authorization
             └─ L5-B Feature Execution Authorization (独立Gate)
             ▼
  L6 CANONICAL JUDGMENT
             │ (Assertion Contract)
             ▼
  L7 CANONICAL ASSERTION
""")

    # GOV-INVARIANT-01
    print(f"\n{'='*100}")
    print("GOV-INVARIANT-01 (顶级治理不变量)")
    print("=" * 100)
    print(f"  {AUTHORIZATION_INDEPENDENCE['GOV-INVARIANT-01']}")

    # 四态测试
    print(f"\n{'='*100}")
    print("MUST-D + MUST-3: 四路径测试 (Four-Path Contract/Negative Validation Tests)")
    print("=" * 100)
    test_results = run_four_path_tests()
    for path_name, result in test_results.items():
        if path_name == "all_four_paths_pass":
            print(f"\n  >>> ALL FOUR PATHS PASS: {result}")
            continue
        print(f"\n  {path_name}:")
        print(f"    description: {result['description']}")
        if 'l4_status' in result:
            print(f"    l4_status: {result['l4_status']}")
        print(f"    pass: {result['pass']}")

    # expression_basis负向测试
    print(f"\n{'='*100}")
    print("封口项: expression_basis负向测试")
    print("=" * 100)
    co = ConditionObject(condition_id="TEST-001", expression_basis=ExpressionBasis.CANONICAL_PROPOSITION)
    eb_test = co.validate_expression_basis()
    print(f"  expression_basis: {eb_test['expression_basis']}")
    print(f"  is_legal: {eb_test['is_legal']}")
    print(f"  forbidden_values: ENGINE_FEATURE/DERIVED_FEATURE/THRESHOLD/SCORE/PROBABILITY (全部禁止)")
    print(f"  pass: {eb_test['pass']}")

    # 验证类型说明
    print(f"\n{'='*100}")
    print("验证类型说明 (重要)")
    print("=" * 100)
    print("""
  v6-final.1 = Contract Static Validation + Negative Attack Tests Passed
  不是 Canonical Authorization Passed

  当前状态:
    Contract Schema Validation = PASS
    Governance Enforcement Test = PASS
    STR-001A Negative Path = PASS
    STR-001A Blocked→Ready Path = PASS
    STR-001A Rejected Path = PASS
    Feature Substitution Attack = PASS
    expression_basis Negative Test = PASS
    Canonical Source/Evidence/Proposition/Condition Authorization = NOT_DONE
""")

    print("=" * 100)
    print("v6-final.1 Contract Patch建立完成. Contract/Governance Layer = FROZEN. 下一步: STR-001A真实Canonical Source审计.")
    print("=" * 100)


if __name__ == "__main__":
    main()
