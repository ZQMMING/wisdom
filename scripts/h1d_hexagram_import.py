"""H1-D: 六十四卦数据导入 (简化版)

只插入hexagrams表的基本数据。
"""
from __future__ import annotations
import json
import logging
import psycopg2

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"

log = logging.getLogger(__name__)

TRIGRAMS = {
    1: ("坎", "010", "水"),
    2: ("坤", "000", "土"),
    3: ("震", "100", "木"),
    4: ("巽", "011", "木"),
    5: ("中", "111", "土"),
    6: ("乾", "111", "金"),
    7: ("兑", "110", "金"),
    8: ("艮", "001", "土"),
    9: ("离", "101", "火"),
}

# 文王卦序 - 上卦,下卦
HEXAGRAM_ORDER = [
    (6, 6), (6, 7), (6, 9), (6, 8), (6, 3), (6, 4), (6, 1), (6, 2),
    (7, 6), (7, 7), (7, 9), (7, 8), (7, 3), (7, 4), (7, 1), (7, 2),
    (9, 6), (9, 7), (9, 9), (9, 8), (9, 3), (9, 4), (9, 1), (9, 2),
    (3, 6), (3, 7), (3, 9), (3, 8), (3, 3), (3, 4), (3, 1), (3, 2),
    (4, 6), (4, 7), (4, 9), (4, 8), (4, 3), (4, 4), (4, 1), (4, 2),
    (1, 6), (1, 7), (1, 9), (1, 8), (1, 3), (1, 4), (1, 1), (1, 2),
    (8, 6), (8, 7), (8, 9), (8, 8), (8, 3), (8, 4), (8, 1), (8, 2),
    (2, 6), (2, 7), (2, 9), (2, 8), (2, 3), (2, 4), (2, 1), (2, 2),
]


def migrate(conn):
    cur = conn.cursor()
    
    # 创建hexagrams表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hexagrams (
            hexagram_id INT PRIMARY KEY,
            name VARCHAR(6) NOT NULL,
            upper_trigram INT NOT NULL,
            lower_trigram INT NOT NULL,
            upper_trigram_name VARCHAR(2),
            lower_trigram_name VARCHAR(2),
            binary_code VARCHAR(6) NOT NULL,
            nature TEXT,
            source_refs JSONB NOT NULL DEFAULT '[]',
            status TEXT NOT NULL DEFAULT 'research',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    
    inserted = 0
    for idx, (upper, lower) in enumerate(HEXAGRAM_ORDER, 1):
        upper_name = TRIGRAMS[upper][0]
        lower_name = TRIGRAMS[lower][0]
        upper_binary = TRIGRAMS[upper][1]
        lower_binary = TRIGRAMS[lower][1]
        binary = upper_binary + lower_binary
        name = f"{upper_name}{lower_name}"
        
        cur.execute("""
            INSERT INTO hexagrams 
                (hexagram_id, name, upper_trigram, lower_trigram,
                 upper_trigram_name, lower_trigram_name, binary_code,
                 source_refs, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (hexagram_id) DO NOTHING
        """, (
            idx, name, upper, lower,
            upper_name, lower_name, binary,
            json.dumps([{"source": "周易", "type": "reference"}], ensure_ascii=False),
            "research"
        ))
        inserted += cur.rowcount or 0
    
    conn.commit()
    log.info("hexagrams: %d rows inserted", inserted)
    return {"hexagrams": inserted}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = psycopg2.connect(DB_URI)
    try:
        stats = migrate(conn)
        print(json.dumps(stats, ensure_ascii=False))
    finally:
        conn.close()
