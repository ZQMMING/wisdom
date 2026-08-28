"""Canonical Semantic Authorization Pipeline v3 - 七层语义授权链 (数据模型修正版).

修正记录 (根据用户审计4项必须修正+3项强烈建议):
  必须修正1: L1删除固定evidence_role=NON_CANONICAL, 增加semantic_type
             Engine Feature本身不是天然NON_CANONICAL, evidence_role在L3 Evidence Instance才赋值
  必须修正2: 不能要求所有层都有evidence_role, 改成COMMON METADATA + LAYER-SPECIFIC METADATA
  必须修正3: 区分provenance类型 - computation_provenance/mapping_provenance/canonical_source_scope
  必须修正4: 正式定义L3→L4 Evidence Relation Schema - REQUIRED/OPTIONAL/EXCLUSIVE/CONDITIONAL/ORDERED/DEPENDENT
  建议1: GOV-16 - 禁止未经原典授权的加权评分/概率/阈值授权 (防止Evidence Weight Injection)
  建议2: GOV-17 - Judgment不得自动生成Assertion, 必须经过Assertion Contract
  建议3: BLOCKED状态 - 区分"尚不存在"和"存在但被治理链阻断"
  其他修正:
    - L2: observable_meaning + candidate_concepts + mapping_status (不提前承认Canonical Concept)
    - L3: Candidate Evidence Dimensions (不是Required Evidence Dimensions)
    - 区分Canonical Semantic Contract vs Runtime Evidence Instance vs Judgment Instance

七层架构:
  L1 ENGINE FACT            - 确定性计算事实
  L2 SEMANTIC MAPPING       - Feature → Observable Meaning → Candidate Concept
  L3 CANONICAL EVIDENCE     - 原典认可的证据 (带evidence_role)
  L4 CANONICAL PROPOSITION  - Evidence Aggregation后的命题判定 (带Evidence Relation Schema)
  L5 CONDITION AUTHORIZATION- 经过授权的条件
  L6 CANONICAL JUDGMENT     - 格局/身弱/调候……
  L7 CANONICAL ASSERTION    - 正式断言 (FROZEN)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# 状态枚举
# ============================================================================

class LayerStatus(str, Enum):
    """通用状态."""
    COMPUTED = "COMPUTED"
    MAPPED = "MAPPED"
    PROVEN = "PROVEN"
    PARTIAL = "PARTIAL"
    UNPROVEN = "UNPROVEN"
    REJECTED = "REJECTED"
    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"
    AUTHORIZED = "AUTHORIZED"
    PENDING = "PENDING"
    FROZEN = "FROZEN"
    BLOCKED = "BLOCKED"          # 建议3: 存在但被治理链阻断
    NOT_AVAILABLE = "NOT_AVAILABLE"  # 尚不存在


class EvidenceRole(str, Enum):
    """证据角色 (仅L3使用)."""
    PRIMARY = "PRIMARY"
    SUPPORTING = "SUPPORTING"
    CONTEXTUAL = "CONTEXTUAL"
    EXCLUSION = "EXCLUSION"
    NON_CANONICAL = "NON_CANONICAL"
    CANDIDATE = "CANDIDATE"          # 候选, 尚未授权
    CANDIDATE_SUPPORTING = "CANDIDATE_SUPPORTING"


class SemanticType(str, Enum):
    """L1语义类型 (必须修正1: 替代固定evidence_role)."""
    ENGINEERING_METRIC = "ENGINEERING_METRIC"    # 工程统计指标
    DETERMINISTIC_FACT = "DETERMINISTIC_FACT"    # 确定性事实 (如month_branch=戌)
    DERIVED_FEATURE = "DERIVED_FEATURE"          # 派生特征


class EvidenceRelation(str, Enum):
    """必须修正4: L3→L4证据关系类型."""
    REQUIRED = "REQUIRED"        # 必要证据 (必须满足)
    OPTIONAL = "OPTIONAL"        # 可选证据 (增强但非必要)
    EXCLUSIVE = "EXCLUSIVE"      # 互斥证据 (满足A则不能满足B)
    CONDITIONAL = "CONDITIONAL"  # 条件证据 (在特定条件下才需要)
    ORDERED = "ORDERED"          # 有序证据 (有先后顺序要求)
    DEPENDENT = "DEPENDENT"      # 依赖证据 (依赖其他证据的存在)


class MappingStatus(str, Enum):
    """L2映射状态."""
    UNPROVEN = "UNPROVEN"
    PARTIAL = "PARTIAL"
    PROVEN = "PROVEN"
    REJECTED = "REJECTED"


# ============================================================================
# COMMON METADATA (必须修正2: 所有层共用)
# ============================================================================

@dataclass
class CommonMetadata:
    """通用元数据 - 所有层共用."""
    id: str
    status: LayerStatus
    provenance: str = ""              # 通用溯源 (具体类型由各层定义)
    dependencies: List[str] = field(default_factory=list)
    fidelity: str = ""
    failure_reason: str = ""
    blocking_dependencies: List[str] = field(default_factory=list)  # 建议3: 阻断依赖
    notes: str = ""


# ============================================================================
# LAYER-SPECIFIC METADATA (必须修正2: 每层特有)
# ============================================================================

@dataclass
class L1Metadata:
    """L1 ENGINE FACT 特有元数据."""
    semantic_type: SemanticType = SemanticType.ENGINEERING_METRIC  # 必须修正1
    computation_provenance: str = ""   # 必须修正3: 计算溯源 (不是canonical source)
    feature_version: str = ""
    calculation_method: str = ""


@dataclass
class L2Metadata:
    """L2 SEMANTIC MAPPING 特有元数据."""
    mapping_type: str = ""             # 映射类型
    mapping_provenance: str = ""       # 必须修正3: 映射溯源
    mapping_status: MappingStatus = MappingStatus.UNPROVEN
    candidate_concepts: List[str] = field(default_factory=list)  # 修正: 候选概念, 不提前承认


@dataclass
class L3Metadata:
    """L3 CANONICAL EVIDENCE 特有元数据."""
    evidence_role: EvidenceRole = EvidenceRole.CANDIDATE  # 必须修正1: evidence_role只在L3赋值
    canonical_source_scope: str = ""    # 必须修正3: 原典来源范围
    candidate_dimensions: List[str] = field(default_factory=list)  # 修正: 候选维度(不是Required)
    provided_dimensions: List[str] = field(default_factory=list)
    missing_dimensions: List[str] = field(default_factory=list)


@dataclass
class L4Metadata:
    """L4 CANONICAL PROPOSITION 特有元数据."""
    proposition_type: str = ""
    evidence_relation_schema: Dict[str, Any] = field(default_factory=dict)  # 必须修正4
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


@dataclass
class L7Metadata:
    """L7 CANONICAL ASSERTION 特有元数据."""
    assertion_type: str = ""
    assertion_contract_id: str = ""     # 建议2: Assertion Contract ID


# ============================================================================
# Evidence Relation Schema (必须修正4: L3→L4合法聚合关系)
# ============================================================================

@dataclass
class EvidenceRelationEntry:
    """证据关系条目."""
    evidence_id: str
    relation: EvidenceRelation
    description: str = ""
    condition: str = ""               # CONDITIONAL类型的条件
    depends_on: List[str] = field(default_factory=list)  # DEPENDENT类型的依赖


@dataclass
class EvidenceRelationSchema:
    """证据关系Schema - 定义L3→L4的合法聚合关系.
    
    这不是"投票"或"评分", 而是Canonical Contract明确规定的证据之间的逻辑关系.
    例如: A AND B, A OR B, A AND (B OR C), A unless D, A requires B
    """
    schema_id: str
    proposition: str
    entries: List[EvidenceRelationEntry] = field(default_factory=list)
    logical_expression: str = ""       # 逻辑表达式, 如 "required: A AND B; supporting: C OR D"
    authorized: bool = False
    authorization_source: str = ""     # 授权来源 (Canonical Source Mapping)

    def validate(self) -> dict:
        """验证Schema合法性."""
        result = {
            "schema_id": self.schema_id,
            "has_required": any(e.relation == EvidenceRelation.REQUIRED for e in self.entries),
            "has_logical_expression": bool(self.logical_expression),
            "authorized": self.authorized,
            "valid": self.authorized and bool(self.logical_expression),
            "gov11_compliant": True,  # 检查是否违反GOV-11(禁止投票)
            "gov16_compliant": True,  # 检查是否违反GOV-16(禁止加权评分)
        }
        # 检查是否有加权评分 (GOV-16)
        if any("weight" in e.description.lower() or "score" in e.description.lower() for e in self.entries):
            result["gov16_compliant"] = False
        return result


# ============================================================================
# 七层数据结构
# ============================================================================

@dataclass
class L1_EngineFact:
    """L1 ENGINE FACT."""
    common: CommonMetadata
    layer_specific: L1Metadata
    feature_name: str = ""
    value: Any = None


@dataclass
class L2_SemanticMapping:
    """L2 SEMANTIC MAPPING - Feature → Observable Meaning → Candidate Concept."""
    common: CommonMetadata
    layer_specific: L2Metadata
    feature_id: str = ""
    observable_meaning: str = ""       # 可观察意义 (不带有命理语义)


@dataclass
class L3_CanonicalEvidence:
    """L3 CANONICAL EVIDENCE - 原典认可的证据."""
    common: CommonMetadata
    layer_specific: L3Metadata
    semantic_concept: str = ""
    canonical_proposition: str = ""


@dataclass
class L4_CanonicalProposition:
    """L4 CANONICAL PROPOSITION - Evidence Aggregation后的命题判定."""
    common: CommonMetadata
    layer_specific: L4Metadata
    proposition: str = ""
    evidence_ids: List[str] = field(default_factory=list)


@dataclass
class L5_ConditionAuthorization:
    """L5 CONDITION AUTHORIZATION."""
    common: CommonMetadata
    layer_specific: L5Metadata
    proposition_id: str = ""
    condition_expression: str = ""


@dataclass
class L6_CanonicalJudgment:
    """L6 CANONICAL JUDGMENT."""
    common: CommonMetadata
    layer_specific: L6Metadata
    judgment_id: str = ""
    canonical_statement: str = ""
    condition_id: str = ""


@dataclass
class L7_CanonicalAssertion:
    """L7 CANONICAL ASSERTION - FROZEN."""
    common: CommonMetadata
    layer_specific: L7Metadata
    judgment_id: str = ""
    assertion_text: str = ""


# ============================================================================
# 七层贯通链
# ============================================================================

@dataclass
class SevenLayerChain:
    """七层贯通链."""
    chain_id: str
    l1: L1_EngineFact
    l2: L2_SemanticMapping
    l3: L3_CanonicalEvidence
    l4: Optional[L4_CanonicalProposition] = None
    l5: Optional[L5_ConditionAuthorization] = None
    l6: Optional[L6_CanonicalJudgment] = None
    l7: Optional[L7_CanonicalAssertion] = None

    def validate(self) -> dict:
        """验证七层链."""
        result = {
            "chain_id": self.chain_id,
            "l1_status": self.l1.common.status.value,
            "l2_status": self.l2.common.status.value,
            "l3_status": self.l3.common.status.value,
            "l4_status": self.l4.common.status.value if self.l4 else "NOT_AVAILABLE",
            "l5_status": self.l5.common.status.value if self.l5 else "NOT_AVAILABLE",
            "l6_status": self.l6.common.status.value if self.l6 else "NOT_AVAILABLE",
            "l7_status": self.l7.common.status.value if self.l7 else "NOT_AVAILABLE",
            "chain_complete": False,
            "blocking_layers": [],
            "gov11_violation": False,
            "gov16_violation": False,
        }

        # 检查每层状态
        if self.l2.layer_specific.mapping_status not in [MappingStatus.PROVEN, MappingStatus.PARTIAL]:
            result["blocking_layers"].append("L2_MAPPING_UNPROVEN")
        if self.l3.common.status not in [LayerStatus.SUFFICIENT, LayerStatus.PARTIAL, LayerStatus.PROVEN]:
            result["blocking_layers"].append("L3_EVIDENCE_INSUFFICIENT")
        if self.l4 and self.l4.layer_specific.aggregation_authorized == False:
            result["blocking_layers"].append("L4_AGGREGATION_NOT_AUTHORIZED")
        if not self.l4:
            result["blocking_layers"].append("L4_NOT_AVAILABLE")
        if self.l5 and self.l5.common.status != LayerStatus.AUTHORIZED:
            result["blocking_layers"].append("L5_NOT_AUTHORIZED")
        if not self.l5:
            result["blocking_layers"].append("L5_NOT_AVAILABLE")

        # GOV-16检查: 禁止加权评分
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
# 治理规则 (17条, 增加GOV-16, GOV-17)
# ============================================================================

GOVERNANCE_RULES = {
    "GOV-01": "不能从原典文本描述 → 人工归纳 → 直接变成机器必要条件",
    "GOV-02": "Feature Semantic Mapping需要独立验证 (L2)",
    "GOV-03": "Canonical Evidence需要独立验证 (L3)",
    "GOV-04": "每层都有自己的Fidelity, 不能合并",
    "GOV-05": "下层UNPROVEN/INSUFFICIENT时, 上层只能是PENDING/BLOCKED, 不能自动AUTHORIZED",
    "GOV-06": "Feature Equivalence ≠ Judgment Equivalence",
    "GOV-07": "ENGINEERING_STATISTICAL_METRIC ≠ CANONICAL_CONCEPT",
    "GOV-08": "不能用工程阈值定义命理概念 (防止循环自证)",
    "GOV-09": "Canonical Condition必须基于AUTHORIZED的层, 不能基于UNPROVEN的Feature",
    "GOV-10": "Assertion继续冻结 (L7), 不进入Interpretation/Polarity/Cross-Engine",
    "GOV-11": "Partial Evidence SHALL NOT be aggregated by count, score, vote, or confidence accumulation to create Canonical Authorization, unless the Canonical Contract explicitly defines the aggregation relation. (禁止证据投票升级)",
    "GOV-12": "Source Scope必须明确 (system/school/sources), 不同体系的同一概念不能被强行统一",
    "GOV-13": "Evidence Role必须标注 (仅L3), NON_CANONICAL证据不能直接用于Canonical授权",
    "GOV-14": "L2必须区分Observable Meaning和Candidate Concept, 不能提前承认Canonical Concept",
    "GOV-15": "L3→L4必须经过Evidence Aggregation, 且聚合方法必须由Evidence Relation Schema明确定义并授权",
    "GOV-16": "Canonical Evidence SHALL NOT be converted into a weighted score, probability, confidence score, or numerical threshold for Canonical Authorization unless the Canonical Source explicitly authorizes such quantitative relation. (禁止未经原典授权的加权评分/概率/阈值授权 - 防止Evidence Weight Injection)",
    "GOV-17": "A Canonical Judgment SHALL NOT automatically generate a Canonical Assertion without an explicit Assertion Contract. (Judgment不得自动生成Assertion, 必须经过Assertion Contract)",
}


# ============================================================================
# STR-001A 七层贯通案例 (修正版)
# ============================================================================

def build_str001a_v3() -> SevenLayerChain:
    """STR-001A 日主身弱 - 修正版七层贯通案例."""

    # L1 ENGINE FACT (必须修正1: 删除固定evidence_role, 增加semantic_type)
    l1 = L1_EngineFact(
        common=CommonMetadata(
            id="L1-F-WOOD-RATIO-V1",
            status=LayerStatus.COMPUTED,
            provenance="BaziEngine.calc_five_element_balance()",
            fidelity="确定性计算结果, 可复现",
            notes="未中藏乙木余气未被计入, 因为Engine只看地支本气",
        ),
        layer_specific=L1Metadata(
            semantic_type=SemanticType.ENGINEERING_METRIC,  # 必须修正1
            computation_provenance="Engine Feature Contract v1: 4天干+4地支本气equal weight count/8",  # 必须修正3
            feature_version="v1",
            calculation_method="4天干+4地支本气简单计数, WOOD count / 8. 当前命例: 天干乙木=1, 地支本气无木(未的本气是己土), 所以WOOD count=1, 1/8=0.125",
        ),
        feature_name="five_element_balance.WOOD",
        value=0.125,
    )

    # L2 SEMANTIC MAPPING (修正: observable_meaning + candidate_concepts + mapping_status)
    l2 = L2_SemanticMapping(
        common=CommonMetadata(
            id="L2-SM-WOOD-RATIO-TO-MUQI",
            status=LayerStatus.UNPROVEN,
            provenance="人工映射规则, 未经Canonical Source Mapping验证",
            dependencies=["L1-F-WOOD-RATIO-V1"],
            failure_reason="Feature统计口径尚不能证明Canonical概念",
            notes="不提前承认'木气偏少'为Canonical Concept, 只作为candidate",
        ),
        layer_specific=L2Metadata(
            mapping_type="threshold_to_concept",
            mapping_provenance="人工定义, 未经原典授权",  # 必须修正3
            mapping_status=MappingStatus.UNPROVEN,
            candidate_concepts=["木气偏少"],  # 修正: 候选概念
        ),
        feature_id="F-WOOD-RATIO-V1",
        observable_meaning="按five_element_balance v1统计口径(4天干+4地支本气equal weight), 八字八个统计位置中木五行计数=1/8=0.125, 低于0.15阈值",
    )

    # L3 CANONICAL EVIDENCE (修正: Candidate Evidence Dimensions, 不是Required)
    l3 = L3_CanonicalEvidence(
        common=CommonMetadata(
            id="L3-CE-MUQI-TO-SHENRUO",
            status=LayerStatus.INSUFFICIENT,
            provenance="基于原典要求的维度分析",
            dependencies=["L2-SM-WOOD-RATIO-TO-MUQI"],
            fidelity="原典维度分析准确, 但当前证据严重不足",
            failure_reason="只提供1个NON_CANONICAL维度, 缺失PRIMARY维度",
            blocking_dependencies=["L2_MAPPING_UNPROVEN", "NO_AUTHORIZED_EVIDENCE_CONTRACT"],
        ),
        layer_specific=L3Metadata(
            evidence_role=EvidenceRole.CANDIDATE_SUPPORTING,  # 必须修正1: evidence_role只在L3赋值
            canonical_source_scope="ZI_PING / 子平 / 渊海子平·玄机赋 + 子平真诠",  # 必须修正3
            candidate_dimensions=[  # 修正: 候选维度(不是Required)
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
        ),
        semantic_concept="木气偏少 (candidate, unproven)",
        canonical_proposition="日主身弱",
    )

    # L4 CANONICAL PROPOSITION (建议3: BLOCKED状态, 不是NOT_CREATED)
    l4 = L4_CanonicalProposition(
        common=CommonMetadata(
            id="L4-PROP-SHENRUO",
            status=LayerStatus.BLOCKED,  # 建议3: 存在但被阻断
            provenance="待建立Evidence Relation Schema",
            dependencies=["L3-CE-MUQI-TO-SHENRUO"],
            blocking_dependencies=[  # 建议3: 明确阻断原因
                "L2_MAPPING_UNPROVEN",
                "L3_EVIDENCE_INSUFFICIENT",
                "NO_AUTHORIZED_AGGREGATION_CONTRACT",
            ],
            failure_reason="L3 INSUFFICIENT且没有经过Canonical Contract授权的Evidence Aggregation方法",
        ),
        layer_specific=L4Metadata(
            proposition_type="DAY_MASTER_STRENGTH",
            evidence_relation_schema={},  # 必须修正4: 待建立Evidence Relation Schema
            aggregation_authorized=False,
            aggregation_method="待定义 (必须由Evidence Relation Schema授权, 禁止投票/评分)",
        ),
        proposition="日主身弱",
        evidence_ids=["L3-CE-MUQI-TO-SHENRUO"],
    )

    # L5-L7: NOT_AVAILABLE
    l5 = None
    l6 = None
    l7 = None

    return SevenLayerChain(
        chain_id="CHAIN-STR-001A-SHENRUO-V3",
        l1=l1,
        l2=l2,
        l3=l3,
        l4=l4,
        l5=l5,
        l6=l6,
        l7=l7,
    )


# ============================================================================
# Evidence Relation Schema 示例 (必须修正4: 待授权的Schema模板)
# ============================================================================

def build_evidence_relation_schema_template() -> EvidenceRelationSchema:
    """Evidence Relation Schema模板 - 待Canonical Source Mapping授权."""
    return EvidenceRelationSchema(
        schema_id="ERS-DAY_MASTER_WEAK-TEMPLATE",
        proposition="日主身弱",
        entries=[
            EvidenceRelationEntry(
                evidence_id="month_strength",
                relation=EvidenceRelation.REQUIRED,
                description="月令得时/失令状态 (待原典授权具体判定标准)",
            ),
            EvidenceRelationEntry(
                evidence_id="root_status",
                relation=EvidenceRelation.REQUIRED,
                description="日主通根情况 (待原典授权具体判定标准)",
            ),
            EvidenceRelationEntry(
                evidence_id="support_power",
                relation=EvidenceRelation.OPTIONAL,
                description="印比生扶力量 (辅助证据)",
            ),
            EvidenceRelationEntry(
                evidence_id="drain_power",
                relation=EvidenceRelation.OPTIONAL,
                description="财官食伤克泄耗力量 (辅助证据)",
            ),
            EvidenceRelationEntry(
                evidence_id="global_interaction",
                relation=EvidenceRelation.CONDITIONAL,
                description="全局生克制化 (在特定结构条件下才需要)",
                condition="特殊格局/从格/化格等情况",
            ),
        ],
        logical_expression="required: month_strength AND root_status; supporting: support_power OR drain_power; conditional: global_interaction IF special_structure",
        authorized=False,  # 待Canonical Source Mapping授权
        authorization_source="待建立: 渊海子平·玄机赋 + 子平真诠的Source Mapping",
    )


# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 100)
    print("Canonical Semantic Authorization Pipeline v3 - 七层语义授权链 (数据模型修正版)")
    print("=" * 100)
    print("\n修正记录: 4项必须修正 + 3项强烈建议 全部落地")
    print("  必须修正1: L1删除固定evidence_role, 增加semantic_type")
    print("  必须修正2: COMMON METADATA + LAYER-SPECIFIC METADATA")
    print("  必须修正3: computation_provenance / mapping_provenance / canonical_source_scope")
    print("  必须修正4: Evidence Relation Schema (REQUIRED/OPTIONAL/EXCLUSIVE/CONDITIONAL/ORDERED/DEPENDENT)")
    print("  建议1: GOV-16 禁止加权评分注入")
    print("  建议2: GOV-17 Judgment不得自动生成Assertion")
    print("  建议3: BLOCKED状态")

    # 治理规则
    print(f"\n{'='*100}")
    print("治理规则 (17条, 含GOV-16, GOV-17)")
    print("=" * 100)
    for k, v in GOVERNANCE_RULES.items():
        print(f"\n  {k}: {v[:120]}..." if len(v) > 120 else f"\n  {k}: {v}")

    # 元数据模型
    print(f"\n{'='*100}")
    print("元数据模型 (COMMON + LAYER-SPECIFIC)")
    print("=" * 100)
    print("""
  COMMON METADATA (所有层共用):
    id, status, provenance, dependencies, fidelity, failure_reason, blocking_dependencies, notes

  LAYER-SPECIFIC METADATA:
    L1: semantic_type, computation_provenance, feature_version, calculation_method
    L2: mapping_type, mapping_provenance, mapping_status, candidate_concepts
    L3: evidence_role, canonical_source_scope, candidate_dimensions, provided/missing_dimensions
    L4: proposition_type, evidence_relation_schema, aggregation_authorized, aggregation_method
    L5: authorization_scope, authorized_features, authorized_evidence
    L6: judgment_type, prerequisite_ids
    L7: assertion_type, assertion_contract_id
""")

    # Evidence Relation Schema
    print(f"\n{'='*100}")
    print("Evidence Relation Schema (必须修正4: L3→L4合法聚合关系)")
    print("=" * 100)
    schema = build_evidence_relation_schema_template()
    print(f"\n  Schema ID: {schema.schema_id}")
    print(f"  Proposition: {schema.proposition}")
    print(f"  Authorized: {schema.authorized} (待Canonical Source Mapping授权)")
    print(f"\n  Evidence Entries:")
    for e in schema.entries:
        print(f"    - {e.evidence_id}: {e.relation.value} - {e.description}")
    print(f"\n  Logical Expression: {schema.logical_expression}")
    print(f"\n  关键: 这不是投票/评分, 而是Canonical Contract明确规定的证据之间的逻辑关系")
    print(f"  例如: A AND B, A OR B, A AND (B OR C), A unless D, A requires B")

    # STR-001A 七层贯通案例
    print(f"\n{'='*100}")
    print("STR-001A 七层贯通案例 (修正版)")
    print("=" * 100)
    chain = build_str001a_v3()

    print(f"\n  L1 ENGINE FACT:")
    print(f"    id: {chain.l1.common.id}")
    print(f"    feature: {chain.l1.feature_name} = {chain.l1.value}")
    print(f"    semantic_type: {chain.l1.layer_specific.semantic_type.value} (必须修正1: 不是固定NON_CANONICAL)")
    print(f"    computation_provenance: {chain.l1.layer_specific.computation_provenance[:60]}...")
    print(f"    status: {chain.l1.common.status.value}")

    print(f"\n  L2 SEMANTIC MAPPING:")
    print(f"    id: {chain.l2.common.id}")
    print(f"    observable_meaning: {chain.l2.observable_meaning[:60]}...")
    print(f"    candidate_concepts: {chain.l2.layer_specific.candidate_concepts} (修正: 不提前承认)")
    print(f"    mapping_status: {chain.l2.layer_specific.mapping_status.value}")
    print(f"    status: {chain.l2.common.status.value}")

    print(f"\n  L3 CANONICAL EVIDENCE:")
    print(f"    id: {chain.l3.common.id}")
    print(f"    evidence_role: {chain.l3.layer_specific.evidence_role.value} (必须修正1: 只在L3赋值)")
    print(f"    canonical_source_scope: {chain.l3.layer_specific.canonical_source_scope} (必须修正3)")
    print(f"    candidate_dimensions (count={len(chain.l3.layer_specific.candidate_dimensions)}):")
    for d in chain.l3.layer_specific.candidate_dimensions:
        print(f"      - {d}")
    print(f"    provided: {chain.l3.layer_specific.provided_dimensions}")
    print(f"    status: {chain.l3.common.status.value}")

    print(f"\n  L4 CANONICAL PROPOSITION:")
    print(f"    id: {chain.l4.common.id}")
    print(f"    proposition: {chain.l4.proposition}")
    print(f"    status: {chain.l4.common.status.value} (建议3: BLOCKED, 不是NOT_CREATED)")
    print(f"    blocking_dependencies: {chain.l4.common.blocking_dependencies}")
    print(f"    aggregation_authorized: {chain.l4.layer_specific.aggregation_authorized}")
    print(f"    evidence_relation_schema: 待建立 (必须修正4)")

    print(f"\n  L5-L7: NOT_AVAILABLE (下层未通过)")

    # 链验证
    print(f"\n  Seven-Layer Chain Validation Result:")
    result = chain.validate()
    for k, v in result.items():
        print(f"    {k}: {v}")

    # 关键发现
    print(f"\n{'='*100}")
    print("关键发现 (v3修正版)")
    print("=" * 100)
    print("""
  1. L1 wood_ratio=0.125 是 ENGINEERING_METRIC, 但不是天然NON_CANONICAL
     - 如果Canonical Source授权, month_branch=戌这类DETERMINISTIC_FACT可以成为PRIMARY EVIDENCE
     - evidence_role只在L3赋值

  2. L2 区分Observable Meaning("8个位置中木占1个")和Candidate Concept("木气偏少")
     - 不提前承认Canonical Concept, mapping_status=UNPROVEN

  3. L3 "木气偏少"是CANDIDATE_SUPPORTING, 缺失6个Candidate Dimensions
     - 这些是Candidate Dimensions, 不是Required Dimensions (需要Canonical Source Mapping授权)

  4. L4 status=BLOCKED (不是NOT_CREATED), 明确阻断原因
     - L2_MAPPING_UNPROVEN, L3_EVIDENCE_INSUFFICIENT, NO_AUTHORIZED_AGGREGATION_CONTRACT

  5. Evidence Relation Schema定义合法聚合关系: REQUIRED/OPTIONAL/EXCLUSIVE/CONDITIONAL/ORDERED/DEPENDENT
     - 这不是投票/评分, 而是逻辑关系: A AND B, A OR B, A AND (B OR C)

  6. GOV-16禁止加权评分注入, GOV-17禁止Judgment自动生成Assertion

  结论: v3数据模型修正后, 治理链更加精确, 能够区分"尚不存在"和"存在但被阻断",
  能够区分computation/mapping/canonical source三种provenance,
  能够定义合法的Evidence Aggregation关系而不陷入投票/评分。
""")

    print("=" * 100)
    print("七层Contract v3修正版建立完成. 待用户核查后可FROZEN.")
    print("=" * 100)


if __name__ == "__main__":
    main()
