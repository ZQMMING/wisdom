"""P6-C-3C-1 盲派Feature Adapter - 基于BlindChart实际字段."""
from __future__ import annotations
from typing import Any
from tongshu.feature_registry.contract import (
    FeatureRegistry, FeatureDefinition, Feature, FeatureMapResult, BaseFeatureAdapter,
)


class BlindSchoolFeatureAdapter(BaseFeatureAdapter):
    def __init__(self, registry: FeatureRegistry):
        super().__init__(registry)
        self._register_default_features()

    def _register_default_features(self) -> None:
        defaults = [
            ("BLIND.BODY", "BODY_USE", "STRING", "NATAL", "BLIND-BODY", "body", "体"),
            ("BLIND.USE", "BODY_USE", "STRING", "NATAL", "BLIND-USE", "use", "用"),
            ("BLIND.GUEST", "GUEST_HOST", "STRING", "NATAL", "BLIND-GUEST", "guest", "宾"),
            ("BLIND.HOST", "GUEST_HOST", "STRING", "NATAL", "BLIND-HOST", "host", "主"),
            ("BLIND.DOING_WORK", "DOING_WORK", "GRAPH", "NATAL", "BLIND-DOING-WORK", "doing_work", "做功链"),
            ("BLIND.PALACE_DATA", "PALACE", "DICT", "NATAL", "BLIND-PALACE-DATA", "palace_data", "宫位数据"),
            ("BLIND.TEN_GOD_PALACE", "TEN_GOD_PALACE", "DICT", "NATAL", "BLIND-TEN-GOD-PALACE", "ten_god_palace", "十神落宫"),
            ("BLIND.GRAVE", "GRAVE", "DICT", "NATAL", "BLIND-GRAVE", "grave", "墓库"),
            ("BLIND.TIMING", "TIMING", "DICT", "NATAL", "BLIND-TIMING", "timing", "应期"),
        ]
        for fid, cat, vtype, scope, rule_id, field, desc in defaults:
            if not self.registry.has(fid):
                self.registry.register(FeatureDefinition(
                    feature_id=fid, engine="BLIND_SCHOOL", namespace="BLIND", category=cat,
                    value_type=vtype, scope=scope, source_rule_id=rule_id,
                    source_field=field, description=desc,
                ))

    def adapt(self, chart: Any) -> FeatureMapResult:
        resolved = []
        unmapped = []
        chart_dict = chart.to_dict() if hasattr(chart, 'to_dict') else (chart if isinstance(chart, dict) else {})
        field_map = {
            "BLIND.BODY": "body",
            "BLIND.USE": "use",
            "BLIND.GUEST": "guest",
            "BLIND.HOST": "host",
            "BLIND.DOING_WORK": "doing_work",
            "BLIND.PALACE_DATA": "palace_data",
            "BLIND.TEN_GOD_PALACE": "ten_god_palace",
            "BLIND.GRAVE": "grave",
            "BLIND.TIMING": "timing",
        }
        for fid, field_name in field_map.items():
            value = chart_dict.get(field_name)
            if value is not None and self.registry.has(fid):
                defn = self.registry.get(fid)
                resolved.append(Feature(
                    feature_id=fid, value=value, engine="BLIND_SCHOOL", namespace="BLIND",
                    category=defn.category, value_type=defn.value_type, scope=defn.scope,
                    source_rule_id=defn.source_rule_id, source_field=defn.source_field,
                    source_evidence_ref=f"BLIND-{field_name.upper()}",
                ))
            elif value is not None:
                unmapped.append({"rule_id": fid, "value": str(value)[:100]})
        return FeatureMapResult(
            engine="BLIND_SCHOOL", total_evidence=len(field_map),
            resolved=len(resolved), unmapped=len(unmapped),
            resolved_features=resolved, unmapped_evidence=unmapped,
        )
