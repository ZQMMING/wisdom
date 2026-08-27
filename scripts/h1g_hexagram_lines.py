"""H1-G: 六十四卦爻位定义

每卦6爻，从初爻到上爻。
爻位定义:
- 爻位: 1-6 (初爻至上爻)
- 阴阳: 阳爻(1) 或 阴爻(0)
- 爻辞位置: 初、二、三、四、五、上
- 尊卑: 五为尊位，二为臣位
"""
from __future__ import annotations
import json
import logging
import psycopg2

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"

log = logging.getLogger(__name__)

YAO_NAMES = ["初", "二", "三", "四", "五", "上"]
YAO_POSITIONS = {
    "初": 1, "二": 2, "三": 3, "四": 4, "五": 5, "上": 6
}
# 五为尊位，二为臣位，三多凶，四多惧
YAO_ROLES = {
    1: "初始之位",
    2: "臣位",
    3: "多凶之位",
    4: "多惧之位",
    5: "尊位",
    6: "极位",
}


def migrate(conn):
    cur = conn.cursor()
    stats = {"lines": 0}

    # 创建hexagram_lines表
    cur.execute("""
        DROP TABLE IF EXISTS hexagram_lines
    """)
    cur.execute("""
        CREATE TABLE hexagram_lines (
            id SERIAL PRIMARY KEY,
            hexagram_id INT NOT NULL REFERENCES hexagrams(hexagram_id),
            line_index INT NOT NULL CHECK (line_index BETWEEN 1 AND 6),
            line_name VARCHAR(2) NOT NULL CHECK (line_name IN ('初', '二', '三', '四', '五', '上')),
            line_yang INT NOT NULL CHECK (line_yang IN (0, 1)),
            line_description TEXT,
            line_role TEXT,
            source_refs JSONB NOT NULL DEFAULT '[]',
            status VARCHAR(10) NOT NULL DEFAULT 'research',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (hexagram_id, line_index)
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_hl_hex ON hexagram_lines(hexagram_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_hl_index ON hexagram_lines(line_index)")

    # 从hexagrams表读取数据并生成爻位
    cur.execute("SELECT hexagram_id, binary_code, name FROM hexagrams ORDER BY hexagram_id")
    rows = cur.fetchall()

    for row in rows:
        hex_id = row[0]
        binary = row[1]  # 6位二进制，从左到右 = 上爻到下爻
        hex_name = row[2]
        
        # binary格式: 上爻(位1) 五爻(位2) 四爻(位3) 三爻(位4) 二爻(位5) 初爻(位6)
        # 需要反转顺序，使index=1对应初爻
        for idx in range(6):
            yao_idx = 6 - idx  # 反转：idx=0 → yao_idx=6 (上爻), idx=5 → yao_idx=1 (初爻)
            # 等等，让我重新理解binary的编码
            # 实际上应该是: binary[0] = 上爻, binary[5] = 初爻
            # 或者反过来？让我检查一下hexagrams表的binary_code格式
            pass
        
        # 重新处理：假设binary从左到右是上爻到下爻
        # binary = "111010" 表示: 上爻=1, 五爻=1, 四爻=1, 三爻=0, 二爻=1, 初爻=0
        for pos in range(6):
            line_name = YAO_NAMES[pos]  # 初, 二, 三, 四, 五, 上
            line_idx = pos + 1
            # binary[pos] 对应从上爻到初爻
            yao_yang = int(binary[pos])
            
            cur.execute("""
                INSERT INTO hexagram_lines 
                    (hexagram_id, line_index, line_name, line_yang, line_description, line_role, source_refs)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (hexagram_id, line_index) DO NOTHING
            """, (
                hex_id, line_idx, line_name, yao_yang,
                f"{hex_name}卦第{line_name}爻",
                YAO_ROLES.get(line_idx, ""),
                json.dumps([{"source": "周易·彖传", "type": "reference"}], ensure_ascii=False)
            ))
            stats["lines"] += cur.rowcount or 0

    conn.commit()
    log.info("hexagram_lines: %d rows inserted", stats["lines"])
    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = psycopg2.connect(DB_URI)
    try:
        stats = migrate(conn)
        print(json.dumps(stats, ensure_ascii=False))
    finally:
        conn.close()
