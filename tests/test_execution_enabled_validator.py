# -*- coding: utf-8 -*-
"""B-6 硬规则校验测试。"""

from __future__ import annotations
import unittest
import json
import tempfile
from pathlib import Path

from tongshu.reasoning.execution_enabled_validator import (
    ExecutionEnabledValidator,
    RuleChainResult,
)


class TestExecutionEnabledValidator(unittest.TestCase):
    """B-6 硬规则校验器单元测试。"""

    def setUp(self):
        """创建临时目录和索引数据。"""
        self.tmpdir = tempfile.mkdtemp()

        # 创建 mappings 目录和数据
        self.mappings_dir = Path(self.tmpdir) / "mappings"
        self.mappings_dir.mkdir()
        self._write_json(self.mappings_dir / "M-001.json", {
            "mapping_id": "M-001",
            "concept_id": "C-001",
            "source_type": "semantic",
        })

        # 创建 concepts 目录和数据
        self.concepts_dir = Path(self.tmpdir) / "concepts"
        self.concepts_dir.mkdir()
        self._write_json(self.concepts_dir / "C-001.json", {
            "concept_id": "C-001",
            "source_refs": [{"evidence_id": "E-001"}],
        })

        # 创建 evidence 目录和数据
        self.evidence_dir = Path(self.tmpdir) / "evidence"
        self.evidence_dir.mkdir()
        self._write_json(self.evidence_dir / "E-001.json", {
            "evidence_id": "E-001",
            "source_layer": "classical_original",
            "verification_status": "verified",
        })

        self.validator = ExecutionEnabledValidator(
            rules_dir=Path(self.tmpdir) / "rules",
            mappings_dir=self.mappings_dir,
            concepts_dir=self.concepts_dir,
            evidence_dir=self.evidence_dir,
        )

    @staticmethod
    def _write_json(path: Path, data: dict) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def test_valid_chain_with_enabled(self):
        """完整链：rule → mapping → concept → evidence，应通过。"""
        rule = {
            "rule_id": "R-001",
            "execution_enabled": True,
            "rule_refs": [{"mapping_id": "M-001"}],
        }
        result = self.validator.validate_rule(rule)
        self.assertTrue(result.chain_valid)
        self.assertFalse(result.degraded)

    def test_missing_mapping(self):
        """rule_refs 指向不存在的 mapping，应失败。"""
        rule = {
            "rule_id": "R-002",
            "execution_enabled": True,
            "rule_refs": [{"mapping_id": "M-NOTEXIST"}],
        }
        result = self.validator.validate_rule(rule)
        self.assertFalse(result.chain_valid)
        self.assertTrue(result.degraded)
        self.assertGreater(len(result.violations), 0)

    def test_missing_concept(self):
        """mapping 指向不存在的 concept，应失败。"""
        self._write_json(self.mappings_dir / "M-002.json", {
            "mapping_id": "M-002",
            "concept_id": "C-NOTEXIST",
        })
        rule = {
            "rule_id": "R-003",
            "execution_enabled": True,
            "rule_refs": [{"mapping_id": "M-002"}],
        }
        result = self.validator.validate_rule(rule)
        self.assertFalse(result.chain_valid)
        self.assertTrue(result.degraded)

    def test_missing_evidence(self):
        """concept 指向不存在的 evidence，应失败。"""
        self._write_json(self.concepts_dir / "C-002.json", {
            "concept_id": "C-002",
            "source_refs": [{"evidence_id": "E-NOTEXIST"}],
        })
        self._write_json(self.mappings_dir / "M-003.json", {
            "mapping_id": "M-003",
            "concept_id": "C-002",
        })
        rule = {
            "rule_id": "R-004",
            "execution_enabled": True,
            "rule_refs": [{"mapping_id": "M-003"}],
        }
        result = self.validator.validate_rule(rule)
        self.assertFalse(result.chain_valid)
        self.assertTrue(result.degraded)

    def test_disabled_rule_passes(self):
        """execution_enabled=false 的 rule 应自动通过。"""
        rule = {
            "rule_id": "R-005",
            "execution_enabled": False,
            "rule_refs": [],
        }
        result = self.validator.validate_rule(rule)
        self.assertTrue(result.chain_valid)
        self.assertFalse(result.degraded)

    def test_no_rule_refs(self):
        """execution_enabled=true 但无 rule_refs，应失败。"""
        rule = {
            "rule_id": "R-006",
            "execution_enabled": True,
            "rule_refs": [],
        }
        result = self.validator.validate_rule(rule)
        self.assertFalse(result.chain_valid)
        self.assertTrue(result.degraded)


if __name__ == "__main__":
    unittest.main()
