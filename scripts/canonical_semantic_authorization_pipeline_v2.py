"""Canonical Semantic Authorization Pipeline - 七层语义授权链 (修正版).

修正记录 (根据用户审计6个结构性问题):
  1. 命名修正: 不是"三层架构", 而是七层语义授权链 (L1-L7)
  2. L2区分: Feature → Observable Meaning → Canonical Concept (不能直接Feature→命理词语)
  3. L3→L4拆开: Canonical Evidence → Evidence Aggregation → Canonical Proposition
  4. 增加Evidence Role: PRIMARY/SUPPORTING/CONTEXTUAL/EXCLUSION/NON_CANONICAL
  5. GOV-11: Partial Evidence SHALL NOT be aggregated by count/score/vote/confidence
  6. 增加Source Scope: system/school/sources (防止不同体系被强行统一)
  7. 每层元数据: status/source_scope/provenance/evidence_role/fidelity/dependencies/failure_reason

七层架构:
  L1 ENGINE FACT          - 确定性计算事实
  L2 SEMANTIC MAPPING     - Feature → Observable Meaning → Canonical Concept
  L3 CANONICAL EVIDENCE   - 原典认可的证据 (带evidence_role)
  L4 CANONICAL PROPOSITION- 例如: 日主身弱 (Evidence Aggregation后的命题判定)
  L5 CONDITION AUTHORIZATION - 经过授权的条件
  L6 CANONICAL JUDGMENT   - 格局/身弱/调候……
  L7 CANONICAL ASSERTION  - 正式断言 (FROZEN)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum


# ============================================================================
# 状态枚举
# ============================================================================

class LayerStatus(str, Enum):
    """每层状态."""
    COMPUTED = "COMPUTED"              # L1: 确定性计算结果
    OBSERVED = "OBSERVED"              # L2a: 可观察意义
    MAPPED = "MAPPED"                  # L2b: 语义映射完成
    PROVEN = "PROVEN"                  # 已证明
    PARTIAL = "PARTIAL"                # 部分相关/部分证明
    UNPROVEN = "UNPROVEN"              # 未验证
    REJECTED = "REJECTED"              # 已拒绝
    SUFFICIENT = "SUFFICIENT"          # L3: 证据充分
    INSUFFICIENT = "INSUFFICIENT"      # L3: 证据不足
    AUTHORIZED = "AUTHORIZED"          # L5: 已授权
    PENDING = "PENDING"                # 待处理
    FROZEN = "FROZEN"                  # L7: 冻结


class EvidenceRole(str, Enum):
    """证据角色 (修正4)."""
    PRIMARY = "PRIMARY"                # 主要证据 (必要条件)
    SUPPORTING = "SUPPORTING"          # 辅助证据 (增强但非必要)
    CONTEXTUAL = "CONTEXTUAL"          # 情境证据 (特定条件下相关)
    EXCLUSION = "EXCLUSION"            # 排除证据 (证明某命题不成立)
    NON_CANONICAL = "NON_CANONICAL"    # 非原典证据 (工程指标, 不能直接用于Canonical授权)


class SourceScope:
    """来源范围 (修正6): 防止不同体系被强行统一."""
    def __init__(self, system: str, school: str, sources: List[str]):
        self.system = system          # 如 ZI_PING / BLIND_SCHOOL / ZI_WEI / HE_LUO / I_CHING
        self.school = school          # 如 子平真诠 / 滴天髓 / 穷通宝鉴 / 渊海子平 / 三命通会
        self.sources = sources        # 具体原典来源列表

    def __repr__(self):
        return f"SourceScope(system={self.system}, school={self.school}, sources={self.sources})"


@dataclass
class LayerMetadata:
    """每层元数据 (修正7): status/source_scope/provenance/evidence_role/fidelity/dependencies/failure_reason."""
    status: LayerStatus
    source_scope: Optional[SourceScope] = None
    provenance: str = ""               # 溯源信息
    evidence_role: Optional[EvidenceRole] = None  # 证据角色
    fidelity: str = ""                 # 保真度描述
    dependencies: List[str] = field(default_factory=list)  # 依赖的下层ID
    failure_reason: str = ""           # 失败原因
    notes: str = ""                    # 备注


# ============================================================================
# 七层数据结构
# ============================================================================

@dataclass
class L1_EngineFact:
    """L1 ENGINE FACT - 确定性计算事实."""
    layer_id: str
    feature_id: str
    feature_name: str
    version: str
    value: object
    calculation_method: str
    semantic_type: str = "ENGINEERING_METRIC"  # ENGINEERING_METRIC / CANONICAL_FACT
    metadata: LayerMetadata = field(default_factory=lambda: LayerMetadata(status=LayerStatus.COMPUTED))


@dataclass
class L2_SemanticMapping:
    """L2 SEMANTIC MAPPING - Feature → Observable Meaning → Canonical Concept (修正2)."""
    layer_id: str
    feature_id: str                    # 关联L1
    observable_meaning: str            # 可观察意义 (如 "按v1统计口径, 八字八个位置中木五行计数=1/8")
    canonical_concept: str             # 原典概念 (如 "木气偏少")
    mapping_rule: str                  # 映射规则
    gap_analysis: str = ""             # Gap分析
    metadata: LayerMetadata = field(default_factory=lambda: LayerMetadata(status=LayerStatus.UNPROVEN))


@dataclass
class L3_CanonicalEvidence:
    """L3 CANONICAL EVIDENCE - 原典认可的证据 (带evidence_role, 修正4)."""
    layer_id: str
    semantic_concept: str              # 关联L2的canonical_concept
    canonical_proposition: str         # 目标Canonical命题 (如 "日主身弱")
    evidence_role: EvidenceRole        # 证据角色
    canonical_sources: List[str] = field(default_factory=list)  # 原典来源
    required_dimensions: List[str] = field(default_factory=list)  # 原典要求的维度
    provided_dimensions: List[str] = field(default_factory=list)  # 当前提供的维度
    missing_dimensions: List[str] = field(default_factory=list)   # 缺失的维度
    gap_analysis: str = ""
    metadata: LayerMetadata = field(default_factory=lambda: LayerMetadata(status=LayerStatus.UNPROVEN))


@dataclass
class L4_CanonicalProposition:
    """L4 CANONICAL PROPOSITION - Evidence Aggregation后的命题判定 (修正3).
    
    注意: Evidence和Proposition不是同一个层级.
    L3是多条证据, L4是经过Evidence Aggregation/Canonical Reasoning后的命题判定.
    """
    layer_id: str
    proposition: str                   # 命题 (如 "日主身弱")
    evidence_ids: List[str] = field(default_factory=list)  # 依赖的L3证据ID
    aggregation_method: str = ""       # 证据聚合方法 (必须由Canonical Contract明确定义)
    aggregation_authorized: bool = False  # 聚合是否经过Canonical Contract授权
    reasoning: str = ""                # 推理过程
    metadata: LayerMetadata = field(default_factory=lambda: LayerMetadata(status=LayerStatus.UNPROVEN))


@dataclass
class L5_ConditionAuthorization:
    """L5 CONDITION AUTHORIZATION - 经过授权的条件."""
    layer_id: str
    proposition_id: str                # 关联L4
    condition_expression: str          # 条件表达式 (必须基于AUTHORIZED的层)
    authorized_features: List[str] = field(default_factory=list)
    authorized_mappings: List[str] = field(default_factory=list)
    authorized_evidence: List[str] = field(default_factory=list)
    metadata: LayerMetadata = field(default_factory=lambda: LayerMetadata(status=LayerStatus.PENDING))


@dataclass
class L6_CanonicalJudgment:
    """L6 CANONICAL JUDGMENT - 格局/身弱/调候……"""
    layer_id: str
    judgment_id: str
    canonical_statement: str
    condition_id: str                  # 关联L5
    prerequisite_ids: List[str] = field(default_factory=list)  # 前提条件 (如STR-001B依赖STR-001A)
    metadata: LayerMetadata = field(default_factory=lambda: LayerMetadata(status=LayerStatus.PENDING))


@dataclass
class L7_CanonicalAssertion:
    """L7 CANONICAL ASSERTION - 正式断言 (FROZEN)."""
    layer_id: str
    judgment_id: str                   # 关联L6
    assertion_text: str
    metadata: LayerMetadata = field(default_factory=lambda: LayerMetadata(status=LayerStatus.FROZEN))


# ============================================================================
# 七层贯通链
# ============================================================================

@dataclass
class SevenLayerChain:
    """七层贯通链: L1→L2→L3→L4→L5→L6→L7."""
    chain_id: str
    l1: L1_EngineFact
    l2: L2_SemanticMapping
    l3: L3_CanonicalEvidence
    l4: Optional[L4_CanonicalProposition] = None
    l5: Optional[L5_ConditionAuthorization] = None
    l6: Optional[L6_CanonicalJudgment] = None
    l7: Optional[L7_CanonicalAssertion] = None

    def validate(self) -> dict:
        """验证七层链的完整性."""
        result = {
            "chain_id": self.chain_id,
            "l1_status": self.l1.metadata.status.value,
            "l2_status": self.l2.metadata.status.value,
            "l3_status": self.l3.metadata.status.value,
            "l4_status": self.l4.metadata.status.value if self.l4 else "NOT_CREATED",
            "l5_status": self.l5.metadata.status.value if self.l5 else "NOT_CREATED",
            "l6_status": self.l6.metadata.status.value if self.l6 else "NOT_CREATED",
            "l7_status": self.l7.metadata.status.value if self.l7 else "NOT_CREATED",
            "chain_complete": False,
            "blocking_layers": [],
            "gov11_violation": False,  # GOV-11检查
        }

        # 检查每层状态
        if self.l2.metadata.status not in [LayerStatus.MAPPED, LayerStatus.PROVEN, LayerStatus.PARTIAL]:
            result["blocking_layers"].append("L2_SEMANTIC_MAPPING")
        if self.l3.metadata.status not in [LayerStatus.SUFFICIENT, LayerStatus.PARTIAL, LayerStatus.PROVEN]:
            result["blocking_layers"].append("L3_CANONICAL_EVIDENCE")
        if self.l4 and self.l4.metadata.status not in [LayerStatus.PROVEN, LayerStatus.PARTIAL]:
            result["blocking_layers"].append("L4_CANONICAL_PROPOSITION")
        if not self.l4:
            result["blocking_layers"].append("L4_CANONICAL_PROPOSITION (NOT_CREATED)")
        if self.l5 and self.l5.metadata.status != LayerStatus.AUTHORIZED:
            result["blocking_layers"].append("L5_CONDITION_AUTHORIZATION")
        if not self.l5:
            result["blocking_layers"].append("L5_CONDITION_AUTHORIZATION (NOT_CREATED)")

        # GOV-11检查: 如果L4的aggregation_method是"count/vote/score"且未被Canonical Contract授权, 则违规
        if self.l4 and self.l4.aggregation_method in ["count", "vote", "score", "confidence_accumulation"]:
            if not self.l4.aggregation_authorized:
                result["gov11_violation"] = True
                result["blocking_layers"].append("GOV-11_EVIDENCE_VOTING_FORBIDDEN")

        result["chain_complete"] = len(result["blocking_layers"]) == 0
        return result


# ============================================================================
# 治理规则 (修正5: GOV-11)
# ============================================================================

GOVERNANCE_RULES = {
    "GOV-01": "不能从原典文本描述 → 人工归纳 → 直接变成机器必要条件",
    "GOV-02": "Feature Semantic Mapping需要独立验证 (L2)",
    "GOV-03": "Canonical Evidence需要独立验证 (L3)",
    "GOV-04": "每层都有自己的Fidelity, 不能合并",
    "GOV-05": "下层UNPROVEN/INSUFFICIENT时, 上层只能是PENDING, 不能自动AUTHORIZED",
    "GOV-06": "Feature Equivalence ≠ Judgment Equivalence",
    "GOV-07": "ENGINEERING_STATISTICAL_METRIC ≠ CANONICAL_CONCEPT",
    "GOV-08": "不能用工程阈值定义命理概念 (防止循环自证)",
    "GOV-09": "Canonical Condition必须基于AUTHORIZED的层, 不能基于UNPROVEN的Feature",
    "GOV-10": "Assertion继续冻结 (L7), 不进入Interpretation/Polarity/Cross-Engine",
    "GOV-11": "Partial Evidence SHALL NOT be aggregated by count, score, vote, or confidence accumulation to create Canonical Authorization, unless the Canonical Contract explicitly defines the aggregation relation. (禁止证据投票升级)",
    "GOV-12": "Source Scope必须明确 (system/school/sources), 不同体系的同一概念不能被强行统一",
    "GOV-13": "Evidence Role必须标注 (PRIMARY/SUPPORTING/CONTEXTUAL/EXCLUSION/NON_CANONICAL), NON_CANONICAL证据不能直接用于Canonical授权",
    "GOV-14": "L2必须区分Observable Meaning和Canonical Concept, 不能直接Feature→命理词语",
    "GOV-15": "L3→L4必须经过Evidence Aggregation, 且聚合方法必须由Canonical Contract明确定义并授权",
}


# ============================================================================
# STR-001A 第一个完整七层贯通案例
# ============================================================================

def build_str001a_seven_layer_chain() -> SevenLayerChain:
    """STR-001A 日主身弱 - 第一个完整七层贯通案例 (验证架构本身)."""

    source_scope = SourceScope(
        system="ZI_PING",
        school="子平",
        sources=["渊海子平·玄机赋", "子平真诠"],
    )

    # L1 ENGINE FACT
    l1 = L1_EngineFact(
        layer_id="L1-F-WOOD-RATIO-V1",
        feature_id="F-WOOD-RATIO-V1",
        feature_name="five_element_balance.WOOD",
        version="v1",
        value=0.125,
        calculation_method="4天干+4地支本气简单计数, WOOD count / 8. 当前命例: 天干乙木=1, 地支本气无木(未的本气是己土), 所以WOOD count=1, 1/8=0.125",
        semantic_type="ENGINEERING_METRIC",
        metadata=LayerMetadata(
            status=LayerStatus.COMPUTED,
            source_scope=source_scope,
            provenance="BaziEngine.calc_five_element_balance()",
            evidence_role=EvidenceRole.NON_CANONICAL,  # 工程指标, 不能直接用于Canonical授权
            fidelity="确定性计算结果, 可复现",
            notes="未中藏乙木余气未被计入, 因为Engine只看地支本气",
        ),
    )

    # L2 SEMANTIC MAPPING (修正2: 区分Observable Meaning和Canonical Concept)
    l2 = L2_SemanticMapping(
        layer_id="L2-SM-WOOD-RATIO-TO-MUQI",
        feature_id="F-WOOD-RATIO-V1",
        observable_meaning="按v1统计口径(4天干+4地支本气equal weight), 八字八个位置中木五行计数=1/8=0.125, 低于0.15阈值",
        canonical_concept="木气偏少",
        mapping_rule="wood_ratio < 0.15",
        gap_analysis=(
            "Observable Meaning只是工程统计事实: 8个位置中木占1个. "
            "但'木气偏少'在子平体系中带有命理力量语义, 需要考虑: "
            "藏干权重(未中藏乙木余气)、月令旺衰(乙木在戌月)、印星生扶(水0.5生木). "
            "因此wood_ratio<0.15不能直接等同于'木气偏少', 需要独立的Semantic Mapping验证."
        ),
        metadata=LayerMetadata(
            status=LayerStatus.UNPROVEN,
            source_scope=source_scope,
            provenance="人工映射规则, 未经Canonical Source Mapping验证",
            evidence_role=EvidenceRole.NON_CANONICAL,
            fidelity="Observable Meaning准确, 但到Canonical Concept的映射未验证",
            dependencies=["L1-F-WOOD-RATIO-V1"],
            failure_reason="缺少藏干/月令/印星生扶的考虑, 简单计数阈值不足以代表命理力量",
        ),
    )

    # L3 CANONICAL EVIDENCE (修正4: evidence_role)
    l3 = L3_CanonicalEvidence(
        layer_id="L3-CE-MUQI-TO-SHENRUO",
        semantic_concept="木气偏少",
        canonical_proposition="日主身弱",
        evidence_role=EvidenceRole.SUPPORTING,  # 只是辅助证据, 不是主要证据
        canonical_sources=[
            "《渊海子平·玄机赋》: '得时俱为旺论，失令便作衰看。'",
            "《渊海子平·玄机赋》: '四柱无根，得时为旺；日干无气，遇劫为强。'",
            "《渊海子平·玄机赋》: '身坐休囚，平生未济。'",
        ],
        required_dimensions=[
            "月令状态: 得时/失令 (PRIMARY_EVIDENCE)",
            "根气: 日主是否通根 (PRIMARY_EVIDENCE)",
            "生扶力量: 印比生扶 (SUPPORTING_EVIDENCE)",
            "克泄耗力量: 财官食伤克泄耗 (SUPPORTING_EVIDENCE)",
            "日主坐旺衰 (CONTEXTUAL_EVIDENCE)",
            "全局生克制化关系 (PRIMARY_EVIDENCE)",
        ],
        provided_dimensions=[
            "木元素简单计数占比 (wood_ratio=0.125) - NON_CANONICAL",
        ],
        missing_dimensions=[
            "月令状态 (得时/失令) - PRIMARY",
            "根气 (通根情况) - PRIMARY",
            "生扶力量 (印比) - SUPPORTING",
            "克泄耗力量 (财官食伤) - SUPPORTING",
            "日主坐旺衰 - CONTEXTUAL",
            "全局生克制化 - PRIMARY",
        ],
        gap_analysis=(
            "'木气偏少' (即使L2 Semantic Mapping被证明) 只是'日主身弱'所需的多个判定维度之一, "
            "且只能作为SUPPORTING_EVIDENCE, 不是PRIMARY_EVIDENCE. "
            "原典明确要求综合考虑: 月令得时/失令(PRIMARY)、根气(PRIMARY)、印比生扶(SUPPORTING)、"
            "财官食伤克泄耗(SUPPORTING)、日主坐旺衰(CONTEXTUAL)、全局生克制化(PRIMARY). "
            "当前只提供了'木元素简单计数占比'一个NON_CANONICAL维度, 缺失5个以上必要维度. "
            "因此'木气偏少'不足以成为'日主身弱'的充分证据."
        ),
        metadata=LayerMetadata(
            status=LayerStatus.INSUFFICIENT,
            source_scope=source_scope,
            provenance="基于原典要求的维度分析",
            evidence_role=EvidenceRole.SUPPORTING,
            fidelity="原典维度分析准确, 但当前证据严重不足",
            dependencies=["L2-SM-WOOD-RATIO-TO-MUQI"],
            failure_reason="只提供1个NON_CANONICAL维度, 缺失PRIMARY维度(月令/根气/全局生克)",
        ),
    )

    # L4 CANONICAL PROPOSITION (修正3: Evidence Aggregation)
    # 注意: 因为L3 INSUFFICIENT, 且没有经过Canonical Contract授权的聚合方法, L4不能创建
    l4 = None  # 不创建, 因为下层INSUFFICIENT且没有授权的聚合方法

    # L5-L7 都不创建
    l5 = None
    l6 = None
    l7 = None

    return SevenLayerChain(
        chain_id="CHAIN-STR-001A-SHENRUO-SEVEN-LAYER",
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
    print("Canonical Semantic Authorization Pipeline - 七层语义授权链 (修正版)")
    print("=" * 100)
    print("\n核心问题: Engine算出了一个数, 不代表这个数已经获得了原典概念的语义授权.")
    print("\n七层架构 (每层独立Fidelity, 下层未通过上层不能自动通过):")
    print("""
  L1 ENGINE FACT            - 确定性计算事实 (COMPUTED)
  L2 SEMANTIC MAPPING       - Feature → Observable Meaning → Canonical Concept
  L3 CANONICAL EVIDENCE     - 原典认可的证据 (带evidence_role: PRIMARY/SUPPORTING/CONTEXTUAL/EXCLUSION/NON_CANONICAL)
  L4 CANONICAL PROPOSITION  - Evidence Aggregation后的命题判定 (如: 日主身弱)
  L5 CONDITION AUTHORIZATION- 经过授权的条件 (AUTHORIZED)
  L6 CANONICAL JUDGMENT     - 格局/身弱/调候……
  L7 CANONICAL ASSERTION    - 正式断言 (FROZEN)
""")

    # 治理规则
    print(f"\n{'='*100}")
    print("治理规则 (15条, 含修正5 GOV-11禁止证据投票)")
    print("=" * 100)
    for k, v in GOVERNANCE_RULES.items():
        print(f"\n  {k}: {v}")

    # STR-001A 七层贯通案例
    print(f"\n{'='*100}")
    print("第一个完整七层贯通案例: STR-001A 日主身弱")
    print("=" * 100)
    chain = build_str001a_seven_layer_chain()

    print(f"\n  L1 ENGINE FACT:")
    print(f"    layer_id: {chain.l1.layer_id}")
    print(f"    feature: {chain.l1.feature_name} = {chain.l1.value}")
    print(f"    semantic_type: {chain.l1.semantic_type}")
    print(f"    status: {chain.l1.metadata.status.value}")
    print(f"    evidence_role: {chain.l1.metadata.evidence_role.value if chain.l1.metadata.evidence_role else 'N/A'}")
    print(f"    calculation: {chain.l1.calculation_method[:80]}...")

    print(f"\n  L2 SEMANTIC MAPPING:")
    print(f"    layer_id: {chain.l2.layer_id}")
    print(f"    observable_meaning: {chain.l2.observable_meaning[:80]}...")
    print(f"    canonical_concept: {chain.l2.canonical_concept}")
    print(f"    status: {chain.l2.metadata.status.value}")
    print(f"    evidence_role: {chain.l2.metadata.evidence_role.value if chain.l2.metadata.evidence_role else 'N/A'}")
    print(f"    gap: {chain.l2.gap_analysis[:80]}...")

    print(f"\n  L3 CANONICAL EVIDENCE:")
    print(f"    layer_id: {chain.l3.layer_id}")
    print(f"    semantic_concept: {chain.l3.semantic_concept}")
    print(f"    canonical_proposition: {chain.l3.canonical_proposition}")
    print(f"    evidence_role: {chain.l3.evidence_role.value}")
    print(f"    status: {chain.l3.metadata.status.value}")
    print(f"    provided_dimensions: {chain.l3.provided_dimensions}")
    print(f"    missing_dimensions (count={len(chain.l3.missing_dimensions)}):")
    for d in chain.l3.missing_dimensions:
        print(f"      - {d}")
    print(f"    gap: {chain.l3.gap_analysis[:80]}...")

    print(f"\n  L4 CANONICAL PROPOSITION: NOT CREATED")
    print(f"    原因: L3 INSUFFICIENT, 且没有经过Canonical Contract授权的Evidence Aggregation方法")
    print(f"    GOV-11检查: 禁止用证据数量/分数/投票累积创建Canonical Authorization")

    print(f"\n  L5-L7: NOT CREATED (下层未通过)")

    # 链验证
    print(f"\n  Seven-Layer Chain Validation Result:")
    result = chain.validate()
    for k, v in result.items():
        print(f"    {k}: {v}")

    # 关键发现
    print(f"\n{'='*100}")
    print("关键发现 (七层贯通案例验证)")
    print("=" * 100)
    print("""
  1. L1 wood_ratio=0.125 是 ENGINEERING_METRIC, evidence_role=NON_CANONICAL, 不能直接用于Canonical授权
  2. L2 必须区分 Observable Meaning("8个位置中木占1个")和 Canonical Concept("木气偏少"), 不能直接映射
  3. L3 "木气偏少"只能作为 SUPPORTING_EVIDENCE, 不是 PRIMARY_EVIDENCE; 缺失月令/根气/全局生克等PRIMARY维度
  4. L4 不能创建, 因为L3 INSUFFICIENT且没有授权的Evidence Aggregation方法
  5. GOV-11: 不能因为有多个PARTIAL证据就投票升级为Canonical Authorization
  6. Source Scope明确: ZI_PING / 子平 / 渊海子平·玄机赋+子平真诠
  7. 七层链在L3被阻断, L4-L7均未创建

  结论: 此架构能够准确识别semantic gap, 防止工程Feature冒充Canonical Concept.
  下一步: 基于此架构, 建立身弱的Canonical Source Mapping, 定义PRIMARY/SUPPORTING维度,
  然后才能建立经过授权的Evidence Aggregation方法.
""")

    print("=" * 100)
    print("七层Contract修正版建立完成. 待用户核查后可FROZEN.")
    print("=" * 100)


if __name__ == "__main__":
    main()
