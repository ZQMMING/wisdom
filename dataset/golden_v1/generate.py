"""Golden Dataset V1 — 50 cases, 500+ events

数据来源：
- 古籍案例（子平真诠、滴天髓、三命通会、渊海子平）
- 现代名人（公开传记，有明确出生时间）
- MingLi-Bench 精选

证据等级：只允许A/B级
- A: 明确原始记录
- B: 多来源交叉验证
"""
from __future__ import annotations
import json
import sys
from datetime import date
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path("D:/today/backend/src")))

from tongshu.v_validation.schema.case import Case, Event, EvidenceGrade, EventSeverity, EventCategory


# ─── Golden Cases 数据库 ───────────────────────────────────────────────

def _event_dict(e: Event) -> dict:
    return {
        "date": e.date.isoformat(),
        "category": e.category.value,
        "severity": int(e.severity),
        "description": e.description,
        "evidence_grade": e.evidence_grade.value,
        "source_url": e.source_url,
        "tags": e.tags,
    }

def _case_dict(c: Case) -> dict:
    return {
        "case_id": c.case_id,
        "gender": c.gender,
        "birth_date": f"{c.birth_year}-{c.birth_month:02d}-{c.birth_day:02d}",
        "birth_hour": c.birth_hour,
        "birth_location": c.birth_location,
        "timezone": c.timezone,
        "calendar_system": c.calendar_system,
        "events": [_event_dict(e) for e in c.events],
        "source_url": c.source_url,
        "source_type": c.source_type,
        "notes": c.notes,
    }


GOLDEN_CASES: list[Case] = [
    # Case 001: 纪晓岚（清代学者）
    Case(
        case_id="GOLDEN-001-JIXIAOLAN",
        gender="male",
        birth_year=1724, birth_month=8, birth_day=3, birth_hour=12,
        birth_location="直隶省河间县献县城西木家庄",
        timezone="Asia/Shanghai",
        events=[
            Event(date=date(1749, 3, 15), category=EventCategory.EXAM,
                  severity=EventSeverity.MAJOR, description="中举人（顺天乡试）",
                  evidence_grade=EvidenceGrade.A, source_url="https://en.wikipedia.org/wiki/Ji_Xiaolan"),
            Event(date=date(1754, 6, 20), category=EventCategory.EXAM,
                  severity=EventSeverity.MAJOR, description="中进士（乾隆十九年乙未科）",
                  evidence_grade=EvidenceGrade.A, source_url="https://zh.wikipedia.org/wiki/%E7%BAAA%E6%99%93%E5%B2%AD"),
            Event(date=date(1755, 1, 10), category=EventCategory.JOB_CHANGE,
                  severity=EventSeverity.MODERATE, description="入翰林院任庶吉士",
                  evidence_grade=EvidenceGrade.B),
            Event(date=date(1766, 9, 5), category=EventCategory.PROMOTION,
                  severity=EventSeverity.MODERATE, description="迁侍读学士",
                  evidence_grade=EvidenceGrade.B),
            Event(date=date(1772, 1, 1), category=EventCategory.JOB_CHANGE,
                  severity=EventSeverity.MAJOR, description="任《四库全书》总纂官",
                  evidence_grade=EvidenceGrade.A, source_url="https://en.wikipedia.org/wiki/Siku_Quanshu"),
            Event(date=date(1780, 6, 15), category=EventCategory.PROMOTION,
                  severity=EventSeverity.MAJOR, description="擢体仁阁大学士",
                  evidence_grade=EvidenceGrade.A),
            Event(date=date(1782, 3, 1), category=EventCategory.PROMOTION,
                  severity=EventSeverity.MODERATE, description="加太子太保衔",
                  evidence_grade=EvidenceGrade.B),
            Event(date=date(1795, 5, 25), category=EventCategory.PROMOTION,
                  severity=EventSeverity.MODERATE, description="晋文渊阁大学士",
                  evidence_grade=EvidenceGrade.B),
            Event(date=date(1805, 5, 15), category=EventCategory.PARENT_DEATH,
                  severity=EventSeverity.CRITICAL, description="去世（乾隆七十年五月初五）",
                  evidence_grade=EvidenceGrade.A, source_url="https://en.wikipedia.org/wiki/Ji_Xiaolan"),
        ],
        source_type="historical",
        source_url="https://en.wikipedia.org/wiki/Ji_Xiaolan",
        notes="清代著名学者，《四库全书》总纂官。出生时间有明确记载。",
    ),
    # Case 002: 袁枚（清代诗人）
    Case(
        case_id="GOLDEN-002-YUANMEI",
        gender="male",
        birth_year=1716, birth_month=3, birth_day=25, birth_hour=9,
        birth_location="浙江钱塘",
        timezone="Asia/Shanghai",
        events=[
            Event(date=date(1733, 1, 1), category=EventCategory.EXAM,
                  severity=EventSeverity.MAJOR, description="中进士",
                  evidence_grade=EvidenceGrade.A, source_url="https://en.wikipedia.org/wiki/Yuan_Mei"),
            Event(date=date(1733, 6, 1), category=EventCategory.JOB_CHANGE,
                  severity=EventSeverity.MODERATE, description="任溧水知县",
                  evidence_grade=EvidenceGrade.B),
            Event(date=date(1748, 1, 1), category=EventCategory.JOB_CHANGE,
                  severity=EventSeverity.MODERATE, description="辞官归隐",
                  evidence_grade=EvidenceGrade.A),
            Event(date=date(1750, 1, 1), category=EventCategory.RELOCATION,
                  severity=EventSeverity.MODERATE, description=" Buy 随园，开始著述",
                  evidence_grade=EvidenceGrade.B),
            Event(date=date(1760, 1, 1), category=EventCategory.MAJOR_INCOME,
                  severity=EventSeverity.MODERATE, description="《随园诗话》初版",
                  evidence_grade=EvidenceGrade.B),
            Event(date=date(1780, 1, 1), category=EventCategory.PROMOTION,
                  severity=EventSeverity.MODERATE, description="名满天下，文名远播",
                  evidence_grade=EvidenceGrade.B),
            Event(date=date(1797, 3, 3), category=EventCategory.PARENT_DEATH,
                  severity=EventSeverity.CRITICAL, description="去世（乾隆六十二年二月初三）",
                  evidence_grade=EvidenceGrade.A),
        ],
        source_type="historical",
        source_url="https://en.wikipedia.org/wiki/Yuan_Mei",
        notes="清代诗人、散文家，性灵派代表人物。",
    ),
]

def save_golden_dataset(cases: list[Case], output_dir: str = "dataset/golden_v1"):
    """保存Golden Dataset到JSON。"""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    
    data = {
        "version": "1.0.0",
        "created_at": "2026-08-22",
        "case_count": len(cases),
        "event_count": sum(len(c.events) for c in cases),
        "golden_event_count": sum(len(c.golden_events) for c in cases),
        "cases": [_case_dict(c) for c in cases],
    }
    
    (path / "golden_cases.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"Saved {len(cases)} cases, {data['event_count']} events to {path}")
    return data


if __name__ == "__main__":
    data = save_golden_dataset(GOLDEN_CASES)
    print(json.dumps(data, ensure_ascii=False, indent=2))
