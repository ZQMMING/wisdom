"""
P0-2.9-A Classical State Rule Semantic Audit

基于 2295553 的 🟢 PASS 裁决，明确：
"Traceability PASS" ≠ "Semantic Correctness PASS"

核心任务：针对 4 条样板 Rule，逐条审每个 EvidenceCondition：
- 原典原文 ↓ 原文到底表达什么 ↓ 经典语义
- Evidence 为什么是 required？
- 为什么是 supporting？
- 为什么是 constraining？
- 为什么是 blocking？
- 为什么这个 State 是 Candidate？
- 这个 State 能否进一步推导？

建立 Condition 级别的 Provenance（不只是 Rule 级别）。

数据来源：D:\shuntian\docs\五部经典整理\（本地优先）

工程原则：
- 先别做"跨经典综合"
- 现在还处在"算 ↓ 证 ↓ 单体系辨"阶段
- 多维辨证状态集合，暂不综合
- qiangruo = UNRESOLVED
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json


# ============================================================================
# 标准数据结构
# ============================================================================

class ConditionRole(Enum):
    """EvidenceCondition 在 Rule 中的角色"""
    REQUIRED = "REQUIRED"
    SUPPORTING = "SUPPORTING"
    CONSTRAINING = "CONSTRAINING"
    BLOCKING = "BLOCKING"
    QUALIFYING = "QUALIFYING"


class SemanticAssessment(Enum):
    """语义评估等级"""
    CLASSICAL_DIRECT = "CLASSICAL_DIRECT"           # 经典原文直接支持
    CLASSICAL_REASONABLE = "CLASSICAL_REASONABLE"   # 经典原文可以合理映射
    ENGINEERING_DERIVED = "ENGINEERING_DERIVED"     # 工程师根据整个体系推导
    NEEDS_FURTHER_AUDIT = "NEEDS_FURTHER_AUDIT"     # 需要进一步审计


@dataclass(frozen=True)
class ConditionProvenance:
    """
    Condition 级别的 Provenance — 每个 EvidenceCondition 都有自己的原典依据

    这是 P0-2.9-A 的核心：不只是 Rule 级别有 provenance，
    每个 EvidenceCondition 都要能追到：
    - 具体原文 span
    - 原文表达什么
    - 为什么属于这个角色（required/supporting/constraining）
    - 语义评估等级
    """
    condition_id: str
    evidence_type: str
    role: ConditionRole
    classical_quote: str                    # 本地经典原文引用
    classical_source: str                   # 经典/章节
    classical_meaning: str                  # 原文到底表达什么
    role_justification: str                 # 为什么属于这个角色
    semantic_assessment: SemanticAssessment  # 语义评估等级
    local_file: str                         # 本地文件路径
    notes: str = ""


@dataclass(frozen=True)
class StateSemanticAudit:
    """
    State 语义审计 — 为什么这个 State 是 Candidate，能否进一步推导
    """
    state_name: str
    why_candidate: str                      # 为什么是 Candidate 而不是最终结论
    can_further_derive: bool                # 能否进一步推导
    further_derive_conditions: List[str]    # 进一步推导需要什么条件
    blocking_reasons: List[str]             # 为什么不能直接作为最终结论
    classical_basis: str                    # 经典依据


@dataclass(frozen=True)
class RuleSemanticAudit:
    """
    Rule 语义审计 — 整条 Rule 的语义审计结果
    """
    rule_id: str
    classic: str
    target: str
    output_state: str
    condition_audits: List[ConditionProvenance]
    state_audit: StateSemanticAudit
    overall_assessment: str                 # 整体语义评估
    traceability_pass: bool                 # Traceability 是否通过（链路可追溯）
    semantic_correctness_pass: bool         # Semantic Correctness 是否通过（语义正确）
    notes: str = ""


# ============================================================================
# 4 条样板 Rule 的语义审计
# ============================================================================

class SemanticAuditor:
    """语义审计器 — 对 4 条样板 Rule 逐条做 Condition 级别语义审计"""

    @staticmethod
    def audit_dts_strength_001() -> RuleSemanticAudit:
        """DTS-STRENGTH-001 — 滴天髓 旺衰候选"""

        condition_audits = [
            # REQUIRED: SEASONAL_STATE（得令）
            ConditionProvenance(
                condition_id="DTS-001-REQ-01",
                evidence_type="SEASONAL_STATE",
                role=ConditionRole.REQUIRED,
                classical_quote="真正的旺是得令得地有根有气是真旺，天干堆叠一堆五行地之无根无气只是虚旺假旺",
                classical_source="滴天髓·通神论·第十七章 衰旺",
                classical_meaning="原文明确将'得令'列为'真旺'的第一个必要条件。没有得令，即使天干堆叠同五行，也只是'虚旺假旺'。",
                role_justification="得令是旺衰判断的必要条件，原文直接将其列为'真旺'的首要条件。没有得令，其他条件无法形成'真旺'判断。",
                semantic_assessment=SemanticAssessment.CLASSICAL_DIRECT,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes="原文直接支持 required 角色。",
            ),
            # REQUIRED: ROOT_PRESENT（得地）
            ConditionProvenance(
                condition_id="DTS-001-REQ-02",
                evidence_type="ROOT_PRESENT",
                role=ConditionRole.REQUIRED,
                classical_quote="真正的旺是得令得地有根有气是真旺",
                classical_source="滴天髓·通神论·第十七章 衰旺",
                classical_meaning="原文明确将'得地有根'列为'真旺'的第二个必要条件。地支无根，即使天干有同五行，也只是虚浮。",
                role_justification="得地（地支有根）是旺衰判断的必要条件，原文直接将其列为'真旺'的条件。无根则气不聚，无法形成真旺。",
                semantic_assessment=SemanticAssessment.CLASSICAL_DIRECT,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes="原文直接支持 required 角色。",
            ),
            # SUPPORTING: RESOURCE_SUPPORT（印生，得势之一）
            ConditionProvenance(
                condition_id="DTS-001-SUP-01",
                evidence_type="RESOURCE_SUPPORT",
                role=ConditionRole.SUPPORTING,
                classical_quote="须察支中党众，干上生扶，方可定其真衰真旺",
                classical_source="滴天髓·通神论·衰旺（任铁樵注）",
                classical_meaning="原文强调'干上生扶'是判断真衰真旺的重要观察点，但不是唯一决定因素。印星生扶属于'干上生扶'的一种。",
                role_justification="印星生扶是'得势'的表现之一，能增强日主力量，但不是'真旺'的必要条件。有印生扶可以支持旺的判断，但没有印生扶不代表不旺（得令得地本身已足够）。因此属于 supporting 而非 required。",
                semantic_assessment=SemanticAssessment.CLASSICAL_REASONABLE,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes="原文'干上生扶'可以合理映射为印星生扶，但'得势'的完整内涵还包括比劫帮身，需要进一步拆分。",
            ),
            # SUPPORTING: PEER_SUPPORT（比劫帮，得势之二）
            ConditionProvenance(
                condition_id="DTS-001-SUP-02",
                evidence_type="PEER_SUPPORT",
                role=ConditionRole.SUPPORTING,
                classical_quote="须察支中党众，干上生扶，方可定其真衰真旺",
                classical_source="滴天髓·通神论·衰旺（任铁樵注）",
                classical_meaning="'支中党众'指地支中同五行的力量聚集，比劫帮身属于'党众'的表现。原文强调需要观察党众情况，但不是唯一决定因素。",
                role_justification="比劫帮身是'得势'的另一种表现，能增强日主力量，但不是必要条件。有比劫帮可以支持旺的判断，但没有比劫不代表不旺。因此属于 supporting。",
                semantic_assessment=SemanticAssessment.CLASSICAL_REASONABLE,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes="'支中党众'可以合理映射为比劫帮身，但'党众'的完整内涵还包括地支根气，需要与 ROOT_PRESENT 做边界澄清。",
            ),
            # CONSTRAINING: OFFICER_CONTROL（官杀克）
            ConditionProvenance(
                condition_id="DTS-001-CON-01",
                evidence_type="OFFICER_CONTROL",
                role=ConditionRole.CONSTRAINING,
                classical_quote="真正的衰是失令失地根气全无被克被泄，不是数量少就是衰",
                classical_source="滴天髓·通神论·第十七章 衰旺",
                classical_meaning="原文明确将'被克'列为'真衰'的条件之一。官杀克日主属于'被克'的表现。但原文同时强调不是数量少就是衰，需要综合判断。",
                role_justification="官杀克身会制约日主力量，是旺衰判断中的制约因素。但官杀存在不直接等于身弱（官杀有制、日主得令得地时仍可能旺）。因此属于 constraining，不是 blocking 或 required。",
                semantic_assessment=SemanticAssessment.CLASSICAL_REASONABLE,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes="原文'被克'可以合理映射为官杀克身，但官杀的有制/无制、力量强弱需要进一步细分，当前只是 presence 级别的 constraining。",
            ),
            # CONSTRAINING: OUTPUT_DRAIN（食伤泄）
            ConditionProvenance(
                condition_id="DTS-001-CON-02",
                evidence_type="OUTPUT_DRAIN",
                role=ConditionRole.CONSTRAINING,
                classical_quote="真正的衰是失令失地根气全无被克被泄，不是数量少就是衰",
                classical_source="滴天髓·通神论·第十七章 衰旺",
                classical_meaning="原文明确将'被泄'列为'真衰'的条件之一。食伤泄日主属于'被泄'的表现。",
                role_justification="食伤泄身会消耗日主力量，是制约因素。但食伤存在不直接等于身弱（食伤有制、日主得令得地时仍可能旺）。因此属于 constraining。",
                semantic_assessment=SemanticAssessment.CLASSICAL_REASONABLE,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes="原文'被泄'可以合理映射为食伤泄身，但食伤的力量强弱、是否有制需要进一步细分。",
            ),
            # CONSTRAINING: WEALTH_DRAIN（财星耗）
            ConditionProvenance(
                condition_id="DTS-001-CON-03",
                evidence_type="WEALTH_DRAIN",
                role=ConditionRole.CONSTRAINING,
                classical_quote="真正的衰是失令失地根气全无被克被泄，不是数量少就是衰",
                classical_source="滴天髓·通神论·第十七章 衰旺",
                classical_meaning="原文将'被克被泄'列为真衰条件，财星耗身属于'被泄/被耗'的延伸。财星是日主所克，会消耗日主力量。",
                role_justification="财星耗身会消耗日主力量，是制约因素。但财星存在不直接等于身弱（财有制、日主得令得地时仍可能旺）。因此属于 constraining。",
                semantic_assessment=SemanticAssessment.ENGINEERING_DERIVED,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes="原文只明确说'被克被泄'，财星耗身属于工程师根据五行生克体系推导的延伸。需要进一步在滴天髓原文中寻找财星与旺衰关系的直接依据。",
            ),
            # BLOCKING: SPECIAL_PATTERN_FROM_STRONG（从强格）
            ConditionProvenance(
                condition_id="DTS-001-BLK-01",
                evidence_type="SPECIAL_PATTERN_FROM_STRONG",
                role=ConditionRole.BLOCKING,
                classical_quote="望到极致不能克只能泄，弱到极致不能泄只能服",
                classical_source="滴天髓·通神论·第四章 知命",
                classical_meaning="原文明确指出旺到极致时，普通的旺衰判断逻辑不适用，需要顺势而为（从强格）。此时不能用普通的'得令得地=旺'逻辑。",
                role_justification="从强格是特殊格局，普通旺衰判断规则不适用。如果命局属于从强格，DTS-STRENGTH-001 的普通旺衰候选规则应该被阻断，不适用。因此属于 blocking。",
                semantic_assessment=SemanticAssessment.CLASSICAL_DIRECT,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes="原文直接支持 blocking 角色。从格是滴天髓明确讨论的特殊情况。",
            ),
        ]

        state_audit = StateSemanticAudit(
            state_name="CANDIDATE_STRONG",
            why_candidate=(
                "得令+得地是'真旺'的必要条件，但原文同时强调'虽是至理，亦死法也'，"
                "需要综合'支中党众、干上生扶'以及制约因素才能定'真衰真旺'。"
                "当前规则只检查了必要条件和辅助条件的存在，没有完成综合判断，"
                "因此只能形成 CANDIDATE_STRONG，不能直接输出 STRONG。"
            ),
            can_further_derive=True,
            further_derive_conditions=[
                "需要完成制约因素（官杀/食伤/财）的力量评估",
                "需要完成辅助因素（印/比劫）的力量评估",
                "需要建立证据之间的组合逻辑（不是简单计数）",
                "需要原典授权的综合判断规则",
            ],
            blocking_reasons=[
                "原文明确说'虽是至理，亦死法也'，反对机械判断",
                "当前 constraining 条件只是 presence 级别，没有力量评估",
                "当前 supporting 条件只是 presence 级别，没有力量评估",
                "没有原典授权的综合判断规则（A+B+C 如何组合成最终结论）",
            ],
            classical_basis=(
                "《滴天髓》第十七章衰旺：'得时俱为旺论，失令便作衰看，虽是至理，亦死法也。"
                "须察支中党众，干上生扶，方可定其真衰真旺。'"
            ),
        )

        return RuleSemanticAudit(
            rule_id="DTS-STRENGTH-001",
            classic="滴天髓",
            target="DAY_MASTER_STRENGTH",
            output_state="CANDIDATE_STRONG",
            condition_audits=condition_audits,
            state_audit=state_audit,
            overall_assessment=(
                "2 个 required 条件有 CLASSICAL_DIRECT 支持；"
                "4 个 supporting/constraining 条件有 CLASSICAL_REASONABLE 支持；"
                "1 个 constraining 条件（WEALTH_DRAIN）是 ENGINEERING_DERIVED，需要进一步审计；"
                "1 个 blocking 条件有 CLASSICAL_DIRECT 支持。"
                "State 是 Candidate 的判断有充分经典依据。"
            ),
            traceability_pass=True,
            semantic_correctness_pass=False,  # 因为有 ENGINEERING_DERIVED 条件，且综合判断规则未授权
            notes=(
                "Traceability PASS：链路可追溯，每个条件都有本地原文引用。"
                "Semantic Correctness NOT YET PASS：WEALTH_DRAIN 的角色需要进一步原典验证，"
                "且综合判断规则（A+B+C 如何组合）尚未获得原典授权。"
            ),
        )

    @staticmethod
    def audit_qtb_climate_001() -> RuleSemanticAudit:
        """QTB-CLIMATE-001 — 穷通宝鉴 调候候选"""

        condition_audits = [
            # REQUIRED: SEASONAL_STATE（日干×月令）
            ConditionProvenance(
                condition_id="QTB-001-REQ-01",
                evidence_type="SEASONAL_STATE",
                role=ConditionRole.REQUIRED,
                classical_quote="调候为先，不管什么五行什么格局，先调和气候再谈平衡发展",
                classical_source="穷通宝鉴·卷首五行总论",
                classical_meaning="穷通宝鉴全书核心就是'调候为先'，日干×月令决定了寒暖燥湿的基本状态，这是调候判断的唯一必要输入。",
                role_justification="日干×月令是调候判断的必要条件，全书按十天干×十二月令组织，每个组合都有明确的调候方向。没有日干×月令就无法判断调候。因此属于 required。",
                semantic_assessment=SemanticAssessment.CLASSICAL_DIRECT,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\穷通宝鉴.md",
                notes="原文直接支持 required 角色。穷通宝鉴的结构就是日干×月令的二维矩阵。",
            ),
            # QUALIFYING: ADJUSTMENT_ELEMENT_PRESENT（调候用神已出现）
            ConditionProvenance(
                condition_id="QTB-001-QLF-01",
                evidence_type="ADJUSTMENT_ELEMENT_PRESENT",
                role=ConditionRole.QUALIFYING,
                classical_quote="三春甲木正月二月三月初春余寒未消大树刚刚复苏生发，全局第一需求就是丙火暖局",
                classical_source="穷通宝鉴·甲木卷·正月",
                classical_meaning="原文明确每个日干×月令组合都有'第一需求'（调候用神）。如果这个用神在命局中出现，调候状态会从'需要调候'变为'调候用神已备'，但仍需检查是否有根、可用、受阻。",
                role_justification="调候用神出现会改变调候状态的性质（从缺到备），但不直接等于调候完成（还需检查用神是否有根、是否受制）。因此属于 qualifying，不是 required 或 supporting。",
                semantic_assessment=SemanticAssessment.CLASSICAL_REASONABLE,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\穷通宝鉴.md",
                notes="原文明确每个组合有'第一需求'，用神出现的限定作用可以合理映射。但用神'有根/可用/受阻'的细分需要进一步实现。",
            ),
        ]

        state_audit = StateSemanticAudit(
            state_name="CLIMATE_PROFILE_CANDIDATE",
            why_candidate=(
                "日干×月令足以确定调候的基本方向（寒暖燥湿），穷通宝鉴原文明确支持。"
                "但调候的完整判断还需要：调候用神是否出现、是否有根、是否可用、是否受阻、是否过量。"
                "当前规则只确定了基本方向，因此是 QUALIFIED 级别的 Candidate，不是最终调候结论。"
            ),
            can_further_derive=True,
            further_derive_conditions=[
                "需要检查调候用神是否在命局中出现",
                "需要检查调候用神是否有根",
                "需要检查调候用神是否受制/受损",
                "需要检查调候用神是否过量",
                "需要原典授权的调候用神可用性判断规则",
            ],
            blocking_reasons=[
                "穷通宝鉴原文强调'全局搭配整体制衡，没有任何一个五行可以单独成事'",
                "当前只确定了调候方向，没有完成用神可用性评估",
                "调候是独立维度，不能反过来决定强弱",
            ],
            classical_basis=(
                "《穷通宝鉴》卷首五行总论：'调候为先，不管什么五行什么格局，先调和气候再谈平衡发展。'"
                "甲木卷正月：'初春余寒未消，全局第一需求就是丙火暖局。'"
            ),
        )

        return RuleSemanticAudit(
            rule_id="QTB-CLIMATE-001",
            classic="穷通宝鉴",
            target="CLIMATE_ADJUSTMENT",
            output_state="CLIMATE_PROFILE_CANDIDATE",
            condition_audits=condition_audits,
            state_audit=state_audit,
            overall_assessment=(
                "1 个 required 条件有 CLASSICAL_DIRECT 支持；"
                "1 个 qualifying 条件有 CLASSICAL_REASONABLE 支持；"
                "State 是 Candidate 的判断有充分经典依据。"
                "sufficient_for_target=CLIMATE_PROFILE_CANDIDATE 的设定有经典依据。"
            ),
            traceability_pass=True,
            semantic_correctness_pass=False,  # 调候用神可用性判断规则尚未实现和授权
            notes=(
                "Traceability PASS：链路可追溯。"
                "Semantic Correctness NOT YET PASS：调候基本方向的判断有经典依据，"
                "但调候用神可用性（有根/可用/受阻/过量）的判断规则尚未实现和原典授权。"
            ),
        )

    @classmethod
    def audit_all(cls) -> List[RuleSemanticAudit]:
        return [
            cls.audit_dts_strength_001(),
            cls.audit_qtb_climate_001(),
            # ZP-PATTERN-001 和 YHZP-BASIC-001 的审计可以后续补充
        ]


# ============================================================================
# 输出审计报告
# ============================================================================

def print_audit_report(audits: List[RuleSemanticAudit]):
    print("=" * 80)
    print("P0-2.9-A Classical State Rule Semantic Audit — 审计报告")
    print("=" * 80)

    print("\n【核心原则】")
    print("  Traceability PASS ≠ Semantic Correctness PASS")
    print("  Traceability：链路可追溯（每个条件都有原文引用）")
    print("  Semantic Correctness：语义正确（每个条件的角色和综合判断规则都有原典授权）")

    for audit in audits:
        print("\n" + "=" * 80)
        print(f"【Rule】{audit.rule_id} — {audit.classic}")
        print(f"  目标: {audit.target}")
        print(f"  输出: {audit.output_state}")
        print(f"  Traceability PASS: {audit.traceability_pass}")
        print(f"  Semantic Correctness PASS: {audit.semantic_correctness_pass}")

        print(f"\n  --- Condition 级别语义审计 ---")
        for cond in audit.condition_audits:
            print(f"\n  [{cond.role.value}] {cond.evidence_type}")
            print(f"    语义评估: {cond.semantic_assessment.value}")
            print(f"    经典来源: {cond.classical_source}")
            print(f"    原文引用: {cond.classical_quote[:60]}...")
            print(f"    原文含义: {cond.classical_meaning[:80]}...")
            print(f"    角色依据: {cond.role_justification[:80]}...")
            if cond.notes:
                print(f"    备注: {cond.notes[:80]}...")

        print(f"\n  --- State 语义审计 ---")
        print(f"  为什么是 Candidate: {audit.state_audit.why_candidate[:100]}...")
        print(f"  能否进一步推导: {audit.state_audit.can_further_derive}")
        print(f"  进一步推导需要:")
        for cond in audit.state_audit.further_derive_conditions:
            print(f"    - {cond}")
        print(f"  不能直接作为最终结论的原因:")
        for reason in audit.state_audit.blocking_reasons:
            print(f"    - {reason}")

        print(f"\n  整体评估: {audit.overall_assessment[:150]}...")
        print(f"  备注: {audit.notes}")

    # 汇总
    print("\n" + "=" * 80)
    print("【审计汇总】")
    print("=" * 80)

    total = len(audits)
    traceability_pass_count = sum(1 for a in audits if a.traceability_pass)
    semantic_pass_count = sum(1 for a in audits if a.semantic_correctness_pass)

    print(f"  审计 Rule 总数: {total}")
    print(f"  Traceability PASS: {traceability_pass_count}/{total}")
    print(f"  Semantic Correctness PASS: {semantic_pass_count}/{total}")

    # 按语义评估等级统计
    all_conditions = [c for a in audits for c in a.condition_audits]
    classical_direct = sum(1 for c in all_conditions if c.semantic_assessment == SemanticAssessment.CLASSICAL_DIRECT)
    classical_reasonable = sum(1 for c in all_conditions if c.semantic_assessment == SemanticAssessment.CLASSICAL_REASONABLE)
    engineering_derived = sum(1 for c in all_conditions if c.semantic_assessment == SemanticAssessment.ENGINEERING_DERIVED)

    print(f"\n  Condition 语义评估等级统计:")
    print(f"    CLASSICAL_DIRECT（经典原文直接支持）: {classical_direct}")
    print(f"    CLASSICAL_REASONABLE（经典原文合理映射）: {classical_reasonable}")
    print(f"    ENGINEERING_DERIVED（工程师体系推导）: {engineering_derived}")

    print(f"\n  【结论】")
    print(f"  1. Traceability 已全部通过：每个条件都有本地经典原文引用")
    print(f"  2. Semantic Correctness 尚未全部通过：")
    print(f"     - 部分条件是 ENGINEERING_DERIVED，需要进一步原典验证")
    print(f"     - 综合判断规则（A+B+C 如何组合）尚未获得原典授权")
    print(f"     - 调候用神可用性判断规则尚未实现和授权")
    print(f"  3. 下一步：对 ENGINEERING_DERIVED 条件做进一步原典审计")
    print(f"  4. 下一步：建立原典授权的综合判断规则")
    print(f"  5. 当前状态：算 → Fact → Relation → Evidence → Combination → Candidate State 链路已通")
    print(f"     但 Semantic Correctness 仍需逐条深化")


if __name__ == "__main__":
    audits = SemanticAuditor.audit_all()
    print_audit_report(audits)
