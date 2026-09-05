# Runtime Boundary Audit Patterns

## Core Principle: Static Check ≠ Runtime Proof

```
源代码里没有字符串  ≠  运行时不会产生这个影响
```

Example: code may not contain `bazi.five_element_balance[` but still compute it via helper function:
```python
balance = compute_balance(chart)      # not in source check
result = transform(balance)            # not in source check either
```

## Three-Layer Test Structure

### Layer 1: Static Guard (源码级隔离验证)
Proves absence of specific string patterns in production code.

```python
import inspect
source = inspect.getsource(extract_heluo_context)
assert 'bazi.five_element_balance[' not in source
```

**What it proves**: This specific code pattern doesn't exist.
**What it doesn't prove**: The output won't be affected by balance changes.

### Layer 2: Runtime Behavioral Test (行为不变量测试)
Mutates input, runs full computation, compares outputs.

```python
# Baseline
result_normal = blind_engine.compute((1984, 1, 1, 0), gender="male")

# Mutated
def patched_compute(solar_date, gender="male"):
    chart = original_compute(solar_date, gender=gender)
    return replace(chart, five_element_imbalance=True,
                  five_element_balance=EXTREME_BALANCE)

with patch.object(engine, 'compute', patched_compute):
    result_mutated = blind_engine.compute((1984, 1, 1, 0), gender="male")

# Invariant
assert result_normal.ti_branches == result_mutated.ti_branches
```

**What it proves**: Changing balance does NOT change canonical signal output.

### Layer 3: Invariant Assertion (字段级对比)
Specific output fields must remain identical across mutations.

```python
assert result_normal.ti_branches == result_mutated.ti_branches
assert result_normal.yong_branches == result_mutated.yong_branches
assert len([s for s in result_normal.signals if s.event_type == "HEALTH_ISSUE"]) == \
       len([s for s in result_mutated.signals if s.event_type == "HEALTH_ISSUE"])
```

## Frozen Dataclass Mutation Testing Pattern

**Problem**: `BaziChart` is frozen dataclass. Engines re-compute internally.
**Solution**: Instance-level monkey-patch with original call.

```python
from unittest.mock import patch
from dataclasses import replace

engine = BaziEngine()
blind_engine = BlindBaziEngine(engine)

# Save original method
original_compute = engine.compute

def patched_compute(solar_date, gender="male"):
    chart = original_compute(solar_date, gender=gender)
    return replace(chart, five_element_imbalance=True,
                  five_element_balance=EXTREME_BALANCE)

# Patch instance method, NOT class method
with patch.object(engine, 'compute', patched_compute):
    result = blind_engine.compute((1984, 1, 1, 0), gender="male")
```

**Common pitfall**: Using `patch.object(BaziEngine, 'compute', ...)` causes recursion because patched method calls itself.

## Violation Detection Patterns

| Pattern | Severity | Detection Method |
|---------|----------|-----------------|
| Direct CanonicalSignal creation | 🔴 HIGH | Runtime mutation test → output differs |
| Feeding into Judgment input | 🔴 HIGH | Config inspection + runtime test |
| Cross-engine usage | 🟡 MEDIUM | Call graph tracing |
| Only in auxiliary logging | 🟢 OK | Source check passes, no signal output |

## Test Quality Anti-Patterns

### ❌ Bad: Static-only test
```python
def test_isolation_via_source_check():
    source = inspect.getsource(extract_heluo_context)
    assert 'five_element_balance[' not in source  # Only proves string absent
```

### ❌ Bad: Weakened invariant
```python
def test_boundary_isolation():
    result = extract_heluo_context(None, chart)
    assert result == {}  # Trivially true when heluo_result=None
```

### ❌ Bad: Comparing different charts
```python
def test_balance_doesnt_affect_signals():
    result1 = blind_engine.compute((1984, 1, 1, 0))  # Different birth year
    result2 = blind_engine.compute((1985, 1, 1, 0))  # Different pillars entirely
    # This proves nothing about balance isolation
```

### ✅ Good: True mutation invariant
```python
def test_balance_mutation_invariant():
    result_normal = blind_engine.compute(birth, gender)
    result_mutated = compute_with_mutated_balance(birth, gender)
    
    assert result_normal.ti_branches == result_mutated.ti_branches
    assert result_normal.yong_branches == result_mutated.yong_branches
    # ... all canonical outputs identical
```

## Commit Quality Signal

When user reviews a fix commit:
- 🟢 Production fix correct + Runtime tests strong → PROVISIONAL PASS
- 🟡 Production fix correct + Tests weakened → CONDITIONAL PASS, requires follow-up
- 🔴 Production fix correct + Tests only static → HOLD, needs mutation tests

**Rule**: Never replace behavioral test with static check, even if production code changed.
