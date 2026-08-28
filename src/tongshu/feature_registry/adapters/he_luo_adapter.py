"""P6-C-3C-1 河洛Feature Adapter - 基于HeluoChart实际字段."""
from __future__ import annotations
from typing import Any
from tongshu.feature_registry.contract import (
    FeatureRegistry, FeatureDefinition, Feature, FeatureMapResult, BaseFeatureAdapter,
)


class HeLuoFeatureAdapter(BaseFeatureAdapter):
    def __init__(self, registry: FeatureRegistry):
        super().__init__(registry)
        self._register_default_features()

    def _register_default_features(self) -> None:
        defaults = [
            ("HL.PRENATAL_HEXAGRAM", "PRENATAL", "STRING", "NATAL", "HL-PRENATAL-HEXAGRAM", "prenatal_hexagram", "先天卦"),
            ("HL.YUANTANG", "YUANTANG", "STRING", "NATAL", "HL-YUANTANG", "yuan_tang", "元堂"),
            ("HL.POSTNATAL_HEXAGRAM", "POSTNATAL", "STRING", "NATAL", "HL-POSTNATAL-HEXAGRAM", "postnatal_hexagram", "后天卦"),
            ("HL.YEAR_HEXAGRAM", "YEAR_HEXAGRAM", "STRING", "YEAR", "HL-YEAR-HEXAGRAM", "year_hexagram", "流年卦"),
            ("HL.MONTH_HEXAGRAM", "MONTH_HEXAGRAM", "STRING", "MONTH", "HL-MONTH-HEXAGRAM", "month_hexagram", "流月卦"),
            ("HL.DAY_HEXAGRAM", "DAY_HEXAGRAM", "STRING", "DAY", "HL-DAY-HEXAGRAM", "day_hexagram", "流日卦"),
            ("HL.YAO", "YAO", "STRING", "NATAL", "HL-YAO", "yao", "爻"),
            ("HL.HEXAGRAM_QI", "HEXAGRAM_QI", "DICT", "NATAL", "HL-HEXAGRAM-QI", "hexagram_qi", "卦气"),
        ]
        for fid, cat, vtype, scope, rule_id, field, desc in defaults:
            if not self.registry.has(fid):
                self.registry.register(FeatureDefinition(
                    feature_id=fid, engine="HE_LUO", namespace="HL", category=cat,
                    value_type=vtype, scope=scope, source_rule_id=rule_id,
                    source_field=field, description=desc,
                ))

    def adapt(self, chart: Any) -> FeatureMapResult:
        resolved = []
        unmapped = []
        # 河洛引擎输出可能是dict或dataclass, 通用处理
        chart_dict = chart.to_dict() if hasattr(chart, 'to_dict') else (chart if isinstance(chart, dict) else {})
        field_map = {
            "HL.PRENATAL_HEXAGRAM": "prenatal_hexagram",
            "HL.YUANTANG": "yuan_tang",
            "HL.POSTNATAL_HEXAGRAM": "postnatal_hexagram",
            "HL.YEAR_HEXAGRAM": "year_hexagram",
            "HL.MONTH_HEXAGRAM": "month_hexagram",
            "HL.DAY_HEXAGRAM": "day_hexagram",
            "HL.YAO": "yao",
            "HL.HEXAGRAM_QI": "hexagram_qi",
        }
        for fid, field_name in field_map.items():
            value = chart_dict.get(field_name)
            if value is not None and self.registry.has(fid):
                defn = self.registry.get(fid)
                resolved.append(Feature(
                    feature_id=fid, value=value, engine="HE_LUO", namespace="HL",
                    category=defn.category, value_type=defn.value_type, scope=defn.scope,
                    source_rule_id=defn.source_rule_id, source_field=defn.source_field,
                    source_evidence_ref=f"HL-{field_name.upper()}",
                ))
            elif value is not None:
                unmapped.append({"rule_id": fid, "value": str(value)[:100]})
        return FeatureMapResult(
            engine="HE_LUO", total_evidence=len(field_map),
            resolved=len(resolved), unmapped=len(unmapped),
            resolved_features=resolved, unmapped_evidence=unmapped,
        )
