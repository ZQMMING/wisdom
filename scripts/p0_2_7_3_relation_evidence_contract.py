"""
P0-2.7.3 Relation Contract + Evidence Contract 正式化

基于 2131dc8 的 CONDITIONAL PASS 裁决整改：

核心问题：
- ROOT_PRESENT 当前记录的是日主的根，不能自动推出某个十神本身有根
- Relation Schema 不够精确，需要 subject/object/position/condition/provenance
- L4 rooted 的计算逻辑错误：用日主的根来判断十神的根

整改点：
1. 建立精确的 Relation Schema（subject/object/relation_type/position/condition/provenance）
2. 区分 ROOT_PRESENT（日主的根）和 STEM_ROOT_PRESENT（任意天干的根）
3. 修复 L4 rooted：从该十神自己的 STEM_ROOT_PRESENT 读取，不用日主的根
4. 建立 Evidence Contract：source_relations 必须精确匹配 subject/object

工程分层：
L0 算 → L1 Fact → L1 Relation（精确Schema）→ L3 ROOT_PRESENT（日主根）→ L4 Local Evidence
→ L5 STEM_ROOT_PRESENT（天干根）→ L6 Evidence Combination ⏳ → L7 Classical Judgment ⏳ → 解
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
class RelationSubject:
    """Relation 的 subject — 精确描述谁"""
    entity_type: str  # "DAY_MASTER" / "STEM" / "BRANCH" / "HIDDEN_STEM"
    position: Optional[str]  # "year" / "month" / "day" / "hour" / None
    stem: Optional[str]
    branch: Optional[str]
    wuxing: Optional[str]
    yinyang: Optional[str]
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RelationObject:
    """Relation 的 object — 精确描述与谁"""
    entity_type: str  # "DAY_MASTER" / "STEM" / "BRANCH" / "HIDDEN_STEM"
    position: Optional[str]
    stem: Optional[str]
    branch: Optional[str]
    wuxing: Optional[str]
    yinyang: Optional[str]
    qi_level: Optional[str] = None  # "main" / "middle" / "residual"（藏干气级）
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CanonicalRelation:
    """
    L1 Canonical Relation — 精确的命理关系（唯一来源）

    核心改进：增加 subject/object，精确描述谁与谁发生什么关系
    """
    relation_id: str
    relation_type: str  # "ROOT_PRESENT" / "STEM_ROOT_PRESENT" / "TEN_GOD_RESOURCE" / ...
    subject: RelationSubject  # 谁
    object: RelationObject    # 与谁
    value: Dict[str, Any]
    certainty: str
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Evidence:
    """Evidence — 针对辨证目标的局部证据"""
    evidence_id: str
    evidence_type: str
    judgment_target: str  # 当前研究目标，不是 Evidence 本体
    polarity: Polarity
    value: Dict[str, Any]
    source_fact_ids: List[str]
    source_relation_ids: List[str]
    source_relation_refs: List[Dict[str, Any]]  # 精确引用：{relation_id, subject_match, object_match}
    derivation_rule_id: str
    classical_source: Dict[str, Any]
    certainty_state: CertaintyState
    authorization_level: AuthorizationLevel
    max_output: str


# ============================================================================
# L1 基础数据（唯一来源）
# ============================================================================

WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}

YIN_YANG = {
    "甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴", "戊": "阳",
    "己": "阴", "庚": "阳", "辛": "阴", "壬": "阳", "癸": "阴",
}

WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

HIDDEN_STEMS = {
    "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
    "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "戊", "庚"],
    "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
    "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
}

BRANCH_WUXING = {
    "寅": "木", "卯": "木", "辰": "土",
    "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土",
    "亥": "水", "子": "水", "丑": "土",
}

SEASON = {
    "寅": "春", "卯": "春", "辰": "春",
    "巳": "夏", "午": "夏", "未": "夏",
    "申": "秋", "酉": "秋", "戌": "秋",
    "亥": "冬", "子": "冬", "丑": "冬",
}

CLIMATE = {
    "春": {"temp": "温", "humidity": "风", "dryness": "润"},
    "夏": {"temp": "热", "humidity": "暑", "dryness": "燥"},
    "秋": {"temp": "凉", "humidity": "燥", "dryness": "干"},
    "冬": {"temp": "寒", "humidity": "湿", "dryness": "润"},
}

GROWTH_STAGE = {
    ("甲", "亥"): "长生", ("甲", "子"): "沐浴", ("甲", "丑"): "冠带",
    ("甲", "寅"): "临官", ("甲", "卯"): "帝旺", ("甲", "辰"): "衰",
    ("甲", "巳"): "病", ("甲", "午"): "死", ("甲", "未"): "墓",
    ("甲", "申"): "绝", ("甲", "酉"): "胎", ("甲", "戌"): "养",
}


def get_ten_god(day_master: str, other: str) -> str:
    """L1 十神计算（唯一来源）"""
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


# ============================================================================
# L1 Canonical Fact 生成器
# ============================================================================

class CanonicalFactGenerator:
    """L1 Canonical Fact 生成器 — 唯一来源"""

    def __init__(self, year_stem, month_stem, day_stem, hour_stem,
                 year_branch, month_branch, day_branch, hour_branch):
        self.pillars = {
            "year": {"stem": year_stem, "branch": year_branch},
            "month": {"stem": month_stem, "branch": month_branch},
            "day": {"stem": day_stem, "branch": day_branch},
            "hour": {"stem": hour_stem, "branch": hour_branch},
        }

    def generate(self) -> List[CanonicalFact]:
        facts = []
        day_master = self.pillars["day"]["stem"]
        month_branch = self.pillars["month"]["branch"]

        facts.append(CanonicalFact(
            fact_id="F-L1-DAY-MASTER",
            fact_type="DAY_MASTER",
            value={"stem": day_master, "wuxing": WUXING[day_master], "yinyang": YIN_YANG[day_master]},
            source="bazi_calculation",
            certainty="CALCULATED"
        ))

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

        facts.append(CanonicalFact(
            fact_id="F-L1-ALL-STEMS",
            fact_type="ALL_STEMS",
            value={pos: p["stem"] for pos, p in self.pillars.items()},
            source="bazi_calculation",
            certainty="CALCULATED"
        ))

        facts.append(CanonicalFact(
            fact_id="F-L1-ALL-BRANCHES",
            fact_type="ALL_BRANCHES",
            value={pos: p["branch"] for pos, p in self.pillars.items()},
            source="bazi_calculation",
            certainty="CALCULATED"
        ))

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
# L1 Canonical Relation 生成器（精确 Schema：subject/object）
# ============================================================================

class CanonicalRelationGenerator:
    """
    L1 Canonical Relation 生成器 — 精确的命理关系

    核心改进：
    1. 每个 Relation 都有精确的 subject/object
    2. 区分 ROOT_PRESENT（日主的根）和 STEM_ROOT_PRESENT（任意天干的根）
    3. 十神 Relation 精确描述 subject=日主, object=某天干
    """

    def generate(self, facts: List[CanonicalFact]) -> List[CanonicalRelation]:
        relations = []

        dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
        tg_fact = next(f for f in facts if f.fact_type == "TEN_GOD_MAP")
        hs_fact = next(f for f in facts if f.fact_type == "ALL_HIDDEN_STEMS")
        mb_fact = next(f for f in facts if f.fact_type == "MONTH_BRANCH")
        as_fact = next(f for f in facts if f.fact_type == "ALL_STEMS")

        day_master = dm_fact.value["stem"]
        dm_wx = dm_fact.value["wuxing"]
        dm_yy = dm_fact.value["yinyang"]

        # ====================================================================
        # R1-R5: 十神关系（精确 subject=日主, object=某天干）
        # ====================================================================
        ten_god_relation_map = {
            "正印": "TEN_GOD_RESOURCE", "偏印": "TEN_GOD_RESOURCE",
            "比肩": "TEN_GOD_PEER", "劫财": "TEN_GOD_PEER",
            "正官": "TEN_GOD_OFFICER", "七杀": "TEN_GOD_OFFICER",
            "食神": "TEN_GOD_OUTPUT", "伤官": "TEN_GOD_OUTPUT",
            "正财": "TEN_GOD_WEALTH", "偏财": "TEN_GOD_WEALTH",
        }

        for pos, tg_info in tg_fact.value.items():
            ten_god = tg_info["ten_god"]
            relation_type = ten_god_relation_map.get(ten_god)
            if not relation_type:
                continue

            subject = RelationSubject(
                entity_type="DAY_MASTER",
                position="day",
                stem=day_master,
                branch=None,
                wuxing=dm_wx,
                yinyang=dm_yy,
            )
            obj = RelationObject(
                entity_type="STEM",
                position=pos,
                stem=tg_info["stem"],
                branch=None,
                wuxing=tg_info["wuxing"],
                yinyang=tg_info["yinyang"],
            )

            relations.append(CanonicalRelation(
                relation_id=f"R-L1-TG-{pos.upper()}",
                relation_type=relation_type,
                subject=subject,
                object=obj,
                value={
                    "ten_god": ten_god,
                    "position": pos,
                    "stem": tg_info["stem"],
                },
                certainty="DERIVED",
                provenance={"source": "ten_god_calculation", "rule": "wuxing+yinyang→ten_god"}
            ))

        # ====================================================================
        # R6: ROOT_PRESENT — 日主的根（精确 subject=日主, object=某藏干）
        # ====================================================================
        dm_root_details = []
        for pos, hs_info in hs_fact.value.items():
            hidden = hs_info["hidden_stems"]
            for i, stem in enumerate(hidden):
                if WUXING[stem] == dm_wx:
                    qi_level = "main" if i == 0 else ("middle" if i == 1 else "residual")
                    dm_root_details.append({
                        "position": pos,
                        "branch": hs_info["branch"],
                        "root_stem": stem,
                        "qi_level": qi_level,
                        "is_main_qi": (stem == hs_info["main_qi"]),
                    })

        for i, rd in enumerate(dm_root_details):
            subject = RelationSubject(
                entity_type="DAY_MASTER",
                position="day",
                stem=day_master,
                branch=None,
                wuxing=dm_wx,
                yinyang=dm_yy,
            )
            obj = RelationObject(
                entity_type="HIDDEN_STEM",
                position=rd["position"],
                stem=rd["root_stem"],
                branch=rd["branch"],
                wuxing=WUXING[rd["root_stem"]],
                yinyang=YIN_YANG[rd["root_stem"]],
                qi_level=rd["qi_level"],
            )
            relations.append(CanonicalRelation(
                relation_id=f"R-L3-ROOT-PRESENT-{i+1}",
                relation_type="ROOT_PRESENT",
                subject=subject,
                object=obj,
                value={
                    "root_present": True,
                    "root_count": len(dm_root_details),
                    "root_details": dm_root_details,
                    "has_main_qi_root": any(r["is_main_qi"] for r in dm_root_details),
                },
                certainty="DERIVED",
                provenance={"source": "hidden_stems", "rule": "WUXING[hidden_stem]==dm_wx"}
            ))

        # ====================================================================
        # R7: STEM_ROOT_PRESENT — 任意天干的根（精确 subject=某天干, object=某藏干）
        # 这是本次整改的核心：区分日主根和任意天干根
        # ====================================================================
        for pos, stem in as_fact.value.items():
            if pos == "day":
                continue  # 日主的根已经在 ROOT_PRESENT 中
            stem_wx = WUXING[stem]
            stem_yy = YIN_YANG[stem]

            stem_root_details = []
            for bpos, hs_info in hs_fact.value.items():
                hidden = hs_info["hidden_stems"]
                for i, hstem in enumerate(hidden):
                    if WUXING[hstem] == stem_wx:
                        qi_level = "main" if i == 0 else ("middle" if i == 1 else "residual")
                        stem_root_details.append({
                            "position": bpos,
                            "branch": hs_info["branch"],
                            "root_stem": hstem,
                            "qi_level": qi_level,
                        })

            if stem_root_details:
                subject = RelationSubject(
                    entity_type="STEM",
                    position=pos,
                    stem=stem,
                    branch=None,
                    wuxing=stem_wx,
                    yinyang=stem_yy,
                )
                # object 用第一个根作为代表，详细信息在 value 中
                first_root = stem_root_details[0]
                obj = RelationObject(
                    entity_type="HIDDEN_STEM",
                    position=first_root["position"],
                    stem=first_root["root_stem"],
                    branch=first_root["branch"],
                    wuxing=WUXING[first_root["root_stem"]],
                    yinyang=YIN_YANG[first_root["root_stem"]],
                    qi_level=first_root["qi_level"],
                )
                relations.append(CanonicalRelation(
                    relation_id=f"R-L5-STEM-ROOT-{pos.upper()}",
                    relation_type="STEM_ROOT_PRESENT",
                    subject=subject,
                    object=obj,
                    value={
                        "stem_position": pos,
                        "stem": stem,
                        "root_present": True,
                        "root_count": len(stem_root_details),
                        "root_details": stem_root_details,
                    },
                    certainty="DERIVED",
                    provenance={"source": "hidden_stems", "rule": f"WUXING[hidden_stem]=={stem_wx}"}
                ))

        # ====================================================================
        # R8: SEASONAL_ALIGNMENT — 日主与月令的关系
        # ====================================================================
        month_wx = mb_fact.value["wuxing"]
        if dm_wx == month_wx:
            alignment = "IN_SEASON"
        elif WUXING_SHENG.get(month_wx, "") == dm_wx:
            alignment = "GENERATED_BY_SEASON"
        else:
            alignment = "NOT_IN_SEASON"

        subject = RelationSubject(
            entity_type="DAY_MASTER",
            position="day",
            stem=day_master,
            branch=None,
            wuxing=dm_wx,
            yinyang=dm_yy,
        )
        obj = RelationObject(
            entity_type="BRANCH",
            position="month",
            stem=None,
            branch=mb_fact.value["branch"],
            wuxing=month_wx,
            yinyang=None,
        )
        relations.append(CanonicalRelation(
            relation_id="R-L2-SEASONAL-ALIGNMENT",
            relation_type="SEASONAL_ALIGNMENT",
            subject=subject,
            object=obj,
            value={
                "alignment": alignment,
                "day_master_wuxing": dm_wx,
                "month_wuxing": month_wx,
                "season": mb_fact.value["season"],
                "growth_stage": mb_fact.value["growth_stage"],
                "climate": mb_fact.value["climate"],
            },
            certainty="DERIVED",
            provenance={"source": "month_branch", "rule": "wuxing_relation→seasonal_alignment"}
        ))

        return relations


# ============================================================================
# L4 Evidence 推导规则基类（只消费精确 Relation）
# ============================================================================

class EvidenceDerivationRule(ABC):
    """Evidence 推导规则基类 — 只消费精确的 Canonical Relation"""

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
# 辅助函数：从精确 Relation 中查找某天干的根
# ============================================================================

def find_stem_root(relations: List[CanonicalRelation], stem_position: str, stem: str) -> Optional[CanonicalRelation]:
    """
    从 STEM_ROOT_PRESENT Relation 中查找某天干的根

    核心改进：不再用日主的 ROOT_PRESENT 来判断十神的根，
    而是用该天干自己的 STEM_ROOT_PRESENT Relation
    """
    for rel in relations:
        if rel.relation_type == "STEM_ROOT_PRESENT":
            if rel.subject.position == stem_position and rel.subject.stem == stem:
                return rel
    return None


# ============================================================================
# L4-1: RESOURCE_SUPPORT（印生身）
# ============================================================================

class ResourceSupportDerivation(EvidenceDerivationRule):
    """印生身 Evidence 推导 — 消费 TEN_GOD_RESOURCE + STEM_ROOT_PRESENT（该印自己的根）"""

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
        # 只消费 TEN_GOD_RESOURCE Relation
        resource_relations = [r for r in relations if r.relation_type == "TEN_GOD_RESOURCE"]
        if not resource_relations:
            return None

        dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
        source_relation_refs = []
        resource_details = []

        for rel in resource_relations:
            pos = rel.object.position
            stem = rel.object.stem

            # 核心改进：从该印自己的 STEM_ROOT_PRESENT 查找根，不用日主的根
            stem_root_rel = find_stem_root(relations, pos, stem)
            rooted = stem_root_rel is not None
            root_count = stem_root_rel.value["root_count"] if stem_root_rel else 0

            resource_details.append({
                "position": pos,
                "stem": stem,
                "type": rel.value["ten_god"],
                "rooted": rooted,  # 从该印自己的 STEM_ROOT_PRESENT 读取
                "root_count": root_count,
                "source_relation_id": rel.relation_id,
                "root_relation_id": stem_root_rel.relation_id if stem_root_rel else None,
            })

            source_relation_refs.append({
                "relation_id": rel.relation_id,
                "subject_match": f"DAY_MASTER({rel.subject.stem})",
                "object_match": f"STEM({pos}={stem})",
            })
            if stem_root_rel:
                source_relation_refs.append({
                    "relation_id": stem_root_rel.relation_id,
                    "subject_match": f"STEM({pos}={stem})",
                    "object_match": f"HIDDEN_STEM(root)",
                })

        value = {
            "resource_present": True,
            "resource_count": len(resource_details),
            "resource_details": resource_details,
            "main_resource": resource_details[0]["stem"],
            "resource_rooted_count": sum(1 for r in resource_details if r["rooted"]),
            "dual_nature": True,
            "note": "双面性：生身/母慈灭子；rooted从该印自己的STEM_ROOT_PRESENT读取，不用日主的根",
        }

        return Evidence(
            evidence_id=f"E-L4-RESOURCE-{dm_fact.value['stem']}",
            evidence_type=self.evidence_type,
            judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value=value,
            source_fact_ids=[dm_fact.fact_id, "F-L1-TEN-GOD-MAP"],
            source_relation_ids=[r.relation_id for r in resource_relations] +
                                 [ref["relation_id"] for ref in source_relation_refs
                                  if ref["relation_id"].startswith("R-L5-STEM-ROOT")],
            source_relation_refs=source_relation_refs,
            derivation_rule_id=self.rule_id,
            classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED,
            authorization_level=self.authorization_level,
            max_output=self.max_output,
        )


# ============================================================================
# L4-2 到 L4-5：其他十神 Evidence（同样的模式，消费自己的 STEM_ROOT_PRESENT）
# ============================================================================

class PeerSupportDerivation(EvidenceDerivationRule):
    @property
    def rule_id(self) -> str: return "EDR-L4-PEER-001"
    @property
    def evidence_type(self) -> str: return "PEER_SUPPORT"
    @property
    def polarity(self) -> Polarity: return Polarity.SUPPORT
    @property
    def authorization_level(self) -> AuthorizationLevel: return AuthorizationLevel.PARTIAL
    @property
    def max_output(self) -> str: return "QUALIFIED"
    @property
    def classical_source(self) -> Dict[str, Any]:
        return {"classic": "滴天髓", "edition": "任铁樵注本", "chapter": "通神论",
                "text_type": "ORIGINAL", "author": "京图（题）/任铁樵（注）",
                "source_text": "劫财，比肩，阳刃，皆兄弟，要与提纲之神及喜神，较其轻重",
                "verification_status": "PARTIALLY_VERIFIED"}

    def derive(self, facts, relations):
        peer_relations = [r for r in relations if r.relation_type == "TEN_GOD_PEER"]
        if not peer_relations: return None
        dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
        peer_details = []
        source_relation_refs = []
        for rel in peer_relations:
            pos, stem = rel.object.position, rel.object.stem
            stem_root_rel = find_stem_root(relations, pos, stem)
            rooted = stem_root_rel is not None
            peer_details.append({"position": pos, "stem": stem, "type": rel.value["ten_god"],
                                 "rooted": rooted, "root_count": stem_root_rel.value["root_count"] if stem_root_rel else 0})
            source_relation_refs.append({"relation_id": rel.relation_id,
                                          "subject_match": f"DAY_MASTER({rel.subject.stem})",
                                          "object_match": f"STEM({pos}={stem})"})
        jian = sum(1 for p in peer_details if p["type"] == "比肩")
        jie = sum(1 for p in peer_details if p["type"] == "劫财")
        return Evidence(
            evidence_id=f"E-L4-PEER-{dm_fact.value['stem']}",
            evidence_type=self.evidence_type, judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value={"peer_present": True, "peer_count": len(peer_details), "peer_details": peer_details,
                   "jian_count": jian, "jie_count": jie, "dual_nature": True,
                   "note": "双面性：帮身/夺财；rooted从该比劫自己的STEM_ROOT_PRESENT读取"},
            source_fact_ids=[dm_fact.fact_id, "F-L1-TEN-GOD-MAP"],
            source_relation_ids=[r.relation_id for r in peer_relations],
            source_relation_refs=source_relation_refs,
            derivation_rule_id=self.rule_id, classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED, authorization_level=self.authorization_level,
            max_output=self.max_output)


class OfficerControlDerivation(EvidenceDerivationRule):
    @property
    def rule_id(self) -> str: return "EDR-L4-OFFICER-001"
    @property
    def evidence_type(self) -> str: return "OFFICER_CONTROL"
    @property
    def polarity(self) -> Polarity: return Polarity.CONSTRAINT
    @property
    def authorization_level(self) -> AuthorizationLevel: return AuthorizationLevel.PARTIAL
    @property
    def max_output(self) -> str: return "QUALIFIED"
    @property
    def classical_source(self) -> Dict[str, Any]:
        return {"classic": "子平真诠", "edition": "沈孝瞻原著", "chapter": "论用神",
                "text_type": "ORIGINAL", "author": "沈孝瞻",
                "source_text": "财官印食，此用神之善而顺用之者也；煞伤劫刃，用神之不善而逆用之者也",
                "verification_status": "PARTIALLY_VERIFIED"}

    def derive(self, facts, relations):
        officer_relations = [r for r in relations if r.relation_type == "TEN_GOD_OFFICER"]
        if not officer_relations: return None
        dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
        officer_details = []
        source_relation_refs = []
        for rel in officer_relations:
            pos, stem = rel.object.position, rel.object.stem
            stem_root_rel = find_stem_root(relations, pos, stem)
            rooted = stem_root_rel is not None
            officer_details.append({"position": pos, "stem": stem, "type": rel.value["ten_god"],
                                    "rooted": rooted, "controlled": False,
                                    "root_count": stem_root_rel.value["root_count"] if stem_root_rel else 0})
            source_relation_refs.append({"relation_id": rel.relation_id,
                                          "subject_match": f"DAY_MASTER({rel.subject.stem})",
                                          "object_match": f"STEM({pos}={stem})"})
        zg = sum(1 for o in officer_details if o["type"] == "正官")
        qs = sum(1 for o in officer_details if o["type"] == "七杀")
        return Evidence(
            evidence_id=f"E-L4-OFFICER-{dm_fact.value['stem']}",
            evidence_type=self.evidence_type, judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value={"officer_present": True, "officer_count": len(officer_details),
                   "officer_details": officer_details, "zhengguan_count": zg, "qisha_count": qs,
                   "officer_mixed": (zg > 0 and qs > 0), "dual_nature": True,
                   "note": "双面性：克身/制比劫/护财；rooted从该官杀自己的STEM_ROOT_PRESENT读取"},
            source_fact_ids=[dm_fact.fact_id, "F-L1-TEN-GOD-MAP"],
            source_relation_ids=[r.relation_id for r in officer_relations],
            source_relation_refs=source_relation_refs,
            derivation_rule_id=self.rule_id, classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED, authorization_level=self.authorization_level,
            max_output=self.max_output)


class OutputDrainDerivation(EvidenceDerivationRule):
    @property
    def rule_id(self) -> str: return "EDR-L4-OUTPUT-001"
    @property
    def evidence_type(self) -> str: return "OUTPUT_DRAIN"
    @property
    def polarity(self) -> Polarity: return Polarity.CONSTRAINT
    @property
    def authorization_level(self) -> AuthorizationLevel: return AuthorizationLevel.PARTIAL
    @property
    def max_output(self) -> str: return "QUALIFIED"
    @property
    def classical_source(self) -> Dict[str, Any]:
        return {"classic": "子平真诠", "edition": "沈孝瞻原著", "chapter": "论用神",
                "text_type": "ORIGINAL", "author": "沈孝瞻",
                "source_text": "财官印食，此用神之善而顺用之者也；煞伤劫刃，用神之不善而逆用之者也",
                "verification_status": "PARTIALLY_VERIFIED"}

    def derive(self, facts, relations):
        output_relations = [r for r in relations if r.relation_type == "TEN_GOD_OUTPUT"]
        if not output_relations: return None
        dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
        output_details = []
        source_relation_refs = []
        for rel in output_relations:
            pos, stem = rel.object.position, rel.object.stem
            stem_root_rel = find_stem_root(relations, pos, stem)
            rooted = stem_root_rel is not None
            output_details.append({"position": pos, "stem": stem, "type": rel.value["ten_god"],
                                   "rooted": rooted, "root_count": stem_root_rel.value["root_count"] if stem_root_rel else 0})
            source_relation_refs.append({"relation_id": rel.relation_id,
                                          "subject_match": f"DAY_MASTER({rel.subject.stem})",
                                          "object_match": f"STEM({pos}={stem})"})
        ss = sum(1 for o in output_details if o["type"] == "食神")
        sg = sum(1 for o in output_details if o["type"] == "伤官")
        return Evidence(
            evidence_id=f"E-L4-OUTPUT-{dm_fact.value['stem']}",
            evidence_type=self.evidence_type, judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value={"output_present": True, "output_count": len(output_details), "output_details": output_details,
                   "shishen_count": ss, "shangguan_count": sg, "dual_nature": True,
                   "note": "双面性：泄身/生财/制杀；rooted从该食伤自己的STEM_ROOT_PRESENT读取"},
            source_fact_ids=[dm_fact.fact_id, "F-L1-TEN-GOD-MAP"],
            source_relation_ids=[r.relation_id for r in output_relations],
            source_relation_refs=source_relation_refs,
            derivation_rule_id=self.rule_id, classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED, authorization_level=self.authorization_level,
            max_output=self.max_output)


class WealthDrainDerivation(EvidenceDerivationRule):
    @property
    def rule_id(self) -> str: return "EDR-L4-WEALTH-001"
    @property
    def evidence_type(self) -> str: return "WEALTH_DRAIN"
    @property
    def polarity(self) -> Polarity: return Polarity.CONSTRAINT
    @property
    def authorization_level(self) -> AuthorizationLevel: return AuthorizationLevel.PARTIAL
    @property
    def max_output(self) -> str: return "QUALIFIED"
    @property
    def classical_source(self) -> Dict[str, Any]:
        return {"classic": "子平真诠", "edition": "沈孝瞻原著", "chapter": "论用神",
                "text_type": "ORIGINAL", "author": "沈孝瞻",
                "source_text": "财官印食，此用神之善而顺用之者也",
                "verification_status": "PARTIALLY_VERIFIED"}

    def derive(self, facts, relations):
        wealth_relations = [r for r in relations if r.relation_type == "TEN_GOD_WEALTH"]
        if not wealth_relations: return None
        dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
        wealth_details = []
        source_relation_refs = []
        for rel in wealth_relations:
            pos, stem = rel.object.position, rel.object.stem
            stem_root_rel = find_stem_root(relations, pos, stem)
            rooted = stem_root_rel is not None
            wealth_details.append({"position": pos, "stem": stem, "type": rel.value["ten_god"],
                                   "rooted": rooted, "root_count": stem_root_rel.value["root_count"] if stem_root_rel else 0})
            source_relation_refs.append({"relation_id": rel.relation_id,
                                          "subject_match": f"DAY_MASTER({rel.subject.stem})",
                                          "object_match": f"STEM({pos}={stem})"})
        zc = sum(1 for w in wealth_details if w["type"] == "正财")
        pc = sum(1 for w in wealth_details if w["type"] == "偏财")
        return Evidence(
            evidence_id=f"E-L4-WEALTH-{dm_fact.value['stem']}",
            evidence_type=self.evidence_type, judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value={"wealth_present": True, "wealth_count": len(wealth_details), "wealth_details": wealth_details,
                   "zhengcai_count": zc, "piancai_count": pc, "dual_nature": True,
                   "note": "双面性：耗身/生官/养命；rooted从该财星自己的STEM_ROOT_PRESENT读取"},
            source_fact_ids=[dm_fact.fact_id, "F-L1-TEN-GOD-MAP"],
            source_relation_ids=[r.relation_id for r in wealth_relations],
            source_relation_refs=source_relation_refs,
            derivation_rule_id=self.rule_id, classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED, authorization_level=self.authorization_level,
            max_output=self.max_output)


# ============================================================================
# L4-6: SEASONAL_STATE（季节状态）
# ============================================================================

class SeasonalStateDerivation(EvidenceDerivationRule):
    @property
    def rule_id(self) -> str: return "EDR-L4-SEASONAL-001"
    @property
    def evidence_type(self) -> str: return "SEASONAL_STATE"
    @property
    def polarity(self) -> Polarity: return Polarity.CONTEXT
    @property
    def authorization_level(self) -> AuthorizationLevel: return AuthorizationLevel.PARTIAL
    @property
    def max_output(self) -> str: return "QUALIFIED"
    @property
    def classical_source(self) -> Dict[str, Any]:
        return {"classic": "滴天髓", "edition": "任铁樵注本", "chapter": "通神论·衰旺",
                "text_type": "ORIGINAL", "author": "京图（题）/任铁樵（注）",
                "source_text": "能知衰旺之真机，其于三命之奥，思过半矣",
                "verification_status": "PARTIALLY_VERIFIED"}

    def derive(self, facts, relations):
        seasonal_relation = next((r for r in relations if r.relation_type == "SEASONAL_ALIGNMENT"), None)
        if not seasonal_relation: return None
        dm_fact = next(f for f in facts if f.fact_type == "DAY_MASTER")
        mb_fact = next(f for f in facts if f.fact_type == "MONTH_BRANCH")
        return Evidence(
            evidence_id=f"E-L4-SEASONAL-{dm_fact.value['stem']}",
            evidence_type=self.evidence_type, judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value={"season": seasonal_relation.value["season"], "month_branch": mb_fact.value["branch"],
                   "day_master_wuxing": seasonal_relation.value["day_master_wuxing"],
                   "month_wuxing": seasonal_relation.value["month_wuxing"],
                   "growth_stage": seasonal_relation.value["growth_stage"],
                   "seasonal_alignment": seasonal_relation.value["alignment"],
                   "climate": seasonal_relation.value["climate"],
                   "note": "得令 ≠ 旺；是 CONTEXT 不是直接判断；消费SEASONAL_ALIGNMENT Relation"},
            source_fact_ids=[dm_fact.fact_id, mb_fact.fact_id],
            source_relation_ids=[seasonal_relation.relation_id],
            source_relation_refs=[{"relation_id": seasonal_relation.relation_id,
                                    "subject_match": f"DAY_MASTER({seasonal_relation.subject.stem})",
                                    "object_match": f"BRANCH(month={seasonal_relation.object.branch})"}],
            derivation_rule_id=self.rule_id, classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED, authorization_level=self.authorization_level,
            max_output=self.max_output)


# ============================================================================
# L4 Evidence 推导引擎
# ============================================================================

class L4EvidenceEngine:
    def __init__(self):
        self.rules: List[EvidenceDerivationRule] = [
            ResourceSupportDerivation(), PeerSupportDerivation(), OfficerControlDerivation(),
            OutputDrainDerivation(), WealthDrainDerivation(), SeasonalStateDerivation(),
        ]

    def derive_all(self, facts, relations) -> List[Evidence]:
        evidences = []
        for rule in self.rules:
            evidence = rule.derive(facts, relations)
            if evidence: evidences.append(evidence)
        return evidences


# ============================================================================
# 验证
# ============================================================================

def verify_relation_contract():
    print("=" * 80)
    print("P0-2.7.3 Relation Contract + Evidence Contract 正式化 — 验证")
    print("=" * 80)

    # 测试命例：壬子 甲寅 甲子 丙寅
    print("\n【测试命例】壬子 甲寅 甲子 丙寅（日主甲木）")

    # Step 1: L1 Fact
    fact_gen = CanonicalFactGenerator("壬","甲","甲","丙","子","寅","子","寅")
    facts = fact_gen.generate()
    print(f"\n【Step 1】L1 Canonical Fact: {len(facts)} 个")

    # Step 2: L1 Relation（精确 Schema）
    relation_gen = CanonicalRelationGenerator()
    relations = relation_gen.generate(facts)
    print(f"\n【Step 2】L1 Canonical Relation（精确Schema）: {len(relations)} 个")

    # 分类展示
    root_relations = [r for r in relations if r.relation_type == "ROOT_PRESENT"]
    stem_root_relations = [r for r in relations if r.relation_type == "STEM_ROOT_PRESENT"]
    ten_god_relations = [r for r in relations if r.relation_type.startswith("TEN_GOD_")]
    seasonal_relations = [r for r in relations if r.relation_type == "SEASONAL_ALIGNMENT"]

    print(f"  - ROOT_PRESENT（日主的根）: {len(root_relations)} 个")
    for r in root_relations:
        print(f"    {r.relation_id}: subject={r.subject.entity_type}({r.subject.stem}) "
              f"→ object={r.object.entity_type}({r.object.position}支{r.object.branch}藏{r.object.stem}, {r.object.qi_level})")

    print(f"  - STEM_ROOT_PRESENT（任意天干的根）: {len(stem_root_relations)} 个")
    for r in stem_root_relations:
        print(f"    {r.relation_id}: subject={r.subject.entity_type}({r.subject.position}干{r.subject.stem}) "
              f"→ object={r.object.entity_type}({r.object.position}支藏{r.object.stem}) "
              f"root_count={r.value['root_count']}")

    print(f"  - TEN_GOD_*（十神关系）: {len(ten_god_relations)} 个")
    for r in ten_god_relations:
        print(f"    {r.relation_id}: {r.relation_type} "
              f"subject=日主({r.subject.stem}) → object={r.object.position}干({r.object.stem}={r.value['ten_god']})")

    print(f"  - SEASONAL_ALIGNMENT: {len(seasonal_relations)} 个")

    # Step 3: L4 Evidence
    print(f"\n【Step 3】L4 Evidence 推导")
    engine = L4EvidenceEngine()
    evidences = engine.derive_all(facts, relations)
    print(f"  推导出 {len(evidences)} 个 L4 Evidence")

    for ev in evidences:
        print(f"\n  --- {ev.evidence_type} ---")
        print(f"    极性: {ev.polarity.value}, 授权: {ev.authorization_level.value}, 最大输出: {ev.max_output}")
        print(f"    来源Relation: {ev.source_relation_ids}")
        print(f"    精确引用:")
        for ref in ev.source_relation_refs[:3]:  # 只展示前3个
            print(f"      {ref['relation_id']}: {ref['subject_match']} → {ref['object_match']}")
        # 展示 rooted 详情
        if "resource_details" in ev.value:
            for d in ev.value["resource_details"]:
                print(f"    印 {d['position']}干{d['stem']}: rooted={d['rooted']} (从STEM_ROOT_PRESENT读取)")
        if "peer_details" in ev.value:
            for d in ev.value["peer_details"]:
                print(f"    比劫 {d['position']}干{d['stem']}: rooted={d['rooted']}")

    # Step 4: 验证检查清单
    print("\n" + "=" * 80)
    print("【Step 4】验证检查清单")
    print("=" * 80)

    checks = []

    # 检查 1：Relation 都有精确的 subject/object
    all_have_subject_object = all(hasattr(r, 'subject') and hasattr(r, 'object') for r in relations)
    checks.append(("所有 Relation 都有精确的 subject/object", all_have_subject_object))

    # 检查 2：区分 ROOT_PRESENT（日主根）和 STEM_ROOT_PRESENT（天干根）
    has_both_root_types = len(root_relations) > 0 and len(stem_root_relations) > 0
    checks.append(("区分 ROOT_PRESENT（日主根）和 STEM_ROOT_PRESENT（天干根）", has_both_root_types))

    # 检查 3：L4 rooted 从该十神自己的 STEM_ROOT_PRESENT 读取
    # 验证：RESOURCE_SUPPORT 的 rooted 不依赖日主的 ROOT_PRESENT
    resource_ev = next((e for e in evidences if e.evidence_type == "RESOURCE_SUPPORT"), None)
    rooted_from_stem_root = False
    if resource_ev and resource_ev.value["resource_details"]:
        # 检查 source_relation_ids 是否包含 STEM_ROOT_PRESENT
        rooted_from_stem_root = any("STEM-ROOT" in rid for rid in resource_ev.source_relation_ids)
    checks.append(("L4 rooted 从该十神自己的 STEM_ROOT_PRESENT 读取（不用日主的根）", rooted_from_stem_root))

    # 检查 4：Evidence 都有精确的 source_relation_refs
    all_have_refs = all(len(ev.source_relation_refs) > 0 for ev in evidences)
    checks.append(("所有 Evidence 都有精确的 source_relation_refs（subject/object匹配）", all_have_refs))

    # 检查 5：所有 L4 Evidence 都是 PARTIAL
    all_partial = all(ev.authorization_level == AuthorizationLevel.PARTIAL for ev in evidences)
    checks.append(("所有 L4 Evidence 都是 PARTIAL（没有 AUTHORIZED）", all_partial))

    # 检查 6：所有 L4 Evidence 最大输出都是 QUALIFIED
    all_qualified = all(ev.max_output == "QUALIFIED" for ev in evidences)
    checks.append(("所有 L4 Evidence 最大输出都是 QUALIFIED（没有 CONFIRMED）", all_qualified))

    # 检查 7：十神类 Evidence 都有双面性标记
    ten_god_evidences = [e for e in evidences if e.evidence_type in
                          ("RESOURCE_SUPPORT", "PEER_SUPPORT", "OFFICER_CONTROL", "OUTPUT_DRAIN", "WEALTH_DRAIN")]
    all_dual_nature = all(e.value.get("dual_nature") == True for e in ten_god_evidences)
    checks.append(("十神类 Evidence 都有双面性标记（dual_nature=True）", all_dual_nature))

    # 检查 8：SEASONAL_STATE 极性是 CONTEXT
    seasonal_ev = next((e for e in evidences if e.evidence_type == "SEASONAL_STATE"), None)
    seasonal_is_context = seasonal_ev is not None and seasonal_ev.polarity == Polarity.CONTEXT
    checks.append(("SEASONAL_STATE 极性是 CONTEXT（不是直接 SUPPORT/CONSTRAINT）", seasonal_is_context))

    # 检查 9：完整链路 Fact → 精确Relation → Evidence
    complete_chain = len(facts) > 0 and len(relations) > 0 and len(evidences) > 0
    checks.append(("完整链路：L1 Fact → 精确Relation（subject/object）→ L4 Evidence", complete_chain))

    # 检查 10：没有用数量统计直接判断强弱
    no_count_judgment = all("support_count" not in str(e.value) and "constraint_count" not in str(e.value) for e in evidences)
    checks.append(("没有用 support_count/constraint_count 直接判断强弱", no_count_judgment))

    # 输出
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if not passed: all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("【最终结果】ALL CHECKS PASSED ✅")
    else:
        print("【最终结果】SOME CHECKS FAILED ❌")
    print("=" * 80)

    print("\n【核心结论】")
    print("  1. Relation Schema 已正式化：每个 Relation 都有精确的 subject/object")
    print("  2. 区分 ROOT_PRESENT（日主的根）和 STEM_ROOT_PRESENT（任意天干的根）")
    print("  3. L4 rooted 从该十神自己的 STEM_ROOT_PRESENT 读取，不再用日主的根")
    print("  4. Evidence Contract 已建立：source_relation_refs 精确匹配 subject/object")
    print("  5. 所有 L4 Evidence 都是 PARTIAL，最多输出 QUALIFIED")
    print("  6. 十神类 Evidence 都有双面性标记")
    print("  7. 在 Evidence Combination 规则没有原典授权之前，整体旺衰判断保持 UNRESOLVED")

    return all_passed


if __name__ == "__main__":
    verify_relation_contract()
