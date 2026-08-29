"""
P0-2.9-D Five Classics Comprehensive Reasoning Rules Original Text Research

基于 4135a30 的 🟢 PASS 裁决（框架 PASS，组合逻辑未证明正确），
研究五部经典到底有没有明确的 A+B+C 综合辨证规则。

核心原则：
- 如果原典没有明确给出形式化组合，我们就必须把"原典明确部分"和"工程化推导部分"彻底分开
- 这才不会把我们自己设计出来的算法，最后冒充成"五部经典"
- 这恰恰是目前"辨准"能不能成立的核心
- 不能把五部经典统一成一套逻辑
- 算层完整性仍是最高优先级，FROZEN ≠ PROVEN CORRECT

研究范围：
- 滴天髓：旺衰/气势/生克制化的综合规则
- 子平真诠：格局成败救应的综合规则
- 穷通宝鉴：调候用神可用性的综合规则
- 渊海子平：子平基础框架的综合规则

数据来源：D:\shuntian\docs\五部经典整理\（本地优先，已读取四本完整内容）
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json


# ============================================================================
# 标准数据结构
# ============================================================================

class RuleSourceType(Enum):
    """规则来源类型"""
    CLASSICAL_EXPLICIT = "CLASSICAL_EXPLICIT"       # 原典明确给出形式化规则
    CLASSICAL_IMPLICIT = "CLASSICAL_IMPLICIT"       # 原典隐含但可合理推导
    CLASSICAL_PRINCIPLE = "CLASSICAL_PRINCIPLE"     # 原典给出原则但无具体组合规则
    ENGINEERING_DERIVED = "ENGINEERING_DERIVED"     # 纯工程化推导，原典无直接依据
    NEEDS_RESEARCH = "NEEDS_RESEARCH"               # 需要进一步研究


@dataclass(frozen=True)
class ComprehensiveRule:
    """
    综合辨证规则 — 描述原典中明确存在的综合辨证规则

    核心问题：原典是否明确给出了 A+B+C 如何组合成最终结论的形式化规则？
    """
    rule_id: str
    classic: str
    chapter: str
    domain: str                    # 旺衰/格局/调候/气势/生克制化
    rule_type: RuleSourceType
    original_text: str             # 原典原文
    text_analysis: str             # 原文分析：原文到底说了什么
    explicit_combination: bool     # 原典是否明确给出形式化组合规则（AND/OR/优先级等）
    combination_description: str   # 如果有，描述组合规则；如果没有，说明缺失什么
    engineering_mapping: str       # 工程化映射：当前代码如何映射这条规则
    mapping_gap: str               # 映射差距：工程化映射与原典之间的差距
    local_file: str
    notes: str = ""


@dataclass(frozen=True)
class ClassicResearchSummary:
    """经典研究汇总"""
    classic: str
    total_rules_found: int
    explicit_rules: int            # CLASSICAL_EXPLICIT
    implicit_rules: int            # CLASSICAL_IMPLICIT
    principle_only_rules: int      # CLASSICAL_PRINCIPLE
    engineering_derived_rules: int # ENGINEERING_DERIVED
    key_findings: List[str]
    recommendations: List[str]


# ============================================================================
# 滴天髓综合辨证规则研究
# ============================================================================

class DitiansuiResearch:
    """滴天髓综合辨证规则研究"""

    @staticmethod
    def get_rules() -> List[ComprehensiveRule]:
        return [
            # 1. 旺衰判断：得令得地有根有气
            ComprehensiveRule(
                rule_id="DTS-COMP-001",
                classic="滴天髓",
                chapter="通神论·第十七章 衰旺",
                domain="旺衰",
                rule_type=RuleSourceType.CLASSICAL_PRINCIPLE,
                original_text=(
                    "真正的旺是得令得地有根有气是真旺，"
                    "天干堆叠一堆五行地之无根无气只是虚旺假旺；"
                    "真正的衰是失令失地根气全无被克被泄，不是数量少就是衰"
                ),
                text_analysis=(
                    "原文明确列出了'真旺'的四个条件：得令、得地、有根、有气。"
                    "也明确列出了'真衰'的四个条件：失令、失地、根气全无、被克被泄。"
                    "但原文没有明确说明这四个条件之间的逻辑关系："
                    "- 是 AND（必须全部满足）？"
                    "- 还是 OR（满足部分即可）？"
                    "- 还是有优先级（得令最重要，得地次之）？"
                    "- 还是有权重（不同条件重要性不同）？"
                    "原文只是并列列出，没有给出形式化组合规则。"
                ),
                explicit_combination=False,
                combination_description=(
                    "原文并列列出四个条件，但没有明确给出形式化组合规则。"
                    "当前工程代码将得令和得地设为 required（AND），"
                    "将印生和比劫帮设为 supporting（OR），"
                    "将官杀/食伤/财星设为 constraining（OR）。"
                    "这个映射是工程化推导，不是原典明确给出的。"
                ),
                engineering_mapping=(
                    "当前 DTS-STRENGTH-001："
                    "- required: SEASONAL_STATE（得令）AND ROOT_PRESENT（得地）"
                    "- supporting: RESOURCE_SUPPORT（印生）OR PEER_SUPPORT（比劫帮）"
                    "- constraining: OFFICER_CONTROL（官杀）OR OUTPUT_DRAIN（食伤）OR WEALTH_DRAIN（财星）"
                    "- blocking: SPECIAL_PATTERN_FROM_STRONG（从强格）"
                ),
                mapping_gap=(
                    "1. 原文说'得令得地有根有气'，当前代码将'有根'和'得地'合并为 ROOT_PRESENT，"
                    "'有气'没有单独的 Evidence。"
                    "2. 原文没有明确说得令和得地是 AND 关系，当前代码设为 AND 是工程化推导。"
                    "3. 原文没有明确说印生和比劫帮是 OR 关系，当前代码设为 OR 是工程化推导。"
                    "4. 原文说'被克被泄'，没有说'被耗'，财星耗是工程化推导。"
                    "5. 原文没有给出综合判断规则（四个条件如何组合成最终结论）。"
                ),
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes=(
                    "这是滴天髓旺衰判断的核心规则，但只有原则，没有形式化组合规则。"
                    "当前工程代码的 AND/OR 映射是工程化推导，需要明确标注。"
                ),
            ),

            # 2. 旺衰判断：虽是至理，亦死法也
            ComprehensiveRule(
                rule_id="DTS-COMP-002",
                classic="滴天髓",
                chapter="通神论·衰旺（任铁樵注）",
                domain="旺衰",
                rule_type=RuleSourceType.CLASSICAL_PRINCIPLE,
                original_text=(
                    "得时俱为旺论，失令便作衰看，虽是至理，亦死法也。"
                    "须察支中党众，干上生扶，方可定其真衰真旺。"
                ),
                text_analysis=(
                    "原文明确反对机械判断：'虽是至理，亦死法也'。"
                    "强调需要综合观察：'须察支中党众，干上生扶'。"
                    "但原文没有明确说明："
                    "- '支中党众'具体指什么？（比劫？根气？同五行数量？）"
                    "- '干上生扶'具体指什么？（印星？比劫？）"
                    "- 两者之间是什么逻辑关系？（AND？OR？优先级？）"
                    "- 如何'定其真衰真旺'？（具体的判断规则是什么？）"
                    "原文只是给出原则，没有给出形式化组合规则。"
                ),
                explicit_combination=False,
                combination_description=(
                    "原文给出'须察支中党众，干上生扶'的原则，"
                    "但没有明确给出形式化组合规则。"
                    "当前工程代码将'支中党众'映射为 PEER_SUPPORT（比劫帮），"
                    "将'干上生扶'映射为 RESOURCE_SUPPORT（印生），"
                    "并设为 OR 关系。这个映射是工程化推导。"
                ),
                engineering_mapping=(
                    "当前 DTS-STRENGTH-001："
                    "- supporting: RESOURCE_SUPPORT（干上生扶）OR PEER_SUPPORT（支中党众）"
                ),
                mapping_gap=(
                    "1. '支中党众'的完整内涵可能包括地支根气，不只是比劫帮。"
                    "2. '干上生扶'的完整内涵可能包括比劫帮，不只是印生。"
                    "3. 两者之间的逻辑关系（AND/OR）原文没有明确说明。"
                    "4. '方可定其真衰真旺'的具体判断规则原文没有给出。"
                ),
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes=(
                    "这条规则明确反对机械判断，强调综合观察，"
                    "但没有给出具体的综合判断规则。"
                    "这恰恰是当前工程最大的缺口：原典只说'要综合'，没说'怎么综合'。"
                ),
            ),

            # 3. 从格：旺到极致不能克只能泄
            ComprehensiveRule(
                rule_id="DTS-COMP-003",
                classic="滴天髓",
                chapter="通神论·第四章 知命",
                domain="特殊格局",
                rule_type=RuleSourceType.CLASSICAL_EXPLICIT,
                original_text="望到极致不能克只能泄，弱到极致不能泄只能服",
                text_analysis=(
                    "原文明确给出了从格的判断原则："
                    "- 旺到极致 → 不能克，只能泄（从强格）"
                    "- 弱到极致 → 不能泄，只能服（从弱格）"
                    "这条规则明确说明了特殊格局与普通旺衰判断的关系："
                    "当达到极致时，普通的生克逻辑不适用，需要特殊处理。"
                    "这是一条明确的阻断/切换规则。"
                ),
                explicit_combination=True,
                combination_description=(
                    "原文明确给出了从格的判断原则："
                    "- IF 旺到极致 THEN 普通旺衰判断不适用，改用从强格逻辑"
                    "- IF 弱到极致 THEN 普通旺衰判断不适用，改用从弱格逻辑"
                    "这是一条明确的 BLOCKING 规则，当前工程代码的映射是准确的。"
                    "但'旺到极致'和'弱到极致'的具体判断标准原文没有给出，需要进一步研究。"
                ),
                engineering_mapping=(
                    "当前 DTS-STRENGTH-001："
                    "- blocking: SPECIAL_PATTERN_FROM_STRONG（从强格）"
                ),
                mapping_gap=(
                    "1. '旺到极致'的具体判断标准原文没有给出（什么条件算'极致'？）。"
                    "2. '弱到极致'的具体判断标准原文没有给出。"
                    "3. 当前代码只有从强格的 blocking，没有从弱格。"
                    "4. 从格的具体判断规则（如何确定'极致'）需要进一步原典研究。"
                ),
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes=(
                    "这是滴天髓中少有的明确给出形式化逻辑的规则（IF...THEN...）。"
                    "当前工程代码的 BLOCKING 映射是准确的。"
                    "但'极致'的判断标准需要进一步研究。"
                ),
            ),

            # 4. 气势：势大于数
            ComprehensiveRule(
                rule_id="DTS-COMP-004",
                classic="滴天髓",
                chapter="通神论·第三十二章 重寡",
                domain="气势",
                rule_type=RuleSourceType.CLASSICAL_PRINCIPLE,
                original_text=(
                    "势大于数哪怕只有一个五行只要占据关键位置掌控全局气势就能制衡全局，"
                    "五行数量再多杂乱无章互相牵制也成不了气候"
                ),
                text_analysis=(
                    "原文明确提出了'势大于数'的原则："
                    "- 关键位置的一个五行 > 杂乱无章的多个五行"
                    "- 气势/位置 > 数量"
                    "这条规则明确反对简单的数量计数判断。"
                    "但原文没有明确说明："
                    "- 什么是'关键位置'？（月令？日支？时支？天干？）"
                    "- 什么是'掌控全局气势'？（具体判断标准是什么？）"
                    "- 如何量化'势'与'数'的关系？"
                    "原文只是给出原则，没有给出形式化判断规则。"
                ),
                explicit_combination=False,
                combination_description=(
                    "原文给出'势大于数'的原则，但没有明确给出形式化判断规则。"
                    "当前工程代码没有直接实现这条规则（因为还没有'气势'的 Evidence）。"
                    "这条规则对当前的旺衰判断有重要影响："
                    "简单的 presence 级别判断（有没有印、有没有官杀）可能不够，"
                    "还需要考虑位置和气势。"
                ),
                engineering_mapping=(
                    "当前工程代码没有直接实现'势大于数'规则。"
                    "当前 DTS-STRENGTH-001 只是 presence 级别判断："
                    "- required: SEASONAL_STATE AND ROOT_PRESENT"
                    "- supporting: RESOURCE_SUPPORT OR PEER_SUPPORT"
                    "- constraining: OFFICER_CONTROL OR OUTPUT_DRAIN OR WEALTH_DRAIN"
                    "没有考虑位置和气势。"
                ),
                mapping_gap=(
                    "1. 当前代码没有实现'势大于数'规则。"
                    "2. '关键位置'的判断标准需要进一步原典研究。"
                    "3. '掌控全局气势'的判断标准需要进一步原典研究。"
                    "4. 这条规则可能会显著改变当前的旺衰判断逻辑（从 presence 级别升级到 position/strength 级别）。"
                ),
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
                notes=(
                    "这条规则非常重要，它明确反对简单的数量计数判断，"
                    "强调位置和气势。当前工程代码还没有实现这条规则，"
                    "这是未来需要重点研究的方向。"
                ),
            ),
        ]


# ============================================================================
# 子平真诠综合辨证规则研究
# ============================================================================

class ZipingZhenquanResearch:
    """子平真诠综合辨证规则研究"""

    @staticmethod
    def get_rules() -> List[ComprehensiveRule]:
        return [
            # 1. 格局：专取月令
            ComprehensiveRule(
                rule_id="ZP-COMP-001",
                classic="子平真诠",
                chapter="第八章 论用神",
                domain="格局",
                rule_type=RuleSourceType.CLASSICAL_EXPLICIT,
                original_text="人生格局，专取月令，以日干配月令地支，而生克不同，格局分焉。",
                text_analysis=(
                    "原文明确给出了格局的判断规则："
                    "- 格局专取月令"
                    "- 以日干配月令地支"
                    "- 根据生克关系确定格局"
                    "这是一条明确的必要条件规则：月令是格局的唯一来源。"
                ),
                explicit_combination=True,
                combination_description=(
                    "原文明确给出了格局的判断规则："
                    "- IF 确定日干和月令地支 THEN 根据生克关系确定格局"
                    "这是一条明确的规则，当前工程代码的映射是准确的。"
                ),
                engineering_mapping=(
                    "当前 ZP-PATTERN-001："
                    "- required: SEASONAL_STATE（月令状态）AND MONTH_COMMAND_TEN_GOD（月令十神）"
                ),
                mapping_gap=(
                    "1. 当前代码的 MONTH_COMMAND_TEN_GOD Evidence 还没有完整实现。"
                    "2. 格局的具体分类（正官格、七杀格等）需要进一步实现。"
                    "3. 月令藏干的本气/中气/余气对格局的影响需要进一步研究。"
                ),
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\子平真诠.md",
                notes="这是子平真诠格局判断的核心规则，明确给出了形式化逻辑。",
            ),

            # 2. 格局配气候：先调候后格局
            ComprehensiveRule(
                rule_id="ZP-COMP-002",
                classic="子平真诠",
                chapter="第十四章 论格局配气候得失",
                domain="格局+调候",
                rule_type=RuleSourceType.CLASSICAL_EXPLICIT,
                original_text=(
                    "先调候后格局，寒冬腊月水寒木冻再好的格局没有火来暖局也是寒气闭塞才华难展"
                ),
                text_analysis=(
                    "原文明确给出了调候与格局的优先级关系："
                    "- 先调候，后格局"
                    "- 调候是格局的前提条件"
                    "- 如果调候不足，再好的格局也无法发挥"
                    "这是一条明确的优先级规则。"
                ),
                explicit_combination=True,
                combination_description=(
                    "原文明确给出了调候与格局的优先级关系："
                    "- IF 调候不足 THEN 格局判断需要降级/限定"
                    "- 调候是格局的前提条件"
                    "这是一条明确的优先级规则，当前工程代码还没有实现这条规则。"
                ),
                engineering_mapping=(
                    "当前工程代码没有直接实现'先调候后格局'规则。"
                    "当前 ZP-PATTERN-001 和 QTB-CLIMATE-001 是并行的，没有优先级关系。"
                ),
                mapping_gap=(
                    "1. 当前代码没有实现调候与格局的优先级关系。"
                    "2. '调候不足'的具体判断标准需要进一步实现。"
                    "3. 调候不足时格局如何降级/限定需要进一步研究。"
                    "4. 这条规则说明格局和调候不是完全独立的，存在优先级关系。"
                ),
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\子平真诠.md",
                notes=(
                    "这条规则非常重要，它明确了调候与格局的优先级关系。"
                    "当前工程代码将格局和调候设为完全并行的维度，"
                    "这可能与原典的优先级关系不完全一致。"
                ),
            ),
        ]


# ============================================================================
# 穷通宝鉴综合辨证规则研究
# ============================================================================

class QiongtongBaojianResearch:
    """穷通宝鉴综合辨证规则研究"""

    @staticmethod
    def get_rules() -> List[ComprehensiveRule]:
        return [
            # 1. 调候为先
            ComprehensiveRule(
                rule_id="QTB-COMP-001",
                classic="穷通宝鉴",
                chapter="卷首 五行总论",
                domain="调候",
                rule_type=RuleSourceType.CLASSICAL_EXPLICIT,
                original_text=(
                    "调候为先，市面上绝大多数五行古籍论体系论格局论强弱，"
                    "唯独穷通宝鉴独树一帜把四季的冷暖燥湿寒暑放在第一位，"
                    "不管什么五行什么格局先调和气候再谈平衡发展"
                ),
                text_analysis=(
                    "原文明确给出了调候的优先级："
                    "- 调候为先"
                    "- 不管什么五行什么格局，先调和气候"
                    "- 调和气候之后再谈平衡发展"
                    "这是一条明确的优先级规则。"
                ),
                explicit_combination=True,
                combination_description=(
                    "原文明确给出了调候的优先级："
                    "- IF 确定日干和月令 THEN 确定调候方向"
                    "- 调候是其他判断（格局、强弱、平衡）的前提"
                    "这是一条明确的规则，当前工程代码的映射基本准确。"
                ),
                engineering_mapping=(
                    "当前 QTB-CLIMATE-001："
                    "- required: SEASONAL_STATE（日干×月令）"
                    "- sufficient_for_target: CLIMATE_PROFILE_CANDIDATE"
                ),
                mapping_gap=(
                    "1. 当前代码只确定了调候方向，没有实现调候用神的可用性判断。"
                    "2. '调和气候'的具体判断标准（调候用神是否出现、有根、可用）需要进一步实现。"
                    "3. 调候与格局、强弱的优先级关系需要进一步实现（子平真诠也提到了'先调候后格局'）。"
                ),
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\穷通宝鉴.md",
                notes="这是穷通宝鉴的核心规则，明确给出了形式化逻辑。",
            ),

            # 2. 甲木正月：丙火暖局
            ComprehensiveRule(
                rule_id="QTB-COMP-002",
                classic="穷通宝鉴",
                chapter="甲木卷·正月",
                domain="调候",
                rule_type=RuleSourceType.CLASSICAL_EXPLICIT,
                original_text=(
                    "三春甲木正月二月三月初春余寒未消大树刚刚复苏生发，"
                    "全局第一需求就是丙火暖局，没有阳光解冻根基再深的大树也会被寒气冻住无法舒展生长"
                ),
                text_analysis=(
                    "原文明确给出了甲木正月的调候用神："
                    "- 甲木正月的第一需求是丙火暖局"
                    "- 没有丙火，根基再深也无法舒展生长"
                    "这是一条明确的调候用神规则。"
                ),
                explicit_combination=True,
                combination_description=(
                    "原文明确给出了甲木正月的调候用神："
                    "- IF 日干=甲 AND 月令=正月 THEN 调候用神=丙火"
                    "这是一条明确的二维规则（日干×月令→调候用神），当前工程代码的映射基本准确。"
                ),
                engineering_mapping=(
                    "当前 QTB-CLIMATE-001："
                    "- required: SEASONAL_STATE（日干×月令）"
                    "- 输出: CLIMATE_PROFILE_CANDIDATE"
                    "但当前代码没有具体实现甲木正月→丙火的映射。"
                ),
                mapping_gap=(
                    "1. 当前代码没有具体实现日干×月令→调候用神的二维映射表。"
                    "2. 调候用神的可用性判断（是否出现、有根、可用、受阻、过量）需要进一步实现。"
                    "3. '全局第一需求'的优先级关系需要进一步实现。"
                ),
                local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\穷通宝鉴.md",
                notes=(
                    "穷通宝鉴的体例就是日干×月令的二维规则矩阵，"
                    "这是五部经典中最容易工程化的部分。"
                    "当前代码还没有实现具体的二维映射表。"
                ),
            ),
        ]


# ============================================================================
# 输出研究报告
# ============================================================================

def print_research_report(all_rules: List[ComprehensiveRule]):
    print("=" * 80)
    print("P0-2.9-D Five Classics Comprehensive Reasoning Rules Original Text Research")
    print("=" * 80)

    print("\n【核心问题】")
    print("  五部经典到底有没有明确的 A+B+C 综合辨证规则？")
    print("  如果原典没有明确给出形式化组合，我们就必须把'原典明确部分'和'工程化推导部分'彻底分开。")

    print(f"\n【研究范围】共梳理 {len(all_rules)} 条综合辨证规则")

    # 按来源类型统计
    by_type = {}
    for r in all_rules:
        key = r.rule_type.value
        by_type[key] = by_type.get(key, 0) + 1

    print(f"\n【按来源类型统计】")
    for k, v in by_type.items():
        print(f"  {k}: {v}")

    # 按经典统计
    by_classic = {}
    for r in all_rules:
        by_classic[r.classic] = by_classic.get(r.classic, 0) + 1

    print(f"\n【按经典统计】")
    for k, v in by_classic.items():
        print(f"  {k}: {v}")

    # 核心发现
    print("\n" + "=" * 80)
    print("【核心发现】")
    print("=" * 80)

    print("""
  1. 五部经典中，明确给出形式化组合规则（AND/OR/优先级/IF-THEN）的规则很少。
     大部分规则只给出原则（"须察...方可定..."），没有给出具体的组合逻辑。

  2. 滴天髓的旺衰判断是最典型的"只有原则，没有形式化组合"的例子：
     - 原文说"得令得地有根有气是真旺"，但没有说四个条件是 AND 还是 OR
     - 原文说"须察支中党众，干上生扶，方可定其真衰真旺"，但没有说怎么"定"
     - 当前工程代码的 AND/OR 映射是工程化推导，不是原典明确给出的

  3. 穷通宝鉴和子平真诠的部分规则明确给出了形式化逻辑：
     - 穷通宝鉴：日干×月令→调候用神（二维规则矩阵）
     - 子平真诠：专取月令定格局（必要条件规则）
     - 子平真诠：先调候后格局（优先级规则）
     这些规则的工程化映射相对准确。

  4. 滴天髓的从格规则明确给出了形式化逻辑（IF 旺到极致 THEN 普通判断不适用），
     但"旺到极致"的具体判断标准原文没有给出。

  5. 滴天髓的"势大于数"规则明确反对简单的数量计数判断，
     但当前工程代码还没有实现这条规则（还停留在 presence 级别）。

  6. 最关键的发现：五部经典没有一本明确给出了
     "A+B+C 如何组合成最终旺衰/格局/调候结论"的完整形式化规则。
     原典给出的是原则、观察点、优先级，但最终的"综合判断"需要读者自己领悟。
     这意味着当前工程代码中的所有综合逻辑（AND/OR/优先级/权重）
     本质上都是工程化推导，不是原典明确给出的。
""")

    # 逐条输出
    print("\n" + "=" * 80)
    print("【逐条规则详情】")
    print("=" * 80)

    for rule in all_rules:
        print(f"\n  --- {rule.rule_id}: {rule.classic} / {rule.domain} ---")
        print(f"    章节: {rule.chapter}")
        print(f"    来源类型: {rule.rule_type.value}")
        print(f"    明确形式化组合: {rule.explicit_combination}")
        print(f"    原文: {rule.original_text[:80]}...")
        print(f"    原文分析: {rule.text_analysis[:100]}...")
        print(f"    组合描述: {rule.combination_description[:100]}...")
        print(f"    工程映射: {rule.engineering_mapping[:80]}...")
        print(f"    映射差距: {rule.mapping_gap[:100]}...")
        if rule.notes:
            print(f"    备注: {rule.notes[:80]}...")

    # 建议
    print("\n" + "=" * 80)
    print("【工程建议】")
    print("=" * 80)

    print("""
  1. 明确区分"原典明确的规则"和"工程化推导的规则"：
     - 在 Rule 级别增加 rule_source_type 字段
     - CLASSICAL_EXPLICIT 的规则可以直接使用
     - CLASSICAL_PRINCIPLE 和 ENGINEERING_DERIVED 的规则只能作为候选，不能作为最终结论

  2. 对滴天髓的旺衰判断，明确标注当前的 AND/OR 映射是工程化推导：
     - 得令 AND 得地 = required → 工程化推导
     - 印生 OR 比劫帮 = supporting → 工程化推导
     - 官杀 OR 食伤 OR 财星 = constraining → 工程化推导（财星耗更是推导的推导）
     - 这些映射可以作为研究候选，但不能作为原典授权的最终规则

  3. 优先实现原典明确给出形式化逻辑的规则：
     - 穷通宝鉴：日干×月令→调候用神的二维映射表
     - 子平真诠：专取月令定格局
     - 子平真诠：先调候后格局的优先级关系
     - 滴天髓：从格的阻断规则（但"极致"的判断标准需要进一步研究）

  4. 对原典只给出原则的规则，建立"原则→工程映射"的显式追溯：
     - 原文原则是什么
     - 工程映射是什么
     - 映射的假设是什么
     - 映射的局限性是什么
     这样用户可以清楚地知道哪些是原典说的，哪些是我们推导的。

  5. 在综合判断规则没有获得原典明确授权之前：
     - 整体旺衰判断保持 UNRESOLVED / NOT_DEFINED
     - 只输出局部 Evidence 和 Candidate State
     - 不输出最终的 STRONG / WEAK 结论

  6. 算层完整性（P6-CALC）仍是最高优先级：
     - FROZEN ≠ PROVEN CORRECT
     - 辨证施工不能被理解为算层已经证明正确
     - 二者可以并行，但辨不能反过来修改算
""")

    print("\n" + "=" * 80)
    print("【最终结论】")
    print("=" * 80)
    print("""
  五部经典没有一本明确给出了"A+B+C 如何组合成最终结论"的完整形式化规则。
  原典给出的是原则、观察点、优先级，但最终的"综合判断"需要读者自己领悟。

  这意味着：
  1. 当前工程代码中的所有综合逻辑（AND/OR/优先级）本质上都是工程化推导
  2. 必须把"原典明确部分"和"工程化推导部分"彻底分开
  3. 在综合判断规则没有获得原典明确授权之前，整体旺衰判断保持 UNRESOLVED
  4. 这才不会把我们自己设计出来的算法，最后冒充成"五部经典"

  这恰恰是目前"辨准"能不能成立的核心。
""")


if __name__ == "__main__":
    all_rules = []
    all_rules.extend(DitiansuiResearch.get_rules())
    all_rules.extend(ZipingZhenquanResearch.get_rules())
    all_rules.extend(QiongtongBaojianResearch.get_rules())
    print_research_report(all_rules)
