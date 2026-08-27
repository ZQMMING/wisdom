"""H1 知识本体层完整迁移入口（V2：含H1-C/H1-D）。

用法:
    cd /d/today/backend
    PYTHONPATH=src python scripts/h1_full_migration.py
    → 运行 DDL（幂等）+ H1-A/B/C/D数据导入 + 状态验证
"""
from __future__ import annotations
import sys
import json
import logging
import psycopg2
from pathlib import Path

# 确保 backend/src 在路径
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"

# DDL绝对路径（不依赖cwd）
DDL_PATH = REPO_ROOT.parent / "docs" / "shuntian" / "13_KNOWLEDGE_ONTOLOGY.sql"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("h1_migration")


def run_ddl(conn: psycopg2.extensions.connection) -> None:
    """执行DDL（幂等）。"""
    ddl_path = DDL_PATH
    if not ddl_path.exists():
        raise FileNotFoundError(f"DDL not found: {ddl_path}")
    sql = ddl_path.read_text(encoding="utf-8")
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    log.info("DDL executed: %s", ddl_path.name)


def run_h1a(conn: psycopg2.extensions.connection) -> dict:
    """H1-A: 河图洛书数据。"""
    from scripts.h1a_knowledge_import import migrate
    return migrate(conn)


def run_h1c(conn: psycopg2.extensions.connection) -> dict:
    """H1-C: 六十甲子 + 干支关系。"""
    from scripts.h1c_ganzhi_import import migrate
    return migrate(conn)


def run_h1d(conn: psycopg2.extensions.connection) -> dict:
    """H1-D: 六十四卦 + 卦象关系。"""
    from scripts.h1d_hexagram_import import migrate
    return migrate(conn)


def verify(conn: psycopg2.extensions.connection) -> None:
    """验证关键表数据量。"""
    cur = conn.cursor()
    tables = [
        "he_tu_numbers", "luo_shu_positions",
        "five_element_relations", "trigrams", "directions",
        "ganzhi_cycles", "stem_branch_relations",
        "hexagrams", "hexagram_relations",
        "calculation_runs", "hl_algorithms",
    ]
    log.info("=== 知识本体层数据量 ===")
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = cur.fetchone()[0]
        bar = "█" * min(cnt // 5, 40)
        log.info("  %-25s %5d  %s", t, cnt, bar)
    cur.close()


def main() -> int:
    log.info("=" * 60)
    log.info("H1 知识本体层 + 计算追踪 完整迁移")
    log.info("=" * 60)

    conn = psycopg2.connect(DB_URI)
    try:
        # Step 1: DDL
        log.info("Step 1: 执行DDL...")
        run_ddl(conn)

        # Step 2: H1-A 河图洛书
        log.info("Step 2: H1-A 河图洛书...")
        stats_a = run_h1a(conn)
        log.info("  H1-A: %s", json.dumps(stats_a, ensure_ascii=False))

        # Step 3: H1-B 五行八卦（已由H1-A脚本处理）
        log.info("Step 3: H1-B 五行八卦（已由H1-A处理）...")

        # Step 4: H1-C 六十甲子
        log.info("Step 4: H1-C 六十甲子...")
        stats_c = run_h1c(conn)
        log.info("  H1-C: %s", json.dumps(stats_c, ensure_ascii=False))

        # Step 5: H1-D 六十四卦
        log.info("Step 5: H1-D 六十四卦...")
        stats_d = run_h1d(conn)
        log.info("  H1-D: %s", json.dumps(stats_d, ensure_ascii=False))

        # Step 6: 验证
        log.info("Step 6: 验证...")
        verify(conn)

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
