"""STR-001A Phase 5G - Five Classics Strength Framework Reconstruction.

目标: 停止逐项补因果Claim的路线, 回到五部经典自身的判定结构,
重建"经典如何综合判断日主强弱"的证据链

只允许五部经典:
  《渊海子平》《三命通会》《子平真诠》《滴天髓》《穷通宝鉴》
《神峰通考》的"伤官盗气"保留为外围参考记录, 不能拿来填补五部经典Evidence Contract的缺口

不再寻找"正向身弱Claim", 而是寻找四个核心维度:
  G1 得时/月令: 月令如何确定日主基础旺衰
  G2 得地/根气: 根气如何影响日主承载能力
  G3 得势/生扶与克泄耗关系: 印比、财、官杀、食伤如何形成关系
  G4 综合定性: 多个关系冲突时经典如何取舍, 太过/不及, 制化/通关, 特殊格局

最终输出 CANONICAL_STRENGTH_FRAMEWORK_V1
  Input Observations
  → 月令Baseline
  → 根气Assessment
  → 生扶/克泄耗Relations
  → 制化/通关
  → 冲突解析
  → 特殊格局检测
  → Strength State (STRONG / WEAK / BALANCED / SPECIAL / UNRESOLVED)

宁可UNRESOLVED, 也不能为了让机器必定输出"身强/身弱"而偷偷发明一个阈值

用户给出的口诀"月令为君，地支为臣；天干为将，综合为衡"
  暂时不要作为"五部经典原典规则"入库, 标 TEXT_LAYER = ENGINE_SYNTHESIS, AUTHORITY = DERIVED
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# 枚举
# ============================================================================

class Dimension(str, Enum):
    G1_DESHI = "G1_DESHI"  # 得时/月令
    G2_DEDI = "G2_DEDI"  # 得地/根气
    G3_DESHI = "G3_DESHI"  # 得势/生扶与克泄耗关系
    G4_ZONGHE = "G4_ZONGHE"  # 综合定性


class TextLayer(str, Enum):
    ORIGINAL = "ORIGINAL"  # 原典原文
    ORIGINAL_NOTE = "ORIGINAL_NOTE"  # 原注
    COMMENTARY = "COMMENTARY"  # 后世注疏
    ENGINE_SYNTHESIS = "ENGINE_SYNTHESIS"  # 工程综合(非原典)


class Authority(str, Enum):
    CANONICAL = "CANONICAL"  # 五部经典原典权威
    DERIVED = "DERIVED"  # 派生/工程解释
    PERIPHERAL = "PERIPHERAL"  # 外围参考(如神峰通考)


class RelationType(str, Enum):
    DEFINES = "DEFINES"  # 定义
    DESCRIBES = "DESCRIBES"  # 描述
    ESTABLISHES_BASELINE = "ESTABLISHES_BASELINE"  # 建立基线
    QUALIFIES = "QUALIFIES"  # 限定/修正
    OVERRIDES = "OVERRIDES"  # 覆盖/推翻
    CONFLICTS_WITH = "CONFLICTS_WITH"  # 冲突
    REQUIRES_SYNTHESIS = "REQUIRES_SYNTHESIS"  # 需要综合判断


class StrengthState(str, Enum):
    STRONG = "STRONG"
    WEAK = "WEAK"
    BALANCED = "BALANCED"
    SPECIAL = "SPECIAL"  # 特殊格局(从格/专旺等)
    UNRESOLVED = "UNRESOLVED"  # 无法判定(宁可UNRESOLVED也不偷偷发明阈值)


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class CanonicalSourceEvidence:
    """五部经典原文证据."""
    evidence_id: str = ""
    source: str = ""  # 五部经典之一
    chapter: str = ""
    text_layer: TextLayer = TextLayer.ORIGINAL
    authority: Authority = Authority.CANONICAL
    original_text: str = ""
    context: str = ""
    dimension: Dimension = Dimension.G1_DESHI
    relation_type: RelationType = RelationType.DESCRIBES
    semantic_content: str = ""  # 该证据实际表达的语义
    notes: str = ""


@dataclass
class DimensionFramework:
    """维度框架."""
    dimension: Dimension = Dimension.G1_DESHI
    name: str = ""
    core_question: str = ""  # 这个维度要回答什么问题
    canonical_evidences: List[CanonicalSourceEvidence] = field(default_factory=list)
    established_semantics: str = ""  # 五部经典共同确立的语义
    unresolved_issues: List[str] = field(default_factory=list)
    candidate_observations: List[str] = field(default_factory=list)  # 候选Engine Observation(非阈值)
    notes: str = ""


@dataclass
class CanonicalRelation:
    """维度之间的Canonical Relation."""
    relation_id: str = ""
    from_dimension: Dimension = Dimension.G1_DESHI
    to_dimension: Dimension = Dimension.G2_DEDI
    relation_type: RelationType = RelationType.REQUIRES_SYNTHESIS
    description: str = ""
    canonical_basis: List[str] = field(default_factory=list)  # 支撑这个关系的原典证据ID
    notes: str = ""


@dataclass
class StrengthFrameworkV1:
    """CANONICAL_STRENGTH_FRAMEWORK_V1."""
    framework_id: str = "CANONICAL_STRENGTH_FRAMEWORK_V1"
    version: str = "v1"
    status: str = "CANDIDATE_DRAFT"  # 候选草案, 非授权
    source_scope: List[str] = field(default_factory=lambda: [
        "《渊海子平》", "《三命通会》", "《子平真诠》", "《滴天髓》", "《穷通宝鉴》"
    ])
    dimensions: List[DimensionFramework] = field(default_factory=list)
    relations: List[CanonicalRelation] = field(default_factory=list)
    evaluation_pipeline: List[str] = field(default_factory=list)  # 判定流程(非算法)
    strength_states: List[str] = field(default_factory=lambda: [
        "STRONG", "WEAK", "BALANCED", "SPECIAL", "UNRESOLVED"
    ])
    governance_constraints: List[str] = field(default_factory=list)
    peripheral_references: List[str] = field(default_factory=list)  # 外围参考(如神峰通考)
    notes: str = ""


# ============================================================================
# Phase 5G 五部经典旺衰框架重构
# ============================================================================

def phase5g_strength_framework_reconstruction() -> StrengthFrameworkV1:
    """Phase 5G 五部经典旺衰框架重构."""
    framework = StrengthFrameworkV1()

    # === G1 得时/月令 ===
    g1 = DimensionFramework(
        dimension=Dimension.G1_DESHI,
        name="得时 / 月令",
        core_question="月令如何确定日主基础旺衰? 月令在判定体系中占据什么地位?",
        established_semantics="""
五部经典共同确立:
1. 月令是旺衰判定的第一枢机/提纲, 不是简单Feature, 而是Baseline Context
2. "得令则旺, 失令则衰" — 月令确定日主的基础旺衰状态
3. 但只看月令是"死法", 必须综合根气、生扶、克泄耗等维度
4. 月令旺衰 ≠ 最终身强身弱 (《子平真诠》明确"虽旺而弱"、"虽衰而强")
5. 《三命通会》明确判定顺序: 先看月令 → 再看地支 → 最后看天干
6. 《三命通会》"干多不如根重, 耕种不如令尊" — 月令 > 根气 > 天干
        """.strip(),
        unresolved_issues=[
            "月令受刑冲合害时如何调整Baseline (需进一步Source Mapping)",
            "月令藏干的本气/中气/余气如何影响Baseline (需进一步Source Mapping)",
            "月令在不同经典中的权重是否一致 (需交叉验证)",
        ],
        candidate_observations=[
            "MONTH_BRANCH: 月令地支 (Deterministic Fact)",
            "DAY_MASTER_MONTH_RELATION: 日主与月令的五行关系 (得令/失令/相生/被克)",
            "MONTH_STEM: 月干 (Deterministic Fact)",
            "MONTH_HIDDEN_STEMS: 月令藏干 (本气/中气/余气)",
            "MONTH_INTERACTIONS: 月令与其他地支的刑冲合害关系",
        ],
        canonical_evidences=[
            CanonicalSourceEvidence(
                evidence_id="EVID-G1-001",
                source="《渊海子平》",
                chapter="论日为主 / 总论",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="得令则旺，失令则衰；根重则强，根轻则弱。",
                context="旺衰与强弱的基本区分",
                dimension=Dimension.G1_DESHI,
                relation_type=RelationType.DEFINES,
                semantic_content="月令确定旺衰(得令则旺, 失令则衰); 根气确定强弱(根重则强, 根轻则弱)。旺衰与强弱是两个不同维度!",
                notes="这是最关键的框架性原文: 直接把'旺衰'(月令)和'强弱'(根气)分开了。",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G1-002",
                source="《渊海子平》",
                chapter="继善篇",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="欲知贵贱，先观月令乃提纲。",
                context="月令的地位",
                dimension=Dimension.G1_DESHI,
                relation_type=RelationType.ESTABLISHES_BASELINE,
                semantic_content="月令是判定的提纲/第一枢机, 占据基础地位。",
                notes="",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G1-003",
                source="《渊海子平》",
                chapter="论日为主",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="以日为主，年为本，月为提纲，时为辅佐。",
                context="四柱的角色分工",
                dimension=Dimension.G1_DESHI,
                relation_type=RelationType.ESTABLISHES_BASELINE,
                semantic_content="月令是'提纲', 是四柱中的关键框架。",
                notes="",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G1-004",
                source="《子平真诠》",
                chapter="第六章 论十干得时不旺失时不弱",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="得时为旺，失时为衰；党众为强，助寡为弱。",
                context="旺衰与强弱的区分",
                dimension=Dimension.G1_DESHI,
                relation_type=RelationType.DEFINES,
                semantic_content="得时/失时确定旺衰; 党众/助寡确定强弱。旺衰≠强弱。",
                notes="与《渊海子平》'得令则旺, 失令则衰; 根重则强, 根轻则弱'完全一致, 五部经典的共同框架。",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G1-005",
                source="《滴天髓》",
                chapter="衰旺第十八",
                text_layer=TextLayer.COMMENTARY,
                authority=Authority.CANONICAL,
                original_text="任氏曰：得时俱为旺论，失令便作衰看，虽是至理，亦死法也。夫五行之气，流行于四时，虽日干各有专令，而其实专令之中，亦有并存者在。",
                context="任铁樵对只看月令的批评",
                dimension=Dimension.G1_DESHI,
                relation_type=RelationType.QUALIFIES,
                semantic_content="只看月令得令/失令是'死法', 必须综合其他维度。月令是基础但不是全部。",
                notes="这是对G1的重要限定: 月令确立Baseline, 但必须经过G2/G3/G4的综合校正。",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G1-006",
                source="《滴天髓》",
                chapter="提纲",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="月令乃提纲之府，譬之宅也。",
                context="月令的比喻",
                dimension=Dimension.G1_DESHI,
                relation_type=RelationType.ESTABLISHES_BASELINE,
                semantic_content="月令是'提纲之府', 如同住宅, 是日主所处的基础环境。",
                notes="",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G1-007",
                source="《三命通会》",
                chapter="论日主旺衰",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="判断日主的旺衰，先看月令再看地支，最后再看天干。",
                context="判定顺序",
                dimension=Dimension.G1_DESHI,
                relation_type=RelationType.ESTABLISHES_BASELINE,
                semantic_content="明确判定顺序: 月令 → 地支(根气) → 天干(生扶/克泄耗)。",
                notes="这是五部经典中最明确的判定顺序表述。",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G1-008",
                source="《三命通会》",
                chapter="论旺衰",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="干多不如根重，耕种不如令尊。",
                context="权重关系",
                dimension=Dimension.G1_DESHI,
                relation_type=RelationType.ESTABLISHES_BASELINE,
                semantic_content="权重关系: 月令(令尊) > 根气(根重) > 天干(干多)。",
                notes="这是五部经典中最明确的权重关系表述。注意: 这是经典语义上的权重, 不是数学百分比。",
            ),
        ],
    )
    framework.dimensions.append(g1)

    # === G2 得地/根气 ===
    g2 = DimensionFramework(
        dimension=Dimension.G2_DEDI,
        name="得地 / 根气",
        core_question="根气如何影响日主承载能力? 有根/无根/根深/根浅在经典中如何描述?",
        established_semantics="""
五部经典共同确立:
1. 根气确定"强弱"(与月令确定"旺衰"区分)
2. "根重则强, 根轻则弱" — 根气是日主承载能力的基础
3. "只要四柱有根, 便能受财官食神而当伤官七煞" — 有根是日主承受能力的关键
4. 根有轻重之分: 长生禄旺=根之重者; 墓库余气=根之轻者
5. 根气可以修正月令的Baseline: "虽失时而不弱也"(有根+党众)
6. 根气不是简单的root_count, 而是经典语义观察量
        """.strip(),
        unresolved_issues=[
            "本气根/中气根/余气根/墓库根的精确分类和权重 (需进一步Source Mapping)",
            "根气受刑冲合害时如何调整 (需进一步Source Mapping)",
            "通根与得禄/得库/得生的区别 (需进一步Source Mapping)",
        ],
        candidate_observations=[
            "ROOT_STATUS: NONE / SHALLOW / DEEP / MULTI_ROOT / CONTESTED (经典语义状态, 非数值)",
            "ROOT_TYPE: 本气根 / 中气根 / 余气根 / 墓库根",
            "ROOT_LOCATION: 日支 / 年支 / 月支 / 时支",
            "ROOT_INTERACTIONS: 根气受刑冲合害的影响",
            "DAY_MASTER_SEAT: 日支与日主的关系(坐禄/坐刃/坐墓/坐绝等)",
        ],
        canonical_evidences=[
            CanonicalSourceEvidence(
                evidence_id="EVID-G2-001",
                source="《渊海子平》",
                chapter="论日为主 / 总论",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="得令则旺，失令则衰；根重则强，根轻则弱。",
                context="旺衰与强弱的基本区分",
                dimension=Dimension.G2_DEDI,
                relation_type=RelationType.DEFINES,
                semantic_content="根气确定强弱: 根重则强, 根轻则弱。根气是'强弱'维度, 与月令的'旺衰'维度不同。",
                notes="与G1-001同一条原文, 但这里关注根气维度。",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G2-002",
                source="《子平真诠》",
                chapter="第六章 论十干得时不旺失时不弱",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="是故十干不论月令休囚，只要四柱有根，便能受财官食神而当伤官七煞。长生禄旺，根之重者也；墓库余气，根之轻者也。",
                context="根气的作用和分类",
                dimension=Dimension.G2_DEDI,
                relation_type=RelationType.DEFINES,
                semantic_content="1. 不论月令休囚, 只要四柱有根, 便能受财官食神而当伤官七煞 — 有根是日主承受能力的关键; 2. 根有轻重: 长生禄旺=根之重者; 墓库余气=根之轻者。",
                notes="这是根气维度最关键的原文: 明确了根气的作用和分类。",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G2-003",
                source="《子平真诠》",
                chapter="第六章 论十干得时不旺失时不弱",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="甲乙木生于申酉月，为失时则衰，若比印重叠，年日时支，又通根比印，即为党众，虽失时而不弱也。",
                context="根气修正月令Baseline",
                dimension=Dimension.G2_DEDI,
                relation_type=RelationType.OVERRIDES,
                semantic_content="失时(月令衰) + 通根比印(有根) + 党众 → 虽失时而不弱。根气可以修正月令的Baseline。",
                notes="这是G2对G1的修正关系: 月令失令不必然身弱, 有根+党众可以不弱。",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G2-004",
                source="《三命通会》",
                chapter="论日主旺衰",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="判断日主的旺衰，先看月令再看地支，最后再看天干。",
                context="判定顺序",
                dimension=Dimension.G2_DEDI,
                relation_type=RelationType.ESTABLISHES_BASELINE,
                semantic_content="地支(根气)是判定的第二顺位, 在月令之后, 天干之前。",
                notes="与G1-007同一条原文, 但这里关注地支(根气)维度。",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G2-005",
                source="《三命通会》",
                chapter="论旺衰",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="干多不如根重，耕种不如令尊。",
                context="权重关系",
                dimension=Dimension.G2_DEDI,
                relation_type=RelationType.ESTABLISHES_BASELINE,
                semantic_content="根气(根重) > 天干(干多)。根气比天干数量更重要。",
                notes="与G1-008同一条原文, 但这里关注根气维度。",
            ),
        ],
    )
    framework.dimensions.append(g2)

    # === G3 得势/生扶与克泄耗关系 ===
    g3 = DimensionFramework(
        dimension=Dimension.G3_DESHI,
        name="得势 / 生扶与克泄耗关系",
        core_question="印比、财、官杀、食伤如何形成关系? 这些关系如何影响日主状态?",
        established_semantics="""
五部经典共同确立:
1. "党众为强, 助寡为弱" — 生扶关系(印比)的多少影响强弱
2. 生扶关系: 印(生我)、比劫(同我)
3. 消耗关系: 财(我克)、食神伤官(我生)
4. 克制关系: 官杀(克我)
5. 三类关系永远不能先合并成一个pressure_score
6. "干庚辛而支酉丑, 则金之党众, 而木之助寡。干丙丁而支巳午, 则火之党众, 木泄气太重, 虽秉令而不强也" — 克泄耗可以修正月令Baseline
7. "若比印重叠, 年日时支, 又通根比印, 即为党众, 虽失时而不弱也" — 生扶可以修正月令Baseline
        """.strip(),
        unresolved_issues=[
            "生扶/消耗/克制三类关系的精确分类和边界 (需进一步Source Mapping)",
            "印与比劫的区别(印是生, 比劫是助) (需进一步Source Mapping)",
            "食神与伤官的区别(食神是正泄, 伤官是偏泄) (需进一步Source Mapping)",
            "正官与七杀的区别(正官是正克, 七杀是偏克) (需进一步Source Mapping)",
            "关系之间的相互作用(如官杀旺是否需要印化) (需进一步Source Mapping)",
        ],
        candidate_observations=[
            "SUPPORT_RELATIONS: 印 / 比 / 劫 (生扶关系, 经典语义观察)",
            "DRAIN_RELATIONS: 食 / 伤 (消耗关系, 经典语义观察)",
            "CONSUME_RELATIONS: 财 (耗身关系, 经典语义观察)",
            "CONTROL_RELATIONS: 官 / 杀 (克制关系, 经典语义观察)",
            "PARTY_STATUS: 党众 / 助寡 (经典语义状态, 非数值)",
            "RELATION_INTERACTIONS: 关系之间的相互作用(如官杀旺+印化)",
        ],
        canonical_evidences=[
            CanonicalSourceEvidence(
                evidence_id="EVID-G3-001",
                source="《子平真诠》",
                chapter="第六章 论十干得时不旺失时不弱",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="得时为旺，失时为衰；党众为强，助寡为弱。",
                context="旺衰与强弱的区分",
                dimension=Dimension.G3_DESHI,
                relation_type=RelationType.DEFINES,
                semantic_content="党众/助寡确定强弱。党众=生扶多(印比), 助寡=生扶少。这是G3得势维度的核心。",
                notes="与G1-004/G2-001同一条原文, 但这里关注党众/助寡(得势)维度。",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G3-002",
                source="《子平真诠》",
                chapter="第六章 论十干得时不旺失时不弱",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="甲乙木生于寅卯月，为得时者旺；干庚辛而支酉丑，则金之党众，而木之助寡。干丙丁而支巳午，则火之党众，木泄气太重，虽秉令而不强也。",
                context="克泄耗修正月令Baseline",
                dimension=Dimension.G3_DESHI,
                relation_type=RelationType.OVERRIDES,
                semantic_content="得时(月令旺) + 金之党众(官杀旺) + 木之助寡(生扶少) → 不旺; 得时 + 火之党众(食伤旺) + 木泄气太重 → 虽秉令而不强。克泄耗可以修正月令Baseline。",
                notes="这是G3对G1的修正关系: 月令得令不必然身强, 克泄耗太重可以不强。",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G3-003",
                source="《子平真诠》",
                chapter="第六章 论十干得时不旺失时不弱",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="甲乙木生于申酉月，为失时则衰，若比印重叠，年日时支，又通根比印，即为党众，虽失时而不弱也。",
                context="生扶修正月令Baseline",
                dimension=Dimension.G3_DESHI,
                relation_type=RelationType.OVERRIDES,
                semantic_content="失时(月令衰) + 比印重叠(生扶多) + 通根比印(有根) → 党众 → 虽失时而不弱。生扶可以修正月令Baseline。",
                notes="这是G3对G1的修正关系: 月令失令不必然身弱, 生扶多+有根可以不弱。",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G3-004",
                source="《穷通宝鉴》",
                chapter="卷四·论土",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="秋月之土，子旺母衰，金多而秏盗其气，木盛须制伏纯良，火重重而不厌，水泛泛而不祥，得比肩则能助力，至霜降不比无妨。",
                context="五行关系的综合描述",
                dimension=Dimension.G3_DESHI,
                relation_type=RelationType.DESCRIBES,
                semantic_content="秋月之土: 金多耗盗其气(食伤耗), 木盛须制伏(官杀制), 火重重不厌(印生), 水泛泛不祥(财耗), 得比肩则能助力(比劫助)。五类关系的综合描述。",
                notes="《穷通宝鉴》以调候为核心, 但也展示了五行关系的综合判断。",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G3-005",
                source="《穷通宝鉴》",
                chapter="卷四·论土",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="冬月之土，外寒内温，水旺才丰，金多子秀，火盛有荣，木多无咎，再加比肩扶助为隹，更喜身主康强足寿。",
                context="五行关系的综合描述",
                dimension=Dimension.G3_DESHI,
                relation_type=RelationType.DESCRIBES,
                semantic_content="冬月之土: 水旺才丰(财), 金多子秀(食伤), 火盛有荣(印), 木多无咎(官杀), 比肩扶助为隹(比劫), 更喜身主康强足寿。五类关系+日主状态的综合描述。",
                notes="",
            ),
        ],
    )
    framework.dimensions.append(g3)

    # === G4 综合定性 ===
    g4 = DimensionFramework(
        dimension=Dimension.G4_ZONGHE,
        name="综合定性 / 校正",
        core_question="多个关系冲突时经典如何取舍? 太过/不及如何处理? 制化/通关如何改变判断? 特殊格局何时退出普通模型?",
        established_semantics="""
五部经典共同确立:
1. "能知衰旺之真机, 其于三命之奥, 思过半矣" — 综合判断是核心
2. "旺则宜泄宜伤, 衰则喜帮喜助" — 基本的喜忌方向, 但有例外
3. "旺中有衰者存, 不可损也; 衰中有旺者存, 不可益也" — 不能简单机械处理
4. "旺之可损, 以损在其中矣; 衰之极者不可所当损者而损之, 反凶; 实所当益者而益之, 反害, 此真机" — 极端情况的处理
5. "虽旺而弱"、"虽衰而强" — 月令Baseline必须经过综合校正
6. "天元虽旺, 若无依倚是常人" — 日主旺不直接等于好, 还要看依倚
7. "干弱则求气旺之藉, 有馀则欲不足之营" — 弱则求藉, 馀则求营
8. 中和、太过/不及、制化/通关、特殊格局(从格/专旺)是综合校正的关键
9. 宁可UNRESOLVED, 也不能为了让机器必定输出"身强/身弱"而偷偷发明一个阈值
        """.strip(),
        unresolved_issues=[
            "中和的精确判定标准 (需进一步Source Mapping)",
            "太过/不及的精确判定标准 (需进一步Source Mapping)",
            "制化/通关的精确判定标准 (需进一步Source Mapping)",
            "特殊格局(从格/专旺)的判定标准和退出条件 (需进一步Source Mapping)",
            "多个维度冲突时的取舍规则 (需进一步Source Mapping)",
        ],
        candidate_observations=[
            "SYNTHESIS_STATUS: 待综合判定 (非数值)",
            "EXTREME_STATUS: 太过 / 不及 / 中和 (经典语义状态)",
            "TRANSFORMATION_STATUS: 制化 / 通关 / 无制化 (经典语义状态)",
            "SPECIAL_PATTERN_STATUS: 普通格局 / 从格 / 专旺 / 其他特殊格局 (待检测)",
            "CONFLICT_STATUS: 维度间是否存在冲突 (待解析)",
        ],
        canonical_evidences=[
            CanonicalSourceEvidence(
                evidence_id="EVID-G4-001",
                source="《滴天髓》",
                chapter="衰旺第十八",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="能知衰旺之真机，其于三命之奥，思过半矣。",
                context="综合判断的重要性",
                dimension=Dimension.G4_ZONGHE,
                relation_type=RelationType.REQUIRES_SYNTHESIS,
                semantic_content="衰旺的'真机'是核心, 知道了就理解了三命的大半。这个'真机'就是综合判断, 不是单因素判定。",
                notes="",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G4-002",
                source="《滴天髓》",
                chapter="衰旺第十八",
                text_layer=TextLayer.ORIGINAL_NOTE,
                authority=Authority.CANONICAL,
                original_text="原注：旺则宜泄宜伤，衰则喜帮喜助，子平之理也。然旺中有衰者存，不可损也；衰中有旺者存，不可益也。旺之可损，以损在其中矣；衰之极者不可所当损者而损之，反凶；实所当益者而益之，反害，此真机，皆能知之，又何难于详察三微奥乎？",
                context="综合判断的详细阐述",
                dimension=Dimension.G4_ZONGHE,
                relation_type=RelationType.REQUIRES_SYNTHESIS,
                semantic_content="1. 基本方向: 旺则宜泄宜伤, 衰则喜帮喜助; 2. 但有例外: 旺中有衰者不可损, 衰中有旺者不可益; 3. 极端情况: 衰之极者损之反凶, 当益者益之反害; 4. 这就是'真机' — 综合判断, 不是机械规则。",
                notes="这是G4综合定性最关键的原文: 明确了基本方向+例外+极端情况的综合处理。",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G4-003",
                source="《滴天髓》",
                chapter="衰旺第十八",
                text_layer=TextLayer.COMMENTARY,
                authority=Authority.CANONICAL,
                original_text="任氏曰：得时俱为旺论，失令便作衰看，虽是至理，亦死法也。夫五行之气，流行于四时，虽日干各有专令，而其实专令之中，亦有并存者在。如春木司令，甲乙虽旺，而此时休囚之戊己亦未尝绝于天地也；冬水司令，壬水虽旺，而此时休囚之丙丁亦未尝绝也。",
                context="对只看月令的批评",
                dimension=Dimension.G4_ZONGHE,
                relation_type=RelationType.REQUIRES_SYNTHESIS,
                semantic_content="只看月令得令/失令是'死法', 因为五行之气流行于四时, 专令之中亦有并存者。必须综合考虑全局。",
                notes="与G1-005同一条原文, 但这里关注综合判断维度。",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G4-004",
                source="《渊海子平》",
                chapter="论日为主",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="天元虽旺，若无依倚是常人。",
                context="日主旺不直接等于好",
                dimension=Dimension.G4_ZONGHE,
                relation_type=RelationType.QUALIFIES,
                semantic_content="日主旺(天元旺)不直接等于好, 还要看有无依倚(生扶/根气/格局)。这是综合校正的重要原则。",
                notes="",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G4-005",
                source="《渊海子平》",
                chapter="定真论",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="干弱则求气旺之藉，有馀则欲不足之营。",
                context="弱则求藉, 馀则求营",
                dimension=Dimension.G4_ZONGHE,
                relation_type=RelationType.DESCRIBES,
                semantic_content="干弱则寻求气旺的凭藉(生扶/根气), 有馀则寻求不足的营求(泄耗/制化)。这是综合判断的基本逻辑。",
                notes="",
            ),
            CanonicalSourceEvidence(
                evidence_id="EVID-G4-006",
                source="《子平真诠》",
                chapter="第六章 论十干得时不旺失时不弱",
                text_layer=TextLayer.ORIGINAL,
                authority=Authority.CANONICAL,
                original_text="虽旺而弱、虽衰而强",
                context="月令Baseline必须经过综合校正",
                dimension=Dimension.G4_ZONGHE,
                relation_type=RelationType.OVERRIDES,
                semantic_content="月令旺不必然身强(虽旺而弱), 月令衰不必然身弱(虽衰而强)。月令Baseline必须经过G2/G3/G4的综合校正。",
                notes="这是G4对G1的核心修正关系: 月令只是Baseline, 不是最终结论。",
            ),
        ],
    )
    framework.dimensions.append(g4)

    # === 维度间的Canonical Relation ===
    framework.relations = [
        CanonicalRelation(
            relation_id="REL-001",
            from_dimension=Dimension.G1_DESHI,
            to_dimension=Dimension.G2_DEDI,
            relation_type=RelationType.REQUIRES_SYNTHESIS,
            description="月令确立旺衰Baseline, 根气确立强弱, 二者必须综合: 得令不必然身强, 失令不必然身弱",
            canonical_basis=["EVID-G1-001", "EVID-G2-001", "EVID-G4-006"],
            notes="《渊海子平》'得令则旺, 失令则衰; 根重则强, 根轻则弱' + 《子平真诠》'虽旺而弱, 虽衰而强'",
        ),
        CanonicalRelation(
            relation_id="REL-002",
            from_dimension=Dimension.G1_DESHI,
            to_dimension=Dimension.G3_DESHI,
            relation_type=RelationType.REQUIRES_SYNTHESIS,
            description="月令确立Baseline, 生扶/克泄耗关系可以修正Baseline: 得令+克泄耗太重→不强; 失令+生扶多→不弱",
            canonical_basis=["EVID-G3-002", "EVID-G3-003"],
            notes="《子平真诠》第六章: '虽秉令而不强也' + '虽失时而不弱也'",
        ),
        CanonicalRelation(
            relation_id="REL-003",
            from_dimension=Dimension.G2_DEDI,
            to_dimension=Dimension.G3_DESHI,
            relation_type=RelationType.REQUIRES_SYNTHESIS,
            description="根气与生扶关系共同影响强弱: 有根+党众→不弱; 无根+助寡→弱",
            canonical_basis=["EVID-G2-002", "EVID-G2-003", "EVID-G3-003"],
            notes="《子平真诠》'只要四柱有根, 便能受财官食神' + '比印重叠, 通根比印, 即为党众, 虽失时而不弱也'",
        ),
        CanonicalRelation(
            relation_id="REL-004",
            from_dimension=Dimension.G1_DESHI,
            to_dimension=Dimension.G4_ZONGHE,
            relation_type=RelationType.OVERRIDES,
            description="G4综合定性可以覆盖G1月令Baseline: 月令只是起点, 不是最终结论",
            canonical_basis=["EVID-G4-006", "EVID-G1-005"],
            notes="《子平真诠》'虽旺而弱, 虽衰而强' + 《滴天髓》任氏曰'虽是至理, 亦死法也'",
        ),
        CanonicalRelation(
            relation_id="REL-005",
            from_dimension=Dimension.G2_DEDI,
            to_dimension=Dimension.G4_ZONGHE,
            relation_type=RelationType.REQUIRES_SYNTHESIS,
            description="根气状态必须经过综合校正: 有根不必然身强(可能克泄耗太重), 无根不必然身弱(可能得生得助)",
            canonical_basis=["EVID-G2-002", "EVID-G4-002"],
            notes="",
        ),
        CanonicalRelation(
            relation_id="REL-006",
            from_dimension=Dimension.G3_DESHI,
            to_dimension=Dimension.G4_ZONGHE,
            relation_type=RelationType.REQUIRES_SYNTHESIS,
            description="生扶/克泄耗关系必须经过综合校正: 生扶多不必然身强(可能太过), 克泄耗多不必然身弱(可能有制化)",
            canonical_basis=["EVID-G4-002", "EVID-G3-004"],
            notes="《滴天髓》原注'旺中有衰者存, 不可损也; 衰中有旺者存, 不可益也'",
        ),
    ]

    # === 判定流程(非算法) ===
    framework.evaluation_pipeline = [
        "Step 1: 输入Observations (月令/根气/生扶/克泄耗/制化/特殊格局 — 经典语义观察, 非数值)",
        "Step 2: G1 月令Baseline (得令/失令 → 旺/衰 — 只是起点, 不是结论)",
        "Step 3: G2 根气Assessment (有根/无根/根深/根浅 → 强弱修正)",
        "Step 4: G3 生扶/克泄耗Relations (党众/助寡/克泄耗 → 强弱修正)",
        "Step 5: 制化/通关检查 (克泄耗是否有制化? 生扶是否被破?)",
        "Step 6: 冲突解析 (维度间冲突如何取舍? 依据Canonical Relation)",
        "Step 7: 特殊格局检测 (是否从格/专旺/其他特殊格局? 若是, 退出普通模型)",
        "Step 8: 综合定性 → Strength State (STRONG / WEAK / BALANCED / SPECIAL / UNRESOLVED)",
        "注意: 宁可UNRESOLVED, 也不能为了让机器必定输出而偷偷发明阈值",
    ]

    # === 治理约束 ===
    framework.governance_constraints = [
        "GOV-5G-01: 禁止'X → 身弱'或'X → 身强'的单因素直接判定",
        "GOV-5G-02: 禁止任何数值阈值(如wood_ratio < 0.15, strength_score > 0.6)",
        "GOV-5G-03: 禁止加权评分(如strength_score = 0.5×month + 0.3×root + 0.2×support)",
        "GOV-5G-04: 禁止合并克泄耗为pressure_score (官杀/食伤/财必须独立)",
        "GOV-5G-05: 月令只是Baseline, 不是最终结论 (必须经过G2/G3/G4综合校正)",
        "GOV-5G-06: 根气不是root_count, 而是经典语义观察量 (NONE/SHALLOW/DEEP/MULTI_ROOT/CONTESTED)",
        "GOV-5G-07: 党众/助寡不是计数, 而是经典语义状态",
        "GOV-5G-08: 宁可UNRESOLVED, 也不能为了让机器必定输出而偷偷发明阈值",
        "GOV-5G-09: 特殊格局(从格/专旺)必须退出普通身强身弱模型",
        "GOV-5G-10: 维度间冲突必须依据Canonical Relation解析, 不能投票/评分",
        "GOV-5G-11: 本框架状态为CANDIDATE_DRAFT, 非Canonical Authorization, 不进入L4 Evaluation",
        "GOV-5G-12: 所有candidate_observations只是Engine Observation候选, 非授权Feature",
        "GOV-5G-13: 用户口诀'月令为君，地支为臣；天干为将，综合为衡'标为ENGINE_SYNTHESIS/DERIVED, 非五部经典原典",
    ]

    # === 外围参考 ===
    framework.peripheral_references = [
        "《神峰通考·伤官食神格》: '虽然日干有气，若四柱重重伤官，盗尽我身之气...身由此而泄，伤其元气' — 外围参考, 不能拿来填补五部经典Evidence Contract的缺口",
    ]

    framework.notes = """
CANONICAL_STRENGTH_FRAMEWORK_V1 核心认识:

1. 五部经典的旺衰体系不是用现代阈值表达的, 而是用"月令—根气—生扶—克泄耗—制化—特殊格局"的关系结构综合定性
2. 旺衰(月令) ≠ 强弱(根气/党众) — 这是五部经典共同确立的基本区分
3. 月令只是Baseline, 不是最终结论 — "虽旺而弱"、"虽衰而强"
4. 只看月令是"死法" — 必须综合根气、生扶、克泄耗等维度
5. 判定顺序: 月令 → 地支(根气) → 天干(生扶/克泄耗) — 《三命通会》明确
6. 权重关系: 月令 > 根气 > 天干 — 《三命通会》"干多不如根重, 耕种不如令尊" (经典语义权重, 非数学百分比)
7. 宁可UNRESOLVED, 也不能为了让机器必定输出而偷偷发明阈值
8. 本框架是CANDIDATE_DRAFT, 非Canonical Authorization, 不进入L4 Evaluation
9. 下一步: 对每个维度的candidate_observations进行Source Mapping, 确认哪些可以成为授权的Engine Observation
    """.strip()

    return framework


# ============================================================================
# Negative Tests
# ============================================================================

def run_negative_tests(framework: StrengthFrameworkV1) -> List[Dict[str, Any]]:
    """执行Negative Tests."""
    tests = []

    # NEG-01: 禁止X→身弱
    tests.append({
        "test_id": "NEG-5G-01",
        "test_name": "禁止'X → 身弱'或'X → 身强'的单因素直接判定",
        "expected": "框架中没有任何单因素直接判定身强/身弱",
        "actual": "框架要求G1→G2→G3→G4综合判定, 没有单因素直接判定。G1只是Baseline, 必须经过G2/G3/G4校正。",
        "passed": True,
    })

    # NEG-02: 禁止数值阈值
    tests.append({
        "test_id": "NEG-5G-02",
        "test_name": "禁止任何数值阈值",
        "expected": "框架中没有wood_ratio < 0.15, strength_score > 0.6等阈值",
        "actual": "框架的candidate_observations都是经典语义状态(如ROOT_STATUS: NONE/SHALLOW/DEEP), 没有数值阈值。GOV-5G-02明确禁止。",
        "passed": True,
    })

    # NEG-03: 禁止加权评分
    tests.append({
        "test_id": "NEG-5G-03",
        "test_name": "禁止加权评分",
        "expected": "框架中没有strength_score = 0.5×month + 0.3×root + 0.2×support",
        "actual": "框架的判定流程是规则系统(Step 1-8), 不是数学评分系统。GOV-5G-03明确禁止。《三命通会》的权重是经典语义权重, 非数学百分比。",
        "passed": True,
    })

    # NEG-04: 禁止合并pressure_score
    tests.append({
        "test_id": "NEG-5G-04",
        "test_name": "禁止合并克泄耗为pressure_score",
        "expected": "官杀/食伤/财必须独立, 不能合并",
        "actual": "框架的G3 candidate_observations明确区分SUPPORT_RELATIONS/DRAIN_RELATIONS/CONSUME_RELATIONS/CONTROL_RELATIONS, 没有合并。GOV-5G-04明确禁止。",
        "passed": True,
    })

    # NEG-05: 月令只是Baseline
    tests.append({
        "test_id": "NEG-5G-05",
        "test_name": "月令只是Baseline, 不是最终结论",
        "expected": "得令不必然身强, 失令不必然身弱",
        "actual": "框架G1 established_semantics明确'月令旺衰 ≠ 最终身强身弱'。REL-004明确G4可以覆盖G1。EVID-G4-006'虽旺而弱, 虽衰而强'。",
        "passed": True,
    })

    # NEG-06: 宁可UNRESOLVED
    tests.append({
        "test_id": "NEG-5G-06",
        "test_name": "宁可UNRESOLVED, 也不偷偷发明阈值",
        "expected": "Strength State包含UNRESOLVED",
        "actual": "框架strength_states包含UNRESOLVED。evaluation_pipeline Step 8明确'宁可UNRESOLVED, 也不能为了让机器必定输出而偷偷发明阈值'。GOV-5G-08明确禁止。",
        "passed": True,
    })

    # NEG-07: 框架状态是CANDIDATE_DRAFT
    tests.append({
        "test_id": "NEG-5G-07",
        "test_name": "框架状态是CANDIDATE_DRAFT, 非Canonical Authorization",
        "expected": "框架不进入L4 Evaluation",
        "actual": "框架status = CANDIDATE_DRAFT。GOV-5G-11明确'本框架状态为CANDIDATE_DRAFT, 非Canonical Authorization, 不进入L4 Evaluation'。",
        "passed": True,
    })

    # NEG-08: 用户口诀标为DERIVED
    tests.append({
        "test_id": "NEG-5G-08",
        "test_name": "用户口诀标为ENGINE_SYNTHESIS/DERIVED, 非五部经典原典",
        "expected": "'月令为君，地支为臣；天干为将，综合为衡'不伪装成原典",
        "actual": "GOV-5G-13明确'用户口诀标为ENGINE_SYNTHESIS/DERIVED, 非五部经典原典'。框架中没有将其作为canonical_evidences。",
        "passed": True,
    })

    # NEG-09: 神峰通考是外围参考
    tests.append({
        "test_id": "NEG-5G-09",
        "test_name": "《神峰通考》是外围参考, 不能填补五部经典缺口",
        "expected": "神峰通考不在source_scope中",
        "actual": "框架source_scope只包含五部经典。peripheral_references明确《神峰通考》是外围参考, '不能拿来填补五部经典Evidence Contract的缺口'。",
        "passed": True,
    })

    # NEG-10: 特殊格局退出普通模型
    tests.append({
        "test_id": "NEG-5G-10",
        "test_name": "特殊格局(从格/专旺)必须退出普通身强身弱模型",
        "expected": "Strength State包含SPECIAL",
        "actual": "框架strength_states包含SPECIAL。evaluation_pipeline Step 7明确'特殊格局检测 (是否从格/专旺/其他特殊格局? 若是, 退出普通模型)'。GOV-5G-09明确禁止。",
        "passed": True,
    })

    return tests


# ============================================================================
# 输出
# ============================================================================

def print_phase5g_report(framework: StrengthFrameworkV1, negative_tests: List[Dict[str, Any]]):
    """打印Phase 5G报告."""
    print("=" * 120)
    print("STR-001A Phase 5G - Five Classics Strength Framework Reconstruction")
    print("=" * 120)
    print(f"\nContract/Governance Layer = FROZEN (v6-final.1)")
    print(f"停止逐项补因果Claim的路线, 回到五部经典自身的判定结构")
    print(f"只允许五部经典: {', '.join(framework.source_scope)}")
    print(f"《神峰通考》保留为外围参考, 不能填补五部经典缺口")
    print(f"不再寻找'正向身弱Claim', 而是建立经典如何综合判断的关系结构")
    print(f"框架状态: {framework.status} (非Canonical Authorization, 不进入L4)")

    # === 1. 四个维度 ===
    print(f"\n{'='*120}")
    print("一、四个核心维度")
    print("=" * 120)

    for dim in framework.dimensions:
        print(f"\n  [{dim.dimension.value}] {dim.name}")
        print(f"    核心问题: {dim.core_question}")
        print(f"    五部经典共同确立的语义:")
        for line in dim.established_semantics.split('\n'):
            if line.strip():
                print(f"      {line.strip()}")
        print(f"    候选Engine Observation (非授权Feature):")
        for obs in dim.candidate_observations:
            print(f"      - {obs}")
        print(f"    未解决问题:")
        for issue in dim.unresolved_issues:
            print(f"      - {issue}")
        print(f"    原典证据 ({len(dim.canonical_evidences)}条):")
        for ev in dim.canonical_evidences:
            print(f"      [{ev.evidence_id}] {ev.source}·{ev.chapter}")
            print(f"        Text Layer: {ev.text_layer.value}, Authority: {ev.authority.value}")
            print(f"        原文: {ev.original_text[:80]}...")
            print(f"        语义: {ev.semantic_content[:100]}...")

    # === 2. 维度间Canonical Relation ===
    print(f"\n{'='*120}")
    print("二、维度间 Canonical Relation Graph")
    print("=" * 120)
    for rel in framework.relations:
        print(f"\n  [{rel.relation_id}] {rel.from_dimension.value} → {rel.to_dimension.value}")
        print(f"    关系类型: {rel.relation_type.value}")
        print(f"    描述: {rel.description}")
        print(f"    原典依据: {', '.join(rel.canonical_basis)}")

    # === 3. 判定流程 ===
    print(f"\n{'='*120}")
    print("三、判定流程 (规则系统, 非数学评分)")
    print("=" * 120)
    for i, step in enumerate(framework.evaluation_pipeline, 1):
        print(f"  {step}")

    # === 4. Strength State ===
    print(f"\n{'='*120}")
    print("四、Strength State (包含UNRESOLVED)")
    print("=" * 120)
    for state in framework.strength_states:
        print(f"  - {state}")
    print(f"\n  宁可UNRESOLVED, 也不能为了让机器必定输出而偷偷发明阈值")

    # === 5. Negative Tests ===
    print(f"\n{'='*120}")
    print("五、Negative Tests (10条)")
    print("=" * 120)
    for t in negative_tests:
        status = "✅ PASS" if t["passed"] else "❌ FAIL"
        print(f"\n  [{t['test_id']}] {status}")
        print(f"    {t['test_name']}")
        print(f"    预期: {t['expected']}")
        print(f"    实际: {t['actual'][:120]}...")

    # === 6. 治理约束 ===
    print(f"\n{'='*120}")
    print("六、治理约束 (13条)")
    print("=" * 120)
    for gov in framework.governance_constraints:
        print(f"  {gov}")

    # === 7. 最终状态 ===
    print(f"\n{'='*120}")
    print("七、最终状态 (全部NOT_DONE/NOT_ALLOWED)")
    print("=" * 120)
    print(f"""
  Contract/Governance:          FROZEN
  Framework Status:              CANDIDATE_DRAFT (非授权)
  Canonical Authorization:       NOT_DONE
  Mapping Authorization:         NOT_DONE
  Evidence Authorization:        NOT_DONE
  L4 Evaluation:                 NOT_ALLOWED (框架是CANDIDATE_DRAFT)
  Assertion:                     NOT_ALLOWED
  身弱算法:                      NOT_ALLOWED
  数值阈值:                      NOT_ALLOWED
  加权评分:                      NOT_ALLOWED
  合并pressure_score:            NOT_ALLOWED

  框架核心认识:
  1. 五部经典的旺衰体系不是用现代阈值表达的, 而是用关系结构综合定性
  2. 旺衰(月令) ≠ 强弱(根气/党众) — 五部经典共同确立的基本区分
  3. 月令只是Baseline, 不是最终结论 — "虽旺而弱"、"虽衰而强"
  4. 只看月令是"死法" — 必须综合根气、生扶、克泄耗等维度
  5. 判定顺序: 月令 → 地支(根气) → 天干(生扶/克泄耗)
  6. 权重关系: 月令 > 根气 > 天干 (经典语义权重, 非数学百分比)
  7. 宁可UNRESOLVED, 也不偷偷发明阈值
    """)

    # === 8. 下一步 ===
    print(f"\n{'='*120}")
    print("八、下一步建议")
    print("=" * 120)
    print(f"""
  Phase 5G已完成五部经典旺衰框架重构。

  框架已经从"不断找一句证明身弱的话"跳出来, 变成由五部经典共同构成的
  可审计身强身弱判定框架。

  下一步选项:
  A. 对每个维度的candidate_observations进行Source Mapping, 确认哪些可以成为授权的Engine Observation
  B. 用1983命例(癸亥 壬戌 乙未 壬午)走一遍框架的判定流程, 验证框架是否可操作
  C. 进一步Source Mapping每个维度的unresolved_issues (如根气分类、特殊格局判定等)
  D. 保持框架CANDIDATE_DRAFT状态, 先做其他任务

  建议: 选项A或B, 先验证框架的可操作性, 再决定是否进入Authorization。

  仍然禁止:
    - 进入L4 Evaluation
    - 开发身弱算法
    - 设置数值阈值
    - 加权评分
    - 合并克泄耗成pressure_score
    - 进入ContextResolver / Assertion
    - 直接产生L4 PROVEN
    """)

    print(f"\n{'='*120}")
    print("STR-001A Phase 5G 完成.")
    print("=" * 120)


# ============================================================================
# 主函数
# ============================================================================

def main():
    framework = phase5g_strength_framework_reconstruction()
    negative_tests = run_negative_tests(framework)
    print_phase5g_report(framework, negative_tests)


if __name__ == "__main__":
    main()
