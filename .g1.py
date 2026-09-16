# -*- coding: utf-8 -*-
import sys; sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.blind_assertion_registry import ASSERTION_REGISTRY
from tongshu.engines.blind_rule_registry import RULE_REGISTRY

# 抽查清单: 5 STRUCTURAL + 2 TIMING + 1 RELATION + 2 MUKU
picks = [
    "A-PJ-ZHENG", "A-ZB-ROBBER_CATCHER", "A-GF-GONGSHEN",
    "A-SX-GONGSYMBOLS", "A-WEALTH-LUASCASH",   # 5 STRUCTURAL
    "A-MARRIAGE-TIMING", "A-DIVORCE-TIMING",   # 2 TIMING
    "A-SX-JIESYMBOLS",                          # 1 RELATION
    "A-MUKU-IDENTIFIED", "A-MUKU-OPENED",       # 2 MUKU
]
for aid in picks:
    a = ASSERTION_REGISTRY[aid]
    r = RULE_REGISTRY[a.rule_id]
    print(f"【{aid}】")
    print(f"  type={a.assertion_type}")
    print(f"  subject={a.subject}  relation={a.relation}  object={a.object}")
    print(f"  rule: {r.rule_id} | {r.description}")
    print(f"  evidence: {a.evidence_id}")
    print(f"  provenance: {a.provenance}")
    print(f"  rule_exclusions: {r.exclusions}")
    print()
