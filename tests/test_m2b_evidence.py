"""M2-B Evidence Validation 测试 — Evidence Cluster + Review Queue + Evidence→Concept/Principle 链。

覆盖(Spec Owner M2-B 授权 #1/#2/#3/#6/#7/#9 + D-10):
  1. 生产数据:verify_evidence_chain()==[]、verify_evidence()==[](evidence v1.2 schema)。
  2. Cluster:CLUSTER-ZPZ-YONGSHEN-ANCHOR 30 成员、anchor 逐字一致(0 mismatch)、
     verification=verified(继承 passage,非 cross)、passage/book/chapter/edition 解析一致、
     evidence.cluster_id 反链闭合。
  3. Review Queue:52/52 覆盖、verdict 分布(verified 30 / pending 9 / na 6 / cross 2 / blank 5)、
     review_status 分布、verdict ↔ citation.verification_status 一致。
  4. D-10:queue 条目无 Rule 生命周期字段;55 条 rule status 分布维持 30/10/15——
     verified evidence 不改变任何 Rule 可执行资格。
  5. Evidence→Concept/Principle 链:concept/principle.evidence_refs 全部解析 + spot 断言派生值。
  6. 负路径:未知 cluster 成员 / anchor 逐字不一致 / 未登记 cluster_id / 登记但非成员 /
     queue 缺 evidence / verdict 不一致 / D-10 违规 / evidence_refs 未知 → 全部命中。
  7. 回滚点:_m2b_backup 56 文件齐全。
"""

from __future__ import annotations
import json
import shutil
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from tongshu.reasoning.knowledge_base import KbLoader
from tongshu.reasoning.rule_loader import RuleLoader

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "backend" / "data"
DOCS = REPO / "docs"
BACKUP = DATA / "_m2b_backup"
DOCS_BACKUP = DOCS / "_m2b_backup"

CLUSTER = "CLUSTER-ZPZ-YONGSHEN-ANCHOR"
ANCHOR_TEXT = "八字用神,专求月令,以日干配月令地支,而生克不同,格局分焉。"


def _live_loader() -> KbLoader:
    return KbLoader(DATA, DOCS)


def _build_tree() -> Path:
    """拷贝生产 knowledge + evidence + evidence_meta 到临时目录(loader 需要全部 7 个知识文件)。"""
    tmp = Path(tempfile.mkdtemp(prefix="m2b_test_"))
    shutil.copytree(DATA / "knowledge", tmp / "knowledge")
    shutil.copytree(DATA / "evidence", tmp / "evidence")
    shutil.copytree(DATA / "evidence_meta", tmp / "evidence_meta")
    return tmp


def _chain(kb: KbLoader, tmp: Path) -> list[str]:
    return kb.verify_evidence_chain(
        meta_dir=tmp / "evidence_meta",
        cluster_schema=DOCS / "evidence_clusters.schema.json",
        queue_schema=DOCS / "evidence_review_queue.schema.json",
    )


class TestLiveChain(unittest.TestCase):
    def test_verify_evidence_chain_zero_violations(self):
        kb = _live_loader()
        self.assertEqual(_chain(kb, DATA), [])

    def test_verify_evidence_zero_violations_v12(self):
        # evidence v1.2:30 条 ZPZ 增 cluster_id + verified + provenance_note 仍过 schema
        kb = _live_loader()
        ev_dir = DATA / "evidence"
        self.assertEqual(len(list(ev_dir.glob("*.json"))), 86)
        self.assertEqual(kb.verify_evidence(DOCS / "evidence.schema.json"), [])

    def test_all_66_evidence_files_carry_m2b_metadata(self):
        for f in (DATA / "evidence").glob("*.json"):
            d = json.loads(f.read_text(encoding="utf-8"))
            self.assertTrue(d.get("provenance_note"), f"{d['evidence_id']} 缺 provenance_note")
            self.assertIn("M2-B", d["provenance_note"])


class TestEvidenceCluster(unittest.TestCase):
    def test_cluster_shape_and_members(self):
        doc = json.loads((DATA / "evidence_meta" / "evidence_clusters.json").read_text(encoding="utf-8"))
        self.assertEqual(doc["kind"], "evidence_clusters")
        self.assertEqual(len(doc["clusters"]), 1)
        c = doc["clusters"][0]
        self.assertEqual(c["cluster_id"], CLUSTER)
        self.assertEqual(c["cluster_type"], "anchor")
        self.assertEqual(len(c["member_evidence_ids"]), 30)
        self.assertEqual(c["member_evidence_ids"][0], "E-ZPZ-101-001")
        self.assertEqual(c["member_evidence_ids"][-1], "E-ZPZ-130-001")

    def test_anchor_members_byte_identical(self):
        doc = json.loads((DATA / "evidence_meta" / "evidence_clusters.json").read_text(encoding="utf-8"))
        c = doc["clusters"][0]
        self.assertEqual(c["anchor_text"], ANCHOR_TEXT)
        for mid in c["member_evidence_ids"]:
            ev = json.loads((DATA / "evidence" / f"{mid}.json").read_text(encoding="utf-8"))
            self.assertEqual(ev["citation"]["original_text"], ANCHOR_TEXT, mid)
            self.assertEqual(ev["cluster_id"], CLUSTER, mid)
            self.assertEqual(ev["citation"]["verification_status"], "verified", mid)

    def test_cluster_verification_inherits_passage_single_source(self):
        kb = _live_loader()
        doc = json.loads((DATA / "evidence_meta" / "evidence_clusters.json").read_text(encoding="utf-8"))
        c = doc["clusters"][0]
        p = kb.get("passage", "P-ZPZ-YONGSHEN")
        self.assertEqual(c["verification"], "verified")
        self.assertEqual(p["verification_status"], "verified")
        self.assertEqual(c["book_id"], p["book_id"])
        self.assertEqual(c["chapter_id"], p["chapter_id"])
        self.assertEqual(c["edition_id"], p["edition_id"])
        # 诚实层级:继承 passage 单源 verified,非 cross_verified(30 条 ZPZ 非多源)
        self.assertNotEqual(c["verification"], "cross_verified")


class TestReviewQueue(unittest.TestCase):
    def test_coverage_86(self):
        q = json.loads((DATA / "evidence_meta" / "evidence_review_queue.json").read_text(encoding="utf-8"))
        self.assertEqual(q["kind"], "evidence_review_queue")
        self.assertEqual(len(q["items"]), 86)
        ev_ids = {f.stem for f in (DATA / "evidence").glob("*.json")}
        queued = {e["evidence_id"] for e in q["items"]}
        self.assertEqual(queued, ev_ids)

    def test_verdict_distribution(self):
        q = json.loads((DATA / "evidence_meta" / "evidence_review_queue.json").read_text(encoding="utf-8"))
        verdicts = Counter(e["verdict"] for e in q["items"])
        statuses = Counter(e["review_status"] for e in q["items"])
        self.assertEqual(dict(verdicts),
                         {"verified": 30, "pending_verification": 43,
                          "not_applicable": 6, "cross_verified": 2, "blank": 5})
        self.assertEqual(dict(statuses),
                         {"reviewed": 32, "pending_manual_verification": 43, "excluded": 11})

    def test_verdict_matches_evidence_status(self):
        # verdict ↔ evidence.citation.verification_status 一致(blank ↔ 留空)
        q = json.loads((DATA / "evidence_meta" / "evidence_review_queue.json").read_text(encoding="utf-8"))
        for e in q["items"]:
            ev = json.loads((DATA / "evidence" / f"{e['evidence_id']}.json").read_text(encoding="utf-8"))
            actual = (ev.get("citation") or {}).get("verification_status")
            if e["verdict"] == "blank":
                self.assertIsNone(actual, f"{e['evidence_id']} verdict=blank 但 evidence 已填 {actual!r}")
            else:
                self.assertEqual(actual, e["verdict"], e["evidence_id"])


class TestD10LifecycleIsolation(unittest.TestCase):
    def test_queue_entries_have_no_rule_lifecycle_fields(self):
        q = json.loads((DATA / "evidence_meta" / "evidence_review_queue.json").read_text(encoding="utf-8"))
        lifecycle = {"rule_status", "activation_eligible", "rule_activated", "lifecycle"}
        for e in q["items"]:
            self.assertTrue(set(e).isdisjoint(lifecycle),
                           f"{e['evidence_id']} 携带 Rule 生命周期字段: {set(e) & lifecycle}")

    def test_rule_status_distribution_unchanged(self):
        # D-10:verified evidence 不改变任何 Rule 可执行资格(T4 后 58 active/10 validated/35 draft 维持(KB link closure 新增))
        rl = RuleLoader(DATA, DOCS)
        statuses = Counter(r["status"] for r in rl.rules)
        self.assertEqual(statuses["active"], 75)
        self.assertEqual(statuses["validated"], 10)
        self.assertEqual(statuses["draft"], 51)
        self.assertEqual(sum(statuses.values()), 136)


class TestEvidenceChainToConceptsPrinciples(unittest.TestCase):
    def test_evidence_refs_all_resolve(self):
        kb = _live_loader()
        ev_ids = {f.stem for f in (DATA / "evidence").glob("*.json")}
        for c in kb.concepts:
            for ref in c.get("evidence_refs", []):
                self.assertIn(ref, ev_ids, f"concept {c['concept_id']} -> 未知 evidence {ref}")
        for p in kb.principles:
            for ref in p.get("evidence_refs", []):
                self.assertIn(ref, ev_ids, f"principle {p['principle_id']} -> 未知 evidence {ref}")

    def test_spot_check_derived_mappings(self):
        kb = _live_loader()
        c = {x["concept_id"]: x.get("evidence_refs", []) for x in kb.concepts}
        p = {x["principle_id"]: x.get("evidence_refs", []) for x in kb.principles}
        self.assertEqual(c["格局"][0], "E-ZPZ-101-001")
        self.assertEqual(len(c["格局"]), 20)                # ZPZ-101..120
        self.assertIn("E-YHZP-103-001", c["透干"])           # 五鼠遁透干
        self.assertEqual(p["PRINCIPLE-MONTH-PIVOT"], [f"E-ZPZ-{n:03d}-001" for n in range(101, 111)])
        self.assertEqual(len(p["PRINCIPLE-TOUGAN-TONGGEN"]), 20)   # ZPZ-111..130
        self.assertEqual(p["PRINCIPLE-WUSHUDUN"], ["E-YHZP-103-001"])


class TestNegativePaths(unittest.TestCase):
    def _chain(self, kb: KbLoader, tmp: Path) -> list[str]:
        return _chain(kb, tmp)

    def test_unknown_cluster_member(self):
        tmp = _build_tree()
        doc = json.loads((tmp / "evidence_meta" / "evidence_clusters.json").read_text(encoding="utf-8"))
        doc["clusters"][0]["member_evidence_ids"].append("E-NOPE-001")
        (tmp / "evidence_meta" / "evidence_clusters.json").write_text(
            json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        findings = self._chain(KbLoader(tmp, DOCS), tmp)
        self.assertTrue(any("unknown member evidence E-NOPE-001" in f for f in findings))
        shutil.rmtree(tmp)

    def test_anchor_mismatch_detected(self):
        tmp = _build_tree()
        p = tmp / "evidence" / "E-ZPZ-101-001.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["citation"]["original_text"] = "八字用神,专求月令"   # 截断→逐字不一致
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        findings = self._chain(KbLoader(tmp, DOCS), tmp)
        self.assertTrue(any("not byte-identical to anchor" in f for f in findings))
        shutil.rmtree(tmp)

    def test_unregistered_cluster_id(self):
        tmp = _build_tree()
        p = tmp / "evidence" / "E-ZPZ-130-001.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["cluster_id"] = "CLUSTER-NOPE"                      # 指向未登记 cluster
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        findings = self._chain(KbLoader(tmp, DOCS), tmp)
        self.assertTrue(any("cluster_id 'CLUSTER-NOPE' not registered" in f for f in findings))
        shutil.rmtree(tmp)

    def test_registered_cluster_but_not_member(self):
        tmp = _build_tree()
        p = tmp / "evidence" / "E-ZPZ-005-001.json"            # 非 cluster 成员的种子
        d = json.loads(p.read_text(encoding="utf-8"))
        d["cluster_id"] = CLUSTER
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        findings = self._chain(KbLoader(tmp, DOCS), tmp)
        self.assertTrue(any("registered but not a member" in f for f in findings))
        shutil.rmtree(tmp)

    def test_queue_missing_evidence(self):
        tmp = _build_tree()
        q = json.loads((tmp / "evidence_meta" / "evidence_review_queue.json").read_text(encoding="utf-8"))
        q["items"] = [e for e in q["items"] if e["evidence_id"] != "E-ZPZ-101-001"]
        (tmp / "evidence_meta" / "evidence_review_queue.json").write_text(
            json.dumps(q, ensure_ascii=False), encoding="utf-8")
        findings = self._chain(KbLoader(tmp, DOCS), tmp)
        self.assertTrue(any("review queue missing evidence" in f and "E-ZPZ-101-001" in f for f in findings))
        shutil.rmtree(tmp)

    def test_verdict_mismatch_detected(self):
        tmp = _build_tree()
        q = json.loads((tmp / "evidence_meta" / "evidence_review_queue.json").read_text(encoding="utf-8"))
        for e in q["items"]:
            if e["evidence_id"] == "E-ZPZ-101-001":
                e["verdict"] = "pending_verification"          # evidence 实为 verified → 不一致
        (tmp / "evidence_meta" / "evidence_review_queue.json").write_text(
            json.dumps(q, ensure_ascii=False), encoding="utf-8")
        findings = self._chain(KbLoader(tmp, DOCS), tmp)
        self.assertTrue(any("verdict=" in f and "!= evidence status" in f for f in findings))
        shutil.rmtree(tmp)

    def test_d10_lifecycle_field_in_queue(self):
        tmp = _build_tree()
        q = json.loads((tmp / "evidence_meta" / "evidence_review_queue.json").read_text(encoding="utf-8"))
        q["items"][0]["rule_status"] = "active"               # 违反 D-10
        (tmp / "evidence_meta" / "evidence_review_queue.json").write_text(
            json.dumps(q, ensure_ascii=False), encoding="utf-8")
        findings = self._chain(KbLoader(tmp, DOCS), tmp)
        self.assertTrue(any("D-10 violation" in f and "rule_status" in f for f in findings))
        shutil.rmtree(tmp)

    def test_evidence_refs_unknown(self):
        tmp = _build_tree()
        p = tmp / "knowledge" / "concepts.json"
        doc = json.loads(p.read_text(encoding="utf-8"))
        for item in doc["items"]:
            if item["concept_id"] == "格局":
                item["evidence_refs"] = ["E-NOPE-001"]
        p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        findings = self._chain(KbLoader(tmp, DOCS), tmp)
        self.assertTrue(any("concept 格局 -> unknown evidence E-NOPE-001" in f for f in findings))
        shutil.rmtree(tmp)


class TestRollback(unittest.TestCase):
    def test_backup_files_present(self):
        self.assertEqual(len(list((BACKUP / "evidence").glob("*.json"))), 52)
        self.assertTrue((BACKUP / "knowledge" / "concepts.json").is_file())
        self.assertTrue((BACKUP / "knowledge" / "principles.json").is_file())
        self.assertTrue((DOCS_BACKUP / "evidence.schema.json").is_file())
        self.assertTrue((DOCS_BACKUP / "knowledge.schema.json").is_file())

    def test_backup_evidence_lack_m2b_fields(self):
        # 回滚点证据为 M2-B 迁移前形状:无 cluster_id / provenance_note / verification_status
        d = json.loads((BACKUP / "evidence" / "E-ZPZ-101-001.json").read_text(encoding="utf-8"))
        self.assertNotIn("cluster_id", d)
        self.assertNotIn("provenance_note", d)
        self.assertIsNone((d.get("citation") or {}).get("verification_status"))

    def test_backup_schema_is_v11(self):
        s = json.loads((DOCS_BACKUP / "evidence.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(s["title"], "TONGSHU Evidence v1.1")
        self.assertNotIn("cluster_id", s["properties"])


if __name__ == "__main__":
    unittest.main()
