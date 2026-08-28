"""P6-C-3C-1 Feature Registry - 五引擎计算特征注册表.

核心原则:
1. 不做抽象Feature, 逐字段盘点五引擎实际输出
2. 每个Feature有独立namespace: ZP.* / BLIND.* / ZW.* / HL.* / YJ.*
3. 禁止跨引擎共用feature_id
4. 每个Feature必须有provenance, 可反查EngineEvidence → engine_rule_id → 原始计算字段
5. 不产生direction/polarity/domain/modern semantic
6. 状态: RESOLVED / UNMAPPED
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class FeatureNamespace(str, Enum):
    ZP = "ZP"
    BLIND = "BLIND"
    ZW = "ZW"
    HL = "HL"
    YJ = "YJ"


class FeatureValueType(str, Enum):
    ENUM = "ENUM"
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    LIST = "LIST"
    DICT = "DICT"
    TUPLE = "TUPLE"
    GRAPH = "GRAPH"


class FeatureScope(str, Enum):
    NATAL = "NATAL"
    DA_YUN = "DA_YUN"
    YEAR = "YEAR"
    MONTH = "MONTH"
    DAY = "DAY"
    HOUR = "HOUR"


ZP_FEATURE_CATEGORIES = ["PILLAR", "DAY_MASTER", "STRENGTH", "PATTERN", "USE_GOD", "TEN_GOD", "RELATION", "STRUCTURE", "LUCK", "SPOUSE", "ELEMENT"]
BLIND_FEATURE_CATEGORIES = ["BODY_USE", "GUEST_HOST", "DOING_WORK", "PALACE", "TEN_GOD_PALACE", "RELATION", "GRAVE", "TIMING", "SYMBOL", "FAMILY"]
ZW_FEATURE_CATEGORIES = ["PALACE", "MAJOR_STAR", "MINOR_STAR", "TRANSFORMATION", "PALACE_STAR", "SANFANG", "OPPOSITE", "DA_LIMIT", "FLOW_YEAR", "FLOW_MONTH", "FLOW_DAY"]
HL_FEATURE_CATEGORIES = ["PRENATAL", "YUANTANG", "POSTNATAL", "YEAR_HEXAGRAM", "MONTH_HEXAGRAM", "DAY_HEXAGRAM", "MOMENT", "JIEHOU", "HEXAGRAM_QI", "POSITION", "NUMBER", "YAO"]
YJ_FEATURE_CATEGORIES = ["HEXAGRAM_TEXT", "YAO_TEXT", "TUAN", "XIANG", "HUMAN_AFFAIRS", "POSITION", "ZHONG_ZHENG", "CHENG_BI", "CHANGED", "DECISION"]


@dataclass(frozen=True)
class FeatureDefinition:
    feature_id: str
    engine: str
    namespace: str
    category: str
    value_type: str
    scope: str
    source_rule_id: str
    source_field: str
    allowed_values: list[str] = field(default_factory=list)
    description: str = ""

    def __post_init__(self):
        if not self.feature_id.startswith(f"{self.namespace}."):
            raise ValueError(f"Feature {self.feature_id}: 必须以namespace '{self.namespace}.' 开头")


@dataclass(frozen=True)
class Feature:
    feature_id: str
    value: Any
    engine: str
    namespace: str
    category: str
    value_type: str
    scope: str
    source_rule_id: str
    source_field: str
    source_evidence_ref: Optional[str] = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "feature_id": self.feature_id, "value": self.value, "engine": self.engine,
            "namespace": self.namespace, "category": self.category, "value_type": self.value_type,
            "scope": self.scope, "source_rule_id": self.source_rule_id, "source_field": self.source_field,
            "source_evidence_ref": self.source_evidence_ref, "attributes": dict(self.attributes),
        }


class FeatureMapStatus(str, Enum):
    RESOLVED = "RESOLVED"
    UNMAPPED = "UNMAPPED"


@dataclass(frozen=True)
class FeatureMapResult:
    engine: str
    total_evidence: int
    resolved: int
    unmapped: int
    resolved_features: list[Feature] = field(default_factory=list)
    unmapped_evidence: list[dict] = field(default_factory=list)

    @property
    def coverage_rate(self) -> float:
        return self.resolved / self.total_evidence if self.total_evidence > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "engine": self.engine, "total_evidence": self.total_evidence,
            "resolved": self.resolved, "unmapped": self.unmapped,
            "coverage_rate": f"{self.coverage_rate:.1%}",
            "unmapped_evidence": [{"rule_id": e.get("rule_id"), "value": str(e.get("value"))[:100]} for e in self.unmapped_evidence],
        }


class FeatureRegistry:
    def __init__(self):
        self._definitions: dict[str, FeatureDefinition] = {}

    def register(self, definition: FeatureDefinition) -> None:
        if definition.feature_id in self._definitions:
            raise ValueError(f"Feature {definition.feature_id} 已注册")
        self._definitions[definition.feature_id] = definition

    def get(self, feature_id: str) -> Optional[FeatureDefinition]:
        return self._definitions.get(feature_id)

    def get_by_engine(self, engine: str) -> list[FeatureDefinition]:
        return [d for d in self._definitions.values() if d.engine == engine]

    def get_by_namespace(self, namespace: str) -> list[FeatureDefinition]:
        return [d for d in self._definitions.values() if d.namespace == namespace]

    def has(self, feature_id: str) -> bool:
        return feature_id in self._definitions

    def stats(self) -> dict[str, Any]:
        result = {}
        for ns in FeatureNamespace:
            defs = self.get_by_namespace(ns.value)
            categories = {}
            for d in defs:
                categories[d.category] = categories.get(d.category, 0) + 1
            result[ns.value] = {"total": len(defs), "categories": categories}
        return result


class BaseFeatureAdapter:
    def __init__(self, registry: FeatureRegistry):
        self.registry = registry

    def adapt(self, evidence_list: list[Any]) -> FeatureMapResult:
        raise NotImplementedError("各引擎必须实现自己的adapt方法")


if __name__ == "__main__":
    print("P6-C-3C-1 Feature Registry - 快速测试")
    print("=" * 60)
    registry = FeatureRegistry()
    zp_features = [
        FeatureDefinition("ZP.YEAR_PILLAR", "ZI_PING", "ZP", "PILLAR", "STRING", "NATAL", "ZP-YEAR-PILLAR", "year_pillar", description="年柱"),
        FeatureDefinition("ZP.MONTH_PILLAR", "ZI_PING", "ZP", "PILLAR", "STRING", "NATAL", "ZP-MONTH-PILLAR", "month_pillar", description="月柱"),
        FeatureDefinition("ZP.DAY_PILLAR", "ZI_PING", "ZP", "PILLAR", "STRING", "NATAL", "ZP-DAY-PILLAR", "day_pillar", description="日柱"),
        FeatureDefinition("ZP.HOUR_PILLAR", "ZI_PING", "ZP", "PILLAR", "STRING", "NATAL", "ZP-HOUR-PILLAR", "hour_pillar", description="时柱"),
        FeatureDefinition("ZP.DAY_MASTER", "ZI_PING", "ZP", "DAY_MASTER", "ENUM", "NATAL", "ZP-DAY-MASTER", "day_master", allowed_values=["JIA","YI","BING","DING","WU","JI","GENG","XIN","REN","GUI"], description="日主"),
    ]
    for f in zp_features:
        registry.register(f)
    print(f"注册子平Feature: {len(zp_features)} 个")
    print(f"Registry统计: {registry.stats()}")
    f = Feature("ZP.DAY_MASTER", "YI", "ZI_PING", "ZP", "DAY_MASTER", "ENUM", "NATAL", "ZP-DAY-MASTER", "day_master", "EV-001")
    print(f"\nFeature实例: {f.feature_id} = {f.value}")
    print(f"  来源: {f.source_rule_id} / {f.source_field} / {f.source_evidence_ref}")
    print("\n" + "=" * 60)
    print("P6-C-3C-1 Feature Registry 测试通过")
