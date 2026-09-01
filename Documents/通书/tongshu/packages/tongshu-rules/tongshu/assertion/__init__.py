"""
Production Admission Governance — Package Entry Point

Exported API:
  - AdmissionProof, CandidateAsset, ProductionAsset, AssetState, AssetType
  - AdmissionAuthority, ProductionRuleLoader
  - verify_production_proof
  - canonicalize
  - Exception classes
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
    ProductionAccessError,
)

# Canonicalizer
from .canonicalizer import canonicalize, compute_digest

# State machine
from .state_machine import AdmittableAsset

# Verifier
from .verifier import (
    verify_production_proof,
    VERIFIER_OK,
    VERIFIER_SIGNATURE_INVALID,
    VERIFIER_DIGEST_MISMATCH,
    VERIFIER_REVOKED,
    VERIFIER_EPOCH_EXPIRED,
    VERIFIER_SCHEMA_ERROR,
    VERIFIER_KEY_UNKNOWN,
)

# Authority
from .authority import AdmissionAuthority, generate_test_authority

# Loader
from .loader import ProductionRuleLoader, load_production_rules

__all__ = [
    # Models
    "AdmissionProof",
    "AssetState",
    "AssetType",
    "CandidateAsset",
    "ProductionAsset",
    "ProductionAccessError",
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
    # Authority
    "AdmissionAuthority",
    "generate_test_authority",
    # Loader
    "ProductionRuleLoader",
    "load_production_rules",
]

__version__ = "0.1.0"
