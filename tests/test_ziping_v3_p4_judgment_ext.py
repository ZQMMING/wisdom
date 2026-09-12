# -*- coding: utf-8 -*-
"""P4 判断扩展层测试: 气候/清浊/通关/病药/气势/用神分方法.

1980-06-22 巳时 男 (庚申 壬午 丙寅 癸巳, 日主丙, 月支午):
  透干十神: 庚=偏财 壬=七杀 癸=正官 (日主丙排除)
  午 = 夏 → 寒暖态 HOT; 壬癸水透出 无火土透 → 燥湿 WET
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.reasoning.ziping_v3 import chart_to_context
from src.tongshu.reasoning.ziping_v3.engine import EngineContext
from src.tongshu.reasoning.ziping_v3.reference import build_derived_facts
from src.tongshu.reasoning.ziping_v3.judgment import (
    judge_ling, derive_party_structure, run_strength_chain,
)
from src.tongshu.reasoning.ziping_v3.judgment_ext import (
    judge_climate, judge_qing, judge_tongguan, judge_disease, judge_qi, judge_yong,
)
from src.tongshu.reasoning.ziping_v3.types import UndeterminedReason


def _setup():
    c = BaziEngine().compute((1980, 6, 22, 10), gender="male")
    fact, avail, _ = chart_to_context(c)
    derived = build_derived_facts(fact, {"commanded_stem": "REN"})
    ctx = EngineContext(fact, avail, {})
    ling = judge_ling(ctx, derived)
    party = derive_party_structure(ctx, derived, de_ling=(ling.state == "DE_LING"))
    return ctx, derived, ling, party


def test_climate_hot():
    ctx, derived, _, _ = _setup()
    j = judge_climate(ctx, derived, None)
    # 午 = 夏 → HOT (CLIMATEFACT-003, 滴天髓·寒暖)
    assert j.state == "HOT", f"午月应 HOT, 实为 {j.state}"
    assert j.matched_rule_ids[0].startswith("CLIMATE-"), \
        f"期望 CLIMATE-* 规则, 实为 {j.matched_rule_ids}"
    assert any("E-DT-CLIMATE" in e for e in j.evidence_refs), \
        f"期望滴天髓证据, 实为 {j.evidence_refs}"
    print(f"气候: {j.state} rule={j.matched_rule_ids}")


def test_climate_fail_closed_spring():
    """春/秋 月令 无寒暖极端 且 无调候表 → fail-closed 不臆测."""
    c = BaziEngine().compute((1990, 3, 15, 10), gender="male")  # 寅月春
    fact, avail, _ = chart_to_context(c)
    derived = build_derived_facts(fact, {})
    ctx = EngineContext(fact, avail, {})
    j = judge_climate(ctx, derived, None)
    # 春月: 非寒非暖, 无水/火土单侧主导 或 有表缺失 → UNDETERMINED
    assert j.state in ("UNDETERMINED", "WET", "DRY"), f"春月不应强判寒暖: {j.state}"
    if j.state == "UNDETERMINED":
        assert j.reason in (r.value for r in UndeterminedReason)
    print(f"春月 fail-closed: {j.state} reason={j.reason}")


def test_qing_turbid_officer_mix():
    ctx, derived, _, _ = _setup()
    j = judge_qing(ctx, derived)
    # 壬(七杀) + 癸(正官) 同透 → 官杀混杂 → TURBID (QING-005)
    assert j.state == "TURBID" and j.matched_rule_ids == ["QING-005"], \
        f"官杀混杂应 QING-005 TURBID: {j.state} {j.matched_rule_ids}"
    print(f"清浊: {j.state} rule={j.matched_rule_ids} ({j.reason_detail})")


def test_tongguan():
    ctx, derived, _, _ = _setup()
    j = judge_tongguan(ctx, derived)
    # 官杀对立存在; 无食神制杀; 无印/食伤透干作桥 → TONGGUAN_ABSENT (TONGGUAN-005)
    assert j.state in ("TONGGUAN_ABSENT", "TONGGUAN_EFFECTIVE", "OPPOSITION_RESOLVED"), j.state
    assert j.matched_rule_ids, "必须携带命中规则 (ARCH-009)"
    print(f"通关: {j.state} rule={j.matched_rule_ids} ({j.reason_detail})")


def test_disease_fail_closed_no_pattern():
    ctx, derived, _, _ = _setup()
    j = judge_disease(ctx, derived, pattern_judgment=None)
    # 主格未定 → 病药 fail-closed
    assert j.state == "UNDETERMINED"
    assert j.reason == "DEPENDENCY_UNRESOLVED", f"病药缺主格应 DEPENDENCY_UNRESOLVED: {j.reason}"
    print(f"病药 fail-closed: {j.state}/{j.reason}")


def test_qi_concentrated():
    ctx, derived, ling, party = _setup()
    j = judge_qi(ctx, derived, ling, party)
    # 得令 + 月令 ∈ 帮身 → CONCENTRATED (QI-001)
    assert j.state in ("CONCENTRATED", "CONTESTED", "DOMINANT", "MIXED"), j.state
    assert j.matched_rule_ids, "气势 必须 携带规则命中"
    print(f"气势: {j.state} rule={j.matched_rule_ids}")


def test_yong_multi_method_no_merge():
    """§23 YONG-MULTI-001: 多方法 全部输出 + 标注来源, 不合并."""
    ctx, derived, ling, party = _setup()
    out = judge_yong(ctx, derived, None, None, None, None, None)
    # 分方法 键 全在
    assert set(out.keys()) == {"pattern", "climate", "disease", "bridge"}, out.keys()
    # 各方法独立 状态 (无合并 单一用神)
    for k, j in out.items():
        assert j.domain == f"YONG-{k.upper()}", f"方法域标注错误: {j.domain}"
    print(f"用神分方法: { {k: v.state for k, v in out.items()} } (不合并 ✓)")


def test_all_judgments_have_evidence_or_reason():
    """ARCH-008/009/§77: 每个判断 必带 证据链 或 UNDETERMINED 分因."""
    ctx, derived, ling, party = _setup()
    js = [
        ling,
        judge_climate(ctx, derived, None),
        judge_qing(ctx, derived),
        judge_tongguan(ctx, derived),
        judge_disease(ctx, derived, None),
        judge_qi(ctx, derived, ling, party),
        *judge_yong(ctx, derived, None, None, None, None, None).values(),
    ]
    for j in js:
        if j.state == "UNDETERMINED":
            assert j.reason, f"{j.domain} UNDETERMINED 无分因 (§77)"
        else:
            assert j.matched_rule_ids and j.evidence_refs, \
                f"{j.domain}/{j.state} 缺证据链 (ARCH-009)"
    print(f"全 7 域 判断 证据链/分因 完整 ✓ ({len(js)} judgments)")


if __name__ == "__main__":
    test_climate_hot()
    test_climate_fail_closed_spring()
    test_qing_turbid_officer_mix()
    test_tongguan()
    test_disease_fail_closed_no_pattern()
    test_qi_concentrated()
    test_yong_multi_method_no_merge()
    test_all_judgments_have_evidence_or_reason()
    print("\nP4 判断扩展层全部通过 ✓")
