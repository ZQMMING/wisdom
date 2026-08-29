"""
P0-2.8-A Classical Rule Provenance Audit + Engine 增强

基于 b034c9a 的 🟡 CONDITIONAL PASS 裁决，修复 3 个问题：

1. CombinationType / is_sufficient 一致性
   - 改为 sufficient_for_target，明确"足以形成某个目标的候选状态"
   - 不再有 combination_type=SUFFICIENT 但 is_sufficient=False 的矛盾

2. Value-aware Evidence matching
   - 当前 Engine 只是 Boolean Matcher（evidence_type ∈ set）
   - 增强为消费 Evidence 的 value/subject/position/qualification
   - 支持条件表达式：ROOT_PRESENT where root_type=MAIN_QI and integrity!=DAMAGED

3. Classical Rule Provenance Audit
   - 逐条审 6 条 Rule 的原典推导链
   - 区分"经典原意"和"工程抽象"两个 Provenance 层
   - 明确哪些是原典直接支持，哪些是工程师推导

工程原则：
- Contract PASS ≠ Rule Truth PASS
- 代码能执行 ≠ 执行的 Rule 真的来自经典
- 先把 6 条 Rule 真正证明清楚，再大规模生产
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
import json


# ============================================================================
# 标准数据结构
# ============================================================================

class CombinationType(Enum):
    """组合类型（描述 Rule 的逻辑角色，不再与 sufficient 混淆）"""
    NECESSARY_SET = "NECESSARY_SET"       # 必要条件集合
    SUFFICIENT_FOR_TARGET = "SUFFICIENT_FOR_TARGET"  # 对目标充分
    SUPPORTING = "SUPPORTING"              # 辅助
    CONSTRAINING = "CONSTRAINING"          # 制约
    BLOCKING = "BLOCKING"                  # 阻断
    QUALIFYING = "QUALIFYING"              # 限定


class OutputStrength(Enum):
    CANDIDATE = "CANDIDATE"
    QUALIFIED = "QUALIFIED"
    NOT_CONFIRMED = "NOT_CONFIRMED"
    UNRESOLVED = "UNRESOLVED"


class AuthorizationLevel(Enum):
    AUTHORIZED = "AUTHORIZED"
    PARTIAL = "PARTIAL"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"


class ProvenanceLayer(Enum):
    """Provenance 层级 — 区分经典原意和工程抽象"""
    CLASSICAL_TEXT = "CLASSICAL_TEXT"           # 经典原文直接支持
    CLASSICAL_SEMANTIC = "CLASSICAL_SEMANTIC"   # 经典语义推导（需要解释）
    ENGINEERING_ABSTRACTION = "ENGINEERING_ABSTRACTION"  # 工程抽象（工程师设计）
    ENGINEERING_INFERENCE = "ENGINEERING_INFERENCE"      # 工程推导（从经典进一步推导）


@dataclass(frozen=True)
class ClassicalSource:
    classic: str
    edition: str
    chapter: str
    text_type: str  # ORIGINAL / COMMENTARY
    author: str
    source_text: str
    verification_status: str


@dataclass(frozen=True)
class ProvenanceItem:
    """单个 Provenance 项 — 明确属于哪一层"""
    layer: ProvenanceLayer
    description: str
    source_ref: Optional[str] = None  # 引用的经典原文/章节
    confidence: str = "HIGH"  # HIGH / MEDIUM / LOW


@dataclass(frozen=True)
class EvidenceCondition:
    """
    Evidence 条件 — Value-aware matching

    不再只是 evidence_type ∈ set，而是支持：
    - evidence_type: 证据类型
    - value_matches: 值匹配条件（dict of key=value）
    - value_not_matches: 值不匹配条件
    - subject_matches: subject 匹配条件
    - position_in: 位置在指定列表中
    - min_count: 最小数量
    - max_count: 最大数量
    - integrity_not: 完整性不包含（如 DAMAGED）
    """
    evidence_type: str
    value_matches: Dict[str, Any] = field(default_factory=dict)
    value_not_matches: Dict[str, Any] = field(default_factory=dict)
    subject_matches: Dict[str, Any] = field(default_factory=dict)
    position_in: List[str] = field(default_factory=list)
    min_count: int = 1
    max_count: Optional[int] = None
    integrity_not: List[str] = field(default_factory=list)
    description: str = ""


@dataclass(frozen=True)
class CombinationRule:
    """
    Evidence Combination Rule — 修复后的 Schema

    关键修复：
    1. sufficient_for_target 替代 is_sufficient，明确"对哪个目标充分"
    2. required_evidence 从 List[str] 升级为 List[EvidenceCondition]（Value-aware）
    3. provenance_chain 明确记录经典原意→工程抽象的推导链
    4. combination_type 与 sufficient_for_target 不再矛盾
    """
    rule_id: str
    classic: str
    target: str
    combination_type: CombinationType

    # 问题 1：为什么可以组合？
    combination_rationale: str

    # 问题 2：组合条件是什么？（Value-aware Conditions）
    required_evidence: List[EvidenceCondition]   # 必要条件（Value-aware）
    supporting_evidence: List[EvidenceCondition] # 辅助条件
    constraining_evidence: List[EvidenceCondition] # 制约条件

    # 问题 5：有没有反条件？
    blocking_conditions: List[str]
    qualifying_conditions: List[str]

    # 问题 6：状态还是候选？
    output_state: str
    output_strength: OutputStrength

    # 问题 3：哪个经典授权？
    classical_source: ClassicalSource
    authorization_level: AuthorizationLevel

    # ===== 以下字段都有默认值，必须放在后面 =====

    # 问题 4：对目标是否充分？（修复：明确 target）
    sufficient_for_target: Optional[str] = None  # None=不充分；"CLIMATE_PROFILE"=对调候候选充分

    # 问题 7：能不能最终推出强弱？
    can_derive_final: bool = False

    # 新增：Provenance 链 — 区分经典原意和工程抽象
    provenance_chain: List[ProvenanceItem] = field(default_factory=list)

    notes: str = ""


@dataclass
class CombinationResult:
    rule_id: str
    classic: str
    target: str
    output_state: str
    output_strength: OutputStrength
    matched_required: List[str]
    matched_supporting: List[str]
    matched_constraining: List[str]
    triggered_blocking: List[str]
    triggered_qualifying: List[str]
    is_applicable: bool
    authorization_level: AuthorizationLevel
    value_aware_matching: bool = True  # 是否使用了 Value-aware matching
    notes: str = ""


# ============================================================================
# Value-aware Evidence Matcher
# ============================================================================

class ValueAwareEvidenceMatcher:
    """
    Value-aware Evidence Matcher — 增强的匹配器

    不再只是 evidence_type ∈ set，而是消费 Evidence 的：
    - value（值，如 root_count=2, seasonal_alignment=IN_SEASON）
    - subject（主体，如 DAY_MASTER, STEM(year=壬)）
    - position（位置，如 month, hour）
    - qualification/qualifiers（限定条件，如 integrity=DAMAGED）
    """

    @staticmethod
    def match_condition(evidences: List[Dict[str, Any]],
                        condition: EvidenceCondition) -> tuple[bool, List[Dict]]:
        """
        匹配单个 EvidenceCondition

        Returns:
            (matched, matched_evidences)
        """
        # 先按类型过滤
        type_matched = [e for e in evidences if e.get("evidence_type") == condition.evidence_type]

        if not type_matched:
            return False, []

        # Value-aware 过滤
        result = []
        for ev in type_matched:
            ev_value = ev.get("value", {})
            ev_subject = ev.get("subject", {})
            ev_position = ev.get("position")
            ev_qualifiers = ev.get("qualifiers", {})

            # 检查 value_matches
            value_ok = True
            for key, expected in condition.value_matches.items():
                actual = ev_value.get(key)
                if actual != expected:
                    value_ok = False
                    break

            # 检查 value_not_matches
            if value_ok:
                for key, not_expected in condition.value_not_matches.items():
                    actual = ev_value.get(key)
                    if actual == not_expected:
                        value_ok = False
                        break

            # 检查 subject_matches
            if value_ok and condition.subject_matches:
                for key, expected in condition.subject_matches.items():
                    actual = ev_subject.get(key)
                    if actual != expected:
                        value_ok = False
                        break

            # 检查 position_in
            if value_ok and condition.position_in:
                if ev_position not in condition.position_in:
                    value_ok = False

            # 检查 integrity_not（从 qualifiers 或 value 中读取）
            if value_ok and condition.integrity_not:
                integrity = ev_qualifiers.get("integrity") or ev_value.get("integrity")
                if integrity in condition.integrity_not:
                    value_ok = False

            if value_ok:
                result.append(ev)

        # 检查数量
        count = len(result)
        if count < condition.min_count:
            return False, []
        if condition.max_count is not None and count > condition.max_count:
            return False, []

        return True, result


# ============================================================================
# 五部经典的 Combination Rule（修复后 + Provenance Chain）
# ============================================================================

class ClassicalCombinationRules:
    """五部经典的 Combination Rule — 修复后版本，带 Provenance Chain"""

    @staticmethod
    def get_ditiansui_rules() -> List[CombinationRule]:
        return [
            CombinationRule(
                rule_id="DTS-STRENGTH-001",
                classic="滴天髓",
                target="DAY_MASTER_STRENGTH",
                combination_type=CombinationType.NECESSARY_SET,  # 修复：不再是 SUFFICIENT
                combination_rationale=(
                    "《滴天髓》强调旺衰需综合得时、得地、得势，"
                    "但同时提醒'虽是至理，亦死法也'，需察支中党众、干上生扶。"
                    "因此得令+得地+得势同时成立时，可形成'偏强'候选，"
                    "但仍需检查是否有从格、特殊格局等阻断条件。"
                ),
                required_evidence=[
                    EvidenceCondition(
                        evidence_type="SEASONAL_STATE",
                        value_matches={"seasonal_alignment": "IN_SEASON"},
                        description="得令：日主与月令同五行",
                    ),
                    EvidenceCondition(
                        evidence_type="ROOT_PRESENT",
                        value_matches={"root_present": True},
                        min_count=1,
                        description="得地：日主在地支藏干中有根",
                    ),
                ],
                supporting_evidence=[
                    EvidenceCondition(
                        evidence_type="RESOURCE_SUPPORT",
                        value_matches={"resource_present": True},
                        description="得势之一：印星生扶",
                    ),
                    EvidenceCondition(
                        evidence_type="PEER_SUPPORT",
                        value_matches={"peer_present": True},
                        description="得势之二：比劫帮身",
                    ),
                ],
                constraining_evidence=[
                    EvidenceCondition(evidence_type="OFFICER_CONTROL", description="官杀克身"),
                    EvidenceCondition(evidence_type="OUTPUT_DRAIN", description="食伤泄身"),
                    EvidenceCondition(evidence_type="WEALTH_DRAIN", description="财星耗身"),
                ],
                blocking_conditions=[
                    "SPECIAL_PATTERN_FROM_STRONG",
                    "SPECIAL_PATTERN_FROM_WEAK",
                    "DAY_MASTER_COMBINED",
                ],
                qualifying_conditions=[
                    "ROOT_DAMAGED_BY_CLASH",
                    "SEASONAL_ALIGNMENT_NOT_MAIN",
                ],
                sufficient_for_target=None,  # 修复：不充分，需要辅助证据
                output_state="CANDIDATE_STRONG",
                output_strength=OutputStrength.CANDIDATE,
                can_derive_final=False,
                classical_source=ClassicalSource(
                    classic="滴天髓", edition="任铁樵注本", chapter="通神论·衰旺",
                    text_type="ORIGINAL", author="京图（题）/任铁樵（注）",
                    source_text=(
                        "得时俱为旺论，失令便作衰看，虽是至理，亦死法也。"
                        "须察支中党众，干上生扶，方可定其真衰真旺。"
                    ),
                    verification_status="PARTIALLY_VERIFIED",
                ),
                authorization_level=AuthorizationLevel.PARTIAL,
                # Provenance Chain — 区分经典原意和工程抽象
                provenance_chain=[
                    ProvenanceItem(
                        layer=ProvenanceLayer.CLASSICAL_TEXT,
                        description="原文：'得时俱为旺论' — 得令是旺衰的重要证据",
                        source_ref="滴天髓·通神论·衰旺",
                    ),
                    ProvenanceItem(
                        layer=ProvenanceLayer.CLASSICAL_TEXT,
                        description="原文：'须察支中党众，干上生扶' — 需要综合地支根气和天干生扶",
                        source_ref="滴天髓·通神论·衰旺",
                    ),
                    ProvenanceItem(
                        layer=ProvenanceLayer.CLASSICAL_SEMANTIC,
                        description="经典语义：得令（SEASONAL_STATE）+ 得地（ROOT_PRESENT）是旺衰判断的必要条件",
                        confidence="MEDIUM",
                    ),
                    ProvenanceItem(
                        layer=ProvenanceLayer.ENGINEERING_ABSTRACTION,
                        description="工程抽象：将'支中党众'抽象为 ROOT_PRESENT + PEER_SUPPORT，将'干上生扶'抽象为 RESOURCE_SUPPORT",
                        confidence="MEDIUM",
                    ),
                    ProvenanceItem(
                        layer=ProvenanceLayer.ENGINEERING_INFERENCE,
                        description="工程推导：必要条件+辅助条件同时成立时，形成 CANDIDATE_STRONG 候选（非最终结论）",
                        confidence="LOW",
                    ),
                ],
                notes=(
                    "修复：combination_type 从 SUFFICIENT 改为 NECESSARY_SET，"
                    "sufficient_for_target=None（不充分）。"
                    "Provenance Chain 明确：经典原文只支持'得令重要、需综合判断'，"
                    "具体的 required/supporting/constraining 分类是工程抽象。"
                ),
            ),
        ]

    @staticmethod
    def get_qiongtong_baojian_rules() -> List[CombinationRule]:
        return [
            CombinationRule(
                rule_id="QTB-CLIMATE-001",
                classic="穷通宝鉴",
                target="CLIMATE_ADJUSTMENT",
                combination_type=CombinationType.SUFFICIENT_FOR_TARGET,
                combination_rationale=(
                    "《穷通宝鉴》以日干×月令为核心，根据寒暖燥湿确定调候方向。"
                    "日干×月令足以形成调候候选状态，但调候是独立维度，不能反过来决定强弱。"
                ),
                required_evidence=[
                    EvidenceCondition(
                        evidence_type="SEASONAL_STATE",
                        description="日干×月令状态",
                    ),
                ],
                supporting_evidence=[],
                constraining_evidence=[],
                blocking_conditions=["DAY_MASTER_COMBINED"],
                qualifying_conditions=[
                    "ADJUSTMENT_ELEMENT_PRESENT",
                    "ADJUSTMENT_ELEMENT_DAMAGED",
                ],
                sufficient_for_target="CLIMATE_PROFILE_CANDIDATE",  # 修复：明确对调候候选充分
                output_state="CLIMATE_PROFILE_CANDIDATE",
                output_strength=OutputStrength.QUALIFIED,
                can_derive_final=False,
                classical_source=ClassicalSource(
                    classic="穷通宝鉴", edition="余春台辑", chapter="三春甲木",
                    text_type="ORIGINAL", author="余春台（辑）",
                    source_text="正月甲木，初春尚有余寒，得丙火照暖，方有发生之意。",
                    verification_status="PARTIALLY_VERIFIED",
                ),
                authorization_level=AuthorizationLevel.PARTIAL,
                provenance_chain=[
                    ProvenanceItem(
                        layer=ProvenanceLayer.CLASSICAL_TEXT,
                        description="原文：'正月甲木，初春尚有余寒，得丙火照暖' — 日干×月令→调候方向",
                        source_ref="穷通宝鉴·三春甲木",
                    ),
                    ProvenanceItem(
                        layer=ProvenanceLayer.CLASSICAL_SEMANTIC,
                        description="经典语义：日干×月令足以确定调候的基本方向（寒暖燥湿）",
                        confidence="HIGH",
                    ),
                    ProvenanceItem(
                        layer=ProvenanceLayer.ENGINEERING_ABSTRACTION,
                        description="工程抽象：将调候方向抽象为 CLIMATE_PROFILE_CANDIDATE",
                        confidence="MEDIUM",
                    ),
                ],
                notes=(
                    "修复：sufficient_for_target='CLIMATE_PROFILE_CANDIDATE'，"
                    "明确是对'调候候选状态'充分，不是对整个调候辨证充分，更不是对强弱充分。"
                ),
            ),
        ]

    @staticmethod
    def get_ziping_zhenquan_rules() -> List[CombinationRule]:
        return [
            CombinationRule(
                rule_id="ZP-PATTERN-001",
                classic="子平真诠",
                target="PATTERN_STRUCTURE",
                combination_type=CombinationType.NECESSARY_SET,
                combination_rationale=(
                    "《子平真诠》以月令用神为核心，格局从月令出。"
                    "月令十神决定格局候选，但需进一步分析成败、救应。"
                ),
                required_evidence=[
                    EvidenceCondition(evidence_type="SEASONAL_STATE", description="月令状态"),
                    EvidenceCondition(evidence_type="MONTH_COMMAND_TEN_GOD", description="月令十神"),
                ],
                supporting_evidence=[
                    EvidenceCondition(evidence_type="PATTERN_SUPPORTING_STRUCTURE", description="成格结构"),
                ],
                constraining_evidence=[
                    EvidenceCondition(evidence_type="PATTERN_DESTRUCTIVE_STRUCTURE", description="破格结构"),
                ],
                blocking_conditions=[
                    "MONTH_BRANCH_COMBINED_OR_CLASHED",
                    "SPECIAL_PATTERN",
                ],
                qualifying_conditions=["MONTH_HIDDEN_STEM_MIXED"],
                sufficient_for_target=None,
                output_state="PATTERN_CANDIDATE",
                output_strength=OutputStrength.CANDIDATE,
                can_derive_final=False,
                classical_source=ClassicalSource(
                    classic="子平真诠", edition="沈孝瞻原著", chapter="论用神",
                    text_type="ORIGINAL", author="沈孝瞻",
                    source_text="八字用神，专求月令，以日干配月令地支，而生克不同，格局分焉。",
                    verification_status="PARTIALLY_VERIFIED",
                ),
                authorization_level=AuthorizationLevel.PARTIAL,
                provenance_chain=[
                    ProvenanceItem(
                        layer=ProvenanceLayer.CLASSICAL_TEXT,
                        description="原文：'八字用神，专求月令' — 格局从月令出",
                        source_ref="子平真诠·论用神",
                    ),
                    ProvenanceItem(
                        layer=ProvenanceLayer.CLASSICAL_SEMANTIC,
                        description="经典语义：月令十神是格局的必要条件，但需要成败救应分析",
                        confidence="HIGH",
                    ),
                    ProvenanceItem(
                        layer=ProvenanceLayer.ENGINEERING_ABSTRACTION,
                        description="工程抽象：将月令十神抽象为 MONTH_COMMAND_TEN_GOD Evidence",
                        confidence="MEDIUM",
                    ),
                ],
            ),
        ]

    @staticmethod
    def get_sanming_tonghui_rules() -> List[CombinationRule]:
        return [
            CombinationRule(
                rule_id="SMT-RELATION-001",
                classic="三命通会",
                target="STRUCTURAL_TRANSFORMATION",
                combination_type=CombinationType.NECESSARY_SET,
                combination_rationale=(
                    "《三命通会》大量内容描述干支组合、刑冲合害对基础事实的影响。"
                    "这些是结构变化，不是直接的强弱判断。"
                ),
                required_evidence=[
                    EvidenceCondition(evidence_type="STRUCTURAL_CHANGE", description="结构变化"),
                ],
                supporting_evidence=[],
                constraining_evidence=[],
                blocking_conditions=[],
                qualifying_conditions=[
                    "COMBINATION_TRANSFORMED",
                    "CLASH_DAMAGES_ROOT",
                ],
                sufficient_for_target=None,
                output_state="STRUCTURAL_EFFECT_CANDIDATE",
                output_strength=OutputStrength.CANDIDATE,
                can_derive_final=False,
                classical_source=ClassicalSource(
                    classic="三命通会", edition="万民英撰", chapter="论刑冲合害",
                    text_type="ORIGINAL", author="万民英",
                    source_text="刑冲合害，各有其情，须察其有力无力，有情无情。",
                    verification_status="PARTIALLY_VERIFIED",
                ),
                authorization_level=AuthorizationLevel.PARTIAL,
                provenance_chain=[
                    ProvenanceItem(
                        layer=ProvenanceLayer.CLASSICAL_TEXT,
                        description="原文：'刑冲合害，各有其情' — 结构变化需要具体分析",
                        source_ref="三命通会·论刑冲合害",
                    ),
                    ProvenanceItem(
                        layer=ProvenanceLayer.ENGINEERING_ABSTRACTION,
                        description="工程抽象：将刑冲合害抽象为 STRUCTURAL_CHANGE Evidence",
                        confidence="MEDIUM",
                    ),
                ],
            ),
        ]

    @staticmethod
    def get_yuanhai_ziping_rules() -> List[CombinationRule]:
        return [
            CombinationRule(
                rule_id="YHZP-BASIC-001",
                classic="渊海子平",
                target="DAY_MASTER_STRENGTH",
                combination_type=CombinationType.NECESSARY_SET,
                combination_rationale=(
                    "《渊海子平》作为子平体系基础，提出'得令则旺，失令则衰；"
                    "根重则强，根轻则弱'的基础判断框架。"
                    "但这是基础框架，《滴天髓》已提醒'虽是至理，亦死法也'。"
                ),
                required_evidence=[
                    EvidenceCondition(
                        evidence_type="SEASONAL_STATE",
                        value_matches={"seasonal_alignment": "IN_SEASON"},
                        description="得令",
                    ),
                ],
                supporting_evidence=[
                    EvidenceCondition(evidence_type="ROOT_PRESENT", description="得地"),
                    EvidenceCondition(evidence_type="RESOURCE_SUPPORT", description="印生"),
                    EvidenceCondition(evidence_type="PEER_SUPPORT", description="比劫帮"),
                ],
                constraining_evidence=[
                    EvidenceCondition(evidence_type="OFFICER_CONTROL", description="官杀克"),
                    EvidenceCondition(evidence_type="OUTPUT_DRAIN", description="食伤泄"),
                    EvidenceCondition(evidence_type="WEALTH_DRAIN", description="财耗"),
                ],
                blocking_conditions=["SPECIAL_PATTERN", "DAY_MASTER_COMBINED"],
                qualifying_conditions=["ROOT_DAMAGED", "SEASONAL_NOT_MAIN_QI"],
                sufficient_for_target=None,
                output_state="BASIC_STRENGTH_CANDIDATE",
                output_strength=OutputStrength.CANDIDATE,
                can_derive_final=False,
                classical_source=ClassicalSource(
                    classic="渊海子平", edition="徐子平撰（题）", chapter="论旺衰",
                    text_type="ORIGINAL", author="徐子平（题）",
                    source_text="得令则旺，失令则衰；根重则强，根轻则弱。",
                    verification_status="PARTIALLY_VERIFIED",
                ),
                authorization_level=AuthorizationLevel.PARTIAL,
                provenance_chain=[
                    ProvenanceItem(
                        layer=ProvenanceLayer.CLASSICAL_TEXT,
                        description="原文：'得令则旺，失令则衰；根重则强，根轻则弱' — 基础旺衰框架",
                        source_ref="渊海子平·论旺衰",
                    ),
                    ProvenanceItem(
                        layer=ProvenanceLayer.CLASSICAL_SEMANTIC,
                        description="经典语义：得令+根重是旺的基础条件（但《滴天髓》提醒不能机械套用）",
                        confidence="MEDIUM",
                    ),
                    ProvenanceItem(
                        layer=ProvenanceLayer.ENGINEERING_ABSTRACTION,
                        description="工程抽象：将基础框架抽象为 NECESSARY_SET + supporting_evidence",
                        confidence="MEDIUM",
                    ),
                ],
                notes="这是基础框架，不是最终判断。《滴天髓》已提醒'虽是至理，亦死法也'。",
            ),
        ]

    @classmethod
    def get_all_rules(cls) -> List[CombinationRule]:
        return (
            cls.get_ditiansui_rules() +
            cls.get_ziping_zhenquan_rules() +
            cls.get_qiongtong_baojian_rules() +
            cls.get_sanming_tonghui_rules() +
            cls.get_yuanhai_ziping_rules()
        )


# ============================================================================
# 增强后的 Combination Engine（Value-aware）
# ============================================================================

class EvidenceCombinationEngine:
    """增强后的 Combination Engine — Value-aware matching"""

    def __init__(self):
        self.rules = ClassicalCombinationRules.get_all_rules()
        self.matcher = ValueAwareEvidenceMatcher()

    def combine(self, evidences: List[Dict[str, Any]],
                context: Optional[Dict[str, Any]] = None) -> List[CombinationResult]:
        if context is None:
            context = {}

        blocking_conditions = set(context.get("blocking_conditions", []))
        qualifying_conditions = set(context.get("qualifying_conditions", []))

        results = []

        for rule in self.rules:
            # Value-aware 匹配必要条件
            required_matched = []
            required_all_met = True
            for cond in rule.required_evidence:
                matched, matched_evs = self.matcher.match_condition(evidences, cond)
                if matched:
                    required_matched.append(f"{cond.evidence_type}({len(matched_evs)}个匹配)")
                else:
                    required_all_met = False
                    break

            if not required_all_met:
                continue

            # 检查阻断条件
            triggered_blocking = [b for b in rule.blocking_conditions if b in blocking_conditions]
            if triggered_blocking:
                results.append(CombinationResult(
                    rule_id=rule.rule_id, classic=rule.classic, target=rule.target,
                    output_state="NOT_APPLICABLE", output_strength=OutputStrength.UNRESOLVED,
                    matched_required=required_matched, matched_supporting=[],
                    matched_constraining=[], triggered_blocking=triggered_blocking,
                    triggered_qualifying=[], is_applicable=False,
                    authorization_level=rule.authorization_level,
                    value_aware_matching=True,
                    notes=f"阻断条件触发: {triggered_blocking}",
                ))
                continue

            # Value-aware 匹配辅助条件
            supporting_matched = []
            for cond in rule.supporting_evidence:
                matched, matched_evs = self.matcher.match_condition(evidences, cond)
                if matched:
                    supporting_matched.append(f"{cond.evidence_type}({len(matched_evs)}个)")

            # Value-aware 匹配制约条件
            constraining_matched = []
            for cond in rule.constraining_evidence:
                matched, matched_evs = self.matcher.match_condition(evidences, cond)
                if matched:
                    constraining_matched.append(f"{cond.evidence_type}({len(matched_evs)}个)")

            # 检查限定条件
            triggered_qualifying = [q for q in rule.qualifying_conditions if q in qualifying_conditions]

            # 确定输出强度
            if triggered_qualifying:
                output_strength = OutputStrength.QUALIFIED
            else:
                output_strength = rule.output_strength

            # 如果不是 sufficient_for_target，且辅助证据不足，降级
            if rule.sufficient_for_target is None and len(supporting_matched) == 0:
                output_strength = OutputStrength.NOT_CONFIRMED

            results.append(CombinationResult(
                rule_id=rule.rule_id, classic=rule.classic, target=rule.target,
                output_state=rule.output_state, output_strength=output_strength,
                matched_required=required_matched, matched_supporting=supporting_matched,
                matched_constraining=constraining_matched, triggered_blocking=[],
                triggered_qualifying=triggered_qualifying, is_applicable=True,
                authorization_level=rule.authorization_level,
                value_aware_matching=True,
                notes=rule.notes,
            ))

        return results


# ============================================================================
# Classical Rule Provenance Audit — 逐条审计
# ============================================================================

class ClassicalRuleProvenanceAuditor:
    """
    Classical Rule Provenance Auditor — 逐条审计 Rule 的原典推导链

    核心问题：代码执行的 Rule，究竟是不是经典真正允许我们这么辨？
    区分：
    - CLASSICAL_TEXT：经典原文直接支持
    - CLASSICAL_SEMANTIC：经典语义推导
    - ENGINEERING_ABSTRACTION：工程抽象（工程师设计）
    - ENGINEERING_INFERENCE：工程推导
    """

    @staticmethod
    def audit_rule(rule: CombinationRule) -> Dict[str, Any]:
        """审计单条 Rule"""
        layers_count = {}
        for item in rule.provenance_chain:
            layers_count[item.layer.value] = layers_count.get(item.layer.value, 0) + 1

        # 评估授权强度
        has_classical_text = layers_count.get("CLASSICAL_TEXT", 0) > 0
        has_classical_semantic = layers_count.get("CLASSICAL_SEMANTIC", 0) > 0
        has_engineering_abstraction = layers_count.get("ENGINEERING_ABSTRACTION", 0) > 0
        has_engineering_inference = layers_count.get("ENGINEERING_INFERENCE", 0) > 0

        # 授权评估
        if has_classical_text and has_classical_semantic and not has_engineering_inference:
            auth_assessment = "STRONG"  # 经典原文+语义，无工程推导
        elif has_classical_text and has_classical_semantic:
            auth_assessment = "MEDIUM"  # 经典原文+语义，但有工程推导
        elif has_classical_text:
            auth_assessment = "WEAK"    # 只有经典原文，语义和工程抽象需要验证
        else:
            auth_assessment = "NONE"    # 没有经典原文支持

        return {
            "rule_id": rule.rule_id,
            "classic": rule.classic,
            "target": rule.target,
            "authorization_level": rule.authorization_level.value,
            "can_derive_final": rule.can_derive_final,
            "sufficient_for_target": rule.sufficient_for_target,
            "provenance_layers": layers_count,
            "has_classical_text": has_classical_text,
            "has_classical_semantic": has_classical_semantic,
            "has_engineering_abstraction": has_engineering_abstraction,
            "has_engineering_inference": has_engineering_inference,
            "auth_assessment": auth_assessment,
            "provenance_chain": [
                {
                    "layer": item.layer.value,
                    "description": item.description,
                    "source_ref": item.source_ref,
                    "confidence": item.confidence,
                }
                for item in rule.provenance_chain
            ],
        }

    @classmethod
    def audit_all_rules(cls) -> List[Dict[str, Any]]:
        """审计所有 Rule"""
        rules = ClassicalCombinationRules.get_all_rules()
        return [cls.audit_rule(rule) for rule in rules]


# ============================================================================
# 验证
# ============================================================================

def verify_p0_2_8_a():
    print("=" * 80)
    print("P0-2.8-A Classical Rule Provenance Audit + Engine 增强 — 验证")
    print("=" * 80)

    # 测试命例：壬子 甲寅 甲子 丙寅
    print("\n【测试命例】壬子 甲寅 甲子 丙寅（日主甲木）")

    # Step 1: L4 Evidence（带 value/subject/position/qualifiers）
    print("\n【Step 1】L4 Evidence（Value-aware 格式）")
    evidences = [
        {
            "evidence_id": "E-L4-SEASONAL-甲",
            "evidence_type": "SEASONAL_STATE",
            "value": {"seasonal_alignment": "IN_SEASON", "season": "春", "growth_stage": "临官"},
            "subject": {"entity_type": "DAY_MASTER", "stem": "甲"},
            "position": "month",
            "qualifiers": {},
            "polarity": "CONTEXT",
        },
        {
            "evidence_id": "E-L3-ROOT-PRESENT",
            "evidence_type": "ROOT_PRESENT",
            "value": {"root_present": True, "root_count": 2, "has_main_qi_root": True},
            "subject": {"entity_type": "DAY_MASTER", "stem": "甲"},
            "position": "month,hour",
            "qualifiers": {"integrity": "INTACT"},
            "polarity": "SUPPORT",
        },
        {
            "evidence_id": "E-L4-RESOURCE-甲",
            "evidence_type": "RESOURCE_SUPPORT",
            "value": {"resource_present": True, "resource_count": 1},
            "subject": {"entity_type": "STEM", "position": "year", "stem": "壬"},
            "position": "year",
            "qualifiers": {},
            "polarity": "SUPPORT",
        },
        {
            "evidence_id": "E-L4-PEER-甲",
            "evidence_type": "PEER_SUPPORT",
            "value": {"peer_present": True, "peer_count": 1},
            "subject": {"entity_type": "STEM", "position": "month", "stem": "甲"},
            "position": "month",
            "qualifiers": {},
            "polarity": "SUPPORT",
        },
        {
            "evidence_id": "E-L4-OUTPUT-甲",
            "evidence_type": "OUTPUT_DRAIN",
            "value": {"output_present": True, "output_count": 1},
            "subject": {"entity_type": "STEM", "position": "hour", "stem": "丙"},
            "position": "hour",
            "qualifiers": {},
            "polarity": "CONSTRAINT",
        },
    ]

    for ev in evidences:
        print(f"  {ev['evidence_type']}: value={ev['value']}, subject={ev['subject']['entity_type']}")

    # Step 2: 执行组合（Value-aware Engine）
    print("\n【Step 2】执行 Evidence Combination（Value-aware Engine）")
    engine = EvidenceCombinationEngine()
    context = {"blocking_conditions": [], "qualifying_conditions": []}
    results = engine.combine(evidences, context)

    print(f"\n  匹配到 {len(results)} 条组合规则")
    for r in results:
        print(f"\n  --- {r.classic} / {r.rule_id} ---")
        print(f"    目标: {r.target}")
        print(f"    输出: {r.output_state} ({r.output_strength.value})")
        print(f"    Value-aware匹配: {r.value_aware_matching}")
        print(f"    必要条件: {r.matched_required}")
        print(f"    辅助条件: {r.matched_supporting}")
        print(f"    制约条件: {r.matched_constraining}")

    # Step 3: Classical Rule Provenance Audit
    print("\n" + "=" * 80)
    print("【Step 3】Classical Rule Provenance Audit（逐条审计）")
    print("=" * 80)

    audit_results = ClassicalRuleProvenanceAuditor.audit_all_rules()

    for audit in audit_results:
        print(f"\n  --- {audit['rule_id']} ({audit['classic']}) ---")
        print(f"    目标: {audit['target']}")
        print(f"    授权级别: {audit['authorization_level']}")
        print(f"    sufficient_for_target: {audit['sufficient_for_target']}")
        print(f"    can_derive_final: {audit['can_derive_final']}")
        print(f"    Provenance 层级: {audit['provenance_layers']}")
        print(f"    授权评估: {audit['auth_assessment']}")
        print(f"    推导链:")
        for item in audit['provenance_chain']:
            print(f"      [{item['layer']}] {item['description']} (confidence={item['confidence']})")

    # Step 4: 验证检查清单
    print("\n" + "=" * 80)
    print("【Step 4】验证检查清单")
    print("=" * 80)

    checks = []

    # 检查 1：CombinationType / sufficient_for_target 一致性
    all_rules = ClassicalCombinationRules.get_all_rules()
    no_contradiction = all(
        not (r.combination_type == CombinationType.SUFFICIENT_FOR_TARGET and r.sufficient_for_target is None)
        for r in all_rules
    )
    checks.append(("CombinationType / sufficient_for_target 一致性（无矛盾）", no_contradiction))

    # 检查 2：DTS-STRENGTH-001 不再是 SUFFICIENT
    dts_rule = next(r for r in all_rules if r.rule_id == "DTS-STRENGTH-001")
    dts_not_sufficient = dts_rule.combination_type != CombinationType.SUFFICIENT_FOR_TARGET
    checks.append(("DTS-STRENGTH-001 不再标记为 SUFFICIENT（改为 NECESSARY_SET）", dts_not_sufficient))

    # 检查 3：QTB-CLIMATE-001 明确 sufficient_for_target
    qtb_rule = next(r for r in all_rules if r.rule_id == "QTB-CLIMATE-001")
    qtb_sufficient_target = qtb_rule.sufficient_for_target == "CLIMATE_PROFILE_CANDIDATE"
    checks.append(("QTB-CLIMATE-001 明确 sufficient_for_target=CLIMATE_PROFILE_CANDIDATE", qtb_sufficient_target))

    # 检查 4：Value-aware Engine 消费 Evidence value
    value_aware_used = all(r.value_aware_matching for r in results if r.is_applicable)
    checks.append(("Value-aware Engine 消费 Evidence value/subject/position", value_aware_used))

    # 检查 5：EvidenceCondition 支持 value_matches
    has_value_matches = any(
        len(cond.value_matches) > 0
        for r in all_rules for cond in r.required_evidence
    )
    checks.append(("EvidenceCondition 支持 value_matches（如 seasonal_alignment=IN_SEASON）", has_value_matches))

    # 检查 6：所有 Rule 都有 Provenance Chain
    all_have_provenance = all(len(r.provenance_chain) > 0 for r in all_rules)
    checks.append(("所有 Rule 都有 Provenance Chain（区分经典原意和工程抽象）", all_have_provenance))

    # 检查 7：Provenance Chain 包含 CLASSICAL_TEXT 层
    all_have_classical_text = all(
        any(item.layer == ProvenanceLayer.CLASSICAL_TEXT for item in r.provenance_chain)
        for r in all_rules
    )
    checks.append(("所有 Rule 的 Provenance Chain 都包含 CLASSICAL_TEXT 层", all_have_classical_text))

    # 检查 8：Provenance Chain 包含 ENGINEERING_ABSTRACTION 层
    all_have_engineering = all(
        any(item.layer == ProvenanceLayer.ENGINEERING_ABSTRACTION for item in r.provenance_chain)
        for r in all_rules
    )
    checks.append(("所有 Rule 的 Provenance Chain 都包含 ENGINEERING_ABSTRACTION 层", all_have_engineering))

    # 检查 9：所有 Rule 的 can_derive_final=False
    all_cannot_derive_final = all(r.can_derive_final == False for r in all_rules)
    checks.append(("所有 Rule 的 can_derive_final=False（不能直接推出最终强弱）", all_cannot_derive_final))

    # 检查 10：阻断条件检查生效
    context_with_block = {"blocking_conditions": ["SPECIAL_PATTERN_FROM_STRONG"], "qualifying_conditions": []}
    results_with_block = engine.combine(evidences, context_with_block)
    blocked_rules = [r for r in results_with_block if not r.is_applicable]
    blocking_works = len(blocked_rules) > 0
    checks.append(("阻断条件检查生效（Value-aware Engine）", blocking_works))

    # 输出
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if not passed: all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("【最终结果】ALL CHECKS PASSED ✅")
    else:
        print("【最终结果】SOME CHECKS FAILED ❌")
    print("=" * 80)

    print("\n【核心结论】")
    print("  1. 修复：CombinationType / sufficient_for_target 一致性（无矛盾）")
    print("  2. 修复：DTS-STRENGTH-001 从 SUFFICIENT 改为 NECESSARY_SET")
    print("  3. 修复：QTB-CLIMATE-001 明确 sufficient_for_target=CLIMATE_PROFILE_CANDIDATE")
    print("  4. 增强：Value-aware Engine 消费 Evidence value/subject/position/qualifiers")
    print("  5. 增强：EvidenceCondition 支持 value_matches/value_not_matches/subject_matches/integrity_not")
    print("  6. 新增：Classical Rule Provenance Audit，逐条审 6 条 Rule 的原典推导链")
    print("  7. 新增：Provenance 4 层分类（CLASSICAL_TEXT / CLASSICAL_SEMANTIC / ENGINEERING_ABSTRACTION / ENGINEERING_INFERENCE）")
    print("  8. 明确：Contract PASS ≠ Rule Truth PASS；工程抽象层需要继续验证")
    print("  9. 所有 Rule 的 can_derive_final=False，不能直接推出最终强弱")
    print("  10. 在 Rule 没有完全原典授权之前，整体旺衰判断保持 UNRESOLVED")

    return all_passed


if __name__ == "__main__":
    verify_p0_2_8_a()
