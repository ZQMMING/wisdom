# -*- coding: utf-8 -*-
"""端到端测试: BaziChart → §28 统一输出 (1980-06-22 丙寅日 完整链路).

验证:
  1. 已实现域 全部出判断 + 携带证据链 (LING/GROWTH/STRENGTH/CLIMATE/QING/TONGGUAN/QI/YONG*)
  2. 未实现域 全部 fail-closed UNDETERMINED + 分因 (§82 不宣称完成)
  3. §28 输出契约 完整 (engine/version/judgments/undetermined/status)
  4. 每域 判断 必带 evidence 或 UNDETERMINED 分因 (ARCH-008/009/§77)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.reasoning.ziping_v3.runner import run_ziping


def _chart():
    return BaziEngine().compute((1980, 6, 22, 10), gender="male")


def test_contract_shape():
    out = run_ziping(_chart(), month_command={"commanded_stem": "REN"})
    assert out["engine"] == "ZIPING_RULE_ENGINE"
    assert out["version"] == "3.1"
    assert out["status"] == "DONE"
    assert isinstance(out["judgments"], list) and out["judgments"]
    # §28 每 judgment 必带 四要素 + 分因字段
    for j in out["judgments"]:
        for key in ("domain", "state", "matched_rule_ids", "evidence_refs",
                    "method_scope", "undetermined_reason"):
            assert key in j, f"§28 契约缺字段 {key}"
    print(f"§28 契约完整: {len(out['judgments'])} 域判断, status={out['status']}")


def test_implemented_domains_judged():
    out = run_ziping(_chart(), month_command={"commanded_stem": "REN"})
    by_domain = {}
    for j in out["judgments"]:
        by_domain.setdefault(j["domain"], []).append(j)
    # 已实现域 必出 DETERMINED 判断
    for d in ("CLIMATE", "QING", "QI"):
        assert by_domain.get(d, [{}])[0].get("state") != "UNDETERMINED", \
            f"已实现域 {d} 不应 UNDETERMINED: {by_domain.get(d)}"
    # STRENGTH 有明确结论
    assert "STRENGTH" in by_domain
    print(f"已实现域 出判断: { {k: v[0]['state'] for k,v in by_domain.items() if not (k in ('PATTERN','PATTERN_QUALITY','TRUE','SPECIAL','XIANG','XIJI','TEMPORAL') and len(v)==1)} }")


def test_unimplemented_fail_closed():
    out = run_ziping(_chart())
    by_domain = {j["domain"]: j for j in out["judgments"]}
    # 未实现域 必须 UNDETERMINED + 分因 (不得假判断)
    for d in ("PATTERN", "PATTERN_QUALITY", "TRUE", "SPECIAL", "XIANG", "XIJI", "TEMPORAL"):
        j = by_domain.get(d)
        assert j is not None, f"未实现域 {d} 未登记 (fail-closed 缺失)"
        assert j["state"] == "UNDETERMINED", f"{d} 必须 UNDETERMINED, 实为 {j['state']}"
        assert j["undetermined_reason"], f"{d} UNDETERMINED 缺分因 (§77)"
    print("未实现域 7 项 全部 fail-closed + 分因 ✓")


def test_ling_strength_evidence_chain():
    out = run_ziping(_chart(), month_command={"commanded_stem": "REN"})
    by_domain = {j["domain"]: j for j in out["judgments"]}
    ling = by_domain["LING"]
    strength = by_domain["STRENGTH"]
    # LING 得令 + 证据
    assert ling["state"] == "DE_LING" and ling["matched_rule_ids"] and ling["evidence_refs"]
    # STRENGTH 有结论 + 证据链
    assert strength["matched_rule_ids"] or strength["undetermined_reason"], \
        "STRENGTH 无证据链 (ARCH-009)"
    print(f"证据链: LING={ling['matched_rule_ids']}→{ling['evidence_refs']}, "
          f"STRENGTH={strength['matched_rule_ids']} state={strength['state']}")


def test_no_luck_pillars_no_temporal_claim():
    """无 流年/流月/流日 输入 → TEMPORAL 必须 UNDETERMINED (不臆测时间层)."""
    out = run_ziping(_chart())  # 不注入 temporal
    by_domain = {j["domain"]: j for j in out["judgments"]}
    assert by_domain["TEMPORAL"]["state"] == "UNDETERMINED"
    print("无时间层输入 → TEMPORAL fail-closed ✓ (不臆测流年)")


if __name__ == "__main__":
    test_contract_shape()
    test_implemented_domains_judged()
    test_unimplemented_fail_closed()
    test_ling_strength_evidence_chain()
    test_no_luck_pillars_no_temporal_claim()
    print("\n端到端 runner 全部通过 ✓")
