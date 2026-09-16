# -*- coding: utf-8 -*-
"""
PATCH-056 QTBJ 调候 Rule Admission
把 QTBJ 202 条(全A级)按「日主×月令→调候用神」注册进 climate_use_state
铁律: 调候用神 ≠ 格局用神 ≠ 扶抑用神; climate_use_state 独立
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# QTBJ 调候用神注册表（日主×月令 → 调候用神 + 条件）
# 以已钉死原文为锚点, 非全量202条——逐条补录前先落结构
CLIMATE_USE_REGISTRY = {
    # 乙木九月(戌月) QTBJ-022-001 A
    ("乙", "戌"): {
        "use": "癸",
        "source": "QTBJ-022-001",
        "grade": "A",
        "conditions": [
            "根枯叶落必赖癸水滋养",
            "癸+辛金发水源→科甲",
            "四柱壬多→水难生乙(癸降级)",
            "支多戊透→作从看(无比劫)"
        ],
        "degrade": {"壬多": "癸水降级"},
    },
}


def climate_use_admit(day_master, month_branch, fact):
    """
    day_master: 日主
    month_branch: 月支
    fact: 命局事实(壬透数/戊透数等)
    return: climate_use_state
    """
    key = (day_master, month_branch)
    if key not in CLIMATE_USE_REGISTRY:
        return {"climate_use_state": "NOT_REGISTERED",
                "note": "该日主月令QTBJ调候未注册, 待逐条补录"}
    reg = CLIMATE_USE_REGISTRY[key]
    use = reg["use"]
    degrade_note = None
    if fact.get("ren_visible", 0) >= 2:
        degrade_note = "四柱壬多→水难生乙, 癸水降级"
        return {"climate_use_state": "DETERMINED", "use": use, "degraded": True,
                "degrade_reason": degrade_note,
                "evidence": [reg["source"]], "grade": reg["grade"],
                "note": "调候用癸, 壬多降级"}
    return {"climate_use_state": "DETERMINED", "use": use, "degraded": False,
            "evidence": [reg["source"]], "grade": reg["grade"],
            "conditions": reg["conditions"], "note": "调候用癸水"}


if __name__ == "__main__":
    print("=== PATCH-056 QTBJ 调候 Rule Admission ===")
    # GC-001 乙木戌月, 壬透3(癸亥壬戌乙未壬午: 天干癸壬壬)
    r = climate_use_admit("乙", "戌", {"ren_visible": 3})
    print("GC-001 乙木戌月 壬透3:")
    print(json.dumps(r, ensure_ascii=False, indent=1))
    # 干净例: 壬透0
    r2 = climate_use_admit("乙", "戌", {"ren_visible": 0})
    print("\n壬透0(干净):")
    print(json.dumps(r2, ensure_ascii=False, indent=1))
