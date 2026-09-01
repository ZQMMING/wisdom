"""
Production Admission Governance — State Machine

Strict state transitions for Production Admission.

States: CANDIDATE → UNDER_REVIEW → ADMITTED → PRODUCTION
FORBIDDEN:  CANDIDATE → PRODUCTION (direct bypass)

AdmittableAsset enforces that state transitions go through explicit methods.
Direct _state / _proof mutation is blocked via property setters.
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
    Direct state mutation via _state / _proof assignment is BLOCKED
    by property setters.
    """

    asset_type: str
    raw_data: dict[str, Any]
    # Dataclass fields — initialized in __init__ via object.__setattr__
    _state: AssetState = field(default=AssetState.CANDIDATE, repr=False)
    _proof: Optional[AdmissionProof] = field(default=None, repr=False)

    @property
    def state(self) -> AssetState:
        return self._state

    @property
    def proof(self) -> Optional[AdmissionProof]:
        return self._proof

    # ---- Protected setters: block direct mutation ----
    @property
    def _state_setter(self):
        """Property to enforce protected write."""
        return self._state

    @property
    def _proof_setter(self):
        """Property to enforce protected write."""
        return self._proof

    def __init__(self, asset_type: str, raw_data: dict[str, Any]) -> None:
        # Initialize dataclass fields via object.__setattr__ (bypasses property check)
        object.__setattr__(self, "_state", AssetState.CANDIDATE)
        object.__setattr__(self, "_proof", None)
        object.__setattr__(self, "asset_type", asset_type)
        object.__setattr__(self, "raw_data", raw_data)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("_state", "_proof"):
            raise AttributeError(
                f"Cannot set {name} directly. "
                f"Use official state transition methods: "
                f"submit_for_admission(), audit_complete(), convert_to_production(), revoke()"
            )
        super().__setattr__(name, value)

    def submit_for_admission(self) -> None:
        """CANDIDATE → UNDER_REVIEW"""
        if self._state != AssetState.CANDIDATE:
            raise AdmissionStateError(
                f"Cannot submit: asset is in state {self._state.value}, "
                f"expected CANDIDATE"
            )
        object.__setattr__(self, "_state", AssetState.UNDER_REVIEW)

    def audit_complete(self, proof: AdmissionProof, current_canonical: Optional[bytes] = None) -> None:
        """
        UNDER_REVIEW → ADMITTED (requires valid proof from Authority).

        P0-B: Verifies that the proof binds to the current asset content.
        If current_canonical is not provided, derives it from self.raw_data.
        """
        if self._state != AssetState.UNDER_REVIEW:
            raise AdmissionStateError(
                f"Cannot complete audit: asset is in state {self._state.value}, "
                f"expected UNDER_REVIEW"
            )
        if proof is None:
            raise AdmissionStateError("Cannot admit without a proof")

        # Derive current_canonical if not provided
        if current_canonical is None:
            current_canonical = self.to_canonical_for_verify()

        # P0-B: Verify proof binds to current asset content
        result = verify_production_proof(proof, current_canonical)
        if result != VERIFIER_OK:
            raise AdmissionStateError(
                f"Proof does not bind to asset content "
                f"(verification failed, code={result})"
            )

        object.__setattr__(self, "_proof", proof)
        object.__setattr__(self, "_state", AssetState.ADMITTED)

    def fail_review(self) -> None:
        """UNDER_REVIEW → CANDIDATE (audit failed)."""
        if self._state != AssetState.UNDER_REVIEW:
            raise AdmissionStateError(
                f"Cannot fail review: asset is in state {self._state.value}, "
                f"expected UNDER_REVIEW"
            )
        object.__setattr__(self, "_state", AssetState.CANDIDATE)
        object.__setattr__(self, "_proof", None)

    def convert_to_production(self) -> bool:
        """
        ADMITTED → PRODUCTION (requires Trusted Verifier check).

        P0-D: Uses consistent canonicalization contract.
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

        # P0-D: Use consistent canonicalization contract
        current_canonical = self.to_canonical_for_verify()
        result = verify_production_proof(self._proof, current_canonical)

        if result == VERIFIER_OK:
            object.__setattr__(self, "_state", AssetState.PRODUCTION)
            return True
        return False

    def revoke(self) -> None:
        """ADMITTED → REVOKED"""
        if self._state != AssetState.ADMITTED:
            raise AdmissionStateError(
                f"Cannot revoke: asset is in state {self._state.value}, "
                f"expected ADMITTED"
            )
        object.__setattr__(self, "_state", AssetState.REVOKED)
        object.__setattr__(self, "_proof", None)

    def is_production(self) -> bool:
        """Check if this asset has valid Production identity."""
        if self._state != AssetState.PRODUCTION:
            return False
        if self._proof is None:
            return False
        # P0-D: Use same canonicalization contract as convert_to_production()
        current_canonical = self.to_canonical_for_verify()
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
