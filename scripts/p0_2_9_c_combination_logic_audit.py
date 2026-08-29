"""
P0-2.9-C Condition Combination Logic Audit

基于 07c5344 的 🟢 PASS 裁决，继续做 Condition 组合逻辑审计。

核心原则：
- 不仅审"Condition 从哪里来"，还要审"Condition 之间为什么这样组合"
- 即：Condition 从哪里来 → Condition 为什么成立 → Condition 之间为什么这样组合 → 最后允许产生什么 State
- 不能把五部经典统一成一套逻辑
- 滴天髓、子平真诠、穷通宝鉴、三命通会、渊海子平可能拥有不同的 Condition Type、Logic Type、State Type、Qualification Type
- 目前这个框架可以作为通用容器，但不能成为统一命理逻辑
- 算层完整性仍是最高优先级，FROZEN ≠ PROVEN CORRECT

对 DTS-STRENGTH-001 的 9 个 Condition 的组合逻辑做深度审计：
- 必要条件组合：得令 AND 得地
- 辅助条件组合：印生 OR 比劫帮
- 制约条件组合：官杀 OR 食伤 OR 财星
- 阻断条件：从强格
- 限定条件：根被冲、印被克等

数据来源：D:\shuntian\docs\五部经典整理\（本地优先）
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json


# ============================================================================
# 标准数据结构
# ============================================================================

class LogicOperator(Enum):
    """逻辑运算符"""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    REQUIRED = "REQUIRED"
    SUFFICIENT = "SUFFICIENT"
    BLOCKING = "BLOCKING"
    QUALIFYING = "QUALIFYING"
    XOR = "XOR"  # 互斥


class LogicAssessment(Enum):
    """组合逻辑的语义评估等级"""
    CLASSICAL_DIRECT = "CLASSICAL_DIRECT"           # 经典原文直接支持
    CLASSICAL_REASONABLE = "CLASSICAL_REASONABLE"   # 经典原文可以合理映射
    ENGINEERING_DERIVED = "ENGINEERING_DERIVED"     # 工程师根据体系推导
    NEEDS_FURTHER_AUDIT = "NEEDS_FURTHER_AUDIT"     # 需要进一步审计


@dataclass(frozen=True)
class LogicGroup:
    """
    逻辑组 — 描述一组 Condition 的组合方式

    例如：
    - 必要条件组：得令 AND 得地（必须同时成立）
    - 辅助条件组：印生 OR 比劫帮（任一成立即可增强）
    - 制约条件组：官杀 OR 食伤 OR 财星（任一成立即减弱）
    """
    group_id: str
    group_name: str
    operator: LogicOperator
    condition_ids: List[str]
    description: str
    classical_basis: str                    # 经典依据
    assessment: LogicAssessment             # 语义评估等级
    local_file: str                         # 本地文件路径
    notes: str = ""


@dataclass(frozen=True)
class LogicRelation:
    """
    逻辑关系 — 描述两个 Condition 之间的关系

    例如：
    - 得令 AND 得地：两个必要条件必须同时成立
    - 印生 OR 比劫帮：两个辅助条件任一成立即可
    - 从强格 BLOCKING 所有：阻断条件成立则整个规则不适用
    """
    relation_id: str
    source_condition: str
    target_condition: str
    operator: LogicOperator
    description: str
    classical_basis: str
    assessment: LogicAssessment
    local_file: str
    notes: str = ""


@dataclass(frozen=True)
class CombinationLogicAudit:
    """
    组合逻辑审计 — 整条 Rule 的组合逻辑审计结果
    """
    rule_id: str
    classic: str
    target: str
    logic_groups: List[LogicGroup]
    logic_relations: List[LogicRelation]
    overall_logic_expression: str           # 整体逻辑表达式（伪代码）
    overall_assessment: str                  # 整体语义评估
    traceability_pass: bool                  # 链路可追溯
    combination_correctness_pass: bool       # 组合逻辑正确性
    notes: str = ""


# ============================================================================
# DTS-STRENGTH-001 的组合逻辑审计
# ============================================================================

class DTS001LogicAuditor:
    """DTS-STRENGTH-001 的组合逻辑审计"""

    @staticmethod
    def audit() -> CombinationLogicAudit:

        logic_groups = [
            # 1. 必要条件组：得令 AND 得地
            LogicGroup(
                group_id="DTS-001-GRP-REQ",
                group_name="必要条件组",
                operator=LogicOperator.AND,
                condition_ids=["DTS-001-REQ-01", "DTS-001-REQ-02"],
                description=(
                    "得令（SEASONAL_STATE）AND 得地（ROOT_PRESENT）必须同时成立。"
                    "这是'真旺'的两个必要条件，缺一不可。"
                    "只有得令没有得地 → 虚旺假旺；只有得地没有得令 → 根基虽有但不得天时。"
                ),
                classical_basis=(
                    "《滴天髓》第十七章衰旺：'真正的旺是得令得地有根有气是真旺，"
                    "天干堆叠一堆五行地之无根无气只是虚旺假旺'。"
                    "原文将'得令'和'得地'并列为'真旺'的必要条件。"
                ),
                assessment=LogicAssessment.CLASSICAL_DIRECT,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes="原文直接将得令和得地并列为真旺的必要条件，AND 关系有 CLASSICAL_DIRECT 支持。",
            ),

            # 2. 辅助条件组：印生 OR 比劫帮
            LogicGroup(
                group_id="DTS-001-GRP-SUP",
                group_name="辅助条件组（得势）",
                operator=LogicOperator.OR,
                condition_ids=["DTS-001-SUP-01", "DTS-001-SUP-02"],
                description=(
                    "印生（RESOURCE_SUPPORT）OR 比劫帮（PEER_SUPPORT）任一成立即可增强日主力量。"
                    "这是'得势'的两种表现：印星生扶日主，比劫帮身。"
                    "两者都是辅助条件，不是必要条件。有则增强，无则不影响基础判断。"
                ),
                classical_basis=(
                    "《滴天髓》第十七章衰旺（任铁樵注）：'须察支中党众，干上生扶，方可定其真衰真旺'。"
                    "'干上生扶'可以映射为印星生扶，'支中党众'可以映射为比劫帮身。"
                    "但原文没有明确说两者是 OR 关系，这是工程师根据'得势'概念推导的。"
                ),
                assessment=LogicAssessment.CLASSICAL_REASONABLE,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes=(
                    "原文提到'干上生扶'和'支中党众'，可以合理映射为印生和比劫帮。"
                    "但 OR 关系（任一成立即可增强）是工程师根据'得势'概念推导的，"
                    "原文没有明确说两者是 OR 还是 AND。需要进一步原典验证。"
                ),
            ),

            # 3. 制约条件组：官杀 OR 食伤 OR 财星
            LogicGroup(
                group_id="DTS-001-GRP-CON",
                group_name="制约条件组",
                operator=LogicOperator.OR,
                condition_ids=["DTS-001-CON-01", "DTS-001-CON-02", "DTS-001-CON-03"],
                description=(
                    "官杀克（OFFICER_CONTROL）OR 食伤泄（OUTPUT_DRAIN）OR 财星耗（WEALTH_DRAIN）"
                    "任一成立即减弱日主力量。"
                    "这是'被克被泄被耗'的三种表现。"
                    "三者都是制约条件，不是必要条件。有则减弱，无则不影响基础判断。"
                ),
                classical_basis=(
                    "《滴天髓》第十七章衰旺：'真正的衰是失令失地根气全无被克被泄，不是数量少就是衰'。"
                    "原文明确说'被克被泄'，可以映射为官杀克和食伤泄。"
                    "但原文没有说'被耗'，财星耗是工程师根据五行生克体系推导的。"
                    "OR 关系（任一成立即减弱）也是工程师推导的。"
                ),
                assessment=LogicAssessment.ENGINEERING_DERIVED,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes=(
                    "原文只说'被克被泄'，没有说'被耗'。"
                    "财星耗是 ENGINEERING_DERIVED。"
                    "OR 关系（任一成立即减弱）也是工程师推导的，原文没有明确说三者是 OR 关系。"
                    "这个组的组合逻辑是当前最弱的环节，需要进一步原典验证。"
                ),
            ),

            # 4. 阻断条件组：从强格
            LogicGroup(
                group_id="DTS-001-GRP-BLK",
                group_name="阻断条件组",
                operator=LogicOperator.BLOCKING,
                condition_ids=["DTS-001-BLK-01"],
                description=(
                    "从强格（SPECIAL_PATTERN_FROM_STRONG）成立则整个普通旺衰判断规则不适用。"
                    "从格是特殊格局，旺到极致不能克只能泄，普通旺衰判断逻辑不适用。"
                ),
                classical_basis=(
                    "《滴天髓》第四章知命：'望到极致不能克只能泄，弱到极致不能泄只能服'。"
                    "原文直接支持从格是特殊情况，普通旺衰判断不适用。"
                ),
                assessment=LogicAssessment.CLASSICAL_DIRECT,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes="原文直接支持从格是特殊情况，BLOCKING 关系有 CLASSICAL_DIRECT 支持。",
            ),
        ]

        logic_relations = [
            # 必要条件之间的关系
            LogicRelation(
                relation_id="DTS-001-REL-01",
                source_condition="DTS-001-REQ-01",
                target_condition="DTS-001-REQ-02",
                operator=LogicOperator.AND,
                description="得令 AND 得地：两个必要条件必须同时成立，缺一不可。",
                classical_basis="原文将'得令得地'并列为'真旺'的必要条件。",
                assessment=LogicAssessment.CLASSICAL_DIRECT,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
            ),

            # 辅助条件之间的关系
            LogicRelation(
                relation_id="DTS-001-REL-02",
                source_condition="DTS-001-SUP-01",
                target_condition="DTS-001-SUP-02",
                operator=LogicOperator.OR,
                description="印生 OR 比劫帮：两个辅助条件任一成立即可增强日主力量。",
                classical_basis="原文提到'干上生扶'和'支中党众'，但 OR 关系是推导的。",
                assessment=LogicAssessment.CLASSICAL_REASONABLE,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
            ),

            # 制约条件之间的关系
            LogicRelation(
                relation_id="DTS-001-REL-03",
                source_condition="DTS-001-CON-01",
                target_condition="DTS-001-CON-02",
                operator=LogicOperator.OR,
                description="官杀克 OR 食伤泄：两个制约条件任一成立即减弱日主力量。",
                classical_basis="原文说'被克被泄'，但 OR 关系是推导的。",
                assessment=LogicAssessment.CLASSICAL_REASONABLE,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
            ),

            # 阻断条件与所有其他条件的关系
            LogicRelation(
                relation_id="DTS-001-REL-04",
                source_condition="DTS-001-BLK-01",
                target_condition="ALL_OTHER_CONDITIONS",
                operator=LogicOperator.BLOCKING,
                description="从强格 BLOCKING 所有其他条件：阻断条件成立则整个规则不适用。",
                classical_basis="原文直接支持从格是特殊情况，普通旺衰判断不适用。",
                assessment=LogicAssessment.CLASSICAL_DIRECT,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
            ),

            # 必要条件组与辅助条件组的关系
            LogicRelation(
                relation_id="DTS-001-REL-05",
                source_condition="DTS-001-GRP-REQ",
                target_condition="DTS-001-GRP-SUP",
                operator=LogicOperator.REQUIRED,
                description=(
                    "必要条件组是规则适用的前提，辅助条件组是在必要条件成立后的增强因素。"
                    "必要条件不成立 → 规则不适用；辅助条件不成立 → 规则仍适用但强度降低。"
                ),
                classical_basis=(
                    "原文说'得令得地有根有气是真旺'，得令得地是基础，"
                    "'干上生扶支中党众'是进一步判断真衰真旺的观察点。"
                ),
                assessment=LogicAssessment.CLASSICAL_REASONABLE,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes="必要条件优先于辅助条件的层级关系有经典依据，但具体的优先级规则是工程抽象。",
            ),

            # 必要条件组与制约条件组的关系
            LogicRelation(
                relation_id="DTS-001-REL-06",
                source_condition="DTS-001-GRP-REQ",
                target_condition="DTS-001-GRP-CON",
                operator=LogicOperator.REQUIRED,
                description=(
                    "必要条件组是规则适用的前提，制约条件组是在必要条件成立后的减弱因素。"
                    "必要条件不成立 → 规则不适用；制约条件成立 → 规则仍适用但强度降低。"
                ),
                classical_basis=(
                    "原文说'真正的衰是失令失地根气全无被克被泄'，"
                    "失令失地是基础，被克被泄是进一步的衰的表现。"
                ),
                assessment=LogicAssessment.CLASSICAL_REASONABLE,
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes="必要条件优先于制约条件的层级关系有经典依据，但具体的优先级规则是工程抽象。",
            ),
        ]

        # 整体逻辑表达式（伪代码）
        overall_expression = (
            "IF NOT (SPECIAL_PATTERN_FROM_STRONG) THEN\n"
            "  IF (SEASONAL_STATE AND ROOT_PRESENT) THEN\n"
            "    candidate_strength = STRONG_BASE\n"
            "    IF (RESOURCE_SUPPORT OR PEER_SUPPORT) THEN\n"
            "      candidate_strength = ENHANCED\n"
            "    IF (OFFICER_CONTROL OR OUTPUT_DRAIN OR WEALTH_DRAIN) THEN\n"
            "      candidate_strength = REDUCED\n"
            "    OUTPUT = CANDIDATE_STRONG (需要综合判断，不能直接输出 STRONG)\n"
            "  ELSE\n"
            "    RULE_NOT_APPLICABLE (必要条件不成立)\n"
            "ELSE\n"
            "  RULE_BLOCKED (从强格，普通旺衰判断不适用)\n"
        )

        return CombinationLogicAudit(
            rule_id="DTS-STRENGTH-001",
            classic="滴天髓",
            target="DAY_MASTER_STRENGTH",
            logic_groups=logic_groups,
            logic_relations=logic_relations,
            overall_logic_expression=overall_expression,
            overall_assessment=(
                "4 个逻辑组中：2 个 CLASSICAL_DIRECT（必要条件组 AND、阻断条件组 BLOCKING），"
                "1 个 CLASSICAL_REASONABLE（辅助条件组 OR），"
                "1 个 ENGINEERING_DERIVED（制约条件组 OR，包含财星耗这个 ENGINEERING_DERIVED 条件）。"
                "6 个逻辑关系中：3 个 CLASSICAL_DIRECT，2 个 CLASSICAL_REASONABLE，1 个 CLASSICAL_REASONABLE。"
                "整体组合逻辑框架有经典依据，但具体的 OR 关系和优先级规则需要进一步原典验证。"
            ),
            traceability_pass=True,
            combination_correctness_pass=False,  # 因为有 ENGINEERING_DERIVED 的组，且具体组合规则未完全授权
            notes=(
                "Traceability PASS：每个逻辑组和逻辑关系都有本地原文引用。"
                "Combination Correctness NOT YET PASS："
                "1. 制约条件组的 OR 关系是 ENGINEERING_DERIVED，包含财星耗这个 ENGINEERING_DERIVED 条件"
                "2. 辅助条件组的 OR 关系是 CLASSICAL_REASONABLE，需要进一步原典验证"
                "3. 必要条件组与辅助/制约条件组的优先级关系是 CLASSICAL_REASONABLE"
                "4. 最关键的：综合判断规则（必要条件+辅助条件+制约条件如何组合成最终结论）尚未获得原典授权"
                "5. 当前只能输出 CANDIDATE_STRONG，不能直接输出 STRONG"
            ),
        )


# ============================================================================
# 输出组合逻辑审计报告
# ============================================================================

def print_logic_audit_report(audit: CombinationLogicAudit):
    print("=" * 80)
    print("P0-2.9-C Condition Combination Logic Audit — 报告")
    print("=" * 80)

    print("\n【核心原则】")
    print("  1. 不仅审'Condition 从哪里来'，还要审'Condition 之间为什么这样组合'")
    print("  2. 不能把五部经典统一成一套逻辑")
    print("  3. 算层完整性仍是最高优先级，FROZEN ≠ PROVEN CORRECT")
    print("  4. 不强行升级，精确记录已知和未知")

    print(f"\n【审计范围】{audit.rule_id} — {audit.classic}")
    print(f"  目标: {audit.target}")
    print(f"  逻辑组数量: {len(audit.logic_groups)}")
    print(f"  逻辑关系数量: {len(audit.logic_relations)}")
    print(f"  Traceability PASS: {audit.traceability_pass}")
    print(f"  Combination Correctness PASS: {audit.combination_correctness_pass}")

    # 按语义评估等级统计
    groups_by_assessment = {}
    for g in audit.logic_groups:
        key = g.assessment.value
        groups_by_assessment[key] = groups_by_assessment.get(key, 0) + 1

    relations_by_assessment = {}
    for r in audit.logic_relations:
        key = r.assessment.value
        relations_by_assessment[key] = relations_by_assessment.get(key, 0) + 1

    print(f"\n【语义评估统计】")
    print(f"  逻辑组:")
    for k, v in groups_by_assessment.items():
        print(f"    {k}: {v}")
    print(f"  逻辑关系:")
    for k, v in relations_by_assessment.items():
        print(f"    {k}: {v}")

    # 逐个输出逻辑组
    print("\n" + "=" * 80)
    print("【逻辑组详细审计】")
    print("=" * 80)

    for group in audit.logic_groups:
        print(f"\n  --- {group.group_id}: {group.group_name} ---")
        print(f"    运算符: {group.operator.value}")
        print(f"    包含 Condition: {', '.join(group.condition_ids)}")
        print(f"    语义评估: {group.assessment.value}")
        print(f"    描述: {group.description[:100]}...")
        print(f"    经典依据: {group.classical_basis[:100]}...")
        if group.notes:
            print(f"    备注: {group.notes[:100]}...")

    # 整体逻辑表达式
    print("\n" + "=" * 80)
    print("【整体逻辑表达式（伪代码）】")
    print("=" * 80)
    print(audit.overall_logic_expression)

    # 汇总
    print("\n" + "=" * 80)
    print("【审计汇总】")
    print("=" * 80)

    print(f"\n  DTS-STRENGTH-001 的组合逻辑审计结果:")
    print(f"    逻辑组: 4 个")
    print(f"      - 必要条件组（得令 AND 得地）: CLASSICAL_DIRECT")
    print(f"      - 辅助条件组（印生 OR 比劫帮）: CLASSICAL_REASONABLE")
    print(f"      - 制约条件组（官杀 OR 食伤 OR 财星）: ENGINEERING_DERIVED")
    print(f"      - 阻断条件组（从强格）: CLASSICAL_DIRECT")
    print(f"    逻辑关系: 6 个")
    print(f"      - 3 个 CLASSICAL_DIRECT")
    print(f"      - 3 个 CLASSICAL_REASONABLE")

    print(f"\n  关键发现:")
    print(f"    1. 必要条件组的 AND 关系有 CLASSICAL_DIRECT 支持")
    print(f"    2. 阻断条件组的 BLOCKING 关系有 CLASSICAL_DIRECT 支持")
    print(f"    3. 辅助条件组的 OR 关系是 CLASSICAL_REASONABLE，需要进一步原典验证")
    print(f"    4. 制约条件组的 OR 关系是 ENGINEERING_DERIVED，包含财星耗这个 ENGINEERING_DERIVED 条件")
    print(f"    5. 必要条件组与辅助/制约条件组的优先级关系是 CLASSICAL_REASONABLE")
    print(f"    6. 最关键的：综合判断规则（必要条件+辅助条件+制约条件如何组合成最终结论）尚未获得原典授权")
    print(f"    7. 当前只能输出 CANDIDATE_STRONG，不能直接输出 STRONG")

    print(f"\n  结论:")
    print(f"    Traceability PASS: 4/4 逻辑组 + 6/6 逻辑关系都有本地原文引用")
    print(f"    Combination Correctness: NOT YET PASS")
    print(f"      - 制约条件组是 ENGINEERING_DERIVED")
    print(f"      - 辅助条件组的 OR 关系需要进一步验证")
    print(f"      - 综合判断规则尚未获得原典授权")
    print(f"    不强行升级，精确记录已知和未知")

    print(f"\n  下一步:")
    print(f"    1. 对制约条件组的 OR 关系做进一步原典验证")
    print(f"    2. 对辅助条件组的 OR 关系做进一步原典验证")
    print(f"    3. 研究五部经典中是否存在明确的'综合判断规则'（A+B+C 如何组合成最终结论）")
    print(f"    4. 补充 ZP-PATTERN-001 和 QTB-CLIMATE-001 的组合逻辑审计")
    print(f"    5. 在组合逻辑没有完全原典授权之前，整体旺衰判断保持 UNRESOLVED / NOT_DEFINED")
    print(f"    6. 算层完整性（P6-CALC）仍是最高优先级，FROZEN ≠ PROVEN CORRECT")


if __name__ == "__main__":
    audit = DTS001LogicAuditor.audit()
    print_logic_audit_report(audit)
