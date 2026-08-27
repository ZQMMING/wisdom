"""H1-E: 干支关系数据导入

包含:
1. 天干相生: 甲→丙, 乙→丁, 丙→戊, 丁→己, 戊→庚, 己→辛, 庚→壬, 辛→癸, 壬→甲, 癸→乙
2. 天干相克: 甲→戊, 乙→己, 丙→庚, 丁→辛, 戊→壬, 己→癸, 庚→甲, 辛→乙, 壬→丙, 癸→丁
3. 天干五合: 甲己合, 乙庚合, 丙辛合, 丁壬合, 戊癸合
4. 地支六合: 子丑合, 寅亥合, 卯戌合, 辰酉合, 巳申合, 午未合
5. 地支三合: 申子辰合水, 亥卯未合木, 寅午戌合火, 巳酉丑合金
6. 地支六冲: 子午冲, 丑未冲, 寅申冲, 卯酉冲, 辰戌冲, 巳亥冲
7. 地支六害: 子未害, 丑午害, 寅巳害, 卯辰害, 申亥害, 酉戌害
8. 地支自刑: 辰辰自刑, 午午自刑, 酉酉自刑, 亥亥自刑
"""
from __future__ import annotations
import json
import logging
import psycopg2

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"

log = logging.getLogger(__name__)

STEMS_CN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES_CN = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def migrate(conn):
    cur = conn.cursor()
    stats = {"relations": 0}

    # 创建stem_branch_relations表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stem_branch_relations (
            rel_id VARCHAR(30) PRIMARY KEY,
            rel_type VARCHAR(2) NOT NULL,
            subtype VARCHAR(20),
            source_elem VARCHAR(2) NOT NULL,
            target_elem VARCHAR(2) NOT NULL,
            element_type VARCHAR(10) NOT NULL CHECK (element_type IN ('天干', '地支')),
            description TEXT,
            source_refs JSONB NOT NULL DEFAULT '[]',
            status VARCHAR(10) NOT NULL DEFAULT 'active',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    # ==================== 天干相生 ====================
    sheng_pairs = [
        ("甲", "丙"), ("乙", "丁"), ("丙", "戊"), ("丁", "己"),
        ("戊", "庚"), ("己", "辛"), ("庚", "壬"), ("辛", "癸"),
        ("壬", "甲"), ("癸", "乙"),
    ]
    for i, (s, t) in enumerate(sheng_pairs):
        rel_id = f"SHP-{i+1:03d}"
        cur.execute("""
            INSERT INTO stem_branch_relations 
                (rel_id, rel_type, subtype, source_elem, target_elem, element_type, description, source_refs)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (rel_id) DO NOTHING
        """, (
            rel_id, "生", None, s, t, "天干",
            f"{s}生{t}",
            json.dumps([{"source": "五行大义", "type": "reference"}], ensure_ascii=False)
        ))
        stats["relations"] += cur.rowcount or 0

    # ==================== 天干相克 ====================
    ke_pairs = [
        ("甲", "戊"), ("乙", "己"), ("丙", "庚"), ("丁", "辛"),
        ("戊", "壬"), ("己", "癸"), ("庚", "甲"), ("辛", "乙"),
        ("壬", "丙"), ("癸", "丁"),
    ]
    for i, (s, t) in enumerate(ke_pairs):
        rel_id = f"KEP-{i+1:03d}"
        cur.execute("""
            INSERT INTO stem_branch_relations 
                (rel_id, rel_type, subtype, source_elem, target_elem, element_type, description, source_refs)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (rel_id) DO NOTHING
        """, (
            rel_id, "克", None, s, t, "天干",
            f"{s}克{t}",
            json.dumps([{"source": "五行大义", "type": "reference"}], ensure_ascii=False)
        ))
        stats["relations"] += cur.rowcount or 0

    # ==================== 天干五合 ====================
    he_pairs = [
        ("甲", "己"), ("乙", "庚"), ("丙", "辛"), ("丁", "壬"), ("戊", "癸"),
    ]
    for i, (s, t) in enumerate(he_pairs):
        rel_id = f"STH-{i+1:03d}"
        cur.execute("""
            INSERT INTO stem_branch_relations 
                (rel_id, rel_type, subtype, source_elem, target_elem, element_type, description, source_refs)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (rel_id) DO NOTHING
        """, (
            rel_id, "合", "天干五合", s, t, "天干",
            f"{s}{t}合",
            json.dumps([{"source": "三命通会", "type": "reference"}], ensure_ascii=False)
        ))
        stats["relations"] += cur.rowcount or 0

    # ==================== 地支六合 ====================
    zhi_he_pairs = [
        ("子", "丑"), ("寅", "亥"), ("卯", "戌"),
        ("辰", "酉"), ("巳", "申"), ("午", "未"),
    ]
    for i, (s, t) in enumerate(zhi_he_pairs):
        rel_id = f"ZHHE-{i+1:03d}"
        cur.execute("""
            INSERT INTO stem_branch_relations 
                (rel_id, rel_type, subtype, source_elem, target_elem, element_type, description, source_refs)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (rel_id) DO NOTHING
        """, (
            rel_id, "合", "地支六合", s, t, "地支",
            f"{s}{t}六合",
            json.dumps([{"source": "渊海子平", "type": "reference"}], ensure_ascii=False)
        ))
        stats["relations"] += cur.rowcount or 0

    # ==================== 地支三合 ====================
    sanhe_groups = [
        (["申", "子", "辰"], "水"),
        (["亥", "卯", "未"], "木"),
        (["寅", "午", "戌"], "火"),
        (["巳", "酉", "丑"], "金"),
    ]
    sid = 1
    for group, element in sanhe_groups:
        for i in range(len(group)):
            for j in range(i+1, len(group)):
                rel_id = f"ZHSAN-{sid:03d}"
                cur.execute("""
                    INSERT INTO stem_branch_relations 
                        (rel_id, rel_type, subtype, source_elem, target_elem, element_type, description, source_refs)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (rel_id) DO NOTHING
                """, (
                    rel_id, "合", "地支三合", group[i], group[j], "地支",
                    f"{group[i]}{group[j]}三合{element}",
                    json.dumps([{"source": "滴天髓", "type": "reference"}], ensure_ascii=False)
                ))
                stats["relations"] += cur.rowcount or 0
                sid += 1

    # ==================== 地支六冲 ====================
    chong_pairs = [
        ("子", "午"), ("丑", "未"), ("寅", "申"),
        ("卯", "酉"), ("辰", "戌"), ("巳", "亥"),
    ]
    for i, (s, t) in enumerate(chong_pairs):
        rel_id = f"ZHC-{i+1:03d}"
        cur.execute("""
            INSERT INTO stem_branch_relations 
                (rel_id, rel_type, subtype, source_elem, target_elem, element_type, description, source_refs)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (rel_id) DO NOTHING
        """, (
            rel_id, "冲", None, s, t, "地支",
            f"{s}{t}六冲",
            json.dumps([{"source": "子平真诠", "type": "reference"}], ensure_ascii=False)
        ))
        stats["relations"] += cur.rowcount or 0

    # ==================== 地支六害 ====================
    hai_pairs = [
        ("子", "未"), ("丑", "午"), ("寅", "巳"),
        ("卯", "辰"), ("申", "亥"), ("酉", "戌"),
    ]
    for i, (s, t) in enumerate(hai_pairs):
        rel_id = f"ZHH-{i+1:03d}"
        cur.execute("""
            INSERT INTO stem_branch_relations 
                (rel_id, rel_type, subtype, source_elem, target_elem, element_type, description, source_refs)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (rel_id) DO NOTHING
        """, (
            rel_id, "害", None, s, t, "地支",
            f"{s}{t}六害",
            json.dumps([{"source": "三命通会", "type": "reference"}], ensure_ascii=False)
        ))
        stats["relations"] += cur.rowcount or 0

    # ==================== 地支自刑 ====================
    zixing = ["辰", "午", "酉", "亥"]
    for i, elem in enumerate(zixing):
        rel_id = f"ZXX-{i+1:03d}"
        cur.execute("""
            INSERT INTO stem_branch_relations 
                (rel_id, rel_type, subtype, source_elem, target_elem, element_type, description, source_refs)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (rel_id) DO NOTHING
        """, (
            rel_id, "刑", "自刑", elem, elem, "地支",
            f"{elem}{elem}自刑",
            json.dumps([{"source": "渊海子平", "type": "reference"}], ensure_ascii=False)
        ))
        stats["relations"] += cur.rowcount or 0

    conn.commit()
    log.info("stem_branch_relations: %d rows inserted", stats["relations"])
    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = psycopg2.connect(DB_URI)
    try:
        stats = migrate(conn)
        print(json.dumps(stats, ensure_ascii=False))
    finally:
        conn.close()
