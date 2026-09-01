"""
Production Admission Governance — Test Verifier

This module provides test-only verification helpers.
It is SEPARATE from the production verifier to enforce P0-3:
  Production code NEVER has access to test injection capabilities.

Usage (tests only):
  from tongshu.assertion.test_verifier import (
      TestVerifier,
      generate_test_keys,
  )

DO NOT import this module in production code.
"""

from __future__ import annotations

from typing import Optional

from .models import AdmissionProof
from .verifier import (
    VERIFIER_OK,
    VERIFIER_SIGNATURE_INVALID,
    VERIFIER_DIGEST_MISMATCH,
    VERIFIER_REVOKED,
    VERIFIER_EPOCH_EXPIRED,
    VERIFIER_SCHEMA_ERROR,
    VERIFIER_KEY_UNKNOWN,
    VERIFIER_CRYPTO_ERROR,
    _in_process_verify,
)


class TestVerifier:
    """
    Test-only verifier that allows injecting trust anchor data.

    This class EXISTS ONLY for testing. Production code must NOT use it.
    It configures the production verifier's internal state for test scenarios.
    """

    def __init__(
        self,
        keys: Optional[dict[str, dict]] = None,
        epoch: int = 1,
        revocation_list: Optional[list[str]] = None,
    ) -> None:
        self._keys = keys or {}
        self._epoch = epoch
        self._revoked = set(revocation_list or [])

    def verify(self, proof: AdmissionProof) -> int:
        """Verify a proof using injected test keys."""
        return _in_process_verify_with(proof, self._keys, self._epoch, self._revoked)

    def mark_revoked(self, proof_id: str) -> None:
        self._revoked.add(proof_id)

    def set_epoch(self, epoch: int) -> None:
        self._epoch = epoch

    def set_keys(self, keys: dict[str, dict]) -> None:
        self._keys = keys

    def inject_into_production(self) -> None:
        """
        Inject test keys into production verifier state.
        Called by tests before running production verification paths.
        MUST NOT be called in production code.
        """
        import tongshu.assertion.verifier as prod_tv
        prod_tv._TRUSTED_KEYS = self._keys
        prod_tv._CURRENT_EPOCH = self._epoch
        prod_tv._REVOCATION_LIST = self._revoked

    def restore_from_production(self) -> None:
        """Restore production verifier state after test."""
        import tongshu.assertion.verifier as prod_tv
        prod_tv._load_trust_anchor()


def _in_process_verify_with(
    proof: AdmissionProof,
    keys: dict[str, dict],
    epoch: int,
    revoked: set[str],
) -> int:
    """
    Internal in-process verification using provided trust anchor.
    Used by TestVerifier. NOT exposed as public API.
    """
    # Schema checks
    if not proof.verify_self_integrity():
        return VERIFIER_DIGEST_MISMATCH

    if proof.version != "1.0":
        return VERIFIER_SCHEMA_ERROR

    if proof.signature_algorithm != "ES256":
        return VERIFIER_SCHEMA_ERROR

    if not proof.signature or len(proof.signature) == 0:
        return VERIFIER_SIGNATURE_INVALID

    # Key lookup
    if proof.public_key_id not in keys:
        return VERIFIER_KEY_UNKNOWN

    key_data = keys[proof.public_key_id]
    if not key_data:
        return VERIFIER_KEY_UNKNOWN

    # Epoch check
    if proof.epoch > epoch:
        return VERIFIER_EPOCH_EXPIRED
    if proof.epoch < 1:
        return VERIFIER_EPOCH_EXPIRED

    # Revocation check
    if proof.proof_id in revoked:
        return VERIFIER_REVOKED

    # Signature verification — FAIL CLOSED on ANY exception
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.exceptions import InvalidSignature

        x_bytes = _decode_coord(key_data.get("x", ""))
        y_bytes = _decode_coord(key_data.get("y", ""))
        if not (x_bytes and y_bytes and len(x_bytes) == 32 and len(y_bytes) == 32):
            return VERIFIER_KEY_UNKNOWN

        public_key = ec.EllipticCurvePublicNumbers(
            x=int.from_bytes(x_bytes, "big"),
            y=int.from_bytes(y_bytes, "big"),
            curve=ec.SECP256R1(),
        ).public_key()

        digest = bytes.fromhex(proof.content_digest)
        public_key.verify(proof.signature, digest, ec.ECDSA(hashes.SHA256()))
        return VERIFIER_OK

    except InvalidSignature:
        return VERIFIER_SIGNATURE_INVALID
    except Exception:
        return VERIFIER_CRYPTO_ERROR


def _decode_coord(s: str) -> bytes:
    """Decode a coordinate that may be base64 or hex encoded."""
    if not s:
        return b""
    import base64
    b = _b64decode(s)
    if len(b) == 32:
        return b
    try:
        h = bytes.fromhex(s)
        if len(h) == 32:
            return h
    except ValueError:
        pass
    return b""


def _b64decode(s: str) -> bytes:
    import base64
    try:
        return base64.b64decode(s)
    except Exception:
        return b""


def generate_test_keys() -> tuple[dict[str, dict], AdmissionProof]:
    """
    Generate a test key pair and return (keys_dict, proof_with_key_ref).
    Used by tests to create verifiable proofs.
    """
    from .authority import AdmissionAuthority

    auth = AdmissionAuthority(authority_id="test-authority", epoch=1)
    pub_info = auth.public_key_info
    keys = {"test-key": pub_info}
    return keys, auth
