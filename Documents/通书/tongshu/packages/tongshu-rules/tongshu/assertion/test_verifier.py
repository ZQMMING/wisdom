"""
Production Admission Governance — Test Verifier

Test-only verifier. Uses in-process _verify_proof() directly.
Requires EXPLICIT activate() to inject into production path.
Never touches production module internals without activation.
"""

from __future__ import annotations

from typing import Optional

from .models import AdmissionProof
from .verifier import _verify_proof


class TestVerifier:
    """
    Test-only verifier. Injects trust anchor directly via _verify_proof().
    
    Requires explicit activate()/deactivate() to toggle between
    in-process test path and subprocess production path.
    
    NEVER modifies production module state without explicit activation.
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
        self._hook_active = False

    def activate(self) -> None:
        """Activate test hook — production verify_production_proof() routes through here."""
        # NOTE: This modifies production module state. Must be called explicitly.
        import tongshu.assertion.verifier as prod
        prod._test_verifier_hook = self._verify_wrapper
        self._hook_active = True

    def deactivate(self) -> None:
        """Deactivate test hook — restores subprocess path."""
        if self._hook_active:
            import tongshu.assertion.verifier as prod
            prod._test_verifier_hook = None
            self._hook_active = False

    def _verify_wrapper(self, proof: AdmissionProof, current_canonical: bytes) -> int:
        return _verify_proof(proof, current_canonical, self._keys, self._epoch, self._revoked)

    def verify(self, proof: AdmissionProof, current_canonical: bytes) -> int:
        """Verify via in-process path (test only, NOT production)."""
        return _verify_proof(proof, current_canonical, self._keys, self._epoch, self._revoked)

    def verify_proof_only(self, proof: AdmissionProof) -> int:
        """Verify proof self-integrity only (no asset binding)."""
        return _verify_proof(proof, proof.asset_canonical, self._keys, self._epoch, self._revoked)

    def mark_revoked(self, proof_id: str) -> None:
        self._revoked.add(proof_id)

    def unmark_revoked(self, proof_id: str) -> None:
        self._revoked.discard(proof_id)

    def set_epoch(self, epoch: int) -> None:
        self._epoch = epoch

    def set_keys(self, keys: dict[str, dict]) -> None:
        self._keys = keys

    def add_revoked(self, proof_ids: list[str]) -> None:
        self._revoked.update(proof_ids)

    def clear_revoked(self) -> None:
        self._revoked.clear()


def generate_test_keys() -> tuple[dict[str, dict], object]:
    """Generate test keys and a sample authority."""
    from .authority import AdmissionAuthority
    auth = AdmissionAuthority(authority_id="test-authority", epoch=1)
    pub_info = auth.public_key_info
    keys = {"test-key": pub_info}
    return keys, auth
