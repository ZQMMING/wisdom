"""P6-B A-only样本逐条审计.

对160条A-only样本(A=MAPPABLE/supportive, B=UNMAPPABLE/DIRECTION_UNCLEAR)
逐条分类:
- A_CORRECT_B_TOO_STRICT: A正确, B过严 (事件明确支持supportive)
- A_TOO_LIBERAL_B_CORRECT: A过宽, B正确 (事件实际是caution或方向不明确)
- NEED_ARBITRATION: 确实需要第三方仲裁

审计规则:
EXAM类:
- 明确成功词(中/登/及第/进士/举人/状元/榜眼/探花/登第) → A_CORRECT
- 明确失败词(落/不中/下第/不第/罢/黜/不第) → A_TOO_LIBERAL (应为caution)
- 中性词(开始读书/启蒙/童试/应试/入学/读书) → NEED_ARBITRATION (应为neutral)

JOB_CHANGE类:
- 明确获得职位(任/授/除/拜/补/选/召/征/起/入/升/迁/擢) → A_CORRECT
- 明确降职(贬/谪/降/罢/免/黜/外放/左迁) → A_TOO_LIBERAL (应为caution)
- 中性/主动离职(辞官/归隐/致仕/乞休/解职/退) → NEED_ARBITRATION (应为neutral)
"""
from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
sys.path.insert(0, "src")

from p6b_annotation_contract import load_annotation_table


# 明确成功词
EXAM_SUCCESS = ["中", "登", "及第", "进士", "举人", "状元", "榜眼", "探花", "登第", "解元", "会元", "传胪", "翰林"]
# 明确失败词
EXAM_FAIL = ["落", "不中", "下第", "不第", "罢", "黜", "不售", "落第", "报罢"]
# 中性词
EXAM_NEUTRAL = ["读书", "启蒙", "童试", "应试", "入学", "就试", "赴试", "考", "考中", "考进士", "考举人", "县试", "府试", "院试", "乡试", "会试", "殿试"]

# 明确获得职位
JOB_GAIN = ["任", "授", "除", "拜", "补", "选", "召", "征", "起", "入", "升", "迁", "擢", "晋", "进", "为", "知", "署", "摄", "判", "守", "令", "丞", "簿", "尉", "参军", "主事", "编修", "检讨", "修撰", "侍读", "侍讲", "学士", "大学士", "尚书", "侍郎", "总督", "巡抚", "御史", "给事中", "郎中", "员外郎", "知府", "知州", "知县", "总纂", "编纂"]
# 明确降职
JOB_LOSE = ["贬", "谪", "降", "罢", "免", "黜", "外放", "左迁", "革职", "撤职", "查办", "议处", "罚俸", "降级"]
# 中性/主动离职
JOB_NEUTRAL = ["辞官", "归隐", "致仕", "乞休", "解职", "退", "归田", "还乡", "回籍", "丁忧", "守制", "终养", "养病", "省亲", "开缺", "告归", "拂袖", "挂冠"]


def classify_exam(description: str) -> tuple[str, str]:
    """分类EXAM事件. 返回(分类, 建议direction)."""
    desc = description

    # 先检查明确失败
    for word in EXAM_FAIL:
        if word in desc:
            return "A_TOO_LIBERAL_B_CORRECT", "caution"

    # 再检查明确成功
    for word in EXAM_SUCCESS:
        if word in desc:
            return "A_CORRECT_B_TOO_STRICT", "supportive"

    # 中性词
    for word in EXAM_NEUTRAL:
        if word in desc:
            return "NEED_ARBITRATION", "neutral"

    # 默认: 需要仲裁
    return "NEED_ARBITRATION", "neutral"


def classify_job_change(description: str) -> tuple[str, str]:
    """分类JOB_CHANGE事件. 返回(分类, 建议direction)."""
    desc = description

    # 先检查明确降职
    for word in JOB_LOSE:
        if word in desc:
            return "A_TOO_LIBERAL_B_CORRECT", "caution"

    # 再检查中性/主动离职
    for word in JOB_NEUTRAL:
        if word in desc:
            return "NEED_ARBITRATION", "neutral"

    # 最后检查明确获得职位
    for word in JOB_GAIN:
        if word in desc:
            return "A_CORRECT_B_TOO_STRICT", "supportive"

    # 默认: 需要仲裁
    return "NEED_ARBITRATION", "neutral"


def main():
    print("=" * 70)
    print("P6-B A-only样本逐条审计 (160条)")
    print("=" * 70)

    table_a = load_annotation_table("dataset/golden_v1/annotations_round_a.json")
    table_b = load_annotation_table("dataset/golden_v1/annotations_round_b.json")

    map_a = {e.event_id: e for e in table_a}
    map_b = {e.event_id: e for e in table_b}

    # 提取A-only
    a_only = []
    for eid in sorted(map_a.keys()):
        a = map_a[eid]
        b = map_b[eid]
        if not a.unmappable and b.unmappable:
            a_only.append((a, b))

    print(f"\nA-only样本数: {len(a_only)}")

    # 逐条审计
    audit_results = []
    classification_dist = Counter()
    suggested_dir_dist = Counter()
    category_dist = Counter()

    for a, b in a_only:
        cat = a.raw_event.get("category", "")
        desc = a.raw_event.get("description", "")

        if cat == "EXAM":
            classification, suggested_dir = classify_exam(desc)
        elif cat == "JOB_CHANGE":
            classification, suggested_dir = classify_job_change(desc)
        else:
            classification, suggested_dir = "NEED_ARBITRATION", "neutral"

        audit_results.append({
            "event_id": a.event_id,
            "case_id": a.case_id,
            "category": cat,
            "description": desc,
            "A_direction": a.direction,
            "B_unmappable_reason": b.unmappable_reason,
            "classification": classification,
            "suggested_direction": suggested_dir,
            "A_domain": a.domain,
            "A_semantic_family": a.semantic_family,
        })

        classification_dist[classification] += 1
        suggested_dir_dist[suggested_dir] += 1
        category_dist[cat] += 1

    print(f"\n=== 审计分类分布 ===")
    for cls, count in classification_dist.most_common():
        print(f"  {cls}: {count} ({count/len(a_only)*100:.1f}%)")

    print(f"\n=== 建议direction分布 ===")
    for d, count in suggested_dir_dist.most_common():
        print(f"  {d}: {count}")

    print(f"\n=== 按category分类 ===")
    for cat in category_dist:
        cat_results = [r for r in audit_results if r["category"] == cat]
        cat_class_dist = Counter(r["classification"] for r in cat_results)
        print(f"\n  {cat} ({len(cat_results)}条):")
        for cls, count in cat_class_dist.most_common():
            print(f"    {cls}: {count}")

    # 详细展示各类别示例
    print(f"\n=== A_TOO_LIBERAL_B_CORRECT 示例 (A过宽, B正确) ===")
    for r in [x for x in audit_results if x["classification"] == "A_TOO_LIBERAL_B_CORRECT"][:10]:
        print(f"  {r['event_id']}: {r['description']}")
        print(f"    A={r['A_direction']} 建议={r['suggested_direction']}")

    print(f"\n=== NEED_ARBITRATION 示例 (需仲裁, 建议neutral) ===")
    for r in [x for x in audit_results if x["classification"] == "NEED_ARBITRATION"][:10]:
        print(f"  {r['event_id']}: {r['description']}")
        print(f"    A={r['A_direction']} 建议={r['suggested_direction']}")

    print(f"\n=== A_CORRECT_B_TOO_STRICT 示例 (A正确, B过严) ===")
    for r in [x for x in audit_results if x["classification"] == "A_CORRECT_B_TOO_STRICT"][:10]:
        print(f"  {r['event_id']}: {r['description']}")
        print(f"    A={r['A_direction']} 建议={r['suggested_direction']}")

    # 保存审计结果
    with open("docs/audit/p6b_a_only_audit.json", "w", encoding="utf-8") as f:
        json.dump({
            "total": len(audit_results),
            "classification_dist": dict(classification_dist),
            "suggested_direction_dist": dict(suggested_dir_dist),
            "audit_results": audit_results,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n审计结果已保存: docs/audit/p6b_a_only_audit.json")

    # 统计: 修正后direction分布变化
    print(f"\n=== 修正前后direction对比 ===")
    original_dirs = Counter(r["A_direction"] for r in audit_results)
    corrected_dirs = Counter(r["suggested_direction"] for r in audit_results)
    print(f"  原始(A): {dict(original_dirs)}")
    print(f"  修正后: {dict(corrected_dirs)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
