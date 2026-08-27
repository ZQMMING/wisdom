#!/usr/bin/env python3
"""
A2-B4 Blind Eligibility Assessment
根据 Oracle Type + Temporal Relation 确定 Blind Eligibility

核心原则：
- O1 + PRE_EVENT → BLIND_ELIGIBLE (可进入预测准确率验证)
- O2 + POST_HOC → EVIDENCE_ONLY (仅作为历史证据)
- OX → NOT_QUALIFIED (静态特征，不可验证)
- THIRD_PARTY provenance → EVIDENCE_ONLY (非官方答案)
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter

BASE_DIR = Path(__file__).parent.parent
PILOT_PATH = BASE_DIR / "dataset/accuracy/pilot/pilot_dataset.json"
HISTORICAL_PATH = BASE_DIR / "dataset/accuracy/historical/historical_dataset_audited.json"
OUTPUT_DIR = BASE_DIR / "dataset/accuracy/blind"
EVIDENCE_DIR = BASE_DIR / "dataset/accuracy/evidence_only"


def infer_temporal_relation(event: dict) -> str:
    """
    推断事件的 temporal_relation
    
    Pilot 数据（fate-bench）特点：
    - 问题问的是"某年发生了什么"
    - 答案是官方在比赛前确定的
    - 参赛者在比赛前无法知道答案
    - 这是一个真正的预测场景 → PRE_EVENT
    
    Historical 数据特点：
    - 历史记录，已经发生
    - 但相对于 prediction_cutoff 可能是 PRE_EVENT
    """
    source_dataset = event.get('source_dataset', 'UNKNOWN')
    
    # Pilot data: fate-bench competition questions
    # These are prediction scenarios where answers were determined before the competition
    if source_dataset == 'PILOT':
        # Check if it's a static trait question (OX)
        oracle_grade = event.get('oracle_grade', 'UNKNOWN')
        if oracle_grade == 'OX':
            return 'UNKNOWN'
        
        # All other Pilot events are prediction scenarios
        return 'PRE_EVENT'
    
    # Historical data: use post_hoc_status if available
    if source_dataset == 'HISTORICAL':
        return event.get('post_hoc_status', 'UNKNOWN')
    
    return 'UNKNOWN'


def assess_blind_eligibility(event: dict) -> dict:
    """
    评估单个事件的 Blind Eligibility
    
    返回:
    {
        "oracle_type": "O1" | "O2" | "OX",
        "temporal_relation": "PRE_EVENT" | "POST_HOC" | "UNKNOWN",
        "blind_eligibility": "BLIND_ELIGIBLE" | "EVIDENCE_ONLY" | "NOT_QUALIFIED" | "REJECTED",
        "exclusion_reason": str | None
    }
    """
    oracle_type = event.get("oracle_grade", "UNKNOWN")
    provenance = event.get("provenance", "UNKNOWN")
    
    # Infer temporal relation
    temporal_relation = infer_temporal_relation(event)
    
    leakage_class = event.get("leakage_class", "UNKNOWN")
    
    # B4.7: Leakage check
    if leakage_class not in ("CLEAN", "REVIEWED"):
        return {
            "oracle_type": oracle_type,
            "temporal_relation": temporal_relation,
            "blind_eligibility": "REJECTED",
            "exclusion_reason": f"Leakage detected: {leakage_class}"
        }
    
    # OX events are static traits, not evaluable
    if oracle_type == "OX":
        return {
            "oracle_type": oracle_type,
            "temporal_relation": temporal_relation,
            "blind_eligibility": "NOT_QUALIFIED",
            "exclusion_reason": "Static trait (OX), not time-based event"
        }
    
    # THIRD_PARTY provenance → EVIDENCE_ONLY
    if provenance == "THIRD_PARTY":
        return {
            "oracle_type": oracle_type,
            "temporal_relation": temporal_relation,
            "blind_eligibility": "EVIDENCE_ONLY",
            "exclusion_reason": "Third-party provenance, not official answer"
        }
    
    # O2 events (historical records) → EVIDENCE_ONLY
    if oracle_type == "O2":
        return {
            "oracle_type": oracle_type,
            "temporal_relation": temporal_relation,
            "blind_eligibility": "EVIDENCE_ONLY",
            "exclusion_reason": "Historical record (O2), not prediction oracle"
        }
    
    # O1 events with PRE_EVENT → BLIND_ELIGIBLE
    if oracle_type == "O1" and temporal_relation == "PRE_EVENT":
        return {
            "oracle_type": oracle_type,
            "temporal_relation": temporal_relation,
            "blind_eligibility": "BLIND_ELIGIBLE",
            "exclusion_reason": None
        }
    
    # O1 events with POST_HOC → EVIDENCE_ONLY
    if oracle_type == "O1" and temporal_relation == "POST_HOC":
        return {
            "oracle_type": oracle_type,
            "temporal_relation": temporal_relation,
            "blind_eligibility": "EVIDENCE_ONLY",
            "exclusion_reason": "POST_HOC event, cannot use for prediction validation"
        }
    
    # Default: NOT_QUALIFIED
    return {
        "oracle_type": oracle_type,
        "temporal_relation": temporal_relation,
        "blind_eligibility": "NOT_QUALIFIED",
        "exclusion_reason": f"Unknown combination: oracle={oracle_type}, temporal={temporal_relation}"
    }


def run_b4_assessment():
    """执行 A2-B4 Blind Eligibility 评估"""
    print("=" * 60)
    print("A2-B4 Blind Eligibility Assessment")
    print("=" * 60)
    
    # Step 1: Load datasets
    print("\n[1/5] Loading datasets...")
    with open(PILOT_PATH, 'r', encoding='utf-8') as f:
        pilot_data = json.load(f)
    
    with open(HISTORICAL_PATH, 'r', encoding='utf-8') as f:
        hist_data = json.load(f)
    
    print(f"  Pilot: {len(pilot_data['persons'])} persons")
    print(f"  Historical: {len(hist_data['persons'])} persons")
    
    # Step 2: Assess all events
    print("\n[2/5] Assessing blind eligibility...")
    
    blind_candidates = []
    evidence_only = []
    excluded_events = []
    
    # Process Pilot events
    for person in pilot_data['persons']:
        for event in person['events']:
            event['source_dataset'] = 'PILOT'
            event['person_id'] = person['person_id']
            
            assessment = assess_blind_eligibility(event)
            event['oracle_type'] = assessment['oracle_type']
            event['temporal_relation'] = assessment['temporal_relation']
            event['blind_eligibility'] = assessment['blind_eligibility']
            event['exclusion_reason'] = assessment['exclusion_reason']
            
            if assessment['blind_eligibility'] == 'BLIND_ELIGIBLE':
                blind_candidates.append(event)
            elif assessment['blind_eligibility'] == 'EVIDENCE_ONLY':
                evidence_only.append(event)
            else:
                excluded_events.append(event)
    
    # Process Historical events
    for person in hist_data['persons']:
        for event in person['events']:
            event['source_dataset'] = 'HISTORICAL'
            event['person_id'] = person['person_id']
            
            assessment = assess_blind_eligibility(event)
            event['oracle_type'] = assessment['oracle_type']
            event['temporal_relation'] = assessment['temporal_relation']
            event['blind_eligibility'] = assessment['blind_eligibility']
            event['exclusion_reason'] = assessment['exclusion_reason']
            
            if assessment['blind_eligibility'] == 'BLIND_ELIGIBLE':
                blind_candidates.append(event)
            elif assessment['blind_eligibility'] == 'EVIDENCE_ONLY':
                evidence_only.append(event)
            else:
                excluded_events.append(event)
    
    print(f"  BLIND_ELIGIBLE: {len(blind_candidates)}")
    print(f"  EVIDENCE_ONLY: {len(evidence_only)}")
    print(f"  EXCLUDED: {len(excluded_events)}")
    
    # Step 3: Generate statistics
    print("\n[3/5] Generating statistics...")
    
    stats = {
        "total_events": len(blind_candidates) + len(evidence_only) + len(excluded_events),
        "blind_eligible": len(blind_candidates),
        "evidence_only": len(evidence_only),
        "excluded": len(excluded_events),
        "by_dataset": {
            "PILOT": {
                "blind": sum(1 for e in blind_candidates if e['source_dataset'] == 'PILOT'),
                "evidence": sum(1 for e in evidence_only if e['source_dataset'] == 'PILOT'),
                "excluded": sum(1 for e in excluded_events if e['source_dataset'] == 'PILOT'),
            },
            "HISTORICAL": {
                "blind": sum(1 for e in blind_candidates if e['source_dataset'] == 'HISTORICAL'),
                "evidence": sum(1 for e in evidence_only if e['source_dataset'] == 'HISTORICAL'),
                "excluded": sum(1 for e in excluded_events if e['source_dataset'] == 'HISTORICAL'),
            }
        },
        "by_oracle_type": {
            "O1": sum(1 for e in blind_candidates + evidence_only + excluded_events if e.get('oracle_type') == 'O1'),
            "O2": sum(1 for e in blind_candidates + evidence_only + excluded_events if e.get('oracle_type') == 'O2'),
            "OX": sum(1 for e in blind_candidates + evidence_only + excluded_events if e.get('oracle_type') == 'OX'),
        },
        "by_event_type": dict(Counter(e.get('event_type', 'UNKNOWN') for e in blind_candidates)),
        "exclusion_reasons": dict(Counter(e.get('exclusion_reason', 'UNKNOWN') for e in excluded_events)),
    }
    
    # Step 4: Save outputs
    print("\n[4/5] Saving outputs...")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Blind candidates
    blind_output = {
        "metadata": {
            "version": "A2-B4-Blind-v1.0",
            "created_at": datetime.now().isoformat(),
            "total_events": len(blind_candidates),
            "criteria": "O1 + PRE_EVENT + OFFICIAL provenance + CLEAN leakage"
        },
        "events": blind_candidates,
        "statistics": stats
    }
    
    with open(OUTPUT_DIR / "blind_candidates.json", 'w', encoding='utf-8') as f:
        json.dump(blind_output, f, ensure_ascii=False, indent=2)
    
    # Evidence only
    evidence_output = {
        "metadata": {
            "version": "A2-B4-Evidence-v1.0",
            "created_at": datetime.now().isoformat(),
            "total_events": len(evidence_only),
            "criteria": "O2 (historical records) or THIRD_PARTY provenance"
        },
        "events": evidence_only
    }
    
    with open(EVIDENCE_DIR / "historical_evidence.json", 'w', encoding='utf-8') as f:
        json.dump(evidence_output, f, ensure_ascii=False, indent=2)
    
    # Excluded events
    excluded_output = {
        "metadata": {
            "version": "A2-B4-Excluded-v1.0",
            "created_at": datetime.now().isoformat(),
            "total_events": len(excluded_events)
        },
        "events": excluded_events
    }
    
    with open(OUTPUT_DIR / "excluded_events.json", 'w', encoding='utf-8') as f:
        json.dump(excluded_output, f, ensure_ascii=False, indent=2)
    
    # Manifest
    manifest = {
        "metadata": {
            "version": "A2-B4-Manifest-v1.0",
            "created_at": datetime.now().isoformat(),
            "assessment_date": datetime.now().isoformat()
        },
        "summary": {
            "total_events_assessed": stats['total_events'],
            "blind_eligible": stats['blind_eligible'],
            "evidence_only": stats['evidence_only'],
            "excluded": stats['excluded'],
            "blind_rate": f"{stats['blind_eligible'] / stats['total_events'] * 100:.1f}%"
        },
        "by_dataset": stats['by_dataset'],
        "by_oracle_type": stats['by_oracle_type'],
        "by_event_type": stats['by_event_type'],
        "exclusion_reasons": stats['exclusion_reasons'],
        "files": {
            "blind_candidates": str(OUTPUT_DIR / "blind_candidates.json"),
            "historical_evidence": str(EVIDENCE_DIR / "historical_evidence.json"),
            "excluded_events": str(OUTPUT_DIR / "excluded_events.json")
        }
    }
    
    with open(OUTPUT_DIR / "blind_manifest.json", 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print(f"  Saved: {OUTPUT_DIR / 'blind_candidates.json'}")
    print(f"  Saved: {EVIDENCE_DIR / 'historical_evidence.json'}")
    print(f"  Saved: {OUTPUT_DIR / 'excluded_events.json'}")
    print(f"  Saved: {OUTPUT_DIR / 'blind_manifest.json'}")
    
    # Step 5: Summary
    print("\n[5/5] Summary")
    print(f"\n  Total Events Assessed: {stats['total_events']}")
    print(f"  BLIND_ELIGIBLE: {stats['blind_eligible']} ({stats['blind_eligible'] / stats['total_events'] * 100:.1f}%)")
    print(f"  EVIDENCE_ONLY: {stats['evidence_only']} ({stats['evidence_only'] / stats['total_events'] * 100:.1f}%)")
    print(f"  EXCLUDED: {stats['excluded']} ({stats['excluded'] / stats['total_events'] * 100:.1f}%)")
    
    print("\n  By Dataset:")
    for dataset, counts in stats['by_dataset'].items():
        print(f"    {dataset}: blind={counts['blind']}, evidence={counts['evidence']}, excluded={counts['excluded']}")
    
    print("\n  By Oracle Type:")
    for oracle, count in stats['by_oracle_type'].items():
        print(f"    {oracle}: {count}")
    
    print("\n  Top Exclusion Reasons:")
    for reason, count in sorted(stats['exclusion_reasons'].items(), key=lambda x: -x[1])[:5]:
        print(f"    {reason}: {count}")
    
    print("=" * 60)
    
    return manifest


if __name__ == "__main__":
    run_b4_assessment()
