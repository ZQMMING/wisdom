"""Layer2 — 嵌入语义相似度。

Per output_validation.md §5. Computes cosine similarity between rendered
output and each atomic claim; passes if min similarity >= threshold.

For v1.0 demo: simplified character-overlap similarity. Real impl uses
embedding model.

T501: degradation-aware — claims the renderer declared dropped (top_k
degradation) are excluded from the entailment set.

依赖：result.py。

Version: 1.0.0
Created: 2026-08-20 (Phase 2 / Step 8)
Migrated from: validation/layer2.py (full file)
"""

from __future__ import annotations

from .result import Layer2Result


# 降低阈值以适应 char-overlap（实际实现用 embeddings）
THRESHOLD: float = 0.20


def _char_overlap_similarity(a: str, b: str) -> float:
    """Approximate character-overlap similarity (Jaccard: inter/union).

    Real impl will use embedding cosine similarity.
    For v1.0 demo this provides a fast deterministic stand-in.
    """
    a_set = set(a)
    b_set = set(b)
    if not a_set or not b_set:
        return 0.0
    intersection = a_set & b_set
    union = a_set | b_set
    return len(intersection) / len(union) if union else 0.0


def validate_layer2(
    rendered_text: str,
    sir: dict,
    degradation: dict | None = None,
) -> Layer2Result:
    """Run Layer 2 semantic similarity check.

    Per output_validation.md §5.

    T501: when the renderer declares a top_k degradation, the dropped
    claims are out of scope for entailment — the renderer was explicitly
    told to omit them. Only kept claims are checked.
    """
    claims = sir.get("atomic_claims", [])
    if not claims:
        return Layer2Result(
            passed=True,
            min_similarity=1.0,
            threshold=THRESHOLD,
            details={"reason": "no claims to check"},
        )

    dropped = set((degradation or {}).get("dropped_claim_ids", []))
    kept = [c for c in claims if c.get("claim_id") not in dropped]
    if not kept:
        # Everything declared dropped — nothing to entail.
        return Layer2Result(
            passed=True,
            min_similarity=1.0,
            threshold=THRESHOLD,
            details={"reason": "all claims declared dropped", "skipped_claim_ids": sorted(dropped)},
        )

    sims = []
    for c in kept:
        claim_text = c.get("claim", "")
        sim = _char_overlap_similarity(rendered_text, claim_text)
        sims.append((c.get("claim_id", ""), sim))

    min_sim = min(s for _, s in sims) if sims else 1.0
    passed = min_sim >= THRESHOLD

    return Layer2Result(
        passed=passed,
        min_similarity=min_sim,
        threshold=THRESHOLD,
        details={
            "claim_similarities": sims,
            "skipped_claim_ids": sorted(dropped) if dropped else [],
        },
    )


__all__ = ["validate_layer2", "_char_overlap_similarity", "THRESHOLD"]
