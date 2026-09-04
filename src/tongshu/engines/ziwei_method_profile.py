"""紫微斗数方法论契约 — ZiweiMethodProfile

定义四种流派的断事方法契约，确保：
1. 输入输出接口统一
2. 证据可追溯
3. 流派隔离

契约版本: v1.0
创建日期: 2026-09-04
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


# ============================================================================
# 枚举类型
# ============================================================================

class MethodId(Enum):
    """流派标识"""
    SANHE = "sanhe"
    ZHONGZHOU = "zhongzhou"
    FEIXING = "feixing"
    QINTIAN = "qintian"


class RuleType(Enum):
    """规则类型"""
    PATTERN = "pattern"
    SIHUA = "sihua"
    PALACE = "palace"
    INTERACTION = "interaction"
    CYCLE = "cycle"


class ConfidenceLevel(Enum):
    """置信度级别"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


# ============================================================================
# 核心数据结构
# ============================================================================

@dataclass(frozen=True)
class EvidenceRef:
    """证据引用"""
    source_type: str
    source_name: str
    section: str
    quote: str
    verified: bool = False
    
    def __post_init__(self):
        if not self.source_name:
            raise ValueError("source_name cannot be empty")


@dataclass(frozen=True)
class RuleSpec:
    """规则规格"""
    rule_id: str
    rule_type: RuleType
    method_ids: Tuple[MethodId, ...]
    condition: Callable[[Any], bool]
    effect: Callable[[Any], Dict[str, Any]]
    
    description: str = ""
    priority: int = 0
    
    evidence: List[EvidenceRef] = field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    version: str = "2026.09"
    
    def applies_to(self, method: MethodId) -> bool:
        """检查是否适用于指定流派"""
        return method in self.method_ids


@dataclass(frozen=True)
class SiHuaTable:
    """四化表"""
    name: str
    description: str
    data: Dict[str, Tuple[str, str, str, str]]
    sources: List[EvidenceRef] = field(default_factory=list)
    
    def get(self, stem: str) -> Optional[Tuple[str, str, str, str]]:
        """获取某天干的四化"""
        return self.data.get(stem)


# ============================================================================
# 方法契约基类
# ============================================================================

class ZiweiMethodContract:
    """紫微斗数方法契约基类"""
    
    method_id: MethodId = MethodId.SANHE
    name: str = "未知流派"
    version: str = "1.0.0"
    
    sihua_table: SiHuaTable = None
    # 规则集合（运行时修改，非 dataclass 字段）
    rules: Dict[str, RuleSpec] = None
    
    @property
    def has_self_hua(self) -> bool:
        return False
    
    @property
    def has_liji_gong(self) -> bool:
        return False
    
    @property
    def has_liuchangliuqu(self) -> bool:
        return False
    
    @property
    def use_xiaoxian(self) -> bool:
        return True
    
    @property
    def empty_palace_policy(self) -> str:
        return "partial"
    
    def __init__(self):
        self.rules = {}
    
    def analyze_pattern(self, fact: Any) -> List[Dict[str, Any]]:
        raise NotImplementedError
    
    def analyze_sihua(self, fact: Any) -> List[Dict[str, Any]]:
        raise NotImplementedError
    
    def analyze_palace(self, fact: Any, palace_name: str) -> Dict[str, Any]:
        raise NotImplementedError
    
    def full_analysis(self, fact: Any) -> Dict[str, Any]:
        raise NotImplementedError
    
    def add_rule(self, rule: RuleSpec) -> None:
        self.rules[rule.rule_id] = rule
    
    def get_rule(self, rule_id: str) -> Optional[RuleSpec]:
        return self.rules.get(rule_id)
    
    def query_rules(self, rule_type: RuleType) -> List[RuleSpec]:
        return [r for r in self.rules.values() if r.rule_type == rule_type]
    
    def validate_evidence(self, rule_id: str) -> bool:
        rule = self.rules.get(rule_id)
        if not rule:
            return False
        return all(e.verified for e in rule.evidence)


# ============================================================================
# 流派契约实现
# ============================================================================

class SanheContract(ZiweiMethodContract):
    """三合派契约（南派）"""
    
    method_id = MethodId.SANHE
    name = "三合派"
    
    sihua_table = SiHuaTable(
        name="classic",
        description="清代通行版四化表（《全集》）",
        data={
            "甲": ("廉贞", "破军", "武曲", "太阳"),
            "乙": ("天机", "天梁", "紫微", "太阴"),
            "丙": ("天同", "天机", "文昌", "廉贞"),
            "丁": ("太阴", "天同", "天机", "巨门"),
            "戊": ("贪狼", "太阴", "右弼", "天机"),
            "己": ("武曲", "贪狼", "天梁", "文曲"),
            "庚": ("太阳", "武曲", "太阴", "天同"),
            "辛": ("巨门", "太阳", "文曲", "文昌"),
            "壬": ("天梁", "紫微", "左辅", "武曲"),
            "癸": ("破军", "巨门", "太阴", "贪狼"),
        },
    )
    
    @property
    def empty_palace_policy(self) -> str:
        return "partial"


class ZhongzhouContract(ZiweiMethodContract):
    """中州派契约"""
    
    method_id = MethodId.ZHONGZHOU
    name = "中州派"
    
    sihua_table = SiHuaTable(
        name="zhongzhou",
        description="中州派四化表（戊干太阳化科）",
        data={
            "甲": ("廉贞", "破军", "武曲", "太阳"),
            "乙": ("天机", "天梁", "紫微", "太阴"),
            "丙": ("天同", "天机", "文昌", "廉贞"),
            "丁": ("太阴", "天同", "天机", "巨门"),
            "戊": ("贪狼", "太阴", "太阳", "天机"),
            "己": ("武曲", "贪狼", "天梁", "文曲"),
            "庚": ("太阳", "武曲", "天府", "天同"),
            "辛": ("巨门", "太阳", "文曲", "文昌"),
            "壬": ("天梁", "紫微", "天府", "武曲"),
            "癸": ("破军", "巨门", "太阴", "贪狼"),
        },
    )
    
    @property
    def has_liuchangliuqu(self) -> bool:
        return True
    
    @property
    def empty_palace_policy(self) -> str:
        return "full"


class FeixingContract(ZiweiMethodContract):
    """飞星派契约（梁若瑜系）"""
    
    method_id = MethodId.FEIXING
    name = "飞星派"
    
    sihua_table = SiHuaTable(
        name="classic",
        description="飞星派使用通行版四化表",
        data={
            "甲": ("廉贞", "破军", "武曲", "太阳"),
            "乙": ("天机", "天梁", "紫微", "太阴"),
            "丙": ("天同", "天机", "文昌", "廉贞"),
            "丁": ("太阴", "天同", "天机", "巨门"),
            "戊": ("贪狼", "太阴", "右弼", "天机"),
            "己": ("武曲", "贪狼", "天梁", "文曲"),
            "庚": ("太阳", "武曲", "太阴", "天同"),
            "辛": ("巨门", "太阳", "文曲", "文昌"),
            "壬": ("天梁", "紫微", "左辅", "武曲"),
            "癸": ("破军", "巨门", "太阴", "贪狼"),
        },
    )
    
    @property
    def use_xiaoxian(self) -> bool:
        return False
    
    @property
    def has_self_hua(self) -> bool:
        return True
    
    @property
    def empty_palace_policy(self) -> str:
        return "partial"


class QintianContract(ZiweiMethodContract):
    """钦天门契约（北派）"""
    
    method_id = MethodId.QINTIAN
    name = "钦天门"
    
    sihua_table = SiHuaTable(
        name="classic",
        description="钦天门使用通行版四化表",
        data={
            "甲": ("廉贞", "破军", "武曲", "太阳"),
            "乙": ("天机", "天梁", "紫微", "太阴"),
            "丙": ("天同", "天机", "文昌", "廉贞"),
            "丁": ("太阴", "天同", "天机", "巨门"),
            "戊": ("贪狼", "太阴", "右弼", "天机"),
            "己": ("武曲", "贪狼", "天梁", "文曲"),
            "庚": ("太阳", "武曲", "太阴", "天同"),
            "辛": ("巨门", "太阳", "文曲", "文昌"),
            "壬": ("天梁", "紫微", "左辅", "武曲"),
            "癸": ("破军", "巨门", "太阴", "贪狼"),
        },
    )
    
    @property
    def has_self_hua(self) -> bool:
        return True
    
    @property
    def has_liji_gong(self) -> bool:
        return True
    
    @property
    def use_xiaoxian(self) -> bool:
        return "partial"
    
    @property
    def empty_palace_policy(self) -> str:
        return "partial"


# ============================================================================
# 方法映射
# ============================================================================

METHOD_CONTRACTS: Dict[MethodId, type] = {
    MethodId.SANHE: SanheContract,
    MethodId.ZHONGZHOU: ZhongzhouContract,
    MethodId.FEIXING: FeixingContract,
    MethodId.QINTIAN: QintianContract,
}


def get_contract(method_id: MethodId) -> type:
    """获取流派契约"""
    contract = METHOD_CONTRACTS.get(method_id)
    if not contract:
        raise ValueError(f"Unknown method_id: {method_id}")
    return contract


def list_contracts() -> List[Dict[str, Any]]:
    """列出所有流派契约"""
    result = []
    for method_id, contract_class in METHOD_CONTRACTS.items():
        instance = contract_class()
        result.append({
            "method_id": method_id.value,
            "name": instance.name,
            "sihua_table": instance.sihua_table.name,
            "has_self_hua": instance.has_self_hua,
            "has_liji_gong": instance.has_liji_gong,
            "has_liuchangliuqu": instance.has_liuchangliuqu,
            "use_xiaoxian": instance.use_xiaoxian,
            "empty_palace_policy": instance.empty_palace_policy,
        })
    return result


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "MethodId",
    "RuleType",
    "ConfidenceLevel",
    "EvidenceRef",
    "RuleSpec",
    "SiHuaTable",
    "ZiweiMethodContract",
    "SanheContract",
    "ZhongzhouContract",
    "FeixingContract",
    "QintianContract",
    "METHOD_CONTRACTS",
    "get_contract",
    "list_contracts",
]
