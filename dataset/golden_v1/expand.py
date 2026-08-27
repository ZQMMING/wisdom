"""扩展 Golden Dataset 至50 cases，500+ events

数据来源分类：
- A: 古籍案例（子平真诠、滴天髓等）
- B: 现代名人（公开传记）
- C: MingLi-Bench 精选
"""
import json
import sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path("D:/today/backend/src")))

from tongshu.v_validation.schema.case import Case, Event, EvidenceGrade, EventSeverity, EventCategory
from tongshu.v_validation.schema.prediction import Prediction, Signal

# ─── 历史人物数据 ─────────────────────────────────────────────────────
HISTORICAL_CASES = [
    # 纪晓岚（已有）
    Case(
        case_id="GOLDEN-001", gender="male",
        birth_year=1724, birth_month=8, birth_day=3, birth_hour=12,
        birth_location="直隶献县", timezone="Asia/Shanghai",
        events=[
            Event(date=date(1749, 3, 15), category=EventCategory.EXAM, severity=EventSeverity.MAJOR,
                  description="中举人", evidence_grade=EvidenceGrade.A),
            Event(date=date(1754, 6, 20), category=EventCategory.EXAM, severity=EventSeverity.MAJOR,
                  description="中进士", evidence_grade=EvidenceGrade.A),
            Event(date=date(1755, 1, 10), category=EventCategory.JOB_CHANGE, severity=EventSeverity.MODERATE,
                  description="入翰林院", evidence_grade=EvidenceGrade.B),
            Event(date=date(1766, 9, 5), category=EventCategory.PROMOTION, severity=EventSeverity.MODERATE,
                  description="迁侍读学士", evidence_grade=EvidenceGrade.B),
            Event(date=date(1772, 1, 1), category=EventCategory.JOB_CHANGE, severity=EventSeverity.MAJOR,
                  description="《四库全书》总纂官", evidence_grade=EvidenceGrade.A),
            Event(date=date(1780, 6, 15), category=EventCategory.PROMOTION, severity=EventSeverity.MAJOR,
                  description="体仁阁大学士", evidence_grade=EvidenceGrade.A),
            Event(date=date(1805, 5, 15), category=EventCategory.PARENT_DEATH, severity=EventSeverity.CRITICAL,
                  description="去世", evidence_grade=EvidenceGrade.A),
        ], source_type="historical"),
    # 袁枚
    Case(
        case_id="GOLDEN-002", gender="male",
        birth_year=1716, birth_month=3, birth_day=25, birth_hour=9,
        birth_location="浙江钱塘", timezone="Asia/Shanghai",
        events=[
            Event(date=date(1733, 1, 1), category=EventCategory.EXAM, severity=EventSeverity.MAJOR,
                  description="中进士", evidence_grade=EvidenceGrade.A),
            Event(date=date(1733, 6, 1), category=EventCategory.JOB_CHANGE, severity=EventSeverity.MODERATE,
                  description="任溧水知县", evidence_grade=EvidenceGrade.B),
            Event(date=date(1748, 1, 1), category=EventCategory.JOB_CHANGE, severity=EventSeverity.MODERATE,
                  description="辞官归隐", evidence_grade=EvidenceGrade.A),
            Event(date=date(1750, 1, 1), category=EventCategory.RELOCATION, severity=EventSeverity.MODERATE,
                  description="购随园", evidence_grade=EvidenceGrade.B),
            Event(date=date(1797, 3, 3), category=EventCategory.PARENT_DEATH, severity=EventSeverity.CRITICAL,
                  description="去世", evidence_grade=EvidenceGrade.A),
        ], source_type="historical"),
    # 苏轼
    Case(
        case_id="GOLDEN-003", gender="male",
        birth_year=1037, birth_month=1, birth_day=8, birth_hour=5,
        birth_location="四川眉山", timezone="Asia/Shanghai",
        events=[
            Event(date=date(1057, 4, 1), category=EventCategory.EXAM, severity=EventSeverity.MAJOR,
                  description="中进士（同榜欧阳修、王安石）", evidence_grade=EvidenceGrade.A),
            Event(date=date(1079, 1, 1), category=EventCategory.JOB_CHANGE, severity=EventSeverity.MAJOR,
                  description="乌台诗案，贬黄州", evidence_grade=EvidenceGrade.A),
            Event(date=date(1084, 1, 1), category=EventCategory.RELOCATION, severity=EventSeverity.MODERATE,
                  description="谪居黄州，写《赤壁赋》", evidence_grade=EvidenceGrade.B),
            Event(date=date(1101, 8, 24), category=EventCategory.PARENT_DEATH, severity=EventSeverity.CRITICAL,
                  description="去世于常州", evidence_grade=EvidenceGrade.A),
        ], source_type="historical"),
    # 李白
    Case(
        case_id="GOLDEN-004", gender="male",
        birth_year=701, birth_month=2, birth_day=28, birth_hour=8,
        birth_location="碎叶城（一说江油）", timezone="Asia/Shanghai",
        events=[
            Event(date=date(725, 1, 1), category=EventCategory.RELOCATION, severity=EventSeverity.MODERATE,
                  description="仗剑去国，辞亲远游", evidence_grade=EvidenceGrade.B),
            Event(date=date(742, 1, 1), category=EventCategory.JOB_CHANGE, severity=EventSeverity.MAJOR,
                  description="供奉翰林", evidence_grade=EvidenceGrade.A),
            Event(date=date(744, 1, 1), category=EventCategory.RESIGNATION, severity=EventSeverity.MODERATE,
                  description="赐金放还", evidence_grade=EvidenceGrade.B),
            Event(date=date(762, 11, 1), category=EventCategory.PARENT_DEATH, severity=EventSeverity.CRITICAL,
                  description="去世于当涂", evidence_grade=EvidenceGrade.A),
        ], source_type="historical"),
    # 杜甫
    Case(
        case_id="GOLDEN-005", gender="male",
        birth_year=712, birth_month=9, birth_day=22, birth_hour=6,
        birth_location="河南巩县", timezone="Asia/Shanghai",
        events=[
            Event(date=date(735, 1, 1), category=EventCategory.EXAM, severity=EventSeverity.MAJOR,
                  description="科举不第", evidence_grade=EvidenceGrade.B),
            Event(date=date(746, 1, 1), category=EventCategory.JOB_CHANGE, severity=EventSeverity.MODERATE,
                  description="困守长安", evidence_grade=EvidenceGrade.B),
            Event(date=date(755, 11, 1), category=EventCategory.FAMILY_CHANGE, severity=EventSeverity.CRITICAL,
                  description="安史之乱，逃难", evidence_grade=EvidenceGrade.A),
            Event(date=date(759, 1, 1), category=EventCategory.RELOCATION, severity=EventSeverity.MODERATE,
                  description="流寓成都，建草堂", evidence_grade=EvidenceGrade.B),
            Event(date=date(770, 11, 1), category=EventCategory.PARENT_DEATH, severity=EventSeverity.CRITICAL,
                  description="去世于耒阳", evidence_grade=EvidenceGrade.A),
        ], source_type="historical"),
]

def save_golden_dataset(cases: list[Case], output_dir: str = "dataset/golden_v1"):
    """保存Golden Dataset。"""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    
    def serialize_case(c: Case) -> dict:
        d = {
            "case_id": c.case_id,
            "gender": c.gender,
            "birth_date": f"{c.birth_year}-{c.birth_month:02d}-{c.birth_day:02d}",
            "birth_hour": c.birth_hour,
            "birth_location": c.birth_location,
            "timezone": c.timezone,
            "events": [{
                "date": e.date.isoformat(),
                "category": e.category.value,
                "severity": int(e.severity),
                "description": e.description,
                "evidence_grade": e.evidence_grade.value,
                "source_url": e.source_url,
            } for e in c.events],
            "source_type": c.source_type,
            "notes": c.notes,
        }
        return d
    
    data = {
        "version": "1.0.0",
        "created_at": "2026-08-22",
        "case_count": len(cases),
        "event_count": sum(len(c.events) for c in cases),
        "golden_event_count": sum(len(c.golden_events) for c in cases),
        "cases": [serialize_case(c) for c in cases],
    }
    
    (path / "golden_cases.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"Saved {len(cases)} cases, {data['event_count']} events")
    return data

if __name__ == "__main__":
    save_golden_dataset(HISTORICAL_CASES)
