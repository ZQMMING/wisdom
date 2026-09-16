# -*- coding: utf-8 -*-
"""盲派 Rule Matcher V3.2
输入: Bazi Facts (Canonical, 不重算)
输出: 命中 Rule_ID 列表 + Assertion + Provenance
禁止: 新增规则/评分/Judgment泄漏/重算Bazi Facts
"""
from typing import Dict, List, Any
from .blind_rule_registry import RULE_REGISTRY, RuleDef


def _hit(rule_id: str, assertion: str, evidence_id: str, inputs: Dict[str, Any]) -> Dict:
    return {
        "rule_id": rule_id,
        "evidence_id": evidence_id,
        "assertion": assertion,
        "inputs": inputs,
        "provenance": f"{rule_id} <- {evidence_id} <- V3.2封板",
    }


def match_rules(chart, blind_result, yingqi_result=None) -> List[Dict]:
    """把现有引擎输出映射到 28 条 Rule。
    只做映射，不新算事实，不新推结论。
    """
    hits: List[Dict] = []

    # ── L1 结构层 ──
    # R-BZ-001 宾主
    hits.append(_hit("R-BZ-001",
        f"MAIN={sorted(blind_result.main_branches)} GUEST={sorted(blind_result.guest_branches)}",
        "EVD-BZ-001",
        {"main": sorted(blind_result.main_branches), "guest": sorted(blind_result.guest_branches)}))

    # R-TY-001 体用
    hits.append(_hit("R-TY-001",
        f"TI={blind_result.ti_stems} YONG={blind_result.yong_stems}",
        "EVD-TY-001",
        {"ti": blind_result.ti_stems, "yong": blind_result.yong_stems}))

    # R-GF-001 功神废神
    hits.append(_hit("R-GF-001",
        f"GONG={sorted(blind_result.zuo_gong_actors)} TARGET={sorted(blind_result.zuo_gong_targets)}",
        "EVD-GF-001",
        {"gong_shen": sorted(blind_result.zuo_gong_actors),
         "targets": sorted(blind_result.zuo_gong_targets)}))

    # R-PJ-001/002 正局反局
    zfj = getattr(blind_result, "zheng_fan_ju", "")
    if zfj == "ZHENG":
        hits.append(_hit("R-PJ-001", "局型=ZHENG", "EVD-PJ-001", {"zheng_fan_ju": zfj}))
    elif zfj == "FAN":
        hits.append(_hit("R-PJ-002", "局型=FAN", "EVD-PJ-002", {"zheng_fan_ju": zfj}))

    # R-ZB-001 贼捕
    zb = getattr(blind_result, "zei_bu", "")
    if zb == "ZEI_BU":
        hits.append(_hit("R-ZB-001",
            f"贼捕结构={blind_result.zei_bu_reason}",
            "EVD-ZB-001", {"zei_bu": zb, "reason": blind_result.zei_bu_reason}))

    # ── L7 MUKU ──
    # R-MUKU-001 墓库识别（从八字事实算）
    all_branches = [chart.year_pillar.earthly_branch,
                    chart.month_pillar.earthly_branch,
                    chart.day_pillar.earthly_branch,
                    chart.hour_pillar.earthly_branch]
    muku_set = {"辰", "戌", "丑", "未"}
    muku_branches = [b for b in all_branches if b in muku_set]
    if muku_branches:
        hits.append(_hit("R-MUKU-001",
            f"MUKU_PRESENT={muku_branches}",
            "EVD-MUKU-001",
            {"muku_branches": muku_branches}))

    # ── L6 神煞 ──
    # R-SHEN-004 驿马
    day_br = chart.day_pillar.earthly_branch
    yima_map = {
        ("申", "子", "辰"): "寅", ("寅", "午", "戌"): "申",
        ("巳", "酉", "丑"): "亥", ("亥", "卯", "未"): "巳",
    }
    for group, yima in yima_map.items():
        if day_br in group:
            hits.append(_hit("R-SHEN-004",
                f"驿马={yima}", "EVD-SHEN-004", {"day_branch": day_br, "yima": yima}))
            break

    # R-SHEN-005 空亡
    xunkong = getattr(chart, "xunkong", [])
    if xunkong:
        hits.append(_hit("R-SHEN-005",
            f"空亡={xunkong}", "EVD-SHEN-005", {"xunkong": list(xunkong)}))

    return hits


def coverage_report() -> Dict[str, Any]:
    """Rule 覆盖率报告"""
    from .blind_rule_registry import RULE_REGISTRY, FORBIDDEN_RULES, COUNTER_EXAMPLES
    return {
        "registry_total": len(RULE_REGISTRY),
        "established": sum(1 for r in RULE_REGISTRY.values() if r.status == "ESTABLISHED"),
        "forbidden_rules": list(FORBIDDEN_RULES.keys()),
        "counter_examples": [ce[0] for ce in COUNTER_EXAMPLES],
        "rule_ids": list(RULE_REGISTRY.keys()),
    }
