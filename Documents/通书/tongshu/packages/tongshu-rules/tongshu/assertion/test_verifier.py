"""
Production Admission Governance — Test Verifier

Test-only verification helpers. SEPARATE from production verifier.
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
    _verify_proof_against_asset,
)


class TestVerifier:
    """
    Test-only verifier that allows injecting trust anchor data.
    Used to configure production verifier state for integration tests.
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

    def verify(self, proof: AdmissionProof, current_canonical: bytes) -> int:
        """Verify a proof against current asset canonical bytes."""
        return _verify_proof_against_asset(
            proof, current_canonical,
            self._keys, self._epoch, self._revoked,
        )

    def verify_proof_only(self, proof: AdmissionProof) -> int:
        """Verify proof self-integrity only (no asset binding)."""
        return _verify_proof_against_asset(
            proof, proof.asset_canonical,
            self._keys, self._epoch, self._revoked,
        )

    def mark_revoked(self, proof_id: str) -> None:
        self._revoked.add(proof_id)

    def set_epoch(self, epoch: int) -> None:
        self._epoch = epoch

    def set_keys(self, keys: dict[str, dict]) -> None:
        self._keys = keys

    def inject_into_production(self) -> None:
        """Inject test keys into production verifier state."""
        import tongshu.assertion.verifier as prod_tv
        prod_tv._TRUSTED_KEYS = self._keys
        prod_tv._CURRENT_EPOCH = self._epoch
        prod_tv._REVOCATION_LIST = self._revoked

    def restore_from_production(self) -> None:
        """Restore production verifier state after test."""
        import tongshu.assertion.verifier as prod_tv
        prod_tv._load_trust_anchor()


def generate_test_keys() -> tuple[dict[str, dict], AdmissionProof]:
    """Generate test keys and a sample proof."""
    from .authority import AdmissionAuthority

    auth = AdmissionAuthority(authority_id="test-authority", epoch=1)
    pub_info = auth.public_key_info
    keys = {"test-key": pub_info}
    return keys, auth
