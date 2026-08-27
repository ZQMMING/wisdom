"""H1-F: 六十四卦卦象关系数据

包含:
1. 错卦 (阴阳全反)
2. 综卦 (旋转180度 = 上下卦互换)
3. 互卦 (取2,3,4爻为上卦，3,4,5爻为下卦)
4. 变卦 (初爻变)
"""
from __future__ import annotations
import json
import logging
import psycopg2

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"

log = logging.getLogger(__name__)

# 八卦定义
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

# 文王卦序
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


def binary_inverse(b: str) -> str:
    """二进制取反"""
    return "".join("1" if c == "0" else "0" for c in b)


def find_hexagram_by_binary(hexagrams, binary):
    """根据二进制码找卦ID"""
    for h in hexagrams:
        if h["binary"] == binary:
            return h["id"]
    return None


def migrate(conn):
    cur = conn.cursor()
    stats = {"relations": 0}

    # 从hexagrams表读取数据
    cur.execute("SELECT hexagram_id, name, upper_trigram_name, lower_trigram_name, binary_code FROM hexagrams ORDER BY hexagram_id")
    hexagrams = []
    for row in cur.fetchall():
        hexagrams.append({
            "id": row[0],
            "name": row[1],
            "upper": row[2],
            "lower": row[3],
            "binary": row[4],
        })

    # 创建索引
    by_id = {h["id"]: h for h in hexagrams}
    by_binary = {}
    for h in hexagrams:
        by_binary[h["binary"]] = h["id"]

    # 创建hexagram_relations表
    cur.execute("""
        DROP TABLE IF EXISTS hexagram_relations
    """)
    cur.execute("""
        CREATE TABLE hexagram_relations (
            id SERIAL PRIMARY KEY,
            source_hexagram INT NOT NULL REFERENCES hexagrams(hexagram_id),
            relation_type VARCHAR(2) NOT NULL CHECK (relation_type IN ('错', '综', '互', '变')),
            target_hexagram INT NOT NULL REFERENCES hexagrams(hexagram_id),
            description TEXT,
            source_refs JSONB NOT NULL DEFAULT '[]',
            status VARCHAR(10) NOT NULL DEFAULT 'active',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_hr_source ON hexagram_relations(source_hexagram)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_hr_target ON hexagram_relations(target_hexagram)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_hr_type ON hexagram_relations(relation_type)")

    # ==================== 错卦 ====================
    cuo_count = 0
    for h in hexagrams:
        inv = binary_inverse(h["binary"])
        target_id = by_binary.get(inv)
        if target_id and target_id != h["id"]:
            rel_id = f"HR-CUO-{cuo_count+1:03d}"
            cur.execute("""
                INSERT INTO hexagram_relations 
                    (source_hexagram, relation_type, target_hexagram, description, source_refs)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                h["id"], "错", target_id,
                f"{h['name']}错为{by_id[target_id]['name']}",
                json.dumps([{"source": "周易·系辞", "type": "reference"}], ensure_ascii=False)
            ))
            stats["relations"] += cur.rowcount or 0
            cuo_count += 1

    # ==================== 综卦 ====================
    zong_count = 0
    for h in hexagrams:
        # 综卦 = 旋转180度 = 上下卦互换
        # 上卦变下卦，下卦变上卦
        target_id = by_binary.get(h["binary"])
        # 重新计算：上下卦互换
        h_data = by_id[h["id"]]
        # 获取上下卦的二进制
        upper_tri = TRIGRAMS.get(h_data["upper"], ("?", "?", "?"))[1]
        lower_tri = TRIGRAMS.get(h_data["lower"], ("?", "?", "?"))[1]
        zong_binary = lower_tri + upper_tri
        target_id = by_binary.get(zong_binary)
        
        if target_id and target_id != h["id"]:
            cur.execute("""
                INSERT INTO hexagram_relations 
                    (source_hexagram, relation_type, target_hexagram, description, source_refs)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                h["id"], "综", target_id,
                f"{h['name']}综为{by_id[target_id]['name']}",
                json.dumps([{"source": "周易·系辞", "type": "reference"}], ensure_ascii=False)
            ))
            stats["relations"] += cur.rowcount or 0
            zong_count += 1

    # ==================== 互卦 ====================
    hu_count = 0
    for h in hexagrams:
        # 互卦：取2,3,4爻为上卦，3,4,5爻为下卦
        binary = h["binary"]
        if len(binary) == 6:
            hu_upper = binary[2:5]  # 第3-5位
            hu_lower = binary[1:4]  # 第2-4位
            hu_binary = hu_upper + hu_lower
            target_id = by_binary.get(hu_binary)
            
            if target_id and target_id != h["id"]:
                cur.execute("""
                    INSERT INTO hexagram_relations 
                        (source_hexagram, relation_type, target_hexagram, description, source_refs)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    h["id"], "互", target_id,
                    f"{h['name']}互为{by_id[target_id]['name']}",
                    json.dumps([{"source": "周易·杂卦", "type": "reference"}], ensure_ascii=False)
                ))
                stats["relations"] += cur.rowcount or 0
                hu_count += 1

    # ==================== 变卦 (初爻变) ====================
    bian_count = 0
    for h in hexagrams:
        binary = h["binary"]
        # 初爻变（最右边一位）
        new_binary = binary[:-1] + ("1" if binary[-1] == "0" else "0")
        target_id = by_binary.get(new_binary)
        
        if target_id:
            cur.execute("""
                INSERT INTO hexagram_relations 
                    (source_hexagram, relation_type, target_hexagram, description, source_refs)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                h["id"], "变", target_id,
                f"{h['name']}初爻变为{by_id[target_id]['name']}",
                json.dumps([{"source": "周易·说卦", "type": "reference"}], ensure_ascii=False)
            ))
            stats["relations"] += cur.rowcount or 0
            bian_count += 1

    conn.commit()
    log.info("hexagram_relations: %d rows inserted (错:%d, 综:%d, 互:%d, 变:%d)",
             stats["relations"], cuo_count, zong_count, hu_count, bian_count)
    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = psycopg2.connect(DB_URI)
    try:
        stats = migrate(conn)
        print(json.dumps(stats, ensure_ascii=False))
    finally:
        conn.close()
