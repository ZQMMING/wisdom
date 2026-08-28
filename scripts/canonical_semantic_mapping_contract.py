"""Canonical Semantic Mapping Contract - 正式架构框架.

核心问题: Engine算出了一个数, 不代表这个数已经获得了原典概念的语义授权.

三层架构 (每层独立Fidelity, 下层未通过上层不能自动通过):

  Layer 1: Engine Feature
    确定性计算结果, 如 wood_ratio=0.125
    状态: COMPUTED

  Layer 2: Feature Semantic Mapping
    回答: 这个Feature能否证明某个语义概念?
    如: wood_ratio<0.15 能否证明 "木气偏少"?
    状态: PROVEN / PARTIAL / UNPROVEN / REJECTED

  Layer 3: Canonical Evidence
    回答: 这个语义概念是否足以成为某个Canonical命题的证据?
    如: "木气偏少" 是否足以成为 "日主身弱" 的证据?
    状态: SUFFICIENT / PARTIAL / INSUFFICIENT / UNPROVEN

  Layer 4: Canonical Condition (经过授权的条件)
    状态: AUTHORIZED / PENDING / REJECTED

  Layer 5: Canonical Judgment
  Layer 6: Canonical Assertion (FROZEN)

治理规则:
  1. 不能从原典文本描述 → 人工归纳 → 直接变成机器必要条件
  2. Feature Semantic Mapping需要独立验证
  3. Canonical Evidence需要独立验证
  4. 每层都有自己的Fidelity, 不能合并
  5. 下层UNPROVEN时, 上层只能是PENDING, 不能自动AUTHORIZED
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


# ============================================================================
# 状态枚举
# ============================================================================

class FeatureStatus(str, Enum):
    COMPUTED = "COMPUTED"  # 确定性计算结果


class SemanticMappingStatus(str, Enum):
    PROVEN = "PROVEN"          # 已证明Feature可以代表该语义概念
    PARTIAL = "PARTIAL"        # 部分相关, 但不充分
    UNPROVEN = "UNPROVEN"      # 未验证
    REJECTED = "REJECTED"      # 已证明不能代表


class CanonicalEvidenceStatus(str, Enum):
    SUFFICIENT = "SUFFICIENT"      # 足以成为Canonical命题的证据
    PARTIAL = "PARTIAL"             # 部分证据, 但不充分
    INSUFFICIENT = "INSUFFICIENT"  # 不足以成为证据
    UNPROVEN = "UNPROVEN"           # 未验证


class CanonicalConditionStatus(str, Enum):
    AUTHORIZED = "AUTHORIZED"  # 经过语义授权的条件
    PENDING = "PENDING"        # 待授权
    REJECTED = "REJECTED"      # 被拒绝


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class EngineFeature:
    """Layer 1: Engine Feature - 确定性计算结果."""
    feature_id: str
    feature_name: str
    version: str
    value: object
    calculation_method: str  # 计算方法描述
    semantic_type: str = "ENGINEERING_METRIC"  # ENGINEERING_METRIC / CANONICAL_FACT
    status: FeatureStatus = FeatureStatus.COMPUTED
    evidence: str = ""  # 计算证据/溯源


@dataclass
class FeatureSemanticMapping:
    """Layer 2: Feature Semantic Mapping - Feature能否证明某个语义概念."""
    mapping_id: str
    feature_id: str  # 关联的Engine Feature
    semantic_concept: str  # 语义概念, 如 "木气偏少"
    mapping_rule: str  # 映射规则, 如 "wood_ratio < 0.15"
    canonical_basis: List[str] = field(default_factory=list)  # 原典依据
    validation_method: str = ""  # 验证方法
    gap_analysis: str = ""  # Gap分析
    status: SemanticMappingStatus = SemanticMappingStatus.UNPROVEN
    notes: str = ""


@dataclass
class CanonicalEvidence:
    """Layer 3: Canonical Evidence - 语义概念是否足以成为Canonical命题的证据."""
    evidence_id: str
    semantic_concept: str  # 语义概念, 如 "木气偏少"
    canonical_proposition: str  # Canonical命题, 如 "日主身弱"
    canonical_sources: List[str] = field(default_factory=list)  # 原典来源
    required_dimensions: List[str] = field(default_factory=list)  # 原典要求的判定维度
    provided_dimensions: List[str] = field(default_factory=list)  # 当前提供的维度
    missing_dimensions: List[str] = field(default_factory=list)  # 缺失的维度
    gap_analysis: str = ""
    status: CanonicalEvidenceStatus = CanonicalEvidenceStatus.UNPROVEN
    notes: str = ""


@dataclass
class CanonicalCondition:
    """Layer 4: Canonical Condition - 经过语义授权的条件."""
    condition_id: str
    canonical_proposition: str  # 如 "日主身弱"
    authorized_features: List[str] = field(default_factory=list)  # 经过授权的Feature列表
    authorized_mappings: List[str] = field(default_factory=list)  # 经过授权的Semantic Mapping
    authorized_evidence: List[str] = field(default_factory=list)  # 经过授权的Canonical Evidence
    condition_expression: str = ""  # 条件表达式 (必须基于AUTHORIZED的层)
    status: CanonicalConditionStatus = CanonicalConditionStatus.PENDING
    authorization_date: Optional[str] = None
    notes: str = ""


@dataclass
class SemanticMappingChain:
    """完整的语义映射链: Feature → Semantic Mapping → Canonical Evidence → Condition."""
    chain_id: str
    feature: EngineFeature
    semantic_mapping: FeatureSemanticMapping
    canonical_evidence: CanonicalEvidence
    canonical_condition: Optional[CanonicalCondition] = None

    def validate_chain(self) -> dict:
        """验证语义映射链的完整性."""
        result = {
            "chain_id": self.chain_id,
            "feature_status": self.feature.status.value,
            "semantic_mapping_status": self.semantic_mapping.status.value,
            "canonical_evidence_status": self.canonical_evidence.status.value,
            "canonical_condition_status": self.canonical_condition.status.value if self.canonical_condition else "NONE",
            "chain_valid": False,
            "blocking_layers": [],
        }

        # 检查每层状态
        if self.semantic_mapping.status not in [SemanticMappingStatus.PROVEN, SemanticMappingStatus.PARTIAL]:
            result["blocking_layers"].append("semantic_mapping")
        if self.canonical_evidence.status not in [CanonicalEvidenceStatus.SUFFICIENT, CanonicalEvidenceStatus.PARTIAL]:
            result["blocking_layers"].append("canonical_evidence")
        if self.canonical_condition and self.canonical_condition.status != CanonicalConditionStatus.AUTHORIZED:
            result["blocking_layers"].append("canonical_condition")
        if not self.canonical_condition:
            result["blocking_layers"].append("canonical_condition (not created)")

        result["chain_valid"] = len(result["blocking_layers"]) == 0
        return result


# ============================================================================
# STR-001 实例: 用Contract框架验证
# ============================================================================

def build_str001_chain() -> SemanticMappingChain:
    """STR-001实例: wood_ratio → 木气偏少 → 日主身弱."""

    # Layer 1: Engine Feature
    feature = EngineFeature(
        feature_id="F-WOOD-RATIO-V1",
        feature_name="five_element_balance.WOOD",
        version="v1",
        value=0.125,
        calculation_method="4天干+4地支本气简单计数, WOOD count / 8",
        semantic_type="ENGINEERING_METRIC",
        status=FeatureStatus.COMPUTED,
        evidence="癸亥 壬戌 乙未 壬午: 天干乙木=1, 地支未中乙木本气? NO - 未的本气是己土. 所以WOOD count=1 (仅天干乙木), 1/8=0.125",
    )

    # Layer 2: Feature Semantic Mapping
    semantic_mapping = FeatureSemanticMapping(
        mapping_id="SM-WOOD-RATIO-TO-MUQIAPIANSHAO",
        feature_id="F-WOOD-RATIO-V1",
        semantic_concept="木气偏少",
        mapping_rule="wood_ratio < 0.15",
        canonical_basis=[
            "需要验证: 8个位置简单计数中木占比低, 是否等于子平体系中的'木气偏少'?",
            "注意: 未中藏乙木(余气)未被计入, 因为Engine只看地支本气",
            "注意: 印星(水)生扶力量未被纳入'木气'的判定",
        ],
        validation_method="需要独立验证: 简单计数占比 < 阈值 是否足以代表'木气偏少'这个语义概念",
        gap_analysis=(
            "wood_ratio=0.125只证明: 在8个位置(4天干+4地支本气)的简单计数中, 木占1/8. "
            "但'木气偏少'在子平体系中可能需要考虑: 藏干权重、月令旺衰、印星生扶、根气等. "
            "特别是未中藏乙木余气未被计入, 印星(水0.5)生扶力量未被纳入."
        ),
        status=SemanticMappingStatus.UNPROVEN,
        notes="不能因为wood_ratio<0.15就自动认定'木气偏少', 需要独立的Semantic Mapping验证",
    )

    # Layer 3: Canonical Evidence
    canonical_evidence = CanonicalEvidence(
        evidence_id="CE-MUQIAPIANSHAO-TO-SHENRUO",
        semantic_concept="木气偏少",
        canonical_proposition="日主身弱",
        canonical_sources=[
            "《渊海子平·玄机赋》: '得时俱为旺论，失令便作衰看。'",
            "《渊海子平·玄机赋》: '四柱无根，得时为旺；日干无气，遇劫为强。'",
            "《渊海子平·玄机赋》: '身坐休囚，平生未济。'",
        ],
        required_dimensions=[
            "月令状态: 得时/失令 (乙木在戌月的月令状态)",
            "根气: 日主是否通根 (未中藏乙木余气)",
            "生扶力量: 印比生扶 (壬水透干×2, 亥水在年支, WATER=0.5)",
            "克泄耗力量: 财官食伤克泄耗 (戊土正财当令, 午火食神)",
            "日主坐旺衰: 乙木坐未土",
            "全局生克制化关系",
        ],
        provided_dimensions=[
            "木元素简单计数占比 (wood_ratio=0.125)",
        ],
        missing_dimensions=[
            "月令状态 (得时/失令)",
            "根气 (通根情况)",
            "生扶力量 (印比)",
            "克泄耗力量 (财官食伤)",
            "日主坐旺衰",
            "全局生克制化",
        ],
        gap_analysis=(
            "'木气偏少' (即使Semantic Mapping被证明) 只是'日主身弱'所需的多个判定维度之一. "
            "原典明确要求综合考虑: 月令得时/失令、根气、印比生扶、财官食伤克泄耗、日主坐旺衰、全局生克制化. "
            "当前只提供了'木元素简单计数占比'一个维度, 缺失5个以上必要维度. "
            "因此'木气偏少'不足以成为'日主身弱'的充分证据."
        ),
        status=CanonicalEvidenceStatus.INSUFFICIENT,
        notes="即使'木气偏少'被证明, 也不足以单独证明'日主身弱', 需要多维度综合判定",
    )

    # Layer 4: Canonical Condition (尚未创建, 因为下层未通过)
    canonical_condition = None  # 不创建, 因为下层UNPROVEN/INSUFFICIENT

    return SemanticMappingChain(
        chain_id="CHAIN-STR-001-SHENRUO",
        feature=feature,
        semantic_mapping=semantic_mapping,
        canonical_evidence=canonical_evidence,
        canonical_condition=canonical_condition,
    )


def build_str001b_chain() -> SemanticMappingChain:
    """STR-001B实例: 身弱 → 喜印比生扶 (前提是身弱已被证明)."""

    # Layer 1: Engine Feature (身弱判定 - 目前没有经过授权的Feature)
    feature = EngineFeature(
        feature_id="F-SHENRUO-PENDING",
        feature_name="day_master_strength",
        version="pending",
        value=None,
        calculation_method="待建立: 需要经过Canonical授权的身弱判定方法",
        semantic_type="PENDING_CANONICAL",
        status=FeatureStatus.COMPUTED,
        evidence="身弱判定方法尚未建立, 当前只有wood_ratio<0.15的工程指标, 不足以证明身弱",
    )

    # Layer 2: Feature Semantic Mapping
    semantic_mapping = FeatureSemanticMapping(
        mapping_id="SM-SHENRUO-TO-SHENRUO",
        feature_id="F-SHENRUO-PENDING",
        semantic_concept="日主身弱",
        mapping_rule="待建立: 需要经过Canonical授权的身弱判定规则",
        canonical_basis=[
            "《渊海子平·玄机赋》: '得时俱为旺论，失令便作衰看。'",
            "《渊海子平·玄机赋》: '四柱无根，得时为旺；日干无气，遇劫为强。'",
        ],
        validation_method="需要建立多维度身弱判定方法, 并通过Canonical Source Mapping验证",
        gap_analysis="身弱判定方法尚未建立, 当前没有经过授权的Feature可以证明'日主身弱'",
        status=SemanticMappingStatus.UNPROVEN,
        notes="STR-001B的前提是STR-001A(身弱)已被证明, 当前前提不成立",
    )

    # Layer 3: Canonical Evidence
    canonical_evidence = CanonicalEvidence(
        evidence_id="CE-SHENRUO-TO-XIYINBI",
        semantic_concept="日主身弱",
        canonical_proposition="身弱喜印比生扶",
        canonical_sources=[
            "《渊海子平·玄机赋》: '身弱喜印，主旺宜官。'",
            "《渊海子平·玄机赋》: '日干无气，遇劫为强。'",
            "《渊海子平·玄机赋》: '身衰则喜扶喜助。'",
        ],
        required_dimensions=[
            "身弱已被证明 (前提条件)",
            "印星是否可用 (是否受制/是否过多)",
            "比劫是否可用 (是否夺财/是否有根)",
            "具体命局的印比可用性判定",
        ],
        provided_dimensions=[
            "原典依据: '身弱喜印'有明确原文支持",
        ],
        missing_dimensions=[
            "身弱已被证明 (前提不成立)",
            "印星可用性判定",
            "比劫可用性判定",
        ],
        gap_analysis=(
            "'身弱喜印比生扶'有明确原典依据('身弱喜印''日干无气遇劫为强''身衰则喜扶喜助'). "
            "但前提是'身弱'已经被独立证明. 当前STR-001A(身弱)尚未被证明, 所以STR-001B的前提不成立. "
            "另外, '身弱喜扶'与'此命具体某一个印/比一定为用神'不是同一层命题, "
            "还需要判定印星/比劫的具体可用性."
        ),
        status=CanonicalEvidenceStatus.UNPROVEN,
        notes="原典依据存在, 但前提(身弱)不成立, 且印比可用性需要单独判定",
    )

    return SemanticMappingChain(
        chain_id="CHAIN-STR-001B-XIYINBI",
        feature=feature,
        semantic_mapping=semantic_mapping,
        canonical_evidence=canonical_evidence,
        canonical_condition=None,
    )


# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 90)
    print("Canonical Semantic Mapping Contract - 正式架构框架")
    print("=" * 90)
    print("\n核心问题: Engine算出了一个数, 不代表这个数已经获得了原典概念的语义授权.")
    print("\n三层架构 (每层独立Fidelity, 下层未通过上层不能自动通过):")
    print("""
  Layer 1: Engine Feature (确定性计算结果, 如 wood_ratio=0.125)
    ↓ Feature Semantic Mapping (回答: 这个Feature能否证明某个语义概念?)
  Layer 2: Semantic Concept (如 "木气偏少")
    ↓ Canonical Evidence (回答: 这个语义概念是否足以成为Canonical命题的证据?)
  Layer 3: Canonical Proposition (如 "日主身弱")
    ↓ Canonical Condition (经过语义授权的条件)
  Layer 4: Authorized Condition
    ↓
  Layer 5: Canonical Judgment
    ↓ (FROZEN)
  Layer 6: Canonical Assertion
""")

    # STR-001A 实例
    print(f"\n{'='*90}")
    print("实例验证: STR-001A 日主身弱 (wood_ratio → 木气偏少 → 身弱)")
    print("=" * 90)
    chain_a = build_str001_chain()
    result_a = chain_a.validate_chain()

    print(f"\n  Layer 1 - Engine Feature:")
    print(f"    feature_id: {chain_a.feature.feature_id}")
    print(f"    value: {chain_a.feature.value}")
    print(f"    calculation: {chain_a.feature.calculation_method}")
    print(f"    semantic_type: {chain_a.feature.semantic_type}")
    print(f"    status: {chain_a.feature.status.value}")
    print(f"    evidence: {chain_a.feature.evidence}")

    print(f"\n  Layer 2 - Feature Semantic Mapping:")
    print(f"    mapping_id: {chain_a.semantic_mapping.mapping_id}")
    print(f"    semantic_concept: {chain_a.semantic_mapping.semantic_concept}")
    print(f"    mapping_rule: {chain_a.semantic_mapping.mapping_rule}")
    print(f"    status: {chain_a.semantic_mapping.status.value}")
    print(f"    gap: {chain_a.semantic_mapping.gap_analysis[:100]}...")

    print(f"\n  Layer 3 - Canonical Evidence:")
    print(f"    evidence_id: {chain_a.canonical_evidence.evidence_id}")
    print(f"    semantic_concept: {chain_a.canonical_evidence.semantic_concept}")
    print(f"    canonical_proposition: {chain_a.canonical_evidence.canonical_proposition}")
    print(f"    status: {chain_a.canonical_evidence.status.value}")
    print(f"    provided_dimensions: {chain_a.canonical_evidence.provided_dimensions}")
    print(f"    missing_dimensions: {chain_a.canonical_evidence.missing_dimensions}")
    print(f"    gap: {chain_a.canonical_evidence.gap_analysis[:100]}...")

    print(f"\n  Layer 4 - Canonical Condition: NOT CREATED (下层未通过)")

    print(f"\n  Chain Validation Result:")
    for k, v in result_a.items():
        print(f"    {k}: {v}")

    # STR-001B 实例
    print(f"\n{'='*90}")
    print("实例验证: STR-001B 身弱喜印比生扶 (前提: 身弱已被证明)")
    print("=" * 90)
    chain_b = build_str001b_chain()
    result_b = chain_b.validate_chain()

    print(f"\n  Layer 1 - Engine Feature: {chain_b.feature.feature_id} (PENDING)")
    print(f"  Layer 2 - Semantic Mapping: {chain_b.semantic_mapping.status.value}")
    print(f"  Layer 3 - Canonical Evidence: {chain_b.canonical_evidence.status.value}")
    print(f"  Layer 4 - Canonical Condition: NOT CREATED")

    print(f"\n  关键问题: STR-001B的前提是STR-001A(身弱)已被证明, 当前前提不成立")
    print(f"  原典依据: '身弱喜印''日干无气遇劫为强''身衰则喜扶喜助' - 存在")
    print(f"  但: '身弱喜扶'与'此命具体某一个印/比一定为用神'不是同一层命题")

    print(f"\n  Chain Validation Result:")
    for k, v in result_b.items():
        print(f"    {k}: {v}")

    # 治理规则
    print(f"\n{'='*90}")
    print("治理规则 (正式确立)")
    print("=" * 90)
    print("""
  1. 不能从原典文本描述 → 人工归纳 → 直接变成机器必要条件
  2. Feature Semantic Mapping需要独立验证 (Layer 2)
  3. Canonical Evidence需要独立验证 (Layer 3)
  4. 每层都有自己的Fidelity, 不能合并
  5. 下层UNPROVEN/INSUFFICIENT时, 上层只能是PENDING, 不能自动AUTHORIZED
  6. Feature Equivalence ≠ Judgment Equivalence (正式架构原则)
  7. ENGINEERING_STATISTICAL_METRIC ≠ CANONICAL_CONCEPT
  8. 不能用工程阈值定义命理概念 (防止循环自证)
  9. Canonical Condition必须基于AUTHORIZED的层, 不能基于UNPROVEN的Feature
  10. Assertion继续冻结, 不进入Interpretation/Polarity/Cross-Engine
""")

    # 当前状态汇总
    print(f"\n{'='*90}")
    print("当前状态汇总 (修正后)")
    print("=" * 90)
    print("""
  Judgment                    Selection  Canonical Fidelity  当前状态
  ─────────────────────────────────────────────────────────────────────
  PAT-001 正财格              ✓          ✓                   VALID
  TUN-001 乙木戌月调候        ✓          ✓                   VALID
  STR-001A 日主身弱           ✓          ❌ (Layer2/3未通过)  HOLD
  STR-001B 身弱喜印比         ✓          ❌ (前提不成立)       HOLD (前提依赖STR-001A)
  PAT-010 用神正财            ✓          ❌ (有正财≠用神)      RETIRE CANDIDATE
  STR-004 五行偏枯            ✓          ❌ (imbalance≠偏枯)    HOLD

  Production-valid Canonical Judgments = 2
  HOLD = 3 (STR-001A, STR-001B, STR-004)
  RETIRE CANDIDATE = 1 (PAT-010)

  注: STR-001已拆分为STR-001A(身弱)和STR-001B(身弱喜印比), 避免Jump1/Jump2被一个Judgment捆绑
""")

    print("=" * 90)
    print("Contract框架建立完成. 此框架可被子平/盲派/紫微/河洛/易经共用.")
    print("下一步: 基于此Contract, 建立身弱的Canonical Source Mapping和Feature Semantic Mapping.")
    print("=" * 90)


if __name__ == "__main__":
    main()
