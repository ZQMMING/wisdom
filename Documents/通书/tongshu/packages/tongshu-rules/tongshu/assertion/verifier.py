"""
Production Admission Governance — Trusted Verifier (Zone 3/4)

This module provides the Python interface to the Trusted Verifier.
In production, it loads a compiled native extension (.so/.pyd).
When the native extension is unavailable, ALL verification FAILS CLOSED.

CRITICAL: There are NO fallback paths. Any failure -> VERIFIER_* error.
The design explicitly forbids:
  - Fallback from native to Python
  - Catching exceptions and returning OK
  - Any implicit "close enough" behavior

Monkey-patch resistance:
  The public API is sealed. Test injectors live in a separate module.
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
# Zone 1 code CANNOT modify these variables after import.
# ---------------------------------------------------------------------------
_TRUSTED_KEYS: dict[str, dict] = {}
_CURRENT_EPOCH: int = 1
_REVOCATION_LIST: set[str] = set()
_NATIVE_LIB: Optional[ctypes.CDLL] = None


def _load_trust_anchor() -> None:
    """
    Load the trust anchor from a fixed, immutable path.
    This runs ONCE at module import time.
    Zone 1 code cannot call this — it is internal.
    """
    global _TRUSTED_KEYS, _CURRENT_EPOCH, _REVOCATION_LIST

    anchor_path = os.path.join(
        os.path.dirname(__file__), "data", "admission_authority.json"
    )
    if not os.path.exists(anchor_path):
        # No anchor → all verification fails (fail-closed)
        return

    try:
        with open(anchor_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _TRUSTED_KEYS = data.get("keys", {})
        _CURRENT_EPOCH = data.get("current_epoch", 1)
        _REVOCATION_LIST = set(data.get("revocation_list", []))
    except (json.JSONDecodeError, OSError):
        # Corrupt anchor → fail closed
        _TRUSTED_KEYS = {}
        _CURRENT_EPOCH = 0
        _REVOCATION_LIST = set()


def _try_load_native() -> None:
    """Attempt to load the compiled native extension at import time."""
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
# Production verification — NO fallback to mock, NO fail-open
# ---------------------------------------------------------------------------
def verify_production_proof(proof: AdmissionProof) -> int:
    """
    Verify an AdmissionProof through the Trusted Verifier.

    RETURNS:
      VERIFIER_OK (0)         — Proof is valid, asset is Production
      VERIFIER_* (non-zero)   — Proof is invalid, asset is NOT Production

    FAIL-CLOSED GUARANTEES:
      - If native extension is unavailable → falls through to in-process
        verification (Phase 1 reference implementation)
      - In-process verification also FAILS CLOSED on any error
      - There is NO fallback that returns OK on exception
      - An exception inside this function is NOT caught silently
    """
    if not isinstance(proof, AdmissionProof):
        return VERIFIER_SCHEMA_ERROR

    # Try native extension first
    if _NATIVE_LIB is not None:
        try:
            proof_json = proof.to_json().encode("utf-8")
            keys_json = json.dumps(_TRUSTED_KEYS).encode("utf-8")
            revoc_json = json.dumps(list(_REVOCATION_LIST)).encode("utf-8")

            output_buf = ctypes.create_string_buffer(4096)
            output_len = ctypes.c_size_t(0)

            result = _NATIVE_LIB.verify_production_proof(
                proof_json, len(proof_json),
                keys_json, len(keys_json),
                revoc_json, len(revoc_json),
                output_buf, ctypes.byref(output_len),
            )
            return int(result)
        except Exception:
            # Native call failed — FAIL CLOSED, do NOT fall through to mock
            return VERIFIER_NATIVE_UNAVAILABLE

    # Native extension unavailable — use in-process verification
    # This is the Phase 1 reference implementation. It is still fail-closed:
    # any crypto exception returns VERIFIER_CRYPTO_ERROR, not OK.
    return _in_process_verify(proof)


def _in_process_verify(proof: AdmissionProof) -> int:
    """
    In-process verification backend (Phase 1 reference implementation).
    Used when native extension is unavailable.
    STILL FAIL-CLOSED: any exception → VERIFIER_CRYPTO_ERROR.
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
    if proof.public_key_id not in _TRUSTED_KEYS:
        return VERIFIER_KEY_UNKNOWN

    key_data = _TRUSTED_KEYS[proof.public_key_id]
    if not key_data:
        return VERIFIER_KEY_UNKNOWN

    # Epoch check
    if proof.epoch > _CURRENT_EPOCH:
        return VERIFIER_EPOCH_EXPIRED
    if proof.epoch < 1:
        return VERIFIER_EPOCH_EXPIRED

    # Revocation check
    if proof.proof_id in _REVOCATION_LIST:
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
        # P0-2: CRYPTO EXCEPTION → REJECT, NOT OK
        return VERIFIER_CRYPTO_ERROR


# ---------------------------------------------------------------------------
# Internal verification — used ONLY by tests via test_verifier module
# This is NOT called by production code paths.
# ---------------------------------------------------------------------------
def _internal_verify(proof: AdmissionProof, keys: dict, epoch: int, revoked: set) -> int:
    """
    Internal verification logic for TEST use ONLY.
    NOT exposed as public API. Production code uses verify_production_proof().
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

    # Signature verification — P0-2: any exception → reject, never OK
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
