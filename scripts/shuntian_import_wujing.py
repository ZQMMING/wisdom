"""五经知识库 → shuntian_kb 全量导入器。

数据源:D:\today\开发资料\参考资料\五经知识库(权威经典证据层,终审 2026-08-20)
导入目标:sources/passages/concepts/principles/rules/evidence/source_audits/source_criticism
状态保留:verified / verified_excerpt / disputed / cross_ref_pending / pending(终审 R1-R5)
不变量:evidence.verification_status 级联镜像源 passage 状态(库内不变量)
诚实纪律:五经无独立 CLAIM 层,claims 表不虚构;source_criticism 只填数据源可确定字段。
幂等:ON CONFLICT DO UPDATE(数据源=权威,重跑可收敛)。

用法:
    PYTHONPATH=src python scripts/shuntian_import_wujing.py [--dry-run]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import psycopg2.extras

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tongshu.db.config import get_dsn  # noqa: E402

KB_ROOT = Path(r"D:\today\开发资料\参考资料\五经知识库")
BOOK_IDS = ["DTS", "PZZQ", "QTBJ", "SMTH", "YHZP"]


def kb_conn():
    dsn = get_dsn().replace("/otcg", "/shuntian_kb")
    return psycopg2.connect(dsn)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_passages() -> list[dict]:
    """遍历 03_PASSAGES/<book>/<book>_P0_passages.json + P1(YHZP)。"""
    out = []
    for book in BOOK_IDS:
        base = KB_ROOT / "03_PASSAGES" / book
        for f in sorted(base.glob(f"{book}_*passages.json")):
            d = load_json(f)
            out.extend(d.get("passages", []))
    return out


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    print(f"[wujing] 数据源: {KB_ROOT}")
    print(f"[wujing] {'DRY-RUN(只统计不写库)' if dry_run else '写库模式'}")

    stats = {"sources": 0, "passages": 0, "concepts": 0, "principles": 0,
             "rules": 0, "evidence": 0, "source_audits": 0, "source_criticism": 0}
    violation_count = 0

    # ---- 1. BOOKS → sources (+ source_criticism 派生) ----
    books = []
    for book in BOOK_IDS:
        p = KB_ROOT / "01_BOOKS" / f"0{BOOK_IDS.index(book)+1}_{book}.json"
        books.append(load_json(p))

    # ---- 2. PASSAGES 预载(用于证据级联校验 + concept_tags) ----
    passages = collect_passages()
    passage_status = {p["passage_id"]: p["verification_status"] for p in passages}

    conn = kb_conn()
    if not dry_run:
        cur = conn.cursor()

    def exec_many(sql: str, rows: list[tuple], page_size=200):
        if dry_run:
            stats[sql.split(" INTO ")[1].split(" (")[0].strip().lower().replace("sources", "sources")] = 0
            return
        psycopg2.extras.execute_values(cur, sql, rows, page_size=page_size)

    # --- sources ---
    src_rows = []
    for b in books:
        src_rows.append((
            b["book_id"], b["title_zh"], b.get("title_en"), b.get("author_or_attribution"),
            b.get("author_or_attribution"),  # claimed_author 暂以署名归属占位(诚实:非托名考证)
            b.get("dynasty"), None, b.get("edition_source"), None, None,
            b.get("chapter_count"), b.get("volume_count"), "classical",
            b.get("verification_status", "pending"), b.get("notes"),
        ))
    stats["sources"] = len(src_rows)

    # --- source_criticism(只填数据源可确定字段) ---
    sc_rows = []
    for b in books:
        sc_rows.append((
            b["book_id"], b.get("author_or_attribution"), b.get("dynasty"),
            None, b.get("edition_source"), None, None, None, None,
            b.get("notes"), None,
        ))
    stats["source_criticism"] = len(sc_rows)

    # --- source_audits ---
    aud_rows = []
    for book in BOOK_IDS:
        p = KB_ROOT / "08_SOURCE_AUDIT" / f"AUD_{book}.json"
        d = load_json(p)
        for a in d.get("source_audits", []):
            aud_rows.append((
                a["audit_id"], book, book, a.get("source_name"), a.get("source_url"),
                a.get("source_type"), a.get("reliability"), a.get("verified_passages", 0),
                a.get("pending_passages", 0), a.get("last_checked"), a.get("notes"),
            ))
    stats["source_audits"] = len(aud_rows)

    # --- passages ---
    psg_rows = []
    for p in passages:
        psg_rows.append((
            p["passage_id"], p["book_id"], p["book_id"], p.get("chapter_id"),
            p.get("chapter_name"), p.get("page"), p.get("original_text"),
            None, p.get("normalized_text"), bool(p.get("is_paraphrase", False)),
            p.get("source_location"), p.get("verification_status", "pending"),
            p.get("confidence"), json.dumps(p.get("source_refs", []), ensure_ascii=False),
            bool(p.get("cross_verified", False)), p.get("version_notes"),
            json.dumps(p.get("concept_tags", []), ensure_ascii=False), p.get("notes"),
        ))
    stats["passages"] = len(psg_rows)

    # --- concepts ---
    con_rows = []
    for book in BOOK_IDS:
        p = KB_ROOT / "04_CONCEPTS" / f"{book}_concepts.json"
        d = load_json(p)
        for c in d.get("concepts", []):
            con_rows.append((
                c["concept_id"], c["concept_name"], c.get("definition"), c.get("domain"),
                json.dumps(c.get("book_ids", []), ensure_ascii=False),
                json.dumps(c.get("source_refs", []), ensure_ascii=False),
                c.get("status", "draft"), c.get("notes"),
            ))
    stats["concepts"] = len(con_rows)

    # --- principles ---
    prn_rows = []
    for book in BOOK_IDS:
        p = KB_ROOT / "05_PRINCIPLES" / f"{book}_principles.json"
        d = load_json(p)
        for pr in d.get("principles", []):
            prn_rows.append((
                pr["principle_id"], pr["principle_name"], pr.get("statement"),
                pr.get("interpretation"),
                json.dumps(pr.get("book_ids", []), ensure_ascii=False),
                json.dumps(pr.get("passage_ids", []), ensure_ascii=False),
                json.dumps(pr.get("concept_ids", []), ensure_ascii=False),
                pr.get("evidence_level"), pr.get("status", "draft"),
                bool(pr.get("conflict", False)), None,
            ))
    stats["principles"] = len(prn_rows)

    # --- rules(draft 全量,条件/结果存 JSONB.description) ---
    rule_rows = []
    for book in BOOK_IDS:
        p = KB_ROOT / "06_RULES_DRAFT" / f"{book}_rules_draft.json"
        d = load_json(p)
        for r in d.get("rules_draft", []):
            cond = r.get("condition", "")
            res = r.get("result", "")
            rule_rows.append((
                r["rule_id"], None, book, book, r.get("passage_id"),
                r.get("concept_id"), r.get("principle_id"),
                "bazi", None,
                f"条件: {cond}\n结果: {res}" if cond else (res or None),
                None, None,
                r.get("status", "draft").upper(), r.get("confidence"),
                r.get("priority", 100), bool(r.get("requires_human_review", True)),
                r.get("provenance", "classical"),
                json.dumps({"description": cond}, ensure_ascii=False),
                json.dumps({"description": res}, ensure_ascii=False),
                json.dumps([], ensure_ascii=False),
                json.dumps(r.get("source_refs", []), ensure_ascii=False),
                r.get("notes"),
            ))
    stats["rules"] = len(rule_rows)

    # --- evidence(级联校验:EVD.status == 源 passage.status) ---
    evd_rows = []
    for book in BOOK_IDS:
        p = KB_ROOT / "07_EVIDENCE" / f"EVD_{book}.json"
        d = load_json(p)
        for e in d.get("evidence_links", []):
            pid = e.get("passage_id")
            if pid and pid in passage_status and e.get("verification_status") != passage_status[pid]:
                violation_count += 1
                print(f"  [违反级联不变量] {e['evidence_id']}: EVD={e.get('verification_status')} != passage={passage_status[pid]}")
            evd_rows.append((
                e["evidence_id"], e.get("source_type"), book, pid, None,
                e.get("source_location"), e.get("original_text"),
                e.get("interpretation"), e.get("verification_status", "pending"),
                e.get("confidence"), bool(e.get("cross_verified", False)),
                json.dumps(e.get("source_refs", []), ensure_ascii=False),
                e.get("version_notes"), e.get("notes"),
            ))
    stats["evidence"] = len(evd_rows)

    # ---- 写库 ----
    if not dry_run:
        exec_many("""
            INSERT INTO sources (source_id, title_zh, title_en, author_or_attribution,
                claimed_author, dynasty, period, edition_source, base_text, editor,
                chapter_count, volume_count, source_type, verification_status, notes)
            VALUES %s
            ON CONFLICT (source_id) DO UPDATE SET
                title_zh=EXCLUDED.title_zh, author_or_attribution=EXCLUDED.author_or_attribution,
                dynasty=EXCLUDED.dynasty, edition_source=EXCLUDED.edition_source,
                chapter_count=EXCLUDED.chapter_count, volume_count=EXCLUDED.volume_count,
                verification_status=EXCLUDED.verification_status, notes=EXCLUDED.notes,
                updated_at=now()
        """, src_rows)

        exec_many("""
            INSERT INTO source_criticism (source_id, claimed_authorship, composition_period,
                edition_history, editorial_history, fragment_status, ocr_risk,
                interpolation_risk, variant_status, scholarly_notes, evidence_level)
            VALUES %s
            ON CONFLICT (source_id) DO UPDATE SET
                claimed_authorship=EXCLUDED.claimed_authorship,
                composition_period=EXCLUDED.composition_period,
                editorial_history=EXCLUDED.editorial_history,
                scholarly_notes=EXCLUDED.scholarly_notes
        """, sc_rows)

        exec_many("""
            INSERT INTO source_audits (audit_id, source_id, book_id, source_name, source_url,
                source_type, reliability, verified_passages, pending_passages, last_checked, notes)
            VALUES %s
            ON CONFLICT (audit_id) DO UPDATE SET
                source_name=EXCLUDED.source_name, source_url=EXCLUDED.source_url,
                source_type=EXCLUDED.source_type, reliability=EXCLUDED.reliability,
                verified_passages=EXCLUDED.verified_passages, pending_passages=EXCLUDED.pending_passages,
                last_checked=EXCLUDED.last_checked, notes=EXCLUDED.notes
        """, aud_rows)

        exec_many("""
            INSERT INTO passages (passage_id, source_id, book_id, chapter_id, chapter_name,
                page, original_text, transcription, normalized_text, is_paraphrase,
                source_location, verification_status, confidence, source_refs, cross_verified,
                version_notes, concept_tags, notes)
            VALUES %s
            ON CONFLICT (passage_id) DO UPDATE SET
                original_text=EXCLUDED.original_text, normalized_text=EXCLUDED.normalized_text,
                source_location=EXCLUDED.source_location,
                verification_status=EXCLUDED.verification_status,
                confidence=EXCLUDED.confidence, source_refs=EXCLUDED.source_refs,
                cross_verified=EXCLUDED.cross_verified, concept_tags=EXCLUDED.concept_tags,
                updated_at=now()
        """, psg_rows)

        exec_many("""
            INSERT INTO concepts (concept_id, concept_name, definition, domain, book_ids,
                source_refs, status, notes)
            VALUES %s
            ON CONFLICT (concept_id) DO UPDATE SET
                concept_name=EXCLUDED.concept_name, definition=EXCLUDED.definition,
                domain=EXCLUDED.domain, book_ids=EXCLUDED.book_ids,
                source_refs=EXCLUDED.source_refs, status=EXCLUDED.status,
                updated_at=now()
        """, con_rows)

        exec_many("""
            INSERT INTO principles (principle_id, principle_name, statement, interpretation,
                book_ids, passage_ids, concept_ids, evidence_level, status, conflict, notes)
            VALUES %s
            ON CONFLICT (principle_id) DO UPDATE SET
                principle_name=EXCLUDED.principle_name, statement=EXCLUDED.statement,
                interpretation=EXCLUDED.interpretation, book_ids=EXCLUDED.book_ids,
                passage_ids=EXCLUDED.passage_ids, concept_ids=EXCLUDED.concept_ids,
                evidence_level=EXCLUDED.evidence_level, status=EXCLUDED.status,
                conflict=EXCLUDED.conflict, updated_at=now()
        """, prn_rows)

        exec_many("""
            INSERT INTO rules (rule_id, claim_id, source_id, book_id, passage_id, concept_id,
                principle_id, system, domain, rule_text, normalized_rule, variant_id,
                rule_status, confidence, priority, requires_human_review, provenance,
                condition, result, test_case_ids, source_refs, notes)
            VALUES %s
            ON CONFLICT (rule_id) DO UPDATE SET
                book_id=EXCLUDED.book_id, passage_id=EXCLUDED.passage_id,
                concept_id=EXCLUDED.concept_id, principle_id=EXCLUDED.principle_id,
                rule_text=EXCLUDED.rule_text, rule_status=EXCLUDED.rule_status,
                confidence=EXCLUDED.confidence, provenance=EXCLUDED.provenance,
                condition=EXCLUDED.condition, result=EXCLUDED.result,
                source_refs=EXCLUDED.source_refs, updated_at=now()
        """, rule_rows)

        exec_many("""
            INSERT INTO evidence (evidence_id, source_type, source_id, passage_id, claim_id,
                source_location, original_text, interpretation, verification_status, confidence,
                cross_verified, source_refs, version_notes, notes)
            VALUES %s
            ON CONFLICT (evidence_id) DO UPDATE SET
                source_type=EXCLUDED.source_type, passage_id=EXCLUDED.passage_id,
                interpretation=EXCLUDED.interpretation,
                verification_status=EXCLUDED.verification_status,
                confidence=EXCLUDED.confidence, cross_verified=EXCLUDED.cross_verified,
                source_refs=EXCLUDED.source_refs, updated_at=now()
        """, evd_rows)

        conn.commit()
        conn.close()

    print(f"[wujing] 导入统计(plan): {stats}")
    print(f"[wujing] 证据级联不变量违反: {violation_count}")
    if violation_count == 0:
        print("[wujing] 证据级联校验: PASS(全部 EVD.status == 源 passage.status)")
    print("[wujing] 完成")


if __name__ == "__main__":
    main()
