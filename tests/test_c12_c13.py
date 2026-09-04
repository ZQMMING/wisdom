"""C9P2A C12/C13 交付测试（纯逻辑，不连 DB）。

覆盖:
  - C12 evidence_clusters 回填: 源 JSON 结构、30 成员、schema 合规、投影正确
  - C13 source_copies 双源门: 缺 edition_provenance 必拒、双源+出处才接受、
    诚实零伪造（不允许把审计记录当 verified 副本）
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "backend" / "scripts"


def _load_script(name: str):
    path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(name[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BL = _load_script("shuntian_backfill_clusters.py")
SY = _load_script("shuntian_sync_source_copies.py")


class TestC12EvidenceClustersBackfill(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clusters = BL.collect_clusters()
        cls.data = json.loads(BL.CLUSTERS_JSON.read_text(encoding="utf-8"))

    def test_json_kind(self):
        self.assertEqual(self.data["kind"], "evidence_clusters")

    def test_cluster_exists(self):
        ids = {c["cluster_id"] for c in self.clusters}
        self.assertIn("CLUSTER-ZPZ-YONGSHEN-ANCHOR", ids)

    def test_member_count_30(self):
        for c in self.clusters:
            if c["cluster_id"] == "CLUSTER-ZPZ-YONGSHEN-ANCHOR":
                self.assertEqual(len(c["member_evidence_ids"]), 30)
                return
        self.fail("cluster not found")

    def test_members_are_E_ZPZ_101_130(self):
        for c in self.clusters:
            if c["cluster_id"] == "CLUSTER-ZPZ-YONGSHEN-ANCHOR":
                expected = {f"E-ZPZ-{i:03d}-001" for i in range(101, 131)}
                self.assertEqual(set(c["member_evidence_ids"]), expected)
                return

    def test_member_ids_unique(self):
        for c in self.clusters:
            self.assertEqual(len(c["member_evidence_ids"]), len(set(c["member_evidence_ids"])))

    def test_anchor_fields(self):
        for c in self.clusters:
            for k in ("passage_id", "book_id", "chapter_id", "edition_id", "anchor_text"):
                self.assertIn(k, c)

    def test_projection_fields(self):
        """DB 投影字段映射完整（cluster_id/anchor_text/member_ids/passage_id）。"""
        for c in self.clusters:
            self.assertTrue(c["anchor_text"].strip())
            self.assertTrue(c["passage_id"].startswith("P-"))
            self.assertRegex(c["cluster_id"], r"^CLUSTER-")


class TestC13SourceCopyGate(unittest.TestCase):
    def _audit(self, **over):
        base = dict(
            audit_id="AUD_T1_001", source_id="T1", book_id="B1", source_name="src",
            source_url="https://x", source_type="数字化底本", reliability="high",
            verified_passages=3, pending_passages=0, last_checked="2026-08-19",
        )
        base.update(over)
        return base

    def test_reject_missing_provenance(self):
        """无 publisher/year/pages → 必拒（M1 裁决三）。"""
        auds = [self._audit(audit_id="A", source_id="T1"),
                self._audit(audit_id="B", source_id="T1")]
        ev = SY.evaluate_candidates(auds)
        cands = ev["T1"]
        self.assertEqual(len(cands), 2)
        for c in cands:
            self.assertTrue(c["_candidate_reason"].startswith("REJECT"))
        self.assertEqual(SY.build_copy_rows(ev), [])

    def test_accept_with_provenance_and_dual_source(self):
        """补全 provenance + 双源 high → ACCEPT（机制可达，非死代码）。"""
        auds = [
            self._audit(audit_id="A", source_id="T1", publisher="中华书局", year=2004, pages="1-300"),
            self._audit(audit_id="B", source_id="T1", publisher="古籍社", year=1999, pages="1-300"),
        ]
        ev = SY.evaluate_candidates(auds)
        cands = ev["T1"]
        # 两候选均具备 provenance + 同书 ≥2 条 high → ACCEPT
        self.assertTrue(all(c["_candidate_reason"] == "ACCEPT" for c in cands))
        rows = SY.build_copy_rows(ev)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][-1], "verified")

    def test_reject_single_source_even_with_provenance(self):
        """单来源即使有出处也拒（条件 2 双源）。"""
        auds = [
            self._audit(audit_id="A", source_id="T1", publisher="中华书局", year=2004, pages="1-300"),
            self._audit(audit_id="B", source_id="T1", source_type="现代整理", reliability="medium"),
        ]
        ev = SY.evaluate_candidates(auds)
        cands = ev["T1"]
        # 仅候选 A；B 不是候选（现代整理/medium）
        self.assertEqual(len(cands), 1)
        self.assertTrue(cands[0]["_candidate_reason"].startswith("REJECT"))

    def test_modern_reorganization_not_candidate(self):
        """现代整理本不构成底本候选。"""
        auds = [
            self._audit(audit_id="A", source_id="T1", source_type="现代整理"),
        ]
        ev = SY.evaluate_candidates(auds)
        self.assertNotIn("T1", ev)

    def test_honest_zero_no_fabrication(self):
        """当前 15 条真实审计 → 0 通过门，不伪造任何 verified 行。"""
        # 使用真实 source_audits 形状（无 provenance 列）
        real = [
            self._audit(audit_id=f"AUD_{b}_{i:03d}", source_id=b, verified_passages=(5 if i == 0 else 0))
            for b in ("DTS", "PZZQ", "QTBJ", "SMTH", "YHZP")
            for i in (0, 1, 2)
        ]
        ev = SY.evaluate_candidates(real)
        self.assertEqual(SY.build_copy_rows(ev), [])


if __name__ == "__main__":
    unittest.main()
