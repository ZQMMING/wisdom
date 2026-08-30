"""P3 Environmental Fit Producer 测试 (DISPATCH_HERMES_ASSERTION_CONTRACT.md §8 / Sprint C).

覆盖:
- 5 主方位 (N/E/S/W/C) × 身强/身弱 命例 (>= 5 测试要求)
- 八卦扩展位 (NE/SE/SW/NW) 映射
- 输入校验缺/错 → INSUFFICIENT_EVIDENCE (Rule 04)
- 输出 dict 结构 (subject/assertion_type/state/direction/mechanism/confidence + audit)
- 中间项可审计 (strength_verdict/favorable/sector_element/relation)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from tongshu.assertion.environmental_fit import (
    GENERATES,
    OVERCOMES,
    SECTOR_CHINESE,
    SECTOR_ELEMENT,
    produce_environmental_fit,
)
from tongshu.engines.bazi_engine import BaziEngine, STEM_ELEMENT


@pytest.fixture(scope="module")
def engine() -> BaziEngine:
    return BaziEngine()


# ---------- 工具: 已知命例(复用现有 strength_engine 测试用例) ----------

def _strong_metal(engine):
    """CASE1: 庚金 身强 (1990-05-15 22:00 male) — test_strength_engine case 1."""
    return engine.compute((1990, 5, 15, 22), gender="male")


def _weak_fire(engine):
    """CASE2: 丙火 身弱 (1985-12-03 08:00 female) — test_strength_engine case 2."""
    return engine.compute((1985, 12, 3, 8), gender="female")


def _strong_wood(engine):
    """甲木 身强 (1986-03-21 06:00 male)."""
    return engine.compute((1986, 3, 21, 6), gender="male")


def _weak_wood(engine):
    """甲木 从弱(假) (1992-10-25 12:00 male). 四柱壬申庚戌甲戌庚午, 无根+泄耗克占绝对主导+阳干印透=假从弱."""
    return engine.compute((1992, 10, 25, 12), gender="male")


# ---------- 五行关系基础规则 ----------

def test_sector_element_mapping_complete():
    """八方 + 中 → 五行: 八方位 + 中央全覆盖."""
    assert set(SECTOR_ELEMENT) == {"N", "NE", "E", "SE", "S", "SW", "W", "NW", "C"}
    # 五方基础 (《淮南子·天文训》)
    assert SECTOR_ELEMENT["N"] == "WATER"
    assert SECTOR_ELEMENT["E"] == "WOOD"
    assert SECTOR_ELEMENT["S"] == "FIRE"
    assert SECTOR_ELEMENT["W"] == "METAL"
    assert SECTOR_ELEMENT["C"] == "EARTH"


def test_five_element_cycle_invariant():
    """五行相生表 / 相克表 闭合 — 验证与 std 一致."""
    # 闭环相生: 任意元素经 5 步回到自己
    for start in GENERATES:
        cur = start
        for _ in range(5):
            cur = GENERATES[cur]
        assert cur == start, f"相生表不闭合: {start}"
    # 闭环相克: 任意元素经 5 步回到自己
    for start in OVERCOMES:
        cur = start
        for _ in range(5):
            cur = OVERCOMES[cur]
        assert cur == start, f"相克表不闭合: {start}"


# ---------- 命例 × 方位 (5 主方位 + 身强/身弱) ----------

def test_strong_wood_east_neutral(engine):
    """DEPRECATED stub: evaluate_strength 已退回 UNRESOLVED, 中性方位 → neutral."""
    chart = _strong_wood(engine)
    out = produce_environmental_fit(chart, {"sector": "E", "label": "上海"})
    assert out["subject"] == "environment"
    assert out["assertion_type"] == "ENVIRONMENT_FIT"
    assert out["direction"] == "neutral"
    assert out["audit"]["relation"] == "同"
    assert out["audit"]["sector_element"] == "WOOD"
    # stub 返回 UNRESOLVED, 无喜用方向
    assert out["audit"]["strength_verdict"] == "UNRESOLVED"
    assert out["confidence"] == "WEAK"


def test_strong_wood_south_positive(engine):
    """DEPRECATED stub: evaluate_strength 已退回 UNRESOLVED, 五行关系仍推导 direction."""
    chart = _strong_wood(engine)
    out = produce_environmental_fit(chart, {"sector": "S", "label": "广州"})
    # 木生火 = 我生 → positive (五行关系不变), 但 confidence WEAK (无喜忌支撑)
    assert out["direction"] == "positive"
    assert out["audit"]["relation"] == "我生"
    assert out["audit"]["sector_element"] == "FIRE"
    assert out["audit"]["strength_verdict"] == "UNRESOLVED"
    assert out["confidence"] == "WEAK"
    assert out["abstain"] is True


def test_weak_wood_north_positive(engine):
    """DEPRECATED stub: evaluate_strength 已退回 UNRESOLVED, 五行关系仍推导 direction."""
    chart = _weak_wood(engine)
    out = produce_environmental_fit(chart, {"sector": "N", "label": "哈尔滨"})
    # 水生木 = 生我 → positive, confidence WEAK (无喜忌支撑)
    assert out["direction"] == "positive"
    assert out["audit"]["relation"] == "生我"
    assert out["audit"]["sector_element"] == "WATER"
    assert out["audit"]["strength_verdict"] == "UNRESOLVED"
    assert out["confidence"] == "WEAK"
    assert out["abstain"] is True


def test_strong_wood_west_negative(engine):
    """DEPRECATED stub: evaluate_strength 已退回 UNRESOLVED, 五行关系仍推导 direction."""
    chart = _strong_wood(engine)
    out = produce_environmental_fit(chart, {"sector": "W", "label": "成都"})
    # 金克木 = 克我 → negative, confidence WEAK
    assert out["direction"] == "negative"
    assert out["audit"]["relation"] == "克我"
    assert out["audit"]["sector_element"] == "METAL"
    assert out["audit"]["strength_verdict"] == "UNRESOLVED"
    assert out["confidence"] == "WEAK"
    assert out["abstain"] is True


def test_weak_wood_center_negative(engine):
    """DEPRECATED stub: evaluate_strength 已退回 UNRESOLVED, 五行关系仍推导 direction."""
    chart = _weak_wood(engine)
    out = produce_environmental_fit(chart, {"sector": "C", "label": "中原"})
    # 木克土 = 我克 → negative, confidence WEAK
    assert out["direction"] == "negative"
    assert out["audit"]["relation"] == "我克"
    assert out["audit"]["sector_element"] == "EARTH"
    assert out["audit"]["strength_verdict"] == "UNRESOLVED"
    assert out["confidence"] == "WEAK"
    assert out["abstain"] is True


# ---------- 八卦扩展位 (NE/SE/SW/NW) ----------

def test_trigram_sectors_consistent(engine):
    """八卦位 (NE/SE/SW/NW) 五行映射: 艮/巽/坤/乾."""
    chart = _strong_wood(engine)
    # NE = 艮 = 土 (我克, negative for strong wood — 喜用神含土 → state 仍激活)
    out_ne = produce_environmental_fit(chart, {"sector": "NE", "label": "山东"})
    assert out_ne["audit"]["sector_element"] == "EARTH"
    assert out_ne["direction"] == "negative"
    assert out_ne["audit"]["relation"] == "我克"

    # SE = 巽 = 木 (比和, neutral)
    out_se = produce_environmental_fit(chart, {"sector": "SE", "label": "厦门"})
    assert out_se["audit"]["sector_element"] == "WOOD"
    assert out_se["direction"] == "neutral"
    assert out_se["audit"]["relation"] == "同"

    # SW = 坤 = 土 (我克, negative)
    out_sw = produce_environmental_fit(chart, {"sector": "SW", "label": "昆明"})
    assert out_sw["audit"]["sector_element"] == "EARTH"
    assert out_sw["direction"] == "negative"

    # NW = 乾 = 金 (克我, negative)
    out_nw = produce_environmental_fit(chart, {"sector": "NW", "label": "乌鲁木齐"})
    assert out_nw["audit"]["sector_element"] == "METAL"
    assert out_nw["direction"] == "negative"
    assert out_nw["audit"]["relation"] == "克我"


# ---------- 输入校验 (Rule 04) ----------

def test_missing_chart_returns_insufficient_evidence():
    """chart 缺失 → INSUFFICIENT_EVIDENCE (Rule 04)."""
    out = produce_environmental_fit(None, {"sector": "E"})
    assert out["abstain"] is True
    assert out["confidence"] == "INSUFFICIENT_EVIDENCE"
    assert out["assertion_type"] == "INSUFFICIENT_EVIDENCE"


def test_missing_location_returns_insufficient_evidence(engine):
    """current_living_location 缺失 → INSUFFICIENT_EVIDENCE."""
    chart = _strong_wood(engine)
    for bad in (None, {}):
        out = produce_environmental_fit(chart, bad)
        assert out["abstain"] is True
        assert out["confidence"] == "INSUFFICIENT_EVIDENCE"


def test_invalid_sector_returns_insufficient_evidence(engine):
    """无效 sector → INSUFFICIENT_EVIDENCE."""
    chart = _strong_wood(engine)
    out = produce_environmental_fit(chart, {"sector": "XY"})
    assert out["confidence"] == "INSUFFICIENT_EVIDENCE"
    assert out["abstain"] is True


# ---------- 输出结构 & 可审计性 ----------

def test_output_dict_has_assertion_fields_and_audit(engine):
    """输出 dict 同时含 Assertion 契约字段 + audit 子字段(中间项可审计)."""
    chart = _strong_wood(engine)
    out = produce_environmental_fit(chart, {"sector": "S", "label": "广州"})
    # 契约字段(§4)
    for f in ("subject", "assertion_type", "state", "direction",
              "mechanism", "time", "confidence", "abstain"):
        assert f in out, f"缺契约字段: {f}"
    assert out["subject"] == "environment"
    assert out["assertion_type"] == "ENVIRONMENT_FIT"
    # audit 字段(中间项可审计)
    assert "audit" in out, "缺 audit 字段 — 中间项不可审计"
    for k in ("day_master", "day_master_element", "strength_verdict",
              "favorable_elements", "unfavorable_elements",
              "sector", "sector_element", "relation"):
        assert k in out["audit"], f"audit 缺: {k}"


def test_mechanism_chain_includes_intermediate_steps(engine):
    """mechanism 字符串包含 旺衰/喜用/方位/关系 全链路 — stub 模式下标注 DEPRECATED."""
    chart = _weak_wood(engine)
    out = produce_environmental_fit(chart, {"sector": "N"})
    m = out["mechanism"]
    assert "旺衰=" in m and "UNRESOLVED" in m
    assert "喜用=" in m
    assert "方位" in m and "=" in m and "WATER" in m
    assert "五行关系=" in m and "生我" in m


def test_strength_verdict_auditable_in_audit(engine):
    """DEPRECATED stub: strength_verdict 在 audit 中显示 UNRESOLVED 标记."""
    chart = _weak_fire(engine)
    out = produce_environmental_fit(chart, {"sector": "S"})
    assert out["audit"]["strength_verdict"] == "UNRESOLVED"
    assert out["audit"]["day_master_element"] == "FIRE"
    assert out["audit"]["verdict_condition"]   # 非空字符串, 含 DEPRECATED 标记


def test_wo_身强_身弱_五行方向对称(engine):
    """DEPRECATED stub: 身强 + 身弱 均返回 UNRESOLVED, 五行关系不变但无喜忌."""
    chart_strong = _strong_wood(engine)
    chart_weak = _weak_wood(engine)
    out_s = produce_environmental_fit(chart_strong, {"sector": "W"})
    out_w = produce_environmental_fit(chart_weak, {"sector": "W"})
    # 关系同源(五行关系不变), 但 stub 模式无喜忌标注
    assert out_s["audit"]["relation"] == out_w["audit"]["relation"]
    assert out_s["audit"]["strength_verdict"] == "UNRESOLVED"
    assert out_w["audit"]["strength_verdict"] == "UNRESOLVED"
    assert out_s["audit"]["favorable_elements"] == []
    assert out_w["audit"]["unfavorable_elements"] == []


def test_abstain_follows_confidence(engine):
    """DEPRECATED stub: abstain 与 confidence 联动 — stub 模式下 WEAK + abstain=True."""
    chart = _weak_wood(engine)
    # 比和 → neutral → WEAK → abstain=True
    out = produce_environmental_fit(chart, {"sector": "E"})
    assert out["direction"] == "neutral"
    assert out["confidence"] == "WEAK"
    assert out["abstain"] is True
    # 即使明确五行关系, stub 无喜忌 → WEAK + abstain=True
    out2 = produce_environmental_fit(chart, {"sector": "N"})
    assert out2["direction"] == "positive"  # 五行关系仍是 生我
    assert out2["confidence"] == "WEAK"
    assert out2["abstain"] is True