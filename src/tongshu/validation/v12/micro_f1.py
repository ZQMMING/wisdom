"""Micro-F1 Calculator — primary metric per V1.2 Contract.

Micro-F1 = 2*TP / (2*TP + FP + FN)
         = precision == recall == F1 (when computed globally)

CRITICAL: NOT macro-F1 (mean of per-case F1s).
CRITICAL: NOT mean of per-event F1s.

V1.2 mandates Micro-F1 as the ONLY primary F1 metric.
Macro-F1 may exist but only as auxiliary.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Set, Tuple


def _compute_tp_fp_fn(
    predictions: Iterable[Set[str]],
    ground_truths: Iterable[Set[str]],
) -> Tuple[int, int, int]:
    """Compute global TP, FP, FN from prediction/ground-truth sets.

    Args:
        predictions: iterable of predicted event IDs per case
        ground_truths: iterable of ground truth event IDs per case

    Returns:
        (tp, fp, fn)
    """
    tp = fp = fn = 0
    for pred, gt in zip(predictions, ground_truths):
        pred_set = set(pred) if pred else set()
        gt_set = set(gt) if gt else set()
        tp += len(pred_set & gt_set)
        fp += len(pred_set - gt_set)
        fn += len(gt_set - pred_set)
    return tp, fp, fn


def micro_precision(predictions: Iterable[Set[str]],
                    ground_truths: Iterable[Set[str]]) -> float:
    """Global precision = TP / (TP + FP)."""
    tp, fp, _ = _compute_tp_fp_fn(predictions, ground_truths)
    denom = tp + fp
    return tp / denom if denom > 0 else 0.0


def micro_recall(predictions: Iterable[Set[str]],
                 ground_truths: Iterable[Set[str]]) -> float:
    """Global recall = TP / (TP + FN)."""
    tp, _, fn = _compute_tp_fp_fn(predictions, ground_truths)
    denom = tp + fn
    return tp / denom if denom > 0 else 0.0


def micro_f1(predictions: Iterable[Set[str]],
             ground_truths: Iterable[Set[str]]) -> float:
    """Micro-F1 = 2*P*R / (P+R) = 2*TP / (2*TP + FP + FN).

    When both precision and recall are zero, returns 0.0.
    """
    tp, fp, fn = _compute_tp_fp_fn(predictions, ground_truths)
    denom = 2 * tp + fp + fn
    if denom == 0:
        return 0.0
    return (2 * tp) / denom


def macro_f1(predictions: Iterable[Set[str]],
             ground_truths: Iterable[Set[str]]) -> float:
    """Macro-F1 = mean of per-case F1s (AUXILIARY ONLY).

    Each case's F1 = 2*tp_i / (2*tp_i + fp_i + fn_i).
    Cases with denominator 0 contribute 0.0.
    """
    f1s: List[float] = []
    for pred, gt in zip(predictions, ground_truths):
        pred_set = set(pred) if pred else set()
        gt_set = set(gt) if gt else set()
        tp = len(pred_set & gt_set)
        fp = len(pred_set - gt_set)
        fn = len(gt_set - pred_set)
        denom = 2 * tp + fp + fn
        f1s.append((2 * tp) / denom if denom > 0 else 0.0)
    return sum(f1s) / len(f1s) if f1s else 0.0


def jaccard_match_rate(predictions: Iterable[Set[str]],
                       ground_truths: Iterable[Set[str]]) -> float:
    """Jaccard similarity = |pred ∩ gt| / |pred ∪ gt| per case, averaged."""
    scores: List[float] = []
    for pred, gt in zip(predictions, ground_truths):
        pred_set = set(pred) if pred else set()
        gt_set = set(gt) if gt else set()
        union = pred_set | gt_set
        if not union:
            scores.append(1.0)  # both empty = perfect match
        else:
            scores.append(len(pred_set & gt_set) / len(union))
    return sum(scores) / len(scores) if scores else 0.0


# ─── Convenience: list-of-lists interface ─────────────────────────────────────

def compute_all_metrics(
    predictions: List[List[str]],
    ground_truths: List[List[str]],
) -> dict:
    """Compute all metrics from list-of-lists input.

    Returns dict with:
        micro_f1, micro_precision, micro_recall,
        macro_f1, jaccard_match_rate
    """
    pred_sets = [set(p) for p in predictions]
    gt_sets = [set(g) for g in ground_truths]

    return {
        "micro_f1": micro_f1(pred_sets, gt_sets),
        "micro_precision": micro_precision(pred_sets, gt_sets),
        "micro_recall": micro_recall(pred_sets, gt_sets),
        "macro_f1": macro_f1(pred_sets, gt_sets),
        "jaccard_match_rate": jaccard_match_rate(pred_sets, gt_sets),
    }


# ─── Invariant: Micro-F1 is primary, never Macro-F1 ──────────────────────────

def assert_micro_primary(micro: float, macro: float) -> None:
    """Verify that micro_f1 != macro_f1 is allowed (they often differ).

    The contract requires micro_f1 to be used as overall_f1, not macro_f1.
    This function just documents the invariant — actual enforcement is in tests.
    """
    pass
