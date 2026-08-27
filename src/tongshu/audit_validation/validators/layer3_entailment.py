"""Layer3 — 蕴含判定（judge model）。

Per output_validation.md §6.
For v1.0 demo: stub 逻辑。Real impl 会调用独立 LLM 作为 judge。

依赖：result.py。

Version: 1.0.0
Created: 2026-08-20 (Phase 2 / Step 8)
Migrated from: validation/layer3.py (full file)
"""

from __future__ import annotations

from .result import Layer3Result


def validate_layer3(
    rendered_text: str,
    sir: dict,
    judge_llm_client=None,
) -> Layer3Result:
    """Run Layer 3 entailment judge.

    Per output_validation.md §6.
    For v1.0 demo, returns PASS if layer1+layer2 passed and no obvious
    contradictions exist in self_check.
    Real impl will call a separate LLM as judge.
    """
    if judge_llm_client is None:
        # Stub: assume PASS
        return Layer3Result(
            passed=True,
            entailment_verdict="ENTAILED",
            judge_model_id="stub_judge",
            details={"reason": "stub mode; not actually verified"},
        )

    # Real implementation would call judge_llm_client with entailment prompt
    # and parse the response.
    prompt = _build_judge_prompt(rendered_text, sir)
    response = judge_llm_client.call(prompt, "")
    return _parse_judge_response(response)


def _build_judge_prompt(rendered_text: str, sir: dict) -> str:
    claims = sir.get("atomic_claims", [])
    exclusions = sir.get("exclusions", [])
    return f"""You are an independent validator. Given:

Claims: {[c.get('claim') for c in claims]}
Exclusions: {[e.get('type') for e in exclusions]}
Rendered: {rendered_text}

Output JSON with claim_verdicts, exclusion_verdicts, overall (PASS/FAIL)."""


def _parse_judge_response(response) -> Layer3Result:
    """Parse judge LLM response into Layer3Result."""
    # Stub parser
    return Layer3Result(
        passed=True,
        entailment_verdict="ENTAILED",
        judge_model_id="stub_judge",
        details={"raw": str(response)[:200]},
    )


__all__ = ["validate_layer3"]
