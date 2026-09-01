"""
Production Admission Governance — Data Models

Core types:
  - AdmissionProof: self-contained cryptographic credential
  - CandidateAsset: unstructured output from Zone 1
  - ProductionAsset: verified output from Zone 3/4
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from .exceptions import AdmissionError


class AssetState(str, Enum):
    """Strict state machine states."""
    CANDIDATE = "CANDIDATE"
    UNDER_REVIEW = "UNDER_REVIEW"
    ADMITTED = "ADMITTED"
    REVOKED = "REVOKED"
    PRODUCTION = "PRODUCTION"


class AssetType(str, Enum):
    ASSERTION_RULE = "AssertionRule"
    ENGINE_EVIDENCE = "EngineEvidence"
    CANDIDATE_ASSERTION = "CandidateAssertion"


SIGNATURE_ALGORITHM = "ES256"
PROOF_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class AdmissionProof:
    """
    Cryptographic proof that an asset has passed Production Admission.

    This is NOT a Python type guard. It is a self-contained,
    verifiable, tamper-evident credential.

    The proof binds to the asset's canonical content via SHA-256 + ECDSA P-256.
    Verification requires calling the Trusted Verifier (Zone 3/4).
    """

    proof_id: str
    authority_id: str
    public_key_id: str
    epoch: int
    timestamp: str  # ISO 8601
    version: str
    asset_type: str
    asset_canonical: bytes  # deterministic JSON serialization
    content_digest: str  # SHA-256 hex of asset_canonical
    signature: bytes  # ECDSA P-256 signature (64 bytes)
    signature_algorithm: str

    @classmethod
    def create(
        cls,
        authority_id: str,
        public_key_id: str,
        epoch: int,
        asset_type: str,
        asset_canonical: bytes,
        signature: bytes,
    ) -> "AdmissionProof":
        content_digest = hashlib.sha256(asset_canonical).hexdigest()
        return cls(
            proof_id=str(uuid.uuid4()),
            authority_id=authority_id,
            public_key_id=public_key_id,
            epoch=epoch,
            timestamp=datetime.now(timezone.utc).isoformat(),
            version=PROOF_SCHEMA_VERSION,
            asset_type=asset_type,
            asset_canonical=asset_canonical,
            content_digest=content_digest,
            signature=signature,
            signature_algorithm=SIGNATURE_ALGORITHM,
        )

    def to_json(self) -> str:
        return json.dumps(
            {
                "proof_id": self.proof_id,
                "authority_id": self.authority_id,
                "public_key_id": self.public_key_id,
                "epoch": self.epoch,
                "timestamp": self.timestamp,
                "version": self.version,
                "asset_type": self.asset_type,
                "asset_canonical": self.asset_canonical.decode("utf-8"),
                "content_digest": self.content_digest,
                "signature": self.signature.hex(),
                "signature_algorithm": self.signature_algorithm,
            },
            ensure_ascii=False,
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AdmissionProof":
        data = json.loads(json_str)
        return cls(
            proof_id=data["proof_id"],
            authority_id=data["authority_id"],
            public_key_id=data["public_key_id"],
            epoch=data["epoch"],
            timestamp=data["timestamp"],
            version=data["version"],
            asset_type=data["asset_type"],
            asset_canonical=data["asset_canonical"].encode("utf-8"),
            content_digest=data["content_digest"],
            signature=bytes.fromhex(data["signature"]),
            signature_algorithm=data["signature_algorithm"],
        )

    def verify_self_integrity(self) -> bool:
        """Quick local check: does content_digest match asset_canonical?"""
        return hashlib.sha256(self.asset_canonical).hexdigest() == self.content_digest


@dataclass
class CandidateAsset:
    """
    Raw output from Zone 1 (Application Runtime).

    Nothing in this object confers Production identity.
    It must go through submit_for_admission() → Trusted Verifier.
    """

    asset_type: str
    raw_data: dict[str, Any]
    state: AssetState = field(default=AssetState.CANDIDATE, repr=False)
    admission_proof: Optional[AdmissionProof] = field(default=None, repr=False)

    def submit_for_admission(self) -> None:
        if self.state != AssetState.CANDIDATE:
            raise ValueError(
                f"Cannot submit asset in state {self.state.value} for admission"
            )
        self.state = AssetState.UNDER_REVIEW

    def mark_admitted(self, proof: AdmissionProof) -> None:
        if self.state != AssetState.UNDER_REVIEW:
            raise ValueError(
                f"Cannot mark admitted: asset is in state {self.state.value}"
            )
        self.admission_proof = proof
        self.state = AssetState.ADMITTED

    def mark_revoked(self) -> None:
        if self.state != AssetState.ADMITTED:
            raise ValueError(
                f"Cannot revoke: asset is in state {self.state.value}"
            )
        self.state = AssetState.REVOKED
        self.admission_proof = None

    def to_canonical(self) -> bytes:
        return _canonicalize(self.raw_data)


@dataclass
class ProductionAsset:
    """
    Wrapper that holds an asset ONLY when the Trusted Verifier has
    confirmed its AdmissionProof.

    Production identity is NOT a Python class. It is the RESULT of:
        trusted_verifier.verify_production_proof(proof) == VERIFIER_OK

    This class enforces that rule by making is_production() call the verifier.
    """

    inner: Any  # the underlying asset (rule, evidence, etc.)
    proof: AdmissionProof

    def is_production(self) -> bool:
        """
        CRITICAL: This ALWAYS calls the Trusted Verifier.
        There is no attribute check, no cached boolean.
        Zone 1 cannot forge Production identity by setting any flag.
        """
        if self.proof is None:
            return False
        from .verifier import verify_production_proof
        # Attempt to get canonical form from inner if it has one
        if hasattr(self.inner, "to_canonical"):
            current_canonical = self.inner.to_canonical()
        elif hasattr(self.inner, "raw_data"):
            from .canonicalizer import canonicalize
            current_canonical = canonicalize(self.inner.raw_data)
        else:
            current_canonical = self.proof.asset_canonical
        result = verify_production_proof(self.proof, current_canonical)
        return result == 0  # VERIFIER_OK

    def to_dict(self) -> dict[str, Any]:
        if not self.is_production():
            raise ProductionAccessError(
                "Cannot access ProductionAsset: verification failed"
            )
        if hasattr(self.inner, "to_dict"):
            return self.inner.to_dict()
        return self.inner
