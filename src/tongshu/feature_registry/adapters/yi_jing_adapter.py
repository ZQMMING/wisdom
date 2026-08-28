"""P6-C-3C-1 易经Feature Adapter - 基于YiJingChart实际字段."""
from __future__ import annotations
from typing import Any
from tongshu.feature_registry.contract import (
    FeatureRegistry, FeatureDefinition, Feature, FeatureMapResult, BaseFeatureAdapter,
)


class YiJingFeatureAdapter(BaseFeatureAdapter):
    def __init__(self, registry: FeatureRegistry):
        super().__init__(registry)
        self._register_default_features()

    def _register_default_features(self) -> None:
        defaults = [
            ("YJ.HEXAGRAM", "HEXAGRAM_TEXT", "STRING", "NATAL", "YJ-HEXAGRAM", "hexagram", "本卦"),
            ("YJ.HEXAGRAM_TEXT", "HEXAGRAM_TEXT", "STRING", "NATAL", "YJ-HEXAGRAM-TEXT", "hexagram_text", "卦辞"),
            ("YJ.YAO", "YAO_TEXT", "STRING", "NATAL", "YJ-YAO", "yao", "爻"),
            ("YJ.YAO_TEXT", "YAO_TEXT", "STRING", "NATAL", "YJ-YAO-TEXT", "yao_text", "爻辞"),
            ("YJ.TUAN_TEXT", "TUAN", "STRING", "NATAL", "YJ-TUAN-TEXT", "tuan_text", "彖辞"),
            ("YJ.DA_XIANG", "XIANG", "STRING", "NATAL", "YJ-DA-XIANG", "da_xiang", "大象"),
            ("YJ.XIAO_XIANG", "XIANG", "STRING", "NATAL", "YJ-XIAO-XIANG", "xiao_xiang", "小象"),
            ("YJ.CHANGED_HEXAGRAM", "CHANGED", "STRING", "NATAL", "YJ-CHANGED-HEXAGRAM", "changed_hexagram", "变卦"),
        ]
        for fid, cat, vtype, scope, rule_id, field, desc in defaults:
            if not self.registry.has(fid):
                self.registry.register(FeatureDefinition(
                    feature_id=fid, engine="YI_JING", namespace="YJ", category=cat,
                    value_type=vtype, scope=scope, source_rule_id=rule_id,
                    source_field=field, description=desc,
                ))

    def adapt(self, chart: Any) -> FeatureMapResult:
        resolved = []
        unmapped = []
        chart_dict = chart.to_dict() if hasattr(chart, 'to_dict') else (chart if isinstance(chart, dict) else {})
        field_map = {
            "YJ.HEXAGRAM": "hexagram",
            "YJ.HEXAGRAM_TEXT": "hexagram_text",
            "YJ.YAO": "yao",
            "YJ.YAO_TEXT": "yao_text",
            "YJ.TUAN_TEXT": "tuan_text",
            "YJ.DA_XIANG": "da_xiang",
            "YJ.XIAO_XIANG": "xiao_xiang",
            "YJ.CHANGED_HEXAGRAM": "changed_hexagram",
        }
        for fid, field_name in field_map.items():
            value = chart_dict.get(field_name)
            if value is not None and self.registry.has(fid):
                defn = self.registry.get(fid)
                resolved.append(Feature(
                    feature_id=fid, value=value, engine="YI_JING", namespace="YJ",
                    category=defn.category, value_type=defn.value_type, scope=defn.scope,
                    source_rule_id=defn.source_rule_id, source_field=defn.source_field,
                    source_evidence_ref=f"YJ-{field_name.upper()}",
                ))
            elif value is not None:
                unmapped.append({"rule_id": fid, "value": str(value)[:100]})
        return FeatureMapResult(
            engine="YI_JING", total_evidence=len(field_map),
            resolved=len(resolved), unmapped=len(unmapped),
            resolved_features=resolved, unmapped_evidence=unmapped,
        )
