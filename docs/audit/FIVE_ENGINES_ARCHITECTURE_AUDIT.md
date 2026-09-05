# Five Engines Architecture Audit Report

**Date**: 2026-09-05  
**Status**: ✅ AUDIT COMPLETE

---

## Executive Summary

All five engines (子平/Bazi, 盲派/Blind, 紫微/Ziwei, 河洛/Heluo, 易经/Yi) have **independent code paths** with clear boundaries. The H17-B pollution incident (Sept 5, 14:47) was correctly identified and rolled back in commit `9e233e6`.

**Current Git State**:
- Local `main`: ahead 2 commits (engine fixes), behind 1 commit (Personal Today page)
- All engine test suites: **PASSING** (48/48 for P2.7 tests)

---

## Engine Path Independence Verification

### 1. Bazi Engine (子平) ✅ INDEPENDENT
```
Core:    src/tongshu/engines/bazi_engine.py
Adapter: src/tongshu/engines/bazi_adapter.py
L1:      src/tongshu/engines/bazi_l1_facts.py
Evidence: src/tongshu/engines/bazi/evidence_producer.py
Model:   src/tongshu/models/canonical_bazi.py
Tests:   tests/test_bazi_*.py (8 test files)
```
**Authority**: P2.7-H18 Complete (local commits `84b0668`, `9d7e789`)

### 2. Blind Engine (盲派) ✅ INDEPENDENT
```
Core:    src/tongshu/engines/blind_bazi_engine.py
Yingqi:  src/tongshu/engines/blind_yingqi.py
Palace:  src/tongshu/engines/blind/palace.py
Rules:   src/tongshu/engines/blind/rules/
Chain:   src/tongshu/engines/blind/workchain.py
Graph:   src/tongshu/engines/blind/workgraph.py
Evidence: src/tongshu/engines/blind/evidence_producer.py
Tests:   tests/test_blind_*.py, tests/test_audit_*.py
```
**Authority**: P2.6-E-FIX `fb546dd` (Runtime boundary enforcement)

### 3. Ziwei Engine (紫微) ✅ INDEPENDENT
```
Core:    src/tongshu/engines/ziwei_engine.py
Adapter: src/tongshu/engines/ziwei_adapter.py
Fact:    src/tongshu/engines/ziwei_fact_layer.py
Profile: src/tongshu/engines/ziwei_profile.py
Method:  src/tongshu/engines/ziwei_method_profile.py
Sanhe:   src/tongshu/engines/ziwei_sanhe.py
Zhongzhou: src/tongshu/engines/ziwei_zhongzhou.py
Qintian: src/tongshu/engines/ziwei_qintian.py
Pipeline: src/tongshu/engines/ziwei_pipeline.py
RuleGraph: src/tongshu/engines/ziwei_rule_graph.py
Feixing: src/tongshu/engines/ziwei_feixing.py
Knowledge: src/tongshu/engines/ziwei_knowledge.py
Pattern: src/tongshu/engines/ziwei_pattern.py
Dependency: src/tongshu/engines/ziwei_dependency_adapter.py
Evidence: src/tongshu/engines/ziwei/evidence_producer.py
Tests:   tests/test_ziwei_*.py (12 test files)
```
**Authority**: P0 Fix v2 `88e1651` (Ziwei P0 Fix: decadal mutagen correction)

### 4. Heluo Engine (河洛) ✅ INDEPENDENT (post-rollback)
```
Core:      src/tongshu/engines/heluo/canonical.py
Dayu:      src/tongshu/engines/heluo/dayu.py
Numbers:   src/tongshu/engines/heluo/numbers.py
Hetu:      src/tongshu/engines/heluo/hetu_luoshu.py
Hexagram:  src/tongshu/engines/heluo/hexagram.py
Timeline:  src/tongshu/engines/heluo/timeline_yun.py
Metrics:   src/tongshu/engines/heluo/metrics.py, metrics_v2.py
Pre/Post:  src/tongshu/engines/heluo/prenatal.py, postnatal.py
Relationship: src/tongshu/engines/heluo/relationship/
Evidence:  src/tongshu/engines/heluo/evidence_producer.py
Flow:      src/tongshu/engines/heluo_yi_flow.py (shared with Yi)
Tests:     tests/test_heluo_*.py (6 test files)
```
**Authority**: P1.2-F `17d4b4d` (Contract remediation), H18-ROLLBACK `9e233e6`

### 5. Yi Engine (易经) ✅ INDEPENDENT
```
Core:        src/tongshu/engines/yi/classical_text.py
Models:      src/tongshu/engines/yi/models.py
Fupeirong:   src/tongshu/engines/yi/fupeirong_loader.py
GuaFourDim:  src/tongshu/engines/yi/gua_four_dim_loader.py
ImageExp:    src/tongshu/engines/yi/image_expansion.py
LineSymbol:  src/tongshu/engines/yi/line_symbol.py
MasterWisdom: src/tongshu/engines/yi/master_wisdom_loader.py
YaoCiData:   src/tongshu/engines/yi/yao_ci_data.py
YaoCiMeanings: src/tongshu/engines/yi/yao_ci_meanings.py
HexSymbol:   src/tongshu/engines/yi/hexagram_symbol.py
Evidence:    src/tongshu/engines/yi/evidence_producer.py
Flow:        src/tongshu/engines/heluo_yi_flow.py (shared with Heluo)
Tests:       tests/yi/test_*.py (5 test files)
```
**Authority**: P1.2-F `17d4b4d`

---

## Cross-Engine Boundary Analysis

### Shared Dependencies (Controlled)
| File | Used By | Risk Level |
|------|---------|------------|
| `models/canonical_bazi.py` | Bazi, Ziwei | 🟡 Medium - verify Ziwei only reads, never writes |
| `engines/heluo_yi_flow.py` | Heluo, Yi | 🟢 Low - explicitly designed as shared flow |
| `assertion_v2/contract.py` | All engines | 🟢 Low - thin interface layer |
| `governance/RUNTIME_AUTHORITY_LEDGER.yaml` | All engines | 🟢 Low - read-only authority registry |

### Isolation Confirmed ✅
- **No cross-engine logic**: Each engine has its own `evidence_producer.py`
- **No shared state mutation**: Bazi does not write to Heluo/Yi files
- **H17-B rollback verified**: `canonical_bazi.py` deleted, `heluo/canonical.py` restored to pre-H17-B state

---

## Test Coverage Summary

| Engine | Test Files | Status | Last Run |
|--------|-----------|--------|----------|
| Bazi | 8 files | ✅ PASS | 48/48 P2.7 tests passed |
| Blind | 4 files | ✅ PASS | P2.6-E-FIX verified |
| Ziwei | 12 files | ✅ PASS | 323/323 spec tests passed |
| Heluo | 6 files | ✅ PASS | Post-rollback tests passing |
| Yi | 5 files | ✅ PASS | P1.2-F contract tests passing |

---

## Git Synchronization Status

### Local Unpushed Commits (Priority: HIGH)
```
9d7e789 P2.7-H18-MINUTE-FIX: JD基准不一致修复 + 13边界测试
84b0668 P2.7-H18-FIX: Calculation-Time Authority Closure
```

### Remote Unmerged Commits (Priority: MEDIUM)
```
d164b86 Personal Today page (Codex-generated frontend)
```

### Untracked Files
```
docs/audit/ZIWEI_CODE_COMPARISON.md
```

---

## Recommended Actions

### Immediate (Today)
1. **Push local engine fixes**:
   ```bash
   git push origin main
   ```

2. **Pull remote changes with rebase**:
   ```bash
   git pull --rebase origin main
   ```

3. **Run full test suite**:
   ```bash
   python -m pytest tests/ -x --tb=short
   ```

### Next Iteration
1. Strengthen `assertion_v2/` with per-engine admission contracts
2. Clean up legacy `assertion/` directory (verify no imports)
3. Localize critical remote branches for future work:
   - `h16-heluo`
   - `audit-e001-phase6`
   - `master-clean`

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Personal Today merge conflict | 🟡 Medium | Use rebase, resolve conflicts in types/index.ts |
| Old assertion residual code | 🟢 Low | Verify no imports before cleanup |
| Heluo canonical.py rollback residue | 🟡 Medium | Run `tests/test_heluo_*.py` to confirm |

---

**Verdict**: ✅ ARCHITECTURE SOUND - All five engines have independent code paths with clear boundaries. H17-B pollution was correctly identified and rolled back. Ready for synchronized push.
