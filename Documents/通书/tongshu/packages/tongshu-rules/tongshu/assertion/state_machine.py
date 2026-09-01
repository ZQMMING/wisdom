"""
Production Admission Governance — Strict State Machine

Transitions:
  CANDIDATE      -> UNDER_REVIEW   (submit_for_admission)
  UNDER_REVIEW   -> ADMITTED       (audit_complete + sign)
  UNDER_REVIEW   -> CANDIDATE      (fail_review)
  ADMITTED       -> REVOKED        (revoke)
  ADMITTED       -> PRODUCTION     (convert_to_production, via Trusted Verifier)

FORBIDDEN:
  CANDIDATE      -> PRODUCTION     (direct bypass)
  Any            -> CANDIDATE      (except from UNDER_REVIEW via fail_review)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .exceptions import AdmissionStateError
from .models import AssetState, AdmissionProof


_VALID_TRANSITIONS = {
    AssetState.CANDIDATE: {AssetState.UNDER_REVIEW},
    AssetState.UNDER_REVIEW: {AssetState.ADMITTED, AssetState.CANDIDATE},
    AssetState.ADMITTED: {AssetState.REVOKED, AssetState.PRODUCTION},
    AssetState.REVOKED: set(),
    AssetState.PRODUCTION: set(),
}


@dataclass
class AdmittableAsset:
    """
    Asset with strict state machine enforcement.

    All state transitions go through this class. Direct state mutation
    is impossible — use the transition methods.
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
        """CANDIDATE -> UNDER_REVIEW"""
        if self._state != AssetState.CANDIDATE:
            raise AdmissionStateError(
                f"Cannot submit: asset is in state {self._state.value}, "
                f"expected CANDIDATE"
            )
        self._state = AssetState.UNDER_REVIEW

    def audit_complete(self, proof: AdmissionProof) -> None:
        """UNDER_REVIEW -> ADMITTED (requires valid proof from Authority)"""
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
        """UNDER_REVIEW -> CANDIDATE (audit failed)"""
        if self._state != AssetState.UNDER_REVIEW:
            raise AdmissionStateError(
                f"Cannot fail review: asset is in state {self._state.value}, "
                f"expected UNDER_REVIEW"
            )
        self._state = AssetState.CANDIDATE
        self._proof = None

    def convert_to_production(self) -> bool:
        """
        ADMITTED -> PRODUCTION (requires Trusted Verifier check).

        Returns True if verification passes, False otherwise.
        This is the ONLY path to PRODUCTION.
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

        from .verifier import verify_production_proof

        result = verify_production_proof(self._proof)
        if result == 0:  # VERIFIER_OK
            self._state = AssetState.PRODUCTION
            return True
        return False

    def revoke(self) -> None:
        """ADMITTED -> REVOKED"""
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
        from .verifier import verify_production_proof
        return verify_production_proof(self._proof) == 0

    def to_canonical(self) -> bytes:
        from .canonicalizer import canonicalize
        return canonicalize(self.raw_data)
