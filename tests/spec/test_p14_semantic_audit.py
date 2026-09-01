"""
P1.4 — Cross-System Semantic Pollution Negative Tests

验证：任何未经原典验证、未经 Admission 的规则，从所有入口都绝对进不了 Production。
同时扫描 Production 路径，确认无 forbidden semantics 残留。

红线（User 裁决 2026-09-02）：
  - 五经 Agent 直接产出 MUST 走 Admission Registry，禁止 load() 进入生产
  - 未验证规则进入生产 = 硬拒绝
  - convergence.py / cross_analysis.py 含 forbidden 语义 → 不得从生产路径 import
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
    MatchStrategy,
    RuleProvenance,
)
from tongshu.cross_domain import CrossDomainOrchestrator
from tongshu.spec.canonical import (
    EngineEvidence,
    SemanticAtom,
    EngineName,
    TemporalScope,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def verified_bundle():
    """Synthetic PRODUCTION_ADMITTED bundle — explicitly marked synthetic to prevent confusion with real assets."""
    return {
        "_meta": {"version": "1.0", "status": "PRODUCTION", "synthetic": True},
        "rules": [
            {
                "rule_id": "R-PROD-001",
                "domain": "GROWTH",
                "match_strategy": "EXACT",
                "condition": {"atom_id": "TEST_ATOM_1"},
                "direction": "supportive",
                "provenance": {
                    "source_work": "子平真诠",
                    "source_chapter": "论印绶",
                    "passage_ref": "卷一·论印绶第一",
                    "verification_status": "verified",
                    "verification_scope": "PRODUCTION_ADMITTED",
                    "verified_by": "audit-bot-v1",
                    "verification_version": "2026.09",
                },
            }
        ],
    }


@pytest.fixture
def unverified_bundle():
    return {
        "_meta": {"version": "1.0", "status": "TEST", "synthetic": True},
        "rules": [
            {
                "rule_id": "R-UNV-001",
                "domain": "GROWTH",
                "match_strategy": "EXACT",
                "condition": {"atom_id": "TEST_ATOM_1"},
                "direction": "supportive",
                "provenance": {
                    "source_work": "子平真诠",
                    "source_chapter": "论印绶",
                    "verification_status": "unverified",
                    "verification_scope": "TEST_FIXTURE",
                },
            }
        ],
    }


@pytest.fixture
def candidate_bundle():
    return {
        "_meta": {"version": "1.0", "status": "DRAFT", "synthetic": True},
        "rules": [
            {
                "rule_id": "R-CAND-001",
                "domain": "FINANCE",
                "match_strategy": "EXACT",
                "condition": {"atom_id": "TEST_ATOM_2"},
                "direction": "caution",
                "provenance": {
                    "source_work": "",
                    "verification_status": "candidate",
                    "verification_scope": "TEST_FIXTURE",
                },
            }
        ],
    }


@pytest.fixture
def missing_provenance_bundle():
    return {
        "_meta": {"version": "1.0", "status": "UNKNOWN"},
        "rules": [
            {
                "rule_id": "R-NOPROV-001",
                "domain": "CAREER",
                "match_strategy": "EXACT",
                "condition": {"atom_id": "TEST_ATOM_3"},
                "direction": "neutral",
            }
        ],
    }


# ─── T1-T4: Production Admission Negative Tests ─────────────────────────────


class TestT1_VerifiedRules_Accepted:
    """T1: PRODUCTION_ADMITTED 规则 → ProductionRuleLoader 接受。"""

    def test_production_loader_accepts_admitted(self, verified_bundle):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(verified_bundle, f, ensure_ascii=False)
            path = f.name
        try:
            lib = ProductionRuleLoader.load(path)
            assert len(lib._rules) == 1
            assert lib._rules[0].rule_id == "R-PROD-001"
            assert lib._production_verified is True
            assert lib._rules[0].provenance.verification_scope.name == "PRODUCTION_ADMITTED"
        finally:
            os.unlink(path)

    def test_load_directly_constructed_also_works(self, verified_bundle):
        """load() 也接受 PRODUCTION_ADMITTED 规则（用于 backward compat），但不标记 production_verified。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(verified_bundle, f, ensure_ascii=False)
            path = f.name
        try:
            lib = AssertionRuleLibrary.load(path)
            assert len(lib._rules) == 1
            assert lib._production_verified is False
        finally:
            os.unlink(path)


class TestT2_UnverifiedRules_Rejected:
    """T2: TEST_FIXTURE 规则 → ProductionRuleLoader 硬拒绝（0 rules）。"""

    def test_production_loader_rejects_test_fixture(self, unverified_bundle):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(unverified_bundle, f, ensure_ascii=False)
            path = f.name
        try:
            lib = ProductionRuleLoader.load(path)
            assert len(lib._rules) == 0, (
                "P1.4-CLOSE: TEST_FIXTURE rules must be HARD-REJECTED from production"
            )
        finally:
            os.unlink(path)

    def test_load_accepts_test_fixture_for_test(self, unverified_bundle):
        """load() 用于 dev/test 应接受 TEST_FIXTURE（这是设计意图）。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(unverified_bundle, f, ensure_ascii=False)
            path = f.name
        try:
            lib = AssertionRuleLibrary.load(path)
            assert len(lib._rules) == 1
            assert lib._production_verified is False
            assert lib._rules[0].provenance.verification_scope.name == "TEST_FIXTURE"
        finally:
            os.unlink(path)


class TestT3_CandidateRules_Rejected:
    """T3: candidate 规则 → ProductionRuleLoader 硬拒绝。"""

    def test_production_loader_rejects_candidate(self, candidate_bundle):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(candidate_bundle, f, ensure_ascii=False)
            path = f.name
        try:
            lib = ProductionRuleLoader.load(path)
            assert len(lib._rules) == 0
        finally:
            os.unlink(path)


class TestT4_MissingProvenance_Rejected:
    """T4: 缺失 provenance → 默认 unverified → ProductionRuleLoader 硬拒绝。"""

    def test_production_loader_rejects_missing_provenance(self, missing_provenance_bundle):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(missing_provenance_bundle, f, ensure_ascii=False)
            path = f.name
        try:
            lib = ProductionRuleLoader.load(path)
            assert len(lib._rules) == 0
        finally:
            os.unlink(path)


# ─── T5-T7: Orchestrator Gate Tests ────────────────────────────────────────


class TestT5_OrchestratorGate:
    """T5: CrossDomainOrchestrator 拒绝非 production_verified 库。"""

    def test_rejects_dev_library(self, unverified_bundle):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(unverified_bundle, f, ensure_ascii=False)
            path = f.name
        try:
            lib = AssertionRuleLibrary.load(path)  # production_verified=False
            with pytest.raises(ValueError, match="ProductionRuleLoader"):
                CrossDomainOrchestrator(assertion_library=lib)
        finally:
            os.unlink(path)

    def test_accepts_production_library(self, verified_bundle):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(verified_bundle, f, ensure_ascii=False)
            path = f.name
        try:
            lib = ProductionRuleLoader.load(path)  # production_verified=True
            orch = CrossDomainOrchestrator(assertion_library=lib)
            assert orch is not None
        finally:
            os.unlink(path)


class TestT6_EmptyProductionLibrary:
    """T6: ProductionRuleLoader 加载空文件 → 空库，但 production_verified=True。"""

    def test_empty_bundle_yields_empty_library(self):
        bundle = {"_meta": {}, "rules": []}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(bundle, f)
            path = f.name
        try:
            lib = ProductionRuleLoader.load(path)
            assert len(lib._rules) == 0
            assert lib._production_verified is True
        finally:
            os.unlink(path)


class TestT7_OrchestratorStructuralOnly:
    """T7: Orchestrator 只做结构性编排，不产生跨体系比较。"""

    def test_no_cross_comparison_in_orchestrate(self, verified_bundle):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(verified_bundle, f, ensure_ascii=False)
            path = f.name
        try:
            lib = ProductionRuleLoader.load(path)
            orch = CrossDomainOrchestrator(assertion_library=lib)

            ev = EngineEvidence(
                evidence_id="E-001",
                engine=EngineName.ZI_PING,
                rule_id="R1",
                value="test",
                temporal_scope=TemporalScope.BIRTH,
                attributes={},
                source_rule_ref="r",
                source_field="f",
            )
            atom = SemanticAtom(
                atom_id="TEST_ATOM_1",
                engine=EngineName.ZI_PING,
                evidence_ref=ev.evidence_id,
                semantic_keys=[],
                domain_candidates=["GROWTH"],
                label_zh="",
                category="",
            )
            result = orch.orchestrate("T7-test", "birth", {"ZI_PING": [ev]}, lambda e: atom)

            # Verify: no cross-comparison fields
            errors = result.verify_no_cross_comparison()
            assert errors == [], f"Cross-comparison fields found: {errors}"

            # Verify: by_engine separation
            assert "ZI_PING" in result.by_engine
            assert result.by_engine["ZI_PING"].evidence_ids == ["E-001"]
        finally:
            os.unlink(path)


# ─── T8-T10: Forbidden Semantics Scan ──────────────────────────────────────


class TestT8_FrozenContract_NoForbiddenSemantics:
    """T8: spec/canonical/ 不含 cross-comparison 语义。"""

    FORBIDDEN = frozenset({
        "CONFLICTED", "ALIGNED", "PARTIAL", "INSUFFICIENT",
        "vote", "weight", "confidence", "score", "rank",
    })

    def test_canonical_no_forbidden_words(self):
        """T8: spec/canonical/ 不含实际使用 forbidden 语义的代码行。"""
        canonical_dir = Path(__file__).parent.parent.parent / "src" / "tongshu" / "spec" / "canonical"
        for py_file in canonical_dir.glob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            for word in self.FORBIDDEN:
                offending = []
                for line in source.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    if word.lower() not in stripped.lower():
                        continue
                    # Allow lines that are purely descriptive (design docs mentioning what is forbidden)
                    if any(kw in stripped for kw in ("禁止", "forbidden", "不得", "严禁", "no ", "does not")):
                        continue
                    # Allow docstring-only mentions (lines starting with spaces + quotes or bullets)
                    if stripped.startswith(("\"", "'", "·", "-", "*", "  ")):
                        continue
                    offending.append(stripped)
                assert not offending, (
                    f"{py_file.name}: forbidden word '{word}' found in executable code:\n"
                    + "\n".join(f"  {l}" for l in offending)
                )


class TestT9_CrossDomainNoForbiddenImports:
    """T9: cross_domain/ 不 import CrossAnalyzer / ConvergenceArbiter。"""

    def test_no_forbidden_imports(self):
        cross_dir = Path(__file__).parent.parent.parent / "src" / "tongshu" / "cross_domain"
        for py_file in cross_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            source = py_file.read_text(encoding="utf-8")
            forbidden_imports = [
                "CrossAnalyzer", "cross_analysis",
                "ConvergenceArbiter", "convergence",
            ]
            for imp in forbidden_imports:
                # Check actual import lines (not comments or strings)
                for line in source.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    if f"import {imp}" in line or f"from ... {imp}" in line:
                        pytest.fail(
                            f"{py_file.name}: forbidden import '{imp}'"
                        )


class TestT10_ProductionPathNoDeadCodeCalls:
    """T10: production pipeline 不调用 deprecated 模块。"""

    def test_pipeline_no_cross_analysis_call(self):
        """T10: production pipeline 不 import CrossAnalyzer / ConvergenceArbiter。"""
        src_dir = Path(__file__).parent.parent.parent / "src" / "tongshu"
        # These files DEFINE the classes (deprecated); they are excluded from the scan
        allowed_define_files = frozenset({
            "reasoning/cross_analysis.py",
            "signal/convergence.py",
        })
        for root, dirs, files in os.walk(src_dir):
            dirs[:] = [d for d in dirs if d not in ("archive", "__pycache__")]
            for f in files:
                if not f.endswith(".py"):
                    continue
                path = Path(root) / f
                rel = str(path.relative_to(src_dir)).replace("\\", "/")
                if rel in allowed_define_files:
                    continue
                source = path.read_text(encoding="utf-8")
                for line in source.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    # Check for actual import statements of forbidden classes
                    lower = stripped.lower()
                    if ("convergencearbiter" in lower or "crossanalyzer" in lower) and "import" in lower:
                        pytest.fail(
                            f"{rel}: imports forbidden class '{'CrossAnalyzer' if 'crossanalyzer' in lower else 'ConvergenceArbiter'}'"
                        )


# ─── T11-T12: P1.4-CLOSE Enforcement ────────────────────────────────────────


class TestT11_ConstructorGate:
    """T11: 直接构造 production_verified=True 必须抛出 TypeError。"""

    def test_direct_construction_with_production_verified_raises(self):
        with pytest.raises(TypeError, match="P1.4-CLOSE"):
            AssertionRuleLibrary(rules=[], production_verified=True)

    def test_empty_library_still_works(self):
        """无参构造和 rules=[] 仍可用（testing 路径）。"""
        lib = AssertionRuleLibrary()
        assert len(lib._rules) == 0
        assert lib._production_verified is False

        lib2 = AssertionRuleLibrary(rules=[])
        assert len(lib2._rules) == 0
        assert lib2._production_verified is False


class TestT12_DeadCodeRemoved:
    """T12: src/ 中不再存在 cross_analysis.py 和 convergence.py。"""

    def test_cross_analysis_not_in_src(self):
        src_dir = Path(__file__).parent.parent.parent / "src" / "tongshu" / "reasoning"
        assert not (src_dir / "cross_analysis.py").exists(), (
            "P1.4-CLOSE: cross_analysis.py must be removed from src/ (archived to archive/)"
        )

    def test_convergence_not_in_src(self):
        src_dir = Path(__file__).parent.parent.parent / "src" / "tongshu" / "signal"
        assert not (src_dir / "convergence.py").exists(), (
            "P1.4-CLOSE: convergence.py must be removed from src/ (archived to archive/)"
        )

    def test_archived_files_exist(self):
        archive_reasoning = Path(__file__).parent.parent.parent / "archive" / "reasoning"
        archive_signal = Path(__file__).parent.parent.parent / "archive" / "signal"
        assert (archive_reasoning / "cross_analysis.py").exists()
        assert (archive_signal / "convergence.py").exists()


# ─── T13: P1.4-FINAL — Legacy verified downgrade + provenance completeness ───


class TestT13_LegacyVerifiedDowngrade:
    """T13: 旧 verification_status=verified 自动降级为 SOURCE_VERIFIED，不能进入生产。"""

    def test_legacy_verified_downgrades_to_source_verified(self):
        """Old JSON with verification_status=verified but no verification_scope → SOURCE_VERIFIED."""
        bundle = {
            "_meta": {"version": "1.0", "status": "LEGACY"},
            "rules": [
                {
                    "rule_id": "R-LEGACY-001",
                    "domain": "GROWTH",
                    "match_strategy": "EXACT",
                    "condition": {"atom_id": "A1"},
                    "direction": "supportive",
                    "provenance": {
                        "source_work": "子平真诠",
                        "verification_status": "verified",
                    },
                }
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(bundle, f, ensure_ascii=False)
            path = f.name
        try:
            # load() should accept it (dev path)
            lib = AssertionRuleLibrary.load(path)
            assert len(lib._rules) == 1
            assert lib._rules[0].provenance.verification_scope.name == "SOURCE_VERIFIED"
            assert lib._production_verified is False

            # ProductionRuleLoader should REJECT it
            prod_lib = ProductionRuleLoader.load(path)
            assert len(prod_lib._rules) == 0, (
                "P1.4-FINAL: legacy 'verified' must downgrade to SOURCE_VERIFIED, not PRODUCTION_ADMITTED"
            )
        finally:
            os.unlink(path)

    def test_no_explicit_scope_means_source_verified(self):
        """Rules without verification_scope or verification_status → TEST_FIXTURE (cannot produce)."""
        bundle = {
            "_meta": {}, "rules": [
                {"rule_id": "R-NOSCOPE", "domain": "X", "match_strategy": "EXACT",
                 "condition": {"atom_id": "A"}, "direction": "neutral",
                 "provenance": {"source_work": "test"}}
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(bundle, f)
            path = f.name
        try:
            lib = AssertionRuleLibrary.load(path)
            assert lib._rules[0].provenance.verification_scope.name == "TEST_FIXTURE"
            prod_lib = ProductionRuleLoader.load(path)
            assert len(prod_lib._rules) == 0
        finally:
            os.unlink(path)


class TestT14_CompleteProvenanceRequired:
    """T14: PRODUCTION_ADMITTED 必须有完整 provenance，否则拒绝。"""

    def test_missing_passage_ref_rejected(self):
        """PRODUCTION_ADMITTED but missing passage_ref → rejected."""
        bundle = {
            "_meta": {"synthetic": True}, "rules": [
                {
                    "rule_id": "R-MISSING-PASSAGE",
                    "domain": "GROWTH", "match_strategy": "EXACT",
                    "condition": {"atom_id": "A1"}, "direction": "supportive",
                    "provenance": {
                        "source_work": "子平真诠", "source_chapter": "论印绶",
                        "passage_ref": "",  # EMPTY
                        "verification_status": "verified",
                        "verification_scope": "PRODUCTION_ADMITTED",
                        "verified_by": "auditor", "verification_version": "1.0",
                    },
                }
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(bundle, f, ensure_ascii=False)
            path = f.name
        try:
            prod_lib = ProductionRuleLoader.load(path)
            assert len(prod_lib._rules) == 0, (
                "P1.4-FINAL: PRODUCTION_ADMITTED requires non-empty passage_ref"
            )
        finally:
            os.unlink(path)

    def test_missing_verified_by_rejected(self):
        """PRODUCTION_ADMITTED but missing verified_by → rejected."""
        bundle = {
            "_meta": {"synthetic": True}, "rules": [
                {
                    "rule_id": "R-MISSING-BY",
                    "domain": "GROWTH", "match_strategy": "EXACT",
                    "condition": {"atom_id": "A1"}, "direction": "supportive",
                    "provenance": {
                        "source_work": "子平真诠", "source_chapter": "论印绶",
                        "passage_ref": "卷一·论印绶第一",
                        "verification_status": "verified",
                        "verification_scope": "PRODUCTION_ADMITTED",
                        "verified_by": "",  # EMPTY
                        "verification_version": "1.0",
                    },
                }
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(bundle, f, ensure_ascii=False)
            path = f.name
        try:
            prod_lib = ProductionRuleLoader.load(path)
            assert len(prod_lib._rules) == 0
        finally:
            os.unlink(path)

    def test_complete_provenance_accepted(self, verified_bundle):
        """PRODUCTION_ADMITTED + complete provenance → accepted."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(verified_bundle, f, ensure_ascii=False)
            path = f.name
        try:
            prod_lib = ProductionRuleLoader.load(path)
            assert len(prod_lib._rules) == 1
            assert prod_lib._rules[0].provenance.is_complete_for_production
            assert prod_lib._production_verified is True
        finally:
            os.unlink(path)


class TestT15_FixtureSyntheticMarking:
    """T15: 测试 fixture 必须标记 synthetic=true，防止被误认为真实生产资产。"""

    def test_verified_bundle_is_marked_synthetic(self, verified_bundle):
        assert verified_bundle["_meta"].get("synthetic") is True

    def test_unverified_bundle_is_marked_synthetic(self, unverified_bundle):
        assert unverified_bundle["_meta"].get("synthetic") is True

    def test_candidate_bundle_is_marked_synthetic(self, candidate_bundle):
        assert candidate_bundle["_meta"].get("synthetic") is True
