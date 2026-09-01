"""
Trusted Verifier — Zone 3 Subprocess
Pre-deployed, immutable verifier script.
Trust anchor loaded from file with hash verification.
Zone 1 cannot inject keys/epoch/revocation into this process.
"""
import base64
import hashlib
import json
import os
import sys

ANCHOR_PATH = os.path.join(os.path.dirname(__file__), "data", "admission_authority.json")
EXPECTED_HASH = os.environ.get("TONGSHU_ANCHOR_HASH", "")


def load_anchor():
    """Load trust anchor from immutable file."""
    try:
        with open(ANCHOR_PATH, "r", encoding="utf-8") as f:
            d = json.load(f)
        
        # Verify anchor integrity
        if EXPECTED_HASH:
            with open(ANCHOR_PATH, "rb") as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
            if actual_hash != EXPECTED_HASH:
                return None, None, None  # Anchor compromised
        
        return d.get("keys", {}), d.get("current_epoch", 1), set(d.get("revocation_list", []))
    except Exception:
        return {}, 0, set()


def decode_c(s):
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
        x = decode_c(kd.get("x", ""))
        y = decode_c(kd.get("y", ""))
        if not (x and y and len(x) == 32 and len(y) == 32):
            return {"r": 6}
        pub = ec.EllipticCurvePublicNumbers(
            x=int.from_bytes(x, "big"),
            y=int.from_bytes(y, "big"),
            curve=ec.SECP256R1(),
        ).public_key()
        pub.verify(sig, bytes.fromhex(pr.get("content_digest", "")), ec.ECDSA(hashes.SHA256()))
        return {"r": 0}
    except InvalidSignature:
        return {"r": 1}
    except Exception:
        return {"r": 7}


def main():
    keys, epoch, revoked = load_anchor()
    if keys is None:
        # Anchor hash mismatch — fail closed
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except Exception:
                pass
            print(json.dumps({"r": 8}), flush=True)
        return
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            r = verify(req.get("p", ""), req.get("c", ""), keys, epoch, revoked)
        except Exception:
            r = {"r": 7}
        print(json.dumps(r), flush=True)


if __name__ == "__main__":
    main()
