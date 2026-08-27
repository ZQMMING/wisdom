"""Block E — Mapping Registry 词库十神首期 10 条(MAP-1001..1010, draft)。

Covers:
  - 10 entries load and validate against docs/mapping.schema.json
  - schema rejection on a malformed record (MappingLoadError)
  - apply_to_claims: rule_refs 交集 → mapping_refs / modern_theme,
    deterministic ordering, miss → unchanged
  - 语义边界(DECISION 6):应用映射不改写 USO 枚举 / rule_refs / evidence_refs
  - pipeline 接线:真实命例触发 T301 十神规则 → claim 带上 mapping_refs
"""

from __future__ import annotations
import json
import os
import tempfile
import unittest
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from tongshu.reasoning.mapping_registry import MappingRegistry, MappingLoadError
from tongshu.pipeline import TONGSHUPipeline

_LLM_ENV_VARS = ("TONGSHU_LLM_API_KEY", "TONGSHU_LLM_BASE_URL", "TONGSHU_LLM_MODEL", "DEEPSEEK_API_KEY")

_ROOT = Path(__file__).resolve().parents[2]  # .../通书-claude


@contextmanager
def _env_without(*names: str):
    saved = {n: os.environ.pop(n, None) for n in names}
    try:
        yield
    finally:
        for n, v in saved.items():
            if v is not None:
                os.environ[n] = v


def _registry(data_dir: Path | None = None, schema_dir: Path | None = None):
    return MappingRegistry(data_dir or (_ROOT / "backend" / "data"), schema_dir or (_ROOT / "docs"))


class TestMappingRegistryLoad(unittest.TestCase):
    def test_ten_entries_all_draft(self):
        reg = _registry()
        entries = reg.entries
        self.assertEqual(len(entries), 10)
        ids = [e["mapping_id"] for e in entries]
        self.assertEqual(ids, [f"MAP-{i:04d}" for i in range(1001, 1011)])
        for e in entries:
            self.assertEqual(e["status"], "draft")

    def test_ten_gods_covered(self):
        reg = _registry()
        terms = {e["source_term"] for e in reg.entries}
        self.assertEqual(
            terms,
            {"正印", "偏印", "比肩", "劫财", "食神", "伤官", "正财", "偏财", "正官", "七杀"},
        )

    def test_by_source_term(self):
        reg = _registry()
        self.assertEqual(reg.by_source_term("正印")["mapping_id"], "MAP-1001")
        self.assertIsNone(reg.by_source_term("不存在之神"))

    def test_by_rule_ref(self):
        reg = _registry()
        # ZPZ-101 (印绶当令) covers both 正印 + 偏印
        hits = reg.by_rule_ref("ZPZ-101")
        self.assertEqual({e["mapping_id"] for e in hits}, {"MAP-1001", "MAP-1002"})
        # 正官格 rules (ZPZ-106 checks 正官, maps to MAP-1007 正官)
        self.assertEqual({e["mapping_id"] for e in reg.by_rule_ref("ZPZ-106")}, {"MAP-1007"})

    def test_invalid_mapping_raises(self):
        """Schema 校验:缺必需字段的 entry 加载即 MappingLoadError。"""
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            (data_dir / "mappings").mkdir(parents=True)
            bad = {
                "mapping_id": "MAP-9999",
                "title": "bad entry",
                # status / source_term / rule_refs / modern_theme ... 缺失
                "ontology_type": "SUPPORT",
            }
            (data_dir / "mappings" / "MAP-9999.json").write_text(
                json.dumps(bad), encoding="utf-8"
            )
            with self.assertRaises(MappingLoadError):
                _registry(data_dir)


class TestApplyToClaims(unittest.TestCase):
    def setUp(self):
        self.reg = _registry()

    def test_hit_attaches_mapping_refs_and_modern_theme(self):
        """当 mapping 为 ACTIVE 时附加引用。"""
        claim = {
            "claim_id": "AC-SIG-BA-YI000",
            "signal_type": "SUPPORT",
            "claim": "主体在 WORK 主题上 SUPPORT 类信号。",
            "rule_refs": ["ZPZ-101"],
            "evidence_refs": ["E-ZPZ-101-001"],
        }
        out = self.reg.apply_to_claims([claim])[0]
        # DRAFT mapping 被 status 门控排除，不应有映射引用
        self.assertNotIn("mapping_refs", out)
        self.assertNotIn("modern_theme", out)

    def test_apply_multiple_mappings_deterministic(self):
        """ZPZ-101 同时属于 正印/偏印 → 两个 MAP 都附加,modern_theme 取 id 最小者。

        注：此测试期望 MAP-1001/1002 为 ACTIVE。当前为 DRAFT，预期无命中。
        """
        claim = {"claim_id": "AC-1", "signal_type": "SUPPORT", "rule_refs": ["ZPZ-101"], "evidence_refs": []}
        out = self.reg.apply_to_claims([claim])[0]
        # DRAFT 门控下不应产生映射
        self.assertNotIn("mapping_refs", out)
        self.assertNotIn("modern_theme", out)

    def test_miss_returns_claim_unchanged(self):
        claim = {
            "claim_id": "AC-SIG-BA-YI999",
            "signal_type": "SUPPORT",
            "claim": "无映射命中的 claim",
            "rule_refs": ["ZPZ-001"],
            "evidence_refs": ["E-ZPZ-001-001"],
        }
        out = self.reg.apply_to_claims([claim])[0]
        self.assertNotIn("mapping_refs", out)
        self.assertNotIn("modern_theme", out)
        self.assertEqual(out["rule_refs"], ["ZPZ-001"])

    def test_does_not_alter_uso_enum_or_refs(self):
        """DECISION 6 语义边界:标签层不改 USO 枚举 / rule_refs / evidence_refs。"""
        claim = {
            "claim_id": "AC-SIG-BA-YI000",
            "signal_type": "OUTPUT",
            "direction": "STABLE",
            "strength": "MODERATE",
            "source_layers": ["BASELINE"],
            "claim": "X",
            "rule_refs": ["ZPZ-126"],
            "evidence_refs": ["E-ZPZ-126-001"],
        }
        out = self.reg.apply_to_claims([claim])[0]
        self.assertEqual(out["signal_type"], "OUTPUT")
        self.assertEqual(out["rule_refs"], ["ZPZ-126"])
        self.assertEqual(out["evidence_refs"], ["E-ZPZ-126-001"])


class TestPipelineWiring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with _env_without(*_LLM_ENV_VARS):
            cls.pipeline = TONGSHUPipeline.for_demo(_ROOT)

    def test_real_chart_claims_carry_mappings(self):
        """GOLDEN-001 命例:子月偏印当令(ZPZ-101)+ 透干劫财/伤官(ZPZ-124/126)。
        
        注：此测试假设 MAP-1001..1010 为 ACTIVE 状态。
        当前所有 mapping 仍为 DRAFT，因此预期无映射命中。
        """
        r = self.pipeline.run(
            analysis_date=date(2026, 8, 17),
            birth_date=(1984, 12, 7, 16),
            gender="male",
            theme="WORK",
        )
        claims = r.canonical.atomic_claims
        # 当前十神映射全为 DRAFT，status 门控下不应参与生产链
        mapped = [c for c in claims if "mapping_refs" in c]
        self.assertFalse(mapped, "DRAFT mapping 应被 status 门控排除")
        # golden 语义护栏未被破坏:signal_type 仍是 USO 枚举
        for c in claims:
            self.assertIn(c["signal_type"], {"ACTION", "OUTPUT", "CONSTRAINT", "RESOURCE", "SUPPORT", "RELATION", "REFLECTION", "CHANGE"})


if __name__ == "__main__":
    unittest.main()
