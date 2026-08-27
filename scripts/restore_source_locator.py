"""恢复 data/evidence/*.json 中被 3e0a3e1 误删的 source_locator 字段。
以 f8c52ec (KNOWN-GOOD BASELINE) 为准：旧文件按 evidence_id 恢复 source_locator；
新增文件(基线中不存在)跳过并报告。
"""
import json
import subprocess
from pathlib import Path

EV_DIR = Path("data/evidence")

# 读基线版本的全部证据文件
out = subprocess.run(
    ["git", "show", "f8c52ec", "--name-only", "--format=", "--", "backend/data/evidence/"],
    capture_output=True, text=True, cwd="..",
)
baseline_files = [Path(p).name for p in out.stdout.split() if p.endswith(".json")]
print(f"Baseline evidence files: {len(baseline_files)}")

restored = skipped_new = already_ok = missing_locator = 0
for path in sorted(EV_DIR.glob("*.json")):
    with open(path, encoding="utf-8") as f:
        ev = json.load(f)
    if "source_locator" in ev and ev["source_locator"].get("work"):
        already_ok += 1
        continue
    if path.name in baseline_files:
        blob = subprocess.run(
            ["git", "show", f"f8c52ec:backend/data/evidence/{path.name}"],
            capture_output=True, text=True, cwd=".",
        )
        old = json.loads(blob.stdout)
        loc = old.get("source_locator")
        if loc and loc.get("work"):
            ev["source_locator"] = loc
            with open(path, "w", encoding="utf-8") as f:
                json.dump(ev, f, ensure_ascii=False, indent=2)
            restored += 1
            continue
    missing_locator += 1
    print(f"  NO-LOCATOR: {path.name}")

print(f"\nrestored={restored} already_ok={already_ok} no_locator_in_baseline={missing_locator}")
