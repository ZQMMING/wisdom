"""C12 — evidence_clusters 回填（CLUSTER-ZPZ-YONGSHEN-ANCHOR）。

数据源: backend/data/evidence_meta/evidence_clusters.json（M2-B Evidence Review
产出的权威簇定义，含 30 条 member + 逐字一致断言 0 mismatch）。
目标: shuntian_kb.evidence_clusters 表（11_SHUNTIAN_SCHEMA.sql §evidence_clusters，
目前 0 行）。

投影说明（表结构是简化投影，非全量 JSON）:
  - cluster_id    <- json.cluster_id
  - cluster_name  <- json.anchor_text（锚句原文，非虚构标签）
  - member_ids    <- json.member_evidence_ids（JSONB）
  - anchor_id     <- json.passage_id（锚 passage；簇无单一锚证据，锚实体=passage）
  - created_at    <- now()（表无 json.reviewed_at 列，保留在 JSON 权威源）

幂等: ON CONFLICT (cluster_id) DO UPDATE（数据源=权威，重跑收敛）。
红线: 只写 evidence_clusters；不碰 rule_status / passage / rule_versions /
DayBoundaryPolicy / source_copies。

用法:
    PYTHONPATH=src python scripts/shuntian_backfill_clusters.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import psycopg2
import psycopg2.extras

from tongshu.db.config import get_dsn  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
CLUSTERS_JSON = REPO_ROOT / "backend" / "data" / "evidence_meta" / "evidence_clusters.json"


def kb_conn():
    dsn = get_dsn().replace("/otcg", "/shuntian_kb")
    return psycopg2.connect(dsn)


def collect_clusters() -> list[dict]:
    data = json.loads(CLUSTERS_JSON.read_text(encoding="utf-8"))
    if data.get("kind") != "evidence_clusters":
        raise SystemExit(f"{CLUSTERS_JSON.name}: kind mismatch")
    return data.get("clusters", [])


def main() -> None:
    ap = argparse.ArgumentParser(description="C12 evidence_clusters backfill")
    ap.add_argument("--dry-run", action="store_true", help="仅打印，不写库")
    args = ap.parse_args()

    clusters = collect_clusters()
    rows = []
    for c in clusters:
        rows.append(
            (
                c["cluster_id"],
                c["anchor_text"],
                psycopg2.extras.Json(list(c["member_evidence_ids"])),
                c["passage_id"],
            )
        )

    if args.dry_run:
        for cid, name, member_list, anchor in (
            (cid, name, members.adapted, anchor) for cid, name, members, anchor in rows
        ):
            print(f"[dry-run] cluster={cid} anchor={anchor} members={len(member_list)}")
        print(f"[dry-run] {len(rows)} cluster(s) would be upserted")
        return

    conn = kb_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO evidence_clusters
                        (cluster_id, cluster_name, member_ids, anchor_id)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (cluster_id) DO UPDATE SET
                        cluster_name=EXCLUDED.cluster_name,
                        member_ids=EXCLUDED.member_ids,
                        anchor_id=EXCLUDED.anchor_id
                    """,
                    rows,
                )
                cur.execute("SELECT cluster_id, jsonb_array_length(member_ids) FROM evidence_clusters ORDER BY cluster_id")
                for cid, n in cur.fetchall():
                    print(f"upserted cluster={cid} members={n}")
    except psycopg2.Error as e:
        print(f"DB error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
