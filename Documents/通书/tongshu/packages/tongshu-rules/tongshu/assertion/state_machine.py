"""
Production Admission Governance — State Machine

Strict state transitions for Production Admission.

States: CANDIDATE → UNDER_REVIEW → ADMITTED → PRODUCTION
FORBIDDEN:  CANDIDATE → PRODUCTION (direct bypass)

AdmittableAsset enforces that state transitions go through explicit methods.
Direct state mutation is impossible via the public API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .canonicalizer import canonicalize
from .exceptions import AdmissionStateError
from .models import AssetState, AdmissionProof
from .verifier import verify_production_proof, VERIFIER_OK


@dataclass
class AdmittableAsset:
    """
    Asset with strict state machine enforcement.

    All state transitions go through explicit methods.
    Direct state mutation via _state assignment is NOT supported
    from outside this class.
    """

    asset_type: str
    raw_data: dict[str, Any]
    _state: AssetState = field(default=AssetState.CANDIDATE, repr=False)
    _proof: Optional[AdmissionProof] = field(default=None, repr=False)

    @property
    def state(self) -> AssetState:
        return self._state

    @property
    def proof(self) -> Optional[AdmissionProof]:
        return self._proof

    def submit_for_admission(self) -> None:
        """CANDIDATE → UNDER_REVIEW"""
        if self._state != AssetState.CANDIDATE:
            raise AdmissionStateError(
                f"Cannot submit: asset is in state {self._state.value}, "
                f"expected CANDIDATE"
            )
        self._state = AssetState.UNDER_REVIEW

    def audit_complete(self, proof: AdmissionProof) -> None:
        """UNDER_REVIEW → ADMITTED (requires valid proof from Authority)."""
        if self._state != AssetState.UNDER_REVIEW:
            raise AdmissionStateError(
                f"Cannot complete audit: asset is in state {self._state.value}, "
                f"expected UNDER_REVIEW"
            )
        if proof is None:
            raise AdmissionStateError("Cannot admit without a proof")
        self._proof = proof
        self._state = AssetState.ADMITTED

    def fail_review(self) -> None:
        """UNDER_REVIEW → CANDIDATE (audit failed)."""
        if self._state != AssetState.UNDER_REVIEW:
            raise AdmissionStateError(
                f"Cannot fail review: asset is in state {self._state.value}, "
                f"expected UNDER_REVIEW"
            )
        self._state = AssetState.CANDIDATE
        self._proof = None

    def convert_to_production(self) -> bool:
        """
        ADMITTED → PRODUCTION (requires Trusted Verifier check).

        P0 FIX: This NOW requires re-verifying that the proof binds
        to the CURRENT asset content (not just that the proof is self-consistent).
        """
        if self._state != AssetState.ADMITTED:
            raise AdmissionStateError(
                f"Cannot convert to production: asset is in state "
                f"{self._state.value}, expected ADMITTED"
            )
        if self._proof is None:
            raise AdmissionStateError(
                "Cannot convert to production: no admission proof"
            )

        # P0 FIX: Re-canonicalize current asset (excluding admission_proof)
        # and verify proof binds to it
        current_canonical = self.to_canonical_for_verify()
        result = verify_production_proof(self._proof, current_canonical)

        if result == VERIFIER_OK:
            self._state = AssetState.PRODUCTION
            return True
        return False

    def revoke(self) -> None:
        """ADMITTED → REVOKED"""
        if self._state != AssetState.ADMITTED:
            raise AdmissionStateError(
                f"Cannot revoke: asset is in state {self._state.value}, "
                f"expected ADMITTED"
            )
        self._state = AssetState.REVOKED
        self._proof = None

    def is_production(self) -> bool:
        """Check if this asset has valid Production identity."""
        if self._state != AssetState.PRODUCTION:
            return False
        if self._proof is None:
            return False
        current_canonical = canonicalize(self.raw_data)
        return verify_production_proof(self._proof, current_canonical) == VERIFIER_OK

    def to_canonical(self) -> bytes:
        return canonicalize(self.raw_data)

    def to_canonical_for_verify(self) -> bytes:
        """
        Canonicalize raw_data for verification, excluding admission_proof.
        The proof was signed over the rule_data WITHOUT the admission_proof field.
        """
        data_for_verify = {k: v for k, v in self.raw_data.items() if k != "admission_proof"}
        return canonicalize(data_for_verify)
