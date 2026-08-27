"""Block D — canonical `meta` 版本族 + v36 schema 校验切换。

Covers V3.6 §6 meta (11 字段版本族 + 可观测性三件套):
  - pipeline 构建完整 meta,所有模式/const 合法
  - 带 meta 的 canonical 通过 v36 schema(01_CANONICAL_SCHEMA.json)
  - 无 meta 的旧形状 SIR 仍通过(超集性质,保护 golden)
  - meta present-but-incomplete 被拒绝(无部分状态)
  - 可观测性三件套一致:meta.request_id == audit.request_id、
    trace_id 透传或自生成、document_id == canonical_id

Runs against the real TONGSHUPipeline with the deterministic Stub renderer
(env keys cleared in setUpClass). The audit log is append-only and shared,
so each test reads the last line right after its own pipeline.run.
"""

from __future__ import annotations
import json
import os
import unittest
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

from tongshu.canonical.canonical_validator import validate_canonical
from tongshu.pipeline import TONGSHUPipeline

_LLM_ENV_VARS = ("TONGSHU_LLM_API_KEY", "TONGSHU_LLM_BASE_URL", "TONGSHU_LLM_MODEL", "DEEPSEEK_API_KEY")

_EXPECTED_META_KEYS = sorted(
    [
        "request_id",
        "trace_id",
        "document_id",
        "schema_version",
        "calculation_version",
        "knowledge_version",
        "mapping_version",
        "translation_version",
        "audit_version",
        "model_version",
        "created_at",
    ]
)


@contextmanager
def _env_without(*names: str):
    saved = {n: os.environ.pop(n, None) for n in names}
    try:
        yield
    finally:
        for n, v in saved.items():
            if v is not None:
                os.environ[n] = v


class TestCanonicalMeta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with _env_without(*_LLM_ENV_VARS):
            cls.root = Path(__file__).resolve().parents[2]  # .../通书-claude
            cls.schema_dir = cls.root / "docs"
            cls.pipeline = TONGSHUPipeline.for_demo(cls.root)
            cls.audit_path = cls.pipeline.audit_writer.log_path

    def _run(self, trace_id=None):
        return self.pipeline.run(
            analysis_date=date(2026, 8, 17),
            birth_date=(1984, 12, 7, 16),
            gender="male",
            theme="WORK",
            trace_id=trace_id,
        )

    def _last_audit_entry(self) -> dict:
        with open(self.audit_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return json.loads(lines[-1])

    # ------------------------------------------------------------------ #
    # meta structure
    # ------------------------------------------------------------------ #

    def test_meta_has_all_11_fields(self):
        r = self._run()
        self.assertIsNotNone(r.canonical.meta)
        self.assertEqual(sorted(r.canonical.meta.keys()), _EXPECTED_META_KEYS)

    def test_meta_patterns_and_const_versions(self):
        r = self._run()
        meta = r.canonical.meta
        self.assertRegex(meta["request_id"], r"^RR-[A-Z0-9-]+$")
        self.assertRegex(meta["trace_id"], r"^TRACE-[A-Z0-9-]+$")
        self.assertRegex(meta["document_id"], r"^CC-[A-Z0-9-]+$")
        self.assertEqual(meta["schema_version"], "3.6.0")
        self.assertEqual(meta["calculation_version"], "1.0.0")
        self.assertEqual(meta["knowledge_version"], "1.0.0")
        self.assertEqual(meta["mapping_version"], "0.1.0")
        self.assertEqual(meta["translation_version"], "0.1.0")
        self.assertEqual(meta["audit_version"], "1.0.0")
        self.assertEqual(meta["model_version"], "stub")  # Stub renderer, no key
        datetime.fromisoformat(meta["created_at"])  # must parse, no raise

    # ------------------------------------------------------------------ #
    # v36 schema switching (superset + fallback)
    # ------------------------------------------------------------------ #

    def test_canonical_with_meta_validates_v36(self):
        r = self._run()
        is_valid, errs = validate_canonical(r.canonical.to_dict(), self.schema_dir)
        self.assertTrue(is_valid, errs)

    def test_legacy_shape_without_meta_still_validates(self):
        """超集性质:旧形状(无 meta)SIR 必须仍通过 v36 schema(保护 golden)。"""
        r = self._run()
        sir = r.canonical.to_dict()
        sir.pop("meta")
        is_valid, errs = validate_canonical(sir, self.schema_dir)
        self.assertTrue(is_valid, errs)

    def test_incomplete_meta_rejected(self):
        """meta present-but-incomplete 必须被拒绝(无部分状态)。"""
        r = self._run()
        sir = r.canonical.to_dict()
        del sir["meta"]["trace_id"]
        is_valid, errs = validate_canonical(sir, self.schema_dir)
        self.assertFalse(is_valid)
        self.assertTrue(any("trace_id" in e for e in errs))

    def test_bad_trace_id_pattern_rejected(self):
        r = self._run()
        sir = r.canonical.to_dict()
        sir["meta"]["trace_id"] = "NOT-A-TRACE"
        is_valid, _ = validate_canonical(sir, self.schema_dir)
        self.assertFalse(is_valid)

    # ------------------------------------------------------------------ #
    # observability trio coherence (§36)
    # ------------------------------------------------------------------ #

    def test_trace_id_echoed_into_meta_and_audit(self):
        r = self._run(trace_id="TRACE-PM-BLOCKD-1")
        entry = self._last_audit_entry()
        self.assertEqual(r.canonical.meta["trace_id"], "TRACE-PM-BLOCKD-1")
        self.assertEqual(entry["trace_id"], "TRACE-PM-BLOCKD-1")

    def test_trace_id_generated_when_absent(self):
        r = self._run()
        self.assertRegex(r.canonical.meta["trace_id"], r"^TRACE-[A-Z0-9-]+$")

    def test_observability_trio_coherent(self):
        r = self._run(trace_id="TRACE-PM-BLOCKD-2")
        entry = self._last_audit_entry()
        meta = r.canonical.meta
        self.assertEqual(meta["request_id"], entry["request_id"])  # meta == audit
        self.assertEqual(meta["document_id"], r.canonical.canonical_id)
        self.assertEqual(entry["document_id"], r.canonical.canonical_id)
        self.assertTrue(meta["request_id"].startswith("RR-"))

    def test_compute_only_also_builds_meta(self):
        r = self.pipeline.run(
            analysis_date=date(2026, 8, 17),
            birth_date=(1984, 12, 7, 16),
            gender="male",
            theme="WORK",
            compute_only=True,
        )
        self.assertIsNotNone(r.canonical.meta)
        self.assertEqual(r.canonical.meta["schema_version"], "3.6.0")


if __name__ == "__main__":
    unittest.main()
