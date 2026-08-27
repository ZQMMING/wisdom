#!/usr/bin/env python3
"""Generate Heluo/Yijing assertion rules from classical references."""
import json
from pathlib import Path
from datetime import datetime, timezone

rules_dir = Path("data/rules")
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

rules = []

# === HL-106~110: 五行不及健康风险 ===
wuxing_health = [
    ("金", "肺/大肠", "HL-106", "DECISION-106"),
    ("木", "肝/胆", "HL-107", "DECISION-107"),
    ("水", "肾/膀胱", "HL-108", "DECISION-108"),
    ("火", "心/小肠", "HL-109", "DECISION-109"),
    ("土", "脾胃", "HL-110", "DECISION-110"),
]
for elem, organ, rid, dec in wuxing_health:
    rules.append({
        "rule_id": rid,
        "title": f"本命卦五行{elem}不及 → {organ}健康风险",
        "rule_type": "健康断事",
        "source": {
            "work": "河洛真数",
            "chapter": "八卦五行归属",
            "location": f"{elem}不及→{organ}"
        },
        "conditions": {
            "all": [
                {"field": "heluo_benming_guawuxing", "op": "eq", "value": elem},
                {"field": "heluo_wuxing_imbalance", "op": "eq", "value": "under"}
            ]
        },
        "conclusion": {
            "rationale_classical": f"本命卦五行{elem}不及，{organ}之气不足，易虚损。",
            "produces_layer_output_template": {
                "direction": "DECLINE",
                "polarity": "caution",
                "health_organ": organ
            }
        },
        "applies_to_layers": ["EVENT_TOPIC"],
        "produces_signal_type": "HEALTH_RISK",
        "forbidden_inferences": [],
        "status": "draft",
        "version": "0.1.0",
        "book_id": "HELUO-LISHU",
        "spec_decisions_ref": [dec],
        "evidence_refs": ["E-K2G-SHIPI-000"],
        "created_at": now
    })

# === HL-111: 河洛数凶判定 ===
rules.append({
    "rule_id": "HL-111",
    "title": "地数有余+生于不利时节 → 数凶（流年卦凶爻应灾）",
    "rule_type": "应期断事",
    "source": {
        "work": "河洛真数",
        "chapter": "天地数吉凶",
        "location": "地数有余·谷雨到芒种不可妄行致凶"
    },
    "conditions": {
        "all": [
            {"field": "heluo_dishu_youyu", "op": "eq", "value": True},
            {"field": "heluo_birth_season_unfavorable", "op": "eq", "value": True}
        ]
    },
    "conclusion": {
        "rationale_classical": "地数有余为凶数，生于谷雨到芒种之候不可妄行，数凶者流年卦逢凶爻应灾。",
        "produces_layer_output_template": {
            "direction": "DECLINE",
            "polarity": "danger",
            "note": "数凶基础，需结合流年卦动爻爻辞定具体应期"
        }
    },
    "applies_to_layers": ["EVENT_TOPIC"],
    "produces_signal_type": "DANGER",
    "forbidden_inferences": ["不可单独断死亡，必须流年卦+流月卦逐层定位"],
    "status": "draft",
    "version": "0.1.0",
    "book_id": "HELUO-LISHU",
    "spec_decisions_ref": ["DECISION-111"],
    "evidence_refs": ["E-HELUO-CASE-LUMOU"],
    "created_at": now
})

# === HL-112~119: 八卦宫位领域基调 ===
gong_domains = [
    ("坎", "事业、财运", "HL-112", "DECISION-112"),
    ("离", "情感、桃花", "HL-113", "DECISION-113"),
    ("震", "学业、考试", "HL-114", "DECISION-114"),
    ("坤", "家庭、健康", "HL-115", "DECISION-115"),
    ("巽", "贵人、助运", "HL-116", "DECISION-116"),
    ("艮", "人际、合作", "HL-117", "DECISION-117"),
    ("兑", "财运、口舌", "HL-118", "DECISION-118"),
    ("乾", "事业、官贵", "HL-119", "DECISION-119"),
]
for trigram, domain, rid, dec in gong_domains:
    rules.append({
        "rule_id": rid,
        "title": f"本命卦{trigram}宫 → 关注{domain}领域",
        "rule_type": "领域定位",
        "source": {
            "work": "河洛理数·现代解读",
            "chapter": "各宫位代表领域",
            "location": f"{trigram}宫→{domain}"
        },
        "conditions": {
            "all": [
                {"field": "heluo_benming_gong", "op": "eq", "value": trigram}
            ]
        },
        "conclusion": {
            "rationale_classical": f"河洛定象：{trigram}宫主{domain}，本命卦落此宫则人生重点在此领域。",
            "produces_layer_output_template": {
                "direction": "STABLE",
                "polarity": "neutral",
                "focus_domain": domain
            }
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "DOMAIN_FOCUS",
        "forbidden_inferences": [],
        "status": "draft",
        "version": "0.1.0",
        "book_id": "HELUO-LISHU",
        "spec_decisions_ref": [dec],
        "evidence_refs": ["E-HELUO-GONG-DOMAIN"],
        "created_at": now
    })

# Write all rules
for r in rules:
    fpath = rules_dir / f"{r['rule_id']}.json"
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    print(f"Created {fpath}")

print(f"\nTotal: {len(rules)} rules created")
