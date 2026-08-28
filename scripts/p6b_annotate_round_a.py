"""P6-B 第一轮盲标注 (Annotator A).

盲标注原则: 只看事件的category/description/severity, 不看系统输出.
标注: domain / semantic_family / direction / unmappable_reason
"""
from __future__ import annotations
import json
import sys
sys.path.insert(0, "src")

from p6b_annotation_contract import (
    AnnotationEntry, extract_events_from_golden, save_annotation_table,
    SEMANTIC_FAMILIES, DOMAINS, DIRECTIONS, UNMAPPABLE_REASONS
)


def annotate_event_a(event: dict) -> dict:
    """Annotator A的标注逻辑.

    只看: category, description, severity, target_year
    不看: 系统输出
    """
    raw = event["raw_event"]
    category = raw.get("category", "")
    description = raw.get("description", "")
    severity = raw.get("severity", 3)
    desc_lower = description.lower()

    # 默认标注
    domain = None
    semantic_family = None
    direction = None
    unmappable = False
    unmappable_reason = None
    notes = ""

    # === 按category标注 ===

    if category == "EXAM":
        # 考试: 中举/中进士/落第
        domain = "CAREER"
        semantic_family = "OUTPUT_EXPRESSION"
        if any(k in description for k in ["中", "登", "及第", "进士", "举人", "状元", "榜眼", "探花"]):
            direction = "supportive"
            notes = "考试成功/获得功名"
        elif any(k in description for k in ["落", "不中", "下第", "罢", "黜"]):
            direction = "caution"
            notes = "考试失败/落第"
        else:
            direction = "supportive"  # 默认考试成功
            notes = "考试相关, 默认成功"

    elif category == "CHILD_BIRTH":
        # 出生
        domain = "FAMILY"
        semantic_family = "STABILITY_SUPPORT"
        direction = "neutral"
        notes = "出生事件, 中性"

    elif category == "PARENT_DEATH":
        # 去世/父母去世/丧亲
        domain = "FAMILY"
        semantic_family = "CHANGE_TRANSFORMATION"
        direction = "caution"
        if any(k in description for k in ["父", "母", "丁忧", "丧父", "丧母", "丁外艰", "丁内艰"]):
            notes = "父母去世/丁忧"
        elif any(k in description for k in ["妻", "夫人", "妾"]):
            domain = "RELATIONSHIP"
            notes = "配偶去世"
        else:
            notes = "去世/丧亲事件"

    elif category == "JOB_CHANGE":
        # 工作变动/任职/调任
        domain = "CAREER"
        semantic_family = "CHANGE_TRANSFORMATION"
        if any(k in description for k in ["贬", "谪", "降", "罢", "免", "黜", "外放"]):
            direction = "caution"
            notes = "贬谪/降职/罢免"
        elif any(k in description for k in ["任", "授", "除", "拜", "补", "选", "召", "征", "起用"]):
            direction = "supportive"
            notes = "获得职位/任职"
        else:
            direction = "supportive"
            notes = "工作变动, 默认获得新职"

    elif category == "PROMOTION":
        # 升迁/晋升
        domain = "CAREER"
        semantic_family = "STABILITY_SUPPORT"
        direction = "supportive"
        notes = "升迁/晋升"

    elif category == "FAMILY_CHANGE":
        # 家庭变故/政治事件/重大变故
        # 这个category比较杂, 需要看具体描述
        if any(k in description for k in ["案", "狱", "贬", "谪", "乱", "变", "祸", "难", "灾", "囚", "流放"]):
            domain = "CAREER"
            semantic_family = "CHANGE_TRANSFORMATION"
            direction = "caution"
            notes = "政治事件/灾祸/贬谪"
        elif any(k in description for k in ["婚", "娶", "嫁", "纳妾"]):
            domain = "RELATIONSHIP"
            semantic_family = "RELATION_CONNECTION"
            direction = "supportive"
            notes = "婚姻/家庭关系变化"
        elif any(k in description for k in ["丧", "死", "卒", "殁", "亡"]):
            domain = "FAMILY"
            semantic_family = "CHANGE_TRANSFORMATION"
            direction = "caution"
            notes = "家人去世"
        elif any(k in description for k in ["生", "育", "得子", "生子"]):
            domain = "FAMILY"
            semantic_family = "STABILITY_SUPPORT"
            direction = "supportive"
            notes = "生育/得子"
        else:
            # 无法可靠映射
            unmappable = True
            unmappable_reason = "EVENT_TOO_VAGUE"
            notes = f"FAMILY_CHANGE描述模糊: {description}"

    elif category == "NEW_RELATIONSHIP":
        # 结婚/新关系
        domain = "RELATIONSHIP"
        semantic_family = "RELATION_CONNECTION"
        direction = "supportive"
        notes = "结婚/新关系建立"

    elif category == "RELOCATION":
        # 迁移/贬谪/购房/迁居
        domain = "MIGRATION"
        semantic_family = "CHANGE_TRANSFORMATION"
        if any(k in description for k in ["贬", "谪", "流放", "贬谪"]):
            direction = "caution"
            notes = "贬谪/流放"
        elif any(k in description for k in ["购", "买", "置", "迁居", "移居", "归隐", "隐居"]):
            direction = "neutral"
            notes = "购房/迁居/隐居"
        elif any(k in description for k in ["去", "离", "游", "行", "出使"]):
            direction = "neutral"
            notes = "出行/游历/出使"
        else:
            direction = "neutral"
            notes = "迁移/环境变化"

    elif category == "MAJOR_INCOME":
        # 重要作品/收入/成就
        if any(k in description for k in ["著", "写", "作", "诗", "文", "书", "画", "集", "赋", "记", "序", "论"]):
            domain = "GROWTH"
            semantic_family = "OUTPUT_EXPRESSION"
            direction = "supportive"
            notes = "重要作品/创作成就"
        elif any(k in description for k in ["银", "金", "钱", "财", "禄", "俸", "赏", "赐", "收入"]):
            domain = "FINANCE"
            semantic_family = "RESOURCE_WEALTH"
            direction = "supportive"
            notes = "重要收入/财富获得"
        else:
            domain = "GROWTH"
            semantic_family = "OUTPUT_EXPRESSION"
            direction = "supportive"
            notes = "重要成就/作品"

    elif category == "RESIGNATION":
        # 辞职/退位/归隐
        domain = "CAREER"
        semantic_family = "CHANGE_TRANSFORMATION"
        if any(k in description for k in ["辞", "退", "归", "隐", "致仕", "乞休", "解职"]):
            direction = "neutral"
            notes = "主动辞职/归隐/致仕"
        elif any(k in description for k in ["罢", "免", "黜", "废"]):
            direction = "caution"
            notes = "被迫辞职/罢免"
        else:
            direction = "neutral"
            notes = "辞职/退位"

    else:
        # 未知category
        unmappable = True
        unmappable_reason = "OUTSIDE_VOCABULARY"
        notes = f"未知category: {category}"

    # severity辅助判断 (但不主导)
    # severity 5通常是重大事件, 但方向仍由事件性质决定

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
    print("P6-B 第一轮盲标注 (Annotator A)")
    print("=" * 60)

    # 提取事件
    events = extract_events_from_golden("dataset/golden_v1/golden_cases.json")
    print(f"\n提取事件数: {len(events)}")

    # 盲标注
    annotations = []
    unmappable_count = 0
    domain_dist = {}
    family_dist = {}
    direction_dist = {}

    for ev in events:
        result = annotate_event_a(ev)

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
            annotator="ANNOTATOR_A",
            annotation_round="ROUND_A",
            annotation_notes=result["notes"],
        )
        annotations.append(entry)

        if result["unmappable"]:
            unmappable_count += 1
        else:
            domain_dist[result["domain"]] = domain_dist.get(result["domain"], 0) + 1
            family_dist[result["semantic_family"]] = family_dist.get(result["semantic_family"], 0) + 1
            direction_dist[result["direction"]] = direction_dist.get(result["direction"], 0) + 1

    # 验证
    errors = []
    for a in annotations:
        errors.extend(a.validate())

    # 保存
    output_path = "dataset/golden_v1/annotations_round_a.json"
    save_annotation_table(annotations, output_path)

    # 报告
    print(f"\n标注完成: {len(annotations)} 条")
    print(f"可映射: {len(annotations) - unmappable_count} ({(len(annotations)-unmappable_count)/len(annotations)*100:.1f}%)")
    print(f"UNMAPPABLE: {unmappable_count} ({unmappable_count/len(annotations)*100:.1f}%)")
    print(f"验证错误: {len(errors)}")
    if errors:
        for e in errors[:10]:
            print(f"  - {e}")

    print(f"\nDomain分布:")
    for d, c in sorted(domain_dist.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")

    print(f"\nSemantic Family分布:")
    for f, c in sorted(family_dist.items(), key=lambda x: -x[1]):
        print(f"  {f}: {c}")

    print(f"\nDirection分布:")
    for d, c in sorted(direction_dist.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")

    print(f"\n已保存: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
