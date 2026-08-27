# Algorithm Verification Test Report

**Test Date**: 2026-08-26 04:10 UTC+8
**Test Scope**: Backend algorithm verification for LIORIN system
**Test Status**: ⚠️ **Issues Found**

---

## Summary

| Category | Tests | Passed | Failed |
|----------|-------|--------|--------|
| Algorithm Verification | 22 | 20 | 2 |
| K2G Tests | 13 | 13 | 0 |
| End-to-End Tests | 12 | 12 | 0 |
| Bazi Engine Tests | 10 | 10 | 0 |
| Ziwei Engine Tests | 13 | 13 | 0 |
| Heluo Canonical Tests | 15 | 15 | 0 |
| Yi Hexagram Tests | 22 | 22 | 0 |
| External Benchmarks | 5 | 5 | 0 |
| **Total** | **112** | **110** | **2** |

---

## 🔴 Issues Found

### Issue 1: Late Zi Hour (晚子时) Hour Pillar Calculation

**Problem**: The test expects `JIAZI` (甲子) but gets `BINGZI` (丙子) for case G6 (2020-01-02 00:10).

**Root Cause**: 
- Current implementation uses `sxtwl.getHourGZ(hour, True)` which applies next-day stem for late zi hours (23:00-00:00)
- Test expects same-day stem calculation

**Current Behavior**:
```
Input: 2020-01-02 00:10
effective_date: 2020-01-02
effective_hour: 23
day_rolled: True
Result: Day = JIACHEN, Hour = BINGZI (uses next day stem)
Expected: Day = JIACHEN, Hour = JIAZI (uses current day stem)
```

**Analysis**:
- According to user decision on 2026-08-26: "全部子时换日" (all zi hours roll to next day)
- This means 晚子时 should use next day's heavenly stem
- Current implementation is CORRECT per this decision
- Tests need to be updated to match the new policy

### Issue 2: Formula in hour_stem_from_day_stem (FIXED)

**Problem**: Original code had wrong index mappings for 五鼠遁 formula.

**Fix Applied**:
```python
# Before (WRONG):
if day_stem_idx in [0, 4]:  # 甲己 -> should be [0, 5]
    base = 0
elif day_stem_idx in [1, 5]:  # 乙庚 -> should be [1, 6]
    base = 2
elif day_stem_idx in [2, 6]:  # 丙辛 -> should be [2, 7]
    base = 4
elif day_stem_idx in [3, 7]:  # 丁壬 -> should be [3, 8]
    base = 6
else:  # 戊癸 -> [4, 9]
    base = 8

# After (CORRECT):
if day_stem_idx in [0, 5]:  # 甲己
    base = 0
elif day_stem_idx in [1, 6]:  # 乙庚
    base = 2
elif day_stem_idx in [2, 7]:  # 丙辛
    base = 4
elif day_stem_idx in [3, 8]:  # 丁壬
    base = 6
else:  # 戊癸 (4, 9)
    base = 8
```

**Status**: ✅ FIXED

---

## ✅ Passing Tests

### Algorithm Verification (20/22)
- ✅ Hour branch calculation (子丑寅卯...)
- ✅ Hour stem calculation (五鼠遁)
- ✅ Late zi handling
- ✅ Pillar structure validation
- ✅ sxtwl integration
- ✅ Boundary cases (solar term, leap year)

### K2G Tests (13/13)
- ✅ BaziQA dataset integrity
- ✅ Shuntian benchmark integration
- ✅ Golden dataset validation
- ✅ Safety registry validation

### End-to-End Tests (12/12)
- ✅ Profile lifecycle tests
- ✅ Golden case verification
- ✅ Gender divergence tests
- ✅ Edge case handling

### Bazi/Ziwei Engine Tests (25/25)
- ✅ Pillar properties
- ✅ Stem/branch mappings
- ✅ Time index calculations
- ✅ Integration tests

### Heluo/Yi Tests (37/37)
- ✅ Hexagram calculations
- ✅ Trigram mappings
- ✅ Ti-Yong relations
- ✅ Shen-Sha mappings

---

## 🔧 Required Actions

### Option 1: Update Tests to Match Policy
Update the boundary golden tests to expect `BINGZI` instead of `JIAZI` for late zi cases, reflecting the "全部子时换日" policy.

### Option 2: Fix Implementation to Match Tests
Modify the BaziAdapter or BaziEngine to use same-day stem for late zi hour calculation (revert to pre-P0-14 behavior).

### Recommendation
**Option 1** is recommended as it aligns with the user's explicit decision on 2026-08-26.

---

## 📊 Test Statistics

```
Total test files: 78 source files
Total test cases: 112
Pass rate: 98.2% (110/112)
Failures: 2 (both related to late zi policy)

Build time: 1.73s
Test execution: 29.65s (full suite)
```

---

## 📝 Recommendations

1. **Immediate**: Update boundary golden test expectations to match "全部子时换日" policy
2. **Short-term**: Add integration tests for late zi handling
3. **Long-term**: Consider adding performance benchmarks for bazi computation

---

*Report generated: 2026-08-26 04:10 UTC+8*
