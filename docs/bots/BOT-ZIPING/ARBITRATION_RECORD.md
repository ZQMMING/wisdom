# BOT-ZIPING 生产准入裁决记录

**审计日期**: 2026-09-06  
**原始报告**: PRODUCTION_ADMISSION_REPORT.md  
**裁决状态**: CONDITIONAL PASS → 冻结暂缓

---

## 总裁决摘要

用户裁决：
> "Bazi 核心可以准入，但暂不做'最终 Calculation Freeze'。"

最终状态定义：
- **CALCULATION_CORE_VALIDATED**: YES
- **PRODUCTION_ADMITTED**: CONDITIONAL
- **CALCULATION_FREEZE**: DEFERRED

---

## 用户最终裁决 (B0-B12)

| B项 | 原始判定 | 用户裁决 | 处理 |
|-----|----------|----------|------|
| B0 Engine职责 | ✅ PASS | ✅ PASS | 可冻结 |
| B1 Frozen State | ✅ PASS | ✅ PASS* | 需补nested immutability检查 |
| B2 Input Contract | ⚠️ CONDITIONAL | 🟡 P2 Required Hardening | 不阻塞准入 |
| B3 死代码 | ⚠️ CONDITIONAL | 🟡 Legacy Purge | 确认后删除 |
| B4 fallback | ⚠️ CONDITIONAL | 🔴 **P1 Architecture Hardening** | **阻塞最终Freeze** |
| B5 全仓引用 | ✅ PASS | ✅ PASS | 无问题 |
| B6 Adapter边界 | ✅ PASS | ✅ PASS | 无问题 |
| B7 Canonical Ownership | ⚠️ CONDITIONAL | 🔴 **P1 - 架构问题** | **阻塞最终Freeze** |
| B8 P2测试覆盖 | ❌ FAIL | 🟡 CONDITIONAL / TEST GAP | Freeze前必须补 |
| B9 sys.exit | ✅ FIXED | ✅ PASS | 已修复 |
| B10 Boundary | ✅ PASS | ✅ PASS | 无问题 |
| B11 Evidence | ✅ EXPLAINED | ✅ PASS | 需固化inventory |
| B12 Admission | CONDITIONAL | 🟡 CONDITIONAL | 不阻塞当前准入 |

*B1需要后续补nested immutability检查（dict/list内部对象不可变性）

---

## 阻塞最终Calculation Freeze的三项

### 🔴 B4: sxtwl fallback → FAIL CLOSED

**问题**: 
- 当前 `_compute_simple()` 在无sxtwl时使用固定公式 `(month + 1) % 12`
- 该公式不考虑节气边界，会产生错误月柱
- 错误结果仍生成合法 `BaziChart`，下游全部建立其上 → **Silent Wrong Calculation**

**必须修复**:
```python
if not self._has_sxtwl:
    raise RuntimeError("sxtwl is required for accurate bazi computation")
```

### 🔴 B7: Canonical Bazi State Ownership

**问题**:
- `BlindBaziEngine` 默认创建独立 `BaziEngine()` 实例
- `ZiweiEngine` stub 直接创建 `BaziEngine().compute()` 2次
- 虽然当前确定性计算输出一致，但违反"唯一计算入口"架构原则

**必须修复**:
- 统一 `Canonical BaziChart` 所有权
- 下游引擎只读消费，不自行创建计算实例
- 使用依赖注入模式

### 🟡 B8: P2字段测试覆盖

**现状**:
- 15个P2字段功能验证全部OK（运行时测试通过）
- 但自动化测试覆盖率 0/15

**必须在最终Freeze前补齐**:
- 创建 `test_bazi_p2_fields.py`
- 覆盖所有15个衍生字段

---

## 下一步行动清单

### 立即执行 (P1阻塞项)
1. [ ] B4: 修改 `_compute_simple()` 为 fail-closed
2. [ ] B7: 统一Bazi引擎实例，下游只读消费

### Freeze前必须完成 (P2)
3. [ ] B8: 补齐P2字段测试覆盖
4. [ ] B2: solar_date输入契约显式校验
5. [ ] B3: 删除 `_recompute_month_with_datetime` 死代码
6. [ ] B11: 固化证据清单统计口径

### 最终Freeze验证
7. [ ] 129边界测试重新运行
8. [ ] Core tests 重新运行
9. [ ] P2 tests 运行
10. [ ] Replay/Determinism 验证
11. [ ] Downstream read-only audit

---

## 最终判定标准

当以下全部满足时，方可升级为 FULL PASS + Calculation Freeze:

```
BAZI CALCULATION
================
CALCULATION_INTEGRITY: PASS ✅
CANONICAL_STATE: PROVEN ✅ (B7修复后)
BOUNDARY_TESTS: PASS ✅
REPLAY_DETERMINISM: PASS (待验证)
DOWNSTREAM_RECALCULATION: NONE ✅ (B7修复后)
FALLBACK: FAIL_CLOSED ✅ (B4修复后)
EVIDENCE_INVENTORY: CONSISTENT ✅ (B11固化后)

PRODUCTION_ADMITTED: YES
CALCULATION_FREEZE: YES
```

---

*裁决记录 by BOT-MASTER | 2026-09-06*
