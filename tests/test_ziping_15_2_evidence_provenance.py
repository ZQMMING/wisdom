"""BZ-FNDR-15.4-P0-1 (⑮-2 Evidence Provenance): 三项 CITATION 元数据修正测试.

User 裁决 (2026-09-10) A3:
  DTS-102   -> E-DTS-101-001   (复用得令, 反义关系)
  SMTH-102  -> E-SMTH-101-001  (复用旺位, 反义关系)
  YHZP-105  -> E-YHZP-105-001  (卷一·论岁君 YHZP_2447)

本测试锁死三项 CITATION evidence_id 元数据 + 实测 _Citations 累积输出.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tongshu.reasoning.judgment import CITATION, _Citations

# BZ-FNDR-15.4 P0-2: repo-relative path resolver (替代 D:/shuntian/... 绝对路径)
_REPO_ROOT = Path(__file__).resolve().parents[1]
_EVIDENCE_DIR_BACKEND = _REPO_ROOT / "backend" / "data" / "evidence"
_EVIDENCE_DIR_FRONTEND = _REPO_ROOT / "data" / "evidence"


def _evidence_path(relative):
    """Resolve evidence resource path via repo-relative (no absolute project root)."""
    backend = _EVIDENCE_DIR_BACKEND / relative
    if backend.exists():
        return backend
    frontend = _EVIDENCE_DIR_FRONTEND / relative
    return frontend


class TestCitationMetadata(unittest.TestCase):
    """P0-1: CITATION 元数据三项修正必须落到源码."""

    def test_dts_102_uses_e_dts_101_001(self):
        """DTS-102 (失令) -> E-DTS-101-001 (得令, 反义关系复用)."""
        rule_id, evidence_id = CITATION["DTS-102"]
        self.assertEqual(rule_id, "DTS-102")
        self.assertEqual(
            evidence_id, "E-DTS-101-001",
            "DTS-102 evidence_id 应 = E-DTS-101-001 (复用得令, 反义关系)",
        )

    def test_smth_102_uses_e_smth_101_001(self):
        """SMTH-102 (十二宫弱位) -> E-SMTH-101-001 (十二宫旺位, 反义关系复用)."""
        rule_id, evidence_id = CITATION["SMTH-102"]
        self.assertEqual(rule_id, "SMTH-102")
        self.assertEqual(
            evidence_id, "E-SMTH-101-001",
            "SMTH-102 evidence_id 应 = E-SMTH-101-001 (复用旺位, 反义关系)",
        )

    def test_yhzp_105_uses_e_yhzp_105_001(self):
        """YHZP-105 (阳刃透杀制伏) -> E-YHZP-105-001 (卷一·论岁君 YHZP_2447)."""
        rule_id, evidence_id = CITATION["YHZP-105"]
        self.assertEqual(rule_id, "YHZP-105")
        self.assertEqual(
            evidence_id, "E-YHZP-105-001",
            "YHZP-105 evidence_id 应 = E-YHZP-105-001 (实际 evidence 真实存在, 元数据已修正)",
        )

    def test_no_citation_entry_still_none(self):
        """修正后 CITATION 表内不应再有 evidence_id=None 的项.

        (DTS-102 / SMTH-102 复用其他 evidence — 是合法的 evidence_id, 不是 None.
         所有真实缺 evidence 的 Rule 应在另一轮处理, 不留 None.)
        """
        none_count = sum(
            1 for rule_id, ev_id in CITATION.values() if ev_id is None
        )
        self.assertEqual(
            none_count, 0,
            f"CITATION 仍有 {none_count} 个 evidence_id=None (P0-1 后应清零)",
        )


class TestCitationsAccumulation(unittest.TestCase):
    """P0-1: 实测 _Citations.add() 累积输出 — 三个 Rule 的 evidence_refs 必须挂上."""

    def test_dts_102_adds_evidence_ref(self):
        """DTS-102 -> evidence_refs 应含 E-DTS-101-001."""
        c = _Citations()
        c.add("DTS-102")
        self.assertIn(
            "E-DTS-101-001", c.evidence_refs,
            "DTS-102 evidence_refs 应含 E-DTS-101-001",
        )

    def test_smth_102_adds_evidence_ref(self):
        """SMTH-102 -> evidence_refs 应含 E-SMTH-101-001."""
        c = _Citations()
        c.add("SMTH-102")
        self.assertIn(
            "E-SMTH-101-001", c.evidence_refs,
            "SMTH-102 evidence_refs 应含 E-SMTH-101-001",
        )

    def test_yhzp_105_adds_evidence_ref(self):
        """YHZP-105 -> evidence_refs 应含 E-YHZP-105-001."""
        c = _Citations()
        c.add("YHZP-105")
        self.assertIn(
            "E-YHZP-105-001", c.evidence_refs,
            "YHZP-105 evidence_refs 应含 E-YHZP-105-001",
        )

    def test_combined_wangshuai_citations_now_complete(self):
        """完整 WANGSHUAI 路径 — 所有 8 个 Rule 的 evidence 都应挂上.

        修正前: DTS-102 / SMTH-102 / DTS-107 等 evidence_refs 缺失 (断链).
        修正后: 8 个 rule_refs + 8 个 evidence_refs 一一对应.
        """
        c = _Citations()
        for k in [
            "DTS-101", "DTS-102", "DTS-104", "DTS-105",
            "DTS-106", "DTS-107", "SMTH-101", "SMTH-102",
        ]:
            c.add(k)
        # 修正前: DTS-102 / SMTH-102 的 evidence_id=None, 累积后 evidence_refs 只有 5 个
        # 修正后: DTS-102 / SMTH-102 复用同源 evidence, 累积后 evidence_refs 应为 6 个 (去重后)
        # (DTS-101/102 共用 E-DTS-101-001, SMTH-101/102 共用 E-SMTH-101-001 → 去重)
        self.assertEqual(len(c.rule_refs), 8)
        self.assertEqual(len(c.evidence_refs), 6,
                         f"修正后 8 个 rule 应累积到 6 个 evidence_refs (去重后), "
                         f"实际只累积 {len(c.evidence_refs)} 个")
        # DTS-102 / SMTH-102 复用同源 evidence 必须挂上
        self.assertIn("E-DTS-101-001", c.evidence_refs)
        self.assertIn("E-SMTH-101-001", c.evidence_refs)


class TestEvidenceResourceExists(unittest.TestCase):
    """P0-1: 修正后的 evidence_id 必须有真实资源对应 (filesystem 验证)."""

    def test_e_dts_101_001_exists(self):
        # BZ-FNDR-15.4 P0-2: repo-relative (was D:/shuntian/backend/data/evidence/E-DTS-101-001.json)
        self.assertTrue(
            _evidence_path("E-DTS-101-001.json").exists(),
            "E-DTS-101-001.json 必须存在 (DTS-102 复用)",
        )

    def test_e_smth_101_001_exists(self):
        # BZ-FNDR-15.4 P0-2: repo-relative
        self.assertTrue(
            _evidence_path("E-SMTH-101-001.json").exists(),
            "E-SMTH-101-001.json 必须存在 (SMTH-102 复用)",
        )

    def test_e_yhzp_105_001_exists(self):
        """E-YHZP-105-001 在 yuan_hai_zi_ping/ 子目录 (不是 evidence/ 根下)."""
        # BZ-FNDR-15.4 P0-2: repo-relative (was D:/shuntian/backend/data/evidence/yuan_hai_zi_ping/...)
        candidates = [
            _evidence_path("yuan_hai_zi_ping/E-YHZP-105-001.json"),
        ]
        self.assertTrue(
            any(p.exists() for p in candidates),
            "E-YHZP-105-001.json (在 yuan_hai_zi_ping/ 子目录) 必须存在",
        )


if __name__ == "__main__":
    unittest.main()
