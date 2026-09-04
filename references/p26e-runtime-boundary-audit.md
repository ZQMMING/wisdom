# P2.6-E Runtime Boundary Audit

**Date**: 2026-09-06
**Status**: 🔴 VIOLATIONS FOUND

---

## Audit Method

Traced `calc_five_element_balance` output through production call graph:

```
bazi_engine.py:calc_five_element_balance()
    ↓ returns dict with balance info
    ↓ assigned to chart.five_element_imbalance
    ↓ consumed by multiple engines
```

---

## Findings

### Violation 1: 🔴 HIGH — Blind Engine Direct Signal Creation

**Location**: `src/tongshu/engines/blind_bazi_engine.py:575`

**Code**:
```python
if getattr(chart, 'five_element_imbalance', False) or body_chonged:
    signals.append(CanonicalSignal(
        event_type="HEALTH_ISSUE",
        severity="high",
        ...
    ))
```

**Problem**: `five_element_imbalance` (AUXILIARY_SIGNAL) directly creates `CanonicalSignal(HEALTH_ISSUE)` — this is Judgment-layer signal creation from an auxiliary calculation.

**Contract Violation**: 
- ✅ `AUTHORITY_STATUS = NOT_AUTHORIZED`
- ✅ `ROLE = AUXILIARY_SIGNAL`
- ❌ But output enters `CanonicalSignal` (Judgment layer)

---

### Violation 2: 🔴 HIGH — Di Tian Sui Strength Path Input

**Location**: `src/tongshu/system_schemas/system_school_contract.py:133`

**Code**:
```python
strength_path = calculate_strength_path(
    bazi=five_element_balance,  # ← AUXILIARY_SIGNAL feeding Judgment input
    ...
)
```

**Problem**: `five_element_balance` result fed into `strength_path` calculation, which then feeds into Di Tian Sui judgment system.

**Contract Violation**: AUXILIARY_SIGNAL → Judgment input chain

---

### Violation 3: 🟡 MEDIUM — Heluo Engine Cross-Reference

**Location**: `src/tongshu/engines/signal_engine.py:97-103`

**Code**:
```python
# Five element imbalance affects Heluo relationships
if five_element_balance:
    # Affects cross-engine calculations
    ...
```

**Problem**: Used in Heluo (河洛) engine for relationship calculations. While not directly creating signals, it influences cross-engine logic.

**Contract Violation**: Minor — affects cross-engine state but not direct Judgment

---

## Root Cause

The downgrade in P2.6-D (`8c47213`) was **declarative only**:
- ✅ Added docstring warnings
- ✅ Added metadata constants
- ❌ Did NOT add runtime enforcement
- ❌ Did NOT remove production call sites

**Lesson**: Architecture markers without runtime enforcement are insufficient.

---

## Required Fixes

### Option A: Complete Isolation (Recommended)

1. Remove `five_element_imbalance` condition from `blind_bazi_engine.py:575`
2. Replace with explicit engineering-only log/warning
3. Remove `five_element_balance` input from `calculate_strength_path`
4. Mark as `engineering_signals` separate from `canonical_signals`

### Option B: Engineering Signal Layer

1. Add `engineering_signals` field to BaziChart
2. Move health-related signals to engineering layer
3. Keep canonical signals pure (only from AUTHORIZED calculations)
4. Explicit contract: canonical ≠ engineering

---

## Test Impact

Existing tests may rely on current behavior. Must verify:
- `test_blind_engine_health_signals` — needs update
- `test_strength_path_input` — needs refactoring
- New test: `test_auxiliary_signal_not_in_canonical` — should fail currently

---

## Conclusion

**Runtime Boundary Audit reveals critical architecture violation.**

The P2.6-D downgrade was correct in intent but incomplete in execution. **Docstring warnings are not enforcement.**

**Next action**: Fix violations before proceeding with sxtwl/起运/大运 investigation.
