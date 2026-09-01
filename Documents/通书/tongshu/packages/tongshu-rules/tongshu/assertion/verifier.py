"""
Production Admission Governance — Verifier Module

Architecture:
  Zone 1 (Python app) → IPC → Zone 3 (Trusted Verifier)
  Trust Anchor loaded from immutable FILE. Zone 1 does NOT inject keys/epoch/revocation.

  Production path: subprocess using FIXED verifier script (deployed, not generated)
  Test path: TestVerifier uses in-process _verify_proof() — requires explicit activate()
  
  Security invariants:
    1. verify_production_proof() NEVER uses in-process fallback
    2. Trust anchor loaded from fixed file, NOT from Zone 1 globals
    3. Subprocess verifies trust anchor hash on startup
    4. Test hook (_test_verifier_hook) ONLY active when TestVerifier.activate() called
       in explicit test context (no implicit injection in production code)

FAIL-CLOSED: subprocess unavailable / anchor hash mismatch → VERIFIER_NATIVE_UNAVAILABLE
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional

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
# Fixed paths — deployed artifacts, not generated
# ---------------------------------------------------------------------------
def _verifier_script_path() -> str:
    """Path to the FIXED verifier script (pre-deployed, not generated at runtime)."""
    return str(Path(__file__).parent / "trusted_verifier.py")


def _trust_anchor_path() -> str:
    """Path to the immutable trust anchor file."""
    return str(Path(__file__).parent / "data" / "admission_authority.json")


# ---------------------------------------------------------------------------
# Core verification logic (used by subprocess worker AND TestVerifier)
# NOT called directly by production verify_production_proof()
# ---------------------------------------------------------------------------
def _verify_proof(
    proof: AdmissionProof,
    current_canonical: bytes,
    keys: dict,
    epoch: int,
    revoked: set,
) -> int:
    """Core verification: check proof binds to current asset."""
    if not proof.verify_self_integrity():
        return VERIFIER_DIGEST_MISMATCH
    if proof.version != "1.0":
        return VERIFIER_SCHEMA_ERROR
    if proof.signature_algorithm != "ES256":
        return VERIFIER_SCHEMA_ERROR
    if not proof.signature or len(proof.signature) == 0:
        return VERIFIER_SIGNATURE_INVALID

    # CRITICAL: Proof MUST bind to CURRENT asset (not self)
    current_digest = hashlib.sha256(current_canonical).hexdigest()
    if current_digest != proof.content_digest:
        return VERIFIER_DIGEST_MISMATCH

    if proof.public_key_id not in keys:
        return VERIFIER_KEY_UNKNOWN
    key_data = keys.get(proof.public_key_id, {})
    if not key_data:
        return VERIFIER_KEY_UNKNOWN

    if proof.epoch > epoch or proof.epoch < 1:
        return VERIFIER_EPOCH_EXPIRED

    if proof.proof_id in revoked:
        return VERIFIER_REVOKED

    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.exceptions import InvalidSignature

        def _decode_coord(s: str) -> bytes:
            if not s:
                return b""
            try:
                b = base64.b64decode(s)
                if len(b) == 32:
                    return b
            except Exception:
                pass
            try:
                h = bytes.fromhex(s)
                if len(h) == 32:
                    return h
            except ValueError:
                pass
            return b""

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
        return VERIFIER_CRYPTO_ERROR


# ---------------------------------------------------------------------------
# Trusted Verifier Process (Zone 3)
# Uses a FIXED, pre-deployed script — NOT dynamically generated.
# ---------------------------------------------------------------------------
class _VerifierProcess:
    def __init__(self) -> None:
        self._proc: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()

    def _spawn(self) -> bool:
        if self._proc is not None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=1)
            except Exception:
                pass
            self._proc = None

        script_path = _verifier_script_path()
        if not os.path.exists(script_path):
            return False

        try:
            self._proc = subprocess.Popen(
                [sys.executable, script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            return True
        except Exception:
            self._proc = None
            return False

    def verify(self, proof_json: str, canonical_b64: str) -> int:
        with self._lock:
            if not self._proc or not self._proc.stdin:
                return VERIFIER_NATIVE_UNAVAILABLE
            request = json.dumps({"p": proof_json, "c": canonical_b64})
            try:
                self._proc.stdin.write(request + "\n")
                self._proc.stdin.flush()
                line = self._proc.stdout.readline()
                if not line:
                    return VERIFIER_CRYPTO_ERROR
                resp = json.loads(line.strip())
                return int(resp.get("r", VERIFIER_CRYPTO_ERROR))
            except Exception:
                self._proc = None
                return VERIFIER_NATIVE_UNAVAILABLE

    def is_alive(self) -> bool:
        with self._lock:
            return (
                self._proc is not None
                and self._proc.stdin is not None
                and self._proc.poll() is None
            )

    def close(self) -> None:
        with self._lock:
            if self._proc:
                try:
                    self._proc.terminate()
                    self._proc.wait(timeout=1)
                except Exception:
                    pass
                self._proc = None


_verifier: Optional[_VerifierProcess] = None


def _get_verifier() -> _VerifierProcess:
    global _verifier
    if _verifier is None:
        _verifier = _VerifierProcess()
    return _verifier


# ---------------------------------------------------------------------------
# Test override hook — accessed ONLY by test_verifier.TestVerifier
# NOT part of production API. Never called directly by production code.
# ---------------------------------------------------------------------------
_test_verifier_hook = None
def verify_production_proof(proof: AdmissionProof, current_canonical: bytes) -> int:
    """
    Production verification via Trusted Verifier Subprocess (Zone 3).
    
    P0: NO in-process fallback. Subprocess unavailable → VERIFIER_NATIVE_UNAVAILABLE.
    Trust anchor lives in subprocess, loaded from immutable file with hash check.
    """
    if not isinstance(proof, AdmissionProof):
        return VERIFIER_SCHEMA_ERROR
    if not current_canonical or len(current_canonical) == 0:
        return VERIFIER_SCHEMA_ERROR

    # Test override: allow TestVerifier to inject in-process verification
    if _test_verifier_hook is not None:
        return _test_verifier_hook(proof, current_canonical)

    vproc = _get_verifier()
    if not vproc.is_alive():
        if not vproc._spawn():
            return VERIFIER_NATIVE_UNAVAILABLE

    proof_json = proof.to_json()
    canonical_b64 = base64.b64encode(current_canonical).decode("ascii")
    return vproc.verify(proof_json, canonical_b64)


def verify_proof_self_contained(proof: AdmissionProof) -> int:
    """Verify proof format only — NOT for production authorization."""
    keys, epoch, revoked = _load_anchor_from_file()
    return _verify_proof(proof, proof.asset_canonical, keys, epoch, revoked)


def _load_anchor_from_file() -> tuple:
    """Load trust anchor from immutable file (for self-contained verification only)."""
    try:
        with open(_trust_anchor_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("keys", {}), data.get("current_epoch", 1), set(data.get("revocation_list", []))
    except Exception:
        return {}, 0, set()


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
import atexit
atexit.register(lambda: _verifier.close() if _verifier else None)
