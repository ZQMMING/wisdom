# P0-1-C Fix Checklist - Updated

**Last Updated**: 2026-09-07  
**Commit**: `797e7743`

---

## P0-1-C Status: ✅ COMPLETE

| Item | Status | Notes |
|------|--------|-------|
| Fix-001: chart-only API | ✅ DONE | `assemble(case_id, chart, gender, target_year)` |
| Fix-001-B: birth_year NameError | ✅ DONE | From `chart.birth_datetime.year` |
| Fix-002: Hardcoded paths | ✅ DONE | All replaced with relative paths |
| Fix-006: Signal.domain | ✅ DONE | Field added to Signal/CanonicalSignal |
| Fix-007: Judgment scaffold | ✅ DONE | 5 domain classes created |
| P0-1-C Phase 1 (BAZI) | ✅ DONE | Pillar.stem_ten_god added |
| P0-1-C Phase 3 (ZIPING) | ✅ DONE | Consumes BAZI fields |
| **P0-1-C-FIX-2** | ✅ **DONE** | **All deterministic tables removed** |

---

## Remaining P0 Items

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| P0-2: Judgment algorithms | 🔴 BLOCKED | BOT-ZIPING | Needs full algorithm design |
| P0-3~P0-5 | 🟡 PENDING | Various | Await BOT-MASTER ruling |
| P0-6: YONGSHEN algorithm | 🔴 BLOCKED | BOT-ZIPING | Returns UNKNOWN placeholder |
| P0-7: E2E integration | 🔴 BLOCKED | BOT-ZIPING | Requires Phase 2 first |

---

## Phase 2: Temporal Engine (BOT-TIME)

**Status**: ⏳ PENDING - Not yet started

**Tasks:**
- [ ] Implement `TimeEngine.compute_temporal_context()`
- [ ] Add `TemporalContext.target_year_pillar`
- [ ] Add `TemporalContext.target_year_stem_ten_god`
- [ ] Update ContextAssembler to consume from TemporalContext
- [ ] Add tests for year pillar calculation

---

## Phase 3: Judgment Algorithms (BOT-ZIPING)

**Status**: ⏳ SCAFFOLD ONLY - Algorithms need implementation

**Tasks:**
- [ ] WANGSHUAIJudgment: Complete 得令+得地+得势+寒暖燥湿 algorithm
- [ ] GEJUJudgment: Implement 月令→透干→成格/破格 chain
- [ ] YONGSHENJudgment: Replace UNKNOWN with real algorithm
- [ ] SHISHENJudgment: Implement semantic interpretation
- [ ] SHIJIANJudgment: Implement event judgment

---

## Git History

```
797e7743 ZP: P0-1-C-FIX-2 Complete - Remove ZIPING deterministic relation tables
1c743d81 ZP: P0-1-C 移除临时fallback，直接消费BAZI字段
4a3a1b12 ZP: P0-1-C Fix - ZIPING端改为消费BAZI字段
3c27746f P0-1-C Phase 1: BAZI 端扩展 stem_ten_god
bb4e6a32 P0: Fix-006/007 (domain field + judgment scaffold)
138c82e2 ZP: Fix-001-B 修复 birth_year NameError
56d6f97f P0: Fix-001/002 (chart-only API, hardcoded paths)
```

---

## Test Results

```
========================= 25 passed, 1 warning in 0.31s =========================
```

| Test File | Result |
|-----------|--------|
| test_bazi_engine.py | 12/12 PASS |
| test_phase3_p0.py | 1/1 PASS |
| test_rule_engine.py | 12/12 PASS |

---

## Next Steps

1. **Phase 2**: Temporal Engine implementation (BOT-TIME)
2. **Phase 3**: Judgment algorithm implementation (BOT-ZIPING)
3. **Pending**: Wait for BOT-MASTER arbitration on P0-2 through P0-5

---

**Note**: This checklist is updated after each commit. GitHub main is the source of truth.
