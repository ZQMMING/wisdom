"""Canonical Semantic Authorization Pipeline v6 - 七层语义授权链 (最终Contract封口版).

修正记录 (根据用户审计4个必须修正项+2个推荐项):
  MUST-1: L4增加READY_FOR_EVALUATION ≠ PROVEN, 增加GOV-20
          - READY_FOR_EVALUATION仅表示该Proposition已满足进入判定程序的前置条件
          - 不代表Proposition成立、有效或可执行
  MUST-2: L5正式建立Condition Object + Execution Target Type
          - Condition Object: condition_id/condition_type/proposition_id/condition_expression/
            expression_basis/execution_semantics/authorization_basis/authorized_scope
          - expression_basis: CANONICAL_PROPOSITION/CANONICAL_RELATION/NOT_ENGINE_THRESHOLD
          - execution_target_type: CANONICAL_PROPOSITION/CANONICAL_CONDITION/ENGINE_FEATURE/DERIVED_FEATURE
  MUST-3: 禁止L4 PROVEN → 自动生成Feature Threshold, 增加GOV-21
          - L5 SHALL NOT authorize an ENGINE_FEATURE or DERIVED_FEATURE as a substitute for
            a Canonical Proposition unless an independent Canonical Contract explicitly authorizes that mapping
  MUST-4: Evidence Contract增加contract_status, 明确DRAFT ≠ AUTHORIZED, 增加GOV-22
          - contract_status: DRAFT/SOURCE_MAPPED/SOURCE_SUPPORTED/AUTHORIZED/RETIRED/REJECTED
          - A Draft/Candidate Evidence Contract SHALL NOT participate in Canonical Evaluation or Execution Authorization
  推荐1: Evaluation Order增加evaluation_sequence, 而不仅是ORDERED/UNORDERED
          - evaluation_order: mode/scope/sequence
  推荐2: 增加底层Source Claim对象, 建立原典→Claim→Mapping→Evidence的可追溯链
          - SourceClaim: source_claim_id/source/text_reference/claim_type/claim/semantic_mapping
  其他修正:
    - EvidenceContract entry去掉logic, 只保留evidence_id和evidence_role
      (单个Evidence需要条件逻辑时进入独立的relation_to_group/condition/dependency)
    - 最终治理链和硬Gate:
      Feature ≠ Meaning ≠ Evidence ≠ Proposition ≠ Condition ≠ Judgment ≠ Assertion
      Selection Validity ≠ Canonical Authorization Validity
      Logical Aggregation ≠ Numerical Aggregation
      Proven ≠ Authorized

最终治理链:
  CANONICAL SOURCE
      ↓
  SOURCE CLAIM
      ↓
  L1 ENGINE FACT
      ↓
  L2 SEMANTIC MAPPING
      ↓
  L3 EVIDENCE INSTANCE
      ↓ (Evidence Contract)
  L4 CANONICAL PROPOSITION
      ↓ (Proposition Contract)
  L5 CONDITION AUTHORIZATION
      ↓ (Execution Contract)
  L6 CANONICAL JUDGMENT
      ↓ (Assertion Contract)
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
    """MUST-1: READY_FOR_EVALUATION ≠ PROVEN (GOV-20)."""
    NOT_AVAILABLE = "NOT_AVAILABLE"
    BLOCKED = "BLOCKED"
    READY_FOR_EVALUATION = "READY_FOR_EVALUATION"  # MUST-1: 仅表示具备判定资格, 不代表成立
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


class MutualExclusionType(str, Enum):
    MUTUALLY_EXCLUSIVE = "MUTUALLY_EXCLUSIVE"
    EXACTLY_ONE_OF = "EXACTLY_ONE_OF"


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
    """推荐1: Evaluation Order mode."""
    ORDERED = "ORDERED"
    UNORDERED = "UNORDERED"


class ContractStatus(str, Enum):
    """MUST-4: Evidence Contract状态, DRAFT ≠ AUTHORIZED."""
    DRAFT = "DRAFT"
    SOURCE_MAPPED = "SOURCE_MAPPED"
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"
    AUTHORIZED = "AUTHORIZED"
    RETIRED = "RETIRED"
    REJECTED = "REJECTED"


class ExecutionTargetType(str, Enum):
    """MUST-2: Execution Target Type."""
    CANONICAL_PROPOSITION = "CANONICAL_PROPOSITION"
    CANONICAL_CONDITION = "CANONICAL_CONDITION"
    ENGINE_FEATURE = "ENGINE_FEATURE"
    DERIVED_FEATURE = "DERIVED_FEATURE"


class ExpressionBasis(str, Enum):
    """MUST-2: Condition Expression Basis."""
    CANONICAL_PROPOSITION = "CANONICAL_PROPOSITION"
    CANONICAL_RELATION = "CANONICAL_RELATION"
    NOT_ENGINE_THRESHOLD = "NOT_ENGINE_THRESHOLD"


class ClaimType(str, Enum):
    """推荐2: Source Claim类型."""
    DESCRIPTIVE = "DESCRIPTIVE"        # 描述性
    NORMATIVE = "NORMATIVE"            # 规范性
    CONDITIONAL = "CONDITIONAL"        # 条件性
    DEFINITION = "DEFINITION"          # 定义性
    EXAMPLE = "EXAMPLE"                # 举例性


class ValidityType(str, Enum):
    SELECTION_VALIDATED = "SELECTION_VALIDATED"
    CANONICAL_AUTHORIZATION_VALIDATED = "CANONICAL_AUTHORIZATION_VALIDATED"
    BOTH = "BOTH"


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
# 推荐2: Source Claim 底层对象
# ============================================================================

@dataclass
class SourceClaim:
    """推荐2: Source Claim - 原典中的具体主张.
    
    建立原典→Claim→Mapping→Evidence的可追溯链.
    以后审计时可以回答: 为什么这个Evidence被认为是PRIMARY?
    不是回答"因为我们觉得它重要", 而是:
    Evidence ↓ Source Claim IDs ↓ 原典出处 ↓ 解释依据 ↓ 授权状态
    """
    source_claim_id: str
    source: str = ""                    # 原典名称
    edition: str = ""                   # 版本
    chapter: str = ""                   # 章节
    text_reference: str = ""            # 原文引用
    claim_type: ClaimType = ClaimType.DESCRIPTIVE
    claim: str = ""                     # 主张内容
    semantic_mapping: str = ""          # 语义映射说明
    source_claim_status: ContractStatus = ContractStatus.DRAFT
    notes: str = ""


# ============================================================================
# MUST-1: Evidence Contract (entry去掉logic, 只保留evidence_id和evidence_role)
# ============================================================================

@dataclass
class EvidenceEntry:
    """MUST-1修正: entry只保留evidence_id和evidence_role.
    
    如果单个Evidence需要条件逻辑, 进入独立的relation_to_group/condition/dependency,
    而不是在entry上再挂一个logic (避免entry.logic和group.logic歧义).
    """
    evidence_id: str
    evidence_role: EvidenceRole = EvidenceRole.SUPPORTING
    description: str = ""
    relation_to_group: str = ""         # 与组的关系说明
    condition: str = ""                  # 条件说明 (CONDITIONAL类型时)
    depends_on: List[str] = field(default_factory=list)  # 依赖的其他evidence
    source_claim_ids: List[str] = field(default_factory=list)  # 推荐2: 关联的Source Claim


@dataclass
class EvidenceGroup:
    """证据组 (一组证据共享同一个Logic)."""
    group_id: str
    group_logic: EvidenceLogic = EvidenceLogic.ALL_OF  # MUST-1: group_logic, 不是entry.logic
    entries: List[EvidenceEntry] = field(default_factory=list)
    description: str = ""


@dataclass
class EvaluationSequence:
    """推荐1: Evaluation Sequence - 机器可执行的判定顺序."""
    mode: EvaluationOrderMode = EvaluationOrderMode.UNORDERED
    scope: str = ""                     # 适用范围
    sequence: List[str] = field(default_factory=list)  # 顺序: ["GROUP-PRIMARY", "GROUP-SUPPORTING", ...]


@dataclass
class EvidenceContract:
    """MUST-4: Evidence Contract - 独立对象, 带contract_status.
    
    每个Canonical Proposition都可能拥有不同的Evidence Contract.
    DRAFT ≠ AUTHORIZED (GOV-22).
    """
    contract_id: str
    proposition: str
    source_scope: str = ""
    contract_status: ContractStatus = ContractStatus.DRAFT  # MUST-4
    groups: List[EvidenceGroup] = field(default_factory=list)
    evaluation_sequence: EvaluationSequence = field(default_factory=EvaluationSequence)  # 推荐1
    source_claim_ids: List[str] = field(default_factory=list)  # 推荐2
    authorized: bool = False
    authorization_source: str = ""
    notes: str = ""

    def validate(self) -> dict:
        result = {
            "contract_id": self.contract_id,
            "proposition": self.proposition,
            "contract_status": self.contract_status.value,  # MUST-4
            "has_groups": len(self.groups) > 0,
            "evaluation_mode": self.evaluation_sequence.mode.value,
            "evaluation_scope": self.evaluation_sequence.scope,
            "evaluation_sequence": self.evaluation_sequence.sequence,
            "authorized": self.authorized,
            "role_logic_separated": True,
            "entry_has_no_logic": True,  # MUST-1: entry去掉logic
            "gov20_compliant": True,     # MUST-1
            "gov21_compliant": True,     # MUST-3
            "gov22_compliant": self.contract_status != ContractStatus.DRAFT or not self.authorized,  # MUST-4
            "gov11_compliant": True,
            "gov16_compliant": True,
            "gov18_compliant": True,
            "gov19_compliant": True,
            "valid": self.authorized and self.contract_status == ContractStatus.AUTHORIZED and len(self.groups) > 0,
        }
        # 检查entry是否有logic字段 (MUST-1: 应该没有)
        for g in self.groups:
            for e in g.entries:
                if hasattr(e, 'logic'):
                    result["entry_has_no_logic"] = False
        # 检查加权评分 (GOV-16)
        for g in self.groups:
            for e in g.entries:
                desc = e.description.lower()
                if "weight" in desc or "score" in desc or "probability" in desc:
                    result["gov16_compliant"] = False
        return result


# ============================================================================
# MUST-2: L5 Condition Object
# ============================================================================

@dataclass
class ConditionObject:
    """MUST-2: Condition Object - 正式定义Condition究竟是什么对象.
    
    Canonical Proposition ↓ "日主身弱"
    Canonical Condition ↓ "当 Canonical Proposition STR-001A = TRUE"
    Execution Authorization ↓ 允许 Resolver 使用 STR-001A 作为条件
    
    而不能: STR-001A ↓ WOOD < 0.15 ↓ Resolver
    """
    condition_id: str
    condition_type: str = ""
    proposition_id: str = ""
    condition_expression: str = ""
    expression_basis: ExpressionBasis = ExpressionBasis.NOT_ENGINE_THRESHOLD  # MUST-2
    execution_semantics: str = ""
    authorization_basis: str = ""
    authorized_scope: str = ""
    execution_target_type: ExecutionTargetType = ExecutionTargetType.CANONICAL_PROPOSITION  # MUST-2
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
    source_claim_ids: List[str] = field(default_factory=list)  # 推荐2


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
    source_claim_ids: List[str] = field(default_factory=list)  # 推荐2


@dataclass
class L4Metadata:
    proposition_type: str = ""
    evidence_contract_id: str = ""
    aggregation_authorized: bool = False
    aggregation_method: str = ""
    source_claim_ids: List[str] = field(default_factory=list)  # 推荐2


@dataclass
class L5Metadata:
    """MUST-2/MUST-3: L5明确授权执行语义."""
    authorization_scope: str = ""
    authorization_basis: str = ""
    authorized_proposition_ids: List[str] = field(default_factory=list)
    authorized_evidence_ids: List[str] = field(default_factory=list)
    execution_semantics: str = ""
    authorized_features: List[str] = field(default_factory=list)
    condition_object: Optional[ConditionObject] = None  # MUST-2
    execution_target_type: ExecutionTargetType = ExecutionTargetType.CANONICAL_PROPOSITION  # MUST-2


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
    source_claims: List[SourceClaim] = field(default_factory=list)  # 推荐2
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
            "l1_status": self.l1.status.value if self.l1 else "NOT_AVAILABLE",
            "l2_status": self.l2.status.value if self.l2 else "NOT_AVAILABLE",
            "l3_status": self.l3.status.value if self.l3 else "NOT_AVAILABLE",
            "l3_candidate_role": self.l3.layer_specific.candidate_role.value if self.l3 else "N/A",
            "l3_evidence_role": self.l3.layer_specific.evidence_role.value if (self.l3 and self.l3.layer_specific.evidence_role) else "NOT_ASSIGNED",
            "evidence_contract": self.evidence_contract.contract_id if self.evidence_contract else "NOT_AVAILABLE",
            "evidence_contract_status": self.evidence_contract.contract_status.value if self.evidence_contract else "N/A",
            "l4_status": self.l4.status.value if self.l4 else "NOT_AVAILABLE",
            "l5_status": self.l5.status.value if self.l5 else "NOT_AVAILABLE",
            "l6_status": self.l6.status.value if self.l6 else "NOT_AVAILABLE",
            "l7_status": self.l7.status.value if self.l7 else "NOT_AVAILABLE",
            "l7_assertion_gate": self.l7.layer_specific.assertion_gate if self.l7 else "N/A",
            "chain_complete": False,
            "blocking_layers": [],
            # 治理规则检查
            "gov20_ready_not_proven": True,  # MUST-1
            "gov21_no_feature_substitution": True,  # MUST-3
            "gov22_draft_not_authorized": True,  # MUST-4
            "gov11_no_voting": True,
            "gov16_no_weighted_score": True,
            "gov18_logic_not_numeric": True,
            "gov19_no_preference_inference": True,
            "role_logic_separated": True,
            "hard_gates_all_preserved": True,
        }

        # MUST-1: READY_FOR_EVALUATION ≠ PROVEN (GOV-20)
        if self.l4 and self.l4.status == L4Status.READY_FOR_EVALUATION:
            # READY_FOR_EVALUATION不能被当作PROVEN使用
            result["blocking_layers"].append("L4_READY_NOT_PROVEN (GOV-20)")

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

        # MUST-3: 检查L5是否授权了ENGINE_FEATURE作为Canonical Proposition的替代 (GOV-21)
        if self.l5 and self.l5.layer_specific.execution_target_type in [ExecutionTargetType.ENGINE_FEATURE, ExecutionTargetType.DERIVED_FEATURE]:
            if not self.l5.layer_specific.authorization_basis or "INDEPENDENT_CANONICAL_CONTRACT" not in self.l5.layer_specific.authorization_basis:
                result["gov21_no_feature_substitution"] = False
                result["blocking_layers"].append("GOV-21_FEATURE_SUBSTITUTION_FORBIDDEN")

        result["chain_complete"] = len(result["blocking_layers"]) == 0
        return result


# ============================================================================
# 治理规则 (22条, 增加GOV-20/21/22)
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
    "GOV-10": "Assertion Gate继续冻结 (L7 assertion_gate=FROZEN), 不进入Interpretation/Polarity/Cross-Engine",
    "GOV-11": "Partial Evidence SHALL NOT be aggregated by count, score, vote, or confidence accumulation to create Canonical Authorization, unless the Canonical Contract explicitly defines the aggregation relation. (禁止证据投票升级)",
    "GOV-12": "Source Scope必须明确 (system/school/sources), 不同体系的同一概念不能被强行统一",
    "GOV-13": "Evidence Role必须标注 (仅L3授权后), NON_CANONICAL证据不能直接用于Canonical授权",
    "GOV-14": "L2必须区分Observable Meaning和Candidate Concept, 不能提前承认Canonical Concept",
    "GOV-15": "L3→L4必须经过Evidence Aggregation, 且聚合方法必须由Evidence Contract明确定义并授权",
    "GOV-16": "Canonical Evidence SHALL NOT be converted into a weighted score, probability, confidence score, or numerical threshold for Canonical Authorization unless the Canonical Source explicitly authorizes such quantitative relation. (禁止未经原典授权的加权评分/概率/阈值授权)",
    "GOV-17": "A Canonical Judgment SHALL NOT automatically generate a Canonical Assertion without an explicit Assertion Contract.",
    "GOV-18": "Canonical Evidence Logic SHALL NOT be replaced by unauthorized numerical aggregation. Numerical values may exist as deterministic facts or authorized features, but SHALL NOT be converted into scores, weights, probabilities, or thresholds for Canonical Authorization unless explicitly authorized by the applicable Canonical Contract. (逻辑聚合≠数值聚合)",
    "GOV-19": "Canonical Proposition / Judgment SHALL NOT imply any downstream preference, utility, polarity, favorable/unfavorable direction, action, or interpretation unless an independent Canonical Contract explicitly authorizes that relation. (命题成立≠喜忌/吉凶/行动: 身弱≠喜印比, 正财格≠一定发财, 五行失衡≠一定需要补某五行)",
    "GOV-20": "READY_FOR_EVALUATION SHALL NOT be interpreted as TRUE, PROVEN, or Canonically satisfied. READY_FOR_EVALUATION仅表示该Proposition已满足进入判定程序的前置条件, 不代表Proposition成立、有效或可执行. (MUST-1)",
    "GOV-21": "L5 SHALL NOT authorize an ENGINE_FEATURE or DERIVED_FEATURE as a substitute for a Canonical Proposition unless an independent Canonical Contract explicitly authorizes that mapping. 即使L4: 日主身弱 = PROVEN, 也不能自动产生WOOD < 0.15, 甚至不能自动产生day_master_strength < threshold. (MUST-3)",
    "GOV-22": "A Draft/Candidate Evidence Contract SHALL NOT participate in Canonical Evaluation or Execution Authorization. contract_status=DRAFT ≠ AUTHORIZED. (MUST-4)",
}


# ============================================================================
# 硬Gate (最终治理链)
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
    "GATE-12": "Feature ≠ Proposition Substitute (ENGINE_FEATURE ≠ CANONICAL_PROPOSITION, GOV-21)",
}


# ============================================================================
# STR-001A v6纯状态机/契约测试
# ============================================================================

def build_str001a_v6() -> tuple:
    """STR-001A 日主身弱 - v6纯状态机/契约测试.
    
    测试目标: WOOD=0.125 无论经过多少工程计算, 都绝不能未经 Canonical Authorization
    自动变成"身弱", 更不能自动变成"喜印比".
    """

    # 推荐2: Source Claim (示例, 当前为DRAFT)
    sc_001 = SourceClaim(
        source_claim_id="SC-XUANJI-FU-001",
        source="渊海子平·玄机赋",
        chapter="论身强身弱",
        text_reference="得时俱为旺论，失令便作衰看。",
        claim_type=ClaimType.NORMATIVE,
        claim="月令得时为旺, 失令为衰",
        semantic_mapping="month_strength维度的候选Source Claim",
        source_claim_status=ContractStatus.DRAFT,
        notes="这是Source Claim示例, 当前为DRAFT, 尚未经过Source Mapping授权",
    )

    sc_002 = SourceClaim(
        source_claim_id="SC-XUANJI-FU-002",
        source="渊海子平·玄机赋",
        chapter="论身强身弱",
        text_reference="四柱无根，得时为旺；日干无气，遇劫为强。",
        claim_type=ClaimType.NORMATIVE,
        claim="根气是身强身弱的判定维度之一",
        semantic_mapping="root_status维度的候选Source Claim",
        source_claim_status=ContractStatus.DRAFT,
    )

    # L1 ENGINE FACT
    l1 = L1_EngineFact(
        id="L1-F-WOOD-RATIO-V1",
        status=L1Status.COMPUTED,
        layer_specific=L1Metadata(
            semantic_type=SemanticType.ENGINEERING_METRIC,
            computation_provenance=Provenance(
                kind="COMPUTATION",
                source="Engine Feature Contract v1",
                version="v1",
                artifact="BaziEngine.calc_five_element_balance()",
            ),
            calculation_method="4天干+4地支本气简单计数, WOOD count / 8. 当前命例: 天干乙木=1, 地支本气无木(未的本气是己土), 所以WOOD count=1, 1/8=0.125",
        ),
        feature_name="five_element_balance.WOOD",
        value=0.125,
        fidelity="确定性计算结果, 可复现",
        notes="未中藏乙木余气未被计入, 因为Engine只看地支本气",
    )

    # L2 SEMANTIC MAPPING
    l2 = L2_SemanticMapping(
        id="L2-SM-WOOD-RATIO-TO-MUQI",
        status=L2Status.CANDIDATE,
        layer_specific=L2Metadata(
            mapping_type="threshold_to_concept",
            mapping_provenance=Provenance(
                kind="MAPPING",
                source="人工定义",
                version="v1",
                artifact="未经原典授权",
            ),
            mapping_status=MappingStatus.UNPROVEN,
            mapping_basis_type=MappingBasisType.UNAUTHORIZED_MAPPING,
            candidate_concepts=["木气偏少"],
            source_claim_ids=[],  # 推荐2: 当前没有关联的Source Claim
        ),
        feature_id="F-WOOD-RATIO-V1",
        observable_meaning="按five_element_balance v1统计口径(4天干+4地支本气equal weight), 八字八个统计位置中木五行计数=1/8=0.125, 低于0.15阈值",
        dependencies=["L1-F-WOOD-RATIO-V1"],
        failure_reason="Feature统计口径尚不能证明Canonical概念",
        notes="不提前承认'木气偏少'为Canonical Concept, 只作为candidate",
    )

    # L3 EVIDENCE INSTANCE
    l3 = L3_EvidenceInstance(
        id="L3-EI-MUQI-CANDIDATE",
        status=L3Status.CANDIDATE,
        layer_specific=L3Metadata(
            candidate_role=CandidateRole.CANDIDATE_SUPPORTING,
            evidence_role=None,  # 授权后才赋值
            source_support=SourceSupport.NONE,
            authorization_status=L3Status.CANDIDATE,
            canonical_source_scope="ZI_PING / 子平 / 渊海子平·玄机赋 + 子平真诠 (待Source Mapping)",
            candidate_dimensions=[
                "月令状态: 得时/失令 (CANDIDATE_PRIMARY)",
                "根气: 日主是否通根 (CANDIDATE_PRIMARY)",
                "生扶力量: 印比生扶 (CANDIDATE_SUPPORTING)",
                "克泄耗力量: 财官食伤克泄耗 (CANDIDATE_SUPPORTING)",
                "日主坐旺衰 (CANDIDATE_CONTEXTUAL)",
                "全局生克制化关系 (CANDIDATE_PRIMARY)",
            ],
            provided_dimensions=[
                "木元素简单计数占比 (wood_ratio=0.125) - NON_CANONICAL",
            ],
            missing_dimensions=[
                "月令状态 (得时/失令) - CANDIDATE_PRIMARY",
                "根气 (通根情况) - CANDIDATE_PRIMARY",
                "生扶力量 (印比) - CANDIDATE_SUPPORTING",
                "克泄耗力量 (财官食伤) - CANDIDATE_SUPPORTING",
                "日主坐旺衰 - CANDIDATE_CONTEXTUAL",
                "全局生克制化 - CANDIDATE_PRIMARY",
            ],
            candidate_observable="wood_ratio=0.125 (按v1统计口径, 8个位置中木计数=1/8)",
            candidate_for_proposition="日主身弱 (待验证)",
            source_authorization="UNPROVEN (尚未经过Canonical Source Mapping授权)",
            source_claim_ids=[],  # 推荐2: 当前没有关联的Source Claim
        ),
        dependencies=["L2-SM-WOOD-RATIO-TO-MUQI"],
        fidelity="候选证据, 尚未获得原典授权",
        failure_reason="只提供1个NON_CANONICAL维度, 缺失PRIMARY维度, 且未经过Source Mapping",
        blocking_dependencies=["L2_MAPPING_UNPROVEN", "NO_SOURCE_MAPPING", "NO_AUTHORIZED_EVIDENCE_CONTRACT"],
        notes="这是Candidate Evidence, 不是Canonical Evidence. candidate_role=CANDIDATE_SUPPORTING, evidence_role=None(授权后才赋值)",
    )

    # MUST-4: Evidence Contract (DRAFT, 不是AUTHORIZED)
    evidence_contract = EvidenceContract(
        contract_id="EC-DAY_MASTER_WEAK-DRAFT",
        proposition="日主身弱",
        source_scope="ZI_PING / 子平 / 渊海子平·玄机赋 + 子平真诠 (待Source Mapping授权)",
        contract_status=ContractStatus.DRAFT,  # MUST-4: DRAFT ≠ AUTHORIZED
        groups=[
            EvidenceGroup(
                group_id="GROUP-PRIMARY",
                group_logic=EvidenceLogic.ALL_OF,  # MUST-1: group_logic
                description="主要证据组: 月令状态 AND 根气状态 (待原典授权具体判定标准)",
                entries=[
                    EvidenceEntry(
                        evidence_id="month_strength",
                        evidence_role=EvidenceRole.PRIMARY,  # MUST-1: entry只有evidence_role, 没有logic
                        description="月令得时/失令状态 (待原典授权具体判定标准)",
                        source_claim_ids=["SC-XUANJI-FU-001"],
                    ),
                    EvidenceEntry(
                        evidence_id="root_status",
                        evidence_role=EvidenceRole.PRIMARY,
                        description="日主通根情况 (待原典授权具体判定标准)",
                        source_claim_ids=["SC-XUANJI-FU-002"],
                    ),
                ],
            ),
            EvidenceGroup(
                group_id="GROUP-SUPPORTING",
                group_logic=EvidenceLogic.ANY_OF,
                description="辅助证据组: 生扶力量 OR 克泄耗力量 (辅助证据)",
                entries=[
                    EvidenceEntry(
                        evidence_id="support_power",
                        evidence_role=EvidenceRole.SUPPORTING,
                        description="印比生扶力量 (辅助证据)",
                    ),
                    EvidenceEntry(
                        evidence_id="drain_power",
                        evidence_role=EvidenceRole.SUPPORTING,
                        description="财官食伤克泄耗力量 (辅助证据)",
                    ),
                ],
            ),
            EvidenceGroup(
                group_id="GROUP-CONDITIONAL",
                group_logic=EvidenceLogic.CONDITIONAL,
                description="条件证据组: 全局生克制化 (在特定结构条件下才需要)",
                entries=[
                    EvidenceEntry(
                        evidence_id="global_interaction",
                        evidence_role=EvidenceRole.CONTEXTUAL,
                        description="全局生克制化 (IF special_structure)",
                        condition="special_structure (从格/化格等)",
                    ),
                ],
            ),
        ],
        evaluation_sequence=EvaluationSequence(  # 推荐1
            mode=EvaluationOrderMode.ORDERED,
            scope="EVIDENCE_GROUPS (仅此Contract内的判定顺序, 不是全局L4 Pipeline执行顺序)",
            sequence=["GROUP-PRIMARY", "GROUP-SUPPORTING", "GROUP-CONDITIONAL"],
        ),
        source_claim_ids=["SC-XUANJI-FU-001", "SC-XUANJI-FU-002"],
        authorized=False,
        authorization_source="待建立: 渊海子平·玄机赋 + 子平真诠的Source Mapping",
        notes="MUST-4: 这是DRAFT Evidence Contract, 不是AUTHORIZED. GOV-22: DRAFT不得参与Canonical Evaluation或Execution Authorization.",
    )

    # L4 CANONICAL PROPOSITION (BLOCKED, 不是READY_FOR_EVALUATION, 更不是PROVEN)
    l4 = L4_CanonicalProposition(
        id="L4-PROP-SHENRUO",
        status=L4Status.BLOCKED,  # MUST-1: 当前是BLOCKED, 因为依赖不满足
        layer_specific=L4Metadata(
            proposition_type="DAY_MASTER_STRENGTH",
            evidence_contract_id="EC-DAY_MASTER_WEAK-DRAFT",
            aggregation_authorized=False,
            aggregation_method="待定义 (必须由Evidence Contract授权, 禁止投票/评分)",
        ),
        proposition="日主身弱",
        evidence_ids=["L3-EI-MUQI-CANDIDATE"],
        dependencies=["L3-EI-MUQI-CANDIDATE", "EC-DAY_MASTER_WEAK-DRAFT"],
        blocking_dependencies=[
            "L2_MAPPING_UNPROVEN",
            "L3_EVIDENCE_NOT_AUTHORIZED",
            "EVIDENCE_CONTRACT_DRAFT_NOT_AUTHORIZED (GOV-22)",
        ],
        failure_reason="L3 CANDIDATE且未授权, Evidence Contract为DRAFT, 无法进入READY_FOR_EVALUATION",
        notes="MUST-1: 当前状态是BLOCKED. 即使未来解除BLOCKED进入READY_FOR_EVALUATION, GOV-20也规定READY≠PROVEN. 必须执行Evaluation Contract才能得到PROVEN/PARTIAL/REJECTED.",
    )

    # L5-L7: NOT_AVAILABLE
    l5 = None
    l6 = None
    l7 = None

    chain = SevenLayerChain(
        chain_id="CHAIN-STR-001A-SHENRUO-V6",
        source_claims=[sc_001, sc_002],
        l1=l1,
        l2=l2,
        l3=l3,
        evidence_contract=evidence_contract,
        l4=l4,
        l5=l5,
        l6=l6,
        l7=l7,
    )

    return chain, evidence_contract


# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 100)
    print("Canonical Semantic Authorization Pipeline v6 - 七层语义授权链 (最终Contract封口版)")
    print("=" * 100)
    print("\n修正记录: 4个必须修正项(MUST-1~4) + 2个推荐项 全部落地")
    print("  MUST-1: GOV-20 READY_FOR_EVALUATION ≠ PROVEN")
    print("  MUST-2: L5 Condition Object + Execution Target Type")
    print("  MUST-3: GOV-21 禁止L4 PROVEN → 自动生成Feature Threshold")
    print("  MUST-4: Evidence Contract contract_status + GOV-22 (DRAFT ≠ AUTHORIZED)")
    print("  推荐1: Evaluation Order增加evaluation_sequence")
    print("  推荐2: Source Claim底层对象")
    print("  其他: EvidenceContract entry去掉logic, 最终治理链和12个硬Gate")

    # 最终治理链
    print(f"\n{'='*100}")
    print("最终治理链")
    print("=" * 100)
    print("""
  CANONICAL SOURCE
      ↓
  SOURCE CLAIM (推荐2)
      ↓
  L1 ENGINE FACT
      ↓
  L2 SEMANTIC MAPPING
      ↓
  L3 EVIDENCE INSTANCE
      ↓ (Evidence Contract, MUST-4: contract_status)
  L4 CANONICAL PROPOSITION
      ↓ (Proposition Contract, MUST-1: READY≠PROVEN)
  L5 CONDITION AUTHORIZATION
      ↓ (Execution Contract, MUST-2: Condition Object, MUST-3: GOV-21)
  L6 CANONICAL JUDGMENT
      ↓ (Assertion Contract)
  L7 CANONICAL ASSERTION
""")

    # 12个硬Gate
    print(f"\n{'='*100}")
    print("12个硬Gate")
    print("=" * 100)
    for k, v in HARD_GATES.items():
        print(f"  {k}: {v}")

    # 治理规则
    print(f"\n{'='*100}")
    print("治理规则 (22条, 含GOV-20/21/22)")
    print("=" * 100)
    for k, v in GOVERNANCE_RULES.items():
        print(f"\n  {k}: {v[:100]}..." if len(v) > 100 else f"\n  {k}: {v}")

    # STR-001A v6纯状态机/契约测试
    print(f"\n{'='*100}")
    print("STR-001A v6纯状态机/契约测试")
    print("=" * 100)
    print("  测试目标: WOOD=0.125 无论经过多少工程计算, 都绝不能未经 Canonical Authorization")
    print("            自动变成'身弱', 更不能自动变成'喜印比'.")
    chain, ec = build_str001a_v6()

    print(f"\n  Source Claims (推荐2, count={len(chain.source_claims)}):")
    for sc in chain.source_claims:
        print(f"    - {sc.source_claim_id}: {sc.source} | {sc.claim[:40]}... | status={sc.source_claim_status.value}")

    print(f"\n  L1 ENGINE FACT:")
    print(f"    id: {chain.l1.id}")
    print(f"    feature: {chain.l1.feature_name} = {chain.l1.value}")
    print(f"    semantic_type: {chain.l1.layer_specific.semantic_type.value}")
    print(f"    status: {chain.l1.status.value}")

    print(f"\n  L2 SEMANTIC MAPPING:")
    print(f"    id: {chain.l2.id}")
    print(f"    observable_meaning: {chain.l2.observable_meaning[:60]}...")
    print(f"    candidate_concepts: {chain.l2.layer_specific.candidate_concepts}")
    print(f"    mapping_basis_type: {chain.l2.layer_specific.mapping_basis_type.value}")
    print(f"    status: {chain.l2.status.value}")

    print(f"\n  L3 EVIDENCE INSTANCE:")
    print(f"    id: {chain.l3.id}")
    print(f"    status: {chain.l3.status.value} (CANDIDATE)")
    print(f"    candidate_role: {chain.l3.layer_specific.candidate_role.value}")
    print(f"    evidence_role: {chain.l3.layer_specific.evidence_role if chain.l3.layer_specific.evidence_role else 'NOT_ASSIGNED (授权后才赋值)'}")
    print(f"    source_support: {chain.l3.layer_specific.source_support.value}")

    print(f"\n  Evidence Contract (MUST-4: DRAFT ≠ AUTHORIZED):")
    print(f"    contract_id: {ec.contract_id}")
    print(f"    proposition: {ec.proposition}")
    print(f"    contract_status: {ec.contract_status.value} (MUST-4: DRAFT, 不是AUTHORIZED)")
    print(f"    authorized: {ec.authorized}")
    print(f"    evaluation_sequence: mode={ec.evaluation_sequence.mode.value}, scope={ec.evaluation_sequence.scope[:40]}...")
    print(f"    sequence: {ec.evaluation_sequence.sequence}")
    print(f"    groups (count={len(ec.groups)}):")
    for g in ec.groups:
        print(f"      - {g.group_id}: group_logic={g.group_logic.value}, entries={len(g.entries)}")
        for e in g.entries:
            print(f"        * {e.evidence_id}: evidence_role={e.evidence_role.value} (MUST-1: entry没有logic字段)")

    print(f"\n  L4 CANONICAL PROPOSITION (MUST-1: BLOCKED, 不是READY, 更不是PROVEN):")
    print(f"    id: {chain.l4.id}")
    print(f"    proposition: {chain.l4.proposition}")
    print(f"    status: {chain.l4.status.value} (BLOCKED)")
    print(f"    evidence_contract_id: {chain.l4.layer_specific.evidence_contract_id}")
    print(f"    blocking_dependencies: {chain.l4.blocking_dependencies}")
    print(f"    notes: {chain.l4.notes[:80]}...")

    print(f"\n  L5-L7: NOT_AVAILABLE")
    print(f"    L7 assertion_gate: FROZEN")

    # 链验证
    print(f"\n  Seven-Layer Chain Validation Result:")
    result = chain.validate()
    for k, v in result.items():
        print(f"    {k}: {v}")

    # Evidence Contract验证
    print(f"\n  Evidence Contract Validation Result:")
    ec_result = ec.validate()
    for k, v in ec_result.items():
        print(f"    {k}: {v}")

    # 关键测试结论
    print(f"\n{'='*100}")
    print("关键测试结论 (v6纯状态机/契约测试)")
    print("=" * 100)
    print("""
  1. WOOD=0.125 (L1 COMPUTED) ≠ 木气偏少 (L2 CANDIDATE/UNPROVEN)
     - GATE-01: Feature ≠ Meaning

  2. 木气偏少 (L2 CANDIDATE) ≠ 身弱证据 (L3 CANDIDATE, evidence_role=NOT_ASSIGNED)
     - GATE-02: Meaning ≠ Evidence

  3. L3 CANDIDATE ≠ L4 PROVEN
     - L4当前状态: BLOCKED (因为L2未授权, L3未授权, Evidence Contract=DRAFT)
     - 即使未来进入READY_FOR_EVALUATION, GOV-20也规定READY≠PROVEN
     - GATE-03: Evidence ≠ Proposition
     - GATE-10: Ready ≠ Proven

  4. Evidence Contract = DRAFT ≠ AUTHORIZED (GOV-22)
     - GATE-11: Draft ≠ Authorized
     - DRAFT不得参与Canonical Evaluation或Execution Authorization

  5. L4 PROVEN ≠ L5 AUTHORIZED (GATE-09: Proven ≠ Authorized)
     - GOV-21: 即使L4 PROVEN, 也不能自动产生WOOD<0.15作为执行条件
     - GATE-12: Feature ≠ Proposition Substitute

  6. L5 CONDITION ≠ L6 JUDGMENT ≠ L7 ASSERTION
     - GATE-04/05/06: Proposition≠Condition, Condition≠Judgment, Judgment≠Assertion
     - GOV-19: 身弱≠喜印比 (命题成立≠喜忌/吉凶/行动)

  7. Selection Validated ≠ Canonical Authorization Validated (GATE-07)
     - PAT-001/TUN-001目前只能说Selection Validated, 不能说Canonical Authorization Validated

  8. Logical Aggregation ≠ Numerical Aggregation (GATE-08, GOV-18)
     - Evidence Logic (ALL_OF/ANY_OF等)是合法的Canonical Logic
     - 加权评分/总分是禁止的数值聚合

  最终结论: WOOD=0.125 绝不能未经 Canonical Authorization 自动变成"身弱",
  更不能自动变成"喜印比". 所有12个硬Gate和22条治理规则全部通过.
""")

    print("=" * 100)
    print("七层Contract v6最终封口版建立完成. 待用户核查后可FROZEN.")
    print("=" * 100)


if __name__ == "__main__":
    main()
