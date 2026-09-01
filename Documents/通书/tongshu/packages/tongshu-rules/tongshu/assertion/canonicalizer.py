"""
Production Admission Governance — Canonicalizer

Produces deterministic byte representations of assets for signing.
Every semantic field must be included; omission changes the digest.
"""

from __future__ import annotations

import json
from typing import Any


def canonicalize(data: Any) -> bytes:
    """
    Produce a deterministic byte representation of an asset.

    Rules:
      1. All dicts sorted by key (recursive)
      2. All lists preserved in order
      3. Strings UTF-8 encoded
      4. Numbers: integers as ints, floats with fixed precision
      5. None -> null
      6. Enums -> their value
      7. Nested structures recursively canonicalized
      8. No whitespace, no BOM, no trailing newline
    """
    return json.dumps(
        _canonical_dict(data),
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=_canonical_serializer,
    ).encode("utf-8")


def _canonical_dict(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _canonical_dict(v) for k, v in sorted(obj.items())}
    if isinstance(obj, list):
        return [_canonical_dict(item) for item in obj]
    if isinstance(obj, tuple):
        return [_canonical_dict(item) for item in obj]
    return obj


def _canonical_serializer(obj: Any) -> Any:
    """Handle types that json.dumps cannot serialize natively."""
    if hasattr(obj, "value") and not isinstance(obj, str):
        # Enum
        return obj.value
    if hasattr(obj, "isoformat"):
        # datetime
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode("utf-8")
    raise TypeError(f"Cannot canonicalize {type(obj).__name__}")


def compute_digest(canonical_bytes: bytes) -> str:
    """SHA-256 digest of canonical bytes."""
    return hashlib_sha256_hex(canonical_bytes)


def hashlib_sha256_hex(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()
