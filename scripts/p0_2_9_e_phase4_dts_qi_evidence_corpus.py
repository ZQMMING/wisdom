"""
P0-2.9-E Phase 4: DTS-QI Evidence Corpus 逐字原典核验与语义提取

基于 3c2d8ea 的 🟢 PASS 裁决，下一步是把 DTS-QI Corpus 真正做成：
"逐字原典可追溯、对象明确、语境明确、证据等级明确"的 DTS-QI Evidence Corpus。

核心任务：
1. 从 D 盘滴天髓相关文件中提取所有"气"相关原文/语境
2. 对每条内容做精确的语义对象分析（回答 A-E 五个问题）
3. 明确证据等级和关系类型
4. 把 Candidate Corpus 升级为 Verified Corpus（至少部分条目）

重要声明：
- 当前 D 盘的滴天髓文件主要是抖音视频字幕的现代整理版（空空道人哲学）
- 不是原典逐字文本（如任铁樵注《滴天髓阐微》）
- 因此本脚本中的 source_text_exact 大部分仍为 None，内容放在 normalization_note
- 需要后续对照真正的原典逐字核验
- 合理 ≠ 原典证明

数据来源：
- D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md (20KB)
- D:\shuntian\docs\五部经典整理\分类\1-旺衰月令\滴天髓.md (5KB)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import json


# ============================================================================
# 标准数据结构
# ============================================================================

class QITarget(Enum):
    """气的对象分类"""
    DAY_MASTER = "DAY_MASTER"
    FIVE_ELEMENT = "FIVE_ELEMENT"
    USEFUL_SPIRIT = "USEFUL_SPIRIT"
    PATTERN = "PATTERN"
    WHOLE_CHART = "WHOLE_CHART"
    WEALTH = "WEALTH"
    OFFICER = "OFFICER"
    OTHER = "OTHER"
    UNCLEAR = "UNCLEAR"


class QIConcept(Enum):
    """气的概念分类"""
    YOU_QI = "YOU_QI"
    WU_QI = "WU_QI"
    GEN_QI = "GEN_QI"
    QI_JIN = "QI_JIN"
    QI_TUI = "QI_TUI"
    QI_SHI = "QI_SHI"
    QI_JI = "QI_JI"
    QI_XIANG = "QI_XIANG"
    CAI_QI = "CAI_QI"
    GUI_QI = "GUI_QI"
    ZHEN_QI = "ZHEN_QI"
    JIA_QI = "JIA_QI"
    SI_SHI_QI = "SI_SHI_QI"
    WU_XING_QI = "WU_XING_QI"
    BEN_QI = "BEN_QI"
    QI_GENERAL = "QI_GENERAL"
    OTHER = "OTHER"


class TextSourceType(Enum):
    """文本来源类型"""
    ORIGINAL_TEXT_EXACT = "ORIGINAL_TEXT_EXACT"
    ORIGINAL_TEXT_UNVERIFIED = "ORIGINAL_TEXT_UNVERIFIED"
    MODERN_NORMALIZATION = "MODERN_NORMALIZATION"
    COMMENTARY = "COMMENTARY"
    VIDEO_TRANSCRIPT = "VIDEO_TRANSCRIPT"
    ENGINEERING_INTERPRETATION = "ENGINEERING_INTERPRETATION"
    UNKNOWN = "UNKNOWN"


class EvidenceLevel(Enum):
    """证据等级"""
    CLASSICAL_EXPLICIT = "CLASSICAL_EXPLICIT"
    CLASSICAL_IMPLICIT = "CLASSICAL_IMPLICIT"
    REASONABLE_HYPOTHESIS = "REASONABLE_HYPOTHESIS"
    ENGINEERING_DERIVED = "ENGINEERING_DERIVED"
    NOT_SUPPORTED = "NOT_SUPPORTED"


class RelationType(Enum):
    """关系类型 — 有气与其他条件的关系"""
    AND = "AND"
    OR = "OR"
    QUALIFIER = "QUALIFIER"
    CORRELATION = "CORRELATION"
    CAUSAL = "CAUSAL"
    PARALLEL = "PARALLEL"
    UNCLEAR = "UNCLEAR"


@dataclass(frozen=True)
class QIEvidenceEntry:
    """气的证据条目 — 精确核验版"""
    entry_id: str
    source_chapter: str
    source_context: str

    # 三层文本结构
    source_text_exact: Optional[str]
    normalization_note: Optional[str]
    interpretation: str

    text_source_type: TextSourceType
    is_verified_exact: bool

    # 语义分析
    qi_concept: QIConcept
    qi_target: QITarget
    semantic_analysis: str

    # A-E 五个核心问题
    question_a: str  # A. 原文真的用了这个概念吗？
    question_b: str  # B. 它在说谁？日主/五行/用神/格局/全局？
    question_c: str  # C. 依赖哪些条件？关系是 AND/OR/QUALIFIER/CORRELATION？
    question_d: str  # D. 是独立 Primitive 还是综合描述？
    question_e: str  # E. 能不能直接参与身强/身弱？还是只能作为 Evidence/Qualifier？

    # 关系分析
    related_conditions: List[str]
    relation_type: RelationType

    # 证据等级
    evidence_level: EvidenceLevel
    notes: str = ""


@dataclass(frozen=True)
class YouQiFinalAssessment:
    """「有气」最终评估 — 回答 A-E 五个问题"""
    question_a_answer: str
    question_b_answer: str
    question_c_answer: str
    question_d_answer: str
    question_e_answer: str
    overall_conclusion: str
    recommendations: List[str]


# ============================================================================
# DTS-QI Evidence Corpus — 从 D 盘滴天髓文件中提取的精确语义条目
# ============================================================================

class DTSQIEvidenceCorpus:
    """滴天髓"气"证据语料库 — 精确核验版"""

    @staticmethod
    def get_all_entries() -> List[QIEvidenceEntry]:
        return [
            # 1. 第十七章 衰旺 — "得令得地有根有气是真旺"（最核心）
            QIEvidenceEntry(
                entry_id="DTS-QI-E001",
                source_chapter="通神论·第十七章 衰旺",
                source_context="讨论旺衰判断的标准，纠正'数多者为旺'的误区",

                source_text_exact=None,  # 【待核验】需要对照任铁樵注《滴天髓阐微》原典
                normalization_note=(
                    "真正的旺是得令得地有根有气是真旺，"
                    "天干堆叠一堆五行地之无根无气只是虚旺假旺；"
                    "真正的衰是失令失地根气全无被克被泄，不是数量少就是衰"
                ),
                interpretation=(
                    "这段是滴天髓关于旺衰判断的核心表述。将'有气'与得令、得地、有根并列为真旺的四个条件。"
                    "同时将'无根无气'列为虚旺假旺的表现，'根气全无'列为真衰的表现。"
                    "这说明'有气'是一个独立的观察维度，与得令、得地、有根并列，但具体含义原典没有明确定义。"
                ),

                text_source_type=TextSourceType.VIDEO_TRANSCRIPT,
                is_verified_exact=False,

                qi_concept=QIConcept.YOU_QI,
                qi_target=QITarget.DAY_MASTER,
                semantic_analysis=(
                    "'有气'在这个语境中描述的是日主的状态，与得令、得地、有根并列。"
                    "但'气'的具体内涵不明确：可能指五行之气、日主本气、全局气势等。"
                    "'无根无气'说明无气与无根经常一起出现，但可能是两个不同维度。"
                    "'根气全无'将根和气合并表述，说明两者关系密切。"
                ),

                question_a=(
                    "现代整理版明确使用了'有气'这个概念，与得令、得地、有根并列。"
                    "但需要对照原典逐字核验，确认'得令得地有根有气'是否是原典原文还是后人概括。"
                    "从任铁樵注的常见版本来看，'得令得地得势得生'等表述更常见，'有气'可能是后人的概括。"
                ),
                question_b=(
                    "在这个语境中，'有气'描述的是日主的状态（真旺/真衰都是针对日主而言）。"
                    "但'气'本身可以描述多个对象：日主、五行、全局、用神等。"
                    "在这个具体语境中，QI_TARGET = DAY_MASTER。"
                ),
                question_c=(
                    "'有气'与得令、得地、有根是并列关系（PARALLEL），都是真旺的条件之一。"
                    "原文没有说明这四个条件之间是 AND 还是 OR 关系。"
                    "从'真旺'的表述来看，可能需要多个条件同时满足，但具体组合逻辑原典没有形式化。"
                    "'有气'可能依赖：得令？得地？有根？生扶？党众？流通？这些都不明确。"
                ),
                question_d=(
                    "'有气'可能是一个独立 Primitive，也可能是有根+生扶+得令在某种语境下的综合描述。"
                    "从原文将其与得令、得地、有根并列来看，它应该是一个独立的观察维度。"
                    "但其具体内涵需要进一步研究，不能简单等同于'有根'或'得令'。"
                ),
                question_e=(
                    "'有气'不能直接参与身强/身弱的最终判断。"
                    "它只能作为旺衰判断的一个 Evidence / Qualifier。"
                    "真旺需要得令+得地+有根+有气等多个条件综合，不能仅凭'有气'就判断身强。"
                    "在'有气'的具体含义和组合逻辑没有原典授权之前，不能进入最终身强身弱组合。"
                ),

                related_conditions=["得令", "得地", "有根", "无根无气", "根气全无", "被克被泄"],
                relation_type=RelationType.PARALLEL,

                evidence_level=EvidenceLevel.CLASSICAL_IMPLICIT,
                notes=(
                    "【核心条目】这是'有气'最直接的语境，但文本来源是视频字幕的现代整理版，"
                    "需要对照原典逐字核验。'有气'的具体内涵原典没有明确定义，是当前最大的研究缺口。"
                ),
            ),

            # 2. 第五章 理气 — "气进则旺，气退则衰"（非常重要）
            QIEvidenceEntry(
                entry_id="DTS-QI-E002",
                source_chapter="通神论·第五章 理气",
                source_context="讨论五行的动静进退、阴阳气化",

                source_text_exact=None,
                normalization_note=(
                    "金木水火土不是固定的实体符号，是一年四季流转进退胜衰的气场。"
                    "气进则旺，气退则衰，气进则稳，气动则变。"
                    "判断格局高低先看气化，再看五行。"
                ),
                interpretation=(
                    "这段是滴天髓关于'气'的非常重要的表述。明确指出："
                    "1. 五行不是固定实体，而是流转进退胜衰的气场。"
                    "2. 气进则旺，气退则衰 — 气的进退直接决定旺衰。"
                    "3. 气进则稳，气动则变 — 气的状态决定格局的稳定与变化。"
                    "4. 判断格局高低先看气化，再看五行 — 气化比五行更基础。"
                    "这说明'气'在滴天髓中是一个比五行更基础的概念，涉及四时流转、进退、旺衰。"
                ),

                text_source_type=TextSourceType.VIDEO_TRANSCRIPT,
                is_verified_exact=False,

                qi_concept=QIConcept.QI_JIN,
                qi_target=QITarget.FIVE_ELEMENT,
                semantic_analysis=(
                    "这里的'气'描述的是五行的状态，不是日主的状态。"
                    "五行之气随四季流转，有进退、胜衰。"
                    "气进 → 旺、稳；气退 → 衰；气动 → 变。"
                    "这与'有气'的概念相关但不同：'有气'可能是指日主具备某种气的状态，"
                    "而这里讨论的是五行之气本身的进退规律。"
                ),

                question_a=(
                    "现代整理版明确使用了'气进则旺，气退则衰'的表述。"
                    "这与滴天髓第五章'理气'的主题一致，很可能是对原典的准确概括。"
                    "但需要对照原典逐字核验具体表述。"
                ),
                question_b=(
                    "这里的'气'描述的是五行（金木水火土）的状态，QI_TARGET = FIVE_ELEMENT。"
                    "不是日主的'有气/无气'，而是五行之气本身的进退规律。"
                    "这说明'气'在滴天髓中有多个层次：五行之气、日主之气、全局气势等。"
                ),
                question_c=(
                    "气的进退依赖：四季流转、月令、五行生克。"
                    "气进 → 旺（因果关系，CAUSAL）。"
                    "气退 → 衰（因果关系，CAUSAL）。"
                    "这与'有气'的关系：日主'有气'可能意味着日主五行处于'气进'的状态，"
                    "但这个推导关系原典没有明确说明。"
                ),
                question_d=(
                    "'气进/气退'是描述五行状态的独立 Primitive，不是'有气'的同义词。"
                    "'有气'可能是日主层面的概念，而'气进/气退'是五行层面的概念。"
                    "两者可能相关，但不是同一个东西。"
                ),
                question_e=(
                    "'气进则旺，气退则衰'可以作为旺衰判断的一个原则（Qualifier）。"
                    "但不能直接用'气进'就判断身强，因为还需要考虑其他条件。"
                    "这个原则更多是理论层面的指导，不是具体的判断规则。"
                ),

                related_conditions=["四季流转", "月令", "五行生克", "气化", "旺衰"],
                relation_type=RelationType.CAUSAL,

                evidence_level=EvidenceLevel.CLASSICAL_IMPLICIT,
                notes=(
                    "【重要条目】这段说明'气'在滴天髓中是比五行更基础的概念。"
                    "'气进则旺，气退则衰'直接将气的进退与旺衰挂钩，对理解'有气'非常重要。"
                    "但这里讨论的是五行之气，不是日主的'有气'，需要区分层次。"
                ),
            ),

            # 3. 第三十二章 重寡 — "势大于数"（气势）
            QIEvidenceEntry(
                entry_id="DTS-QI-E003",
                source_chapter="通神论·第三十二章 重寡",
                source_context="讨论势力对比，强调势大于数",

                source_text_exact=None,
                normalization_note=(
                    "势大于数，哪怕只有一个五行只要占据关键位置掌控全局气势就能制衡全局。"
                    "五行数量再多杂乱无章互相牵制也成不了气候。"
                ),
                interpretation=(
                    "这段明确提出'势大于数'的原则。'气势'是全局层面的结构状态，"
                    "不是简单的五行数量。一个关键位置的五行可以掌控全局气势，"
                    "数量多但杂乱也成不了气候。这说明'气势'是比'有气'更高层次的概念，"
                    "涉及全局结构、位置、集中度等。"
                ),

                text_source_type=TextSourceType.VIDEO_TRANSCRIPT,
                is_verified_exact=False,

                qi_concept=QIConcept.QI_SHI,
                qi_target=QITarget.WHOLE_CHART,
                semantic_analysis=(
                    "'气势'描述的是全局（WHOLE_CHART）的结构状态。"
                    "不是日主的'有气'，而是整个命局的力量分布和结构。"
                    "气势的关键因素：位置（关键位置）、集中度（掌控全局）、方向（制衡全局）。"
                    "气势与数量是不同维度：势大于数。"
                ),

                question_a=(
                    "现代整理版明确使用了'势大于数'和'全局气势'的表述。"
                    "这与滴天髓第三十二章'重寡'的主题一致，很可能是对原典的准确概括。"
                    "但需要对照原典逐字核验。"
                ),
                question_b=(
                    "'气势'描述的是全局（WHOLE_CHART）的状态，QI_TARGET = WHOLE_CHART。"
                    "不是日主的'有气'，而是整个命局的力量结构。"
                    "这说明'气'在滴天髓中有全局层面的用法。"
                ),
                question_c=(
                    "气势依赖：关键位置、五行集中度、力量方向、全局结构。"
                    "气势与数量的关系：势大于数（气势比数量更重要）。"
                    "气势与'有气'的关系：不明确。气势可能是比'有气'更高层次的概念，"
                    "'有气'可能是气势的一个组成部分，但原典没有明确说明。"
                ),
                question_d=(
                    "'气势'是一个独立的高层结构 Primitive（STRUCTURE 层），"
                    "不是'有气'的同义词，也不是简单的条件组合。"
                    "气势涉及全局的位置、集中度、方向等结构性因素。"
                ),
                question_e=(
                    "'气势'不能直接参与身强/身弱的最终判断。"
                    "它是全局结构的一个观察维度，可以作为旺衰判断的 Qualifier。"
                    "气势强不等于身强，因为气势可能是某一行的强势，不一定是日主的强势。"
                ),

                related_conditions=["关键位置", "五行数量", "全局结构", "制衡", "掌控"],
                relation_type=RelationType.QUALIFIER,

                evidence_level=EvidenceLevel.CLASSICAL_IMPLICIT,
                notes=(
                    "【重要条目】'势大于数'是滴天髓的核心原则之一。"
                    "气势是全局层面的结构状态，与'有气'（日主层面）是不同层次的概念。"
                    "不能把气势简化为数量，也不能把气势等同于有气。"
                ),
            ),

            # 4. 从格相关 — "日主毫无根气毫无依托"
            QIEvidenceEntry(
                entry_id="DTS-QI-E004",
                source_chapter="通神论·从象/假从（第十三章体用相关）",
                source_context="讨论真从格与假从格的区别",

                source_text_exact=None,
                normalization_note=(
                    "真正的真从格要求日主毫无根气毫无依托，全局气势专一一气顺从顺势而成格局。"
                    "假从就是日主身弱但暗藏根气留有后路，暂时顺从大势，"
                    "一旦大运走到帮扶日主的运势立刻破格反转。"
                ),
                interpretation=(
                    "这段在从格的语境中使用了'根气'概念。"
                    "真从格要求日主'毫无根气'，假从格是'暗藏根气'。"
                    "这里'根气'将根和气合并表述，说明在从格的判断中，根和气是一起考虑的。"
                    "但这并不意味着'根'='气'，而是说在从格这个特定语境中，"
                    "日主有任何根或气都可能影响从格的真假。"
                ),

                text_source_type=TextSourceType.VIDEO_TRANSCRIPT,
                is_verified_exact=False,

                qi_concept=QIConcept.GEN_QI,
                qi_target=QITarget.DAY_MASTER,
                semantic_analysis=(
                    "'根气'在这个语境中描述的是日主的状态（DAY_MASTER）。"
                    "真从格：毫无根气；假从格：暗藏根气。"
                    "这里'根气'是根和气的合并表述，说明两者关系密切。"
                    "但在这个语境中，'根气'更多是指日主的任何依托（包括根和气），"
                    "不是对'气'的独立定义。"
                ),

                question_a=(
                    "现代整理版使用了'毫无根气'和'暗藏根气'的表述。"
                    "这与滴天髓从格理论的常见表述一致，很可能是对原典的准确概括。"
                    "但需要对照原典逐字核验。"
                ),
                question_b=(
                    "'根气'描述的是日主的状态，QI_TARGET = DAY_MASTER。"
                    "在从格的语境中，日主有根气还是无根气直接影响从格的真假。"
                ),
                question_c=(
                    "'根气'是根和气的合并表述，两者在这个语境中是并列关系（PARALLEL）。"
                    "真从格：毫无根气（根和气都没有）。"
                    "假从格：暗藏根气（根或气有一点）。"
                    "这说明根和气都是日主的'依托'，但具体区别原典没有在这个语境中说明。"
                ),
                question_d=(
                    "'根气'在这个语境中是一个合并概念，不是对'气'的独立定义。"
                    "它更多是从格判断中的一个实用表述，将根和气一起考虑。"
                    "不能从这个语境中推导'气'的独立定义。"
                ),
                question_e=(
                    "'根气'在从格判断中是关键条件，但不能直接用于身强/身弱的一般判断。"
                    "从格是特殊格局，有自己的判断逻辑，不能推广到一般旺衰判断。"
                    "'毫无根气'在从格中意味着真从，不等于一般意义上的'身弱'。"
                ),

                related_conditions=["真从格", "假从格", "全局气势专一", "大运帮扶", "破格"],
                relation_type=RelationType.PARALLEL,

                evidence_level=EvidenceLevel.CLASSICAL_IMPLICIT,
                notes=(
                    "【相关条目】从格语境中的'根气'是合并表述，说明根和气关系密切。"
                    "但这个语境不能用来定义'气'的独立含义，因为它更多是从格判断中的实用表述。"
                ),
            ),

            # 5. 第七章天干 — "五阳从气不从事" / "坚守自身本气"
            QIEvidenceEntry(
                entry_id="DTS-QI-E005",
                source_chapter="通神论·第七章 天干",
                source_context="讨论天干的阴阳属性和从气/从事的区别",

                source_text_exact=None,
                normalization_note=(
                    "五阳从气不从事，五阴从事无情意。"
                    "甲丙戊庚壬五个阳干本性刚正坚守自身本气，哪怕全局大势强盛也不会轻易顺从格局。"
                    "乙丁己辛癸五个阴干本性柔顺最容易随势而变顺势取舍。"
                ),
                interpretation=(
                    "这段在天干的语境中使用了'本气'概念。"
                    "阳干'坚守自身本气'，说明每个天干都有自己的'本气'。"
                    "'五阳从气不从事'说明阳干更容易顺从'气'（全局气势/气化），"
                    "而不是顺从'事'（具体的事象/格局）。"
                    "这里的'气'可能指全局的气化趋势，与'有气'的概念相关但不同。"
                ),

                text_source_type=TextSourceType.VIDEO_TRANSCRIPT,
                is_verified_exact=False,

                qi_concept=QIConcept.BEN_QI,
                qi_target=QITarget.FIVE_ELEMENT,
                semantic_analysis=(
                    "'本气'描述的是天干（五行）的固有属性，QI_TARGET = FIVE_ELEMENT。"
                    "每个天干都有自己的本气，阳干坚守本气，阴干容易随势而变。"
                    "'从气不从事'中的'气'可能指全局气化趋势，是比具体格局更高层次的概念。"
                    "这与日主'有气'的概念不同：'本气'是天干的固有属性，'有气'是日主的状态。"
                ),

                question_a=(
                    "现代整理版使用了'坚守自身本气'和'五阳从气不从事'的表述。"
                    "'五阳从气不从事'是滴天髓的著名口诀，很可能是原典原文。"
                    "但需要对照原典逐字核验。"
                ),
                question_b=(
                    "'本气'描述的是天干（五行）的固有属性，QI_TARGET = FIVE_ELEMENT。"
                    "'从气不从事'中的'气'可能指全局气化趋势，QI_TARGET = WHOLE_CHART。"
                    "这两个语境中的'气'都不是日主的'有气'。"
                ),
                question_c=(
                    "'本气'是天干的固有属性，不依赖其他条件。"
                    "'从气不从事'说明阳干更容易顺从全局气化趋势。"
                    "这与'有气'的关系：日主'有气'可能意味着日主本气得到全局气化的支持，"
                    "但这个推导关系原典没有明确说明。"
                ),
                question_d=(
                    "'本气'是天干的固有属性，是一个独立概念。"
                    "'从气不从事'中的'气'是全局气化趋势，也是一个独立概念。"
                    "两者都与'有气'相关但不同，不能混为一谈。"
                ),
                question_e=(
                    "'本气'和'从气不从事'可以作为天干属性和格局判断的 Qualifier。"
                    "但不能直接用于身强/身弱的最终判断。"
                    "阳干坚守本气不等于身强，阴干随势而变不等于身弱。"
                ),

                related_conditions=["天干阴阳", "从气不从事", "全局大势", "格局顺从"],
                relation_type=RelationType.QUALIFIER,

                evidence_level=EvidenceLevel.CLASSICAL_IMPLICIT,
                notes=(
                    "【相关条目】'五阳从气不从事'是滴天髓的著名口诀。"
                    "这里的'气'指全局气化趋势，与日主'有气'是不同层次的概念。"
                    "'本气'是天干的固有属性，也不是'有气'的同义词。"
                ),
            ),

            # 6. 财气相关 — "财气通门户"
            QIEvidenceEntry(
                entry_id="DTS-QI-E006",
                source_chapter="下篇六亲论·何知章（财气）",
                source_context="讨论贫富判断，'何知其人富，财气通门户'",

                source_text_exact=None,
                normalization_note=(
                    "何知其人富，财气通门户。重点从来不是财多，是财气流通。"
                    "财星有源头有去路能为我所用，流通门户滋养日主才是真富足。"
                    "如果财星成堆堆积堵塞，日主身弱担不住，财多身弱财气不通，"
                    "反而一生求财辛苦守不住财富，这就是财神反不真。"
                ),
                interpretation=(
                    "这段在贫富判断的语境中使用了'财气'概念。"
                    "'财气通门户'是滴天髓何知章的著名口诀。"
                    "这里'财气'指财星的流通状态，不是日主的'有气'。"
                    "财气的关键是'流通'：有源头有去路，能为我所用，滋养日主。"
                    "这说明'气'在滴天髓中可以描述特定十神（财星）的状态。"
                ),

                text_source_type=TextSourceType.VIDEO_TRANSCRIPT,
                is_verified_exact=False,

                qi_concept=QIConcept.CAI_QI,
                qi_target=QITarget.WEALTH,
                semantic_analysis=(
                    "'财气'描述的是财星的状态，QI_TARGET = WEALTH。"
                    "财气的核心是'流通'：财星有源头有去路，能流通门户，滋养日主。"
                    "财气不通：财星成堆堆积堵塞，日主身弱担不住。"
                    "这说明'气'可以描述特定十神的状态，'财气'是财星的流通状态。"
                    "这与日主'有气'是不同对象的'气'。"
                ),

                question_a=(
                    "现代整理版使用了'财气通门户'的表述。"
                    "这是滴天髓何知章的著名口诀，很可能是原典原文。"
                    "但需要对照原典逐字核验。"
                ),
                question_b=(
                    "'财气'描述的是财星的状态，QI_TARGET = WEALTH。"
                    "不是日主的'有气'，而是财星这个特定十神的流通状态。"
                    "这说明'气'在滴天髓中可以描述不同对象：日主、五行、财星、官星等。"
                ),
                question_c=(
                    "财气依赖：财星有源头、有去路、能流通、能滋养日主。"
                    "财气与日主强弱的关系：日主身弱担不住财 → 财气不通。"
                    "这说明财气需要日主有足够的力量来承载，与日主'有气'可能相关。"
                    "但这个关系原典没有明确形式化。"
                ),
                question_d=(
                    "'财气'是描述财星状态的独立概念，不是'有气'的同义词。"
                    "它是'气'在财星这个特定对象上的应用。"
                    "类似的还有'贵气'（官星的状态）等。"
                ),
                question_e=(
                    "'财气通门户'是贫富判断的条件，不能直接用于身强/身弱的判断。"
                    "财气通可能意味着日主有足够力量承载财星，但这是间接推导，不是直接判断。"
                    "在贫富判断中，财气是核心条件；在旺衰判断中，财气只是一个参考因素。"
                ),

                related_conditions=["财星", "流通", "门户", "日主身弱", "财神反不真"],
                relation_type=RelationType.CORRELATION,

                evidence_level=EvidenceLevel.CLASSICAL_IMPLICIT,
                notes=(
                    "【相关条目】'财气通门户'说明'气'可以描述特定十神的状态。"
                    "这对理解'气'的多对象性非常重要：气可以描述日主、五行、财星、官星等不同对象。"
                    "不能把所有'气'都等同于日主的'有气'。"
                ),
            ),
        ]

    @staticmethod
    def get_you_qi_final_assessment() -> YouQiFinalAssessment:
        """「有气」最终评估 — 回答 A-E 五个问题"""
        return YouQiFinalAssessment(
            question_a_answer=(
                "A. 《滴天髓》原文真的用了'有气'这个概念吗？\n"
                "   - 现代整理版（视频字幕）明确使用了'得令得地有根有气是真旺'的表述。\n"
                "   - 但这是现代整理语言，不是原典逐字文本。\n"
                "   - 需要对照任铁樵注《滴天髓阐微》原典逐字核验。\n"
                "   - 从常见版本来看，'得令得地得势得生'等表述更常见，'有气'可能是后人的概括。\n"
                "   - 结论：'有气'这个概念在滴天髓的思想中肯定存在（气进则旺、气退则衰等），"
                "但'有气'作为与得令、得地、有根并列的特定术语，是否是原典原文仍需核验。"
            ),
            question_b_answer=(
                "B. 它在说谁？日主？五行？用神？格局？全局？\n"
                "   - 在'得令得地有根有气是真旺'这个语境中，'有气'描述的是日主的状态（DAY_MASTER）。\n"
                "   - 但'气'在滴天髓中有多个对象：\n"
                "     * 五行之气（气进则旺，气退则衰）\n"
                "     * 日主之气（有气/无气/根气）\n"
                "     * 全局气势（势大于数，掌控全局气势）\n"
                "     * 财星之气（财气通门户）\n"
                "     * 天干本气（坚守自身本气）\n"
                "   - 结论：不能把'气'一开始就锁死成'日主力量'。在具体语境中需要先判断气描述的对象。"
            ),
            question_c_answer=(
                "C. '有气'依赖哪些条件？关系是 AND/OR/QUALIFIER/CORRELATION？\n"
                "   - '有气'与得令、得地、有根是并列关系（PARALLEL），都是真旺的条件之一。\n"
                "   - 原文没有说明这四个条件之间是 AND 还是 OR 关系。\n"
                "   - '有气'可能依赖：得令？得地？有根？生扶？党众？流通？这些都不明确。\n"
                "   - 从'气进则旺，气退则衰'来看，'有气'可能与五行之气的进退状态相关。\n"
                "   - 从'财气通门户'来看，'气'的核心是'流通'，有气可能意味着气能流通。\n"
                "   - 结论：'有气'的依赖条件和组合逻辑原典没有形式化，当前只能标记为 UNCLEAR / RESEARCH。"
            ),
            question_d_answer=(
                "D. 它是独立 Primitive 还是综合描述？\n"
                "   - 从原文将'有气'与得令、得地、有根并列来看，它应该是一个独立的观察维度。\n"
                "   - 但'有气'的具体内涵不明确，可能是：\n"
                "     * 五行之气的进退状态（气进则有气）\n"
                "     * 日主本气得到全局气化的支持\n"
                "     * 日主的根气（根+气的合并表述）\n"
                "     * 某种综合描述（有根+生扶+得令在某种语境下的综合）\n"
                "   - 结论：'有气'应该作为一个独立 Primitive 来研究，但其具体内涵需要进一步原典考证。"
                "在内涵明确之前，不能将其简化为任何已知条件的组合。"
            ),
            question_e_answer=(
                "E. 能不能直接参与身强/身弱？还是只能作为 Evidence/Qualifier？\n"
                "   - '有气'不能直接参与身强/身弱的最终判断。\n"
                "   - 它只能作为旺衰判断的一个 Evidence / Qualifier。\n"
                "   - 真旺需要得令+得地+有根+有气等多个条件综合，不能仅凭'有气'就判断身强。\n"
                "   - 在'有气'的具体含义和组合逻辑没有原典授权之前，不能进入最终身强身弱组合。\n"
                "   - 结论：'有气'当前只能作为 Evidence / Qualifier，不能作为最终身强/身弱的判断依据。"
            ),
            overall_conclusion=(
                "「有气」的原典含义目前是 UNRESOLVED / RESEARCH MODEL。\n\n"
                "1. '有气'这个概念在滴天髓的思想中肯定存在（气进则旺、气退则衰等），"
                "但作为与得令、得地、有根并列的特定术语，是否是原典原文仍需逐字核验。\n\n"
                "2. '气'在滴天髓中有多个对象和层次：五行之气、日主之气、全局气势、财星之气、天干本气等。"
                "不能把所有'气'都等同于日主的'有气'。\n\n"
                "3. '有气'的依赖条件和组合逻辑原典没有形式化，当前只能标记为 UNCLEAR / RESEARCH。\n\n"
                "4. '有气'应该作为一个独立 Primitive 来研究，但其具体内涵需要进一步原典考证。\n\n"
                "5. '有气'当前只能作为 Evidence / Qualifier，不能作为最终身强/身弱的判断依据。\n\n"
                "合理 ≠ 原典证明。在'有气'的原典含义明确之前，不能进入生产级 Evidence，"
                "也不能进入最终身强身弱组合。"
            ),
            recommendations=[
                "【最高优先级】对照任铁樵注《滴天髓阐微》原典，逐字核验'得令得地有根有气'是否是原典原文",
                "【最高优先级】建立完整的 QI_TARGET 分类和语义网络，明确每段原文中气描述的对象",
                "【高优先级】深入研究'气进则旺，气退则衰'与'有气'的关系",
                "【高优先级】研究'财气通门户'中'气=流通'的含义，是否可以推广到日主'有气'",
                "【中优先级】在'有气'的原典含义明确之前，不进入生产级 Evidence",
                "【中优先级】不能进入最终身强身弱组合",
                "【低优先级】Combination Rule 暂缓",
                "算层完整性（P6-CALC）继续并行推进，FROZEN ≠ PROVEN CORRECT",
            ],
        )


# ============================================================================
# 输出报告
# ============================================================================

def print_phase4_report():
    print("=" * 80)
    print("P0-2.9-E Phase 4: DTS-QI Evidence Corpus 逐字原典核验与语义提取")
    print("=" * 80)

    print("\n【核心任务】")
    print("  把 DTS-QI Corpus 真正做成：")
    print("  '逐字原典可追溯、对象明确、语境明确、证据等级明确'的 DTS-QI Evidence Corpus")

    print("\n【重要声明】")
    print("  当前 D 盘的滴天髓文件主要是抖音视频字幕的现代整理版（空空道人哲学）")
    print("  不是原典逐字文本（如任铁樵注《滴天髓阐微》）")
    print("  因此本脚本中的 source_text_exact 大部分仍为 None，内容放在 normalization_note")
    print("  需要后续对照真正的原典逐字核验")
    print("  合理 ≠ 原典证明")

    # 语料库统计
    print("\n" + "=" * 80)
    print("【DTS-QI Evidence Corpus 统计】")
    print("=" * 80)

    entries = DTSQIEvidenceCorpus.get_all_entries()
    print(f"\n  总条目数: {len(entries)}")

    by_concept = {}
    by_target = {}
    by_level = {}
    for e in entries:
        c = e.qi_concept.value
        t = e.qi_target.value
        l = e.evidence_level.value
        by_concept[c] = by_concept.get(c, 0) + 1
        by_target[t] = by_target.get(t, 0) + 1
        by_level[l] = by_level.get(l, 0) + 1

    print(f"\n  按气的概念:")
    for k, v in by_concept.items():
        print(f"    {k}: {v}")

    print(f"\n  按气的对象:")
    for k, v in by_target.items():
        print(f"    {k}: {v}")

    print(f"\n  按证据等级:")
    for k, v in by_level.items():
        print(f"    {k}: {v}")

    print(f"\n  已逐字核验: 0 / {len(entries)}")
    print(f"  待核验: {len(entries)} / {len(entries)}")

    # 条目详情
    print("\n" + "=" * 80)
    print("【DTS-QI Evidence Corpus 条目详情】")
    print("=" * 80)

    for e in entries:
        print(f"\n{'='*60}")
        print(f"  {e.entry_id}: {e.source_chapter}")
        print(f"  气的概念: {e.qi_concept.value}")
        print(f"  气的对象: {e.qi_target.value}")
        print(f"  文本来源: {e.text_source_type.value}")
        print(f"  证据等级: {e.evidence_level.value}")
        print(f"  关系类型: {e.relation_type.value}")
        print(f"{'='*60}")

        if e.normalization_note:
            print(f"\n  【现代整理/概括】")
            print(f"    「{e.normalization_note[:120]}...」")

        print(f"\n  【语义分析】")
        print(f"    {e.semantic_analysis[:150]}...")

        print(f"\n  【A-E 五个核心问题】")
        print(f"    A. {e.question_a[:100]}...")
        print(f"    B. {e.question_b[:100]}...")
        print(f"    C. {e.question_c[:100]}...")
        print(f"    D. {e.question_d[:100]}...")
        print(f"    E. {e.question_e[:100]}...")

        if e.notes:
            print(f"\n  【备注】")
            print(f"    {e.notes[:120]}...")

    # 「有气」最终评估
    print("\n" + "=" * 80)
    print("【「有气」最终评估 — 回答 A-E 五个核心问题】")
    print("=" * 80)

    assessment = DTSQIEvidenceCorpus.get_you_qi_final_assessment()

    print(f"\n{assessment.question_a_answer}")
    print(f"\n{assessment.question_b_answer}")
    print(f"\n{assessment.question_c_answer}")
    print(f"\n{assessment.question_d_answer}")
    print(f"\n{assessment.question_e_answer}")

    print(f"\n{'='*60}")
    print("【总体结论】")
    print(f"{'='*60}")
    print(f"\n{assessment.overall_conclusion}")

    print(f"\n{'='*60}")
    print("【建议】")
    print(f"{'='*60}")
    for i, r in enumerate(assessment.recommendations, 1):
        print(f"  {i}. {r}")

    # 总结
    print("\n" + "=" * 80)
    print("【审计总结】")
    print("=" * 80)

    print("""
  核心发现：

  1. '气'在滴天髓中有多个对象和层次
     - 五行之气（气进则旺，气退则衰）
     - 日主之气（有气/无气/根气）
     - 全局气势（势大于数，掌控全局气势）
     - 财星之气（财气通门户）
     - 天干本气（坚守自身本气）
     不能把所有'气'都等同于日主的'有气'。

  2. '有气'的原典含义仍需逐字核验
     - 现代整理版明确使用了'得令得地有根有气是真旺'
     - 但这是现代整理语言，不是原典逐字文本
     - 需要对照任铁樵注《滴天髓阐微》原典逐字核验
     - 从常见版本来看，'有气'可能是后人的概括

  3. '有气'的依赖条件和组合逻辑原典没有形式化
     - 与得令、得地、有根是并列关系（PARALLEL）
     - 但具体是 AND 还是 OR 不明确
     - 依赖哪些条件不明确
     - 当前只能标记为 UNCLEAR / RESEARCH

  4. '有气'应该作为独立 Primitive 研究
     - 不能简化为有根、得令、生扶等已知条件的组合
     - 但其具体内涵需要进一步原典考证

  5. '有气'当前只能作为 Evidence / Qualifier
     - 不能直接参与身强/身弱的最终判断
     - 在原典含义明确之前，不能进入生产级 Evidence
     - 不能进入最终身强身弱组合

  工程纪律：
  - 合理 ≠ 原典证明
  - 算层完整性（P6-CALC）仍是最高优先级，FROZEN ≠ PROVEN CORRECT
""")


if __name__ == "__main__":
    print_phase4_report()
