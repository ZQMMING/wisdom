"""
P0-2.9-E Phase 5: Evidence Level 重新定义 + 6 条证据降级修正 + QI_TARGET 验证规则

基于 b6133e9 的 🟡 CONDITIONAL PASS 裁决，修正以下关键问题：

1. 🔴 把"研究假设"写得太接近"原典结论"
   - 6 条证据 source_text_exact = None, is_verified_exact = False, text_source_type = VIDEO_TRANSCRIPT
   - 但却标为 CLASSICAL_IMPLICIT
   - 必须降级为 SOURCE_UNVERIFIED

2. 🔴 "有气 = 独立 Primitive"的结论太早
   - "文本上并列"不等于"理论上独立"
   - 必须改为候选假设，待原典核验

3. 🔴 QI_JIN ≠ YOU_QI
   - "气进则旺"讨论的是动态五行气化语境
   - "有气"是否就是"气进"没有证据
   - 禁止跨概念推导

4. 🟡 QI_TARGET 不能变成"自由解释器"
   - Target 必须由原文语境证明
   - 建立 target_span / semantic_anchor 验证规则

5. 🟡 EvidenceLevel 重新定义
   - 增加 SOURCE_UNVERIFIED
   - 明确升级流程

核心原则：
- 合理 ≠ 原典证明
- 文本上并列 ≠ 理论上独立
- 现代整理 ↓ 候选语义 ↓ 必须核验原典
- 先把证据钉死，再做辨
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import json


# ============================================================================
# 重新定义的 EvidenceLevel（修正版）
# ============================================================================

class EvidenceLevel(Enum):
    """
    证据等级（修正版）— 严格区分原典核验状态

    升级流程：
    SOURCE_UNVERIFIED
        ↓ 找到原典逐字文本 + source_span + 原典上下文
    CLASSICAL_EXPLICIT
        ↓ 如果需要语义推导（原典没有形式化表达工程关系）
    CLASSICAL_IMPLICIT
        ↓ 如果工程模型进一步推导
    REASONABLE_HYPOTHESIS
        ↓ 纯工程推导
    ENGINEERING_DERIVED
    """
    SOURCE_UNVERIFIED = "SOURCE_UNVERIFIED"      # 来源未核验（现代整理/视频字幕，未找到原典逐字文本）
    CLASSICAL_EXPLICIT = "CLASSICAL_EXPLICIT"    # 原典明确（已找到原典逐字文本，原典直接表达）
    CLASSICAL_IMPLICIT = "CLASSICAL_IMPLICIT"    # 原典隐含（已找到原典逐字文本，原典没有形式化表达工程关系）
    REASONABLE_HYPOTHESIS = "REASONABLE_HYPOTHESIS"  # 合理假说（基于原典的工程推导，但原典没有明确支持）
    ENGINEERING_DERIVED = "ENGINEERING_DERIVED"  # 工程推导（纯工程模型推导，原典没有直接或间接支持）
    NOT_SUPPORTED = "NOT_SUPPORTED"              # 不支持（原典明确反对或没有任何支持）


class EvidenceStatus(Enum):
    """证据状态"""
    CANDIDATE = "CANDIDATE"          # 候选（现代整理，待原典核验）
    VERIFIED = "VERIFIED"            # 已核验（找到原典逐字文本）
    REJECTED = "REJECTED"            # 已拒绝（原典不支持）
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"  # 部分核验（找到部分原典支持）


# ============================================================================
# QI_TARGET 验证规则
# ============================================================================

@dataclass(frozen=True)
class QITargetVerification:
    """
    QI_TARGET 验证规则

    Target 必须由原文语境证明，而不能由工程师看到"气"后自行选择。
    Evidence Contract 应该至少要求：
    source_span ↓ target_span / semantic_anchor ↓ target classification
    """
    target: str                       # QI_TARGET 分类
    target_span: Optional[str]        # 原文中指向 target 的具体文本片段
    semantic_anchor: Optional[str]    # 语义锚点（原文中支持 target 分类的上下文）
    verification_method: str          # 验证方法（如何从原文推导出这个 target）
    is_verified: bool                 # 是否经过原文验证
    confidence: str                   # 置信度（HIGH/MEDIUM/LOW/UNCLEAR）
    notes: str = ""


# ============================================================================
# 修正后的证据条目
# ============================================================================

@dataclass(frozen=True)
class CorrectedQIEvidenceEntry:
    """修正后的气证据条目 — 严格区分原典核验状态"""
    entry_id: str
    source_chapter: str

    # 文本来源
    source_text_exact: Optional[str]   # 原典逐字文本（没有则为 None）
    normalization_note: Optional[str]   # 现代整理/概括
    text_source_type: str
    is_verified_exact: bool

    # 【修正】证据等级和状态
    evidence_level: EvidenceLevel       # 证据等级（修正后，大部分应为 SOURCE_UNVERIFIED）
    evidence_status: EvidenceStatus     # 证据状态（CANDIDATE/VERIFIED/...）

    # 气的概念和对象
    qi_concept: str
    qi_target: str
    qi_target_verification: Optional[QITargetVerification]  # QI_TARGET 验证

    # 语义分析（标注哪些是候选，哪些是原典支持）
    semantic_analysis_candidate: str    # 候选语义分析（基于现代整理）
    semantic_analysis_verified: Optional[str]  # 已核验语义分析（基于原典）

    # A-E 五个核心问题（标注置信度）
    question_a: str
    question_a_confidence: str
    question_b: str
    question_b_confidence: str
    question_c: str
    question_c_confidence: str
    question_d: str
    question_d_confidence: str
    question_e: str
    question_e_confidence: str

    # 关系分析（标注是否经过原典验证）
    related_conditions: List[str]
    relation_type: str
    relation_verified: bool

    # 禁止的推导（明确标注哪些推导是不允许的）
    forbidden_inferences: List[str]

    notes: str = ""


# ============================================================================
# 6 条证据的修正版
# ============================================================================

class CorrectedDTSQIEvidenceCorpus:
    """修正后的滴天髓"气"证据语料库 — 严格降级"""

    @staticmethod
    def get_all_entries() -> List[CorrectedQIEvidenceEntry]:
        return [
            # ============================================================
            # E001 修正版 — 最大幅度降级
            # ============================================================
            CorrectedQIEvidenceEntry(
                entry_id="DTS-QI-E001-R",
                source_chapter="通神论·第十七章 衰旺",

                source_text_exact=None,  # 【关键】未找到原典逐字文本
                normalization_note=(
                    "真正的旺是得令得地有根有气是真旺，"
                    "天干堆叠一堆五行地之无根无气只是虚旺假旺；"
                    "真正的衰是失令失地根气全无被克被泄，不是数量少就是衰"
                ),
                text_source_type="VIDEO_TRANSCRIPT",
                is_verified_exact=False,

                # 【修正】从 CLASSICAL_IMPLICIT 降级为 SOURCE_UNVERIFIED
                evidence_level=EvidenceLevel.SOURCE_UNVERIFIED,
                evidence_status=EvidenceStatus.CANDIDATE,

                qi_concept="YOU_QI",
                qi_target="DAY_MASTER",
                qi_target_verification=QITargetVerification(
                    target="DAY_MASTER",
                    target_span=None,  # 【修正】原文中没有明确指向"日主"的具体片段
                    semantic_anchor="真旺/真衰通常是针对日主而言的，但这是传统命理的默认假设，不是这段文本的明确表达",
                    verification_method="基于传统命理默认假设，不是原文明确表达",
                    is_verified=False,
                    confidence="MEDIUM",
                    notes="QI_TARGET=DAY_MASTER 是基于传统命理的默认假设，需要原典上下文进一步验证",
                ),

                semantic_analysis_candidate=(
                    "现代整理版将'有气'与得令、得地、有根并列为真旺的四个条件。"
                    "同时将'无根无气'列为虚旺假旺的表现，'根气全无'列为真衰的表现。"
                ),
                semantic_analysis_verified=None,  # 【修正】没有原典逐字文本，无法验证

                question_a=(
                    "现代整理版明确使用了'有气'这个概念，与得令、得地、有根并列。"
                    "但这是现代整理语言，不是原典逐字文本。"
                    "需要对照任铁樵注《滴天髓阐微》原典逐字核验。"
                    "从常见版本来看，'得令得地得势得生'等表述更常见，'有气'可能是后人的概括。"
                    "【置信度：LOW】原典是否使用'有气'作为特定术语，目前无法确认。"
                ),
                question_a_confidence="LOW",

                question_b=(
                    "在'真旺/真衰'这个语境中，'有气'可能描述的是日主的状态。"
                    "但这是基于传统命理的默认假设，不是这段文本的明确表达。"
                    "原典中'气'可以描述多个对象：日主、五行、全局、财星等。"
                    "【置信度：MEDIUM】需要原典上下文进一步验证。"
                ),
                question_b_confidence="MEDIUM",

                question_c=(
                    "现代整理版将'有气'与得令、得地、有根并列，但没有说明是 AND 还是 OR 关系。"
                    "'有气'可能依赖：得令？得地？有根？生扶？党众？流通？这些都不明确。"
                    "【置信度：LOW】依赖条件和组合逻辑原典没有形式化，当前只能标记为 UNCLEAR。"
                ),
                question_c_confidence="LOW",

                question_d=(
                    "【修正】之前的结论'有气应该是一个独立的观察维度'太早。"
                    "正确应该是：现代整理文本出现'有气' ↓ 候选语义 ↓ 可能是独立 Primitive ↓ "
                    "也可能是传统术语组合/概括 ↓ 必须核验原典。"
                    "'文本上并列'不等于'理论上独立'。"
                    "【置信度：LOW】是否是独立 Primitive，目前无法确认。"
                ),
                question_d_confidence="LOW",

                question_e=(
                    "'有气'不能直接参与身强/身弱的最终判断。"
                    "它只能作为旺衰判断的一个候选 Evidence / Qualifier。"
                    "在原典含义明确之前，不能进入生产级 Evidence，也不能进入最终身强身弱组合。"
                    "【置信度：HIGH】这是工程纪律，不依赖原典核验。"
                ),
                question_e_confidence="HIGH",

                related_conditions=["得令", "得地", "有根", "无根无气", "根气全无"],
                relation_type="PARALLEL (CANDIDATE)",  # 【修正】标注为候选
                relation_verified=False,

                # 【关键】明确禁止的推导
                forbidden_inferences=[
                    "❌ 禁止：现代整理文本并列出现 → 所以 = 独立 Primitive",
                    "❌ 禁止：source_text_exact=None → 标为 CLASSICAL_IMPLICIT",
                    "❌ 禁止：有气 = 有根",
                    "❌ 禁止：有气 = 得令",
                    "❌ 禁止：有气 → 身强",
                    "❌ 禁止：得令+得地+有根+有气 → 真旺（AND关系未经验证）",
                ],

                notes=(
                    "【最大幅度降级】E001 是整个 Corpus 的核心，但也是证据最薄弱的一条。"
                    "如果最后证明'得令得地有根有气'只是现代整理，而原典实际表达的是另外一套条件，"
                    "那么我们现在关于'有气 = 独立 Primitive'的整个假设都必须重新调整。"
                    "反过来，如果原典确实存在，并且上下文明确支持它，那么我们才真正开始有资格设计 YOU_QI 的工程语义。"
                ),
            ),

            # ============================================================
            # E002 修正版 — QI_JIN ≠ YOU_QI
            # ============================================================
            CorrectedQIEvidenceEntry(
                entry_id="DTS-QI-E002-R",
                source_chapter="通神论·第五章 理气",

                source_text_exact=None,
                normalization_note=(
                    "金木水火土不是固定的实体符号，是一年四季流转进退胜衰的气场。"
                    "气进则旺，气退则衰，气进则稳，气动则变。"
                    "判断格局高低先看气化，再看五行。"
                ),
                text_source_type="VIDEO_TRANSCRIPT",
                is_verified_exact=False,

                evidence_level=EvidenceLevel.SOURCE_UNVERIFIED,
                evidence_status=EvidenceStatus.CANDIDATE,

                qi_concept="QI_JIN",
                qi_target="FIVE_ELEMENT",
                qi_target_verification=QITargetVerification(
                    target="FIVE_ELEMENT",
                    target_span=None,
                    semantic_anchor="'金木水火土不是固定的实体符号，是一年四季流转进退胜衰的气场' — 这里明确讨论的是五行",
                    verification_method="现代整理文本明确提到'金木水火土'，因此 QI_TARGET=FIVE_ELEMENT",
                    is_verified=False,  # 【修正】虽然文本明确，但仍是现代整理，不是原典逐字
                    confidence="HIGH",
                    notes="QI_TARGET=FIVE_ELEMENT 在现代整理文本中有明确支持，但仍需原典逐字核验",
                ),

                semantic_analysis_candidate=(
                    "现代整理版明确指出：五行不是固定实体，而是流转进退胜衰的气场。"
                    "气进 → 旺、稳；气退 → 衰；气动 → 变。"
                    "判断格局高低先看气化，再看五行。"
                ),
                semantic_analysis_verified=None,

                question_a=(
                    "现代整理版明确使用了'气进则旺，气退则衰'的表述。"
                    "这与滴天髓第五章'理气'的主题一致，很可能是对原典的准确概括。"
                    "但需要对照原典逐字核验具体表述。"
                    "【置信度：MEDIUM】概念很可能存在，但具体表述需核验。"
                ),
                question_a_confidence="MEDIUM",

                question_b=(
                    "这里的'气'描述的是五行（金木水火土）的状态，QI_TARGET = FIVE_ELEMENT。"
                    "不是日主的'有气/无气'，而是五行之气本身的进退规律。"
                    "【置信度：HIGH】现代整理文本明确提到'金木水火土'。"
                ),
                question_b_confidence="HIGH",

                question_c=(
                    "气的进退依赖：四季流转、月令、五行生克。"
                    "气进 → 旺（因果关系，CAUSAL）。"
                    "气退 → 衰（因果关系，CAUSAL）。"
                    "但这是现代整理版的语义理解，需原典核验。"
                    "【置信度：MEDIUM】因果关系在文本中比较明确，但仍需原典核验。"
                ),
                question_c_confidence="MEDIUM",

                question_d=(
                    "'气进/气退'是描述五行状态的独立概念，不是'有气'的同义词。"
                    "【修正】之前的推导'有气可能意味着日主五行处于气进状态'不能接受。"
                    "QI_JIN ≠ YOU_QI，至少目前如此。"
                    "【置信度：HIGH】这是两个不同层次的概念，禁止跨概念推导。"
                ),
                question_d_confidence="HIGH",

                question_e=(
                    "'气进则旺，气退则衰'可以作为旺衰判断的一个理论原则（Qualifier）。"
                    "但不能直接用'气进'就判断身强，因为还需要考虑其他条件。"
                    "这个原则更多是理论层面的指导，不是具体的判断规则。"
                    "【置信度：MEDIUM】作为理论原则可以接受，作为具体判断规则需谨慎。"
                ),
                question_e_confidence="MEDIUM",

                related_conditions=["四季流转", "月令", "五行生克", "气化", "旺衰"],
                relation_type="CAUSAL (CANDIDATE)",
                relation_verified=False,

                forbidden_inferences=[
                    "❌ 禁止：QI_JIN = YOU_QI（气进 ≠ 有气）",
                    "❌ 禁止：有气可能意味着日主五行处于气进状态（跨概念推导）",
                    "❌ 禁止：气进 → 身强（理论原则 ≠ 具体判断）",
                ],

                notes=(
                    "【关键修正】QI_JIN ≠ YOU_QI。"
                    "'气进则旺，气退则衰'讨论的是一个动态的五行气化语境；"
                    "而'有气'是否就是'气进'，没有证据。"
                    "这两个概念必须保持隔离，直到原典明确说明它们的关系。"
                ),
            ),

            # ============================================================
            # E003 修正版 — 气势方向正确，但仍需降级
            # ============================================================
            CorrectedQIEvidenceEntry(
                entry_id="DTS-QI-E003-R",
                source_chapter="通神论·第三十二章 重寡",

                source_text_exact=None,
                normalization_note=(
                    "势大于数，哪怕只有一个五行只要占据关键位置掌控全局气势就能制衡全局。"
                    "五行数量再多杂乱无章互相牵制也成不了气候。"
                ),
                text_source_type="VIDEO_TRANSCRIPT",
                is_verified_exact=False,

                evidence_level=EvidenceLevel.SOURCE_UNVERIFIED,
                evidence_status=EvidenceStatus.CANDIDATE,

                qi_concept="QI_SHI",
                qi_target="WHOLE_CHART",
                qi_target_verification=QITargetVerification(
                    target="WHOLE_CHART",
                    target_span=None,
                    semantic_anchor="'掌控全局气势'、'制衡全局' — 这里明确讨论的是全局",
                    verification_method="现代整理文本明确提到'全局气势'，因此 QI_TARGET=WHOLE_CHART",
                    is_verified=False,
                    confidence="HIGH",
                    notes="QI_TARGET=WHOLE_CHART 在现代整理文本中有明确支持，但仍需原典逐字核验",
                ),

                semantic_analysis_candidate=(
                    "现代整理版明确提出'势大于数'的原则。"
                    "气势是全局层面的结构状态，不是简单的五行数量。"
                    "一个关键位置的五行可以掌控全局气势，数量多但杂乱也成不了气候。"
                ),
                semantic_analysis_verified=None,

                question_a=(
                    "现代整理版明确使用了'势大于数'和'全局气势'的表述。"
                    "这与滴天髓第三十二章'重寡'的主题一致，很可能是对原典的准确概括。"
                    "但需要对照原典逐字核验。"
                    "【置信度：MEDIUM】概念很可能存在，但具体表述需核验。"
                ),
                question_a_confidence="MEDIUM",

                question_b=(
                    "'气势'描述的是全局（WHOLE_CHART）的状态。"
                    "不是日主的'有气'，而是整个命局的力量结构。"
                    "【置信度：HIGH】现代整理文本明确提到'全局气势'。"
                ),
                question_b_confidence="HIGH",

                question_c=(
                    "气势依赖：关键位置、五行集中度、力量方向、全局结构。"
                    "气势与数量的关系：势大于数（气势比数量更重要）。"
                    "气势与'有气'的关系：不明确。气势可能是比'有气'更高层次的概念。"
                    "【置信度：MEDIUM】势大于数在文本中比较明确，但与有气的关系不明确。"
                ),
                question_c_confidence="MEDIUM",

                question_d=(
                    "'气势'是一个独立的高层结构概念（STRUCTURE 层），"
                    "不是'有气'的同义词，也不是简单的条件组合。"
                    "气势涉及全局的位置、集中度、方向等结构性因素。"
                    "【置信度：HIGH】这是一个独立的高层概念。"
                ),
                question_d_confidence="HIGH",

                question_e=(
                    "'气势'不能直接参与身强/身弱的最终判断。"
                    "它是全局结构的一个观察维度，可以作为旺衰判断的 Qualifier。"
                    "气势强不等于身强，因为气势可能是某一行的强势，不一定是日主的强势。"
                    "【置信度：HIGH】这是工程纪律，气势 ≠ 身强。"
                ),
                question_e_confidence="HIGH",

                related_conditions=["关键位置", "五行数量", "全局结构", "制衡", "掌控"],
                relation_type="QUALIFIER (CANDIDATE)",
                relation_verified=False,

                forbidden_inferences=[
                    "❌ 禁止：QI_SHI = STRONG → DAY_MASTER = STRONG（跨对象推导）",
                    "❌ 禁止：气势 = 有气（不同层次概念）",
                    "❌ 禁止：气势 = 五行数量（势大于数明确反对）",
                ],

                notes=(
                    "【方向正确】E003 的方向非常好，坚持了势 ≠ 数，气势 ≠ 身强。"
                    "但仍需降级为 SOURCE_UNVERIFIED，因为 source_text_exact = None。"
                    "建议将'气势强不等于身强'这个原则直接锁死，以后工程里绝对不能 QI_SHI=STRONG → DAY_MASTER=STRONG。"
                ),
            ),

            # ============================================================
            # E004 修正版 — 根气是合并表述
            # ============================================================
            CorrectedQIEvidenceEntry(
                entry_id="DTS-QI-E004-R",
                source_chapter="通神论·从象/假从（第十三章体用相关）",

                source_text_exact=None,
                normalization_note=(
                    "真正的真从格要求日主毫无根气毫无依托，全局气势专一一气顺从顺势而成格局。"
                    "假从就是日主身弱但暗藏根气留有后路，暂时顺从大势。"
                ),
                text_source_type="VIDEO_TRANSCRIPT",
                is_verified_exact=False,

                evidence_level=EvidenceLevel.SOURCE_UNVERIFIED,
                evidence_status=EvidenceStatus.CANDIDATE,

                qi_concept="GEN_QI",
                qi_target="DAY_MASTER",
                qi_target_verification=QITargetVerification(
                    target="DAY_MASTER",
                    target_span=None,
                    semantic_anchor="'日主毫无根气' — 这里明确指向日主",
                    verification_method="现代整理文本明确提到'日主毫无根气'，因此 QI_TARGET=DAY_MASTER",
                    is_verified=False,
                    confidence="HIGH",
                    notes="QI_TARGET=DAY_MASTER 在现代整理文本中有明确支持，但仍需原典逐字核验",
                ),

                semantic_analysis_candidate=(
                    "现代整理版在从格的语境中使用了'根气'概念。"
                    "真从格要求日主'毫无根气'，假从格是'暗藏根气'。"
                    "这里'根气'将根和气合并表述，说明在从格的判断中，根和气是一起考虑的。"
                ),
                semantic_analysis_verified=None,

                question_a=(
                    "现代整理版使用了'毫无根气'和'暗藏根气'的表述。"
                    "这与从格理论的常见表述一致，很可能是对原典的准确概括。"
                    "但需要对照原典逐字核验。"
                    "【置信度：MEDIUM】概念很可能存在，但具体表述需核验。"
                ),
                question_a_confidence="MEDIUM",

                question_b=(
                    "'根气'描述的是日主的状态，QI_TARGET = DAY_MASTER。"
                    "在从格的语境中，日主有根气还是无根气直接影响从格的真假。"
                    "【置信度：HIGH】现代整理文本明确提到'日主毫无根气'。"
                ),
                question_b_confidence="HIGH",

                question_c=(
                    "'根气'是根和气的合并表述，两者在这个语境中是并列关系（PARALLEL）。"
                    "真从格：毫无根气（根和气都没有）。"
                    "假从格：暗藏根气（根或气有一点）。"
                    "但这是从格语境中的实用表述，不能拿这个语境反过来定义'气'。"
                    "【置信度：MEDIUM】在从格语境中关系比较明确，但不能推广到一般旺衰判断。"
                ),
                question_c_confidence="MEDIUM",

                question_d=(
                    "'根气'在从格语境中是一个合并概念，不是对'气'的独立定义。"
                    "它更多是从格判断中的一个实用表述，将根和气一起考虑。"
                    "不能从这个语境中推导'气'的独立含义。"
                    "【置信度：HIGH】这是从格语境中的合并表述，不是气的独立定义。"
                ),
                question_d_confidence="HIGH",

                question_e=(
                    "'根气'在从格判断中是关键条件，但不能直接用于身强/身弱的一般判断。"
                    "从格是特殊格局，有自己的判断逻辑，不能推广到一般旺衰判断。"
                    "'毫无根气'在从格中意味着真从，不等于一般意义上的'身弱'。"
                    "【置信度：HIGH】从格是特殊格局，不能推广到一般旺衰判断。"
                ),
                question_e_confidence="HIGH",

                related_conditions=["真从格", "假从格", "全局气势专一", "大运帮扶", "破格"],
                relation_type="PARALLEL (CANDIDATE, 从格语境)",
                relation_verified=False,

                forbidden_inferences=[
                    "❌ 禁止：根气 = 根（根 ≠ 气，根气是合并表述）",
                    "❌ 禁止：从格语境中的根气 → 一般旺衰判断中的有气",
                    "❌ 禁止：通根 → 有根 → 有气 → 身强（自动链）",
                ],

                notes=(
                    "【处理正确】E004 没有犯'根气 = 根'的错误。"
                    "它指出'根气'是从格语境里的合并表述，不能拿这个语境反过来定义'气'。"
                    "根、气、根气三个东西必须先保持区分。"
                ),
            ),

            # ============================================================
            # E005 修正版 — 本气 ≠ 有气
            # ============================================================
            CorrectedQIEvidenceEntry(
                entry_id="DTS-QI-E005-R",
                source_chapter="通神论·第七章 天干",

                source_text_exact=None,
                normalization_note=(
                    "五阳从气不从事，五阴从事无情意。"
                    "甲丙戊庚壬五个阳干本性刚正坚守自身本气，哪怕全局大势强盛也不会轻易顺从格局。"
                ),
                text_source_type="VIDEO_TRANSCRIPT",
                is_verified_exact=False,

                evidence_level=EvidenceLevel.SOURCE_UNVERIFIED,
                evidence_status=EvidenceStatus.CANDIDATE,

                qi_concept="BEN_QI",
                qi_target="FIVE_ELEMENT",
                qi_target_verification=QITargetVerification(
                    target="FIVE_ELEMENT",
                    target_span=None,
                    semantic_anchor="'甲丙戊庚壬五个阳干本性刚正坚守自身本气' — 这里明确讨论的是天干/五行",
                    verification_method="现代整理文本明确提到'五个阳干坚守自身本气'，因此 QI_TARGET=FIVE_ELEMENT",
                    is_verified=False,
                    confidence="HIGH",
                    notes="QI_TARGET=FIVE_ELEMENT 在现代整理文本中有明确支持，但仍需原典逐字核验",
                ),

                semantic_analysis_candidate=(
                    "现代整理版在天干的语境中使用了'本气'概念。"
                    "阳干'坚守自身本气'，说明每个天干都有自己的'本气'。"
                    "'五阳从气不从事'说明阳干更容易顺从'气'（全局气势/气化）。"
                ),
                semantic_analysis_verified=None,

                question_a=(
                    "现代整理版使用了'坚守自身本气'和'五阳从气不从事'的表述。"
                    "'五阳从气不从事'是滴天髓的著名口诀，很可能是原典原文。"
                    "但需要对照原典逐字核验。"
                    "【置信度：MEDIUM】'五阳从气不从事'很可能是原典原文，但需核验。"
                ),
                question_a_confidence="MEDIUM",

                question_b=(
                    "'本气'描述的是天干（五行）的固有属性，QI_TARGET = FIVE_ELEMENT。"
                    "'从气不从事'中的'气'可能指全局气化趋势，QI_TARGET = WHOLE_CHART。"
                    "这两个语境中的'气'都不是日主的'有气'。"
                    "【置信度：HIGH】现代整理文本明确提到天干和全局大势。"
                ),
                question_b_confidence="HIGH",

                question_c=(
                    "'本气'是天干的固有属性，不依赖其他条件。"
                    "'从气不从事'说明阳干更容易顺从全局气化趋势。"
                    "这与'有气'的关系：日主'有气'可能意味着日主本气得到全局气化的支持，"
                    "但这个推导关系原典没有明确说明。"
                    "【置信度：LOW】与有气的关系不明确，禁止跨概念推导。"
                ),
                question_c_confidence="LOW",

                question_d=(
                    "'本气'是天干的固有属性，是一个独立概念。"
                    "'从气不从事'中的'气'是全局气化趋势，也是一个独立概念。"
                    "两者都与'有气'相关但不同，不能混为一谈。"
                    "【置信度：HIGH】这是两个独立概念，与有气不同。"
                ),
                question_d_confidence="HIGH",

                question_e=(
                    "'本气'和'从气不从事'可以作为天干属性和格局判断的 Qualifier。"
                    "但不能直接用于身强/身弱的最终判断。"
                    "阳干坚守本气不等于身强，阴干随势而变不等于身弱。"
                    "【置信度：HIGH】作为 Qualifier 可以，作为最终判断依据不行。"
                ),
                question_e_confidence="HIGH",

                related_conditions=["天干阴阳", "从气不从事", "全局大势", "格局顺从"],
                relation_type="QUALIFIER (CANDIDATE)",
                relation_verified=False,

                forbidden_inferences=[
                    "❌ 禁止：本气 = 有气（固有属性 ≠ 状态判断）",
                    "❌ 禁止：从气 = 有气（全局气化 ≠ 日主状态）",
                    "❌ 禁止：阳干坚守本气 → 身强",
                ],

                notes=(
                    "【处理正确】E005 坚持了本气 ≠ 有气。"
                    "'本气'更多是天干自身所属五行的本质属性，而'有气'是某对象当前是否具有某种气的状态。"
                    "这一层如果后面五部经典继续做下去，会非常重要。"
                ),
            ),

            # ============================================================
            # E006 修正版 — 财气独立对象
            # ============================================================
            CorrectedQIEvidenceEntry(
                entry_id="DTS-QI-E006-R",
                source_chapter="下篇六亲论·何知章（财气）",

                source_text_exact=None,
                normalization_note=(
                    "何知其人富，财气通门户。重点从来不是财多，是财气流通。"
                    "财星有源头有去路能为我所用，流通门户滋养日主才是真富足。"
                ),
                text_source_type="VIDEO_TRANSCRIPT",
                is_verified_exact=False,

                evidence_level=EvidenceLevel.SOURCE_UNVERIFIED,
                evidence_status=EvidenceStatus.CANDIDATE,

                qi_concept="CAI_QI",
                qi_target="WEALTH",
                qi_target_verification=QITargetVerification(
                    target="WEALTH",
                    target_span=None,
                    semantic_anchor="'财气通门户'、'财星有源头有去路' — 这里明确讨论的是财星",
                    verification_method="现代整理文本明确提到'财气'和'财星'，因此 QI_TARGET=WEALTH",
                    is_verified=False,
                    confidence="HIGH",
                    notes="QI_TARGET=WEALTH 在现代整理文本中有明确支持，但仍需原典逐字核验",
                ),

                semantic_analysis_candidate=(
                    "现代整理版在贫富判断的语境中使用了'财气'概念。"
                    "'财气通门户'是滴天髓何知章的著名口诀。"
                    "这里'财气'指财星的流通状态，不是日主的'有气'。"
                    "财气的关键是'流通'：有源头有去路，能为我所用，滋养日主。"
                ),
                semantic_analysis_verified=None,

                question_a=(
                    "现代整理版使用了'财气通门户'的表述。"
                    "这是滴天髓何知章的著名口诀，很可能是原典原文。"
                    "但需要对照原典逐字核验。"
                    "【置信度：MEDIUM】'财气通门户'很可能是原典原文，但需核验。"
                ),
                question_a_confidence="MEDIUM",

                question_b=(
                    "'财气'描述的是财星的状态，QI_TARGET = WEALTH。"
                    "不是日主的'有气'，而是财星这个特定十神的流通状态。"
                    "这说明'气'在滴天髓中可以描述不同对象：日主、五行、财星、官星等。"
                    "【置信度：HIGH】现代整理文本明确提到'财气'和'财星'。"
                ),
                question_b_confidence="HIGH",

                question_c=(
                    "财气依赖：财星有源头、有去路、能流通、能滋养日主。"
                    "财气与日主强弱的关系：日主身弱担不住财 → 财气不通。"
                    "这说明财气需要日主有足够的力量来承载，与日主'有气'可能相关。"
                    "但这个关系原典没有明确形式化。"
                    "【置信度：MEDIUM】财气的条件在文本中比较明确，但与日主有气的关系不明确。"
                ),
                question_c_confidence="MEDIUM",

                question_d=(
                    "'财气'是描述财星状态的独立概念，不是'有气'的同义词。"
                    "它是'气'在财星这个特定对象上的应用。"
                    "类似的还有'贵气'（官星的状态）等。"
                    "【置信度：HIGH】这是一个独立概念，是气在财星上的应用。"
                ),
                question_d_confidence="HIGH",

                question_e=(
                    "'财气通门户'是贫富判断的条件，不能直接用于身强/身弱的判断。"
                    "财气通可能意味着日主有足够力量承载财星，但这是间接推导，不是直接判断。"
                    "在贫富判断中，财气是核心条件；在旺衰判断中，财气只是一个参考因素。"
                    "【置信度：HIGH】财气是贫富判断的条件，不是旺衰判断的直接依据。"
                ),
                question_e_confidence="HIGH",

                related_conditions=["财星", "流通", "门户", "日主身弱", "财神反不真"],
                relation_type="CORRELATION (CANDIDATE)",
                relation_verified=False,

                forbidden_inferences=[
                    "❌ 禁止：财气 = 日主有气（不同对象）",
                    "❌ 禁止：财气通 → 身强（间接推导 ≠ 直接判断）",
                    "❌ 禁止：财星多 → 财气通（数量 ≠ 流通）",
                ],

                notes=(
                    "【很有价值】E006 更进一步证明了我们的核心架构："
                    "'气'应该理解成一种语义载体/状态描述机制，它可以作用于不同对象。"
                    "这意味着未来可能出现 QiState(target=DAY_MASTER, ...), QiState(target=FIVE_ELEMENT, ...), "
                    "QiState(target=WEALTH, ...), QiState(target=WHOLE_CHART, ...)。"
                    "这比简单搞一个 has_qi: bool 强得多。"
                ),
            ),
        ]

    @staticmethod
    def get_correction_summary() -> Dict[str, Any]:
        """修正摘要"""
        entries = CorrectedDTSQIEvidenceCorpus.get_all_entries()
        return {
            "total_entries": len(entries),
            "all_downgraded_to_source_unverified": True,
            "all_status_candidate": True,
            "all_source_text_exact_none": True,
            "all_is_verified_exact_false": True,
            "key_corrections": [
                "E001: 从 CLASSICAL_IMPLICIT 降级为 SOURCE_UNVERIFIED；'有气=独立Primitive'改为候选假设",
                "E002: QI_JIN ≠ YOU_QI，禁止跨概念推导",
                "E003: 气势方向正确，但仍降级为 SOURCE_UNVERIFIED；'气势强≠身强'原则锁死",
                "E004: 根气是从格语境合并表述，不能推广到一般旺衰判断",
                "E005: 本气 ≠ 有气，保持隔离",
                "E006: 财气独立对象，证明气是语义载体可作用于不同对象",
            ],
            "evidence_level_upgrade_flow": (
                "SOURCE_UNVERIFIED → (找到原典逐字文本) → CLASSICAL_EXPLICIT → "
                "(需要语义推导) → CLASSICAL_IMPLICIT → (工程模型进一步推导) → "
                "REASONABLE_HYPOTHESIS → (纯工程推导) → ENGINEERING_DERIVED"
            ),
            "forbidden_inferences_total": sum(len(e.forbidden_inferences) for e in entries),
        }


# ============================================================================
# 输出报告
# ============================================================================

def print_phase5_report():
    print("=" * 80)
    print("P0-2.9-E Phase 5: Evidence Level 重新定义 + 6 条证据降级修正")
    print("=" * 80)

    print("\n【修正背景】")
    print("  基于 b6133e9 的 🟡 CONDITIONAL PASS 裁决，修正以下关键问题：")
    print("  1. 把'研究假设'写得太接近'原典结论'")
    print("  2. '有气 = 独立 Primitive'的结论太早")
    print("  3. QI_JIN ≠ YOU_QI")
    print("  4. QI_TARGET 不能变成'自由解释器'")
    print("  5. EvidenceLevel 需要重新定义")

    # 修正摘要
    print("\n" + "=" * 80)
    print("【修正摘要】")
    print("=" * 80)

    summary = CorrectedDTSQIEvidenceCorpus.get_correction_summary()
    print(f"\n  总条目数: {summary['total_entries']}")
    print(f"  全部降级为 SOURCE_UNVERIFIED: {summary['all_downgraded_to_source_unverified']}")
    print(f"  全部状态为 CANDIDATE: {summary['all_status_candidate']}")
    print(f"  全部 source_text_exact = None: {summary['all_source_text_exact_none']}")
    print(f"  全部 is_verified_exact = False: {summary['all_is_verified_exact_false']}")
    print(f"  禁止推导总数: {summary['forbidden_inferences_total']}")

    print(f"\n  【证据等级升级流程】")
    print(f"    {summary['evidence_level_upgrade_flow']}")

    print(f"\n  【关键修正】")
    for i, c in enumerate(summary["key_corrections"], 1):
        print(f"    {i}. {c}")

    # 6 条证据的修正详情
    print("\n" + "=" * 80)
    print("【6 条证据修正详情】")
    print("=" * 80)

    entries = CorrectedDTSQIEvidenceCorpus.get_all_entries()
    for e in entries:
        print(f"\n{'='*60}")
        print(f"  {e.entry_id}: {e.source_chapter}")
        print(f"  气的概念: {e.qi_concept}")
        print(f"  气的对象: {e.qi_target}")
        print(f"  证据等级: {e.evidence_level.value} (修正前: CLASSICAL_IMPLICIT)")
        print(f"  证据状态: {e.evidence_status.value}")
        print(f"  source_text_exact: {e.source_text_exact}")
        print(f"  is_verified_exact: {e.is_verified_exact}")
        print(f"{'='*60}")

        print(f"\n  【A-E 五个核心问题（标注置信度）】")
        print(f"    A. [{e.question_a_confidence}] {e.question_a[:80]}...")
        print(f"    B. [{e.question_b_confidence}] {e.question_b[:80]}...")
        print(f"    C. [{e.question_c_confidence}] {e.question_c[:80]}...")
        print(f"    D. [{e.question_d_confidence}] {e.question_d[:80]}...")
        print(f"    E. [{e.question_e_confidence}] {e.question_e[:80]}...")

        if e.qi_target_verification:
            print(f"\n  【QI_TARGET 验证】")
            print(f"    target: {e.qi_target_verification.target}")
            print(f"    target_span: {e.qi_target_verification.target_span}")
            print(f"    is_verified: {e.qi_target_verification.is_verified}")
            print(f"    confidence: {e.qi_target_verification.confidence}")

        print(f"\n  【禁止的推导】({len(e.forbidden_inferences)} 条)")
        for f in e.forbidden_inferences:
            print(f"    {f}")

        if e.notes:
            print(f"\n  【备注】")
            print(f"    {e.notes[:120]}...")

    # 核心原则
    print("\n" + "=" * 80)
    print("【核心原则】")
    print("=" * 80)

    print("""
  1. 合理 ≠ 原典证明
  2. 文本上并列 ≠ 理论上独立
  3. 现代整理 ↓ 候选语义 ↓ 必须核验原典
  4. source_text_exact = None → 证据等级最高只能是 SOURCE_UNVERIFIED
  5. QI_TARGET 必须由原文语境证明，不能由工程师自由选择
  6. QI_JIN ≠ YOU_QI（禁止跨概念推导）
  7. 气势强 ≠ 身强（禁止跨对象推导）
  8. 先把证据钉死，再做辨

  证据等级升级流程：
  SOURCE_UNVERIFIED
      ↓ 找到原典逐字文本 + source_span + 原典上下文
  CLASSICAL_EXPLICIT
      ↓ 如果需要语义推导
  CLASSICAL_IMPLICIT
      ↓ 如果工程模型进一步推导
  REASONABLE_HYPOTHESIS
      ↓ 纯工程推导
  ENGINEERING_DERIVED
""")

    # 下一步
    print("\n" + "=" * 80)
    print("【下一步】")
    print("=" * 80)

    print("""
  不是继续增加 E007 E008 E009。

  而是先把这 6 条真正完成：
  DTS-QI-E001 ~ E006
  现代整理 ↓ 找到真正原典 ↓ 逐字 source_text_exact ↓ source_span ↓ 原典上下文
  ↓ 重新回答 A-E ↓ 重新判定 EvidenceLevel

  特别是 E001。
  因为 E001 如果最后证明'得令得地有根有气'只是现代整理，而原典实际表达的是另外一套条件，
  那么我们现在关于'有气 = 独立 Primitive'的整个假设都必须重新调整。

  反过来，如果原典确实存在，并且上下文明确支持它，
  那么我们才真正开始有资格设计 YOU_QI 的工程语义。

  项目总纪律不变：算准 → 辨准 → 解准；FROZEN ≠ PROVEN CORRECT。
  P6-CALC Calculation Integrity 仍是施工区和最高优先级。
""")


if __name__ == "__main__":
    print_phase5_report()
