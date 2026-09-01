"""
Production Admission Governance — Production Rule Loader

Loads assertion rules from JSON files, processes them through
the admission pipeline, and produces Production assets.

Fail-closed: any error raises an exception — no empty Production.
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
from .verifier import verify_production_proof


class ProductionRuleLoader:
    """
    Loads and admits assertion rules from JSON files.

    Usage:
        loader = ProductionRuleLoader(path="rules.json", authority=auth)
        rules = loader.load()  # Returns dict[str, ProductionAsset]
    """

    def __init__(
        self,
        path: str,
        authority: AdmissionAuthority,
        public_key_id: str = "default",
    ) -> None:
        self.path = path
        self.authority = authority
        self.public_key_id = public_key_id

    def load(self) -> dict[str, AdmittableAsset]:
        """
        Load rules from JSON, admit them, and return Production assets.

        Raises AdmissionLoadError on any failure (fail-closed).
        """
        rules = self._load_rules()

        if not rules:
            raise AdmissionLoadError(
                f"Empty rules in {self.path} — no Production output"
            )

        produced: dict[str, AdmittableAsset] = {}

        for rule_id, rule_data in rules.items():
            asset = self._admit_rule(rule_id, rule_data)
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
            # Support both array and dict formats
            if isinstance(data, dict):
                return data
            raise AdmissionSchemaError(
                f"Expected array or object of rules, got {type(data).__name__}"
            )

        # Convert list format to dict by rule_id
        result = {}
        for item in data:
            if not isinstance(item, dict):
                raise AdmissionSchemaError(f"Invalid rule entry: {item}")
            rule_id = item.get("rule_id")
            if not rule_id:
                raise AdmissionSchemaError("Rule missing 'rule_id' field")
            result[rule_id] = item

        return result

    def _admit_rule(self, rule_id: str, rule_data: dict) -> AdmittableAsset:
        """Submit a single rule through the admission pipeline."""
        asset = AdmittableAsset(
            asset_type=AssetType.ASSERTION_RULE.value,
            raw_data=rule_data,
        )

        # Step 1: Submit for admission
        asset.submit_for_admission()

        # Step 2: Audit (check provenance completeness)
        self._audit_rule(asset)

        # Step 3: Authority signs
        canonical = asset.to_canonical()
        proof = self.authority.sign(
            asset_type=AssetType.ASSERTION_RULE.value,
            asset_canonical=canonical,
            public_key_id=self.public_key_id,
        )
        asset.audit_complete(proof)

        # Step 4: Trusted Verifier converts to Production
        ok = asset.convert_to_production()
        if not ok:
            # Verifier rejected — asset stays ADMITTED, not PRODUCTION
            raise AdmissionLoadError(
                f"Verifier rejected rule {rule_id}"
            )

        return asset

    def _audit_rule(self, asset: AdmittableAsset) -> None:
        """
        Audit a rule for admission criteria.
        Checks: provenance completeness, source verification.
        """
        data = asset.raw_data
        provenance = data.get("provenance", {})

        required_fields = ["source_work", "source_chapter"]
        for field in required_fields:
            if not provenance.get(field):
                raise AdmissionSchemaError(
                    f"Rule {asset.raw_data.get('rule_id', '?')} "
                    f"missing provenance field: {field}"
                )


def load_production_rules(
    path: str,
    authority: AdmissionAuthority,
    public_key_id: str = "default",
) -> dict[str, AdmittableAsset]:
    """Convenience function to load and admit rules."""
    loader = ProductionRuleLoader(path, authority, public_key_id)
    return loader.load()
