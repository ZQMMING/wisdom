"""P3 Environmental Fit Producer (DISPATCH_HERMES_ASSERTION_CONTRACT.md §8 / §10 Sprint C).

骨架实现 — 用户可操作后天变量(生活地方位)与先天结构的适配度判定。

== 设计原则 ==
- 排盘(确定性层)负责"算对"; 本 Producer 只读 BaziChart + D1StrengthResult, 不重算。
- 五行关系(相生/相克/比和)是单一确定性信号; 喜用神派生基于旺衰结论, 全部中间项可审计。
- 输出为 Assertion 结构 + audit dict(包含 旺衰结论/喜用五行/方位适配度)。
- 单体系信号 (契约 §9) → 最高 LIKELY, 不可 SUPPORTED。

== 经典依据(每个断言机制链内附古籍出处) ==
- 五行方位: 《淮南子·天文训》"木=东/火=南/土=中/金=西/水=北"
- 八方五行: 后天八卦(坎北水 / 艮东北土 / 震东木 / 巽东南木 / 离南火 / 坤西南土 / 兑西金 / 乾西北金)
- 喜忌取用: 《滴天髓·通神论·衰旺》"能知衰旺, 真机已达"; 《子平真诠》"论用神: 月令乃提纲"
- 五行相生相克: 《五行大义》(生: 木→火→土→金→水→木; 克: 木→土→水→火→金→木)

== 输入契约 ==
  chart: BaziChart
  current_living_location: dict { 'sector': 'N'|'NE'|'E'|'SE'|'S'|'SW'|'W'|'NW'|'C', 'label'?: str }

== 输出 ==
  dict — 含 Assertion 字段 (subject/assertion_type/state/direction/mechanism/confidence/abstain)
       + audit 子字段 (strength_verdict/day_master/favorable/unfavorable/sector/sector_element/relation)
  输入不合法 → INSUFFICIENT_EVIDENCE (Rule 04 优先)
"""
from __future__ import annotations

from typing import Any

from tongshu.assertion.contract import (
    Assertion,
    AssertionType,
    Confidence,
    Direction,
    StateKind,
    insufficient_evidence,
)
from tongshu.engines.bazi_engine import STEM_ELEMENT, BaziChart
from tongshu.engines.strength_engine import evaluate_strength


# === 五行相生表(我生) ===
# key = 我, value = 我所生者
GENERATES: dict[str, str] = {
    "WOOD": "FIRE",     # 木生火
    "FIRE": "EARTH",    # 火生土
    "EARTH": "METAL",   # 土生金
    "METAL": "WATER",   # 金生水
    "WATER": "WOOD",    # 水生木
}

# === 五行相克表(我克) ===
# key = 我, value = 我所克者
OVERCOMES: dict[str, str] = {
    "WOOD": "EARTH",    # 木克土
    "EARTH": "WATER",   # 土克水
    "WATER": "FIRE",    # 水克火
    "FIRE": "METAL",    # 火克金
    "METAL": "WOOD",    # 金克木
}

# === 同党(生扶) / 异党(克泄耗) 集合 ===
# 与 strength_engine._SUPPORT_ELEMENTS / _DRAIN_ELEMENTS 保持一致(架构原则: 不重算)
SUPPORT_ELEMENTS: dict[str, set[str]] = {
    "WOOD": {"WOOD", "WATER"},      # 比劫 + 印
    "FIRE": {"FIRE", "WOOD"},
    "EARTH": {"EARTH", "FIRE"},
    "METAL": {"METAL", "EARTH"},
    "WATER": {"WATER", "METAL"},
}
DRAIN_ELEMENTS: dict[str, set[str]] = {
    "WOOD": {"FIRE", "EARTH", "METAL"},   # 食伤 + 财 + 官杀
    "FIRE": {"EARTH", "METAL", "WATER"},
    "EARTH": {"METAL", "WATER", "WOOD"},
    "METAL": {"WATER", "WOOD", "FIRE"},
    "WATER": {"WOOD", "FIRE", "EARTH"},
}

# === 八方 + 中央 → 五行 ===
# 五方(基础): 木东/火南/土中/金西/水北 (《淮南子·天文训》)
# 八方(扩展): 后天八卦标准映射
SECTOR_ELEMENT: dict[str, str] = {
    "N":  "WATER",   # 北 / 坎
    "NE": "EARTH",   # 东北 / 艮
    "E":  "WOOD",    # 东 / 震
    "SE": "WOOD",   # 东南 / 巽(取木, 风生木)
    "S":  "FIRE",    # 南 / 离
    "SW": "EARTH",   # 西南 / 坤
    "W":  "METAL",   # 西 / 兑
    "NW": "METAL",   # 西北 / 乾
    "C":  "EARTH",   # 中央
}

SECTOR_CHINESE: dict[str, str] = {
    "N":  "北",
    "NE": "东北",
    "E":  "东",
    "SE": "东南",
    "S":  "南",
    "SW": "西南",
    "W":  "西",
    "NW": "西北",
    "C":  "中",
}


def _derive_favorable(dm_el: str, verdict: str) -> tuple[set[str], set[str]]:
    """根据旺衰结论派生喜用神 / 忌神集合.

    V2.5 fix: 原逻辑从强=身强喜克泄耗、从弱=身弱喜生扶, 与 judgment_engine._XIJI_MAP 矛盾.
    从格喜忌需反转: 从强喜印比+食伤泄秀(忌官杀破局), 从弱喜财官食伤(忌印比破局).
    假从格(从强(假)/从弱(假))按普通身强/身弱处理.

    五行→十神映射: 生我=SEAL印, 同我=COMPANION比劫, 我生=EATING食伤, 我克=WEALTH财, 克我=OFFICIAL官杀.

    Returns:
        (favorable_elements, unfavorable_elements) — 元素集合
        若 verdict 未知则两集合均为空集.
    """
    # 假从格按普通身强/身弱处理
    if "(假)" in verdict:
        verdict = "身强" if "从强" in verdict else "身弱"

    seal_el = _reverse_generate(dm_el)        # 生我者=印
    companion_el = dm_el                        # 同我者=比劫
    eating_el = GENERATES[dm_el]               # 我生者=食伤
    wealth_el = OVERCOMES[dm_el]               # 我克者=财
    official_el = _reverse_overcome(dm_el)     # 克我者=官杀

    if verdict == "身强":
        # 身强: 喜克泄耗(官杀+食伤+财), 忌生扶(印+比劫)
        return {official_el, eating_el, wealth_el}, {seal_el, companion_el}
    if verdict == "身弱":
        # 身弱: 喜生扶(印+比劫), 忌克泄耗(官杀+食伤+财)
        return {seal_el, companion_el}, {official_el, eating_el, wealth_el}
    if verdict == "从强":
        # 从强: 喜印比+食伤泄秀, 忌官杀克身破局
        return {seal_el, companion_el, eating_el}, {official_el}
    if verdict == "从弱":
        # 从弱: 喜财官食伤, 忌印比生身破局
        return {wealth_el, official_el, eating_el}, {seal_el, companion_el}
    return set(), set()


def _reverse_generate(el: str) -> str:
    """反向查找五行相生: 谁生 el."""
    for k, v in GENERATES.items():
        if v == el:
            return k
    return el


def _reverse_overcome(el: str) -> str:
    """反向查找五行相克: 谁克 el."""
    for k, v in OVERCOMES.items():
        if v == el:
            return k
    return el


def _element_relation(dm_el: str, sector_el: str) -> str:
    """判定 日主五行 与 方位五行 的关系.

    Returns:
        "同"      比和
        "我生"    日主生方位(泄)
        "生我"    方位生日主(印/生扶)
        "我克"    日主克方位(耗)
        "克我"    方位克日主(克)
    """
    if dm_el == sector_el:
        return "同"
    if GENERATES[dm_el] == sector_el:
        return "我生"
    if GENERATES[sector_el] == dm_el:
        return "生我"
    if OVERCOMES[dm_el] == sector_el:
        return "我克"
    if OVERCOMES[sector_el] == dm_el:
        return "克我"
    return "未知"


def _relation_to_direction(dm_el: str, sector_el: str) -> Direction:
    """五行关系 → direction(契约: 相生=positive, 相克=negative, 比和=neutral).

    注: 喜忌信息不参与此映射, 仅作 audit 保留;
        旺衰结论影响 state 与 confidence, 不直接覆盖五行关系规则。
    """
    rel = _element_relation(dm_el, sector_el)
    if rel in ("我生", "生我"):
        return Direction.POSITIVE
    if rel in ("我克", "克我"):
        return Direction.NEGATIVE
    # 同 / 未知: neutral
    return Direction.NEUTRAL


def _state_for_fit(
    verdict: str,
    sector_el: str,
    favorable: set[str],
    unfavorable: set[str],
) -> StateKind:
    """基于 喜用神 / 忌神 匹配 → 结构状态.

    - 方位五行 ∈ 喜用神 → ACTIVATION (喜用结构被激活)
    - 方位五行 ∈ 忌神   → SUPPRESSION (忌神结构压制)
    - 其它 / 未知      → STABLE
    """
    if favorable and sector_el in favorable:
        return StateKind.ACTIVATION
    if unfavorable and sector_el in unfavorable:
        return StateKind.SUPPRESSION
    return StateKind.STABLE


def _confidence_for_fit(verdict: str, direction: Direction) -> Confidence:
    """置信裁定(契约 §9: 单体系信号最高 LIKELY).

    V2.5 fix: 假从格(从强(假)/从弱(假))按普通身强/身弱处理, 原白名单漏掉假从格导致恒为WEAK.
    - 旺衰结论明确 + direction ≠ neutral → LIKELY
    - direction = neutral(比和)        → WEAK(中性信息本身置信有限)
    - 旺衰结论未知                   → WEAK
    """
    # 假从格按普通身强/身弱处理
    verdict_for_conf = verdict
    if "(假)" in verdict:
        verdict_for_conf = "身强" if "从强" in verdict else "身弱"
    if verdict_for_conf not in ("身强", "身弱", "从强", "从弱"):
        return Confidence.WEAK
    if direction == Direction.NEUTRAL:
        return Confidence.WEAK
    return Confidence.LIKELY


def _build_mechanism(
    dm: str,
    dm_el: str,
    verdict: str,
    verdict_condition: str,
    favorable: set[str],
    unfavorable: set[str],
    sector: str,
    sector_label: str,
    sector_el: str,
    relation: str,
    direction: Direction,
) -> str:
    """构造证据机制链字符串(可审计文本).

    结构: [日主] | [旺衰判定] | [喜用神/忌神] | [方位] | [五行关系] | [方向]
    """
    fav_str = ",".join(sorted(favorable)) if favorable else "无"
    unfav_str = ",".join(sorted(unfavorable)) if unfavorable else "无"
    return (
        f"日主={dm}({dm_el}); 旺衰={verdict}({verdict_condition}); "
        f"喜用=[{fav_str}], 忌=[{unfav_str}]; "
        f"方位{sector}({sector_label})={sector_el}; "
        f"五行关系={relation} → {direction.value}"
    )


def produce_environmental_fit(
    chart: BaziChart | None,
    current_living_location: dict | None,
) -> dict[str, Any]:
    """P3 Environmental Fit Producer — 骨架.

    输入:
        chart: BaziChart — P0 排盘层产出(确定性)
        current_living_location: dict — 必含 'sector' (N/NE/E/SE/S/SW/W/NW/C); 可选 'label'

    输出:
        dict — Assertion 字段 + audit 字段
        缺/错输入 → INSUFFICIENT_EVIDENCE (Rule 04 优先于硬断)
    """
    # ---- 输入校验 ----
    if chart is None or not isinstance(chart, BaziChart):
        return _to_dict(insufficient_evidence("environment", "chart is not BaziChart"))
    if not current_living_location:
        return _to_dict(insufficient_evidence(
            "environment", "current_living_location required (Rule 01)"
        ))
    sector = current_living_location.get("sector")
    if sector not in SECTOR_ELEMENT:
        return _to_dict(insufficient_evidence(
            "environment",
            f"sector must be one of {sorted(SECTOR_ELEMENT)}; got {sector!r}",
        ))
    label = current_living_location.get("label") or SECTOR_CHINESE[sector]

    # ---- 1. D1 旺衰判定(复用 strength_engine, 不重算) ----
    strength = evaluate_strength(chart)
    dm = chart.day_master
    dm_el = STEM_ELEMENT[dm]
    verdict = strength.verdict

    # ---- 2. 喜用神派生 ----
    favorable, unfavorable = _derive_favorable(dm_el, verdict)

    # ---- 3. 方位五行 ----
    sector_el = SECTOR_ELEMENT[sector]

    # ---- 4. 五行关系 → direction ----
    relation = _element_relation(dm_el, sector_el)
    direction = _relation_to_direction(dm_el, sector_el)

    # ---- 5. state ----
    state = _state_for_fit(verdict, sector_el, favorable, unfavorable)

    # ---- 6. confidence ----
    confidence = _confidence_for_fit(verdict, direction)

    # ---- 7. mechanism 机制链 ----
    mechanism = _build_mechanism(
        dm=dm,
        dm_el=dm_el,
        verdict=verdict,
        verdict_condition=strength.verdict_condition,
        favorable=favorable,
        unfavorable=unfavorable,
        sector=sector,
        sector_label=label,
        sector_el=sector_el,
        relation=relation,
        direction=direction,
    )

    assertion = Assertion(
        subject="environment",
        assertion_type=AssertionType.ENVIRONMENT_FIT,
        state=state,
        direction=direction,
        mechanism=mechanism,
        time="常年",
        confidence=confidence,
        # abstain 由 _confidence_for_fit 决定: LIKELY → 解禁(给出方向);
        # WEAK/INSUFFICIENT → 仍 abort(契约 Rule 04)
        abstain=(confidence in (Confidence.WEAK, Confidence.INSUFFICIENT_EVIDENCE)),
    )

    return _to_dict(assertion, audit={
        "day_master": dm,
        "day_master_element": dm_el,
        "strength_verdict": verdict,
        "verdict_condition": strength.verdict_condition,
        "favorable_elements": sorted(favorable),
        "unfavorable_elements": sorted(unfavorable),
        "sector": sector,
        "sector_label": label,
        "sector_element": sector_el,
        "relation": relation,
        "state_basis": _state_basis(verdict, sector_el, favorable, unfavorable),
    })


def _state_basis(
    verdict: str,
    sector_el: str,
    favorable: set[str],
    unfavorable: set[str],
) -> str:
    """state 推导说明(便于审计 state 来源)."""
    if favorable and sector_el in favorable:
        return f"sector_element({sector_el}) ∈ 喜用神 → ACTIVATION"
    if unfavorable and sector_el in unfavorable:
        return f"sector_element({sector_el}) ∈ 忌神 → SUPPRESSION"
    return f"sector_element({sector_el}) ∉ 喜用神/忌神 → STABLE"


def _to_dict(assertion: Assertion, audit: dict | None = None) -> dict[str, Any]:
    """将 Assertion 转 dict 并附加 audit(契约字段 + 可审计中间项).

    NOTE: 这是 Producer 内部边界 — 上游接收 dict 即可同时获取契约字段与审计字段。
          audit 字段不污染 Assertion 结构, 也不进入 contract.py 序列化。
    """
    d = assertion.to_dict()
    if audit is not None:
        d["audit"] = audit
    return d


__all__ = [
    "produce_environmental_fit",
    "SECTOR_ELEMENT",
    "SECTOR_CHINESE",
    "GENERATES",
    "OVERCOMES",
    "_derive_favorable",
    "_element_relation",
    "_relation_to_direction",
]