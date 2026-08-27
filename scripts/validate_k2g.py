#!/usr/bin/env python3
"""Validate K2G concept YAML files."""
import yaml
from pathlib import Path

concepts_dir = Path("src/tongshu/k2g/concepts")
all_ids = []
for f in ["bazi_concepts.yaml", "ziwei_concepts.yaml", "calendar_concepts.yaml", "yi_concepts.yaml"]:
    data = yaml.safe_load((concepts_dir / f).read_text(encoding="utf-8"))
    domain = data["registry"]["domain"]
    count = data["registry"]["total_count"]
    actual = len(data["concepts"])
    ids = [c["concept_id"] for c in data["concepts"]]
    all_ids.extend(ids)
    print(f"{domain}: declared={count} actual={actual} dup_ids={len(ids)-len(set(ids))}")

print(f"Global: total={len(all_ids)} dup={len(all_ids)-len(set(all_ids))}")
dup_ids = [x for x in set(all_ids) if all_ids.count(x) > 1]
if dup_ids:
    print(f"DUP IDs: {dup_ids}")

yi = yaml.safe_load((concepts_dir / "yi_concepts.yaml").read_text(encoding="utf-8"))
cats = {}
for c in yi["concepts"]:
    cats[c["category"]] = cats.get(c["category"], 0) + 1
print(f"YIJING categories: {cats}")
print(f"Sample 1: {yi['concepts'][0]['traditional_term']} -> {yi['concepts'][0]['concept_id']}")
print(f"Sample 2: {yi['concepts'][8]['traditional_term']} -> {yi['concepts'][8]['concept_id']}")
print(f"Sample 3: {yi['concepts'][72]['traditional_term']} -> {yi['concepts'][72]['concept_id']}")
