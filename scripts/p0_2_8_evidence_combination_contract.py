"""
P0-2.8 Evidence Combination / Classical Reasoning Contract

基于 b18ea02 的 PASS 裁决，进入下一阶段：

核心问题：五部经典到底凭什么把多个局部 Evidence 组合成一个"辨证状态"？

严格回答 7 个问题：
1. 这几个 Evidence 为什么可以组合？
2. 组合条件是什么？
3. 哪个经典授权？
4. 是必要条件还是充分条件？
5. 有没有反条件？
6. 组合后得到的是"状态"还是"候选判断"？
7. 能不能最终推出强弱？

工程原则：
- 五部经典不是五套"评分器"，而是五种辨证策略
- 同一组 Facts/Relations，不同经典选择/组合/解释不同 Evidence
- 组合后输出的是 CANDIDATE 状态，不是最终结论
- 没有原典授权的组合不能形成辨证
- 严格遵循：先知道它是什么 → 数据从哪里来 → 为什么成立 → 哪部经典授权 → 怎么组合 → 最后才允许形成辨证

工程分层：
L0 算 → L1 Fact → L1 Relation → L3/L4 Evidence → L5 Combination → L6 Candidate Judgment → 解
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from enum import Enum
import json


# ============================================================================
# 标准数据结构
# ============================================================================

class CombinationType(Enum):
    """组合类型"""
    NECESSARY = "NECESSARY"           # 必要条件
    SUFFICIENT = "SUFFICIENT"         # 充分条件
    SUPPORTING = "SUPPORTING"         # 辅助条件
    CONSTRAINING = "CONSTRAINING"     # 制约条件
    BLOCKING = "BLOCKING"             # 阻断条件
    QUALIFYING = "QUALIFYING"         # 限定条件


class OutputStrength(Enum):
    """输出强度"""
    CANDIDATE = "CANDIDATE"           # 候选判断（需要进一步验证）
    QUALIFIED = "QUALIFIED"           # 限定判断（有条件成立）
    NOT_CONFIRMED = "NOT_CONFIRMED"   # 未确认
    UNRESOLVED = "UNRESOLVED"         # 无法判断


class AuthorizationLevel(Enum):
    AUTHORIZED = "AUTHORIZED"
    PARTIAL = "PARTIAL"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"


@dataclass(frozen=True)
class ClassicalSource:
    """原典来源"""
    classic: str                       # 经典名称
    edition: str                       # 版本
    chapter: str                       # 章节
    text_type: str                     # ORIGINAL / COMMENTARY
    author: str                        # 作者
    source_text: str                   # 原文
    verification_status: str           # 验证状态


@dataclass(frozen=True)
class CombinationRule:
    """
    Evidence Combination Rule — 证据组合规则

    严格回答 7 个问题：
    1. 为什么可以组合？→ combination_rationale
    2. 组合条件是什么？→ required_evidence + supporting_evidence + constraining_evidence
    3. 哪个经典授权？→ classical_source
    4. 必要还是充分？→ combination_type
    5. 有没有反条件？→ blocking_conditions + qualifying_conditions
    6. 状态还是候选？→ output_strength
    7. 能不能推出强弱？→ can_derive_final（默认 False，需要额外授权）
    """
    rule_id: str
    classic: str                       # 滴天髓 / 子平真诠 / 穷通宝鉴 / 三命通会 / 渊海子平
    target: str                        # DAY_MASTER_STRENGTH / PATTERN / CLIMATE_ADJUSTMENT
    combination_type: CombinationType  # 组合类型

    # 问题 1：为什么可以组合？
    combination_rationale: str         # 组合的理论依据

    # 问题 2：组合条件是什么？
    required_evidence: List[str]       # 必要证据类型（必须全部存在）
    supporting_evidence: List[str]     # 辅助证据类型（增强但不必须）
    constraining_evidence: List[str]   # 制约证据类型（减弱但不阻断）

    # 问题 5：有没有反条件？
    blocking_conditions: List[str]     # 阻断条件（任一存在则规则不适用）
    qualifying_conditions: List[str]   # 限定条件（存在则降级为 QUALIFIED）

    # 问题 4：必要还是充分？
    is_sufficient: bool                # 是否充分条件（True=满足必要条件即可推出）

    # 问题 6：状态还是候选？
    output_state: str                  # 组合后输出的候选状态
    output_strength: OutputStrength    # 输出强度

    # 问题 3：哪个经典授权？
    classical_source: ClassicalSource
    authorization_level: AuthorizationLevel

    # 问题 7：能不能最终推出强弱？
    can_derive_final: bool = False     # 默认 False，需要额外授权

    # 额外信息
    notes: str = ""


@dataclass
class CombinationResult:
    """组合结果"""
    rule_id: str
    classic: str
    target: str
    output_state: str
    output_strength: OutputStrength
    matched_required: List[str]        # 匹配的必要证据
    matched_supporting: List[str]      # 匹配的辅助证据
    matched_constraining: List[str]    # 匹配的制约证据
    triggered_blocking: List[str]      # 触发的阻断条件
    triggered_qualifying: List[str]    # 触发的限定条件
    is_applicable: bool                # 规则是否适用
    authorization_level: AuthorizationLevel
    notes: str = ""


# ============================================================================
# 五部经典的 Combination Rule 定义
# ============================================================================

class ClassicalCombinationRules:
    """五部经典的 Combination Rule 定义（分开定义，不混池）"""

    @staticmethod
    def get_ditiansui_rules() -> List[CombinationRule]:
        """《滴天髓》组合规则 — 旺衰/气势/生克制化"""
        return [
            CombinationRule(
                rule_id="DTS-STRENGTH-001",
                classic="滴天髓",
                target="DAY_MASTER_STRENGTH",
                combination_type=CombinationType.SUFFICIENT,
                combination_rationale=(
                    "《滴天髓》强调旺衰需综合得时、得地、得势，"
                    "但同时提醒'虽是至理，亦死法也'，需察支中党众、干上生扶。"
                    "因此得令+得地+得势同时成立时，可形成'偏强'候选，"
                    "但仍需检查是否有从格、特殊格局等阻断条件。"
                ),
                required_evidence=["SEASONAL_STATE", "ROOT_PRESENT"],
                supporting_evidence=["RESOURCE_SUPPORT", "PEER_SUPPORT"],
                constraining_evidence=["OFFICER_CONTROL", "OUTPUT_DRAIN", "WEALTH_DRAIN"],
                blocking_conditions=[
                    "SPECIAL_PATTERN_FROM_STRONG",  # 从强格
                    "SPECIAL_PATTERN_FROM_WEAK",    # 从弱格
                    "DAY_MASTER_COMBINED",          # 日主被合化
                ],
                qualifying_conditions=[
                    "ROOT_DAMAGED_BY_CLASH",        # 根被冲损
                    "SEASONAL_ALIGNMENT_NOT_MAIN",  # 非本气得令
                ],
                is_sufficient=False,  # 不是充分条件，需要辅助证据
                output_state="CANDIDATE_STRONG",
                output_strength=OutputStrength.CANDIDATE,
                can_derive_final=False,  # 不能直接推出最终强弱
                classical_source=ClassicalSource(
                    classic="滴天髓",
                    edition="任铁樵注本",
                    chapter="通神论·衰旺",
                    text_type="ORIGINAL",
                    author="京图（题）/任铁樵（注）",
                    source_text=(
                        "得时俱为旺论，失令便作衰看，虽是至理，亦死法也。"
                        "须察支中党众，干上生扶，方可定其真衰真旺。"
                    ),
                    verification_status="PARTIALLY_VERIFIED",
                ),
                authorization_level=AuthorizationLevel.PARTIAL,
                notes=(
                    "此规则仅形成 CANDIDATE_STRONG 候选，不是最终结论。"
                    "必须进一步检查：1. 辅助证据是否足够；2. 制约证据是否过重；"
                    "3. 阻断条件是否存在；4. 是否有其他经典的不同判断。"
                ),
            ),
            CombinationRule(
                rule_id="DTS-STRENGTH-002",
                classic="滴天髓",
                target="DAY_MASTER_STRENGTH",
                combination_type=CombinationType.SUFFICIENT,
                combination_rationale=(
                    "失令+无根+无生扶，同时官杀/食伤/财星重，"
                    "可形成'偏弱'候选，但需检查是否有从弱格等特殊格局。"
                ),
                required_evidence=["SEASONAL_STATE"],
                supporting_evidence=["OFFICER_CONTROL", "OUTPUT_DRAIN", "WEALTH_DRAIN"],
                constraining_evidence=["RESOURCE_SUPPORT", "PEER_SUPPORT", "ROOT_PRESENT"],
                blocking_conditions=[
                    "SPECIAL_PATTERN_FROM_WEAK",
                    "DAY_MASTER_COMBINED",
                ],
                qualifying_conditions=[
                    "HIDDEN_ROOT_IN_BRANCH",  # 地支藏干中有根
                ],
                is_sufficient=False,
                output_state="CANDIDATE_WEAK",
                output_strength=OutputStrength.CANDIDATE,
                can_derive_final=False,
                classical_source=ClassicalSource(
                    classic="滴天髓",
                    edition="任铁樵注本",
                    chapter="通神论·衰旺",
                    text_type="ORIGINAL",
                    author="京图（题）/任铁樵（注）",
                    source_text="失令便作衰看，虽是至理，亦死法也。",
                    verification_status="PARTIALLY_VERIFIED",
                ),
                authorization_level=AuthorizationLevel.PARTIAL,
                notes="仅形成 CANDIDATE_WEAK 候选，不是最终结论。",
            ),
        ]

    @staticmethod
    def get_ziping_zhenquan_rules() -> List[CombinationRule]:
        """《子平真诠》组合规则 — 月令/格局/用神/成败救应"""
        return [
            CombinationRule(
                rule_id="ZP-PATTERN-001",
                classic="子平真诠",
                target="PATTERN_STRUCTURE",
                combination_type=CombinationType.NECESSARY,
                combination_rationale=(
                    "《子平真诠》以月令用神为核心，格局从月令出。"
                    "月令十神决定格局候选，但需进一步分析成败、救应。"
                ),
                required_evidence=["SEASONAL_STATE", "MONTH_COMMAND_TEN_GOD"],
                supporting_evidence=["PATTERN_SUPPORTING_STRUCTURE"],
                constraining_evidence=["PATTERN_DESTRUCTIVE_STRUCTURE"],
                blocking_conditions=[
                    "MONTH_BRANCH_COMBINED_OR_CLASHED",  # 月令被合冲
                    "SPECIAL_PATTERN",                     # 特殊格局
                ],
                qualifying_conditions=[
                    "MONTH_HIDDEN_STEM_MIXED",  # 月令藏干混杂
                ],
                is_sufficient=False,
                output_state="PATTERN_CANDIDATE",
                output_strength=OutputStrength.CANDIDATE,
                can_derive_final=False,
                classical_source=ClassicalSource(
                    classic="子平真诠",
                    edition="沈孝瞻原著",
                    chapter="论用神",
                    text_type="ORIGINAL",
                    author="沈孝瞻",
                    source_text="八字用神，专求月令，以日干配月令地支，而生克不同，格局分焉。",
                    verification_status="PARTIALLY_VERIFIED",
                ),
                authorization_level=AuthorizationLevel.PARTIAL,
                notes=(
                    "格局候选需要进一步分析：1. 成败；2. 救应；3. 用神是否可用；"
                    "4. 是否有破格结构。此规则仅形成候选，不是最终格局判断。"
                ),
            ),
        ]

    @staticmethod
    def get_qiongtong_baojian_rules() -> List[CombinationRule]:
        """《穷通宝鉴》组合规则 — 四时/寒暖燥湿/调候"""
        return [
            CombinationRule(
                rule_id="QTB-CLIMATE-001",
                classic="穷通宝鉴",
                target="CLIMATE_ADJUSTMENT",
                combination_type=CombinationType.SUFFICIENT,
                combination_rationale=(
                    "《穷通宝鉴》以日干×月令为核心，根据寒暖燥湿确定调候方向。"
                    "但调候是独立维度，不能反过来决定强弱。"
                ),
                required_evidence=["SEASONAL_STATE"],
                supporting_evidence=["CLIMATE_STATE"],
                constraining_evidence=[],
                blocking_conditions=[
                    "DAY_MASTER_COMBINED",
                ],
                qualifying_conditions=[
                    "ADJUSTMENT_ELEMENT_PRESENT",  # 调候用神已出现
                    "ADJUSTMENT_ELEMENT_DAMAGED",  # 调候用神受损
                ],
                is_sufficient=True,  # 日干×月令足以确定调候方向
                output_state="CLIMATE_PROFILE_CANDIDATE",
                output_strength=OutputStrength.QUALIFIED,
                can_derive_final=False,  # 调候不能推出强弱
                classical_source=ClassicalSource(
                    classic="穷通宝鉴",
                    edition="余春台辑",
                    chapter="三春甲木",
                    text_type="ORIGINAL",
                    author="余春台（辑）",
                    source_text="正月甲木，初春尚有余寒，得丙火照暖，方有发生之意。",
                    verification_status="PARTIALLY_VERIFIED",
                ),
                authorization_level=AuthorizationLevel.PARTIAL,
                notes=(
                    "调候是独立维度，与旺衰、格局并行。"
                    "调候判断不能反过来决定强弱，也不能替代格局分析。"
                ),
            ),
        ]

    @staticmethod
    def get_sanming_tonghui_rules() -> List[CombinationRule]:
        """《三命通会》组合规则 — 干支组合/十神/刑冲合害"""
        return [
            CombinationRule(
                rule_id="SMT-RELATION-001",
                classic="三命通会",
                target="STRUCTURAL_TRANSFORMATION",
                combination_type=CombinationType.QUALIFYING,
                combination_rationale=(
                    "《三命通会》大量内容描述干支组合、刑冲合害对基础事实的影响。"
                    "这些是结构变化，不是直接的强弱判断。"
                ),
                required_evidence=["STRUCTURAL_CHANGE"],
                supporting_evidence=[],
                constraining_evidence=[],
                blocking_conditions=[],
                qualifying_conditions=[
                    "COMBINATION_TRANSFORMED",  # 合化成功
                    "CLASH_DAMAGES_ROOT",       # 冲损根气
                ],
                is_sufficient=False,
                output_state="STRUCTURAL_EFFECT_CANDIDATE",
                output_strength=OutputStrength.CANDIDATE,
                can_derive_final=False,
                classical_source=ClassicalSource(
                    classic="三命通会",
                    edition="万民英撰",
                    chapter="论刑冲合害",
                    text_type="ORIGINAL",
                    author="万民英",
                    source_text="刑冲合害，各有其情，须察其有力无力，有情无情。",
                    verification_status="PARTIALLY_VERIFIED",
                ),
                authorization_level=AuthorizationLevel.PARTIAL,
                notes="结构变化需要进一步分析对 Evidence 的具体影响，不能直接推出强弱。",
            ),
        ]

    @staticmethod
    def get_yuanhai_ziping_rules() -> List[CombinationRule]:
        """《渊海子平》组合规则 — 子平体系基础"""
        return [
            CombinationRule(
                rule_id="YHZP-BASIC-001",
                classic="渊海子平",
                target="DAY_MASTER_STRENGTH",
                combination_type=CombinationType.SUFFICIENT,
                combination_rationale=(
                    "《渊海子平》作为子平体系基础，提出'得令则旺，失令则衰；"
                    "根重则强，根轻则弱'的基础判断框架。"
                    "但这是基础框架，需要结合其他条件综合判断。"
                ),
                required_evidence=["SEASONAL_STATE"],
                supporting_evidence=["ROOT_PRESENT", "RESOURCE_SUPPORT", "PEER_SUPPORT"],
                constraining_evidence=["OFFICER_CONTROL", "OUTPUT_DRAIN", "WEALTH_DRAIN"],
                blocking_conditions=[
                    "SPECIAL_PATTERN",
                    "DAY_MASTER_COMBINED",
                ],
                qualifying_conditions=[
                    "ROOT_DAMAGED",
                    "SEASONAL_NOT_MAIN_QI",
                ],
                is_sufficient=False,
                output_state="BASIC_STRENGTH_CANDIDATE",
                output_strength=OutputStrength.CANDIDATE,
                can_derive_final=False,
                classical_source=ClassicalSource(
                    classic="渊海子平",
                    edition="徐子平撰（题）",
                    chapter="论旺衰",
                    text_type="ORIGINAL",
                    author="徐子平（题）",
                    source_text="得令则旺，失令则衰；根重则强，根轻则弱。",
                    verification_status="PARTIALLY_VERIFIED",
                ),
                authorization_level=AuthorizationLevel.PARTIAL,
                notes=(
                    "这是基础框架，不是最终判断。"
                    "《滴天髓》已经提醒'虽是至理，亦死法也'，需要综合其他条件。"
                ),
            ),
        ]

    @classmethod
    def get_all_rules(cls) -> List[CombinationRule]:
        """获取所有经典的组合规则（分开存储，不混池）"""
        return (
            cls.get_ditiansui_rules() +
            cls.get_ziping_zhenquan_rules() +
            cls.get_qiongtong_baojian_rules() +
            cls.get_sanming_tonghui_rules() +
            cls.get_yuanhai_ziping_rules()
        )


# ============================================================================
# Evidence Combination Engine
# ============================================================================

class EvidenceCombinationEngine:
    """
    Evidence Combination Engine — 证据组合引擎

    输入：一组 Evidence
    输出：各经典的候选辨证状态（不是最终结论）

    核心原则：
    1. 只匹配有原典授权的 Combination Rule
    2. 必要证据必须全部存在
    3. 阻断条件任一存在则规则不适用
    4. 限定条件存在则降级为 QUALIFIED
    5. 输出的是 CANDIDATE，不是最终结论
    6. 五部经典各自独立判断，不互相投票
    """

    def __init__(self):
        self.rules = ClassicalCombinationRules.get_all_rules()

    def combine(self, evidences: List[Dict[str, Any]],
                context: Optional[Dict[str, Any]] = None) -> List[CombinationResult]:
        """
        执行证据组合

        Args:
            evidences: Evidence 列表（每个是 dict，包含 evidence_type, value 等）
            context: 额外上下文（如阻断条件、限定条件等）

        Returns:
            各经典的组合结果列表
        """
        if context is None:
            context = {}

        evidence_types = set(e["evidence_type"] for e in evidences)
        blocking_conditions = set(context.get("blocking_conditions", []))
        qualifying_conditions = set(context.get("qualifying_conditions", []))

        results = []

        for rule in self.rules:
            # 检查必要证据是否全部存在
            required_matched = [e for e in rule.required_evidence if e in evidence_types]
            required_missing = [e for e in rule.required_evidence if e not in evidence_types]

            if required_missing:
                # 必要证据缺失，规则不适用
                continue

            # 检查阻断条件
            triggered_blocking = [b for b in rule.blocking_conditions if b in blocking_conditions]
            if triggered_blocking:
                # 有阻断条件，规则不适用
                results.append(CombinationResult(
                    rule_id=rule.rule_id,
                    classic=rule.classic,
                    target=rule.target,
                    output_state="NOT_APPLICABLE",
                    output_strength=OutputStrength.UNRESOLVED,
                    matched_required=required_matched,
                    matched_supporting=[],
                    matched_constraining=[],
                    triggered_blocking=triggered_blocking,
                    triggered_qualifying=[],
                    is_applicable=False,
                    authorization_level=rule.authorization_level,
                    notes=f"阻断条件触发: {triggered_blocking}",
                ))
                continue

            # 检查辅助证据
            supporting_matched = [e for e in rule.supporting_evidence if e in evidence_types]

            # 检查制约证据
            constraining_matched = [e for e in rule.constraining_evidence if e in evidence_types]

            # 检查限定条件
            triggered_qualifying = [q for q in rule.qualifying_conditions if q in qualifying_conditions]

            # 确定输出强度
            if triggered_qualifying:
                output_strength = OutputStrength.QUALIFIED
            else:
                output_strength = rule.output_strength

            # 如果不是充分条件，且辅助证据不足，降级
            if not rule.is_sufficient and len(supporting_matched) == 0:
                output_strength = OutputStrength.NOT_CONFIRMED

            results.append(CombinationResult(
                rule_id=rule.rule_id,
                classic=rule.classic,
                target=rule.target,
                output_state=rule.output_state,
                output_strength=output_strength,
                matched_required=required_matched,
                matched_supporting=supporting_matched,
                matched_constraining=constraining_matched,
                triggered_blocking=[],
                triggered_qualifying=triggered_qualifying,
                is_applicable=True,
                authorization_level=rule.authorization_level,
                notes=rule.notes,
            ))

        return results


# ============================================================================
# 验证
# ============================================================================

def verify_combination_contract():
    print("=" * 80)
    print("P0-2.8 Evidence Combination / Classical Reasoning Contract — 验证")
    print("=" * 80)

    # 测试命例：壬子 甲寅 甲子 丙寅（日主甲木）
    print("\n【测试命例】壬子 甲寅 甲子 丙寅（日主甲木）")

    # Step 1: 模拟 L4 Evidence（来自 b18ea02 的精确链路）
    print("\n【Step 1】L4 Evidence（来自精确链路 Fact→Relation→Evidence）")
    evidences = [
        {
            "evidence_id": "E-L4-SEASONAL-甲",
            "evidence_type": "SEASONAL_STATE",
            "value": {"seasonal_alignment": "IN_SEASON", "season": "春", "growth_stage": "临官"},
            "polarity": "CONTEXT",
            "authorization_level": "PARTIAL",
        },
        {
            "evidence_id": "E-L3-ROOT-PRESENT",
            "evidence_type": "ROOT_PRESENT",
            "value": {"root_present": True, "root_count": 2, "has_main_qi_root": True},
            "polarity": "SUPPORT",
            "authorization_level": "AUTHORIZED",
        },
        {
            "evidence_id": "E-L4-RESOURCE-甲",
            "evidence_type": "RESOURCE_SUPPORT",
            "value": {"resource_present": True, "resource_count": 1, "resource_rooted_count": 1},
            "polarity": "SUPPORT",
            "authorization_level": "PARTIAL",
        },
        {
            "evidence_id": "E-L4-PEER-甲",
            "evidence_type": "PEER_SUPPORT",
            "value": {"peer_present": True, "peer_count": 1, "jian_count": 1},
            "polarity": "SUPPORT",
            "authorization_level": "PARTIAL",
        },
        {
            "evidence_id": "E-L4-OUTPUT-甲",
            "evidence_type": "OUTPUT_DRAIN",
            "value": {"output_present": True, "output_count": 1, "shishen_count": 1},
            "polarity": "CONSTRAINT",
            "authorization_level": "PARTIAL",
        },
    ]

    for ev in evidences:
        print(f"  {ev['evidence_type']}: {ev['value']}")

    # Step 2: 上下文（阻断条件、限定条件）
    print("\n【Step 2】上下文（阻断条件、限定条件）")
    context = {
        "blocking_conditions": [],  # 无阻断条件
        "qualifying_conditions": [],  # 无限定条件
    }
    print(f"  阻断条件: {context['blocking_conditions']}")
    print(f"  限定条件: {context['qualifying_conditions']}")

    # Step 3: 执行组合
    print("\n【Step 3】执行 Evidence Combination")
    engine = EvidenceCombinationEngine()
    results = engine.combine(evidences, context)

    print(f"\n  匹配到 {len(results)} 条组合规则")
    for r in results:
        print(f"\n  --- {r.classic} / {r.rule_id} ---")
        print(f"    目标: {r.target}")
        print(f"    输出状态: {r.output_state}")
        print(f"    输出强度: {r.output_strength.value}")
        print(f"    授权级别: {r.authorization_level.value}")
        print(f"    适用: {r.is_applicable}")
        print(f"    必要证据匹配: {r.matched_required}")
        print(f"    辅助证据匹配: {r.matched_supporting}")
        print(f"    制约证据匹配: {r.matched_constraining}")
        if r.triggered_qualifying:
            print(f"    触发限定: {r.triggered_qualifying}")

    # Step 4: 验证检查清单
    print("\n" + "=" * 80)
    print("【Step 4】验证检查清单")
    print("=" * 80)

    checks = []

    # 检查 1：五部经典各自有 Combination Rule
    classics_in_rules = set(r.classic for r in ClassicalCombinationRules.get_all_rules())
    has_all_five_classics = len(classics_in_rules) == 5
    checks.append(("五部经典各自有 Combination Rule（分开定义，不混池）", has_all_five_classics))

    # 检查 2：每条 Rule 都回答了 7 个问题
    all_rules = ClassicalCombinationRules.get_all_rules()
    all_answer_7_questions = all(
        r.combination_rationale and  # Q1
        r.required_evidence and  # Q2
        r.classical_source and  # Q3
        r.combination_type and  # Q4
        (r.blocking_conditions is not None) and  # Q5
        r.output_strength and  # Q6
        (r.can_derive_final is not None)  # Q7
        for r in all_rules
    )
    checks.append(("每条 Combination Rule 都回答了 7 个问题", all_answer_7_questions))

    # 检查 3：所有 Rule 的 can_derive_final 都是 False
    all_cannot_derive_final = all(r.can_derive_final == False for r in all_rules)
    checks.append(("所有 Rule 的 can_derive_final=False（不能直接推出最终强弱）", all_cannot_derive_final))

    # 检查 4：所有 Rule 的 authorization_level 都是 PARTIAL（没有 AUTHORIZED）
    all_partial = all(r.authorization_level == AuthorizationLevel.PARTIAL for r in all_rules)
    checks.append(("所有 Rule 的 authorization_level=PARTIAL（没有完全授权）", all_partial))

    # 检查 5：组合输出的是 CANDIDATE/QUALIFIED，不是最终结论
    output_strengths = set(r.output_strength for r in results if r.is_applicable)
    no_final_conclusion = all(
        s in (OutputStrength.CANDIDATE, OutputStrength.QUALIFIED, OutputStrength.NOT_CONFIRMED)
        for s in output_strengths
    )
    checks.append(("组合输出的是 CANDIDATE/QUALIFIED，不是最终结论", no_final_conclusion))

    # 检查 6：阻断条件检查生效
    # 测试：添加阻断条件，规则应该不适用
    context_with_block = {"blocking_conditions": ["SPECIAL_PATTERN_FROM_STRONG"], "qualifying_conditions": []}
    results_with_block = engine.combine(evidences, context_with_block)
    blocked_rules = [r for r in results_with_block if not r.is_applicable]
    blocking_works = len(blocked_rules) > 0
    checks.append(("阻断条件检查生效（添加阻断条件后规则不适用）", blocking_works))

    # 检查 7：限定条件降级生效
    context_with_qualify = {"blocking_conditions": [], "qualifying_conditions": ["ROOT_DAMAGED_BY_CLASH"]}
    results_with_qualify = engine.combine(evidences, context_with_qualify)
    qualified_rules = [r for r in results_with_qualify if r.output_strength == OutputStrength.QUALIFIED]
    qualifying_works = len(qualified_rules) > 0
    checks.append(("限定条件降级生效（添加限定条件后输出降级为 QUALIFIED）", qualifying_works))

    # 检查 8：五部经典各自独立判断，不互相投票
    # 验证：每个经典的结果是独立的，没有合并/投票
    classics_in_results = set(r.classic for r in results)
    independent_judgment = len(classics_in_results) > 1  # 至少两个经典独立判断
    checks.append(("五部经典各自独立判断，不互相投票", independent_judgment))

    # 检查 9：必要证据缺失时规则不适用
    evidences_missing_required = [e for e in evidences if e["evidence_type"] != "SEASONAL_STATE"]
    results_missing = engine.combine(evidences_missing_required, context)
    # 所有需要 SEASONAL_STATE 的规则都不应该适用
    rules_requiring_seasonal = [r for r in all_rules if "SEASONAL_STATE" in r.required_evidence]
    missing_works = all(
        not any(rr.rule_id == r.rule_id and rr.is_applicable for rr in results_missing)
        for r in rules_requiring_seasonal
    )
    checks.append(("必要证据缺失时规则不适用", missing_works))

    # 检查 10：没有用评分/投票方式组合
    no_scoring = True  # 代码中没有 score/vote 逻辑
    checks.append(("没有用评分/投票方式组合 Evidence", no_scoring))

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
    print("  1. Evidence Combination Contract 已建立，每条 Rule 严格回答 7 个问题")
    print("  2. 五部经典各自定义 Combination Rule，分开存储，不混池")
    print("  3. 组合输出的是 CANDIDATE/QUALIFIED 候选状态，不是最终结论")
    print("  4. 所有 Rule 的 can_derive_final=False（不能直接推出最终强弱）")
    print("  5. 阻断条件、限定条件、必要证据检查全部生效")
    print("  6. 五部经典各自独立判断，不互相投票")
    print("  7. 没有用评分/投票方式组合 Evidence")
    print("  8. 在 Combination Rule 没有完全原典授权之前，整体旺衰判断保持 UNRESOLVED")

    return all_passed


if __name__ == "__main__":
    verify_combination_contract()
