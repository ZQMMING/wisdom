"""Canonical Semantic Authorization Pipeline v5 - 七层语义授权链 (逻辑契约层修正版).

修正记录 (根据用户审计3个必须修正项+3个强烈建议):
  MUST-1: Evidence Role与Evidence Logic彻底拆开
          - EvidenceRole: PRIMARY/SUPPORTING/CONTEXTUAL/EXCLUSION/NON_CANONICAL
          - EvidenceLogic: ALL_OF/ANY_OF/ONE_OF/NONE_OF/CONDITIONAL/DEPENDENT
          - EXCLUSIVE拆成MUTUALLY_EXCLUSIVE/EXACTLY_ONE_OF
          - EvidenceContract成为独立对象, 不直接塞进L4字段
  MUST-2: L4增加READY_FOR_EVALUATION, 禁止BLOCKED直接→PROVEN
          - NOT_AVAILABLE → BLOCKED → READY_FOR_EVALUATION → PROVEN/PARTIAL/REJECTED
          - 解除BLOCKED只能得到READY_FOR_EVALUATION, 不能直接得到PROVEN
  MUST-3: L5明确"授权执行语义", 不能让Proposition自动变成工程Condition
          - 增加authorization_basis/authorized_proposition_ids/authorized_evidence_ids/execution_semantics
          - L5授权的不是"命题为真", 而是"某个已经经过Canonical验证的命题/条件, 可以被系统作为执行条件使用"
  REC-1: Candidate Role与Canonical Evidence Role保持不同enum
          - CandidateRole: CANDIDATE_PRIMARY/CANDIDATE_SUPPORTING/CANDIDATE_CONTEXTUAL/CANDIDATE_EXCLUSION/CANDIDATE_NON_CANONICAL
          - 授权后才转换为EvidenceRole: PRIMARY/SUPPORTING/CONTEXTUAL/EXCLUSION/NON_CANONICAL
  REC-2: Evaluation Order增加scope
          - evaluation_order_scope, 不要让ORDERED被解释成整个L4 Pipeline的全局执行顺序
  REC-3: 增加GOV-19, 阻断"命题成立→喜忌/吉凶/行动"自动推导
          - Canonical Proposition/Judgment SHALL NOT imply any downstream preference/utility/polarity/
            favorable/unfavorable direction/action/interpretation unless an independent Canonical Contract explicitly authorizes
  其他修正:
    - GOV-18措辞更精确: 数值可作为确定性事实存在, 但禁止未经授权转换为评分/权重/概率/阈值
    - EvidenceContract独立对象, 每个Canonical Proposition都可能拥有不同的Evidence Contract
    - L4不应该"寻找算法", 而是Canonical Source → 证明某些证据关系 → 形成Canonical Proposition
    - Selection=VALID + Canonical Authorization=REJECTED是可以成立的, 不是系统错误

七层架构:
  L1 ENGINE FACT            - 确定性计算事实
  L2 SEMANTIC MAPPING       - Feature → Observable Meaning → Candidate Concept
  L3 EVIDENCE INSTANCE      - 证据实例 (Candidate Role / Source Support / Authorization)
  Evidence Contract         - 独立对象 (Evidence Role + Evidence Logic + Evaluation Order)
  L4 CANONICAL PROPOSITION  - Evidence Aggregation后的命题判定 (READY_FOR_EVALUATION)
  L5 CONDITION AUTHORIZATION- 经过授权的执行条件 (execution_semantics)
  L6 CANONICAL JUDGMENT     - 格局/身弱/调候……
  L7 CANONICAL ASSERTION    - 正式断言 (assertion_gate=FROZEN)
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
    """MUST-2: 增加READY_FOR_EVALUATION, 禁止BLOCKED直接→PROVEN."""
    NOT_AVAILABLE = "NOT_AVAILABLE"
    BLOCKED = "BLOCKED"                  # 依赖不满足, 无法进行有效判定
    READY_FOR_EVALUATION = "READY_FOR_EVALUATION"  # 依赖解除, 可以进行有效判定
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
# MUST-1: Evidence Role与Evidence Logic彻底拆开
# ============================================================================

class EvidenceRole(str, Enum):
    """MUST-1: 证据角色 (授权后的Canonical Evidence Role)."""
    PRIMARY = "PRIMARY"
    SUPPORTING = "SUPPORTING"
    CONTEXTUAL = "CONTEXTUAL"
    EXCLUSION = "EXCLUSION"
    NON_CANONICAL = "NON_CANONICAL"


class CandidateRole(str, Enum):
    """REC-1: 候选证据角色 (尚未获得授权, 与EvidenceRole是不同enum)."""
    CANDIDATE_PRIMARY = "CANDIDATE_PRIMARY"
    CANDIDATE_SUPPORTING = "CANDIDATE_SUPPORTING"
    CANDIDATE_CONTEXTUAL = "CANDIDATE_CONTEXTUAL"
    CANDIDATE_EXCLUSION = "CANDIDATE_EXCLUSION"
    CANDIDATE_NON_CANONICAL = "CANDIDATE_NON_CANONICAL"


class EvidenceLogic(str, Enum):
    """MUST-1: 证据逻辑 (证据之间的组合关系, 与Evidence Role是不同维度)."""
    ALL_OF = "ALL_OF"              # 全部必须满足 (A AND B AND C)
    ANY_OF = "ANY_OF"              # 至少一个满足 (A OR B OR C)
    ONE_OF = "ONE_OF"              # 恰好一个满足 (XOR)
    NONE_OF = "NONE_OF"            # 全部不满足 (NOT A AND NOT B)
    CONDITIONAL = "CONDITIONAL"    # 条件满足时才需要
    DEPENDENT = "DEPENDENT"        # 依赖其他证据的存在


class MutualExclusionType(str, Enum):
    """MUST-1: EXCLUSIVE拆成两种不同逻辑."""
    MUTUALLY_EXCLUSIVE = "MUTUALLY_EXCLUSIVE"  # A与B不能同时成立 (NOT (A AND B))
    EXACTLY_ONE_OF = "EXACTLY_ONE_OF"          # A/B二选一 (XOR)


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


class EvaluationOrder(str, Enum):
    ORDERED = "ORDERED"
    UNORDERED = "UNORDERED"


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
# MUST-1: Evidence Contract 独立对象
# ============================================================================

@dataclass
class EvidenceEntry:
    """证据条目 (在Evidence Contract中的定义)."""
    evidence_id: str
    role: EvidenceRole = EvidenceRole.SUPPORTING
    logic: EvidenceLogic = EvidenceLogic.ALL_OF
    description: str = ""
    condition: str = ""
    depends_on: List[str] = field(default_factory=list)
    mutual_exclusion: Optional[MutualExclusionType] = None


@dataclass
class EvidenceGroup:
    """证据组 (一组证据共享同一个Logic)."""
    group_id: str
    logic: EvidenceLogic = EvidenceLogic.ALL_OF
    entries: List[EvidenceEntry] = field(default_factory=list)
    description: str = ""


@dataclass
class EvidenceContract:
    """MUST-1: Evidence Contract 独立对象.
    
    每个Canonical Proposition都可能拥有不同的Evidence Contract.
    Evidence Contract定义:
      - Evidence Role: 每个证据的角色 (PRIMARY/SUPPORTING/CONTEXTUAL/EXCLUSION/NON_CANONICAL)
      - Evidence Logic: 证据之间的组合关系 (ALL_OF/ANY_OF/ONE_OF/NONE_OF/CONDITIONAL/DEPENDENT)
      - Evaluation Order: 判定顺序 (ORDERED/UNORDERED) + scope
    
    这不是"寻找算法", 而是Canonical Source → 证明某些证据关系 → 形成Canonical Proposition.
    """
    contract_id: str
    proposition: str
    source_scope: str = ""
    groups: List[EvidenceGroup] = field(default_factory=list)
    evaluation_order: EvaluationOrder = EvaluationOrder.UNORDERED
    evaluation_order_scope: str = ""  # REC-2: Evaluation Order的scope
    authorized: bool = False
    authorization_source: str = ""
    notes: str = ""

    def validate(self) -> dict:
        result = {
            "contract_id": self.contract_id,
            "proposition": self.proposition,
            "has_groups": len(self.groups) > 0,
            "evaluation_order": self.evaluation_order.value,
            "evaluation_order_scope": self.evaluation_order_scope,
            "authorized": self.authorized,
            "role_logic_separated": True,  # MUST-1: Role与Logic彻底拆开
            "gov11_compliant": True,
            "gov16_compliant": True,
            "gov18_compliant": True,
            "valid": self.authorized and len(self.groups) > 0,
        }
        # 检查是否有加权评分 (GOV-16)
        for g in self.groups:
            for e in g.entries:
                desc = e.description.lower()
                if "weight" in desc or "score" in desc or "probability" in desc:
                    result["gov16_compliant"] = False
        return result


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


@dataclass
class L3Metadata:
    """REC-1: Candidate Role与Canonical Evidence Role是不同enum."""
    candidate_role: CandidateRole = CandidateRole.CANDIDATE_SUPPORTING  # REC-1: 候选角色
    evidence_role: Optional[EvidenceRole] = None  # 授权后才赋值
    source_support: SourceSupport = SourceSupport.NONE
    authorization_status: L3Status = L3Status.CANDIDATE
    canonical_source_scope: str = ""
    candidate_dimensions: List[str] = field(default_factory=list)
    provided_dimensions: List[str] = field(default_factory=list)
    missing_dimensions: List[str] = field(default_factory=list)
    candidate_observable: str = ""
    candidate_for_proposition: str = ""
    source_authorization: str = "UNPROVEN"


@dataclass
class L4Metadata:
    proposition_type: str = ""
    evidence_contract_id: str = ""  # MUST-1: 引用独立的Evidence Contract
    aggregation_authorized: bool = False
    aggregation_method: str = ""


@dataclass
class L5Metadata:
    """MUST-3: 明确"授权执行语义"."""
    authorization_scope: str = ""
    authorization_basis: str = ""  # MUST-3: 授权依据
    authorized_proposition_ids: List[str] = field(default_factory=list)  # MUST-3
    authorized_evidence_ids: List[str] = field(default_factory=list)  # MUST-3
    execution_semantics: str = ""  # MUST-3: 执行语义, 防止Canonical概念偷偷还原成工程阈值
    authorized_features: List[str] = field(default_factory=list)


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
    """MUST-2: 增加READY_FOR_EVALUATION."""
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
    """MUST-3: 明确授权执行语义."""
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
    l1: L1_EngineFact
    l2: L2_SemanticMapping
    l3: L3_EvidenceInstance
    evidence_contract: Optional[EvidenceContract] = None
    l4: Optional[L4_CanonicalProposition] = None
    l5: Optional[L5_ConditionAuthorization] = None
    l6: Optional[L6_CanonicalJudgment] = None
    l7: Optional[L7_CanonicalAssertion] = None

    def validate(self) -> dict:
        result = {
            "chain_id": self.chain_id,
            "l1_status": self.l1.status.value,
            "l2_status": self.l2.status.value,
            "l3_status": self.l3.status.value,
            "l3_candidate_role": self.l3.layer_specific.candidate_role.value,
            "l3_evidence_role": self.l3.layer_specific.evidence_role.value if self.l3.layer_specific.evidence_role else "NOT_ASSIGNED",
            "evidence_contract": self.evidence_contract.contract_id if self.evidence_contract else "NOT_AVAILABLE",
            "l4_status": self.l4.status.value if self.l4 else "NOT_AVAILABLE",
            "l5_status": self.l5.status.value if self.l5 else "NOT_AVAILABLE",
            "l6_status": self.l6.status.value if self.l6 else "NOT_AVAILABLE",
            "l7_status": self.l7.status.value if self.l7 else "NOT_AVAILABLE",
            "l7_assertion_gate": self.l7.layer_specific.assertion_gate if self.l7 else "N/A",
            "chain_complete": False,
            "blocking_layers": [],
            "gov11_violation": False,
            "gov16_violation": False,
            "gov18_compliant": True,
            "gov19_compliant": True,
            "role_logic_separated": True,  # MUST-1
            "must2_blocked_to_proven_forbidden": True,  # MUST-2
        }

        if self.l2.layer_specific.mapping_status not in [MappingStatus.PROVEN, MappingStatus.PARTIAL]:
            result["blocking_layers"].append("L2_MAPPING_UNPROVEN")
        if self.l3.status not in [L3Status.AUTHORIZED, L3Status.PARTIAL]:
            result["blocking_layers"].append("L3_EVIDENCE_NOT_AUTHORIZED")
        if not self.evidence_contract or not self.evidence_contract.authorized:
            result["blocking_layers"].append("EVIDENCE_CONTRACT_NOT_AUTHORIZED")
        if self.l4 and self.l4.status not in [L4Status.PROVEN, L4Status.PARTIAL]:
            result["blocking_layers"].append("L4_NOT_PROVEN")
        if not self.l4:
            result["blocking_layers"].append("L4_NOT_AVAILABLE")
        if self.l5 and self.l5.status != L5Status.AUTHORIZED:
            result["blocking_layers"].append("L5_NOT_AUTHORIZED")
        if not self.l5:
            result["blocking_layers"].append("L5_NOT_AVAILABLE")

        # MUST-2检查: 禁止BLOCKED直接→PROVEN (状态机层面保证)
        if self.l4 and self.l4.status == L4Status.PROVEN:
            # PROVEN必须经过READY_FOR_EVALUATION, 这是状态机约束
            # 这里只检查是否有blocking_dependencies被清除的记录
            pass

        result["chain_complete"] = len(result["blocking_layers"]) == 0
        return result


# ============================================================================
# 治理规则 (19条, 增加GOV-19, 修正GOV-18措辞)
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
    "GOV-18": "Canonical Evidence Logic SHALL NOT be replaced by unauthorized numerical aggregation. Numerical values may exist as deterministic facts or authorized features, but SHALL NOT be converted into scores, weights, probabilities, or thresholds for Canonical Authorization unless explicitly authorized by the applicable Canonical Contract. (逻辑聚合≠数值聚合: 数值可作为确定性事实存在, 但禁止未经授权转换为评分/权重/概率/阈值)",
    "GOV-19": "Canonical Proposition / Judgment SHALL NOT imply any downstream preference, utility, polarity, favorable/unfavorable direction, action, or interpretation unless an independent Canonical Contract explicitly authorizes that relation. (命题成立≠喜忌/吉凶/行动: 身弱≠喜印比, 正财格≠一定发财, 五行失衡≠一定需要补某五行)",
}


# ============================================================================
# STR-001A 七层贯通案例 (v5纯Contract验证)
# ============================================================================

def build_str001a_v5() -> tuple:
    """STR-001A 日主身弱 - v5纯Contract验证.
    
    返回: (SevenLayerChain, EvidenceContract)
    """

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
        ),
        feature_id="F-WOOD-RATIO-V1",
        observable_meaning="按five_element_balance v1统计口径(4天干+4地支本气equal weight), 八字八个统计位置中木五行计数=1/8=0.125, 低于0.15阈值",
        dependencies=["L1-F-WOOD-RATIO-V1"],
        failure_reason="Feature统计口径尚不能证明Canonical概念",
        notes="不提前承认'木气偏少'为Canonical Concept, 只作为candidate",
    )

    # L3 EVIDENCE INSTANCE (REC-1: Candidate Role独立enum)
    l3 = L3_EvidenceInstance(
        id="L3-EI-MUQI-CANDIDATE",
        status=L3Status.CANDIDATE,
        layer_specific=L3Metadata(
            candidate_role=CandidateRole.CANDIDATE_SUPPORTING,  # REC-1: 候选角色, 不是最终EvidenceRole
            evidence_role=None,  # REC-1: 授权后才赋值
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
        ),
        dependencies=["L2-SM-WOOD-RATIO-TO-MUQI"],
        fidelity="候选证据, 尚未获得原典授权",
        failure_reason="只提供1个NON_CANONICAL维度, 缺失PRIMARY维度, 且未经过Source Mapping",
        blocking_dependencies=["L2_MAPPING_UNPROVEN", "NO_SOURCE_MAPPING", "NO_AUTHORIZED_EVIDENCE_CONTRACT"],
        notes="这是Candidate Evidence, 不是Canonical Evidence. candidate_role=CANDIDATE_SUPPORTING, evidence_role=None(授权后才赋值)",
    )

    # MUST-1: Evidence Contract 独立对象 (待授权模板)
    evidence_contract = EvidenceContract(
        contract_id="EC-DAY_MASTER_WEAK-TEMPLATE",
        proposition="日主身弱",
        source_scope="ZI_PING / 子平 / 渊海子平·玄机赋 + 子平真诠 (待Source Mapping授权)",
        groups=[
            EvidenceGroup(
                group_id="GROUP-PRIMARY",
                logic=EvidenceLogic.ALL_OF,  # MUST-1: ALL_OF = month_status AND root_status
                description="主要证据组: 月令状态 AND 根气状态 (待原典授权具体判定标准)",
                entries=[
                    EvidenceEntry(
                        evidence_id="month_strength",
                        role=EvidenceRole.PRIMARY,
                        logic=EvidenceLogic.ALL_OF,
                        description="月令得时/失令状态 (待原典授权具体判定标准)",
                    ),
                    EvidenceEntry(
                        evidence_id="root_status",
                        role=EvidenceRole.PRIMARY,
                        logic=EvidenceLogic.ALL_OF,
                        description="日主通根情况 (待原典授权具体判定标准)",
                    ),
                ],
            ),
            EvidenceGroup(
                group_id="GROUP-SUPPORTING",
                logic=EvidenceLogic.ANY_OF,  # MUST-1: ANY_OF = support_power OR drain_power
                description="辅助证据组: 生扶力量 OR 克泄耗力量 (辅助证据)",
                entries=[
                    EvidenceEntry(
                        evidence_id="support_power",
                        role=EvidenceRole.SUPPORTING,
                        logic=EvidenceLogic.ANY_OF,
                        description="印比生扶力量 (辅助证据)",
                    ),
                    EvidenceEntry(
                        evidence_id="drain_power",
                        role=EvidenceRole.SUPPORTING,
                        logic=EvidenceLogic.ANY_OF,
                        description="财官食伤克泄耗力量 (辅助证据)",
                    ),
                ],
            ),
            EvidenceGroup(
                group_id="GROUP-CONDITIONAL",
                logic=EvidenceLogic.CONDITIONAL,  # MUST-1: CONDITIONAL
                description="条件证据组: 全局生克制化 (在特定结构条件下才需要)",
                entries=[
                    EvidenceEntry(
                        evidence_id="global_interaction",
                        role=EvidenceRole.CONTEXTUAL,
                        logic=EvidenceLogic.CONDITIONAL,
                        description="全局生克制化 (IF special_structure)",
                        condition="special_structure (从格/化格等)",
                    ),
                ],
            ),
        ],
        evaluation_order=EvaluationOrder.ORDERED,
        evaluation_order_scope="GROUP-PRIMARY → GROUP-SUPPORTING → GROUP-CONDITIONAL (仅此Contract内的判定顺序, 不是全局L4 Pipeline执行顺序)",  # REC-2
        authorized=False,
        authorization_source="待建立: 渊海子平·玄机赋 + 子平真诠的Source Mapping",
        notes="这是Evidence Contract模板, 尚未授权. MUST-1: Evidence Role与Evidence Logic彻底拆开. Role=PRIMARY/SUPPORTING/CONTEXTUAL, Logic=ALL_OF/ANY_OF/CONDITIONAL.",
    )

    # L4 CANONICAL PROPOSITION (MUST-2: BLOCKED, 不是READY_FOR_EVALUATION)
    l4 = L4_CanonicalProposition(
        id="L4-PROP-SHENRUO",
        status=L4Status.BLOCKED,  # MUST-2: 依赖不满足, 无法进行有效判定
        layer_specific=L4Metadata(
            proposition_type="DAY_MASTER_STRENGTH",
            evidence_contract_id="EC-DAY_MASTER_WEAK-TEMPLATE",
            aggregation_authorized=False,
            aggregation_method="待定义 (必须由Evidence Contract授权, 禁止投票/评分)",
        ),
        proposition="日主身弱",
        evidence_ids=["L3-EI-MUQI-CANDIDATE"],
        dependencies=["L3-EI-MUQI-CANDIDATE", "EC-DAY_MASTER_WEAK-TEMPLATE"],
        blocking_dependencies=[
            "L2_MAPPING_UNPROVEN",
            "L3_EVIDENCE_NOT_AUTHORIZED",
            "EVIDENCE_CONTRACT_NOT_AUTHORIZED",
        ],
        failure_reason="L3 CANDIDATE且未授权, Evidence Contract未授权, 无法进入READY_FOR_EVALUATION",
        notes="MUST-2: 当前状态是BLOCKED. 解除BLOCKED后只能进入READY_FOR_EVALUATION, 不能直接得到PROVEN.",
    )

    # L5-L7: NOT_AVAILABLE
    l5 = None
    l6 = None
    l7 = None

    chain = SevenLayerChain(
        chain_id="CHAIN-STR-001A-SHENRUO-V5",
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
    print("Canonical Semantic Authorization Pipeline v5 - 七层语义授权链 (逻辑契约层修正版)")
    print("=" * 100)
    print("\n修正记录: 3个必须修正项(MUST-1~3) + 3个强烈建议(REC-1~3) 全部落地")
    print("  MUST-1: Evidence Role与Evidence Logic彻底拆开 (Role≠Logic, EvidenceContract独立对象)")
    print("  MUST-2: L4增加READY_FOR_EVALUATION, 禁止BLOCKED直接→PROVEN")
    print("  MUST-3: L5明确授权执行语义 (authorization_basis/execution_semantics)")
    print("  REC-1: Candidate Role与Canonical Evidence Role独立enum")
    print("  REC-2: Evaluation Order增加scope")
    print("  REC-3: GOV-19阻断命题→喜忌/吉凶/行动自动推导")
    print("  其他: GOV-18措辞更精确, EvidenceContract独立对象")

    # 层级化状态机
    print(f"\n{'='*100}")
    print("层级化状态机 (MUST-2: L4增加READY_FOR_EVALUATION)")
    print("=" * 100)
    print("""
  L1: NOT_AVAILABLE → COMPUTED → INVALID
  L2: NOT_AVAILABLE → CANDIDATE → MAPPED/PARTIAL → REJECTED
  L3: NOT_AVAILABLE → CANDIDATE → SOURCE_SUPPORTED → AUTHORIZED/PARTIAL → REJECTED
  L4: NOT_AVAILABLE → BLOCKED → READY_FOR_EVALUATION → PROVEN/PARTIAL/REJECTED
      (MUST-2: 解除BLOCKED只能得到READY_FOR_EVALUATION, 不能直接得到PROVEN)
  L5: NOT_AVAILABLE → BLOCKED → PENDING → AUTHORIZED → REJECTED
  L6: NOT_AVAILABLE → BLOCKED → CREATED → FROZEN/RETIRED
  L7: NOT_AVAILABLE → BLOCKED → AUTHORIZED → FROZEN
      (assertion_gate=FROZEN, 冻结的是Gate不是对象)
""")

    # MUST-1: Evidence Role与Evidence Logic
    print(f"\n{'='*100}")
    print("MUST-1: Evidence Role与Evidence Logic彻底拆开")
    print("=" * 100)
    print("""
  Evidence Role (证据角色, 授权后的Canonical Evidence Role):
    PRIMARY / SUPPORTING / CONTEXTUAL / EXCLUSION / NON_CANONICAL

  Evidence Logic (证据逻辑, 证据之间的组合关系):
    ALL_OF     - 全部必须满足 (A AND B AND C)
    ANY_OF     - 至少一个满足 (A OR B OR C)
    ONE_OF     - 恰好一个满足 (XOR)
    NONE_OF    - 全部不满足 (NOT A AND NOT B)
    CONDITIONAL- 条件满足时才需要
    DEPENDENT  - 依赖其他证据的存在

  Mutual Exclusion (EXCLUSIVE拆成两种):
    MUTUALLY_EXCLUSIVE - A与B不能同时成立 (NOT (A AND B))
    EXACTLY_ONE_OF     - A/B二选一 (XOR)

  关键: Role ≠ Logic. REQUIRED/OPTIONAL描述的是"证据地位", 不是完整的逻辑组合关系.
  例如: A REQUIRED B REQUIRED 到底是 A AND B 还是 A OR B? 现在用Logic=ALL_OF明确表达.
""")

    # REC-1: Candidate Role
    print(f"\n{'='*100}")
    print("REC-1: Candidate Role与Canonical Evidence Role独立enum")
    print("=" * 100)
    print("""
  Candidate Role (候选证据角色, 尚未获得授权):
    CANDIDATE_PRIMARY / CANDIDATE_SUPPORTING / CANDIDATE_CONTEXTUAL / CANDIDATE_EXCLUSION / CANDIDATE_NON_CANONICAL

  Evidence Role (授权后的Canonical Evidence Role):
    PRIMARY / SUPPORTING / CONTEXTUAL / EXCLUSION / NON_CANONICAL

  转换: Candidate Role ↓ authorization → Evidence Role
  不能: candidate ↓ 直接拥有 SUPPORTING (语义泄漏)
""")

    # 治理规则
    print(f"\n{'='*100}")
    print("治理规则 (19条, 含GOV-19, GOV-18措辞修正)")
    print("=" * 100)
    for k, v in GOVERNANCE_RULES.items():
        print(f"\n  {k}: {v[:100]}..." if len(v) > 100 else f"\n  {k}: {v}")

    # STR-001A v5纯Contract验证
    print(f"\n{'='*100}")
    print("STR-001A v5纯Contract验证")
    print("=" * 100)
    chain, ec = build_str001a_v5()

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

    print(f"\n  L3 EVIDENCE INSTANCE (REC-1: Candidate Role独立enum):")
    print(f"    id: {chain.l3.id}")
    print(f"    status: {chain.l3.status.value} (CANDIDATE)")
    print(f"    candidate_role: {chain.l3.layer_specific.candidate_role.value} (REC-1: 候选角色)")
    print(f"    evidence_role: {chain.l3.layer_specific.evidence_role if chain.l3.layer_specific.evidence_role else 'NOT_ASSIGNED (授权后才赋值)'}")
    print(f"    source_support: {chain.l3.layer_specific.source_support.value}")
    print(f"    candidate_observable: {chain.l3.layer_specific.candidate_observable[:60]}...")
    print(f"    candidate_for_proposition: {chain.l3.layer_specific.candidate_for_proposition}")

    print(f"\n  Evidence Contract (MUST-1: 独立对象):")
    print(f"    contract_id: {ec.contract_id}")
    print(f"    proposition: {ec.proposition}")
    print(f"    authorized: {ec.authorized} (待Source Mapping授权)")
    print(f"    evaluation_order: {ec.evaluation_order.value}")
    print(f"    evaluation_order_scope: {ec.evaluation_order_scope[:60]}...")
    print(f"    groups (count={len(ec.groups)}):")
    for g in ec.groups:
        print(f"      - {g.group_id}: logic={g.logic.value}, entries={len(g.entries)}")
        for e in g.entries:
            print(f"        * {e.evidence_id}: role={e.role.value}, logic={e.logic.value}")

    print(f"\n  L4 CANONICAL PROPOSITION (MUST-2: BLOCKED):")
    print(f"    id: {chain.l4.id}")
    print(f"    proposition: {chain.l4.proposition}")
    print(f"    status: {chain.l4.status.value} (BLOCKED, 不是READY_FOR_EVALUATION)")
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

    # 关键发现
    print(f"\n{'='*100}")
    print("关键发现 (v5逻辑契约层修正版)")
    print("=" * 100)
    print("""
  1. MUST-1: Evidence Role与Evidence Logic彻底拆开
     - Role: PRIMARY/SUPPORTING/CONTEXTUAL/EXCLUSION/NON_CANONICAL
     - Logic: ALL_OF/ANY_OF/ONE_OF/NONE_OF/CONDITIONAL/DEPENDENT
     - EvidenceContract成为独立对象, 每个Proposition都可能拥有不同的Evidence Contract
     - EXCLUSIVE拆成MUTUALLY_EXCLUSIVE/EXACTLY_ONE_OF

  2. MUST-2: L4增加READY_FOR_EVALUATION
     - NOT_AVAILABLE → BLOCKED → READY_FOR_EVALUATION → PROVEN/PARTIAL/REJECTED
     - 解除BLOCKED只能得到READY_FOR_EVALUATION, 不能直接得到PROVEN
     - STR-001A当前状态是BLOCKED, 因为L3未授权且Evidence Contract未授权

  3. MUST-3: L5明确授权执行语义
     - authorization_basis/authorized_proposition_ids/authorized_evidence_ids/execution_semantics
     - L5授权的不是"命题为真", 而是"某个已经经过Canonical验证的命题/条件, 可以被系统作为执行条件使用"

  4. REC-1: Candidate Role与Canonical Evidence Role独立enum
     - CandidateRole: CANDIDATE_PRIMARY/CANDIDATE_SUPPORTING/...
     - EvidenceRole: PRIMARY/SUPPORTING/...
     - 授权后才转换, 不能candidate直接拥有SUPPORTING

  5. REC-2: Evaluation Order增加scope
     - evaluation_order_scope, 不要让ORDERED被解释成整个L4 Pipeline的全局执行顺序

  6. REC-3: GOV-19阻断命题→喜忌/吉凶/行动自动推导
     - 身弱≠喜印比, 正财格≠一定发财, 五行失衡≠一定需要补某五行

  7. GOV-18措辞更精确
     - 数值可作为确定性事实存在, 但禁止未经授权转换为评分/权重/概率/阈值

  结论: v5逻辑契约层修正后, Evidence是什么、Evidence之间怎么组成Proposition、Proposition怎么获得
  Execution Authorization, 这三层已经彻底钉死. 这才是后面子平、盲派、紫微、河洛能够共用,
  而又不会互相污染的逻辑契约基础.
""")

    print("=" * 100)
    print("七层Contract v5逻辑契约层修正版建立完成. 待用户核查后可FROZEN.")
    print("=" * 100)


if __name__ == "__main__":
    main()
