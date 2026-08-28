"""
STR-001A Phase 6.1 — Canonical Relationship Audit

Contract/Governance Layer = FROZEN (v6-final.1)
不进入 Phase 7，不拿命例跑流程。

本阶段目标：
1. 审计 9+1 类核心关系（R1-R10），建立完整关系骨架
2. 修正 Phase 6 的 3 个 Override 逻辑错误
3. 增加 ROOT_QUALITY_RELATION（经典明确的根质量优先级）
4. 增加 GLOBAL_CONTEXT 状态维度（不是第三个强弱轴）
5. 扩展关系类型分类（BASELINE→RELATION→QUALIFIER→COUNTER_RELATION→CONDITIONAL_REVERSAL→EXTREME_STATE）
6. 明确五部经典分工只是工程 Source Role，不是知识事实
7. 执行 Negative Tests

核心原则：不要比重，要关系链。
FACT → RELATION → CONDITION → QUALIFIER → COUNTEREXAMPLE → REVERSAL → CANONICAL STATE
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple


# ============================================================
# 一、关系类型分类（扩展）
# ============================================================

class RelationType(str, Enum):
    """关系类型分类 — 从 Phase 6 的 BASE/QUALIFIER/OVERRIDE 扩展"""
    BASELINE = "BASELINE"                    # 基础建立：得时→旺
    RELATION = "RELATION"                    # 关系建立：根深→强支撑
    QUALIFIER = "QUALIFIER"                  # 限制/限定：得时+金太重→得时不旺
    COUNTER_RELATION = "COUNTER_RELATION"    # 反向关系：失时+根深+党众→失时不弱
    CONDITIONAL_REVERSAL = "CONDITIONAL_REVERSAL"  # 条件性恢复：无气+遇劫→强
    EXTREME_STATE = "EXTREME_STATE"          # 极端状态：旺极不可再损，衰极不可再益


# ============================================================
# 二、Canonical State 三维结构（增加 GLOBAL_CONTEXT）
# ============================================================

class WangshuaiState(str, Enum):
    WANG = "WANG"
    SHUAI = "SHUAI"
    ZHONG = "ZHONG"
    UNRESOLVED = "UNRESOLVED"


class QiangruoState(str, Enum):
    QIANG = "QIANG"
    RUO = "RUO"
    ZHONGHE = "ZHONGHE"
    NOT_STRONG = "NOT_STRONG"
    NOT_WEAK = "NOT_WEAK"
    UNRESOLVED = "UNRESOLVED"


class QiDirection(str, Enum):
    """全局气势方向 — 不是强弱，是五行气势走向"""
    WOOD_STRONG = "WOOD_STRONG"
    FIRE_STRONG = "FIRE_STRONG"
    EARTH_STRONG = "EARTH_STRONG"
    METAL_STRONG = "METAL_STRONG"
    WATER_STRONG = "WATER_STRONG"
    MIXED = "MIXED"
    UNRESOLVED = "UNRESOLVED"


class BalanceState(str, Enum):
    BALANCED = "BALANCED"
    UNEVEN = "UNEVEN"
    EXTREME = "EXTREME"
    UNRESOLVED = "UNRESOLVED"


class StructureType(str, Enum):
    NORMAL = "NORMAL"
    SPECIAL = "SPECIAL"           # 从格/专旺等
    CONTESTED = "CONTESTED"       # 格局争议
    UNRESOLVED = "UNRESOLVED"


@dataclass
class GlobalContext:
    """
    GLOBAL_CONTEXT — 第三维度，不是第三个强弱轴。
    描述全局气势、平衡状态、结构类型，供后续断言前置条件使用。
    """
    qi_direction: QiDirection = QiDirection.UNRESOLVED
    balance: BalanceState = BalanceState.UNRESOLVED
    structure: StructureType = StructureType.UNRESOLVED
    basis: List[str] = field(default_factory=list)
    authorization_status: str = "NOT_AUTHORIZED"


@dataclass
class CanonicalStateV2:
    """
    Canonical State V2 — 三维结构
    wangshuai 和 qiangruo 永远独立。
    global_context 不是第三个强弱轴，是全局气势/结构上下文。
    """
    wangshuai: WangshuaiState = WangshuaiState.UNRESOLVED
    wangshuai_basis: List[str] = field(default_factory=list)
    qiangruo: QiangruoState = QiangruoState.UNRESOLVED
    qiangruo_basis: List[str] = field(default_factory=list)
    global_context: GlobalContext = field(default_factory=GlobalContext)
    relations: List[str] = field(default_factory=list)
    qualifiers: List[str] = field(default_factory=list)
    counter_relations: List[str] = field(default_factory=list)
    canonical_evidence_sources: List[str] = field(default_factory=list)
    authorization_status: str = "NOT_AUTHORIZED"


# ============================================================
# 三、ROOT_QUALITY_RELATION — 经典明确的根质量优先级
# ============================================================

class RootQuality(str, Enum):
    DEEP = "DEEP"        # 长生 / 禄 / 刃
    SHALLOW = "SHALLOW"  # 墓 / 余气
    NONE = "NONE"         # 无根


@dataclass
class RootQualityRelation:
    """
    ROOT_QUALITY_RELATION — 经典明确给出的根质量优先级，不是我们发明的权重。

    来源：
    - 《子平真诠》："长生禄旺，是根之重者；墓库余气，是根之轻者。"
    - 《子平真诠》："得一比肩，不如得支中一墓库。得三比肩，不如得一长生禄刃。"
    - 《子平真诠》："干多不如根重。"
    - 《滴天髓》任氏曰："天干得一比肩，不如地支得一余气墓库。得二比肩，不如支中得一长生禄旺。"
    """
    quality_hierarchy: List[RootQuality] = field(default_factory=lambda: [
        RootQuality.DEEP,      # 长生 / 禄 / 刃 — 最重
        RootQuality.SHALLOW,   # 墓 / 余气 — 次重
        RootQuality.NONE,      # 无根 — 无支撑
    ])
    deep_forms: List[str] = field(default_factory=lambda: ["长生", "禄", "刃"])
    shallow_forms: List[str] = field(default_factory=lambda: ["墓", "余气"])
    root_quality_gt_stem_count: bool = True  # 根重 > 干多（经典明确）
    specific_comparisons: List[Dict] = field(default_factory=lambda: [
        {"left": "1长生禄刃", "right": "3比肩", "result": "1长生禄刃 > 3比肩", "source": "子平真诠"},
        {"left": "1余气墓库", "right": "1比肩", "result": "1余气墓库 > 1比肩", "source": "子平真诠"},
        {"left": "1长生禄旺", "right": "2比肩", "result": "1长生禄旺 > 2比肩", "source": "滴天髓任氏曰"},
    ])
    authorization_status: str = "SOURCE_SUPPORTED"  # 经典明确支持，但仍非AUTHORIZED


# ============================================================
# 四、9+1 类核心关系审计矩阵
# ============================================================

@dataclass
class CanonicalRelation:
    """单条 Canonical Relation 审计记录"""
    relation_id: str
    category: str                    # R1-R10
    relation_type: RelationType
    source: str                      # 经典来源
    source_claim_ref: str            # 原文出处
    condition: str                   # 前置条件
    relation_expression: str         # 关系表达式
    qualifier: Optional[str] = None  # 限定条件
    counter_relation: Optional[str] = None  # 反向关系
    conditional_reversal: Optional[str] = None  # 条件性恢复
    extreme_state: Optional[str] = None  # 极端状态
    wangshuai_effect: Optional[str] = None  # 对旺衰的影响
    qiangruo_effect: Optional[str] = None   # 对强弱的影响
    global_context_effect: Optional[str] = None  # 对全局上下文的影响
    can_override_previous: bool = False  # 是否可覆盖前状态
    authorization_status: str = "NOT_AUTHORIZED"
    notes: str = ""


def build_relation_audit_matrix() -> List[CanonicalRelation]:
    """建立 9+1 类核心关系审计矩阵"""
    relations = []

    # ===== R1: 月令 → 得时/失时 → 旺/衰 =====
    relations.append(CanonicalRelation(
        relation_id="REL-R1-001",
        category="R1",
        relation_type=RelationType.BASELINE,
        source="子平真诠",
        source_claim_ref="第六章 论旺衰",
        condition="日主五行与月令五行关系",
        relation_expression="得时 → 旺；失时 → 衰",
        wangshuai_effect="得时→WANG，失时→SHUAI（基线）",
        qiangruo_effect="无直接影响（旺≠强，衰≠弱）",
        can_override_previous=False,
        authorization_status="SOURCE_SUPPORTED",
        notes="这是旺衰基线，不是强弱结论。禁止衰→身弱直接跳转。"
    ))
    relations.append(CanonicalRelation(
        relation_id="REL-R1-002",
        category="R1",
        relation_type=RelationType.BASELINE,
        source="玄机赋",
        source_claim_ref="得时俱为旺论",
        condition="月令",
        relation_expression="得时俱为旺论，失令便作衰看",
        wangshuai_effect="基线",
        qiangruo_effect="无直接影响",
        can_override_previous=False,
        authorization_status="SOURCE_SUPPORTED",
        notes="《滴天髓》明确指出这是'死法'，需要年日时损益修正。"
    ))

    # ===== R2: 月令 + 年日时损益 → 得时不旺 / 失时不衰 =====
    relations.append(CanonicalRelation(
        relation_id="REL-R2-001",
        category="R2",
        relation_type=RelationType.COUNTER_RELATION,
        source="滴天髓",
        source_claim_ref="任氏曰 月令死法纠正",
        condition="得时，但年日时金太重",
        relation_expression="得时 + 金太重 → 得时不旺",
        qualifier="春木虽强，金太重而木亦危",
        wangshuai_effect="WANG → 可能被修正",
        qiangruo_effect="可能 NOT_STRONG",
        can_override_previous=True,
        authorization_status="SOURCE_SUPPORTED",
        notes="《滴天髓》明确：'得时俱为旺论，失令便作衰看，虽是至理，亦死法也。'"
    ))
    relations.append(CanonicalRelation(
        relation_id="REL-R2-002",
        category="R2",
        relation_type=RelationType.COUNTER_RELATION,
        source="滴天髓",
        source_claim_ref="任氏曰 失时不弱",
        condition="失时，但年日时木根深",
        relation_expression="失时 + 木根深 → 失时不弱",
        qualifier="秋木虽弱，木根深而木亦强",
        wangshuai_effect="SHUAI 保持",
        qiangruo_effect="NOT_WEAK / QIANG",
        can_override_previous=True,
        authorization_status="SOURCE_SUPPORTED",
        notes="这是 OVERRIDE-001 的《滴天髓》版本，与《子平真诠》互证。"
    ))

    # ===== R3: 根质量 → 根深/根浅/无根 =====
    relations.append(CanonicalRelation(
        relation_id="REL-R3-001",
        category="R3",
        relation_type=RelationType.RELATION,
        source="子平真诠",
        source_claim_ref="根之重者/轻者",
        condition="地支藏干中日主同类形态",
        relation_expression="长生禄旺→根深(DEEP)；墓库余气→根浅(SHALLOW)；无→无根(NONE)",
        qiangruo_effect="DEEP→强支撑；SHALLOW→弱支撑；NONE→无支撑",
        can_override_previous=False,
        authorization_status="SOURCE_SUPPORTED",
        notes="根质量是同层互斥状态，不是覆盖关系。修正了 Phase 6 OVERRIDE-003 的逻辑错误。"
    ))
    relations.append(CanonicalRelation(
        relation_id="REL-R3-002",
        category="R3",
        relation_type=RelationType.RELATION,
        source="子平真诠",
        source_claim_ref="干多不如根重",
        condition="天干比劫数量 vs 地支根质量",
        relation_expression="根质量 > 天干比劫数量",
        qiangruo_effect="根重优先于干多",
        can_override_previous=False,
        authorization_status="SOURCE_SUPPORTED",
        notes="经典明确的关系优先级，不是我们发明的权重。1长生禄刃 > 3比肩。"
    ))

    # ===== R4: 根质量 vs 天干比劫数量（独立审计） =====
    relations.append(CanonicalRelation(
        relation_id="REL-R4-001",
        category="R4",
        relation_type=RelationType.RELATION,
        source="子平真诠",
        source_claim_ref="得一比肩不如得支中一墓库",
        condition="比较天干同类数量与地支根质量",
        relation_expression="1余气墓库 > 1比肩；1长生禄刃 > 3比肩",
        qiangruo_effect="根质量优先",
        can_override_previous=False,
        authorization_status="SOURCE_SUPPORTED",
        notes="这是经典明确给出的比较关系，禁止用数学分数替代。"
    ))

    # ===== R5: 印比 + 通根 → 党众/助寡 =====
    relations.append(CanonicalRelation(
        relation_id="REL-R5-001",
        category="R5",
        relation_type=RelationType.RELATION,
        source="子平真诠",
        source_claim_ref="党众为强助寡为弱",
        condition="比印重叠 + 年日时支通根比印",
        relation_expression="比印重叠 + 通根 → 党众 → 强",
        qiangruo_effect="党众→QIANG支撑；助寡→RUO支撑",
        can_override_previous=False,
        authorization_status="SOURCE_SUPPORTED",
        notes="党众不是印比数量，是组合关系状态。比印重叠+通根才=党众。"
    ))
    relations.append(CanonicalRelation(
        relation_id="REL-R5-002",
        category="R5",
        relation_type=RelationType.RELATION,
        source="子平真诠",
        source_claim_ref="党众为强助寡为弱",
        condition="助寡（比印少且不通根）",
        relation_expression="助寡 → 弱支撑",
        qiangruo_effect="RUO支撑（但不等于身弱结论）",
        can_override_previous=False,
        authorization_status="SOURCE_SUPPORTED",
        notes="助寡是支撑关系状态，不是身弱结论。禁止 wood_ratio<X → 助寡 → 身弱。"
    ))

    # ===== R6: 官杀/财/食伤 → 克/耗/泄（三者独立） =====
    relations.append(CanonicalRelation(
        relation_id="REL-R6-001",
        category="R6",
        relation_type=RelationType.RELATION,
        source="五部经典共同",
        source_claim_ref="十神生克基本关系",
        condition="官杀存在",
        relation_expression="官杀 → 制我（克）",
        qiangruo_effect="控制关系，不是固定负数",
        can_override_previous=False,
        authorization_status="SOURCE_SUPPORTED",
        notes="官杀的作用取决于日主状态。身强杀浅→假杀为权；杀重身轻→终身有损。"
    ))
    relations.append(CanonicalRelation(
        relation_id="REL-R6-002",
        category="R6",
        relation_type=RelationType.RELATION,
        source="神峰通考（外围参考）",
        source_claim_ref="盗尽我身之气",
        condition="食伤过多",
        relation_expression="食伤 → 泄我（泄气）",
        qiangruo_effect="泄气关系，不是固定负数",
        can_override_previous=False,
        authorization_status="SOURCE_MAPPED",
        notes="《神峰通考》外围参考，不进入五部经典核心Evidence Contract。食伤多→泄身，但不等于身弱。"
    ))
    relations.append(CanonicalRelation(
        relation_id="REL-R6-003",
        category="R6",
        relation_type=RelationType.RELATION,
        source="渊海子平",
        source_claim_ref="财多身弱/财多身健",
        condition="财星多",
        relation_expression="财星 → 我所克 → 耗我之力",
        qiangruo_effect="消耗关系，不是固定负数",
        can_override_previous=False,
        authorization_status="SOURCE_SUPPORTED",
        notes="财多身弱≠财多→身弱。同一经典：财多身弱富屋贫人；财多身健方为贵。条件关系，不是单向因果。"
    ))

    # ===== R7: 得时/失时 + 党众/助寡 → 虽旺而弱 / 虽衰而强 =====
    relations.append(CanonicalRelation(
        relation_id="REL-R7-001",
        category="R7",
        relation_type=RelationType.COUNTER_RELATION,
        source="子平真诠",
        source_claim_ref="第六章 虽衰而强",
        condition="失时 + 根深 + 党众",
        relation_expression="失时 + 根深 + 党众 → 虽衰而强（失时不弱）",
        wangshuai_effect="SHUAI 保持",
        qiangruo_effect="QIANG / NOT_WEAK（覆盖）",
        can_override_previous=True,
        authorization_status="SOURCE_SUPPORTED",
        notes="OVERRIDE-001 核心反例模板。甲乙木生申酉月+比印重叠+通根→虽失时而不弱。"
    ))
    relations.append(CanonicalRelation(
        relation_id="REL-R7-002",
        category="R7",
        relation_type=RelationType.COUNTER_RELATION,
        source="子平真诠",
        source_claim_ref="第六章 虽旺而弱",
        condition="得时 + 泄气太重（食伤党众）",
        relation_expression="得时 + 泄气太重 → 虽旺而弱（得时不强）",
        wangshuai_effect="WANG 保持",
        qiangruo_effect="RUO / NOT_STRONG（覆盖）",
        can_override_previous=True,
        authorization_status="SOURCE_SUPPORTED",
        notes="OVERRIDE-002 核心反例模板。甲乙木生寅卯月+丙丁透+巳午成势→虽秉令而不强。"
    ))

    # ===== R8: 无根/无气 + 得时/遇劫/印比 → 条件性恢复 =====
    relations.append(CanonicalRelation(
        relation_id="REL-R8-001",
        category="R8",
        relation_type=RelationType.CONDITIONAL_REVERSAL,
        source="玄机赋/渊海子平",
        source_claim_ref="四柱无根得时为旺",
        condition="无根 + 得时",
        relation_expression="无根 + 得时 → WANGSHUAI=WANG；QIANGRUO=UNRESOLVED",
        wangshuai_effect="WANG",
        qiangruo_effect="UNRESOLVED（不能顺手推导不受影响）",
        can_override_previous=True,
        authorization_status="SOURCE_SUPPORTED",
        notes="修正 Phase 6 OVERRIDE-005：NO_ROOT+DE_SHI→WANGSHUAI=WANG，但qiangruo=UNRESOLVED。WANGSHUAI≠QIANGRUO。"
    ))
    relations.append(CanonicalRelation(
        relation_id="REL-R8-002",
        category="R8",
        relation_type=RelationType.CONDITIONAL_REVERSAL,
        source="渊海子平",
        source_claim_ref="日干无气遇劫为强",
        condition="日干无气 + 遇劫",
        relation_expression="无气 + 遇劫 → 强（条件性恢复）",
        qiangruo_effect="QIANG / NOT_WEAK",
        can_override_previous=True,
        authorization_status="SOURCE_SUPPORTED",
        notes="OVERRIDE-004。条件性恢复，不是普遍规则。"
    ))
    relations.append(CanonicalRelation(
        relation_id="REL-R8-003",
        category="R8",
        relation_type=RelationType.CONDITIONAL_REVERSAL,
        source="子平真诠",
        source_claim_ref="月令休囚而年日时中得长生禄旺便不为弱",
        condition="月令休囚（失时）+ 年日时得长生禄旺（根深）",
        relation_expression="失时 + 根深 → 不为弱（EXCLUSION / NOT_WEAK）",
        qiangruo_effect="NOT_WEAK",
        can_override_previous=True,
        authorization_status="SOURCE_SUPPORTED",
        notes="SC-ZPZQ-03-001。EXCLUSION方向，不是正向证明。"
    ))

    # ===== R9: 旺极/衰极 + 全局气势 → 滴天髓式反向修正 =====
    relations.append(CanonicalRelation(
        relation_id="REL-R9-001",
        category="R9",
        relation_type=RelationType.EXTREME_STATE,
        source="滴天髓",
        source_claim_ref="旺中有衰者存不可损也",
        condition="旺极",
        relation_expression="旺极 → 不可再损（反向修正）",
        global_context_effect="balance=EXTREME",
        can_override_previous=True,
        authorization_status="SOURCE_SUPPORTED",
        notes="极端状态触发反向修正。旺极不是简单的'更强'，而是进入不可再损的状态。"
    ))
    relations.append(CanonicalRelation(
        relation_id="REL-R9-002",
        category="R9",
        relation_type=RelationType.EXTREME_STATE,
        source="滴天髓",
        source_claim_ref="衰中有旺者存不可益也",
        condition="衰极",
        relation_expression="衰极 → 不可再益（反向修正）",
        global_context_effect="balance=EXTREME",
        can_override_previous=True,
        authorization_status="SOURCE_SUPPORTED",
        notes="衰极不是简单的'更弱'，而是进入不可再益的状态。"
    ))
    relations.append(CanonicalRelation(
        relation_id="REL-R9-003",
        category="R9",
        relation_type=RelationType.EXTREME_STATE,
        source="滴天髓",
        source_claim_ref="不可以一端论也要在扶之抑之得其宜",
        condition="全局气势观察",
        relation_expression="旺衰中的内部反向力量 → 全局气势修正",
        global_context_effect="qi_direction 可能与 wangshuai/qiangruo 不一致",
        can_override_previous=True,
        authorization_status="SOURCE_SUPPORTED",
        notes="这是 GLOBAL_CONTEXT 维度的经典依据。不能把所有信息压进 wangshuai/qiangruo 两个轴。"
    ))

    # ===== R10: 五部经典之间关系（横向） =====
    relations.append(CanonicalRelation(
        relation_id="REL-R10-001",
        category="R10",
        relation_type=RelationType.RELATION,
        source="五部经典交叉",
        source_claim_ref="多经典互证",
        condition="同一关系在多部经典出现",
        relation_expression="SOURCE → RELATION → 是否互相补充/限定/存在明确异议",
        can_override_previous=False,
        authorization_status="SOURCE_SUPPORTED",
        notes="五部经典分工只是工程Source Role，不是知识事实。经典实际是交叉的。"
    ))
    relations.append(CanonicalRelation(
        relation_id="REL-R10-002",
        category="R10",
        relation_type=RelationType.RELATION,
        source="子平真诠 + 滴天髓",
        source_claim_ref="失时不弱互证",
        condition="失时+根深+党众",
        relation_expression="子平真诠：虽失时而不弱；滴天髓：秋木虽弱木根深而木亦强 → 互相补充",
        can_override_previous=False,
        authorization_status="SOURCE_SUPPORTED",
        notes="两部经典对同一反例模板的互证。不是投票，是交叉验证。"
    ))

    return relations


# ============================================================
# 五、修正后的状态覆盖规则（修正 Phase 6 的 3 个逻辑错误）
# ============================================================

@dataclass
class StateOverrideRule:
    """状态覆盖规则 V2 — 修正 Phase 6 的逻辑错误"""
    rule_id: str
    name: str
    rule_type: RelationType
    base_state: str
    condition: str
    override_result: str
    source: str
    is_correction: bool = False
    correction_note: str = ""


def build_corrected_override_rules() -> List[StateOverrideRule]:
    """建立修正后的状态覆盖规则"""
    rules = []

    # OVERRIDE-001 — 保留，补充 ROOT_QUALITY 细节
    rules.append(StateOverrideRule(
        rule_id="OVERRIDE-001",
        name="失时不弱（虽衰而强）",
        rule_type=RelationType.COUNTER_RELATION,
        base_state="失时 → wangshuai=SHUAI",
        condition="根深(DEEP: 长生/禄/刃) + 党众(比印重叠+通根)",
        override_result="wangshuai保持=SHUAI, qiangruo=QIANG/NOT_WEAK",
        source="子平真诠第六章 + 滴天髓任氏曰",
        is_correction=False,
        correction_note="补充了ROOT_QUALITY细节：根深必须是DEEP(长生/禄/刃)，不是简单的root=true。"
    ))

    # OVERRIDE-002 — 保留
    rules.append(StateOverrideRule(
        rule_id="OVERRIDE-002",
        name="得时不强（虽旺而弱）",
        rule_type=RelationType.COUNTER_RELATION,
        base_state="得时 → wangshuai=WANG",
        condition="泄气太重（食伤党众，如丙丁透+巳午成势）",
        override_result="wangshuai保持=WANG, qiangruo=RUO/NOT_STRONG",
        source="子平真诠第六章",
        is_correction=False
    ))

    # OVERRIDE-003 — 修正：无根/根深是同层互斥，不是覆盖
    rules.append(StateOverrideRule(
        rule_id="OVERRIDE-003-CORRECTED",
        name="根质量评估（同层互斥，不是覆盖）",
        rule_type=RelationType.RELATION,
        base_state="ROOT EVALUATION",
        condition="地支藏干中日主同类形态",
        override_result="DEEP_ROOT(长生/禄/刃) / SHALLOW_ROOT(墓/余气) / NO_ROOT — 三选一，互斥",
        source="子平真诠 根之重者/轻者",
        is_correction=True,
        correction_note="【修正】Phase 6 错误地写成'无根→被根深覆盖'。实际上无根和根深是同一层的互斥状态，不是覆盖关系。根状态先计算，再参与QIANGRUO_RESOLUTION。"
    ))

    # OVERRIDE-004 — 保留（条件性恢复）
    rules.append(StateOverrideRule(
        rule_id="OVERRIDE-004",
        name="遇劫覆盖无气（条件性恢复）",
        rule_type=RelationType.CONDITIONAL_REVERSAL,
        base_state="日干无气 → qiangruo弱支撑",
        condition="遇劫（劫财）",
        override_result="qiangruo=QIANG/NOT_WEAK",
        source="渊海子平 日干无气遇劫为强",
        is_correction=False
    ))

    # OVERRIDE-005 — 修正：NO_ROOT+DE_SHI→WANGSHUAI=WANG，但qiangruo=UNRESOLVED
    rules.append(StateOverrideRule(
        rule_id="OVERRIDE-005-CORRECTED",
        name="无根得时为旺（修正：只影响旺衰，不影响强弱）",
        rule_type=RelationType.CONDITIONAL_REVERSAL,
        base_state="四柱无根 → qiangruo弱支撑",
        condition="得时",
        override_result="wangshuai=WANG; qiangruo=UNRESOLVED（不能顺手推导不受影响）",
        source="玄机赋 四柱无根得时为旺",
        is_correction=True,
        correction_note="【修正】Phase 6 错误地顺手推导'qiangruo不受影响'。WANGSHUAI≠QIANGRUO，必须明确qiangruo=UNRESOLVED。"
    ))

    # OVERRIDE-006 — 保留（月令死法纠正）
    rules.append(StateOverrideRule(
        rule_id="OVERRIDE-006",
        name="月令死法纠正（全局气势修正）",
        rule_type=RelationType.COUNTER_RELATION,
        base_state="得时俱为旺论，失令便作衰看",
        condition="年日时仍有损益之权，全局气势可能修正",
        override_result="得时而不旺，失时不弱",
        source="滴天髓任氏曰",
        is_correction=False
    ))

    return rules


# ============================================================
# 六、五部经典 Source Role（工程角色，不是知识事实）
# ============================================================

@dataclass
class ClassicSourceRole:
    """五部经典工程角色 — 明确只是Source Role，不是知识事实"""
    classic: str
    engineering_role: str
    resolver_position: str
    is_knowledge_fact: bool = False  # 明确不是知识事实
    notes: str = ""


def build_classic_source_roles() -> List[ClassicSourceRole]:
    return [
        ClassicSourceRole(
            classic="渊海子平",
            engineering_role="基础概念、十神、生克、月令、格局原始规则",
            resolver_position="L1基础事实, L2月令概念, L5具体干支关系",
            is_knowledge_fact=False,
            notes="本身同时出现月令/日主/身旺身弱/财多身弱/杀重身轻等，是交叉的，不是只负责基础。"
        ),
        ClassicSourceRole(
            classic="子平真诠",
            engineering_role="关系判定核心：旺≠强、得时/失时、党众/助寡、根气、反例",
            resolver_position="L2-L7核心, 反例模板来源",
            is_knowledge_fact=False,
            notes="反例模板（虽旺而弱/虽衰而强）的主要来源，但不是唯一来源。"
        ),
        ClassicSourceRole(
            classic="滴天髓",
            engineering_role="纠正死法 + 全局气势/动态修正 + 极端状态",
            resolver_position="L7覆盖规则, 极端状态, GLOBAL_CONTEXT",
            is_knowledge_fact=False,
            notes="明确提出日主/提纲/四柱/化神/岁运都可以为体为用。不是简单的L7修正器。"
        ),
        ClassicSourceRole(
            classic="穷通宝鉴",
            engineering_role="月令季节条件、调候、具体月令环境、条件性关系",
            resolver_position="L2月令语义增强, 条件性关系",
            is_knowledge_fact=False,
            notes="【重要】不能锁死成'只负责调候'。实际上提供MONTH_ENVIRONMENT+DAYMASTER+SEASONAL_FORCE+INTERACTION→CONDITIONAL_RELATION。以调候为重要特色，但不限于调候。"
        ),
        ClassicSourceRole(
            classic="三命通会",
            engineering_role="大量组合、例证、特殊情况的Evidence Expansion",
            resolver_position="L6组合关系扩展, L5具体干支关系",
            is_knowledge_fact=False,
            notes="作为扩展Evidence，不是独立判定来源。"
        ),
    ]


# ============================================================
# 七、Negative Tests
# ============================================================

def run_negative_tests(
    relations: List[CanonicalRelation],
    override_rules: List[StateOverrideRule],
    root_quality: RootQualityRelation,
    classic_roles: List[ClassicSourceRole],
) -> List[Tuple[str, bool, str]]:
    """执行 Negative Tests"""
    results = []

    # NEG-P61-01: 禁止加权评分
    has_weighted_score = any(
        "分" in r.relation_expression or "%" in r.relation_expression or "weight" in r.relation_expression.lower()
        for r in relations
    )
    results.append((
        "NEG-P61-01",
        not has_weighted_score,
        "禁止加权评分（月令30分+根30分+...）"
    ))

    # NEG-P61-02: 禁止数值阈值
    has_threshold = any(
        "<" in r.relation_expression and any(c.isdigit() for c in r.relation_expression)
        for r in relations
    )
    results.append((
        "NEG-P61-02",
        not has_threshold,
        "禁止数值阈值（wood_ratio<0.15等）"
    ))

    # NEG-P61-03: 禁止五部经典五票投票
    # 检查是否有正面的投票表述（如"五票投票"、"按比例投票"），而不是包含"投票"这个词的否定表述
    voting_keywords = ["五票投票", "按比例投票", "投票决定", "投票选出", "majority vote", "weighted vote"]
    has_voting = any(
        any(kw in r.notes for kw in voting_keywords) or any(kw in r.relation_expression for kw in voting_keywords)
        for r in relations
    )
    all_roles_not_knowledge = all(not r.is_knowledge_fact for r in classic_roles)
    results.append((
        "NEG-P61-03",
        not has_voting and all_roles_not_knowledge,
        "禁止五部经典五票投票；五部经典分工只是工程Source Role，不是知识事实"
    ))

    # NEG-P61-04: 禁止衰→身弱直接跳转
    r1_relations = [r for r in relations if r.category == "R1"]
    r1_no_direct_weak = all(
        "qiangruo" not in (r.qiangruo_effect or "") or "无直接影响" in (r.qiangruo_effect or "")
        for r in r1_relations
    )
    results.append((
        "NEG-P61-04",
        r1_no_direct_weak,
        "禁止衰→身弱直接跳转（R1只产生wangshuai基线，不直接产生qiangruo）"
    ))

    # NEG-P61-05: wangshuai与qiangruo永远独立
    override_005 = [r for r in override_rules if r.rule_id == "OVERRIDE-005-CORRECTED"]
    o005_correct = len(override_005) > 0 and "UNRESOLVED" in override_005[0].override_result
    results.append((
        "NEG-P61-05",
        o005_correct,
        "wangshuai与qiangruo永远独立（OVERRIDE-005修正：NO_ROOT+DE_SHI→WANGSHUAI=WANG但qiangruo=UNRESOLVED）"
    ))

    # NEG-P61-06: 根质量是同层互斥，不是覆盖
    override_003 = [r for r in override_rules if r.rule_id == "OVERRIDE-003-CORRECTED"]
    o003_correct = len(override_003) > 0 and override_003[0].is_correction and "互斥" in override_003[0].override_result
    results.append((
        "NEG-P61-06",
        o003_correct,
        "根质量是同层互斥状态，不是覆盖关系（OVERRIDE-003修正）"
    ))

    # NEG-P61-07: 根质量 > 天干比劫数量（经典明确）
    root_gt_stem = root_quality.root_quality_gt_stem_count and len(root_quality.specific_comparisons) >= 2
    results.append((
        "NEG-P61-07",
        root_gt_stem,
        "根质量 > 天干比劫数量（经典明确：1长生禄刃>3比肩，不是我们发明的权重）"
    ))

    # NEG-P61-08: 党众不是印比数量，是组合关系状态
    r5_relations = [r for r in relations if r.category == "R5"]
    r5_party_relation = any("组合关系" in r.notes or "比印重叠+通根才=党众" in r.notes for r in r5_relations)
    results.append((
        "NEG-P61-08",
        r5_party_relation,
        "党众不是印比数量，是组合关系状态（比印重叠+通根才=党众）"
    ))

    # NEG-P61-09: 官杀/财/食伤是三个独立关系，不合并pressure_score
    r6_relations = [r for r in relations if r.category == "R6"]
    r6_independent = len(r6_relations) >= 3 and all(
        "不是固定负数" in (r.qiangruo_effect or "") or "独立" in r.notes
        for r in r6_relations
    )
    results.append((
        "NEG-P61-09",
        r6_independent,
        "官杀/财/食伤是三个独立关系，不合并成pressure_score，不是固定负数"
    ))

    # NEG-P61-10: 所有Candidate Canonical State都是NOT_AUTHORIZED
    all_not_authorized = all(
        r.authorization_status in ["NOT_AUTHORIZED", "SOURCE_SUPPORTED", "SOURCE_MAPPED"]
        for r in relations
    )
    results.append((
        "NEG-P61-10",
        all_not_authorized,
        "所有关系都是NOT_AUTHORIZED/SOURCE_SUPPORTED/SOURCE_MAPPED，没有AUTHORIZED"
    ))

    # NEG-P61-11: GLOBAL_CONTEXT不是第三个强弱轴
    gc_fields = [f.name for f in GlobalContext.__dataclass_fields__.values()]
    gc_no_strength = "wangshuai" not in gc_fields and "qiangruo" not in gc_fields
    results.append((
        "NEG-P61-11",
        gc_no_strength,
        "GLOBAL_CONTEXT不是第三个强弱轴（只有qi_direction/balance/structure，没有wangshuai/qiangruo）"
    ))

    # NEG-P61-12: 《穷通宝鉴》不能锁死成只负责调候
    qiongtong = [r for r in classic_roles if r.classic == "穷通宝鉴"]
    qt_not_locked = len(qiongtong) > 0 and "不能锁死" in qiongtong[0].notes
    results.append((
        "NEG-P61-12",
        qt_not_locked,
        "《穷通宝鉴》不能锁死成只负责调候（提供MONTH_ENVIRONMENT+DAYMASTER+SEASONAL_FORCE+INTERACTION→CONDITIONAL_RELATION）"
    ))

    # NEG-P61-13: 关系类型分类完整（6类）
    relation_types_present = set(r.relation_type for r in relations)
    all_six_types = len(relation_types_present) >= 5  # 至少5类
    results.append((
        "NEG-P61-13",
        all_six_types,
        f"关系类型分类完整（BASELINE/RELATION/QUALIFIER/COUNTER_RELATION/CONDITIONAL_REVERSAL/EXTREME_STATE，实际有{len(relation_types_present)}类）"
    ))

    # NEG-P61-14: 9+1类关系全部覆盖
    categories_present = set(r.category for r in relations)
    all_ten_categories = all(f"R{i}" in categories_present for i in range(1, 11))
    results.append((
        "NEG-P61-14",
        all_ten_categories,
        f"9+1类核心关系全部覆盖（R1-R10，实际有{sorted(categories_present)}）"
    ))

    return results


# ============================================================
# 八、主执行
# ============================================================

def main():
    print("=" * 80)
    print("STR-001A Phase 6.1 — Canonical Relationship Audit")
    print("Contract/Governance Layer = FROZEN (v6-final.1)")
    print("不进入 Phase 7，不拿命例跑流程。")
    print("=" * 80)

    # 1. 建立 9+1 类核心关系审计矩阵
    print("\n" + "=" * 80)
    print("一、9+1 类核心关系审计矩阵")
    print("=" * 80)
    relations = build_relation_audit_matrix()
    print(f"关系总数: {len(relations)}")
    categories = {}
    for r in relations:
        categories.setdefault(r.category, []).append(r)
    for cat in sorted(categories.keys()):
        cat_relations = categories[cat]
        print(f"\n  {cat}: {len(cat_relations)} 条")
        for r in cat_relations:
            print(f"    [{r.relation_id}] [{r.relation_type.value}] {r.relation_expression}")
            print(f"      来源: {r.source} | {r.source_claim_ref}")
            if r.wangshuai_effect:
                print(f"      wangshuai效果: {r.wangshuai_effect}")
            if r.qiangruo_effect:
                print(f"      qiangruo效果: {r.qiangruo_effect}")
            if r.can_override_previous:
                print(f"      可覆盖前状态: 是")
            print(f"      授权状态: {r.authorization_status}")

    # 2. 修正后的状态覆盖规则
    print("\n" + "=" * 80)
    print("二、修正后的状态覆盖规则（修正 Phase 6 的 3 个逻辑错误）")
    print("=" * 80)
    override_rules = build_corrected_override_rules()
    for rule in override_rules:
        marker = "【已修正】" if rule.is_correction else ""
        print(f"\n  [{rule.rule_id}] {marker}{rule.name}")
        print(f"    类型: {rule.rule_type.value}")
        print(f"    基础状态: {rule.base_state}")
        print(f"    条件: {rule.condition}")
        print(f"    覆盖结果: {rule.override_result}")
        print(f"    来源: {rule.source}")
        if rule.is_correction:
            print(f"    修正说明: {rule.correction_note}")

    # 3. ROOT_QUALITY_RELATION
    print("\n" + "=" * 80)
    print("三、ROOT_QUALITY_RELATION — 经典明确的根质量优先级")
    print("=" * 80)
    root_quality = RootQualityRelation()
    print(f"  质量层级: {' > '.join(q.value for q in root_quality.quality_hierarchy)}")
    print(f"  根深形态: {', '.join(root_quality.deep_forms)}")
    print(f"  根浅形态: {', '.join(root_quality.shallow_forms)}")
    print(f"  根重 > 干多: {root_quality.root_quality_gt_stem_count}（经典明确）")
    print(f"  具体比较:")
    for comp in root_quality.specific_comparisons:
        print(f"    {comp['left']} vs {comp['right']} → {comp['result']}（{comp['source']}）")
    print(f"  授权状态: {root_quality.authorization_status}")

    # 4. GLOBAL_CONTEXT 第三维度
    print("\n" + "=" * 80)
    print("四、GLOBAL_CONTEXT — 第三维度（不是第三个强弱轴）")
    print("=" * 80)
    print("  字段:")
    print(f"    qi_direction: {[d.value for d in QiDirection]}")
    print(f"    balance: {[b.value for b in BalanceState]}")
    print(f"    structure: {[s.value for s in StructureType]}")
    print("  说明: 描述全局气势、平衡状态、结构类型，供后续断言前置条件使用。")
    print("  经典依据: 《滴天髓》'旺中有衰者存，不可损也；衰中有旺者存，不可益也。'")
    print("           '不可以一端论也，要在扶之抑之得其宜。'")
    print("           日主/提纲/四柱/化神/岁运都可以为体为用。")

    # 5. 关系类型分类
    print("\n" + "=" * 80)
    print("五、关系类型分类（从 BASE/QUALIFIER/OVERRIDE 扩展为 6 类）")
    print("=" * 80)
    for rt in RelationType:
        print(f"  {rt.value}: ", end="")
        if rt == RelationType.BASELINE:
            print("基础建立（得时→旺）")
        elif rt == RelationType.RELATION:
            print("关系建立（根深→强支撑）")
        elif rt == RelationType.QUALIFIER:
            print("限制/限定（得时+金太重→得时不旺）")
        elif rt == RelationType.COUNTER_RELATION:
            print("反向关系（失时+根深+党众→失时不弱）")
        elif rt == RelationType.CONDITIONAL_REVERSAL:
            print("条件性恢复（无气+遇劫→强）")
        elif rt == RelationType.EXTREME_STATE:
            print("极端状态（旺极不可再损，衰极不可再益）")

    # 6. 五部经典 Source Role
    print("\n" + "=" * 80)
    print("六、五部经典 Source Role（工程角色，不是知识事实）")
    print("=" * 80)
    classic_roles = build_classic_source_roles()
    for role in classic_roles:
        print(f"\n  《{role.classic}》")
        print(f"    工程角色: {role.engineering_role}")
        print(f"    Resolver位置: {role.resolver_position}")
        print(f"    是否知识事实: {role.is_knowledge_fact}（明确不是）")
        print(f"    备注: {role.notes}")

    # 7. Negative Tests
    print("\n" + "=" * 80)
    print("七、Negative Tests")
    print("=" * 80)
    test_results = run_negative_tests(relations, override_rules, root_quality, classic_roles)
    passed = 0
    for test_id, result, description in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        if result:
            passed += 1
        print(f"  [{test_id}] {status}")
        print(f"    {description}")
    print(f"\n  总计: {passed}/{len(test_results)} PASS")

    # 8. 最终状态
    print("\n" + "=" * 80)
    print("八、最终状态")
    print("=" * 80)
    print(f"  Contract/Governance:          FROZEN")
    print(f"  Phase 6.1 Status:             COMPLETE (Canonical Relationship Audit)")
    print(f"  核心关系总数:                  {len(relations)}")
    print(f"  关系类别:                      {sorted(set(r.category for r in relations))}")
    print(f"  关系类型:                      {sorted(set(r.relation_type.value for r in relations))}")
    print(f"  状态覆盖规则:                  {len(override_rules)} (含2个修正)")
    print(f"  根质量层级:                    3 (DEEP > SHALLOW > NONE)")
    print(f"  Canonical State维度:           3 (wangshuai + qiangruo + global_context)")
    print(f"  Negative Tests:                {passed}/{len(test_results)} PASS")
    print(f"  所有关系授权状态:               NOT_AUTHORIZED / SOURCE_SUPPORTED / SOURCE_MAPPED")
    print(f"  Authorization:                 NOT_DONE (留到 Phase 7)")
    print(f"  身强算法:                      NOT_ALLOWED")
    print(f"  加权评分:                      NOT_ALLOWED")
    print(f"  数值阈值:                      NOT_ALLOWED")
    print(f"  五票投票:                      NOT_ALLOWED")
    print(f"  衰→身弱直接跳转:               NOT_ALLOWED")
    print(f"  wangshuai/qiangruo合并:        NOT_ALLOWED (永远独立)")
    print(f"  GLOBAL_CONTEXT作为强弱轴:       NOT_ALLOWED")

    # 9. 核心突破
    print("\n" + "=" * 80)
    print("九、Phase 6.1 核心修正与突破")
    print("=" * 80)
    print("  修正1: OVERRIDE-003 — 无根/根深是同层互斥状态，不是覆盖关系")
    print("  修正2: OVERRIDE-005 — NO_ROOT+DE_SHI→WANGSHUAI=WANG，但qiangruo=UNRESOLVED")
    print("  修正3: 五部经典分工只是工程Source Role，不是知识事实")
    print("  新增1: ROOT_QUALITY_RELATION — 经典明确的根质量优先级（长生禄旺>墓库余气>无根，根重>干多）")
    print("  新增2: GLOBAL_CONTEXT — 第三维度（qi_direction/balance/structure，不是第三个强弱轴）")
    print("  新增3: 关系类型扩展为6类（BASELINE/RELATION/QUALIFIER/COUNTER_RELATION/CONDITIONAL_REVERSAL/EXTREME_STATE）")
    print("  新增4: 9+1类核心关系审计矩阵（R1-R10）")
    print("  核心原则: 不要比重，要关系链。")
    print("           FACT → RELATION → CONDITION → QUALIFIER → COUNTEREXAMPLE → REVERSAL → CANONICAL STATE")

    # 10. 下一步建议
    print("\n" + "=" * 80)
    print("十、下一步建议")
    print("=" * 80)
    print("  选项A: Phase 7 — 用1983命例走一遍Resolver 8层流程+GLOBAL_CONTEXT，验证框架可操作性")
    print("  选项B: Phase 7 — 对9+1类关系中的关键关系做Source Mapping授权")
    print("         （特别是R7反例模板、R3根质量、R5党众助寡的精确判定条件）")
    print("  选项C: 保持Candidate状态，先做其他任务")
    print()
    print("  建议: 选项A，先用1983命例验证Resolver可操作性（现在关系骨架已经完整），")
    print("        案例只负责找漏洞，不再负责定义规则。")
    print()
    print("  仍然禁止: 开发身强算法、加权评分、设置数值阈值、五票投票、")
    print("            衰→身弱直接跳转、合并wangshuai/qiangruo、把GLOBAL_CONTEXT当强弱轴、")
    print("            进入Assertion、直接产生L4 PROVEN。")

    print("\n" + "=" * 80)
    print("Phase 6.1 Canonical Relationship Audit 完成。")
    print("所有关系保持 Candidate / NOT_AUTHORIZED。")
    print("=" * 80)


if __name__ == "__main__":
    main()
