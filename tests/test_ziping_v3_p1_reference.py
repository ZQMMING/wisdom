# -*- coding: utf-8 -*-
"""P1 派生层测试: 根气/党众/透干 (Deterministic First, 零外部表).

用 1980-06-22 巳时 男 (庚申 壬午 丙寅 癸巳, 日主丙) 锁定确定性派生行为.
全部断言基于 已核对的 Bazi 冻结事实, 验证 子平派生层 无重算/无臆测.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.reasoning.ziping_v3 import chart_to_context
from src.tongshu.reasoning.ziping_v3.reference import (
    build_derived_facts,
    derive_root_strength,
    derive_party,
    derive_tong_stems,
)


def _fact():
    c = BaziEngine().compute((1980, 6, 22, 10), gender="male")
    fact, _avail, _ti = chart_to_context(c)
    return fact


def test_root_strength():
    df = build_derived_facts(_fact())
    r = df.states["root_strength"]
    assert r["day_master"] == "BING"
    assert r["has_root"] is True
    # 日柱天干==日主 → TONG_GAN 根
    assert any(x["type"] == "TONG_GAN" and x["position"] == "DAY" for x in r["roots"])
    # 藏干根: 午丁本气 / 寅丙中气 / 巳丙本气
    grades = {(x["position"], x["stem"], x["grade"]) for x in r["roots"]
              if x["type"] == "CANG_GAN"}
    assert ("MONTH", "DING", "本气") in grades, grades
    assert ("DAY", "BING", "中气") in grades, grades
    assert ("HOUR", "BING", "本气") in grades, grades
    # 长生根: 午帝旺/寅长生/巳临官 (申=病 被排除)
    growth = {(x["position"], x["growth"]) for x in r["growth_roots"]}
    assert growth == {("MONTH", "帝旺"), ("DAY", "长生"), ("HOUR", "临官")}, growth
    assert r["root_grade"] == "TONG_GAN"  # 建禄根最强
    print(f"根气: grade={r['root_grade']} roots={len(r['roots'])} growth={len(r['growth_roots'])}")


def test_party():
    df = build_derived_facts(_fact())
    p = df.states["party"]
    # 日主丙(火): 帮身=同我(丙丁)+生我(甲乙木)
    # 克泄耗=我克(庚辛金)+我生(戊己土)+克我(壬癸水)
    aligned = {(x["position"], x["stem"], x["layer"]) for x in p["aligned"]}
    opposed = {(x["position"], x["stem"], x["layer"]) for x in p["opposed"]}
    # 帮身: 日干丙(透) + 午藏丁 + 寅藏甲 + 寅藏丙 + 巳藏丙
    assert ("DAY", "BING", "STEM") in aligned, aligned
    assert ("MONTH", "DING", "HIDDEN") in aligned, aligned
    assert ("DAY", "JIA", "HIDDEN") in aligned, aligned
    # 克泄耗: 年干庚 + 月干壬 + 时干癸 (透干层)
    assert ("YEAR", "GENG", "STEM") in opposed, opposed
    assert ("MONTH", "REN", "STEM") in opposed, opposed
    assert ("HOUR", "GUI", "STEM") in opposed, opposed
    assert p["party_state"] == "BOTH"
    print(f"党众: state={p['party_state']} aligned={p['aligned_roots']} opposed={p['opposed_roots']}")


def test_party_classify_correctness():
    """逐干验证 五行生克 分类 (确定性, 非计数)."""
    from src.tongshu.reasoning.ziping_v3.reference import _classify_party
    FIRE = "FIRE"
    assert _classify_party(FIRE, "BING") == "ALIGNED"   # 同我
    assert _classify_party(FIRE, "DING") == "ALIGNED"   # 同我
    assert _classify_party(FIRE, "JIA") == "ALIGNED"    # 生我(木生火)
    assert _classify_party(FIRE, "GUI") == "OPPOSED"    # 克我(水克火)
    assert _classify_party(FIRE, "REN") == "OPPOSED"    # 克我
    assert _classify_party(FIRE, "WU") == "OPPOSED"    # 我生(火生土, 泄)
    assert _classify_party(FIRE, "GENG") == "OPPOSED"  # 我克(火克金, 耗)
    assert _classify_party("", "BING") is None          # 日主五行缺失 → 不参与
    print("党众分类 逐干验证 ✓")


def test_tong_stems_fail_closed():
    fact = _fact()
    # 缺司令干 → fail-closed, 不臆测
    r = derive_tong_stems(fact, None)
    assert r["state"] == "UNDETERMINED" and r["reason"] == "FACT_MISSING:month_command"
    # 有司令干壬 → 壬在四柱干中 → 透出
    r2 = derive_tong_stems(fact, "REN")
    assert r2["is_tong"] is True and r2["state"] == "DETERMINED"
    # 司令干为某不透之干 → False
    r3 = derive_tong_stems(fact, "XIN")
    assert r3["is_tong"] is False
    print(f"透干 fail-closed ✓ (REN透出={r2['is_tong']}, XIN={r3['is_tong']})")


if __name__ == "__main__":
    test_root_strength()
    test_party()
    test_party_classify_correctness()
    test_tong_stems_fail_closed()
    print("\nP1 派生层全部通过 ✓")
