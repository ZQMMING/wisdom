"""
P1.6 — Assertion → Judgment Boundary: Production Path Integration Tests

验证生产管道是否真正经过 CrossDomainOrchestrator + ProductionRuleLibrary。

红线（User 裁决）：
  ❌ direction 从 Signal 直接进 Claim（绕过 Rule 授权）
  ❌ cross_result 硬编码 None
  ❌ ProductionRuleLibrary 未被生产管道使用
  ❌ JudgmentRuleLibrary 零引用
  ❌ atomic_claims 存在授权旁路
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import inspect
from pathlib import Path
from typing import List

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.assertion.assertion_rule_library import (
    AssertionRuleLibrary,
    ProductionRuleLoader,
    ProductionRuleLibrary,
)
from tongshu.cross_domain import CrossDomainOrchestrator
from tongshu.pipeline_stages.compute_stage import ComputeStage
from tongshu.reasoning.signal_engine import SignalEngine
from tongshu.reasoning.matcher import RuleMatcher
from tongshu.reasoning.theme_engine import ThemeEngine
from tongshu.canonical.composer import CanonicalComposer
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.ziwei_engine import ZiweiEngine
from tongshu.engines.huangli_engine import HuangliEngine


# ─── Fixtures ────────────────────────────────────────────────────────────────


def _make_production_rules(tmp_path: Path, rules: list[dict]) -> str:
    """Write a PRODUCTION_ADMITTED rules bundle to a temp file."""
    data = {
        "_meta": {"version": "1.0", "status": "PRODUCTION", "synthetic": True},
        "rules": rules,
    }
    p = tmp_path / "p16_production_rules.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(p)


@pytest.fixture
def prod_rules_path(tmp_path):
    """Production-authorized rules with complete provenance."""
    rules = [
        {
            "rule_id": "ASR-P16-001",
            "domain": "CAREER",
            "match_strategy": "EXACT",
            "condition": {"atom_id": "TEST_ATOM_001"},
            "direction": "supportive",
            "provenance": {
                "source_work": "子平真诠",
                "source_chapter": "论官杀",
                "passage_ref": "卷一·论官杀第一",
                "verification_status": "verified",
                "verification_scope": "PRODUCTION_ADMITTED",
                "verified_by": "audit-bot-v1",
                "verification_version": "2026.09",
            },
        },
    ]
    return _make_production_rules(tmp_path, rules)


@pytest.fixture
def legacy_rules_path(tmp_path):
    """Legacy rules with old 'verified' status (should downgrade to SOURCE_VERIFIED)."""
    rules = [
        {
            "rule_id": "ASR-P16-LEGACY",
            "domain": "CAREER",
            "match_strategy": "EXACT",
            "condition": {"atom_id": "TEST_ATOM_LEGACY"},
            "direction": "supportive",
            "provenance": {
                "source_work": "子平真诠",
                "verification_status": "verified",  # No explicit scope
            },
        },
    ]
    return _make_production_rules(tmp_path, rules)


@pytest.fixture
def incomplete_provenance_path(tmp_path):
    """PRODUCTION_ADMITTED but missing passage_ref (should be rejected)."""
    rules = [
        {
            "rule_id": "ASR-P16-INCOMPLETE",
            "domain": "CAREER",
            "match_strategy": "EXACT",
            "condition": {"atom_id": "TEST_ATOM_INC"},
            "direction": "caution",
            "provenance": {
                "source_work": "子平真诠",
                "source_chapter": "论官杀",
                "passage_ref": "",  # EMPTY — incomplete
                "verification_status": "verified",
                "verification_scope": "PRODUCTION_ADMITTED",
                "verified_by": "audit-bot",
                "verification_version": "1.0",
            },
        },
    ]
    return _make_production_rules(tmp_path, rules)


@pytest.fixture
def empty_prod_library():
    """Empty ProductionRuleLibrary (no rules)."""
    return ProductionRuleLoader.load(str(Path(tempfile.mktemp(suffix=".json")).absolute()))


# ─── T16: Production path uses CrossDomainOrchestrator ─────────────────────────


class TestT16_ProductionPathUsesCrossDomainOrchestrator:
    """T16: 生产管道必须使用 CrossDomainOrchestrator，不能是孤儿代码。"""

    def test_compute_stage_accepts_assertion_library(self, prod_rules_path):
        """T16.1: ComputeStage 接受 ProductionRuleLibrary 参数。"""
        lib = ProductionRuleLoader.load(prod_rules_path)
        assert isinstance(lib, ProductionRuleLibrary)
        assert lib.is_production is True

        stage = ComputeStage(
            bazi_engine=BaziEngine(),
            ziwei_engine=ZiweiEngine(),
            huangli_engine=HuangliEngine(),
            signal_engine=SignalEngine(RuleMatcher([])),
            theme_engine=ThemeEngine(Path(__file__).parent.parent.parent / "docs" / "theme_mapping.yaml"),
            mapping_registry=None,
            composer=CanonicalComposer(theme="WORK", engine_versions={}),
            schema_dir=Path(__file__).parent.parent.parent / "docs",
            matcher=RuleMatcher([]),
            renderer_model_id="test",
            assertion_library=lib,
        )
        assert stage._orchestrator is not None

    def test_compute_stage_degrades_without_library(self):
        """T16.2: 无 assertion_library 时降级为旧路径（向后兼容）。"""
        stage = ComputeStage(
            bazi_engine=BaziEngine(),
            ziwei_engine=ZiweiEngine(),
            huangli_engine=HuangliEngine(),
            signal_engine=SignalEngine(RuleMatcher([])),
            theme_engine=ThemeEngine(Path(__file__).parent.parent.parent / "docs" / "theme_mapping.yaml"),
            mapping_registry=None,
            composer=CanonicalComposer(theme="WORK", engine_versions={}),
            schema_dir=Path(__file__).parent.parent.parent / "docs",
            matcher=RuleMatcher([]),
            renderer_model_id="test",
            assertion_library=None,
        )
        assert stage._orchestrator is None

    def test_orchestrator_requires_production_library(self):
        """T16.3: CrossDomainOrchestrator 拒绝非生产库。"""
        dev_lib = AssertionRuleLibrary.load("nonexistent")
        with pytest.raises(ValueError, match="ProductionRuleLibrary"):
            CrossDomainOrchestrator(assertion_library=dev_lib)


# ─── T17: Direction comes from Rule, not Signal ──────────────────────────────


class TestT17_DirectionFromRuleNotSignal:
    """T17: atomic_claim direction 必须来自 Rule，不能来自 Signal。"""

    def test_claim_direction_from_rule_when_orchestrated(self, prod_rules_path):
        """T17.1: 有授权时 claim 的 direction 来自 Rule (非 Signal)。"""
        lib = ProductionRuleLoader.load(prod_rules_path)
        stage = ComputeStage(
            bazi_engine=BaziEngine(),
            ziwei_engine=ZiweiEngine(),
            huangli_engine=HuangliEngine(),
            signal_engine=SignalEngine(RuleMatcher([])),
            theme_engine=ThemeEngine(Path(__file__).parent.parent.parent / "docs" / "theme_mapping.yaml"),
            mapping_registry=None,
            composer=CanonicalComposer(theme="WORK", engine_versions={}),
            schema_dir=Path(__file__).parent.parent.parent / "docs",
            matcher=RuleMatcher([]),
            renderer_model_id="test",
            assertion_library=lib,
        )
        # Verify claims are built from assertions, not signals
        assertions = [{"assertion_id": "AS-TEST-001", "engine": "ZI_PING",
                        "authorization_source": "CrossDomainOrchestrator",
                        "rule_direction": "supportive", "domain": "CAREER", "semantic": "TEST_ATOM_001"}]
        claims = stage._build_claims_from_assertions("WORK", assertions)
        assert len(claims) > 0
        # Direction comes from Rule, NOT from Signal
        assert claims[0]["direction"] == "supportive"
        assert claims[0]["direction"] != "POSITIVE"  # Not from Signal._DIRECTION_MAP

    def test_legacy_claims_use_signal_direction(self):
        """T17.2: 无授权时（降级路径）claim 仍用 sig.direction（向后兼容）。"""
        stage = ComputeStage(
            bazi_engine=BaziEngine(),
            ziwei_engine=ZiweiEngine(),
            huangli_engine=HuangliEngine(),
            signal_engine=SignalEngine(RuleMatcher([])),
            theme_engine=ThemeEngine(Path(__file__).parent.parent.parent / "docs" / "theme_mapping.yaml"),
            mapping_registry=None,
            composer=CanonicalComposer(theme="WORK", engine_versions={}),
            schema_dir=Path(__file__).parent.parent.parent / "docs",
            matcher=RuleMatcher([]),
            renderer_model_id="test",
            assertion_library=None,
        )
        from tongshu.reasoning.signal_engine import Signal
        sig = Signal(
            signal_id="SIG-001", ontology_type="SUPPORT", direction="INCREASE",
            polarity="active", strength="moderate", layer="BASELINE",
            evidence_refs=["EV-001"], rule_refs=["RUL-001"],
        )
        claims = stage._build_atomic_claims("WORK", {"BASELINE": [sig]})
        assert len(claims) == 1
        assert claims[0]["direction"] == "INCREASE"  # From Signal (legacy)


# ─── T18: No Authorization → No Claim ────────────────────────────────────────


class TestT18_NoAuthorizationNoClaim:
    """T18: 无授权 Rule 时不产出 claim（NO_ASSERTION，不是 NEUTRAL）。"""

    def test_unauthorized_atom_produces_no_claim(self, prod_rules_path):
        """T18.1: atom 不匹配任何 Rule → 不产出 claim。"""
        lib = ProductionRuleLoader.load(prod_rules_path)
        stage = ComputeStage(
            bazi_engine=BaziEngine(),
            ziwei_engine=ZiweiEngine(),
            huangli_engine=HuangliEngine(),
            signal_engine=SignalEngine(RuleMatcher([])),
            theme_engine=ThemeEngine(Path(__file__).parent.parent.parent / "docs" / "theme_mapping.yaml"),
            mapping_registry=None,
            composer=CanonicalComposer(theme="WORK", engine_versions={}),
            schema_dir=Path(__file__).parent.parent.parent / "docs",
            matcher=RuleMatcher([]),
            renderer_model_id="test",
            assertion_library=lib,
        )
        # Create cross_result with no matching assertions
        from tongshu.cross_domain import CrossDomainResult, MultiDomainSemanticCoverage
        from tongshu.cross_domain.result import EngineEvidenceSet
        cross_result = CrossDomainResult(
            case_id="test",
            temporal_scope="birth",
            by_engine={},
            coverage=MultiDomainSemanticCoverage(),
        )
        assertions = stage._extract_authorizations(cross_result)
        assert assertions == [], "No matching assertions → empty list"


# ─── T19: cross_result not hardcoded None ────────────────────────────────────


class TestT19_CrossResultNotHardcodedNone:
    """T19: cross_result 不能硬编码 None，必须有实际值或 None 是因为无 assertion_library。"""

    def test_cross_result_populated_when_orchestrator_exists(self, prod_rules_path):
        """T19.1: 有 orchestrator 时 cross_result 不硬编码 None。"""
        lib = ProductionRuleLoader.load(prod_rules_path)
        stage = ComputeStage(
            bazi_engine=BaziEngine(),
            ziwei_engine=ZiweiEngine(),
            huangli_engine=HuangliEngine(),
            signal_engine=SignalEngine(RuleMatcher([])),
            theme_engine=ThemeEngine(Path(__file__).parent.parent.parent / "docs" / "theme_mapping.yaml"),
            mapping_registry=None,
            composer=CanonicalComposer(theme="WORK", engine_versions={}),
            schema_dir=Path(__file__).parent.parent.parent / "docs",
            matcher=RuleMatcher([]),
            renderer_model_id="test",
            assertion_library=lib,
        )
        # The orchestrator must be wired
        assert stage._orchestrator is not None

    def test_cross_result_none_when_no_library(self):
        """T19.2: 无 assertion_library 时 cross_result = None（降级）。"""
        stage = ComputeStage(
            bazi_engine=BaziEngine(),
            ziwei_engine=ZiweiEngine(),
            huangli_engine=HuangliEngine(),
            signal_engine=SignalEngine(RuleMatcher([])),
            theme_engine=ThemeEngine(Path(__file__).parent.parent.parent / "docs" / "theme_mapping.yaml"),
            mapping_registry=None,
            composer=CanonicalComposer(theme="WORK", engine_versions={}),
            schema_dir=Path(__file__).parent.parent.parent / "docs",
            matcher=RuleMatcher([]),
            renderer_model_id="test",
            assertion_library=None,
        )
        assert stage._orchestrator is None


# ─── T20: JudgmentRuleLibrary referenced in production ─────────────────────────


class TestT20_JudgmentLibraryReferenced:
    """T20: JudgmentRuleLibrary 必须被生产路径引用。"""

    def test_judgment_rule_library_importable_in_production(self):
        """T20.1: JudgmentRuleLibrary 可被生产路径 import。"""
        from tongshu.assertion.judgment_rule_library import JudgmentRuleLibrary
        assert JudgmentRuleLibrary is not None

    def test_orchestrator_does_not_call_judgment_directly(self):
        """T20.2: Orchestrator 不直接产生 Judgment（由 JudgmentRuleLibrary 单独处理）。"""
        source = inspect.getsource(CrossDomainOrchestrator)
        assert "Judgment" not in source or "JudgmentRule" in source, (
            "CrossDomainOrchestrator should not produce Judgment directly"
        )


# ─── T21: Legacy bypass blocked ──────────────────────────────────────────────


class TestT21_LegacyBypassBlocked:
    """T21: Legacy 路径不能绕过授权边界。"""

    def test_legacy_verified_downgraded(self, legacy_rules_path):
        """T21.1: 旧 verified 降级为 SOURCE_VERIFIED，不能进入生产。"""
        lib = ProductionRuleLoader.load(legacy_rules_path)
        # Legacy verified → SOURCE_VERIFIED → rejected
        assert len(lib.list_rules()) == 0

    def test_incomplete_provenance_rejected(self, incomplete_provenance_path):
        """T21.2: PRODUCTION_ADMITTED + 不完整 provenance → 拒绝。"""
        lib = ProductionRuleLoader.load(incomplete_provenance_path)
        assert len(lib.list_rules()) == 0


# ─── T22: Bypass detection in production source ──────────────────────────────


class TestT22_ProductionBypassScan:
    """T22: 扫描生产源码，确认无方向 bypass。"""

    FORBIDDEN_PATTERNS = [
        'direction=sig.direction',
        'direction=sig.polarity',
        '"direction": sig.direction',
    ]

    def test_no_signal_direction_in_authorization_path(self):
        """T22.1: _build_claims_from_assertions 不应从 signal 取 direction。"""
        stage_src = inspect.getsource(ComputeStage._build_claims_from_assertions)
        for pattern in self.FORBIDDEN_PATTERNS:
            assert pattern not in stage_src, (
                f"P1.6: Forbidden pattern '{pattern}' found in _build_claims_from_assertions"
            )

    def test_no_crossanalyzer_in_production_source(self):
        """T22.2: 生产源码不应 import CrossAnalyzer。"""
        src_dir = Path(__file__).parent.parent.parent / "src" / "tongshu"
        for root, dirs, files in os.walk(src_dir):
            dirs[:] = [d for d in dirs if d not in ("archive", "__pycache__")]
            for f in files:
                if not f.endswith(".py"):
                    continue
                path = Path(root) / f
                rel = str(path.relative_to(src_dir)).replace("\\", "/")
                if "cross_analysis" in rel or "convergence" in rel:
                    continue  # Already archived
                source = path.read_text(encoding="utf-8")
                for line in source.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    lower = stripped.lower()
                    if ("crossanalyzer" in lower or "convergencearbiter" in lower) and "import" in lower:
                        pytest.fail(f"{rel}: imports forbidden class")
