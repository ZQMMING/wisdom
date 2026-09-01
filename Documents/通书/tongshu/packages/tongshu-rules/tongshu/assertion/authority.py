"""
Production Admission Governance — Admission Authority (Zone 2)

The Authority:
  1. Receives candidate assets from Zone 1
  2. Canonicalizes their content deterministically
  3. Computes SHA-256 digest
  4. Signs with ECDSA P-256 (private key)
  5. Issues AdmissionProof

The private key NEVER enters the Python runtime in production.
For testing, a test key pair is generated on demand.
"""

from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone
from typing import Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from .canonicalizer import canonicalize
from .models import AdmissionProof, AssetType
from .exceptions import AdmissionError


class AdmissionAuthority:
    """
    Signs admission proofs for candidate assets.

    In production, this runs in Zone 2 (offline, air-gapped).
    The private key is never exposed to Zone 1.
    """

    def __init__(
        self,
        authority_id: str,
        private_key: Optional[ec.EllipticCurvePrivateKey] = None,
        public_key: Optional[ec.EllipticCurvePublicKey] = None,
        epoch: int = 1,
    ) -> None:
        self.authority_id = authority_id
        self.epoch = epoch

        if private_key is not None and public_key is not None:
            self._private_key = private_key
            self._public_key = public_key
        else:
            # Generate ephemeral key pair (for testing / initial setup)
            self._private_key = ec.generate_private_key(ec.SECP256R1())
            self._public_key = self._private_key.public_key()

    @property
    def public_key_info(self) -> dict:
        """Extract public key info for trust anchor distribution."""
        pub = self._public_key
        pub_nums = pub.public_numbers()
        return {
            "algorithm": "ES256",
            "x": base64.b64encode(pub_nums.x.to_bytes(32, "big")).decode("ascii"),
            "y": base64.b64encode(pub_nums.y.to_bytes(32, "big")).decode("ascii"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "revoked_at": None,
            "epoch": self.epoch,
        }

    def sign(
        self,
        asset_type: str,
        asset_canonical: bytes,
        public_key_id: str = "default",
    ) -> AdmissionProof:
        """
        Sign a candidate asset and issue an AdmissionProof.

        This is the Authority's core operation:
          canonical_content -> SHA-256 -> ECDSA P-256 signature -> Proof
        """
        import hashlib
        digest = hashlib.sha256(asset_canonical).digest()
        proof = AdmissionProof.create(
            authority_id=self.authority_id,
            public_key_id=public_key_id,
            epoch=self.epoch,
            asset_type=asset_type,
            asset_canonical=asset_canonical,
            signature=self._private_key.sign(
                digest,
                ec.ECDSA(hashes.SHA256()),
            ),
        )
        return proof

    def sign_from_data(
        self,
        asset_type: str,
        raw_data: dict,
        public_key_id: str = "default",
    ) -> AdmissionProof:
        """Convenience: canonicalize then sign."""
        canonical = canonicalize(raw_data)
        return self.sign(asset_type, canonical, public_key_id)


def generate_test_authority(
    authority_id: str = "test-authority",
    epoch: int = 1,
) -> tuple[AdmissionAuthority, str]:
    """
    Generate a test authority and return (authority, public_key_id).
    The public key info must be distributed to the verifier's trust anchor.
    """
    auth = AdmissionAuthority(
        authority_id=authority_id,
        epoch=epoch,
    )
    return auth, "test-key"
