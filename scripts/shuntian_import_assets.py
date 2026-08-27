"""词库V4.0 + TONGSHU 运行时数据 → shuntian_kb 导入器。

数据源:
  1. D:\today\开发资料\参考资料\词库V4.0(11 层语义词库,交付层 JSON 为标准)
     - 04_MAPPING_REGISTRY.json(156)→ semantic_mappings
     - 03_CLASSICAL_SEMANTICS.json(10)→ semantic_mappings
     - 02_TRADITIONAL_TERMS.json(26)→ lexicons
     - 09_GOLDENMAPPING_GOLDEN.json(10)+ 09_GOLDENEXPRESSION_GOLDEN.json(4)→ golden_cases
     - 10_FORBIDDEN_PATTERNS.json(39)→ forbidden_patterns
  2. D:\today\backend\data(运行时语料)
     - knowledge/{books,passages,concepts,principles}.json(6书/14passage/16概念/10原则)
     - rules/*.json(55)→ rules(runtime_status 保留原始 active/draft,rule_status 保守 DRAFT)
     - evidence/*.json(52)→ evidence
     - docs/golden_cases/GOLDEN-0*.yaml(20)→ golden_cases
     - mappings/MAP-1001..1010(10)→ semantic_mappings

纪律:
  - 运行时规则 rule_status 一律 DRAFT(不越权激活;FROZEN 需 Spec Owner 逐条审批),
    原始运行时 status 存 runtime_status 列,notes 记录工程状态。
  - 数据隔离:原文(original_text)/规范化(normalized)/现代解释(interpretation)分列。
  - 幂等:ON CONFLICT DO UPDATE(数据源=权威)。

用法: PYTHONPATH=src python scripts/shuntian_import_assets.py [--dry-run]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import psycopg2
import psycopg2.extras
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tongshu.db.config import get_dsn  # noqa: E402

LEXICON_ROOT = Path(r"D:\today\开发资料\参考资料\词库V4.0")
DELIVERABLES = LEXICON_ROOT / "11_DELIVERABLES — 交付物层"
GOLDEN_LAYER = LEXICON_ROOT / "09_GOLDEN — 黄金案例层"
RUNTIME_DATA = Path(__file__).resolve().parents[1] / "data"
REPO_ROOT = Path(__file__).resolve().parents[2]


def kb_conn():
    dsn = get_dsn().replace("/otcg", "/shuntian_kb")
    return psycopg2.connect(dsn)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def items_of(path: Path) -> list[dict]:
    d = load_json(path)
    return d.get("items", [])


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    print(f"[assets] {'DRY-RUN' if dry_run else '写库'} 词库+运行时导入")

    # ---------- 词库 ----------
    # 1. MAPPING_REGISTRY(156)
    map_rows = []
    for m in items_of(DELIVERABLES / "04_MAPPING_REGISTRY.json"):
        map_rows.append((
            m["mapping_id"], m.get("source_domain"), m.get("source_concept"),
            m.get("mapping_type"), json.dumps([], ensure_ascii=False),
            m.get("semantic_label"), m.get("product_semantic"),
            json.dumps(m.get("theme", []), ensure_ascii=False),
            json.dumps(m.get("allowed_context", []), ensure_ascii=False),
            json.dumps(m.get("forbidden_context", []), ensure_ascii=False),
            json.dumps(m.get("allowed_actions", []), ensure_ascii=False),
            json.dumps(m.get("forbidden_actions", []), ensure_ascii=False),
            json.dumps(m.get("source_refs", []), ensure_ascii=False),
            m.get("version"), m.get("status", "DRAFT"),
        ))
    # 2. CLASSICAL_SEMANTICS(10)
    _PREFIX_DOMAIN = {"BAZI": "BAZI", "CAL": "CALENDAR", "ZIWEI": "ZIWEI",
                      "SEM": "EXPRESSIONS", "REL": "RELATIONAL"}
    for c in items_of(DELIVERABLES / "03_CLASSICAL_SEMANTICS.json"):
        _prefix = str(c["mapping_id"]).split("_")[0]
        _domain = _PREFIX_DOMAIN.get(_prefix, _prefix)
        map_rows.append((
            c["mapping_id"], _domain, c.get("traditional_term"), "semantic",
            json.dumps(c.get("classical_semantic", []), ensure_ascii=False),
            c.get("product_semantic"), c.get("product_semantic"),
            json.dumps(c.get("themes", []), ensure_ascii=False),
            json.dumps(c.get("contexts", []), ensure_ascii=False),
            json.dumps([], ensure_ascii=False),
            json.dumps(c.get("allowed_actions", []), ensure_ascii=False),
            json.dumps(c.get("forbidden_actions", []), ensure_ascii=False),
            json.dumps(c.get("source_refs", []), ensure_ascii=False),
            c.get("version"), c.get("status", "DRAFT"),
        ))
    # 3. 运行时 MAP-1001..1010
    for p in sorted((RUNTIME_DATA / "mappings").glob("MAP-*.json")):
        m = load_json(p)
        map_rows.append((
            m["mapping_id"], "BAZI", m.get("source_term"), "semantic",
            json.dumps([], ensure_ascii=False), m.get("modern_theme"),
            m.get("modern_gloss"), json.dumps([], ensure_ascii=False),
            json.dumps([], ensure_ascii=False), json.dumps([], ensure_ascii=False),
            json.dumps([], ensure_ascii=False), json.dumps([], ensure_ascii=False),
            json.dumps([], ensure_ascii=False), m.get("version"),
            m.get("status", "draft").upper(),
        ))

    # 去重(mapping_id 重复时保留最后一条,避免 ON CONFLICT 二次命中)
    map_dedup = {}
    for row in map_rows:
        map_dedup[row[0]] = row
    map_rows = list(map_dedup.values())

    # 4. TRADITIONAL_TERMS(26)→ lexicons
    lex_rows = []
    for t in items_of(DELIVERABLES / "02_TRADITIONAL_TERMS.json"):
        lex_rows.append((
            f"LEX_{t.get('type','').upper()}_{len(lex_rows)+1:03d}",
            t.get("type"), t.get("traditional_term"), t.get("type"),
            t.get("classical_basis"), None, json.dumps([], ensure_ascii=False),
            t.get("version"), t.get("status", "DRAFT"),
        ))

    # 5. 词库 GOLDEN(MAP 10 + EXP 4)→ golden_cases
    gc_rows = []
    gm = load_json(GOLDEN_LAYER / "09_GOLDENMAPPING_GOLDEN.json")
    for c in gm.get("mapping_golden", []):
        gc_rows.append((
            c["case_id"],
            json.dumps(c.get("input_semantics", {}), ensure_ascii=False),
            json.dumps({}, ensure_ascii=False), json.dumps({}, ensure_ascii=False),
            json.dumps({}, ensure_ascii=False), json.dumps({}, ensure_ascii=False),
            json.dumps({}, ensure_ascii=False),
            json.dumps({"expected_semantic": c.get("expected_semantic"),
                        "expected_theme": c.get("expected_theme"),
                        "expected_mapping": c.get("expected_mapping")}, ensure_ascii=False),
            json.dumps(c.get("expected_actions", []), ensure_ascii=False),
            json.dumps(c.get("forbidden_drift", []), ensure_ascii=False),
            "词库V4.0 09_GOLDENMAPPING_GOLDEN", c.get("status", "DRAFT"),
            None, c.get("version"), None,
        ))
    ge = load_json(GOLDEN_LAYER / "09_GOLDENEXPRESSION_GOLDEN.json")
    for c in ge.get("expression_golden", []):
        gc_rows.append((
            c["case_id"],
            json.dumps(c.get("input_semantics", {}), ensure_ascii=False),
            json.dumps({}, ensure_ascii=False), json.dumps({}, ensure_ascii=False),
            json.dumps({}, ensure_ascii=False), json.dumps({}, ensure_ascii=False),
            json.dumps({}, ensure_ascii=False),
            json.dumps({"expected_expression": c.get("expected_expression"),
                        "expected_mapping": c.get("expected_mapping")}, ensure_ascii=False),
            json.dumps([], ensure_ascii=False),
            json.dumps(c.get("forbidden_patterns", []), ensure_ascii=False),
            "词库V4.0 09_GOLDENEXPRESSION_GOLDEN", c.get("status", "DRAFT"),
            None, c.get("version"), None,
        ))

    # 6. FORBIDDEN_PATTERNS(39)→ forbidden_patterns
    fb_rows = []
    fb_idx = 0
    for p in items_of(DELIVERABLES / "10_FORBIDDEN_PATTERNS.json"):
        fb_idx += 1
        pid = p.get("pattern_id") or f"FBD_{p.get('category','misc').upper()[:4]}_{fb_idx:03d}"
        name = p.get("name") or p.get("category") or pid
        fb_rows.append((
            pid, p.get("category"), name,
            p.get("source_file"), json.dumps(p.get("examples", []), ensure_ascii=False),
            "ACTIVE",
        ))

    # ---------- 运行时 knowledge ----------
    # 7. books(6)→ sources
    def _runtime_status(s: str | None) -> str:
        # 运行时状态 → 手册枚举(保守映射,不丢失语义)
        if s in ("verified", "cross_verified", "validated"):
            return "verified"
        if s == "verified_excerpt":
            return "verified_excerpt"
        if s in ("disputed",):
            return "disputed"
        return "pending"

    def _runtime_book_status(s: str | None) -> str:
        # 运行时 validated(M1 已验证版本)→ 手册 verified;其余保守 pending
        if s == "validated":
            return "verified"
        return "pending"

    src_rows = []
    for b in items_of(RUNTIME_DATA / "knowledge" / "books.json"):
        src_rows.append((
            b["book_id"], b.get("title"), None, b.get("author"), b.get("author"),
            None, b.get("era"), b.get("edition"), None, None,
            None, None, b.get("source_type", "classical_text"),
            _runtime_book_status(b.get("status")),
            f"运行时语料(M1 Edition Registry); pinned_edition_id={b.get('pinned_edition_id')}",
        ))
    # 8. passages(14)→ passages
    psg_rows = []
    for p in items_of(RUNTIME_DATA / "knowledge" / "passages.json"):
        co = p.get("classical_original", {})
        para = p.get("paraphrase")
        if isinstance(para, dict):
            para_text = para.get("text")
            para_loc = para.get("locator") or ""
        else:
            para_text = para
            para_loc = ""
        psg_rows.append((
            p["passage_id"], p.get("book_id"), p.get("book_id"), p.get("chapter_id"),
            None, None, co.get("text") if isinstance(co, dict) else co, None,
            para_text, False, p.get("source_reference"),
            _runtime_status(p.get("verification_status", "pending")),
            _runtime_status(co.get("verification")) if isinstance(co, dict) else None,
            json.dumps([p.get("source_reference")] if p.get("source_reference") else [], ensure_ascii=False),
            _runtime_status(co.get("verification")) == "verified" if isinstance(co, dict) else False,
            f"运行时语料; edition_id={p.get('edition_id')}; {p.get('edition_note','')}; paraphrase_locator={para_loc}",
            json.dumps([], ensure_ascii=False), p.get("status"),
        ))
    # 9. concepts(16)
    con_rows = []
    for c in items_of(RUNTIME_DATA / "knowledge" / "concepts.json"):
        con_rows.append((
            c["concept_id"], c.get("concept_name"), c.get("definition"),
            c.get("category"),
            json.dumps(c.get("source_refs", []), ensure_ascii=False),
            json.dumps(c.get("evidence_refs", []), ensure_ascii=False),
            c.get("status", "draft"), None,
        ))
    # 10. principles(10)
    prn_rows = []
    for pr in items_of(RUNTIME_DATA / "knowledge" / "principles.json"):
        prn_rows.append((
            pr["principle_id"], pr.get("name"), pr.get("description"), None,
            json.dumps(pr.get("book_refs", []), ensure_ascii=False),
            json.dumps(pr.get("passage_refs", []), ensure_ascii=False),
            json.dumps([], ensure_ascii=False), None, pr.get("status", "draft"),
            False, pr.get("confidence"),
        ))

    # ---------- 运行时规则/证据 ----------
    # 中文书名 → sources.source_id 键值映射(运行时语料 source.work 是书名,
    # sources 表主键是键值;必须归一化否则外键悬空)
    _WORK_TO_SOURCE_ID = {
        "子平真诠": "ZIPING-ZHENQUAN",
        "滴天髓": "DITIANSUI",
        "穷通宝鉴": "QIONGTONG-BAOJIAN",
        "三命通会": "SANMING-TONGHUI",
        "渊海子平": "YUANHAI-ZIPING",
        "紫微斗数": "ZIWEI-DOUSHU",
    }

    # 11. rules(55); source_id 用 book_id(键),工程种子 book_id=None → NULL(诚实:无经典来源)
    rule_rows = []
    for p in sorted((RUNTIME_DATA / "rules").glob("*.json")):
        r = load_json(p)
        rid = r["rule_id"]
        system = "ziwei" if rid.startswith("ZW") else "bazi"
        src_id = r.get("book_id")  # 键值(与 sources 主键一致);工程种子 ZPZ-001..005 为 None
        provenance = "engineering_seed" if system == "ziwei" else "classical"
        notes = (
            f"运行时规则(TONGSHU); 工程status={r.get('status')}; "
            f"applies_to_layers={r.get('applies_to_layers')}; "
            f"spec_decisions_ref={r.get('spec_decisions_ref')}. "
            f"rule_status 保守 DRAFT,冻结判定待 Spec Owner 逐条审批。"
        )
        rule_rows.append((
            rid, None, src_id, r.get("book_id"), r.get("passage_id"),
            r.get("concept_id"), r.get("principle_id"), system,
            r.get("produces_signal_type"), r.get("title"), None, None,
            "DRAFT", r.get("status"), None, r.get("precedence", 100), True,
            provenance, json.dumps(r.get("conditions", {}), ensure_ascii=False),
            json.dumps(r.get("conclusion", {}), ensure_ascii=False),
            json.dumps(r.get("forbidden_inferences", []), ensure_ascii=False),
            json.dumps(r.get("evidence_refs", []), ensure_ascii=False), notes,
        ))
    # 12. evidence(52); source_id 用 work→键 映射(证据只有 source_locator.work)
    # 工程种子(E-ZPZ-001..005/E-ZIWEI-001/E-QTB-014-001)无经典来源 → NULL(诚实)
    # passage_id 经 rule_refs→rules.passage_id 反查(数据自身关联,非虚构);
    # 反查不到的(规则无 passage_id)→ NULL
    rule_passage = {}
    for p in sorted((RUNTIME_DATA / "rules").glob("*.json")):
        r = load_json(p)
        rule_passage[r["rule_id"]] = r.get("passage_id")
    evd_rows = []
    for p in sorted((RUNTIME_DATA / "evidence").glob("*.json")):
        e = load_json(p)
        loc = e.get("source_locator", {})
        work = loc.get("work") if isinstance(loc, dict) else None
        src_id = _WORK_TO_SOURCE_ID.get(work)  # 映射不到(工程种子)→ None
        _refs = e.get("rule_refs") or []
        _pid = None
        for _rid in _refs:
            if rule_passage.get(_rid):
                _pid = rule_passage[_rid]
                break
        citation = e.get("citation", {})
        evd_rows.append((
            e["evidence_id"], "citation", src_id, _pid, None,
            None, citation.get("original_text") if isinstance(citation, dict) else None,
            e.get("modern_paraphrase"),
            _runtime_status(citation.get("verification_status")) if isinstance(citation, dict) else "pending",
            e.get("evidence_strength"), False,
            json.dumps([], ensure_ascii=False), json.dumps({
                "provenance_note": e.get("provenance_note"),
                "edition_id": e.get("edition_id"), "source_layer": e.get("source_layer"),
                "cluster_id": e.get("cluster_id"), "rule_refs": e.get("rule_refs"),
            }, ensure_ascii=False), e.get("version"),
        ))

    # 13. 运行时 golden(20)
    golden_known = 0
    for p in sorted(REPO_ROOT.glob("docs/golden_cases/GOLDEN-0*.yaml")):
        c = yaml.safe_load(p.read_text(encoding="utf-8"))
        if not isinstance(c, dict):
            continue
        golden_known += 1
        theme = (c.get("input") or {}).get("theme") if isinstance(c.get("input"), dict) else None
        gc_rows.append((
            c["case_id"],
            json.dumps(c.get("input", {}), ensure_ascii=False),
            json.dumps(c.get("bazi", {}), ensure_ascii=False),
            json.dumps(c.get("ziwei", {}), ensure_ascii=False),
            json.dumps({}, ensure_ascii=False), json.dumps({}, ensure_ascii=False),
            json.dumps({}, ensure_ascii=False),
            json.dumps({"expected_signals": c.get("expected_signals"),
                        "expected_atomic_claims": c.get("expected_atomic_claims"),
                        "expected_cross_analysis": c.get("expected_cross_analysis"),
                        "expected_rendered_output_features": c.get("expected_rendered_output_features")},
                       ensure_ascii=False),
            json.dumps([], ensure_ascii=False), json.dumps([], ensure_ascii=False),
            f"TONGSHU golden(GOLDEN-001..020, commit babc22b); spec_version={c.get('spec_version')}",
            c.get("status", "active"), theme, None, None,
        ))

    # ---------- 汇总 ----------
    stats = {"semantic_mappings": len(map_rows), "lexicons": len(lex_rows),
             "golden_cases": len(gc_rows), "forbidden_patterns": len(fb_rows),
             "sources": len(src_rows), "passages": len(psg_rows),
             "concepts": len(con_rows), "principles": len(prn_rows),
             "rules": len(rule_rows), "evidence": len(evd_rows),
             "runtime_golden_known": golden_known}
    print(f"[assets] 统计: {stats}")
    if dry_run:
        return

    conn = kb_conn()
    cur = conn.cursor()

    def exec_many(sql, rows):
        psycopg2.extras.execute_values(cur, sql, rows, page_size=200)

    exec_many("""
        INSERT INTO semantic_mappings (mapping_id, source_domain, source_concept, mapping_type,
            classical_semantic, semantic_label, product_semantic, theme, allowed_context,
            forbidden_context, allowed_actions, forbidden_actions, source_refs, version, status)
        VALUES %s
        ON CONFLICT (mapping_id) DO UPDATE SET
            source_domain=EXCLUDED.source_domain, source_concept=EXCLUDED.source_concept,
            semantic_label=EXCLUDED.semantic_label, product_semantic=EXCLUDED.product_semantic,
            theme=EXCLUDED.theme, allowed_context=EXCLUDED.allowed_context,
            forbidden_context=EXCLUDED.forbidden_context, allowed_actions=EXCLUDED.allowed_actions,
            forbidden_actions=EXCLUDED.forbidden_actions, source_refs=EXCLUDED.source_refs,
            status=EXCLUDED.status, updated_at=now()
    """, map_rows)

    exec_many("""
        INSERT INTO lexicons (term_id, domain, traditional_term, term_type, classical_basis,
            semantic_label, source_refs, version, status)
        VALUES %s
        ON CONFLICT (term_id) DO UPDATE SET
            traditional_term=EXCLUDED.traditional_term, term_type=EXCLUDED.term_type,
            classical_basis=EXCLUDED.classical_basis, status=EXCLUDED.status
    """, lex_rows)

    exec_many("""
        INSERT INTO golden_cases (case_id, input, expected_bazi, expected_ziwei,
            expected_hetu, expected_huangli, expected_calendar, expected_state,
            expected_actions, forbidden_drift, source, verification_status, theme,
            version, notes)
        VALUES %s
        ON CONFLICT (case_id) DO UPDATE SET
            input=EXCLUDED.input, expected_bazi=EXCLUDED.expected_bazi,
            expected_ziwei=EXCLUDED.expected_ziwei, expected_state=EXCLUDED.expected_state,
            expected_actions=EXCLUDED.expected_actions, source=EXCLUDED.source,
            verification_status=EXCLUDED.verification_status, theme=EXCLUDED.theme,
            updated_at=now()
    """, gc_rows)

    exec_many("""
        INSERT INTO forbidden_patterns (pattern_id, pattern_type, pattern_name, description,
            trigger_text, status)
        VALUES %s
        ON CONFLICT (pattern_id) DO UPDATE SET
            pattern_type=EXCLUDED.pattern_type, pattern_name=EXCLUDED.pattern_name,
            trigger_text=EXCLUDED.trigger_text
    """, fb_rows)

    exec_many("""
        INSERT INTO sources (source_id, title_zh, title_en, author_or_attribution,
            claimed_author, dynasty, period, edition_source, base_text, editor,
            chapter_count, volume_count, source_type, verification_status, notes)
        VALUES %s
        ON CONFLICT (source_id) DO UPDATE SET
            title_zh=EXCLUDED.title_zh, author_or_attribution=EXCLUDED.author_or_attribution,
            period=EXCLUDED.period, edition_source=EXCLUDED.edition_source,
            source_type=EXCLUDED.source_type, verification_status=EXCLUDED.verification_status,
            notes=EXCLUDED.notes, updated_at=now()
    """, src_rows)

    exec_many("""
        INSERT INTO passages (passage_id, source_id, book_id, chapter_id, chapter_name,
            page, original_text, transcription, normalized_text, is_paraphrase,
            source_location, verification_status, confidence, source_refs, cross_verified,
            version_notes, concept_tags, notes)
        VALUES %s
        ON CONFLICT (passage_id) DO UPDATE SET
            original_text=EXCLUDED.original_text, normalized_text=EXCLUDED.normalized_text,
            verification_status=EXCLUDED.verification_status,
            source_refs=EXCLUDED.source_refs, cross_verified=EXCLUDED.cross_verified,
            version_notes=EXCLUDED.version_notes, updated_at=now()
    """, psg_rows)

    exec_many("""
        INSERT INTO concepts (concept_id, concept_name, definition, domain, book_ids,
            source_refs, status, notes)
        VALUES %s
        ON CONFLICT (concept_id) DO UPDATE SET
            concept_name=EXCLUDED.concept_name, definition=EXCLUDED.definition,
            domain=EXCLUDED.domain, book_ids=EXCLUDED.book_ids,
            source_refs=EXCLUDED.source_refs, status=EXCLUDED.status, updated_at=now()
    """, con_rows)

    exec_many("""
        INSERT INTO principles (principle_id, principle_name, statement, interpretation,
            book_ids, passage_ids, concept_ids, evidence_level, status, conflict, notes)
        VALUES %s
        ON CONFLICT (principle_id) DO UPDATE SET
            principle_name=EXCLUDED.principle_name, statement=EXCLUDED.statement,
            interpretation=EXCLUDED.interpretation, book_ids=EXCLUDED.book_ids,
            passage_ids=EXCLUDED.passage_ids, concept_ids=EXCLUDED.concept_ids,
            status=EXCLUDED.status, updated_at=now()
    """, prn_rows)

    exec_many("""
        INSERT INTO rules (rule_id, claim_id, source_id, book_id, passage_id, concept_id,
            principle_id, system, domain, rule_text, normalized_rule, variant_id,
            rule_status, runtime_status, confidence, priority, requires_human_review,
            provenance, condition, result, test_case_ids, source_refs, notes)
        VALUES %s
        ON CONFLICT (rule_id) DO UPDATE SET
            source_id=EXCLUDED.source_id, book_id=EXCLUDED.book_id,
            passage_id=EXCLUDED.passage_id,
            concept_id=EXCLUDED.concept_id, principle_id=EXCLUDED.principle_id,
            system=EXCLUDED.system, domain=EXCLUDED.domain, rule_text=EXCLUDED.rule_text,
            rule_status=EXCLUDED.rule_status, runtime_status=EXCLUDED.runtime_status,
            priority=EXCLUDED.priority, provenance=EXCLUDED.provenance,
            condition=EXCLUDED.condition, result=EXCLUDED.result,
            source_refs=EXCLUDED.source_refs, notes=EXCLUDED.notes, updated_at=now()
    """, rule_rows)

    exec_many("""
        INSERT INTO evidence (evidence_id, source_type, source_id, passage_id, claim_id,
            source_location, original_text, interpretation, verification_status, confidence,
            cross_verified, source_refs, version_notes, notes)
        VALUES %s
        ON CONFLICT (evidence_id) DO UPDATE SET
            source_type=EXCLUDED.source_type, source_id=EXCLUDED.source_id,
            passage_id=EXCLUDED.passage_id,
            interpretation=EXCLUDED.interpretation,
            verification_status=EXCLUDED.verification_status,
            confidence=EXCLUDED.confidence, version_notes=EXCLUDED.version_notes,
            updated_at=now()
    """, evd_rows)

    conn.commit()
    conn.close()
    print("[assets] 导入完成")


if __name__ == "__main__":
    main()
