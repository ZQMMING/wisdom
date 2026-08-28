"""P6-B Ground Truth Quality Review.

审计160条A-only (A=MAPPABLE, B=UNMAPPABLE) 和2条双标注不一致.
逐条分类: A正确/B过严, A过宽/B正确, 需第三方仲裁.
"""
from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
sys.path.insert(0, "src")

from p6b_annotation_contract import load_annotation_table


def main():
    print("=" * 70)
    print("P6-B Ground Truth Quality Review")
    print("=" * 70)

    table_a = load_annotation_table("dataset/golden_v1/annotations_round_a.json")
    table_b = load_annotation_table("dataset/golden_v1/annotations_round_b.json")

    map_a = {e.event_id: e for e in table_a}
    map_b = {e.event_id: e for e in table_b}

    # 分类
    a_only = []  # A=mappable, B=unmappable
    b_only = []  # A=unmappable, B=mappable
    both_mappable_disagree = []
    both_mappable_agree = []
    both_unmappable = []

    for eid in sorted(map_a.keys()):
        a = map_a[eid]
        b = map_b[eid]

        if not a.unmappable and b.unmappable:
            a_only.append((a, b))
        elif a.unmappable and not b.unmappable:
            b_only.append((a, b))
        elif not a.unmappable and not b.unmappable:
            agree = (a.domain == b.domain and
                     a.semantic_family == b.semantic_family and
                     a.direction == b.direction)
            if agree:
                both_mappable_agree.append((a, b))
            else:
                both_mappable_disagree.append((a, b))
        else:
            both_unmappable.append((a, b))

    print(f"\n=== 样本分类 ===")
    print(f"  双标注一致: {len(both_mappable_agree)}")
    print(f"  双标注不一致: {len(both_mappable_disagree)}")
    print(f"  A-only (A可映射, B不可映射): {len(a_only)}")
    print(f"  B-only (A不可映射, B可映射): {len(b_only)}")
    print(f"  双标注UNMAPPABLE: {len(both_unmappable)}")
    print(f"  总计: {len(both_mappable_agree) + len(both_mappable_disagree) + len(a_only) + len(b_only) + len(both_unmappable)}")

    # A-only按category分布
    print(f"\n=== A-only样本按category分布 ({len(a_only)}条) ===")
    cat_dist = Counter()
    cat_examples = defaultdict(list)
    for a, b in a_only:
        cat = a.raw_event.get("category", "UNKNOWN")
        cat_dist[cat] += 1
        if len(cat_examples[cat]) < 5:
            cat_examples[cat].append({
                "event_id": a.event_id,
                "description": a.raw_event.get("description", ""),
                "A": f"{a.domain}/{a.semantic_family}/{a.direction}",
                "B_reason": b.unmappable_reason,
                "B_notes": b.annotation_notes,
            })

    for cat, count in cat_dist.most_common():
        print(f"\n  {cat}: {count}条")
        for ex in cat_examples[cat][:3]:
            print(f"    - {ex['event_id']}: {ex['description'][:40]}")
            print(f"      A={ex['A']}  B=UNMAPPABLE({ex['B_reason']})")

    # 双标注不一致
    print(f"\n=== 双标注不一致 ({len(both_mappable_disagree)}条) ===")
    for a, b in both_mappable_disagree:
        print(f"  {a.event_id}: {a.raw_event.get('description', '')}")
        print(f"    A={a.domain}/{a.semantic_family}/{a.direction}")
        print(f"    B={b.domain}/{b.semantic_family}/{b.direction}")
        print(f"    A_notes: {a.annotation_notes}")
        print(f"    B_notes: {b.annotation_notes}")

    # A-only按B的unmappable_reason分布
    print(f"\n=== A-only中B的UNMAPPABLE原因分布 ===")
    reason_dist = Counter()
    for a, b in a_only:
        reason_dist[b.unmappable_reason] += 1
    for reason, count in reason_dist.most_common():
        print(f"  {reason}: {count}")

    # A-only中A的direction分布
    print(f"\n=== A-only中A的direction分布 ===")
    dir_dist = Counter()
    for a, b in a_only:
        dir_dist[a.direction] += 1
    for d, c in dir_dist.most_common():
        print(f"  {d}: {c}")

    # 保存审计数据
    audit_data = {
        "classification": {
            "both_mappable_agree": len(both_mappable_agree),
            "both_mappable_disagree": len(both_mappable_disagree),
            "a_only": len(a_only),
            "b_only": len(b_only),
            "both_unmappable": len(both_unmappable),
        },
        "a_only_by_category": dict(cat_dist),
        "a_only_b_reasons": dict(reason_dist),
        "a_only_a_directions": dict(dir_dist),
        "disagreements": [
            {
                "event_id": a.event_id,
                "description": a.raw_event.get("description", ""),
                "A": f"{a.domain}/{a.semantic_family}/{a.direction}",
                "B": f"{b.domain}/{b.semantic_family}/{b.direction}",
            }
            for a, b in both_mappable_disagree
        ],
    }

    with open("docs/audit/p6b_quality_review.json", "w", encoding="utf-8") as f:
        json.dump(audit_data, f, ensure_ascii=False, indent=2)

    print(f"\n审计数据已保存: docs/audit/p6b_quality_review.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
