"""H2 时间引擎 DDL + 数据导入 (最终修正版)

根据实际数据库schema调整。
"""
from __future__ import annotations
import json
import logging
import psycopg2

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"

log = logging.getLogger(__name__)

# 24节气数据 (term_id, term_name, term_index, month_sequence, solar_ref)
SOLAR_TERMS = [
    ("立春", "立春", 1, "01", "315"),
    ("雨水", "雨水", 2, "01", "330"),
    ("惊蛰", "惊蛰", 3, "02", "345"),
    ("春分", "春分", 4, "02", "000"),
    ("清明", "清明", 5, "03", "015"),
    ("谷雨", "谷雨", 6, "03", "030"),
    ("立夏", "立夏", 7, "04", "045"),
    ("小满", "小满", 8, "04", "060"),
    ("芒种", "芒种", 9, "05", "075"),
    ("夏至", "夏至", 10, "05", "090"),
    ("小暑", "小暑", 11, "06", "105"),
    ("大暑", "大暑", 12, "06", "120"),
    ("立秋", "立秋", 13, "07", "135"),
    ("处暑", "处暑", 14, "07", "150"),
    ("白露", "白露", 15, "08", "165"),
    ("秋分", "秋分", 16, "08", "180"),
    ("寒露", "寒露", 17, "09", "195"),
    ("霜降", "霜降", 18, "09", "210"),
    ("立冬", "立冬", 19, "10", "225"),
    ("小雪", "小雪", 20, "10", "240"),
    ("大雪", "大雪", 21, "11", "255"),
    ("冬至", "冬至", 22, "11", "270"),
    ("小寒", "小寒", 23, "12", "285"),
    ("大寒", "大寒", 24, "12", "300"),
]


def migrate(conn):
    cur = conn.cursor()
    stats = {}

    # ==================== solar_terms 数据填充 ====================
    inserted = 0
    for term in SOLAR_TERMS:
        term_id, term_name, term_index, month_sequence, solar_ref = term
        cur.execute("""
            INSERT INTO solar_terms 
                (term_id, term_name, term_index, month_sequence, solar_ref)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (term_id) DO NOTHING
        """, (term_id, term_name, term_index, month_sequence, solar_ref))
        inserted += cur.rowcount or 0
    stats["solar_terms"] = inserted

    # ==================== time_cycles 表创建 ====================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS time_cycles (
            cycle_id VARCHAR(30) PRIMARY KEY,
            cycle_type VARCHAR(10) NOT NULL CHECK (cycle_type IN ('年', '月', '日', '时')),
            cycle_start TIMESTAMPTZ NOT NULL,
            cycle_end TIMESTAMPTZ,
            solar_term VARCHAR(4),
            ganzhi_year VARCHAR(4),
            ganzhi_month VARCHAR(4),
            ganzhi_day VARCHAR(4),
            ganzhi_hour VARCHAR(4),
            description TEXT,
            source_refs JSONB NOT NULL DEFAULT '[]',
            status VARCHAR(10) NOT NULL DEFAULT 'draft',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tc_type ON time_cycles(cycle_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tc_start ON time_cycles(cycle_start)")
    stats["time_cycles_table"] = 1

    # ==================== HL-09~12 Algorithm Registry ====================
    # 使用正确的column名和status值
    algorithms = [
        ("HL-ALG-009", "HL-ALG-009", "大运计算", "数理", "CALC", "HL-09",
         json.dumps([{"name": "birth", "type": "HeluoBirthInput"}, {"name": "target_year", "type": "int"}], ensure_ascii=False),
         json.dumps([{"name": "da_yun_stem_branch", "type": "str"}, {"name": "da_yun_hexagram", "type": "str"}], ensure_ascii=False),
         json.dumps([{"page": None, "book_id": "HELUO-LISHU", "chapter_id": "HELUO-LISHU-04"}], ensure_ascii=False),
         json.dumps(["RL-HL-009"], ensure_ascii=False),
         json.dumps([], ensure_ascii=False),
         "RESEARCHING", "V0.1", "卷之四·论大运：阳男阴女顺排，阴男阳女逆排", "待核验"),
        ("HL-ALG-010", "HL-ALG-010", "流年计算", "数理", "CALC", "HL-10",
         json.dumps([{"name": "birth", "type": "HeluoBirthInput"}, {"name": "target_year", "type": "int"}], ensure_ascii=False),
         json.dumps([{"name": "liu_nian_stem_branch", "type": "str"}, {"name": "liu_nian_hexagram", "type": "str"}], ensure_ascii=False),
         json.dumps([{"page": None, "book_id": "HELUO-LISHU", "chapter_id": "HELUO-LISHU-04"}], ensure_ascii=False),
         json.dumps(["RL-HL-010"], ensure_ascii=False),
         json.dumps([], ensure_ascii=False),
         "RESEARCHING", "V0.1", "卷之四·论流年", "待核验"),
        ("HL-ALG-011", "HL-ALG-011", "流月计算", "数理", "CALC", "HL-11",
         json.dumps([{"name": "birth", "type": "HeluoBirthInput"}, {"name": "target_year", "type": "int"}, {"name": "target_month", "type": "int"}], ensure_ascii=False),
         json.dumps([{"name": "liu_yue_stem_branch", "type": "str"}, {"name": "liu_yue_hexagram", "type": "str"}], ensure_ascii=False),
         json.dumps([{"page": None, "book_id": "HELUO-LISHU", "chapter_id": "HELUO-LISHU-04"}], ensure_ascii=False),
         json.dumps(["RL-HL-011"], ensure_ascii=False),
         json.dumps([], ensure_ascii=False),
         "RESEARCHING", "V0.1", "卷之四·论流月", "待核验"),
        ("HL-ALG-012", "HL-ALG-012", "流日计算", "数理", "CALC", "HL-12",
         json.dumps([{"name": "birth", "type": "HeluoBirthInput"}, {"name": "target_date", "type": "date"}], ensure_ascii=False),
         json.dumps([{"name": "liu_ri_stem_branch", "type": "str"}, {"name": "liu_ri_hexagram", "type": "str"}], ensure_ascii=False),
         json.dumps([{"page": None, "book_id": "HELUO-LISHU", "chapter_id": "HELUO-LISHU-05"}], ensure_ascii=False),
         json.dumps(["RL-HL-012"], ensure_ascii=False),
         json.dumps([], ensure_ascii=False),
         "RESEARCHING", "V0.1", "卷之五·论流日", "待核验"),
    ]

    for algo in algorithms:
        algo_id, algo_code, algo_name, algo_domain, algo_type, hl_module, input_spec, output_spec, source_scope, rule_scope, golden_scope, status, version, desc, notes = algo
        cur.execute("""
            INSERT INTO hl_algorithms 
                (algorithm_id, algorithm_code, algorithm_name, algorithm_domain, algorithm_type,
                 hl_module, input_spec, output_spec, source_scope, rule_scope, golden_scope,
                 status, hl_calc_version, description, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (algorithm_id) DO NOTHING
        """, (
            algo_id, algo_code, algo_name, algo_domain, algo_type,
            hl_module, input_spec, output_spec, source_scope, rule_scope, golden_scope,
            status, version, desc, notes
        ))
        stats[algo_id] = cur.rowcount or 0

    conn.commit()
    log.info("H2 migration complete: %s", json.dumps(stats, ensure_ascii=False))
    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = psycopg2.connect(DB_URI)
    try:
        stats = migrate(conn)
        print(json.dumps(stats, ensure_ascii=False))
    finally:
        conn.close()
