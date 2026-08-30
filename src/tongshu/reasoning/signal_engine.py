# -*- coding: utf-8 -*-
"""Signal Engine - extracts Universal Signals from Bazi / Ziwei / Huangli charts.

Per architecture_decisions_v1.md DECISION-002, signals MUST be preserved
across three layers (BASELINE / CYCLE_CONTEXT / DAILY_ACTIVATION) independently.

T201/T205 (v3.1): rule matching runs through RuleMatcher (typed condition DSL)
and resolve_conflicts (precedence + specificity; an unresolvable tie drops the
Signal). The single source of rules is backend/data/rules/*.json via RuleLoader.
"""

from __future__ import annotations
from dataclasses import dataclass, replace

from ..engines.bazi_engine import STEM_ELEMENT
from ..spec.signal_ontology import USO_TYPES
from ..spec.signal_layers import SIGNAL_LAYERS
from .matcher import RuleContext, RuleMatcher, resolve_conflicts, rule_refs_of
from .bazi_ten_gods import (
    SEASON_BY_BRANCH,
    hidden_main_stem_is_transparent,
    hidden_main_stem,
    month_hidden_main_ten_god,
    ten_god,
    transparent_ten_gods as transparent_ten_gods_list,
)
from .bazi_fixed_tables import (
    longhu_stage,
    road_branch,
    absolute_branch,
    tianyi_guiren,
)

# 河洛五行映射（上卦→五行）
_HELUO_TRIGRAM_ELEMENT = {
    "乾": "金", "兑": "金", "离": "火", "震": "木",
    "巽": "木", "坎": "水", "艮": "土", "坤": "土",
}

# 河洛五行→八字五行键名映射
_HELUO_WUXING_TO_BASI_KEY = {
    "金": "METAL", "木": "WOOD", "水": "WATER", "火": "FIRE", "土": "EARTH",
}

# 河洛不利时节（谷雨-芒种≈辰月，即农历三月）
_HELUO_UNFAVORABLE_BRANCHES = {"辰"}

# 五行失衡阈值（本命卦五行在八字中占比）
_WUXING_OVER_THRESHOLD = 0.30  # >30% 为过旺
_WUXING_UNDER_THRESHOLD = 0.10  # <10% 为不及


def extract_heluo_context(heluo_result, bazi) -> dict:
    """从HeluoResult提取规则匹配所需的河洛字段。"""
    if heluo_result is None:
        return {}
    out = {}
    benming_wuxing = None
    prenatal = getattr(heluo_result, "prenatal", None)
    if prenatal and getattr(prenatal, "upper_gua", None):
        elem = _HELUO_TRIGRAM_ELEMENT.get(prenatal.upper_gua)
        if elem:
            out["heluo_benming_guawuxing"] = elem
            benming_wuxing = elem
        out["heluo_benming_gong"] = prenatal.upper_gua
        out["heluo_benming_guaming"] = getattr(prenatal, "hexagram_name", None)
    yuantang = getattr(heluo_result, "yuantang", None)
    if yuantang:
        out["heluo_yuantang"] = getattr(yuantang, "yuantang", None)
        out["heluo_yuantang_index"] = getattr(yuantang, "yuantang_index", None)
    postnatal = getattr(heluo_result, "postnatal", None)
    if postnatal:
        out["heluo_houtian_guaming"] = getattr(postnatal, "hexagram_name", None)
    numbers = getattr(heluo_result, "numbers", None)
    if numbers and getattr(numbers, "di_shu", None) is not None:
        out["heluo_dishu_youyu"] = numbers.di_shu > 30
    if bazi and getattr(bazi, "month_pillar", None):
        out["heluo_birth_season_unfavorable"] = (
            bazi.month_pillar.earthly_branch in _HELUO_UNFAVORABLE_BRANCHES
        )
    if benming_wuxing and bazi and getattr(bazi, "five_element_balance", None):
        bazi_key = _HELUO_WUXING_TO_BASI_KEY.get(benming_wuxing)
        if bazi_key and bazi_key in bazi.five_element_balance:
            ratio = bazi.five_element_balance[bazi_key]
            if ratio > _WUXING_OVER_THRESHOLD:
                out["heluo_wuxing_imbalance"] = "over"
            elif ratio < _WUXING_UNDER_THRESHOLD:
                out["heluo_wuxing_imbalance"] = "under"
            else:
                out["heluo_wuxing_imbalance"] = "none"
        else:
            out["heluo_wuxing_imbalance"] = "none"
    else:
        out["heluo_wuxing_imbalance"] = "none"
    return out


SIGNAL_LAYER_ORDER = ("BASELINE", "CYCLE_CONTEXT", "DAILY_ACTIVATION")


@dataclass(frozen=True)
class Signal:
    signal_id: str
    ontology_type: str
    direction: str
    polarity: str
    strength: str
    layer: str
    rule_refs: list
    evidence_refs: list

    def __post_init__(self):
        if self.ontology_type not in USO_TYPES:
            raise ValueError(f"Invalid ontology_type: {self.ontology_type}")
        if self.layer not in SIGNAL_LAYERS:
            raise ValueError(f"Invalid layer: {self.layer}")


def _FOUR_BRANCHES(bazi) -> list[str]:
    return [
        bazi.year_pillar.earthly_branch,
        bazi.month_pillar.earthly_branch,
        bazi.day_pillar.earthly_branch,
        bazi.hour_pillar.earthly_branch,
    ]


def build_rule_context(bazi, ziwei, huangli, layer=None, theme=None, heluo_result=None) -> RuleContext:
    heluo_fields = extract_heluo_context(heluo_result, bazi)
    return RuleContext(
        day_master=bazi.day_master if bazi else None,
        day_master_element=STEM_ELEMENT[bazi.day_master] if bazi else None,
        day_branch=bazi.day_pillar.earthly_branch if bazi else None,
        month_stem=bazi.month_pillar.heavenly_stem if bazi else None,
        month_branch=bazi.month_pillar.earthly_branch if bazi else None,
        year_stem=bazi.year_pillar.heavenly_stem if bazi else None,
        year_branch=bazi.year_pillar.earthly_branch if bazi else None,
        hour_stem=bazi.hour_pillar.heavenly_stem if bazi else None,
        hour_branch=bazi.hour_pillar.earthly_branch if bazi else None,
        season=(
            SEASON_BY_BRANCH.get(bazi.month_pillar.earthly_branch)
            if bazi else None
        ),
        month_hidden_main_ten_god=(
            month_hidden_main_ten_god(bazi.day_master, bazi.month_pillar.earthly_branch)
            if bazi else None
        ),
        month_hidden_main_ten_god_transparent=(
            hidden_main_stem_is_transparent(
                bazi.month_pillar.earthly_branch,
                [
                    bazi.year_pillar.heavenly_stem,
                    bazi.month_pillar.heavenly_stem,
                    bazi.day_pillar.heavenly_stem,
                    bazi.hour_pillar.heavenly_stem,
                ],
            )
            if bazi else None
        ),
        transparent_ten_gods=(
            transparent_ten_gods_list(
                bazi.day_master,
                bazi.year_pillar.heavenly_stem,
                bazi.month_pillar.heavenly_stem,
                bazi.hour_pillar.heavenly_stem,
            )
            if bazi else None
        ),
        day_master_stage_month=(
            longhu_stage(bazi.day_master, bazi.month_pillar.earthly_branch)
            if bazi else None
        ),
        day_master_road_month=(
            road_branch(bazi.day_master) == bazi.month_pillar.earthly_branch
            if bazi else None
        ),
        day_master_absolute_month=(
            absolute_branch(bazi.day_master) == bazi.month_pillar.earthly_branch
            if bazi else None
        ),
        day_branch_main_ten_god=(
            ten_god(bazi.day_master, hidden_main_stem(bazi.day_pillar.earthly_branch))
            if bazi else None
        ),
        tianyi_guiren_branches=(
            [b for b in _FOUR_BRANCHES(bazi) if b in tianyi_guiren(bazi.day_master)]
            if bazi else None
        ),
        soul_palace_main_star_key=ziwei.soul_palace_main_star if ziwei else None,
        soul_palace_main_star_zh=(
            (ziwei.palace_data or {}).get("raw_soul_main_star") if ziwei else None
        ),
        analysis_day_stem=huangli.day_stem if huangli else None,
        analysis_day_branch=huangli.day_branch if huangli else None,
        layer=layer,
        theme=theme,
        **heluo_fields,
    )


# ═══════════════════════════════════════════════════════════════════
# T1 修复: produces_semantic_atoms → direction/polarity 推导
# ═══════════════════════════════════════════════════════════════════
# 方向: INCREASE / STABLE / DECREASE
# 极性: active / neutral / restricted

_ATOM_DIRECTION_MAP = {
    # SUPPORT 族: 稳定支撑(非增长)
    "SUPPORT": "STABLE",
    "STRENGTHEN": "STABLE",
    "PROTECTION": "STABLE",
    "RESOURCE": "STABLE",
    "ENDURANCE": "STABLE",
    "STABILITY": "STABLE",
    "NEUTRAL": "STABLE",
    "BALANCE": "STABLE",
    "CALM": "STABLE",
    # ACTION 族: 推动增长
    "ACTION": "INCREASE",
    "EXECUTION": "INCREASE",
    "INITIATIVE": "INCREASE",
    "MOVEMENT": "INCREASE",
    "EXPANSION": "INCREASE",
    "GROWTH": "INCREASE",
    # CONTRACTION 族: 收缩减弱
    "WEAKEN": "DECREASE",
    "OPPOSE": "DECREASE",
    "RESTRAINT": "DECREASE",
    "CONTRACTION": "DECREASE",
}

_ATOM_POLARITY_MAP = {
    # SUPPORT 族: 积极支持
    "SUPPORT": "active",
    "STRENGTHEN": "active",
    "PROTECTION": "active",
    "RESOURCE": "active",
    "ENDURANCE": "active",
    # ACTION 族: 主动推进
    "ACTION": "active",
    "EXECUTION": "active",
    "INITIATIVE": "active",
    "MOVEMENT": "active",
    "EXPANSION": "active",
    "GROWTH": "active",
    # OUTPUT 族: 输出也是积极的（表达、创造）
    "OUTPUT": "active",
    "CREATE": "active",
    "EXPRESS": "active",
    "GENERATE": "active",
    # CONSTRAINT 族: 规范约束也是积极的（有序即积极）
    "CONSTRAINT": "active",
    "DISCIPLINE": "active",
    "RULE": "active",
    "RESPONSIBILITY": "active",
    # RELATION 族: 同我关系也是积极的（互助即积极）
    "RELATION": "active",
    "SOCIAL": "active",
    "CONNECTION": "active",
    "PARTNERSHIP": "active",
    # STABILITY 族: 中性稳定
    "STABILITY": "neutral",
    "NEUTRAL": "neutral",
    "BALANCE": "neutral",
    "CALM": "neutral",
    # CONTRACTION 族: 限制约束
    "WEAKEN": "restricted",
    "OPPOSE": "restricted",
    "RESTRAINT": "restricted",
    "CONTRACTION": "restricted",
}


def _derive_direction_polarity(rule: dict) -> tuple[str | None, str | None]:
    """从 rule conclusion 推导 (direction, polarity)。

    支持两种格式：
    1. produces_layer_output_template → 直接取 template["direction"/"polarity"]
    2. produces_semantic_atoms → 从第一个原子推导
    """
    conclusion = rule.get("conclusion", {})

    # 格式1: produces_layer_output_template
    template = conclusion.get("produces_layer_output_template")
    if template is not None:
        return template.get("direction"), template.get("polarity")

    # 格式2: produces_semantic_atoms
    atoms = conclusion.get("produces_semantic_atoms")
    if atoms is not None and len(atoms) > 0:
        first_atom = atoms[0]
        direction = _ATOM_DIRECTION_MAP.get(first_atom, "STABLE")
        polarity = _ATOM_POLARITY_MAP.get(first_atom, "neutral")
        return direction, polarity

    return None, None


def _rule_to_signal(rule: dict, layer: str, index: int, extra_id: str = "") -> Signal | None:
    direction, polarity = _derive_direction_polarity(rule)
    if direction is None:
        return None
    return Signal(
        signal_id=f"SIG-{layer[:2].upper()}-{extra_id}{index:03d}",
        ontology_type=rule["produces_signal_type"],
        direction=direction,
        polarity=polarity,
        strength="moderate",
        layer=layer,
        rule_refs=rule_refs_of(rule),
        evidence_refs=rule.get("evidence_refs", []),
    )


def _build_layer_signals(matcher, bazi, ziwei, huangli, layer, gender, theme, heluo_result=None) -> list:
    ctx = build_rule_context(bazi, ziwei, huangli, layer=layer, theme=theme, heluo_result=heluo_result)
    ctx = replace(ctx, gender=gender)
    matched = matcher.match_all(ctx, layer=layer)
    resolved = resolve_conflicts(matched)
    if layer in ("BASELINE", "CYCLE_CONTEXT"):
        extra_id = bazi.day_master if bazi else ""
    else:
        extra_id = huangli.day_stem if huangli else ""
    return [
        s for s in (
            _rule_to_signal(r, layer, i, extra_id)
            for i, r in enumerate(resolved)
        )
        if s is not None
    ]


def build_signals(bazi, ziwei, huangli, matcher, gender, theme=None, heluo_result=None) -> dict:
    """Match rules per layer and emit one Signal per resolved (layer, type).

    gender is REQUIRED per Profile Contract §1.2 (forbidden_default=true).
    """
    assert gender in ("male", "female"), f"gender must be male/female, got {gender!r}"
    return {
        layer: _build_layer_signals(matcher, bazi, ziwei, huangli, layer, gender, theme, heluo_result=heluo_result)
        for layer in SIGNAL_LAYER_ORDER
    }


class SignalEngine:
    def __init__(self, matcher: RuleMatcher):
        self._matcher = matcher

    def build(self, bazi, ziwei, huangli, gender, theme=None, heluo_result=None) -> dict:
        """Build signals. gender is REQUIRED."""
        return build_signals(bazi, ziwei, huangli, self._matcher, gender=gender, theme=theme, heluo_result=heluo_result)
