"""
Production Admission Governance — Trusted Verifier (Zone 3 Subprocess)

Architecture:
  Zone 1 (Python app) → IPC → Zone 3 (Verifier subprocess)
  Trust anchor (keys/epoch/revocation) lives ONLY in subprocess.
  Zone 1 CANNOT poison it via globals.

FAIL-CLOSED: subprocess unavailable → VERIFIER_NATIVE_UNAVAILABLE
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import threading
import tempfile
from pathlib import Path
from typing import Optional

from .models import AdmissionProof

# Result codes
VERIFIER_OK = 0
VERIFIER_SIGNATURE_INVALID = 1
VERIFIER_DIGEST_MISMATCH = 2
VERIFIER_REVOKED = 3
VERIFIER_EPOCH_EXPIRED = 4
VERIFIER_SCHEMA_ERROR = 5
VERIFIER_KEY_UNKNOWN = 6
VERIFIER_CRYPTO_ERROR = 7
VERIFIER_NATIVE_UNAVAILABLE = 8


def _trust_anchor_path() -> str:
    return str(Path(__file__).parent / "data" / "admission_authority.json")


# ---------------------------------------------------------------------------
# Core verification (used by subprocess worker AND TestVerifier)
# NOT called directly by production verify_production_proof()
# ---------------------------------------------------------------------------
def _verify_proof(
    proof: AdmissionProof,
    current_canonical: bytes,
    keys: dict,
    epoch: int,
    revoked: set,
) -> int:
    if not proof.verify_self_integrity():
        return VERIFIER_DIGEST_MISMATCH
    if proof.version != "1.0":
        return VERIFIER_SCHEMA_ERROR
    if proof.signature_algorithm != "ES256":
        return VERIFIER_SCHEMA_ERROR
    if not proof.signature or len(proof.signature) == 0:
        return VERIFIER_SIGNATURE_INVALID

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
# Trusted Verifier Subprocess (Zone 3)
# Loads trust anchor from immutable FILE — Zone 1 cannot poison it.
# ---------------------------------------------------------------------------
class _VerifierProcess:
    def __init__(self) -> None:
        self._proc: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._script_path: Optional[str] = None

    def _spawn(self) -> bool:
        if self._proc is not None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=1)
            except Exception:
                pass
            self._proc = None
        self._script_path = _create_verifier_script()
        try:
            self._proc = subprocess.Popen(
                [sys.executable, self._script_path],
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
            if self._script_path:
                try:
                    os.unlink(self._script_path)
                except Exception:
                    pass
                self._script_path = None


_verifier: Optional[_VerifierProcess] = None


def _get_verifier() -> _VerifierProcess:
    global _verifier
    if _verifier is None:
        _verifier = _VerifierProcess()
        _verifier._spawn()
    return _verifier


def _create_verifier_script() -> str:
    anchor = _trust_anchor_path()
    script = '''"""Trusted Verifier Subprocess — Zone 3. Trust anchor from file only."""
import base64, hashlib, json, sys
ANCHOR = %r

def load_anchor():
    try:
        with open(ANCHOR, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d.get("keys", {}), d.get("current_epoch", 1), set(d.get("revocation_list", []))
    except Exception:
        return {}, 0, set()

def decode_c(s):
    try:
        b = base64.b64decode(s)
        if len(b) == 32: return b
    except Exception: pass
    try:
        h = bytes.fromhex(s)
        if len(h) == 32: return h
    except ValueError: pass
    return b""

def verify(p, cb64, keys, epoch, revoked):
    try:
        can = base64.b64decode(cb64)
    except Exception:
        return {"r": 5}
    try:
        pr = json.loads(p)
    except Exception:
        return {"r": 5}
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.exceptions import InvalidSignature
    except ImportError:
        return {"r": 7}
    if pr.get("version") != "1.0" or pr.get("signature_algorithm") != "ES256":
        return {"r": 5}
    sig = bytes.fromhex(pr.get("signature", ""))
    if not sig or len(sig) == 0:
        return {"r": 1}
    cd = hashlib.sha256(can).hexdigest()
    if cd != pr.get("content_digest", ""):
        return {"r": 2}
    kid = pr.get("public_key_id", "")
    if kid not in keys:
        return {"r": 6}
    kd = keys.get(kid, {})
    if not kd:
        return {"r": 6}
    ep = pr.get("epoch", 0)
    if ep > epoch or ep < 1:
        return {"r": 4}
    if pr.get("proof_id", "") in revoked:
        return {"r": 3}
    try:
        x = decode_c(kd.get("x", "")); y = decode_c(kd.get("y", ""))
        if not (x and y and len(x) == 32 and len(y) == 32):
            return {"r": 6}
        pub = ec.EllipticCurvePublicNumbers(x=int.from_bytes(x,"big"), y=int.from_bytes(y,"big"), curve=ec.SECP256R1()).public_key()
        pub.verify(sig, bytes.fromhex(pr.get("content_digest","")), ec.ECDSA(hashes.SHA256()))
        return {"r": 0}
    except InvalidSignature:
        return {"r": 1}
    except Exception:
        return {"r": 7}

def main():
    keys, epoch, revoked = load_anchor()
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try:
            req = json.loads(line)
            r = verify(req.get("p",""), req.get("c",""), keys, epoch, revoked)
        except Exception:
            r = {"r": 7}
        print(json.dumps(r), flush=True)

if __name__ == "__main__":
    main()
''' % anchor
    fd, path = tempfile.mkstemp(suffix=".py", prefix="svr_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(script)
    return path


# ---------------------------------------------------------------------------
# Test override hook — allows TestVerifier to inject in-process verification
# Production path: subprocess (Zone 3)
# Test path: in-process _verify_proof() with injected trust anchor
# ---------------------------------------------------------------------------
_test_verifier_hook = None


def _set_test_verifier(hook):
    """INTERNAL: Set by TestVerifier for test runs only."""
    global _test_verifier_hook
    _test_verifier_hook = hook


def _clear_test_verifier():
    """INTERNAL: Clear test override."""
    global _test_verifier_hook
    _test_verifier_hook = None


# ---------------------------------------------------------------------------
# Production API — ALWAYS uses subprocess (unless test hook is active)
# ---------------------------------------------------------------------------
def verify_production_proof(proof: AdmissionProof, current_canonical: bytes) -> int:
    """
    Production verification via Trusted Verifier Subprocess (Zone 3).
    NO in-process fallback. Subprocess unavailable → VERIFIER_NATIVE_UNAVAILABLE.
    Trust anchor lives in subprocess, loaded from immutable file.
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
    try:
        with open(_trust_anchor_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("keys", {}), data.get("current_epoch", 1), set(data.get("revocation_list", []))
    except Exception:
        return {}, 0, set()


import atexit
atexit.register(lambda: _verifier.close() if _verifier else None)
