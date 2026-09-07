"""P6-C-3C-1 梅花易数Feature Adapter - 基于MeihuaResult实际字段."""
from __future__ import annotations
from typing import Any
from tongshu.feature_registry.contract import (
    FeatureRegistry, FeatureDefinition, Feature, FeatureMapResult, BaseFeatureAdapter,
)


class MeiHuaFeatureAdapter(BaseFeatureAdapter):
    def __init__(self, registry: FeatureRegistry):
        super().__init__(registry)
        self._register_default_features()

    def _register_default_features(self) -> None:
        defaults = [
            ("MH.BEN_GUA", "HEXAGRAM", "STRING", "NATAL", "MH-BEN-GUA", "ben_gua", "本卦"),
            ("MH.UPPER", "TRIGRAM", "STRING", "NATAL", "MH-UPPER", "upper", "上卦"),
            ("MH.LOWER", "TRIGRAM", "STRING", "NATAL", "MH-LOWER", "lower", "下卦"),
            ("MH.BIAN_GUA", "CHANGED", "STRING", "NATAL", "MH-BIAN-GUA", "bian_gua", "变卦"),
            ("MH.HU_GUA", "HUA_GUA", "STRING", "NATAL", "MH-HU-GUA", "hu_gua", "互卦"),
            ("MH.CUO_GUA", "CUO_GUA", "STRING", "NATAL", "MH-CUO-GUA", "cuo_gua", "错卦"),
            ("MH.ZONG_GUA", "ZONG_GUA", "STRING", "NATAL", "MH-ZONG-GUA", "zong_gua", "综卦"),
            ("MH.DONG_YAO", "DONG_YAO", "INT", "NATAL", "MH-DONG-YAO", "dong_yao_1based", "动爻"),
            ("MH.TI", "TI_YONG", "STRING", "NATAL", "MH-TI", "ti", "体卦"),
            ("MH.YONG", "TI_YONG", "STRING", "NATAL", "MH-YONG", "yong", "用卦"),
            ("MH.TI_ELEMENT", "TI_YONG", "STRING", "NATAL", "MH-TI-ELEM", "ti_element", "体卦五行"),
            ("MH.YONG_ELEMENT", "TI_YONG", "STRING", "NATAL", "MH-YONG-ELEM", "yong_element", "用卦五行"),
            ("MH.TI_YONG_RELATION", "TI_YONG", "STRING", "NATAL", "MH-TI-YONG-REL", "ti_yong_relation", "体用关系"),
            ("MH.METHOD", "METHOD", "STRING", "NATAL", "MH-METHOD", "method", "起卦方法"),
            ("MH.QUESTION", "QUESTION", "STRING", "NATAL", "MH-QUESTION", "question", "所问之事"),
        ]
        for fid, cat, vtype, scope, rule_id, field, desc in defaults:
            if not self.registry.has(fid):
                self.registry.register(FeatureDefinition(
                    feature_id=fid, engine="MEIHUA", namespace="MH", category=cat,
                    value_type=vtype, scope=scope, source_rule_id=rule_id,
                    source_field=field, description=desc,
                ))

    def adapt(self, chart: Any) -> FeatureMapResult:
        resolved = []
        unmapped = []
        chart_dict = chart.to_dict() if hasattr(chart, 'to_dict') else (chart if isinstance(chart, dict) else {})
        field_map = {
            "MH.BEN_GUA": "ben_gua",
            "MH.UPPER": "upper",
            "MH.LOWER": "lower",
            "MH.BIAN_GUA": "bian_gua",
            "MH.HU_GUA": "hu_gua",
            "MH.CUO_GUA": "cuo_gua",
            "MH.ZONG_GUA": "zong_gua",
            "MH.DONG_YAO": "dong_yao_1based",
            "MH.TI": "ti",
            "MH.YONG": "yong",
            "MH.TI_ELEMENT": "ti_element",
            "MH.YONG_ELEMENT": "yong_element",
            "MH.TI_YONG_RELATION": "ti_yong_relation",
            "MH.METHOD": "method",
            "MH.QUESTION": "question",
        }
        for fid, field_name in field_map.items():
            value = chart_dict.get(field_name)
            if value is not None and self.registry.has(fid):
                defn = self.registry.get(fid)
                resolved.append(Feature(
                    feature_id=fid, value=value, engine="MEIHUA", namespace="MH",
                    category=defn.category, value_type=defn.value_type, scope=defn.scope,
                    source_rule_id=defn.source_rule_id, source_field=defn.source_field,
                    source_evidence_ref=f"MH-{field_name.upper()}",
                ))
            elif value is not None:
                unmapped.append({"rule_id": fid, "value": str(value)[:100]})
        return FeatureMapResult(
            engine="MEIHUA", total_evidence=len(field_map),
            resolved=len(resolved), unmapped=len(unmapped),
            resolved_features=resolved, unmapped_evidence=unmapped,
        )
