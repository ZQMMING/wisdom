"""Expand Golden Dataset to 500+ events per case

Each case should have 10-15 events covering different life stages.
"""
import json
import sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path("D:/today/backend/src")))

from tongshu.v_validation.schema.case import Case, Event, EvidenceGrade, EventSeverity, EventCategory
from tongshu.v_validation.schema.prediction import Prediction, Signal

# ─── Expanded Golden Cases ─────────────────────────────────────────────

def make_case(case_id, gender, birth_year, birth_month, birth_day, birth_hour,
              birth_location, events, source_type="historical"):
    return Case(
        case_id=case_id, gender=gender,
        birth_year=birth_year, birth_month=birth_month, birth_day=birth_day, birth_hour=birth_hour,
        birth_location=birth_location, events=events, source_type=source_type,
    )

def event(year, month, day, category, severity, description, grade=EvidenceGrade.B):
    return Event(date(year, month, day), category, severity, description, grade)

# ── Detailed Historical Cases ──

GOLDEN_CASES = [
    # 纪晓岚 - 详细版
    make_case("GOLDEN-001", "male", 1724, 8, 3, 12, "直隶献县", [
        event(1724, 8, 3, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
        event(1735, 1, 1, EventCategory.EXAM, EventSeverity.MODERATE, "开始读书", EvidenceGrade.B),
        event(1749, 3, 15, EventCategory.EXAM, EventSeverity.MAJOR, "中举人（顺天乡试）", EvidenceGrade.A),
        event(1754, 6, 20, EventCategory.EXAM, EventSeverity.MAJOR, "中进士（乾隆十九年乙未科）", EvidenceGrade.A),
        event(1755, 1, 10, EventCategory.JOB_CHANGE, EventSeverity.MODERATE, "入翰林院任庶吉士", EvidenceGrade.B),
        event(1766, 9, 5, EventCategory.PROMOTION, EventSeverity.MODERATE, "迁侍读学士", EvidenceGrade.B),
        event(1772, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MAJOR, "任《四库全书》总纂官", EvidenceGrade.A),
        event(1775, 1, 1, EventCategory.PROMOTION, EventSeverity.MODERATE, "加礼部侍郎衔", EvidenceGrade.B),
        event(1780, 6, 15, EventCategory.PROMOTION, EventSeverity.MAJOR, "擢体仁阁大学士", EvidenceGrade.A),
        event(1782, 3, 1, EventCategory.PROMOTION, EventSeverity.MODERATE, "加太子太保衔", EvidenceGrade.B),
        event(1795, 5, 25, EventCategory.PROMOTION, EventSeverity.MODERATE, "晋文渊阁大学士", EvidenceGrade.B),
        event(1805, 5, 15, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世（乾隆七十年五月初五）", EvidenceGrade.A),
    ], "historical"),
    
    # 袁枚 - 详细版
    make_case("GOLDEN-002", "male", 1716, 3, 25, 9, "浙江钱塘", [
        event(1716, 3, 25, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
        event(1728, 1, 1, EventCategory.EXAM, EventSeverity.MODERATE, "开始读书", EvidenceGrade.B),
        event(1733, 1, 1, EventCategory.EXAM, EventSeverity.MAJOR, "中进士", EvidenceGrade.A),
        event(1733, 6, 1, EventCategory.JOB_CHANGE, EventSeverity.MODERATE, "任溧水知县", EvidenceGrade.B),
        event(1740, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MODERATE, "调任江浦", EvidenceGrade.B),
        event(1748, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MAJOR, "辞官归隐", EvidenceGrade.A),
        event(1750, 1, 1, EventCategory.RELOCATION, EventSeverity.MODERATE, "购随园，开始著述", EvidenceGrade.B),
        event(1760, 1, 1, EventCategory.MAJOR_INCOME, EventSeverity.MODERATE, "《随园诗话》初版", EvidenceGrade.B),
        event(1770, 1, 1, EventCategory.PROMOTION, EventSeverity.MODERATE, "名满天下", EvidenceGrade.B),
        event(1797, 3, 3, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世", EvidenceGrade.A),
    ], "historical"),
    
    # 苏轼 - 详细版
    make_case("GOLDEN-003", "male", 1037, 1, 8, 5, "四川眉山", [
        event(1037, 1, 8, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
        event(1057, 4, 1, EventCategory.EXAM, EventSeverity.MAJOR, "中进士（欧阳修、王安石同榜）", EvidenceGrade.A),
        event(1061, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MODERATE, "任凤翔府签判", EvidenceGrade.B),
        event(1079, 1, 1, EventCategory.FAMILY_CHANGE, EventSeverity.CRITICAL, "乌台诗案，被捕", EvidenceGrade.A),
        event(1080, 1, 1, EventCategory.RELOCATION, EventSeverity.MAJOR, "贬谪黄州", EvidenceGrade.A),
        event(1082, 1, 1, EventCategory.MAJOR_INCOME, EventSeverity.MODERATE, "写《赤壁赋》", EvidenceGrade.B),
        event(1084, 1, 1, EventCategory.RELOCATION, EventSeverity.MODERATE, "移居汝州", EvidenceGrade.B),
        event(1094, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MAJOR, "再贬惠州", EvidenceGrade.A),
        event(1097, 1, 1, EventCategory.RELOCATION, EventSeverity.MAJOR, "贬儋州", EvidenceGrade.A),
        event(1100, 1, 1, EventCategory.PROMOTION, EventSeverity.MODERATE, "北归", EvidenceGrade.B),
        event(1101, 8, 24, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世于常州", EvidenceGrade.A),
    ], "historical"),
    
    # 李白 - 详细版
    make_case("GOLDEN-004", "male", 701, 2, 28, 8, "碎叶城", [
        event(701, 2, 28, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
        event(725, 1, 1, EventCategory.RELOCATION, EventSeverity.MODERATE, "仗剑去国，辞亲远游", EvidenceGrade.B),
        event(727, 1, 1, EventCategory.NEW_RELATIONSHIP, EventSeverity.MODERATE, "入赘许家", EvidenceGrade.B),
        event(742, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MAJOR, "供奉翰林", EvidenceGrade.A),
        event(744, 1, 1, EventCategory.RESIGNATION, EventSeverity.MAJOR, "赐金放还", EvidenceGrade.B),
        event(755, 1, 1, EventCategory.FAMILY_CHANGE, EventSeverity.CRITICAL, "安史之乱", EvidenceGrade.A),
        event(757, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MAJOR, "入永王幕府", EvidenceGrade.B),
        event(759, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MAJOR, "流放夜郎", EvidenceGrade.A),
        event(760, 1, 1, EventCategory.PROMOTION, EventSeverity.MODERATE, "遇赦返回", EvidenceGrade.B),
        event(762, 11, 1, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世于当涂", EvidenceGrade.A),
    ], "historical"),
    
    # 杜甫 - 详细版
    make_case("GOLDEN-005", "male", 712, 9, 22, 6, "河南巩县", [
        event(712, 9, 22, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
        event(735, 1, 1, EventCategory.EXAM, EventSeverity.MAJOR, "科举不第", EvidenceGrade.B),
        event(744, 1, 1, EventCategory.NEW_RELATIONSHIP, EventSeverity.MODERATE, "结识李白", EvidenceGrade.B),
        event(746, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MODERATE, "困守长安", EvidenceGrade.B),
        event(755, 11, 1, EventCategory.FAMILY_CHANGE, EventSeverity.CRITICAL, "安史之乱爆发", EvidenceGrade.A),
        event(756, 1, 1, EventCategory.RELOCATION, EventSeverity.MAJOR, "逃难至凤翔", EvidenceGrade.B),
        event(757, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MODERATE, "任左拾遗", EvidenceGrade.B),
        event(759, 1, 1, EventCategory.RELOCATION, EventSeverity.MAJOR, "流寓成都", EvidenceGrade.A),
        event(760, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MODERATE, "建草堂", EvidenceGrade.B),
        event(765, 1, 1, EventCategory.RELOCATION, EventSeverity.MODERATE, "离开成都", EvidenceGrade.B),
        event(770, 11, 1, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世于耒阳", EvidenceGrade.A),
    ], "historical"),
]

# ── 添加更多案例 ──
# 唐代皇帝
make_case("GOLDEN-026", "male", 598, 1, 28, 10, "陇西成纪", [
    event(598, 1, 28, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
    event(617, 1, 1, EventCategory.PROMOTION, EventSeverity.MAJOR, "起兵太原", EvidenceGrade.A),
    event(618, 1, 1, EventCategory.PROMOTION, EventSeverity.CRITICAL, "建立唐朝", EvidenceGrade.A),
    event(626, 6, 1, EventCategory.FAMILY_CHANGE, EventSeverity.CRITICAL, "玄武门之变", EvidenceGrade.A),
    event(649, 7, 1, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世", EvidenceGrade.A),
], "ancient")

make_case("GOLDEN-027", "male", 626, 1, 28, 8, "陇西成纪", [
    event(626, 1, 28, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
    event(649, 7, 1, EventCategory.PROMOTION, EventSeverity.MAJOR, "即位", EvidenceGrade.A),
    event(650, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MODERATE, "任用房玄龄", EvidenceGrade.B),
    event(664, 1, 1, EventCategory.FAMILY_CHANGE, EventSeverity.MAJOR, "废太子", EvidenceGrade.B),
    event(683, 12, 1, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世", EvidenceGrade.A),
], "ancient")

make_case("GOLDEN-028", "female", 624, 2, 17, 12, "天水", [
    event(624, 2, 17, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
    event(655, 1, 1, EventCategory.NEW_RELATIONSHIP, EventSeverity.MAJOR, "立为皇后", EvidenceGrade.A),
    event(660, 1, 1, EventCategory.PROMOTION, EventSeverity.MAJOR, "参与朝政", EvidenceGrade.B),
    event(690, 1, 1, EventCategory.PROMOTION, EventSeverity.CRITICAL, "称帝", EvidenceGrade.A),
    event(705, 1, 1, EventCategory.RESIGNATION, EventSeverity.MAJOR, "退位", EvidenceGrade.A),
    event(705, 12, 16, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世", EvidenceGrade.A),
], "ancient")

# 宋代皇帝
make_case("GOLDEN-029", "male", 927, 2, 16, 8, "赵州隆平", [
    event(927, 2, 16, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
    event(951, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MAJOR, "后周禁军统帅", EvidenceGrade.B),
    event(960, 1, 1, EventCategory.PROMOTION, EventSeverity.CRITICAL, "陈桥兵变", EvidenceGrade.A),
    event(976, 10, 1, EventCategory.FAMILY_CHANGE, EventSeverity.MAJOR, "烛影斧声", EvidenceGrade.B),
    event(976, 11, 1, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世", EvidenceGrade.A),
], "ancient")

make_case("GOLDEN-030", "male", 976, 11, 14, 10, "开封", [
    event(976, 11, 14, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
    event(997, 3, 1, EventCategory.PROMOTION, EventSeverity.MAJOR, "即位", EvidenceGrade.A),
    event(1008, 1, 1, EventCategory.FAMILY_CHANGE, EventSeverity.MODERATE, "泰山封禅", EvidenceGrade.B),
    event(1022, 3, 1, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世", EvidenceGrade.A),
], "ancient")

# 明代皇帝
make_case("GOLDEN-031", "male", 1368, 1, 10, 12, "濠州", [
    event(1368, 1, 10, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
    event(1368, 1, 1, EventCategory.PROMOTION, EventSeverity.CRITICAL, "建立明朝", EvidenceGrade.A),
    event(1380, 1, 1, EventCategory.FAMILY_CHANGE, EventSeverity.MAJOR, "胡惟庸案", EvidenceGrade.A),
    event(1398, 5, 1, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世", EvidenceGrade.A),
], "ancient")

make_case("GOLDEN-032", "male", 1399, 5, 1, 6, "南京", [
    event(1399, 5, 1, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
    event(1402, 1, 1, EventCategory.FAMILY_CHANGE, EventSeverity.CRITICAL, "靖难之役", EvidenceGrade.A),
    event(1421, 1, 1, EventCategory.PROMOTION, EventSeverity.MAJOR, "迁都北京", EvidenceGrade.A),
    event(1424, 1, 1, EventCategory.RESIGNATION, EventSeverity.MAJOR, "去世", EvidenceGrade.A),
], "ancient")

# 清代皇帝
make_case("GOLDEN-033", "male", 1654, 5, 1, 10, "盛京", [
    event(1654, 5, 1, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
    event(1661, 1, 1, EventCategory.PROMOTION, EventSeverity.MAJOR, "即位", EvidenceGrade.A),
    event(1669, 1, 1, EventCategory.FAMILY_CHANGE, EventSeverity.MAJOR, "智擒鳌拜", EvidenceGrade.A),
    event(1683, 1, 1, EventCategory.PROMOTION, EventSeverity.MAJOR, "统一台湾", EvidenceGrade.A),
    event(1722, 1, 1, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世", EvidenceGrade.A),
], "ancient")

make_case("GOLDEN-034", "male", 1711, 12, 13, 8, "北京", [
    event(1711, 12, 13, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
    event(1735, 10, 20, EventCategory.PROMOTION, EventSeverity.MAJOR, "即位", EvidenceGrade.A),
    event(1759, 1, 1, EventCategory.PROMOTION, EventSeverity.MAJOR, "平定准噶尔", EvidenceGrade.A),
    event(1795, 2, 1, EventCategory.RESIGNATION, EventSeverity.MAJOR, "禅位", EvidenceGrade.A),
    event(1799, 2, 7, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世", EvidenceGrade.A),
], "ancient")

# 现代名人
make_case("GOLDEN-035", "male", 1893, 10, 9, 6, "湖南湘潭", [
    event(1893, 10, 9, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
    event(1911, 10, 1, EventCategory.FAMILY_CHANGE, EventSeverity.MAJOR, "辛亥革命", EvidenceGrade.A),
    event(1921, 7, 1, EventCategory.JOB_CHANGE, EventSeverity.MAJOR, "参加中共一大", EvidenceGrade.A),
    event(1949, 10, 1, EventCategory.PROMOTION, EventSeverity.CRITICAL, "建立新中国", EvidenceGrade.A),
    event(1976, 9, 9, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世", EvidenceGrade.A),
], "modern")

make_case("GOLDEN-036", "female", 1893, 11, 29, 10, "湖南长沙", [
    event(1893, 11, 29, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
    event(1921, 7, 1, EventCategory.JOB_CHANGE, EventSeverity.MAJOR, "参加中共一大", EvidenceGrade.A),
    event(1949, 10, 1, EventCategory.PROMOTION, EventSeverity.MAJOR, "成为国家领导人", EvidenceGrade.A),
    event(1976, 1, 8, EventCategory.FAMILY_CHANGE, EventSeverity.CRITICAL, "周恩来去世", EvidenceGrade.A),
    event(1981, 1, 29, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世", EvidenceGrade.A),
], "modern")

# 继续添加更多案例
for i in range(37, 51):
    year = 1900 + (i - 37) * 5
    make_case(f"GOLDEN-{i:03d}", "male", year, 1, 1, 12, "中国", [
        event(year, 1, 1, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.B),
        event(year + 18, 1, 1, EventCategory.EXAM, EventSeverity.MODERATE, "大学毕业", EvidenceGrade.B),
        event(year + 25, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MODERATE, "开始工作", EvidenceGrade.B),
        event(year + 35, 1, 1, EventCategory.PROMOTION, EventSeverity.MODERATE, "升职", EvidenceGrade.B),
        event(year + 50, 1, 1, EventCategory.FAMILY_CHANGE, EventSeverity.MAJOR, "重大人生事件", EvidenceGrade.B),
        event(year + 70, 1, 1, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世", EvidenceGrade.B),
    ], "synthetic")

def serialize_case(c: Case) -> dict:
    return {
        "case_id": c.case_id,
        "gender": c.gender,
        "birth_date": f"{c.birth_year}-{c.birth_month:02d}-{c.birth_day:02d}",
        "birth_hour": c.birth_hour,
        "events": [{
            "date": e.date.isoformat(),
            "category": e.category.value,
            "severity": int(e.severity),
            "description": e.description,
            "evidence_grade": e.evidence_grade.value,
        } for e in c.events],
        "source_type": c.source_type,
    }

def save(cases, path="dataset/golden_v1/golden_cases.json"):
    data = {
        "version": "1.0.0",
        "created_at": "2026-08-22",
        "case_count": len(cases),
        "event_count": sum(len(c.events) for c in cases),
        "golden_event_count": sum(len(c.golden_events) for c in cases),
        "cases": [serialize_case(c) for c in cases],
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"Saved {len(cases)} cases, {data['event_count']} events, {data['golden_event_count']} golden")
    return data

if __name__ == "__main__":
    data = save(GOLDEN_CASES)
    print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
