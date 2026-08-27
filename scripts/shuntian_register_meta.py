"""SHUNTIAN 知识库元数据登记 CLI(C1-C3,Codex 交接 Phase A)。

一次性登记三张 CORE 元数据表(建库时留空的表,见 01_ERD_SCHEMA §3):
    C1 schema_versions — SHUNTIAN schema 版本首行(v1.0)
    C2 engine_versions — 五引擎版本(bazi/ziwei/huangli/rules/reasoning)
    C3 agents          — 三 Agent 分工(CODEX/CLAUDE/HERMES,手册 SHARED 协议 §22)

纪律:
    * 幂等 —— 全部 `ON CONFLICT DO NOTHING`,可反复执行,不重复造行。
    * 只增不改 —— 已登记行绝不覆盖(元数据登记是审计基线,不是刷新)。
    * 数据写入由本脚本负责,Codex 只读走 backend/src/tongshu/db/kb_reader.py。

用法:
    PYTHONPATH=src python scripts/shuntian_register_meta.py          # 登记(幂等)
    PYTHONPATH=src python scripts/shuntian_register_meta.py --check  # 只查不改,打印三表现状
"""

from __future__ import annotations

import sys
from pathlib import Path

import psycopg2
import psycopg2.extras

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

from tongshu.db.config import get_dsn  # noqa: E402

DB_NAME = "shuntian_kb"

# C1 —— SHUNTIAN schema 版本首行(建库 2026-08-20,十二域七十一表)
SCHEMA_VERSION_ROWS = [
    (
        "v1.0",
        "SHUNTIAN 知识库十二域七十一表底座（建库 2026-08-20）",
    ),
]

# C2 —— 五引擎版本(engine_id, engine_version, system, notes)
# 口径对齐运行时 backend 各引擎;system 与手册 §2 引擎系统名一致。
ENGINE_VERSION_ROWS = [
    ("BAZI_ENGINE", "1.0.0", "bazi", "八字引擎(四柱/十神/大运/神煞)"),
    ("ZIWEI_ENGINE", "1.0.0", "ziwei", "紫微斗数引擎(安星/四化/大限/流年)"),
    ("HUANGLI_ENGINE", "1.0.0", "huangli", "黄历引擎(宜忌/冲煞/吉神/建除)"),
    ("RULES_ENGINE", "1.0.0", "rules", "规则引擎(规则生命周期/激活裁决)"),
    ("REASONING_ENGINE", "1.0.0", "reasoning", "推理引擎(信号合成/交叉分析/审计门)"),
]

# C3 —— 三 Agent 分工(agent_id, role, permissions JSONB)
AGENT_ROWS = [
    (
        "CODEX",
        "Principal Engineering Agent",
        ["code:read", "code:write", "engine:run", "test:run", "deploy:write"],
    ),
    (
        "CLAUDE",
        "Knowledge + Database Engineer",
        ["schema:read", "schema:write", "evidence:write", "rule_registry:write"],
    ),
    (
        "HERMES",
        "Research + Audit Agent",
        ["research:read", "audit:write"],
    ),
]


def kb_dsn() -> str:
    return get_dsn().replace("/otcg", f"/{DB_NAME}")


def register(conn) -> None:
    cur = conn.cursor()
    n_schema = n_engine = n_agent = 0
    # with conn: 事务上下文——正常退出自动 commit,异常自动 rollback
    with conn:
        cur.executemany(
            "INSERT INTO schema_versions (schema_version, description) VALUES (%s, %s) "
            "ON CONFLICT (schema_version) DO NOTHING",
            SCHEMA_VERSION_ROWS,
        )
        n_schema = cur.rowcount
        cur.executemany(
            "INSERT INTO engine_versions (engine_id, engine_version, system, notes) "
            "VALUES (%s, %s, %s, %s) "
            "ON CONFLICT (engine_id) DO NOTHING",
            ENGINE_VERSION_ROWS,
        )
        n_engine = cur.rowcount
        # permissions 是 JSONB 列;Python list 会被 psycopg2 适配成 text[],
        # 需用 extras.Json 显式包装成 JSONB。
        agent_rows = [
            (aid, role, psycopg2.extras.Json(perms)) for aid, role, perms in AGENT_ROWS
        ]
        cur.executemany(
            "INSERT INTO agents (agent_id, role, permissions) VALUES (%s, %s, %s) "
            "ON CONFLICT (agent_id) DO NOTHING",
            agent_rows,
        )
        n_agent = cur.rowcount
    print(f"[meta] schema_versions 新增 {n_schema} 行")
    print(f"[meta] engine_versions 新增 {n_engine} 行")
    print(f"[meta] agents          新增 {n_agent} 行")


def check(conn) -> None:
    cur = conn.cursor()
    cur.execute("SELECT schema_version, description FROM schema_versions ORDER BY applied_at")
    print("[check] schema_versions:")
    for r in cur.fetchall():
        print(f"  - {r[0]}: {r[1]}")
    cur.execute("SELECT engine_id, engine_version, system, status FROM engine_versions ORDER BY engine_id")
    print("[check] engine_versions:")
    for r in cur.fetchall():
        print(f"  - {r[0]} / {r[1]} / {r[2]} / {r[3]}")
    cur.execute("SELECT agent_id, role, permissions FROM agents ORDER BY agent_id")
    print("[check] agents:")
    for r in cur.fetchall():
        print(f"  - {r[0]} / {r[1]} / {r[2]}")


def main() -> None:
    conn = psycopg2.connect(kb_dsn())
    try:
        if "--check" in sys.argv[1:]:
            check(conn)
        else:
            register(conn)
            check(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
