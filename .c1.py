# -*- coding: utf-8 -*-
import sys; sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.blind_rule_registry import RULE_REGISTRY
from collections import Counter
layers = Counter(r.layer for r in RULE_REGISTRY.values())
for k, v in sorted(layers.items()):
    print(f"{k}: {v}")
print(f"TOTAL: {len(RULE_REGISTRY)}")
print("---")
# 列所有rule_id
for rid in sorted(RULE_REGISTRY.keys()):
    print(rid)
