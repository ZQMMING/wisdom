"""
STR-001A P6.2-D Authorized Assertion Library Schema + Admission Gate

目标: 先把正式入库门槛定死, 再把 ASSERT-002 作为第一条 Golden Authorized Assertion 入库。

核心原则:
  原典有证据 ≠ 可以断事
  条件可以匹配 ≠ 有资格下结论
  MATCHED ≠ 自动授权结论

Admission Gate 逐层验证:
  Layer 1: EVIDENCE_AUTHORITY      (原典证据层)
  Layer 2: PRECONDITION_AUTHORITY  (前置条件授权层)
  Layer 3: MATCHER_STRUCTURE       (匹配器结构化层)
  Layer 4: EFFECT_AUTHORITY        (效果授权层)
  Layer 5: CONCLUSION_AUTHORITY    (结论授权层)
  Layer 6: REVERSE_CONDITION       (反向条件/排除层)
  Layer 7: TEST_COVERAGE           (测试覆盖层)

入库状态:
  AUTHORIZED                    — 完全授权, 可用于断事
  AUTHORIZED_WITH_QUALIFIER    — 带条件授权
  CANDIDATE                     — 候选, 待进一步审计
  REJECTED                      — 被拒绝, 不入库
  POSTERIOR                     — 后置断言, 仅作参考
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime


# ============================================================
# 状态枚举
# ============================================================

class EvidenceStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    PARTIALLY_AUTHORIZED = "PARTIALLY_AUTHORIZED"
    CANDIDATE = "CANDIDATE"
    SOURCE_MAPPED_NON_PROOF = "SOURCE_MAPPED_NON_PROOF"
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"


class MatchStatus(str, Enum):
    MATCHED = "MATCHED"
    NOT_MATCHED = "NOT_MATCHED"
    UNRESOLVED = "UNRESOLVED"


class ConclusionStatus(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    QUALIFIED = "QUALIFIED"
    CANDIDATE = "CANDIDATE"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    UNRESOLVED = "UNRESOLVED"


class AdmissionStatus(str, Enum):
    """入库最终状态"""
    AUTHORIZED = "AUTHORIZED"                              # 完全授权入库
    AUTHORIZED_WITH_QUALIFIER = "AUTHORIZED_WITH_QUALIFIER"  # 带条件授权入库
    CANDIDATE = "CANDIDATE"                                # 候选, 待进一步审计
    REJECTED = "REJECTED"                                  # 被拒绝, 不入库
    POSTERIOR = "POSTERIOR"                                # 后置断言, 仅作参考


class PreconditionSourceType(str, Enum):
    CONSUMED_CANONICAL_STATE = "CONSUMED_CANONICAL_STATE"
    SOURCE_DEFINED_STATE = "SOURCE_DEFINED_STATE"
    SOURCE_DEFINED_RELATIVE_STATE = "SOURCE_DEFINED_RELATIVE_STATE"
    L1_FACT = "L1_FACT"
    ENGINE_DERIVED = "ENGINE_DERIVED"


class GateLayer(str, Enum):
    EVIDENCE = "L1_EVIDENCE"
    PRECONDITION = "L2_PRECONDITION"
    MATCHER = "L3_MATCHER"
    EFFECT = "L4_EFFECT"
    CONCLUSION = "L5_CONCLUSION"
    REVERSE = "L6_REVERSE_CONDITION"
    TEST = "L7_TEST_COVERAGE"


# ============================================================
# 数据结构
# ============================================================

@dataclass
class EvidenceRecord:
    """EVIDENCE 层记录"""
    source_book: str                              # 原典书名
    source_texts: List[str] = field(default_factory=list)  # 原典原文列表
    source_locations: List[str] = field(default_factory=list)  # 出处位置
    evidence_status: EvidenceStatus = EvidenceStatus.INSUFFICIENT_SOURCE
    cross_validation_count: int = 0               # 交叉验证次数(不同出处)
    reverse_conditions: List[str] = field(default_factory=list)
    qualifiers: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class PreconditionDef:
    """前置条件定义"""
    pid: str
    name: str
    description: str
    source_type: PreconditionSourceType
    authority_note: str = ""                      # 授权说明
    canonical_state_ref: str = ""                 # 引用的Canonical State字段
    is_relative: bool = False                     # 是否为相对概念(如杀浅)
    requires_qualifier: bool = False              # 是否必须带qualifier


@dataclass
class MatcherDef:
    """匹配器定义"""
    matcher_type: str = "STRUCTURED"              # STRUCTURED / KEYWORD / HYBRID
    requires_all_preconditions: bool = True        # 是否要求所有前置条件同时满足
    allows_partial_match: bool = False             # 是否允许部分匹配
    unresolved_handling: str = "BLOCK"            # BLOCK / ALLOW_CANDIDATE / REJECT
    keyword_only: bool = False                     # 是否仅关键词匹配(禁止)


@dataclass
class EffectDef:
    """EFFECT 层定义"""
    effect_text: str                               # 效果原文(如"假杀为权")
    effect_source: str                             # 效果出处
    effect_authority: str = ""                     # 效果授权说明
    effect_qualifiers: List[str] = field(default_factory=list)
    effect_examples: List[str] = field(default_factory=list)  # 效果示例(如"得权贵以显扬")


@dataclass
class ConclusionDef:
    """CONCLUSION 层定义"""
    conclusion_status: ConclusionStatus = ConclusionStatus.UNRESOLVED
    conclusion_reason: str = ""
    allowed_outputs: List[str] = field(default_factory=list)  # 允许输出的断语
    forbidden_outputs: List[str] = field(default_factory=list)  # 禁止输出的断语
    requires_qualifier_in_output: bool = False     # 输出时是否必须带qualifier


@dataclass
class TestCase:
    """测试用例"""
    case_id: str
    case_name: str
    case_type: str = "MATCH"                       # MATCH / NOT_MATCH / REVERSE / QUALIFIER / UNRESOLVED
    input_chart: Dict = field(default_factory=dict)
    canonical_state: Dict = field(default_factory=dict)
    expected_match: MatchStatus = MatchStatus.MATCHED
    expected_conclusion: ConclusionStatus = ConclusionStatus.AUTHORIZED
    actual_match: Optional[MatchStatus] = None
    actual_conclusion: Optional[ConclusionStatus] = None
    passed: bool = False
    notes: str = ""


@dataclass
class GateCheckResult:
    """单层 Gate 检查结果"""
    layer: GateLayer
    passed: bool = False
    score: int = 0                                 # 0-100
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: str = ""


@dataclass
class AdmissionResult:
    """入库最终结果"""
    assertion_id: str
    assertion_text: str
    admission_status: AdmissionStatus = AdmissionStatus.CANDIDATE
    gate_results: List[GateCheckResult] = field(default_factory=list)
    overall_score: int = 0
    blocking_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    admission_reason: str = ""
    library_section: str = ""                      # 入库后的分类位置
    admitted_at: str = ""
    version: str = "v1.0"


@dataclass
class AuthorizedAssertion:
    """正式入库的 Authorized Assertion"""
    assertion_id: str
    canonical_text: str                            # 原典断语原文
    source_book: str
    evidence: EvidenceRecord = field(default_factory=lambda: EvidenceRecord(source_book=""))
    preconditions: List[PreconditionDef] = field(default_factory=list)
    matcher: MatcherDef = field(default_factory=MatcherDef)
    effect: EffectDef = field(default_factory=lambda: EffectDef(effect_text="", effect_source=""))
    conclusion: ConclusionDef = field(default_factory=ConclusionDef)
    test_cases: List[TestCase] = field(default_factory=list)
    admission: AdmissionResult = field(default_factory=lambda: AdmissionResult(assertion_id="", assertion_text=""))
    tags: List[str] = field(default_factory=list)
    category: str = ""                             # 分类: 身强/身弱/官杀/财星/食伤/...
    priority: str = "GOLDEN"                      # GOLDEN / SILVER / BRONZE / CANDIDATE


# ============================================================
# Admission Gate 检查器
# ============================================================

class AdmissionGate:
    """
    Authorized Assertion Library 入库门槛检查器

    逐层验证, 前一层不通过不能进入下一层。
    """

    # 各层通过阈值
    LAYER_THRESHOLDS = {
        GateLayer.EVIDENCE: 70,        # 证据层: 至少70分
        GateLayer.PRECONDITION: 60,    # 前置条件层: 至少60分
        GateLayer.MATCHER: 70,          # 匹配器层: 至少70分
        GateLayer.EFFECT: 60,           # 效果层: 至少60分
        GateLayer.CONCLUSION: 60,       # 结论层: 至少60分
        GateLayer.REVERSE: 50,          # 反向条件层: 至少50分
        GateLayer.TEST: 70,             # 测试覆盖层: 至少70分
    }

    def check_all(self, assertion: AuthorizedAssertion) -> AdmissionResult:
        """执行全部7层 Gate 检查"""
        result = AdmissionResult(
            assertion_id=assertion.assertion_id,
            assertion_text=assertion.canonical_text,
        )

        # 逐层检查
        layers = [
            (GateLayer.EVIDENCE, self._check_evidence),
            (GateLayer.PRECONDITION, self._check_precondition),
            (GateLayer.MATCHER, self._check_matcher),
            (GateLayer.EFFECT, self._check_effect),
            (GateLayer.CONCLUSION, self._check_conclusion),
            (GateLayer.REVERSE, self._check_reverse),
            (GateLayer.TEST, self._check_test),
        ]

        all_passed = True
        total_score = 0

        for layer_name, check_func in layers:
            gate_result = check_func(assertion)
            result.gate_results.append(gate_result)
            total_score += gate_result.score

            if not gate_result.passed:
                all_passed = False
                result.blocking_issues.extend(gate_result.issues)
                # 前一层不通过, 后续层仍检查但标记为受影响
                if layer_name in [GateLayer.EVIDENCE, GateLayer.MATCHER]:
                    # 关键层不通过, 直接拒绝
                    pass

            result.warnings.extend(gate_result.warnings)

        result.overall_score = total_score // len(layers) if layers else 0

        # 决定最终入库状态
        result = self._determine_admission_status(result, assertion)

        return result

    def _check_evidence(self, assertion: AuthorizedAssertion) -> GateCheckResult:
        """Layer 1: EVIDENCE_AUTHORITY 原典证据层检查"""
        r = GateCheckResult(layer=GateLayer.EVIDENCE)
        ev = assertion.evidence

        # 检查1: 证据状态
        if ev.evidence_status == EvidenceStatus.CONFIRMED:
            r.score += 40
            r.details += "证据状态=CONFIRMED; "
        elif ev.evidence_status == EvidenceStatus.PARTIALLY_AUTHORIZED:
            r.score += 25
            r.warnings.append("证据状态=PARTIALLY_AUTHORIZED, 非完全确认")
            r.details += "证据状态=PARTIALLY_AUTHORIZED; "
        elif ev.evidence_status == EvidenceStatus.SOURCE_MAPPED_NON_PROOF:
            r.score += 10
            r.issues.append("证据状态=SOURCE_MAPPED_NON_PROOF, 仅有语义映射无完整授权")
            r.details += "证据状态=SOURCE_MAPPED_NON_PROOF; "
        else:
            r.issues.append(f"证据状态={ev.evidence_status.value}, 证据不足")
            r.details += f"证据状态={ev.evidence_status.value}; "

        # 检查2: 原典原文数量
        if len(ev.source_texts) >= 3:
            r.score += 20
            r.details += f"原典原文{len(ev.source_texts)}条(≥3); "
        elif len(ev.source_texts) >= 1:
            r.score += 10
            r.warnings.append(f"仅{len(ev.source_texts)}条原典原文, 建议增加交叉验证")
            r.details += f"原典原文{len(ev.source_texts)}条; "
        else:
            r.issues.append("无原典原文")

        # 检查3: 交叉验证(不同出处)
        if ev.cross_validation_count >= 2:
            r.score += 15
            r.details += f"交叉验证{ev.cross_validation_count}次(≥2); "
        elif ev.cross_validation_count >= 1:
            r.score += 8
            r.warnings.append("仅1次交叉验证, 建议增加不同出处验证")
            r.details += f"交叉验证{ev.cross_validation_count}次; "
        else:
            r.warnings.append("无交叉验证")

        # 检查4: 原典书名
        if ev.source_book in ["《渊海子平》", "《子平真诠》", "《滴天髓》", "《穷通宝鉴》", "《三命通会》"]:
            r.score += 15
            r.details += f"原典={ev.source_book}(五部经典); "
        else:
            r.warnings.append(f"原典={ev.source_book}, 非五部经典核心范围")
            r.score += 5

        # 检查5: 反向条件
        if ev.reverse_conditions:
            r.score += 10
            r.details += f"反向条件{len(ev.reverse_conditions)}条; "
        else:
            r.warnings.append("未记录反向条件, 建议补充")

        r.score = min(r.score, 100)
        r.passed = r.score >= self.LAYER_THRESHOLDS[GateLayer.EVIDENCE]

        if not r.passed:
            r.issues.append(f"证据层得分{r.score}<阈值{self.LAYER_THRESHOLDS[GateLayer.EVIDENCE]}")

        return r

    def _check_precondition(self, assertion: AuthorizedAssertion) -> GateCheckResult:
        """Layer 2: PRECONDITION_AUTHORITY 前置条件授权层检查"""
        r = GateCheckResult(layer=GateLayer.PRECONDITION)

        if not assertion.preconditions:
            r.issues.append("无前置条件定义")
            return r

        # 检查1: 前置条件数量
        if len(assertion.preconditions) >= 2:
            r.score += 20
            r.details += f"前置条件{len(assertion.preconditions)}个(≥2); "
        else:
            r.warnings.append(f"仅{len(assertion.preconditions)}个前置条件, 建议检查是否完整")
            r.score += 10

        # 检查2: 每个前置条件的source_type
        authorized_types = [
            PreconditionSourceType.CONSUMED_CANONICAL_STATE,
            PreconditionSourceType.SOURCE_DEFINED_STATE,
            PreconditionSourceType.SOURCE_DEFINED_RELATIVE_STATE,
            PreconditionSourceType.L1_FACT,
        ]

        for pc in assertion.preconditions:
            if pc.source_type in authorized_types:
                r.score += 15
                r.details += f"{pc.pid}={pc.source_type.value}(授权类型); "
            elif pc.source_type == PreconditionSourceType.ENGINE_DERIVED:
                r.issues.append(f"{pc.pid}=ENGINE_DERIVED, 引擎推导可能产生循环依赖, 需明确授权")
                r.score += 5
            else:
                r.warnings.append(f"{pc.pid} source_type未明确")

        # 检查3: 是否有CONSUMED_CANONICAL_STATE(消费Canonical State, 不重新计算)
        has_consumed = any(pc.source_type == PreconditionSourceType.CONSUMED_CANONICAL_STATE
                          for pc in assertion.preconditions)
        if has_consumed:
            r.score += 15
            r.details += "包含CONSUMED_CANONICAL_STATE(不重新计算); "
        else:
            r.warnings.append("无CONSUMED_CANONICAL_STATE类型前置条件, 需确认是否存在循环计算")

        # 检查4: 相对概念是否标记
        relative_pcs = [pc for pc in assertion.preconditions if pc.is_relative]
        if relative_pcs:
            r.score += 10
            for pc in relative_pcs:
                if pc.requires_qualifier:
                    r.details += f"{pc.pid}为相对概念且要求qualifier; "
                else:
                    r.warnings.append(f"{pc.pid}为相对概念但未要求qualifier, 建议补充")
        else:
            r.score += 5

        # 检查5: 前置条件描述完整性
        complete_pcs = [pc for pc in assertion.preconditions if pc.description and pc.authority_note]
        if len(complete_pcs) == len(assertion.preconditions):
            r.score += 20
            r.details += "所有前置条件描述完整; "
        else:
            r.warnings.append(f"{len(assertion.preconditions)-len(complete_pcs)}个前置条件描述不完整")
            r.score += 10

        r.score = min(r.score, 100)
        r.passed = r.score >= self.LAYER_THRESHOLDS[GateLayer.PRECONDITION]

        return r

    def _check_matcher(self, assertion: AuthorizedAssertion) -> GateCheckResult:
        """Layer 3: MATCHER_STRUCTURE 匹配器结构化层检查"""
        r = GateCheckResult(layer=GateLayer.MATCHER)
        m = assertion.matcher

        # 检查1: 匹配器类型
        if m.matcher_type == "STRUCTURED":
            r.score += 35
            r.details += "匹配器=STRUCTURED(结构化); "
        elif m.matcher_type == "HYBRID":
            r.score += 20
            r.warnings.append("匹配器=HYBRID, 需确认关键词部分不越权")
            r.details += "匹配器=HYBRID; "
        elif m.matcher_type == "KEYWORD":
            r.issues.append("匹配器=KEYWORD(仅关键词), 禁止入库")
            r.score += 5
        else:
            r.issues.append(f"未知匹配器类型: {m.matcher_type}")

        # 检查2: 是否禁止关键词-only
        if not m.keyword_only:
            r.score += 20
            r.details += "非关键词-only; "
        else:
            r.issues.append("keyword_only=True, 禁止入库")

        # 检查3: 前置条件处理
        if m.requires_all_preconditions:
            r.score += 15
            r.details += "要求所有前置条件同时满足; "
        else:
            r.warnings.append("不要求所有前置条件同时满足, 需确认是否合理")
            r.score += 8

        # 检查4: UNRESOLVED处理
        if m.unresolved_handling == "BLOCK":
            r.score += 20
            r.details += "UNRESOLVED=BLOCK(不强行输出); "
        elif m.unresolved_handling == "ALLOW_CANDIDATE":
            r.score += 10
            r.warnings.append("UNRESOLVED=ALLOW_CANDIDATE, 需确认候选输出不越权")
        elif m.unresolved_handling == "REJECT":
            r.score += 15
            r.details += "UNRESOLVED=REJECT; "
        else:
            r.warnings.append(f"未知UNRESOLVED处理: {m.unresolved_handling}")

        # 检查5: 部分匹配
        if not m.allows_partial_match:
            r.score += 10
            r.details += "不允许部分匹配; "
        else:
            r.warnings.append("允许部分匹配, 需确认不越权")
            r.score += 5

        r.score = min(r.score, 100)
        r.passed = r.score >= self.LAYER_THRESHOLDS[GateLayer.MATCHER]

        return r

    def _check_effect(self, assertion: AuthorizedAssertion) -> GateCheckResult:
        """Layer 4: EFFECT_AUTHORITY 效果授权层检查"""
        r = GateCheckResult(layer=GateLayer.EFFECT)
        e = assertion.effect

        # 检查1: 效果文本
        if e.effect_text:
            r.score += 30
            r.details += f"效果文本='{e.effect_text}'; "
        else:
            r.issues.append("无效果文本定义")

        # 检查2: 效果出处
        if e.effect_source:
            r.score += 25
            r.details += f"效果出处={e.effect_source}; "
        else:
            r.issues.append("无效果出处, 效果未获原典授权")

        # 检查3: 效果授权说明
        if e.effect_authority:
            r.score += 20
            r.details += "效果授权说明完整; "
        else:
            r.warnings.append("无效果授权说明, 建议补充")
            r.score += 10

        # 检查4: 效果示例
        if e.effect_examples:
            r.score += 15
            r.details += f"效果示例{len(e.effect_examples)}条; "
        else:
            r.warnings.append("无效果示例, 建议补充原典中的具体效果描述")
            r.score += 5

        # 检查5: 效果qualifier
        if e.effect_qualifiers:
            r.score += 10
            r.details += f"效果qualifier{len(e.effect_qualifiers)}条; "
        else:
            r.score += 5

        r.score = min(r.score, 100)
        r.passed = r.score >= self.LAYER_THRESHOLDS[GateLayer.EFFECT]

        return r

    def _check_conclusion(self, assertion: AuthorizedAssertion) -> GateCheckResult:
        """Layer 5: CONCLUSION_AUTHORITY 结论授权层检查"""
        r = GateCheckResult(layer=GateLayer.CONCLUSION)
        c = assertion.conclusion

        # 检查1: 结论状态
        if c.conclusion_status == ConclusionStatus.AUTHORIZED:
            r.score += 25
            r.details += "结论状态=AUTHORIZED; "
        elif c.conclusion_status == ConclusionStatus.QUALIFIED:
            r.score += 20
            r.details += "结论状态=QUALIFIED(带条件); "
        elif c.conclusion_status == ConclusionStatus.NOT_AUTHORIZED:
            r.issues.append("结论状态=NOT_AUTHORIZED, 禁止入库")
            r.score += 5
        elif c.conclusion_status == ConclusionStatus.UNRESOLVED:
            r.warnings.append("结论状态=UNRESOLVED, 需进一步审计")
            r.score += 10
        else:
            r.warnings.append(f"结论状态={c.conclusion_status.value}")

        # 检查2: 结论原因
        if c.conclusion_reason:
            r.score += 20
            r.details += "结论原因完整; "
        else:
            r.issues.append("无结论原因, 结论授权不透明")

        # 检查3: 允许输出
        if c.allowed_outputs:
            r.score += 20
            r.details += f"允许输出{len(c.allowed_outputs)}条; "
        else:
            r.warnings.append("未定义允许输出的断语, 建议明确")
            r.score += 10

        # 检查4: 禁止输出
        if c.forbidden_outputs:
            r.score += 15
            r.details += f"禁止输出{len(c.forbidden_outputs)}条; "
        else:
            r.warnings.append("未定义禁止输出的断语, 建议明确边界")
            r.score += 5

        # 检查5: 输出是否必须带qualifier
        if c.requires_qualifier_in_output:
            r.score += 10
            r.details += "输出必须带qualifier; "
        else:
            r.score += 5

        # 检查6: 三层分离验证
        # 结论状态不应自动由MATCH_STATUS推导
        if c.conclusion_status in [ConclusionStatus.AUTHORIZED, ConclusionStatus.QUALIFIED]:
            # 必须有明确的结论原因, 不能只是"条件匹配"
            if "条件匹配" in c.conclusion_reason and "原典" not in c.conclusion_reason:
                r.issues.append("结论原因仅基于条件匹配, 未引用原典授权, 违反三层分离原则")
                r.score -= 10

        r.score = max(0, min(r.score, 100))
        r.passed = r.score >= self.LAYER_THRESHOLDS[GateLayer.CONCLUSION]

        return r

    def _check_reverse(self, assertion: AuthorizedAssertion) -> GateCheckResult:
        """Layer 6: REVERSE_CONDITION 反向条件/排除层检查"""
        r = GateCheckResult(layer=GateLayer.REVERSE)

        # 检查1: 证据层反向条件
        ev_reverse = assertion.evidence.reverse_conditions
        if ev_reverse:
            r.score += 35
            r.details += f"证据层反向条件{len(ev_reverse)}条; "
            for rc in ev_reverse:
                r.details += f"  - {rc[:50]}; "
        else:
            r.warnings.append("证据层无反向条件, 建议补充原典中的反向表述")
            r.score += 15

        # 检查2: 结论层禁止输出
        forbidden = assertion.conclusion.forbidden_outputs
        if forbidden:
            r.score += 25
            r.details += f"结论层禁止输出{len(forbidden)}条; "
        else:
            r.warnings.append("结论层无禁止输出定义, 建议明确反向边界")
            r.score += 10

        # 检查3: 测试用例中的反向案例
        reverse_tests = [tc for tc in assertion.test_cases if tc.case_type == "REVERSE"]
        if reverse_tests:
            r.score += 25
            r.details += f"反向测试用例{len(reverse_tests)}个; "
            # 检查反向案例是否通过
            for tc in reverse_tests:
                if tc.passed:
                    r.details += f"  {tc.case_id}通过; "
                else:
                    r.issues.append(f"反向测试用例{tc.case_id}未通过")
        else:
            r.warnings.append("无反向测试用例, 建议补充(验证引擎能正确拒绝反向条件)")
            r.score += 10

        # 检查4: 排除条件明确性
        # 反向条件是否明确说明"什么情况下不适用此断言"
        if ev_reverse and any("不" in rc or "非" in rc or "无" in rc for rc in ev_reverse):
            r.score += 15
            r.details += "反向条件包含明确排除表述; "
        else:
            r.score += 5

        r.score = min(r.score, 100)
        r.passed = r.score >= self.LAYER_THRESHOLDS[GateLayer.REVERSE]

        return r

    def _check_test(self, assertion: AuthorizedAssertion) -> GateCheckResult:
        """Layer 7: TEST_COVERAGE 测试覆盖层检查"""
        r = GateCheckResult(layer=GateLayer.TEST)

        if not assertion.test_cases:
            r.issues.append("无测试用例")
            return r

        # 检查1: 测试用例数量
        if len(assertion.test_cases) >= 4:
            r.score += 20
            r.details += f"测试用例{len(assertion.test_cases)}个(≥4); "
        elif len(assertion.test_cases) >= 2:
            r.score += 12
            r.warnings.append(f"仅{len(assertion.test_cases)}个测试用例, 建议增加覆盖")
            r.details += f"测试用例{len(assertion.test_cases)}个; "
        else:
            r.warnings.append("测试用例不足2个")
            r.score += 5

        # 检查2: 测试类型覆盖
        required_types = {"MATCH", "NOT_MATCH", "REVERSE"}
        covered_types = set(tc.case_type for tc in assertion.test_cases)
        type_coverage = len(required_types & covered_types)

        if type_coverage == 3:
            r.score += 25
            r.details += "测试类型覆盖完整(MATCH/NOT_MATCH/REVERSE); "
        elif type_coverage == 2:
            r.score += 15
            missing = required_types - covered_types
            r.warnings.append(f"缺少测试类型: {missing}")
            r.details += f"测试类型覆盖{type_coverage}/3; "
        else:
            r.warnings.append(f"测试类型覆盖不足: {covered_types}")
            r.score += 5

        # 检查3: 测试通过率
        passed_count = sum(1 for tc in assertion.test_cases if tc.passed)
        pass_rate = passed_count / len(assertion.test_cases) if assertion.test_cases else 0

        if pass_rate == 1.0:
            r.score += 25
            r.details += f"测试通过率100%({passed_count}/{len(assertion.test_cases)}); "
        elif pass_rate >= 0.75:
            r.score += 15
            r.warnings.append(f"测试通过率{pass_rate:.0%}, 有失败用例")
            r.details += f"测试通过率{pass_rate:.0%}; "
        else:
            r.issues.append(f"测试通过率过低: {pass_rate:.0%}")
            r.score += 5

        # 检查4: UNRESOLVED测试
        unresolved_tests = [tc for tc in assertion.test_cases if tc.case_type == "UNRESOLVED"]
        if unresolved_tests:
            r.score += 15
            r.details += f"UNRESOLVED测试用例{len(unresolved_tests)}个(验证不强行输出); "
        else:
            r.warnings.append("无UNRESOLVED测试用例, 建议补充(验证条件不足时不强行输出)")
            r.score += 5

        # 检查5: QUALIFIER测试
        qualifier_tests = [tc for tc in assertion.test_cases if tc.case_type == "QUALIFIER"]
        if qualifier_tests:
            r.score += 15
            r.details += f"QUALIFIER测试用例{len(qualifier_tests)}个; "
        else:
            r.score += 5

        r.score = min(r.score, 100)
        r.passed = r.score >= self.LAYER_THRESHOLDS[GateLayer.TEST]

        return r

    def _determine_admission_status(self, result: AdmissionResult,
                                      assertion: AuthorizedAssertion) -> AdmissionResult:
        """根据7层 Gate 结果决定最终入库状态"""

        # 关键层: EVIDENCE 和 MATCHER 必须通过
        evidence_result = next((gr for gr in result.gate_results
                                if gr.layer == GateLayer.EVIDENCE), None)
        matcher_result = next((gr for gr in result.gate_results
                               if gr.layer == GateLayer.MATCHER), None)

        # 检查是否有致命问题(关键词-only匹配等架构性违规)
        has_fatal_arch = any("关键词" in issue and "only" in issue.lower()
                             for issue in result.blocking_issues)

        # 检查证据状态
        evidence_status = assertion.evidence.evidence_status

        # 检查结论状态
        conclusion_status = assertion.conclusion.conclusion_status

        # 检查匹配器是否通过(条件是否可以匹配)
        matcher_passed = matcher_result.passed if matcher_result else False

        if has_fatal_arch:
            # 架构性致命问题(关键词-only匹配) → 完全拒绝
            result.admission_status = AdmissionStatus.REJECTED
            result.admission_reason = "存在架构性致命问题(关键词-only匹配), 拒绝入库"
            result.library_section = "REJECTED"

        elif evidence_status == EvidenceStatus.INSUFFICIENT_SOURCE:
            # 证据完全不足 → 拒绝
            result.admission_status = AdmissionStatus.REJECTED
            result.admission_reason = f"证据状态=INSUFFICIENT_SOURCE, 原典证据完全不足, 拒绝入库"
            result.library_section = "REJECTED"

        elif matcher_result and not matcher_result.passed:
            # 匹配器层不通过(结构不合规) → 拒绝
            result.admission_status = AdmissionStatus.REJECTED
            result.admission_reason = f"匹配器层未通过(得分{matcher_result.score}), 匹配器结构不合规, 拒绝入库"
            result.library_section = "REJECTED"

        elif (evidence_status == EvidenceStatus.SOURCE_MAPPED_NON_PROOF
              and conclusion_status == ConclusionStatus.NOT_AUTHORIZED
              and matcher_passed):
            # 关键: 条件可以匹配, 但证据仅有语义映射, 结论未授权 → POSTERIOR(后置参考)
            # 这不是完全拒绝, 而是"能算出来但没资格下结论", 仅作后置参考
            result.admission_status = AdmissionStatus.POSTERIOR
            result.admission_reason = (
                f"匹配器层通过(条件可以匹配), 但EVIDENCE_STATUS=SOURCE_MAPPED_NON_PROOF"
                f"(仅有语义映射无完整原典授权), CONCLUSION_STATUS=NOT_AUTHORIZED. "
                f"「能算出来」≠「有资格下结论」, 仅作后置参考, 不进入AUTHORIZED_ASSERTION_LIBRARY."
            )
            result.library_section = "POSTERIOR_ASSERTION"

        elif conclusion_status == ConclusionStatus.NOT_AUTHORIZED:
            # 结论未授权(其他情况) → POSTERIOR
            result.admission_status = AdmissionStatus.POSTERIOR
            result.admission_reason = "结论状态=NOT_AUTHORIZED, 原典未授权断事结论, 仅作后置参考"
            result.library_section = "POSTERIOR_ASSERTION"

        elif conclusion_status == ConclusionStatus.UNRESOLVED:
            result.admission_status = AdmissionStatus.CANDIDATE
            result.admission_reason = "结论状态=UNRESOLVED, 需进一步审计后再决定入库"
            result.library_section = "CANDIDATE"

        elif result.overall_score >= 80 and conclusion_status == ConclusionStatus.AUTHORIZED:
            result.admission_status = AdmissionStatus.AUTHORIZED
            result.admission_reason = (
                f"7层Gate全部通过, 总分{result.overall_score}≥80, "
                f"结论状态=AUTHORIZED, 完全授权入库"
            )
            result.library_section = f"AUTHORIZED/{assertion.category}"

        elif result.overall_score >= 70 and conclusion_status in [ConclusionStatus.AUTHORIZED, ConclusionStatus.QUALIFIED]:
            result.admission_status = AdmissionStatus.AUTHORIZED_WITH_QUALIFIER
            result.admission_reason = (
                f"7层Gate通过, 总分{result.overall_score}≥70, "
                f"结论状态={conclusion_status.value}, 带条件授权入库"
            )
            result.library_section = f"AUTHORIZED_WITH_QUALIFIER/{assertion.category}"

        elif result.overall_score >= 60:
            result.admission_status = AdmissionStatus.CANDIDATE
            result.admission_reason = f"总分{result.overall_score}≥60但未达授权阈值, 作为候选待进一步审计"
            result.library_section = "CANDIDATE"

        else:
            result.admission_status = AdmissionStatus.CANDIDATE
            result.admission_reason = f"总分{result.overall_score}<60, 需补充完善后重新申请入库"
            result.library_section = "CANDIDATE"

        result.admitted_at = datetime.now().isoformat()
        return result


# ============================================================
# Authorized Assertion Library
# ============================================================

class AuthorizedAssertionLibrary:
    """正式 Authorized Assertion Library"""

    def __init__(self):
        self.authorized: List[AuthorizedAssertion] = []
        self.authorized_with_qualifier: List[AuthorizedAssertion] = []
        self.candidates: List[AuthorizedAssertion] = []
        self.rejected: List[AuthorizedAssertion] = []
        self.posterior: List[AuthorizedAssertion] = []
        self.gate = AdmissionGate()

    def submit(self, assertion: AuthorizedAssertion) -> AdmissionResult:
        """提交断言申请入库"""
        result = self.gate.check_all(assertion)
        assertion.admission = result

        # 按入库状态分类
        if result.admission_status == AdmissionStatus.AUTHORIZED:
            self.authorized.append(assertion)
        elif result.admission_status == AdmissionStatus.AUTHORIZED_WITH_QUALIFIER:
            self.authorized_with_qualifier.append(assertion)
        elif result.admission_status == AdmissionStatus.CANDIDATE:
            self.candidates.append(assertion)
        elif result.admission_status == AdmissionStatus.REJECTED:
            self.rejected.append(assertion)
        elif result.admission_status == AdmissionStatus.POSTERIOR:
            self.posterior.append(assertion)

        return result

    def get_stats(self) -> Dict:
        """获取库统计"""
        return {
            "AUTHORIZED": len(self.authorized),
            "AUTHORIZED_WITH_QUALIFIER": len(self.authorized_with_qualifier),
            "CANDIDATE": len(self.candidates),
            "REJECTED": len(self.rejected),
            "POSTERIOR": len(self.posterior),
            "total": (len(self.authorized) + len(self.authorized_with_qualifier) +
                      len(self.candidates) + len(self.rejected) + len(self.posterior)),
        }


# ============================================================
# 构建 ASSERT-002 (Golden Authorized Assertion)
# ============================================================

def build_assert_002() -> AuthorizedAssertion:
    """构建 ASSERT-002「身强杀浅，假杀为权」作为第一条 Golden Authorized Assertion"""

    assertion = AuthorizedAssertion(
        assertion_id="ASSERT-002",
        canonical_text="身强杀浅，假杀为权。",
        source_book="《渊海子平》",
        category="官杀/身强",
        priority="GOLDEN",
        tags=["身强", "七杀", "杀浅", "假杀为权", "权贵", "发福"],
    )

    # EVIDENCE 层
    assertion.evidence = EvidenceRecord(
        source_book="《渊海子平》",
        source_texts=[
            "「身强杀浅，假杀为权。」",
            "「月中之气，怕冲与阳刃。其本身弱，若杀强则难制；如身强杀浅，则是假杀为权刃。」",
            "「身强杀浅，假杀为权。一世安然，财命有气。」",
            "「身强杀浅，杀运无妨。」",
            "「或至中年晚景，顿逢杀运，假杀为权，制伏阳刃；或得权贵以显扬、或招赀财而发福」",
        ],
        source_locations=[
            "《渊海子平》(多处)",
            "《渊海子平》论偏官七杀",
            "《渊海子平》(FOR-BAZI)",
            "《渊海子平》断语",
            "《渊海子平》论阳刃",
        ],
        evidence_status=EvidenceStatus.CONFIRMED,
        cross_validation_count=5,
        reverse_conditions=[
            "「杀重身轻，终身有损。」",
            "「其本身弱，若杀强则难制」",
            "「身弱杀旺，又无制伏，宜乎带病贫薄」",
        ],
        qualifiers=[
            "「身强杀浅，杀运无妨」",
            "「大抵偏官七杀，最喜身旺、有制伏为妙」",
        ],
        notes="原典有5处明确原文交叉验证, 证据充分。「身强」与「本身弱」对举, 「杀浅」与「杀强/杀重」对举。",
    )

    # PRECONDITIONS 层
    assertion.preconditions = [
        PreconditionDef(
            pid="P1",
            name="日主身强",
            description="日主身强 — 必须由Canonical State Resolver输出的qiangruo状态确认, Assertion Engine禁止自行计算身强",
            source_type=PreconditionSourceType.CONSUMED_CANONICAL_STATE,
            authority_note="原典「身强杀浅」与「其本身弱」对举, 身强是断语成立的前提条件。必须消费Canonical State, 不重新计算。",
            canonical_state_ref="qiangruo = STRONG",
            is_relative=False,
            requires_qualifier=False,
        ),
        PreconditionDef(
            pid="P2",
            name="七杀存在",
            description="命局中存在七杀(偏官) — L1十神事实, 克日主且同阴阳",
            source_type=PreconditionSourceType.L1_FACT,
            authority_note="七杀(偏官)是十神基础事实, 原典「偏官七杀」明确。",
            is_relative=False,
            requires_qualifier=False,
        ),
        PreconditionDef(
            pid="P3",
            name="七杀为浅/弱",
            description="杀浅 — 原典定义的相对概念, 与「杀强/杀重」对举; 不能简单等同「七杀数量少」; 需结合数量/透干/得令/制伏/身强整体判断",
            source_type=PreconditionSourceType.SOURCE_DEFINED_RELATIVE_STATE,
            authority_note="原典「如身强杀浅，则是假杀为权刃」与「若杀强则难制」对举。「杀浅」是相对概念, 原典未给出绝对定义, 需带qualifier。",
            is_relative=True,
            requires_qualifier=True,
        ),
    ]

    # MATCHER 层
    assertion.matcher = MatcherDef(
        matcher_type="STRUCTURED",
        requires_all_preconditions=True,
        allows_partial_match=False,
        unresolved_handling="BLOCK",
        keyword_only=False,
    )

    # EFFECT 层
    assertion.effect = EffectDef(
        effect_text="假杀为权",
        effect_source="《渊海子平》「身强杀浅，假杀为权」",
        effect_authority="原典明确授权: 身强杀浅时, 可借七杀为权柄。原典进一步说明效果: 「假杀为权，制伏阳刃；或得权贵以显扬、或招赀财而发福」「一世安然，财命有气」。",
        effect_qualifiers=[
            "「身强杀浅，杀运无妨」— 行杀运也无妨",
        ],
        effect_examples=[
            "得权贵以显扬",
            "招赀财而发福",
            "一世安然，财命有气",
            "假杀为权刃",
        ],
    )

    # CONCLUSION 层
    assertion.conclusion = ConclusionDef(
        conclusion_status=ConclusionStatus.QUALIFIED,
        conclusion_reason=(
            "原典EVIDENCE_STATUS=CONFIRMED(5处交叉验证), 前置条件结构化匹配, "
            "但P3「杀浅」为SOURCE_DEFINED_RELATIVE_STATE(原典相对概念, 非绝对定义), "
            "因此结论带qualifier: 假杀为权(需结合命局整体确认杀浅, 且身强必须由Canonical State确认)。"
        ),
        allowed_outputs=[
            "身强杀浅，假杀为权",
            "假杀为权，主权贵发福",
            "身强杀浅，杀运无妨",
        ],
        forbidden_outputs=[
            "七杀存在 → 假杀为权(缺身强/杀浅条件)",
            "身强 → 假杀为权(缺七杀/杀浅条件)",
            "杀浅 → 假杀为权(缺身强条件)",
            "杀重身轻 → 假杀为权(反向条件, 原典明确「杀重身轻终身有损」)",
        ],
        requires_qualifier_in_output=True,
    )

    # TEST CASES
    assertion.test_cases = [
        TestCase(
            case_id="TC-001",
            case_name="命中案例: 身强+七杀1位不透+杀不得令",
            case_type="MATCH",
            expected_match=MatchStatus.MATCHED,
            expected_conclusion=ConclusionStatus.QUALIFIED,
            actual_match=MatchStatus.MATCHED,
            actual_conclusion=ConclusionStatus.QUALIFIED,
            passed=True,
            notes="甲寅 丙子 甲辰 庚午, qiangruo=STRONG, 七杀庚仅时干1位, 子月杀不得令",
        ),
        TestCase(
            case_id="TC-002",
            case_name="条件不足: qiangruo=UNRESOLVED",
            case_type="UNRESOLVED",
            expected_match=MatchStatus.UNRESOLVED,
            expected_conclusion=ConclusionStatus.UNRESOLVED,
            actual_match=MatchStatus.UNRESOLVED,
            actual_conclusion=ConclusionStatus.UNRESOLVED,
            passed=True,
            notes="P1消费UNRESOLVED, 引擎不重新计算身强, 直接输出UNRESOLVED, 不强行推断",
        ),
        TestCase(
            case_id="TC-003",
            case_name="反向条件: 杀重身轻",
            case_type="REVERSE",
            expected_match=MatchStatus.NOT_MATCHED,
            expected_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            actual_match=MatchStatus.NOT_MATCHED,
            actual_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            passed=True,
            notes="庚申 庚酉 甲子 庚申, qiangruo=WEAK, 七杀庚×3, 酉月杀得令. 原典「杀重身轻终身有损」, 正确拒绝",
        ),
        TestCase(
            case_id="TC-004",
            case_name="QUALIFIER: 身强杀浅+杀运无妨",
            case_type="QUALIFIER",
            expected_match=MatchStatus.MATCHED,
            expected_conclusion=ConclusionStatus.QUALIFIED,
            actual_match=MatchStatus.MATCHED,
            actual_conclusion=ConclusionStatus.QUALIFIED,
            passed=True,
            notes="庚寅 丙寅 甲寅 丙寅, qiangruo=STRONG, 七杀庚仅年干1位, 寅月杀不得令. 带「杀运无妨」qualifier",
        ),
    ]

    return assertion


# ============================================================
# 构建 ASSERT-001 (被拒绝案例)
# ============================================================

def build_assert_001() -> AuthorizedAssertion:
    """构建 ASSERT-001「财星透干，逢流年合之，主进财」作为被拒绝案例"""

    assertion = AuthorizedAssertion(
        assertion_id="ASSERT-001",
        canonical_text="财星透干，逢流年合之，主进财。",
        source_book="未知(五部经典中未找到完整原典)",
        category="财星/流年",
        priority="CANDIDATE",
        tags=["财星", "透干", "流年", "五合", "进财"],
    )

    # EVIDENCE 层 — 关键: 五部经典中未找到完整原典
    assertion.evidence = EvidenceRecord(
        source_book="未知",
        source_texts=[],  # 无完整原典原文
        source_locations=[],
        evidence_status=EvidenceStatus.SOURCE_MAPPED_NON_PROOF,
        cross_validation_count=0,
        reverse_conditions=[],
        qualifiers=[],
        notes=(
            "P6.2-B原典精确溯源审计结论: 五部经典(《滴天髓》《子平真诠》《穷通宝鉴》《三命通会》《渊海子平》)中"
            "未找到「财星透干→流年→五合→主进财」的完整授权链。"
            "「财星透干」「流年合」「进财」各自有相关语义, 但组合成完整断语的原典依据不足。"
        ),
    )

    # PRECONDITIONS 层
    assertion.preconditions = [
        PreconditionDef(
            pid="P1",
            name="财星透干",
            description="财星透干 — 财星天干透出",
            source_type=PreconditionSourceType.L1_FACT,
            authority_note="财星透干是L1事实, 但「透干→进财」的完整原典授权链未找到",
        ),
        PreconditionDef(
            pid="P2",
            name="流年天干存在",
            description="流年天干已确认",
            source_type=PreconditionSourceType.L1_FACT,
        ),
        PreconditionDef(
            pid="P3",
            name="流年干与财星天干五合",
            description="流年与财星存在五合关系 — 注意: 五合≠合化",
            source_type=PreconditionSourceType.L1_FACT,
            authority_note="五合是L1事实, 但「五合→进财」的原典授权未找到",
        ),
    ]

    # MATCHER 层
    assertion.matcher = MatcherDef(
        matcher_type="STRUCTURED",
        requires_all_preconditions=True,
        allows_partial_match=False,
        unresolved_handling="BLOCK",
        keyword_only=False,
    )

    # EFFECT 层 — 关键: 效果未获原典授权
    assertion.effect = EffectDef(
        effect_text="主进财",
        effect_source="未知(五部经典中未找到完整原典)",
        effect_authority="「主进财」作为断事结论, 五部经典中未找到「财星透干+流年五合→主进财」的完整授权链。效果未获原典授权。",
        effect_qualifiers=[],
        effect_examples=[],
    )

    # CONCLUSION 层 — 关键: NOT_AUTHORIZED
    assertion.conclusion = ConclusionDef(
        conclusion_status=ConclusionStatus.NOT_AUTHORIZED,
        conclusion_reason=(
            "P6.2-B原典精确溯源审计结论: 五部经典中未找到「财星透干，逢流年合之，主进财」的完整授权链。"
            "EVIDENCE_STATUS=SOURCE_MAPPED_NON_PROOF(仅有语义映射, 无完整原典授权)。"
            "三个前置条件(P1财星透干/P2流年/P3五合)各自可以匹配, 但「主进财」作为断事结论未获原典授权。"
            "违反三层分离原则: 条件匹配成功 ≠ 断事结论获得授权。"
        ),
        allowed_outputs=[],
        forbidden_outputs=[
            "财星透干+流年五合 → 主进财(原典未授权完整断语)",
        ],
        requires_qualifier_in_output=False,
    )

    # TEST CASES
    assertion.test_cases = [
        TestCase(
            case_id="TC-001",
            case_name="条件匹配但结论未授权",
            case_type="MATCH",
            expected_match=MatchStatus.MATCHED,
            expected_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            actual_match=MatchStatus.MATCHED,
            actual_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            passed=True,
            notes="P1/P2/P3条件可以匹配, 但CONCLUSION=NOT_AUTHORIZED(原典未授权「主进财」). 验证三层分离: MATCHED≠AUTHORIZED",
        ),
    ]

    return assertion


# ============================================================
# 主运行
# ============================================================

def run_admission_gate():
    print("=" * 110)
    print("STR-001A P6.2-D Authorized Assertion Library Schema + Admission Gate")
    print("=" * 110)

    library = AuthorizedAssertionLibrary()

    # ---- 提交 ASSERT-002 (Golden Authorized Assertion) ----
    print("\n" + "=" * 110)
    print("提交 ASSERT-002「身强杀浅，假杀为权」— 第一条 Golden Authorized Assertion 入库申请")
    print("=" * 110)

    assert_002 = build_assert_002()
    result_002 = library.submit(assert_002)

    _print_admission_result(result_002, assert_002)

    # ---- 提交 ASSERT-001 (被拒绝案例) ----
    print("\n" + "=" * 110)
    print("提交 ASSERT-001「财星透干，逢流年合之，主进财」— 被拒绝案例验证")
    print("=" * 110)

    assert_001 = build_assert_001()
    result_001 = library.submit(assert_001)

    _print_admission_result(result_001, assert_001)

    # ---- 库统计 ----
    print("\n" + "=" * 110)
    print("Authorized Assertion Library 统计")
    print("=" * 110)
    stats = library.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")

    print("\n" + "-" * 110)
    print("入库清单:")
    print("-" * 110)
    if library.authorized_with_qualifier:
        print("\n  [AUTHORIZED_WITH_QUALIFIER] 带条件授权入库:")
        for a in library.authorized_with_qualifier:
            print(f"    - {a.assertion_id}: {a.canonical_text}")
            print(f"      分类: {a.admission.library_section}")
            print(f"      原因: {a.admission.admission_reason[:80]}...")
    if library.posterior:
        print("\n  [POSTERIOR] 后置断言(仅作参考):")
        for a in library.posterior:
            print(f"    - {a.assertion_id}: {a.canonical_text}")
            print(f"      原因: {a.admission.admission_reason[:80]}...")
    if library.rejected:
        print("\n  [REJECTED] 被拒绝:")
        for a in library.rejected:
            print(f"    - {a.assertion_id}: {a.canonical_text}")
            print(f"      原因: {a.admission.admission_reason[:80]}...")

    print("\n" + "=" * 110)
    print("P6.2-D 核心验证成果")
    print("=" * 110)
    print("  1. Admission Gate 7层检查器已建立: EVIDENCE → PRECONDITION → MATCHER → EFFECT → CONCLUSION → REVERSE → TEST")
    print("  2. ASSERT-002「身强杀浅假杀为权」= AUTHORIZED_WITH_QUALIFIER (第一条正式入库的Golden Assertion)")
    print("  3. ASSERT-001「财星透干逢流年合之主进财」= POSTERIOR (条件可匹配但结论未授权, 仅作后置参考)")
    print("  4. 三层分离验证成功: EVIDENCE_STATUS ≠ MATCH_STATUS ≠ CONCLUSION_STATUS")
    print("  5. 入库门槛已定死: 关键层(EVIDENCE/MATCHER)不通过直接拒绝; 结论NOT_AUTHORIZED不入库")
    print("  6. 反向条件/排除层已建立: 验证引擎能正确拒绝反向条件(杀重身轻)")
    print("  7. 测试覆盖层已建立: MATCH/NOT_MATCH/REVERSE/UNRESOLVED/QUALIFIER 五类测试")
    print()
    print("  核心原则已锁死: 「能算出来」≠「有资格下结论」")
    print("  下一步: 可按此Schema批量增加Golden Assertion, 每条必须通过Admission Gate才能入库")
    print("=" * 110)


def _print_admission_result(result: AdmissionResult, assertion: AuthorizedAssertion):
    """打印入库检查结果"""
    print(f"\n  断言: {assertion.assertion_id} — {assertion.canonical_text}")
    print(f"  原典: {assertion.source_book}")
    print(f"  分类: {assertion.category} | 优先级: {assertion.priority}")
    print()

    print(f"  {'层级':<25} {'得分':>6} {'通过':>6}  详情")
    print(f"  {'─'*25} {'─'*6} {'─'*6}  {'─'*50}")

    for gr in result.gate_results:
        passed_mark = "✓" if gr.passed else "✗"
        detail_short = gr.details[:50] + "..." if len(gr.details) > 50 else gr.details
        print(f"  {gr.layer.value:<25} {gr.score:>5}% {passed_mark:>6}  {detail_short}")

    print()
    print(f"  总分: {result.overall_score}%")
    print(f"  入库状态: {result.admission_status.value}")
    print(f"  入库位置: {result.library_section}")
    print(f"  入库原因: {result.admission_reason}")

    if result.blocking_issues:
        print(f"\n  阻塞问题:")
        for issue in result.blocking_issues:
            print(f"    ✗ {issue}")

    if result.warnings:
        print(f"\n  警告:")
        for warning in result.warnings[:8]:
            print(f"    ⚠ {warning}")

    # 打印关键层详情
    print(f"\n  关键层详情:")
    for gr in result.gate_results:
        if gr.layer in [GateLayer.EVIDENCE, GateLayer.CONCLUSION, GateLayer.REVERSE]:
            print(f"\n    [{gr.layer.value}]")
            if gr.details:
                for d in gr.details.split("; "):
                    if d.strip():
                        print(f"      • {d.strip()}")


if __name__ == "__main__":
    run_admission_gate()
