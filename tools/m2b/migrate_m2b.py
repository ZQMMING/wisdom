"""M2-B Evidence Validation migration — 一次性、确定性、可追溯。

Spec Owner 授权范围:Evidence Validation / Knowledge Structuring。
允许:Evidence 去重归并(保留全部 source provenance)、Evidence Cluster、30 条 active ZPZ
Evidence Review、pending 按五书分批核验、五部经典 Evidence Validation、Concept Context、
Principle↔Evidence/Concept 关系整理、provenance/validator/audit/tests、Evidence Review Queue。

严禁(本脚本不执行):模型推断写入 verified、pending 自动升级 verified、修改 Rule 生命周期、
激活 draft、修改 Golden/算法/日界/Mapping/API。D-10:verified evidence 不赋予 Rule 可执行资格。

唯一合法知识生命周期:SOURCE → PASSAGE → VERIFIED EVIDENCE → CONCEPT → PRINCIPLE →
RULE PROPOSAL → REVIEW → VALIDATED → ACTIVE。Evidence 验证与 Rule 激活是两个独立审批链。

数据变更纪律:
  - 30 条 E-ZPZ-101..130:citation 与 P-ZPZ-YONGSHEN.classical_original.text 逐字一致
    (程序化断言,0 mismatch)→ cluster_id + citation.verification_status=verified(继承该
    passage 的 verified,单源,通行本句读从排印本;非 cross_verified)+ provenance_note。
  - E-ZPZ-001..005:工程种子(D-2 选项 A)→ provenance_note,verification 维持留空(诚实)。
  - 9 条 pending(DTS×4/SMTH×3/YHZP×2):维持 pending_verification + provenance_note。
  - 6 条 not_applicable(QTB-014/ZIWEI-001/ZW-405..408):维持 + provenance_note。
  - E-YHZP-102/103:维持 cross_verified(P0-15 BAZI-002/004)+ provenance_note。
  - 新建 data/evidence_meta/evidence_clusters.json + evidence_review_queue.json。
  - concepts/principles 增 evidence_refs(由 rule.evidence_refs 程序化反向回填)。

运行:PYTHONPATH=src TONGSHU_ENV_FILE=/dev/null python tools/m2b/migrate_m2b.py
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]          # 通书-claude/
DATA = REPO / "backend" / "data"
EVIDENCE_DIR = DATA / "evidence"
KB_DIR = DATA / "knowledge"
META_DIR = DATA / "evidence_meta"
DOCS = REPO / "docs"
AUDIT_DIR = DOCS / "v40" / "_m2b_audit"

REVIEWED_AT = "2026-08-19T00:00:00Z"
REVIEWER = "M2-B Evidence Review"
REVIEW_NOTE = "审查记录见 data/evidence_meta/evidence_review_queue.json"

# ---- 批次(以实测 52 条为据) ----
ZPZ_ANCHOR_IDS = [f"E-ZPZ-{n:03d}-001" for n in range(101, 131)]           # 30
ZPZ_SEED_IDS = [f"E-ZPZ-{n:03d}-001" for n in range(1, 6)]                # 5
PENDING_BY_BOOK = {
    "DTS": ["E-DTS-101-001", "E-DTS-103-001", "E-DTS-104-001", "E-DTS-105-001"],
    "SMTH": ["E-SMTH-101-001", "E-SMTH-103-001", "E-SMTH-104-001"],
    "YHZP": ["E-YHZP-101-001", "E-YHZP-104-001"],
}
NA_BY_BATCH = {
    "QTB": ["E-QTB-014-001"],
    "ZW": ["E-ZIWEI-001", "E-ZW-405-001", "E-ZW-406-001", "E-ZW-407-001", "E-ZW-408-001"],
}
CROSS_IDS = {"E-YHZP-102-001": "P0-15 BAZI-002(论起大运法 眉批)",
             "E-YHZP-103-001": "P0-15 BAZI-004(论日上起时例 五鼠遁)"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(msg: str) -> None:
    sys.stderr.write(f"[M2B-MIGRATE] FATAL: {msg}\n")
    sys.exit(1)


def main() -> None:
    # ---- 前提断言 ----
    evidence_files = sorted(EVIDENCE_DIR.glob("*.json"))
    if len(evidence_files) != 52:
        fail(f"evidence 文件数 != 52(实测 {len(evidence_files)})")
    evidence = {load_json(f)["evidence_id"]: f for f in evidence_files}
    expected = (set(ZPZ_ANCHOR_IDS) | set(ZPZ_SEED_IDS)
                | set(x for ids in PENDING_BY_BOOK.values() for x in ids)
                | set(x for ids in NA_BY_BATCH.values() for x in ids)
                | set(CROSS_IDS))
    if set(evidence) != expected:
        fail(f"evidence id 集合与批次定义不符\n  缺: {sorted(expected - set(evidence))}\n  多: {sorted(set(evidence) - expected)}")

    # 锚 passage(数据派生,不硬编码)
    passages = load_json(KB_DIR / "passages.json")["items"]
    anchor = next(p for p in passages if p["passage_id"] == "P-ZPZ-YONGSHEN")
    anchor_text = anchor["classical_original"]["text"]
    anchor_meta = {
        "book_id": anchor["book_id"],
        "chapter_id": anchor["chapter_id"],
        "edition_id": anchor["edition_id"],
        "verification": anchor["classical_original"]["verification"],
        "locator": anchor["classical_original"]["locator"],
    }
    if anchor_meta["verification"] != "verified":
        fail(f"P-ZPZ-YONGSHEN verification != verified({anchor_meta['verification']!r})")

    # 逐字一致断言:30 条成员 citation == 锚句(0 mismatch)
    mismatches = []
    for eid in ZPZ_ANCHOR_IDS:
        d = load_json(evidence[eid])
        text = (d.get("citation") or {}).get("original_text", "")
        if text != anchor_text:
            mismatches.append((eid, text, anchor_text))
        if (d.get("citation") or {}).get("verification_status") is not None:
            fail(f"{eid} 已带 verification_status(重复迁移?)")
    if mismatches:
        fail(f"锚句逐字一致断言失败: {len(mismatches)} 条 mismatch: {mismatches[:3]}")
    print(f"[M2B] 锚句逐字一致断言通过(30/30,0 mismatch): {anchor_text!r}")

    META_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- 1) 逐 evidence 变更(保留全部既有字段,仅增/改) ----
    anchor_note = ("M2-B:citation 与 P-ZPZ-YONGSHEN.classical_original.text 逐字一致"
                   "(程序化断言 0 mismatch);citation.verification_status=verified 继承该 "
                   "passage 的 verified(单源,通行本句读从排印本;非 cross_verified);"
                   f"归并 CLUSTER-ZPZ-YONGSHEN-ANCHOR;{REVIEW_NOTE}")
    seed_note = ("M2-B:D-2 选项 A——工程种子引文(source_locator.work=工程种子),非经典版本"
                 f"核验;citation.verification_status 维持留空(诚实);不进核验域;{REVIEW_NOTE}")
    pending_note = ("M2-B:五书分批核验(DTS×4/SMTH×3/YHZP×2)——(待校,paraphrase) 前缀 + "
                    "paraphrase 层,无逐字经典引文;citation.verification_status 维持 "
                    f"pending_verification(严禁自动升级);需人工双源核验对应章节原文;{REVIEW_NOTE}")
    na_note = ("M2-B:工程种子/spec 引文(source_layer=engineering_seed),非经典版本核验;"
               f"citation.verification_status 维持 not_applicable;不进核验域;{REVIEW_NOTE}")
    cross_note = f"M2-B:维持 cross_verified;{REVIEW_NOTE}"

    for eid in ZPZ_ANCHOR_IDS:
        path = evidence[eid]
        d = load_json(path)
        d["cluster_id"] = "CLUSTER-ZPZ-YONGSHEN-ANCHOR"
        d["citation"]["verification_status"] = "verified"
        d["provenance_note"] = anchor_note
        path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    for eid in ZPZ_SEED_IDS:
        path = evidence[eid]
        d = load_json(path)
        d["provenance_note"] = seed_note
        path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    for eid in [x for ids in PENDING_BY_BOOK.values() for x in ids]:
        path = evidence[eid]
        d = load_json(path)
        d["provenance_note"] = pending_note
        path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    for eid in [x for ids in NA_BY_BATCH.values() for x in ids]:
        path = evidence[eid]
        d = load_json(path)
        d["provenance_note"] = na_note
        path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    for eid, basis in CROSS_IDS.items():
        path = evidence[eid]
        d = load_json(path)
        d["provenance_note"] = f"M2-B:维持 cross_verified({basis},classical_verbatim_multi 多源核验);{REVIEW_NOTE}"
        path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- 2) evidence_clusters.json ----
    clusters = [{
        "cluster_id": "CLUSTER-ZPZ-YONGSHEN-ANCHOR",
        "cluster_type": "anchor",
        "anchor_text": anchor_text,
        "book_id": anchor_meta["book_id"],
        "chapter_id": anchor_meta["chapter_id"],
        "passage_id": "P-ZPZ-YONGSHEN",
        "edition_id": anchor_meta["edition_id"],
        "verification": "verified",
        "verification_basis": (f"P-ZPZ-YONGSHEN.classical_original.verification=verified,"
                               f"locator={anchor_meta['locator']};30 条 member citation 与 "
                               "anchor_text 逐字一致(程序化断言 0 mismatch)"),
        "member_evidence_ids": ZPZ_ANCHOR_IDS,
        "rationale": ("30 条 E-ZPZ-101..130 共享同一锚句(八字用神,专求月令…),证据去重归并 "
                      "为单一 cluster;member 逐条保留全部 source provenance(rule_refs/"
                      "source_locator/edition_id/modern_paraphrase)"),
        "status": "validated",
        "version": "1.0.0",
        "created_at": REVIEWED_AT,
        "reviewed_at": REVIEWED_AT,
        "reviewer": REVIEWER,
    }]
    (META_DIR / "evidence_clusters.json").write_text(
        json.dumps({"kind": "evidence_clusters", "clusters": clusters}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    # ---- 3) evidence_review_queue.json(52 条) ----
    entries = []
    for eid in ZPZ_ANCHOR_IDS:
        entries.append({
            "evidence_id": eid, "batch": "ZPZ-anchor", "review_status": "reviewed",
            "verdict": "verified", "cluster_id": "CLUSTER-ZPZ-YONGSHEN-ANCHOR",
            "verdict_basis": ("citation 与 P-ZPZ-YONGSHEN.classical_original.text 逐字一致"
                              "(0 mismatch);继承 passage verified(单源,通行本句读从排印本,"
                              "非 cross_verified)"),
            "reviewer": REVIEWER, "reviewed_at": REVIEWED_AT, "next_step": None,
        })
    for eid in ZPZ_SEED_IDS:
        entries.append({
            "evidence_id": eid, "batch": "ZPZ-engineering-seed", "review_status": "excluded",
            "verdict": "blank",
            "verdict_basis": ("工程种子引文(source_locator.work=工程种子,五行之性通行表述);"
                              "非经典版本核验;verification 维持留空(诚实,D-2 选项 A)"),
            "reviewer": REVIEWER, "reviewed_at": REVIEWED_AT, "next_step": None,
        })
    for book, ids in PENDING_BY_BOOK.items():
        for eid in ids:
            entries.append({
                "evidence_id": eid, "batch": book, "review_status": "pending_manual_verification",
                "verdict": "pending_verification",
                "verdict_basis": ("(待校,paraphrase) 前缀 + paraphrase 层;无逐字经典引文;"
                                  f"{book} 批次审查维持 pending_verification(严禁自动升级)"),
                "reviewer": REVIEWER, "reviewed_at": REVIEWED_AT,
                "next_step": "人工双源核验对应章节原文后再定",
            })
    for batch, ids in NA_BY_BATCH.items():
        for eid in ids:
            entries.append({
                "evidence_id": eid, "batch": batch, "review_status": "excluded",
                "verdict": "not_applicable",
                "verdict_basis": "工程种子/spec 引文(source_layer=engineering_seed);非经典版本核验;维持 not_applicable",
                "reviewer": REVIEWER, "reviewed_at": REVIEWED_AT, "next_step": None,
            })
    for eid, basis in CROSS_IDS.items():
        entries.append({
            "evidence_id": eid, "batch": "YHZP", "review_status": "reviewed",
            "verdict": "cross_verified",
            "verdict_basis": f"{basis},classical_verbatim_multi 多源核验;citation 与对应 passage 逐字一致",
            "reviewer": REVIEWER, "reviewed_at": REVIEWED_AT, "next_step": None,
        })
    entries.sort(key=lambda e: e["evidence_id"])
    if len(entries) != 52:
        fail(f"review queue 条目 != 52({len(entries)})")
    (META_DIR / "evidence_review_queue.json").write_text(
        json.dumps({
            "kind": "evidence_review_queue",
            "review_batch": "M2-B-2026-08-19",
            "description": ("全 52 条 evidence 审查记录。verdict 仅表达 evidence 核验域;"
                            "不含任何 Rule 生命周期字段(D-10:verified evidence 不得自动获得 "
                            "Rule 可执行资格;Evidence 验证与 Rule 激活是两个独立审批链)。"),
            "items": entries,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- 4) concept/principle 增 evidence_refs(由 rule.evidence_refs 程序化反向回填) ----
    rules = [load_json(f) for f in sorted((DATA / "rules").glob("*.json"))]
    concept_ev: dict[str, set] = defaultdict(set)
    principle_ev: dict[str, set] = defaultdict(set)
    for r in rules:
        for ev in r.get("evidence_refs", []):
            if r.get("concept_id"):
                concept_ev[r["concept_id"]].add(ev)
            if r.get("principle_id"):
                principle_ev[r["principle_id"]].add(ev)
    for fname, id_field, mapping in (("concepts.json", "concept_id", concept_ev),
                                     ("principles.json", "principle_id", principle_ev)):
        path = KB_DIR / fname
        doc = load_json(path)
        for item in doc["items"]:
            refs = sorted(mapping.get(item[id_field], []))
            if refs:
                item["evidence_refs"] = refs
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- 5) 审计 manifest ----
    manifest = {
        "migration": "M2-B-2026-08-19",
        "scope": "Evidence Validation / Knowledge Structuring(Spec Owner 批准)",
        "evidence_total": 52,
        "anchor_mismatch": 0,
        "batch_counts": {
            "ZPZ-anchor(→verified+cluster)": len(ZPZ_ANCHOR_IDS),
            "ZPZ-engineering-seed(verification 留空)": len(ZPZ_SEED_IDS),
            "pending_verification(维持)": sum(len(v) for v in PENDING_BY_BOOK.values()),
            "not_applicable(维持)": sum(len(v) for v in NA_BY_BATCH.values()),
            "cross_verified(维持)": len(CROSS_IDS),
        },
        "concept_evidence_refs": {k: sorted(v) for k, v in sorted(concept_ev.items()) if v},
        "principle_evidence_refs": {k: sorted(v) for k, v in sorted(principle_ev.items()) if v},
        "files_written": [
            "data/evidence/*.json(52,字段变更)",
            "data/evidence_meta/evidence_clusters.json",
            "data/evidence_meta/evidence_review_queue.json",
            "data/knowledge/concepts.json",
            "data/knowledge/principles.json",
        ],
        "rule_lifecycle": "零改动(D-10:verified evidence 不赋予 Rule 可执行资格)",
    }
    (AUDIT_DIR / "migration_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[M2B] manifest 已写:{AUDIT_DIR / 'migration_manifest.json'}")
    print(f"[M2B] 完成:52 evidence 变更 + cluster 1 + review queue 52 + concept/principle evidence_refs 回填")


if __name__ == "__main__":
    main()
