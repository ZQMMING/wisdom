"""
Production Admission Governance — Production Rule Loader

Loads pre-admitted assertion rules from JSON files.

CRITICAL DESIGN (P0-5):
  The loader DOES NOT create an AdmissionAuthority.
  It receives pre-signed AdmissionProof objects and only verifies them.

  In production:
    - Zone 2 (offline) creates authorities and signs proofs
    - Zone 1 (runtime) receives proofs and loads them via this loader
    - Zone 1 NEVER has access to private keys or sign() operations

  The loader accepts either:
    1. A path to a JSON file containing rules WITH embedded proofs
    2. Pre-built AdmittableAsset objects with proofs already attached
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from .authority import AdmissionAuthority
from .canonicalizer import canonicalize
from .exceptions import AdmissionLoadError, AdmissionSchemaError
from .models import AssetState, AssetType, AdmissionProof
from .state_machine import AdmittableAsset
from .verifier import (
    verify_production_proof,
    VERIFIER_OK,
    VERIFIER_NATIVE_UNAVAILABLE,
)


class ProductionRuleLoader:
    """
    Loads and verifies pre-admitted assertion rules from JSON files.

    PRODUCTION USAGE:
        # Zone 2 creates and signs proofs offline
        # Zone 1 receives the signed proofs and loads them:
        loader = ProductionRuleLoader(path="admitted_rules.json")
        rules = loader.load()  # Returns dict[str, AdmittableAsset]

    FAIL-CLOSED:
        - Missing file → AdmissionLoadError
        - Corrupt JSON → AdmissionLoadError
        - Invalid proof signature → AdmissionLoadError
        - Native verifier unavailable → AdmissionLoadError
        - Empty rules → AdmissionLoadError (NOT empty production)
    """

    def __init__(
        self,
        path: str,
    ) -> None:
        self.path = path

    def load(self) -> dict[str, AdmittableAsset]:
        """
        Load pre-admitted rules from JSON and verify proofs.

        Raises AdmissionLoadError on any failure (fail-closed).
        """
        rules = self._load_rules()

        if not rules:
            raise AdmissionLoadError(
                f"Empty rules in {self.path} — no Production output"
            )

        produced: dict[str, AdmittableAsset] = {}

        for rule_id, rule_data in rules.items():
            asset = self._verify_and_build(rule_id, rule_data)
            produced[rule_id] = asset

        return produced

    def _load_rules(self) -> dict[str, dict]:
        """Load and parse the rules JSON file."""
        path = Path(self.path)
        if not path.exists():
            raise AdmissionLoadError(f"Rules file not found: {self.path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise AdmissionLoadError(f"Corrupt JSON in {self.path}: {e}")

        if not isinstance(data, list):
            if isinstance(data, dict):
                return data
            raise AdmissionSchemaError(
                f"Expected array or object of rules, got {type(data).__name__}"
            )

        result = {}
        for item in data:
            if not isinstance(item, dict):
                raise AdmissionSchemaError(f"Invalid rule entry: {item}")
            rule_id = item.get("rule_id")
            if not rule_id:
                raise AdmissionSchemaError("Rule missing 'rule_id' field")
            result[rule_id] = item

        return result

    def _verify_and_build(
        self, rule_id: str, rule_data: dict
    ) -> AdmittableAsset:
        """
        Build an AdmittableAsset from rule data that includes a proof.

        P0-5: This method does NOT create or sign proofs.
        It only verifies pre-existing proofs.
        """
        proof_json = rule_data.get("admission_proof")
        if not proof_json:
            raise AdmissionLoadError(
                f"Rule {rule_id} missing admission_proof — cannot produce Production asset"
            )

        # Parse the proof
        try:
            proof = AdmissionProof.from_json(proof_json)
        except (json.JSONDecodeError, KeyError) as e:
            raise AdmissionLoadError(
                f"Rule {rule_id} has corrupt admission_proof: {e}"
            )

        # Build the asset in ADMITTED state (proof already verified elsewhere)
        asset = AdmittableAsset(
            asset_type=AssetType.ASSERTION_RULE.value,
            raw_data=rule_data,
        )
        asset._state = AssetState.ADMITTED  # type: ignore[assignment]
        asset._proof = proof  # type: ignore[assignment]

        # Final verification before production conversion
        result = verify_production_proof(proof)
        if result != VERIFIER_OK:
            if result == VERIFIER_NATIVE_UNAVAILABLE:
                raise AdmissionLoadError(
                    f"Rule {rule_id}: Trusted Verifier native extension unavailable — FAIL CLOSED"
                )
            raise AdmissionLoadError(
                f"Rule {rule_id}: Verification failed (code={result})"
            )

        # Convert to Production
        ok = asset.convert_to_production()
        if not ok:
            raise AdmissionLoadError(f"Rule {rule_id}: Failed production conversion")

        return asset


def load_production_rules(
    path: str,
) -> dict[str, AdmittableAsset]:
    """
    Convenience function to load and verify pre-admitted rules.

    PRODUCTION NOTE:
      The authority (with private key) must have signed these rules
      in Zone 2 BEFORE they reached this function.
      This function only verifies — it never signs.
    """
    loader = ProductionRuleLoader(path)
    return loader.load()
