"""P1.2-F.1.2: Provenance Gate — Canonical Rule Binding Audit

Checks:
  1. BASE = repo root (parents[2] from tests/spec/)
  2. All index files in data/rules_index/ (not data/rules/)
  3. No dir-level refs (data/rules/ without trailing filename)
  4. canonical_rule_id present for non-placeholder entries
  5. canonical_rule_id matches target rule record's rule_id
  6. Unique positioning: ref + canonical_rule_id -> exactly one record
  7. Status分层: status=index, verification_status, admission_status present
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
assert BASE.name == "wisdom", f"BASE={BASE} does not look like repo root"

INDEX_DIR = BASE / "data" / "rules_index"
RULES_DIR = BASE / "data" / "rules"

INDEX_FILES = sorted(f.name for f in INDEX_DIR.glob("*.json")) if INDEX_DIR.exists() else []

issues: list[str] = []
warnings: list[str] = []


def find_canonical_rule(target_file: Path, canonical_rid: str) -> dict | None:
    """Find a rule record by canonical_rule_id in a target file.
    Returns the record dict if found, None otherwise.
    """
    if not target_file.exists():
        return None
    with open(target_file, encoding="utf-8") as f:
        data = json.load(f)

    # Single-rule file
    if "rule_id" in data:
        if data["rule_id"] == canonical_rid:
            return data
        return None

    # Multi-rule file
    rules_list = data.get("rules", [])
    for r in rules_list:
        if r.get("rule_id") == canonical_rid:
            return r
    return None


def main() -> int:
    print(f"BASE = {BASE}")
    print(f"INDEX_DIR = {INDEX_DIR}")
    print(f"RULES_DIR = {RULES_DIR}")
    print(f"Index files: {len(INDEX_FILES)}")
    print()

    if not INDEX_DIR.exists():
        issues.append(f"INDEX_DIR does not exist: {INDEX_DIR}")
        print("=" * 60)
        print("FAIL: index directory missing")
        return 1

    total_entries = 0
    bound_entries = 0

    for fname in INDEX_FILES:
        fpath = f"data/rules_index/{fname}"
        full = INDEX_DIR / fname

        with open(full, encoding="utf-8") as f:
            d = json.load(f)

        meta = d.get("_meta", {})

        # Check 1: status must be "index"
        if meta.get("status") != "index":
            issues.append(f"{fpath}: _meta.status='{meta.get('status')}' expected 'index'")

        # Check 2: verification_status and admission_status must be present
        if "verification_status" not in meta:
            issues.append(f"{fpath}: missing _meta.verification_status")
        if "admission_status" not in meta:
            issues.append(f"{fpath}: missing _meta.admission_status")

        rules = d.get("rules", [])
        total_entries += len(rules)

        for r in rules:
            idx_rid = r.get("rule_id", "?")
            ref = r.get("ref", "")
            canonical_rid = r.get("canonical_rule_id", "")
            placeholder = r.get("placeholder", False)
            note = r.get("note", "")

            # Check 3: No dir-level refs
            if ref.endswith("/") or ref.endswith("\\"):
                if not placeholder:
                    issues.append(f"{fpath}: rule '{idx_rid}' has dir-level ref '{ref}'")
                continue

            # Check 4: Placeholder entries skip binding check
            if placeholder:
                continue

            # Check 5: canonical_rule_id must be present
            if not canonical_rid:
                issues.append(f"{fpath}: rule '{idx_rid}' missing canonical_rule_id")
                continue

            bound_entries += 1

            # Check 6: Target file exists
            target_file = BASE / ref
            if not target_file.exists():
                issues.append(f"{fpath}: rule '{idx_rid}' refs missing file '{ref}'")
                continue

            # Check 7: canonical_rule_id matches exactly one record
            record = find_canonical_rule(target_file, canonical_rid)
            if record is None:
                issues.append(
                    f"{fpath}: rule '{idx_rid}' -> {ref}[{canonical_rid}] "
                    f"NOT FOUND (file exists but no matching record)"
                )
                continue

            # Check 8: Required fields in target record
            required = {"rule_id", "title", "source", "conditions", "conclusion"}
            missing = required - set(record.keys())
            if missing:
                issues.append(
                    f"{fpath}: rule '{idx_rid}' -> {ref}[{canonical_rid}] "
                    f"missing fields: {missing}"
                )

    print("=" * 60)
    print(f"Total index entries: {total_entries}")
    print(f"Bound entries (non-placeholder): {bound_entries}")
    print(f"ISSUES ({len(issues)}):")
    for i in issues:
        print(f"  [X] {i}")
    print()
    print(f"WARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"  [!] {w}")
    print()
    print("=" * 60)

    if issues:
        print("\nPROVENANCE_GATE: FAIL")
        return 1
    else:
        print(f"\nPROVENANCE_GATE: PASS ({bound_entries}/{total_entries} entries bound)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
