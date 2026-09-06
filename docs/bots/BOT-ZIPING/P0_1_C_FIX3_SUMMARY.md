# P0-1-C-FIX-3: Year Pillar Fail-Closed Boundary

**Commit**: pending  
**Status**: 🔴 BLOCKED - Requires BOT-MASTER review

---

## Summary

P0-1-C-FIX-2 removed the explicit fallback calculation, but the code still allowed `year_pillar=None` to silently pass with `None` values. P0-1-C-FIX-3 enforces **fail-closed** behavior: if `chart.year_pillar` is missing, raise `ValueError` immediately.

---

## Changes Made

### 1. context_assembler.py

**Before:**
```python
year_pillar = getattr(chart, 'year_pillar', None)
year_stem = getattr(year_pillar, 'heavenly_stem', None) if year_pillar else None
year_branch = getattr(year_pillar, 'earthly_branch', None) if year_pillar else None
year_stem_ten_god = getattr(year_pillar, 'stem_ten_god', None) if year_pillar else None

# Fallback: calculate year from chart data if needed
if not year_branch:
    base_year = 1984
    offset = (target_year - base_year) % 60
    # ... calculate year pillar (VIOLATION)
```

**After:**
```python
year_pillar = getattr(chart, 'year_pillar', None)

# P0-1-C-FIX-3: 强制 fail-closed
if year_pillar is None:
    raise ValueError(
        "chart.year_pillar 不能为 None。\n"
        "流年干支是确定性事实，必须由 BAZI/Temporal Engine 计算后传入。\n"
        "ZIPING 不拥有 Year Pillar 的计算权。"
    )

year_stem = year_pillar.heavenly_stem
year_branch = year_pillar.earthly_branch
year_stem_ten_god = year_pillar.stem_ten_god
```

### 2. temporal_context_contract.py

Added missing `dayun_year_harms` field to `YearContext`:
```python
dayun_year_harms: list[str] = field(default_factory=list)  # 流年与大运害
```

### 3. test_p0_1c_negative.py (NEW)

5 negative tests enforcing ZIPING boundary:
- `test_ziping_does_not_compute_year_pillar`: Fail-closed test
- `test_no_local_year_cycle_formula`: No `% 60` / `base_year = 1984`
- `test_no_local_ten_god_for_year`: No `ten_god(day_master, year_stem)`
- `test_year_context_requires_chart`: Must accept chart parameter
- `test_no_branh_relation_tables`: No local BRANCH_CLASH/HARM/COMBINATION tables

---

## Architecture Boundary (After FIX-3)

```
BAZI Frozen Chart
├── year_pillar                ← Mandatory
├── month_pillar.stem_ten_god  ← Consumed
├── day_pillar.stem_ten_god    ← Consumed
├── hour_pillar.stem_ten_god   ← Consumed
├── branch_clash_map           ← Consumed
├── branch_he_map              ← Consumed
├── branch_harm_map            ← Consumed
└── luck_pillars[]             ← Consumed

ZIPING ContextAssembler
├── assemble_natal_context()   ← Consumes BAZI fields
├── assemble_dayun_context()   ← Consumes chart.luck_pillars
└── assemble_year_context()    ← REQUIRES chart.year_pillar
                              ← FAILS with ValueError if None
                              ← NO fallback calculation allowed
```

---

## Test Results

```
=== P0-1-C 负向测试 ===
✅ PASS: Year pillar 不应 fallback 计算
✅ PASS: 无本地 60年循环公式
✅ PASS: 无 Year ten_god 重算
✅ PASS: Year context 需 chart 参数
✅ PASS: 无本地 branch relation 表

总计: 5/5 PASS

25 passed (existing tests)
30 total: 30 PASS
```

---

## Remaining: Phase 2 Temporal Engine (BOT-TIME)

**Status**: ⏳ PENDING

**Task**: Implement proper year pillar calculation
```
target_year
    ↓
Temporal Engine (BOT-TIME)
    ↓
TemporalContext.target_year_pillar
    ↓
ContextAssembler.assemble_year_context()
```

**After Phase 2 implementation:**
- Remove `chart.year_pillar` dependency from ZIPING
- Use `temporal_context.target_year_pillar` instead
- Update `assemble()` signature to accept `temporal_context`

---

## GIT History

```
797e7743 ZP: P0-1-C-FIX-2 Complete - Remove ZIPING deterministic relation tables
b8a1c007 ZP: P0-1-C-FIX-2 Documentation
[NEW]   ZP: P0-1-C-FIX-3 - Year pillar fail-closed boundary
```

---

## Next Actions

1. ✅ Fix-3 executed locally
2. ⏳ Commit & push to origin/main
3. ⏳ Notify BOT-MASTER for review
4. ⏳ Transfer task to BOT-TIME for Phase 2 (Temporal Engine)

---

**Note**: This fix completes P0-1-C boundary enforcement. ZIPING no longer has any deterministic year pillar calculation. The only remaining task is Phase 2 (BOT-TIME) to provide the canonical year pillar source.
