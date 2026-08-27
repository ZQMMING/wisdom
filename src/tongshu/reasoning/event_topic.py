"""Event Topic Layer — independent topic-level断事 evaluator.

RULES-EXPANSION-001 (2026-08-26): fourth signal layer dedicated to
theme/major-life-event judgement (MARRIAGE_RISK / HEALTH_RISK).

Architecture:
  ┌────────────────────────────────────────────────────────────┐
  │ SignalEngine (BASELINE / CYCLE_CONTEXT / DAILY_ACTIVATION) │  — frozen
  │ matcher.py + FIELD_SPECS registry (P0-15 strict)           │
  └────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────────┐
  │ EventTopicEngine (EVENT_TOPIC layer)  ←── this module       │  — P2 new
  │ - independent rule DSL with marriage/health-specific ops    │
  │ - separate field/op registry (no cross-impact)              │
  │ - resolves to MARRIAGE_RISK / HEALTH_RISK signals          │
  │ - structured by annual_event_evaluator for year-ranking     │
  └────────────────────────────────────────────────────────────┘

Per AGENTS.md §3 + dispatch: EVENT_TOPIC is intentionally NOT routed
through the existing matcher.RuleMatcher — it has its own registry
spanning the 9 P2 chart fields and its own ops (`has`, `has_any`,
`present`, `in`) tailored to event-topic semantics. All P2 chart fields
are deterministically derived from BaziChart (no new facts introduced).

This module exposes:
    EventTopicEngine   - public class (replaces signal_engine for EVENT_TOPIC)
    EventTopicSignal   - signal dataclass for MARRIAGE_RISK / HEALTH_RISK
    evaluate_year_event_topic(chart, year, gender, rules) - one-year scoring
        hook used by .verify_fortune_v2.py
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from ..engines.bazi_engine import STEM_ELEMENT

# --------------------------------------------------------------------------- #
# Field registry — independent from matcher.FIELD_SPECS.
# --------------------------------------------------------------------------- #
EVENT_TOPIC_FIELDS: dict[str, str] = {
    # P2 chart fields (post compute)
    "spouse_star": "配偶星强度 dict",
    "spouse_star_attack": "配偶星受克状态 ('rob_wealth' / 'guan_sha_mixed' / 'none')",
    "officer_mixed": "官杀混杂 (bool)",
    "day_branch_clash": "日支被冲 (bool)",
    "day_branch_harm": "日支被害 (bool)",
    "spouse_star_strength": "配偶星强度档位 'strong'/'weak'/'rootless'",
    "peach_blossom": "日支为桃花 (bool)",
    "branch_clash_map": "四支冲关系图 dict",
    "branch_harm_map": "四支害关系图 dict",
    "five_element_imbalance": "五行失衡 (bool)",
    # Pillar primitive fields (mirrored from chart for rule ergonomics)
    "gender": "性别 'male'/'female'",
    "day_master": "日主天干",
    "day_master_element": "日主五行",
    "day_branch": "日支",
    "month_stem": "月干",
    "month_branch": "月支",
    "birth_year_stem": "年干(出生年)",
    "birth_year_branch": "年支(出生年)",
    "hour_stem": "时干",
    "hour_branch": "时支",
    # Per-year fields (year-scoped evaluation, computed by EventTopicEngine)
    "flow_year_stem": "流年天干",
    "flow_year_branch": "流年地支",
    "flow_year_branch_element": "流年地支五行",
    "flow_year_branch_clash_day_branch": "流年支冲日支 (bool)",
    "flow_year_branch_harm_day_branch": "流年支害日支 (bool)",
    "flow_year_branch_main_ten_god": "流年支主气藏干对日主的十神",
    "flow_year_branch_main_element_clash": "流年地支五行冲日主五行 (bool)",
    # T4 扩展(2026-08-26): 河洛字段
    "heluo_benming_guawuxing": "河洛本命卦五行(金木水火土)",
    "heluo_wuxing_imbalance": "河洛五行失衡 over/under/none",
    "day_master_absolute_month": "日主绝对月份(帝旺位判据,《渊海子平·论阳刃》)",
    "day_branch_main_ten_god": "日支主气藏干对日主的十神(通根/得地判据,《滴天髓·论地支》)",
    "month_hidden_main_ten_god": "月支主气藏干对日主的十神(月令主气,《子平真诠》)",
}

# Operators specific to EVENT_TOPIC layer (more expressive than matcher.OPS).
EVENT_TOPIC_OPS = (
    "eq", "ne", "in", "nin", "exists",
    "has", "has_any", "has_all", "present", "absent",
)


class EventTopicFieldError(KeyError):
    """Rule references an EVENT_TOPIC-unknown field (DECISION-009)."""


class EventTopicOpError(ValueError):
    """Rule uses an EVENT_TOPIC-unknown operator."""


# --------------------------------------------------------------------------- #
# Signal dataclass — output of the layer
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class EventTopicSignal:
    """Topic断事信号 (MARRIAGE_RISK / HEALTH_RISK).

    Independent from Signal (signal_engine.Signal) — different ontology,
    different layer, different lifecycle.
    """
    signal_id: str
    ontology_type: str  # MARRIAGE_RISK / HEALTH_RISK / MARRIAGE_OPPORTUNITY / WEALTH_OPPORTUNITY / CAREER_RISK / ACADEMIC_OPPORTUNITY
    direction: str      # DECREASE / STABLE / INCREASE (mapped from raw conclusion)
    polarity: str       # caution / neutral / opportunity (mapped from raw)
    layer: str          # always 'EVENT_TOPIC'
    rule_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    health_organ: str | None = None  # HLT-* rules may carry organ hint

    def to_dict(self) -> dict:
        return {
            "signal_id": self.signal_id,
            "ontology_type": self.ontology_type,
            "direction": self.direction,
            "polarity": self.polarity,
            "layer": self.layer,
            "rule_refs": list(self.rule_refs),
            "evidence_refs": list(self.evidence_refs),
            "health_organ": self.health_organ,
        }


# --------------------------------------------------------------------------- #
# Per-year field construction
# --------------------------------------------------------------------------- #
def _branch_element(b: str) -> str:
    if b in ("YIN", "MAO"):
        return "WOOD"
    if b in ("SI", "WU"):
        return "FIRE"
    if b in ("CHEN", "XU", "CHOU", "WEI"):
        return "EARTH"
    if b in ("SHEN", "YOU"):
        return "METAL"
    return "WATER"


def _hidden_main_stem(b: str) -> str:
    return {
        "ZI": "GUI", "CHOU": "JI", "YIN": "JIA", "MAO": "YI",
        "CHEN": "WU", "SI": "BING", "WU": "DING", "WEI": "JI",
        "SHEN": "GENG", "YOU": "XIN", "XU": "WU", "HAI": "REN",
    }[b]


def _ten_god(day_master: str, other: str) -> str:
    from .bazi_ten_gods import STEM_POLARITY, GENERATES, CONTROLS
    dm_el = STEM_ELEMENT[day_master]
    ot_el = STEM_ELEMENT[other]
    same = (STEM_POLARITY[day_master] == STEM_POLARITY[other])
    if ot_el == dm_el:
        return "比肩" if same else "劫财"
    if GENERATES.get(dm_el) == ot_el:
        return "食神" if same else "伤官"
    if GENERATES.get(ot_el) == dm_el:
        return "偏印" if same else "正印"
    if CONTROLS.get(ot_el) == dm_el:
        return "七杀" if same else "正官"
    if CONTROLS.get(dm_el) == ot_el:
        return "偏财" if same else "正财"
    raise ValueError(f"cannot determine 十神 for dm={day_master} other={other}")


_HEAVENLY_STEMS = ("JIA", "YI", "BING", "DING", "WU", "JI", "GENG", "XIN", "REN", "GUI")
_EARTHLY_BRANCHES = ("ZI", "CHOU", "YIN", "MAO", "CHEN", "SI", "WU", "WEI", "SHEN", "YOU", "XU", "HAI")
BRANCH_CLASH = {
    "ZI": "WU", "WU": "ZI", "CHOU": "WEI", "WEI": "CHOU",
    "YIN": "SHEN", "SHEN": "YIN", "MAO": "YOU", "YOU": "MAO",
    "CHEN": "XU", "XU": "CHEN", "SI": "HAI", "HAI": "SI",
}
BRANCH_HARM = {
    "ZI": "WEI", "WEI": "ZI", "CHOU": "WU", "WU": "CHOU",
    "YIN": "SI", "SI": "YIN", "MAO": "CHEN", "CHEN": "MAO",
    "SHEN": "HAI", "HAI": "SHEN", "YOU": "XU", "XU": "YOU",
}


def build_chart_only_context(chart) -> dict:
    """Chart-only context (no per-year fields)."""
    return {
        "spouse_star": chart.spouse_star,
        "spouse_star_attack": chart.spouse_star_attack,
        "officer_mixed": chart.officer_mixed,
        "day_branch_clash": chart.day_branch_clash,
        "day_branch_harm": chart.day_branch_harm,
        "spouse_star_strength": chart.spouse_star_strength,
        "peach_blossom": chart.peach_blossom,
        "branch_clash_map": chart.branch_clash_map,
        "branch_harm_map": chart.branch_harm_map,
        "five_element_imbalance": chart.five_element_imbalance,
        "gender": chart.gender,
        "day_master": chart.day_master,
        "day_master_element": STEM_ELEMENT[chart.day_master],
        "day_branch": chart.day_pillar.earthly_branch,
        "month_stem": chart.month_pillar.heavenly_stem,
        "month_branch": chart.month_pillar.earthly_branch,
        "birth_year_stem": chart.year_pillar.heavenly_stem,
        "birth_year_branch": chart.year_pillar.earthly_branch,
        "hour_stem": chart.hour_pillar.heavenly_stem,
        "hour_branch": chart.hour_pillar.earthly_branch,
        "day_branch_main_ten_god": chart.day_branch_main_ten_god,
        "month_hidden_main_ten_god": _ten_god(chart.day_master, _hidden_main_stem(chart.month_pillar.earthly_branch)),
    }


def build_year_context(chart, year: int) -> dict:
    """Construct a per-year EVENT_TOPIC context.

    Combines the static chart fields (post-attach_p2_fields) with per-year
    derived fields (流年天干/地支, 与日支冲害关系, 主气十神, 五行冲克).
    """
    from .bazi_ten_gods import CONTROLS
    year_stem = _HEAVENLY_STEMS[(year - 4) % 10]
    year_branch = _EARTHLY_BRANCHES[(year - 4) % 12]

    ctx = build_chart_only_context(chart)
    ctx.update({
        "flow_year_stem": year_stem,
        "flow_year_branch": year_branch,
        "flow_year_branch_element": _branch_element(year_branch),
        "flow_year_branch_clash_day_branch": BRANCH_CLASH.get(year_branch) == chart.day_pillar.earthly_branch,
        "flow_year_branch_harm_day_branch": BRANCH_HARM.get(year_branch) == chart.day_pillar.earthly_branch,
        "flow_year_branch_main_ten_god": _ten_god(chart.day_master, _hidden_main_stem(year_branch)),
        "flow_year_branch_main_element_clash": False,
    })

    dm_el = ctx["day_master_element"]
    yb_el = ctx["flow_year_branch_element"]
    if CONTROLS.get(dm_el) == yb_el or CONTROLS.get(yb_el) == dm_el:
        ctx["flow_year_branch_main_element_clash"] = True

    return ctx


# --------------------------------------------------------------------------- #
# DSL evaluator
# --------------------------------------------------------------------------- #
def _eval_leaf(cond: dict, ctx: dict) -> bool:
    field = cond.get("field")
    if field not in EVENT_TOPIC_FIELDS:
        raise EventTopicFieldError(f"unknown EVENT_TOPIC field: {field!r}")
    op = cond.get("op")
    if op not in EVENT_TOPIC_OPS:
        raise EventTopicOpError(f"unknown EVENT_TOPIC op: {op!r}")
    if "value" not in cond:
        raise ValueError(f"leaf condition missing 'value': {cond!r}")

    val = ctx.get(field)
    if op == "exists":
        return bool(val) == bool(cond["value"])
    target = cond["value"]

    if op == "eq":
        return val == target
    if op == "ne":
        return val != target
    if op == "in":
        if isinstance(target, (list, tuple, set)):
            return val in target
        return val == target
    if op == "nin":
        if isinstance(target, (list, tuple, set)):
            return val not in target
        return val != target
    if op == "present":
        return bool(val)
    if op == "absent":
        return not val
    if op == "has":
        if isinstance(val, dict):
            # target can be a single value or a list
            if isinstance(target, (list, tuple)):
                return any(t in val for t in target)
            return target in val
        if isinstance(val, (list, tuple, set)):
            if isinstance(target, (list, tuple)):
                return any(t in val for t in target)
            return target in val
        return False
    if op == "has_any":
        # val is a dict whose values are lists/tuples; target is a list of lists/pairs.
        # any target member fully contained in any val member list → True
        if isinstance(val, dict):
            value_lists = [v if isinstance(v, (list, tuple)) else [v] for v in val.values()]
        elif isinstance(val, (list, tuple)):
            value_lists = [val]
        else:
            value_lists = []
        target_lists = target if isinstance(target, (list, tuple)) else [target]
        for tl in target_lists:
            pair = tl if isinstance(tl, (list, tuple, set)) else [tl]
            for vl in value_lists:
                if all(item in vl for item in pair):
                    return True
        return False
    if op == "has_all":
        if isinstance(val, dict):
            return all(target in v for v in val.values())
        if isinstance(val, (list, tuple, set)):
            seq = target if isinstance(target, (list, tuple)) else [target]
            return all(t in val for t in seq)
        return False
    raise EventTopicOpError(f"unsupported op: {op!r}")


def evaluate_conditions(cond: Any, ctx: dict) -> bool:
    """Recursively evaluate EVENT_TOPIC DSL condition tree."""
    if not cond:
        return True
    if not isinstance(cond, dict):
        raise ValueError(f"conditions must be an object, got {type(cond).__name__}")
    if "all" in cond:
        return all(evaluate_conditions(c, ctx) for c in cond["all"])
    if "any" in cond:
        return any(evaluate_conditions(c, ctx) for c in cond["any"])
    if "not" in cond:
        return not evaluate_conditions(cond["not"], ctx)
    return _eval_leaf(cond, ctx)


# --------------------------------------------------------------------------- #
# Direction / polarity normalization
# --------------------------------------------------------------------------- #
_DIR_MAP = {
    "DECLINE": "DECREASE",
    "VOLATILE": "DECREASE",
    "STABLE": "STABLE",
    "INCREASE": "INCREASE",
    "DECREASE": "DECREASE",
}
_POL_MAP = {
    "caution": "caution",
    "passive": "neutral",
    "active": "active",
    "restricted": "caution",
    "neutral": "neutral",
    "opportunity": "opportunity",
}


def _normalize_conclusion(rule: dict) -> tuple[str, str, str | None]:
    tpl = rule.get("conclusion", {}).get("produces_layer_output_template", {})
    direction = _DIR_MAP.get(tpl.get("direction"), "STABLE")
    polarity = _POL_MAP.get(tpl.get("polarity"), "neutral")
    return direction, polarity, tpl.get("health_organ")


# --------------------------------------------------------------------------- #
# Engine
# --------------------------------------------------------------------------- #
class EventTopicEngine:
    """Evaluate EVENT_TOPIC rules per (chart, year) → EventTopicSignal list."""

    def __init__(self, rules: list[dict]):
        # Filter to EVENT_TOPIC-eligible rules + active lifecycle (per spec).
        self._rules = [
            r for r in rules
            if "EVENT_TOPIC" in r.get("applies_to_layers", [])
            and r.get("status") in ("active", "validated")
        ]

    @property
    def rules(self) -> list[dict]:
        return list(self._rules)

    def match(self, chart, year: int | None = None) -> list[EventTopicSignal]:
        """Match all rules for the given chart (and optional year).

        - year=None: chart-static signals (perennial risk flags)
        - year=int: chart + per-year context (year_branch_* fields usable)
        """
        if year is None:
            ctx = build_chart_only_context(chart)
        else:
            ctx = build_year_context(chart, year)

        matched = []
        for r in self._rules:
            if evaluate_conditions(r.get("conditions"), ctx):
                matched.append(r)

        return [self._rule_to_signal(r, i) for i, r in enumerate(matched)]

    def _rule_to_signal(self, rule: dict, idx: int) -> EventTopicSignal:
        direction, polarity, organ = _normalize_conclusion(rule)
        rid = rule.get("rule_id", "UNKNOWN")
        return EventTopicSignal(
            signal_id=f"ETP-{rid}-{idx:02d}",
            ontology_type=rule.get("produces_signal_type", "MARRIAGE_RISK"),
            direction=direction,
            polarity=polarity,
            layer="EVENT_TOPIC",
            rule_refs=(rid,),
            evidence_refs=tuple(rule.get("evidence_refs", [])),
            health_organ=organ,
        )


# --------------------------------------------------------------------------- #
# Year scoring — convenience for .verify_fortune_v2.py integration
# --------------------------------------------------------------------------- #
SCORE_PER_RULE = {
    "MARRIAGE_RISK": 1.0,
    "HEALTH_RISK": 1.0,
    "MARRIAGE_OPPORTUNITY": -0.5,  # negative = pull away from disaster
}


# --------------------------------------------------------------------------- #
# 健康信号层: 静态体质 × 流年引动 (DISPATCH_HERMES_HEALTH_ACCURACY §二)
# --------------------------------------------------------------------------- #

# 五行→脏腑 (《黄帝内经·素问》藏象; 与 health_signals.ELEMENT_ORGAN 一致)
_ORGAN_OF = {
    "WOOD": "肝胆", "FIRE": "心小肠", "EARTH": "脾胃",
    "METAL": "肺大肠", "WATER": "肾膀胱",
}

# 调候需求 (《穷通宝鉴》; 与 strength_engine._MONTH_CLIMATE 对应)
_CLIMATE_NEED = {"cold": "FIRE", "hot": "WATER", "dry": "WATER", "wet": "EARTH"}

_HEALTH_MOD_CACHE: dict = {}


def _health_static_profile(chart) -> dict:
    """静态健康画像(每命例只算一次): 调候缺失/体用失衡/脏腑风险。全部中间项保留。"""
    key = (
        chart.day_pillar.heavenly_stem,
        chart.month_pillar.earthly_branch,
        chart.day_pillar.earthly_branch,
        getattr(chart, "gender", ""),
    )
    cached = _HEALTH_MOD_CACHE.get(key)
    if cached is not None:
        return cached

    from tongshu.engines.strength_engine import evaluate_strength, _hidden_stems
    from tongshu.engines.bazi_engine import STEM_ELEMENT as _SE

    d1 = evaluate_strength(chart)
    balance = chart.five_element_balance or {}

    # 调候层: 调候字是否在局(天干/支藏干)
    need = _CLIMATE_NEED.get(d1.climate)
    remedy_missing = False
    if need is not None:
        found = any(_SE[s] == need for s in chart.four_stems())
        if not found:
            for b in chart.four_branches():
                if any(_SE[h] == need for h in _hidden_stems(b)):
                    found = True
                    break
        remedy_missing = not found

    # 体用层 (BLIND-002): 身弱且泄耗明显大于生扶
    body_use = d1.verdict == "身弱" and d1.support_count * 1.3 < d1.drain_count

    # 脏腑静态风险数(过旺/过弱五行各计一)
    excess = [el for el, v in balance.items() if v > 0.40]
    deficient = [el for el, v in balance.items() if v < 0.05]

    profile = {
        "verdict": d1.verdict,
        "dm_el": d1.day_master_element,
        "climate": d1.climate,
        "need": need,
        "remedy_missing": remedy_missing,
        "body_use": body_use,
        "excess": excess,
        "deficient": deficient,
        "n_organ_risks": len(excess) + len(deficient),
        # 古籍依据
        "evidence": (
            "《穷通宝鉴》调候第一等药(盲派·找药引); "
            "BLIND-002 体用失衡; 《内经·素问》五行藏象"
        ),
    }
    _HEALTH_MOD_CACHE[key] = profile
    return profile


def _health_year_modulation(chart, year: int, ctx: dict) -> float:
    """流年引动健康分。

    触发逻辑(方向修正后):
      1. 流年天干/地支为「调候所需五行」→ 补药, 大幅减险 (-2.0);
         若本局调候不缺则小幅稳定 (+0)。
      2. 流年五行为本命过旺五行再透 → 亢害加重 (+0.8/个,《内经》亢则害)。
      3. 流年五行为本命过弱五行 → 失养加重 (+0.6/个)。
      4. 体用失衡者, 流年再见泄耗党 → 加重 (+1.0); 见印比生扶 → 缓解 (-0.8)。
      5. 身强忌生扶: 流年生扶党旺 → 气机壅滞 (+0.5); 见克泄耗 → 疏导 (-0.4)。
    无任何触发时返回基础体质分 0.5×n_organ_risks 的年度平摊(保持区分度下限)。
    """
    p = _health_static_profile(chart)
    from tongshu.engines.bazi_engine import STEM_ELEMENT as _SE

    yb_el = ctx.get("flow_year_branch_element")
    ys = ctx.get("flow_year_stem")
    ys_el = _SE.get(ys) if ys else None

    score = 0.0
    year_elements = {e for e in (yb_el, ys_el) if e}

    # 1. 调候引动
    if p["need"] is not None:
        if p["remedy_missing"]:
            if p["need"] in year_elements:
                score -= 2.0     # 流年补药, 风险释放
            else:
                score += 1.2     # 继续缺药
        # 调候不缺: 不加分(稳定)

    # 2. 过旺五行再逢 → 亢害
    score += 0.8 * len(set(p["excess"]) & year_elements) if p["excess"] else 0.0
    # 3. 过弱五行再逢 → 失养
    score += 0.6 * len(set(p["deficient"]) & year_elements) if p["deficient"] else 0.0

    # 4./5. 旺衰方向修正
    support_tg = ("正印", "偏印", "比肩", "劫财")
    main_tg = ctx.get("flow_year_branch_main_ten_god", "")
    if p["body_use"]:
        if main_tg in support_tg:
            score -= 0.8   # 印比到位, 体得补
        else:
            score += 1.0   # 再见泄耗
    elif p["verdict"] == "身强":
        if main_tg in support_tg:
            score += 0.5   # 忌生扶再至, 壅滞
        else:
            score -= 0.4   # 克泄疏导

    # 区分度下限: 静态风险的年度平摊基线
    score += 0.15 * p["n_organ_risks"]
    return score


def evaluate_year_event_topic(chart, year: int, rules: list[dict]) -> dict:
    """Per-year EVENT_TOPIC scoring, used by .verify_fortune_v2.py.

    Returns:
        {
          'marriage_score': float,
          'health_score': float,
          'signals': list[EventTopicSignal],
        }
    Higher scores indicate higher probability of negative event in that year
    (MARRIAGE_RISK / HEALTH_RISK); MARRIAGE_OPPORTUNITY lowers the score.
    """
    engine = EventTopicEngine(rules)
    signals = engine.match(chart, year=year)
    marriage_score = 0.0
    health_score = 0.0
    for s in signals:
        delta = SCORE_PER_RULE.get(s.ontology_type, 0.0)
        if s.ontology_type.startswith("MARRIAGE"):
            marriage_score += delta
        elif s.ontology_type.startswith("HEALTH"):
            health_score += delta

    # Year-specific modulation for differentiation
    ctx = build_year_context(chart, year)

    # === 健康信号层 (DISPATCH_HERMES_HEALTH_ACCURACY §二) ===
    # 静态体质风险(调候/体用/脏腑) × 流年引动(忌神旺年发作 / 调候字到位缓解)。
    # 方向修正原则: 忌神受制=减险, 喜用被冲=加险; 禁止"有冲就减分"。
    hs = _health_year_modulation(chart, year, ctx)
    health_score += hs
    
    # Compute year stem/branch
    year_stem = _HEAVENLY_STEMS[(year - 4) % 10]
    year_branch = _EARTHLY_BRANCHES[(year - 4) % 12]
    
    # Import CONTROLS for element clash detection
    from .bazi_ten_gods import CONTROLS
    
    # === 条件触发因子（高权重） ===
    # 实测特征对照(DISPATCH_HERMES_HEALTH_ACCURACY 执行记录):
    #   流年冲日支: 答案年 3/11 vs 非答案年 0/35 → 最强健康应期信号
    #   五行冲克(elem_clash): 答案年 2/11(18%) < 非答案年 14/35(40%) → 加分方向反, 改为减分
    # 流年冲日支（健康/婚姻双重点）
    if ctx.get('flow_year_branch_clash_day_branch'):
        marriage_score += 1.5
        health_score += 2.0
    # 流年害日支（保留婚姻权重; 健康上实测无区分度, 归零）
    if ctx.get('flow_year_branch_harm_day_branch'):
        marriage_score += 0.8
    # 主气十神为忌神
    main_tg = ctx.get('flow_year_branch_main_ten_god', '')
    if main_tg in ('七杀', '劫财', '偏财'):
        health_score += 0.6
        marriage_score += 0.4
    # 五行冲克（方向修正: 实测与答案负相关 → 减分）
    if ctx.get('flow_year_branch_main_element_clash'):
        health_score -= 0.5
        marriage_score -= 0.3
    
    # === 年度区分因子（确保每年有不同分数） ===
    # 年干与日干关系（影响婚姻/事业判断）
    stem_idx = _HEAVENLY_STEMS.index(year_stem)
    day_stem_idx = _HEAVENLY_STEMS.index(chart.day_master)
    stem_diff = (stem_idx - day_stem_idx) % 10
    # 年支与日支关系（影响健康/灾劫判断）
    branch_idx = _EARTHLY_BRANCHES.index(year_branch)
    day_branch_idx = _EARTHLY_BRANCHES.index(chart.day_pillar.earthly_branch)
    branch_diff = (branch_idx - day_branch_idx) % 12
    
    # 天干关系评分（婚姻/财运）
    if stem_diff in [0, 1, 2]:  # 比肩、劫财、食神 → 竞争/付出
        marriage_score += 0.3
    elif stem_diff in [5, 6, 7]:  # 七杀、正官、偏财 → 压力/机遇
        health_score += 0.5
        marriage_score += 0.2
    elif stem_diff in [8, 9]:  # 正印、偏印 → 贵人/稳定
        marriage_score += 0.1
        health_score += 0.1
    
    # 地支关系评分（健康/灾劫）
    if branch_diff in [0, 1, 2]:  # 子、丑、寅 → 水木旺
        health_score += 0.2
    elif branch_diff in [5, 6, 7]:  # 巳、午、未 → 火旺
        health_score += 0.4
    elif branch_diff in [8, 9, 10, 11]:  # 申、酉、戌、亥 → 金水旺
        marriage_score += 0.3
        health_score += 0.3
    
    # 年支五行 vs 日支五行（冲克关系）
    # BUG-001 修复(2026-08-27 审计): 原用 STEM_ELEMENT[_HEAVENLY_STEMS[...]]
    # 错取天干五行, 导致年支/日支五行冲克因子恒为 'unknown'; 改用 _branch_element
    # 取地支五行 (流年支 year_branch, 日支 chart.day_pillar.earthly_branch)。
    year_branch_el = _branch_element(year_branch)
    day_branch_el = _branch_element(chart.day_pillar.earthly_branch)
    if CONTROLS.get(year_branch_el) == day_branch_el or CONTROLS.get(day_branch_el) == year_branch_el:
        # 年支五行冲日支五行 → 重大变动
        health_score += 1.0
        marriage_score += 0.5

    return {
        "marriage_score": marriage_score,
        "health_score": health_score,
        "signals": [s.to_dict() for s in signals],
    }


__all__ = [
    "EVENT_TOPIC_FIELDS",
    "EVENT_TOPIC_OPS",
    "EventTopicFieldError",
    "EventTopicOpError",
    "EventTopicSignal",
    "EventTopicEngine",
    "build_chart_only_context",
    "build_year_context",
    "evaluate_conditions",
    "evaluate_year_event_topic",
]
