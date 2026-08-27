"""H1完整迁移脚本 - 最终版本

用法:
    cd /d/today/backend
    PYTHONPATH=src python scripts/h1_final_migration.py
"""
import sys
import json
import logging
import psycopg2
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("h1_migration")

def run_ddl(conn):
    """执行DDL"""
    ddl_path = REPO_ROOT.parent / "docs" / "shuntian" / "13_KNOWLEDGE_ONTOLOGY.sql"
    if not ddl_path.exists():
        raise FileNotFoundError(f"DDL not found: {ddl_path}")
    sql = ddl_path.read_text(encoding="utf-8")
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    log.info("DDL executed: %s", ddl_path.name)

def verify_tables(conn):
    """验证表结构和数据量"""
    cur = conn.cursor()
    tables = [
        "he_tu_numbers", "luo_shu_positions",
        "five_element_relations", "trigrams", "directions",
        "ganzhi_cycles", "stem_branch_relations",
        "hexagrams", "hexagram_relations",
        "calculation_runs", "hl_algorithms"
    ]
    log.info("=== 知识本体层数据量 ===")
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
            log.info("  %-25s %5d rows", t, cnt)
        except Exception as e:
            log.warning("  %-25s ERROR: %s", t, e)
    cur.close()

def main():
    log.info("=" * 60)
    log.info("H1 知识本体层完整迁移 V2")
    log.info("=" * 60)
    
    conn = psycopg2.connect(DB_URI)
    try:
        # Step 1: DDL
        log.info("Step 1: 执行DDL...")
        run_ddl(conn)
        
        # Step 2: H1-C 六十甲子
        log.info("Step 2: H1-C 六十甲子...")
        from scripts.h1c_ganzhi_import import migrate as migrate_ganzhi
        stats_c = migrate_ganzhi(conn)
        log.info("  H1-C: %s", json.dumps(stats_c, ensure_ascii=False))
        
        # Step 3: H1-D 六十四卦
        log.info("Step 3: H1-D 六十四卦...")
        from scripts.h1d_hexagram_import import migrate as migrate_hexagrams
        stats_d = migrate_hexagrams(conn)
        log.info("  H1-D: %s", json.dumps(stats_d, ensure_ascii=False))
        
        # Step 4: 验证
        log.info("Step 4: 验证...")
        verify_tables(conn)
        
        log.info("✅ H1 迁移完成")
        return 0
        
    except Exception as e:
        log.error("❌ 迁移失败: %s", e)
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main())
