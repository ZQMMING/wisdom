"""Validate Canonical Content against the current Canonical schema.

Per architecture_decisions_v1.md, the Canonical Validator MUST run
before any LLM call (per cross_analysis.md §3 and output_validation.md §4).

V3.6 §27 adapter-first: the canonical validator now prefers
docs/v36/01_CANONICAL_SCHEMA.json (a superset of the frozen v1.0.0 schema —
old shapes without `meta` still validate). The legacy
docs/canonical_content.schema.json is used only when the v36 file is absent.
This is a file-availability fallback, NOT a validation fallback: a canonical
that fails the v36 schema is a real failure and never re-tried against the
legacy schema.
"""

from __future__ import annotations
import json
from pathlib import Path

try:
    import jsonschema
except ImportError:
    jsonschema = None

V36_CANONICAL_SCHEMA = ("v36", "01_CANONICAL_SCHEMA.json")
LEGACY_CANONICAL_SCHEMA = "canonical_content.schema.json"


def _resolve_schema_path(schema_dir: Path) -> Path | None:
    """Pick the current Canonical schema: v36 superset first, legacy fallback."""
    v36 = schema_dir.joinpath(*V36_CANONICAL_SCHEMA)
    if v36.exists():
        return v36
    legacy = schema_dir / LEGACY_CANONICAL_SCHEMA
    if legacy.exists():
        return legacy
    return None


def validate_canonical(canonical_dict: dict, schema_dir: Path) -> tuple[bool, list[str]]:
    """Validate a Canonical Content dict against the schema.

    Returns:
        (is_valid, list_of_errors)
    """
    if jsonschema is None:
        return True, ["jsonschema not installed; skipping validation"]

    schema_path = _resolve_schema_path(schema_dir)
    if schema_path is None:
        return False, [
            f"Schema not found: {schema_dir.joinpath(*V36_CANONICAL_SCHEMA)} "
            f"nor {schema_dir / LEGACY_CANONICAL_SCHEMA}"
        ]

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    validator = jsonschema.Draft202012Validator(schema)
    errors = list(validator.iter_errors(canonical_dict))
    if not errors:
        return True, []
    return False, [f"{'/'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in errors]
