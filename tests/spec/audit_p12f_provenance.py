"""P1.2-F.1: Provenance/Admission Gate Audit Script"""
import json, os
from pathlib import Path

BASE = Path(__file__).parent / "wisdom"
if not BASE.exists():
    BASE = Path(__file__).parent

index_files = [
    "data/rules/bazi_stems.json", "data/rules/bazi_branches.json", "data/rules/bazi_ten_gods.json",
    "data/rules/bazi_branch_relations.json", "data/rules/bazi_peach_blossom.json", "data/rules/bazi_five_elements.json",
    "data/rules/blind_main_guest.json", "data/rules/blind_ti_yong.json", "data/rules/blind_zuogong.json",
    "data/rules/blind_ten_gods.json", "data/rules/heluo_numbers.json", "data/rules/yi_hexagrams.json",
    "data/rules/ziwei_stars.json"
]

issues = []
warnings = []

# Build set of all existing rule IDs in data/rules/
existing_rule_ids = {}
for f in os.listdir(BASE / "data" / "rules"):
    if f.endswith(".json") and f not in [os.path.basename(p) for p in index_files]:
        with open(BASE / "data" / "rules" / f, encoding="utf-8") as fh:
            d = json.load(fh)
            existing_rule_ids[d.get("rule_id", "")] = f

print(f"Known rule files: {len(existing_rule_ids)}")
print(f"Index files to audit: {len(index_files)}")
print()

for fpath in index_files:
    full = BASE / fpath
    if not full.exists():
        issues.append(f"MISSING FILE: {fpath}")
        continue
    with open(full, encoding="utf-8") as f:
        d = json.load(f)
    meta = d.get("_meta", {})
    rules = d.get("rules", [])

    # Check meta status
    status = meta.get("status", "")
    if status == "verified":
        issues.append(f"{fpath}: _meta.status='verified' but this is a rule INDEX, not a verified asset. Use 'index' or 'candidate'.")

    for r in rules:
        ref = r.get("ref", "")
        rule_id = r.get("rule_id", "?")

        # Check dir-level refs
        if ref.endswith("/") or ref.endswith("\\"):
            issues.append(f"{fpath}: rule '{rule_id}' has dir-level ref '{ref}' — must point to specific file")
            continue

        # Check ref exists
        if ref and not os.path.exists(BASE / ref):
            issues.append(f"{fpath}: rule '{rule_id}' refs missing file '{ref}'")

        # Check if ref points to a known rule file
        ref_basename = os.path.basename(ref) if ref else ""
        if ref and ref not in existing_rule_ids and ref_basename not in existing_rule_ids.values():
            # The ref might be to an existing file that just doesn't have a rule_id we indexed
            if os.path.exists(BASE / ref):
                warnings.append(f"{fpath}: rule '{rule_id}' refs '{ref}' (file exists but rule_id unknown)")
            else:
                issues.append(f"{fpath}: rule '{rule_id}' refs '{ref}' (FILE NOT FOUND)")

print("=" * 60)
print(f"ISSUES ({len(issues)}):")
for i in issues:
    print(f"  [X] {i}")
print()
print(f"WARNINGS ({len(warnings)}):")
for w in warnings:
    print(f"  [!] {w}")
print()
print("=" * 60)

# Now check: which rule_ids in existing data/rules/ are NOT referenced by any index?
all_referenced = set()
for fpath in index_files:
    full = BASE / fpath
    if not full.exists():
        continue
    with open(full, encoding="utf-8") as f:
        d = json.load(f)
    for r in d.get("rules", []):
        ref = r.get("ref", "")
        if ref and not ref.endswith("/"):
            all_referenced.add(os.path.basename(ref))

unreferenced = [rid for rid, fname in existing_rule_ids.items() if fname not in all_referenced]
print(f"Existing rule files NOT referenced by any index: {len(unreferenced)}")
for rid in unreferenced[:20]:
    print(f"  - {rid} ({existing_rule_ids[rid]})")
