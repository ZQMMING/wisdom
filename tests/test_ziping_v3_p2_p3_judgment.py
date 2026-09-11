# -*- coding: utf-8 -*-
"""P2/P3 判断层测试: 月令/得令 + 十二长生 + 有效根 + 党众 + 身强弱六态.

1980-06-22 巳时 男 (庚申 壬午 丙寅 癸巳, 日主丙火, 月支午火):
  - LING: 月支午(火) 对 日主丙(火) → 同我 SAME → 得令 DE_LING
  - GROWTH: 日支寅 → 丙长生 → ROOTING
  - STRENGTH: 得令 + 建禄根(TONG_GAN日支... 日主丙, 日支寅藏丙中气根)
              + 帮身(丙丁甲) + 但克泄耗结构(庚壬癸戊己)并存 → 结构判定
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.reasoning.ziping_v3 import chart_to_context
from src.tongshu.reasoning.ziping_v3.reference import build_derived_facts
from src.tongshu.reasoning.ziping_v3.judgment import (
    judge_ling, judge_growth, derive_effective_root,
    derive_party_structure, judge_strength, run_strength_chain,
)


def _ctx():
    c = BaziEngine().compute((1980, 6, 22, 10), gender="male")
    fact, avail, _ti = chart_to_context(c)
    from src.tongshu.reasoning.ziping_v3.engine import EngineContext
    derived = build_derived_facts(fact, {"commanded_stem": "REN"})
    return EngineContext(fact, avail, {}), derived


def test_ling_de_ling():
    ctx, derived = _ctx()
    ling = judge_ling(ctx, derived)
    # 午(火) 对 丙(火): SAME → 得令
    assert ling.state == "DE_LING", f"应得令, 实为 {ling.state} {ling.to_dict()}"
    assert ling.matched_rule_ids and ling.evidence_refs, "缺 rule/evidence (ARCH-009)"
    print(f"月令: {ling.state} rule={ling.matched_rule_ids} ev={ling.evidence_refs}")


def test_growth_rooting():
    ctx, derived = _ctx()
    g = judge_growth(ctx, derived)
    # 日支寅, 丙火长生 → ROOTING
    assert g.state == "ROOTING", f"日支寅丙长生应 ROOTING, 实为 {g.state}"
    print(f"长生: {g.state} rule={g.matched_rule_ids}")


def test_effective_root_present():
    ctx, derived = _ctx()
    er = derive_effective_root(ctx, derived)
    assert er["ROOT_PRESENT"] is True, "日主丙 有建禄根, 应 ROOT_PRESENT"
    # 建禄根 = 重根
    assert er["ROOT_KIND"] == "HEAVY", f"丙建禄应重根, 实为 {er['ROOT_KIND']}"
    assert er["EFFECTIVE_ROOT"] in ("TRUE", "CONDITIONAL")
    print(f"有效根: kind={er['ROOT_KIND']} available={er['ROOT_IS_AVAILABLE']} "
          f"effective={er['EFFECTIVE_ROOT']} damaged={er['ROOT_IS_DAMAGED']}")


def test_party_structure():
    ctx, derived = _ctx()
    p = derive_party_structure(ctx, derived, de_ling=True)
    sup = set(p["SUPPORT_STRUCTURE"])
    opp = set(p["OPPOSITION_STRUCTURE"])
    # 帮身: 月令(午火同我) + 日支根(寅藏丙) + 比劫(丙丁)
    assert "月令" in sup, f"得令应含月令支持: {sup}"
    assert "比劫" in sup, f"丙丁同类应比劫: {sup}"
    assert "日支根" in sup, f"寅藏丙应日支根: {sup}"
    # 对立: 庚金我克→财耗, 壬癸水克我→官杀, 戊己土我生→食伤
    assert "官杀" in opp, f"壬癸水克火应官杀: {opp}"
    assert "财耗" in opp, f"庚金火克应财耗: {opp}"
    # §53 禁止计数: 结果必须是结构清单(列表), 非 support_count 数字
    assert isinstance(p["SUPPORT_STRUCTURE"], list) and isinstance(p["OPPOSITION_STRUCTURE"], list)
    print(f"党众: 帮身={sorted(sup)} 对立={sorted(opp)}")


def test_strength_chain_full():
    """完整判据链: 月令→长生→根→党众→身强弱 六态裁决."""
    ctx, derived = _ctx()
    result = run_strength_chain(ctx, derived, special_valid=False)
    ling, growth, strength = result["LING"], result["GROWTH"], result["STRENGTH"]
    assert ling.state == "DE_LING"
    assert growth.state == "ROOTING"
    # 身强弱: 得令 + 建禄有效根 + 帮身结构 + 对立结构并存
    #   帮身(月令+比劫+日支根) 与 对立(官杀+财耗) 并存 → 结构未主导 → 中和或得令不旺
    valid_states = {"STRONG", "WEAK", "BALANCED", "WANG_BUT_NOT_STRONG",
                    "SHUAI_BUT_NOT_WEAK", "UNDETERMINED"}
    assert strength.state in valid_states, f"非法身强弱态 {strength.state}"
    # 每域判断必须携带 证据链 (ARCH-008/009) — UNDETERMINED 则携带 reason
    for name, j in (("ling", ling), ("growth", growth), ("strength", strength)):
        if j.state != "UNDETERMINED":
            assert j.matched_rule_ids and j.evidence_refs, f"{name} 缺证据链"
        else:
            assert j.reason, f"{name} UNDETERMINED 缺 reason (§77)"
    print(f"身强弱: {strength.state} rule={strength.matched_rule_ids} "
          f"reason={strength.reason}")


def test_strength_no_count_forbidden():
    """§53 REV-PARTY-006: 禁 support_count 数字阈值 — 断言无 数量比较 泄漏."""
    import re
    src = Path("D:/shuntian/src/tongshu/reasoning/ziping_v3/judgment.py").read_text(encoding="utf-8")
    # 禁止: len(x) 数量 或 阈值数字 驱动 身强弱
    assert not re.search(r"len\((support|opposition)\)\s*[<>]=?\s*\d", src), \
        "身强弱 不得用 集合大小 数字阈值 判定 (§53/§50)"
    print("§53 无计数阈值 ✓ (身强弱 纯结构谓词)")


if __name__ == "__main__":
    test_ling_de_ling()
    test_growth_rooting()
    test_effective_root_present()
    test_party_structure()
    test_strength_chain_full()
    test_strength_no_count_forbidden()
    print("\n辨层 P2/P3 全部通过 ✓")
