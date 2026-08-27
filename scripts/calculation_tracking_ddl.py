"""计算追踪Schema DDL（calculation_runs + calculation_snapshots + sync_results）。

用法:
    cd /d/today/backend
    PYTHONPATH=src python scripts/calculation_tracking_ddl.py migrate
    PYTHONPATH=src python scripts/calculation_tracking_ddl.py status
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

import psycopg2
from tongshu.db.config import get_dsn

DB_NAME = "shuntian_kb"
SCHEMA_PATH = REPO_ROOT / "docs" / "shuntian" / "13_KNOWLEDGE_ONTOLOGY.sql"
MIGRATION_VERSION = "20260821_shuntian_calculation_tracking_v1"

TRACKING_TABLES = ["calculation_runs", "calculation_snapshots", "sync_results"]


def kb_dsn() -> str:
    dsn = get_dsn()
    return dsn.replace("/otcg", f"/{DB_NAME}")


def cmd_migrate() -> None:
    ddl = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = psycopg2.connect(kb_dsn())
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute("SELECT version FROM migration_versions")
        applied = {r[0] for r in cur.fetchall()}
    except psycopg2.errors.UndefinedTable:
        applied = set()
    if MIGRATION_VERSION in applied:
        print(f"[migrate] MIGRATION_VERSION {MIGRATION_VERSION} 已应用,短路跳过")
        conn.close()
        return
    conn.autocommit = False
    try:
        cur.execute(ddl)
        cur.execute(
            "INSERT INTO migration_versions (version) VALUES (%s) ON CONFLICT DO NOTHING",
            (MIGRATION_VERSION,),
        )
        conn.commit()
        print(f"[migrate] 计算追踪Schema落地完成,版本 {MIGRATION_VERSION}")
        print(f"[migrate] 新增表: {', '.join(TRACKING_TABLES)}")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def cmd_status() -> None:
    conn = psycopg2.connect(kb_dsn())
    cur = conn.cursor()
    for t in TRACKING_TABLES:
        try:
            cur.execute(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name=%s", (t,)
            )
            exists = cur.fetchone()[0]
            if exists:
                cur.execute(f"SELECT count(*) FROM {t}")
                count = cur.fetchone()[0]
                print(f"[status] {t:<30} 存在, {count} 行")
            else:
                print(f"[status] {t:<30} 不存在")
        except Exception as e:
            print(f"[status] {t:<30} 错误: {e}")
    conn.close()


def cmd_all() -> None:
    cmd_migrate()
    cmd_status()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"migrate": cmd_migrate, "status": cmd_status, "all": cmd_all}[cmd]()
