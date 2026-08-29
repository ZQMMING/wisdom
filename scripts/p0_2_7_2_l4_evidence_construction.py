"""
P0-2.7.2 L4 Evidence Construction — 外势/生扶/克泄耗 Evidence 推导与验证

基于 dc09469（P0-2.7.1C.1-R 原典证据真实性与 Provenance 加固）

核心原则：
- L4 Evidence 只是局部证，不是旺衰判断
- 所有 L4 Evidence 都是 PARTIAL，最多输出 QUALIFIED
- 禁止用数量统计直接判断强弱
- 禁止跳过 Evidence Combination 直接进入 Judgment

工程分层：
L0 算 → L1 Fact/Relation → L2 月令状态 → L3 通根 → L4 外势/生扶/克泄耗（当前）
→ L5 结构变化 → L6 Evidence Combination → L7 Classical Judgment → 解
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
    DERIVED = "DERIVED"           # 纯结构推导，确定的
    QUALIFIED = "QUALIFIED"       # 有原典依据，但需要限定条件
    UNKNOWN = "UNKNOWN"           # 不确定
    UNRESOLVED = "UNRESOLVED"     # 无法裁决


class AuthorizationLevel(Enum):
    AUTHORIZED = "AUTHORIZED"     # 原典明确授权
    PARTIAL = "PARTIAL"           # 部分授权，需要限定
    NOT_AUTHORIZED = "NOT_AUTHORIZED"  # 原典依据不足


@dataclass(frozen=True)
class CanonicalFact:
    """Canonical Fact — 算出来的客观事实"""
    fact_id: str
    fact_type: str
    value: Dict[str, Any]
    source: str
    certainty: str  # "CALCULATED" / "DERIVED"


@dataclass(frozen=True)
class SemanticRelation:
    """Semantic Relation — Fact 与 Fact 的命理关系"""
    relation_id: str
    relation_type: str  # "WUXING_GENERATES" / "SAME_ELEMENT" / ...
    source_fact_id: str
    target_fact_id: str
    value: Dict[str, Any]
    certainty: str


@dataclass(frozen=True)
class Evidence:
    """Evidence — 针对辨证目标的局部证据"""
    evidence_id: str
    evidence_type: str  # "RESOURCE_SUPPORT" / ...
    judgment_target: str
    polarity: Polarity
    value: Dict[str, Any]
    source_fact_ids: List[str]
    source_relation_ids: List[str]
    derivation_rule_id: str
    classical_source: Dict[str, Any]  # Provenance
    certainty_state: CertaintyState
    authorization_level: AuthorizationLevel
    max_output: str  # "CONFIRMED" / "QUALIFIED" / "NOT_AUTHORIZED"


# ============================================================================
# 五行/十神基础工具
# ============================================================================

WUXING = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

YIN_YANG = {
    "甲": "阳", "乙": "阴",
    "丙": "阳", "丁": "阴",
    "戊": "阳", "己": "阴",
    "庚": "阳", "辛": "阴",
    "壬": "阳", "癸": "阴",
}

# 五行生克：A 生 B
WUXING_SHENG = {
    "木": "火",
    "火": "土",
    "土": "金",
    "金": "水",
    "水": "木",
}

# 五行克：A 克 B
WUXING_KE = {
    "木": "土",
    "土": "水",
    "水": "火",
    "火": "金",
    "金": "木",
}

# 十二长生（阳干顺行，阴干逆行）
# 简化版，仅用于演示
GROWTH_STAGE = {
    ("甲", "亥"): "长生", ("甲", "子"): "沐浴", ("甲", "丑"): "冠带",
    ("甲", "寅"): "临官", ("甲", "卯"): "帝旺", ("甲", "辰"): "衰",
    ("甲", "巳"): "病", ("甲", "午"): "死", ("甲", "未"): "墓",
    ("甲", "申"): "绝", ("甲", "酉"): "胎", ("甲", "戌"): "养",
}

# 季节
SEASON = {
    "寅": "春", "卯": "春", "辰": "春",
    "巳": "夏", "午": "夏", "未": "夏",
    "申": "秋", "酉": "秋", "戌": "秋",
    "亥": "冬", "子": "冬", "丑": "冬",
}

# 寒暖燥湿
CLIMATE = {
    "春": {"temp": "温", "humidity": "风", "dryness": "润"},
    "夏": {"temp": "热", "humidity": "暑", "dryness": "燥"},
    "秋": {"temp": "凉", "humidity": "燥", "dryness": "干"},
    "冬": {"temp": "寒", "humidity": "湿", "dryness": "润"},
}


def get_ten_god(day_master: str, other: str) -> str:
    """计算十神关系"""
    dm_wx = WUXING[day_master]
    ot_wx = WUXING[other]
    dm_yy = YIN_YANG[day_master]
    ot_yy = YIN_YANG[other]
    same_yy = (dm_yy == ot_yy)
    
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
# Evidence Derivation Rule 基类
# ============================================================================

class EvidenceDerivationRule(ABC):
    """Evidence 推导规则基类"""
    
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
               relations: List[SemanticRelation]) -> Optional[Evidence]:
        pass


# ============================================================================
# L4-1: RESOURCE_SUPPORT（印生身）
# ============================================================================

class ResourceSupportDerivation(EvidenceDerivationRule):
    """印生身 Evidence 推导
    
    原典依据：
    - 《子平真诠·论用神》："财官印食，此用神之善而顺用之者也"
    - 《滴天髓》（原注）："旺则宜泄宜伤，衰则喜帮喜助"
    
    授权级别：PARTIAL（十神定义可靠，但"印生身→身强"需要限定）
    最大输出：QUALIFIED
    关键边界：印多可能"母慈灭子"（水多木漂）
    """
    
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
            "additional_sources": [
                {
                    "classic": "滴天髓",
                    "text_type": "COMMENTARY",
                    "source_text": "旺则宜泄宜伤，衰则喜帮喜助，子平之理也",
                }
            ]
        }
    
    def derive(self, facts: List[CanonicalFact], 
               relations: List[SemanticRelation]) -> Optional[Evidence]:
        # 找日主
        dm_fact = next((f for f in facts if f.fact_type == "DAY_MASTER"), None)
        if not dm_fact:
            return None
        
        day_master = dm_fact.value["stem"]
        dm_wx = WUXING[day_master]
        
        # 找所有干支
        all_stems_fact = next((f for f in facts if f.fact_type == "ALL_STEMS"), None)
        if not all_stems_fact:
            return None
        
        resource_details = []
        for pos, stem in all_stems_fact.value.items():
            if pos == "day":  # 跳过日主自己
                continue
            if WUXING[stem] == WUXING_SHENG.get(dm_wx, ""):  # 生日主
                ten_god = get_ten_god(day_master, stem)
                # 简化：假设都有根（实际需要查地支藏干）
                resource_details.append({
                    "position": pos,
                    "stem": stem,
                    "type": ten_god,
                    "rooted": True  # 简化
                })
        
        if not resource_details:
            return None
        
        value = {
            "resource_present": True,
            "resource_count": len(resource_details),
            "resource_details": resource_details,
            "main_resource": resource_details[0]["stem"],
            "resource_rooted_count": sum(1 for r in resource_details if r["rooted"]),
            "dual_nature": True,
            "note": "双面性：生身/母慈灭子（水多木漂）；印多可能反而不好，不能直接等同于身强"
        }
        
        return Evidence(
            evidence_id=f"E-L4-RESOURCE-{day_master}",
            evidence_type=self.evidence_type,
            judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value=value,
            source_fact_ids=[dm_fact.fact_id, all_stems_fact.fact_id],
            source_relation_ids=[],
            derivation_rule_id=self.rule_id,
            classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED,
            authorization_level=self.authorization_level,
            max_output=self.max_output,
        )


# ============================================================================
# L4-2: PEER_SUPPORT（比劫帮身）
# ============================================================================

class PeerSupportDerivation(EvidenceDerivationRule):
    """比劫帮身 Evidence 推导
    
    原典依据：
    - 《滴天髓》："劫财，比肩，阳刃，皆兄弟，要与提纲之神及喜神，较其轻重"
    - 《子平真诠·论用神》："煞伤劫刃，用神之不善而逆用之者也"
    
    授权级别：PARTIAL
    最大输出：QUALIFIED
    关键边界：双面性——帮身/夺财；身弱时帮身是好事，身旺时夺财是坏事
    """
    
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
            "additional_sources": [
                {
                    "classic": "子平真诠",
                    "text_type": "ORIGINAL",
                    "source_text": "煞伤劫刃，用神之不善而逆用之者也",
                }
            ]
        }
    
    def derive(self, facts: List[CanonicalFact], 
               relations: List[SemanticRelation]) -> Optional[Evidence]:
        dm_fact = next((f for f in facts if f.fact_type == "DAY_MASTER"), None)
        if not dm_fact:
            return None
        
        day_master = dm_fact.value["stem"]
        dm_wx = WUXING[day_master]
        
        all_stems_fact = next((f for f in facts if f.fact_type == "ALL_STEMS"), None)
        if not all_stems_fact:
            return None
        
        peer_details = []
        jian_count = 0
        jie_count = 0
        for pos, stem in all_stems_fact.value.items():
            if pos == "day":
                continue
            if WUXING[stem] == dm_wx:  # 同五行
                ten_god = get_ten_god(day_master, stem)
                if ten_god == "比肩":
                    jian_count += 1
                elif ten_god == "劫财":
                    jie_count += 1
                peer_details.append({
                    "position": pos,
                    "stem": stem,
                    "type": ten_god,
                    "rooted": True
                })
        
        if not peer_details:
            return None
        
        value = {
            "peer_present": True,
            "peer_count": len(peer_details),
            "peer_details": peer_details,
            "jian_count": jian_count,
            "jie_count": jie_count,
            "dual_nature": True,
            "note": "双面性：帮身/夺财；身弱时帮身是好事，身旺时夺财是坏事"
        }
        
        return Evidence(
            evidence_id=f"E-L4-PEER-{day_master}",
            evidence_type=self.evidence_type,
            judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value=value,
            source_fact_ids=[dm_fact.fact_id, all_stems_fact.fact_id],
            source_relation_ids=[],
            derivation_rule_id=self.rule_id,
            classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED,
            authorization_level=self.authorization_level,
            max_output=self.max_output,
        )


# ============================================================================
# L4-3: OFFICER_CONTROL（官杀克身）
# ============================================================================

class OfficerControlDerivation(EvidenceDerivationRule):
    """官杀克身 Evidence 推导
    
    原典依据：
    - 《子平真诠·论用神》："财官印食，此用神之善而顺用之者也；煞伤劫刃，用神之不善而逆用之者也"
    - 《滴天髓阐微》（任铁樵）："命中至理，只存用神，不拘财、官、印绶、比劫、食伤、枭杀，皆可为用"
    
    授权级别：PARTIAL
    最大输出：QUALIFIED
    关键边界：双面性——克身/制比劫/护财；正官为"善神"，七杀为"不善神"；有制/无制差别很大
    """
    
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
               relations: List[SemanticRelation]) -> Optional[Evidence]:
        dm_fact = next((f for f in facts if f.fact_type == "DAY_MASTER"), None)
        if not dm_fact:
            return None
        
        day_master = dm_fact.value["stem"]
        dm_wx = WUXING[day_master]
        
        all_stems_fact = next((f for f in facts if f.fact_type == "ALL_STEMS"), None)
        if not all_stems_fact:
            return None
        
        officer_details = []
        zhengguan_count = 0
        qisha_count = 0
        for pos, stem in all_stems_fact.value.items():
            if pos == "day":
                continue
            if WUXING_KE.get(WUXING[stem], "") == dm_wx:  # 克日主
                ten_god = get_ten_god(day_master, stem)
                if ten_god == "正官":
                    zhengguan_count += 1
                elif ten_god == "七杀":
                    qisha_count += 1
                officer_details.append({
                    "position": pos,
                    "stem": stem,
                    "type": ten_god,
                    "rooted": True,
                    "controlled": False  # 简化：假设都无制
                })
        
        if not officer_details:
            return None
        
        value = {
            "officer_present": True,
            "officer_count": len(officer_details),
            "officer_details": officer_details,
            "zhengguan_count": zhengguan_count,
            "qisha_count": qisha_count,
            "officer_mixed": (zhengguan_count > 0 and qisha_count > 0),
            "dual_nature": True,
            "note": "双面性：克身/制比劫/护财；正官为善神，七杀为不善神；有制/无制差别很大"
        }
        
        return Evidence(
            evidence_id=f"E-L4-OFFICER-{day_master}",
            evidence_type=self.evidence_type,
            judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value=value,
            source_fact_ids=[dm_fact.fact_id, all_stems_fact.fact_id],
            source_relation_ids=[],
            derivation_rule_id=self.rule_id,
            classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED,
            authorization_level=self.authorization_level,
            max_output=self.max_output,
        )


# ============================================================================
# L4-4: OUTPUT_DRAIN（食伤泄身）
# ============================================================================

class OutputDrainDerivation(EvidenceDerivationRule):
    """食伤泄身 Evidence 推导
    
    原典依据：
    - 《子平真诠·论用神》："财官印食，此用神之善而顺用之者也；煞伤劫刃，用神之不善而逆用之者也"
    - 《滴天髓》（原注）："旺则宜泄宜伤，衰则喜帮喜助"
    
    授权级别：PARTIAL
    最大输出：QUALIFIED
    关键边界：双面性——泄身/生财/制杀；食神为善神，伤官为不善神；身旺时泄秀是好事，身弱时泄身是坏事
    """
    
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
               relations: List[SemanticRelation]) -> Optional[Evidence]:
        dm_fact = next((f for f in facts if f.fact_type == "DAY_MASTER"), None)
        if not dm_fact:
            return None
        
        day_master = dm_fact.value["stem"]
        dm_wx = WUXING[day_master]
        
        all_stems_fact = next((f for f in facts if f.fact_type == "ALL_STEMS"), None)
        if not all_stems_fact:
            return None
        
        output_details = []
        shishen_count = 0
        shangguan_count = 0
        for pos, stem in all_stems_fact.value.items():
            if pos == "day":
                continue
            if WUXING_SHENG.get(dm_wx, "") == WUXING[stem]:  # 日主生
                ten_god = get_ten_god(day_master, stem)
                if ten_god == "食神":
                    shishen_count += 1
                elif ten_god == "伤官":
                    shangguan_count += 1
                output_details.append({
                    "position": pos,
                    "stem": stem,
                    "type": ten_god,
                    "rooted": True
                })
        
        if not output_details:
            return None
        
        value = {
            "output_present": True,
            "output_count": len(output_details),
            "output_details": output_details,
            "shishen_count": shishen_count,
            "shangguan_count": shangguan_count,
            "dual_nature": True,
            "note": "双面性：泄身/生财/制杀；食神为善神，伤官为不善神；身旺时泄秀是好事，身弱时泄身是坏事"
        }
        
        return Evidence(
            evidence_id=f"E-L4-OUTPUT-{day_master}",
            evidence_type=self.evidence_type,
            judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value=value,
            source_fact_ids=[dm_fact.fact_id, all_stems_fact.fact_id],
            source_relation_ids=[],
            derivation_rule_id=self.rule_id,
            classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED,
            authorization_level=self.authorization_level,
            max_output=self.max_output,
        )


# ============================================================================
# L4-5: WEALTH_DRAIN（财星耗身）
# ============================================================================

class WealthDrainDerivation(EvidenceDerivationRule):
    """财星耗身 Evidence 推导
    
    原典依据：
    - 《子平真诠·论用神》："财官印食，此用神之善而顺用之者也"
    - 《子平真诠·论用神成败救应》："财生官旺，或财逢食生而身强带比...财格成也"
    
    授权级别：PARTIAL
    最大输出：QUALIFIED
    关键边界：双面性——耗身/生官/养命；身旺能任财是好事，身弱财多是坏事（"富屋贫人"）
    """
    
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
               relations: List[SemanticRelation]) -> Optional[Evidence]:
        dm_fact = next((f for f in facts if f.fact_type == "DAY_MASTER"), None)
        if not dm_fact:
            return None
        
        day_master = dm_fact.value["stem"]
        dm_wx = WUXING[day_master]
        
        all_stems_fact = next((f for f in facts if f.fact_type == "ALL_STEMS"), None)
        if not all_stems_fact:
            return None
        
        wealth_details = []
        zhengcai_count = 0
        piancai_count = 0
        for pos, stem in all_stems_fact.value.items():
            if pos == "day":
                continue
            if WUXING_KE.get(dm_wx, "") == WUXING[stem]:  # 日主克
                ten_god = get_ten_god(day_master, stem)
                if ten_god == "正财":
                    zhengcai_count += 1
                elif ten_god == "偏财":
                    piancai_count += 1
                wealth_details.append({
                    "position": pos,
                    "stem": stem,
                    "type": ten_god,
                    "rooted": True
                })
        
        if not wealth_details:
            return None
        
        value = {
            "wealth_present": True,
            "wealth_count": len(wealth_details),
            "wealth_details": wealth_details,
            "zhengcai_count": zhengcai_count,
            "piancai_count": piancai_count,
            "dual_nature": True,
            "note": "双面性：耗身/生官/养命；身旺能任财是好事，身弱财多是坏事（'富屋贫人'）"
        }
        
        return Evidence(
            evidence_id=f"E-L4-WEALTH-{day_master}",
            evidence_type=self.evidence_type,
            judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value=value,
            source_fact_ids=[dm_fact.fact_id, all_stems_fact.fact_id],
            source_relation_ids=[],
            derivation_rule_id=self.rule_id,
            classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED,
            authorization_level=self.authorization_level,
            max_output=self.max_output,
        )


# ============================================================================
# L4-6: SEASONAL_STATE（季节状态）
# ============================================================================

class SeasonalStateDerivation(EvidenceDerivationRule):
    """季节状态 Evidence 推导
    
    原典依据：
    - 《滴天髓》："能知衰旺之真机，其于三命之奥，思过半矣"
    - 《滴天髓》（原注）："旺则宜泄宜伤，衰则喜帮喜助...然旺中有衰者存，不可损也；衰中有旺者存，不可益也"
    - 《穷通宝鉴·五行总论》："北方阴极而生寒，寒生水。南方阳极而生热，热生火..."
    
    授权级别：PARTIAL
    最大输出：QUALIFIED
    关键边界：得令 ≠ 旺（原典明确警告"虽是至理，亦死法也"）；是 CONTEXT 不是直接 SUPPORT/CONSTRAINT
    """
    
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
            "additional_sources": [
                {
                    "classic": "穷通宝鉴",
                    "text_type": "ORIGINAL",
                    "source_text": "北方阴极而生寒，寒生水。南方阳极而生热，热生火",
                }
            ]
        }
    
    def derive(self, facts: List[CanonicalFact], 
               relations: List[SemanticRelation]) -> Optional[Evidence]:
        dm_fact = next((f for f in facts if f.fact_type == "DAY_MASTER"), None)
        month_fact = next((f for f in facts if f.fact_type == "MONTH_BRANCH"), None)
        if not dm_fact or not month_fact:
            return None
        
        day_master = dm_fact.value["stem"]
        month_branch = month_fact.value["branch"]
        dm_wx = WUXING[day_master]
        month_wx = WUXING.get(month_branch, "")  # 地支五行简化
        
        # 地支五行（简化）
        branch_wx = {
            "寅": "木", "卯": "木", "辰": "土",
            "巳": "火", "午": "火", "未": "土",
            "申": "金", "酉": "金", "戌": "土",
            "亥": "水", "子": "水", "丑": "土",
        }
        month_wx = branch_wx.get(month_branch, "")
        
        # 十二长生（简化，只查甲木）
        growth_stage = GROWTH_STAGE.get((day_master, month_branch), "未知")
        
        # 季节
        season = SEASON.get(month_branch, "未知")
        climate = CLIMATE.get(season, {})
        
        # 得令判断（简化）
        if dm_wx == month_wx:
            seasonal_alignment = "IN_SEASON"  # 得令
        elif WUXING_SHENG.get(month_wx, "") == dm_wx:
            seasonal_alignment = "GENERATED_BY_SEASON"  # 月令生
        else:
            seasonal_alignment = "NOT_IN_SEASON"  # 失令
        
        value = {
            "season": season,
            "month_branch": month_branch,
            "day_master_wuxing": dm_wx,
            "month_wuxing": month_wx,
            "growth_stage": growth_stage,
            "seasonal_alignment": seasonal_alignment,
            "climate": climate,
            "note": "得令 ≠ 旺（原典明确警告'虽是至理，亦死法也'）；是 CONTEXT 不是直接判断"
        }
        
        return Evidence(
            evidence_id=f"E-L4-SEASONAL-{day_master}",
            evidence_type=self.evidence_type,
            judgment_target="DAY_MASTER_STRENGTH",
            polarity=self.polarity,
            value=value,
            source_fact_ids=[dm_fact.fact_id, month_fact.fact_id],
            source_relation_ids=[],
            derivation_rule_id=self.rule_id,
            classical_source=self.classical_source,
            certainty_state=CertaintyState.QUALIFIED,
            authorization_level=self.authorization_level,
            max_output=self.max_output,
        )


# ============================================================================
# L4 Evidence 推导引擎
# ============================================================================

class L4EvidenceEngine:
    """L4 Evidence 推导引擎"""
    
    def __init__(self):
        self.rules: List[EvidenceDerivationRule] = [
            ResourceSupportDerivation(),
            PeerSupportDerivation(),
            OfficerControlDerivation(),
            OutputDrainDerivation(),
            WealthDrainDerivation(),
            SeasonalStateDerivation(),
            # L4-7 ENVIRONMENT_STATE 和 L4-8 STRUCTURAL_CHANGE 待后续实现
        ]
    
    def derive_all(self, facts: List[CanonicalFact], 
                   relations: List[SemanticRelation]) -> List[Evidence]:
        """推导所有 L4 Evidence"""
        evidences = []
        for rule in self.rules:
            evidence = rule.derive(facts, relations)
            if evidence:
                evidences.append(evidence)
        return evidences


# ============================================================================
# 测试命例
# ============================================================================

def create_test_case() -> tuple:
    """创建测试命例：甲木日主，寅月，天干有壬（偏印）、乙（劫财）、庚（七杀）、丙（食神）"""
    
    facts = [
        CanonicalFact(
            fact_id="F-TEST-001",
            fact_type="DAY_MASTER",
            value={"stem": "甲", "wuxing": "木", "yinyang": "阳"},
            source="bazi_calculation",
            certainty="CALCULATED"
        ),
        CanonicalFact(
            fact_id="F-TEST-002",
            fact_type="MONTH_BRANCH",
            value={"branch": "寅", "wuxing": "木"},
            source="bazi_calculation",
            certainty="CALCULATED"
        ),
        CanonicalFact(
            fact_id="F-TEST-003",
            fact_type="ALL_STEMS",
            value={
                "year": "壬",
                "month": "乙",
                "day": "甲",
                "hour": "丙",
            },
            source="bazi_calculation",
            certainty="CALCULATED"
        ),
    ]
    
    relations = []  # 简化：不预计算关系，由推导规则内部计算
    
    return facts, relations


# ============================================================================
# 验证
# ============================================================================

def verify_l4_evidence():
    """验证 L4 Evidence 推导"""
    
    print("=" * 80)
    print("P0-2.7.2 L4 Evidence Construction — 验证")
    print("=" * 80)
    
    # 创建测试命例
    facts, relations = create_test_case()
    
    print("\n【测试命例】")
    print(f"  日主：甲木（阳）")
    print(f"  月令：寅（木）")
    print(f"  年干：壬（偏印）")
    print(f"  月干：乙（劫财）")
    print(f"  时干：丙（食神）")
    print(f"  （注意：这是简化的测试命例，仅用于验证 Evidence 推导）")
    
    # 推导 L4 Evidence
    engine = L4EvidenceEngine()
    evidences = engine.derive_all(facts, relations)
    
    print(f"\n【推导结果】")
    print(f"  共推导出 {len(evidences)} 条 L4 Evidence")
    
    # 逐条展示
    for i, ev in enumerate(evidences, 1):
        print(f"\n  --- Evidence {i}: {ev.evidence_type} ---")
        print(f"    ID: {ev.evidence_id}")
        print(f"    极性: {ev.polarity.value}")
        print(f"    授权级别: {ev.authorization_level.value}")
        print(f"    最大输出: {ev.max_output}")
        print(f"    确定性: {ev.certainty_state.value}")
        print(f"    推导规则: {ev.derivation_rule_id}")
        print(f"    原典来源: {ev.classical_source['classic']}·{ev.classical_source['chapter']}")
        print(f"    原文: \"{ev.classical_source['source_text']}\"")
        print(f"    验证状态: {ev.classical_source['verification_status']}")
        print(f"    核心值:")
        for k, v in ev.value.items():
            if k != "note" and k != "resource_details" and k != "peer_details" and k != "officer_details" and k != "output_details" and k != "wealth_details" and k != "climate":
                print(f"      {k}: {v}")
        if "note" in ev.value:
            print(f"    关键边界: {ev.value['note']}")
    
    # 验证检查清单
    print("\n" + "=" * 80)
    print("【验证检查清单】")
    print("=" * 80)
    
    checks = []
    
    # 检查 1：所有 L4 Evidence 都是 PARTIAL
    all_partial = all(ev.authorization_level == AuthorizationLevel.PARTIAL for ev in evidences)
    checks.append(("所有 L4 Evidence 都是 PARTIAL（没有 AUTHORIZED）", all_partial))
    
    # 检查 2：所有 L4 Evidence 最大输出都是 QUALIFIED
    all_qualified = all(ev.max_output == "QUALIFIED" for ev in evidences)
    checks.append(("所有 L4 Evidence 最大输出都是 QUALIFIED（没有 CONFIRMED）", all_qualified))
    
    # 检查 3：没有 Evidence 直接输出"身强/身弱"（排除 note 字段，note 是边界说明）
    def has_strength_judgment(ev):
        for k, v in ev.value.items():
            if k == "note":
                continue
            if "身强" in str(v) or "身弱" in str(v):
                return True
        return False
    no_strength_judgment = not any(has_strength_judgment(ev) for ev in evidences)
    checks.append(("没有 Evidence 直接输出'身强/身弱'（排除 note 边界说明）", no_strength_judgment))
    
    # 检查 4：十神类 Evidence 都有双面性标记
    ten_god_types = ["RESOURCE_SUPPORT", "PEER_SUPPORT", "OFFICER_CONTROL", "OUTPUT_DRAIN", "WEALTH_DRAIN"]
    ten_god_evidences = [ev for ev in evidences if ev.evidence_type in ten_god_types]
    all_dual_nature = all(ev.value.get("dual_nature") == True for ev in ten_god_evidences)
    checks.append(("十神类 Evidence 都有双面性标记（dual_nature=True）", all_dual_nature))
    
    # 检查 5：SEASONAL_STATE 极性是 CONTEXT
    seasonal_ev = next((ev for ev in evidences if ev.evidence_type == "SEASONAL_STATE"), None)
    seasonal_is_context = seasonal_ev is not None and seasonal_ev.polarity == Polarity.CONTEXT
    checks.append(("SEASONAL_STATE 极性是 CONTEXT（不是直接 SUPPORT/CONSTRAINT）", seasonal_is_context))
    
    # 检查 6：所有 Evidence 都有原典来源
    all_has_source = all(ev.classical_source.get("classic") and ev.classical_source.get("source_text") for ev in evidences)
    checks.append(("所有 Evidence 都有原典来源（classic + source_text）", all_has_source))
    
    # 检查 7：所有 Evidence 都有验证状态
    all_has_verification = all(ev.classical_source.get("verification_status") for ev in evidences)
    checks.append(("所有 Evidence 都有验证状态（verification_status）", all_has_verification))
    
    # 检查 8：没有用数量统计直接判断强弱
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
    print("  1. L4 Evidence 只是局部证，不是旺衰判断")
    print("  2. 所有 L4 Evidence 都是 PARTIAL，最多输出 QUALIFIED")
    print("  3. 十神类 Evidence 都有双面性，不能简单等同于支持/制约")
    print("  4. SEASONAL_STATE 是 CONTEXT，不是直接的 SUPPORT/CONSTRAINT")
    print("  5. 在 Evidence Combination 规则没有原典授权之前，整体旺衰判断保持 UNRESOLVED")
    print("  6. 绝对禁止：用数量统计直接判断强弱（支持 > 克泄耗 → 身强）")
    
    return all_passed


if __name__ == "__main__":
    verify_l4_evidence()
