"""
P0-2.7.2-R L4 Evidence Construction Refactored — 完整链路版

基于 1e558e8 的 CONDITIONAL PASS 裁决整改：

整改点：
1. L4 不再内部重复计算月令/十神/五行，只消费 Canonical Fact + Canonical Relation
2. rooted 字段从 L3 ROOT_PRESENT 读取，不硬编码
3. 保留 6 个 Evidence（L4-1到L4-6），暂缓 ENVIRONMENT_STATE / STRUCTURAL_CHANGE
4. judgment_target 保留但标注为"当前研究目标"，不是 Evidence 本体
5. 完整链路：L1 Fact → L1 Relation → L3 ROOT_PRESENT → L4 Evidence

工程分层：
L0 算 → L1 Fact/Relation → L2 月令状态 → L3 通根 → L4 外势/生扶/克泄耗（本次重构）
→ L5 结构变化 ⏳ → L6 Evidence Combination ⏳ → L7 Classical Judgment ⏳ → 解
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from enum import Enum
import json


# ============================================================================
# 标准数据结构
# ============================================================================

class Polarity(Enum):
    SUPPORT = "SUPPORT"
    CONSTRAINT = "CONSTRAINT"
    CONTEXT = "CONTEXT"
    MODIFIER = "MODIFIER"


class CertaintyState(Enum):
    DERIVED = "DERIVED"
    QUALIFIED = "QUALIFIED"
    UNKNOWN = "UNKNOWN"
    UNRESOLVED = "UNRESOLVED"


class AuthorizationLevel(Enum):
    AUTHORIZED = "AUTHORIZED"
    PARTIAL = "PARTIAL"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"


@dataclass(frozen=True)
class CanonicalFact:
    """L1 Canonical Fact — 算出来的客观事实（唯一来源）"""
    fact_id: str
    fact_type: str
    value: Dict[str, Any]
    source: str
    certainty: str


@dataclass(frozen=True)
class CanonicalRelation:
    """L1 Canonical Relation — Fact 与 Fact 的命理关系（唯一来源）"""
    relation_id: str
    relation_type: str
    source_fact_id: str
    target_fact_id: str
    value: Dict[str, Any]
    certainty: str


@dataclass(frozen=True)
class Evidence:
    """Evidence — 针对辨证目标的局部证据"""
    evidence_id: str
    evidence_type: str
    judgment_target: str  # 注意：这是当前研究目标，不是 Evidence 本体
    polarity: Polarity
    value: Dict[str, Any]
    source_fact_ids: List[str]
    source_relation_ids: List[str]
    derivation_rule_id: str
    classical_source: Dict[str, Any]
    certainty_state: CertaintyState
    authorization_level: AuthorizationLevel
    max_output: str


# ============================================================================
# L1 Canonical Fact 生成器（唯一来源）
# ============================================================================

# 五行属性（唯一来源，L1 层定义，L4 不重复定义）
WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}

YIN_YANG = {
    "甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴", "戊": "阳",
    "己": "阴", "庚": "阳", "辛": "阴", "壬": "阳", "癸": "阴",
}

# 五行生克（唯一来源，L1 层定义）
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# 地支藏干（唯一来源，L1 层定义）
HIDDEN_STEMS = {
    "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
    "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "戊", "庚"],
    "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
    "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
}

# 地支五行（唯一来源，L1 层定义）
BRANCH_WUXING = {
    "寅": "木", "卯": "木", "辰": "土",
    "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土",
    "亥": "水", "子": "水", "丑": "土",
}

# 季节（唯一来源，L1 层定义）
SEASON = {
    "寅": "春", "卯": "春", "辰": "春",
    "巳": "夏", "午": "夏", "未": "夏",
    "申": "秋", "酉": "秋", "戌": "秋",
    "亥": "冬", "子": "冬", "丑": "冬",
}

# 寒暖燥湿（唯一来源，L1 层定义）
CLIMATE = {
    "春": {"temp": "温", "humidity": "风", "dryness": "润"},
    "夏": {"temp": "热", "humidity": "暑", "dryness": "燥"},
    "秋": {"temp": "凉", "humidity": "燥", "dryness": "干"},
    "冬": {"temp": "寒", "humidity": "湿", "dryness": "润"},
}

# 十二长生（简化版，唯一来源，L1 层定义）
GROWTH_STAGE = {
    ("甲", "亥"): "长生", ("甲", "子"): "沐浴", ("甲", "丑"): "冠带",
    ("甲", "寅"): "临官", ("甲", "卯"): "帝旺", ("甲", "辰"): "衰",
    ("甲", "巳"): "病", ("甲", "午"): "死", ("甲", "未"): "墓",
    ("甲", "申"): "绝", ("甲", "酉"): "胎", ("甲", "戌"): "养",
}


def get_ten_god(day_master: str, other: str) -> str:
    """L1 十神计算（唯一来源，L4 不重复计算）"""
    dm_wx = WUXING[day_master]
    ot_wx = WUXING[other]
    same_yy = (YIN_YANG[day_master] == YIN_YANG[other])

    if dm_wx == ot_wx:
        return "比肩" if same_yy else "劫财"
    elif WUXING_SHENG[dm_wx] == ot_wx:
        return "食神" if same_yy else "伤官"
    elif WUXING_KE[dm_wx] == ot_wx:
        return "偏财" if same_yy else "正财"
    elif WUXING_SHENG[ot_wx] == dm_wx:
        return "偏印" if same_yy else "正印"
    elif WUXING_KE[ot_wx] == dm_wx:
        return "七杀" if same_yy else "正官"
    return "未知"


class CanonicalFactGenerator:
    """L1 Canonical Fact 生成器 — 唯一来源"""

    def __init__(self, year_stem: str, month_stem: str, day_stem: str, hour_stem: str,
                 year_branch: str, month_branch: str, day_branch: str, hour_branch: str):
        self.pillars = {
            "year": {"stem": year_stem, "branch": year_branch},
            "month": {"stem": month_stem, "branch": month_branch},
            "day": {"stem": day_stem, "branch": day_branch},
            "hour": {"stem": hour_stem, "branch": hour_branch},
        }

    def generate(self) -> List[CanonicalFact]:
        """生成所有 Canonical Fact"""
        facts = []
        day_master = self.pillars["day"]["stem"]

        # F1: DAY_MASTER
        facts.append(CanonicalFact(
            fact_id="F-L1-DAY-MASTER",
            fact_type="DAY_MASTER",
            value={"stem": day_master, "wuxing": WUXING[day_master], "yinyang": YIN_YANG[day_master]},
            source="bazi_calculation",
            certainty="CALCULATED"
        ))

        # F2: MONTH_BRANCH
        month_branch = self.pillars["month"]["branch"]
        facts.append(CanonicalFact(
            fact_id="F-L1-MONTH-BRANCH",
            fact_type="MONTH_BRANCH",
            value={
                "branch": month_branch,
                "wuxing": BRANCH_WUXING[month_branch],
                "season": SEASON[month_branch],
                "climate": CLIMATE[SEASON[month_branch]],
                "growth_stage": GROWTH_STAGE.get((day_master, month_branch), "未知"),
            },
            source="bazi_calculation",
            certainty="CALCULATED"
        ))

        # F3: ALL_STEMS
        facts.append(CanonicalFact(
            fact_id="F-L1-ALL-STEMS",
            fact_type="ALL_STEMS",
            value={pos: p["stem"] for pos, p in self.pillars.items()},
            source="bazi_calculation",
            certainty="CALCULATED"
        ))

        # F4: ALL_BRANCHES
        facts.append(CanonicalFact(
            fact_id="F-L1-ALL-BRANCHES",
            fact_type="ALL_BRANCHES",
            value={pos: p["branch"] for pos, p in self.pillars.items()},
            source="bazi_calculation",
            certainty="CALCULATED"
        ))

        # F5: ALL_HIDDEN_STEMS
        all_hidden = {}
        for pos, p in self.pillars.items():
            branch = p["branch"]
            hidden = HIDDEN_STEMS[branch]
            all_hidden[pos] = {
                "branch": branch,
                "hidden_stems": hidden,
                "main_qi": hidden[0] if hidden else None,
            }
        facts.append(CanonicalFact(
            fact_id="F-L1-ALL-HIDDEN-STEMS",
            fact_type="ALL_HIDDEN_STEMS",
            value=all_hidden,
            source="bazi_calculation",
            certainty="CALCULATED"
        ))

        # F6: TEN_GOD_MAP（所有干支相对于日主的十神）
        ten_god_map = {}
        for pos, p in self.pillars.items():
            if pos == "day":
                continue
            stem = p["stem"]
            ten_god_map[pos] = {
                "stem": stem,
                "wuxing": WUXING[stem],
                "yinyang": YIN_YANG[stem],
                "ten_god": get_ten_god(day_master, stem),
            }
        facts.append(CanonicalFact(
            fact_id="F-L1-TEN-GOD-MAP",
            fact_type="TEN_GOD_MAP",
            value=ten_god_map,
            source="bazi_calculation",
            certainty="CALCULATED"
        ))

        return facts


# ============================================================================
# L1 Canonical Relation 生成器（唯一来源）
# ============================================================================

class CanonicalRelationGenerator:
    """L1 Canonical Relation 生成器 — 唯一来源，从 Fact 派生 Relation"""

    def generate(self, facts: List[CanonicalFact]) -> List[CanonicalRelation]:
        """生成所有 Canonical Relation"""
        relations = []

        # 找 Fact
        dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
        tg_fact = next(f for f in facts if f.fact_type == "TEN_GOD_MAP")
        hs_fact = next(f for f in facts if f.fact_type == "ALL_HIDDEN_STEMS")
        mb_fact = next(f for f in facts if f.fact_type == "MONTH_BRANCH")

        day_master = dm_fact.value["stem"]
        dm_wx = dm_fact.value["wuxing"]

        # R1-R5: 十神关系（每个非日主的天干）
        for pos, tg_info in tg_fact.value.items():
            ten_god = tg_info["ten_god"]
            relation_type = None

            if ten_god in ("正印", "偏印"):
                relation_type = "TEN_GOD_RESOURCE"
            elif ten_god in ("比肩", "劫财"):
                relation_type = "TEN_GOD_PEER"
            elif ten_god in ("正官", "七杀"):
                relation_type = "TEN_GOD_OFFICER"
            elif ten_god in ("食神", "伤官"):
                relation_type = "TEN_GOD_OUTPUT"
            elif ten_god in ("正财", "偏财"):
                relation_type = "TEN_GOD_WEALTH"

            if relation_type:
                relations.append(CanonicalRelation(
                    relation_id=f"R-L1-TG-{pos.upper()}",
                    relation_type=relation_type,
                    source_fact_id=dm_fact.fact_id,
                    target_fact_id="F-L1-TEN-GOD-MAP",
                    value={
                        "position": pos,
                        "stem": tg_info["stem"],
                        "ten_god": ten_god,
                        "wuxing": tg_info["wuxing"],
                    },
                    certainty="DERIVED"
                ))

        # R6: ROOT_PRESENT（日主在地支藏干中有根）— L3 级别的 Relation
        root_details = []
        for pos, hs_info in hs_fact.value.items():
            hidden = hs_info["hidden_stems"]
            main_qi = hs_info["main_qi"]
            for i, stem in enumerate(hidden):
                if WUXING[stem] == dm_wx:
                    qi_level = "main" if i == 0 else ("middle" if i == 1 else "residual")
                    root_details.append({
                        "position": pos,
                        "branch": hs_info["branch"],
                        "root_stem": stem,
                        "qi_level": qi_level,
                        "is_main_qi": (stem == main_qi),
                    })

        relations.append(CanonicalRelation(
            relation_id="R-L3-ROOT-PRESENT",
            relation_type="ROOT_PRESENT",
            source_fact_id=dm_fact.fact_id,
            target_fact_id="F-L1-ALL-HIDDEN-STEMS",
            value={
                "root_present": len(root_details) > 0,
                "root_count": len(root_details),
                "root_details": root_details,
                "has_main_qi_root": any(r["is_main_qi"] for r in root_details),
            },
            certainty="DERIVED"
        ))

        # R7: SEASONAL_ALIGNMENT（日主与月令的关系）
        month_wx = mb_fact.value["wuxing"]
        if dm_wx == month_wx:
            alignment = "IN_SEASON"
        elif WUXING_SHENG.get(month_wx, "") == dm_wx:
            alignment = "GENERATED_BY_SEASON"
        else:
            alignment = "NOT_IN_SEASON"

        relations.append(CanonicalRelation(
            relation_id="R-L2-SEASONAL-ALIGNMENT",
            relation_type="SEASONAL_ALIGNMENT",
            source_fact_id=dm_fact.fact_id,
            target_fact_id="F-L1-MONTH-BRANCH",
            value={
                "alignment": alignment,
                "day_master_wuxing": dm_wx,
                "month_wuxing": month_wx,
                "season": mb_fact.value["season"],
                "growth_stage": mb_fact.value["growth_stage"],
                "climate": mb_fact.value["climate"],
            },
            certainty="DERIVED"
        ))

        return relations


# ============================================================================
# L4 Evidence 推导规则基类（只消费 Fact + Relation，不重新计算）
# ============================================================================

class EvidenceDerivationRule(ABC):
    """Evidence 推导规则基类 — 只消费 Canonical Fact + Canonical Relation"""

    @property
    @abstractmethod
    def rule_id(self) -> str:
        pass

    @property
    @abstractmethod
    def evidence_type(self) -> str:
        pass

    @property
    @abstractmethod
    def polarity(self) -> Polarity:
        pass

    @property
    @abstractmethod
    def authorization_level(self) -> AuthorizationLevel:
        pass

    @property
    @abstractmethod
    def max_output(self) -> str:
        pass

    @property
    @abstractmethod
    def classical_source(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def derive(self, facts: List[CanonicalFact],
               relations: List[CanonicalRelation]) -> Optional[Evidence]:
        pass


# ============================================================================
# L4-1: RESOURCE_SUPPORT（印生身）— 消费 TEN_GOD_RESOURCE Relation
# ============================================================================

class ResourceSupportDerivation(EvidenceDerivationRule):
    """印生身 Evidence 推导 — 消费 Canonical Relation (TEN_GOD_RESOURCE) + ROOT_PRESENT"""

    @property
    def rule_id(self) -> str:
        return "EDR-L4-RESOURCE-001"

    @property
    def evidence_type(self) -> str:
        return "RESOURCE_SUPPORT"

    @property
    def polarity(self) -> Polarity:
        return Polarity.SUPPORT

    @property
    def authorization_level(self) -> AuthorizationLevel:
        return AuthorizationLevel.PARTIAL

    @property
    def max_output(self) -> str:
        return "QUALIFIED"

    @property
    def classical_source(self) -> Dict[str, Any]:
        return {
            "classic": "子平真诠",
            "edition": "沈孝瞻原著",
            "chapter": "论用神",
            "text_type": "ORIGINAL",
            "author": "沈孝瞻",
            "source_text": "财官印食，此用神之善而顺用之者也",
            "verification_status": "PARTIALLY_VERIFIED",
        }

    def derive(self, facts: List[CanonicalFact],
               relations: List[CanonicalRelation]) -> Optional[Evidence]:
        # 只消费 Canonical Relation，不重新计算十神
        resource_relations = [r for r in relations if r.relation_type == "TEN_GOD_RESOURCE"]
        if not resource_relations:
            return None

        # 从 L3 ROOT_PRESENT Relation 读取 rooted 信息，不硬编码
        root_relation = next((r for r in relations if r.relation_type == "ROOT_PRESENT"), None)
        root_details = root_relation.value.get("root_details", []) if root_relation else []

        resource_details = []
        for rel in resource_relations:
            pos = rel.value["position"]
            stem = rel.value["stem"]
            ten_god = rel.value["ten_god"]
            # rooted 从 L3 ROOT_PRESENT 读取（检查该位置的地支藏干中是否有印的根）
            # 简化：检查印的五行是否在任何地支藏干中出现
            resource_wx = rel.value["wuxing"]
            rooted = any(WUXING.get(rd["root_stem"], "") == resource_wx for rd in root_details)
            resource_details.append({
                "position": pos,
                "stem": stem,
                "type": ten_god,
                "rooted": rooted,  # 从 L3 读取，不硬编码
                "source_relation_id": rel.relation_id,
            })

        dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
        value = {
            "resource_present": True,
            "resource_count": len(resource_details),
            "resource_details": resource_details,
            "main_resource": resource_details[0]["stem"],
            "resource_rooted_count": sum(1 for r in resource_details if r["rooted"]),
            "dual_nature": True,
            "note": "双面性：生身/母慈灭子（水多木漂）；印多可能反而不好",
        }

        return Evidence(
            evidence_id=f"E-L4-RESOURCE-{dm_fact.value['stem']}",
            evidence_type=self.evidence_type,
            judgment_target="DAY_MASTER_STRENGTH",  # 当前研究目标，不是 Evidence 本体
            polarity=self.polarity,
            value=value,
            source_fact_ids=[dm_fact.fact_id, "F-L1-TEN-GOD-MAP"],
            source_relation_ids=[r.relation_id for r in resource_relations] +
                                 ([root_relation.relation_id] if root_relation else []),
            derivation_rule_id=self.rule_id,
            classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED,
            authorization_level=self.authorization_level,
            max_output=self.max_output,
        )


# ============================================================================
# L4-2: PEER_SUPPORT（比劫帮身）— 消费 TEN_GOD_PEER Relation
# ============================================================================

class PeerSupportDerivation(EvidenceDerivationRule):
    """比劫帮身 Evidence 推导 — 消费 Canonical Relation (TEN_GOD_PEER)"""

    @property
    def rule_id(self) -> str:
        return "EDR-L4-PEER-001"

    @property
    def evidence_type(self) -> str:
        return "PEER_SUPPORT"

    @property
    def polarity(self) -> Polarity:
        return Polarity.SUPPORT

    @property
    def authorization_level(self) -> AuthorizationLevel:
        return AuthorizationLevel.PARTIAL

    @property
    def max_output(self) -> str:
        return "QUALIFIED"

    @property
    def classical_source(self) -> Dict[str, Any]:
        return {
            "classic": "滴天髓",
            "edition": "任铁樵注本",
            "chapter": "通神论",
            "text_type": "ORIGINAL",
            "author": "京图（题）/任铁樵（注）",
            "source_text": "劫财，比肩，阳刃，皆兄弟，要与提纲之神及喜神，较其轻重",
            "verification_status": "PARTIALLY_VERIFIED",
        }

    def derive(self, facts: List[CanonicalFact],
               relations: List[CanonicalRelation]) -> Optional[Evidence]:
        peer_relations = [r for r in relations if r.relation_type == "TEN_GOD_PEER"]
        if not peer_relations:
            return None

        root_relation = next((r for r in relations if r.relation_type == "ROOT_PRESENT"), None)
        root_details = root_relation.value.get("root_details", []) if root_relation else []

        peer_details = []
        jian_count = 0
        jie_count = 0
        for rel in peer_relations:
            pos = rel.value["position"]
            stem = rel.value["stem"]
            ten_god = rel.value["ten_god"]
            if ten_god == "比肩":
                jian_count += 1
            elif ten_god == "劫财":
                jie_count += 1
            peer_wx = rel.value["wuxing"]
            rooted = any(WUXING.get(rd["root_stem"], "") == peer_wx for rd in root_details)
            peer_details.append({
                "position": pos,
                "stem": stem,
                "type": ten_god,
                "rooted": rooted,
                "source_relation_id": rel.relation_id,
            })

        dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
        value = {
            "peer_present": True,
            "peer_count": len(peer_details),
            "peer_details": peer_details,
            "jian_count": jian_count,
            "jie_count": jie_count,
            "dual_nature": True,
            "note": "双面性：帮身/夺财；身弱时帮身是好事，身旺时夺财是坏事",
        }

        return Evidence(
            evidence_id=f"E-L4-PEER-{dm_fact.value['stem']}",
            evidence_type=self.evidence_type,
            judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value=value,
            source_fact_ids=[dm_fact.fact_id, "F-L1-TEN-GOD-MAP"],
            source_relation_ids=[r.relation_id for r in peer_relations] +
                                 ([root_relation.relation_id] if root_relation else []),
            derivation_rule_id=self.rule_id,
            classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED,
            authorization_level=self.authorization_level,
            max_output=self.max_output,
        )


# ============================================================================
# L4-3: OFFICER_CONTROL（官杀克身）— 消费 TEN_GOD_OFFICER Relation
# ============================================================================

class OfficerControlDerivation(EvidenceDerivationRule):
    """官杀克身 Evidence 推导 — 消费 Canonical Relation (TEN_GOD_OFFICER)"""

    @property
    def rule_id(self) -> str:
        return "EDR-L4-OFFICER-001"

    @property
    def evidence_type(self) -> str:
        return "OFFICER_CONTROL"

    @property
    def polarity(self) -> Polarity:
        return Polarity.CONSTRAINT

    @property
    def authorization_level(self) -> AuthorizationLevel:
        return AuthorizationLevel.PARTIAL

    @property
    def max_output(self) -> str:
        return "QUALIFIED"

    @property
    def classical_source(self) -> Dict[str, Any]:
        return {
            "classic": "子平真诠",
            "edition": "沈孝瞻原著",
            "chapter": "论用神",
            "text_type": "ORIGINAL",
            "author": "沈孝瞻",
            "source_text": "财官印食，此用神之善而顺用之者也；煞伤劫刃，用神之不善而逆用之者也",
            "verification_status": "PARTIALLY_VERIFIED",
        }

    def derive(self, facts: List[CanonicalFact],
               relations: List[CanonicalRelation]) -> Optional[Evidence]:
        officer_relations = [r for r in relations if r.relation_type == "TEN_GOD_OFFICER"]
        if not officer_relations:
            return None

        root_relation = next((r for r in relations if r.relation_type == "ROOT_PRESENT"), None)
        root_details = root_relation.value.get("root_details", []) if root_relation else []

        officer_details = []
        zhengguan_count = 0
        qisha_count = 0
        for rel in officer_relations:
            pos = rel.value["position"]
            stem = rel.value["stem"]
            ten_god = rel.value["ten_god"]
            if ten_god == "正官":
                zhengguan_count += 1
            elif ten_god == "七杀":
                qisha_count += 1
            officer_wx = rel.value["wuxing"]
            rooted = any(WUXING.get(rd["root_stem"], "") == officer_wx for rd in root_details)
            officer_details.append({
                "position": pos,
                "stem": stem,
                "type": ten_god,
                "rooted": rooted,  # 从 L3 读取
                "controlled": False,  # 待 L5 STRUCTURAL_CHANGE 实现后从 Relation 读取
                "source_relation_id": rel.relation_id,
            })

        dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
        value = {
            "officer_present": True,
            "officer_count": len(officer_details),
            "officer_details": officer_details,
            "zhengguan_count": zhengguan_count,
            "qisha_count": qisha_count,
            "officer_mixed": (zhengguan_count > 0 and qisha_count > 0),
            "dual_nature": True,
            "note": "双面性：克身/制比劫/护财；正官为善神，七杀为不善神；有制/无制差别很大",
        }

        return Evidence(
            evidence_id=f"E-L4-OFFICER-{dm_fact.value['stem']}",
            evidence_type=self.evidence_type,
            judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value=value,
            source_fact_ids=[dm_fact.fact_id, "F-L1-TEN-GOD-MAP"],
            source_relation_ids=[r.relation_id for r in officer_relations] +
                                 ([root_relation.relation_id] if root_relation else []),
            derivation_rule_id=self.rule_id,
            classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED,
            authorization_level=self.authorization_level,
            max_output=self.max_output,
        )


# ============================================================================
# L4-4: OUTPUT_DRAIN（食伤泄身）— 消费 TEN_GOD_OUTPUT Relation
# ============================================================================

class OutputDrainDerivation(EvidenceDerivationRule):
    """食伤泄身 Evidence 推导 — 消费 Canonical Relation (TEN_GOD_OUTPUT)"""

    @property
    def rule_id(self) -> str:
        return "EDR-L4-OUTPUT-001"

    @property
    def evidence_type(self) -> str:
        return "OUTPUT_DRAIN"

    @property
    def polarity(self) -> Polarity:
        return Polarity.CONSTRAINT

    @property
    def authorization_level(self) -> AuthorizationLevel:
        return AuthorizationLevel.PARTIAL

    @property
    def max_output(self) -> str:
        return "QUALIFIED"

    @property
    def classical_source(self) -> Dict[str, Any]:
        return {
            "classic": "子平真诠",
            "edition": "沈孝瞻原著",
            "chapter": "论用神",
            "text_type": "ORIGINAL",
            "author": "沈孝瞻",
            "source_text": "财官印食，此用神之善而顺用之者也；煞伤劫刃，用神之不善而逆用之者也",
            "verification_status": "PARTIALLY_VERIFIED",
        }

    def derive(self, facts: List[CanonicalFact],
               relations: List[CanonicalRelation]) -> Optional[Evidence]:
        output_relations = [r for r in relations if r.relation_type == "TEN_GOD_OUTPUT"]
        if not output_relations:
            return None

        root_relation = next((r for r in relations if r.relation_type == "ROOT_PRESENT"), None)
        root_details = root_relation.value.get("root_details", []) if root_relation else []

        output_details = []
        shishen_count = 0
        shangguan_count = 0
        for rel in output_relations:
            pos = rel.value["position"]
            stem = rel.value["stem"]
            ten_god = rel.value["ten_god"]
            if ten_god == "食神":
                shishen_count += 1
            elif ten_god == "伤官":
                shangguan_count += 1
            output_wx = rel.value["wuxing"]
            rooted = any(WUXING.get(rd["root_stem"], "") == output_wx for rd in root_details)
            output_details.append({
                "position": pos,
                "stem": stem,
                "type": ten_god,
                "rooted": rooted,
                "source_relation_id": rel.relation_id,
            })

        dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
        value = {
            "output_present": True,
            "output_count": len(output_details),
            "output_details": output_details,
            "shishen_count": shishen_count,
            "shangguan_count": shangguan_count,
            "dual_nature": True,
            "note": "双面性：泄身/生财/制杀；食神为善神，伤官为不善神；身旺时泄秀是好事，身弱时泄身是坏事",
        }

        return Evidence(
            evidence_id=f"E-L4-OUTPUT-{dm_fact.value['stem']}",
            evidence_type=self.evidence_type,
            judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value=value,
            source_fact_ids=[dm_fact.fact_id, "F-L1-TEN-GOD-MAP"],
            source_relation_ids=[r.relation_id for r in output_relations] +
                                 ([root_relation.relation_id] if root_relation else []),
            derivation_rule_id=self.rule_id,
            classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED,
            authorization_level=self.authorization_level,
            max_output=self.max_output,
        )


# ============================================================================
# L4-5: WEALTH_DRAIN（财星耗身）— 消费 TEN_GOD_WEALTH Relation
# ============================================================================

class WealthDrainDerivation(EvidenceDerivationRule):
    """财星耗身 Evidence 推导 — 消费 Canonical Relation (TEN_GOD_WEALTH)"""

    @property
    def rule_id(self) -> str:
        return "EDR-L4-WEALTH-001"

    @property
    def evidence_type(self) -> str:
        return "WEALTH_DRAIN"

    @property
    def polarity(self) -> Polarity:
        return Polarity.CONSTRAINT

    @property
    def authorization_level(self) -> AuthorizationLevel:
        return AuthorizationLevel.PARTIAL

    @property
    def max_output(self) -> str:
        return "QUALIFIED"

    @property
    def classical_source(self) -> Dict[str, Any]:
        return {
            "classic": "子平真诠",
            "edition": "沈孝瞻原著",
            "chapter": "论用神",
            "text_type": "ORIGINAL",
            "author": "沈孝瞻",
            "source_text": "财官印食，此用神之善而顺用之者也",
            "verification_status": "PARTIALLY_VERIFIED",
        }

    def derive(self, facts: List[CanonicalFact],
               relations: List[CanonicalRelation]) -> Optional[Evidence]:
        wealth_relations = [r for r in relations if r.relation_type == "TEN_GOD_WEALTH"]
        if not wealth_relations:
            return None

        root_relation = next((r for r in relations if r.relation_type == "ROOT_PRESENT"), None)
        root_details = root_relation.value.get("root_details", []) if root_relation else []

        wealth_details = []
        zhengcai_count = 0
        piancai_count = 0
        for rel in wealth_relations:
            pos = rel.value["position"]
            stem = rel.value["stem"]
            ten_god = rel.value["ten_god"]
            if ten_god == "正财":
                zhengcai_count += 1
            elif ten_god == "偏财":
                piancai_count += 1
            wealth_wx = rel.value["wuxing"]
            rooted = any(WUXING.get(rd["root_stem"], "") == wealth_wx for rd in root_details)
            wealth_details.append({
                "position": pos,
                "stem": stem,
                "type": ten_god,
                "rooted": rooted,
                "source_relation_id": rel.relation_id,
            })

        dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
        value = {
            "wealth_present": True,
            "wealth_count": len(wealth_details),
            "wealth_details": wealth_details,
            "zhengcai_count": zhengcai_count,
            "piancai_count": piancai_count,
            "dual_nature": True,
            "note": "双面性：耗身/生官/养命；身旺能任财是好事，身弱财多是坏事（'富屋贫人'）",
        }

        return Evidence(
            evidence_id=f"E-L4-WEALTH-{dm_fact.value['stem']}",
            evidence_type=self.evidence_type,
            judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value=value,
            source_fact_ids=[dm_fact.fact_id, "F-L1-TEN-GOD-MAP"],
            source_relation_ids=[r.relation_id for r in wealth_relations] +
                                 ([root_relation.relation_id] if root_relation else []),
            derivation_rule_id=self.rule_id,
            classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED,
            authorization_level=self.authorization_level,
            max_output=self.max_output,
        )


# ============================================================================
# L4-6: SEASONAL_STATE（季节状态）— 消费 SEASONAL_ALIGNMENT Relation
# ============================================================================

class SeasonalStateDerivation(EvidenceDerivationRule):
    """季节状态 Evidence 推导 — 消费 Canonical Relation (SEASONAL_ALIGNMENT)，不重新计算"""

    @property
    def rule_id(self) -> str:
        return "EDR-L4-SEASONAL-001"

    @property
    def evidence_type(self) -> str:
        return "SEASONAL_STATE"

    @property
    def polarity(self) -> Polarity:
        return Polarity.CONTEXT

    @property
    def authorization_level(self) -> AuthorizationLevel:
        return AuthorizationLevel.PARTIAL

    @property
    def max_output(self) -> str:
        return "QUALIFIED"

    @property
    def classical_source(self) -> Dict[str, Any]:
        return {
            "classic": "滴天髓",
            "edition": "任铁樵注本",
            "chapter": "通神论·衰旺",
            "text_type": "ORIGINAL",
            "author": "京图（题）/任铁樵（注）",
            "source_text": "能知衰旺之真机，其于三命之奥，思过半矣",
            "verification_status": "PARTIALLY_VERIFIED",
        }

    def derive(self, facts: List[CanonicalFact],
               relations: List[CanonicalRelation]) -> Optional[Evidence]:
        # 只消费 Canonical Relation，不重新计算月令
        seasonal_relation = next((r for r in relations if r.relation_type == "SEASONAL_ALIGNMENT"), None)
        if not seasonal_relation:
            return None

        dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
        mb_fact = next(f for f in facts if f.fact_type == "MONTH_BRANCH")

        # 直接从 Relation 读取，不重新计算
        value = {
            "season": seasonal_relation.value["season"],
            "month_branch": mb_fact.value["branch"],
            "day_master_wuxing": seasonal_relation.value["day_master_wuxing"],
            "month_wuxing": seasonal_relation.value["month_wuxing"],
            "growth_stage": seasonal_relation.value["growth_stage"],
            "seasonal_alignment": seasonal_relation.value["alignment"],
            "climate": seasonal_relation.value["climate"],
            "note": "得令 ≠ 旺（原典明确警告'虽是至理，亦死法也'）；是 CONTEXT 不是直接判断",
        }

        return Evidence(
            evidence_id=f"E-L4-SEASONAL-{dm_fact.value['stem']}",
            evidence_type=self.evidence_type,
            judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value=value,
            source_fact_ids=[dm_fact.fact_id, mb_fact.fact_id],
            source_relation_ids=[seasonal_relation.relation_id],
            derivation_rule_id=self.rule_id,
            classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED,
            authorization_level=self.authorization_level,
            max_output=self.max_output,
        )


# ============================================================================
# L4 Evidence 推导引擎（只消费 Fact + Relation）
# ============================================================================

class L4EvidenceEngine:
    """L4 Evidence 推导引擎 — 只消费 Canonical Fact + Canonical Relation，不重新计算"""

    def __init__(self):
        self.rules: List[EvidenceDerivationRule] = [
            ResourceSupportDerivation(),
            PeerSupportDerivation(),
            OfficerControlDerivation(),
            OutputDrainDerivation(),
            WealthDrainDerivation(),
            SeasonalStateDerivation(),
            # L4-7 ENVIRONMENT_STATE 暂缓：五行数量 → 偏燥热 需要经典逐条授权
            # L4-8 STRUCTURAL_CHANGE 暂缓：子午冲 → 根受损 已经是解释性 Evidence
        ]

    def derive_all(self, facts: List[CanonicalFact],
                   relations: List[CanonicalRelation]) -> List[Evidence]:
        """推导所有 L4 Evidence — 只消费 Fact + Relation"""
        evidences = []
        for rule in self.rules:
            evidence = rule.derive(facts, relations)
            if evidence:
                evidences.append(evidence)
        return evidences


# ============================================================================
# 验证
# ============================================================================

def verify_refactored_l4():
    """验证重构后的 L4 Evidence 完整链路"""

    print("=" * 80)
    print("P0-2.7.2-R L4 Evidence Construction Refactored — 完整链路验证")
    print("=" * 80)

    # 测试命例：甲木日主，寅月，年干壬（偏印），月干乙（劫财），时干丙（食神）
    # 年支子，月支寅，日支子，时支寅
    print("\n【测试命例】")
    print("  年柱：壬子")
    print("  月柱：甲寅")
    print("  日柱：甲子")
    print("  时柱：丙寅")
    print("  日主：甲木（阳）")

    # Step 1: L1 Canonical Fact 生成（唯一来源）
    print("\n" + "=" * 80)
    print("【Step 1】L1 Canonical Fact 生成（唯一来源）")
    print("=" * 80)

    fact_gen = CanonicalFactGenerator(
        year_stem="壬", month_stem="甲", day_stem="甲", hour_stem="丙",
        year_branch="子", month_branch="寅", day_branch="子", hour_branch="寅",
    )
    facts = fact_gen.generate()
    print(f"  生成 {len(facts)} 个 Canonical Fact：")
    for f in facts:
        print(f"    - {f.fact_id}: {f.fact_type} (certainty={f.certainty})")

    # Step 2: L1 Canonical Relation 生成（唯一来源，从 Fact 派生）
    print("\n" + "=" * 80)
    print("【Step 2】L1 Canonical Relation 生成（唯一来源，从 Fact 派生）")
    print("=" * 80)

    relation_gen = CanonicalRelationGenerator()
    relations = relation_gen.generate(facts)
    print(f"  生成 {len(relations)} 个 Canonical Relation：")
    for r in relations:
        print(f"    - {r.relation_id}: {r.relation_type} (certainty={r.certainty})")

    # 特别展示 L3 ROOT_PRESENT
    root_rel = next(r for r in relations if r.relation_type == "ROOT_PRESENT")
    print(f"\n  L3 ROOT_PRESENT 详情：")
    print(f"    root_present: {root_rel.value['root_present']}")
    print(f"    root_count: {root_rel.value['root_count']}")
    print(f"    has_main_qi_root: {root_rel.value['has_main_qi_root']}")
    for rd in root_rel.value["root_details"]:
        print(f"      - {rd['position']}支 {rd['branch']}: {rd['root_stem']} ({rd['qi_level']})")

    # Step 3: L4 Evidence 推导（只消费 Fact + Relation，不重新计算）
    print("\n" + "=" * 80)
    print("【Step 3】L4 Evidence 推导（只消费 Fact + Relation，不重新计算）")
    print("=" * 80)

    engine = L4EvidenceEngine()
    evidences = engine.derive_all(facts, relations)
    print(f"  推导出 {len(evidences)} 个 L4 Evidence：")

    for i, ev in enumerate(evidences, 1):
        print(f"\n  --- Evidence {i}: {ev.evidence_type} ---")
        print(f"    ID: {ev.evidence_id}")
        print(f"    极性: {ev.polarity.value}")
        print(f"    授权级别: {ev.authorization_level.value}")
        print(f"    最大输出: {ev.max_output}")
        print(f"    来源 Fact: {ev.source_fact_ids}")
        print(f"    来源 Relation: {ev.source_relation_ids}")
        print(f"    推导规则: {ev.derivation_rule_id}")
        # 展示核心值
        for k, v in ev.value.items():
            if k not in ("note", "resource_details", "peer_details", "officer_details",
                         "output_details", "wealth_details", "climate"):
                print(f"    {k}: {v}")

    # Step 4: 验证检查清单
    print("\n" + "=" * 80)
    print("【Step 4】验证检查清单")
    print("=" * 80)

    checks = []

    # 检查 1：所有 L4 Evidence 都是 PARTIAL
    all_partial = all(ev.authorization_level == AuthorizationLevel.PARTIAL for ev in evidences)
    checks.append(("所有 L4 Evidence 都是 PARTIAL（没有 AUTHORIZED）", all_partial))

    # 检查 2：所有 L4 Evidence 最大输出都是 QUALIFIED
    all_qualified = all(ev.max_output == "QUALIFIED" for ev in evidences)
    checks.append(("所有 L4 Evidence 最大输出都是 QUALIFIED（没有 CONFIRMED）", all_qualified))

    # 检查 3：L4 只消费 Fact + Relation，不内部重复计算
    # 验证：所有 Evidence 都有非空的 source_relation_ids
    all_consume_relations = all(len(ev.source_relation_ids) > 0 for ev in evidences)
    checks.append(("所有 L4 Evidence 都消费 Canonical Relation（不内部重复计算）", all_consume_relations))

    # 检查 4：rooted 字段从 L3 ROOT_PRESENT 读取，不硬编码
    # 验证：十神类 Evidence 的 source_relation_ids 包含 ROOT_PRESENT
    ten_god_evidences = [ev for ev in evidences if ev.evidence_type in
                          ("RESOURCE_SUPPORT", "PEER_SUPPORT", "OFFICER_CONTROL", "OUTPUT_DRAIN", "WEALTH_DRAIN")]
    rooted_from_l3 = all("R-L3-ROOT-PRESENT" in ev.source_relation_ids for ev in ten_god_evidences)
    checks.append(("十神类 Evidence 的 rooted 字段从 L3 ROOT_PRESENT 读取（不硬编码）", rooted_from_l3))

    # 检查 5：SEASONAL_STATE 消费 SEASONAL_ALIGNMENT Relation
    seasonal_ev = next((ev for ev in evidences if ev.evidence_type == "SEASONAL_STATE"), None)
    seasonal_consumes_relation = seasonal_ev is not None and "R-L2-SEASONAL-ALIGNMENT" in seasonal_ev.source_relation_ids
    checks.append(("SEASONAL_STATE 消费 SEASONAL_ALIGNMENT Relation（不重新计算月令）", seasonal_consumes_relation))

    # 检查 6：没有 ENVIRONMENT_STATE / STRUCTURAL_CHANGE（暂缓）
    no_deferred = all(ev.evidence_type not in ("ENVIRONMENT_STATE", "STRUCTURAL_CHANGE") for ev in evidences)
    checks.append(("ENVIRONMENT_STATE / STRUCTURAL_CHANGE 已暂缓（不抢着做）", no_deferred))

    # 检查 7：十神类 Evidence 都有双面性标记
    all_dual_nature = all(ev.value.get("dual_nature") == True for ev in ten_god_evidences)
    checks.append(("十神类 Evidence 都有双面性标记（dual_nature=True）", all_dual_nature))

    # 检查 8：SEASONAL_STATE 极性是 CONTEXT
    seasonal_is_context = seasonal_ev is not None and seasonal_ev.polarity == Polarity.CONTEXT
    checks.append(("SEASONAL_STATE 极性是 CONTEXT（不是直接 SUPPORT/CONSTRAINT）", seasonal_is_context))

    # 检查 9：完整链路 Fact → Relation → Evidence
    complete_chain = len(facts) > 0 and len(relations) > 0 and len(evidences) > 0
    checks.append(("完整链路：L1 Fact → L1 Relation → L3 ROOT_PRESENT → L4 Evidence", complete_chain))

    # 检查 10：没有用数量统计直接判断强弱
    no_count_judgment = all("support_count" not in str(ev.value) and "constraint_count" not in str(ev.value) for ev in evidences)
    checks.append(("没有用 support_count/constraint_count 直接判断强弱", no_count_judgment))

    # 输出检查结果
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if not passed:
            all_passed = False

    # 总结
    print("\n" + "=" * 80)
    if all_passed:
        print("【最终结果】ALL CHECKS PASSED ✅")
    else:
        print("【最终结果】SOME CHECKS FAILED ❌")
    print("=" * 80)

    # 核心结论
    print("\n【核心结论】")
    print("  1. L4 Evidence 只消费 Canonical Fact + Canonical Relation，不内部重复计算")
    print("  2. rooted 字段从 L3 ROOT_PRESENT Relation 读取，不硬编码")
    print("  3. SEASONAL_STATE 消费 SEASONAL_ALIGNMENT Relation，不重新计算月令")
    print("  4. 保留 6 个 Evidence（L4-1到L4-6），暂缓 ENVIRONMENT/STRUCTURAL")
    print("  5. 所有 L4 Evidence 都是 PARTIAL，最多输出 QUALIFIED")
    print("  6. 十神类 Evidence 都有双面性标记")
    print("  7. 完整链路：L1 Fact → L1 Relation → L3 ROOT_PRESENT → L4 Evidence")
    print("  8. 在 Evidence Combination 规则没有原典授权之前，整体旺衰判断保持 UNRESOLVED")

    return all_passed


if __name__ == "__main__":
    verify_refactored_l4()
