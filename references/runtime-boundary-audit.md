# Runtime Boundary Audit Methodology

**Created**: 2026-09-06
**Purpose**: Ensure AUXILIARY_SIGNAL/ENGINEERING_HEURISTIC functions are properly isolated from Judgment layer

---

## Why This Matters

After P2.6-D (`8c47213`), `calc_five_element_balance` was marked as:
- `AUTHORITY_STATUS = NOT_AUTHORIZED`
- `ROLE = AUXILIARY_SIGNAL`
- Docstring warning added

**But runtime audit found 3 violations** where the function output still enters Judgment signals.

**Lesson**: Architecture markers without runtime enforcement are insufficient.

---

## Audit Procedure

### Step 1: Identify Call Sites

Search production code (NOT tests) for all invocations:

```bash
# Example: Find all uses of five_element_imbalance
rg -n "five_element_imbalance" src/ --type py
```

### Step 2: Trace Output Flow

For each call site, determine:
1. Where does the result go?
   - Local variable?
   - Chart field?
   - Signal object?
2. What consumes that field?
   - CanonicalSignal? ❌
   - RuleResolver? ❌
   - Assertion/Judgment? ❌
   - Engineering log only? ✅

### Step 3: Check Contract Compliance

| Input | Output | Contract |
|-------|--------|----------|
| AUTHORIZED | CanonicalSignal | ✅ OK |
| NOT_AUTHORIZED/AUXILIARY | CanonicalSignal | ❌ VIOLATION |
| NOT_AUTHORIZED/AUXILIARY | Engineering log | ✅ OK |
| NOT_AUTHORIZED/AUXILIARY | Cross-engine input | 🟡 MEDIUM |

### Step 4: Report Findings

Template:
```markdown
## Violation N: [Severity] — [Title]

**Location**: `path/to/file.py:line`

**Code**:
```python
[relevant snippet]
```

**Problem**: [what contract is violated]

**Fix**: [suggested remediation]
```

---

## Common Violation Patterns

### Pattern 1: Direct Signal Creation

```python
if chart.five_element_imbalance:
    signals.append(CanonicalSignal(
        event_type="HEALTH_ISSUE",
        ...
    ))
```

**Fix**: Remove from canonical signal generation. Use engineering signal layer instead.

### Pattern 2: Judgment Input Contamination

```python
strength_path = calculate_strength_path(
    bazi=five_element_balance,  # ← AUXILIARY_SIGNAL in canonical input
    ...
)
```

**Fix**: Separate engineering inputs from canonical inputs.

### Pattern 3: Cross-Engine Influence

```python
# In Heluo engine
if five_element_balance:
    # Affects other calculations
    ...
```

**Fix**: Document as cross-engine reference. May need isolation.

---

## Test Pattern

```python
def test_auxiliary_signal_not_in_canonical_judgment():
    """Verify AUXILIARY_SIGNAL output does not enter CanonicalSignal."""
    chart = compute_with_imbalance_case()
    signals = generate_canonical_signals(chart)
    
    for sig in signals:
        assert "five_element_imbalance" not in str(sig.event_type), \
            f"AUXILIARY_SIGNAL must not produce CanonicalSignal: {sig}"
```

---

## After Fix Verification

1. Re-run runtime boundary audit
2. Confirm all ❌ violations resolved
3. Run full test suite
4. Document fix in commit

---

## References

- P2.6-D: `8c47213` — Five element balance downgrade
- P2.6-E: `8851ef7` — This audit report
- `bazi-engine-verification` skill: Phase 11
