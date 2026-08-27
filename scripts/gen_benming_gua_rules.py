#!/usr/bin/env python3
"""Generate Heluo benming gua assertion rules with classical basis."""
import json
from pathlib import Path
from datetime import datetime, timezone

rules_dir = Path("data/rules")
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

rules = [
    {
        "rule_id": "HL-120",
        "title": "本命卦乾为天 → 刚健中正，主事业官贵（生于四月/纳甲本命者富贵）",
        "rule_type": "体用辨析",
        "source": {
            "work": "河洛真数",
            "chapter": "乾为天卦解",
            "location": "卦属四月，纳甲甲子甲寅甲辰壬午壬申壬戌，金秋旺"
        },
        "conditions": {
            "all": [
                {"field": "heluo_benming_guaming", "op": "eq", "value": "乾为天"}
            ]
        },
        "conclusion": {
            "rationale_classical": "本命乾为天，三爻皆阳，刚健中正，主事业官贵。卦属四月，纳甲本命者富贵；乾金秋旺，不及时不纳甲者需后天努力。",
            "produces_layer_output_template": {
                "direction": "INCREASE",
                "polarity": "active"
            }
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "OUTPUT",
        "forbidden_inferences": [],
        "status": "draft",
        "version": "0.1.0",
        "book_id": "HELUO-LISHU",
        "spec_decisions_ref": ["DECISION-120"],
        "evidence_refs": ["E-K2G-SHIPI-000"],
        "created_at": now
    },
    {
        "rule_id": "HL-121",
        "title": "本命卦地天泰 → 天地交泰，主通达顺利（六爻皆宜固定，不可轻进）",
        "rule_type": "体用辨析",
        "source": {
            "work": "河洛真数",
            "chapter": "地天泰卦解",
            "location": "坤宫三世卦，属正月，纳甲甲子甲寅甲辰癸丑癸亥癸酉"
        },
        "conditions": {
            "all": [
                {"field": "heluo_benming_guaming", "op": "eq", "value": "地天泰"}
            ]
        },
        "conclusion": {
            "rationale_classical": "本命地天泰，天地交泰，主通达顺利。坤宫三世卦，属正月，六爻皆宜固定，不可轻进妄动，守正则吉。",
            "produces_layer_output_template": {
                "direction": "INCREASE",
                "polarity": "active"
            }
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "OUTPUT",
        "forbidden_inferences": [],
        "status": "draft",
        "version": "0.1.0",
        "book_id": "HELUO-LISHU",
        "spec_decisions_ref": ["DECISION-121"],
        "evidence_refs": ["E-K2G-SHIPI-000"],
        "created_at": now
    },
]

for r in rules:
    fpath = rules_dir / f"{r['rule_id']}.json"
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    print(f"Created {fpath}")

print(f"\nTotal: {len(rules)} rules created")
