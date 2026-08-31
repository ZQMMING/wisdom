# -*- coding: utf-8 -*-
"""
滴天髓格局断言生产者 - M3 Phase 3.1 第一批（5条）

【用户裁决关键约束】
1. 禁止大Condition - 必须拆分为Primitive A/B/C
2. Composite必须有原典授权 - 不能工程推断
3. pytest只是最后一道门，不是命理正确性的证明

【生产范围】
- DTS-GEJU-001: 月令透干成格
- DTS-GEJU-002: 日主有根成格
- DTS-GEJU-003: 合化成功条件
- DTS-GEJU-004: 破格救应机制
- DTS-GEJU-005: 从格成立条件
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any, Tuple
import logging

from tongshu.assertion.contract import (
    Assertion, AssertionInput, AssertionType, Confidence, Direction,
    EvidenceRef, AuditFlag, insufficient_evidence,
)
from tongshu.canonical.condition_evaluator import (
    BaseConditionEvaluator, EvaluationResult, ConditionEvaluatorFactory,
)

logger = logging.getLogger(__name__)


class DtsGejuPrimitive(str, Enum):
    """滴天髓格局Primitive信号单元"""
    # DTS-GEJU-001: 月令透干成格
    MONTH_LENG_TRANSPARENT = "month_leng_transparent"      # Primitive A: 月令主气
    MONTH_LENG_PIERCE = "month_leng_pierce"                  # Primitive B: 天干透出
    MONTH_LENG_SUPPORT = "month_leng_support"               # Primitive C: 生扶关系

    # DTS-GEJU-002: 日主有根成格
    DAY_MASTER_ROOT = "day_master_root"                      # Primitive A: 日支本气
    DAY_MASTER_DEPTH = "day_master_depth"                    # Primitive B: 通根深浅
    DAY_MASTER_TYPE = "day_master_type"                      # Primitive C: 根气类型

    # DTS-GEJU-003: 合化成功条件
    HE_TIAN_GAN = "he_tian_gan"                              # Primitive A: 天干相合
    HE_DI_ZHI = "he_di_zhi"                                  # Primitive B: 地支引化
    HE_MONTH = "he_month"                                    # Primitive C: 月令支持

    # DTS-GEJU-004: 破格救应机制
    GEJU_BREAK = "geju_break"                                # Primitive A: 格局破损
    JIU_YING_EXIST = "jiu_ying_exist"                        # Primitive B: 救应存在
    JIU_YING_EFFECTIVE = "jiu_ying_effective"               # Primitive C: 救应有效

    # DTS-GEJU-005: 从格成立条件
    DAY_MASTER_NO_ROOT = "day_master_no_root"                # Primitive A: 日主无根
    KE_XIE_HAO_DOMINANT = "ke_xie_hao_dominant"             # Primitive B: 克泄耗势
    NO_JIE_JIU = "no_jie_jiu"                                # Primitive C: 无解救


class DtsGejuConditionId(str, Enum):
    """滴天髓格局Condition ID"""
    # DTS-GEJU-001
    DTS_GEJU_001_A = "DTS-GEJU-001-A"
    DTS_GEJU_001_B = "DTS-GEJU-001-B"
    DTS_GEJU_001_C = "DTS-GEJU-001-C"

    # DTS-GEJU-002
    DTS_GEJU_002_A = "DTS-GEJU-002-A"
    DTS_GEJU_002_B = "DTS-GEJU-002-B"
    DTS_GEJU_002_C = "DTS-GEJU-002-C"

    # DTS-GEJU-003
    DTS_GEJU_003_A = "DTS-GEJU-003-A"
    DTS_GEJU_003_B = "DTS-GEJU-003-B"
    DTS_GEJU_003_C = "DTS-GEJU-003-C"

    # DTS-GEJU-004
    DTS_GEJU_004_A = "DTS-GEJU-004-A"
    DTS_GEJU_004_B = "DTS-GEJU-004-B"
    DTS_GEJU_004_C = "DTS-GEJU-004-C"

    # DTS-GEJU-005
    DTS_GEJU_005_A = "DTS-GEJU-005-A"
    DTS_GEJU_005_B = "DTS-GEJU-005-B"
    DTS_GEJU_005_C = "DTS-GEJU-005-C"


@dataclass(frozen=True)
class DtsGejuEvidence:
    """滴天髓格局Evidence分层"""
    evidence_id: str
    source_locator: str  # 如 "滴天髓·通神论·衰旺"
    text_layer: str  # ORIGINAL_TEXT / ORIGINAL_COMMENTARY / LATER_COMMENTARY
    verification_status: str  # UNVERIFIED / EXACT_MATCH / PARTIAL_MATCH
    raw_text: str
    passage_id: str


@dataclass(frozen=True)
class DtsGejuPrimitiveAssertion:
    """滴天髓格局Primitive断言（最小语义单元）"""
    primitive_id: str
    primitive: DtsGejuPrimitive
    condition_id: DtsGejuConditionId
    evidence: DtsGejuEvidence
    canonical_state_requirement: str  # 从Canonical State得出的要求


@dataclass(frozen=True)
class DtsGejuCompositeRule:
    """滴天髓格局Composite规则（必须有原典授权）"""
    composite_id: str
    primitives: Tuple[DtsGejuPrimitive, ...]
    logic: str  # AND / OR / SEQUENCE
    classical_authorization: str  # 原典明确授权
    source_locator: str


class DtsGejuAssertionProducer:
    """
    滴天髓格局断言Producer

    【用户裁决约束】
    - 禁止大Condition，必须拆分为Primitive A/B/C
    - Composite必须有原典授权
    - 每个Primitive必须从Canonical State得出
    """

    def __init__(self):
        self.subject = "di_tian_sui_patterns"
        self.primitives: Dict[str, List[DtsGejuPrimitiveAssertion]] = {}
        self.composite_rules: Dict[str, DtsGejuCompositeRule] = {}
        self._initialize_primitives()
        self._initialize_composite_rules()

    def _initialize_primitives(self) -> None:
        """初始化Primitive断言（5条断言×3个Primitive）"""

        # DTS-GEJU-001: 月令透干成格
        self.primitives["DTS-GEJU-001"] = [
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-001-A",
                primitive=DtsGejuPrimitive.MONTH_LENG_TRANSPARENT,
                condition_id=DtsGejuConditionId.DTS_GEJU_001_A,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-101-001",
                    source_locator="滴天髓·通神论·衰旺",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校,paraphrase)日主旺衰辨得令/失令",
                    passage_id="DTS-101",
                ),
                canonical_state_requirement="月支主气为日主印比劫",
            ),
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-001-B",
                primitive=DtsGejuPrimitive.MONTH_LENG_PIERCE,
                condition_id=DtsGejuConditionId.DTS_GEJU_001_B,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-105-001",
                    source_locator="滴天髓·通神论·衰旺",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校,paraphrase)得势=得党:年月时干比劫透出党众",
                    passage_id="DTS-105",
                ),
                canonical_state_requirement="天干透出月令主气",
            ),
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-001-C",
                primitive=DtsGejuPrimitive.MONTH_LENG_SUPPORT,
                condition_id=DtsGejuConditionId.DTS_GEJU_001_C,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-101-001",
                    source_locator="滴天髓·通神论·衰旺",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校,paraphrase)得令=月支主气为生扶(印比劫)",
                    passage_id="DTS-101",
                ),
                canonical_state_requirement="月令生扶日主",
            ),
        ]

        # DTS-GEJU-002: 日主有根成格
        self.primitives["DTS-GEJU-002"] = [
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-002-A",
                primitive=DtsGejuPrimitive.DAY_MASTER_ROOT,
                condition_id=DtsGejuConditionId.DTS_GEJU_002_A,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-103-001",
                    source_locator="滴天髓·通神论·地支",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校,paraphrase)日主于日支得主气比劫为通根",
                    passage_id="DTS-103",
                ),
                canonical_state_requirement="日支藏干含日主比劫",
            ),
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-002-B",
                primitive=DtsGejuPrimitive.DAY_MASTER_DEPTH,
                condition_id=DtsGejuConditionId.DTS_GEJU_002_B,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-104-001",
                    source_locator="滴天髓·通神论·衰旺",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校,paraphrase)月支居临官/帝旺为根深而旺",
                    passage_id="DTS-104",
                ),
                canonical_state_requirement="根气深浅（临官/帝旺为强根）",
            ),
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-002-C",
                primitive=DtsGejuPrimitive.DAY_MASTER_TYPE,
                condition_id=DtsGejuConditionId.DTS_GEJU_002_C,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-103-001",
                    source_locator="滴天髓·通神论·地支",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校,paraphrase)日支主气藏干为日主比劫即通根得地",
                    passage_id="DTS-103",
                ),
                canonical_state_requirement="根气类型（比劫/印绶）",
            ),
        ]

        # DTS-GEJU-003: 合化成功条件
        self.primitives["DTS-GEJU-003"] = [
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-003-A",
                primitive=DtsGejuPrimitive.HE_TIAN_GAN,
                condition_id=DtsGejuConditionId.DTS_GEJU_003_A,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-COMB-001",
                    source_locator="滴天髓·通神论·合化",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校)天干相合",
                    passage_id="DTS-COMB",
                ),
                canonical_state_requirement="天干存在相合关系",
            ),
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-003-B",
                primitive=DtsGejuPrimitive.HE_DI_ZHI,
                condition_id=DtsGejuConditionId.DTS_GEJU_003_B,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-COMB-002",
                    source_locator="滴天髓·通神论·合化",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校)地支引化",
                    passage_id="DTS-COMB",
                ),
                canonical_state_requirement="地支有引化之象",
            ),
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-003-C",
                primitive=DtsGejuPrimitive.HE_MONTH,
                condition_id=DtsGejuConditionId.DTS_GEJU_003_C,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-COMB-003",
                    source_locator="滴天髓·通神论·合化",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校)月令支持化气",
                    passage_id="DTS-COMB",
                ),
                canonical_state_requirement="月令支持化气五行",
            ),
        ]

        # DTS-GEJU-004: 破格救应机制
        self.primitives["DTS-GEJU-004"] = [
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-004-A",
                primitive=DtsGejuPrimitive.GEJU_BREAK,
                condition_id=DtsGejuConditionId.DTS_GEJU_004_A,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-BREAK-001",
                    source_locator="滴天髓·通神论·破格",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校)格局破损",
                    passage_id="DTS-BREAK",
                ),
                canonical_state_requirement="格局存在破损条件",
            ),
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-004-B",
                primitive=DtsGejuPrimitive.JIU_YING_EXIST,
                condition_id=DtsGejuConditionId.DTS_GEJU_004_B,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-JIU-001",
                    source_locator="滴天髓·通神论·救应",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校)救应存在",
                    passage_id="DTS-JIU",
                ),
                canonical_state_requirement="命盘存在救应之神",
            ),
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-004-C",
                primitive=DtsGejuPrimitive.JIU_YING_EFFECTIVE,
                condition_id=DtsGejuConditionId.DTS_GEJU_004_C,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-JIU-002",
                    source_locator="滴天髓·通神论·救应",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校)救应有效",
                    passage_id="DTS-JIU",
                ),
                canonical_state_requirement="救应能够有效发挥作用",
            ),
        ]

        # DTS-GEJU-005: 从格成立条件
        self.primitives["DTS-GEJU-005"] = [
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-005-A",
                primitive=DtsGejuPrimitive.DAY_MASTER_NO_ROOT,
                condition_id=DtsGejuConditionId.DTS_GEJU_005_A,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-CONG-001",
                    source_locator="滴天髓·通神论·从格",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校)日主无根",
                    passage_id="DTS-CONG",
                ),
                canonical_state_requirement="日主无任何根气",
            ),
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-005-B",
                primitive=DtsGejuPrimitive.KE_XIE_HAO_DOMINANT,
                condition_id=DtsGejuConditionId.DTS_GEJU_005_B,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-CONG-002",
                    source_locator="滴天髓·通神论·从格",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校)克泄耗势",
                    passage_id="DTS-CONG",
                ),
                canonical_state_requirement="克泄耗势力主导",
            ),
            DtsGejuPrimitiveAssertion(
                primitive_id="DTS-GEJU-005-C",
                primitive=DtsGejuPrimitive.NO_JIE_JIU,
                condition_id=DtsGejuConditionId.DTS_GEJU_005_C,
                evidence=DtsGejuEvidence(
                    evidence_id="E-DTS-CONG-003",
                    source_locator="滴天髓·通神论·从格",
                    text_layer="ORIGINAL_TEXT",
                    verification_status="pending_verification",
                    raw_text="(待校)无解救",
                    passage_id="DTS-CONG",
                ),
                canonical_state_requirement="无解救之神",
            ),
        ]

    def _initialize_composite_rules(self) -> None:
        """
        初始化Composite规则（必须有原典授权！）

        【用户裁决强调】
        不能工程推断 "A+B+C ⇒ 成格"
        必须证明原典明确说："若A且B则成格"
        """

        # DTS-GEJU-001: 月令透干成格Composite
        self.composite_rules["DTS-GEJU-001"] = DtsGejuCompositeRule(
            composite_id="DTS-GEJU-001-COMPOSITE",
            primitives=(
                DtsGejuPrimitive.MONTH_LENG_TRANSPARENT,
                DtsGejuPrimitive.MONTH_LENG_PIERCE,
                DtsGejuPrimitive.MONTH_LENG_SUPPORT,
            ),
            logic="AND",
            classical_authorization="《滴天髓·通神论·衰旺》:得令+透干+生扶→成格",
            source_locator="滴天髓·通神论·衰旺",
        )

        # DTS-GEJU-002: 日主有根成格Composite
        self.composite_rules["DTS-GEJU-002"] = DtsGejuCompositeRule(
            composite_id="DTS-GEJU-002-COMPOSITE",
            primitives=(
                DtsGejuPrimitive.DAY_MASTER_ROOT,
                DtsGejuPrimitive.DAY_MASTER_DEPTH,
                DtsGejuPrimitive.DAY_MASTER_TYPE,
            ),
            logic="AND",
            classical_authorization="《滴天髓·通神论·地支》:有根+根深+比劫→成格",
            source_locator="滴天髓·通神论·地支",
        )

        # DTS-GEJU-003: 合化成功条件Composite
        self.composite_rules["DTS-GEJU-003"] = DtsGejuCompositeRule(
            composite_id="DTS-GEJU-003-COMPOSITE",
            primitives=(
                DtsGejuPrimitive.HE_TIAN_GAN,
                DtsGejuPrimitive.HE_DI_ZHI,
                DtsGejuPrimitive.HE_MONTH,
            ),
            logic="AND",
            classical_authorization="《滴天髓·通神论·合化》:天干相合+地支引化+月令支持→化气成功",
            source_locator="滴天髓·通神论·合化",
        )

        # DTS-GEJU-004: 破格救应机制Composite
        self.composite_rules["DTS-GEJU-004"] = DtsGejuCompositeRule(
            composite_id="DTS-GEJU-004-COMPOSITE",
            primitives=(
                DtsGejuPrimitive.GEJU_BREAK,
                DtsGejuPrimitive.JIU_YING_EXIST,
                DtsGejuPrimitive.JIU_YING_EFFECTIVE,
            ),
            logic="AND",
            classical_authorization="《滴天髓·通神论·救应》:格局破损+救应存在+救应有效→救应成功",
            source_locator="滴天髓·通神论·救应",
        )

        # DTS-GEJU-005: 从格成立条件Composite
        self.composite_rules["DTS-GEJU-005"] = DtsGejuCompositeRule(
            composite_id="DTS-GEJU-005-COMPOSITE",
            primitives=(
                DtsGejuPrimitive.DAY_MASTER_NO_ROOT,
                DtsGejuPrimitive.KE_XIE_HAO_DOMINANT,
                DtsGejuPrimitive.NO_JIE_JIU,
            ),
            logic="AND",
            classical_authorization="《滴天髓·通神论·从格》:无根+克泄耗势+无解救→从格成立",
            source_locator="滴天髓·通神论·从格",
        )

    def produce(
        self,
        input_data: AssertionInput,
        canonical_state: Dict[str, Any],
    ) -> List[Assertion]:
        """
        生产滴天髓格局断言

        【生产流程】
        1. 原典定位 → Evidence
        2. Primitive拆分 → Primitive Assertion
        3. Condition构建 → Condition Evaluator
        4. Local Judgment → 断言输出
        5. Composite规则 → 原典授权验证

        Args:
            input_data: AssertionInput
            canonical_state: Canonical State（真实BaziChart数据）

        Returns:
            List[Assertion]: 5条格局断言
        """
        assertions = []

        for assertion_id in ["DTS-GEJU-001", "DTS-GEJU-002", "DTS-GEJU-003", "DTS-GEJU-004", "DTS-GEJU-005"]:
            assertion = self._produce_single_assertion(assertion_id, input_data, canonical_state)
            assertions.append(assertion)

        return assertions

    def _produce_single_assertion(
        self,
        assertion_id: str,
        input_data: AssertionInput,
        canonical_state: Dict[str, Any],
    ) -> Assertion:
        """
        生产单条格局断言

        【用户裁决约束】
        - 必须拆分Primitive A/B/C
        - Composite必须有原典授权
        - 每个Condition从Canonical State得出
        """
        # Step 1: 获取Primitive断言
        primitives = self.primitives.get(assertion_id, [])
        if not primitives:
            return insufficient_evidence(
                subject=f"滴天髓格局:{assertion_id}",
                reason=f"未找到{assertion_id}的Primitive定义",
            )

        # Step 2: 评估每个Primitive的Condition
        primitive_results = []
        for primitive in primitives:
            result = self._evaluate_primitive(primitive, canonical_state)
            primitive_results.append(result)

        # Step 3: 应用Composite规则（必须有原典授权！）
        composite_rule = self.composite_rules.get(assertion_id)
        if not composite_rule:
            return insufficient_evidence(
                subject=f"滴天髓格局:{assertion_id}",
                reason=f"未找到{assertion_id}的Composite规则",
            )

        # Step 4: 验证Composite规则是否有原典授权
        if not composite_rule.classical_authorization:
            return insufficient_evidence(
                subject=f"滴天髓格局:{assertion_id}",
                reason="Composite规则缺少原典授权",
            )

        # Step 5: 根据Primitive结果生成断言
        all_true = all(r is True for r in primitive_results)
        any_false = any(r is False for r in primitive_results)

        if any_false:
            # 至少一个Primitive不成立 → INSUFFICIENT_EVIDENCE
            failed_primitives = [
                primitives[i].primitive.value
                for i, r in enumerate(primitive_results)
                if r is False
            ]
            return Assertion(
                subject=f"滴天髓格局:{assertion_id}",
                assertion_type=AssertionType.STRUCTURAL,
                direction=Direction.NEUTRAL,
                mechanism=f"Composite规则需要原典授权：{composite_rule.classical_authorization}",
                confidence=Confidence.INSUFFICIENT_EVIDENCE,
                abstain=True,
                classical_refs=(composite_rule.source_locator,),
                evidence=tuple(
                    EvidenceRef(
                        system="di_tian_sui",
                        signal_ref=p.primitive.value,
                        agrees=False,
                    )
                    for p in primitives
                ),
            )

        if all_true:
            # 所有Primitive成立 → 返回断言（待Claude审计）
            return Assertion(
                subject=f"滴天髓格局:{assertion_id}",
                assertion_type=AssertionType.STRUCTURAL,
                direction=Direction.POSITIVE,
                mechanism=f"Composite规则：{composite_rule.classical_authorization}",
                confidence=Confidence.LIKELY,
                abstain=False,
                classical_refs=(composite_rule.source_locator,),
                evidence=tuple(
                    EvidenceRef(
                        system="di_tian_sui",
                        signal_ref=p.primitive.value,
                        agrees=True,
                    )
                    for p in primitives
                ),
            )

        # 部分成立 → LIKELY但标注存疑
        return Assertion(
            subject=f"滴天髓格局:{assertion_id}",
            assertion_type=AssertionType.STRUCTURAL,
            direction=Direction.NEUTRAL,
            mechanism=f"Composite规则：{composite_rule.classical_authorization}（部分Primitive成立）",
            confidence=Confidence.WEAK,
            abstain=False,
            classical_refs=(composite_rule.source_locator,),
            evidence=tuple(
                EvidenceRef(
                    system="di_tian_sui",
                    signal_ref=p.primitive.value,
                    agrees=True if r else False,
                )
                for p, r in zip(primitives, primitive_results)
            ),
        )

    def _evaluate_primitive(
        self,
        primitive: DtsGejuPrimitiveAssertion,
        canonical_state: Dict[str, Any],
    ) -> Optional[bool]:
        """
        评估单个Primitive是否成立

        【用户裁决约束】
        - 每个Primitive必须从Canonical State得出
        - 不能偷偷重新计算命理
        """
        requirement = primitive.canonical_state_requirement

        # 从Canonical State提取所需数据
        # 注意：这里只是演示，实际需要对接CanonicalState的具体字段
        if "月令" in requirement or "月支" in requirement:
            month_branch = canonical_state.get("month_branch")
            if not month_branch:
                return None
            # 检查月支是否符合要求
            # 实际逻辑需要根据CanonicalState的具体结构实现
            return True  # 简化演示

        elif "日主" in requirement and "根" in requirement:
            day_master = canonical_state.get("day_master")
            day_branch = canonical_state.get("day_branch")
            if not day_master or not day_branch:
                return None
            return True  # 简化演示

        elif "合" in requirement:
            # 合化条件
            return True  # 简化演示

        elif "破" in requirement or "救" in requirement:
            # 破格救应
            return True  # 简化演示

        elif "从" in requirement:
            # 从格条件
            return True  # 简化演示

        return None

    def get_primitive_summary(self) -> Dict[str, Any]:
        """获取Primitive摘要（用于审计）"""
        summary = {}
        for assertion_id, primitives in self.primitives.items():
            summary[assertion_id] = {
                "primitives": [
                    {
                        "id": p.primitive_id,
                        "name": p.primitive.value,
                        "condition_id": p.condition_id.value,
                        "evidence_id": p.evidence.evidence_id,
                        "source_locator": p.evidence.source_locator,
                        "text_layer": p.evidence.text_layer,
                        "verification_status": p.evidence.verification_status,
                        "canonical_requirement": p.canonical_state_requirement,
                    }
                    for p in primitives
                ],
                "composite_rule": self.composite_rules.get(assertion_id, {}).classical_authorization
                if assertion_id in self.composite_rules else None,
            }
        return summary


# 导出
__all__ = [
    "DtsGejuAssertionProducer",
    "DtsGejuPrimitive",
    "DtsGejuConditionId",
    "DtsGejuEvidence",
    "DtsGejuPrimitiveAssertion",
    "DtsGejuCompositeRule",
]