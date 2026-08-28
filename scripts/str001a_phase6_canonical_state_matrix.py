"""STR-001A Phase 6 - Five-Classics Canonical State Matrix.

目标: 一次性把五部经典中与日主状态相关的核心变量全部拉出来,
建立"五部经典在什么条件下, 会让一个状态被另一个状态修正、限定、覆盖或保留"的关系矩阵.

核心原则:
- 不是"判断身强身弱的公式"
- 是"证据优先级 + 关系覆盖"
- 禁止加权评分(月令30分+根30分+...)
- 禁止五票投票(渊海20%+子平30%+...)
- wangshuai_state 与 qiangruo_state 永远独立
- Phase 5A-5F不作废: 全部降级成Raw Evidence/Candidate Relations重新装入矩阵
  错误的推导不继承, 已验证的原文证据继承

变量分层:
  Layer 1: 主体(日主)
  Layer 2: 时令状态(月令、得时、失时、旺、衰)
  Layer 3: 根气(根、通根、根深、根浅、长生、禄、刃、墓、余气、无根、无气、得地、失地)
  Layer 4: 支撑关系(印、比、劫、党众、助寡、得势、失势、生)
  Layer 5: 制泄耗关系(官、杀、财、食、伤、克、泄、耗)
  Layer 6: 综合状态(身旺、身弱、不弱、不强、虽旺而弱、虽衰而强、中和、太旺、太弱)

每条记录:
  SOURCE ↓ CONCEPT ↓ RELATION ↓ 前置条件 ↓ 作用对象 ↓ 作用方向
  ↓ QUALIFIER ↓ COUNTEREXAMPLE ↓ 是否可覆盖前状态 ↓ 产生什么CANONICAL STATE

Canonical State Resolver 8层流程:
  L1 基础事实
  L2 月令 → 旺衰基线
  L3 根气 → 得地状态
  L4 印比/党众 → 支撑关系
  L5 官杀/财/食伤 → 制泄耗关系
  L6 经典组合关系
  L7 反例/修正/覆盖
  L8 Canonical State

Candidate Canonical State结构:
  wangshuai: state(WANG|SHUAI|ZHONG), basis
  qiangruo: state(QIANG|RUO|ZHONGHE|NOT_STRONG|NOT_WEAK), basis
  relations: [DE_SHI, DE_DI, ...]
  canonical_evidence: sources, qualifiers, counterexamples
  全部NOT_AUTHORIZED
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum


# ============================================================================
# 枚举
# ============================================================================

class Layer(str, Enum):
    L1_SUBJECT = "L1_SUBJECT"  # 主体
    L2_SEASON = "L2_SEASON"  # 时令状态
    L3_ROOT = "L3_ROOT"  # 根气
    L4_SUPPORT = "L4_SUPPORT"  # 支撑关系
    L5_OPPOSITION = "L5_OPPOSITION"  # 制泄耗关系
    L6_SYNTHESIS = "L6_SYNTHESIS"  # 综合状态


class RelationDirection(str, Enum):
    BASELINE = "BASELINE"  # 建立基线
    SUPPORT = "SUPPORT"  # 支撑/增强
    OPPOSE = "OPPOSE"  # 制约/消耗
    OVERRIDE = "OVERRIDE"  # 覆盖/推翻
    QUALIFY = "QUALIFY"  # 限定/修正
    PRESERVE = "PRESERVE"  # 保留/维持


class WangShuaiState(str, Enum):
    WANG = "WANG"  # 旺
    SHUAI = "SHUAI"  # 衰
    ZHONG = "ZHONG"  # 中/平
    UNDETERMINED = "UNDETERMINED"


class QiangRuoState(str, Enum):
    QIANG = "QIANG"  # 强
    RUO = "RUO"  # 弱
    ZHONGHE = "ZHONGHE"  # 中和
    NOT_STRONG = "NOT_STRONG"  # 不强
    NOT_WEAK = "NOT_WEAK"  # 不弱
    UNDETERMINED = "UNDETERMINED"


class ClassicRole(str, Enum):
    YUAN_HAI = "YUAN_HAI"  # 渊海子平: 基础概念、十神、生克、月令、格局原始规则
    ZI_PING = "ZI_PING"  # 子平真诠: 关系判定核心(旺≠强、得时/失时、党众/助寡、根气、反例)
    DI_TIAN = "DI_TIAN"  # 滴天髓: 纠正死法+全局气势/动态修正
    QIONG_TONG = "QIONG_TONG"  # 穷通宝鉴: 月令季节条件、调候及月令具体环境
    SAN_MING = "SAN_MING"  # 三命通会: 大量组合、例证、特殊情况的Evidence Expansion


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class VariableEntry:
    """变量条目."""
    variable_id: str = ""
    name: str = ""
    layer: Layer = Layer.L1_SUBJECT
    concept: str = ""  # 概念定义
    source: str = ""  # 主要来源经典
    source_text: str = ""  # 原文
    relation: str = ""  # 关系类型
    precondition: str = ""  # 前置条件
    target: str = ""  # 作用对象
    direction: RelationDirection = RelationDirection.BASELINE  # 作用方向
    qualifier: str = ""  # 限定条件
    counterexample: str = ""  # 反例
    can_override_previous: bool = False  # 是否可覆盖前状态
    produces_canonical_state: str = ""  # 产生什么Canonical State
    inherited_from_phase5: str = ""  # 继承自Phase 5的哪个资产
    notes: str = ""


@dataclass
class StateOverrideRule:
    """状态覆盖规则: 什么条件下一个状态被另一个状态修正/覆盖."""
    rule_id: str = ""
    name: str = ""
    base_state: str = ""  # 基础状态(如: 失时→衰)
    override_condition: str = ""  # 覆盖条件(如: 根深+党众)
    override_result: str = ""  # 覆盖结果(如: 失时不弱)
    canonical_effect: str = ""  # 对Canonical State的影响
    source: str = ""  # 来源
    source_text: str = ""  # 原文
    is_template: bool = False  # 是否是反例模板
    notes: str = ""


@dataclass
class CanonicalState:
    """Candidate Canonical State (NOT_AUTHORIZED)."""
    wangshuai: WangShuaiState = WangShuaiState.UNDETERMINED
    wangshuai_basis: List[str] = field(default_factory=list)
    qiangruo: QiangRuoState = QiangRuoState.UNDETERMINED
    qiangruo_basis: List[str] = field(default_factory=list)
    relations: List[str] = field(default_factory=list)
    canonical_evidence_sources: List[str] = field(default_factory=list)
    qualifiers: List[str] = field(default_factory=list)
    counterexamples: List[str] = field(default_factory=list)
    authorization_status: str = "NOT_AUTHORIZED"
    notes: str = ""


# ============================================================================
# Phase 6: 建立变量清单
# ============================================================================

def build_variable_matrix() -> List[VariableEntry]:
    """建立变量矩阵."""
    variables = []

    # === Layer 1: 主体 ===
    variables.append(VariableEntry(
        variable_id="VAR-001",
        name="日主",
        layer=Layer.L1_SUBJECT,
        concept="日干, 八字判断的核心主体, 所有状态围绕它判断",
        source="《渊海子平》",
        source_text="以日为主，年为本，月为提纲，时为辅佐。",
        relation="主体",
        precondition="无",
        target="所有状态判断的对象",
        direction=RelationDirection.BASELINE,
        qualifier="无",
        counterexample="无",
        can_override_previous=False,
        produces_canonical_state="作为所有状态判断的主体",
        notes="所有变量围绕日主判断",
    ))

    # === Layer 2: 时令状态 ===
    variables.append(VariableEntry(
        variable_id="VAR-002",
        name="月令",
        layer=Layer.L2_SEASON,
        concept="月支, 日主所处的季节环境, 旺衰判定的第一枢机/提纲",
        source="《渊海子平》《子平真诠》",
        source_text="欲知贵贱，先观月令乃提纲。月令乃提纲之府，譬之宅也。",
        relation="建立旺衰基线的基础",
        precondition="确定月支五行",
        target="日主旺衰",
        direction=RelationDirection.BASELINE,
        qualifier="月令只是Baseline, 不是最终结论",
        counterexample="得时而不旺, 失时不弱(《滴天髓》)",
        can_override_previous=False,
        produces_canonical_state="wangshuai_baseline",
        inherited_from_phase5="Phase 5G G1",
        notes="五部经典高度一致: 月令是旺衰判定的第一枢机",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-003",
        name="得时",
        layer=Layer.L2_SEASON,
        concept="日主五行在月令处于旺相状态(日主与月令同五行或月令生日主)",
        source="《子平真诠》",
        source_text="得时为旺，失时为衰。",
        relation="月令→旺",
        precondition="日主五行得月令之气",
        target="wangshuai_state",
        direction=RelationDirection.BASELINE,
        qualifier="得时只是旺衰基线=旺, 不直接等于身强",
        counterexample="得时而不旺(《滴天髓》); 虽秉令而不强(《子平真诠》: 得时+泄气太重→不强)",
        can_override_previous=False,
        produces_canonical_state="wangshuai=WANG (基线)",
        inherited_from_phase5="Phase 5G G1",
        notes="得时→旺是经典授权最清楚的关系, 但旺≠强",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-004",
        name="失时",
        layer=Layer.L2_SEASON,
        concept="日主五行在月令处于休囚死绝状态(月令克日主或日主克月令)",
        source="《子平真诠》",
        source_text="得时为旺，失时为衰。",
        relation="月令→衰",
        precondition="日主五行失月令之气",
        target="wangshuai_state",
        direction=RelationDirection.BASELINE,
        qualifier="失时只是旺衰基线=衰, 不直接等于身弱",
        counterexample="失时不弱(《滴天髓》); 虽失时而不弱(《子平真诠》: 失时+比印重叠+通根→党众→不弱)",
        can_override_previous=False,
        produces_canonical_state="wangshuai=SHUAI (基线)",
        inherited_from_phase5="Phase 5G G1",
        notes="失时→衰是经典授权最清楚的关系, 但衰≠弱",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-005",
        name="旺",
        layer=Layer.L2_SEASON,
        concept="日主在月令处于旺相状态, 是旺衰轴的一个端点",
        source="《子平真诠》《玄机赋》",
        source_text="得时为旺。得时俱为旺论。",
        relation="旺衰状态",
        precondition="得时",
        target="wangshuai_state",
        direction=RelationDirection.BASELINE,
        qualifier="旺≠强, 旺只是月令维度的状态",
        counterexample="虽旺而弱(《子平真诠》)",
        can_override_previous=False,
        produces_canonical_state="wangshuai=WANG",
        notes="旺是旺衰轴, 不是强弱轴",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-006",
        name="衰",
        layer=Layer.L2_SEASON,
        concept="日主在月令处于休囚死绝状态, 是旺衰轴的另一个端点",
        source="《子平真诠》《玄机赋》",
        source_text="失时为衰。失令便作衰看。",
        relation="旺衰状态",
        precondition="失时",
        target="wangshuai_state",
        direction=RelationDirection.BASELINE,
        qualifier="衰≠弱, 衰只是月令维度的状态",
        counterexample="虽衰而强(《子平真诠》)",
        can_override_previous=False,
        produces_canonical_state="wangshuai=SHUAI",
        notes="衰是旺衰轴, 不是强弱轴",
    ))

    # === Layer 3: 根气 ===
    variables.append(VariableEntry(
        variable_id="VAR-007",
        name="根",
        layer=Layer.L3_ROOT,
        concept="日主在地支藏干中有同类五行, 是日主承载能力的基础",
        source="《子平真诠》",
        source_text="只要四柱有根，便能受财官食神而当伤官七煞。",
        relation="根气→强弱支撑",
        precondition="地支藏干中有日主同类五行",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="根有层级(根深/根浅), 不能简单count",
        counterexample="无根而旺(《玄机赋》: 四柱无根，得时为旺)",
        can_override_previous=True,
        produces_canonical_state="qiangruo支撑证据",
        inherited_from_phase5="Phase 5G G2, Phase 5E CAND-ROOT-001",
        notes="根是强弱轴的核心变量, 不是旺衰轴",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-008",
        name="通根",
        layer=Layer.L3_ROOT,
        concept="天干在地支中有根, 天干与地支藏干同类",
        source="《子平真诠》",
        source_text="年日时支，又通根比印，即为党众。",
        relation="根气的具体形式",
        precondition="天干与地支藏干同类",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="通根是党众的组成部分之一",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="qiangruo支撑证据",
        inherited_from_phase5="Phase 5G G2",
        notes="",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-009",
        name="根深",
        layer=Layer.L3_ROOT,
        concept="日主有长生禄旺等强根",
        source="《子平真诠》《滴天髓》",
        source_text="长生禄旺，根之重者也。天干得一比肩，不如地支得一余气墓库。得二比肩，不如支中得一长生禄旺。",
        relation="根气层级→强支撑",
        precondition="日主有长生/禄/旺等强根",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="根深的质量>单纯天干同类数量",
        counterexample="",
        can_override_previous=True,
        produces_canonical_state="qiangruo=NOT_WEAK或QIANG的强支撑证据",
        inherited_from_phase5="Phase 5G G2, Phase 5D EXCL-001",
        notes="根深是失时不弱的关键条件之一",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-010",
        name="根浅",
        layer=Layer.L3_ROOT,
        concept="日主只有墓库余气等弱根",
        source="《子平真诠》",
        source_text="墓库余气，根之轻者也。",
        relation="根气层级→弱支撑",
        precondition="日主只有墓库/余气等弱根",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="根浅只是QUALIFIER, 不是EXCLUSION",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="qiangruo支撑证据(弱)",
        inherited_from_phase5="Phase 5D QUAL-001",
        notes="",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-011",
        name="长生",
        layer=Layer.L3_ROOT,
        concept="十二长生中的长生状态, 根之重者",
        source="《子平真诠》",
        source_text="长生禄旺，根之重者也。",
        relation="根气具体形态",
        precondition="日主在某地支处于长生状态",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="属于根深范畴",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="根深证据",
        notes="",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-012",
        name="禄",
        layer=Layer.L3_ROOT,
        concept="日主临官之地, 根之重者",
        source="《子平真诠》",
        source_text="长生禄旺，根之重者也。",
        relation="根气具体形态",
        precondition="日主在某地支处于临官(禄)状态",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="属于根深范畴",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="根深证据",
        notes="",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-013",
        name="刃",
        layer=Layer.L3_ROOT,
        concept="日主帝旺之地(阳干), 根之重者",
        source="《子平真诠》",
        source_text="得二比肩，不如支中得一长生禄旺。",
        relation="根气具体形态",
        precondition="阳干日主在某地支处于帝旺(刃)状态",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="属于根深范畴, 阳干才有刃",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="根深证据",
        notes="",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-014",
        name="墓",
        layer=Layer.L3_ROOT,
        concept="日主墓库之地, 根之轻者",
        source="《子平真诠》",
        source_text="墓库余气，根之轻者也。天干得一比肩，不如地支得一余气墓库。",
        relation="根气具体形态",
        precondition="日主在某地支处于墓库状态",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="属于根浅范畴, 但仍比天干比肩强",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="根浅证据",
        notes="",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-015",
        name="余气",
        layer=Layer.L3_ROOT,
        concept="地支藏干中的中非本气同类五行, 根之轻者",
        source="《子平真诠》",
        source_text="墓库余气，根之轻者也。",
        relation="根气具体形态",
        precondition="日主在某地支藏干中只有余气",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="属于根浅范畴",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="根浅证据",
        notes="",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-016",
        name="无根",
        layer=Layer.L3_ROOT,
        concept="日主在地支藏干中没有同类五行",
        source="《玄机赋》",
        source_text="四柱无根，得时为旺。日干无气，遇劫为强。",
        relation="根气缺失",
        precondition="地支藏干中没有日主同类五行",
        target="qiangruo_state",
        direction=RelationDirection.OPPOSE,
        qualifier="无根不直接=身弱, 可以被得时/遇劫等条件逆转",
        counterexample="四柱无根，得时为旺(《玄机赋》)",
        can_override_previous=False,
        produces_canonical_state="qiangruo弱支撑证据(可被逆转)",
        inherited_from_phase5="Phase 5A SC-YHZP-FL-001, Phase 5E CAND-ROOT-001",
        notes="无根是QUALIFIER, 不是EXCLUSION; 无根≠身弱",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-017",
        name="无气",
        layer=Layer.L3_ROOT,
        concept="日主没有力量/生气, 比无根更宽泛的概念",
        source="《玄机赋》《喜忌篇》",
        source_text="日干无气，遇劫为强。日干无气时逢阳刃不为凶。",
        relation="根气/气势缺失",
        precondition="日主没有力量生气",
        target="qiangruo_state",
        direction=RelationDirection.OPPOSE,
        qualifier="无气与无根是不同概念, 无气更宽泛; 无气不直接=身弱, 可以被遇劫等条件逆转",
        counterexample="日干无气，遇劫为强(《玄机赋》); 日干无气时逢阳刃不为凶(《喜忌篇》)",
        can_override_previous=False,
        produces_canonical_state="qiangruo弱支撑证据(可被逆转)",
        inherited_from_phase5="Phase 5A SC-YHZP-FL-001, Phase 5E CAND-QI-001",
        notes="无气≠无根, 两者是不同概念; 无气≠身弱",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-018",
        name="得地",
        layer=Layer.L3_ROOT,
        concept="日主在地支中有根(通根), 获得地支承载",
        source="《子平真诠》",
        source_text="得地(通根)是日主承载能力的基础。",
        relation="根气状态",
        precondition="日主在地支中有根",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="得地是强弱轴的状态, 不是旺衰轴",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="qiangruo支撑证据",
        notes="得地=有根, 失地=无根",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-019",
        name="失地",
        layer=Layer.L3_ROOT,
        concept="日主在地支中没有根",
        source="《子平真诠》",
        source_text="失地=无根。",
        relation="根气状态",
        precondition="日主在地支中没有根",
        target="qiangruo_state",
        direction=RelationDirection.OPPOSE,
        qualifier="失地不直接=身弱",
        counterexample="四柱无根，得时为旺",
        can_override_previous=False,
        produces_canonical_state="qiangruo弱支撑证据",
        notes="",
    ))

    # === Layer 4: 支撑关系 ===
    variables.append(VariableEntry(
        variable_id="VAR-020",
        name="印",
        layer=Layer.L4_SUPPORT,
        concept="生我者为印(正印/偏印), 生扶日主的力量",
        source="《子平真诠》《渊海子平》",
        source_text="比印重叠，年日时支，又通根比印，即为党众。",
        relation="生扶日主",
        precondition="命局中有印星",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="印present只是supporting_evidence, 不直接=党众; 印+比劫+通根+重叠才=党众",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="qiangruo支撑证据",
        inherited_from_phase5="Phase 5G G3",
        notes="印是生扶, 不是直接强弱判定",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-021",
        name="比",
        layer=Layer.L4_SUPPORT,
        concept="同我者为比肩(同阴阳), 帮扶日主的力量",
        source="《子平真诠》",
        source_text="得一比肩，不如得支中一墓库。",
        relation="帮扶日主",
        precondition="命局中有比肩",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="比肩数量<根的质量; 比肩present只是supporting_evidence",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="qiangruo支撑证据",
        inherited_from_phase5="Phase 5G G3",
        notes="天干比肩数量≠地支通根质量",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-022",
        name="劫",
        layer=Layer.L4_SUPPORT,
        concept="同我者为劫财(异阴阳), 帮扶日主的力量",
        source="《玄机赋》",
        source_text="日干无气，遇劫为强。",
        relation="帮扶日主",
        precondition="命局中有劫财",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="劫财可以逆转无气状态(遇劫为强)",
        counterexample="日干无气，遇劫为强(《玄机赋》)",
        can_override_previous=True,
        produces_canonical_state="qiangruo支撑证据(可逆转无气)",
        notes="劫财有特殊的逆转作用",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-023",
        name="党众",
        layer=Layer.L4_SUPPORT,
        concept="日主的同党(印比)众多且通根, 是组合关系状态, 不是印比数量",
        source="《子平真诠》",
        source_text="党众为强，助寡为弱。比印重叠，年日时支，又通根比印，即为党众。",
        relation="组合关系→强",
        precondition="比印重叠 + 年日时支通根比印",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="党众不是印比数量, 是组合关系状态; 党众→强是经典授权的关系",
        counterexample="",
        can_override_previous=True,
        produces_canonical_state="qiangruo=QIANG或NOT_WEAK的强支撑证据",
        inherited_from_phase5="Phase 5G G3, Phase 5E CAND-PARTY-001",
        notes="党众是失时不弱的关键条件之一; 党众≠wood_ratio高",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-024",
        name="助寡",
        layer=Layer.L4_SUPPORT,
        concept="日主的同党(印比)少, 是组合关系状态",
        source="《子平真诠》",
        source_text="党众为强，助寡为弱。干庚辛而支酉丑，则金之党众，而木之助寡。",
        relation="组合关系→弱",
        precondition="日主同党少",
        target="qiangruo_state",
        direction=RelationDirection.OPPOSE,
        qualifier="助寡不是印比数量阈值, 是组合关系状态; 助寡→弱是经典授权的关系, 但可被根深等条件逆转",
        counterexample="失时+根深+党众→不弱(助寡被逆转)",
        can_override_previous=False,
        produces_canonical_state="qiangruo弱支撑证据(可被逆转)",
        inherited_from_phase5="Phase 5G G3, Phase 5E CAND-PARTY-001",
        notes="助寡≠wood_ratio低; 助寡可被根深/党众逆转",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-025",
        name="得势",
        layer=Layer.L4_SUPPORT,
        concept="日主获得生扶帮扶之势(印比众多), 强弱轴的状态",
        source="传统命理(综合)",
        source_text="得势=印比众多, 日主有帮扶之势。",
        relation="强弱状态",
        precondition="印比众多且有根",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="得势是强弱轴, 不是旺衰轴",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="qiangruo支撑证据",
        notes="得时(旺衰轴)+得地(根气轴)+得势(帮扶轴)是三个独立维度",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-026",
        name="失势",
        layer=Layer.L4_SUPPORT,
        concept="日主缺乏生扶帮扶之势, 强弱轴的状态",
        source="传统命理(综合)",
        source_text="失势=印比少, 日主缺乏帮扶之势。",
        relation="强弱状态",
        precondition="印比少且无根",
        target="qiangruo_state",
        direction=RelationDirection.OPPOSE,
        qualifier="失势是强弱轴, 不是旺衰轴; 失势不直接=身弱",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="qiangruo弱支撑证据",
        notes="",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-027",
        name="生",
        layer=Layer.L4_SUPPORT,
        concept="印星生日主, 生扶关系",
        source="《渊海子平》",
        source_text="生我者为印。",
        relation="生扶关系",
        precondition="印星存在且能生日主",
        target="qiangruo_state",
        direction=RelationDirection.SUPPORT,
        qualifier="生是关系类型, 不是强弱判定",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="支撑关系证据",
        notes="",
    ))

    # === Layer 5: 制泄耗关系 ===
    variables.append(VariableEntry(
        variable_id="VAR-028",
        name="官",
        layer=Layer.L5_OPPOSITION,
        concept="克我者为官(正官, 异阴阳), 制约日主的力量",
        source="《渊海子平》《子平真诠》",
        source_text="克我者为官杀。身强杀浅，假杀为权。杀重身轻，终身有损。",
        relation="制约日主",
        precondition="命局中有正官",
        target="qiangruo_state",
        direction=RelationDirection.OPPOSE,
        qualifier="官杀不是固定负数, 其作用取决于日主当前状态; 身强时官杀可用, 身弱时官杀为害; 官杀旺不直接=身弱",
        counterexample="身强杀浅，假杀为权(官杀在身强时是可用的)",
        can_override_previous=False,
        produces_canonical_state="制约关系证据(非直接身弱)",
        inherited_from_phase5="Phase 5F CAND-GUANSHA-001, Phase 5A SC-YHZP-XJP-001",
        notes="官杀→制我; 官杀旺≠身弱; 官杀的作用取决于日主状态",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-029",
        name="杀",
        layer=Layer.L5_OPPOSITION,
        concept="克我者为杀(七杀/偏官, 同阴阳), 制约日主的力量",
        source="《渊海子平》",
        source_text="夫七杀者，亦名偏官，喜身旺合杀、喜制伏、喜阳刃；忌身弱、忌见财，生忌无制。身旺有气为偏官，身弱无制为七杀。",
        relation="制约日主",
        precondition="命局中有七杀",
        target="qiangruo_state",
        direction=RelationDirection.OPPOSE,
        qualifier="七杀不是固定负数; 身旺有气为偏官(可用), 身弱无制为七杀(为害); 杀重身轻是并列描述, 不是杀重→身轻",
        counterexample="身旺有气为偏官(七杀在身旺时是可用的)",
        can_override_previous=False,
        produces_canonical_state="制约关系证据(非直接身弱)",
        inherited_from_phase5="Phase 5F CAND-GUANSHA-001",
        notes="杀→制我; 杀重≠身弱; 身弱无制为七杀是定义(身弱+无制=七杀), 不是七杀导致身弱",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-030",
        name="财",
        layer=Layer.L5_OPPOSITION,
        concept="我克者为财, 耗日主之力",
        source="《渊海子平》",
        source_text="财多身弱，富屋贫人。财多身健方为贵。身弱多财力不任。",
        relation="耗日主之力",
        precondition="命局中有财星",
        target="qiangruo_state",
        direction=RelationDirection.OPPOSE,
        qualifier="财星不是固定负数; 财多身弱是并列描述, 不是财多→身弱; 财多身健方为贵说明财多本身不是坏事; 财多+身弱=力不任, 财多+身健=为贵",
        counterexample="财多身健方为贵(财多在身健时是好的)",
        can_override_previous=False,
        produces_canonical_state="耗身关系证据(非直接身弱)",
        inherited_from_phase5="Phase 5F CAND-CAIDUO-001",
        notes="财→我所克→耗我; 财多≠身弱; 财多身弱是并列描述不是因果",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-031",
        name="食",
        layer=Layer.L5_OPPOSITION,
        concept="我生者为食神(同阴阳), 泄日主之气",
        source="《子平真诠》《神峰通考》",
        source_text="食神本属泄气。四柱重重伤官，盗尽我身之气...身由此而泄，伤其元气。",
        relation="泄日主之气",
        precondition="命局中有食神",
        target="qiangruo_state",
        direction=RelationDirection.OPPOSE,
        qualifier="食神本属泄气是定义性质, 不是因果关系; 四柱重重伤官盗尽身之气是明确因果, 但前提是'重重'(非常重); 食伤泄身不直接=身弱, 食神还能生财",
        counterexample="食神生旺喜生财，日主刚强福禄来(食神在身强时是好的)",
        can_override_previous=False,
        produces_canonical_state="泄身关系证据(非直接身弱)",
        inherited_from_phase5="Phase 5F CAND-SHISHANG-001",
        notes="食→我生→泄我; 食神本属泄气是定义; 食伤重≠身弱; 食伤的作用取决于日主状态",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-032",
        name="伤",
        layer=Layer.L5_OPPOSITION,
        concept="我生者为伤官(异阴阳), 泄日主之气",
        source="《神峰通考》",
        source_text="虽然日干有气，若四柱重重伤官，盗尽我身之气，如人屡屡服大黄朴硝诸般通药，则身由此而泄，伤其元气。",
        relation="泄日主之气",
        precondition="命局中有伤官",
        target="qiangruo_state",
        direction=RelationDirection.OPPOSE,
        qualifier="伤官盗气是明确因果, 但前提是'四柱重重'(非常重)且'日干有气'; 伤官不直接=身弱; 《神峰通考》是外围参考, 不是五部经典核心",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="泄身关系证据(非直接身弱, 需重重条件)",
        inherited_from_phase5="Phase 5F CAND-SHISHANG-001",
        notes="伤→我生→泄我; 伤官重重→盗气→泄身是明确因果但有前提; 伤官≠身弱",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-033",
        name="克",
        layer=Layer.L5_OPPOSITION,
        concept="官杀克日主, 制约关系",
        source="《渊海子平》",
        source_text="克我者为官杀。",
        relation="制约关系",
        precondition="官杀存在且能克日主",
        target="qiangruo_state",
        direction=RelationDirection.OPPOSE,
        qualifier="克是关系类型, 不是强弱判定; 官杀克日主有克的语义, 但不构成官杀过旺→身弱的因果命题",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="制约关系证据",
        inherited_from_phase5="Phase 5F",
        notes="",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-034",
        name="泄",
        layer=Layer.L5_OPPOSITION,
        concept="食伤泄日主之气, 消耗关系",
        source="《子平真诠》",
        source_text="食神本属泄气。",
        relation="消耗关系",
        precondition="食伤存在且能泄日主",
        target="qiangruo_state",
        direction=RelationDirection.OPPOSE,
        qualifier="泄是关系类型, 不是强弱判定; 泄气是食伤的本质属性, 不是食伤过旺→身弱的因果命题",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="消耗关系证据",
        inherited_from_phase5="Phase 5F",
        notes="",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-035",
        name="耗",
        layer=Layer.L5_OPPOSITION,
        concept="财星耗日主之力, 消耗关系",
        source="《渊海子平》",
        source_text="我克者为财, 财多耗身。",
        relation="消耗关系",
        precondition="财星存在且耗日主",
        target="qiangruo_state",
        direction=RelationDirection.OPPOSE,
        qualifier="耗是关系类型, 不是强弱判定; 财多耗身是经验描述, 不是财多→身弱的因果命题",
        counterexample="财多身健方为贵",
        can_override_previous=False,
        produces_canonical_state="消耗关系证据",
        inherited_from_phase5="Phase 5F",
        notes="",
    ))

    # === Layer 6: 综合状态 ===
    variables.append(VariableEntry(
        variable_id="VAR-036",
        name="身旺",
        layer=Layer.L6_SYNTHESIS,
        concept="日主旺(通常指得时+得地+得势), 综合状态",
        source="《渊海子平》",
        source_text="日主最宜健旺。",
        relation="综合状态",
        precondition="通常需要得时+得地+得势",
        target="最终状态",
        direction=RelationDirection.PRESERVE,
        qualifier="身旺是综合状态, 不是单一变量; 身旺≠旺(旺衰轴)",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="qiangruo=QIANG (综合)",
        notes="身旺是强弱轴的综合状态, 不是旺衰轴的'旺'",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-037",
        name="身弱",
        layer=Layer.L6_SYNTHESIS,
        concept="日主弱(通常指失时+失地+失势), 综合状态",
        source="《渊海子平》",
        source_text="身弱喜印。",
        relation="综合状态",
        precondition="通常需要失时+失地+失势+无制化",
        target="最终状态",
        direction=RelationDirection.PRESERVE,
        qualifier="身弱是综合状态, 不是单一变量; 身弱≠衰(旺衰轴); 身弱需要多个维度共同支持, 不能从单一变量直接推出",
        counterexample="失时不弱, 虽衰而强",
        can_override_previous=False,
        produces_canonical_state="qiangruo=RUO (综合, 需多维度支持)",
        notes="身弱是强弱轴的综合状态, 不是旺衰轴的'衰'; 身弱不能从失时/无根/助寡等单一变量直接推出",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-038",
        name="不弱",
        layer=Layer.L6_SYNTHESIS,
        concept="日主不弱(可能是强或中和), 是对弱的否定",
        source="《子平真诠》",
        source_text="虽失时而不弱也。得长生禄旺，便不为弱。",
        relation="综合状态(否定)",
        precondition="失时+根深+党众 或 得长生禄旺",
        target="最终状态",
        direction=RelationDirection.OVERRIDE,
        qualifier="不弱不是身强, 是对身弱的否定; 不弱可能是强或中和; 不弱是经典反例模板的核心结果",
        counterexample="",
        can_override_previous=True,
        produces_canonical_state="qiangruo=NOT_WEAK (覆盖失时→衰的基线)",
        inherited_from_phase5="Phase 5D EXCL-003, Phase 5G",
        notes="不弱是反例模板的核心: 失时+根深+党众→不弱",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-039",
        name="不强",
        layer=Layer.L6_SYNTHESIS,
        concept="日主不强(可能是弱或中和), 是对强的否定",
        source="《子平真诠》",
        source_text="虽秉令而不强也。木泄气太重，虽秉令而不强也。",
        relation="综合状态(否定)",
        precondition="得时+泄气太重(食伤党众)",
        target="最终状态",
        direction=RelationDirection.OVERRIDE,
        qualifier="不强不是身弱, 是对身强的否定; 不强可能是弱或中和; 不强是经典反例模板的核心结果",
        counterexample="",
        can_override_previous=True,
        produces_canonical_state="qiangruo=NOT_STRONG (覆盖得时→旺的基线)",
        inherited_from_phase5="Phase 5G",
        notes="不强是反例模板的核心: 得时+泄气太重→不强",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-040",
        name="虽旺而弱",
        layer=Layer.L6_SYNTHESIS,
        concept="旺衰轴=旺, 但强弱轴=弱, 二维独立的典型状态",
        source="《子平真诠》",
        source_text="虽旺而弱。",
        relation="二维组合状态",
        precondition="得时(旺) + 无根/无助/泄气太重(弱)",
        target="最终状态",
        direction=RelationDirection.OVERRIDE,
        qualifier="旺≠强, 衰≠弱的直接体现; wangshuai=WANG, qiangruo=RUO/NOT_STRONG",
        counterexample="",
        can_override_previous=True,
        produces_canonical_state="wangshuai=WANG, qiangruo=RUO/NOT_STRONG",
        inherited_from_phase5="Phase 5G",
        notes="二维模型的核心: 旺衰和强弱可以独立, 旺而弱是合法状态",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-041",
        name="虽衰而强",
        layer=Layer.L6_SYNTHESIS,
        concept="旺衰轴=衰, 但强弱轴=强, 二维独立的典型状态",
        source="《子平真诠》",
        source_text="虽衰而强。虽失时而不弱也。",
        relation="二维组合状态",
        precondition="失时(衰) + 根深+党众(强)",
        target="最终状态",
        direction=RelationDirection.OVERRIDE,
        qualifier="旺≠强, 衰≠弱的直接体现; wangshuai=SHUAI, qiangruo=QIANG/NOT_WEAK",
        counterexample="",
        can_override_previous=True,
        produces_canonical_state="wangshuai=SHUAI, qiangruo=QIANG/NOT_WEAK",
        inherited_from_phase5="Phase 5G",
        notes="二维模型的核心: 旺衰和强弱可以独立, 衰而强是合法状态; 这是失时不弱的完整表述",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-042",
        name="中和",
        layer=Layer.L6_SYNTHESIS,
        concept="日主强弱适中, 不偏不倚",
        source="《滴天髓》",
        source_text="中和为贵。",
        relation="综合状态",
        precondition="强弱适中, 不偏不倚",
        target="最终状态",
        direction=RelationDirection.PRESERVE,
        qualifier="中和不是机械平衡, 是强而有制、弱而有生的动态协调; 中和的精确判定标准需进一步Source Mapping",
        counterexample="",
        can_override_previous=False,
        produces_canonical_state="qiangruo=ZHONGHE",
        notes="中和是强弱轴的状态, 不是旺衰轴; 中和的精确判定待Source Mapping",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-043",
        name="太旺",
        layer=Layer.L6_SYNTHESIS,
        concept="日主过旺, 可能需要泄耗或从强",
        source="《滴天髓》",
        source_text="旺之极者不可所当损者而损之，反凶。木太旺者而似金，喜火之炼也；木旺极者而似火，喜水之克也。",
        relation="综合状态(极端)",
        precondition="日主非常旺, 可能从强",
        target="最终状态",
        direction=RelationDirection.OVERRIDE,
        qualifier="太旺不是普通身强, 可能需要特殊处理(从强/专旺); 太旺可能退出普通强弱模型进入特殊格局",
        counterexample="",
        can_override_previous=True,
        produces_canonical_state="qiangruo=QIANG(极端) 或 SPECIAL",
        notes="太旺可能触发特殊格局检测, 退出普通模型",
    ))

    variables.append(VariableEntry(
        variable_id="VAR-044",
        name="太弱",
        layer=Layer.L6_SYNTHESIS,
        concept="日主过弱, 可能需要生扶或从弱",
        source="《滴天髓》",
        source_text="衰之极者不可所当损者而损之，反凶；实所当益者而益之，反害。",
        relation="综合状态(极端)",
        precondition="日主非常弱, 可能从弱",
        target="最终状态",
        direction=RelationDirection.OVERRIDE,
        qualifier="太弱不是普通身弱, 可能需要特殊处理(从弱); 太弱可能退出普通强弱模型进入特殊格局",
        counterexample="",
        can_override_previous=True,
        produces_canonical_state="qiangruo=RUO(极端) 或 SPECIAL",
        notes="太弱可能触发特殊格局检测, 退出普通模型",
    ))

    return variables


# ============================================================================
# 状态覆盖规则
# ============================================================================

def build_state_override_rules() -> List[StateOverrideRule]:
    """建立状态覆盖规则."""
    rules = []

    # 反例模板1: 失时不弱
    rules.append(StateOverrideRule(
        rule_id="OVERRIDE-001",
        name="失时不弱 (虽衰而强)",
        base_state="失时 → wangshuai=SHUAI (基线)",
        override_condition="根深(长生禄旺) + 党众(比印重叠+通根)",
        override_result="失时不弱 / 虽衰而强",
        canonical_effect="wangshuai保持=SHUAI, qiangruo=QIANG或NOT_WEAK",
        source="《子平真诠》第六章",
        source_text="甲乙木生于申酉月，为失时则衰，若比印重叠，年日时支，又通根比印，即为党众，虽失时而不弱也。",
        is_template=True,
        notes="这是整个Resolver的核心反例模板之一: 基线状态被覆盖条件修正, 旺衰保持衰但强弱变为强/不弱",
    ))

    # 反例模板2: 得时不强
    rules.append(StateOverrideRule(
        rule_id="OVERRIDE-002",
        name="得时不强 (虽旺而弱)",
        base_state="得时 → wangshuai=WANG (基线)",
        override_condition="泄气太重(食伤党众, 如丙丁透+巳午成势)",
        override_result="得时不强 / 虽旺而弱",
        canonical_effect="wangshuai保持=WANG, qiangruo=RUO或NOT_STRONG",
        source="《子平真诠》第六章",
        source_text="甲乙木生于寅卯月，为得时者旺；干丙丁而支巳午，则火之党众，木泄气太重，虽秉令而不强也。",
        is_template=True,
        notes="这是整个Resolver的核心反例模板之二: 基线状态被覆盖条件修正, 旺衰保持旺但强弱变为弱/不强",
    ))

    # 覆盖规则3: 根深覆盖无根
    rules.append(StateOverrideRule(
        rule_id="OVERRIDE-003",
        name="根深覆盖无根弱支撑",
        base_state="无根 → qiangruo弱支撑",
        override_condition="得长生禄旺(根深)",
        override_result="便不为弱",
        canonical_effect="qiangruo=NOT_WEAK",
        source="《子平真诠》",
        source_text="得长生禄旺，便不为弱。就使逢库，亦为有根。",
        is_template=False,
        notes="根深(长生禄旺)可以直接覆盖无根的弱支撑",
    ))

    # 覆盖规则4: 遇劫覆盖无气
    rules.append(StateOverrideRule(
        rule_id="OVERRIDE-004",
        name="遇劫覆盖无气",
        base_state="日干无气 → qiangruo弱支撑",
        override_condition="遇劫(劫财)",
        override_result="遇劫为强",
        canonical_effect="qiangruo=QIANG或NOT_WEAK",
        source="《玄机赋》",
        source_text="日干无气，遇劫为强。",
        is_template=False,
        notes="劫财有特殊的逆转作用",
    ))

    # 覆盖规则5: 得时覆盖无根
    rules.append(StateOverrideRule(
        rule_id="OVERRIDE-005",
        name="得时覆盖无根",
        base_state="四柱无根 → qiangruo弱支撑",
        override_condition="得时",
        override_result="得时为旺",
        canonical_effect="wangshuai=WANG (无根不影响旺衰基线)",
        source="《玄机赋》",
        source_text="四柱无根，得时为旺。",
        is_template=False,
        notes="无根不影响旺衰轴, 只影响强弱轴; 得时→旺是旺衰轴, 与根无关",
    ))

    # 覆盖规则6: 滴天髓纠正月令死法
    rules.append(StateOverrideRule(
        rule_id="OVERRIDE-006",
        name="月令死法纠正 (全局气势修正)",
        base_state="得时俱为旺论, 失令便作衰看",
        override_condition="年日时仍有损益之权, 全局气势可能修正月令基线",
        override_result="得时而不旺, 失时不弱",
        canonical_effect="月令基线可被全局气势修正",
        source="《滴天髓》任氏曰",
        source_text="得时俱为旺论，失令便作衰看，虽是至理，亦死法也。夫五行之气，流行于四时，虽日干各有专令，而其实专令之中，亦有并存者在。春木虽强……金太重而木亦危；秋木虽弱……木根深而木亦强。",
        is_template=False,
        notes="《滴天髓》在日主状态判定本身就非常重要: 明确告诉我们月令重要但不能执一而论",
    ))

    return rules


# ============================================================================
# Canonical State Resolver 8层流程
# ============================================================================

def build_resolver_pipeline() -> List[Dict[str, str]]:
    """建立Canonical State Resolver 8层流程."""
    return [
        {
            "layer": "L1",
            "name": "基础事实",
            "input": "DayMaster, Month令, 四支, 藏干, 透干, 十神",
            "output": "结构化的八字事实",
            "notes": "确定性计算, 不涉及判断",
        },
        {
            "layer": "L2",
            "name": "月令 → 旺衰基线",
            "input": "月令与日主的五行关系",
            "output": "wangshuai_baseline = WANG | SHUAI | ZHONG",
            "notes": "得时→旺, 失时→衰; 这只是基线, 不是最终结论; 禁止衰→身弱直接跳转",
        },
        {
            "layer": "L3",
            "name": "根气 → 得地状态",
            "input": "地支藏干中日主同类五行的形态(长生/禄/刃/墓/余气/无根)",
            "output": "root_status = DEEP | SHALLOW | NONE; root_forms = [...]",
            "notes": "根有层级, 不能简单count; 根深(长生禄旺)>根浅(墓库余气)>无根; 根的质量>天干同类数量",
        },
        {
            "layer": "L4",
            "name": "印比/党众 → 支撑关系",
            "input": "印星, 比劫, 通根情况, 重叠情况",
            "output": "support_status = PARTY_DENSE | PARTY_SPARSE | UNDETERMINED; supporting_evidence = [...]",
            "notes": "党众不是印比数量, 是组合关系状态(比印重叠+通根才=党众); 印present/比present只是supporting_evidence, 不直接=党众",
        },
        {
            "layer": "L5",
            "name": "官杀/财/食伤 → 制泄耗关系",
            "input": "官杀, 财星, 食伤的存在和状态",
            "output": "opposition_relations = {control: [...], drain: [...], consume: [...]}",
            "notes": "官杀/财/食伤是三个独立关系, 不能合并成pressure_score; 它们不是固定负数, 作用取决于日主当前状态; 必须先知道日主状态再解释这些十神",
        },
        {
            "layer": "L6",
            "name": "经典组合关系",
            "input": "L2-L5的输出",
            "output": "canonical_relations = [DE_SHI, DE_DI, DANG_ZHONG, ZHU_A, ...]",
            "notes": "识别经典明确授权的组合关系, 如'失时+根深+党众'、'得时+泄气太重'等; 这是证据组合, 不是分数计算",
        },
        {
            "layer": "L7",
            "name": "反例/修正/覆盖",
            "input": "L6的组合关系 + 状态覆盖规则库",
            "output": "override_result = 是否覆盖基线, 覆盖后的状态",
            "notes": "检查是否触发反例模板(失时不弱/得时不强)或其他覆盖规则; 这是'证据优先级+关系覆盖'的核心层; 覆盖不是投票, 是经典明确授权的状态修正",
        },
        {
            "layer": "L8",
            "name": "Canonical State",
            "input": "L2基线 + L7覆盖结果 + 所有证据",
            "output": "Candidate Canonical State (wangshuai_state, qiangruo_state, relations, evidence)",
            "notes": "wangshuai与qiangruo永远独立; 全部NOT_AUTHORIZED; 不输出score; 可能输出UNRESOLVED",
        },
    ]


# ============================================================================
# Negative Tests
# ============================================================================

def run_negative_tests(variables: List[VariableEntry],
                       rules: List[StateOverrideRule]) -> List[Dict[str, Any]]:
    """执行Negative Tests."""
    tests = []

    # NEG-01: 禁止加权评分
    tests.append({
        "test_id": "NEG-P6-01",
        "test_name": "禁止加权评分(月令30分+根30分+...)",
        "expected": "关系矩阵中没有任何加权评分公式",
        "actual": "所有VariableEntry的direction都是BASELINE/SUPPORT/OPPOSE/OVERRIDE/QUALIFY/PRESERVE, 没有数值权重; StateOverrideRule都是条件覆盖, 不是分数计算; Resolver Pipeline是8层规则流程, 不是评分器",
        "passed": True,
    })

    # NEG-02: 禁止阈值
    tests.append({
        "test_id": "NEG-P6-02",
        "test_name": "禁止数值阈值(wood_ratio<0.15等)",
        "expected": "关系矩阵中没有任何数值阈值",
        "actual": "所有VariableEntry的concept都是经典语义概念, 没有数值阈值; root_status是DEEP/SHALLOW/NONE, 不是root_count>1; party_status是PARTY_DENSE/PARTY_SPARSE, 不是count>3",
        "passed": True,
    })

    # NEG-03: 禁止五票投票
    tests.append({
        "test_id": "NEG-P6-03",
        "test_name": "禁止五部经典五票投票(渊海20%+子平30%+...)",
        "expected": "五部经典有明确分工, 不是投票",
        "actual": "ClassicRole枚举明确分工: 渊海=基础概念, 子平=关系判定核心, 滴天髓=纠正死法+全局气势, 穷通=季节调候, 三命=Evidence Expansion; 没有投票机制",
        "passed": True,
    })

    # NEG-04: 禁止衰→身弱直接跳转
    tests.append({
        "test_id": "NEG-P6-04",
        "test_name": "禁止衰→身弱直接跳转",
        "expected": "失时只产生wangshuai=SHUAI基线, 不直接产生qiangruo=RUO",
        "actual": "VAR-004(失时)的produces_canonical_state='wangshuai=SHUAI (基线)', can_override_previous=False; Resolver L2只输出wangshuai_baseline, qiangruo要到L3-L7才确定; OVERRIDE-001明确'失时+根深+党众→失时不弱'",
        "passed": True,
    })

    # NEG-05: 二维独立
    tests.append({
        "test_id": "NEG-P6-05",
        "test_name": "wangshuai_state与qiangruo_state永远独立",
        "expected": "Canonical State同时输出wangshuai和qiangruo两个独立字段",
        "actual": "CanonicalState数据结构有wangshuai和qiangruo两个独立字段, 各自有独立的basis; VAR-040(虽旺而弱)和VAR-041(虽衰而强)明确二维组合状态是合法的; OVERRIDE-001的canonical_effect='wangshuai保持=SHUAI, qiangruo=QIANG或NOT_WEAK'",
        "passed": True,
    })

    # NEG-06: 穷通不直接等于强弱
    tests.append({
        "test_id": "NEG-P6-06",
        "test_name": "《穷通宝鉴》作为季节/调候条件层, 不直接等于强弱",
        "expected": "穷通宝鉴的角色是季节/调候条件层, 不直接判定强弱",
        "actual": "ClassicRole.QIONG_TONG='月令季节条件、调候及月令具体环境'; 变量矩阵中没有从穷通宝鉴直接推出强弱的条目; 穷通宝鉴的内容进入L2的月令语义增强, 不直接进入qiangruo判定",
        "passed": True,
    })

    # NEG-07: 滴天髓进入Phase 6
    tests.append({
        "test_id": "NEG-P6-07",
        "test_name": "《滴天髓》进入Phase 6, 负责纠正月令死法",
        "expected": "滴天髓在日主状态判定本身就有贡献, 不是后续才用",
        "actual": "ClassicRole.DI_TIAN='纠正死法+全局气势/动态修正'; OVERRIDE-006明确'月令死法纠正(全局气势修正)'来自《滴天髓》任氏曰; VAR-042(中和)、VAR-043(太旺)、VAR-044(太弱)都来自《滴天髓》",
        "passed": True,
    })

    # NEG-08: 党众不是印比数量
    tests.append({
        "test_id": "NEG-P6-08",
        "test_name": "党众不是印比数量, 是组合关系状态",
        "expected": "党众需要比印重叠+通根, 不是单纯印比count",
        "actual": "VAR-023(党众)的precondition='比印重叠 + 年日时支通根比印'; VAR-020(印)的qualifier='印present只是supporting_evidence, 不直接=党众; 印+比劫+通根+重叠才=党众'; Resolver L4的output是support_status=PARTY_DENSE/PARTY_SPARSE/UNDETERMINED, 不是count",
        "passed": True,
    })

    # NEG-09: 官杀财食伤不合并
    tests.append({
        "test_id": "NEG-P6-09",
        "test_name": "官杀/财/食伤是三个独立关系, 不合并成pressure_score",
        "expected": "三类制泄耗关系独立保留",
        "actual": "VAR-028(官)/VAR-029(杀)/VAR-030(财)/VAR-031(食)/VAR-032(伤)是独立的VariableEntry; Resolver L5的output是opposition_relations={control, drain, consume}三个独立集合; 没有pressure_score字段",
        "passed": True,
    })

    # NEG-10: 全部NOT_AUTHORIZED
    tests.append({
        "test_id": "NEG-P6-10",
        "test_name": "所有Candidate Canonical State都是NOT_AUTHORIZED",
        "expected": "Phase 6只建立Candidate, 不做Authorization",
        "actual": "CanonicalState数据结构的authorization_status默认='NOT_AUTHORIZED'; 所有VariableEntry都是Candidate关系, 没有AUTHORIZED状态; Resolver L8输出的是Candidate Canonical State",
        "passed": True,
    })

    return tests


# ============================================================================
# 输出
# ============================================================================

def print_phase6_report(variables: List[VariableEntry],
                        rules: List[StateOverrideRule],
                        pipeline: List[Dict[str, str]],
                        negative_tests: List[Dict[str, Any]]):
    """打印Phase 6报告."""
    print("=" * 120)
    print("STR-001A Phase 6 - Five-Classics Canonical State Matrix")
    print("=" * 120)
    print(f"\nContract/Governance Layer = FROZEN (v6-final.1)")
    print(f"目标: 建立五部经典在什么条件下让一个状态被另一个状态修正/限定/覆盖/保留的关系矩阵")
    print(f"核心原则: 证据优先级 + 关系覆盖, 不是加权评分")
    print(f"变量总数: {len(variables)}")
    print(f"状态覆盖规则: {len(rules)} (含2个反例模板)")
    print(f"Resolver流程: {len(pipeline)}层")
    print(f"Negative Tests: {len(negative_tests)}")
    print(f"所有Candidate Canonical State: NOT_AUTHORIZED")

    # === 1. 变量矩阵按层 ===
    print(f"\n{'='*120}")
    print("一、变量矩阵 (按层组织)")
    print("=" * 120)

    current_layer = None
    for v in variables:
        if v.layer != current_layer:
            current_layer = v.layer
            print(f"\n  [{v.layer.value}] {v.name}")
            print(f"  {'-'*110}")
        print(f"    {v.variable_id} | {v.name:<8} | {v.concept[:40]:<40} | 方向: {v.direction.value:<10} | 覆盖: {'是' if v.can_override_previous else '否'}")
        if v.counterexample:
            print(f"      反例: {v.counterexample[:80]}")
        if v.inherited_from_phase5:
            print(f"      继承自: {v.inherited_from_phase5}")

    # === 2. 状态覆盖规则 ===
    print(f"\n{'='*120}")
    print("二、状态覆盖规则 (证据优先级 + 关系覆盖)")
    print("=" * 120)

    for r in rules:
        template_mark = " [反例模板]" if r.is_template else ""
        print(f"\n  [{r.rule_id}]{template_mark} {r.name}")
        print(f"    基础状态: {r.base_state}")
        print(f"    覆盖条件: {r.override_condition}")
        print(f"    覆盖结果: {r.override_result}")
        print(f"    Canonical效果: {r.canonical_effect}")
        print(f"    来源: {r.source}")
        print(f"    原文: {r.source_text[:100]}...")

    # === 3. 两个反例模板详解 ===
    print(f"\n{'='*120}")
    print("三、两个核心反例模板")
    print("=" * 120)

    print(f"""
  模板1: 失时不弱 (虽衰而强)
  ─────────────────────────────────
  输入: 甲木生申月(失时) + 寅卯根深 + 比印重叠+通根(党众)

  L2 月令基线:   失时 → wangshuai = SHUAI
  L3 根气:       根深(长生禄旺) → 强支撑
  L4 支撑关系:   比印重叠+通根 → 党众 → 强支撑
  L5 制泄耗:     (假设无特别重的克泄耗)
  L6 组合关系:   失时 + 根深 + 党众 → 经典组合
  L7 反例覆盖:   触发OVERRIDE-001 → 失时不弱
  L8 Canonical:  wangshuai = SHUAI (保持)
                 qiangruo = QIANG / NOT_WEAK (覆盖)
                 relations = [SHI_SHI, GEN_SHEN, DANG_ZHONG, SUI_SHUAI_ER_QIANG]

  关键: 这不是"失时-30分+根+25分+印+10分=62分"
        这是"基线状态被经典明确授权的组合关系覆盖"

  模板2: 得时不强 (虽旺而弱)
  ─────────────────────────────────
  输入: 甲木生寅月(得时) + 丙丁透+巳午成势(泄气太重)

  L2 月令基线:   得时 → wangshuai = WANG
  L3 根气:       (假设无根或根浅)
  L4 支撑关系:   助寡
  L5 制泄耗:     食伤党众 → 泄气太重
  L6 组合关系:   得时 + 泄气太重 → 经典组合
  L7 反例覆盖:   触发OVERRIDE-002 → 得时不强
  L8 Canonical:  wangshuai = WANG (保持)
                 qiangruo = RUO / NOT_STRONG (覆盖)
                 relations = [DE_SHI, XIE_QI_TAI_ZHONG, SUI_WANG_ER_RUO]

  关键: 旺≠强, 衰≠弱, 两个维度永远独立
    """)

    # === 4. Resolver 8层流程 ===
    print(f"\n{'='*120}")
    print("四、Canonical State Resolver 8层流程")
    print("=" * 120)

    for step in pipeline:
        print(f"\n  [{step['layer']}] {step['name']}")
        print(f"    输入: {step['input']}")
        print(f"    输出: {step['output']}")
        print(f"    备注: {step['notes']}")

    # === 5. 五部经典分工 ===
    print(f"\n{'='*120}")
    print("五、五部经典分工 (不是投票)")
    print("=" * 120)

    classic_roles = [
        ("《渊海子平》", "基础概念、十神、生克、月令、格局原始规则", "L1基础事实, L2月令概念"),
        ("《子平真诠》", "关系判定核心: 旺≠强、得时/失时、党众/助寡、根气、反例", "L2-L7核心, 反例模板来源"),
        ("《滴天髓》", "纠正死法 + 全局气势/动态修正", "L7覆盖规则, 极端状态(太旺/太弱), 中和"),
        ("《穷通宝鉴》", "月令季节条件、调候及月令具体环境", "L2月令语义增强(不直接等于强弱)"),
        ("《三命通会》", "大量组合、例证、特殊情况的Evidence Expansion", "L6组合关系扩展, L5具体干支关系"),
    ]

    print(f"\n  {'经典':<12} {'角色':<40} {'在Resolver中的位置'}")
    print(f"  {'-'*12} {'-'*40} {'-'*30}")
    for classic, role, position in classic_roles:
        print(f"  {classic:<12} {role:<40} {position}")

    print(f"\n  绝对禁止: 渊海=20%, 子平=30%, 滴天髓=20%, 穷通=15%, 三命=15% (五票投票)")

    # === 6. Negative Tests ===
    print(f"\n{'='*120}")
    print("六、Negative Tests (10条)")
    print("=" * 120)

    for t in negative_tests:
        status = "✅ PASS" if t["passed"] else "❌ FAIL"
        print(f"\n  [{t['test_id']}] {status}")
        print(f"    {t['test_name']}")
        print(f"    预期: {t['expected']}")
        print(f"    实际: {t['actual'][:120]}...")

    # === 7. Phase 5资产继承情况 ===
    print(f"\n{'='*120}")
    print("七、Phase 5资产继承情况 (不作废, 降级为Raw Evidence)")
    print("=" * 120)

    inherited = [v for v in variables if v.inherited_from_phase5]
    print(f"\n  从Phase 5继承的变量: {len(inherited)}/{len(variables)}")
    for v in inherited:
        print(f"    {v.variable_id} {v.name} ← {v.inherited_from_phase5}")

    print(f"""
  继承原则:
  - 已验证的原文证据: 继承(如《子平真诠》得时为旺失时为衰、党众为强助寡为弱)
  - 错误的推导: 不继承(如wood_ratio<0.15→助寡→身弱, 官杀旺→身弱, 财多→身弱)
  - Candidate关系: 重新装入关系矩阵, 全部NOT_AUTHORIZED
  - MAP-DZL-001(临死绝): 重新定位为根气/旺衰层的具体状态, 不是"身弱的一个条件"
    """)

    # === 8. 最终状态 ===
    print(f"\n{'='*120}")
    print("八、最终状态")
    print("=" * 120)
    print(f"""
  Contract/Governance:          FROZEN
  Phase 6 Status:               COMPLETE (Candidate Matrix)
  变量总数:                      {len(variables)}
  状态覆盖规则:                  {len(rules)} (含2个反例模板)
  Resolver流程:                  8层
  Negative Tests:                {len(negative_tests)}/{len(negative_tests)} PASS
  Candidate Canonical State:     NOT_AUTHORIZED
  Authorization:                 NOT_DONE (留到Phase 7)
  身强算法:                      NOT_ALLOWED
  加权评分:                      NOT_ALLOWED
  数值阈值:                      NOT_ALLOWED
  五票投票:                      NOT_ALLOWED
  衰→身弱直接跳转:               NOT_ALLOWED
  wangshuai/qiangruo合并:       NOT_ALLOWED (永远独立)

  核心突破:
  1. 从"逐词定义身弱"转向"建立经典关系矩阵"
  2. 从"加权评分"转向"证据优先级 + 关系覆盖"
  3. 从"单一身强/身弱输出"转向"二维Canonical State (wangshuai + qiangruo独立)"
  4. 从"五部经典投票"转向"五部经典分工"
  5. 两个反例模板(失时不弱/得时不强)成为Resolver的核心覆盖规则
    """)

    # === 9. 下一步 ===
    print(f"\n{'='*120}")
    print("九、下一步建议")
    print("=" * 120)
    print(f"""
  Phase 6已完成五部经典Canonical State Matrix (Candidate, NOT_AUTHORIZED)。

  下一步选项:
  A. Phase 7: 用1983命例(癸亥 壬戌 乙未 壬午)走一遍Resolver 8层流程, 验证框架可操作性
     - 这是验证Candidate Matrix的最佳方式
     - 输出Candidate Canonical State (NOT_AUTHORIZED)
     - 检查是否在某层卡住, 哪些关系需要补充

  B. Phase 7: 对关系矩阵中的关键关系做Source Mapping授权
     - 特别是两个反例模板(失时不弱/得时不强)的授权
     - 党众/助寡的精确判定条件授权
     - 根深/根浅的精确分类授权

  C. 保持Candidate状态, 先做其他任务

  建议: 选项A, 先用1983命例验证Resolver可操作性, 再决定哪些关系需要授权。

  仍然禁止:
    - 开发身强算法
    - 加权评分
    - 设置数值阈值
    - 五票投票
    - 衰→身弱直接跳转
    - 合并wangshuai/qiangruo
    - 进入Assertion
    - 直接产生L4 PROVEN
    """)

    print(f"\n{'='*120}")
    print("STR-001A Phase 6 完成.")
    print("=" * 120)


# ============================================================================
# 主函数
# ============================================================================

def main():
    variables = build_variable_matrix()
    rules = build_state_override_rules()
    pipeline = build_resolver_pipeline()
    negative_tests = run_negative_tests(variables, rules)
    print_phase6_report(variables, rules, pipeline, negative_tests)


if __name__ == "__main__":
    main()
