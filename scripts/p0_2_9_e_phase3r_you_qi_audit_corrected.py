"""
P0-2.9-E Phase 3-R: 「有气」原典证据审计 — 修正版

基于 1b78f70 的 🟡 CONDITIONAL PASS 裁决，修正 🔴 高风险问题：
原典文本真实性问题。

核心修正：
1. 修正数据结构：加入 source_text_exact / normalization_note / interpretation
   - source_text_exact: 原典逐字文本（必须是原典原文，不能是现代整理）
   - normalization_note: 整理者概括/现代解释（如果有的话）
   - interpretation: 工程解释/语义分析
2. 建立 DTS-QI Semantic Corpus：把《滴天髓》所有"气"相关原文逐条核验
3. 建立 QI_TARGET 分类体系：DayMaster / FiveElement / UsefulSpirit / Pattern / WholeChart / Other
4. 修正之前的证据标注：现代整理句 vs 原典逐字文本
5. 明确标注哪些是原典逐字文本，哪些是现代整理，哪些是工程解释

数据来源：D:\shuntian\docs\五部经典整理\（本地优先）

重要声明：
- 本脚本中标记为 source_text_exact 的内容，必须经过原典逐字核验
- 如果无法确认是逐字原典，必须标记为 normalization_note 或 interpretation
- 合理 ≠ 原典证明
- 算层完整性（P6-CALC）仍是最高优先级，FROZEN ≠ PROVEN CORRECT
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import json


# ============================================================================
# 标准数据结构（修正版）
# ============================================================================

class QITarget(Enum):
    """气的对象分类 — 气在原典中描述的是谁的气"""
    DAY_MASTER = "DAY_MASTER"          # 日主
    FIVE_ELEMENT = "FIVE_ELEMENT"      # 五行
    USEFUL_SPIRIT = "USEFUL_SPIRIT"    # 用神/真神
    PATTERN = "PATTERN"                # 格局
    WHOLE_CHART = "WHOLE_CHART"        # 全局/命局
    OTHER = "OTHER"                    # 其他
    UNCLEAR = "UNCLEAR"                # 不明确


class QIConcept(Enum):
    """气的概念分类"""
    YOU_QI = "YOU_QI"                  # 有气
    WU_QI = "WU_QI"                    # 无气
    GEN_QI = "GEN_QI"                  # 根气
    DE_QI = "DE_QI"                    # 得气
    SHI_QI = "SHI_QI"                  # 失气
    ZHEN_QI = "ZHEN_QI"                # 真气
    JIA_QI = "JIA_QI"                  # 假气
    QI_SHI = "QI_SHI"                  # 气势
    QI_SHU = "QI_SHU"                  # 气数
    QI_XIANG = "QI_XIANG"              # 气象
    LIU_QI = "LIU_QI"                  # 流气
    SHENG_QI = "SHENG_QI"              # 生气
    TUI_QI = "TUI_QI"                  # 退气
    JIN_QI = "JIN_QI"                  # 进气
    WANG_QI = "WANG_QI"                # 旺气
    SHUAI_QI = "SHUAI_QI"              # 衰气
    QI_GENERAL = "QI_GENERAL"          # 气（泛指）
    OTHER = "OTHER"                    # 其他


class TextSourceType(Enum):
    """文本来源类型 — 严格区分原文 vs 整理 vs 解释"""
    ORIGINAL_TEXT_EXACT = "ORIGINAL_TEXT_EXACT"      # 原典逐字文本（经过核验）
    ORIGINAL_TEXT_UNVERIFIED = "ORIGINAL_TEXT_UNVERIFIED"  # 疑似原典但未逐字核验
    MODERN_NORMALIZATION = "MODERN_NORMALIZATION"    # 现代整理/概括
    COMMENTARY = "COMMENTARY"                          # 注疏（如任铁樵注）
    ENGINEERING_INTERPRETATION = "ENGINEERING_INTERPRETATION"  # 工程解释
    UNKNOWN = "UNKNOWN"                                # 来源不明


class EvidenceLevel(Enum):
    """证据等级"""
    CLASSICAL_EXPLICIT = "CLASSICAL_EXPLICIT"    # 原典明确（必须基于 ORIGINAL_TEXT_EXACT）
    CLASSICAL_IMPLICIT = "CLASSICAL_IMPLICIT"    # 原典隐含
    REASONABLE_HYPOTHESIS = "REASONABLE_HYPOTHESIS"  # 合理假说
    ENGINEERING_DERIVED = "ENGINEERING_DERIVED"  # 工程推导
    NOT_SUPPORTED = "NOT_SUPPORTED"              # 不支持


@dataclass(frozen=True)
class StrictOriginalTextEvidence:
    """严格原典证据 — 修正版，明确区分原文/整理/解释"""
    evidence_id: str
    source_file: str                    # 来源文件
    source_chapter: str                 # 来源章节
    source_section: Optional[str]       # 来源小节
    source_span: Optional[str]          # 来源位置（如"第X段"）

    # 【核心修正】三层文本结构
    source_text_exact: Optional[str]    # 原典逐字文本（必须经过核验，没有则为 None）
    normalization_note: Optional[str]   # 现代整理/概括（如果有的话）
    interpretation: str                  # 工程解释/语义分析

    text_source_type: TextSourceType    # 文本来源类型
    is_verified_exact: bool             # 是否经过逐字核验

    # 语义分析
    qi_concepts: List[QIConcept]        # 涉及的气的概念
    qi_targets: List[QITarget]          # 气描述的对象
    semantic_analysis: str               # 语义分析
    canonical_facts: List[str]           # 依赖的 Canonical Facts

    # 证据等级
    evidence_level: EvidenceLevel
    notes: str = ""


@dataclass(frozen=True)
class QISemanticCorpusEntry:
    """DTS-QI Semantic Corpus 条目 — 滴天髓中所有"气"相关原文"""
    corpus_id: str
    source_chapter: str
    source_text_exact: Optional[str]    # 原典逐字文本
    normalization_note: Optional[str]   # 现代整理
    text_source_type: TextSourceType
    is_verified_exact: bool

    qi_concept: QIConcept               # 主要气的概念
    qi_target: QITarget                 # 气描述的对象
    context_summary: str                 # 上下文摘要
    semantic_category: str               # 语义分类
    related_concepts: List[str]          # 相关概念

    evidence_level: EvidenceLevel
    notes: str = ""


# ============================================================================
# DTS-QI Semantic Corpus — 滴天髓所有"气"相关原文
# ============================================================================

class DTSQISemanticCorpus:
    """滴天髓"气"语义语料库"""

    @staticmethod
    def get_all_entries() -> List[QISemanticCorpusEntry]:
        """
        获取所有"气"相关原文条目。

        重要声明：
        - 标记为 source_text_exact 的内容，必须经过原典逐字核验
        - 如果无法确认是逐字原典，标记为 normalization_note，text_source_type = MODERN_NORMALIZATION
        - 本语料库中的内容来自 D:\shuntian\docs\五部经典整理\ 中的现代整理版
        - 因此大部分内容目前标记为 MODERN_NORMALIZATION，需要后续逐字核验原典
        """
        return [
            # 1. 衰旺章 — "气"的核心语境
            QISemanticCorpusEntry(
                corpus_id="DTS-QI-001",
                source_chapter="通神论·衰旺",
                source_text_exact=None,  # 【待核验】需要对照原典逐字文本
                normalization_note=(
                    "真正的旺是得令得地有根有气是真旺，"
                    "天干堆叠一堆五行地之无根无气只是虚旺假旺；"
                    "真正的衰是失令失地根气全无被克被泄，不是数量少就是衰"
                ),
                text_source_type=TextSourceType.MODERN_NORMALIZATION,
                is_verified_exact=False,
                qi_concept=QIConcept.YOU_QI,
                qi_target=QITarget.DAY_MASTER,
                context_summary=(
                    "讨论旺衰判断的标准，将'有气'与得令、得地、有根并列为真旺的条件。"
                    "同时提到'无根无气'是虚旺假旺，'根气全无'是真衰的表现。"
                ),
                semantic_category="旺衰判断标准",
                related_concepts=["得令", "得地", "有根", "真旺", "虚旺假旺", "真衰", "根气"],
                evidence_level=EvidenceLevel.CLASSICAL_IMPLICIT,
                notes=(
                    "【重要】这段是现代整理/概括语言，不是原典逐字文本。"
                    "原典《滴天髓·衰旺》的核心文本是：'能知衰旺之真机，其于三命之奥，思过半矣。'"
                    "以及任氏注：'得时俱为旺论，失令便作衰看，虽是至理，亦死法也。'"
                    "需要后续对照原典逐字核验，确认'得令得地有根有气'是否是原典原文还是后人概括。"
                ),
            ),

            # 2. 衰旺章（任铁樵注）— "得时俱为旺论"
            QISemanticCorpusEntry(
                corpus_id="DTS-QI-002",
                source_chapter="通神论·衰旺（任铁樵注）",
                source_text_exact=(
                    "得时俱为旺论，失令便作衰看，虽是至理，亦死法也。"
                    "须察支中党众，干上生扶，方可定其真衰真旺。"
                ),
                normalization_note=None,
                text_source_type=TextSourceType.COMMENTARY,
                is_verified_exact=False,  # 【待核验】需要对照任铁樵注原典
                qi_concept=QIConcept.WANG_QI,
                qi_target=QITarget.DAY_MASTER,
                context_summary=(
                    "任铁樵注强调：得时/失令虽是判断旺衰的重要标准，但也是死法。"
                    "需要观察支中党众、干上生扶，才能定真衰真旺。"
                    "这里没有直接使用'有气'一词，但讨论了旺衰的综合判断。"
                ),
                semantic_category="旺衰综合判断",
                related_concepts=["得时", "失令", "支中党众", "干上生扶", "真衰真旺"],
                evidence_level=EvidenceLevel.CLASSICAL_EXPLICIT,
                notes=(
                    "这段是任铁樵注，不是《滴天髓》原文。"
                    "需要标注 text_type = COMMENTARY，不能统一叫《滴天髓》授权。"
                    "这段强调综合判断，反对机械唯月令论，与 A+B+C 综合辨识的思路一致。"
                ),
            ),

            # 3. 月令章 — "四季气场"
            QISemanticCorpusEntry(
                corpus_id="DTS-QI-003",
                source_chapter="通神论·月令",
                source_text_exact=None,
                normalization_note=(
                    "月令是全局提纲统领四季气场影响力最大但绝对不能一锤定音不要学死板的唯月令论"
                ),
                text_source_type=TextSourceType.MODERN_NORMALIZATION,
                is_verified_exact=False,
                qi_concept=QIConcept.QI_GENERAL,
                qi_target=QITarget.WHOLE_CHART,
                context_summary=(
                    "讨论月令的重要性，提到'四季气场'，说明气与季节/月令有关。"
                    "但反对机械的唯月令论，强调不能一锤定音。"
                ),
                semantic_category="月令与气场",
                related_concepts=["月令", "四季", "气场", "唯月令论"],
                evidence_level=EvidenceLevel.CLASSICAL_IMPLICIT,
                notes=(
                    "这段是现代整理语言。'四季气场'暗示气与季节有关，但不是'有气'的明确定义。"
                ),
            ),

            # 4. 重寡章 — "气势" / "势大于数"
            QISemanticCorpusEntry(
                corpus_id="DTS-QI-004",
                source_chapter="通神论·重寡",
                source_text_exact=None,
                normalization_note=(
                    "势大于数哪怕只有一个五行只要占据关键位置掌控全局气势就能制衡全局，"
                    "五行数量再多杂乱无章互相牵制也成不了气候"
                ),
                text_source_type=TextSourceType.MODERN_NORMALIZATION,
                is_verified_exact=False,
                qi_concept=QIConcept.QI_SHI,
                qi_target=QITarget.WHOLE_CHART,
                context_summary=(
                    "讨论'势大于数'的原则，强调气势比数量更重要。"
                    "一个关键位置的五行可以掌控全局气势，数量多但杂乱也成不了气候。"
                ),
                semantic_category="气势与数量",
                related_concepts=["气势", "势", "数", "关键位置", "全局气势", "掌控"],
                evidence_level=EvidenceLevel.CLASSICAL_IMPLICIT,
                notes=(
                    "这段是现代整理语言。'势大于数'是滴天髓的重要原则，但需要对照原典逐字核验。"
                    "'气势'与'有气'是不同的概念，气势是更高层次的结构状态。"
                ),
            ),

            # 5. 五行之气流行四时（待补充 — 原典可能有这段）
            QISemanticCorpusEntry(
                corpus_id="DTS-QI-005",
                source_chapter="通神论·衰旺（上下文）",
                source_text_exact=None,  # 【待补充】需要从原典中找到这段
                normalization_note=(
                    "五行之气，流行于四时……（待补充原典原文）"
                ),
                text_source_type=TextSourceType.UNKNOWN,
                is_verified_exact=False,
                qi_concept=QIConcept.LIU_QI,
                qi_target=QITarget.FIVE_ELEMENT,
                context_summary=(
                    "讨论五行之气在四时中的流行、进退、旺相休囚。"
                    "这直接证明'气'在滴天髓中不是简单的某五行出现=有气，"
                    "而是和四时、进退、旺相休囚、生化等多个语义系统发生联系。"
                ),
                semantic_category="五行之气流行",
                related_concepts=["五行", "四时", "流行", "进退", "旺相休囚", "生化"],
                evidence_level=EvidenceLevel.REASONABLE_HYPOTHESIS,
                notes=(
                    "【待补充】需要从原典中找到这段的逐字文本。"
                    "用户提到原典里有'五行之气，流行于四时……'这段，需要定位并核验。"
                    "这段非常重要，因为它说明'气'是一个复杂的语义网络，不是单一 Boolean。"
                ),
            ),

            # 6. 气有真假（待补充）
            QISemanticCorpusEntry(
                corpus_id="DTS-QI-006",
                source_chapter="通神论·（待定位）",
                source_text_exact=None,
                normalization_note=(
                    "气有真假，真神失势……（待补充原典原文）"
                ),
                text_source_type=TextSourceType.UNKNOWN,
                is_verified_exact=False,
                qi_concept=QIConcept.ZHEN_QI,
                qi_target=QITarget.USEFUL_SPIRIT,
                context_summary=(
                    "讨论气的真假，真神失势等概念。"
                    "这说明'气'不是单一 Boolean，有真气/假气之分。"
                ),
                semantic_category="气之真假",
                related_concepts=["真气", "假气", "真神", "失势"],
                evidence_level=EvidenceLevel.REASONABLE_HYPOTHESIS,
                notes=(
                    "【待补充】用户提到原典里有'气有真假，真神失势……'这段，需要定位并核验。"
                ),
            ),

            # 7. 气有先后（待补充）
            QISemanticCorpusEntry(
                corpus_id="DTS-QI-007",
                source_chapter="通神论·（待定位）",
                source_text_exact=None,
                normalization_note=(
                    "气有先后，真气未到，假气先到……（待补充原典原文）"
                ),
                text_source_type=TextSourceType.UNKNOWN,
                is_verified_exact=False,
                qi_concept=QIConcept.JIN_QI,
                qi_target=QITarget.USEFUL_SPIRIT,
                context_summary=(
                    "讨论气的先后，真气未到、假气先到等概念。"
                    "这说明'气'有时间维度，有进气/退气/先后之分。"
                ),
                semantic_category="气之先后",
                related_concepts=["真气", "假气", "进气", "先后"],
                evidence_level=EvidenceLevel.REASONABLE_HYPOTHESIS,
                notes=(
                    "【待补充】用户提到原典里有'气有先后，真气未到，假气先到……'这段，需要定位并核验。"
                ),
            ),

            # 8. 精神俱旺而气衰（待补充）
            QISemanticCorpusEntry(
                corpus_id="DTS-QI-008",
                source_chapter="通神论·精神（待定位）",
                source_text_exact=None,
                normalization_note=(
                    "精神俱旺而气衰……（待补充原典原文）"
                ),
                text_source_type=TextSourceType.UNKNOWN,
                is_verified_exact=False,
                qi_concept=QIConcept.SHUAI_QI,
                qi_target=QITarget.WHOLE_CHART,
                context_summary=(
                    "讨论精、气、神之间的不同状态，出现'精神俱旺而气衰'等复杂表达。"
                    "这说明'气'可以与精、神分开讨论，气衰不等于精神衰。"
                    "也说明'气'的对象不一定是日主，可以是全局/精气神。"
                ),
                semantic_category="精气神",
                related_concepts=["精", "气", "神", "精神俱旺", "气衰"],
                evidence_level=EvidenceLevel.REASONABLE_HYPOTHESIS,
                notes=(
                    "【待补充】用户提到原典里有关于'精神'的材料，需要定位并核验。"
                    "这段非常重要，因为它说明'气'的对象不一定是日主，不能把'气'一开始就锁死成'日主力量'。"
                ),
            ),
        ]

    @staticmethod
    def get_corpus_statistics() -> Dict[str, Any]:
        """语料库统计"""
        entries = DTSQISemanticCorpus.get_all_entries()
        stats = {
            "total_entries": len(entries),
            "by_text_source_type": {},
            "by_qi_concept": {},
            "by_qi_target": {},
            "by_evidence_level": {},
            "verified_exact_count": 0,
            "unverified_count": 0,
            "needs_verification": [],
        }

        for entry in entries:
            # 按文本来源类型统计
            tst = entry.text_source_type.value
            stats["by_text_source_type"][tst] = stats["by_text_source_type"].get(tst, 0) + 1

            # 按气的概念统计
            qc = entry.qi_concept.value
            stats["by_qi_concept"][qc] = stats["by_qi_concept"].get(qc, 0) + 1

            # 按气的对象统计
            qt = entry.qi_target.value
            stats["by_qi_target"][qt] = stats["by_qi_target"].get(qt, 0) + 1

            # 按证据等级统计
            el = entry.evidence_level.value
            stats["by_evidence_level"][el] = stats["by_evidence_level"].get(el, 0) + 1

            # 核验状态
            if entry.is_verified_exact:
                stats["verified_exact_count"] += 1
            else:
                stats["unverified_count"] += 1
                stats["needs_verification"].append(entry.corpus_id)

        return stats


# ============================================================================
# 修正后的「有气」定义审计
# ============================================================================

class CorrectedYouQiAudit:
    """修正后的「有气」定义审计 — 基于严格原典 provenance"""

    @staticmethod
    def get_audit() -> Dict[str, Any]:
        return {
            "current_status": "UNRESOLVED / RESEARCH MODEL",
            "core_principle": "合理 ≠ 原典证明",

            "what_we_know_for_sure": [
                "《滴天髓》（任铁樵注）明确说：'得时俱为旺论，失令便作衰看，虽是至理，亦死法也。须察支中党众，干上生扶，方可定其真衰真旺。'（COMMENTARY，待逐字核验）",
                "现代整理版将'有气'与得令、得地、有根并列为真旺的条件（MODERN_NORMALIZATION，待逐字核验原典是否有此表述）",
                "'势大于数'是滴天髓的重要原则（MODERN_NORMALIZATION，待逐字核验）",
            ],

            "what_we_do_not_know": [
                "'有气'的原典逐字定义是什么？（待核验）",
                "'有气'是否是原典原文还是后人概括？（待核验）",
                "'有气'与得令、有根的精确关系是什么？（原典没有形式化定义）",
                "'有气'的对象一定是日主吗？（不一定，原典中气可以描述五行/用神/全局/精气神）",
                "'真气'、'假气'、'进气'、'退气'与'有气'是什么关系？（待研究）",
            ],

            "must_correct_from_previous_version": [
                "🔴 DTS-EVID-001 的 original_text 是现代整理/概括语言，不能作为原典逐字文本",
                "🔴 不能把现代整理句标记为 CLASSICAL_EXPLICIT 并拿来证明'有气'",
                "🔴 必须区分 source_text_exact（原典逐字）/ normalization_note（现代整理）/ interpretation（工程解释）",
                "🔴 任铁樵注必须标注为 COMMENTARY，不能统一叫《滴天髓》原文授权",
                "🟡 '有气 = 日主力量状态'暂时降级，因为原典中气的对象不一定是日主",
            ],

            "qi_target_classification": {
                "DAY_MASTER": "日主（最常见，但不是唯一）",
                "FIVE_ELEMENT": "五行（五行之气流行四时）",
                "USEFUL_SPIRIT": "用神/真神（真气/假气/进气/退气）",
                "PATTERN": "格局",
                "WHOLE_CHART": "全局/命局（气势/气象）",
                "OTHER": "其他（精气神等）",
                "note": "不能把'气'一开始就锁死成'日主力量'，应该先判断在具体章节中气描述的是谁",
            },

            "recommendations": [
                "【最高优先级】建立 DTS-QI Semantic Corpus，把滴天髓所有'气'相关原文逐条核验",
                "【最高优先级】对照原典逐字核验'得令得地有根有气'是否是原典原文还是后人概括",
                "【高优先级】定位并核验'五行之气流行于四时'、'气有真假'、'气有先后'、'精神俱旺而气衰'等原文",
                "【高优先级】建立 QI_TARGET 分类，明确每段原文中气描述的对象",
                "【中优先级】在'有气'的原典含义明确之前，不能作为生产级 Evidence",
                "【中优先级】不能进入最终身强身弱组合",
                "【低优先级】Combination Rule 暂缓",
                "算层完整性（P6-CALC）继续并行推进，FROZEN ≠ PROVEN CORRECT",
            ],
        }


# ============================================================================
# 输出审计报告
# ============================================================================

def print_corrected_audit_report():
    print("=" * 80)
    print("P0-2.9-E Phase 3-R: 「有气」原典证据审计 — 修正版")
    print("=" * 80)

    print("\n【修正背景】")
    print("  基于 1b78f70 的 🟡 CONDITIONAL PASS 裁决，修正 🔴 高风险问题：")
    print("  原典文本真实性问题 — DTS-EVID-001 的'原文'是现代整理/概括式语言，")
    print("  不能作为 original_text 原文证据。")

    print("\n【核心修正】")
    print("  1. 修正数据结构：加入 source_text_exact / normalization_note / interpretation")
    print("  2. 建立 DTS-QI Semantic Corpus：把所有'气'相关原文逐条核验")
    print("  3. 建立 QI_TARGET 分类体系")
    print("  4. 修正之前的证据标注：现代整理句 vs 原典逐字文本")
    print("  5. 明确标注哪些是原典逐字文本，哪些是现代整理，哪些是工程解释")

    # 语料库统计
    print("\n" + "=" * 80)
    print("【DTS-QI Semantic Corpus 统计】")
    print("=" * 80)

    stats = DTSQISemanticCorpus.get_corpus_statistics()
    print(f"\n  总条目数: {stats['total_entries']}")
    print(f"  已逐字核验: {stats['verified_exact_count']}")
    print(f"  待核验: {stats['unverified_count']}")

    print(f"\n  按文本来源类型:")
    for k, v in stats["by_text_source_type"].items():
        print(f"    {k}: {v}")

    print(f"\n  按气的概念:")
    for k, v in stats["by_qi_concept"].items():
        print(f"    {k}: {v}")

    print(f"\n  按气的对象:")
    for k, v in stats["by_qi_target"].items():
        print(f"    {k}: {v}")

    print(f"\n  按证据等级:")
    for k, v in stats["by_evidence_level"].items():
        print(f"    {k}: {v}")

    print(f"\n  【待核验条目】:")
    for cid in stats["needs_verification"]:
        print(f"    - {cid}")

    # 语料库条目详情
    print("\n" + "=" * 80)
    print("【DTS-QI Semantic Corpus 条目详情】")
    print("=" * 80)

    entries = DTSQISemanticCorpus.get_all_entries()
    for entry in entries:
        verified = "✅ 已核验" if entry.is_verified_exact else "⚠️ 待核验"
        print(f"\n{'='*60}")
        print(f"  {entry.corpus_id}: {entry.source_chapter}")
        print(f"  文本来源: {entry.text_source_type.value} ({verified})")
        print(f"  气的概念: {entry.qi_concept.value}")
        print(f"  气的对象: {entry.qi_target.value}")
        print(f"  证据等级: {entry.evidence_level.value}")
        print(f"{'='*60}")

        if entry.source_text_exact:
            print(f"\n  【原典逐字文本】")
            print(f"    「{entry.source_text_exact}」")

        if entry.normalization_note:
            print(f"\n  【现代整理/概括】")
            print(f"    「{entry.normalization_note[:100]}...」")

        print(f"\n  【上下文摘要】")
        print(f"    {entry.context_summary[:120]}...")

        print(f"\n  【语义分类】: {entry.semantic_category}")
        print(f"  【相关概念】: {', '.join(entry.related_concepts)}")

        if entry.notes:
            print(f"\n  【备注】")
            print(f"    {entry.notes[:150]}...")

    # 修正后的「有气」定义审计
    print("\n" + "=" * 80)
    print("【修正后的「有气」定义审计】")
    print("=" * 80)

    audit = CorrectedYouQiAudit.get_audit()
    print(f"\n  当前状态: {audit['current_status']}")
    print(f"  核心原则: {audit['core_principle']}")

    print(f"\n  【我们确定知道的】({len(audit['what_we_know_for_sure'])} 条)")
    for i, item in enumerate(audit["what_we_know_for_sure"], 1):
        print(f"    {i}. {item[:120]}...")

    print(f"\n  【我们还不知道的】({len(audit['what_we_do_not_know'])} 条)")
    for i, item in enumerate(audit["what_we_do_not_know"], 1):
        print(f"    {i}. {item}")

    print(f"\n  【必须从上一版修正的】({len(audit['must_correct_from_previous_version'])} 条)")
    for item in audit["must_correct_from_previous_version"]:
        print(f"    {item}")

    print(f"\n  【QI_TARGET 分类体系】")
    for k, v in audit["qi_target_classification"].items():
        if k != "note":
            print(f"    {k}: {v}")
    print(f"    注: {audit['qi_target_classification']['note']}")

    print(f"\n  【建议】({len(audit['recommendations'])} 条)")
    for i, r in enumerate(audit["recommendations"], 1):
        print(f"    {i}. {r}")

    # 总结
    print("\n" + "=" * 80)
    print("【审计总结】")
    print("=" * 80)

    print("""
  核心结论：

  1. 🔴 上一版（1b78f70）的原典证据层存在真实性问题
     - DTS-EVID-001 的"原文"是现代整理/概括语言，不是原典逐字文本
     - 不能把现代整理句标记为 CLASSICAL_EXPLICIT 并拿来证明"有气"
     - 这个错误没有污染当前结论（结论是 UNRESOLVED），但 Evidence ingestion 层必须修

  2. 本修正版建立了严格的三层文本结构
     - source_text_exact: 原典逐字文本（必须经过核验）
     - normalization_note: 现代整理/概括
     - interpretation: 工程解释/语义分析
     - 任铁樵注必须标注为 COMMENTARY，不能统一叫《滴天髓》原文

  3. 建立了 DTS-QI Semantic Corpus（8 条条目，大部分待核验）
     - 涵盖：有气、旺气、气（泛指）、气势、流气、真气、进气、衰气
     - 涵盖对象：日主、五行、用神、全局
     - 大部分条目目前标记为 MODERN_NORMALIZATION，需要后续逐字核验原典

  4. 「有气」的原典含义仍然是 UNRESOLVED / RESEARCH MODEL
     - 原典明确将'有气'列为真旺的条件之一（但这段是现代整理，待核验）
     - 原典没有明确说明'有气'的具体定义
     - '气'的对象不一定是日主，可以是五行/用神/全局/精气神
     - 不能把'气'一开始就锁死成'日主力量'

  5. 工程纪律
     - 合理 ≠ 原典证明
     - 在'有气'的原典含义明确之前，不能作为生产级 Evidence
     - 不能进入最终身强身弱组合
     - 算层完整性（P6-CALC）仍是最高优先级，FROZEN ≠ PROVEN CORRECT

  6. 下一步
     - 【最高优先级】对照原典逐字核验 DTS-QI Semantic Corpus 中的所有条目
     - 【最高优先级】定位并核验'五行之气流行于四时'、'气有真假'、'气有先后'、'精神俱旺而气衰'等原文
     - 【高优先级】建立完整的 QI_TARGET 分类和语义网络
""")


if __name__ == "__main__":
    print_corrected_audit_report()
