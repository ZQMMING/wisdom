"""
Production Admission Governance — Production Rule Loader

Loads pre-admitted assertion rules from JSON files.

CRITICAL DESIGN (P0-5, P0-new):
  The loader DOES NOT create an AdmissionAuthority.
  It receives pre-signed AdmissionProof objects and verifies them.

  P0 FIX (Proof ↔ Asset binding):
    The loader now passes current_canonical to verify_production_proof(),
    ensuring the proof binds to the ACTUAL rule_data being loaded,
    not just the proof's self-contained content.

  In production:
    - Zone 2 (offline) creates authorities and signs proofs
    - Zone 1 (runtime) receives proofs and loads them via this loader
    - Zone 1 NEVER has access to private keys or sign() operations
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

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
        loader = ProductionRuleLoader(path="admitted_rules.json")
        rules = loader.load()

    FAIL-CLOSED:
        - Missing file → AdmissionLoadError
        - Corrupt JSON → AdmissionLoadError
        - Proof doesn't bind to current rule → AdmissionLoadError (P0 fix)
        - Empty rules → AdmissionLoadError
    """

    def __init__(self, path: str) -> None:
        self.path = path

    def load(self) -> dict[str, AdmittableAsset]:
        """
        Load pre-admitted rules from JSON, verify proof binding, return Production assets.

        P0 FIX: Each rule's proof is verified against the CURRENT rule_data,
        not just the proof's self-contained canonical content.
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
        Build an AdmittableAsset from rule data with embedded proof.

        P0 FIX: Verifies that the proof binds to the CURRENT rule_data
        (via current_canonical → content_digest match), not just that
        the proof is internally consistent.
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

        # P0 FIX: Compute current_canonical from rule_data (excluding admission_proof)
        # and verify proof binds to it.
        # The proof was signed over the rule_data WITHOUT the admission_proof field.
        rule_for_verify = {k: v for k, v in rule_data.items() if k != "admission_proof"}
        current_canonical = canonicalize(rule_for_verify)
        result = verify_production_proof(proof, current_canonical)

        if result != VERIFIER_OK:
            if result == VERIFIER_NATIVE_UNAVAILABLE:
                raise AdmissionLoadError(
                    f"Rule {rule_id}: Trusted Verifier unavailable — FAIL CLOSED"
                )
            raise AdmissionLoadError(
                f"Rule {rule_id}: Proof does not bind to current rule "
                f"(verification failed, code={result})"
            )

        # Build asset — use proper state transition
        asset = AdmittableAsset(
            asset_type=AssetType.ASSERTION_RULE.value,
            raw_data=rule_data,
        )
        # Set state directly to ADMITTED (proof already verified above)
        asset._state = AssetState.ADMITTED  # type: ignore[assignment]
        asset._proof = proof  # type: ignore[assignment]

        # Final production conversion (re-verifies binding)
        ok = asset.convert_to_production()
        if not ok:
            raise AdmissionLoadError(
                f"Rule {rule_id}: Production conversion failed (binding check)"
            )

        return asset


def load_production_rules(path: str) -> dict[str, AdmittableAsset]:
    """
    Convenience function to load and verify pre-admitted rules.

    PRODUCTION NOTE:
      The authority (with private key) must have signed these rules
      in Zone 2 BEFORE they reached this function.
      This function only verifies — it never signs.
    """
    loader = ProductionRuleLoader(path)
    return loader.load()
