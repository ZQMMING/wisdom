"""P6-C-3C-1 子平Feature Adapter - 基于BaziChart实际字段逐字段映射."""
from __future__ import annotations
from typing import Any
from tongshu.feature_registry.contract import (
    FeatureRegistry, FeatureDefinition, Feature, FeatureMapResult, BaseFeatureAdapter,
)


class ZiPingFeatureAdapter(BaseFeatureAdapter):
    def __init__(self, registry: FeatureRegistry):
        super().__init__(registry)
        self._register_default_features()

    def _register_default_features(self) -> None:
        defaults = [
            ("ZP.YEAR_PILLAR", "PILLAR", "STRING", "NATAL", "ZP-YEAR-PILLAR", "year_pillar", "年柱"),
            ("ZP.MONTH_PILLAR", "PILLAR", "STRING", "NATAL", "ZP-MONTH-PILLAR", "month_pillar", "月柱"),
            ("ZP.DAY_PILLAR", "PILLAR", "STRING", "NATAL", "ZP-DAY-PILLAR", "day_pillar", "日柱"),
            ("ZP.HOUR_PILLAR", "PILLAR", "STRING", "NATAL", "ZP-HOUR-PILLAR", "hour_pillar", "时柱"),
            ("ZP.YEAR_STEM", "PILLAR", "ENUM", "NATAL", "ZP-YEAR-STEM", "year_pillar.heavenly_stem", "年干"),
            ("ZP.YEAR_BRANCH", "PILLAR", "ENUM", "NATAL", "ZP-YEAR-BRANCH", "year_pillar.earthly_branch", "年支"),
            ("ZP.MONTH_STEM", "PILLAR", "ENUM", "NATAL", "ZP-MONTH-STEM", "month_pillar.heavenly_stem", "月干"),
            ("ZP.MONTH_BRANCH", "PILLAR", "ENUM", "NATAL", "ZP-MONTH-BRANCH", "month_pillar.earthly_branch", "月支"),
            ("ZP.DAY_STEM", "PILLAR", "ENUM", "NATAL", "ZP-DAY-STEM", "day_pillar.heavenly_stem", "日干"),
            ("ZP.DAY_BRANCH", "PILLAR", "ENUM", "NATAL", "ZP-DAY-BRANCH", "day_pillar.earthly_branch", "日支"),
            ("ZP.HOUR_STEM", "PILLAR", "ENUM", "NATAL", "ZP-HOUR-STEM", "hour_pillar.heavenly_stem", "时干"),
            ("ZP.HOUR_BRANCH", "PILLAR", "ENUM", "NATAL", "ZP-HOUR-BRANCH", "hour_pillar.earthly_branch", "时支"),
            ("ZP.DAY_MASTER", "DAY_MASTER", "ENUM", "NATAL", "ZP-DAY-MASTER", "day_master", "日主"),
            ("ZP.START_AGE", "LUCK", "FLOAT", "NATAL", "ZP-START-AGE", "start_age", "起运岁数"),
            ("ZP.LUCK_PILLARS", "LUCK", "LIST", "DA_YUN", "ZP-LUCK-PILLARS", "luck_pillars", "大运列表"),
            ("ZP.SPOUSE_STAR", "SPOUSE", "DICT", "NATAL", "ZP-SPOUSE-STAR", "spouse_star", "配偶星强度"),
            ("ZP.SPOUSE_STAR_ATTACK", "SPOUSE", "ENUM", "NATAL", "ZP-SPOUSE-STAR-ATTACK", "spouse_star_attack", "配偶星受克"),
            ("ZP.OFFICER_MIXED", "SPOUSE", "BOOLEAN", "NATAL", "ZP-OFFICER-MIXED", "officer_mixed", "官杀混杂"),
            ("ZP.SPOUSE_STAR_STRENGTH", "SPOUSE", "ENUM", "NATAL", "ZP-SPOUSE-STAR-STRENGTH", "spouse_star_strength", "配偶星强度档位"),
            ("ZP.PEACH_BLOSSOM", "SPOUSE", "BOOLEAN", "NATAL", "ZP-PEACH-BLOSSOM", "peach_blossom", "桃花"),
            ("ZP.DAY_BRANCH_CLASH", "RELATION", "BOOLEAN", "NATAL", "ZP-DAY-BRANCH-CLASH", "day_branch_clash", "日支被冲"),
            ("ZP.DAY_BRANCH_HARM", "RELATION", "BOOLEAN", "NATAL", "ZP-DAY-BRANCH-HARM", "day_branch_harm", "日支被害"),
            ("ZP.BRANCH_CLASH_MAP", "RELATION", "DICT", "NATAL", "ZP-BRANCH-CLASH-MAP", "branch_clash_map", "地支冲关系图"),
            ("ZP.BRANCH_HARM_MAP", "RELATION", "DICT", "NATAL", "ZP-BRANCH-HARM-MAP", "branch_harm_map", "地支害关系图"),
            ("ZP.BRANCH_HE_MAP", "RELATION", "DICT", "NATAL", "ZP-BRANCH-HE-MAP", "branch_he_map", "地支六合关系图"),
            ("ZP.BRANCH_SANHE_MAP", "RELATION", "DICT", "NATAL", "ZP-BRANCH-SANHE-MAP", "branch_sanhe_map", "地支三合关系图"),
            ("ZP.BRANCH_SANXING_MAP", "RELATION", "DICT", "NATAL", "ZP-BRANCH-SANXING-MAP", "branch_sanxing_map", "地支三刑关系图"),
            ("ZP.KONG_WANG", "RELATION", "TUPLE", "NATAL", "ZP-KONG-WANG", "kong_wang", "空亡"),
            ("ZP.FIVE_ELEMENT_BALANCE", "ELEMENT", "DICT", "NATAL", "ZP-FIVE-ELEMENT-BALANCE", "five_element_balance", "五行分布"),
            ("ZP.FIVE_ELEMENT_IMBALANCE", "ELEMENT", "BOOLEAN", "NATAL", "ZP-FIVE-ELEMENT-IMBALANCE", "five_element_imbalance", "五行失衡"),
            ("ZP.DAY_BRANCH_MAIN_TEN_GOD", "STRUCTURE", "STRING", "NATAL", "ZP-DAY-BRANCH-MAIN-TEN-GOD", "day_branch_main_ten_god", "日支主气十神"),
            ("ZP.GENDER", "STRUCTURE", "ENUM", "NATAL", "ZP-GENDER", "gender", "性别"),
        ]
        for fid, cat, vtype, scope, rule_id, field, desc in defaults:
            if not self.registry.has(fid):
                self.registry.register(FeatureDefinition(
                    feature_id=fid, engine="ZI_PING", namespace="ZP", category=cat,
                    value_type=vtype, scope=scope, source_rule_id=rule_id,
                    source_field=field, description=desc,
                ))

    def adapt(self, chart: Any) -> FeatureMapResult:
        resolved_features = []
        unmapped = []
        field_mappings = [
            ("ZP.YEAR_PILLAR", f"{chart.year_pillar.heavenly_stem}_{chart.year_pillar.earthly_branch}", "ZP-YEAR-PILLAR"),
            ("ZP.MONTH_PILLAR", f"{chart.month_pillar.heavenly_stem}_{chart.month_pillar.earthly_branch}", "ZP-MONTH-PILLAR"),
            ("ZP.DAY_PILLAR", f"{chart.day_pillar.heavenly_stem}_{chart.day_pillar.earthly_branch}", "ZP-DAY-PILLAR"),
            ("ZP.HOUR_PILLAR", f"{chart.hour_pillar.heavenly_stem}_{chart.hour_pillar.earthly_branch}", "ZP-HOUR-PILLAR"),
            ("ZP.YEAR_STEM", chart.year_pillar.heavenly_stem, "ZP-YEAR-STEM"),
            ("ZP.YEAR_BRANCH", chart.year_pillar.earthly_branch, "ZP-YEAR-BRANCH"),
            ("ZP.MONTH_STEM", chart.month_pillar.heavenly_stem, "ZP-MONTH-STEM"),
            ("ZP.MONTH_BRANCH", chart.month_pillar.earthly_branch, "ZP-MONTH-BRANCH"),
            ("ZP.DAY_STEM", chart.day_pillar.heavenly_stem, "ZP-DAY-STEM"),
            ("ZP.DAY_BRANCH", chart.day_pillar.earthly_branch, "ZP-DAY-BRANCH"),
            ("ZP.HOUR_STEM", chart.hour_pillar.heavenly_stem, "ZP-HOUR-STEM"),
            ("ZP.HOUR_BRANCH", chart.hour_pillar.earthly_branch, "ZP-HOUR-BRANCH"),
            ("ZP.DAY_MASTER", chart.day_master, "ZP-DAY-MASTER"),
            ("ZP.START_AGE", chart.start_age, "ZP-START-AGE"),
            ("ZP.GENDER", chart.gender, "ZP-GENDER"),
            ("ZP.SPOUSE_STAR", dict(chart.spouse_star), "ZP-SPOUSE-STAR"),
            ("ZP.SPOUSE_STAR_ATTACK", chart.spouse_star_attack, "ZP-SPOUSE-STAR-ATTACK"),
            ("ZP.OFFICER_MIXED", chart.officer_mixed, "ZP-OFFICER-MIXED"),
            ("ZP.DAY_BRANCH_CLASH", chart.day_branch_clash, "ZP-DAY-BRANCH-CLASH"),
            ("ZP.DAY_BRANCH_HARM", chart.day_branch_harm, "ZP-DAY-BRANCH-HARM"),
            ("ZP.SPOUSE_STAR_STRENGTH", chart.spouse_star_strength, "ZP-SPOUSE-STAR-STRENGTH"),
            ("ZP.PEACH_BLOSSOM", chart.peach_blossom, "ZP-PEACH-BLOSSOM"),
            ("ZP.BRANCH_CLASH_MAP", {k: list(v) for k, v in chart.branch_clash_map.items()}, "ZP-BRANCH-CLASH-MAP"),
            ("ZP.BRANCH_HARM_MAP", {k: list(v) for k, v in chart.branch_harm_map.items()}, "ZP-BRANCH-HARM-MAP"),
            ("ZP.BRANCH_HE_MAP", {k: list(v) for k, v in chart.branch_he_map.items()}, "ZP-BRANCH-HE-MAP"),
            ("ZP.BRANCH_SANHE_MAP", {k: list(v) for k, v in chart.branch_sanhe_map.items()}, "ZP-BRANCH-SANHE-MAP"),
            ("ZP.BRANCH_SANXING_MAP", {k: list(v) for k, v in chart.branch_sanxing_map.items()}, "ZP-BRANCH-SANXING-MAP"),
            ("ZP.KONG_WANG", list(chart.kong_wang), "ZP-KONG-WANG"),
            ("ZP.FIVE_ELEMENT_BALANCE", dict(chart.five_element_balance), "ZP-FIVE-ELEMENT-BALANCE"),
            ("ZP.FIVE_ELEMENT_IMBALANCE", chart.five_element_imbalance, "ZP-FIVE-ELEMENT-IMBALANCE"),
            ("ZP.DAY_BRANCH_MAIN_TEN_GOD", chart.day_branch_main_ten_god, "ZP-DAY-BRANCH-MAIN-TEN-GOD"),
            ("ZP.LUCK_PILLARS", [p.to_dict() for p in chart.luck_pillars], "ZP-LUCK-PILLARS"),
        ]
        for fid, value, ev_ref in field_mappings:
            if self.registry.has(fid):
                defn = self.registry.get(fid)
                resolved_features.append(Feature(
                    feature_id=fid, value=value, engine="ZI_PING", namespace="ZP",
                    category=defn.category, value_type=defn.value_type, scope=defn.scope,
                    source_rule_id=defn.source_rule_id, source_field=defn.source_field,
                    source_evidence_ref=ev_ref,
                ))
            else:
                unmapped.append({"rule_id": fid, "value": str(value)[:100]})
        return FeatureMapResult(
            engine="ZI_PING", total_evidence=len(field_mappings),
            resolved=len(resolved_features), unmapped=len(unmapped),
            resolved_features=resolved_features, unmapped_evidence=unmapped,
        )
