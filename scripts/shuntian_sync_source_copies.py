"""C13 — source_audits → source_copies 同步（只接受已双源核验）。

原则（M1 Edition Registry 裁决三）: 版本副本（出版社/年份/页码级）未经双源核验
不得登记。source_audits 是"来源审计"（URL/类型/可靠性/已核验 passage 计数），
**不是** source_copy 本身——不能把审计记录直接当副本登记。

双源门（两个条件必须同时满足才可登记为 verified 副本）:
  1. edition_provenance: 副本具备出版社/年份/页码级出处（本表 payload 中须有
     publisher / year / pages 键，且三者齐全）。当前 15 条 audit 均无 → 全拒。
  2. dual_source: 同书存在 ≥2 条独立来源（source_id 相同、audit_id 不同）且
     均为 reliability='high'，且程序化文本比对（cross-verified passages）已记录。

当前数据: 15 条 audit 全部缺 edition_provenance → 双源门全部拒绝，
source_copies 保持诚实为空（0 条 verified / 0 条 pending 被登记）。
本脚本的职责是"机制 + 报告"：列出每本书候选副本及被拒原因，
任何登记都必须经过双源门（含 `--allow-verified-rows` 也无法绕过条件 1）。

红线: 只写 source_copies；不伪造 verified 状态；不碰 rule_status / passage /
rule_versions / DayBoundaryPolicy / evidence_clusters。

用法:
    PYTHONPATH=src python scripts/shuntian_sync_source_copies.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import psycopg2
import psycopg2.extras

from tongshu.db.config import get_dsn  # noqa: E402


def kb_conn():
    dsn = get_dsn().replace("/otcg", "/shuntian_kb")
    return psycopg2.connect(dsn)


# 来源审计 → 副本候选的映射规则：仅"数字化底本/校勘本"且 reliability='high'
# 且 verified_passages>0 的来源才构成候选（现代整理本不算底本副本）。
_CANDIDATE_TYPES = ("数字化底本", "校勘本")


def collect_audits(conn) -> list[dict]:
    cur = conn.cursor()
    cur.execute(
        "SELECT audit_id, source_id, book_id, source_name, source_url, source_type,"
        "       reliability, verified_passages, pending_passages, last_checked"
        " FROM source_audits ORDER BY audit_id"
    )
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def evaluate_candidates(audits: list[dict]) -> dict:
    """返回 per-book 候选与门判定。"""
    by_book: dict[str, list[dict]] = {}
    for a in audits:
        by_book.setdefault(a["source_id"], []).append(a)

    out: dict[str, list[dict]] = {}
    for book, auds in by_book.items():
        cands = [
            a for a in auds
            if a["source_type"] in _CANDIDATE_TYPES
            and a["reliability"] == "high"
            and (a["verified_passages"] or 0) > 0
        ]
        for a in cands:
            a["_high_count"] = sum(
                1 for x in auds if x["reliability"] == "high"
            )
            a["_candidate_reason"] = _gate_reason(a, auds)
            out.setdefault(book, []).append(a)
    return out


def _gate_reason(audit: dict, book_audits: list[dict]) -> str:
    """返回该候选被接受或被拒的原因。"""
    # 条件 1: edition_provenance（出版社/年份/页码）。source_audits 无此数据。
    missing = [k for k in ("publisher", "year", "pages") if k not in audit]
    # source_audits 表结构本身不含 publisher/year/pages 列 → 永远缺失。
    provenance = not missing if missing else True
    # 条件 2: 同书 ≥2 条 high 独立来源。
    high_ids = {a["audit_id"] for a in book_audits if a["reliability"] == "high"}
    dual = len(high_ids) >= 2 and audit["audit_id"] in high_ids

    if not provenance:
        return "REJECT: 缺 edition_provenance（publisher/year/pages 未核验，M1 裁决三）"
    if not dual:
        return f"REJECT: 缺双源（同书 high 来源数={len(high_ids)}，需≥2）"
    return "ACCEPT"


def build_copy_rows(evaluated: dict) -> list[tuple]:
    """仅接受 ACCEPT 候选。当前无 ACCEPT → 空列表（诚实）。"""
    rows = []
    for book, cands in evaluated.items():
        for c in cands:
            if c["_candidate_reason"] != "ACCEPT":
                continue
            payload = {
                "source_url": c["source_url"],
                "source_type": c["source_type"],
                "audit_id": c["audit_id"],
                "last_checked": c["last_checked"],
                "verified_passages": c["verified_passages"],
            }
            copy_id = f"COPY_{c['audit_id']}"
            rows.append(
                (
                    copy_id,
                    c["source_id"],
                    c["source_name"],
                    "SOURCE_COPY",
                    psycopg2.extras.Json(payload),
                    "verified",
                )
            )
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="C13 source_audits→source_copies sync (dual-source gate)")
    ap.add_argument("--dry-run", action="store_true", help="仅打印判定，不写库")
    args = ap.parse_args()

    conn = kb_conn()
    try:
        audits = collect_audits(conn)
        evaluated = evaluate_candidates(audits)
        rows = build_copy_rows(evaluated)

        total_cands = sum(len(v) for v in evaluated.values())
        accepted = len(rows)
        print(f"source_audits={len(audits)} 候选={total_cands} 通过双源门={accepted}")
        for book, cands in evaluated.items():
            for c in cands:
                print(f"  [{book}] {c['audit_id']} {c['source_name']} -> {c['_candidate_reason']}")

        if accepted == 0:
            print("source_copies 保持诚实为空：无候选通过双源门（M1 §3 符合）")

        if args.dry_run or accepted == 0:
            return

        with conn:
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO source_copies (copy_id, source_id, edition_label, copy_type, payload, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (copy_id) DO UPDATE SET
                        source_id=EXCLUDED.source_id,
                        edition_label=EXCLUDED.edition_label,
                        payload=EXCLUDED.payload,
                        status=EXCLUDED.status
                    """,
                    rows,
                )
                cur.execute("SELECT copy_id, status FROM source_copies ORDER BY copy_id")
                for cid, st in cur.fetchall():
                    print(f"synced copy={cid} status={st}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
