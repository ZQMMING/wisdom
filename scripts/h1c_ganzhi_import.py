"""H1-C: 六十甲子数据导入 (修正版)

使用中文天干地支作为外键引用。
"""
from __future__ import annotations
import json
import logging
import psycopg2

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"

log = logging.getLogger(__name__)

STEMS_CN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES_CN = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ELEMENTS = ["木", "木", "火", "火", "土", "土", "金", "金", "水", "水"]
YIN_YANG = ["阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴"]

NA_YIN_LIST = [
    "海中金", "海中金", "炉中火", "炉中火", "大林木", "大林木",
    "路旁土", "路旁土", "剑锋金", "剑锋金", "山头火", "山头火",
    "涧下水", "涧下水", "城头土", "城头土", "白蜡金", "白蜡金",
    "杨柳木", "杨柳木", "泉中水", "泉中水", "屋上土", "屋上土",
    "霹雳火", "霹雳火", "松柏木", "松柏木", "长流水", "长流水",
    "砂中金", "砂中金", "山下火", "山下火", "平地木", "平地木",
    "壁上土", "壁上土", "金簿金", "金簿金", "覆灯火", "覆灯火",
    "天河水", "天河水", "大驿土", "大驿土", "钗钏金", "钗钏金",
    "桑柘木", "桑柘木", "大溪水", "大溪水", "沙中土", "沙中土",
    "天上火", "天上火", "石榴木", "石榴木", "大海水", "大海水"
]


def migrate(conn):
    cur = conn.cursor()
    inserted = 0
    
    for i in range(60):
        stem_cn = STEMS_CN[i % 10]
        branch_cn = BRANCHES_CN[i % 12]
        cycle_id = f"{stem_cn}{branch_cn}"
        
        cur.execute("""
            INSERT INTO ganzhi_cycles 
                (cycle_id, heavenly_stem, earthly_branch, cycle_index, 
                 na_yin, element, description, source_refs, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (cycle_id) DO NOTHING
        """, (
            cycle_id,
            stem_cn,
            branch_cn,
            i + 1,
            NA_YIN_LIST[i],
            ELEMENTS[i % 10],
            f"{cycle_id} - {YIN_YANG[i%10]}{ELEMENTS[i%10]}",
            json.dumps([{"source": "三命通会·卷一", "type": "reference"}], ensure_ascii=False),
            "research"
        ))
        inserted += cur.rowcount or 0
    
    conn.commit()
    log.info("ganzhi_cycles: %d rows inserted", inserted)
    return {"ganzhi_cycles": inserted}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = psycopg2.connect(DB_URI)
    try:
        stats = migrate(conn)
        print(json.dumps(stats, ensure_ascii=False))
    finally:
        conn.close()
