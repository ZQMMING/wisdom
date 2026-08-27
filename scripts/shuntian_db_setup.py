"""SHUNTIAN 知识库建库 CLI。

用法:
    PYTHONPATH=src python scripts/shuntian_db_setup.py init      # 创建 shuntian_kb 库(不存在则建)
    PYTHONPATH=src python scripts/shuntian_db_setup.py migrate   # 幂等落地十二域 DDL
    PYTHONPATH=src python scripts/shuntian_db_setup.py status    # 表清单 + schema 版本 + 行数
    PYTHONPATH=src python scripts/shuntian_db_setup.py all       # init + migrate + status

权威 DDL:docs/shuntian/11_SHUNTIAN_SCHEMA.sql
迁移机制:幂等重放(全部 CREATE TABLE IF NOT EXISTS),MIGRATION_VERSION 记入
migration_versions 表。新增表必须改 MIGRATION_VERSION 否则短路跳过。
"""

from __future__ import annotations

import sys
from pathlib import Path

import psycopg2
import psycopg2.extensions

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

from tongshu.db.config import get_dsn, get_admin_dsn  # noqa: E402

DB_NAME = "shuntian_kb"
SCHEMA_PATH = REPO_ROOT / "docs" / "shuntian" / "11_SHUNTIAN_SCHEMA.sql"
MIGRATION_VERSION = "20260820_shuntian_v1_twelvedomains_71tables_sc_nullable"


def admin_conn() -> psycopg2.extensions.connection:
    return psycopg2.connect(get_admin_dsn())


def kb_dsn() -> str:
    dsn = get_dsn()
    # 把 otcg 换成 shuntian_kb(DSN 里是 /otcg)
    return dsn.replace("/otcg", f"/{DB_NAME}")


def kb_conn():
    return psycopg2.connect(kb_dsn())


def _db_exists(cur) -> bool:
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    return cur.fetchone() is not None


def cmd_init() -> None:
    conn = admin_conn()
    conn.autocommit = True
    cur = conn.cursor()
    if _db_exists(cur):
        print(f"[init] 库 {DB_NAME} 已存在,跳过创建")
    else:
        cur.execute(f'CREATE DATABASE {DB_NAME}')
        print(f"[init] 已创建库 {DB_NAME}")
    conn.close()


def cmd_migrate() -> None:
    ddl = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = kb_conn()
    conn.autocommit = True
    cur = conn.cursor()
    # 首次落地时 migration_versions 尚不存在,视为未应用
    try:
        cur.execute("SELECT version FROM migration_versions")
        applied = {r[0] for r in cur.fetchall()}
    except psycopg2.errors.UndefinedTable:
        applied = set()
    if MIGRATION_VERSION in applied:
        print(f"[migrate] MIGRATION_VERSION {MIGRATION_VERSION} 已应用,短路跳过")
        conn.close()
        return
    # 记录开始前的事务化执行:先应用 DDL 再写版本
    conn.autocommit = False
    try:
        cur.execute(ddl)
        cur.execute(
            "INSERT INTO migration_versions (version) VALUES (%s) ON CONFLICT DO NOTHING",
            (MIGRATION_VERSION,),
        )
        conn.commit()
        print(f"[migrate] DDL 落地完成,版本 {MIGRATION_VERSION}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def cmd_status() -> None:
    conn = kb_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"
    )
    tables = [r[0] for r in cur.fetchall()]
    print(f"[status] shuntian_kb 共 {len(tables)} 张表")
    for t in tables:
        cur.execute(f'SELECT count(*) FROM "{t}"')
        n = cur.fetchone()[0]
        cur.execute(
            "SELECT obj_description(c.oid) FROM pg_class c WHERE c.relname=%s AND c.relkind='r'",
            (t,),
        )
        comment = cur.fetchone()[0]
        tail = f"  -- {comment[:60]}" if comment else ""
        print(f"  - {t:32s} {n:5d}{tail}")
    cur.execute("SELECT schema_version FROM schema_versions ORDER BY applied_at")
    ver = cur.fetchall()
    print(f"[status] schema_versions: {ver if ver else '空(未登记)'}")
    conn.close()


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "init":
        cmd_init()
    elif cmd == "migrate":
        cmd_migrate()
    elif cmd == "status":
        cmd_status()
    elif cmd == "all":
        cmd_init()
        cmd_migrate()
        cmd_status()
    else:
        print(f"未知命令: {cmd}")
        sys.exit(2)


if __name__ == "__main__":
    main()
