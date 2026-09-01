"""
Production Admission Governance — Package Entry Point

Exported API:
  - AdmissionProof, CandidateAsset, ProductionAsset, AssetState, AssetType
  - AdmissionAuthority (test-only constructor), ProductionRuleLoader
  - verify_production_proof (production verifier — no fallback)
  - canonicalize
  - Exception classes

NOTE: Test-only modules are NOT exported here.
  Import test_verifier directly in test files only.
"""

from __future__ import annotations

# Models
from .models import (
    AdmissionProof,
    AssetState,
    AssetType,
    CandidateAsset,
    ProductionAsset,
)

# Exceptions
from .exceptions import (
    AdmissionError,
    AdmissionLoadError,
    AdmissionSchemaError,
    AdmissionStateError,
    AdmissionAuditError,
    VerifierError,
)

# Canonicalizer
from .canonicalizer import canonicalize, compute_digest

# State machine
from .state_machine import AdmittableAsset

# Verifier (production — no fallback)
from .verifier import (
    verify_production_proof,
    VERIFIER_OK,
    VERIFIER_SIGNATURE_INVALID,
    VERIFIER_DIGEST_MISMATCH,
    VERIFIER_REVOKED,
    VERIFIER_EPOCH_EXPIRED,
    VERIFIER_SCHEMA_ERROR,
    VERIFIER_KEY_UNKNOWN,
    VERIFIER_CRYPTO_ERROR,
    VERIFIER_NATIVE_UNAVAILABLE,
)

# Authority (test-only sign; production receives pre-signed proofs)
from .authority import AdmissionAuthority, generate_test_authority

# Loader (verifies pre-signed proofs only)
from .loader import ProductionRuleLoader, load_production_rules

__all__ = [
    # Models
    "AdmissionProof",
    "AssetState",
    "AssetType",
    "CandidateAsset",
    "ProductionAsset",
    # Exceptions
    "AdmissionError",
    "AdmissionLoadError",
    "AdmissionSchemaError",
    "AdmissionStateError",
    "AdmissionAuditError",
    "VerifierError",
    # Canonicalizer
    "canonicalize",
    "compute_digest",
    # State machine
    "AdmittableAsset",
    # Verifier
    "verify_production_proof",
    "VERIFIER_OK",
    "VERIFIER_SIGNATURE_INVALID",
    "VERIFIER_DIGEST_MISMATCH",
    "VERIFIER_REVOKED",
    "VERIFIER_EPOCH_EXPIRED",
    "VERIFIER_SCHEMA_ERROR",
    "VERIFIER_KEY_UNKNOWN",
    "VERIFIER_CRYPTO_ERROR",
    "VERIFIER_NATIVE_UNAVAILABLE",
    # Authority
    "AdmissionAuthority",
    "generate_test_authority",
    # Loader
    "ProductionRuleLoader",
    "load_production_rules",
]

__version__ = "0.2.0"
