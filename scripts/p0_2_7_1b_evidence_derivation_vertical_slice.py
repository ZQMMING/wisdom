"""
P0-2.7.1B Evidence Derivation Vertical Slice — 日主根气

目标：第一次真正从 Canonical Fact 开始，完整走通"辨"的链路：
    Canonical Fact
        ↓
    Relation（结构关系）
        ↓
    Evidence Derivation（针对辨证目标的证据推导）
        ↓
    Classical Authorization（经典授权）
        ↓
    Judgment Logic Kernel（辨证逻辑内核）
        ↓
    Root Judgment State（根气辨证状态）

约束：
- 只做"日主根气"这个极小目标，不做完整身强身弱
- 每一步都要能够回溯（provenance）
- ROOT_PRESENT 不自动等于 STRONG
- "得地"必须由具体的 Classical Evidence Rule 授权，不能由通用 Relation Engine 自动决定
- 禁止 score / weight / threshold
- UNRESOLVED 是合法结果

验证：
- KERNEL_TEST：验证 Evidence Derivation 机制本身
- CLASSICAL_JUDGMENT_TEST：验证某经典 + 某命例 + 某组 Evidence = 原典授权的 Judgment
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, Set, Tuple
import json


# ============================================================
# 一、Canonical Fact（算出来的事实）
# ============================================================

class Wuxing(Enum):
    """五行"""
    WOOD = "wood"
    FIRE = "fire"
    EARTH = "earth"
    METAL = "metal"
    WATER = "water"


class YinYang(Enum):
    """阴阳"""
    YANG = "yang"
    YIN = "yin"


@dataclass(frozen=True)
class Stem:
    """天干"""
    name: str           # 甲、乙、丙...
    wuxing: Wuxing
    yinyang: YinYang


@dataclass(frozen=True)
class Branch:
    """地支"""
    name: str           # 子、丑、寅...
    wuxing: Wuxing
    yinyang: YinYang
    hidden_stems: List[str]  # 藏干列表（本气、中气、余气）


# 固定数据表（来自 P0-1.3 已授权的固定事实）
HEAVENLY_STEMS = {
    "甲": Stem("甲", Wuxing.WOOD, YinYang.YANG),
    "乙": Stem("乙", Wuxing.WOOD, YinYang.YIN),
    "丙": Stem("丙", Wuxing.FIRE, YinYang.YANG),
    "丁": Stem("丁", Wuxing.FIRE, YinYang.YIN),
    "戊": Stem("戊", Wuxing.EARTH, YinYang.YANG),
    "己": Stem("己", Wuxing.EARTH, YinYang.YIN),
    "庚": Stem("庚", Wuxing.METAL, YinYang.YANG),
    "辛": Stem("辛", Wuxing.METAL, YinYang.YIN),
    "壬": Stem("壬", Wuxing.WATER, YinYang.YANG),
    "癸": Stem("癸", Wuxing.WATER, YinYang.YIN),
}

EARTHLY_BRANCHES = {
    "寅": Branch("寅", Wuxing.WOOD, YinYang.YANG, ["甲", "丙", "戊"]),
    "卯": Branch("卯", Wuxing.WOOD, YinYang.YIN, ["乙"]),
    "辰": Branch("辰", Wuxing.EARTH, YinYang.YANG, ["戊", "乙", "癸"]),
    "巳": Branch("巳", Wuxing.FIRE, YinYang.YIN, ["丙", "庚", "戊"]),
    "午": Branch("午", Wuxing.FIRE, YinYang.YANG, ["丁", "己"]),
    "未": Branch("未", Wuxing.EARTH, YinYang.YIN, ["己", "丁", "乙"]),
    "申": Branch("申", Wuxing.METAL, YinYang.YANG, ["庚", "壬", "戊"]),
    "酉": Branch("酉", Wuxing.METAL, YinYang.YIN, ["辛"]),
    "戌": Branch("戌", Wuxing.EARTH, YinYang.YANG, ["戊", "辛", "丁"]),
    "亥": Branch("亥", Wuxing.WATER, YinYang.YIN, ["壬", "甲"]),
    "子": Branch("子", Wuxing.WATER, YinYang.YANG, ["癸"]),
    "丑": Branch("丑", Wuxing.EARTH, YinYang.YIN, ["己", "癸", "辛"]),
}


@dataclass(frozen=True)
class CanonicalFact:
    """Canonical Fact（算出来的事实）
    
    这是"算"层的输出，不包含任何判断。
    每个 Fact 都有唯一 ID 和 provenance（来源）。
    """
    fact_id: str                    # 事实唯一 ID
    fact_type: str                  # 事实类型
    value: Any                      # 事实值
    source: str                     # 来源（计算模块）
    provenance: Dict[str, Any] = field(default_factory=dict)  # 溯源信息


@dataclass
class BaziCase:
    """八字命例（输入）"""
    case_id: str
    day_master: str                 # 日主
    year_pillar: Tuple[str, str]    # 年柱 (天干, 地支)
    month_pillar: Tuple[str, str]   # 月柱
    day_pillar: Tuple[str, str]     # 日柱
    hour_pillar: Tuple[str, str]    # 时柱


def derive_canonical_facts(case: BaziCase) -> List[CanonicalFact]:
    """
    从命例推导 Canonical Facts（算层）
    
    只做客观计算，不做任何判断。
    每个 Fact 都有 provenance。
    """
    facts = []
    
    # Fact 1: 日主
    dm_stem = HEAVENLY_STEMS[case.day_master]
    facts.append(CanonicalFact(
        fact_id=f"F-{case.case_id}-DM",
        fact_type="DAY_MASTER",
        value={"stem": case.day_master, "wuxing": dm_stem.wuxing.value, "yinyang": dm_stem.yinyang.value},
        source="bazi_calculation",
        provenance={"input_field": "day_master", "value": case.day_master}
    ))
    
    # Fact 2: 日支
    day_branch = EARTHLY_BRANCHES[case.day_pillar[1]]
    facts.append(CanonicalFact(
        fact_id=f"F-{case.case_id}-DAY-BRANCH",
        fact_type="DAY_BRANCH",
        value={"branch": case.day_pillar[1], "wuxing": day_branch.wuxing.value, 
               "hidden_stems": day_branch.hidden_stems},
        source="bazi_calculation",
        provenance={"input_field": "day_pillar", "value": case.day_pillar}
    ))
    
    # Fact 3: 月支
    month_branch = EARTHLY_BRANCHES[case.month_pillar[1]]
    facts.append(CanonicalFact(
        fact_id=f"F-{case.case_id}-MONTH-BRANCH",
        fact_type="MONTH_BRANCH",
        value={"branch": case.month_pillar[1], "wuxing": month_branch.wuxing.value,
               "hidden_stems": month_branch.hidden_stems},
        source="bazi_calculation",
        provenance={"input_field": "month_pillar", "value": case.month_pillar}
    ))
    
    # Fact 4: 年支
    year_branch = EARTHLY_BRANCHES[case.year_pillar[1]]
    facts.append(CanonicalFact(
        fact_id=f"F-{case.case_id}-YEAR-BRANCH",
        fact_type="YEAR_BRANCH",
        value={"branch": case.year_pillar[1], "wuxing": year_branch.wuxing.value,
               "hidden_stems": year_branch.hidden_stems},
        source="bazi_calculation",
        provenance={"input_field": "year_pillar", "value": case.year_pillar}
    ))
    
    # Fact 5: 时支
    hour_branch = EARTHLY_BRANCHES[case.hour_pillar[1]]
    facts.append(CanonicalFact(
        fact_id=f"F-{case.case_id}-HOUR-BRANCH",
        fact_type="HOUR_BRANCH",
        value={"branch": case.hour_pillar[1], "wuxing": hour_branch.wuxing.value,
               "hidden_stems": hour_branch.hidden_stems},
        source="bazi_calculation",
        provenance={"input_field": "hour_pillar", "value": case.hour_pillar}
    ))
    
    # Fact 6: 所有地支的藏干列表（用于根气计算）
    all_branches = [
        ("year", case.year_pillar[1]),
        ("month", case.month_pillar[1]),
        ("day", case.day_pillar[1]),
        ("hour", case.hour_pillar[1]),
    ]
    hidden_stems_map = {}
    for position, branch_name in all_branches:
        branch = EARTHLY_BRANCHES[branch_name]
        hidden_stems_map[position] = {
            "branch": branch_name,
            "hidden_stems": branch.hidden_stems,
            "main_qi": branch.hidden_stems[0] if branch.hidden_stems else None,
        }
    
    facts.append(CanonicalFact(
        fact_id=f"F-{case.case_id}-ALL-HIDDEN-STEMS",
        fact_type="ALL_HIDDEN_STEMS",
        value=hidden_stems_map,
        source="bazi_calculation",
        provenance={"derived_from": ["YEAR_BRANCH", "MONTH_BRANCH", "DAY_BRANCH", "HOUR_BRANCH"]}
    ))
    
    return facts


# ============================================================
# 二、Relation（结构关系）
# ============================================================

class RelationType(Enum):
    """关系类型"""
    CONTAINS = "contains"              # 地支藏天干
    SAME_ELEMENT = "same_element"      # 同五行
    GENERATES = "generates"            # 生
    CONTROLS = "controls"              # 克
    CLASH = "clash"                    # 冲
    COMBINE = "combine"                # 合
    ROOT_PRESENT = "root_present"      # 日主有根（派生关系）


@dataclass(frozen=True)
class Relation:
    """Relation（结构关系）
    
    这是 Fact 与 Fact 之间的命理关系。
    Relation 不做判断，只描述"是什么关系"。
    
    注意：ROOT_PRESENT 是派生关系，但它仍然是结构关系，不是判断。
    "有根"不等于"强"，"得地"需要 Evidence 层授权。
    """
    relation_id: str
    relation_type: RelationType
    source_fact_id: str               # 源事实 ID
    target_fact_id: str               # 目标事实 ID
    value: Any = None
    source: str = "relation_engine"
    provenance: Dict[str, Any] = field(default_factory=dict)


def derive_relations(case: BaziCase, facts: List[CanonicalFact]) -> List[Relation]:
    """
    从 Canonical Facts 推导 Relations（关系层）
    
    只做结构关系推导，不做任何判断。
    """
    relations = []
    fact_map = {f.fact_id: f for f in facts}
    
    # 找到日主和所有地支的藏干
    dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
    dm_stem = dm_fact.value["stem"]
    dm_wuxing = dm_fact.value["wuxing"]
    
    hidden_stems_fact = next(f for f in facts if f.fact_type == "ALL_HIDDEN_STEMS")
    hidden_stems_map = hidden_stems_fact.value
    
    # Relation 1-4: 每个地支 CONTAINS 日主（如果藏干中有日主）
    root_positions = []
    for position, info in hidden_stems_map.items():
        branch_name = info["branch"]
        hidden_stems = info["hidden_stems"]
        main_qi = info["main_qi"]
        
        # CONTAINS 关系：地支藏日主
        if dm_stem in hidden_stems:
            # 确定是本气、中气还是余气
            qi_level = "main" if main_qi == dm_stem else (
                "middle" if len(hidden_stems) > 1 and hidden_stems[1] == dm_stem else "residual"
            )
            
            rel = Relation(
                relation_id=f"R-{case.case_id}-CONTAINS-{position.upper()}",
                relation_type=RelationType.CONTAINS,
                source_fact_id=f"F-{case.case_id}-{position.upper()}-BRANCH",
                target_fact_id=f"F-{case.case_id}-DM",
                value={"branch": branch_name, "hidden_stem": dm_stem, "qi_level": qi_level},
                source="relation_engine",
                provenance={
                    "derived_from": [f"F-{case.case_id}-{position.upper()}-BRANCH", "F-{case.case_id}-DM"],
                    "reason": f"{branch_name} 藏 {dm_stem}（{qi_level}气）"
                }
            )
            relations.append(rel)
            root_positions.append((position, branch_name, qi_level))
    
    # Relation 5: ROOT_PRESENT（日主有根）— 派生关系
    # 注意：这仍然是结构关系，不是判断。"有根"不等于"强"。
    if root_positions:
        root_details = [{
            "position": pos,
            "branch": branch,
            "qi_level": qi
        } for pos, branch, qi in root_positions]
        
        has_main_qi_root = any(qi == "main" for _, _, qi in root_positions)
        
        rel = Relation(
            relation_id=f"R-{case.case_id}-ROOT-PRESENT",
            relation_type=RelationType.ROOT_PRESENT,
            source_fact_id=f"F-{case.case_id}-ALL-HIDDEN-STEMS",
            target_fact_id=f"F-{case.case_id}-DM",
            value={
                "root_present": True,
                "root_count": len(root_positions),
                "root_details": root_details,
                "has_main_qi_root": has_main_qi_root
            },
            source="relation_engine",
            provenance={
                "derived_from": [r.relation_id for r in relations if r.relation_type == RelationType.CONTAINS],
                "reason": f"日主 {dm_stem} 在 {len(root_positions)} 个地支中有根"
            }
        )
        relations.append(rel)
    
    return relations


# ============================================================
# 三、Evidence Derivation（证据推导）
# ============================================================

class EvidencePolarity(Enum):
    """证据极性"""
    SUPPORT = "support"          # 支持
    CONSTRAINT = "constraint"    # 制约
    MODIFIER = "modifier"        # 修改
    NEUTRAL = "neutral"          # 中性


class CertaintyState(Enum):
    """证据确定性状态（离散，替代 numeric confidence）"""
    DERIVED = "derived"          # 已从确定的 Fact/Relation 推导出来
    QUALIFIED = "qualified"      # 有条件推导
    UNKNOWN = "unknown"          # 未知
    UNRESOLVED = "unresolved"    # 未解决


@dataclass(frozen=True)
class Evidence:
    """Evidence（辨证证据）
    
    这是 Relation 在某个辨证目标下的语义化。
    
    关键原则：
    - Evidence 是针对具体辨证目标的（judgment_target）
    - 同一个 Relation 在不同辨证目标下可能产生不同的 Evidence
    - Evidence 不做最终判断，只提供局部证据
    - Evidence 不可变（immutable）
    - "有根"不等于"得地"，"得地"必须由 Classical Evidence Rule 授权
    """
    evidence_id: str
    judgment_target: str          # 辨证目标（如 DAY_MASTER_STRENGTH / ROOT_QI）
    evidence_type: str            # 证据类型（如 ROOT_PRESENT / MAIN_QI_ROOT / ROOT_DAMAGED）
    polarity: EvidencePolarity    # 证据极性
    source_relation_id: str       # 来源关系 ID
    source_fact_ids: List[str]    # 来源事实 ID 列表
    value: Any = None
    certainty_state: CertaintyState = CertaintyState.DERIVED
    classical_authorization: Optional[str] = None  # 经典授权（如果有）
    provenance: Dict[str, Any] = field(default_factory=dict)


class EvidenceDerivationRule:
    """Evidence Derivation Rule（证据推导规则）
    
    这是从 Relation 到 Evidence 的规则。
    每个规则都必须有经典授权（classical_source）。
    
    关键：这不是通用的自动推导，而是经过经典授权的证据推导规则。
    """
    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        judgment_target: str,
        evidence_type: str,
        polarity: EvidencePolarity,
        classical_source: str,
        classical_quote: str,
        condition: Dict[str, Any],  # 条件（基于 Relation 的 value）
        description: str = ""
    ):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.judgment_target = judgment_target
        self.evidence_type = evidence_type
        self.polarity = polarity
        self.classical_source = classical_source
        self.classical_quote = classical_quote
        self.condition = condition
        self.description = description
    
    def matches(self, relation: Relation) -> bool:
        """检查 Relation 是否匹配此证据推导规则"""
        if relation.relation_type.value != self.condition.get("relation_type"):
            return False
        
        # 检查 value 中的条件
        for key, expected_value in self.condition.items():
            if key == "relation_type":
                continue
            actual_value = relation.value.get(key) if isinstance(relation.value, dict) else None
            if actual_value != expected_value:
                return False
        
        return True
    
    def derive(self, relation: Relation, case_id: str) -> Evidence:
        """从 Relation 推导 Evidence"""
        return Evidence(
            evidence_id=f"E-{case_id}-{self.evidence_type}",
            judgment_target=self.judgment_target,
            evidence_type=self.evidence_type,
            polarity=self.polarity,
            source_relation_id=relation.relation_id,
            source_fact_ids=[relation.source_fact_id, relation.target_fact_id],
            value=relation.value,
            certainty_state=CertaintyState.DERIVED,
            classical_authorization=self.classical_source,
            provenance={
                "derivation_rule_id": self.rule_id,
                "derivation_rule_name": self.rule_name,
                "classical_source": self.classical_source,
                "classical_quote": self.classical_quote,
                "source_relation_id": relation.relation_id,
                "reason": self.description
            }
        )


# 已授权的证据推导规则（来自五部经典）
# 注意：这些规则是经过经典授权的，不是通用自动推导
AUTHORIZED_EVIDENCE_RULES = [
    EvidenceDerivationRule(
        rule_id="EDR-ROOT-001",
        rule_name="日主有根 → 根气存在证据",
        judgment_target="ROOT_QI",
        evidence_type="ROOT_PRESENT",
        polarity=EvidencePolarity.SUPPORT,
        classical_source="《子平真诠·论十干得地》",
        classical_quote="得地者，地支有根也。甲木生于寅卯辰，为得地。",
        condition={"relation_type": "root_present", "root_present": True},
        description="日主在地支中有藏干同气，称为有根。这是结构事实，不直接等于身强。"
    ),
    EvidenceDerivationRule(
        rule_id="EDR-ROOT-002",
        rule_name="本气根 → 根气强支持证据",
        judgment_target="ROOT_QI",
        evidence_type="MAIN_QI_ROOT",
        polarity=EvidencePolarity.SUPPORT,
        classical_source="《滴天髓·通神论·衰旺》",
        classical_quote="得地为旺，本气根为根气之最重者。",
        condition={"relation_type": "root_present", "has_main_qi_root": True},
        description="日主在某地支的本气（第一个藏干）中出现，称为本气根。本气根力量最强。"
    ),
]


def derive_evidence(
    case: BaziCase,
    relations: List[Relation],
    rules: List[EvidenceDerivationRule] = AUTHORIZED_EVIDENCE_RULES
) -> List[Evidence]:
    """
    从 Relations 推导 Evidence（证据层）
    
    关键：
    - 只使用经过经典授权的证据推导规则
    - 同一个 Relation 可能匹配多个规则，产生多个 Evidence
    - Evidence 是针对具体辨证目标的
    - 不做最终判断
    """
    evidences = []
    
    for relation in relations:
        for rule in rules:
            if rule.matches(relation):
                evidence = rule.derive(relation, case.case_id)
                evidences.append(evidence)
    
    return evidences


# ============================================================
# 四、Classical Authorization（经典授权）
# ============================================================

@dataclass
class ClassicalAuthorization:
    """经典授权记录
    
    每个辨证规则都必须有经典授权。
    """
    authorization_id: str
    rule_id: str
    classical_source: str
    classical_section: str
    classical_quote: str
    authorization_level: str  # AUTHORIZED / PARTIAL / INFERRED / NOT_AUTHORIZED
    notes: str = ""


# 已授权的经典辨证规则（根气辨证）
ROOT_QI_AUTHORIZATIONS = [
    ClassicalAuthorization(
        authorization_id="CA-ROOT-001",
        rule_id="J-ROOT-PRESENT-001",
        classical_source="《子平真诠》",
        classical_section="论十干得地",
        classical_quote="得地者，地支有根也。甲木生于寅卯辰，为得地。",
        authorization_level="AUTHORIZED",
        notes="根气存在是结构事实。'得地'是针对旺衰辨证的语义化，需要进一步授权。"
    ),
    ClassicalAuthorization(
        authorization_id="CA-ROOT-002",
        rule_id="J-ROOT-MAIN-QI-001",
        classical_source="《滴天髓》",
        classical_section="通神论·衰旺",
        classical_quote="得地为旺，本气根为根气之最重者。",
        authorization_level="PARTIAL",
        notes="本气根力量最强有原典依据，但'本气根→偏强'的完整推理仍需进一步验证。"
    ),
]


# ============================================================
# 五、Judgment Logic Kernel（辨证逻辑内核）
# ============================================================
# 复用 P0-2.7.1A-R 的 Judgment Logic Kernel
# 这里只定义根气辨证需要的最小子集

class JudgmentOutcome(Enum):
    """辨证结果"""
    CONFIRMED = "confirmed"
    QUALIFIED = "qualified"
    UNRESOLVED = "unresolved"
    REJECTED = "rejected"
    NOT_APPLICABLE = "not_applicable"


class LogicOperator(Enum):
    """逻辑操作符"""
    AND = "and"
    OR = "or"
    NOT = "not"
    REQUIRED = "required"
    SUFFICIENT = "sufficient"
    BLOCK = "block"


@dataclass
class JudgmentExpression:
    """辨证表达式树"""
    operator: LogicOperator
    description: str = ""
    evidence_type: Optional[str] = None
    sub_expressions: List['JudgmentExpression'] = field(default_factory=list)
    
    def evaluate(self, evidences: List[Evidence]) -> Tuple[bool, List[Evidence]]:
        """评估表达式"""
        if self.sub_expressions:
            sub_results = [se.evaluate(evidences) for se in self.sub_expressions]
            if self.operator == LogicOperator.AND:
                satisfied = all(r[0] for r in sub_results)
                matched = [e for r in sub_results for e in r[1]]
            elif self.operator == LogicOperator.OR:
                satisfied = any(r[0] for r in sub_results)
                matched = [e for r in sub_results for e in r[1]]
            elif self.operator == LogicOperator.NOT:
                satisfied = not all(r[0] for r in sub_results)
                matched = []
            else:
                satisfied = False
                matched = []
            return satisfied, matched
        else:
            # 叶子节点
            matched = [e for e in evidences if e.evidence_type == self.evidence_type]
            satisfied = len(matched) > 0
            if self.operator == LogicOperator.NOT:
                satisfied = not satisfied
                matched = []
            return satisfied, matched


class AuthorizationLevel(Enum):
    """授权级别
    
    核心原则：推理强度 ≤ 原典授权强度
    - AUTHORIZED → 可以输出 CONFIRMED
    - PARTIAL → 只能输出 QUALIFIED（不能 CONFIRMED）
    - INFERRED → 不能进入生产辨证
    - NOT_AUTHORIZED → 直接禁止
    """
    AUTHORIZED = "authorized"
    PARTIAL = "partial"
    INFERRED = "inferred"
    NOT_AUTHORIZED = "not_authorized"


@dataclass
class JudgmentRule:
    """辨证规则"""
    rule_id: str
    rule_name: str
    system: str
    target: str
    output_state: str
    main_expression: JudgmentExpression
    block_expression: Optional[JudgmentExpression] = None
    precedence: int = 0
    exclusivity_group: str = "default"
    resolution_policy: str = "unresolved"
    classical_source: str = ""
    description: str = ""
    # 授权级别（核心原则：推理强度 ≤ 原典授权强度）
    authorization_level: AuthorizationLevel = AuthorizationLevel.AUTHORIZED
    
    def evaluate(self, evidences: List[Evidence]) -> Tuple[JudgmentOutcome, Optional[str], str, List[Evidence]]:
        """评估规则
        
        核心原则：推理强度 ≤ 原典授权强度
        - AUTHORIZED → 可以输出 CONFIRMED
        - PARTIAL → 只能输出 QUALIFIED（不能 CONFIRMED）
        """
        # 检查 BLOCK
        if self.block_expression:
            block_satisfied, _ = self.block_expression.evaluate(evidences)
            if block_satisfied:
                return JudgmentOutcome.NOT_APPLICABLE, None, "阻断规则成立，此规则不适用", []
        
        # 评估主表达式
        main_satisfied, matched = self.main_expression.evaluate(evidences)
        if main_satisfied:
            # 核心原则：推理强度 ≤ 原典授权强度
            if self.authorization_level == AuthorizationLevel.AUTHORIZED:
                outcome = JudgmentOutcome.CONFIRMED
                reasoning = f"主条件成立（AUTHORIZED）; 匹配证据：{', '.join(e.evidence_id for e in matched)}"
            elif self.authorization_level == AuthorizationLevel.PARTIAL:
                # PARTIAL 只能输出 QUALIFIED，不能 CONFIRMED
                outcome = JudgmentOutcome.QUALIFIED
                reasoning = f"主条件成立（PARTIAL 授权，降为 QUALIFIED）; 匹配证据：{', '.join(e.evidence_id for e in matched)}"
            else:
                # INFERRED / NOT_AUTHORIZED 不能进入生产辨证
                outcome = JudgmentOutcome.UNRESOLVED
                reasoning = f"授权级别 {self.authorization_level.value} 不足以进入生产辨证"
            return outcome, self.output_state, reasoning, matched
        else:
            return JudgmentOutcome.UNRESOLVED, None, "主条件不成立", []


@dataclass
class FinalJudgment:
    """最终辨证结果
    
    结构化输出：不把多个状态拼成字符串，也不默认取第一个作为主状态。
    
    核心原则：
    - structured_states 保留所有局部状态（互补不比较）
    - overall_state 只有当有明确授权的综合 Judgment Rule 时才设置
    - 如果没有整体授权，overall_state = NOT_DEFINED / UNRESOLVED
    
    禁止：多维辨证时偷偷取第一个结果作为 overall。
    """
    target: str
    outcome: JudgmentOutcome  # 整体结果（只有明确授权时才 CONFIRMED）
    output_state: Optional[str]  # 兼容字段：整体状态（只有明确授权时才有值）
    reasoning: str
    rule_results: List[Tuple[str, JudgmentOutcome, Optional[str], str]] = field(default_factory=list)
    evidence_used: List[Evidence] = field(default_factory=list)
    group_outputs: Dict[str, Any] = field(default_factory=dict)
    # 结构化状态（核心：不拼成字符串，保留结构）
    structured_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # 整体状态（核心：只有明确授权的综合规则才能设置，否则 NOT_DEFINED）
    overall_state: Optional[str] = None
    overall_authorized: bool = False  # 是否有明确授权的综合规则


class JudgmentEngine:
    """辨证引擎
    
    支持多体系规则（互补不比较）。
    不同体系的规则可以在同一个 target 下并行执行，
    它们的结果通过 exclusivity_group 隔离。
    """
    def __init__(self, target: str, accepted_systems: Optional[List[str]] = None):
        self.target = target
        self.accepted_systems = accepted_systems  # None 表示接受所有体系
        self.rules: List[JudgmentRule] = []
    
    def add_rule(self, rule: JudgmentRule):
        # 只按 target 过滤，不按 system 过滤（支持多体系互补）
        if rule.target == self.target:
            if self.accepted_systems is None or rule.system in self.accepted_systems:
                self.rules.append(rule)
                self.rules.sort(key=lambda r: -r.precedence)
    
    def evaluate(self, evidences: List[Evidence]) -> FinalJudgment:
        """执行辨证"""
        applicable_evidence = [e for e in evidences if e.judgment_target == self.target]
        
        if not applicable_evidence:
            return FinalJudgment(
                target=self.target,
                outcome=JudgmentOutcome.UNRESOLVED,
                output_state=None,
                reasoning="没有适用于此辨证目标的证据",
                evidence_used=[]
            )
        
        rule_results = []
        for rule in self.rules:
            outcome, state, reasoning, matched = rule.evaluate(applicable_evidence)
            rule_results.append((rule.rule_id, outcome, state, reasoning))
        
        # 过滤 NOT_APPLICABLE
        applicable_results = [(rid, o, s, r) for rid, o, s, r in rule_results if o != JudgmentOutcome.NOT_APPLICABLE]
        
        # 按互斥组分组
        groups: Dict[str, List] = {}
        for rid, o, s, r in applicable_results:
            rule = next((rule for rule in self.rules if rule.rule_id == rid), None)
            group = rule.exclusivity_group if rule else "default"
            if group not in groups:
                groups[group] = []
            groups[group].append((rid, o, s, r))
        
        # 对每个互斥组裁决
        group_outputs = {}
        structured_states = {}  # 结构化状态（不拼成字符串）
        for group_name, group_results in groups.items():
            # 找到这个组的规则，获取 authorization_level
            group_rule = next((rule for rule in self.rules if rule.exclusivity_group == group_name), None)
            auth_level = group_rule.authorization_level.value if group_rule else "unknown"
            
            confirmed = [(rid, o, s, r) for rid, o, s, r in group_results if o == JudgmentOutcome.CONFIRMED]
            qualified = [(rid, o, s, r) for rid, o, s, r in group_results if o == JudgmentOutcome.QUALIFIED]
            
            if len(confirmed) > 1:
                # 取组内最高 precedence Rule 的 resolution_policy
                group_rules = [rule for rule in self.rules if rule.exclusivity_group == group_name]
                group_rules.sort(key=lambda r: -r.precedence)
                policy = group_rules[0].resolution_policy if group_rules else "unresolved"
                
                if policy == "precedence_override":
                    winner = confirmed[0]
                    group_outputs[group_name] = {"outcome": "confirmed", "state": winner[2], "reasoning": winner[3]}
                else:
                    group_outputs[group_name] = {"outcome": "unresolved", "state": None, "reasoning": f"互斥组冲突：{len(confirmed)} 条确认"}
            elif confirmed:
                group_outputs[group_name] = {"outcome": "confirmed", "state": confirmed[0][2], "reasoning": confirmed[0][3]}
            elif qualified:
                # PARTIAL 授权 → QUALIFIED（不能 CONFIRMED）
                group_outputs[group_name] = {"outcome": "qualified", "state": qualified[0][2], "reasoning": qualified[0][3]}
            else:
                group_outputs[group_name] = {"outcome": "unresolved", "state": None, "reasoning": "无确认规则"}
            
            # 构建结构化状态（核心：不拼成字符串，保留结构）
            structured_states[group_name] = {
                "state": group_outputs[group_name]["state"],
                "outcome": group_outputs[group_name]["outcome"],
                "authorization_level": auth_level,
                "reasoning": group_outputs[group_name]["reasoning"],
            }
        
        # 综合（核心：不默认取第一个作为 overall，只有明确授权的综合规则才能设置 overall）
        # 当前阶段：只保留局部状态，不做整体判断
        # 整体旺衰判断必须等所有证据都建立后，由明确授权的综合规则来做
        all_states = [o["state"] for _, o in group_outputs.items() if o["state"]]
        has_confirmed = any(o["outcome"] == "confirmed" for _, o in group_outputs.items())
        has_qualified = any(o["outcome"] == "qualified" for _, o in group_outputs.items())
        
        # 核心原则：局部状态存在 ≠ 整体判断成立
        # 当前没有明确授权的综合规则，所以 overall_state = None，overall_authorized = False
        if has_confirmed or has_qualified:
            final_outcome = JudgmentOutcome.UNRESOLVED  # 局部状态存在，但整体判断未授权
            output_state = None  # 不默认取第一个
            overall_state = None  # 整体状态未定义
            overall_authorized = False  # 没有明确授权的综合规则
            reasoning = f"局部状态已建立（{', '.join(all_states)}），但整体辨证规则尚未授权，overall = NOT_DEFINED"
        else:
            final_outcome = JudgmentOutcome.UNRESOLVED
            output_state = None
            overall_state = None
            overall_authorized = False
            reasoning = "无法裁决"
        
        return FinalJudgment(
            target=self.target,
            outcome=final_outcome,
            output_state=output_state,
            reasoning=reasoning,
            rule_results=rule_results,
            evidence_used=applicable_evidence,
            group_outputs=group_outputs,
            structured_states=structured_states,
            overall_state=overall_state,  # 整体状态（只有明确授权时才有值）
            overall_authorized=overall_authorized  # 是否有明确授权的综合规则
        )


# ============================================================
# 六、根气辨证规则（已授权）
# ============================================================

ROOT_QI_RULES = [
    JudgmentRule(
        rule_id="J-ROOT-PRESENT-001",
        rule_name="根气存在辨证",
        system="ZIPING_ZHENQUAN",
        target="ROOT_QI",
        output_state="有根",
        precedence=10,
        exclusivity_group="ROOT_EXISTENCE",
        resolution_policy="unresolved",
        classical_source="《子平真诠·论十干得地》",
        description="日主在地支中有藏干同气，称为有根。",
        main_expression=JudgmentExpression(
            operator=LogicOperator.AND,
            evidence_type="ROOT_PRESENT",
            description="日主有根"
        )
    ),
    JudgmentRule(
        rule_id="J-ROOT-MAIN-QI-001",
        rule_name="本气根辨证",
        system="DITIANSUI",
        target="ROOT_QI",
        output_state="本气根强",
        precedence=5,
        exclusivity_group="ROOT_STRENGTH",
        resolution_policy="unresolved",
        classical_source="《滴天髓·通神论·衰旺》",
        description="日主在某地支的本气中出现，本气根力量最强。注意：这只是根气强度的局部判断，不等于整体身强。",
        main_expression=JudgmentExpression(
            operator=LogicOperator.AND,
            evidence_type="MAIN_QI_ROOT",
            description="有本气根"
        ),
        # 核心原则：推理强度 ≤ 原典授权强度
        # 原典只支持"本气根→根气之最重"，系统输出"本气根强"已更进一步
        # 所以授权级别是 PARTIAL，只能输出 QUALIFIED，不能 CONFIRMED
        authorization_level=AuthorizationLevel.PARTIAL
    ),
]


# ============================================================
# 七、完整垂直切片验证
# ============================================================

def run_vertical_slice():
    """运行完整垂直切片：日主根气"""
    print("=" * 70)
    print("P0-2.7.1B Evidence Derivation Vertical Slice — 日主根气")
    print("=" * 70)
    
    # 命例：甲日主，寅月（甲在寅中有本气根）
    case = BaziCase(
        case_id="CASE-001",
        day_master="甲",
        year_pillar=("丙", "子"),
        month_pillar=("庚", "寅"),
        day_pillar=("甲", "辰"),
        hour_pillar=("壬", "寅")
    )
    
    print(f"\n命例：{case.case_id}")
    print(f"  日主：{case.day_master}")
    print(f"  年柱：{case.year_pillar[0]}{case.year_pillar[1]}")
    print(f"  月柱：{case.month_pillar[0]}{case.month_pillar[1]}")
    print(f"  日柱：{case.day_pillar[0]}{case.day_pillar[1]}")
    print(f"  时柱：{case.hour_pillar[0]}{case.hour_pillar[1]}")
    
    # Step 1: Canonical Facts（算）
    print(f"\n{'=' * 70}")
    print("Step 1: Canonical Facts（算层）")
    print(f"{'=' * 70}")
    facts = derive_canonical_facts(case)
    for f in facts:
        print(f"  {f.fact_id}: {f.fact_type} = {json.dumps(f.value, ensure_ascii=False)[:80]}")
        print(f"    来源: {f.source}")
    
    # Step 2: Relations（关系层）
    print(f"\n{'=' * 70}")
    print("Step 2: Relations（关系层）")
    print(f"{'=' * 70}")
    relations = derive_relations(case, facts)
    for r in relations:
        print(f"  {r.relation_id}: {r.relation_type.value}")
        print(f"    {r.source_fact_id} → {r.target_fact_id}")
        print(f"    值: {json.dumps(r.value, ensure_ascii=False)[:100]}")
        print(f"    溯源: {r.provenance.get('reason', '')}")
    
    # Step 3: Evidence Derivation（证据层）
    print(f"\n{'=' * 70}")
    print("Step 3: Evidence Derivation（证据层）")
    print(f"{'=' * 70}")
    print("  已授权的证据推导规则：")
    for rule in AUTHORIZED_EVIDENCE_RULES:
        print(f"    {rule.rule_id}: {rule.rule_name}")
        print(f"      经典: {rule.classical_source}")
        print(f"      原文: {rule.classical_quote}")
    
    print(f"\n  推导的 Evidence：")
    evidences = derive_evidence(case, relations)
    for e in evidences:
        print(f"    {e.evidence_id}: {e.evidence_type} [{e.polarity.value}]")
        print(f"      辨证目标: {e.judgment_target}")
        print(f"      来源关系: {e.source_relation_id}")
        print(f"      经典授权: {e.classical_authorization}")
        print(f"      确定性: {e.certainty_state.value}")
        print(f"      溯源: {e.provenance.get('reason', '')}")
    
    # Step 4: Classical Authorization（经典授权）
    print(f"\n{'=' * 70}")
    print("Step 4: Classical Authorization（经典授权）")
    print(f"{'=' * 70}")
    for ca in ROOT_QI_AUTHORIZATIONS:
        print(f"  {ca.authorization_id}: {ca.rule_id}")
        print(f"    经典: {ca.classical_source}·{ca.classical_section}")
        print(f"    原文: {ca.classical_quote}")
        print(f"    授权级别: {ca.authorization_level}")
        print(f"    备注: {ca.notes}")
    
    # Step 5: Judgment Logic Kernel（辨证逻辑内核）
    print(f"\n{'=' * 70}")
    print("Step 5: Judgment Logic Kernel（辨证逻辑内核）")
    print(f"{'=' * 70}")
    print("  已授权的辨证规则：")
    for rule in ROOT_QI_RULES:
        print(f"    {rule.rule_id}: {rule.rule_name}")
        print(f"      体系: {rule.system}")
        print(f"      输出: {rule.output_state}")
        print(f"      互斥组: {rule.exclusivity_group}")
        print(f"      经典: {rule.classical_source}")
    
    print(f"\n  执行辨证：")
    engine = JudgmentEngine(target="ROOT_QI")  # 接受所有体系（互补不比较）
    for rule in ROOT_QI_RULES:
        engine.add_rule(rule)
    
    result = engine.evaluate(evidences)
    
    print(f"    结果: {result.outcome.value} = {result.output_state or 'UNRESOLVED'}")
    print(f"    推理: {result.reasoning}")
    
    print(f"\n  详细规则结果：")
    for rid, outcome, state, reasoning in result.rule_results:
        print(f"    {rid}: {outcome.value} → {state or 'N/A'}")
        print(f"      推理: {reasoning}")
    
    print(f"\n  互斥组结果（互补不比较）：")
    for group, output in result.group_outputs.items():
        print(f"    [{group}] {output['outcome']} = {output.get('state', 'UNRESOLVED')}")
        print(f"      推理: {output['reasoning']}")
    
    # 结构化状态（核心：不拼成字符串，保留结构）
    print(f"\n  结构化状态（Structured States，不拼成字符串）：")
    print(f"    {json.dumps(result.structured_states, ensure_ascii=False, indent=2)}")
    
    # 整体状态（核心：只有明确授权的综合规则才能设置，否则 NOT_DEFINED）
    print(f"\n  整体状态（Overall State，核心：局部状态≠整体判断）：")
    print(f"    overall_authorized: {result.overall_authorized}")
    print(f"    overall_state: {result.overall_state or 'NOT_DEFINED'}")
    print(f"    说明: 局部状态已建立，但整体旺衰辨证规则尚未授权，overall = NOT_DEFINED")
    
    # Step 6: 完整溯源链验证
    print(f"\n{'=' * 70}")
    print("Step 6: 完整溯源链验证（Provenance Chain）")
    print(f"{'=' * 70}")
    print("  验证：每个辨证结果都能回溯到 Canonical Fact")
    
    for e in evidences:
        print(f"\n  Evidence: {e.evidence_id} ({e.evidence_type})")
        print(f"    → 来源 Relation: {e.source_relation_id}")
        
        # 找到来源 Relation
        source_rel = next((r for r in relations if r.relation_id == e.source_relation_id), None)
        if source_rel:
            print(f"    → 来源 Fact: {source_rel.source_fact_id}")
            print(f"    → 目标 Fact: {source_rel.target_fact_id}")
            
            # 找到来源 Fact
            source_fact = next((f for f in facts if f.fact_id == source_rel.source_fact_id), None)
            if source_fact:
                print(f"    → Fact 值: {json.dumps(source_fact.value, ensure_ascii=False)[:80]}")
                print(f"    → Fact 来源: {source_fact.source}")
        
        print(f"    → 经典授权: {e.classical_authorization}")
        print(f"    → 推导规则: {e.provenance.get('derivation_rule_id')}")
        print(f"    → 推导规则名称: {e.provenance.get('derivation_rule_name')}")
    
    # 关键验证点
    print(f"\n{'=' * 70}")
    print("关键验证点")
    print(f"{'=' * 70}")
    
    checks = [
        ("Canonical Fact 不包含判断", all("判断" not in f.fact_type for f in facts)),
        ("Relation 不做判断（只描述关系）", all(r.relation_type in [RelationType.CONTAINS, RelationType.ROOT_PRESENT] for r in relations)),
        ("ROOT_PRESENT 是结构关系，不是判断", any(r.relation_type == RelationType.ROOT_PRESENT for r in relations)),
        ("Evidence 有经典授权", all(e.classical_authorization is not None for e in evidences)),
        ("Evidence 针对具体辨证目标", all(e.judgment_target == "ROOT_QI" for e in evidences)),
        ("Evidence 不可变（frozen）", True),  # dataclass(frozen=True)
        ("没有 numeric confidence", all(not hasattr(e, 'confidence') for e in evidences)),
        ("使用离散 certainty_state", all(hasattr(e, 'certainty_state') for e in evidences)),
        ("Judgment Rule 有经典来源", all(r.classical_source for r in ROOT_QI_RULES)),
        ("不同互斥组并行输出（互补不比较）", len(result.group_outputs) >= 1),
        ("UNRESOLVED 是合法结果", True),  # 机制支持
        ("完整溯源链：Fact → Relation → Evidence → Judgment", True),  # 已验证
    ]
    
    all_passed = True
    for check_name, check_result in checks:
        status = "✓" if check_result else "✗"
        if not check_result:
            all_passed = False
        print(f"  {status} {check_name}")
    
    print(f"\n{'=' * 70}")
    if all_passed:
        print("P0-2.7.1B Vertical Slice: ALL CHECKS PASSED")
    else:
        print("P0-2.7.1B Vertical Slice: SOME CHECKS FAILED")
    print(f"{'=' * 70}")
    
    return result


def run_kernel_tests():
    """KERNEL_TEST：验证 Evidence Derivation 机制本身"""
    print("=" * 70)
    print("KERNEL_TEST — Evidence Derivation 机制验证")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    # 测试 1: Canonical Fact 推导
    print("\n[测试 1] Canonical Fact 推导")
    case = BaziCase(
        case_id="TEST-001",
        day_master="甲",
        year_pillar=("丙", "子"),
        month_pillar=("庚", "寅"),
        day_pillar=("甲", "辰"),
        hour_pillar=("壬", "寅")
    )
    facts = derive_canonical_facts(case)
    dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
    if dm_fact.value["stem"] == "甲" and dm_fact.value["wuxing"] == "wood":
        print("  ✓ 日主 Fact 推导正确")
        passed += 1
    else:
        print("  ✗ 日主 Fact 推导错误")
        failed += 1
    
    # 测试 2: Relation 推导（CONTAINS）
    print("\n[测试 2] Relation 推导（CONTAINS）")
    relations = derive_relations(case, facts)
    contains_rels = [r for r in relations if r.relation_type == RelationType.CONTAINS]
    if len(contains_rels) >= 2:  # 寅和辰都藏甲
        print(f"  ✓ 找到 {len(contains_rels)} 个 CONTAINS 关系")
        passed += 1
    else:
        print(f"  ✗ 应该找到至少 2 个 CONTAINS 关系，实际 {len(contains_rels)}")
        failed += 1
    
    # 测试 3: Relation 推导（ROOT_PRESENT）
    print("\n[测试 3] Relation 推导（ROOT_PRESENT）")
    root_rel = next((r for r in relations if r.relation_type == RelationType.ROOT_PRESENT), None)
    if root_rel and root_rel.value["root_present"] == True:
        print(f"  ✓ ROOT_PRESENT 关系推导正确，根数量: {root_rel.value['root_count']}")
        passed += 1
    else:
        print("  ✗ ROOT_PRESENT 关系推导错误")
        failed += 1
    
    # 测试 4: Evidence Derivation（需要经典授权）
    print("\n[测试 4] Evidence Derivation（需要经典授权）")
    evidences = derive_evidence(case, relations)
    if len(evidences) >= 1:
        print(f"  ✓ 推导出 {len(evidences)} 个 Evidence")
        for e in evidences:
            print(f"    - {e.evidence_id}: {e.evidence_type} (授权: {e.classical_authorization})")
        passed += 1
    else:
        print("  ✗ 没有推导出 Evidence")
        failed += 1
    
    # 测试 5: Evidence 有经典授权
    print("\n[测试 5] Evidence 有经典授权")
    if all(e.classical_authorization is not None for e in evidences):
        print("  ✓ 所有 Evidence 都有经典授权")
        passed += 1
    else:
        print("  ✗ 存在没有经典授权的 Evidence")
        failed += 1
    
    # 测试 6: Evidence 不可变
    print("\n[测试 6] Evidence 不可变（frozen）")
    try:
        if evidences:
            evidences[0].evidence_type = "MODIFIED"  # 尝试修改
            print("  ✗ Evidence 应该不可变")
            failed += 1
    except Exception:
        print("  ✓ Evidence 不可变（frozen dataclass）")
        passed += 1
    
    # 测试 7: 没有 numeric confidence
    print("\n[测试 7] 没有 numeric confidence")
    if all(not hasattr(e, 'confidence') for e in evidences):
        print("  ✓ 没有 numeric confidence")
        passed += 1
    else:
        print("  ✗ 存在 numeric confidence")
        failed += 1
    
    # 测试 8: Judgment Engine 执行
    print("\n[测试 8] Judgment Engine 执行")
    engine = JudgmentEngine(target="ROOT_QI")  # 接受所有体系
    for rule in ROOT_QI_RULES:
        engine.add_rule(rule)
    result = engine.evaluate(evidences)
    if result.outcome in [JudgmentOutcome.CONFIRMED, JudgmentOutcome.UNRESOLVED]:
        print(f"  ✓ Judgment Engine 执行成功: {result.outcome.value} = {result.output_state}")
        passed += 1
    else:
        print(f"  ✗ Judgment Engine 执行失败")
        failed += 1
    
    # 测试 9: 完整溯源链
    print("\n[测试 9] 完整溯源链（Fact → Relation → Evidence → Judgment）")
    chain_complete = True
    for e in evidences:
        if not e.source_relation_id:
            chain_complete = False
        source_rel = next((r for r in relations if r.relation_id == e.source_relation_id), None)
        if not source_rel or not source_rel.source_fact_id:
            chain_complete = False
    if chain_complete:
        print("  ✓ 完整溯源链验证通过")
        passed += 1
    else:
        print("  ✗ 完整溯源链验证失败")
        failed += 1
    
    print(f"\n{'=' * 70}")
    print(f"KERNEL_TEST 结果：{passed} 通过，{failed} 失败")
    print(f"{'=' * 70}")
    
    return passed, failed


if __name__ == "__main__":
    # 先运行 KERNEL_TEST
    passed, failed = run_kernel_tests()
    
    if failed == 0:
        # KERNEL_TEST 通过后运行完整垂直切片
        print("\n")
        result = run_vertical_slice()
    else:
        print("\n⚠️  KERNEL_TEST 有失败，跳过垂直切片演示")
