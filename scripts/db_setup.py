"""OTC-G DB 平台层 CLI(task #57 落地)。

用法(backend/ 下):
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python scripts/db_setup.py status
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python scripts/db_setup.py init
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python scripts/db_setup.py migrate
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python scripts/db_setup.py seed
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python scripts/db_setup.py all

连接:默认 postgres://postgres:postgres@127.0.0.1:5432/otcg,可用环境变量
OTC_G_DATABASE_URL / OTC_G_ADMIN_DATABASE_URL 覆盖。DB 不可达时所有子命令
给出明确提示并退出码 2(不静默成功)。

V1 运行时仍为内存/无 DB;本工具是平台层(Phase C)的可选落地路径。
"""

from __future__ import annotations

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "src"))

from tongshu.db.config import DB_NAME, db_available, get_dsn  # noqa: E402
from tongshu.db.migrate import migrate  # noqa: E402
from tongshu.db.seed import seed  # noqa: E402
from tongshu.db.init_auth import init_auth_schema  # noqa: E402  # B-09 R2: exported so callers can chain auth migration explicitly

EXPECTED_TABLES = [
    "users", "birth_profiles", "calculation_runs", "rule_results", "expressions",
    "rules", "rule_versions", "books", "passages", "evidence",
    "mappings", "mapping_versions", "semantic_objects",
    "audit_runs", "audit_findings", "golden_cases", "prompt_versions",
    "model_versions", "api_requests", "schema_versions", "migration_versions",
]


def _status(dsn: str) -> int:
    ok, err = db_available(dsn)
    print(f"target: {dsn}")
    if not ok:
        print(f"DB unavailable: {err}")
        print("  hint: 启动本地 Postgres 服务或设置 OTC_G_DATABASE_URL")
        return 2
    import psycopg2

    conn = psycopg2.connect(dsn)
    try:
        cur = conn.cursor()
        cur.execute("SELECT current_database(), version()")
        db, ver = cur.fetchone()
        print(f"connected: {db} | {ver.split(',')[0].strip()}")
        cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        )
        present = {r[0] for r in cur.fetchall()}
        missing = [t for t in EXPECTED_TABLES if t not in present]
        print(f"tables: {len(present & set(EXPECTED_TABLES))}/{len(EXPECTED_TABLES)} contract tables present")
        if missing:
            print(f"  missing: {', '.join(missing)}  (run: migrate)")
        for table, label in (("rules", "规则"), ("evidence", "证据"), ("mappings", "映射")):
            cur.execute(f"SELECT count(*) FROM {table}")
            print(f"  {label} seed: {table}={cur.fetchone()[0]}")
        cur.execute(
            "SELECT version, applied_at FROM migration_versions ORDER BY applied_at DESC LIMIT 1"
        )
        row = cur.fetchone()
        print(f"migration: {row[0] if row else '(none)'}")
    finally:
        conn.close()
    return 0


def _init(dsn: str, admin_dsn: str) -> int:
    ok, err = db_available(admin_dsn)
    if not ok:
        print(f"admin DB unavailable: {err}")
        return 2
    import psycopg2

    conn = psycopg2.connect(admin_dsn)
    try:
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (DB_NAME,))
        if cur.fetchone():
            print(f"database {DB_NAME} already exists")
        else:
            # 与契约 11_DATABASE_SCHEMA.sql 相同的库字符集假设(UTF8)
            cur.execute(f'CREATE DATABASE "{DB_NAME}" ENCODING \'UTF8\'')
            print(f"created database {DB_NAME}")
    finally:
        conn.close()
    return 0


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else "status"
    dsn = get_dsn()
    admin = __import__("tongshu.db.config", fromlist=["get_admin_dsn"]).get_admin_dsn()

    if cmd == "status":
        return _status(dsn)
    if cmd == "init":
        return _init(dsn, admin)
    if cmd == "migrate":
        ok, err = db_available(dsn)
        if not ok:
            print(f"DB unavailable: {err}")
            return 2
        res = migrate(dsn)
        print(f"migrate: {res}")
        # B-09 R2: print auth chain status (migrate() chains init_auth_schema() internally)
        if isinstance(res, dict) and "auth_chain" in res:
            print(f"  auth_chain: {res['auth_chain']}")
        return 0
    if cmd == "seed":
        ok, err = db_available(dsn)
        if not ok:
            print(f"DB unavailable: {err}")
            return 2
        counts = seed(dsn)
        print("seed:", ", ".join(f"{k}={v}" for k, v in counts.items()))
        return 0
    if cmd == "all":
        rc = _init(dsn, admin)
        if rc:
            return rc
        rc = migrate(dsn)
        print(f"migrate: {rc}")
        rc = seed(dsn)
        print("seed:", ", ".join(f"{k}={v}" for k, v in rc.items()))
        return _status(dsn)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
