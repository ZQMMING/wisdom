#!/usr/bin/env python3
"""Fix YIJING concept IDs to be per-category sequential (matching other domains)."""
import yaml
from pathlib import Path

fpath = Path("src/tongshu/k2g/concepts/yi_concepts.yaml")
data = yaml.safe_load(fpath.read_text(encoding="utf-8"))

counters = {"TRIGRAMS": 0, "HEXAGRAMS": 0, "KEY_TERMS": 0}
prefixes = {"TRIGRAMS": "YI_TR", "HEXAGRAMS": "YI_HX", "KEY_TERMS": "YI_KT"}

for c in data["concepts"]:
    cat = c["category"]
    counters[cat] += 1
    c["concept_id"] = f"{prefixes[cat]}_{counters[cat]:03d}"

with open(fpath, "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

print(f"修正完成:")
for cat, cnt in counters.items():
    print(f"  {cat}: {prefixes[cat]}_001-{prefixes[cat]}_{cnt:03d}")
