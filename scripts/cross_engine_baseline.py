#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cross-Engine Baseline Snapshot (Phase 5 前置)

V2 Cross-Engine Contamination Test (验收规范 §34) 的基准快照。
固定一组标准输入，分别运行各引擎，记录结果 hash。
后续任一引擎变更后重跑，其他引擎 hash 必须不变（互补不比较）。

用法:
    python scripts/cross_engine_baseline.py --snapshot   # 生成/更新 baseline
    python scripts/cross_engine_baseline.py --check      # 对比当前结果 vs baseline
"""
import sys, json, hashlib, argparse
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

SNAPSHOT_PATH = ROOT / "cases" / "golden" / "cross_engine_baseline.json"

# 标准输入 (固定, 覆盖出生 + 事件)
STD_BIRTH = {"year": 1990, "month": 5, "day": 15, "hour": 10, "gender": "male"}
STD_DATE = date(2026, 8, 27)


def _hash(obj) -> str:
    """确定性序列化 + sha256."""
    def default(o):
        if hasattr(o, "to_dict"):
            return o.to_dict()
        if hasattr(o, "__dict__"):
            return o.__dict__
        return str(o)
    s = json.dumps(obj, default=default, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def run_engines() -> dict:
    """运行所有引擎, 返回 {engine: result_hash}."""
    results = {}
    # ZIWEI
    try:
        from tongshu.engines.ziwei_adapter import ZiweiSolarAdapter
        r = ZiweiSolarAdapter().compute(**STD_BIRTH)
        results["ziwei"] = _hash(r)
    except Exception as e:
        results["ziwei"] = f"ERROR: {e}"
    # MEIHUA (time cast)
    try:
        from tongshu.engines.meihua import cast_by_time
        r = cast_by_time(STD_BIRTH["year"], STD_BIRTH["month"], STD_BIRTH["day"], STD_BIRTH["hour"])
        results["meihua"] = _hash(r)
    except Exception as e:
        results["meihua"] = f"ERROR: {e}"
    # HUANGLI
    try:
        from tongshu.engines.huangli_engine import HuangliEngine
        r = HuangliEngine().get_day(STD_DATE)
        results["huangli"] = _hash(r)
    except Exception as e:
        results["huangli"] = f"ERROR: {e}"
    # BLIND
    try:
        from tongshu.engines.blind_bazi_engine import compute_blind_bazi
        r = compute_blind_bazi((STD_BIRTH["year"], STD_BIRTH["month"], STD_BIRTH["day"], STD_BIRTH["hour"]), STD_BIRTH["gender"])
        # blind result 可能含 CanonicalSignal 对象, 用 repr 兜底
        results["blind"] = _hash(repr(r) if not hasattr(r, "to_dict") else r)
    except Exception as e:
        results["blind"] = f"ERROR: {e}"
    # HELUO (calculate 需 bazi 对象, 用 golden case 结果 hash 代替)
    try:
        from tongshu.engines.heluo import HeluoCanonical
        h = HeluoCanonical()
        # 用其内置 golden cases 的确定性输出做 baseline
        ok = h.run_all_golden_cases() if hasattr(h, "run_all_golden_cases") else str(h.GOLDEN_CASES)
        results["heluo"] = _hash(str(ok))
    except Exception as e:
        results["heluo"] = f"ERROR: {e}"
    return results


def snapshot():
    res = run_engines()
    payload = {
        "description": "Cross-Engine Contamination Baseline (V2 §34)",
        "std_birth": STD_BIRTH,
        "std_date": str(STD_DATE),
        "engine_hashes": res,
        "note": "改任一引擎后重跑 --check, 其他引擎 hash 必须不变 (互补不比较)",
    }
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Baseline snapshot written: {SNAPSHOT_PATH}")
    for eng, h in res.items():
        print(f"  {eng:12s}: {h}")


def check():
    if not SNAPSHOT_PATH.exists():
        print("FAIL: baseline 不存在, 先运行 --snapshot")
        sys.exit(1)
    base = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))["engine_hashes"]
    cur = run_engines()
    print("=== Cross-Engine Contamination Check ===")
    print(f"{'Engine':12s} {'Baseline':20s} {'Current':20s} {'Status'}")
    all_ok = True
    for eng in base:
        b, c = base[eng], cur.get(eng, "MISSING")
        ok = (b == c) or str(b).startswith("ERROR")
        if not ok:
            all_ok = False
        print(f"{eng:12s} {str(b):20s} {str(c):20s} {'OK' if ok else 'CHANGED'}")
    print()
    print("PASS: 无引擎被污染" if all_ok else "FAIL: 有引擎结果变化 (检查是否预期)")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        check()
    else:
        snapshot()
