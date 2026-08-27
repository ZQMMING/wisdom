"""Layer1 — 表述覆盖校验。

Per output_validation.md §4. Checks:
    - Output JSON schema (text, covered_claim_ids, honored_exclusion_ids, self_check)
    - Length bounds
    - Coverage (covered_claim_ids == set of claim_ids in SIR; degradation-aware,
      T501: renderer-declared dropped claim_ids are excluded from the expected set
      and the drop itself is sanity-checked)
    - Exclusion honor
    - Forbidden keywords / regex
    - Self-check fields

依赖：result.py。

Version: 1.0.0
Created: 2026-08-20 (Phase 2 / Step 8)
Migrated from: validation/layer1.py
"""

from __future__ import annotations

import re

from .result import Layer1Result


def validate_layer1(
    rendered_output: dict,
    sir: dict,
    render_request: dict,
    forbidden_inference_records: list = None,
) -> Layer1Result:
    """Run Layer 1 deterministic validation.

    Returns Layer1Result with passed/errors/details.
    """
    errors: list[str] = []
    details = {
        "length_ok": False,
        "coverage_ok": False,
        "exclusion_ok": False,
        "forbidden_check_ok": False,
        "self_check_ok": False,
    }

    # 4.1 Output Schema check (must have these fields)
    required = ("text", "covered_claim_ids", "honored_exclusion_ids", "self_check")
    for f in required:
        if f not in rendered_output:
            errors.append(f"missing field: {f}")

    if errors:
        return Layer1Result(False, errors, details)

    text = rendered_output["text"]
    covered_ids = set(rendered_output["covered_claim_ids"])
    honored_ids = set(rendered_output["honored_exclusion_ids"])
    self_check = rendered_output["self_check"]

    # 4.3 Length check
    length_cfg = render_request.get("length", {"min": 80, "max": 150})
    n = len(text)
    details["length_ok"] = length_cfg["min"] <= n <= length_cfg["max"]
    if not details["length_ok"]:
        errors.append(f"length {n} out of bounds [{length_cfg['min']}, {length_cfg['max']}]")

    # 4.4 Coverage check — degradation-aware (T501).
    # When the renderer exceeded its capacity it may declare a top_k
    # degradation, dropping the weakest claims. Coverage is then judged
    # against (expected minus dropped), and the drop itself is sanity-checked:
    # dropped ids must be real claims and must not also be covered.
    degradation = rendered_output.get("degradation") or {}
    dropped_ids = set(degradation.get("dropped_claim_ids", []))
    all_expected = {c["claim_id"] for c in sir.get("atomic_claims", [])}
    expected_ids = all_expected - dropped_ids
    details["degraded"] = bool(dropped_ids)
    details["dropped_claim_ids"] = sorted(dropped_ids)

    unknown = dropped_ids - all_expected
    if unknown:
        errors.append(f"degradation dropped unknown claim_ids: {sorted(unknown)}")
    dropped_but_covered = dropped_ids & covered_ids
    if dropped_but_covered:
        errors.append(
            f"degradation dropped but still covered claim_ids: {sorted(dropped_but_covered)}"
        )
    if all_expected and dropped_ids == all_expected:
        errors.append("degradation cannot drop all claim_ids")

    details["coverage_ok"] = covered_ids == expected_ids
    if not details["coverage_ok"]:
        missing = expected_ids - covered_ids
        extra = covered_ids - expected_ids
        if missing:
            errors.append(f"missing claim_ids: {missing}")
        if extra:
            errors.append(f"extra claim_ids: {extra}")

    # 4.5 Exclusion honor check
    expected_excl = {e["exclusion_id"] for e in sir.get("exclusions", [])}
    details["exclusion_ok"] = expected_excl.issubset(honored_ids)
    if not details["exclusion_ok"]:
        missing = expected_excl - honored_ids
        if missing:
            errors.append(f"missing exclusion_ids: {missing}")

    # 4.6 Forbidden keyword / regex check
    fi_records = forbidden_inference_records or []
    forbidden_violations = []
    for fi in fi_records:
        for kw in fi.get("pattern_keywords", []):
            if kw and kw in text:
                forbidden_violations.append(f"FI={fi['fi_id']} keyword={kw}")
        for pat in fi.get("pattern_regex", []):
            if re.search(pat, text):
                forbidden_violations.append(f"FI={fi['fi_id']} regex={pat}")
    details["forbidden_check_ok"] = len(forbidden_violations) == 0
    if forbidden_violations:
        errors.extend(forbidden_violations)

    # 4.7 Self-check
    sc_ok = (
        self_check.get("forbidden_content_absent", False) is True
        and self_check.get("all_claims_covered", False) is True
        and self_check.get("length_within_bounds", False) is True
    )
    details["self_check_ok"] = sc_ok
    if not sc_ok:
        errors.append(f"self_check failed: {self_check}")

    passed = len(errors) == 0
    return Layer1Result(passed, errors, details)


__all__ = ["validate_layer1"]
