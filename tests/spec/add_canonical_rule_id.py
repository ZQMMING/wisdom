"""P1.2-F.1.2: Canonical Rule Binding — 为每个 index entry 添加 canonical_rule_id 并验证绑定"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
INDEX_DIR = BASE / "data" / "rules_index"
RULES_DIR = BASE / "data" / "rules"

# Canonical rule_id mapping: ref_path -> canonical_rule_id
# For single-rule files, the rule_id is the filename stem
# For multi-rule files, we need explicit mapping

# Pre-computed mapping based on existing rule files
CANONICAL_RULE_MAP: dict[str, str] = {
    # Bazi stems — ZPZ-101 covers day master element baseline
    "data/rules/ZPZ-101.json": "ZPZ-101",
    "data/rules/ZPZ-001.json": "ZPZ-001",
    "data/rules/YHZP-103.json": "YHZP-103",
    # Bazi branches — same as stems
    "data/rules/HLT-101.json": "HLT-101",
    # Bazi ten gods — ZPZ-121 covers non-acting ten god transparency
    "data/rules/MAR-106.json": "MAR-106",
    "data/rules/HL-101.json": "HL-101",
    # Blind
    "data/rules/MAR-101.json": "MAR-101",
    "data/rules/WLT-101.json": "WLT-101",
    # Ziwei
    "data/rules/ZW-405.json": "ZW-405",
}


def resolve_canonical_rule_id(ref: str, idx_file: str) -> str:
    """Resolve canonical_rule_id from ref path."""
    if ref in CANONICAL_RULE_MAP:
        return CANONICAL_RULE_MAP[ref]

    # Fallback: derive from filename
    stem = Path(ref).stem
    if stem in CANONICAL_RULE_MAP.values():
        return stem

    # Try to load the file and extract rule_id
    full = BASE / ref
    if full.exists():
        with open(full, encoding="utf-8") as f:
            d = json.load(f)
        if "rule_id" in d:
            return d["rule_id"]
        if "rules" in d and d["rules"]:
            return d["rules"][0].get("rule_id", "")

    raise ValueError(f"Cannot resolve canonical_rule_id for ref={ref} in {idx_file}")


def main() -> int:
    issues: list[str] = []
    updated_count = 0

    for idx_file in sorted(INDEX_DIR.glob("*.json")):
        with open(idx_file, encoding="utf-8") as f:
            d = json.load(f)

        meta = d.get("_meta", {})
        rules = d.get("rules", [])

        for r in rules:
            ref = r.get("ref", "")
            rid = r.get("rule_id", "?")
            placeholder = r.get("placeholder", False)

            if placeholder:
                # Placeholder entries don't need canonical_rule_id yet
                r["canonical_rule_id"] = ""
                continue

            if not ref or ref.endswith("/") or ref.endswith("\\"):
                issues.append(f"{idx_file.name}: rule '{rid}' has invalid ref '{ref}'")
                r["canonical_rule_id"] = ""
                continue

            try:
                canonical_rid = resolve_canonical_rule_id(ref, idx_file.name)
                r["canonical_rule_id"] = canonical_rid
                updated_count += 1
            except ValueError as e:
                issues.append(f"{idx_file.name}: {e}")
                r["canonical_rule_id"] = ""

        # Write back
        with open(idx_file, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

    print(f"Updated {updated_count} index entries with canonical_rule_id")
    print(f"Issues: {len(issues)}")
    for i in issues:
        print(f"  [X] {i}")

    if issues:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
