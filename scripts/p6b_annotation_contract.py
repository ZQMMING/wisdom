"""P6-B Ground Truth Annotation Contract.

盲标注契约: 标注人员只看事件资料, 不看系统输出.

Annotation Contract:
- event_id: 唯一标识
- case_id: 所属案例
- target_year: 事件发生年份
- raw_event: 原始事件描述
- domain: CAREER/FINANCE/RELATIONSHIP/FAMILY/HEALTH/GROWTH/DECISION/MIGRATION
- semantic_family: 来自Canonical Vocabulary (9个)
- direction: supportive/caution/neutral
- unmappable: True/False
- unmappable_reason: 如果unmappable, 说明原因
- annotator: 标注者标识
- annotation_round: 轮次 (A/B)

Canonical Vocabulary (semantic_family):
1. OUTPUT_EXPRESSION - 输出/表达/创造/可见度/自主
2. RESOURCE_WEALTH - 资源/财富/资产/丰裕
3. STABILITY_SUPPORT - 稳定/支持/持久
4. CONSTRAINT_RULE - 约束/纪律/规则/责任
5. CHANGE_TRANSFORMATION - 变化/转型/波动/颠覆
6. REFLECTION_GROWTH - 反思/觉察/洞察/成长/主动
7. RELATION_CONNECTION - 关系/社交/连接/合作/和谐/吸引/张力/冲突
8. ACTION_EXECUTION - 行动/执行/运动
9. HEALTH_CAUTION - 健康/谨慎/预防/脆弱

Domain (8个):
- CAREER - 事业/工作/职位/考试
- FINANCE - 财富/资源/资产/收入
- RELATIONSHIP - 感情/婚姻/亲密关系
- FAMILY - 家庭/父母/子女/居住
- HEALTH - 健康/疾病/精力
- GROWTH - 个人成长/学习/定位
- DECISION - 决策/判断/选择
- MIGRATION - 迁移/环境变化/旅行

Direction (3个):
- supportive - 有利条件 (事件对人生是积极的/成功的/获得的)
- caution - 需要注意 (事件对人生是困难的/损失的/挑战的)
- neutral - 无明显方向性偏移 (事件中性/信息不足/无法判断)

UNMAPPABLE原因:
- EVENT_TOO_VAGUE - 事件描述太模糊, 无法可靠映射
- DOMAIN_AMBIGUOUS - domain不明确, 跨多个维度
- DIRECTION_UNCLEAR - 方向不明确, 好坏参半
- OUTSIDE_VOCABULARY - 事件类型不在当前词汇表范围内
- INSUFFICIENT_CONTEXT - 上下文不足, 无法判断
"""
from __future__ import annotations
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional, Literal
from datetime import datetime

sys.path.insert(0, "src")

# Canonical Vocabulary
SEMANTIC_FAMILIES = [
    "OUTPUT_EXPRESSION",
    "RESOURCE_WEALTH",
    "STABILITY_SUPPORT",
    "CONSTRAINT_RULE",
    "CHANGE_TRANSFORMATION",
    "REFLECTION_GROWTH",
    "RELATION_CONNECTION",
    "ACTION_EXECUTION",
    "HEALTH_CAUTION",
]

DOMAINS = [
    "CAREER", "FINANCE", "RELATIONSHIP", "FAMILY",
    "HEALTH", "GROWTH", "DECISION", "MIGRATION",
]

DIRECTIONS = ["supportive", "caution", "neutral"]

UNMAPPABLE_REASONS = [
    "EVENT_TOO_VAGUE",
    "DOMAIN_AMBIGUOUS",
    "DIRECTION_UNCLEAR",
    "OUTSIDE_VOCABULARY",
    "INSUFFICIENT_CONTEXT",
]


@dataclass
class AnnotationEntry:
    """单条标注条目."""
    event_id: str
    case_id: str
    target_year: int
    raw_event: dict  # 原始事件: date/category/severity/description/evidence_grade
    domain: Optional[str] = None
    semantic_family: Optional[str] = None
    direction: Optional[str] = None
    unmappable: bool = False
    unmappable_reason: Optional[str] = None
    annotator: str = ""
    annotation_round: str = ""
    annotation_notes: str = ""

    def validate(self) -> list[str]:
        """验证标注完整性."""
        errors = []
        if self.unmappable:
            if not self.unmappable_reason:
                errors.append(f"{self.event_id}: unmappable但缺少unmappable_reason")
            elif self.unmappable_reason not in UNMAPPABLE_REASONS:
                errors.append(f"{self.event_id}: 无效的unmappable_reason={self.unmappable_reason}")
        else:
            if not self.domain:
                errors.append(f"{self.event_id}: 缺少domain")
            elif self.domain not in DOMAINS:
                errors.append(f"{self.event_id}: 无效domain={self.domain}")
            if not self.semantic_family:
                errors.append(f"{self.event_id}: 缺少semantic_family")
            elif self.semantic_family not in SEMANTIC_FAMILIES:
                errors.append(f"{self.event_id}: 无效semantic_family={self.semantic_family}")
            if not self.direction:
                errors.append(f"{self.event_id}: 缺少direction")
            elif self.direction not in DIRECTIONS:
                errors.append(f"{self.event_id}: 无效direction={self.direction}")
        return errors


def extract_events_from_golden(dataset_path: str) -> list[dict]:
    """从Golden Dataset提取所有事件, 建立标注表框架."""
    with open(dataset_path, encoding="utf-8") as f:
        dataset = json.load(f)

    events = []
    for case in dataset.get("cases", []):
        case_id = case["case_id"]
        for i, event in enumerate(case.get("events", [])):
            # 提取target_year
            event_date = event.get("date", "")
            try:
                target_year = int(event_date.split("-")[0])
            except (ValueError, IndexError):
                target_year = 0

            event_id = f"{case_id}_EV{i+1:03d}"
            events.append({
                "event_id": event_id,
                "case_id": case_id,
                "target_year": target_year,
                "raw_event": event,
            })

    return events


def build_annotation_table(events: list[dict], annotator: str, round_name: str) -> list[AnnotationEntry]:
    """建立标注表(空白, 等待标注)."""
    table = []
    for ev in events:
        entry = AnnotationEntry(
            event_id=ev["event_id"],
            case_id=ev["case_id"],
            target_year=ev["target_year"],
            raw_event=ev["raw_event"],
            annotator=annotator,
            annotation_round=round_name,
        )
        table.append(entry)
    return table


def save_annotation_table(table: list[AnnotationEntry], path: str):
    """保存标注表."""
    data = {
        "annotation_contract_version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "semantic_families": SEMANTIC_FAMILIES,
        "domains": DOMAINS,
        "directions": DIRECTIONS,
        "unmappable_reasons": UNMAPPABLE_REASONS,
        "total_events": len(table),
        "annotations": [asdict(e) for e in table],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_annotation_table(path: str) -> list[AnnotationEntry]:
    """加载标注表."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [AnnotationEntry(**a) for a in data["annotations"]]


def compute_agreement(table_a: list[AnnotationEntry], table_b: list[AnnotationEntry]) -> dict:
    """计算双人标注一致性."""
    map_a = {e.event_id: e for e in table_a}
    map_b = {e.event_id: e for e in table_b}

    common_ids = set(map_a.keys()) & set(map_b.keys())
    total = len(common_ids)

    if total == 0:
        return {"error": "No common events"}

    # Domain一致性
    domain_match = sum(1 for eid in common_ids if map_a[eid].domain == map_b[eid].domain)
    # Semantic Family一致性
    family_match = sum(1 for eid in common_ids if map_a[eid].semantic_family == map_b[eid].semantic_family)
    # Direction一致性
    direction_match = sum(1 for eid in common_ids if map_a[eid].direction == map_b[eid].direction)
    # Unmappable一致性
    unmappable_match = sum(1 for eid in common_ids if map_a[eid].unmappable == map_b[eid].unmappable)
    # 完全一致 (domain+family+direction都匹配, 或都unmappable)
    full_match = sum(
        1 for eid in common_ids
        if (map_a[eid].unmappable and map_b[eid].unmappable) or
           (map_a[eid].domain == map_b[eid].domain and
            map_a[eid].semantic_family == map_b[eid].semantic_family and
            map_a[eid].direction == map_b[eid].direction)
    )

    return {
        "total_common_events": total,
        "domain_agreement_pct": round(domain_match / total * 100, 1),
        "semantic_family_agreement_pct": round(family_match / total * 100, 1),
        "direction_agreement_pct": round(direction_match / total * 100, 1),
        "unmappable_agreement_pct": round(unmappable_match / total * 100, 1),
        "full_agreement_pct": round(full_match / total * 100, 1),
        "domain_match": domain_match,
        "family_match": family_match,
        "direction_match": direction_match,
        "full_match": full_match,
    }


if __name__ == "__main__":
    # 测试: 提取事件
    events = extract_events_from_golden("dataset/golden_v1/golden_cases.json")
    print(f"提取事件数: {len(events)}")
    print(f"前3个事件:")
    for ev in events[:3]:
        print(f"  {ev['event_id']}: {ev['target_year']} - {ev['raw_event'].get('description', '?')}")

    # 建立空白标注表
    table = build_annotation_table(events, "ANNOTATOR_A", "ROUND_A")
    print(f"\n空白标注表条目数: {len(table)}")
    print(f"Annotation Contract:")
    print(f"  Semantic Families ({len(SEMANTIC_FAMILIES)}): {SEMANTIC_FAMILIES}")
    print(f"  Domains ({len(DOMAINS)}): {DOMAINS}")
    print(f"  Directions ({len(DIRECTIONS)}): {DIRECTIONS}")
    print(f"  Unmappable Reasons ({len(UNMAPPABLE_REASONS)}): {UNMAPPABLE_REASONS}")
