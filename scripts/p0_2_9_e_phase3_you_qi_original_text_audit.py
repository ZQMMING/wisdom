"""
P0-2.9-E Phase 3: "You Qi" (有气) Original Text Evidence Audit

基于 0e3eb93 的 🟢 PASS / CONDITIONAL 裁决，
下一步不是继续写代码，而是做「有气」原典证据审计。

核心原则：
- 合理 ≠ 原典证明
- 把《滴天髓》全文所有"气 / 有气 / 无气 / 根 / 得令 / 得地 / 势 / 流通"等上下文全部拉出来
- 建立：原文 ↓ 语义 ↓ Primitive ↓ Canonical Facts ↓ 关系分析
- 分析：是否同义？是否包含关系？是否因果关系？是否只是并列观察维度？
- 特别关注"有气"的原典含义，以及它与得令、有根、气势的关系
- 明确标记哪些是原典明确的，哪些是合理假说，哪些是工程推导
- 算层完整性（P6-CALC）仍是最高优先级，FROZEN ≠ PROVEN CORRECT

数据来源：D:\shuntian\docs\五部经典整理\（本地优先，已读取滴天髓全文）
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import json


# ============================================================================
# 标准数据结构
# ============================================================================

class ConceptRelationType(Enum):
    """概念之间的关系类型"""
    SYNONYM = "SYNONYM"                    # 同义
    SUBSET = "SUBSET"                      # 包含（A ⊂ B）
    SUPERSET = "SUPERSET"                  # 被包含（A ⊃ B）
    CAUSAL = "CAUSAL"                      # 因果（A → B）
    PARALLEL_OBSERVATION = "PARALLEL_OBSERVATION"  # 并列观察维度
    OVERLAP = "OVERLAP"                    # 重叠（相关但不等同）
    UNCLEAR = "UNCLEAR"                    # 不明确
    INDEPENDENT = "INDEPENDENT"            # 独立


class EvidenceLevel(Enum):
    """证据等级"""
    CLASSICAL_EXPLICIT = "CLASSICAL_EXPLICIT"    # 原典明确
    CLASSICAL_IMPLICIT = "CLASSICAL_IMPLICIT"    # 原典隐含
    REASONABLE_HYPOTHESIS = "REASONABLE_HYPOTHESIS"  # 合理假说
    ENGINEERING_DERIVED = "ENGINEERING_DERIVED"  # 工程推导
    NOT_SUPPORTED = "NOT_SUPPORTED"              # 不支持


@dataclass(frozen=True)
class OriginalTextEvidence:
    """原文证据 — 滴天髓全文中的相关原文片段"""
    evidence_id: str
    chapter: str
    original_text: str
    context: str                       # 上下文说明
    key_concepts: List[str]            # 涉及的核心概念（气/有气/无气/根/得令/得地/势/流通等）
    semantic_analysis: str             # 语义分析：这段原文到底表达了什么
    primitive_mapping: Dict[str, str]  # Primitive 映射：概念 → Primitive
    canonical_facts: List[str]         # 依赖的 Canonical Facts
    relation_to_you_qi: str           # 与"有气"的关系
    evidence_level: EvidenceLevel      # 证据等级
    notes: str = ""


@dataclass(frozen=True)
class ConceptRelation:
    """概念关系 — 两个概念之间的关系分析"""
    relation_id: str
    concept_a: str
    concept_b: str
    relation_type: ConceptRelationType
    classical_basis: str               # 原典依据
    analysis: str                      # 关系分析
    evidence_level: EvidenceLevel      # 证据等级
    is_proven: bool                    # 是否原典明确证明


@dataclass(frozen=True)
class YouQiDefinitionAudit:
    """「有气」定义审计 — 综合所有原文证据后的定义审计"""
    current_definition_hypothesis: str  # 当前的定义假说
    classical_explicit_parts: List[str] # 原典明确支持的部分
    classical_implicit_parts: List[str] # 原典隐含支持的部分
    reasonable_hypothesis_parts: List[str]  # 合理假说部分
    engineering_derived_parts: List[str]    # 工程推导部分
    not_supported_parts: List[str]          # 不支持的部分
    final_assessment: str                    # 最终评估
    recommendations: List[str]               # 建议


# ============================================================================
# 滴天髓全文原文证据提取
# ============================================================================

class DitiansuiOriginalTextExtractor:
    """滴天髓全文原文证据提取器"""

    @staticmethod
    def get_all_evidence() -> List[OriginalTextEvidence]:
        return [
            # 1. 第十七章 衰旺 — 最核心的"有气"原文
            OriginalTextEvidence(
                evidence_id="DTS-EVID-001",
                chapter="通神论·第十七章 衰旺",
                original_text=(
                    "真正的旺是得令得地有根有气是真旺，"
                    "天干堆叠一堆五行地之无根无气只是虚旺假旺；"
                    "真正的衰是失令失地根气全无被克被泄，不是数量少就是衰"
                ),
                context=(
                    "这是滴天髓关于旺衰判断的核心段落，明确列出了'真旺'的四个条件："
                    "得令、得地、有根、有气。同时列出了'真衰'的条件：失令、失地、根气全无、被克被泄。"
                ),
                key_concepts=["有气", "无气", "根", "得令", "得地", "真旺", "真衰", "虚旺假旺"],
                semantic_analysis=(
                    "这段原文明确将'有气'列为'真旺'的四个并列条件之一，与'得令'、'得地'、'有根'并列。"
                    "这说明："
                    "1. '有气'是一个独立的观察维度，不等于'得令'或'有根'（否则不需要并列）。"
                    "2. '有气'与'无根无气'相对，说明'气'与'根'是相关但不同的概念。"
                    "3. '根气全无'被列为真衰的条件，说明'根'和'气'经常一起出现，但可能是两个不同维度。"
                    "4. 原文没有明确说明'有气'的具体含义，只是将其列为真旺的条件之一。"
                ),
                primitive_mapping={
                    "得令": "DE_LING (STATE)",
                    "得地": "DE_DI (STATE)",
                    "有根": "YOU_GEN (RELATION/STATE)",
                    "有气": "YOU_QI (STATE) — 含义不明确",
                    "无根无气": "NO_ROOT_NO_QI (STATE)",
                    "根气全无": "ROOT_QI_NONE (STATE)",
                },
                canonical_facts=[
                    "DayMaster（日主天干）",
                    "MonthBranch（月令地支）",
                    "MonthBranchHiddenStems（月令藏干）",
                    "AllBranchesHiddenStems（全部地支藏干）",
                    "FiveElementRelationship（五行关系）",
                ],
                relation_to_you_qi=(
                    "这是'有气'最直接的原典依据。原文将'有气'与'得令'、'得地'、'有根'并列为真旺的四个条件，"
                    "说明'有气'是一个独立的观察维度，但具体含义原典没有明确说明。"
                ),
                evidence_level=EvidenceLevel.CLASSICAL_EXPLICIT,
                notes=(
                    "【核心证据】这是'有气'最直接的原典依据。"
                    "关键发现：'有气'与'得令'、'得地'、'有根'并列，说明它是独立维度。"
                    "但'有气'的具体含义原典没有明确说明，需要从其他上下文推断。"
                ),
            ),

            # 2. 第十五章 月令 — 气场相关
            OriginalTextEvidence(
                evidence_id="DTS-EVID-002",
                chapter="通神论·第十五章 月令",
                original_text=(
                    "月令是全局提纲统领四季气场影响力最大但绝对不能一锤定音不要学死板的唯月令论"
                ),
                context=(
                    "这是滴天髓关于月令的核心段落，强调月令的重要性，但反对机械的唯月令论。"
                ),
                key_concepts=["气场", "月令", "得令", "四季"],
                semantic_analysis=(
                    "这段原文提到'四季气场'，说明'气'与季节/月令有关。"
                    "月令统领四季气场，说明得令可能是'有气'的来源之一。"
                    "但原文没有明确说'得令 = 有气'，只是说月令统领气场。"
                ),
                primitive_mapping={
                    "月令": "MONTH_BRANCH (FACT)",
                    "四季气场": "SEASONAL_QI (STATE) — 与得令相关",
                },
                canonical_facts=[
                    "MonthBranch（月令地支）",
                    "Season（季节）",
                    "FiveElementOfMonth（月令五行）",
                ],
                relation_to_you_qi=(
                    "这段原文暗示'气'与季节/月令有关，得令可能是'有气'的来源之一。"
                    "但原文没有明确说'得令 = 有气'，只是说月令统领气场。"
                ),
                evidence_level=EvidenceLevel.CLASSICAL_IMPLICIT,
                notes=(
                    "这段原文暗示'气'与季节/月令有关，但没有明确说明'有气'的定义。"
                    "得令可能是'有气'的来源之一，但不是唯一来源。"
                ),
            ),

            # 3. 第三十二章 重寡 — 气势相关
            OriginalTextEvidence(
                evidence_id="DTS-EVID-003",
                chapter="通神论·第三十二章 重寡",
                original_text=(
                    "势大于数哪怕只有一个五行只要占据关键位置掌控全局气势就能制衡全局，"
                    "五行数量再多杂乱无章互相牵制也成不了气候"
                ),
                context=(
                    "这是滴天髓关于'势大于数'的核心段落，强调气势比数量更重要。"
                ),
                key_concepts=["气势", "势", "数", "关键位置", "全局气势", "掌控"],
                semantic_analysis=(
                    "这段原文明确提出'势大于数'的原则，强调："
                    "1. 一个关键位置的五行可以掌控全局气势。"
                    "2. 五行数量多但杂乱无章、互相牵制，也成不了气候。"
                    "3. '气势'与'数量'是不同的维度，气势比数量更重要。"
                    "但原文没有明确说明'气势'与'有气'的关系。"
                    "'气势'可能是比'有气'更高层次的概念，涉及全局结构。"
                ),
                primitive_mapping={
                    "气势": "QI_SHI (STRUCTURE) — 全局力量结构",
                    "势": "SHI (STRUCTURE)",
                    "数": "COUNT (FACT) — 五行数量统计",
                    "关键位置": "KEY_POSITION (FACT/STATE)",
                },
                canonical_facts=[
                    "AllStemsAndBranches（全部干支）",
                    "FiveElementDistribution（五行分布）",
                    "FiveElementConcentration（五行集中度）",
                    "KeyPositions（关键位置）",
                    "CombinationsAndClashes（合冲关系）",
                ],
                relation_to_you_qi=(
                    "这段原文讨论的是'气势'，而不是'有气'。"
                    "'气势'可能是比'有气'更高层次的概念，涉及全局结构。"
                    "'有气'可能是'气势'的基础组成部分之一，但这个关系原典没有明确说明。"
                ),
                evidence_level=EvidenceLevel.CLASSICAL_EXPLICIT,
                notes=(
                    "【核心证据】这是'气势'最直接的原典依据。"
                    "关键发现：'气势'与'数量'是不同维度，气势比数量更重要。"
                    "但'气势'与'有气'的关系原典没有明确说明，需要进一步研究。"
                ),
            ),

            # 4. 衰旺章 — 虽是至理亦死法也
            OriginalTextEvidence(
                evidence_id="DTS-EVID-004",
                chapter="通神论·衰旺（任铁樵注）",
                original_text=(
                    "得时俱为旺论，失令便作衰看，虽是至理，亦死法也。"
                    "须察支中党众，干上生扶，方可定其真衰真旺。"
                ),
                context=(
                    "这是滴天髓（任铁樵注）关于旺衰判断的重要段落，强调需要综合观察，反对机械判断。"
                ),
                key_concepts=["得时", "失令", "支中党众", "干上生扶", "真衰真旺"],
                semantic_analysis=(
                    "这段原文强调："
                    "1. '得时俱为旺论，失令便作衰看'虽是至理，但也是死法。"
                    "2. 需要观察'支中党众'和'干上生扶'才能定真衰真旺。"
                    "这里的'支中党众'和'干上生扶'可能与'有气'有关："
                    "- '支中党众'可能指地支中有同五行的根气/党羽。"
                    "- '干上生扶'可能指天干有印星生扶或比劫帮身。"
                    "这些可能是'有气'的来源，但原文没有明确说'有气 = 支中党众 + 干上生扶'。"
                ),
                primitive_mapping={
                    "得时": "DE_LING (STATE)",
                    "失令": "SHI_LING (STATE)",
                    "支中党众": "BRANCH_PEER_GROUP (STATE) — 可能与有气有关",
                    "干上生扶": "STEM_SUPPORT (STATE) — 可能与有气有关",
                },
                canonical_facts=[
                    "AllBranchesHiddenStems（全部地支藏干）",
                    "AllStems（全部天干）",
                    "FiveElementRelationship（五行关系）",
                    "TenGods（十神）",
                ],
                relation_to_you_qi=(
                    "这段原文的'支中党众'和'干上生扶'可能与'有气'有关，"
                    "但原文没有明确说'有气 = 支中党众 + 干上生扶'。"
                    "这是一个合理假说，但不是原典明确的定义。"
                ),
                evidence_level=EvidenceLevel.CLASSICAL_IMPLICIT,
                notes=(
                    "这段原文的'支中党众'和'干上生扶'可能是'有气'的来源，"
                    "但这个关系是合理假说，不是原典明确的定义。"
                ),
            ),
        ]

    @staticmethod
    def get_concept_relations() -> List[ConceptRelation]:
        """概念关系分析"""
        return [
            # 1. 有气 vs 得令
            ConceptRelation(
                relation_id="REL-001",
                concept_a="有气",
                concept_b="得令",
                relation_type=ConceptRelationType.OVERLAP,
                classical_basis=(
                    "原文将'有气'与'得令'并列为真旺的四个条件之一（DTS-EVID-001）。"
                    "原文提到月令统领四季气场（DTS-EVID-002），暗示得令可能是有气的来源之一。"
                ),
                analysis=(
                    "有气与得令是相关但不等同的概念："
                    "1. 原文将两者并列为真旺的条件，说明它们是独立观察维度。"
                    "2. 月令统领气场，暗示得令可能是有气的来源之一。"
                    "3. 但有气还可能来自其他来源（生扶、同党、流通等）。"
                    "4. 因此两者是 OVERLAP（有重叠但不等同），不是 SUBSET 或 SYNONYM。"
                ),
                evidence_level=EvidenceLevel.CLASSICAL_IMPLICIT,
                is_proven=False,  # 原典没有明确说明两者的精确关系
            ),

            # 2. 有气 vs 有根
            ConceptRelation(
                relation_id="REL-002",
                concept_a="有气",
                concept_b="有根",
                relation_type=ConceptRelationType.OVERLAP,
                classical_basis=(
                    "原文将'有气'与'有根'并列为真旺的四个条件之一（DTS-EVID-001）。"
                    "原文提到'无根无气'和'根气全无'，说明根和气经常一起出现。"
                ),
                analysis=(
                    "有气与有根是相关但不等同的概念："
                    "1. 原文将两者并列为真旺的条件，说明它们是独立观察维度。"
                    "2. '无根无气'和'根气全无'说明根和气经常一起出现，但可能是两个不同维度。"
                    "3. '根'强调依托（地支藏干），'气'可能更宽泛（力量状态）。"
                    "4. 因此两者是 OVERLAP（有重叠但不等同），不是 SUBSET 或 SYNONYM。"
                    "5. 有根可能是有气的来源之一，但不是唯一来源。"
                ),
                evidence_level=EvidenceLevel.CLASSICAL_IMPLICIT,
                is_proven=False,  # 原典没有明确说明两者的精确关系
            ),

            # 3. 有气 vs 气势
            ConceptRelation(
                relation_id="REL-003",
                concept_a="有气",
                concept_b="气势",
                relation_type=ConceptRelationType.UNCLEAR,
                classical_basis=(
                    "原文讨论了'有气'（DTS-EVID-001）和'气势'（DTS-EVID-003），"
                    "但没有明确说明两者的关系。"
                ),
                analysis=(
                    "有气与气势的关系原典没有明确说明："
                    "1. '有气'是真旺的条件之一，偏向日主的力量状态。"
                    "2. '气势'是全局的力量结构，涉及位置、集中度、方向等。"
                    "3. 气势可能是比有气更高层次的概念（STRUCTURE vs STATE）。"
                    "4. 有气可能是气势的基础组成部分之一，但这个关系是假说，不是原典明确。"
                    "5. 因此当前标记为 UNCLEAR，需要进一步研究。"
                ),
                evidence_level=EvidenceLevel.REASONABLE_HYPOTHESIS,
                is_proven=False,
            ),

            # 4. 有气 vs 支中党众 + 干上生扶
            ConceptRelation(
                relation_id="REL-004",
                concept_a="有气",
                concept_b="支中党众 + 干上生扶",
                relation_type=ConceptRelationType.UNCLEAR,
                classical_basis=(
                    "原文提到'须察支中党众，干上生扶，方可定其真衰真旺'（DTS-EVID-004）。"
                    "这可能与'有气'有关，但原文没有明确说'有气 = 支中党众 + 干上生扶'。"
                ),
                analysis=(
                    "有气与'支中党众 + 干上生扶'的关系是合理假说："
                    "1. '支中党众'可能指地支中有同五行的根气/党羽。"
                    "2. '干上生扶'可能指天干有印星生扶或比劫帮身。"
                    "3. 这些可能是'有气'的来源。"
                    "4. 但原文没有明确说'有气 = 支中党众 + 干上生扶'。"
                    "5. 因此这是合理假说，不是原典明确的定义。"
                ),
                evidence_level=EvidenceLevel.REASONABLE_HYPOTHESIS,
                is_proven=False,
            ),
        ]

    @staticmethod
    def get_you_qi_definition_audit() -> YouQiDefinitionAudit:
        """「有气」定义审计"""
        return YouQiDefinitionAudit(
            current_definition_hypothesis=(
                "当前假说：有气是日主在全局中的力量状态，可能包括得令、有根、生扶、同党、流通等来源。"
            ),
            classical_explicit_parts=[
                "'有气'是真旺的四个并列条件之一（与得令、得地、有根并列）",
                "'有气'是独立的观察维度，不等于得令或有根",
                "'无根无气'和'根气全无'是真衰的表现",
            ],
            classical_implicit_parts=[
                "得令可能是有气的来源之一（月令统领四季气场）",
                "有根可能是有气的来源之一（根气经常一起出现）",
                "'支中党众'和'干上生扶'可能与有气有关",
            ],
            reasonable_hypothesis_parts=[
                "有气可能包括生扶（印星生扶）作为来源",
                "有气可能包括同党（比劫帮身）作为来源",
                "有气可能包括流通（五行流通）作为来源",
                "有气可能是气势的基础组成部分之一",
            ],
            engineering_derived_parts=[
                "将有气定义为'更广泛的力量状态'（这是工程抽象，不是原典定义）",
                "将有气的来源列举为6项（得令、有根、生扶、同党、流通、时势）（这是工程假说）",
                "将有气映射为 STATE 层（这是工程分层，不是原典分层）",
            ],
            not_supported_parts=[
                "时势（大运/流年）作为有气的原局来源（原典讨论的是原局，时势属于Temporal Context）",
                "有气 = 有根（原典将两者并列，说明不等同）",
                "有气 = 得令（原典将两者并列，说明不等同）",
                "有气 = 五行数量多（势大于数，数量多不等于有气）",
                "气势 = 有气的 SUPERSET（这是假说，不是原典明确关系）",
            ],
            final_assessment=(
                "「有气」的原典含义目前是 UNRESOLVED / RESEARCH MODEL。"
                "原典明确将'有气'列为真旺的四个并列条件之一，说明它是独立的观察维度。"
                "但原典没有明确说明'有气'的具体定义和精确内涵。"
                "当前提出的'有气 = 更广泛的力量状态，包括得令、有根、生扶、同党、流通等来源'"
                "是一个合理假说（REASONABLE_HYPOTHESIS），不是原典明确的定义（CLASSICAL_EXPLICIT）。"
                "在'有气'的原典含义没有明确之前，不能将其作为生产级 Evidence，"
                "也不能将其与得令、有根的关系固定为 SUBSET/SUPERSET。"
                "时势（大运/流年）必须暂时从有气的原局定义中移除，因为它属于 Temporal Context。"
            ),
            recommendations=[
                "【最高优先级】将 YOU_QI 标记为 UNRESOLVED / RESEARCH MODEL，不进入生产",
                "从滴天髓全文中继续搜索'气'相关上下文，寻找更多关于'有气'定义的线索",
                "明确'有气'与得令、有根的关系是 OVERLAP（有重叠但不等同），不是 SUBSET/SYNONYM",
                "将时势（大运/流年）从有气的原局定义中移除，标记为未来的 Temporal Qualifier",
                "将'有气 = 更广泛的力量状态'标记为 REASONABLE_HYPOTHESIS，不是 CLASSICAL_EXPLICIT",
                "将气势 = 有气的 SUPERSET 标记为 HYPOTHESIS，不得升级为 CLASSICAL_RELATION",
                "在'有气'的原典含义明确之前，不进入最终身强身弱组合",
                "继续保持算层完整性（P6-CALC）为最高优先级，FROZEN ≠ PROVEN CORRECT",
            ],
        )


# ============================================================================
# 输出审计报告
# ============================================================================

def print_audit_report(
    evidences: List[OriginalTextEvidence],
    relations: List[ConceptRelation],
    definition_audit: YouQiDefinitionAudit
):
    print("=" * 80)
    print("P0-2.9-E Phase 3: 「有气」原典证据审计 — 报告")
    print("=" * 80)

    print("\n【核心原则】")
    print("  1. 合理 ≠ 原典证明")
    print("  2. 把《滴天髓》全文所有'气 / 有气 / 无气 / 根 / 得令 / 得地 / 势 / 流通'等上下文全部拉出来")
    print("  3. 建立：原文 ↓ 语义 ↓ Primitive ↓ Canonical Facts ↓ 关系分析")
    print("  4. 分析：是否同义？是否包含关系？是否因果关系？是否只是并列观察维度？")
    print("  5. 算层完整性（P6-CALC）仍是最高优先级，FROZEN ≠ PROVEN CORRECT")

    print(f"\n【审计范围】")
    print(f"  原文证据: {len(evidences)} 条")
    print(f"  概念关系: {len(relations)} 个")
    print(f"  核心目标: 「有气」的原典含义与定义审计")

    # 原文证据
    print("\n" + "=" * 80)
    print("【原文证据】")
    print("=" * 80)

    for ev in evidences:
        print(f"\n{'='*60}")
        print(f"  {ev.evidence_id}: {ev.chapter}")
        print(f"  证据等级: {ev.evidence_level.value}")
        print(f"  涉及概念: {', '.join(ev.key_concepts)}")
        print(f"{'='*60}")

        print(f"\n  【原文】")
        print(f"    「{ev.original_text}」")

        print(f"\n  【上下文】")
        print(f"    {ev.context[:120]}...")

        print(f"\n  【语义分析】")
        print(f"    {ev.semantic_analysis[:200]}...")

        print(f"\n  【Primitive 映射】")
        for k, v in ev.primitive_mapping.items():
            print(f"    {k} → {v}")

        print(f"\n  【依赖 Canonical Facts】")
        for f in ev.canonical_facts:
            print(f"    - {f}")

        print(f"\n  【与「有气」的关系】")
        print(f"    {ev.relation_to_you_qi[:150]}...")

        if ev.notes:
            print(f"\n  【备注】")
            print(f"    {ev.notes[:120]}...")

    # 概念关系
    print("\n" + "=" * 80)
    print("【概念关系分析】")
    print("=" * 80)

    for rel in relations:
        proven = "✅ 原典明确" if rel.is_proven else "⚠️ 需进一步研究"
        print(f"\n  {rel.relation_id}: {rel.concept_a} ↔ {rel.concept_b}")
        print(f"    关系类型: {rel.relation_type.value} ({proven})")
        print(f"    证据等级: {rel.evidence_level.value}")
        print(f"    原典依据: {rel.classical_basis[:100]}...")
        print(f"    关系分析: {rel.analysis[:150]}...")

    # 定义审计
    print("\n" + "=" * 80)
    print("【「有气」定义审计】")
    print("=" * 80)

    print(f"\n  当前定义假说: {definition_audit.current_definition_hypothesis[:120]}...")

    print(f"\n  【原典明确支持的部分】({len(definition_audit.classical_explicit_parts)} 条)")
    for p in definition_audit.classical_explicit_parts:
        print(f"    ✅ {p}")

    print(f"\n  【原典隐含支持的部分】({len(definition_audit.classical_implicit_parts)} 条)")
    for p in definition_audit.classical_implicit_parts:
        print(f"    🟡 {p}")

    print(f"\n  【合理假说部分】({len(definition_audit.reasonable_hypothesis_parts)} 条)")
    for p in definition_audit.reasonable_hypothesis_parts:
        print(f"    🟠 {p}")

    print(f"\n  【工程推导部分】({len(definition_audit.engineering_derived_parts)} 条)")
    for p in definition_audit.engineering_derived_parts:
        print(f"    🔵 {p}")

    print(f"\n  【不支持的部分】({len(definition_audit.not_supported_parts)} 条)")
    for p in definition_audit.not_supported_parts:
        print(f"    ❌ {p}")

    print(f"\n  【最终评估】")
    print(f"    {definition_audit.final_assessment[:300]}...")

    print(f"\n  【建议】({len(definition_audit.recommendations)} 条)")
    for i, r in enumerate(definition_audit.recommendations, 1):
        print(f"    {i}. {r}")

    # 总结
    print("\n" + "=" * 80)
    print("【审计总结】")
    print("=" * 80)

    print("""
  核心结论：

  1. 「有气」的原典含义目前是 UNRESOLVED / RESEARCH MODEL
     - 原典明确将'有气'列为真旺的四个并列条件之一（与得令、得地、有根并列）
     - 但原典没有明确说明'有气'的具体定义和精确内涵
     - 当前提出的定义是合理假说，不是原典明确的定义

  2. 「有气」与其他概念的关系
     - 有气 vs 得令: OVERLAP（有重叠但不等同），不是 SUBSET/SYNONYM
     - 有气 vs 有根: OVERLAP（有重叠但不等同），不是 SUBSET/SYNONYM
     - 有气 vs 气势: UNCLEAR（原典没有明确说明），气势可能是更高层次概念
     - 有气 vs 支中党众+干上生扶: UNCLEAR（合理假说，不是原典明确）

  3. 必须纠正的地方
     - 时势（大运/流年）必须从有气的原局定义中移除（属于 Temporal Context）
     - 气势 = 有气的 SUPERSET 必须标记为 HYPOTHESIS，不得升级为 CLASSICAL_RELATION
     - '有气 = 更广泛的力量状态'必须标记为 REASONABLE_HYPOTHESIS，不是 CLASSICAL_EXPLICIT

  4. 工程纪律
     - 合理 ≠ 原典证明
     - 在'有气'的原典含义明确之前，不能作为生产级 Evidence
     - 不能进入最终身强身弱组合
     - 算层完整性（P6-CALC）仍是最高优先级，FROZEN ≠ PROVEN CORRECT
""")


if __name__ == "__main__":
    extractor = DitiansuiOriginalTextExtractor()
    evidences = extractor.get_all_evidence()
    relations = extractor.get_concept_relations()
    definition_audit = extractor.get_you_qi_definition_audit()
    print_audit_report(evidences, relations, definition_audit)
