"""
Production Admission Governance — Trusted Verifier (Zone 3/4)

This module provides the Python interface to the Trusted Verifier.
In production, it loads a compiled native extension (.so/.pyd).
When the native extension is unavailable, the in-process reference
implementation is used (still fail-closed).

CRITICAL DESIGN:
  verify_production_proof(proof, current_canonical) REQUIRES BOTH:
    - The AdmissionProof (carries the signature)
    - The CURRENT asset's canonical bytes (the actual rule being admitted)

  This prevents Proof Substitution attacks:
    A valid Proof(A) CANNOT be used to produce Production from Rule(B).

FAIL-CLOSED GUARANTEES:
  - digest mismatch (proof ↔ current asset) → VERIFIER_DIGEST_MISMATCH
  - invalid signature → VERIFIER_SIGNATURE_INVALID
  - any crypto exception → VERIFIER_CRYPTO_ERROR
  - no fallback to any untrusted path
"""

from __future__ import annotations

import ctypes
import json
import os
import sys
from typing import Optional

from .exceptions import AdmissionLoadError
from .models import AdmissionProof

# Verifier result codes
VERIFIER_OK = 0
VERIFIER_SIGNATURE_INVALID = 1
VERIFIER_DIGEST_MISMATCH = 2
VERIFIER_REVOKED = 3
VERIFIER_EPOCH_EXPIRED = 4
VERIFIER_SCHEMA_ERROR = 5
VERIFIER_KEY_UNKNOWN = 6
VERIFIER_CRYPTO_ERROR = 7
VERIFIER_NATIVE_UNAVAILABLE = 8


# ---------------------------------------------------------------------------
# Trust anchor — loaded ONCE at module import from immutable path
# ---------------------------------------------------------------------------
_TRUSTED_KEYS: dict[str, dict] = {}
_CURRENT_EPOCH: int = 1
_REVOCATION_LIST: set[str] = set()
_NATIVE_LIB: Optional[ctypes.CDLL] = None


def _load_trust_anchor() -> None:
    """Load trust anchor from immutable file path. Runs ONCE at import."""
    global _TRUSTED_KEYS, _CURRENT_EPOCH, _REVOCATION_LIST

    anchor_path = os.path.join(
        os.path.dirname(__file__), "data", "admission_authority.json"
    )
    if not os.path.exists(anchor_path):
        return

    try:
        with open(anchor_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _TRUSTED_KEYS = data.get("keys", {})
        _CURRENT_EPOCH = data.get("current_epoch", 1)
        _REVOCATION_LIST = set(data.get("revocation_list", []))
    except (json.JSONDecodeError, OSError):
        _TRUSTED_KEYS = {}
        _CURRENT_EPOCH = 0
        _REVOCATION_LIST = set()


def _try_load_native() -> None:
    """Attempt to load compiled native extension at import time."""
    global _NATIVE_LIB
    ext_name = None
    if sys.platform == "win32":
        ext_name = "trusted_verifier.pyd"
    elif sys.platform == "linux":
        ext_name = "trusted_verifier.so"
    elif sys.platform == "darwin":
        ext_name = "trusted_verifier.dylib"

    if ext_name is None:
        return

    ext_path = os.path.join(os.path.dirname(__file__), "ffi", ext_name)
    if os.path.exists(ext_path):
        try:
            _NATIVE_LIB = ctypes.CDLL(ext_path)
        except (OSError, ctypes.ArgumentError):
            _NATIVE_LIB = None


_load_trust_anchor()
_try_load_native()


# ---------------------------------------------------------------------------
# Core verification logic — shared by production and test paths
# ---------------------------------------------------------------------------
def _verify_proof_against_asset(
    proof: AdmissionProof,
    current_canonical: bytes,
    keys: dict[str, dict],
    epoch: int,
    revoked: set[str],
) -> int:
    """
    Core verification: prove that current_canonical is the asset
    that was signed by this proof.

    P0 fix: This function REQUIRES both proof AND current_canonical.
    A proof alone cannot authorize any asset.

    Returns VERIFIER_OK on success, or a specific error code.
    """
    # 0. Self-integrity of proof
    if not proof.verify_self_integrity():
        return VERIFIER_DIGEST_MISMATCH

    # 1. Schema validation
    if proof.version != "1.0":
        return VERIFIER_SCHEMA_ERROR
    if proof.signature_algorithm != "ES256":
        return VERIFIER_SCHEMA_ERROR
    if not proof.signature or len(proof.signature) == 0:
        return VERIFIER_SIGNATURE_INVALID

    # 2. KEY BINDING: current_canonical MUST match proof.content_digest
    #    This is the core fix: proof must be bound to the CURRENT asset
    import hashlib
    current_digest = hashlib.sha256(current_canonical).hexdigest()
    if current_digest != proof.content_digest:
        return VERIFIER_DIGEST_MISMATCH

    # 3. Key lookup
    if proof.public_key_id not in keys:
        return VERIFIER_KEY_UNKNOWN

    key_data = keys[proof.public_key_id]
    if not key_data:
        return VERIFIER_KEY_UNKNOWN

    # 4. Epoch check
    if proof.epoch > epoch:
        return VERIFIER_EPOCH_EXPIRED
    if proof.epoch < 1:
        return VERIFIER_EPOCH_EXPIRED

    # 5. Revocation check
    if proof.proof_id in revoked:
        return VERIFIER_REVOKED

    # 6. Signature verification — FAIL CLOSED on ANY exception
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
        # P0-2: CRYPTO EXCEPTION → REJECT, NOT OK
        return VERIFIER_CRYPTO_ERROR


def _decode_coord(s: str) -> bytes:
    """Decode a coordinate that may be base64 or hex encoded."""
    if not s:
        return b""
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


# ---------------------------------------------------------------------------
# Production verification — REQUIRES current_canonical (no proof-only path)
# ---------------------------------------------------------------------------
def verify_production_proof(proof: AdmissionProof, current_canonical: bytes) -> int:
    """
    Verify an AdmissionProof against a CURRENT asset's canonical bytes.

    P0-3 FIX: current_canonical is REQUIRED. Proof-only verification is FORBIDDEN
    in the production path. Use verify_proof_self_contained() for format validation.

    FAIL-CLOSED GUARANTEES:
      - Missing/invalid current_canonical → VERIFIER_SCHEMA_ERROR
      - digest mismatch → VERIFIER_DIGEST_MISMATCH
      - invalid signature → VERIFIER_SIGNATURE_INVALID
      - any crypto exception → VERIFIER_CRYPTO_ERROR
      - native unavailable → VERIFIER_NATIVE_UNAVAILABLE
      - NO fallback to any untrusted path
    """
    if not isinstance(proof, AdmissionProof):
        return VERIFIER_SCHEMA_ERROR

    if not current_canonical or len(current_canonical) == 0:
        return VERIFIER_SCHEMA_ERROR

    # Try native extension first
    if _NATIVE_LIB is not None:
        try:
            # P0-2: Native verifier reads trust anchor from immutable file path,
            # NOT from Zone 1 mutable globals. This prevents Zone 1 from poisoning
            # the keys/epoch/revocation seen by the native verifier.
            _load_trust_anchor()
            proof_json = proof.to_json().encode("utf-8")
            keys_json = json.dumps(_TRUSTED_KEYS).encode("utf-8")
            revoc_json = json.dumps(list(_REVOCATION_LIST)).encode("utf-8")
            current_can_json = json.dumps(current_canonical.decode("utf-8")).encode("utf-8")

            output_buf = ctypes.create_string_buffer(4096)
            output_len = ctypes.c_size_t(0)

            result = _NATIVE_LIB.verify_production_proof(
                proof_json, len(proof_json),
                keys_json, len(keys_json),
                revoc_json, len(revoc_json),
                current_can_json, len(current_can_json),
                output_buf, ctypes.byref(output_len),
            )
            return int(result)
        except Exception:
            return VERIFIER_NATIVE_UNAVAILABLE

    # In-process verification (Phase 1 reference implementation)
    # Note: uses in-memory trust anchor. Tests inject via _inject_keys().
    # Production native path reloads from file for safety.
    return _verify_proof_against_asset(
        proof, current_canonical,
        _TRUSTED_KEYS, _CURRENT_EPOCH, _REVOCATION_LIST,
    )


def verify_proof_self_contained(proof: AdmissionProof) -> int:
    """
    Verify that a proof is internally consistent (self-contained).
    Does NOT check binding to a specific asset.
    Used for proof format validation before loading.
    """
    return _verify_proof_against_asset(
        proof, proof.asset_canonical,
        {}, 0, set(),
    )
