# -*- coding: utf-8 -*-
"""新旧输出逐条比对，作为「断言输入源切换」的前置证据
用法：python -m tests.test_new_vs_old [--out report.jsonl]
"""
import json, sys, argparse
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.common.unified_overview import build_unified_overview
from engines.axis_xiuqi   import xiuqi_axis
from engines.axis_fude    import fude_axis
from engines.special_merge import merge

MAP  = json.load(Path("docs/migrations/pattern_rename_v1.json").open(encoding="utf-8-sig"))
S2C  = json.load(Path("docs/migrations/state_to_confidence_v1.json").open(encoding="utf-8-sig"))
CASES= json.load(Path("tests/cases_l1_v1.json").open(encoding="utf-8-sig"))

EXPECTED_MISMATCH = {
    "li-066": {"field":"confidence",
               "old":"CONFIRMED", "new":"MID",
               "reason":"D-争合降档（新增维度，旧引擎未实现）"},
    "F1":     {"field":"family+confidence",
               "old":("","REJECT"), "new":("一行成象·炎上","MID"),
               "reason":"D-财星减项翻转"},
    "li-071": {"field":"family+confidence",
               "old":("从旺格","CANDIDATE"), "new":("一行成象·从革","CONFIRMED"),
               "reason":"D-财星硬闸（行为变更）"},
    "A5":     {"field":"confidence",
               "old":"CANDIDATE", "new":"CONFIRMED",
               "reason":"D-稼穑四库全（旧引擎dm_ju不认四库全）"},
    "A6":     {"field":"pattern_claimed",
               "old":"从旺格", "new":"无",
               "reason":"D-从格fallback（confidence一致，均为REJECT）"},
    "A8":     {"field":"pattern_claimed",
               "old":"从旺格", "new":"无",
               "reason":"D-从格fallback（同上）"},
}

def parse_key(key):
    """'癸亥乙卯乙未壬午' -> {'year':('癸','亥'), ...}"""
    gans = key[0::2]
    zhis = key[1::2]
    keys = ["year", "month", "day", "hour"]
    return {k: (gans[i], zhis[i]) for i, k in enumerate(keys)}

def build_facts(pillars):
    """从build_unified_overview提取facts"""
    result = build_unified_overview(pillars)
    facts = {
        "month_branch": pillars["month"][1],
        "combination_facts": result.get("daymaster_power_network", {}).get("facts", {}).get("combination_facts", {}),
    }
    return facts, result

# ---------- 旧引擎归一化 ----------
def norm_old(raw):
    sp = raw.get("special_pattern", {}) or {}
    pats = sp.get("patterns") or []
    fam = pats[-1] if isinstance(pats, list) and pats else ""
    if isinstance(fam, dict):
        fam = fam.get("name", "")
    state = sp.get("pattern", {}).get("state") if isinstance(sp.get("pattern"), dict) else None
    if state is None:
        state = sp.get("zhuanwang_state")
    conf = S2C.get(str(state), S2C.get("_default", "REJECT"))
    ptype = "化气型" if sp.get("hua_qi") else ("专旺型" if sp.get("zhuanwang") else "无")
    claimed = MAP.get(fam, fam) or "无"
    return {"pattern_claimed": claimed, "pattern_type": ptype, "confidence": conf, "_raw": sp}

# ---------- 新层归一化 ----------
def norm_new(out):
    """新层merge返回元组(pattern_claimed, pattern_type, confidence, score)"""
    claimed, ptype, conf, score = out
    claimed = claimed or "无"
    ptype = ptype or "无"
    conf = conf or "REJECT"
    return {"pattern_claimed": claimed, "pattern_type": ptype, "confidence": conf, "score": score}

def run_new(pillars, facts, gate_debug):
    x = xiuqi_axis(pillars, facts, gate_debug)
    f = fude_axis(pillars, facts, gate_debug)
    return merge(x, f, "")

# ---------- 比对 ----------
def compare(a, b):
    diffs = []
    for k in ("pattern_claimed","pattern_type","confidence"):
        if a[k] != b[k]:
            diffs.append(f"{k}: {a[k]!r} vs {b[k]!r}")
    return diffs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="tests/new_vs_old.jsonl")
    args = ap.parse_args()

    rows, summary = [], defaultdict(int)
    for c in CASES:
        try:
            pillars = parse_key(c["key"])
            facts, raw_old = build_facts(pillars)
            gate_debug = raw_old.get("special_pattern", {}).get("_gate_debug", [])
            old = norm_old(raw_old)
            new = norm_new(run_new(pillars, facts, gate_debug))
        except Exception as e:
            rows.append({"id": c["id"], "key": c["key"], "status": "ERROR", "msg": str(e)})
            summary["ERROR"] += 1
            continue

        diffs = compare(old, new)
        in_wl = c["id"] in EXPECTED_MISMATCH
        status = "MATCH" if not diffs else ("WL_EXPECTED" if in_wl else "UNEXPECTED")
        summary[status] += 1

        row = {"id": c["id"], "key": c["key"], "status": status,
               "old": {k: old[k] for k in ("pattern_claimed","pattern_type","confidence")},
               "new": {k: new[k] for k in ("pattern_claimed","pattern_type","confidence")},
               "diffs": diffs}
        if in_wl:
            row["wl"] = EXPECTED_MISMATCH[c["id"]]
        rows.append(row)
        print(f"{c['id']:8s} {status:12s} old={old['pattern_claimed']}/{old['confidence']:<9s} "
              f"new={new['pattern_claimed']}/{new['confidence']:<9s}" + (f" | {'; '.join(diffs)}" if diffs else ""))

    Path(args.out).write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    print(f"\n汇总: {dict(summary)}  产物: {args.out}")

    vanished = [r["id"] for r in rows if r["status"]=="MATCH" and r["id"] in EXPECTED_MISMATCH]
    if vanished:
        print(f"可移出白名单: {vanished}")
    unexpected = [r for r in rows if r["status"]=="UNEXPECTED"]
    if unexpected:
        print(f"意外差异（需登记 divergence）:")
        for r in unexpected: print(f"  {r['id']}: {r['diffs']}")

    sys.exit(0 if not unexpected else 1)

if __name__ == "__main__":
    main()
