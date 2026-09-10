"""BZ-FNDR G0-2 Resolved Provenance — 分级放行 + raw 保留 + G1 不修改 契约测试。

覆盖 15.11 §2（V3+V4 八档）+ 三条施工红线（User 2026-09-10 授权时锁定）:
  - verified / cross_verified / pending / UNVERIFIED / missing / not_applicable /
    disputed / unknown-invalid 八档
  - 大小写归一（PENDING_VERIFICATION ≡ pending_verification, 15.9 §⑦）
  - disputed / unknown 一律 BLOCK
  - 原始字段保留（raw_* 不覆盖, 15.11 §2.3）
  - 本模块【不调用、不改写、不覆盖】 G1（红线 1）
  - 本模块【不产生】 event_type / SHIJIAN mapping（红线 2, 15.14）
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))

from tongshu.governance.evidence_index import EvidenceIndex  # noqa: E402
from tongshu.governance.provenance_resolver import (  # noqa: E402
    ProvenanceResolver,
    ProvenanceTier,
)

_TREE_B = _REPO_ROOT / "data" / "evidence"


def _by_cit_status(idx, value):
    """iter_raw_statuses() 逐资源 yield dict, 按 citation status 抽相对路径。"""
    return [s["relative_path"] for s in idx.iter_raw_statuses()
            if s["raw_citation_verification_status"] == value]


def _by_top_status(idx, value):
    return [s["relative_path"] for s in idx.iter_raw_statuses()
            if s["raw_top_verification_status"] == value]


class TestG02ProvenanceContract(unittest.TestCase):
    """15.11 §2 八档 + raw 保留 + G1 不触碰。"""

    @classmethod
    def setUpClass(cls):
        cls.idx = EvidenceIndex.build(_TREE_B, tree="corpus_base")
        cls.res = ProvenanceResolver(cls.idx)

    # --- 分层放行表（15.11 §2.1） ---
    def test_verified_admitted(self):
        rels = _by_cit_status(self.idx, "verified")
        self.assertGreater(len(rels), 0, "树B 应有 verified 资源（15.9 §① 30 条）")
        for rel in rels[:5]:
            rp = self.res.resolve(rel)
            self.assertEqual(rp.tier, ProvenanceTier.VERIFIED)
            self.assertTrue(rp.admitted)
            self.assertNotIn("PROVENANCE-PENDING", rp.claim_markers)

    def test_cross_verified_admitted_with_marker(self):
        rels = _by_cit_status(self.idx, "cross_verified")
        for rel in rels[:3]:
            rp = self.res.resolve(rel)
            self.assertEqual(rp.tier, ProvenanceTier.CROSS_VERIFIED)
            self.assertTrue(rp.admitted)
            self.assertIn("CROSS-VERIFIED", rp.claim_markers)

    def test_pending_admitted_with_provenance_pending_marker(self):
        """V3: pending 系放行 + PROVENANCE-PENDING（不 BLOCK）。"""
        rels = _by_cit_status(self.idx, "pending_verification")
        for rel in rels[:5]:
            rp = self.res.resolve(rel)
            self.assertEqual(rp.tier, ProvenanceTier.PENDING,
                             f"pending_verification 应归 PENDING: {rel}={rp.tier}")
            self.assertTrue(rp.admitted, "pending 不得 BLOCK（V3 裁决）")
            self.assertIn("PROVENANCE-PENDING", rp.claim_markers)

    def test_unverified_top_level_admitted_with_marker(self):
        """V3: UNVERIFIED（顶层抽取批占位）放行 + PROVENANCE-PENDING。"""
        rels = _by_top_status(self.idx, "UNVERIFIED")
        self.assertGreater(len(rels), 1000, "15.9: UNVERIFIED≈1412（顶层）")
        for rel in rels[:5]:
            rp = self.res.resolve(rel)
            self.assertEqual(rp.tier, ProvenanceTier.UNVERIFIED)
            self.assertTrue(rp.admitted)
            self.assertIn("PROVENANCE-PENDING", rp.claim_markers)

    def test_missing_both_layers(self):
        """顶层 + 嵌套双缺失 → MISSING 档（放行但显式标记, 不伪装已核验）。"""
        rels = [s["relative_path"] for s in self.idx.iter_raw_statuses()
                if s["raw_top_verification_status"] == "<MISSING>"
                and s["raw_citation_verification_status"] == "<MISSING>"]
        self.assertGreater(len(rels), 50, "15.9: 顶层缺失 + 嵌套缺失 大量存在")
        for rel in rels[:3]:
            rp = self.res.resolve(rel)
            self.assertEqual(rp.tier, ProvenanceTier.MISSING)
            self.assertTrue(rp.admitted)
            self.assertIn("PROVENANCE-PENDING", rp.claim_markers,
                          "缺失档必须显式标记, 不得伪装 verified")

    def test_not_applicable_admitted_with_engineering_marker(self):
        rels = _by_cit_status(self.idx, "not_applicable")
        for rel in rels[:3]:
            rp = self.res.resolve(rel)
            self.assertEqual(rp.tier, ProvenanceTier.NOT_APPLICABLE)
            self.assertTrue(rp.admitted)
            self.assertIn("PROVENANCE-ENGINEERING", rp.claim_markers)

    def test_disputed_blocks(self):
        """V3 表：disputed → BLOCK，不得产生生产 claim。"""
        any_rel = next(iter(self.idx.by_relpath))
        rp = self.res._build(
            identity=self.idx.by_relpath[any_rel],
            tier=ProvenanceTier.DISPUTED,
            raw_top="disputed", raw_cit="disputed",
        )
        self.assertFalse(rp.admitted)
        self.assertEqual(rp.to_claim_mark().split(":")[0], "BLOCK")

    def test_unknown_or_invalid_blocks(self):
        """V3 表：未知/非法值 → BLOCK（不得静默放行）。"""
        any_rel = next(iter(self.idx.by_relpath))
        rp = self.res._build(
            identity=self.idx.by_relpath[any_rel],
            tier=ProvenanceTier.UNKNOWN,
            raw_top="FUTURE_STATUS_XYZ", raw_cit="FUTURE_STATUS_XYZ",
        )
        self.assertFalse(rp.admitted)

    def test_unknown_status_from_resolve(self):
        """经 _resolve_tier 走未知值：任一取到未知即一票 BLOCK。"""
        tier = self.res._resolve_tier("FUTURE_STATUS_XYZ", "<MISSING>")
        self.assertEqual(tier, ProvenanceTier.UNKNOWN)

    # --- 大小写归一（15.9 §⑦） ---
    def test_case_insensitive_normalization(self):
        """PENDING_VERIFICATION（15.9 §⑦ 大小写变体）≡ pending_verification。"""
        tier = self.res._resolve_tier("PENDING_VERIFICATION", "<MISSING>")
        self.assertEqual(tier, ProvenanceTier.PENDING,
                         "大小写变体必须归一到 PENDING 档")
        tier2 = self.res._resolve_tier("source_verification_required", "<MISSING>")
        self.assertEqual(tier2, ProvenanceTier.PENDING,
                         "SOURCE_VERIFICATION_REQUIRED 归并 PENDING 系")

    # --- 红线 1: G1 不修改 ---
    def test_g1_module_untouched_by_resolver(self):
        """红线 1: G0-2 不 import / 不调用 / 不改写 G1。
        允许模块 docstring 提及 "g1_evidence.py"（红线陈述）, 但不得 import/调用。"""
        text = (_REPO_ROOT / "src" / "tongshu" / "governance" / "provenance_resolver.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("import g1_evidence", text)
        self.assertNotIn("from ..audit_validation", text)
        self.assertNotIn("from .audit_validation", text)
        self.assertNotIn("evidence_gate(", text, "不得调用 G1 gate 函数")
        self.assertNotIn("gate_evidence(", text)

    # --- 红线 2: 不夹带 SHIJIAN / event ---
    def test_no_event_method_leak(self):
        text = (_REPO_ROOT / "src" / "tongshu" / "governance" / "provenance_resolver.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("event_type", text)
        self.assertNotIn("SHIJIAN", text)
        self.assertNotIn("EVENT_MAPPING", text)

    # --- raw 保留（15.11 §2.3） ---
    def test_raw_fields_preserved(self):
        rels = _by_cit_status(self.idx, "verified")
        rel = rels[0]
        rp = self.res.resolve(rel)
        self.assertEqual(rp.raw_citation_verification_status, "verified",
                         "原始字段必须原样保留, 不得被 Resolved 层覆盖")
        self.assertEqual(rp.tier, ProvenanceTier.VERIFIED)

    # --- 统计面（15.9 对账基线） ---
    def test_tier_summary_covers_all_resources(self):
        ts = self.res.tier_summary()
        self.assertEqual(sum(ts.values()), len(self.idx.by_relpath),
                         "tier_summary 覆盖所有 Index 资源（无遗漏）")


if __name__ == "__main__":
    unittest.main()
