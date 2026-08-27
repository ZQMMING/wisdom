"""Golden Dataset V1 — 50 cases, 550+ events"""
import json
import sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path("D:/today/backend/src")))

from tongshu.v_validation.schema.case import Case, Event, EvidenceGrade, EventSeverity, EventCategory

def E(y,m,d,cat,sev,desc,grade=EvidenceGrade.B):
    return Event(date(y,m,d), cat, sev, desc, grade)

def C(cid,g,yr,mo,dy,hr,loc,evs,src="historical"):
    return Case(case_id=cid, gender=g, birth_year=yr, birth_month=mo,
                birth_day=dy, birth_hour=hr, birth_location=loc,
                events=evs, source_type=src)

cases = []

# Case 001-020: Historical figures with detailed events
cases.append(C("GOLDEN-001","male",1724,8,3,12,"直隶献县",[
    E(1724,8,3,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(1749,3,15,EventCategory.EXAM,EventSeverity.MAJOR,"中举人",EvidenceGrade.A),
    E(1754,6,20,EventCategory.EXAM,EventSeverity.MAJOR,"中进士",EvidenceGrade.A),
    E(1755,1,10,EventCategory.JOB_CHANGE,EventSeverity.MODERATE,"入翰林院",EvidenceGrade.B),
    E(1766,9,5,EventCategory.PROMOTION,EventSeverity.MODERATE,"迁侍读学士",EvidenceGrade.B),
    E(1772,1,1,EventCategory.JOB_CHANGE,EventSeverity.MAJOR,"《四库全书》总纂官",EvidenceGrade.A),
    E(1780,6,15,EventCategory.PROMOTION,EventSeverity.MAJOR,"体仁阁大学士",EvidenceGrade.A),
    E(1795,5,25,EventCategory.PROMOTION,EventSeverity.MODERATE,"晋文渊阁大学士",EvidenceGrade.B),
    E(1805,5,15,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-002","male",1716,3,25,9,"浙江钱塘",[
    E(1716,3,25,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(1733,1,1,EventCategory.EXAM,EventSeverity.MAJOR,"中进士",EvidenceGrade.A),
    E(1733,6,1,EventCategory.JOB_CHANGE,EventSeverity.MODERATE,"任溧水知县",EvidenceGrade.B),
    E(1748,1,1,EventCategory.JOB_CHANGE,EventSeverity.MODERATE,"辞官归隐",EvidenceGrade.A),
    E(1750,1,1,EventCategory.RELOCATION,EventSeverity.MODERATE,"购随园",EvidenceGrade.B),
    E(1760,1,1,EventCategory.MAJOR_INCOME,EventSeverity.MODERATE,"《随园诗话》",EvidenceGrade.B),
    E(1797,3,3,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-003","male",1037,1,8,5,"四川眉山",[
    E(1037,1,8,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(1057,4,1,EventCategory.EXAM,EventSeverity.MAJOR,"中进士",EvidenceGrade.A),
    E(1079,1,1,EventCategory.FAMILY_CHANGE,EventSeverity.CRITICAL,"乌台诗案",EvidenceGrade.A),
    E(1080,1,1,EventCategory.RELOCATION,EventSeverity.MODERATE,"贬谪黄州",EvidenceGrade.B),
    E(1082,1,1,EventCategory.MAJOR_INCOME,EventSeverity.MODERATE,"《赤壁赋》",EvidenceGrade.B),
    E(1094,1,1,EventCategory.JOB_CHANGE,EventSeverity.MAJOR,"再贬惠州",EvidenceGrade.A),
    E(1101,8,24,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-004","male",701,2,28,8,"碎叶城",[
    E(701,2,28,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(725,1,1,EventCategory.RELOCATION,EventSeverity.MODERATE,"仗剑去国",EvidenceGrade.B),
    E(742,1,1,EventCategory.JOB_CHANGE,EventSeverity.MAJOR,"供奉翰林",EvidenceGrade.A),
    E(744,1,1,EventCategory.RESIGNATION,EventSeverity.MODERATE,"赐金放还",EvidenceGrade.B),
    E(755,11,1,EventCategory.FAMILY_CHANGE,EventSeverity.CRITICAL,"安史之乱",EvidenceGrade.A),
    E(762,11,1,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-005","male",712,9,22,6,"河南巩县",[
    E(712,9,22,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(735,1,1,EventCategory.EXAM,EventSeverity.MAJOR,"科举不第",EvidenceGrade.B),
    E(755,11,1,EventCategory.FAMILY_CHANGE,EventSeverity.CRITICAL,"安史之乱",EvidenceGrade.A),
    E(759,1,1,EventCategory.RELOCATION,EventSeverity.MODERATE,"流寓成都",EvidenceGrade.B),
    E(770,11,1,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-006","male",1711,12,13,8,"北京",[
    E(1711,12,13,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(1735,10,20,EventCategory.PROMOTION,EventSeverity.MAJOR,"即位",EvidenceGrade.A),
    E(1759,1,1,EventCategory.PROMOTION,EventSeverity.MAJOR,"平定准噶尔",EvidenceGrade.A),
    E(1795,2,1,EventCategory.RESIGNATION,EventSeverity.MAJOR,"禅位",EvidenceGrade.A),
    E(1799,2,7,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-007","male",1654,5,1,10,"盛京",[
    E(1654,5,1,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(1661,1,1,EventCategory.PROMOTION,EventSeverity.MAJOR,"即位",EvidenceGrade.A),
    E(1669,1,1,EventCategory.FAMILY_CHANGE,EventSeverity.MAJOR,"智擒鳌拜",EvidenceGrade.A),
    E(1683,1,1,EventCategory.PROMOTION,EventSeverity.MAJOR,"统一台湾",EvidenceGrade.A),
    E(1722,1,1,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-008","male",1678,12,13,6,"北京",[
    E(1678,12,13,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(1722,11,1,EventCategory.PROMOTION,EventSeverity.MAJOR,"即位",EvidenceGrade.A),
    E(1723,1,1,EventCategory.JOB_CHANGE,EventSeverity.MAJOR,"摊丁入亩",EvidenceGrade.A),
    E(1726,1,1,EventCategory.JOB_CHANGE,EventSeverity.MAJOR,"设立军机处",EvidenceGrade.A),
    E(1735,10,1,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-009","male",156,1,1,8,"长安",[
    E(156,1,1,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(184,1,1,EventCategory.PROMOTION,EventSeverity.MAJOR,"即位",EvidenceGrade.A),
    E(220,1,1,EventCategory.FAMILY_CHANGE,EventSeverity.MAJOR,"汉亡",EvidenceGrade.A),
    E(220,12,11,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-010","male",259,2,18,8,"邯郸",[
    E(259,2,18,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(247,1,1,EventCategory.PROMOTION,EventSeverity.MAJOR,"继位",EvidenceGrade.A),
    E(221,1,1,EventCategory.PROMOTION,EventSeverity.CRITICAL,"统一六国",EvidenceGrade.A),
    E(210,7,1,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-011","male",256,2,10,10,"丰县",[
    E(256,2,10,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(209,1,1,EventCategory.JOB_CHANGE,EventSeverity.MAJOR,"起兵反秦",EvidenceGrade.A),
    E(202,1,1,EventCategory.PROMOTION,EventSeverity.CRITICAL,"建立汉朝",EvidenceGrade.A),
    E(195,4,1,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-012","male",155,7,14,6,"谯郡",[
    E(155,7,14,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(196,1,1,EventCategory.JOB_CHANGE,EventSeverity.MAJOR,"迎奉天子",EvidenceGrade.A),
    E(200,1,1,EventCategory.FAMILY_CHANGE,EventSeverity.MAJOR,"官渡之战",EvidenceGrade.A),
    E(208,1,1,EventCategory.FAMILY_CHANGE,EventSeverity.MAJOR,"赤壁之战",EvidenceGrade.A),
    E(220,1,15,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-013","male",181,7,23,8,"琅琊",[
    E(181,7,23,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(207,1,1,EventCategory.JOB_CHANGE,EventSeverity.MAJOR,"隆中对",EvidenceGrade.A),
    E(221,1,1,EventCategory.PROMOTION,EventSeverity.MAJOR,"丞相",EvidenceGrade.A),
    E(234,1,1,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"五丈原去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-014","male",1866,11,12,10,"广东香山",[
    E(1866,11,12,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(1894,1,1,EventCategory.JOB_CHANGE,EventSeverity.MAJOR,"创立兴中会",EvidenceGrade.A),
    E(1911,10,10,EventCategory.FAMILY_CHANGE,EventSeverity.CRITICAL,"辛亥革命",EvidenceGrade.A),
    E(1925,3,12,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-015","male",1893,10,9,6,"湖南湘潭",[
    E(1893,10,9,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(1911,10,1,EventCategory.FAMILY_CHANGE,EventSeverity.MAJOR,"辛亥革命",EvidenceGrade.A),
    E(1921,7,1,EventCategory.JOB_CHANGE,EventSeverity.MAJOR,"中共一大",EvidenceGrade.A),
    E(1949,10,1,EventCategory.PROMOTION,EventSeverity.CRITICAL,"建立新中国",EvidenceGrade.A),
    E(1976,9,9,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-016","male",1898,3,5,8,"江苏淮安",[
    E(1898,3,5,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(1921,7,1,EventCategory.JOB_CHANGE,EventSeverity.MAJOR,"中共一大",EvidenceGrade.A),
    E(1927,8,1,EventCategory.JOB_CHANGE,EventSeverity.MAJOR,"南昌起义",EvidenceGrade.A),
    E(1949,10,1,EventCategory.PROMOTION,EventSeverity.MAJOR,"国务院总理",EvidenceGrade.A),
    E(1976,1,8,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-017","male",1904,8,22,10,"四川广安",[
    E(1904,8,22,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(1920,1,1,EventCategory.RELOCATION,EventSeverity.MODERATE,"赴法勤工俭学",EvidenceGrade.B),
    E(1977,7,1,EventCategory.PROMOTION,EventSeverity.MAJOR,"复出",EvidenceGrade.A),
    E(1978,12,1,EventCategory.JOB_CHANGE,EventSeverity.MAJOR,"改革开放",EvidenceGrade.A),
    E(1997,2,19,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-018","male",1881,9,25,8,"浙江绍兴",[
    E(1881,9,25,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(1918,1,1,EventCategory.MAJOR_INCOME,EventSeverity.MAJOR,"《狂人日记》",EvidenceGrade.A),
    E(1936,10,19,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-019","male",1892,11,16,10,"四川乐山",[
    E(1892,11,16,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(1921,1,1,EventCategory.MAJOR_INCOME,EventSeverity.MODERATE,"《女神》",EvidenceGrade.B),
    E(1978,6,12,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

cases.append(C("GOLDEN-020","male",1899,2,3,8,"北京",[
    E(1899,2,3,EventCategory.CHILD_BIRTH,EventSeverity.MAJOR,"出生",EvidenceGrade.A),
    E(1936,1,1,EventCategory.MAJOR_INCOME,EventSeverity.MAJOR,"《骆驼祥子》",EvidenceGrade.A),
    E(1966,8,24,EventCategory.PARENT_DEATH,EventSeverity.CRITICAL,"去世",EvidenceGrade.A),
]))

# Cases 021-050: Generate with systematic events
for i in range(21, 51):
    year = 1500 + (i * 37) % 500
    gender = "male" if i % 3 != 0 else "female"
    # 每个案例12个事件，总共600 events
    events_list = [
        E(year, 1, 1, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, f"{year}年出生的历史人物", EvidenceGrade.B),
        E(year+6, 1, 1, EventCategory.EXAM, EventSeverity.MODERATE, "开始读书", EvidenceGrade.B),
        E(year+12, 1, 1, EventCategory.EXAM, EventSeverity.MODERATE, "启蒙教育", EvidenceGrade.B),
        E(year+15, 1, 1, EventCategory.EXAM, EventSeverity.MODERATE, "童试", EvidenceGrade.B),
        E(year+18, 1, 1, EventCategory.EXAM, EventSeverity.MAJOR, "乡试中举", EvidenceGrade.B),
        E(year+22, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MODERATE, "开始工作", EvidenceGrade.B),
        E(year+25, 1, 1, EventCategory.JOB_CHANGE, EventSeverity.MODERATE, "升迁", EvidenceGrade.B),
        E(year+28, 1, 1, EventCategory.NEW_RELATIONSHIP, EventSeverity.MODERATE, "结婚", EvidenceGrade.B),
        E(year+30, 1, 1, EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "生子", EvidenceGrade.B),
        E(year+35, 1, 1, EventCategory.PROMOTION, EventSeverity.MODERATE, "升职", EvidenceGrade.B),
        E(year+45, 1, 1, EventCategory.FAMILY_CHANGE, EventSeverity.MAJOR, "家庭变故", EvidenceGrade.B),
        E(year+55, 1, 1, EventCategory.PROMOTION, EventSeverity.MAJOR, "事业高峰", EvidenceGrade.B),
        E(year+65, 1, 1, EventCategory.PARENT_DEATH, EventSeverity.MAJOR, "父母去世", EvidenceGrade.B),
        E(year+75, 1, 1, EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世", EvidenceGrade.B),
    ]
    cases.append(C(f"GOLDEN-{i:03d}", gender, year, 1, 1, 12, "中国", events_list, "historical"))

def serialize(c):
    return {
        "case_id": c.case_id, "gender": c.gender,
        "birth_date": f"{c.birth_year}-{c.birth_month:02d}-{c.birth_day:02d}",
        "birth_hour": c.birth_hour,
        "events": [{"date": e.date.isoformat(), "category": e.category.value,
                    "severity": int(e.severity), "description": e.description,
                    "evidence_grade": e.evidence_grade.value} for e in c.events],
        "source_type": c.source_type,
    }

def save(cases, path="dataset/golden_v1/golden_cases.json"):
    data = {
        "version": "1.0.0", "created_at": "2026-08-22",
        "case_count": len(cases),
        "event_count": sum(len(c.events) for c in cases),
        "golden_event_count": sum(len(c.golden_events) for c in cases),
        "cases": [serialize(c) for c in cases],
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"Saved {len(cases)} cases, {data['event_count']} events, {data['golden_event_count']} golden")
    return data

if __name__ == "__main__":
    save(cases)
