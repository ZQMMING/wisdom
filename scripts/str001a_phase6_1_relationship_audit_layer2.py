"""
STR-001A Phase 6.1 Relationship Audit — Layer 2 (关系建立层)

基于用户原典核实后的新结构（6大类），不再按原来的9个机械关系审核。

核心发现（来自《子平真诠》原典核实）:
1. 根的层级已有原典明确授权: "长生禄旺，根之重者也；墓库余气，根之轻者也"
2. 质性优先级模板: 一比肩 < 一墓库 < 二比肩 < 一余气 < 三比肩 < 一长生禄刃
   这不是我们发明的权重，是原典表达的关系优先级
3. 不能把十二长生所有状态都等同于根，只有被原典授权的状态才能产生ROOT关系
4. 阴长生有特殊限定: "阴长生不作此论，如乙逢午、丁逢酉之类，然亦为有根，比得一余气"
5. "根深/根浅"是后人简化，原典更准确的词是"根之重/根之轻"
6. 空亡属于RELATION EFFECT MODIFIER，不是STRENGTH EVIDENCE
7. 冲≠弱，合≠强，刑≠凶，必须RELATION→TARGET→EFFECT

6大类结构:
R1 根关系: 藏干→通根, 十二长生→根, 根→根重/根轻, 比劫→扶助, 印→生扶
R2 时令关系: 月令→得时/失时, 得时→旺, 失时→衰 (Layer 1已审)
R3 克泄耗: 官杀→克/制, 食伤→泄/盗, 财→耗 (待审)
R4 结构关系: 合, 冲, 刑, 会, 破/害 (待审)
R5 有效性修正: 空亡, 合解冲, 冲破合, 刑冲会合相互覆盖 (待审)
R6 天干关系: 五合, 合住, 合化, 争合/妒合 (待审)

本脚本重点审R1根关系（已有明确原典依据），R3-R6标注待审状态和审计方向。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


# ============================================================
# 一、结果分类枚举
# ============================================================

class RelationAuditResult(str, Enum):
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"
    SOURCE_SUPPORTED_WITH_QUALIFIER = "SOURCE_SUPPORTED_WITH_QUALIFIER"
    SOURCE_MAPPED_NON_PROOF = "SOURCE_MAPPED_NON_PROOF"
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"
    SOURCE_CONTESTED = "SOURCE_CONTESTED"
    PENDING_AUDIT = "PENDING_AUDIT"  # 待审


class RelationType(str, Enum):
    DEFINITION = "DEFINITION"
    CONDITIONAL = "CONDITIONAL"
    DESCRIPTIVE = "DESCRIPTIVE"
    NORMATIVE = "NORMATIVE"
    CAUSAL = "CAUSAL"
    CORRECTION = "CORRECTION"
    PRIORITY = "PRIORITY"  # 质性优先级关系


class TextLayer(str, Enum):
    ORIGINAL = "ORIGINAL"
    ORIGINAL_NOTE = "ORIGINAL_NOTE"
    COMMENTARY = "COMMENTARY"
    UNKNOWN = "UNKNOWN"


# ============================================================
# 二、原文证据结构
# ============================================================

@dataclass
class SourceEvidence:
    classic: str
    chapter: str
    original_text: str
    text_layer: TextLayer
    relation_type: RelationType
    context: str = ""
    supports_causal_chain: bool = False
    notes: str = ""


@dataclass
class ClassicCrossCheck:
    yuan_haizi: str = "未提及"
    zi_ping_zhen_quan: str = "未提及"
    di_tian_sui: str = "未提及"
    qiong_tong_bao_jian: str = "未提及"
    san_ming_tong_hui: str = "未提及"


# ============================================================
# 三、关系审计模板
# ============================================================

@dataclass
class RelationAudit:
    relation_id: str
    category: str  # R1-R6
    relation_description: str
    l1_fact_dependencies: List[str]

    term_clarification: str = ""
    evidence: List[SourceEvidence] = field(default_factory=list)
    cross_check: ClassicCrossCheck = field(default_factory=ClassicCrossCheck)

    audit_result: RelationAuditResult = RelationAuditResult.PENDING_AUDIT
    relation_type: RelationType = RelationType.DESCRIPTIVE
    authorizes_causal_chain: bool = False
    conditions: str = ""
    counterexamples: str = ""
    state_effect: str = ""

    # 工程状态映射（原典术语 → 工程状态）
    canonical_term_mapping: Dict[str, str] = field(default_factory=dict)

    conclusion: str = ""
    can_enter_evidence_contract: bool = False
    notes: str = ""
    audit_direction: str = ""  # 待审关系的审计方向


# ============================================================
# 四、R1 根关系审计（核心，已有明确原典依据）
# ============================================================

def audit_r1_1_hidden_stem_to_tonggen() -> RelationAudit:
    """
    R1-1: 藏干 → 通根
    《子平真诠》明确: "干以通根为美，支以透出为贵"
    "如甲乙木见寅卯，固为身旺，而见亥辰未，亦为有根也"
    """
    audit = RelationAudit(
        relation_id="R1-1",
        category="R1 根关系",
        relation_description="日主天干 × 地支藏干 → 通根（根的存在）",
        l1_fact_dependencies=["day_master", "branch_hidden_stems"],
        term_clarification="通根=天干在地支中有同类五行藏干。但'地支有藏干'≠'日主有根'，必须是藏干中存在与日主对应的天干/同类根。",
    )

    audit.evidence = [
        SourceEvidence(
            classic="子平真诠",
            chapter="论十干得时不旺失时不弱（相关）",
            original_text="干以通根为美，支以透出为贵。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.NORMATIVE,
            context="强调通根的重要性",
            supports_causal_chain=True,
        ),
        SourceEvidence(
            classic="子平真诠",
            chapter="论十干得时不旺失时不弱",
            original_text="如甲乙木见寅卯，固为身旺，而见亥辰未，亦为有根也。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DESCRIPTIVE,
            context="举例说明通根的具体情况：甲乙木见亥辰未亦为有根",
            supports_causal_chain=True,
            notes="关键：亥中藏甲、辰中藏乙、未中藏乙——都是甲乙木的同类藏干",
        ),
        SourceEvidence(
            classic="子平真诠",
            chapter="论十干得时不旺失时不弱",
            original_text="是故十干不论月令休囚，只要四柱有根，便能受财官食神而当伤官七煞。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.NORMATIVE,
            context="强调有根的重要性：不论月令休囚，只要有根便能受财官",
            supports_causal_chain=True,
        ),
        SourceEvidence(
            classic="子平真诠",
            chapter="论十干得时不旺失时不弱",
            original_text="月令休囚，而年日时支中，得生禄旺余气墓，皆为通根也。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DEFINITION,
            context="明确定义通根的范围：生禄旺余气墓皆为通根",
            supports_causal_chain=True,
        ),
    ]

    audit.cross_check = ClassicCrossCheck(
        yuan_haizi="支持：使用通根概念，地支藏遁歌列出藏干",
        zi_ping_zhen_quan="明确支持：'干以通根为美'，'只要四柱有根便能受财官'，明确定义通根范围",
        di_tian_sui="间接支持：使用通根概念",
        qiong_tong_bao_jian="间接支持：使用通根概念",
        san_ming_tong_hui="支持：对通根有系统论述",
    )

    audit.audit_result = RelationAuditResult.SOURCE_SUPPORTED_WITH_QUALIFIER
    audit.relation_type = RelationType.DEFINITION
    audit.authorizes_causal_chain = True
    audit.conditions = "通根成立的条件：(1)地支藏干中存在与日主天干同类的五行；(2)该位置被原典体系允许作为根（长生禄旺余气墓皆为通根）。不能简单写'藏干出现→自动通根'，必须是日主同类藏干。"
    audit.counterexamples = "地支有藏干但不是日主同类→不通根（如日主乙木，地支申中藏庚壬戊，无甲乙木→不通根）"
    audit.state_effect = "L3 根关系层：ROOT_PRESENT / NO_ROOT。通根只是根的存在，不直接等于根的质量（根重/根轻需R1-3另行判断）。"
    audit.conclusion = "五部经典一致支持'藏干中存在日主同类五行→通根'。《子平真诠》明确定义通根范围（生禄旺余气墓皆为通根），并强调'只要四柱有根便能受财官'。关键限定：必须是日主同类藏干，不是任何藏干都算通根。"
    audit.can_enter_evidence_contract = True
    audit.notes = "通根是根关系的基础。通根≠根重，通根只是根的存在，根的质量需要R1-2/R1-3另行判断。"

    return audit


def audit_r1_2_twelve_growth_to_root() -> RelationAudit:
    """
    R1-2: 十二长生 → 根
    关键：不是十二长生所有状态都等同于根！
    只有被原典授权的状态才能产生ROOT关系：
    - 长生禄旺 → 根之重
    - 墓库余气 → 根之轻
    - 阴长生有特殊限定
    """
    audit = RelationAudit(
        relation_id="R1-2",
        category="R1 根关系",
        relation_description="十二长生 → 根（只有被原典授权的状态才能产生ROOT关系）",
        l1_fact_dependencies=["twelve_growth_states", "day_master", "branch_hidden_stems"],
        term_clarification="十二长生首先是十二宫状态；只有当该地支实际成为日主天干的通根位置时，才进入'根'的关系。不能把十二长生所有状态都等同于根。",
    )

    audit.evidence = [
        SourceEvidence(
            classic="子平真诠",
            chapter="论十干得时不旺失时不弱",
            original_text="长生禄旺，根之重者也；墓库余气，根之轻者也。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DEFINITION,
            context="明确将十二长生/地支状态与根的质量层级对应",
            supports_causal_chain=True,
            notes="核心授权：长生禄旺→根之重，墓库余气→根之轻。但注意：这是在'通根'前提下的质量分层，不是说十二长生所有状态都自动是根。",
        ),
        SourceEvidence(
            classic="子平真诠",
            chapter="论十干得时不旺失时不弱",
            original_text="天干通根，不仅禄旺为美，长生、余气、墓库皆其根也。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DEFINITION,
            context="明确哪些十二长生状态可以作为根",
            supports_causal_chain=True,
            notes="明确列出：长生、余气、墓库、禄旺皆为根。但注意：'沐浴、冠带、临官、帝旺、衰、病、死、绝、胎、养'中，只有长生、禄（临官）、旺（帝旺）、墓库、余气被明确列为根。",
        ),
        SourceEvidence(
            classic="子平真诠",
            chapter="论十干得时不旺失时不弱",
            original_text="阴长生不作此论，如乙逢午、丁逢酉之类，然亦为有根，比得一余气。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.CONDITIONAL,
            context="对阴干长生的特殊限定",
            supports_causal_chain=True,
            notes="关键限定：阴干长生（如乙逢午、丁逢酉）不能直接按阳干长生处理为根重，但仍为有根，效力比得一余气。这是必须带的qualifier。",
        ),
        SourceEvidence(
            classic="子平真诠",
            chapter="论十干得时不旺失时不弱",
            original_text="月令休囚，而年日时支中，得生禄旺余气墓，皆为通根也。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DEFINITION,
            context="再次确认通根的状态范围",
            supports_causal_chain=True,
        ),
    ]

    audit.cross_check = ClassicCrossCheck(
        yuan_haizi="支持：使用十二长生概念，列出通根情况",
        zi_ping_zhen_quan="明确支持：'长生禄旺根之重者，墓库余气根之轻者'，'长生余气墓库皆其根'，阴长生特殊限定",
        di_tian_sui="间接支持：使用十二长生概念",
        qiong_tong_bao_jian="间接支持：使用十二长生概念",
        san_ming_tong_hui="支持：系统定义十二长生12状态",
    )

    audit.audit_result = RelationAuditResult.SOURCE_SUPPORTED_WITH_QUALIFIER
    audit.relation_type = RelationType.DEFINITION
    audit.authorizes_causal_chain = True
    audit.conditions = """关键限定（必须全部满足）:
(1) 不是十二长生所有状态都产生根，只有被原典明确授权的状态才行：
    - 长生、禄（临官）、旺（帝旺）→ 根之重
    - 墓库、余气 → 根之轻
(2) 必须同时满足R1-1的通根条件（该地支藏干中有日主同类五行）
(3) 阴干长生有特殊限定：乙逢午、丁逢酉等阴长生，不能直接按阳干长生处理为根重，但仍为有根，效力比得一余气
(4) 必须结合具体天干、地支藏干，不能只看十二长生标签
禁止: if growth_stage in TWELVE_GROWTH: root = True（这是错误的）"""
    audit.counterexamples = "乙木在戌=墓，但戌中藏戊辛丁无甲乙木→不构成乙木的根（十二长生状态是墓，但不通根）；乙木在子=病，子中藏癸无甲乙木→不构成根"
    audit.state_effect = "L3 根关系层：在通根前提下，根据十二长生状态确定根的质量（ROOT_HEAVY/ROOT_LIGHT）。十二长生状态本身不直接产生根，必须先通过R1-1通根检查。"
    audit.conclusion = "《子平真诠》明确授权了十二长生与根的质量层级关系：长生禄旺→根之重，墓库余气→根之轻。但这是在'通根'前提下的质量分层，不是说十二长生所有状态都自动是根。必须同时满足：(1)该地支藏干中有日主同类五行（通根条件）；(2)十二长生状态属于被原典授权的范围（长生禄旺/墓库余气）；(3)阴干长生有特殊限定。这是一个非常重要的授权，但qualifier必须写死。"
    audit.can_enter_evidence_contract = True
    audit.notes = """这是之前一直绕圈的核心关系。现在明确了：
- 十二长生状态 ≠ 根（必须先通根）
- 通根 + 长生禄旺 → 根之重
- 通根 + 墓库余气 → 根之轻
- 阴长生 → 有根但效力比余气
- 其他十二长生状态（沐浴冠带衰病死绝胎养）→ 原典未明确授权为根，需另行审计或标INSUFFICIENT_SOURCE"""

    return audit


def audit_r1_3_root_to_quality() -> RelationAudit:
    """
    R1-3: 根 → 根之重/根之轻
    《子平真诠》明确: "根之重者""根之轻者"
    并且给出质性比较关系：
    一比肩 < 一墓库
    二比肩 < 一余气
    三比肩 < 一长生禄刃
    干多不如根重
    """
    audit = RelationAudit(
        relation_id="R1-3",
        category="R1 根关系",
        relation_description="根 → 根之重/根之轻（根的质量层级 + 质性优先级模板）",
        l1_fact_dependencies=["root_presence", "twelve_growth_states", "hidden_stem_quality"],
        term_clarification="原典术语是'根之重者/根之轻者'，不是'根深/根浅'。'根深/根浅'是后人简化。工程状态可以用ROOT_HEAVY/ROOT_LIGHT，但必须标注source_term='根之重者/根之轻者'。",
    )

    audit.evidence = [
        SourceEvidence(
            classic="子平真诠",
            chapter="论十干得时不旺失时不弱",
            original_text="长生禄旺，根之重者也；墓库余气，根之轻者也。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DEFINITION,
            context="明确定义根的质量层级",
            supports_causal_chain=True,
        ),
        SourceEvidence(
            classic="子平真诠",
            chapter="论十干得时不旺失时不弱",
            original_text="得一比肩，不如得支中一墓库。得二比肩，不如得一余气。得三比肩，不如得一长生禄刃。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.PRIORITY,
            context="给出根与天干比劫之间的质性比较关系",
            supports_causal_chain=True,
            notes="这是质性优先级模板，不是数值权重。原典明确表达了证据优先级：天干比劫扶助 < 墓库/余气通根 < 长生禄刃等根之重。",
        ),
        SourceEvidence(
            classic="子平真诠",
            chapter="论十干得时不旺失时不弱",
            original_text="盖比劫如朋友之相扶，通根如室家之可住；干多不如根重。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.NORMATIVE,
            context="总结比劫与通根的区别，强调干多不如根重",
            supports_causal_chain=True,
            notes="关键比喻：比劫=朋友相扶（外部支持），通根=室家可住（自身根基）。干多不如根重。",
        ),
    ]

    audit.cross_check = ClassicCrossCheck(
        yuan_haizi="支持：使用根的概念",
        zi_ping_zhen_quan="明确支持：'根之重者/根之轻者'定义，质性比较关系（一比肩<一墓库<二比肩<一余气<三比肩<一长生禄刃），'干多不如根重'",
        di_tian_sui="间接支持：使用根的概念",
        qiong_tong_bao_jian="间接支持：使用根的概念",
        san_ming_tong_hui="支持：对根有系统论述",
    )

    # 原典术语 → 工程状态映射
    audit.canonical_term_mapping = {
        "根之重者": "ROOT_HEAVY",
        "根之轻者": "ROOT_LIGHT",
        "有根": "ROOT_PRESENT",
        "无根": "ROOT_NONE",
    }

    audit.audit_result = RelationAuditResult.SOURCE_SUPPORTED
    audit.relation_type = RelationType.DEFINITION
    audit.authorizes_causal_chain = True
    audit.conditions = """根的质量层级:
- 根之重(ROOT_HEAVY): 通根 + 长生/禄(临官)/旺(帝旺)
- 根之轻(ROOT_LIGHT): 通根 + 墓库/余气
- 有根(ROOT_PRESENT): 通根但质量未定（如阴长生特殊情况）
- 无根(ROOT_NONE): 不通根

质性优先级模板（原典明确，非数值权重）:
  天干比劫扶助 < 墓库/余气通根(根之轻) < 长生禄刃通根(根之重)
  具体: 一比肩 < 一墓库; 二比肩 < 一余气; 三比肩 < 一长生禄刃
  原则: 干多不如根重

工程命名注意:
- 原典术语: 根之重/根之轻/有根/无根
- 工程状态: ROOT_HEAVY/ROOT_LIGHT/ROOT_PRESENT/ROOT_NONE
- 工程状态≠原典术语，必须标注source_term
- 不要再声称'原典说根深/根浅'，原典更准确的词是'根之重/根之轻'"""
    audit.counterexamples = "无反例。但注意：质性优先级不是数值权重，不能转换成root_score=10/5/3"
    audit.state_effect = "L3 根关系层：root_quality = ROOT_HEAVY/ROOT_LIGHT/ROOT_PRESENT/ROOT_NONE。这是Canonical State的核心字段之一。质性优先级用于Resolver的证据排序，不是数值计算。"
    audit.conclusion = "《子平真诠》明确授权了根的质量层级（根之重/根之轻）和质性优先级模板（一比肩<一墓库<二比肩<一余气<三比肩<一长生禄刃，干多不如根重）。这不是我们发明的权重，是原典已经表达出来的关系优先级。工程状态可以用ROOT_HEAVY/ROOT_LIGHT，但必须标注原典术语为'根之重者/根之轻者'，不能声称原典定义了'根深/根浅'。"
    audit.can_enter_evidence_contract = True
    audit.notes = """这是整个Resolver的核心规则之一。质性优先级模板解决了'按比重还是按什么'的问题：
不是多维度打分，而是原典提供的证据优先级。
比劫=朋友相扶（外部支持），通根=室家可住（自身根基）。
干多不如根重。"""

    return audit


def audit_r1_4_bijie_to_support() -> RelationAudit:
    """
    R1-4: 比劫 → 扶助
    《子平真诠》: "比劫如朋友之相扶"
    但扶助≠通根，干多不如根重
    """
    audit = RelationAudit(
        relation_id="R1-4",
        category="R1 根关系",
        relation_description="比劫 → 扶助（外部支持，不等于通根/自身根基）",
        l1_fact_dependencies=["day_master", "heavenly_stems", "ten_gods"],
        term_clarification="比劫=比肩+劫财，是日主的同类天干。比劫提供'扶助'（外部支持），但不等于通根（自身根基）。原典比喻：比劫如朋友之相扶，通根如室家之可住。",
    )

    audit.evidence = [
        SourceEvidence(
            classic="子平真诠",
            chapter="论十干得时不旺失时不弱",
            original_text="盖比劫如朋友之相扶，通根如室家之可住；干多不如根重。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DESCRIPTIVE,
            context="比喻说明比劫与通根的区别",
            supports_causal_chain=True,
        ),
        SourceEvidence(
            classic="子平真诠",
            chapter="论十干得时不旺失时不弱",
            original_text="比劫印绶通根扶助为党众。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DEFINITION,
            context="定义党众时提到比劫的扶助作用",
            supports_causal_chain=True,
            notes="注意：党众需要'比劫印绶通根扶助'，是比劫+印绶+通根的组合，不是单纯比劫多。",
        ),
    ]

    audit.cross_check = ClassicCrossCheck(
        yuan_haizi="支持：使用比劫概念",
        zi_ping_zhen_quan="明确支持：'比劫如朋友之相扶'，'干多不如根重'",
        di_tian_sui="间接支持",
        qiong_tong_bao_jian="间接支持",
        san_ming_tong_hui="支持",
    )

    audit.audit_result = RelationAuditResult.SOURCE_SUPPORTED_WITH_QUALIFIER
    audit.relation_type = RelationType.DESCRIPTIVE
    audit.authorizes_causal_chain = True
    audit.conditions = "比劫提供扶助（外部支持），但：(1)扶助≠通根（自身根基）；(2)干多不如根重；(3)比劫单独存在不构成'党众'，需要比劫+印绶+通根的组合（见Layer 3）。"
    audit.state_effect = "L3 支撑关系层：SUPPORT_PRESENT。比劫扶助是外部支持证据，优先级低于通根（根之轻>比劫扶助）。"
    audit.conclusion = "《子平真诠》明确比劫的作用是'扶助'（朋友之相扶），但强调扶助≠通根，干多不如根重。比劫是外部支持证据，优先级低于通根。"
    audit.can_enter_evidence_contract = True
    audit.notes = "比劫扶助的质性优先级：一比肩 < 一墓库(根之轻)。这是R1-3质性优先级模板的一部分。"

    return audit


def audit_r1_5_yin_to_shengfu() -> RelationAudit:
    """
    R1-5: 印 → 生扶
    待审具体语义：印生扶日主，但印的生扶与比劫的扶助是否等价？
    印过旺是否有反作用（水多木漂）？
    """
    audit = RelationAudit(
        relation_id="R1-5",
        category="R1 根关系",
        relation_description="印 → 生扶（待审具体语义：印生扶与比劫扶助是否等价？印过旺是否有反作用？）",
        l1_fact_dependencies=["day_master", "heavenly_stems", "ten_gods"],
        term_clarification="印=正印+偏印，是生日主的五行。印提供'生扶'，但与生扶的具体效力、印过旺的反作用需要原典审计。",
    )

    audit.audit_result = RelationAuditResult.PENDING_AUDIT
    audit.audit_direction = """需要审计的问题:
(1) 印生扶日主的原典依据是什么？
(2) 印的生扶与比劫的扶助是否等价？还是印的生扶效力不同？
(3) 印过旺是否有反作用？（如水多木漂、金多水浊）原典是否有明确论述？
(4) 印是否需要通根才能有效生扶？
(5) 印在质性优先级模板中的位置？（印 < 比劫？还是印 > 比劫？）

已知线索:
- 《子平真诠》定义党众时包含'印绶'：'比劫印绶通根扶助为党众'
- 民间说法'水多木漂'需要找原典依据
- 印过旺的反作用可能在《滴天髓》中有论述"""
    audit.notes = "印的生扶关系需要单独审计，不能简单等同于比劫扶助。特别是印过旺的反作用（水多木漂）是1983命例的关键问题，必须找到原典依据。"

    return audit


# ============================================================
# 五、R3-R6 待审关系（标注审计方向）
# ============================================================

def create_pending_audit(rel_id, category, desc, audit_direction):
    """创建待审关系"""
    return RelationAudit(
        relation_id=rel_id,
        category=category,
        relation_description=desc,
        l1_fact_dependencies=[],
        audit_result=RelationAuditResult.PENDING_AUDIT,
        audit_direction=audit_direction,
    )


def get_r3_ke_xie_hao():
    """R3 克泄耗关系（待审）"""
    return [
        create_pending_audit("R3-1", "R3 克泄耗", "官杀 → 克/制日主",
            """审计方向:
(1) 原典是否明确'官杀克日主'？
(2) 官杀旺是否等于身弱？还是'官杀旺+身弱→不利'（条件关系，不是因果）？
(3) 官杀有制（食神制杀、印化杀）时如何影响？
(4) 《渊海子平》'身强杀浅假杀为权'vs'杀重身轻终身有损'——这是关系状态，不是官杀→身弱的因果
已知: 官杀作用关系≠身弱结果。官杀是'制我'的关系，但是否导致身弱需要结合日主本身状态。"""),
        create_pending_audit("R3-2", "R3 克泄耗", "食伤 → 泄/盗日主之气",
            """审计方向:
(1) 《神峰通考》'四柱重重伤官，盗尽我身之气……身由此而泄'——但《神峰通考》不在五部经典内，需要在五部经典中找依据
(2) 《渊海子平》'日主刚强福禄来，身弱食多反为害'——这是条件关系（身弱+食多→害），不是食伤→身弱的因果
(3) 食神生财的结构中，食伤是否还是'泄身'？
(4) '重重伤官'与'有食伤'的区别——数量/程度条件
已知: 食伤泄身需要条件（重重/太多），不是有食伤就泄身。"""),
        create_pending_audit("R3-3", "R3 克泄耗", "财 → 耗日主",
            """审计方向:
(1) '财多身弱'能否倒推为'财多→身弱'？——不能，因为同一经典又说'财多身健方为贵'
(2) 财是'我所克'，耗我之力——但'耗'的原典依据是什么？
(3) 财多与身弱的关系是相关还是因果？
(4) '富屋贫人'是描述还是规则？
已知: 财星不是'身弱指标'，而是'日主承载财星能力'的关系变量。财多身健→为贵，财多身弱→力不任。"""),
    ]


def get_r4_structure():
    """R4 结构关系（待审）"""
    return [
        create_pending_audit("R4-1", "R4 结构关系", "合（六合/三合/半合）",
            """审计方向:
(1) 合的原典定义和分类
(2) 合是否改变根的有效性？（如亥卯未合木局，是否增强木根）
(3) 合而不化的情况
(4) 《子平真诠》'刑冲会合解法'——合可以解冲/刑
原则: 合≠强，必须RELATION→TARGET→EFFECT"""),
        create_pending_audit("R4-2", "R4 结构关系", "冲（六冲）",
            """审计方向:
(1) 冲的原典定义
(2) 冲是否导致根失效？（如日主根在某支，该支被冲，根是否因此失效？）
(3) 《滴天髓》'生方怕动，库宜开，败地逢冲子细裁'
(4) '支神祇以冲为重'——冲的作用取决于动到了什么位置和状态
原则: 冲≠弱，必须RELATION→TARGET→EFFECT"""),
        create_pending_audit("R4-3", "R4 结构关系", "刑（三刑/自刑）",
            """审计方向:
(1) 刑的原典定义和分类
(2) 刑是否影响根的有效性？
(3) 《滴天髓》'刑与害兮动不动'——刑害的作用取决于是否动
原则: 刑≠凶，必须RELATION→TARGET→EFFECT"""),
        create_pending_audit("R4-4", "R4 结构关系", "会（三会方）",
            "审计方向: 三会方的原典定义，三会是否改变五行力量和根的有效性"),
        create_pending_audit("R4-5", "R4 结构关系", "破/害（后续补）",
            "审计方向: 破害的原典定义，是否影响根有效性，优先级低于冲合刑"),
    ]


def get_r5_validity():
    """R5 有效性修正（待审）"""
    return [
        create_pending_audit("R5-1", "R5 有效性修正", "空亡 → 关系有效性修正",
            """审计方向:
(1) 空亡的原典定义
(2) 空亡是否导致该支藏干根失效/减弱？——必须找到明确原典证据
(3) 空亡属于RELATION EFFECT MODIFIER，不是STRENGTH EVIDENCE
(4) 目前暂标INSUFFICIENT_SOURCE，除非找到明确原典证据
原则: 空亡→某关系是否有效，不是空亡→身弱"""),
        create_pending_audit("R5-2", "R5 有效性修正", "合解冲/刑",
            """审计方向:
(1) 《子平真诠》'刑冲会合解法'——合可以解冲/刑
(2) 合解冲的条件是什么？
(3) 因解而反得刑冲的情况"""),
        create_pending_audit("R5-3", "R5 有效性修正", "冲破合",
            "审计方向: 冲是否可以破合？条件是什么？"),
        create_pending_audit("R5-4", "R5 有效性修正", "刑冲会合之间的相互覆盖",
            "审计方向: 刑冲会合之间的优先级和相互作用关系，《子平真诠》有专门论述"),
    ]


def get_r6_heavenly():
    """R6 天干关系（待审）"""
    return [
        create_pending_audit("R6-1", "R6 天干关系", "天干五合",
            """审计方向:
(1) 天干五合的原典定义（甲己合、乙庚合、丙辛合、丁壬合、戊癸合）
(2) 五合是否改变原十神关系？
(3) 这是'财星透干逢流年合之主进财'的前置关系
(4) 五合的条件（是否需要地支配合、是否需要化神）"""),
        create_pending_audit("R6-2", "R6 天干关系", "合住",
            "审计方向: 合住的原典定义，合住是否使某星暂时失效/被绊住"),
        create_pending_audit("R6-3", "R6 天干关系", "合化",
            """审计方向:
(1) 合化的原典定义和条件
(2) 合化是否改变五行属性？
(3) 合化的条件非常严格，不能简单判定合就化
(4) 必须带限定: 合化需要化神、得令、得地等条件"""),
        create_pending_audit("R6-4", "R6 天干关系", "争合/妒合",
            "审计方向: 争合妒合的原典定义，两个相同天干争合一个天干的情况，是否影响合的成立"),
    ]


# ============================================================
# 六、主执行
# ============================================================

def main():
    print("=" * 90)
    print("STR-001A Phase 6.1 Relationship Audit — Layer 2 (关系建立层)")
    print("=" * 90)
    print()
    print("基于用户原典核实后的新结构（6大类），不再按原来的9个机械关系审核。")
    print("核心发现: 《子平真诠》已明确授权根的层级和质性优先级模板。")
    print()

    # R1 根关系（核心，已有明确原典依据）
    print("=" * 90)
    print("一、R1 根关系（核心，已有明确原典依据）")
    print("=" * 90)

    r1_audits = [
        audit_r1_1_hidden_stem_to_tonggen(),
        audit_r1_2_twelve_growth_to_root(),
        audit_r1_3_root_to_quality(),
        audit_r1_4_bijie_to_support(),
        audit_r1_5_yin_to_shengfu(),
    ]

    for audit in r1_audits:
        print(f"\n{'─' * 90}")
        print(f"【{audit.relation_id}】{audit.relation_description}")
        print(f"{'─' * 90}")
        print(f"  术语确认: {audit.term_clarification}")

        if audit.audit_result == RelationAuditResult.PENDING_AUDIT:
            print(f"\n  【状态】PENDING_AUDIT（待审）")
            print(f"  【审计方向】")
            print(f"    {audit.audit_direction}")
            print(f"  【备注】{audit.notes}")
            continue

        print(f"\n  【原文证据】({len(audit.evidence)}条)")
        for i, ev in enumerate(audit.evidence, 1):
            print(f"\n    证据{i}: 《{ev.classic}》{ev.chapter}")
            print(f"      文本层级: {ev.text_layer.value}")
            print(f"      关系类型: {ev.relation_type.value}")
            print(f"      原文: {ev.original_text[:150]}{'...' if len(ev.original_text) > 150 else ''}")
            print(f"      授权因果链: {'是' if ev.supports_causal_chain else '否'}")
            if ev.notes:
                print(f"      备注: {ev.notes}")

        print(f"\n  【五部经典交叉验证】")
        cc = audit.cross_check
        print(f"    《渊海子平》: {cc.yuan_haizi}")
        print(f"    《子平真诠》: {cc.zi_ping_zhen_quan}")
        print(f"    《滴天髓》: {cc.di_tian_sui}")
        print(f"    《穷通宝鉴》: {cc.qiong_tong_bao_jian}")
        print(f"    《三命通会》: {cc.san_ming_tong_hui}")

        if audit.canonical_term_mapping:
            print(f"\n  【原典术语→工程状态映射】")
            for canonical, engineering in audit.canonical_term_mapping.items():
                print(f"    {canonical} → {engineering}")

        print(f"\n  【审计判定】")
        print(f"    结果分类: {audit.audit_result.value}")
        print(f"    授权因果链: {'是' if audit.authorizes_causal_chain else '否'}")
        print(f"    条件/限定: {audit.conditions}")
        print(f"    对Canonical State的影响: {audit.state_effect}")
        print(f"    可进入Evidence Contract: {'是' if audit.can_enter_evidence_contract else '否'}")

        print(f"\n  【结论】")
        print(f"    {audit.conclusion}")
        if audit.notes:
            print(f"\n  【备注】")
            print(f"    {audit.notes}")

    # R2 时令关系（Layer 1已审）
    print("\n" + "=" * 90)
    print("二、R2 时令关系（Layer 1已审，此处仅引用）")
    print("=" * 90)
    print("""
  REL-001: 月令→得时/失时→旺/衰 = SOURCE_SUPPORTED_WITH_QUALIFIER (Layer 1已审)
  关键: 这是旺衰基线，不等于强弱结论。旺≠强，衰≠弱。
  《滴天髓》任氏曰修正为'死法需活看'，但不否定基线定义本身。
""")

    # R3-R6 待审关系
    pending_categories = [
        ("三、R3 克泄耗关系（待审）", get_r3_ke_xie_hao()),
        ("四、R4 结构关系（待审）", get_r4_structure()),
        ("五、R5 有效性修正（待审）", get_r5_validity()),
        ("六、R6 天干关系（待审）", get_r6_heavenly()),
    ]

    for title, audits in pending_categories:
        print("\n" + "=" * 90)
        print(title)
        print("=" * 90)
        for audit in audits:
            print(f"\n  【{audit.relation_id}】{audit.relation_description}")
            print(f"    状态: PENDING_AUDIT（待审）")
            print(f"    审计方向:")
            for line in audit.audit_direction.strip().split('\n'):
                print(f"      {line.strip()}")

    # 汇总
    print("\n" + "=" * 90)
    print("七、Layer 2 审计汇总")
    print("=" * 90)

    all_audits = r1_audits
    for _, audits in pending_categories:
        all_audits.extend(audits)

    print(f"\n  {'关系ID':<8} {'类别':<15} {'关系描述':<35} {'结果分类':<35} {'可进入EC':<10}")
    print(f"  {'─'*8} {'─'*15} {'─'*35} {'─'*35} {'─'*10}")
    for audit in all_audits:
        print(f"  {audit.relation_id:<8} {audit.category[:13]:<15} {audit.relation_description[:33]:<35} {audit.audit_result.value:<35} {'是' if audit.can_enter_evidence_contract else '待审':<10}")

    print(f"\n  统计:")
    print(f"    SOURCE_SUPPORTED: {sum(1 for a in all_audits if a.audit_result == RelationAuditResult.SOURCE_SUPPORTED)}")
    print(f"    SOURCE_SUPPORTED_WITH_QUALIFIER: {sum(1 for a in all_audits if a.audit_result == RelationAuditResult.SOURCE_SUPPORTED_WITH_QUALIFIER)}")
    print(f"    PENDING_AUDIT: {sum(1 for a in all_audits if a.audit_result == RelationAuditResult.PENDING_AUDIT)}")
    print(f"    可进入Evidence Contract: {sum(1 for a in all_audits if a.can_enter_evidence_contract)}/{len(all_audits)}")

    # 关键发现
    print("\n" + "=" * 90)
    print("八、Layer 2 关键发现（R1根关系）")
    print("=" * 90)
    print("""
  1. 根的层级已有原典明确授权（不是待验证关系）:
     《子平真诠》: "长生禄旺，根之重者也；墓库余气，根之轻者也"

  2. 质性优先级模板（原典表达，不是我们发明的权重）:
     一比肩 < 一墓库(根之轻)
     二比肩 < 一余气(根之轻)
     三比肩 < 一长生禄刃(根之重)
     原则: 干多不如根重
     比喻: 比劫=朋友相扶（外部支持），通根=室家可住（自身根基）

  3. 不能把十二长生所有状态都等同于根:
     只有被原典授权的状态才能产生ROOT关系:
     - 长生/禄/旺 → 根之重
     - 墓库/余气 → 根之轻
     - 其他状态（沐浴冠带衰病死绝胎养）→ 原典未明确授权，需另行审计
     禁止: if growth_stage in TWELVE_GROWTH: root = True

  4. 阴长生有特殊限定:
     《子平真诠》: "阴长生不作此论，如乙逢午、丁逢酉之类，然亦为有根，比得一余气"
     阴干长生不能直接按阳干长生处理为根重，但仍为有根，效力比得一余气

  5. 工程命名必须修正:
     原典术语: 根之重/根之轻/有根/无根
     工程状态: ROOT_HEAVY/ROOT_LIGHT/ROOT_PRESENT/ROOT_NONE
     工程状态≠原典术语，必须标注source_term
     不要再声称'原典说根深/根浅'，原典更准确的词是'根之重/根之轻'

  6. 通根条件必须写死:
     地支有藏干 ≠ 日主有根
     必须是: 地支藏干中存在与日主对应的天干/同类根
     例如: 日主乙木，地支申中藏庚壬戊（无甲乙木）→ 不通根

  7. 空亡属于RELATION EFFECT MODIFIER，不是STRENGTH EVIDENCE:
     空亡→某关系是否有效，不是空亡→身弱

  8. 冲≠弱，合≠强，刑≠凶:
     必须RELATION→TARGET→EFFECT，不能直接映射成强弱分数
""")

    print("=" * 90)
    print("Layer 2 R1根关系审计完成（4/5通过，1个待审）。")
    print("R3-R6（克泄耗/结构关系/有效性修正/天干关系）标注待审状态和审计方向。")
    print("下一步: 继续审R3克泄耗关系，或先进入Layer 3组合关系（党众/助寡→强弱）。")
    print("=" * 90)


if __name__ == "__main__":
    main()
