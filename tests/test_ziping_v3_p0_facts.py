# -*- coding: utf-8 -*-
"""P0 层测试: BaziChart → FrozenBaziFact 事实适配.

验证 (V3.1 §3 FACT / §51 REV-TYPE / ARCH-003~006):
  1. 四柱/日主/月支 正确搬运 (1980-06-22 巳时 男 → 庚申 壬午 丙寅 癸巳)
  2. 藏干/十神/干支关系/长生 从 BaziChart 只读搬运
  3. NOT_AUTHORIZED 字段 (five_element_balance / spouse_star* / officer_mixed /
     peach_blossom) 不进入 FrozenBaziFact
  4. 适配层零重算: 结果只依赖 BaziChart 既有字段 (ARCH-003~006)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.reasoning.ziping_v3 import build_frozen_fact, chart_to_context
from src.tongshu.reasoning.ziping_v3.types import FrozenBaziFact


def _chart():
    return BaziEngine().compute(
        solar_date=(1980, 6, 22, 10), gender="male"
    )


def test_four_pillars():
    c = _chart()
    fact, available, _ti = chart_to_context(c)
    assert c.year_pillar.to_dict() and c.day_master
    # 1980-06-22 巳时: 庚申 壬午 丙寅 癸巳, 日主丙
    got = [(p[0], p[1]) for p in fact.four_pillars]
    exp = [
        (c.year_pillar.heavenly_stem, c.year_pillar.earthly_branch),
        (c.month_pillar.heavenly_stem, c.month_pillar.earthly_branch),
        (c.day_pillar.heavenly_stem, c.day_pillar.earthly_branch),
        (c.hour_pillar.heavenly_stem, c.hour_pillar.earthly_branch),
    ]
    assert got == exp, f"四柱搬运不符: {got} vs {exp}"
    assert fact.day_master == c.day_master
    assert fact.month_branch == c.month_pillar.earthly_branch
    print(f"四柱: {got}  日主: {fact.day_master}  月支: {fact.month_branch}")


def test_facts_populated():
    c = _chart()
    fact, available, _ti = chart_to_context(c)
    # 基础事实必须齐
    for k in ("four_pillars", "day_master", "month_branch", "hidden_stems",
              "raw_relations", "stem_ten_gods"):
        assert k in available, f"{k} 缺失于 available_facts"
    # 藏干: 月支午 主气丁 (Bazi 侧英文键)
    assert fact.hidden_stems.get("MONTH", {}).get("main") == "DING", \
        f"月支藏干主气应为 DING, 实为 {fact.hidden_stems.get('MONTH')}"
    # 十二长生键归一为 子平大写位置
    assert "MONTH" in fact.twelve_growth, f"twelve_growth 键未归一: {list(fact.twelve_growth)}"
    print(f"available: {sorted(available)}")
    print(f"月支藏干: {fact.hidden_stems.get('MONTH')}")


def test_not_authorized_not_leaked():
    """§0.6 合规: NOT_AUTHORIZED 字段不得进入子平事实."""
    c = _chart()
    fact, _available, _ti = chart_to_context(c)
    leaked = [f for f in vars(fact) if f in (
        "five_element_balance", "five_element_imbalance",
        "spouse_star", "spouse_star_attack", "officer_mixed", "peach_blossom")]
    assert not leaked, f"NOT_AUTHORIZED 字段泄漏进 FrozenBaziFact: {leaked}"
    # 且 dataclass 根本无这些字段
    fields = set(vars(fact).keys())
    assert "five_element_balance" not in fields
    print("NOT_AUTHORIZED 字段未泄漏 ✓ (五要素平衡/配偶星/官混/桃花 均不进入子平)")


def test_zero_recompute():
    """ARCH-003~006: 适配层零重算 — 同 chart 同 fact, 幂等确定性."""
    c = _chart()
    f1, a1, _ = chart_to_context(c)
    f2, a2, _ = chart_to_context(c)
    assert f1 == f2, "事实适配非确定性 (同输入不同输出)"
    assert a1 == a2
    print("零重算幂等: 同 BaziChart → 同 FrozenBaziFact ✓")


if __name__ == "__main__":
    test_four_pillars()
    test_facts_populated()
    test_not_authorized_not_leaked()
    test_zero_recompute()
    print("\nP0 事实适配层全部通过 ✓")
