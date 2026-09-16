# -*- coding: utf-8 -*-
"""PATCH-067 Climate Condition Runtime Contract
原文条件→谓词; 主次用拆分; 状态枚举(禁百分比/评分)
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 状态枚举(068冻结)
CLIMATE_STATE_ENUM = ["PRIMARY", "SECONDARY", "SUPPORTING", "DEGRADED", "ABSENT"]

# 10x12 谓词表(主用/辅/忌/降级条件)
CLIMATE_PREDICATES = {
    ("乙", "戌"): {"primary": "癸", "secondary": "", "avoid": "戊制癸", "degrade_when": "壬透多", "degrade_target": "癸", "src": "QTBJ-022-001"},
    ("乙", "午"): {"primary": "癸", "secondary": "丙", "avoid": "", "degrade_when": "", "degrade_target": "", "src": "QTBJ-018-001"},
    ("丙", "午"): {"primary": "壬", "secondary": "庚", "avoid": "戊己制壬", "degrade_when": "", "degrade_target": "", "src": "QTBJ-031-001"},
    ("庚", "申"): {"primary": "丁", "secondary": "甲", "avoid": "壬癸", "degrade_when": "", "degrade_target": "", "src": "QTBJ-068-001"},
}


def climate_eval(daymaster, month_branch, stems_present=None):
    """
    谓词求值: IF 日主 AND 月令 THEN primary/secondary
    降级: IF degrade_when条件成立 THEN target=DEGRADED
    """
    key = (daymaster, month_branch)
    if key not in CLIMATE_PREDICATES:
        return {"status": "ABSENT", "reason": "NOT_IN_REGISTRY", "namespace": "QTBJ.climate_use"}
    p = CLIMATE_PREDICATES[key]
    out = {
        "status": "RESOLVED",
        "namespace": "QTBJ.climate_use",
        "primary_use": p["primary"],
        "primary_state": "PRIMARY",
        "secondary_use": p["secondary"] or None,
        "secondary_state": "SECONDARY" if p["secondary"] else "ABSENT",
        "avoid": p["avoid"] or None,
        "src": p["src"]
    }
    # 降级判定(GC-001: 壬透多→癸降级)
    if p["degrade_when"] and stems_present:
        if "壬透多" in p["degrade_when"] and stems_present.count("壬") >= 2:
            out["degraded"] = {"target": p["degrade_target"], "state": "DEGRADED", "reason": "壬透多水难生乙"}
    return out


if __name__ == '__main__':
    print("=== PATCH-067 调候运行时 ===")
    # GC-001: 乙木戌月, 天干壬癸壬(壬=2)
    r = climate_eval("乙", "戌", stems_present=["癸", "壬", "乙", "壬"])
    print("GC-001 乙戌(壬透二):")
    for k, v in r.items():
        print(f"  {k}: {v}")
