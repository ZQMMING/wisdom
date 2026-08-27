"""H1-A 河图洛书数据导入脚本。

用法:
    cd /d/today/backend
    PYTHONPATH=src python scripts/h1a_knowledge_import.py
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

import psycopg2
from tongshu.db.config import get_dsn

DB_NAME = "shuntian_kb"


def kb_dsn() -> str:
    dsn = get_dsn()
    return dsn.replace("/otcg", f"/{DB_NAME}")


# ---------------------------------------------------------------------------
# 1. 河图数数据（天一生水，地六成之...）
# ---------------------------------------------------------------------------
HE_TU_DATA = [
    # number, number_type, heaven_earth, direction, direction_zh, element, gua, description
    (1, "生数", "天", "NORTH", "北", "水", "坎", "天一生水，地六成之"),
    (2, "生数", "地", "SOUTH", "南", "火", "离", "地二生火，天七成之"),
    (3, "生数", "天", "EAST", "东", "木", "震", "天三生木，地八成之"),
    (4, "生数", "地", "WEST", "西", "金", "兑", "地四生金，天九成之"),
    (5, "生数", "天", "CENTER", "中", "土", "中宫", "天五生土，地十成之"),
    (6, "成数", "地", "NORTH", "北", "水", "坎", "地六成之（成数=生数+5）"),
    (7, "成数", "天", "SOUTH", "南", "火", "离", "天七成之"),
    (8, "成数", "地", "EAST", "东", "木", "震", "地八成之"),
    (9, "成数", "天", "WEST", "西", "金", "兑", "天九成之"),
    (10, "成数", "地", "CENTER", "中", "土", "中宫", "地十成之（遇十不用）"),
]

LUO_SHU_DATA = [
    # position, palace_zh, direction, direction_zh, element, gua, formula
    (1, "坎", "NORTH", "北", "水", "坎", "戴九履一，履一为坎（北）"),
    (2, "坤", "SOUTH-WEST", "西南", "土", "坤", "二黑在右肩属坤（西南）"),
    (3, "震", "EAST", "东", "木", "震", "左三属震（东）"),
    (4, "巽", "SOUTH-EAST", "东南", "木", "巽", "四碧在左肩属巽（东南）"),
    (5, "中宫", "CENTER", "中", "土", "中宫", "五数居中，以维八方"),
    (6, "乾", "NORTH-WEST", "西北", "金", "乾", "六白近右足属乾（西北）"),
    (7, "兑", "WEST", "西", "金", "兑", "七赤在右属兑（西）"),
    (8, "艮", "SOUTH-EAST", "东北", "土", "艮", "八白近左足属艮（东北）"),
    (9, "离", "SOUTH", "南", "火", "离", "九紫近头属离（南）"),
]

FIVE_ELEMENT_DATA = [
    # from, to, relation_type, description
    ("木", "火", "生", "木生火：木燃成火"),
    ("火", "土", "生", "火生土：火烧成灰"),
    ("土", "金", "生", "土生金：矿出於土"),
    ("金", "水", "生", "金生水：金凝成露"),
    ("水", "木", "生", "水生木：水润养木"),
    ("木", "土", "克", "木克土：木根固土"),
    ("土", "水", "克", "土克水：堤防蓄水"),
    ("水", "火", "克", "水克火：水灭火"),
    ("火", "金", "克", "火克金：火熔金属"),
    ("金", "木", "克", "金克木：金伐树木"),
    ("木", "金", "侮", "木侮金：木盛反伤金（乘侮反向）"),
    ("金", "木", "乘", "金乘木：金强克木过度"),
    ("水", "土", "侮", "水侮土：水盛反溃土堤"),
    ("土", "水", "乘", "土乘水：土强压水过度"),
    ("火", "水", "侮", "火侮水：火盛反蒸水"),
    ("水", "火", "乘", "水乘火：水强灭火过度"),
    ("木", "木", "比和", "同类相助"),
    ("火", "火", "比和", "同类相助"),
    ("土", "土", "比和", "同类相助"),
    ("金", "金", "比和", "同类相助"),
    ("水", "水", "比和", "同类相助"),
]

TRIGRAM_DATA = [
    # gua_id, name_zh, name_en, lines, nature_zh, nature_en, direction, element, family
    ("QIAN", "乾", "Heaven", "111", "天", "Heaven", "NW", "金", "父"),
    ("KUN", "坤", "Earth", "000", "地", "Earth", "SW", "土", "母"),
    ("ZHEN", "震", "Thunder", "100", "雷", "Thunder", "E", "木", "长男"),
    ("XUN", "巽", "Wind", "011", "风", "Wind", "SE", "木", "长女"),
    ("KAN", "坎", "Water", "010", "水", "Water", "N", "水", "中男"),
    ("LI", "离", "Fire", "101", "火", "Fire", "S", "火", "中女"),
    ("GEN", "艮", "Mountain", "001", "山", "Mountain", "NE", "土", "少男"),
    ("DUUI", "兑", "Lake", "110", "泽", "Lake", "W", "金", "少女"),
]

DIRECTION_DATA = [
    # dir_id, dir_zh, dir_en, angle, element, description
    ("N", "北", "North", 0, "水", "北方属水，河图一六水"),
    ("S", "南", "South", 180, "火", "南方属火，河图二七火"),
    ("E", "东", "East", 90, "木", "东方属木，河图三八木"),
    ("W", "西", "West", 270, "金", "西方属金，河图四九金"),
    ("CENTER", "中", "Center", None, "土", "中央属土，河图五土"),
    ("NE", "东北", "North-East", 45, "土", "艮宫，东北方"),
    ("NW", "西北", "North-West", 315, "金", "乾宫，西北方"),
    ("SE", "东南", "South-East", 135, "木", "巽宫，东南方"),
    ("SW", "西南", "South-West", 225, "土", "坤宫，西南方"),
]

STEM_DATA = [
    # stem, yin_yang, number_heaven(洛书), number_hetu(河图), element, direction
    ("甲", "阳", 3, 8, "木", "E"),
    ("乙", "阴", 4, 9, "木", "E"),
    ("丙", "阳", 7, 2, "火", "S"),
    ("丁", "阴", 8, 1, "火", "S"),
    ("戊", "阳", 5, 5, "土", "CENTER"),
    ("己", "阴", 5, 10, "土", "CENTER"),
    ("庚", "阳", 9, 4, "金", "W"),
    ("辛", "阴", 6, 3, "金", "W"),
    ("壬", "阳", 1, 6, "水", "N"),
    ("癸", "阴", 2, 7, "水", "N"),
]

BRANCH_DATA = [
    # branch, yin_yang, number_hetu, number_luoshu, element, direction, shichou
    ("子", "阳", 1, 1, "水", "N", "23:00-01:00"),
    ("丑", "阴", 6, 2, "土", "NE", "01:00-03:00"),
    ("寅", "阳", 3, 3, "木", "E", "03:00-05:00"),
    ("卯", "阴", 8, 4, "木", "E", "05:00-07:00"),
    ("辰", "阳", 5, 5, "土", "NE", "07:00-09:00"),
    ("巳", "阴", 10, 6, "火", "S", "09:00-11:00"),
    ("午", "阳", 2, 9, "火", "S", "11:00-13:00"),
    ("未", "阴", 7, 8, "土", "SW", "13:00-15:00"),
    ("申", "阳", 4, 7, "金", "W", "15:00-17:00"),
    ("酉", "阴", 9, 6, "金", "W", "17:00-19:00"),
    ("戌", "阳", 5, 5, "土", "NW", "19:00-21:00"),
    ("亥", "阴", 10, 1, "水", "N", "21:00-23:00"),
]


def main():
    conn = psycopg2.connect(kb_dsn())
    conn.autocommit = True
    cur = conn.cursor()

    # ---- 1. he_tu_numbers ----
    print("[H1-A] 插入河图数...")
    for row in HE_TU_DATA:
        cur.execute("""
            INSERT INTO he_tu_numbers
                (number, number_type, heaven_earth, direction, direction_zh,
                 element, gua, description, source_refs, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (number) DO UPDATE SET
                number_type=EXCLUDED.number_type,
                heaven_earth=EXCLUDED.heaven_earth,
                direction=EXCLUDED.direction,
                direction_zh=EXCLUDED.direction_zh,
                element=EXCLUDED.element,
                gua=EXCLUDED.gua,
                description=EXCLUDED.description
        """, (*row, '[]', 'research'))
    print(f"  → {len(HE_TU_DATA)} 行")

    # ---- 2. luo_shu_positions ----
    print("[H1-A] 插入洛书九宫...")
    for row in LUO_SHU_DATA:
        cur.execute("""
            INSERT INTO luo_shu_positions
                (position, palace_zh, direction, direction_zh, element, gua, formula, source_refs, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (position) DO UPDATE SET
                palace_zh=EXCLUDED.palace_zh,
                direction=EXCLUDED.direction,
                direction_zh=EXCLUDED.direction_zh,
                element=EXCLUDED.element,
                gua=EXCLUDED.gua,
                formula=EXCLUDED.formula
        """, (*row, '[]', 'research'))
    print(f"  → {len(LUO_SHU_DATA)} 行")

    # ---- 3. five_element_relations ----
    print("[H1-A] 插入五行生克...")
    for row in FIVE_ELEMENT_DATA:
        cur.execute("""
            INSERT INTO five_element_relations
                (from_element, to_element, relation_type, description, source_refs, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (*row, '[]', 'research'))
    print(f"  → {len(FIVE_ELEMENT_DATA)} 行")

    # ---- 4. trigrams ----
    print("[H1-A] 插入八卦...")
    for row in TRIGRAM_DATA:
        cur.execute("""
            INSERT INTO trigrams
                (gua_id, gua_name_zh, gua_name_en, trigram_lines, nature_zh, nature_en,
                 direction, element, family, source_refs, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (gua_id) DO UPDATE SET
                gua_name_zh=EXCLUDED.gua_name_zh,
                trigram_lines=EXCLUDED.trigram_lines,
                element=EXCLUDED.element,
                family=EXCLUDED.family
        """, (*row, '[]', 'research'))
    print(f"  → {len(TRIGRAM_DATA)} 行")

    # ---- 5. directions ----
    print("[H1-A] 插入方位...")
    for row in DIRECTION_DATA:
        cur.execute("""
            INSERT INTO directions
                (dir_id, dir_zh, dir_en, angle_deg, element, description, source_refs, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (dir_id) DO UPDATE SET
                dir_zh=EXCLUDED.dir_zh,
                element=EXCLUDED.element
        """, (*row, '[]', 'research'))
    print(f"  → {len(DIRECTION_DATA)} 行")

    # ---- 6. stem_mapping ----
    print("[H1-A] 插入天干映射...")
    for row in STEM_DATA:
        cur.execute("""
            INSERT INTO stem_mapping
                (stem, yin_yang, number_heaven, number_hetu, element, direction, source_refs, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (stem) DO UPDATE SET
                number_heaven=EXCLUDED.number_heaven,
                number_hetu=EXCLUDED.number_hetu,
                element=EXCLUDED.element
        """, (*row, '[]', 'research'))
    print(f"  → {len(STEM_DATA)} 行")

    # ---- 7. branch_mapping ----
    print("[H1-A] 插入地支映射...")
    for row in BRANCH_DATA:
        cur.execute("""
            INSERT INTO branch_mapping
                (branch, yin_yang, number_hetu, number_luoshu, element, direction, shichou, source_refs, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (branch) DO UPDATE SET
                number_hetu=EXCLUDED.number_hetu,
                number_luoshu=EXCLUDED.number_luoshu,
                element=EXCLUDED.element,
                shichou=EXCLUDED.shichou
        """, (*row, '[]', 'research'))
    print(f"  → {len(BRANCH_DATA)} 行")

    conn.close()
    print("\n[H1-A] 完成。所有数据状态=research（待印刷版逐字核验后升verified）")


if __name__ == "__main__":
    main()
