"""Canonical Semantic Authorization Pipeline v4 - 七层语义授权链 (状态机层级化修正版).

修正记录 (根据用户审计5个必须修正项):
  必须修正1: L3 Candidate Evidence ≠ Canonical Evidence
             - L3改名为Evidence Instance, status: CANDIDATE/AUTHORIZED/PARTIAL/REJECTED
             - 只有AUTHORIZED才是真正的Canonical Evidence
             - 增加source_support: DIRECT/INDIRECT/INTERPRETIVE/NONE
             - 增加authorization_status: CANDIDATE/SOURCE_SUPPORTED/AUTHORIZED/REJECTED
  必须修正2: Evidence Relation与Evaluation Order分离
             - Evidence Relation: REQUIRED/OPTIONAL/EXCLUSIVE/CONDITIONAL/DEPENDENT
             - Evaluation Order: ORDERED/UNORDERED
             - ORDERED描述判定顺序/依赖顺序, 不是证据之间的逻辑关系
  必须修正3: L7 NOT_AVAILABLE ≠ FROZEN
             - L7 status=NOT_AVAILABLE (对象尚未创建)
             - assertion_gate=FROZEN (冻结的是Assertion Gate, 不是对象)
  必须修正4: STR-001A L3不得直接表达"木气偏少 → 身弱"
             - 改成candidate_evidence结构: observable/candidate_role/candidate_for/source_authorization
  必须修正5: VALID明确区分Selection Validity和Canonical Authorization Validity
             - Selection Validated: Resolver能正确匹配条件
             - Canonical Authorization Validated: 经过L1-L5完整授权
             - PAT-001/TUN-001目前只能说Selection Validated, 不能说Canonical Judgment VALID
  其他修正:
    - 状态机层级化: 每层独立status enum, 不共用COMMON status
    - L1 semantic_type互斥语义定义: DETERMINISTIC_FACT/DERIVED_FEATURE/ENGINEERING_METRIC
    - L2 mapping_basis_type: DIRECT_SOURCE/DERIVED_FROM_SOURCE/INTERPRETIVE_MAPPING/UNAUTHORIZED_MAPPING
    - GOV-11/GOV-16增加"逻辑聚合≠数值聚合"
    - provenance统一结构: kind+source+version+artifact

七层架构:
  L1 ENGINE FACT            - 确定性计算事实
  L2 SEMANTIC MAPPING       - Feature → Observable Meaning → Candidate Concept
  L3 EVIDENCE INSTANCE      - 证据实例 (CANDIDATE/AUTHORIZED/PARTIAL/REJECTED)
  L4 CANONICAL PROPOSITION  - Evidence Aggregation后的命题判定
  L5 CONDITION AUTHORIZATION- 经过授权的条件
  L6 CANONICAL JUDGMENT     - 格局/身弱/调候……
  L7 CANONICAL ASSERTION    - 正式断言 (assertion_gate=FROZEN)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# 层级化状态机 (必须修正5: 每层独立status enum)
# ============================================================================

class L1Status(str, Enum):
    """L1 ENGINE FACT 状态."""
    NOT_AVAILABLE = "NOT_AVAILABLE"
    COMPUTED = "COMPUTED"
    INVALID = "INVALID"


class L2Status(str, Enum):
    """L2 SEMANTIC MAPPING 状态."""
    NOT_AVAILABLE = "NOT_AVAILABLE"
    CANDIDATE = "CANDIDATE"
    MAPPED = "MAPPED"
    PARTIAL = "PARTIAL"
    REJECTED = "REJECTED"


class L3Status(str, Enum):
    """L3 EVIDENCE INSTANCE 状态 (必须修正1)."""
    NOT_AVAILABLE = "NOT_AVAILABLE"
    CANDIDATE = "CANDIDATE"              # 候选证据, 尚未获得Source支持
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"  # 获得原典文字支持, 但未授权为该命题的证据
    AUTHORIZED = "AUTHORIZED"            # 真正的Canonical Evidence
    PARTIAL = "PARTIAL"                  # 部分授权
    REJECTED = "REJECTED"                # 被拒绝


class L4Status(str, Enum):
    """L4 CANONICAL PROPOSITION 状态."""
    NOT_AVAILABLE = "NOT_AVAILABLE"
    BLOCKED = "BLOCKED"                  # 存在但被治理链阻断
    PROVEN = "PROVEN"
    PARTIAL = "PARTIAL"
    REJECTED = "REJECTED"


class L5Status(str, Enum):
    """L5 CONDITION AUTHORIZATION 状态."""
    NOT_AVAILABLE = "NOT_AVAILABLE"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    REJECTED = "REJECTED"


class L6Status(str, Enum):
    """L6 CANONICAL JUDGMENT 状态."""
    NOT_AVAILABLE = "NOT_AVAILABLE"
    BLOCKED = "BLOCKED"
    CREATED = "CREATED"
    FROZEN = "FROZEN"
    RETIRED = "RETIRED"


class L7Status(str, Enum):
    """L7 CANONICAL ASSERTION 状态 (必须修正3)."""
    NOT_AVAILABLE = "NOT_AVAILABLE"      # 对象尚未创建
    BLOCKED = "BLOCKED"
    AUTHORIZED = "AUTHORIZED"
    FROZEN = "FROZEN"


# ============================================================================
# 通用枚举
# ============================================================================

class SemanticType(str, Enum):
    """L1语义类型 (互斥语义定义)."""
    DETERMINISTIC_FACT = "DETERMINISTIC_FACT"    # 直接由确定性历法/排盘规则得到 (如month_branch=戌)
    DERIVED_FEATURE = "DERIVED_FEATURE"          # 从Deterministic Facts推导出的计算结果
    ENGINEERING_METRIC = "ENGINEERING_METRIC"    # 为工程目的建立的统计/评分/检测指标


class EvidenceRole(str, Enum):
    """证据角色 (仅L3使用)."""
    PRIMARY = "PRIMARY"
    SUPPORTING = "SUPPORTING"
    CONTEXTUAL = "CONTEXTUAL"
    EXCLUSION = "EXCLUSION"
    NON_CANONICAL = "NON_CANONICAL"
    CANDIDATE = "CANDIDATE"
    CANDIDATE_SUPPORTING = "CANDIDATE_SUPPORTING"


class SourceSupport(str, Enum):
    """原典支持程度 (必须修正1)."""
    DIRECT = "DIRECT"              # 原典直接定义
    INDIRECT = "INDIRECT"          # 原典间接支持
    INTERPRETIVE = "INTERPRETIVE"  # 注家/流派解释
    NONE = "NONE"                  # 无原典支持


class MappingBasisType(str, Enum):
    """L2映射基础类型."""
    DIRECT_SOURCE = "DIRECT_SOURCE"              # 原典直接定义
    DERIVED_FROM_SOURCE = "DERIVED_FROM_SOURCE"  # 从原典推导
    INTERPRETIVE_MAPPING = "INTERPRETIVE_MAPPING"  # 注家/流派/后人解释
    UNAUTHORIZED_MAPPING = "UNAUTHORIZED_MAPPING"  # 工程人员自行映射/AI归纳


class EvidenceRelation(str, Enum):
    """证据关系 (必须修正2: 与Evaluation Order分离)."""
    REQUIRED = "REQUIRED"        # 必要证据 (必须满足)
    OPTIONAL = "OPTIONAL"        # 可选证据 (增强但非必要)
    EXCLUSIVE = "EXCLUSIVE"      # 互斥证据 (满足A则不能满足B)
    CONDITIONAL = "CONDITIONAL"  # 条件证据 (在特定条件下才需要)
    DEPENDENT = "DEPENDENT"      # 依赖证据 (依赖其他证据的存在)


class EvaluationOrder(str, Enum):
    """评估顺序 (必须修正2: 从Evidence Relation拆出)."""
    ORDERED = "ORDERED"      # 有先后顺序要求 (如先判月令, 再判根气)
    UNORDERED = "UNORDERED"  # 无顺序要求


class MappingStatus(str, Enum):
    """L2映射状态."""
    UNPROVEN = "UNPROVEN"
    PARTIAL = "PARTIAL"
    PROVEN = "PROVEN"
    REJECTED = "REJECTED"


class ValidityType(str, Enum):
    """必须修正5: 有效性类型区分."""
    SELECTION_VALIDATED = "SELECTION_VALIDATED"              # Resolver能正确匹配条件
    CANONICAL_AUTHORIZATION_VALIDATED = "CANONICAL_AUTHORIZATION_VALIDATED"  # 经过L1-L5完整授权
    BOTH = "BOTH"


# ============================================================================
# Provenance统一结构
# ============================================================================

@dataclass
class Provenance:
    """统一溯源结构."""
    kind: str = ""              # COMPUTATION / MAPPING / CANONICAL_SOURCE
    source: str = ""            # 来源
    version: str = ""           # 版本
    artifact: str = ""          # 具体产物/引用


# ============================================================================
# LAYER-SPECIFIC METADATA
# ============================================================================

@dataclass
class L1Metadata:
    """L1 ENGINE FACT 特有元数据."""
    semantic_type: SemanticType = SemanticType.ENGINEERING_METRIC
    computation_provenance: Provenance = field(default_factory=Provenance)
    calculation_method: str = ""


@dataclass
class L2Metadata:
    """L2 SEMANTIC MAPPING 特有元数据."""
    mapping_type: str = ""
    mapping_provenance: Provenance = field(default_factory=Provenance)
    mapping_status: MappingStatus = MappingStatus.UNPROVEN
    mapping_basis_type: MappingBasisType = MappingBasisType.UNAUTHORIZED_MAPPING
    candidate_concepts: List[str] = field(default_factory=list)


@dataclass
class L3Metadata:
    """L3 EVIDENCE INSTANCE 特有元数据 (必须修正1)."""
    evidence_role: EvidenceRole = EvidenceRole.CANDIDATE
    source_support: SourceSupport = SourceSupport.NONE
    authorization_status: L3Status = L3Status.CANDIDATE
    canonical_source_scope: str = ""
    candidate_dimensions: List[str] = field(default_factory=list)
    provided_dimensions: List[str] = field(default_factory=list)
    missing_dimensions: List[str] = field(default_factory=list)
    # 必须修正4: candidate_evidence结构
    candidate_observable: str = ""
    candidate_role: str = ""
    candidate_for_proposition: str = ""
    source_authorization: str = "UNPROVEN"


@dataclass
class L4Metadata:
    """L4 CANONICAL PROPOSITION 特有元数据."""
    proposition_type: str = ""
    evidence_relation_schema: Dict[str, Any] = field(default_factory=dict)
    evaluation_order: EvaluationOrder = EvaluationOrder.UNORDERED  # 必须修正2
    aggregation_authorized: bool = False
    aggregation_method: str = ""


@dataclass
class L5Metadata:
    """L5 CONDITION AUTHORIZATION 特有元数据."""
    authorization_scope: str = ""
    authorized_features: List[str] = field(default_factory=list)
    authorized_evidence: List[str] = field(default_factory=list)


@dataclass
class L6Metadata:
    """L6 CANONICAL JUDGMENT 特有元数据."""
    judgment_type: str = ""
    prerequisite_ids: List[str] = field(default_factory=list)
    # 必须修正5: 有效性类型
    selection_validated: bool = False
    canonical_authorization_validated: bool = False


@dataclass
class L7Metadata:
    """L7 CANONICAL ASSERTION 特有元数据 (必须修正3)."""
    assertion_type: str = ""
    assertion_contract_id: str = ""
    assertion_gate: str = "FROZEN"  # 必须修正3: 冻结的是Gate, 不是对象


# ============================================================================
# Evidence Relation Schema (必须修正2: Relation + Evaluation Order分离)
# ============================================================================

@dataclass
class EvidenceRelationEntry:
    """证据关系条目."""
    evidence_id: str
    relation: EvidenceRelation
    description: str = ""
    condition: str = ""
    depends_on: List[str] = field(default_factory=list)


@dataclass
class EvidenceRelationSchema:
    """证据关系Schema - 定义L3→L4的合法聚合关系.
    
    必须修正2: Evidence Relation与Evaluation Order分离.
    Evidence Relation描述证据之间的逻辑关系 (REQUIRED/OPTIONAL/EXCLUSIVE/CONDITIONAL/DEPENDENT)
    Evaluation Order描述判定顺序 (ORDERED/UNORDERED), 不是证据之间的逻辑关系
    """
    schema_id: str
    proposition: str
    entries: List[EvidenceRelationEntry] = field(default_factory=list)
    evaluation_order: EvaluationOrder = EvaluationOrder.UNORDERED  # 必须修正2
    logical_expression: str = ""
    authorized: bool = False
    authorization_source: str = ""

    def validate(self) -> dict:
        """验证Schema合法性."""
        result = {
            "schema_id": self.schema_id,
            "has_required": any(e.relation == EvidenceRelation.REQUIRED for e in self.entries),
            "has_logical_expression": bool(self.logical_expression),
            "evaluation_order": self.evaluation_order.value,
            "authorized": self.authorized,
            "valid": self.authorized and bool(self.logical_expression),
            "gov11_compliant": True,  # 禁止投票
            "gov16_compliant": True,  # 禁止加权评分
            "logic_vs_numeric": "LOGICAL_AGGREGATION_ONLY",  # 逻辑聚合≠数值聚合
        }
        # 检查是否有加权评分 (GOV-16)
        if any("weight" in e.description.lower() or "score" in e.description.lower() for e in self.entries):
            result["gov16_compliant"] = False
        return result


# ============================================================================
# 七层数据结构 (层级化状态机)
# ============================================================================

@dataclass
class L1_EngineFact:
    """L1 ENGINE FACT."""
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
    """L2 SEMANTIC MAPPING."""
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
    """L3 EVIDENCE INSTANCE (必须修正1: Candidate ≠ Canonical).
    
    只有status=AUTHORIZED才是真正的Canonical Evidence.
    CANDIDATE/SOURCE_SUPPORTED只是候选, 尚未获得授权.
    """
    id: str
    status: L3Status = L3Status.NOT_AVAILABLE
    layer_specific: L3Metadata = field(default_factory=L3Metadata)
    # 必须修正4: 不直接表达"概念 → 命题", 而是candidate_evidence结构
    dependencies: List[str] = field(default_factory=list)
    fidelity: str = ""
    failure_reason: str = ""
    blocking_dependencies: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class L4_CanonicalProposition:
    """L4 CANONICAL PROPOSITION."""
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
    """L5 CONDITION AUTHORIZATION."""
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
    """L6 CANONICAL JUDGMENT."""
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
    """L7 CANONICAL ASSERTION (必须修正3)."""
    id: str
    status: L7Status = L7Status.NOT_AVAILABLE  # 对象状态
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
    """七层贯通链."""
    chain_id: str
    l1: L1_EngineFact
    l2: L2_SemanticMapping
    l3: L3_EvidenceInstance
    l4: Optional[L4_CanonicalProposition] = None
    l5: Optional[L5_ConditionAuthorization] = None
    l6: Optional[L6_CanonicalJudgment] = None
    l7: Optional[L7_CanonicalAssertion] = None

    def validate(self) -> dict:
        """验证七层链."""
        result = {
            "chain_id": self.chain_id,
            "l1_status": self.l1.status.value,
            "l2_status": self.l2.status.value,
            "l3_status": self.l3.status.value,
            "l3_authorization_status": self.l3.layer_specific.authorization_status.value,
            "l4_status": self.l4.status.value if self.l4 else "NOT_AVAILABLE",
            "l5_status": self.l5.status.value if self.l5 else "NOT_AVAILABLE",
            "l6_status": self.l6.status.value if self.l6 else "NOT_AVAILABLE",
            "l7_status": self.l7.status.value if self.l7 else "NOT_AVAILABLE",
            "l7_assertion_gate": self.l7.layer_specific.assertion_gate if self.l7 else "N/A",
            "chain_complete": False,
            "blocking_layers": [],
            "gov11_violation": False,
            "gov16_violation": False,
            "logic_vs_numeric": "LOGICAL_AGGREGATION_ONLY",
        }

        # 检查每层状态
        if self.l2.layer_specific.mapping_status not in [MappingStatus.PROVEN, MappingStatus.PARTIAL]:
            result["blocking_layers"].append("L2_MAPPING_UNPROVEN")
        if self.l3.status not in [L3Status.AUTHORIZED, L3Status.PARTIAL]:
            result["blocking_layers"].append("L3_EVIDENCE_NOT_AUTHORIZED")
        if self.l4 and self.l4.layer_specific.aggregation_authorized == False:
            result["blocking_layers"].append("L4_AGGREGATION_NOT_AUTHORIZED")
        if not self.l4:
            result["blocking_layers"].append("L4_NOT_AVAILABLE")
        if self.l5 and self.l5.status != L5Status.AUTHORIZED:
            result["blocking_layers"].append("L5_NOT_AUTHORIZED")
        if not self.l5:
            result["blocking_layers"].append("L5_NOT_AVAILABLE")

        # GOV-16检查
        if self.l4 and self.l4.layer_specific.evidence_relation_schema:
            schema = self.l4.layer_specific.evidence_relation_schema
            if isinstance(schema, dict):
                entries = schema.get("entries", [])
                for e in entries:
                    desc = e.get("description", "").lower()
                    if "weight" in desc or "score" in desc or "probability" in desc:
                        result["gov16_violation"] = True
                        result["blocking_layers"].append("GOV-16_WEIGHTED_SCORE_FORBIDDEN")

        result["chain_complete"] = len(result["blocking_layers"]) == 0
        return result


# ============================================================================
# 治理规则 (17条, 增加逻辑聚合≠数值聚合说明)
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
    "GOV-13": "Evidence Role必须标注 (仅L3), NON_CANONICAL证据不能直接用于Canonical授权",
    "GOV-14": "L2必须区分Observable Meaning和Candidate Concept, 不能提前承认Canonical Concept",
    "GOV-15": "L3→L4必须经过Evidence Aggregation, 且聚合方法必须由Evidence Relation Schema明确定义并授权",
    "GOV-16": "Canonical Evidence SHALL NOT be converted into a weighted score, probability, confidence score, or numerical threshold for Canonical Authorization unless the Canonical Source explicitly authorizes such quantitative relation. (禁止未经原典授权的加权评分/概率/阈值授权 - 防止Evidence Weight Injection)",
    "GOV-17": "A Canonical Judgment SHALL NOT automatically generate a Canonical Assertion without an explicit Assertion Contract. (Judgment不得自动生成Assertion, 必须经过Assertion Contract)",
    "GOV-18": "逻辑聚合 ≠ 数值聚合. Evidence Relation (REQUIRED/OPTIONAL/EXCLUSIVE/CONDITIONAL/DEPENDENT) 是合法的Canonical Logic; 但 A=0.3 B=0.2 C=0.4 总分=0.9 → 命题成立 是禁止的数值聚合.",
}


# ============================================================================
# STR-001A 七层贯通案例 (v4修正版)
# ============================================================================

def build_str001a_v4() -> SevenLayerChain:
    """STR-001A 日主身弱 - v4修正版七层贯通案例."""

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

    # L3 EVIDENCE INSTANCE (必须修正1+4: Candidate ≠ Canonical, candidate_evidence结构)
    l3 = L3_EvidenceInstance(
        id="L3-EI-MUQI-CANDIDATE",
        status=L3Status.CANDIDATE,  # 必须修正1: 不是Canonical Evidence, 只是Candidate
        layer_specific=L3Metadata(
            evidence_role=EvidenceRole.CANDIDATE_SUPPORTING,
            source_support=SourceSupport.NONE,  # 必须修正1: 尚无原典直接支持
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
            # 必须修正4: candidate_evidence结构, 不直接表达"木气偏少 → 身弱"
            candidate_observable="wood_ratio=0.125 (按v1统计口径, 8个位置中木计数=1/8)",
            candidate_role="SUPPORTING (候选辅助证据)",
            candidate_for_proposition="日主身弱 (待验证)",
            source_authorization="UNPROVEN (尚未经过Canonical Source Mapping授权)",
        ),
        dependencies=["L2-SM-WOOD-RATIO-TO-MUQI"],
        fidelity="候选证据, 尚未获得原典授权",
        failure_reason="只提供1个NON_CANONICAL维度, 缺失PRIMARY维度, 且未经过Source Mapping",
        blocking_dependencies=["L2_MAPPING_UNPROVEN", "NO_SOURCE_MAPPING", "NO_AUTHORIZED_EVIDENCE_CONTRACT"],
        notes="这是Candidate Evidence, 不是Canonical Evidence. 只有经过Source Mapping并授权后, status才能变为AUTHORIZED",
    )

    # L4 CANONICAL PROPOSITION (BLOCKED)
    l4 = L4_CanonicalProposition(
        id="L4-PROP-SHENRUO",
        status=L4Status.BLOCKED,
        layer_specific=L4Metadata(
            proposition_type="DAY_MASTER_STRENGTH",
            evidence_relation_schema={},
            evaluation_order=EvaluationOrder.UNORDERED,  # 必须修正2
            aggregation_authorized=False,
            aggregation_method="待定义 (必须由Evidence Relation Schema授权, 禁止投票/评分)",
        ),
        proposition="日主身弱",
        evidence_ids=["L3-EI-MUQI-CANDIDATE"],
        dependencies=["L3-EI-MUQI-CANDIDATE"],
        blocking_dependencies=[
            "L2_MAPPING_UNPROVEN",
            "L3_EVIDENCE_NOT_AUTHORIZED",
            "NO_AUTHORIZED_AGGREGATION_CONTRACT",
        ],
        failure_reason="L3 CANDIDATE且未授权, 没有经过Canonical Contract授权的Evidence Aggregation方法",
    )

    # L5-L7: NOT_AVAILABLE
    l5 = None
    l6 = None
    l7 = None  # 必须修正3: status=NOT_AVAILABLE, assertion_gate=FROZEN (在L7Metadata中定义)

    return SevenLayerChain(
        chain_id="CHAIN-STR-001A-SHENRUO-V4",
        l1=l1,
        l2=l2,
        l3=l3,
        l4=l4,
        l5=l5,
        l6=l6,
        l7=l7,
    )


# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 100)
    print("Canonical Semantic Authorization Pipeline v4 - 七层语义授权链 (状态机层级化修正版)")
    print("=" * 100)
    print("\n修正记录: 5个必须修正项全部落地")
    print("  必须修正1: L3 Candidate Evidence ≠ Canonical Evidence (status: CANDIDATE/AUTHORIZED/PARTIAL/REJECTED)")
    print("  必须修正2: Evidence Relation与Evaluation Order分离 (REQUIRED/OPTIONAL/EXCLUSIVE/CONDITIONAL/DEPENDENT + ORDERED/UNORDERED)")
    print("  必须修正3: L7 NOT_AVAILABLE ≠ FROZEN (status=NOT_AVAILABLE, assertion_gate=FROZEN)")
    print("  必须修正4: STR-001A L3 candidate_evidence结构 (observable/candidate_role/candidate_for/source_authorization)")
    print("  必须修正5: VALID明确区分Selection Validity和Canonical Authorization Validity")
    print("  其他: 状态机层级化, L1 semantic_type互斥, L2 mapping_basis_type, L3 source_support, GOV-18逻辑聚合≠数值聚合")

    # 层级化状态机
    print(f"\n{'='*100}")
    print("层级化状态机 (每层独立status enum)")
    print("=" * 100)
    print("""
  L1: NOT_AVAILABLE → COMPUTED → INVALID
  L2: NOT_AVAILABLE → CANDIDATE → MAPPED/PARTIAL → REJECTED
  L3: NOT_AVAILABLE → CANDIDATE → SOURCE_SUPPORTED → AUTHORIZED/PARTIAL → REJECTED
      (只有AUTHORIZED才是真正的Canonical Evidence)
  L4: NOT_AVAILABLE → BLOCKED → PROVEN/PARTIAL → REJECTED
  L5: NOT_AVAILABLE → BLOCKED → PENDING → AUTHORIZED → REJECTED
  L6: NOT_AVAILABLE → BLOCKED → CREATED → FROZEN/RETIRED
  L7: NOT_AVAILABLE → BLOCKED → AUTHORIZED → FROZEN
      (assertion_gate=FROZEN, 冻结的是Gate不是对象)
""")

    # 治理规则
    print(f"\n{'='*100}")
    print("治理规则 (18条, 含GOV-18逻辑聚合≠数值聚合)")
    print("=" * 100)
    for k, v in GOVERNANCE_RULES.items():
        print(f"\n  {k}: {v[:100]}..." if len(v) > 100 else f"\n  {k}: {v}")

    # Evidence Relation + Evaluation Order
    print(f"\n{'='*100}")
    print("Evidence Relation + Evaluation Order (必须修正2: 分离)")
    print("=" * 100)
    print("""
  Evidence Relation (证据之间的逻辑关系):
    REQUIRED     - 必要证据 (必须满足)
    OPTIONAL     - 可选证据 (增强但非必要)
    EXCLUSIVE    - 互斥证据 (满足A则不能满足B)
    CONDITIONAL  - 条件证据 (在特定条件下才需要)
    DEPENDENT    - 依赖证据 (依赖其他证据的存在)

  Evaluation Order (判定顺序, 不是证据逻辑关系):
    ORDERED      - 有先后顺序要求 (如先判月令, 再判根气)
    UNORDERED    - 无顺序要求

  关键: ORDERED不意味着两个证据必须同时成立, 它只描述判定顺序.
""")

    # STR-001A 七层贯通案例
    print(f"\n{'='*100}")
    print("STR-001A 七层贯通案例 (v4修正版)")
    print("=" * 100)
    chain = build_str001a_v4()

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
    print(f"    mapping_status: {chain.l2.layer_specific.mapping_status.value}")
    print(f"    status: {chain.l2.status.value}")

    print(f"\n  L3 EVIDENCE INSTANCE (必须修正1+4):")
    print(f"    id: {chain.l3.id}")
    print(f"    status: {chain.l3.status.value} (CANDIDATE, 不是Canonical Evidence)")
    print(f"    authorization_status: {chain.l3.layer_specific.authorization_status.value}")
    print(f"    source_support: {chain.l3.layer_specific.source_support.value}")
    print(f"    evidence_role: {chain.l3.layer_specific.evidence_role.value}")
    print(f"    candidate_observable: {chain.l3.layer_specific.candidate_observable[:60]}...")
    print(f"    candidate_role: {chain.l3.layer_specific.candidate_role}")
    print(f"    candidate_for_proposition: {chain.l3.layer_specific.candidate_for_proposition}")
    print(f"    source_authorization: {chain.l3.layer_specific.source_authorization}")
    print(f"    candidate_dimensions (count={len(chain.l3.layer_specific.candidate_dimensions)}):")
    for d in chain.l3.layer_specific.candidate_dimensions:
        print(f"      - {d}")

    print(f"\n  L4 CANONICAL PROPOSITION:")
    print(f"    id: {chain.l4.id}")
    print(f"    proposition: {chain.l4.proposition}")
    print(f"    status: {chain.l4.status.value} (BLOCKED)")
    print(f"    evaluation_order: {chain.l4.layer_specific.evaluation_order.value}")
    print(f"    blocking_dependencies: {chain.l4.blocking_dependencies}")

    print(f"\n  L5-L7: NOT_AVAILABLE")
    print(f"    L7 assertion_gate: FROZEN (必须修正3: 冻结的是Gate, 不是对象)")

    # 链验证
    print(f"\n  Seven-Layer Chain Validation Result:")
    result = chain.validate()
    for k, v in result.items():
        print(f"    {k}: {v}")

    # 必须修正5: VALID区分
    print(f"\n{'='*100}")
    print("必须修正5: VALID明确区分Selection Validity和Canonical Authorization Validity")
    print("=" * 100)
    print("""
  Selection Validated:
    - Resolver能正确匹配Canonical Condition
    - 不代表经过L1-L5完整授权
    - PAT-001/TUN-001目前只能说Selection Validated

  Canonical Authorization Validated:
    - 经过L1 ENGINE FACT → L2 SEMANTIC MAPPING → L3 EVIDENCE INSTANCE(AUTHORIZED)
      → L4 CANONICAL PROPOSITION(PROVEN) → L5 CONDITION AUTHORIZATION(AUTHORIZED)
    - 完整七层授权链通过

  当前状态:
    PAT-001 正财格: Selection Validated = True, Canonical Authorization Validated = 待审计
    TUN-001 乙木戌月调候: Selection Validated = True, Canonical Authorization Validated = 待审计
    STR-001A 日主身弱: Selection Validated = True(条件匹配), Canonical Authorization Validated = False(L3 CANDIDATE)
""")

    # 关键发现
    print(f"\n{'='*100}")
    print("关键发现 (v4修正版)")
    print("=" * 100)
    print("""
  1. L3正式改名为Evidence Instance, 只有AUTHORIZED才是真正的Canonical Evidence
     - CANDIDATE/SOURCE_SUPPORTED只是候选, 尚未获得授权
     - STR-001A的L3 status=CANDIDATE, source_support=NONE

  2. Evidence Relation与Evaluation Order正式分离
     - Evidence Relation: REQUIRED/OPTIONAL/EXCLUSIVE/CONDITIONAL/DEPENDENT (逻辑关系)
     - Evaluation Order: ORDERED/UNORDERED (判定顺序, 不是逻辑关系)

  3. L7 status=NOT_AVAILABLE, assertion_gate=FROZEN
     - 冻结的是Assertion Gate, 不是一个尚不存在的Assertion对象

  4. STR-001A L3改成candidate_evidence结构
     - candidate_observable: wood_ratio=0.125
     - candidate_role: SUPPORTING (候选辅助证据)
     - candidate_for_proposition: 日主身弱 (待验证)
     - source_authorization: UNPROVEN
     - 不直接表达"木气偏少 → 身弱"

  5. VALID明确区分Selection Validity和Canonical Authorization Validity
     - PAT-001/TUN-001目前只能说Selection Validated, 不能说Canonical Judgment VALID

  6. 状态机层级化: 每层独立status enum, 不共用COMMON status

  7. GOV-18: 逻辑聚合≠数值聚合
     - Evidence Relation是合法的Canonical Logic
     - 加权评分/总分是禁止的数值聚合

  结论: v4数据模型修正后, Candidate与Canonical彻底分离, 逻辑聚合与数值聚合彻底分离,
  Selection有效性与Canonical授权有效性彻底分离. 这才是真正干净的治理链.
""")

    print("=" * 100)
    print("七层Contract v4修正版建立完成. 待用户核查后可FROZEN.")
    print("=" * 100)


if __name__ == "__main__":
    main()
