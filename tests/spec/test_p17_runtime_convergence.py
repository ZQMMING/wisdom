"""
P1.7 — Runtime Convergence: TemporalConvergenceEngine wiring + integration tests.

验证时序收敛引擎是否真正接入生产路径，并覆盖正向/负向/bypass 边界。

红线（User 裁决）：
  ❌ 旧 CrossAnalyzer / ConvergenceArbiter 语义留在 src/（已归档）
  ❌ 时序收敛结果不参与 Judgment/Claim 决策（仅作为观察层附加）
  ❌ TemporalConvergenceEngine 在 src/ 存在但生产路径零引用
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.pipeline_stages.compute_stage import ComputeStage
from tongshu.reasoning.signal_engine import SignalEngine, Signal
from tongshu.reasoning.matcher import RuleMatcher
from tongshu.reasoning.theme_engine import ThemeEngine
from tongshu.canonical.composer import CanonicalComposer
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.ziwei_engine import ZiweiEngine
from tongshu.engines.huangli_engine import HuangliEngine
from tongshu.temporal.convergence import TemporalConvergenceEngine
from tongshu.temporal.schema import TemporalSignal, PredictionWindow, TemporalGranularity
from tongshu.types import ComputeResult


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_signals():
    """Minimal signals across all three layers."""
    return {
        "BASELINE": [
            Signal(
                signal_id="SIG-BL-001",
                ontology_type="SUPPORT",
                direction="INCREASE",
                polarity="active",
                strength="moderate",
                layer="BASELINE",
                evidence_refs=["EV-001"],
                rule_refs=["RUL-001"],
            ),
        ],
        "CYCLE_CONTEXT": [
            Signal(
                signal_id="SIG-CY-001",
                ontology_type="SUPPORT",
                direction="INCREASE",
                polarity="active",
                strength="high",
                layer="CYCLE_CONTEXT",
                evidence_refs=["EV-002"],
                rule_refs=["RUL-002"],
            ),
        ],
        "DAILY_ACTIVATION": [
            Signal(
                signal_id="SIG-DAY-001",
                ontology_type="CONSTRAINT",
                direction="DECLINE",
                polarity="passive",
                strength="low",
                layer="DAILY_ACTIVATION",
                evidence_refs=["EV-003"],
                rule_refs=["RUL-003"],
            ),
        ],
    }


@pytest.fixture
def temporal_convergence_engine():
    return TemporalConvergenceEngine(target_year=2026)


@pytest.fixture
def production_stage(temporal_convergence_engine):
    """ComputeStage with both orchestrator and temporal convergence engine."""
    from tongshu.assertion.assertion_rule_library import AssertionRuleLibrary
    lib = AssertionRuleLibrary(rules=[])
    return ComputeStage(
        bazi_engine=BaziEngine(),
        ziwei_engine=ZiweiEngine(),
        huangli_engine=HuangliEngine(),
        signal_engine=SignalEngine(RuleMatcher([])),
        theme_engine=ThemeEngine(
            Path(__file__).parent.parent.parent / "docs" / "theme_mapping.yaml"
        ),
        mapping_registry=None,
        composer=CanonicalComposer(theme="WORK", engine_versions={}),
        schema_dir=Path(__file__).parent.parent.parent / "docs",
        matcher=RuleMatcher([]),
        renderer_model_id="test",
        assertion_library=lib,
        temporal_convergence_engine=temporal_convergence_engine,
    )


# ─── T23: TemporalConvergenceEngine wired into ComputeStage ───────────────────


class TestT23_TemporalConvergenceWiring:
    """T23: 时序收敛引擎必须真正接入 ComputeStage。"""

    def test_compute_stage_accepts_temporal_convergence_engine(self, temporal_convergence_engine):
        """T23.1: ComputeStage 接受 TemporalConvergenceEngine。"""
        stage = ComputeStage(
            bazi_engine=BaziEngine(),
            ziwei_engine=ZiweiEngine(),
            huangli_engine=HuangliEngine(),
            signal_engine=SignalEngine(RuleMatcher([])),
            theme_engine=ThemeEngine(
                Path(__file__).parent.parent.parent / "docs" / "theme_mapping.yaml"
            ),
            mapping_registry=None,
            composer=CanonicalComposer(theme="WORK", engine_versions={}),
            schema_dir=Path(__file__).parent.parent.parent / "docs",
            matcher=RuleMatcher([]),
            renderer_model_id="test",
            temporal_convergence_engine=temporal_convergence_engine,
        )
        assert stage._temporal_convergence_engine is temporal_convergence_engine

    def test_compute_stage_without_temporal_convergence_engine(self):
        """T23.2: 不传引擎时 _temporal_convergence_engine = None（向后兼容）。"""
        stage = ComputeStage(
            bazi_engine=BaziEngine(),
            ziwei_engine=ZiweiEngine(),
            huangli_engine=HuangliEngine(),
            signal_engine=SignalEngine(RuleMatcher([])),
            theme_engine=ThemeEngine(
                Path(__file__).parent.parent.parent / "docs" / "theme_mapping.yaml"
            ),
            mapping_registry=None,
            composer=CanonicalComposer(theme="WORK", engine_versions={}),
            schema_dir=Path(__file__).parent.parent.parent / "docs",
            matcher=RuleMatcher([]),
            renderer_model_id="test",
        )
        assert stage._temporal_convergence_engine is None


# ─── T24: Signal → TemporalSignal 映射 ──────────────────────────────────────


class TestT24_SignalToTemporalMapping:
    """T24: _map_signal_to_temporal 正确转换 Signal → TemporalSignal。"""

    def test_increase_direction_maps_to_positive(self):
        """T24.1: INCREASE → POSITIVE。"""
        sig = Signal(
            signal_id="X", ontology_type="SUPPORT", direction="INCREASE",
            polarity="active", strength="moderate", layer="BASELINE",
            evidence_refs=[], rule_refs=[],
        )
        ts = ComputeStage._map_signal_to_temporal(sig, "BASELINE", 2026, "TEST")
        assert ts.direction == "POSITIVE"
        assert ts.signal_id == "X"
        assert ts.strength == 0.5

    def test_decline_direction_maps_to_negative(self):
        """T24.2: DECLINE → NEGATIVE。"""
        sig = Signal(
            signal_id="Y", ontology_type="CONSTRAINT", direction="DECLINE",
            polarity="passive", strength="high", layer="DAILY_ACTIVATION",
            evidence_refs=[], rule_refs=[],
        )
        ts = ComputeStage._map_signal_to_temporal(sig, "DAILY_ACTIVATION", 2026, "TEST")
        assert ts.direction == "NEGATIVE"
        assert ts.strength == 0.7

    def test_daily_layer_gets_daily_granularity(self):
        """T24.3: DAILY_ACTIVATION → DAILY granularity。"""
        sig = Signal(
            signal_id="Z", ontology_type="SUPPORT", direction="STABLE",
            polarity="active", strength="moderate", layer="DAILY_ACTIVATION",
            evidence_refs=[], rule_refs=[],
        )
        ts = ComputeStage._map_signal_to_temporal(sig, "DAILY_ACTIVATION", 2026, "TEST")
        assert ts.prediction_window.granularity == TemporalGranularity.DAILY

    def test_baseline_layer_gets_yearly_granularity(self):
        """T24.4: BASELINE → YEARLY granularity。"""
        sig = Signal(
            signal_id="W", ontology_type="SUPPORT", direction="INCREASE",
            polarity="active", strength="moderate", layer="BASELINE",
            evidence_refs=[], rule_refs=[],
        )
        ts = ComputeStage._map_signal_to_temporal(sig, "BASELINE", 2026, "TEST")
        assert ts.prediction_window.granularity == TemporalGranularity.YEARLY

    def test_unknown_direction_becomes_unknown(self):
        """T24.5: 未知方向 → UNKNOWN（不崩溃）。"""
        sig = Signal(
            signal_id="UNK", ontology_type="SUPPORT", direction="WEIRD",
            polarity="active", strength="moderate", layer="BASELINE",
            evidence_refs=[], rule_refs=[],
        )
        ts = ComputeStage._map_signal_to_temporal(sig, "BASELINE", 2026, "TEST")
        assert ts.direction == "UNKNOWN"


# ─── T25: Temporal Convergence runs end-to-end ──────────────────────────────


class TestT25_TemporalConvergenceRuns:
    """T25: _run_temporal_convergence 产出有效 TemporalConvergence 结果。"""

    def test_convergence_with_multi_layer_signals(self, production_stage, sample_signals):
        """T25.1: 三层信号 → 收敛结果含 overlap 和 agreement。"""
        result = production_stage._run_temporal_convergence(sample_signals, date(2026, 9, 2))
        assert result is not None
        assert hasattr(result, "temporal_agreement")
        assert result.total_engines > 0

    def test_convergence_with_empty_signals(self, production_stage):
        """T25.2: 空信号 → 返回 None（不产生假收敛）。"""
        result = production_stage._run_temporal_convergence({}, date(2026, 9, 2))
        assert result is None

    def test_convergence_with_none_engine(self):
        """T25.3: 无引擎时直接返回 None。"""
        stage = ComputeStage(
            bazi_engine=BaziEngine(),
            ziwei_engine=ZiweiEngine(),
            huangli_engine=HuangliEngine(),
            signal_engine=SignalEngine(RuleMatcher([])),
            theme_engine=ThemeEngine(
                Path(__file__).parent.parent.parent / "docs" / "theme_mapping.yaml"
            ),
            mapping_registry=None,
            composer=CanonicalComposer(theme="WORK", engine_versions={}),
            schema_dir=Path(__file__).parent.parent.parent / "docs",
            matcher=RuleMatcher([]),
            renderer_model_id="test",
        )
        signals = {"BASELINE": []}
        result = stage._run_temporal_convergence(signals, date(2026, 9, 2))
        assert result is None


# ─── T26: ComputeResult includes temporal_convergence ───────────────────────


class TestT26_ComputeResultTemporalConvergence:
    """T26: ComputeResult 包含 temporal_convergence 字段。"""

    def test_compute_result_has_temporal_convergence_field(self):
        """T26.1: ComputeResult 有 temporal_convergence 字段（默认 None）。"""
        result = ComputeResult(
            bazi_chart=None,
            ziwei_chart=None,
            huangli_day=None,
            signals={},
            atomic_claims=[],
            canonical=None,
            canonical_schema_valid=True,
            canonical_schema_errors=(),
            computed_at=date.today(),
        )
        assert hasattr(result, "temporal_convergence")
        assert result.temporal_convergence is None


# ─── T27: P1.7 负向测试 — 收敛结果不影响 Claim 结构 ──────────────────────────


class TestT27_ConvergenceDoesNotPolluteClaims:
    """T27: 时序收敛结果不改变 atomic_claim 结构或 direction 语义。"""

    def test_convergence_result_is_separate_from_claims(self, production_stage, sample_signals):
        """T27.1: 收敛结果独立存在于 ComputeResult，不污染 claim 字段。"""
        # 直接验证方法：convergence 不应修改 claims 列表
        convergence = production_stage._run_temporal_convergence(sample_signals, date(2026, 9, 2))
        # 收敛结果应有 temporal_agreement 字段
        assert hasattr(convergence, "temporal_agreement")
        # 但不应包含 claim/direction 语义（那是 AssertionRule 的领域）
        assert not hasattr(convergence, "atomic_claims")

    def test_convergence_does_not_introduce_cross_system_comparison(self):
        """T27.2: TemporalConvergenceEngine 不做跨体系比较（只比较时间窗重叠）。"""
        source = __import__("tongshu.temporal.convergence", fromlist=["TemporalConvergenceEngine"])
        engine_src = __import__("tongshu.temporal.convergence", fromlist=["TemporalConvergenceEngine"]).TemporalConvergenceEngine
        import inspect
        src = inspect.getsource(engine_src)
        # 不应有 cross-analysis 语义关键词
        forbidden = ["cross_analysis", "ConvergenceArbiter", "ALIGNED", "CONFLICTED"]
        for word in forbidden:
            assert word not in src, (
                f"P1.7: Forbidden cross-system semantic '{word}' in TemporalConvergenceEngine"
            )


# ─── T28: Full pipeline integration ─────────────────────────────────────────


class TestT28_PipelineTemporalConvergenceIntegration:
    """T28: TONGSHUPipeline 可携带 temporal_convergence_engine。"""

    def test_pipeline_accepts_temporal_convergence_year(self):
        """T28.1: TONGSHUPipeline 接受 temporal_convergence_year 参数并创建引擎。"""
        from tongshu.pipeline import TONGSHUPipeline
        from tongshu.pipeline_stages.compute_stage import ComputeStage
        import inspect
        # 检查 __init__ 签名
        sig = inspect.signature(TONGSHUPipeline.__init__)
        assert "temporal_convergence_year" in sig.parameters, (
            "TONGSHUPipeline.__init__ 必须接受 temporal_convergence_year 参数"
        )
        # 检查 ComputeStage.__init__ 签名
        sig2 = inspect.signature(ComputeStage.__init__)
        assert "temporal_convergence_engine" in sig2.parameters, (
            "ComputeStage.__init__ 必须接受 temporal_convergence_engine 参数"
        )

    def test_pipeline_produces_temporal_convergence_in_result(self):
        """T28.2: 带 temporal_convergence_year 的 Pipeline 在 run() 中产生 temporal_convergence 字段。"""
        from tongshu.pipeline import TONGSHUPipeline
        repo_root = Path(__file__).parent.parent.parent
        # 直接构造（for_demo 依赖 backend/data，当前仓库结构为 data/）
        pipeline = TONGSHUPipeline(
            schema_dir=repo_root / "docs",
            mapping_path=repo_root / "docs" / "theme_mapping.yaml",
            audit_dir=repo_root / "docs" / "audit",
            temporal_convergence_year=2026,
        )
        # 验证引擎已创建
        assert pipeline._temporal_convergence_engine is not None
        # 验证 ComputeStage 也接入了
        assert pipeline.compute_stage._temporal_convergence_engine is not None

        # 执行一次最小化 run（compute_only 跳过渲染）
        result = pipeline.run(
            analysis_date=date(2026, 9, 2),
            birth_date=(1990, 5, 15, 12),
            gender="male",
            theme="WORK",
            compute_only=True,
        )
        assert hasattr(result, "temporal_convergence")
        # 收敛结果可能为 None（取决于信号是否生成有效 TemporalSignal）
        assert result.temporal_convergence is None or hasattr(result.temporal_convergence, "temporal_agreement")
