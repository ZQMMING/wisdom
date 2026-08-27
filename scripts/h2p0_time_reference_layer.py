"""H2-P0: TIME_REFERENCE_LAYER DDL + 数据

建立时间参考层，包含:
1. solar_terms (已存在，24行)
2. time_reference (新建，存储基准参数)
3. ganzhi_base (新建，干支基准表)

冻结后不可修改，后续只能扩展。
"""
from __future__ import annotations
import json
import logging
import psycopg2
from datetime import datetime

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"
log = logging.getLogger(__name__)


def migrate(conn) -> dict:
    cur = conn.cursor()
    stats = {}

    # ==================== time_reference 表 ====================
    # 存储时间计算的全局基准参数
    cur.execute("""
        CREATE TABLE IF NOT EXISTS time_reference (
            param_key   VARCHAR(50) PRIMARY KEY,
            param_value TEXT NOT NULL,
            param_type  VARCHAR(20) NOT NULL CHECK (param_type IN ('date', 'number', 'string', 'json')),
            source_ref  TEXT,
            verified_at TIMESTAMPTZ,
            verified_by VARCHAR(50),
            notes       TEXT,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    stats["time_reference_table"] = 1

    # 插入基准参数
    params = [
        ("jiazi_base_date", "0004-01-01", "date", 
         "《协纪辨方书》卷一: '昔在庖牺，始造甲子'", 
         "2026-08-21", "待核验"),
        ("solar_longitude_step", "15", "number",
         "《时宪书》: 黄经每节15度",
         "2026-08-21", "待核验"),
        ("true_solar_time_default", "true", "string",
         "默认启用真太阳时",
         "2026-08-21", "配置项"),
        ("longitude_base", "120.0", "number",
         "东经120度基准（北京时间）",
         "2026-08-21", "配置项"),
        ("equation_of_time_source", "precomputed_table", "string",
         "均时差数据来源: precomputed_table | astronomical",
         "2026-08-21", "配置项"),
    ]
    
    inserted_params = 0
    for key, value, ptype, source, verified_at, notes in params:
        cur.execute("""
            INSERT INTO time_reference 
                (param_key, param_value, param_type, source_ref, verified_at, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (param_key) DO NOTHING
        """, (key, value, ptype, source, verified_at, notes))
        inserted_params += cur.rowcount or 0
    stats["time_reference_inserted"] = inserted_params

    # ==================== ganzhi_base 表 ====================
    # 干支基准表: 存储天干地支的数学定义
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ganzhi_base (
            id          SERIAL PRIMARY KEY,
            ganzhi_type VARCHAR(10) NOT NULL CHECK (ganzhi_type IN ('stem', 'branch')),
            index       SMALLINT NOT NULL,
            symbol      VARCHAR(4) NOT NULL,
            element     VARCHAR(10) NOT NULL CHECK (element IN ('木', '火', '土', '金', '水')),
            yinyang     VARCHAR(10) NOT NULL CHECK (yinyang IN ('阳', '阴')),
            source_ref  TEXT,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    stats["ganzhi_base_table"] = 1

    # 天干数据
    stems_data = [
        (0, "甲", "木", "阳"), (1, "乙", "木", "阴"),
        (2, "丙", "火", "阳"), (3, "丁", "火", "阴"),
        (4, "戊", "土", "阳"), (5, "己", "土", "阴"),
        (6, "庚", "金", "阳"), (7, "辛", "金", "阴"),
        (8, "壬", "水", "阳"), (9, "癸", "水", "阴"),
    ]
    
    # 地支数据
    branches_data = [
        (0, "子", "水", "阳"), (1, "丑", "土", "阴"),
        (2, "寅", "木", "阳"), (3, "卯", "木", "阴"),
        (4, "辰", "土", "阳"), (5, "巳", "火", "阴"),
        (6, "午", "火", "阳"), (7, "未", "土", "阴"),
        (8, "申", "金", "阳"), (9, "酉", "金", "阴"),
        (10, "戌", "土", "阳"), (11, "亥", "水", "阴"),
    ]
    
    inserted_base = 0
    for idx, symbol, element, yinyang in stems_data:
        cur.execute("""
            INSERT INTO ganzhi_base (ganzhi_type, index, symbol, element, yinyang, source_ref)
            VALUES ('stem', %s, %s, %s, %s, '《河洛理数》')
            ON CONFLICT DO NOTHING
        """, (idx, symbol, element, yinyang))
        inserted_base += cur.rowcount or 0
    
    for idx, symbol, element, yinyang in branches_data:
        cur.execute("""
            INSERT INTO ganzhi_base (ganzhi_type, index, symbol, element, yinyang, source_ref)
            VALUES ('branch', %s, %s, %s, %s, '《河洛理数》')
            ON CONFLICT DO NOTHING
        """, (idx, symbol, element, yinyang))
        inserted_base += cur.rowcount or 0
    stats["ganzhi_base_inserted"] = inserted_base

    # ==================== 创建索引 ====================
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tr_key ON time_reference(param_key)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_gb_type ON ganzhi_base(ganzhi_type)")
    stats["indices_created"] = 2

    conn.commit()
    log.info("TIME_REFERENCE_LAYER migration complete: %s", json.dumps(stats, ensure_ascii=False))
    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = psycopg2.connect(DB_URI)
    try:
        stats = migrate(conn)
        print(json.dumps(stats, ensure_ascii=False))
    finally:
        conn.close()
