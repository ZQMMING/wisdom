"""
Production Admission Governance — Admission Authority (Zone 2)

The Authority:
  1. Receives candidate assets from Zone 1
  2. Canonicalizes their content deterministically
  3. Computes SHA-256 digest
  4. Signs with ECDSA P-256 (private key)
  5. Issues AdmissionProof

PRODUCTION CONSTRAINT (P0-4):
  In production, this class MUST NEVER run in Zone 1 (application runtime).
  The private key must only exist in Zone 2 (offline/air-gapped).

  For testing, a separate test utility creates ephemeral keys.
  Production code should receive pre-signed proofs, never call sign().
"""

from __future__ import annotations

import base64
import hashlib
from datetime import datetime, timezone
from typing import Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from .canonicalizer import canonicalize
from .models import AdmissionProof, AssetType
from .exceptions import AdmissionError


class AdmissionAuthority:
    """
    Signs admission proofs for candidate assets.

    PRODUCTION NOTE:
      This class MUST NOT be instantiated in Zone 1 (application runtime).
      The private key must only exist in Zone 2 (offline/air-gapped).
      Production code receives pre-signed AdmissionProof objects, not
      AdmissionAuthority instances.

    For testing only, ephemeral key pairs can be generated.
    """

    def __init__(
        self,
        authority_id: str,
        private_key: Optional[ec.EllipticCurvePrivateKey] = None,
        public_key: Optional[ec.EllipticCurvePublicKey] = None,
        epoch: int = 1,
        production_mode: bool = False,
    ) -> None:
        self.authority_id = authority_id
        self.epoch = epoch
        self._production_mode = production_mode

        if production_mode:
            # In production mode, private key MUST be provided externally
            # (loaded from HSM/secure storage in Zone 2)
            if private_key is None:
                raise AdmissionError(
                    "Production Authority requires an externally-provided private key. "
                    "Ephemeral key generation is FORBIDDEN in production mode."
                )
            if public_key is None:
                raise AdmissionError(
                    "Production Authority requires an externally-provided public key."
                )
        else:
            # Test mode: allow ephemeral key generation
            if private_key is not None and public_key is not None:
                self._private_key = private_key
                self._public_key = public_key
            else:
                self._private_key = ec.generate_private_key(ec.SECP256R1())
                self._public_key = self._private_key.public_key()

    @property
    def is_production_mode(self) -> bool:
        return self._production_mode

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

        PRODUCTION NOTE:
          This method MUST NOT be called from Zone 1 in production.
          Sign operations must occur exclusively in Zone 2.
        """
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
    Generate a TEST authority only.
    Returns (authority, public_key_id).
    DO NOT use this in production code.
    """
    auth = AdmissionAuthority(
        authority_id=authority_id,
        epoch=epoch,
        production_mode=False,
    )
    return auth, "test-key"
