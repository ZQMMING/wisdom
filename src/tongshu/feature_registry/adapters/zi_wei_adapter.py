"""P6-C-3C-1 紫微Feature Adapter - 基于ZiweiChart实际字段."""
from __future__ import annotations
from typing import Any
from tongshu.feature_registry.contract import (
    FeatureRegistry, FeatureDefinition, Feature, FeatureMapResult, BaseFeatureAdapter,
)


class ZiWeiFeatureAdapter(BaseFeatureAdapter):
    def __init__(self, registry: FeatureRegistry):
        super().__init__(registry)
        self._register_default_features()

    def _register_default_features(self) -> None:
        defaults = [
            ("ZW.SOUL_PALACE_MAIN_STAR", "MAJOR_STAR", "STRING", "NATAL", "ZW-SOUL-PALACE-MAIN-STAR", "soul_palace_main_star", "命宫主星"),
            ("ZW.SOUL_PALACE_MAIN_STARS", "MAJOR_STAR", "LIST", "NATAL", "ZW-SOUL-PALACE-MAIN-STARS", "soul_palace_main_stars", "命宫全部主星"),
            ("ZW.SOUL_PALACE_SIHUA", "TRANSFORMATION", "LIST", "NATAL", "ZW-SOUL-PALACE-SIHUA", "soul_palace_sihua", "命宫四化"),
            ("ZW.PALACE_DATA", "PALACE", "DICT", "NATAL", "ZW-PALACE-DATA", "palace_data", "十二宫数据"),
            ("ZW.DAILY_LUCK_PALACE", "FLOW_DAY", "STRING", "DAY", "ZW-DAILY-LUCK-PALACE", "daily_luck_palace", "流日命宫"),
            ("ZW.SOURCE", "STRUCTURE", "STRING", "NATAL", "ZW-SOURCE", "source", "数据来源"),
        ]
        for fid, cat, vtype, scope, rule_id, field, desc in defaults:
            if not self.registry.has(fid):
                self.registry.register(FeatureDefinition(
                    feature_id=fid, engine="ZI_WEI", namespace="ZW", category=cat,
                    value_type=vtype, scope=scope, source_rule_id=rule_id,
                    source_field=field, description=desc,
                ))

    def adapt(self, chart: Any) -> FeatureMapResult:
        resolved = []
        unmapped = []
        mappings = [
            ("ZW.SOUL_PALACE_MAIN_STAR", chart.soul_palace_main_star, "ZW-SOUL-PALACE-MAIN-STAR"),
            ("ZW.SOUL_PALACE_MAIN_STARS", list(chart.soul_palace_main_stars), "ZW-SOUL-PALACE-MAIN-STARS"),
            ("ZW.SOUL_PALACE_SIHUA", list(chart.soul_palace_sihua), "ZW-SOUL-PALACE-SIHUA"),
            ("ZW.PALACE_DATA", dict(chart.palace_data), "ZW-PALACE-DATA"),
            ("ZW.DAILY_LUCK_PALACE", chart.daily_luck_palace, "ZW-DAILY-LUCK-PALACE"),
            ("ZW.SOURCE", chart.source, "ZW-SOURCE"),
        ]
        for fid, value, ev_ref in mappings:
            if self.registry.has(fid):
                defn = self.registry.get(fid)
                resolved.append(Feature(
                    feature_id=fid, value=value, engine="ZI_WEI", namespace="ZW",
                    category=defn.category, value_type=defn.value_type, scope=defn.scope,
                    source_rule_id=defn.source_rule_id, source_field=defn.source_field,
                    source_evidence_ref=ev_ref,
                ))
            else:
                unmapped.append({"rule_id": fid, "value": str(value)[:100]})
        return FeatureMapResult(
            engine="ZI_WEI", total_evidence=len(mappings),
            resolved=len(resolved), unmapped=len(unmapped),
            resolved_features=resolved, unmapped_evidence=unmapped,
        )
