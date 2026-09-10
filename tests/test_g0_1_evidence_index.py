"""BZ-FNDR G0-1 Evidence Index — 契约测试（Construction Test）。

覆盖 15.11 §1.4 锁定的 Index 契约 + 15.10 对账事实（作为审计基线常数钉死）:
  - Corpus Base = data/evidence（tree B）, Legacy Snapshot = backend/data/evidence（tree A）
  - Stable Resource ID ≠ 文件系统路径（resolve 走 Logical URI, 路径可重定位）
  - 非资源排除（manifest / reports / no-evidence-id 内容判定）
  - 同 ID 多实例不折叠（15.10 §2 的 12 组）
  - schema6 合规面（15.10 §4: B=4240, A=141）
  - P0 路径独立性（模块内 0 绝对路径）
  - SHIJIAN 红线（15.14: 本模块不含 event_type / event mapping）
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))

from tongshu.governance.evidence_index import (  # noqa: E402
    EvidenceIndex,
    ResourceIdentity,
)

_TREE_B = _REPO_ROOT / "data" / "evidence"
_TREE_A = _REPO_ROOT / "backend" / "data" / "evidence"


class TestG01IndexContract(unittest.TestCase):
    """15.11 §1.4 契约: Index 消费 Corpus Base, 非 rglob 黑盒事实来源。"""

    @classmethod
    def setUpClass(cls):
        cls.idx_b = EvidenceIndex.build(_TREE_B, tree="corpus_base")
        cls.idx_a = EvidenceIndex.build(_TREE_A, tree="legacy_snapshot")

    def test_15_10_audit_counts_tree_b(self):
        """15.10 对账基线: tree B 证据资源 / schema 合规 / 唯一 ID / 非资源排除。"""
        s = self.idx_b.summary()
        # 15.10: tree B evidence files=5693, 排除 manifest+reports 段后内容判定
        self.assertEqual(s["schema_compliant"], 4240, "15.10 §4: tree B schema6=4240")
        self.assertEqual(s["unique_evidence_ids"], 5668, "15.10 §1: tree B 唯一 ID=5668")
        self.assertGreaterEqual(s["total_resources"], 5600)
        # 非资源（no_evidence_id + reports 段名级排除）: 15.10 登记 21 项中内容判定面
        self.assertGreaterEqual(s["excluded_non_resource"], 10)

    def test_15_10_audit_counts_tree_a(self):
        s = self.idx_a.summary()
        self.assertEqual(s["schema_compliant"], 141, "15.10 §4: tree A schema6=141")
        self.assertEqual(s["unique_evidence_ids"], 1563, "15.10 §1: tree A 唯一 ID=1563")

    def test_multi_instance_ids_preserved(self):
        """15.10 §2: 同 ID 多文件（根级-子目录双份等）不得被 Index 折叠为 1:1。"""
        ids = self.idx_b.summary()["multi_instance_ids"]
        # 15.10 §2 登记的 12 组同 ID 多文件（两树同构）
        self.assertGreaterEqual(len(ids), 12, "12 组同 ID 多文件必须全部保留可见")
        # DTS 根级/子目录双份必须在其中
        self.assertIn("E-DTS-106-001", ids)
        self.assertGreaterEqual(len(ids["E-DTS-106-001"]), 2)

    def test_a_only_resource_not_in_tree_b(self):
        """15.10 §1: E-DTS-145-001 为唯一 A-only, tree B Index 中不得出现。"""
        self.assertNotIn("E-DTS-145-001", self.idx_b.by_evidence_id)
        self.assertIn("E-DTS-145-001", self.idx_a.by_evidence_id)

    def test_logical_uri_identity_not_path(self):
        """契约: Stable Resource ID ≠ 文件系统路径（resolve 经 Logical URI）。"""
        inst = self.idx_b.instances_of("E-DTS-101-001")
        self.assertGreaterEqual(len(inst), 2, "根级 + di_tian_sui/ 双份同 ID")
        for ident in inst:
            self.assertTrue(ident.logical_uri.startswith("evid://corpus_base/"))
            # Runtime Resolver: URI → 部署内实际路径（可重定位, 不写死）
            resolved = self.idx_b.resolve(ident.logical_uri)
            self.assertIsNotNone(resolved)
            self.assertTrue(resolved.is_file())

    def test_no_absolute_paths_in_module(self):
        """P0 路径独立性红线: governance 包内 0 开发机绝对路径。"""
        for f in ("evidence_index", "provenance_resolver"):
            p = _REPO_ROOT / "src" / "tongshu" / "governance" / (f + ".py")
            if p.exists():
                text = p.read_text(encoding="utf-8")
                self.assertIsNone(
                    re.search(r"['\"]([A-Za-z]:[/\\\\])|(/srv/|/home/|/Users/)", text),
                    f"路径独立性违规: {p.name}",
                )

    def test_no_shijian_event_method_leak(self):
        """15.14 红线: G0-1 基础设施不得夹带 SHIJIAN / event mapping。"""
        text = (_REPO_ROOT / "src" / "tongshu" / "governance" / "evidence_index.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("event_type", text)
        self.assertNotIn("SHIJIAN", text)
        self.assertNotIn("EVENT_MAPPING", text)


if __name__ == "__main__":
    unittest.main()
