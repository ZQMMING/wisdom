# -*- coding: utf-8 -*-
"""河洛域 D 系列三补表迁移(D-01/D-02/D-03)。

用法:
    PYTHONPATH=src python scripts/shuntian_hl_schema.py migrate   # 幂等落地 12_HL_SCHEMA.sql
    PYTHONPATH=src python scripts/shuntian_hl_schema.py status    # 查询三表状态
    PYTHONPATH=src python scripts/shuntian_hl_schema.py all       # migrate + status

迁移机制:幂等重放(全部 CREATE TABLE IF NOT EXISTS),MIGRATION_VERSION 记入
migration_versions 表。新增表必须改 MIGRATION_VERSION 否则短路跳过。
不修改冻结基线 11_SHUNTIAN_SCHEMA.sql/71 表;本迁移为纯增量(12_HL_SCHEMA.sql)。
权威方向:HL_H1_KICKOFF_AND_RULINGS.md §7。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

import psycopg2  # noqa: E402
from tongshu.db.config import get_dsn  # noqa: E402

DB_NAME = "shuntian_kb"
SCHEMA_PATH = REPO_ROOT / "docs" / "shuntian" / "12_HL_SCHEMA.sql"
MIGRATION_VERSION = "20260821_shuntian_hl_v1_three_registries"

HL_TABLES = ["hl_algorithms", "hl_ambiguities", "hl_algorithm_evidence"]


def kb_dsn() -> str:
    dsn = get_dsn()
    # 把运行时 otcg 换成知识库 shuntian_kb(与 shuntian_db_setup 同构)
    return dsn.replace("/otcg", f"/{DB_NAME}")


def kb_conn() -> psycopg2.extensions.connection:
    return psycopg2.connect(kb_dsn())


def cmd_migrate() -> None:
    ddl = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = kb_conn()
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
        print(f"[migrate] 河洛三补表 DDL 落地完成,版本 {MIGRATION_VERSION}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def cmd_status() -> None:
    conn = kb_conn()
    cur = conn.cursor()
    for t in HL_TABLES:
        try:
            cur.execute(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name=%s",
                (t,),
            )
            exists = cur.fetchone()[0] == 1
            if exists:
                cur.execute(f"SELECT count(*) FROM {t}")
                n = cur.fetchone()[0]
                print(f"[status] {t:28s} 存在,{n} 行")
            else:
                print(f"[status] {t:28s} 缺失")
        except Exception as e:
            print(f"[status] {t:28s} ERR {repr(e)[:120]}")
    try:
        cur.execute("SELECT version FROM migration_versions ORDER BY version DESC")
        print("[status] migration_versions 尾部:", [r[0] for r in cur.fetchall()][:5])
    except Exception as e:
        print("[status] migration_versions ERR", repr(e)[:120])
    conn.close()


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "migrate":
        cmd_migrate()
    elif cmd == "status":
        cmd_status()
    elif cmd == "all":
        cmd_migrate()
        cmd_status()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
