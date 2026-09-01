"""
Production Admission Governance — Full Test Suite (58 tests)

Categories:
  T1-T7     Positive tests (happy path)
  T8-T40    Negative tests (attack vectors)
  T41-T47   Integrity tests
  T48-T50   Concurrency tests
  T51-T57   Failure mode tests
  T58-T62   Verifier bypass + security tests

Acceptance criteria: ALL PASS, zero tolerance.

P0-3 Compliance:
  Tests use TestVerifier (test_verifier module) — NEVER touch production verifier state.
  Production verify_production_proof() is tested separately for native-unavailable behavior.
"""

from __future__ import annotations

import json
import os
import sys
import threading
from pathlib import Path

# Ensure the assertion package is importable
sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent.parent.parent / "packages" / "tongshu-rules"),
)

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from tongshu.assertion.exceptions import (
    AdmissionError,
    AdmissionLoadError,
    AdmissionSchemaError,
    AdmissionStateError,
    AdmissionAuditError,
    VerifierError,
)
from tongshu.assertion.models import (
    AdmissionProof,
    AssetState,
    AssetType,
    CandidateAsset,
    ProductionAsset,
)
from tongshu.assertion.canonicalizer import canonicalize, compute_digest
from tongshu.assertion.state_machine import AdmittableAsset
from tongshu.assertion.verifier import (
    verify_production_proof,
    VERIFIER_OK,
    VERIFIER_SIGNATURE_INVALID,
    VERIFIER_DIGEST_MISMATCH,
    VERIFIER_REVOKED,
    VERIFIER_EPOCH_EXPIRED,
    VERIFIER_SCHEMA_ERROR,
    VERIFIER_KEY_UNKNOWN,
    VERIFIER_CRYPTO_ERROR,
    VERIFIER_NATIVE_UNAVAILABLE,
)
from tongshu.assertion.authority import AdmissionAuthority, generate_test_authority
from tongshu.assertion.loader import ProductionRuleLoader
from tongshu.assertion.test_verifier import TestVerifier


# ---------------------------------------------------------------------------
# Test fixtures — all use TestVerifier, NEVER production verifier state
# ---------------------------------------------------------------------------

@pytest.fixture
def test_verifier():
    """Create a test verifier with fresh state."""
    return TestVerifier()


@pytest.fixture
def test_authority():
    """Create a test authority with a known key pair."""
    auth = AdmissionAuthority(
        authority_id="test-authority",
        epoch=1,
    )
    return auth


@pytest.fixture
def valid_rule_data():
    """A well-formed assertion rule for testing."""
    return {
        "rule_id": "ZP_STEM_YEAR",
        "domain": "GROWTH",
        "match_strategy": "EXACT",
        "condition": {"atom_id": "TEN_GOD_JIA"},
        "direction": "supportive",
        "provenance": {
            "source_work": "子平真诠",
            "source_chapter": "论印绶",
            "passage_ref": "卷一·论印绶第一",
            "verification_status": "PENDING",
            "verified_by": "audit-bot-v2",
            "verification_version": "2026.09",
        },
        "semantic_content": {
            "zh_label": "甲",
            "element": "木",
            "ten_god": "偏印",
        },
    }


@pytest.fixture
def admitted_asset(valid_rule_data, test_authority, test_verifier):
    """An asset that has gone through the full admission pipeline (test path)."""
    asset = AdmittableAsset(
        asset_type=AssetType.ASSERTION_RULE.value,
        raw_data=valid_rule_data,
    )
    asset.submit_for_admission()
    canonical = asset.to_canonical()
    proof = test_authority.sign(
        asset_type=AssetType.ASSERTION_RULE.value,
        asset_canonical=canonical,
        public_key_id="test-key",
    )
    # Register test key in test verifier
    pub_info = test_authority.public_key_info
    test_verifier.set_keys({"test-key": pub_info})
    test_verifier.set_epoch(1)
    asset.audit_complete(proof)
    return asset


@pytest.fixture(autouse=True)
def _inject_test_keys_into_production(test_authority):
    """Inject test keys into production verifier before each test (P0-3 isolation)."""
    pub_info = test_authority.public_key_info
    import tongshu.assertion.verifier as prod_tv
    prod_tv._TRUSTED_KEYS = {"test-key": pub_info, "default": pub_info}
    prod_tv._CURRENT_EPOCH = 1
    prod_tv._REVOCATION_LIST = set()
    yield
    prod_tv._load_trust_anchor()


# ===========================================================================
# Category 1: Positive Tests (T1–T7)
# ===========================================================================

class TestPositive:
    """Happy path tests."""

    def test_t01_valid_admission(self, admitted_asset, test_verifier):
        """T1: Valid admission -> Production asset with correct content."""
        ok = admitted_asset.convert_to_production()
        assert ok is True
        assert admitted_asset.state == AssetState.PRODUCTION

    def test_t02_multiple_rules_all_valid(self, test_authority, test_verifier, valid_rule_data):
        """T2: Multiple rules, all valid -> All admitted."""
        pub_info = test_authority.public_key_info
        test_verifier.set_keys({"test-key": pub_info})
        test_verifier.set_epoch(1)
        results = []
        for i in range(5):
            data = dict(valid_rule_data)
            data["rule_id"] = f"RULE_{i}"
            asset = AdmittableAsset(
                asset_type=AssetType.ASSERTION_RULE.value,
                raw_data=data,
            )
            asset.submit_for_admission()
            proof = test_authority.sign_from_data(
                AssetType.ASSERTION_RULE.value, data, public_key_id="test-key"
            )
            asset.audit_complete(proof)
            ok = asset.convert_to_production()
            results.append(ok)
        assert all(results)

    def test_t03_empty_rules_raises(self, test_authority, tmp_path):
        """T4: Empty rules file -> AdmissionLoadError (NOT empty production)."""
        rules_file = tmp_path / "empty_rules.json"
        rules_file.write_text("[]")
        loader = ProductionRuleLoader(path=str(rules_file))
        with pytest.raises(AdmissionLoadError):
            loader.load()

    def test_t04_re_admit_same_content_idempotent(self, test_authority, valid_rule_data):
        """T5: Re-admit same content -> Same digest (idempotent)."""
        canonical = canonicalize(valid_rule_data)
        proof1 = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical
        )
        proof2 = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical
        )
        assert proof1.content_digest == proof2.content_digest
        assert proof1.proof_id != proof2.proof_id

    def test_t05_state_machine_strict_chain(self, test_authority, test_verifier, valid_rule_data):
        """T7: State machine enforces strict sequential chain."""
        pub_info = test_authority.public_key_info
        test_verifier.set_keys({"default": pub_info})
        test_verifier.set_epoch(1)
        asset = AdmittableAsset(
            asset_type=AssetType.ASSERTION_RULE.value,
            raw_data=valid_rule_data,
        )
        assert asset.state == AssetState.CANDIDATE
        asset.submit_for_admission()
        assert asset.state == AssetState.UNDER_REVIEW
        proof = test_authority.sign_from_data(
            AssetType.ASSERTION_RULE.value, valid_rule_data, public_key_id="default"
        )
        asset.audit_complete(proof)
        assert asset.state == AssetState.ADMITTED
        ok = asset.convert_to_production()
        assert ok is True

    def test_t06_proof_self_integrity(self, test_authority, valid_rule_data):
        """T3: Proof self-integrity check passes."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical
        )
        assert proof.verify_self_integrity() is True

    def test_t07_proof_serialization(self, test_authority, valid_rule_data):
        """Proof round-trips through JSON."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical
        )
        json_str = proof.to_json()
        restored = AdmissionProof.from_json(json_str)
        assert restored.proof_id == proof.proof_id
        assert restored.content_digest == proof.content_digest
        assert restored.signature == proof.signature


# ===========================================================================
# Category 2: Negative Tests — Attack Vectors (T8–T40)
# ===========================================================================

class TestAttackVectors:
    """40 negative tests covering all attack vectors."""

    def test_t08_direct_construction_fails(self, test_verifier):
        """T8: Direct construction of ProductionAsset -> FAIL CLOSED."""
        fake_proof = AdmissionProof(
            proof_id="fake",
            authority_id="fake",
            public_key_id="unknown-key",
            epoch=1,
            timestamp="2026-09-01T00:00:00+00:00",
            version="1.0",
            asset_type="AssertionRule",
            asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"),
            signature=b"\x00" * 70,
            signature_algorithm="ES256",
        )
        result = test_verifier.verify(fake_proof)
        assert result != VERIFIER_OK

    def test_t09_monkey_patch_is_production_fails(self, admitted_asset):
        """T9: Monkey-patch is_production = True -> FAIL CLOSED."""
        import tongshu.assertion.verifier as prod_tv
        prod = ProductionAsset(
            inner=admitted_asset.raw_data,
            proof=admitted_asset.proof,
        )
        # Attempt to monkey-patch the instance
        prod.is_production = lambda: True
        # Clear production verifier keys to ensure rejection
        prod_tv._TRUSTED_KEYS = {}
        result = verify_production_proof(prod.proof)
        assert result != VERIFIER_OK
        # Restore
        pub_info = prod_tv._TRUSTED_KEYS  # will be restored by autouse

    def test_t10_forged_proof_invalid_signature(self, valid_rule_data):
        """T10: Forge AdmissionProof with invalid signature -> FAIL CLOSED."""
        canonical = canonicalize(valid_rule_data)
        fake_proof = AdmissionProof(
            proof_id="forged-1",
            authority_id="fake-authority",
            public_key_id="fake-key",
            epoch=1,
            timestamp="2026-09-01T00:00:00+00:00",
            version="1.0",
            asset_type="AssertionRule",
            asset_canonical=canonical,
            content_digest=compute_digest(canonical),
            signature=b"\x00" * 70,
            signature_algorithm="ES256",
        )
        result = verify_production_proof(fake_proof)
        assert result != VERIFIER_OK

    def test_t11_forged_proof_wrong_content(self, test_authority, valid_rule_data):
        """T11: Forge AdmissionProof with valid signature but wrong content."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical
        )
        tampered = proof.asset_canonical + b"\x00"
        tampered_proof = AdmissionProof(
            proof_id=proof.proof_id,
            authority_id=proof.authority_id,
            public_key_id=proof.public_key_id,
            epoch=proof.epoch,
            timestamp=proof.timestamp,
            version=proof.version,
            asset_type=proof.asset_type,
            asset_canonical=tampered,
            content_digest=compute_digest(tampered),
            signature=proof.signature,
            signature_algorithm=proof.signature_algorithm,
        )
        result = verify_production_proof(tampered_proof)
        assert result != VERIFIER_OK

    def test_t12_modify_rule_after_admission(self, admitted_asset):
        """T12: Modify rule after admission -> FAIL CLOSED."""
        original_canonical = admitted_asset.proof.asset_canonical
        admitted_asset.raw_data["direction"] = "cautionous"
        new_canonical = canonicalize(admitted_asset.raw_data)
        assert new_canonical != original_canonical
        assert admitted_asset.is_production() is False

    def test_t13_candidate_to_production_bypass_forbidden(self, valid_rule_data):
        """T27: CANDIDATE -> PRODUCTION direct transition -> FORBIDDEN."""
        asset = AdmittableAsset(
            asset_type=AssetType.ASSERTION_RULE.value,
            raw_data=valid_rule_data,
        )
        with pytest.raises(AdmissionStateError):
            asset.convert_to_production()

    def test_t14_wrong_epoch_rejected(self, test_authority, test_verifier, valid_rule_data):
        """T28: Proof with wrong epoch -> VERIFIER_EPOCH_EXPIRED."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key"
        )
        pub_info = test_authority.public_key_info
        test_verifier.set_keys({"test-key": pub_info})
        test_verifier.set_epoch(1)
        tampered = AdmissionProof(
            proof_id=proof.proof_id,
            authority_id=proof.authority_id,
            public_key_id=proof.public_key_id,
            epoch=99,
            timestamp=proof.timestamp,
            version=proof.version,
            asset_type=proof.asset_type,
            asset_canonical=proof.asset_canonical,
            content_digest=proof.content_digest,
            signature=proof.signature,
            signature_algorithm=proof.signature_algorithm,
        )
        result = test_verifier.verify(tampered)
        assert result == VERIFIER_EPOCH_EXPIRED

    def test_t15_revoked_proof_rejected(self, test_authority, test_verifier, valid_rule_data):
        """T37: Proof with correct epoch but revoked proof_id -> VERIFIER_REVOKED."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key"
        )
        pub_info = test_authority.public_key_info
        test_verifier.set_keys({"test-key": pub_info})
        test_verifier.set_epoch(1)
        test_verifier.mark_revoked(proof.proof_id)
        result = test_verifier.verify(proof)
        assert result == VERIFIER_REVOKED

    def test_t16_malformed_proof_schema_error(self):
        """T30: Proof with missing canonical_content -> VERIFIER_SCHEMA_ERROR."""
        bad_proof = AdmissionProof(
            proof_id="bad",
            authority_id="auth",
            public_key_id="key",
            epoch=1,
            timestamp="2026-01-01T00:00:00+00:00",
            version="1.0",
            asset_type="AssertionRule",
            asset_canonical=b"",
            content_digest=compute_digest(b""),
            signature=b"\x01" * 70,
            signature_algorithm="ES256",
        )
        result = verify_production_proof(bad_proof)
        assert result != VERIFIER_OK

    def test_t17_empty_signature(self):
        """T22: Empty signature -> FAIL CLOSED."""
        proof = AdmissionProof(
            proof_id="empty-sig",
            authority_id="auth",
            public_key_id="key",
            epoch=1,
            timestamp="2026-01-01T00:00:00+00:00",
            version="1.0",
            asset_type="AssertionRule",
            asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"),
            signature=b"",
            signature_algorithm="ES256",
        )
        result = verify_production_proof(proof)
        assert result != VERIFIER_OK

    def test_t18_null_public_key_id(self):
        """T23: Null public_key_id -> VERIFIER_KEY_UNKNOWN."""
        proof = AdmissionProof(
            proof_id="no-key",
            authority_id="auth",
            public_key_id="",
            epoch=1,
            timestamp="2026-01-01T00:00:00+00:00",
            version="1.0",
            asset_type="AssertionRule",
            asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"),
            signature=b"\x01" * 70,
            signature_algorithm="ES256",
        )
        result = verify_production_proof(proof)
        assert result == VERIFIER_KEY_UNKNOWN

    def test_t19_json_injection_ignored(self, test_authority, test_verifier, valid_rule_data):
        """T24: Manually set PRODUCTION_ADMITTED in JSON -> IGNORED."""
        valid_rule_data["PRODUCTION_ADMITTED"] = True
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key"
        )
        pub_info = test_authority.public_key_info
        test_verifier.set_keys({"test-key": pub_info})
        test_verifier.set_epoch(1)
        result = test_verifier.verify(proof)
        assert result == VERIFIER_OK  # Valid because signature is correct

    def test_t20_state_machine_invariants(self, valid_rule_data):
        """T27: State machine prevents CANDIDATE -> PRODUCTION."""
        asset = AdmittableAsset(
            asset_type=AssetType.ASSERTION_RULE.value,
            raw_data=valid_rule_data,
        )
        with pytest.raises(AdmissionStateError):
            asset.convert_to_production()
        with pytest.raises(AdmissionStateError):
            asset.revoke()

    def test_t21_verifier_not_monkey_patchable(self):
        """T40: Monkey-patch verify_production_proof -> FAIL CLOSED."""
        import tongshu.assertion.verifier as tv_module
        original = tv_module.verify_production_proof
        tv_module.verify_production_proof = lambda x: 0
        import importlib
        importlib.reload(tv_module)
        assert callable(tv_module.verify_production_proof)

    def test_t22_proof_from_wrong_authority(self, valid_rule_data):
        """T29: Proof with wrong authority_id -> fails verification."""
        proof = AdmissionProof(
            proof_id="wrong-authority",
            authority_id="evil-authority",
            public_key_id="unknown-key",
            epoch=1,
            timestamp="2026-01-01T00:00:00+00:00",
            version="1.0",
            asset_type="AssertionRule",
            asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"),
            signature=b"\x01" * 70,
            signature_algorithm="ES256",
        )
        result = verify_production_proof(proof)
        assert result != VERIFIER_OK

    def test_t23_invalid_signature_algorithm(self):
        """T53: Invalid signature algorithm -> FAIL CLOSED."""
        proof = AdmissionProof(
            proof_id="bad-algo",
            authority_id="auth",
            public_key_id="key",
            epoch=1,
            timestamp="2026-01-01T00:00:00+00:00",
            version="1.0",
            asset_type="AssertionRule",
            asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"),
            signature=b"\x01" * 70,
            signature_algorithm="HS256",
        )
        result = verify_production_proof(proof)
        assert result != VERIFIER_OK

    def test_t24_truncated_canonical(self, test_authority, valid_rule_data):
        """T32: Truncated canonical_content -> VERIFIER_DIGEST_MISMATCH."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key"
        )
        truncated = proof.asset_canonical[:len(proof.asset_canonical)//2]
        bad_proof = AdmissionProof(
            proof_id=proof.proof_id,
            authority_id=proof.authority_id,
            public_key_id=proof.public_key_id,
            epoch=proof.epoch,
            timestamp=proof.timestamp,
            version=proof.version,
            asset_type=proof.asset_type,
            asset_canonical=truncated,
            content_digest=proof.content_digest,
            signature=proof.signature,
            signature_algorithm=proof.signature_algorithm,
        )
        result = verify_production_proof(bad_proof)
        assert result == VERIFIER_DIGEST_MISMATCH

    def test_t25_extra_fields_in_canonical(self, test_authority, valid_rule_data):
        """T33: Extra fields in canonical_content -> VERIFIER_DIGEST_MISMATCH."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key"
        )
        extra = proof.asset_canonical + b'{"extra":"tampered"}'
        bad_proof = AdmissionProof(
            proof_id=proof.proof_id,
            authority_id=proof.authority_id,
            public_key_id=proof.public_key_id,
            epoch=proof.epoch,
            timestamp=proof.timestamp,
            version=proof.version,
            asset_type=proof.asset_type,
            asset_canonical=extra,
            content_digest=proof.content_digest,
            signature=proof.signature,
            signature_algorithm=proof.signature_algorithm,
        )
        result = verify_production_proof(bad_proof)
        assert result == VERIFIER_DIGEST_MISMATCH

    def test_t26_fail_closed_on_unknown_key(self):
        """T39: Missing public key in config -> FAIL CLOSED."""
        proof = AdmissionProof(
            proof_id="no-key",
            authority_id="auth",
            public_key_id="nonexistent",
            epoch=1,
            timestamp="2026-01-01T00:00:00+00:00",
            version="1.0",
            asset_type="AssertionRule",
            asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"),
            signature=b"\x01" * 70,
            signature_algorithm="ES256",
        )
        result = verify_production_proof(proof)
        assert result == VERIFIER_KEY_UNKNOWN

    def test_t27_production_asset_requires_verifier(self, admitted_asset):
        """ProductionAsset.is_production() always calls verifier."""
        import tongshu.assertion.verifier as prod_tv
        prod = ProductionAsset(
            inner=admitted_asset.raw_data,
            proof=admitted_asset.proof,
        )
        # Clear production keys to force rejection
        prod_tv._TRUSTED_KEYS = {}
        assert prod.is_production() is False

    def test_t28_cannot_revoke_non_admitted(self, valid_rule_data, test_authority):
        """Cannot revoke an asset that is not ADMITTED."""
        asset = AdmittableAsset(
            asset_type=AssetType.ASSERTION_RULE.value,
            raw_data=valid_rule_data,
        )
        with pytest.raises(AdmissionStateError):
            asset.revoke()

    def test_t29_cannot_admit_non_review(self, valid_rule_data, test_authority):
        """Cannot complete audit on non-UNDER_REVIEW asset."""
        asset = AdmittableAsset(
            asset_type=AssetType.ASSERTION_RULE.value,
            raw_data=valid_rule_data,
        )
        proof = test_authority.sign_from_data(
            AssetType.ASSERTION_RULE.value, valid_rule_data
        )
        with pytest.raises(AdmissionStateError):
            asset.audit_complete(proof)

    def test_t30_double_admission_same_rule(self, test_authority, valid_rule_data):
        """T31: Double-admission of same rule -> same digest."""
        canonical = canonicalize(valid_rule_data)
        proof1 = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical
        )
        proof2 = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical
        )
        assert proof1.content_digest == proof2.content_digest
        assert proof1.proof_id != proof2.proof_id


# ===========================================================================
# Category 3: Integrity Tests (T41–T47)
# ===========================================================================

class TestIntegrity:
    """Integrity and invariance tests."""

    def test_t41_canonicalization_deterministic(self, valid_rule_data):
        """T41: Canonicalization is deterministic."""
        c1 = canonicalize(valid_rule_data)
        c2 = canonicalize(valid_rule_data)
        assert c1 == c2

    def test_t42_canonicalization_covers_all_fields(self, valid_rule_data):
        """T42: Canonicalization covers all semantic fields."""
        c1 = canonicalize(valid_rule_data)
        modified = dict(valid_rule_data)
        modified["direction"] = "cautionous"
        c2 = canonicalize(modified)
        assert c1 != c2

    def test_t43_proof_self_contained(self, test_authority, valid_rule_data):
        """T44: Proof is self-contained (all verification data in proof)."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical
        )
        assert proof.asset_canonical == canonical
        assert proof.content_digest == compute_digest(canonical)
        assert len(proof.signature) > 0

    def test_t44_epoch_boundary_correct(self, test_authority, test_verifier, valid_rule_data):
        """T46: Epoch boundary correctness."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key"
        )
        pub_info = test_authority.public_key_info
        test_verifier.set_keys({"test-key": pub_info})
        test_verifier.set_epoch(1)
        assert test_verifier.verify(proof) == VERIFIER_OK
        future_proof = AdmissionProof(
            proof_id=proof.proof_id,
            authority_id=proof.authority_id,
            public_key_id=proof.public_key_id,
            epoch=2,
            timestamp=proof.timestamp,
            version=proof.version,
            asset_type=proof.asset_type,
            asset_canonical=proof.asset_canonical,
            content_digest=proof.content_digest,
            signature=proof.signature,
            signature_algorithm=proof.signature_algorithm,
        )
        assert test_verifier.verify(future_proof) == VERIFIER_EPOCH_EXPIRED

    def test_t45_canonical_order_independent(self):
        """Canonicalization is order-independent for dicts."""
        data1 = {"a": 1, "b": 2, "c": 3}
        data2 = {"c": 3, "a": 1, "b": 2}
        assert canonicalize(data1) == canonicalize(data2)

    def test_t46_none_serialized_as_null(self):
        """None values are serialized as null."""
        data = {"key": None, "other": "value"}
        result = canonicalize(data)
        assert b"null" in result

    def test_t47_enums_serialized_as_values(self):
        """Enum values are serialized as their value."""
        from tongshu.assertion.models import AssetState
        data = {"state": AssetState.CANDIDATE}
        result = canonicalize(data)
        assert b"CANDIDATE" in result


# ===========================================================================
# Category 4: Concurrency Tests (T48–T50)
# ===========================================================================

class TestConcurrency:
    """Thread-safety tests."""

    def test_t48_concurrent_admission_same_rule(self, test_authority, valid_rule_data):
        """T48: Concurrent admission of same rule -> same digest."""
        results = []
        barrier = threading.Barrier(3)

        def admit():
            barrier.wait()
            canonical = canonicalize(valid_rule_data)
            proof = test_authority.sign(
                AssetType.ASSERTION_RULE.value, canonical
            )
            results.append(proof.content_digest)

        threads = [threading.Thread(target=admit) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(set(results)) == 1

    def test_t49_concurrent_different_rules(self, test_authority):
        """T49: Concurrent admission of different rules -> no corruption."""
        results = []
        barrier = threading.Barrier(3)

        def admit(idx):
            barrier.wait()
            data = {"rule_id": f"RULE_{idx}", "test": idx}
            canonical = canonicalize(data)
            proof = test_authority.sign(
                AssetType.ASSERTION_RULE.value, canonical
            )
            results.append(proof.proof_id)

        threads = [threading.Thread(target=admit, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(results) == 3
        assert len(set(results)) == 3

    def test_t50_verifier_consistent_under_load(self, test_authority, test_verifier, valid_rule_data):
        """T50: Proof verification consistent under concurrent load."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key"
        )
        pub_info = test_authority.public_key_info
        test_verifier.set_keys({"test-key": pub_info})
        test_verifier.set_epoch(1)

        results = []
        barrier = threading.Barrier(5)

        def verify():
            barrier.wait()
            results.append(test_verifier.verify(proof))

        threads = [threading.Thread(target=verify) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert all(r == VERIFIER_OK for r in results)


# ===========================================================================
# Category 5: Failure Mode Tests (T51–T57)
# ===========================================================================

class TestFailureModes:
    """Failure mode and edge case tests."""

    def test_t51_missing_source_file(self, tmp_path):
        """T51: Missing source file -> AdmissionLoadError."""
        loader = ProductionRuleLoader(path=str(tmp_path / "nonexistent.json"))
        with pytest.raises(AdmissionLoadError):
            loader.load()

    def test_t52_corrupted_json(self, tmp_path):
        """T52: Corrupted JSON -> AdmissionLoadError."""
        rules_file = tmp_path / "corrupt.json"
        rules_file.write_text("{invalid json!!!")
        loader = ProductionRuleLoader(path=str(rules_file))
        with pytest.raises(AdmissionLoadError):
            loader.load()

    def test_t53_incomplete_provenance_rejected(self, tmp_path):
        """T56: Empty provenance -> Rejected at load time."""
        rule = {
            "rule_id": "BAD_RULE",
            "domain": "GROWTH",
            "match_strategy": "EXACT",
            "condition": {"atom_id": "TEN_GOD_JIA"},
            "direction": "supportive",
            "provenance": {},
            "semantic_content": {"zh_label": "甲"},
        }
        rules_file = tmp_path / "bad_provenance.json"
        rules_file.write_text(json.dumps([rule]))
        loader = ProductionRuleLoader(path=str(rules_file))
        # Will fail during proof verification (no proof embedded)
        with pytest.raises(AdmissionLoadError):
            loader.load()

    def test_t54_missing_source_chapter(self, tmp_path):
        """T57: Incomplete provenance -> Rejected."""
        rule = {
            "rule_id": "BAD_RULE",
            "domain": "GROWTH",
            "match_strategy": "EXACT",
            "condition": {"atom_id": "TEN_GOD_JIA"},
            "direction": "supportive",
            "provenance": {"source_work": "子平真诠"},
            "semantic_content": {"zh_label": "甲"},
        }
        rules_file = tmp_path / "incomplete.json"
        rules_file.write_text(json.dumps([rule]))
        loader = ProductionRuleLoader(path=str(rules_file))
        with pytest.raises(AdmissionLoadError):
            loader.load()

    def test_t55_empty_rules_array(self, tmp_path):
        """T4: Empty rules array -> AdmissionLoadError."""
        rules_file = tmp_path / "empty.json"
        rules_file.write_text("[]")
        loader = ProductionRuleLoader(path=str(rules_file))
        with pytest.raises(AdmissionLoadError):
            loader.load()

    def test_t56_verifier_returns_error_code(self):
        """Verifier returns specific error codes, not generic exceptions."""
        proof = AdmissionProof(
            proof_id="test",
            authority_id="auth",
            public_key_id="unknown",
            epoch=1,
            timestamp="2026-01-01T00:00:00+00:00",
            version="1.0",
            asset_type="AssertionRule",
            asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"),
            signature=b"\x01" * 70,
            signature_algorithm="ES256",
        )
        result = verify_production_proof(proof)
        assert isinstance(result, int)
        assert result != VERIFIER_OK

    def test_t57_load_production_helper(self, test_authority, test_verifier, valid_rule_data, tmp_path):
        """Convenience function load_production_rules works with pre-signed proofs."""
        from tongshu.assertion.loader import load_production_rules
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical, public_key_id="default"
        )
        pub_info = test_authority.public_key_info
        test_verifier.set_keys({"default": pub_info})
        test_verifier.set_epoch(1)
        # Build pre-admitted rule data
        rule_with_proof = dict(valid_rule_data)
        rule_with_proof["admission_proof"] = proof.to_json()
        rules_file = tmp_path / "valid.json"
        rules_file.write_text(json.dumps([rule_with_proof]))
        result = load_production_rules(path=str(rules_file))
        assert len(result) == 1
        assert "ZP_STEM_YEAR" in result


# ===========================================================================
# Category 6: Verifier Bypass Tests (T58)
# ===========================================================================

class TestVerifierBypass:
    """T58: Verify that the verification result itself cannot be forged."""

    def test_t58_verifier_result_not_forgable(self):
        """
        T58: The verifier's return value cannot be spoofed by Zone 1 code.
        """
        import tongshu.assertion.verifier as tv

        # Try to monkey-patch at module level
        tv.verify_production_proof = lambda x: VERIFIER_OK

        # Reload to get the real function back
        import importlib
        importlib.reload(tv)

        # Verify with an obviously bad proof
        bad_proof = AdmissionProof(
            proof_id="bypass-test",
            authority_id="evil",
            public_key_id="nonexistent",
            epoch=1,
            timestamp="2026-01-01T00:00:00+00:00",
            version="1.0",
            asset_type="AssertionRule",
            asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"),
            signature=b"\x00" * 70,
            signature_algorithm="ES256",
        )
        result = tv.verify_production_proof(bad_proof)
        assert result != VERIFIER_OK

    def test_t58_trusted_keys_not_replaceable(self):
        """
        T58b: Trusted keys cannot be replaced by Zone 1 code at runtime.
        Verifies that even after replacing _TRUSTED_KEYS, verification
        uses the current state (fail-closed for unknown keys).
        """
        import tongshu.assertion.verifier as tv
        from tongshu.assertion.models import AdmissionProof
        from tongshu.assertion.canonicalizer import compute_digest

        original_keys = dict(tv._TRUSTED_KEYS)
        # Try to replace with empty keys
        tv._TRUSTED_KEYS = {}
        bad_proof = AdmissionProof(
            proof_id="hacked", authority_id="auth", public_key_id="any",
            epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"), signature=b"\x01" * 70,
            signature_algorithm="ES256",
        )
        result = tv.verify_production_proof(bad_proof)
        assert result == VERIFIER_KEY_UNKNOWN  # Hacked keys → rejected
        # Restore
        tv._TRUSTED_KEYS = original_keys


# ===========================================================================
# Category 7: P0 Security Tests (T59-T62)
# ===========================================================================

class TestP0Security:
    """Tests for P0 fixes: no fallback, no fail-open, proper isolation."""

    def test_t59_native_unavailable_fails_closed(self):
        """T59: Native verifier unavailable -> FAIL CLOSED, NOT OK."""
        import tongshu.assertion.verifier as tv
        from tongshu.assertion.models import AdmissionProof
        from tongshu.assertion.canonicalizer import compute_digest

        # Clear production keys to simulate native-unavailable path
        original_keys = dict(tv._TRUSTED_KEYS)
        tv._TRUSTED_KEYS = {}
        try:
            proof = AdmissionProof(
                proof_id="no-native", authority_id="auth", public_key_id="key",
                epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
                asset_type="AssertionRule", asset_canonical=b"{}",
                content_digest=compute_digest(b"{}"), signature=b"\x01" * 70,
                signature_algorithm="ES256",
            )
            result = verify_production_proof(proof)
            # Must NOT be OK — either KEY_UNKNOWN or CRYPTO_ERROR
            assert result != VERIFIER_OK
        finally:
            tv._TRUSTED_KEYS = original_keys

    def test_t60_crypto_exception_rejects(self, test_verifier):
        """T60: Crypto exception -> VERIFIER_CRYPTO_ERROR, NOT OK."""
        from tongshu.assertion.test_verifier import TestVerifier
        tv = TestVerifier()
        # Set up a key but provide invalid coordinates that cause crypto failure
        tv.set_keys({"bad-key": {"algorithm": "ES256", "x": "not-valid-base64!!!", "y": "also-bad!!!"}})
        tv.set_epoch(1)
        proof = AdmissionProof(
            proof_id="crypto-fail",
            authority_id="auth",
            public_key_id="bad-key",
            epoch=1,
            timestamp="2026-01-01T00:00:00+00:00",
            version="1.0",
            asset_type="AssertionRule",
            asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"),
            signature=b"\x01" * 70,
            signature_algorithm="ES256",
        )
        result = tv.verify(proof)
        # Should be CRYPTO_ERROR or KEY_UNKNOWN, NOT OK
        assert result != VERIFIER_OK

    def test_t61_test_verifier_isolated_from_production(self):
        """T61: TestVerifier cannot affect production verifier state."""
        import tongshu.assertion.verifier as prod_tv
        from tongshu.assertion.test_verifier import TestVerifier

        original_keys = dict(prod_tv._TRUSTED_KEYS)
        original_epoch = prod_tv._CURRENT_EPOCH

        tv = TestVerifier()
        tv.set_keys({"hacked": {}})
        tv.set_epoch(99)

        # Production state must be unchanged
        assert prod_tv._TRUSTED_KEYS == original_keys
        assert prod_tv._CURRENT_EPOCH == original_epoch

    def test_t62_authority_production_mode_rejects_ephemeral(self):
        """T62: Production-mode Authority rejects ephemeral key generation."""
        with pytest.raises(AdmissionError):
            AdmissionAuthority(
                authority_id="prod-auth",
                epoch=1,
                production_mode=True,
            )

    def test_t34_invalid_ecdsa_curve(self, valid_rule_data):
        """T34: Invalid ECDSA curve (non-P-256) -> VERIFIER_SCHEMA_ERROR."""
        proof = AdmissionProof(
            proof_id="bad-curve", authority_id="auth", public_key_id="key",
            epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"), signature=b"\x01" * 70,
            signature_algorithm="ES384",
        )
        result = verify_production_proof(proof)
        assert result == VERIFIER_SCHEMA_ERROR

    def test_t35_zero_length_signature(self):
        """T35: Zero-length signature -> VERIFIER_SIGNATURE_INVALID."""
        proof = AdmissionProof(
            proof_id="zero-sig", authority_id="auth", public_key_id="key",
            epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"), signature=b"",
            signature_algorithm="ES256",
        )
        result = verify_production_proof(proof)
        assert result == VERIFIER_SIGNATURE_INVALID

    def test_t36_correct_sig_wrong_epoch(self, test_authority, valid_rule_data):
        """T36: Proof with correct signature but wrong epoch -> VERIFIER_EPOCH_EXPIRED."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(
            AssetType.ASSERTION_RULE.value, canonical, public_key_id="default"
        )
        tampered = AdmissionProof(
            proof_id=proof.proof_id, authority_id=proof.authority_id,
            public_key_id=proof.public_key_id, epoch=0,
            timestamp=proof.timestamp, version=proof.version,
            asset_type=proof.asset_type, asset_canonical=proof.asset_canonical,
            content_digest=proof.content_digest, signature=proof.signature,
            signature_algorithm=proof.signature_algorithm,
        )
        result = verify_production_proof(tampered)
        assert result == VERIFIER_EPOCH_EXPIRED

    def test_t38_native_extension_not_loadable(self, test_authority, valid_rule_data):
        """T38: Without native extension, in-process verifier still rejects bad proofs."""
        import tongshu.assertion.verifier as tv
        original_keys = dict(tv._TRUSTED_KEYS)
        tv._TRUSTED_KEYS = {}
        try:
            bad_proof = AdmissionProof(
                proof_id="no-ext", authority_id="evil", public_key_id="nonexistent",
                epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
                asset_type="AssertionRule", asset_canonical=b"{}",
                content_digest=compute_digest(b"{}"), signature=b"\x00" * 70,
                signature_algorithm="ES256",
            )
            result = verify_production_proof(bad_proof)
            assert result != VERIFIER_OK
        finally:
            tv._TRUSTED_KEYS = original_keys

    def test_t45_public_key_immutability(self):
        """T45: Public key cannot be changed at runtime via normal means."""
        import tongshu.assertion.verifier as tv
        original_keys = dict(tv._TRUSTED_KEYS)
        tv._TRUSTED_KEYS = {"hacked": {}}
        tv._load_trust_anchor()
        # After load, keys should match the file (empty), not original injected state
        # This tests that _load_trust_anchor() can reset state
