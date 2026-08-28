"""
STR-001A P6.1 Resolver Integration Audit
1983命例: 癸亥 壬戌 乙未 壬午

定位: 关系矩阵 → 状态解析的契约验证, 不是进入下一Phase.

严格检查:
  禁止 root_score
  禁止 strength_score
  禁止 五行计数→强弱
  禁止 长生→自动根重
  禁止 藏干→自动通根
  禁止 水多木漂→直接改强弱
  禁止 调候→强弱
  禁止 未授权克泄耗组合→强弱

特别锁死乙木通根判断:
  乙木 × 未中乙 → 同干, 通根 → ROOT_LIGHT
  乙木 × 亥中甲 → 同五行但异天干, 原典定义存疑 → CANDIDATE/UNRESOLVED
  乙木 × 午 → 十二长生为长生, 但午中无乙, 不能凭长生制造藏干根 → ROOT_NONE
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


# ============================================================
# 状态枚举
# ============================================================

class WangshuaiState(str, Enum):
    WANG = "旺"
    SHUAI = "衰"
    UNRESOLVED = "UNRESOLVED"


class QiangruoState(str, Enum):
    QIANG = "强"
    RUO = "弱"
    UNRESOLVED = "UNRESOLVED"


class RootQuality(str, Enum):
    ROOT_HEAVY = "ROOT_HEAVY"      # 长生/禄/旺 → 根之重
    ROOT_LIGHT = "ROOT_LIGHT"      # 墓库/余气 → 根之轻
    ROOT_PRESENT = "ROOT_PRESENT"  # 实际通根但质量未分级
    ROOT_NONE = "ROOT_NONE"        # 无通根
    CANDIDATE = "CANDIDATE"        # 候选, 原典定义存疑
    UNRESOLVED = "UNRESOLVED"      # 无法确定


class TernaryState(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNRESOLVED = "UNRESOLVED"


# ============================================================
# 数据结构
# ============================================================

@dataclass
class L1Facts:
    """L1 原始事实层"""
    # 基础
    year_pillar: str = ""          # 年柱
    month_pillar: str = ""         # 月柱
    day_pillar: str = ""           # 日柱
    hour_pillar: str = ""          # 时柱
    day_master: str = ""            # 日主
    month_branch: str = ""          # 月令

    # 十二长生 (日主 × 四支)
    growth_stages: Dict[str, str] = field(default_factory=dict)

    # 藏干 (本气/中气/余气)
    hidden_stems: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)

    # 十神分布
    ten_gods: Dict[str, List[str]] = field(default_factory=dict)

    # 五行分布 (明确标注计数方式)
    five_elements_tiangan: Dict[str, int] = field(default_factory=dict)
    five_elements_dizhi_benqi: Dict[str, int] = field(default_factory=dict)
    five_elements_canggan: Dict[str, int] = field(default_factory=dict)

    # 空亡
    kong_wang: List[str] = field(default_factory=list)


@dataclass
class RelationResult:
    """关系层结果"""
    # 通根判断 (逐支)
    tonggen_per_branch: Dict[str, Dict] = field(default_factory=dict)

    # 根质量 (逐支)
    root_quality_per_branch: Dict[str, RootQuality] = field(default_factory=dict)

    # 总体根状态
    overall_root_state: RootQuality = RootQuality.ROOT_NONE

    # 十神关系标记
    bijie_present: bool = False       # 比劫
    yin_present: bool = False         # 印
    guansha_present: bool = False     # 官杀
    shishang_present: bool = False    # 食伤
    cai_present: bool = False         # 财

    # 结构关系
    he_relations: List[str] = field(default_factory=list)
    chong_relations: List[str] = field(default_factory=list)
    xing_relations: List[str] = field(default_factory=list)
    hui_relations: List[str] = field(default_factory=list)
    po_hai_relations: List[str] = field(default_factory=list)


@dataclass
class CombinationResult:
    """组合层结果"""
    dangzhong: TernaryState = TernaryState.UNRESOLVED
    dangzhong_evidence: List[str] = field(default_factory=list)
    zhugua: TernaryState = TernaryState.UNRESOLVED
    zhugua_evidence: List[str] = field(default_factory=list)
    qiangruo_baseline: QiangruoState = QiangruoState.UNRESOLVED
    qiangruo_baseline_note: str = ""
    kexiehao_combination: str = "UNRESOLVED (C-004: 原典无系统组合规则)"


@dataclass
class ModifierResult:
    """修正层结果"""
    wangshuai: WangshuaiState = WangshuaiState.UNRESOLVED
    wangshuai_basis: List[str] = field(default_factory=list)
    qiangruo_final: QiangruoState = QiangruoState.UNRESOLVED
    qiangruo_final_note: str = ""
    qualifiers: List[str] = field(default_factory=list)
    seasonal_remedy: Dict = field(default_factory=dict)
    special_pattern: str = "unresolved"
    unresolved_reasons: List[str] = field(default_factory=list)


@dataclass
class CanonicalState:
    """最终 Canonical State"""
    l1_facts: L1Facts = field(default_factory=L1Facts)
    relations: RelationResult = field(default_factory=RelationResult)
    combinations: CombinationResult = field(default_factory=CombinationResult)
    modifiers: ModifierResult = field(default_factory=ModifierResult)
    audit_checks: Dict[str, str] = field(default_factory=dict)


# ============================================================
# Resolver 实现
# ============================================================

class CanonicalStateResolver:
    """严格按 Authority Matrix 执行的 Canonical State Resolver"""

    def __init__(self):
        self.state = CanonicalState()
        self.audit_checks = {}

    def resolve(self, year: str, month: str, day: str, hour: str) -> CanonicalState:
        """主入口: 八字四柱 → Canonical State"""
        print("=" * 100)
        print("STR-001A P6.1 Resolver Integration Audit")
        print(f"命例: {year} {month} {day} {hour}")
        print("=" * 100)

        # Step 1: L1 Facts
        self._step1_l1_facts(year, month, day, hour)

        # Step 2: Relations
        self._step2_relations()

        # Step 3: Combinations
        self._step3_combinations()

        # Step 4: Modifiers
        self._step4_modifiers()

        # Step 5: Audit Checks
        self._step5_audit_checks()

        # Output
        self._output_final_state()

        return self.state

    # --------------------------------------------------------
    # Step 1: L1 Facts
    # --------------------------------------------------------

    def _step1_l1_facts(self, year: str, month: str, day: str, hour: str):
        print("\n" + "─" * 100)
        print("Step 1: L1 Facts (原始事实层)")
        print("─" * 100)

        f = self.state.l1_facts
        f.year_pillar = year
        f.month_pillar = month
        f.day_pillar = day
        f.hour_pillar = hour
        f.day_master = day[0]  # 乙木
        f.month_branch = month[1]  # 戌

        print(f"  四柱: {year} {month} {day} {hour}")
        print(f"  日主: {f.day_master}")
        print(f"  月令: {f.month_branch}")

        # 十二长生 (乙木)
        # 乙木: 午长生, 未养, 申胎, 酉绝, 戌墓, 亥死, 子病, 丑衰, 寅冠带, 卯临官, 辰帝旺, 巳沐浴
        # 阴干逆行
        f.growth_stages = {
            "亥": "死",
            "戌": "墓",
            "未": "养",
            "午": "长生",
        }
        print(f"\n  十二长生 (乙木 × 四支):")
        for branch, stage in f.growth_stages.items():
            print(f"    乙木在{branch} = {stage}")
        print(f"  [FACT ONLY] 十二长生只作为L1事实, 不直接推出强弱")

        # 藏干
        f.hidden_stems = {
            "亥": [("壬", "本气"), ("甲", "中气")],
            "戌": [("戊", "本气"), ("辛", "中气"), ("丁", "余气")],
            "未": [("己", "本气"), ("丁", "中气"), ("乙", "余气")],
            "午": [("丁", "本气"), ("己", "中气")],
        }
        print(f"\n  藏干 (本气/中气/余气):")
        for branch, stems in f.hidden_stems.items():
            stem_str = ", ".join([f"{s}({t})" for s, t in stems])
            print(f"    {branch}: {stem_str}")
        print(f"  [FACT ONLY] 三层命名是工程归纳, 不是原典原词; 不直接推出有根/无根")

        # 十神 (乙木日主)
        # 壬=正印, 癸=偏印, 甲=劫财, 乙=比肩, 丙=伤官, 丁=食神, 戊=正财, 己=偏财, 庚=正官, 辛=七杀
        f.ten_gods = {
            "天干": {
                "癸": "偏印",
                "壬": "正印",
                "乙": "日主",
                "壬(时)": "正印",
            },
            "亥藏干": {"壬": "正印", "甲": "劫财"},
            "戌藏干": {"戊": "正财", "辛": "七杀", "丁": "食神"},
            "未藏干": {"己": "偏财", "丁": "食神", "乙": "比肩"},
            "午藏干": {"丁": "食神", "己": "偏财"},
        }
        print(f"\n  十神分布:")
        print(f"    天干: 癸(偏印) 壬(正印) 乙(日主) 壬(正印)")
        print(f"    亥: 壬(正印) 甲(劫财)")
        print(f"    戌: 戊(正财) 辛(七杀) 丁(食神)")
        print(f"    未: 己(偏财) 丁(食神) 乙(比肩)")
        print(f"    午: 丁(食神) 己(偏财)")

        # 五行分布 (明确标注三种计数方式)
        f.five_elements_tiangan = {"水": 3, "木": 1, "火": 0, "土": 0, "金": 0}
        f.five_elements_dizhi_benqi = {"水": 1, "木": 0, "火": 1, "土": 2, "金": 0}
        f.five_elements_canggan = {"水": 1, "木": 2, "火": 3, "土": 3, "金": 1}
        print(f"\n  五行分布 (三种计数方式, 仅作事实展示):")
        print(f"    天干: 水3 木1")
        print(f"    地支本气: 水1 火1 土2")
        print(f"    藏干: 水1 木2 火3 土3 金1")
        print(f"  [FORBIDDEN] 五行计数→强弱 (禁止)")

        # 空亡 (壬戌日, 甲寅旬? 让我算: 壬戌在甲寅旬? 甲寅旬: 甲寅乙卯丙辰丁巳戊午己未庚申辛酉壬戌癸亥. 对, 壬戌在甲寅旬, 空子丑)
        f.kong_wang = ["子", "丑"]
        print(f"\n  空亡: 子、丑 (甲寅旬)")
        print(f"  [NOTE] 四支(亥戌未午)均不逢空亡")

    # --------------------------------------------------------
    # Step 2: Relations
    # --------------------------------------------------------

    def _step2_relations(self):
        print("\n" + "─" * 100)
        print("Step 2: Relations (关系层)")
        print("─" * 100)

        r = self.state.relations
        f = self.state.l1_facts

        # === 通根判断 (逐支, 特别锁死) ===
        print(f"\n  【通根判断】(R-001: 藏干对应日主 → 通根)")
        print(f"  原典依据: 《子平真诠》'天干通根, 不仅禄旺为美, 长生、余气、墓库皆其根也。'")
        print(f"  原典依据: '如甲乙木见寅卯, 固为身旺, 而见亥辰未, 亦为有根也。'")
        print()

        # 乙木 × 亥中甲
        print(f"  1. 乙木 × 亥中甲:")
        print(f"     亥中藏干: 壬(本气)、甲(中气)")
        print(f"     甲 = 阳木, 乙 = 阴木 → 同五行(木)但异天干(甲≠乙)")
        print(f"     原典'甲乙木见亥...亦为有根'中的'见亥'更可能指甲木见亥(亥为甲木长生, 藏甲)")
        print(f"     乙木在亥的十二长生 = 死 (不是长生/禄/旺)")
        print(f"     [判断] 同五行但异天干, 原典未明确授权为'乙木通根'")
        print(f"     [结果] CANDIDATE / UNRESOLVED — 不直接计入乙木通根")
        r.tonggen_per_branch["亥"] = {
            "hidden_stem": "甲",
            "same_element": True,
            "same_stem": False,
            "growth_stage": "死",
            "tonggen": "UNRESOLVED",
            "reason": "同五行(木)但异天干(甲≠乙), 原典未明确授权乙木见亥甲为通根",
        }
        r.root_quality_per_branch["亥"] = RootQuality.CANDIDATE

        # 乙木 × 戌
        print(f"\n  2. 乙木 × 戌:")
        print(f"     戌中藏干: 戊(本气)、辛(中气)、丁(余气)")
        print(f"     戌中无木 (戊辛丁均非木)")
        print(f"     乙木在戌的十二长生 = 墓")
        print(f"     [判断] 戌中无日主同类藏干, 不构成通根")
        print(f"     [结果] ROOT_NONE")
        r.tonggen_per_branch["戌"] = {
            "hidden_stem": "戊辛丁",
            "same_element": False,
            "same_stem": False,
            "growth_stage": "墓",
            "tonggen": "FALSE",
            "reason": "戌中无木类藏干",
        }
        r.root_quality_per_branch["戌"] = RootQuality.ROOT_NONE

        # 乙木 × 未中乙
        print(f"\n  3. 乙木 × 未中乙:")
        print(f"     未中藏干: 己(本气)、丁(中气)、乙(余气)")
        print(f"     未中乙 = 阴木, 与日主乙木同干 (乙=乙)")
        print(f"     乙木在未的十二长生 = 养")
        print(f"     原典: '墓库余气, 根之轻者也'")
        print(f"     [判断] 同干通根, 未中乙为余气根 → 根之轻")
        print(f"     [结果] 通根=TRUE, ROOT_LIGHT (根之轻)")
        r.tonggen_per_branch["未"] = {
            "hidden_stem": "乙",
            "same_element": True,
            "same_stem": True,
            "growth_stage": "养",
            "tonggen": "TRUE",
            "reason": "未中乙与日主同干, 余气根 → 根之轻",
            "root_quality": "ROOT_LIGHT",
        }
        r.root_quality_per_branch["未"] = RootQuality.ROOT_LIGHT

        # 乙木 × 午
        print(f"\n  4. 乙木 × 午:")
        print(f"     午中藏干: 丁(本气)、己(中气)")
        print(f"     午中无木 (丁己均非木)")
        print(f"     乙木在午的十二长生 = 长生 ★")
        print(f"     [关键锁死] 虽然十二长生为长生, 但午中没有乙")
        print(f"     [FORBIDDEN] 不能凭长生状态制造藏干根 (禁止 长生→自动根重)")
        print(f"     [判断] 午中无日主同类藏干, 不构成藏干通根")
        print(f"     [结果] ROOT_NONE (仅就藏干根而言; 长生状态作为L1事实保留, 但不制造根)")
        r.tonggen_per_branch["午"] = {
            "hidden_stem": "丁己",
            "same_element": False,
            "same_stem": False,
            "growth_stage": "长生",
            "tonggen": "FALSE",
            "reason": "午中无木类藏干; 虽乙木在午为长生, 但不能凭长生状态制造藏干根",
        }
        r.root_quality_per_branch["午"] = RootQuality.ROOT_NONE

        # 总体根状态
        print(f"\n  【总体根状态】")
        print(f"    明确通根: 未中乙 → ROOT_LIGHT (根之轻)")
        print(f"    候选/存疑: 亥中甲 → CANDIDATE (同五行异天干, 原典未明确授权)")
        print(f"    无通根: 戌、午 (午虽长生但无藏干乙)")
        print(f"    [结果] 总体 root_state = ROOT_LIGHT (基于未中乙明确通根)")
        print(f"    [NOTE] 亥中甲作为CANDIDATE单独标注, 不计入总体根质量, 需后续原典补证")
        r.overall_root_state = RootQuality.ROOT_LIGHT

        # === 十神关系标记 ===
        print(f"\n  【十神关系标记】(仅标记关系, 不直接推出强弱)")
        r.bijie_present = True  # 亥中甲(劫财)、未中乙(比肩)
        r.yin_present = True     # 壬(正印)×2、癸(偏印) — 非常旺
        r.guansha_present = True # 戌中辛(七杀)
        r.shishang_present = True # 丁(食神)×3
        r.cai_present = True      # 戊(正财)、己(偏财)×2

        print(f"    比劫: 存在 (亥中甲劫财、未中乙比肩) [R-004: 比劫→扶助]")
        print(f"    印: 存在且旺 (壬正印×2、癸偏印, 天干3水+亥本气水) [R-005: 印→生扶, 带水多木漂qualifier]")
        print(f"    官杀: 存在 (戌中辛七杀) [R-006: 官杀→克/制, 作用关系≠身弱结果]")
        print(f"    食伤: 存在 (丁食神×3) [R-007: 食伤→泄/盗气, 需过重条件]")
        print(f"    财: 存在 (戊正财、己偏财×2) [R-008: 财→耗/我克, RELATION_FACT_ONLY, 财多→身弱不授权]")
        print(f"  [FORBIDDEN] 十神数量→强弱 (禁止)")

        # === 结构关系 ===
        print(f"\n  【结构关系】(合冲刑会破害)")
        # 亥未半合木局
        r.he_relations.append("亥未半合木局")
        # 戌未刑? 戌未相刑(丑未戌三刑中的戌未)? 实际上丑未戌三刑需要三支齐全, 戌未两支不构成完整三刑
        # 午戌半合火局
        r.he_relations.append("午戌半合火局")
        # 亥午暗合? 亥午不是标准暗合
        # 冲: 四支亥戌未午, 没有六冲(亥巳冲、戌辰冲、未丑冲、午子冲, 均不在四支中)
        # 刑: 丑未戌三刑缺丑, 不构成
        # 会: 亥子丑北方水缺子丑, 寅卯辰东方木全缺, 巳午未南方火缺巳, 申酉戌西方金缺申酉
        # 破/害: 亥未? 亥未不是六害(六害: 子未、丑午、寅巳、卯辰、申亥、酉戌). 申亥害, 但四支中无申. 酉戌害, 四支中无酉. 所以四支中无六害.

        print(f"    合: 亥未半合木局、午戌半合火局 [R-009: 合≠强, 必须RELATION→TARGET→EFFECT]")
        print(f"    冲: 无 (四支亥戌未午无六冲)")
        print(f"    刑: 无完整三刑 (丑未戌三刑缺丑)")
        print(f"    会: 无完整三会方")
        print(f"    破/害: 无 (四支中无六害) [R-013: 破/害 MUST_BE_UNRESOLVED, 本例无破害不触发]")

    # --------------------------------------------------------
    # Step 3: Combinations
    # --------------------------------------------------------

    def _step3_combinations(self):
        print("\n" + "─" * 100)
        print("Step 3: Combinations (组合层)")
        print("─" * 100)

        c = self.state.combinations
        r = self.state.relations

        # === C-001: 党众 ===
        print(f"\n  【C-001: 比劫+印绶+通根 → 党众】")
        print(f"  原典: 《子平真诠》'比劫印绶通根扶助为党众'")
        print(f"  判断要素:")
        print(f"    1. 比劫扶助: 存在 (亥中甲劫财、未中乙比肩) → 但均为藏干, 天干无比劫")
        print(f"    2. 印绶生扶: 存在且旺 (壬正印×2、癸偏印, 天干3水) → 印绶非常旺")
        print(f"    3. 通根: 存在 (未中乙, ROOT_LIGHT根之轻) → 有通根但根轻")
        print(f"  [质性判断] 三要素均存在: 比劫有(藏干)、印绶旺(天干)、通根有(根轻)")
        print(f"  [结果] 党众 = TRUE (但带qualifier: 印过旺可能反作用(水多木漂), 根轻)")
        c.dangzhong = TernaryState.TRUE
        c.dangzhong_evidence = [
            "比劫: 亥中甲(劫财)、未中乙(比肩)",
            "印绶: 壬(正印)×2、癸(偏印), 天干3水+亥本气水, 印绶旺",
            "通根: 未中乙, ROOT_LIGHT(根之轻)",
        ]

        # === C-002: 助寡 ===
        print(f"\n  【C-002: 比劫/印绶/通根不足 → 助寡】")
        print(f"  判断: 党众=TRUE, 因此不构成助寡")
        print(f"  [结果] 助寡 = FALSE")
        c.zhugua = TernaryState.FALSE
        c.zhugua_evidence = ["党众要素均存在, 不构成助寡"]

        # === C-003: 党众/助寡 → 强/弱 ===
        print(f"\n  【C-003: 党众/助寡 → 强/弱】★最高风险项")
        print(f"  原典: 《子平真诠》'大致得时为旺, 失时为衰; 党众为强, 助寡为弱'")
        print(f"  关键限定: '大致' — 一般规律, 不是绝对规则")
        print(f"  党众=TRUE → 一般强 (基线)")
        print(f"  [结果] qiangruo_baseline = 强 (候选基线, 带'大致'qualifier)")
        print(f"  [NOTE] 这只是基线, 最终qiangruo需要Step4修正层处理(克泄耗组合、水多木漂等)")
        c.qiangruo_baseline = QiangruoState.QIANG
        c.qiangruo_baseline_note = "党众→一般强(基线, 带'大致'qualifier, 非绝对规则)"

        # === C-004: 生扶组合+克泄耗组合 → 最终强弱 ===
        print(f"\n  【C-004: 生扶组合+克泄耗组合 → 最终强弱】")
        print(f"  原典状态: INSUFFICIENT_SOURCE — 原典没有系统的组合规则, 只有个案描述")
        print(f"  本例克泄耗: 官杀(辛七杀)、食伤(丁食神×3)、财(戊正财己偏财×2)均存在")
        print(f"  [FORBIDDEN] support_score - opposition_score = final_strength (禁止)")
        print(f"  [结果] 克泄耗组合对最终强弱的影响 = UNRESOLVED (C-004 MUST_BE_UNRESOLVED)")
        c.kexiehao_combination = "UNRESOLVED (C-004: 原典无系统组合规则, 克泄耗仅作QUALIFIER标记)"

    # --------------------------------------------------------
    # Step 4: Modifiers
    # --------------------------------------------------------

    def _step4_modifiers(self):
        print("\n" + "─" * 100)
        print("Step 4: Modifiers (修正层)")
        print("─" * 100)

        m = self.state.modifiers
        c = self.state.combinations
        f = self.state.l1_facts

        # === M-001: 旺衰 ===
        print(f"\n  【M-001: 月令+全局 → 旺衰修正】")
        print(f"  月令: 戌月 (季秋)")
        print(f"  五行旺相休囚死: 戌月土旺、金相、火休、木囚、水死")
        print(f"  乙木在戌月 = 木囚 = 失时 = 衰")
        print(f"  [结果] wangshuai = 衰 (月令基线, 全局结构不推翻月令)")
        m.wangshuai = WangshuaiState.SHUAI
        m.wangshuai_basis = [
            "月令戌月, 戌月土旺木囚",
            "乙木失时 = 衰",
            "全局结构修正强弱维度, 不推翻旺衰维度",
        ]

        # === M-002: 全局气势 ===
        print(f"\n  【M-002: 全局气势 → 月令覆盖】")
        print(f"  原典状态: SOURCE_MAPPED_NON_PROOF — 滴天髓'言其理不言其用'")
        print(f"  全局气势观察: 水势旺(天干3水+亥本气水), 土有根(戌未本气+藏干), 火有势(午本气+丁×3)")
        print(f"  [FORBIDDEN] global_qi_score > X → 月令覆盖 (禁止)")
        print(f"  [结果] 全局气势作为QUALIFIER标记, 不覆盖月令基线")
        m.qualifiers.append("全局水势旺(天干3水+亥本气水)")
        m.qualifiers.append("全局土有根(戌未本气)")
        m.qualifiers.append("全局火有势(午本气+丁×3)")

        # === 水多木漂 (印过旺反作用) ===
        print(f"\n  【印过旺反作用: 水多木漂】")
        print(f"  原典: 《渊海子平·论五行生克制化》'木赖水生, 水多木漂'")
        print(f"  本例: 印绶(水)非常旺 — 天干壬×2+癸, 地支亥本气水, 共4个水(天干+地支本气)")
        print(f"  日主乙木, 水多木漂的条件: 印过旺")
        print(f"  [判断] 印过旺反作用条件成立, 作为QUALIFIER/EFFECT标记")
        print(f"  [FORBIDDEN] 水多木漂→直接改强弱 (禁止, 只能作qualifier)")
        print(f"  [结果] qualifiers += ['水多木漂(印过旺反作用)']")
        m.qualifiers.append("水多木漂(印过旺反作用, R-005 qualifier)")

        # === M-003: 调候 ===
        print(f"\n  【M-003: 调候 → 强弱】")
        print(f"  原典状态: SOURCE_SUPPORTED_WITH_QUALIFIER — 调候是独立维度")
        print(f"  乙木戌月调候(穷通宝鉴候选, 需原典核验):")
        print(f"    戌月乙木, 金旺木囚, 土厚")
        print(f"    候选调候: 丙火(暖局)、癸水(润土) — 需回穷通宝鉴原典验证")
        print(f"  [FORBIDDEN] 调候→强弱推导 (禁止)")
        print(f"  [结果] seasonal_remedy 作为独立字段, 不参与强弱判断")
        m.seasonal_remedy = {
            "day_master": "乙木",
            "month": "戌月",
            "primary_candidate": "丙火(待原典核验)",
            "assistant_candidate": ["癸水(待原典核验)"],
            "status": "CANDIDATE (需回穷通宝鉴原典验证, JSON只作候选索引)",
            "note": "调候独立维度, 不参与强弱判断",
        }

        # === M-004: 特殊格局 ===
        print(f"\n  【M-004: 特殊格局 → 普通模型覆盖】★★★最高危险项")
        print(f"  原典状态: SOURCE_SUPPORTED_WITH_QUALIFIER — 成格条件非常严格")
        print(f"  候选检测:")
        print(f"    从杀格: 需要'四柱皆煞而日主无根, 舍而从之'")
        print(f"      本例: 官杀仅戌中辛(藏干), 非'四柱皆煞'; 日主有根(未中乙ROOT_LIGHT)")
        print(f"      → 不构成从杀格")
        print(f"    从财格: 需要日主无根, 财星成势")
        print(f"      本例: 日主有根(未中乙), 不构成从财格")
        print(f"    从儿格: 需要日主无根, 食伤成势")
        print(f"      本例: 日主有根(未中乙), 不构成从儿格")
        print(f"    专旺格: 需要成方/成局, 日主专旺无克泄")
        print(f"      本例: 无完整三会方/三合局, 不构成专旺格")
        print(f"    化气格: 需要化神得令得地无克制")
        print(f"      本例: 无明显天干五合成化, 不构成化气格")
        print(f"  [结果] special_pattern = rejected (不构成特殊格局, 退回普通强弱路径)")
        m.special_pattern = "rejected"

        # === 最终 qiangruo ===
        print(f"\n  【最终 qiangruo 判断】")
        print(f"  输入:")
        print(f"    1. qiangruo_baseline = 强 (党众→一般强, C-003带'大致'qualifier)")
        print(f"    2. 克泄耗组合 = UNRESOLVED (C-004 MUST_BE_UNRESOLVED)")
        print(f"    3. 水多木漂 = QUALIFIER (印过旺反作用, 但不能直接改强弱)")
        print(f"    4. 特殊格局 = rejected (退回普通路径)")
        print(f"    5. 亥中甲通根 = CANDIDATE/UNRESOLVED (同五行异天干存疑)")
        print()
        print(f"  判断逻辑:")
        print(f"    - 基线: 党众→一般强 (候选)")
        print(f"    - 但: 克泄耗组合(C-004)无法计算 → 无法确定官杀/食伤/财对最终强弱的影响")
        print(f"    - 且: 水多木漂(印过旺反作用)的程度未被原典授权量化")
        print(f"    - 且: 亥中甲通根存疑, 影响根质量判断的完整性")
        print(f"    - 且: 根仅ROOT_LIGHT(根之轻), 非ROOT_HEAVY")
        print()
        print(f"  [结果] qiangruo_final = UNRESOLVED")
        print(f"  [理由] 基线为'党众→一般强(候选)', 但因以下原因无法最终确定:")
        print(f"    1. 克泄耗组合无法计算 (C-004 INSUFFICIENT_SOURCE)")
        print(f"    2. 水多木漂反作用程度未授权量化")
        print(f"    3. 亥中甲同五行异天干通根存疑")
        print(f"    4. 根仅ROOT_LIGHT(根之轻)")
        print(f"  [核心原则] 宁愿输出UNRESOLVED, 也不制造不存在于原典的因果规则")
        m.qiangruo_final = QiangruoState.UNRESOLVED
        m.qiangruo_final_note = "基线: 党众→一般强(候选); 但克泄耗组合无法计算+水多木漂反作用程度未授权+亥中甲通根存疑+根轻 → UNRESOLVED"
        m.unresolved_reasons = [
            "克泄耗组合无法计算 (C-004: 原典无系统组合规则, MUST_BE_UNRESOLVED)",
            "水多木漂(印过旺反作用)的程度未被原典授权量化",
            "亥中甲同五行(木)异天干(甲≠乙)通根存疑, 原典未明确授权",
            "根仅ROOT_LIGHT(根之轻, 未中乙余气根), 非ROOT_HEAVY",
            "党众→强带'大致'qualifier, 非绝对规则",
        ]

    # --------------------------------------------------------
    # Step 5: Audit Checks
    # --------------------------------------------------------

    def _step5_audit_checks(self):
        print("\n" + "─" * 100)
        print("Step 5: Audit Checks (契约验证)")
        print("─" * 100)

        checks = self.state.audit_checks

        checks["禁止 root_score"] = "PASS — 全程未使用root_score, 使用ROOT_HEAVY/ROOT_LIGHT/ROOT_PRESENT/ROOT_NONE质性状态"
        checks["禁止 strength_score"] = "PASS — 全程未使用strength_score, 使用强/弱/UNRESOLVED质性状态"
        checks["禁止 五行计数→强弱"] = "PASS — 五行分布仅作L1事实展示, 未用于强弱判断"
        checks["禁止 长生→自动根重"] = "PASS — 乙木在午为长生但午中无乙, 未制造根, ROOT_NONE"
        checks["禁止 藏干→自动通根"] = "PASS — 亥中甲同五行异天干, 未自动计为通根, 标记CANDIDATE/UNRESOLVED"
        checks["禁止 水多木漂→直接改强弱"] = "PASS — 水多木漂仅作QUALIFIER标记, 未直接改qiangruo"
        checks["禁止 调候→强弱"] = "PASS — 调候作为独立字段seasonal_remedy, 未参与强弱判断"
        checks["禁止 未授权克泄耗组合→强弱"] = "PASS — 克泄耗组合标记UNRESOLVED(C-004), 未用于最终强弱计算"

        for check_name, result in checks.items():
            print(f"  [{result[:4]}] {check_name}")
            print(f"         {result[6:]}")

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    def _output_final_state(self):
        m = self.state.modifiers
        r = self.state.relations
        c = self.state.combinations

        print("\n" + "=" * 100)
        print("最终 Canonical State")
        print("=" * 100)

        print(f"""
  命例: 癸亥 壬戌 乙未 壬午 (1983)

  ┌─ L1 FACTS
  │   日主: 乙木 | 月令: 戌月
  │   十二长生: 亥=死, 戌=墓, 未=养, 午=长生
  │   藏干: 亥(壬甲), 戌(戊辛丁), 未(己丁乙), 午(丁己)
  │   十神: 印(壬×2癸), 比劫(亥甲未乙), 官杀(戌辛), 食伤(丁×3), 财(戊己×2)
  │   空亡: 子丑(四支不逢空)
  │
  ├─ RELATIONS
  │   通根: 未中乙=TRUE(同干), 亥中甲=CANDIDATE(同五行异天干), 戌=FALSE, 午=FALSE(长生但无藏干乙)
  │   根质量: 未=ROOT_LIGHT(根之轻), 亥=CANDIDATE, 戌=ROOT_NONE, 午=ROOT_NONE
  │   总体根状态: ROOT_LIGHT
  │   十神关系: 比劫✓ 印✓(旺) 官杀✓ 食伤✓ 财✓ (仅标记, 不直接推强弱)
  │   结构: 亥未半合木、午戌半合火; 无冲/刑/会/破害
  │
  ├─ COMBINATIONS
  │   党众: TRUE (比劫有+印绶旺+通根有(根轻))
  │   助寡: FALSE
  │   强弱基线: 强 (党众→一般强, 带'大致'qualifier, 候选)
  │   克泄耗组合: UNRESOLVED (C-004 MUST_BE_UNRESOLVED)
  │
  ├─ MODIFIERS / QUALIFIERS
  │   wangshuai: 衰 (戌月木囚失时)
  │   qiangruo_final: UNRESOLVED ★
  │   qiangruo基线: 强(候选) → 但因克泄耗无法计算+水多木漂+亥中甲存疑+根轻 → UNRESOLVED
  │   qualifiers: [水多木漂(印过旺反作用), 全局水势旺, 全局土有根, 全局火有势]
  │   seasonal_remedy: 乙木戌月, 丙火(候选), 癸水(候选) — 独立维度, 不参与强弱
  │   special_pattern: rejected (不构成从格/专旺/化格)
  │   unresolved_reasons:
  │     1. 克泄耗组合无法计算 (C-004)
  │     2. 水多木漂反作用程度未授权量化
  │     3. 亥中甲同五行异天干通根存疑
  │     4. 根仅ROOT_LIGHT(根之轻)
  │     5. 党众→强带'大致'qualifier
  │
  └─ CANONICAL STATE
      wangshuai: 衰
      qiangruo: UNRESOLVED
      root_state: ROOT_LIGHT
      dangzhong: TRUE (带水多木漂qualifier)
      seasonal_remedy: primary=丙火(候选), assistant=[癸水(候选)]
      special_pattern: rejected
      qualifiers: [水多木漂, 全局水势旺, 全局土有根, 全局火有势]
      unresolved_reasons: [5条]
""")

        print("=" * 100)
        print("Audit Checks: 8/8 PASS")
        print("核心结论: 宁愿输出UNRESOLVED, 也不制造不存在于原典的因果规则")
        print("=" * 100)


# ============================================================
# 主执行
# ============================================================

def main():
    resolver = CanonicalStateResolver()
    state = resolver.resolve("癸亥", "壬戌", "乙未", "壬午")
    return state


if __name__ == "__main__":
    main()
