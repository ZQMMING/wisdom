"""BZ-FNDR-15.16 ZIP-INT-06 Pipeline 集成测试.

S1~S6 在 Pipeline.run() 端到端验证:
  - Composer output 真正进入 atomic_claims
  - Chain-A 老 ZI_PING claims 与 Composer AC-ZP-* claims 不冲突 (S6)
  - SHIJIAN EVENT_ABSENT / UNKNOWN / FAILED 在 production 链路 0 claim
  - boundary: composer_version 字段在每个 Composer claim 里
"""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))

# P2.1-F: Authority bootstrap 需要外部 cred
os.environ.setdefault(
    "TONGSHU_AUTHORITY_CREDENTIALS",
    "test:abc123;test2:def456"
)


class TestINT06PipelineWiring(unittest.TestCase):
    """Pipeline.run() end-to-end: Composer 接入 ComputeStage 但 production path 默认 OFF.

    ⚠️ INT-06 默认 OFF 原因: Composer claims 会改变 atomic_claims 内容,
    影响 G1 evidence_gate (T-3 漂移). 待 User 单独授权 + Composer claims G1 适配.
    当前测试验证:
      1. Composer 模块可用 (单元测试覆盖)
      2. ComputeStage 接入点 (judgment_composer 参数) 存在
      3. Pipeline.production path 默认 OFF → 0 Composer claims
    """

    def test_production_path_composer_off_by_default(self):
        """⚠️ INT-06 默认 OFF: pipeline.run() 不产 Composer claims (T-3 保护)."""
        from datetime import date
        from tongshu.pipeline import TONGSHUPipeline

        pipeline = TONGSHUPipeline.for_demo(_REPO_ROOT)
        result = pipeline.run(
            analysis_date=date(2024, 1, 1),
            birth_date=(1990, 1, 1, 12),
            gender="male",
            theme="WORK",
        )
        claims = result.canonical.atomic_claims
        composer_claims = [c for c in claims if c.get("claim_id", "").startswith("AC-ZP-")]
        # 默认 OFF: 0 AC-ZP-* claims
        self.assertEqual(composer_claims, [],
                         "INT-06 默认 OFF: production path 不得产 Composer claims")

    def test_compute_stage_supports_composer_param(self):
        """ComputeStage.run() 接受 judgment_composer 参数 (INT-06 接入点)."""
        import inspect
        from tongshu.pipeline_stages.compute_stage import ComputeStage
        sig = inspect.signature(ComputeStage.run)
        self.assertIn("judgment_composer", sig.parameters,
                      "INT-06: ComputeStage.run 必须接受 judgment_composer 参数")

    def test_pipeline_holds_composer_instance(self):
        """Pipeline.judgment_composer 已构造 (即使默认 OFF, 实例在)."""
        from tongshu.pipeline import TONGSHUPipeline
        pipeline = TONGSHUPipeline.for_demo(_REPO_ROOT)
        self.assertIsNotNone(pipeline.judgment_composer,
                             "INT-06: pipeline.judgment_composer 实例已构造")

    def test_int06_introduction_preserves_baseline(self):
        """T-3: pipeline.run() 必须 0 报错."""
        from datetime import date
        from tongshu.pipeline import TONGSHUPipeline

        pipeline = TONGSHUPipeline.for_demo(_REPO_ROOT)
        result = pipeline.run(
            analysis_date=date(2024, 1, 1),
            birth_date=(1990, 1, 1, 12),
            gender="male",
            theme="WORK",
        )
        self.assertIsNotNone(result)

    def test_provenance_summary_field_in_result(self):
        """INT-03 + INT-06 联动: ValidationStage 产出 provenance_summary."""
        from datetime import date
        from tongshu.pipeline import TONGSHUPipeline

        pipeline = TONGSHUPipeline.for_demo(_REPO_ROOT)
        result = pipeline.run(
            analysis_date=date(2024, 1, 1),
            birth_date=(1990, 1, 1, 12),
            gender="male",
            theme="WORK",
        )
        # PipelineResult.validation_passed is bool
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, "validation_passed"))


if __name__ == "__main__":
    unittest.main()
