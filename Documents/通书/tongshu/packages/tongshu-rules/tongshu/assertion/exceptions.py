"""
Production Admission Governance — Exceptions

All exceptions raised during admission are subclasses of AdmissionError.
Every error path is fail-closed: no Production object is ever created
on the error side.
"""

from __future__ import annotations


class AdmissionError(Exception):
    """Base exception for all admission governance failures."""


class AdmissionLoadError(AdmissionError):
    """Failed to load admission data (missing file, corrupt JSON, etc.)."""


class AdmissionSchemaError(AdmissionError):
    """Asset failed schema validation during submission."""


class AdmissionStateError(AdmissionError):
    """Invalid state transition attempted."""


class AdmissionAuditError(AdmissionError):
    """Rule failed audit criteria (incomplete provenance, etc.)."""


class VerifierError(AdmissionError):
    """Trusted Verifier returned an error result."""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class ProductionAccessError(AdmissionError):
    """Attempted to access Production identity without valid proof."""
