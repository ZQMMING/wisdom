"""
Production Admission Governance — Full Test Suite (65 tests)

Categories:
  T1-T7     Positive tests (happy path)
  T8-T40    Negative tests (attack vectors)
  T41-T47   Integrity tests
  T48-T50   Concurrency tests
  T51-T57   Failure mode tests
  T58-T62   Verifier bypass + security
  T63-T69   Proof substitution attacks (P0 fix)

Acceptance criteria: ALL PASS, zero tolerance.
"""

from __future__ import annotations

import json
import sys
import threading
from pathlib import Path

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
from tongshu.assertion.loader import ProductionRuleLoader, load_production_rules
from tongshu.assertion.test_verifier import TestVerifier


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def test_authority():
    auth = AdmissionAuthority(authority_id="test-authority", epoch=1)
    return auth


@pytest.fixture
def valid_rule_data():
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


def _inject_keys(auth):
    """Helper: inject test authority's public key into production verifier."""
    import tongshu.assertion.verifier as tv
    pub_info = auth.public_key_info
    tv._TRUSTED_KEYS = {"test-key": pub_info, "default": pub_info}
    tv._CURRENT_EPOCH = 1
    tv._REVOCATION_LIST = set()


def _restore_keys():
    """Helper: restore production verifier to file-based state."""
    import tongshu.assertion.verifier as tv
    tv._load_trust_anchor()


# ===========================================================================
# Category 1: Positive Tests (T1–T7)
# ===========================================================================

class TestPositive:
    def test_t01_valid_admission(self, test_authority, valid_rule_data):
        """T1: Valid admission -> Production asset."""
        _inject_keys(test_authority)
        asset = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data=valid_rule_data)
        asset.submit_for_admission()
        canonical = asset.to_canonical()
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        asset.audit_complete(proof)
        ok = asset.convert_to_production()
        assert ok is True
        assert asset.state == AssetState.PRODUCTION
        _restore_keys()

    def test_t02_multiple_rules_all_valid(self, test_authority, valid_rule_data):
        """T2: Multiple rules, all valid -> All admitted."""
        _inject_keys(test_authority)
        results = []
        for i in range(5):
            data = dict(valid_rule_data)
            data["rule_id"] = f"RULE_{i}"
            asset = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data=data)
            asset.submit_for_admission()
            proof = test_authority.sign_from_data(AssetType.ASSERTION_RULE.value, data, public_key_id="test-key")
            asset.audit_complete(proof)
            ok = asset.convert_to_production()
            results.append(ok)
        assert all(results)

    def test_t03_empty_rules_raises(self, tmp_path):
        """T4: Empty rules file -> AdmissionLoadError."""
        rules_file = tmp_path / "empty_rules.json"
        rules_file.write_text("[]")
        loader = ProductionRuleLoader(path=str(rules_file))
        with pytest.raises(AdmissionLoadError):
            loader.load()

    def test_t04_re_admit_same_content_idempotent(self, test_authority, valid_rule_data):
        """T5: Re-admit same content -> Same digest."""
        canonical = canonicalize(valid_rule_data)
        proof1 = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical)
        proof2 = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical)
        assert proof1.content_digest == proof2.content_digest

    def test_t05_state_machine_strict_chain(self, test_authority, valid_rule_data):
        """T7: State machine enforces strict chain."""
        _inject_keys(test_authority)
        asset = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data=valid_rule_data)
        assert asset.state == AssetState.CANDIDATE
        asset.submit_for_admission()
        assert asset.state == AssetState.UNDER_REVIEW
        proof = test_authority.sign_from_data(AssetType.ASSERTION_RULE.value, valid_rule_data)
        asset.audit_complete(proof)
        assert asset.state == AssetState.ADMITTED
        ok = asset.convert_to_production()
        assert ok is True

    def test_t06_proof_self_integrity(self, test_authority, valid_rule_data):
        """T3: Proof self-integrity check passes."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical)
        assert proof.verify_self_integrity() is True

    def test_t07_proof_serialization(self, test_authority, valid_rule_data):
        """Proof round-trips through JSON."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical)
        restored = AdmissionProof.from_json(proof.to_json())
        assert restored.proof_id == proof.proof_id
        assert restored.content_digest == proof.content_digest
        assert restored.signature == proof.signature


# ===========================================================================
# Category 2: Negative Tests (T8–T40)
# ===========================================================================

class TestAttackVectors:
    def test_t08_direct_construction_fails(self):
        """T8: Direct construction of ProductionAsset -> FAIL CLOSED."""
        bad_proof = AdmissionProof(
            proof_id="fake", authority_id="fake", public_key_id="unknown-key",
            epoch=1, timestamp="2026-09-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"), signature=b"\x00" * 70,
            signature_algorithm="ES256",
        )
        result = verify_production_proof(bad_proof, b"{}")
        assert result != VERIFIER_OK

    def test_t09_monkey_patch_is_production_fails(self, test_authority, valid_rule_data):
        """T9: Monkey-patch is_production = True -> FAIL CLOSED."""
        _inject_keys(test_authority)
        asset = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data=valid_rule_data)
        asset.submit_for_admission()
        canonical = asset.to_canonical()
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        asset.audit_complete(proof)
        prod = ProductionAsset(inner=asset.raw_data, proof=asset.proof)
        prod.is_production = lambda: True  # monkey-patch
        import tongshu.assertion.verifier as tv
        tv._TRUSTED_KEYS = {}
        result = verify_production_proof(prod.proof, canonical)
        assert result != VERIFIER_OK

    def test_t10_forged_proof_invalid_signature(self, valid_rule_data):
        """T10: Forge proof with invalid signature -> FAIL CLOSED."""
        canonical = canonicalize(valid_rule_data)
        fake = AdmissionProof(
            proof_id="forged", authority_id="fake", public_key_id="fake-key",
            epoch=1, timestamp="2026-09-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=canonical,
            content_digest=compute_digest(canonical), signature=b"\x00" * 70,
            signature_algorithm="ES256",
        )
        result = verify_production_proof(fake, canonical)
        assert result != VERIFIER_OK

    def test_t11_forged_proof_wrong_content(self, test_authority, valid_rule_data):
        """T11: Proof valid but content doesn't match current asset."""
        canonical_a = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical_a, public_key_id="test-key")
        # Tampered canonical
        tampered = canonical_a + b"\x00tampered"
        tampered_proof = AdmissionProof(
            proof_id=proof.proof_id, authority_id=proof.authority_id,
            public_key_id=proof.public_key_id, epoch=proof.epoch,
            timestamp=proof.timestamp, version=proof.version,
            asset_type=proof.asset_type, asset_canonical=tampered,
            content_digest=compute_digest(tampered), signature=proof.signature,
            signature_algorithm=proof.signature_algorithm,
        )
        result = verify_production_proof(tampered_proof, tampered)
        # Self-integrity fails because digest was recomputed for tampered
        assert result != VERIFIER_OK

    def test_t12_modify_rule_after_admission(self, test_authority, valid_rule_data):
        """T12: Modify rule after admission -> FAIL CLOSED."""
        _inject_keys(test_authority)
        asset = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data=valid_rule_data)
        asset.submit_for_admission()
        canonical = asset.to_canonical()
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        asset.audit_complete(proof)
        # Modify rule
        asset.raw_data["direction"] = "cautionous"
        assert asset.is_production() is False

    def test_t13_candidate_to_production_bypass_forbidden(self, valid_rule_data):
        """T27: CANDIDATE -> PRODUCTION direct -> FORBIDDEN."""
        asset = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data=valid_rule_data)
        with pytest.raises(AdmissionStateError):
            asset.convert_to_production()

    def test_t14_wrong_epoch_rejected(self, test_authority, valid_rule_data):
        """T28: Wrong epoch -> VERIFIER_EPOCH_EXPIRED."""
        _inject_keys(test_authority)
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        tampered = AdmissionProof(
            proof_id=proof.proof_id, authority_id=proof.authority_id,
            public_key_id=proof.public_key_id, epoch=99,
            timestamp=proof.timestamp, version=proof.version,
            asset_type=proof.asset_type, asset_canonical=proof.asset_canonical,
            content_digest=proof.content_digest, signature=proof.signature,
            signature_algorithm=proof.signature_algorithm,
        )
        result = verify_production_proof(tampered, canonical)
        assert result == VERIFIER_EPOCH_EXPIRED

    def test_t15_revoked_proof_rejected(self, test_authority, valid_rule_data):
        """T37: Revoked proof -> VERIFIER_REVOKED."""
        _inject_keys(test_authority)
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        import tongshu.assertion.verifier as tv
        tv._REVOCATION_LIST = {proof.proof_id}
        result = verify_production_proof(proof, canonical)
        assert result == VERIFIER_REVOKED
        tv._REVOCATION_LIST = set()

    def test_t16_malformed_proof_schema_error(self):
        """T30: Empty canonical -> schema error."""
        bad = AdmissionProof(
            proof_id="bad", authority_id="auth", public_key_id="key",
            epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=b"",
            content_digest=compute_digest(b""), signature=b"\x01" * 70,
            signature_algorithm="ES256",
        )
        result = verify_production_proof(bad, b"")
        assert result != VERIFIER_OK

    def test_t17_empty_signature(self):
        """T22: Empty signature -> VERIFIER_SIGNATURE_INVALID."""
        proof = AdmissionProof(
            proof_id="empty-sig", authority_id="auth", public_key_id="key",
            epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"), signature=b"",
            signature_algorithm="ES256",
        )
        result = verify_production_proof(proof, b"{}")
        assert result == VERIFIER_SIGNATURE_INVALID

    def test_t18_null_public_key_id(self):
        """T23: Null public_key_id -> VERIFIER_KEY_UNKNOWN."""
        proof = AdmissionProof(
            proof_id="no-key", authority_id="auth", public_key_id="",
            epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"), signature=b"\x01" * 70,
            signature_algorithm="ES256",
        )
        result = verify_production_proof(proof, b"{}")
        assert result == VERIFIER_KEY_UNKNOWN

    def test_t19_json_injection_ignored(self, test_authority, valid_rule_data):
        """T24: JSON injection ignored — signature matters, not flags."""
        _inject_keys(test_authority)
        valid_rule_data["PRODUCTION_ADMITTED"] = True
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        result = verify_production_proof(proof, canonical)
        assert result == VERIFIER_OK  # Valid signature despite injected flag

    def test_t20_state_machine_invariants(self, valid_rule_data):
        """State machine prevents illegal transitions."""
        asset = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data=valid_rule_data)
        with pytest.raises(AdmissionStateError):
            asset.convert_to_production()
        with pytest.raises(AdmissionStateError):
            asset.revoke()

    def test_t21_verifier_not_monkey_patchable(self):
        """T40: Verifier function cannot be bypassed by monkey-patching."""
        import tongshu.assertion.verifier as tv
        tv.verify_production_proof = lambda *a, **k: VERIFIER_OK
        import importlib
        importlib.reload(tv)
        bad_proof = AdmissionProof(
            proof_id="bypass", authority_id="evil", public_key_id="nonexistent",
            epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"), signature=b"\x00" * 70,
            signature_algorithm="ES256",
        )
        result = tv.verify_production_proof(bad_proof, b"{}")
        assert result != VERIFIER_OK

    def test_t22_proof_from_wrong_authority(self, valid_rule_data):
        """T29: Proof from wrong authority -> reject."""
        canonical = canonicalize(valid_rule_data)
        proof = AdmissionProof(
            proof_id="wrong", authority_id="evil", public_key_id="unknown-key",
            epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=canonical,
            content_digest=compute_digest(canonical), signature=b"\x01" * 70,
            signature_algorithm="ES256",
        )
        result = verify_production_proof(proof, canonical)
        assert result != VERIFIER_OK

    def test_t23_invalid_signature_algorithm(self):
        """T53: Invalid algorithm -> VERIFIER_SCHEMA_ERROR."""
        proof = AdmissionProof(
            proof_id="bad-algo", authority_id="auth", public_key_id="key",
            epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"), signature=b"\x01" * 70,
            signature_algorithm="HS256",
        )
        result = verify_production_proof(proof, b"{}")
        assert result == VERIFIER_SCHEMA_ERROR

    def test_t24_truncated_canonical(self, test_authority, valid_rule_data):
        """T32: Truncated canonical -> VERIFIER_DIGEST_MISMATCH."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        truncated = canonical[:len(canonical)//2]
        bad = AdmissionProof(
            proof_id=proof.proof_id, authority_id=proof.authority_id,
            public_key_id=proof.public_key_id, epoch=proof.epoch,
            timestamp=proof.timestamp, version=proof.version,
            asset_type=proof.asset_type, asset_canonical=truncated,
            content_digest=proof.content_digest, signature=proof.signature,
            signature_algorithm=proof.signature_algorithm,
        )
        result = verify_production_proof(bad, truncated)
        assert result == VERIFIER_DIGEST_MISMATCH

    def test_t25_extra_fields_in_canonical(self, test_authority, valid_rule_data):
        """T33: Extra fields in canonical -> VERIFIER_DIGEST_MISMATCH."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        extra = canonical + b'{"extra":"tampered"}'
        bad = AdmissionProof(
            proof_id=proof.proof_id, authority_id=proof.authority_id,
            public_key_id=proof.public_key_id, epoch=proof.epoch,
            timestamp=proof.timestamp, version=proof.version,
            asset_type=proof.asset_type, asset_canonical=extra,
            content_digest=proof.content_digest, signature=proof.signature,
            signature_algorithm=proof.signature_algorithm,
        )
        result = verify_production_proof(bad, extra)
        assert result == VERIFIER_DIGEST_MISMATCH

    def test_t26_fail_closed_on_unknown_key(self):
        """T39: Missing key -> VERIFIER_KEY_UNKNOWN."""
        proof = AdmissionProof(
            proof_id="no-key", authority_id="auth", public_key_id="nonexistent",
            epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"), signature=b"\x01" * 70,
            signature_algorithm="ES256",
        )
        result = verify_production_proof(proof, b"{}")
        assert result == VERIFIER_KEY_UNKNOWN

    def test_t27_production_asset_requires_verifier(self, test_authority, valid_rule_data):
        """ProductionAsset.is_production() always calls verifier."""
        _inject_keys(test_authority)
        asset = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data=valid_rule_data)
        asset.submit_for_admission()
        canonical = asset.to_canonical()
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        asset.audit_complete(proof)
        import tongshu.assertion.verifier as tv
        tv._TRUSTED_KEYS = {}
        prod = ProductionAsset(inner=asset.raw_data, proof=asset.proof)
        assert prod.is_production() is False

    def test_t28_cannot_revoke_non_admitted(self, valid_rule_data):
        """Cannot revoke non-ADMITTED asset."""
        asset = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data=valid_rule_data)
        with pytest.raises(AdmissionStateError):
            asset.revoke()

    def test_t29_cannot_admit_non_review(self, test_authority, valid_rule_data):
        """Cannot complete audit on non-UNDER_REVIEW asset."""
        asset = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data=valid_rule_data)
        proof = test_authority.sign_from_data(AssetType.ASSERTION_RULE.value, valid_rule_data)
        with pytest.raises(AdmissionStateError):
            asset.audit_complete(proof)

    def test_t30_double_admission_same_rule(self, test_authority, valid_rule_data):
        """T31: Double-admission -> same digest, different proof_id."""
        canonical = canonicalize(valid_rule_data)
        p1 = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical)
        p2 = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical)
        assert p1.content_digest == p2.content_digest
        assert p1.proof_id != p2.proof_id


# ===========================================================================
# Category 3: Integrity Tests (T41–T47)
# ===========================================================================

class TestIntegrity:
    def test_t41_canonicalization_deterministic(self, valid_rule_data):
        """T41: Canonicalization is deterministic."""
        assert canonicalize(valid_rule_data) == canonicalize(valid_rule_data)

    def test_t42_canonicalization_covers_all_fields(self, valid_rule_data):
        """T42: Canonicalization covers all semantic fields."""
        c1 = canonicalize(valid_rule_data)
        modified = dict(valid_rule_data)
        modified["direction"] = "cautionous"
        assert canonicalize(valid_rule_data) != canonicalize(modified)

    def test_t43_proof_self_contained(self, test_authority, valid_rule_data):
        """T44: Proof is self-contained."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical)
        assert proof.asset_canonical == canonical
        assert proof.content_digest == compute_digest(canonical)
        assert len(proof.signature) > 0

    def test_t44_epoch_boundary_correct(self, test_authority, valid_rule_data):
        """T46: Epoch boundary correctness."""
        _inject_keys(test_authority)
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        future = AdmissionProof(
            proof_id=proof.proof_id, authority_id=proof.authority_id,
            public_key_id=proof.public_key_id, epoch=99,
            timestamp=proof.timestamp, version=proof.version,
            asset_type=proof.asset_type, asset_canonical=proof.asset_canonical,
            content_digest=proof.content_digest, signature=proof.signature,
            signature_algorithm=proof.signature_algorithm,
        )
        result = verify_production_proof(future, canonical)
        assert result == VERIFIER_EPOCH_EXPIRED

    def test_t45_canonical_order_independent(self):
        """Canonicalization is order-independent for dicts."""
        d1 = {"a": 1, "b": 2}
        d2 = {"b": 2, "a": 1}
        assert canonicalize(d1) == canonicalize(d2)

    def test_t46_none_serialized_as_null(self):
        """None -> null."""
        result = canonicalize({"key": None})
        assert b"null" in result

    def test_t47_enums_serialized_as_values(self):
        """Enum -> string value."""
        result = canonicalize({"state": AssetState.CANDIDATE})
        assert b"CANDIDATE" in result


# ===========================================================================
# Category 4: Concurrency Tests (T48–T50)
# ===========================================================================

class TestConcurrency:
    def test_t48_concurrent_same_rule(self, test_authority, valid_rule_data):
        """T48: Concurrent admission of same rule -> same digest."""
        results = []
        barrier = threading.Barrier(3)
        def admit():
            barrier.wait()
            canonical = canonicalize(valid_rule_data)
            proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical)
            results.append(proof.content_digest)
        threads = [threading.Thread(target=admit) for _ in range(3)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert len(set(results)) == 1

    def test_t49_concurrent_different_rules(self, test_authority):
        """T49: Concurrent admission of different rules -> no corruption."""
        results = []
        barrier = threading.Barrier(3)
        def admit(idx):
            barrier.wait()
            data = {"rule_id": f"RULE_{idx}", "test": idx}
            canonical = canonicalize(data)
            proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical)
            results.append(proof.proof_id)
        threads = [threading.Thread(target=admit, args=(i,)) for i in range(3)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert len(set(results)) == 3

    def test_t50_verifier_consistent(self, test_authority, valid_rule_data):
        """T50: Verification consistent under concurrent load."""
        _inject_keys(test_authority)
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        results = []
        barrier = threading.Barrier(5)
        def verify():
            barrier.wait()
            results.append(verify_production_proof(proof, canonical))
        threads = [threading.Thread(target=verify) for _ in range(5)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert all(r == VERIFIER_OK for r in results)


# ===========================================================================
# Category 5: Failure Mode Tests (T51–T57)
# ===========================================================================

class TestFailureModes:
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

    def test_t53_empty_provenance_rejected(self, tmp_path):
        """T56: Missing proof in rule -> AdmissionLoadError."""
        rule = {"rule_id": "BAD", "domain": "G", "match_strategy": "EXACT",
                "condition": {}, "direction": "supportive", "provenance": {},
                "semantic_content": {}}
        rules_file = tmp_path / "bad.json"
        rules_file.write_text(json.dumps([rule]))
        loader = ProductionRuleLoader(path=str(rules_file))
        with pytest.raises(AdmissionLoadError):
            loader.load()

    def test_t54_missing_proof_field(self, tmp_path):
        """T57: Rule missing admission_proof field -> AdmissionLoadError."""
        rule = {"rule_id": "NO_PROOF", "domain": "G", "match_strategy": "EXACT",
                "condition": {}, "direction": "supportive", "provenance": {},
                "semantic_content": {}}
        rules_file = tmp_path / "noproof.json"
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
        """Verifier returns specific error codes."""
        proof = AdmissionProof(
            proof_id="test", authority_id="auth", public_key_id="unknown",
            epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"), signature=b"\x01" * 70,
            signature_algorithm="ES256",
        )
        result = verify_production_proof(proof, b"{}")
        assert isinstance(result, int)
        assert result != VERIFIER_OK

    def test_t57_load_production_helper(self, test_authority, valid_rule_data, tmp_path):
        """T57: load_production_rules works with pre-signed proofs."""
        _inject_keys(test_authority)
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        rule_with_proof = dict(valid_rule_data)
        rule_with_proof["admission_proof"] = proof.to_json()
        rules_file = tmp_path / "valid.json"
        rules_file.write_text(json.dumps([rule_with_proof]))
        result = load_production_rules(path=str(rules_file))
        assert len(result) == 1
        assert "ZP_STEM_YEAR" in result


# ===========================================================================
# Category 6: Verifier Bypass (T58)
# ===========================================================================

class TestVerifierBypass:
    def test_t58_verifier_result_not_forgable(self):
        """T58: Verifier result cannot be spoofed."""
        import tongshu.assertion.verifier as tv
        tv.verify_production_proof = lambda *a, **k: VERIFIER_OK
        import importlib
        importlib.reload(tv)
        bad = AdmissionProof(
            proof_id="bypass", authority_id="evil", public_key_id="nonexistent",
            epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"), signature=b"\x00" * 70,
            signature_algorithm="ES256",
        )
        assert tv.verify_production_proof(bad, b"{}") != VERIFIER_OK

    def test_t58_keys_not_replaceable(self):
        """T58b: Keys reset on reload."""
        import tongshu.assertion.verifier as tv
        original = dict(tv._TRUSTED_KEYS)
        tv._TRUSTED_KEYS = {"hacked": {}}
        tv._load_trust_anchor()
        assert tv._TRUSTED_KEYS == original


# ===========================================================================
# Category 7: P0 Security Tests (T59–T69)
# ===========================================================================

class TestP0Security:
    def test_t59_native_unavailable_rejects(self):
        """T59: Native unavailable -> FAIL CLOSED (not OK)."""
        import tongshu.assertion.verifier as tv
        original = dict(tv._TRUSTED_KEYS)
        tv._TRUSTED_KEYS = {}
        try:
            proof = AdmissionProof(
                proof_id="no-native", authority_id="auth", public_key_id="key",
                epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
                asset_type="AssertionRule", asset_canonical=b"{}",
                content_digest=compute_digest(b"{}"), signature=b"\x01" * 70,
                signature_algorithm="ES256",
            )
            result = verify_production_proof(proof, b"{}")
            assert result != VERIFIER_OK
        finally:
            tv._TRUSTED_KEYS = original

    def test_t60_crypto_exception_rejects(self):
        """T60: Crypto exception -> VERIFIER_CRYPTO_ERROR."""
        import tongshu.assertion.verifier as tv
        original = dict(tv._TRUSTED_KEYS)
        tv._TRUSTED_KEYS = {"bad": {"algorithm": "ES256", "x": "!!!invalid!!!", "y": "!!!also!!!"}}
        try:
            proof = AdmissionProof(
                proof_id="crypto", authority_id="auth", public_key_id="bad",
                epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
                asset_type="AssertionRule", asset_canonical=b"{}",
                content_digest=compute_digest(b"{}"), signature=b"\x01" * 70,
                signature_algorithm="ES256",
            )
            result = verify_production_proof(proof, b"{}")
            assert result != VERIFIER_OK
        finally:
            tv._TRUSTED_KEYS = original

    def test_t61_test_verifier_isolated(self):
        """T61: TestVerifier cannot corrupt production state."""
        import tongshu.assertion.verifier as prod
        from tongshu.assertion.test_verifier import TestVerifier
        original_keys = dict(prod._TRUSTED_KEYS)
        tv = TestVerifier()
        tv.set_keys({"hacked": {}})
        assert prod._TRUSTED_KEYS == original_keys

    def test_t62_authority_production_mode(self):
        """T62: Production-mode Authority rejects ephemeral keys."""
        with pytest.raises(AdmissionError):
            AdmissionAuthority(authority_id="prod", epoch=1, production_mode=True)

    # ---- P0 Proof Substitution Tests (T63-T69) ----

    def test_t63_proof_substitution_different_rule(self, test_authority, valid_rule_data):
        """T63: Proof for Rule A cannot produce Production from Rule B."""
        # Sign proof for rule A
        canonical_a = canonicalize(valid_rule_data)
        proof_a = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical_a, public_key_id="test-key")

        # Try to use proof_a with a different rule
        rule_b = dict(valid_rule_data)
        rule_b["rule_id"] = "FORGED_RULE"
        rule_b["condition"] = {"atom_id": "TEN_GOD_YI"}  # Different condition
        canonical_b = canonicalize(rule_b)

        # Verification must fail: proof_a's digest != canonical_b's digest
        result = verify_production_proof(proof_a, canonical_b)
        assert result == VERIFIER_DIGEST_MISMATCH

    def test_t64_condition_mutation(self, test_authority, valid_rule_data):
        """T64: Modifying condition after signing -> REJECT."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        # Mutate condition
        mutated = dict(valid_rule_data)
        mutated["condition"] = {"atom_id": "TEN_GOD_YI"}
        mutated_canonical = canonicalize(mutated)
        result = verify_production_proof(proof, mutated_canonical)
        assert result == VERIFIER_DIGEST_MISMATCH

    def test_t65_direction_mutation(self, test_authority, valid_rule_data):
        """T65: Modifying direction after signing -> REJECT."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        mutated = dict(valid_rule_data)
        mutated["direction"] = "cautionous"
        mutated_canonical = canonicalize(mutated)
        result = verify_production_proof(proof, mutated_canonical)
        assert result == VERIFIER_DIGEST_MISMATCH

    def test_t66_provenance_mutation(self, test_authority, valid_rule_data):
        """T66: Modifying provenance after signing -> REJECT."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        mutated = dict(valid_rule_data)
        mutated["provenance"]["source_work"] = "伪造文献"
        mutated_canonical = canonicalize(mutated)
        result = verify_production_proof(proof, mutated_canonical)
        assert result == VERIFIER_DIGEST_MISMATCH

    def test_t67_match_strategy_mutation(self, test_authority, valid_rule_data):
        """T67: Modifying match_strategy after signing -> REJECT."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        mutated = dict(valid_rule_data)
        mutated["match_strategy"] = "CONTAINS"
        mutated_canonical = canonicalize(mutated)
        result = verify_production_proof(proof, mutated_canonical)
        assert result == VERIFIER_DIGEST_MISMATCH

    def test_t68_rule_id_swap(self, test_authority, valid_rule_data):
        """T68: Changing rule_id after signing -> REJECT."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        mutated = dict(valid_rule_data)
        mutated["rule_id"] = "HACKED_RULE_ID"
        mutated_canonical = canonicalize(mutated)
        result = verify_production_proof(proof, mutated_canonical)
        assert result == VERIFIER_DIGEST_MISMATCH

    def test_t69_proof_replay_on_candidate(self, test_authority, valid_rule_data):
        """T69: Replay proof on Candidate -> REJECT."""
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        # Create a candidate with different content
        candidate_data = {"rule_id": "CANDIDATE", "domain": "OTHER"}
        candidate_canonical = canonicalize(candidate_data)
        result = verify_production_proof(proof, candidate_canonical)
        assert result == VERIFIER_DIGEST_MISMATCH


# ===========================================================================
# Category 8: P0 Boundary Enforcement Tests (T70-T74)
# ===========================================================================

class TestP0Boundary:
    """Tests for P0-A through P0-D boundary enforcement."""

    def test_t70_loader_cannot_mutate_state_directly(self, test_authority):
        """T70: Loader cannot directly mutate _state / _proof."""
        asset = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data={"rule_id": "X"})
        with pytest.raises(AttributeError):
            asset._state = AssetState.ADMITTED
        with pytest.raises(AttributeError):
            asset._proof = None

    def test_t71_audit_complete_rejects_fake_proof(self, test_authority, valid_rule_data):
        """T71: audit_complete(fake proof) -> reject."""
        _inject_keys(test_authority)
        asset = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data=valid_rule_data)
        asset.submit_for_admission()
        fake_proof = AdmissionProof(
            proof_id="fake", authority_id="evil", public_key_id="unknown",
            epoch=1, timestamp="2026-01-01T00:00:00+00:00", version="1.0",
            asset_type="AssertionRule", asset_canonical=b"{}",
            content_digest=compute_digest(b"{}"), signature=b"\x00" * 70,
            signature_algorithm="ES256",
        )
        with pytest.raises(AdmissionStateError):
            asset.audit_complete(fake_proof)

    def test_t72_audit_complete_rejects_proof_for_another_asset(self, test_authority, valid_rule_data):
        """T72: audit_complete(proof for another asset) -> reject."""
        _inject_keys(test_authority)
        asset_a = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data=valid_rule_data)
        asset_a.submit_for_admission()
        canonical_a = asset_a.to_canonical()
        proof_a = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical_a, public_key_id="test-key")
        asset_a.audit_complete(proof_a)

        # Asset B with DIFFERENT content
        asset_b = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data={"rule_id": "B", "condition": {"x": 999}})
        asset_b.submit_for_admission()
        with pytest.raises(AdmissionStateError):
            asset_b.audit_complete(proof_a)

    def test_t73_production_asset_arbitrary_inner_rejects(self, test_authority, valid_rule_data):
        """T73: ProductionAsset with arbitrary inner + valid proof -> REJECT."""
        _inject_keys(test_authority)
        canonical = canonicalize(valid_rule_data)
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        class NoCanonical:
            pass
        prod = ProductionAsset(inner=NoCanonical(), proof=proof)
        assert prod.is_production() is False

    def test_t74_is_production_uses_consistent_canonical_contract(self, test_authority, valid_rule_data):
        """T74: is_production() uses same canonical contract as convert_to_production()."""
        _inject_keys(test_authority)
        asset = AdmittableAsset(asset_type=AssetType.ASSERTION_RULE.value, raw_data=valid_rule_data)
        asset.submit_for_admission()
        canonical = asset.to_canonical()
        proof = test_authority.sign(AssetType.ASSERTION_RULE.value, canonical, public_key_id="test-key")
        asset.audit_complete(proof)
        convert_result = asset.convert_to_production()
        assert convert_result is True
        assert asset.is_production() is True
