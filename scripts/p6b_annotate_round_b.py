"""P6-B 第二轮盲标注 (Annotator B).

Annotator B特点: 更严格, 对模糊事件更倾向于UNMAPPABLE,
对direction判断更谨慎, 不假设默认成功.
"""
from __future__ import annotations
import json
import sys
sys.path.insert(0, "src")

from p6b_annotation_contract import (
    AnnotationEntry, extract_events_from_golden, save_annotation_table,
)


def annotate_event_b(event: dict) -> dict:
    """Annotator B的标注逻辑 - 更严格, 更谨慎."""
    raw = event["raw_event"]
    category = raw.get("category", "")
    description = raw.get("description", "")
    severity = raw.get("severity", 3)

    domain = None
    semantic_family = None
    direction = None
    unmappable = False
    unmappable_reason = None
    notes = ""

    if category == "EXAM":
        domain = "CAREER"
        semantic_family = "OUTPUT_EXPRESSION"
        # B更严格: 只有明确说"中/登/及第"才标supportive
        if any(k in description for k in ["中", "登", "及第", "进士", "举人", "状元", "榜眼", "探花", "登第"]):
            direction = "supportive"
            notes = "明确考试成功"
        elif any(k in description for k in ["落", "不中", "下第", "罢", "黜", "不第"]):
            direction = "caution"
            notes = "明确考试失败"
        else:
            # B更谨慎: 描述不明确时标neutral而不是默认成功
            direction = "neutral"
            unmappable = True
            unmappable_reason = "DIRECTION_UNCLEAR"
            notes = "考试事件但方向不明确"

    elif category == "CHILD_BIRTH":
        domain = "FAMILY"
        semantic_family = "STABILITY_SUPPORT"
        direction = "neutral"
        notes = "出生事件, 中性"

    elif category == "PARENT_DEATH":
        domain = "FAMILY"
        semantic_family = "CHANGE_TRANSFORMATION"
        direction = "caution"
        if any(k in description for k in ["父", "母", "丁忧", "丧父", "丧母"]):
            notes = "父母去世/丁忧"
        elif any(k in description for k in ["妻", "夫人"]):
            domain = "RELATIONSHIP"
            notes = "配偶去世"
        else:
            notes = "去世/丧亲"

    elif category == "JOB_CHANGE":
        domain = "CAREER"
        semantic_family = "CHANGE_TRANSFORMATION"
        if any(k in description for k in ["贬", "谪", "降", "罢", "免", "黜", "外放", "左迁"]):
            direction = "caution"
            notes = "明确贬谪/降职"
        elif any(k in description for k in ["任", "授", "除", "拜", "补", "选", "召", "征", "起", "入"]):
            direction = "supportive"
            notes = "明确获得职位"
        else:
            # B更谨慎
            direction = "neutral"
            unmappable = True
            unmappable_reason = "DIRECTION_UNCLEAR"
            notes = "工作变动但方向不明确"

    elif category == "PROMOTION":
        domain = "CAREER"
        semantic_family = "STABILITY_SUPPORT"
        # PROMOTION本身就是升迁, 但B检查是否有负面词
        if any(k in description for k in ["贬", "降", "罢", "免"]):
            direction = "caution"
            notes = "名义升迁实际降职"
        else:
            direction = "supportive"
            notes = "升迁/晋升"

    elif category == "FAMILY_CHANGE":
        # B对FAMILY_CHANGE更严格, 更多UNMAPPABLE
        if any(k in description for k in ["案", "狱", "贬", "谪", "乱", "变", "祸", "难", "灾", "囚", "流放", "文字狱"]):
            domain = "CAREER"
            semantic_family = "CHANGE_TRANSFORMATION"
            direction = "caution"
            notes = "政治事件/灾祸"
        elif any(k in description for k in ["婚", "娶", "嫁", "纳妾"]):
            domain = "RELATIONSHIP"
            semantic_family = "RELATION_CONNECTION"
            direction = "supportive"
            notes = "婚姻"
        elif any(k in description for k in ["丧", "死", "卒", "殁", "亡"]):
            domain = "FAMILY"
            semantic_family = "CHANGE_TRANSFORMATION"
            direction = "caution"
            notes = "家人去世"
        elif any(k in description for k in ["生", "育", "得子", "生子"]):
            domain = "FAMILY"
            semantic_family = "STABILITY_SUPPORT"
            direction = "supportive"
            notes = "生育"
        else:
            unmappable = True
            unmappable_reason = "EVENT_TOO_VAGUE"
            notes = f"FAMILY_CHANGE模糊: {description}"

    elif category == "NEW_RELATIONSHIP":
        domain = "RELATIONSHIP"
        semantic_family = "RELATION_CONNECTION"
        if any(k in description for k in ["婚", "娶", "嫁"]):
            direction = "supportive"
            notes = "结婚"
        else:
            direction = "neutral"
            unmappable = True
            unmappable_reason = "DIRECTION_UNCLEAR"
            notes = "新关系但方向不明确"

    elif category == "RELOCATION":
        domain = "MIGRATION"
        semantic_family = "CHANGE_TRANSFORMATION"
        if any(k in description for k in ["贬", "谪", "流放"]):
            direction = "caution"
            notes = "贬谪/流放"
        elif any(k in description for k in ["购", "买", "置"]):
            direction = "supportive"
            notes = "购房/置业"
        elif any(k in description for k in ["迁居", "移居", "归隐", "隐居", "去", "离"]):
            direction = "neutral"
            notes = "迁居/归隐/出行"
        else:
            direction = "neutral"
            notes = "迁移"

    elif category == "MAJOR_INCOME":
        if any(k in description for k in ["著", "写", "作", "诗", "文", "书", "画", "集", "赋", "记", "序", "论"]):
            domain = "GROWTH"
            semantic_family = "OUTPUT_EXPRESSION"
            direction = "supportive"
            notes = "重要作品"
        elif any(k in description for k in ["银", "金", "钱", "财", "禄", "俸", "赏", "赐"]):
            domain = "FINANCE"
            semantic_family = "RESOURCE_WEALTH"
            direction = "supportive"
            notes = "重要收入"
        else:
            domain = "GROWTH"
            semantic_family = "OUTPUT_EXPRESSION"
            direction = "supportive"
            notes = "重要成就"

    elif category == "RESIGNATION":
        domain = "CAREER"
        semantic_family = "CHANGE_TRANSFORMATION"
        if any(k in description for k in ["辞", "退", "归", "隐", "致仕", "乞休", "解职", "禅"]):
            direction = "neutral"
            notes = "主动辞职/退位"
        elif any(k in description for k in ["罢", "免", "黜", "废"]):
            direction = "caution"
            notes = "被迫罢免"
        else:
            direction = "neutral"
            notes = "辞职"

    else:
        unmappable = True
        unmappable_reason = "OUTSIDE_VOCABULARY"
        notes = f"未知category: {category}"

    return {
        "domain": domain,
        "semantic_family": semantic_family,
        "direction": direction,
        "unmappable": unmappable,
        "unmappable_reason": unmappable_reason,
        "notes": notes,
    }


def main():
    print("=" * 60)
    print("P6-B 第二轮盲标注 (Annotator B - 更严格)")
    print("=" * 60)

    events = extract_events_from_golden("dataset/golden_v1/golden_cases.json")
    print(f"\n提取事件数: {len(events)}")

    annotations = []
    unmappable_count = 0
    domain_dist = {}
    family_dist = {}
    direction_dist = {}

    for ev in events:
        result = annotate_event_b(ev)
        entry = AnnotationEntry(
            event_id=ev["event_id"],
            case_id=ev["case_id"],
            target_year=ev["target_year"],
            raw_event=ev["raw_event"],
            domain=result["domain"],
            semantic_family=result["semantic_family"],
            direction=result["direction"],
            unmappable=result["unmappable"],
            unmappable_reason=result["unmappable_reason"],
            annotator="ANNOTATOR_B",
            annotation_round="ROUND_B",
            annotation_notes=result["notes"],
        )
        annotations.append(entry)

        if result["unmappable"]:
            unmappable_count += 1
        else:
            domain_dist[result["domain"]] = domain_dist.get(result["domain"], 0) + 1
            family_dist[result["semantic_family"]] = family_dist.get(result["semantic_family"], 0) + 1
            direction_dist[result["direction"]] = direction_dist.get(result["direction"], 0) + 1

    errors = []
    for a in annotations:
        errors.extend(a.validate())

    output_path = "dataset/golden_v1/annotations_round_b.json"
    save_annotation_table(annotations, output_path)

    print(f"\n标注完成: {len(annotations)} 条")
    print(f"可映射: {len(annotations) - unmappable_count} ({(len(annotations)-unmappable_count)/len(annotations)*100:.1f}%)")
    print(f"UNMAPPABLE: {unmappable_count} ({unmappable_count/len(annotations)*100:.1f}%)")
    print(f"验证错误: {len(errors)}")

    print(f"\nDomain分布:")
    for d, c in sorted(domain_dist.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
    print(f"\nDirection分布:")
    for d, c in sorted(direction_dist.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
    print(f"\n已保存: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
