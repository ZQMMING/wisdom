"""
STR-001A P6.1.1 Semantic State Hardening

只修正 TRUE/FALSE 与 CANDIDATE/CONFIRMED/UNRESOLVED 的语义边界,
不增加任何新命理规则.

核心修正:
  1. root_state: 增加 ROOT_UNRESOLVED
  2. dangzhong_state: CONFIRMED / CANDIDATE / NOT_ESTABLISHED / UNRESOLVED
  3. 每一层严格区分: RELATION层只说关系是否确认,
     COMBINATION层说组合是否成立, CONCLUSION层说最终结论
  4. 1983命例重新表达

层级语义:
  L1 FACTS → 原始事实, 无判断
  RELATIONS → 原典关系是否成立 (CONFIRMED/CANDIDATE/REJECTED/UNRESOLVED)
  COMBINATION → 关系组合是否成立 (CONFIRMED/QUALIFIED/CANDIDATE/NOT_ESTABLISHED)
  CONCLUSION → 最终结论 (CONFIRMED/CANDIDATE/UNRESOLVED)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


# ============================================================
# 语义状态枚举 (修正后)
# ============================================================

class ConfirmationState(str, Enum):
    """通用确认状态: 用于RELATION层"""
    CONFIRMED = "CONFIRMED"           # 原典明确授权, 条件满足
    CANDIDATE = "CANDIDATE"           # 候选, 原典定义存疑或条件不完整
    REJECTED = "REJECTED"             # 原典明确不授权
    UNRESOLVED = "UNRESOLVED"         # 无法确定


class CombinationState(str, Enum):
    """组合状态: 用于COMBINATION层"""
    CONFIRMED = "CONFIRMED"           # 组合条件全部确认满足
    QUALIFIED = "QUALIFIED"           # 组合基本成立但带qualifier(如根轻、部分CANDIDATE)
    CANDIDATE = "CANDIDATE"           # 组合候选, 关键要素仍为CANDIDATE
    NOT_ESTABLISHED = "NOT_ESTABLISHED"  # 组合不成立
    UNRESOLVED = "UNRESOLVED"         # 无法确定


class ConclusionState(str, Enum):
    """结论状态: 用于CONCLUSION层"""
    CONFIRMED = "CONFIRMED"           # 最终结论确认
    CANDIDATE = "CANDIDATE"           # 结论候选
    UNRESOLVED = "UNRESOLVED"         # 无法确定 (不强行输出)


class RootQuality(str, Enum):
    """根质量 (修正后增加ROOT_UNRESOLVED)"""
    ROOT_HEAVY = "ROOT_HEAVY"         # 长生/禄/旺 → 根之重
    ROOT_LIGHT = "ROOT_LIGHT"         # 墓库/余气 → 根之轻
    ROOT_PRESENT = "ROOT_PRESENT"     # 实际通根但质量未分级
    ROOT_NONE = "ROOT_NONE"           # 无通根
    ROOT_UNRESOLVED = "ROOT_UNRESOLVED"  # 根状态无法确定 (如亥中甲同五行异天干)


class Wangshuai(str, Enum):
    WANG = "旺"
    SHUAI = "衰"
    UNRESOLVED = "UNRESOLVED"


class Qiangruo(str, Enum):
    STRONG = "强"
    WEAK = "弱"
    UNRESOLVED = "UNRESOLVED"


# ============================================================
# 分层数据结构
# ============================================================

@dataclass
class L1Facts:
    """L1 原始事实层 — 无判断"""
    day_master: str = ""
    month_branch: str = ""
    pillars: Dict[str, str] = field(default_factory=dict)
    growth_stages: Dict[str, str] = field(default_factory=dict)  # 地支→十二长生
    hidden_stems: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)  # 地支→[(藏干,层级)]
    ten_gods: Dict[str, str] = field(default_factory=dict)
    five_elements: Dict[str, int] = field(default_factory=dict)
    kong_wang: List[str] = field(default_factory=list)


@dataclass
class RelationEntry:
    """RELATION层条目 — 只说原典关系是否成立"""
    relation_id: str
    description: str
    l1_evidence: str                  # 基于哪些L1事实
    source_basis: str                  # 原典依据
    state: ConfirmationState           # CONFIRMED/CANDIDATE/REJECTED/UNRESOLVED
    root_quality: Optional[RootQuality] = None
    reason: str = ""


@dataclass
class RelationsLayer:
    """RELATION层 — 原典关系是否成立"""
    tonggen_per_branch: Dict[str, RelationEntry] = field(default_factory=dict)
    bijie_relation: Optional[RelationEntry] = None
    yin_relation: Optional[RelationEntry] = None
    guansha_relation: Optional[RelationEntry] = None
    shishang_relation: Optional[RelationEntry] = None
    cai_relation: Optional[RelationEntry] = None
    structure_relations: List[str] = field(default_factory=list)


@dataclass
class CombinationEntry:
    """COMBINATION层条目 — 关系组合是否成立"""
    combo_id: str
    description: str
    required_relations: List[str]     # 需要哪些RELATION层关系
    relation_states: Dict[str, str]   # 各关系的状态
    state: CombinationState            # CONFIRMED/QUALIFIED/CANDIDATE/NOT_ESTABLISHED
    qualifiers: List[str] = field(default_factory=list)
    reason: str = ""


@dataclass
class CombinationsLayer:
    """COMBINATION层 — 关系组合是否成立"""
    dangzhong: Optional[CombinationEntry] = None
    zhugua: Optional[CombinationEntry] = None
    kexiehao_combo: Optional[CombinationEntry] = None


@dataclass
class ConclusionEntry:
    """CONCLUSION层条目 — 最终结论"""
    conclusion_id: str
    description: str
    basis: str                        # 基于哪些COMBINATION层结果
    state: ConclusionState             # CONFIRMED/CANDIDATE/UNRESOLVED
    unresolved_reasons: List[str] = field(default_factory=list)
    qualifiers: List[str] = field(default_factory=list)


@dataclass
class ConclusionsLayer:
    """CONCLUSION层 — 最终结论"""
    wangshuai: Optional[ConclusionEntry] = None
    qiangruo: Optional[ConclusionEntry] = None
    special_pattern: Optional[ConclusionEntry] = None


@dataclass
class HardenedCanonicalState:
    """修正后的 Canonical State — 严格分层"""
    l1: L1Facts = field(default_factory=L1Facts)
    relations: RelationsLayer = field(default_factory=RelationsLayer)
    combinations: CombinationsLayer = field(default_factory=CombinationsLayer)
    conclusions: ConclusionsLayer = field(default_factory=ConclusionsLayer)
    modifiers: List[str] = field(default_factory=list)
    seasonal_remedy: Dict = field(default_factory=dict)


# ============================================================
# Resolver (修正语义后)
# ============================================================

class HardenedResolver:
    """语义修正后的 Canonical State Resolver"""

    def __init__(self):
        self.state = HardenedCanonicalState()

    def resolve(self, year: str, month: str, day: str, hour: str) -> HardenedCanonicalState:
        print("=" * 100)
        print("STR-001A P6.1.1 Semantic State Hardening")
        print(f"命例: {year} {month} {day} {hour}")
        print("=" * 100)
        print()
        print("核心原则: 每一层不能偷偷替下一层做决定")
        print("  L1 FACTS → 原始事实, 无判断")
        print("  RELATIONS → 原典关系是否成立 (CONFIRMED/CANDIDATE/REJECTED)")
        print("  COMBINATION → 关系组合是否成立 (CONFIRMED/QUALIFIED/CANDIDATE)")
        print("  CONCLUSION → 最终结论 (CONFIRMED/CANDIDATE/UNRESOLVED)")

        self._step1_l1_facts(year, month, day, hour)
        self._step2_relations()
        self._step3_combinations()
        self._step4_conclusions()
        self._step5_output()

        return self.state

    # --------------------------------------------------------
    # Step 1: L1 Facts
    # --------------------------------------------------------

    def _step1_l1_facts(self, year: str, month: str, day: str, hour: str):
        print("\n" + "─" * 100)
        print("Step 1: L1 FACTS (原始事实层 — 无判断)")
        print("─" * 100)

        l1 = self.state.l1
        l1.pillars = {"年": year, "月": month, "日": day, "时": hour}
        l1.day_master = day[0]  # 乙木
        l1.month_branch = month[1]  # 戌

        # 十二长生 (乙木阴干逆行)
        l1.growth_stages = {"亥": "死", "戌": "墓", "未": "养", "午": "长生"}

        # 藏干
        l1.hidden_stems = {
            "亥": [("壬", "本气"), ("甲", "中气")],
            "戌": [("戊", "本气"), ("辛", "中气"), ("丁", "余气")],
            "未": [("己", "本气"), ("丁", "中气"), ("乙", "余气")],
            "午": [("丁", "本气"), ("己", "中气")],
        }

        # 十神 (乙木日主)
        l1.ten_gods = {
            "癸": "偏印", "壬": "正印", "甲": "劫财", "乙": "比肩/日主",
            "丁": "食神", "戊": "正财", "己": "偏财", "辛": "七杀",
        }

        # 五行分布 (天干+地支本气, 仅作事实展示)
        l1.five_elements = {"水": 4, "木": 1, "火": 1, "土": 2, "金": 0}

        # 空亡
        l1.kong_wang = ["子", "丑"]

        print(f"  日主: {l1.day_master} | 月令: {l1.month_branch}")
        print(f"  十二长生: 亥={l1.growth_stages['亥']}, 戌={l1.growth_stages['戌']}, "
              f"未={l1.growth_stages['未']}, 午={l1.growth_stages['午']}")
        print(f"  藏干: 亥(壬甲), 戌(戊辛丁), 未(己丁乙), 午(丁己)")
        print(f"  五行分布(天干+地支本气): 水4 木1 火1 土2 金0 [仅事实展示, 不用于判断]")
        print(f"  空亡: 子丑 [四支不逢空]")
        print(f"  [L1 ONLY] 此层无任何判断, 全部为原始事实")

    # --------------------------------------------------------
    # Step 2: Relations (原典关系是否成立)
    # --------------------------------------------------------

    def _step2_relations(self):
        print("\n" + "─" * 100)
        print("Step 2: RELATIONS (原典关系是否成立 — CONFIRMED/CANDIDATE/REJECTED)")
        print("─" * 100)

        rel = self.state.relations

        # === 通根判断 (逐支, 严格分层) ===
        print(f"\n  【通根关系】(R-001: 藏干对应日主 → 通根)")
        print(f"  原典: 《子平真诠》'天干通根, 不仅禄旺为美, 长生、余气、墓库皆其根也。'")
        print()

        # 未中乙
        print(f"  1. 未中乙:")
        print(f"     L1事实: 未藏己丁乙, 乙=日主同干")
        print(f"     原典: 余气→根之轻")
        print(f"     判断: 同干通根, 条件明确满足")
        print(f"     [RELATION] 通根 = CONFIRMED | 根质 = ROOT_LIGHT")
        rel.tonggen_per_branch["未"] = RelationEntry(
            relation_id="REL-TONGGEN-WEI",
            description="未中乙 → 乙木通根",
            l1_evidence="未藏己丁乙, 乙与日主乙木同干",
            source_basis="《子平真诠》余气→根之轻",
            state=ConfirmationState.CONFIRMED,
            root_quality=RootQuality.ROOT_LIGHT,
            reason="同干通根, 余气根→根之轻",
        )

        # 亥中甲
        print(f"\n  2. 亥中甲:")
        print(f"     L1事实: 亥藏壬甲, 甲=阳木, 乙=阴木 → 同五行(木)但异天干(甲≠乙)")
        print(f"     原典: '甲乙木见亥辰未亦为有根' — 但'见亥'更可能指甲木见亥(亥为甲木长生)")
        print(f"     原典: 乙木在亥的十二长生 = 死 (不是长生/禄/旺)")
        print(f"     判断: 同五行但异天干, 原典未明确授权乙木见亥甲为通根")
        print(f"     [RELATION] 通根 = CANDIDATE | 根质 = ROOT_UNRESOLVED")
        rel.tonggen_per_branch["亥"] = RelationEntry(
            relation_id="REL-TONGGEN-HAI",
            description="亥中甲 → 乙木通根(同五行异天干)",
            l1_evidence="亥藏壬甲, 甲=阳木, 乙=阴木, 同五行但异天干; 乙木在亥=死",
            source_basis="《子平真诠》'甲乙木见亥辰未亦为有根' — 但'见亥'更可能指甲木",
            state=ConfirmationState.CANDIDATE,
            root_quality=RootQuality.ROOT_UNRESOLVED,
            reason="同五行(木)但异天干(甲≠乙), 原典未明确授权乙木见亥甲为通根",
        )

        # 午
        print(f"\n  3. 午:")
        print(f"     L1事实: 午藏丁己, 无木; 乙木在午的十二长生 = 长生 ★")
        print(f"     关键锁死: 虽然十二长生为长生, 但午中没有乙")
        print(f"     [FORBIDDEN] 不能凭长生状态制造藏干根 (禁止 长生→自动根重)")
        print(f"     [RELATION] 通根 = REJECTED | 根质 = ROOT_NONE")
        rel.tonggen_per_branch["午"] = RelationEntry(
            relation_id="REL-TONGGEN-WU",
            description="午 → 乙木通根",
            l1_evidence="午藏丁己, 无木类藏干; 乙木在午=长生(仅L1事实)",
            source_basis="通根需要藏干中有日主同类, 午中无木",
            state=ConfirmationState.REJECTED,
            root_quality=RootQuality.ROOT_NONE,
            reason="午中无木类藏干; 虽乙木在午为长生, 但不能凭长生状态制造藏干根",
        )

        # 戌
        print(f"\n  4. 戌:")
        print(f"     L1事实: 戌藏戊辛丁, 无木; 乙木在戌=墓")
        print(f"     [RELATION] 通根 = REJECTED | 根质 = ROOT_NONE")
        rel.tonggen_per_branch["戌"] = RelationEntry(
            relation_id="REL-TONGGEN-XU",
            description="戌 → 乙木通根",
            l1_evidence="戌藏戊辛丁, 无木类藏干",
            source_basis="通根需要藏干中有日主同类, 戌中无木",
            state=ConfirmationState.REJECTED,
            root_quality=RootQuality.ROOT_NONE,
            reason="戌中无木类藏干",
        )

        # === 十神关系 (仅标记关系存在, 不判断强弱) ===
        print(f"\n  【十神关系】(仅标记关系存在, 不直接推强弱)")

        rel.bijie_relation = RelationEntry(
            relation_id="REL-BIJIE",
            description="比劫扶助",
            l1_evidence="亥中甲(劫财)、未中乙(比肩) — 均为藏干, 天干无比劫",
            source_basis="《子平真诠》比劫如朋友之相扶",
            state=ConfirmationState.CONFIRMED,
            reason="比劫存在(藏干), 但天干无比劫",
        )
        print(f"    比劫: CONFIRMED (亥中甲劫财、未中乙比肩, 均为藏干)")

        rel.yin_relation = RelationEntry(
            relation_id="REL-YIN",
            description="印绶生扶",
            l1_evidence="天干壬(正印)×2、癸(偏印); 地支亥本气水; 印绶非常旺",
            source_basis="《渊海子平》木赖水生; 《子平真诠》印绶喜其生身",
            state=ConfirmationState.CONFIRMED,
            reason="印绶存在且旺(天干3水+亥本气水); 带水多木漂qualifier",
        )
        print(f"    印绶: CONFIRMED (壬×2+癸, 天干3水+亥本气水, 印绶旺; 带水多木漂qualifier)")

        rel.guansha_relation = RelationEntry(
            relation_id="REL-GUANSHA",
            description="官杀克制",
            l1_evidence="戌中辛(七杀) — 仅藏干",
            source_basis="《渊海子平》七杀克身; 但官杀作用关系≠身弱结果",
            state=ConfirmationState.CONFIRMED,
            reason="官杀存在(戌中辛七杀, 藏干); 作用关系≠身弱结果",
        )
        print(f"    官杀: CONFIRMED (戌中辛七杀, 仅藏干; 作用关系≠身弱结果)")

        rel.shishang_relation = RelationEntry(
            relation_id="REL-SHISHANG",
            description="食伤泄/盗气",
            l1_evidence="丁(食神)×3 — 戌未午藏干",
            source_basis="《渊海子平》食伤名盗气; 但泄身需要过重条件",
            state=ConfirmationState.CONFIRMED,
            reason="食伤存在(丁×3); 盗气关系有原典依据, 但泄身需要过重条件",
        )
        print(f"    食伤: CONFIRMED (丁食神×3; 盗气有原典依据, 泄身需过重条件)")

        rel.cai_relation = RelationEntry(
            relation_id="REL-CAI",
            description="财耗/我克",
            l1_evidence="戊(正财)、己(偏财)×2 — 戌未午藏干",
            source_basis="《渊海子平》财为我克; 但财多→身弱不授权(财多身健方为贵反例)",
            state=ConfirmationState.CONFIRMED,
            reason="财存在(戊己×3); 财→耗为RELATION_FACT, 财多→身弱不授权",
        )
        print(f"    财: CONFIRMED (戊正财、己偏财×2; 财→耗为关系事实, 财多→身弱不授权)")

        # 结构关系
        rel.structure_relations = ["亥未半合木局", "午戌半合火局"]
        print(f"    结构: 亥未半合木、午戌半合火; 无冲/刑/会/破害")

    # --------------------------------------------------------
    # Step 3: Combinations (关系组合是否成立)
    # --------------------------------------------------------

    def _step3_combinations(self):
        print("\n" + "─" * 100)
        print("Step 3: COMBINATIONS (关系组合是否成立 — CONFIRMED/QUALIFIED/CANDIDATE)")
        print("─" * 100)

        comb = self.state.combinations
        rel = self.state.relations

        # === C-001: 党众 ===
        print(f"\n  【C-001: 比劫+印绶+通根扶助 → 党众】")
        print(f"  原典: 《子平真诠》'比劫印绶通根扶助为党众'")
        print(f"  三要素检查:")
        print(f"    1. 比劫扶助: CONFIRMED (亥中甲劫财、未中乙比肩, 均为藏干)")
        print(f"    2. 印绶生扶: CONFIRMED (壬×2+癸, 印绶旺; 带水多木漂qualifier)")
        print(f"    3. 通根: CONFIRMED (未中乙, ROOT_LIGHT根之轻) — 但亥中甲为CANDIDATE")
        print()
        print(f"  关键语义修正:")
        print(f"    通根只有未中乙CONFIRMED(根之轻), 亥中甲仍为CANDIDATE")
        print(f"    因此党众不能简单=TRUE, 应为QUALIFIED(基本成立但带qualifier)")
        print(f"    [FORBIDDEN] 不能把 dangzhong=TRUE 当成最终事实")
        print()
        print(f"  [COMBINATION] 党众 = QUALIFIED")
        print(f"    qualifiers: [根仅ROOT_LIGHT(根之轻), 亥中甲通根CANDIDATE, 印过旺水多木漂]")

        comb.dangzhong = CombinationEntry(
            combo_id="COMBO-DANGZHONG",
            description="比劫+印绶+通根扶助 → 党众",
            required_relations=["比劫扶助", "印绶生扶", "通根"],
            relation_states={
                "比劫扶助": "CONFIRMED(藏干)",
                "印绶生扶": "CONFIRMED(旺, 带水多木漂)",
                "通根": "CONFIRMED(未中乙ROOT_LIGHT) + CANDIDATE(亥中甲)",
            },
            state=CombinationState.QUALIFIED,
            qualifiers=[
                "根仅ROOT_LIGHT(根之轻, 未中乙余气根)",
                "亥中甲通根为CANDIDATE(同五行异天干, 原典未明确授权)",
                "印过旺可能反作用(水多木漂)",
            ],
            reason="三要素基本满足, 但通根仅根之轻且亥中甲为CANDIDATE, 印过旺带水多木漂qualifier",
        )

        # === C-002: 助寡 ===
        print(f"\n  【C-002: 比劫/印绶/通根不足 → 助寡】")
        print(f"  判断: 党众=QUALIFIED(基本成立), 因此不构成助寡")
        print(f"  [COMBINATION] 助寡 = NOT_ESTABLISHED")
        comb.zhugua = CombinationEntry(
            combo_id="COMBO-ZHUGUA",
            description="比劫/印绶/通根不足 → 助寡",
            required_relations=["比劫不足", "印绶不足", "通根不足"],
            relation_states={"党众": "QUALIFIED(基本成立)"},
            state=CombinationState.NOT_ESTABLISHED,
            reason="党众基本成立, 不构成助寡",
        )

        # === C-004: 克泄耗组合 ===
        print(f"\n  【C-004: 生扶组合+克泄耗组合 → 最终强弱】")
        print(f"  原典状态: INSUFFICIENT_SOURCE — 原典没有系统的组合规则")
        print(f"  本例克泄耗: 官杀(辛)、食伤(丁×3)、财(戊己×3)均存在")
        print(f"  [FORBIDDEN] support_score - opposition_score = final_strength")
        print(f"  [COMBINATION] 克泄耗组合 = UNRESOLVED (MUST_BE_UNRESOLVED)")
        comb.kexiehao_combo = CombinationEntry(
            combo_id="COMBO-KEXIEHAO",
            description="生扶组合+克泄耗组合 → 最终强弱",
            required_relations=["生扶组合", "克泄耗组合"],
            relation_states={"生扶": "QUALIFIED", "克泄耗": "CONFIRMED(官杀食伤财均存在)"},
            state=CombinationState.UNRESOLVED,
            reason="C-004 INSUFFICIENT_SOURCE: 原典没有系统的生扶+克泄耗组合规则",
        )

    # --------------------------------------------------------
    # Step 4: Conclusions (最终结论)
    # --------------------------------------------------------

    def _step4_conclusions(self):
        print("\n" + "─" * 100)
        print("Step 4: CONCLUSIONS (最终结论 — CONFIRMED/CANDIDATE/UNRESOLVED)")
        print("─" * 100)

        conc = self.state.conclusions
        comb = self.state.combinations

        # === 旺衰 ===
        print(f"\n  【旺衰结论】")
        print(f"  基础: 月令戌月, 戌月土旺木囚, 乙木失时")
        print(f"  原典: 《子平真诠》'得时为旺, 失时为衰'")
        print(f"  [CONCLUSION] 旺衰 = 衰 (CONFIRMED)")
        conc.wangshuai = ConclusionEntry(
            conclusion_id="CONC-WANGSHUAI",
            description="旺衰结论",
            basis="月令戌月, 乙木失时=衰",
            state=ConclusionState.CONFIRMED,
            qualifiers=["旺衰维度独立于强弱维度"],
        )

        # === 强弱 ===
        print(f"\n  【强弱结论】★关键")
        print(f"  输入:")
        print(f"    1. 党众组合 = QUALIFIED (基本成立, 但带3个qualifier)")
        print(f"       - 根仅ROOT_LIGHT(根之轻)")
        print(f"       - 亥中甲通根CANDIDATE")
        print(f"       - 印过旺水多木漂")
        print(f"    2. 克泄耗组合 = UNRESOLVED (C-004 MUST_BE_UNRESOLVED)")
        print(f"    3. 特殊格局 = rejected (不构成从格/专旺/化格)")
        print()
        print(f"  判断逻辑:")
        print(f"    - 党众=QUALIFIED → 强弱基线 = CANDIDATE强 (不是CONFIRMED强)")
        print(f"    - 但克泄耗组合UNRESOLVED → 无法确定官杀/食伤/财对最终强弱的影响")
        print(f"    - 且水多木漂反作用程度未授权量化")
        print(f"    - 且亥中甲通根CANDIDATE, 影响根质量判断完整性")
        print(f"    - 且党众本身=QUALIFIED(非CONFIRMED)")
        print()
        print(f"  [CONCLUSION] 强弱 = UNRESOLVED")
        print(f"  [核心原则] 宁愿输出UNRESOLVED, 也不制造不存在于原典的因果规则")
        print(f"  [关键修正] 不再输出 党众=TRUE → 强弱基线=强 → 最终UNRESOLVED")
        print(f"    而是: 党众=QUALIFIED → 强弱基线=CANDIDATE → 最终UNRESOLVED")

        conc.qiangruo = ConclusionEntry(
            conclusion_id="CONC-QIANGRUO",
            description="强弱结论",
            basis="党众=QUALIFIED(非CONFIRMED); 克泄耗组合=UNRESOLVED; 水多木漂程度未授权; 亥中甲通根CANDIDATE",
            state=ConclusionState.UNRESOLVED,
            unresolved_reasons=[
                "克泄耗组合无法计算 (C-004 INSUFFICIENT_SOURCE, MUST_BE_UNRESOLVED)",
                "党众=QUALIFIED(非CONFIRMED): 根仅ROOT_LIGHT, 亥中甲CANDIDATE, 印过旺水多木漂",
                "水多木漂(印过旺反作用)的程度未被原典授权量化",
                "亥中甲同五行(木)异天干(甲≠乙)通根存疑, 原典未明确授权",
                "党众→强带'大致'qualifier, 非绝对规则",
            ],
            qualifiers=[
                "强弱基线=CANDIDATE强(基于党众=QUALIFIED, 非CONFIRMED)",
                "旺衰=衰与强弱=UNRESOLVED二维独立",
            ],
        )

        # === 特殊格局 ===
        print(f"\n  【特殊格局结论】")
        print(f"  从杀格: 需要'四柱皆煞而日主无根' → 官杀仅戌中辛(藏干), 日主有根(未中乙) → 不构成")
        print(f"  从财/从儿格: 需要日主无根 → 日主有根(未中乙) → 不构成")
        print(f"  专旺格: 需要成方/成局 → 无完整三会方/三合局 → 不构成")
        print(f"  化气格: 需要化神得令得地 → 无明显天干五合成化 → 不构成")
        print(f"  [CONCLUSION] 特殊格局 = rejected (退回普通强弱路径)")
        conc.special_pattern = ConclusionEntry(
            conclusion_id="CONC-SPECIAL-PATTERN",
            description="特殊格局结论",
            basis="从杀/从财/从儿/专旺/化气均不满足成格条件",
            state=ConclusionState.CONFIRMED,
            qualifiers=["特殊格局=rejected, 退回普通强弱路径"],
        )

        # Modifiers
        self.state.modifiers = [
            "水多木漂(印过旺反作用, R-005 qualifier) — 仅作qualifier, 不直接改强弱",
            "全局水势旺(天干3水+亥本气水) — 仅作qualifier",
            "全局土有根(戌未本气) — 仅作qualifier",
            "全局火有势(午本气+丁×3) — 仅作qualifier",
        ]
        self.state.seasonal_remedy = {
            "day_master": "乙木",
            "month": "戌月",
            "primary_candidate": "丙火(待原典核验)",
            "assistant_candidate": ["癸水(待原典核验)"],
            "status": "CANDIDATE (需回穷通宝鉴原典验证)",
            "note": "调候独立维度, 不参与强弱判断",
        }

    # --------------------------------------------------------
    # Step 5: Output
    # --------------------------------------------------------

    def _step5_output(self):
        s = self.state
        print("\n" + "=" * 100)
        print("最终 Hardened Canonical State (语义修正后)")
        print("=" * 100)

        print(f"""
  命例: 癸亥 壬戌 乙未 壬午 (1983)

  ┌─ L1 FACTS (原始事实, 无判断)
  │   日主: 乙木 | 月令: 戌月
  │   十二长生: 亥=死, 戌=墓, 未=养, 午=长生
  │   藏干: 亥(壬甲), 戌(戊辛丁), 未(己丁乙), 午(丁己)
  │   五行分布: 水4 木1 火1 土2 金0 [仅事实展示]
  │
  ├─ RELATIONS (原典关系是否成立)
  │   通根:
  │     未中乙: CONFIRMED | ROOT_LIGHT (同干, 余气根→根之轻)
  │     亥中甲: CANDIDATE | ROOT_UNRESOLVED (同五行木异天干甲≠乙, 原典未明确授权)
  │     午:     REJECTED | ROOT_NONE (午中无乙, 虽长生但不能凭长生制造根)
  │     戌:     REJECTED | ROOT_NONE (戌中无木)
  │   十神关系:
  │     比劫: CONFIRMED (藏干, 天干无比劫)
  │     印绶: CONFIRMED (旺, 带水多木漂qualifier)
  │     官杀: CONFIRMED (戌中辛, 仅藏干; 作用关系≠身弱结果)
  │     食伤: CONFIRMED (丁×3; 盗气有原典依据, 泄身需过重条件)
  │     财:   CONFIRMED (戊己×3; 财→耗为关系事实, 财多→身弱不授权)
  │   结构: 亥未半合木、午戌半合火; 无冲/刑/会/破害
  │
  ├─ COMBINATIONS (关系组合是否成立)
  │   党众: QUALIFIED ★ (不再是TRUE)
  │     三要素: 比劫CONFIRMED + 印绶CONFIRMED(旺) + 通根CONFIRMED(未中乙ROOT_LIGHT)
  │     qualifiers: [根仅ROOT_LIGHT, 亥中甲通根CANDIDATE, 印过旺水多木漂]
  │   助寡: NOT_ESTABLISHED
  │   克泄耗组合: UNRESOLVED (C-004 MUST_BE_UNRESOLVED)
  │
  ├─ CONCLUSIONS (最终结论)
  │   旺衰: 衰 (CONFIRMED) — 戌月木囚失时
  │   强弱: UNRESOLVED ★
  │     基线: CANDIDATE强 (基于党众=QUALIFIED, 非CONFIRMED)
  │     unresolved_reasons:
  │       1. 克泄耗组合无法计算 (C-004)
  │       2. 党众=QUALIFIED(非CONFIRMED): 根仅ROOT_LIGHT, 亥中甲CANDIDATE, 水多木漂
  │       3. 水多木漂反作用程度未授权量化
  │       4. 亥中甲同五行异天干通根存疑
  │       5. 党众→强带'大致'qualifier
  │   特殊格局: rejected (退回普通路径)
  │
  └─ MODIFIERS / 独立维度
      qualifiers: [水多木漂, 全局水势旺, 全局土有根, 全局火有势]
      seasonal_remedy: 乙木戌月, 丙火(候选), 癸水(候选) — 独立维度, 不参与强弱
""")

        print("=" * 100)
        print("语义修正关键点:")
        print("  1. 党众: TRUE → QUALIFIED (因为通根仅根之轻, 亥中甲CANDIDATE, 印过旺)")
        print("  2. 强弱基线: 强 → CANDIDATE强 (基于党众=QUALIFIED, 非CONFIRMED)")
        print("  3. root_state增加ROOT_UNRESOLVED (亥中甲)")
        print("  4. 每一层严格区分: RELATION(CONFIRMED/CANDIDATE) → COMBINATION(QUALIFIED) → CONCLUSION(UNRESOLVED)")
        print("  5. 不再把 dangzhong=TRUE 当成最终事实触发 党众→强")
        print("=" * 100)
        print("P6.1.1 Semantic State Hardening 完成.")
        print("下一步: P6.2 Assertion Precondition Engine")
        print("  第一条: '财星透干, 逢流年合之, 主进财.'")
        print("=" * 100)


# ============================================================
# 主执行
# ============================================================

def main():
    resolver = HardenedResolver()
    state = resolver.resolve("癸亥", "壬戌", "乙未", "壬午")
    return state


if __name__ == "__main__":
    main()
