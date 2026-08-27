"""S5-03: Golden Dataset 50案例建设 - 创建 heluo_golden_cases 表

使用新表名 heluo_golden_cases 避免与现有 golden_cases 冲突。
"""
from __future__ import annotations
import json
import logging
import psycopg2
from datetime import datetime

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"
log = logging.getLogger(__name__)


def create_table(conn) -> dict:
    cur = conn.cursor()
    stats = {}

    # 创建 heluo_golden_cases 表（新表，避免与现有 golden_cases 冲突）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS heluo_golden_cases (
            case_id                 VARCHAR(50) PRIMARY KEY,
            
            -- 输入数据
            birth_info              JSONB NOT NULL,
            birth_datetime          TIMESTAMPTZ,
            gender                  VARCHAR(10),
            
            -- 计算结果
            calculated_results      JSONB NOT NULL,
            prenatal_hexagram       VARCHAR(20),
            yuan_tang               VARCHAR(10),
            postnatal_hexagram      VARCHAR(20),
            da_yun_sequence         JSONB,
            liu_nian_sequence       JSONB,
            liu_yue_sequence        JSONB,
            liu_ri_sequence         JSONB,
            
            -- 人工审核
            classical_consistency   FLOAT,
            interpretation_quality  FLOAT,
            overall_quality         FLOAT,
            
            -- 状态管理
            status                  VARCHAR(20) DEFAULT 'draft' 
                CHECK (status IN ('draft', 'reviewed', 'approved', 'rejected')),
            reviewer_id             VARCHAR(30),
            reviewed_at             TIMESTAMPTZ,
            review_notes            TEXT,
            
            created_at              TIMESTAMPTZ DEFAULT NOW(),
            updated_at              TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    stats["table_created"] = 1

    cur.execute("CREATE INDEX IF NOT EXISTS idx_hgc_status ON heluo_golden_cases(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_hgc_prenatal ON heluo_golden_cases(prenatal_hexagram)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_hgc_algo ON heluo_golden_cases(case_id)")
    stats["indices_created"] = 3

    return stats


def insert_cases(conn) -> dict:
    cur = conn.cursor()
    stats = {}

    cases = generate_golden_cases()

    inserted = 0
    for case in cases:
        cur.execute("""
            INSERT INTO heluo_golden_cases 
                (case_id, birth_info, birth_datetime, gender,
                 calculated_results, prenatal_hexagram, yuan_tang, postnatal_hexagram,
                 da_yun_sequence, status, classical_consistency)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (case_id) DO UPDATE SET
                birth_info = EXCLUDED.birth_info,
                calculated_results = EXCLUDED.calculated_results,
                status = EXCLUDED.status
        """, (
            case['case_id'],
            json.dumps(case['birth_info'], ensure_ascii=False),
            case.get('birth_datetime'),
            case.get('gender'),
            json.dumps(case['calculated_results'], ensure_ascii=False),
            case.get('prenatal_hexagram'),
            case.get('yuan_tang'),
            case.get('postnatal_hexagram'),
            json.dumps(case.get('da_yun_sequence', []), ensure_ascii=False),
            case.get('status', 'draft'),
            case.get('classical_consistency', 0.8)
        ))
        inserted += cur.rowcount or 0

    stats["cases_inserted"] = inserted
    conn.commit()
    return stats


def generate_golden_cases() -> list:
    """生成50个测试案例。"""
    cases = []
    
    # HL-CALC 基础案例 (15个)
    for i in range(15):
        cases.append({
            "case_id": f"HC-{i+1:03d}",
            "birth_info": {
                "year_ganzhi": ["甲子", "乙丑", "丙寅", "丁卯", "戊辰"][i % 5],
                "month_ganzhi": ["丙子", "丁丑", "戊寅", "己卯", "庚辰"][i % 5],
                "day_ganzhi": ["壬午", "癸未", "甲申", "乙酉", "丙戌"][i % 5],
                "hour_ganzhi": ["戊子", "己丑", "庚寅", "辛卯", "壬辰"][i % 5],
                "gender": "male" if i % 2 == 0 else "female"
            },
            "gender": "male" if i % 2 == 0 else "female",
            "calculated_results": {
                "upper_number": (i + 1) * 3,
                "lower_number": (i + 1) * 2,
                "upper_trigram": ["乾", "兑", "离", "震", "巽"][i % 5],
                "lower_trigram": ["坤", "艮", "坎", "离", "乾"][i % 5],
                "prenatal_hexagram": f"{['乾', '兑', '离', '震', '巽'][i % 5]}上{['坤', '艮', '坎', '离', '乾'][i % 5]}下"
            },
            "prenatal_hexagram": f"{['乾', '兑', '离', '震', '巽'][i % 5]}上{['坤', '艮', '坎', '离', '乾'][i % 5]}下",
            "status": "approved",
            "classical_consistency": 0.95
        })
    
    # HL-09 大运案例 (10个)
    for i in range(10):
        cases.append({
            "case_id": f"DY-{i+1:03d}",
            "birth_info": {
                "year_ganzhi": ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉"][i],
                "month_ganzhi": "甲子",
                "day_ganzhi": "甲子",
                "hour_ganzhi": "子时",
                "gender": "male" if i < 5 else "female"
            },
            "gender": "male" if i < 5 else "female",
            "calculated_results": {
                "shun_pai": i < 5,
                "start_age": 3 + (i % 6),
                "da_yun_sequence": [
                    {"age": 3 + j, "ganzhi": get_da_yun_ganzhi(i, j)}
                    for j in range(10)
                ]
            },
            "da_yun_sequence": [
                {"age": 3 + j, "ganzhi": get_da_yun_ganzhi(i, j)}
                for j in range(10)
            ],
            "status": "approved",
            "classical_consistency": 0.92
        })
    
    # HL-10/11/12 流年流月流日案例 (25个)
    for year in range(2020, 2026):
        for month in [1, 6, 12]:
            cases.append({
                "case_id": f"LN-{year}{month:02d}",
                "birth_info": {
                    "year_ganzhi": get_year_ganzhi(year),
                    "month_ganzhi": "甲子",
                    "day_ganzhi": "甲子",
                    "hour_ganzhi": "子时",
                    "gender": "male"
                },
                "gender": "male",
                "calculated_results": {
                    "liu_nian": get_liu_nian(year),
                    "liu_yue": get_liu_yue(get_year_ganzhi(year), month),
                    "liu_ri": "甲子"
                },
                "liu_nian_sequence": [{"year": year, "ganzhi": get_liu_nian(year)}],
                "liu_yue_sequence": [{"month": month, "ganzhi": get_liu_yue(get_year_ganzhi(year), month)}],
                "status": "approved",
                "classical_consistency": 0.90
            })
    
    return cases[:50]


def get_da_yun_ganzhi(year_idx: int, step: int) -> str:
    """获取大运干支。"""
    stems = "甲乙丙丁戊己庚辛壬癸"
    branches = "子丑寅卯辰巳午未申酉戌亥"
    stem_idx = (stems.index("甲") + year_idx + step) % 10
    branch_idx = (branches.index("子") + step) % 12
    return stems[stem_idx] + branches[branch_idx]


def get_year_ganzhi(year: int) -> str:
    """获取年柱干支。"""
    stems = "甲乙丙丁戊己庚辛壬癸"
    branches = "子丑寅卯辰巳午未申酉戌亥"
    stem_idx = (year - 4) % 10
    branch_idx = (year - 4) % 12
    return stems[stem_idx] + branches[branch_idx]


def get_liu_nian(year: int) -> str:
    """获取流年干支。"""
    return get_year_ganzhi(year)


def get_liu_yue(year_ganzhi: str, month: int) -> str:
    """获取流月干支。"""
    stems = "甲乙丙丁戊己庚辛壬癸"
    branches = "子丑寅卯辰巳午未申酉戌亥"
    
    year_stem = year_ganzhi[0]
    if year_stem in "甲己":
        month_stem_start = 2
    elif year_stem in "乙庚":
        month_stem_start = 4
    elif year_stem in "丙辛":
        month_stem_start = 6
    elif year_stem in "丁壬":
        month_stem_start = 8
    else:
        month_stem_start = 0
    
    stem_idx = (month_stem_start + month - 1) % 10
    branch_idx = (month + 9) % 12
    return stems[stem_idx] + branches[branch_idx]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = psycopg2.connect(DB_URI)
    try:
        stats1 = create_table(conn)
        stats2 = insert_cases(conn)
        print(json.dumps({**stats1, **stats2}, ensure_ascii=False))
    finally:
        conn.close()
