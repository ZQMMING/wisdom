# BOT-ZIPING 架构修复任务单 (A→B→再解冻)

## 总裁决指令

**用户裁决**: A → B → 再解冻  
**执行顺序**: B4 → 测试 → B7 → 测试 → B8 → 完整Replay → 再审

---

## 禁止事项 ⛔

在当前流程完成前，**严格禁止**:
- ❌ 不做 Bazi 算法重写
- ❌ 不增加新的 Bazi 判断逻辑
- ❌ 不把 heuristic 升级成权威信号
- ❌ 不让 ZiPing/Blind 在 Bazi 上自行增加计算
- ❌ 不宣布 CALCULATION_FREEZE: YES

---

## 执行计划

### Phase A1: B4 - sxtwl fallback → FAIL CLOSED

**目标**: 
- sxtwl可用 → 正常计算
- sxtwl不可用 → FAIL CLOSED → 不生成可用于生产的BaziChart
- 禁止保留 `_compute_simple()` 作为生产降级路径

**步骤**:
1. 定位 `_compute_simple()` 方法 (bazi_engine.py)
2. 确认当前fallback逻辑
3. 修改为fail-closed模式
4. 编写单元测试验证
5. 运行129边界测试确认无回归

---

### Phase A2: B7 - Canonical Bazi State Ownership

**目标**:
- CalculationContext → BaziEngine → 唯一Canonical BaziChart → Frozen
- 下游(ZiPing/Blind/Ziwei/Heluo)只读消费，不重新排盘

**步骤**:
1. 扫描所有 `BaziEngine()` 实例化位置
2. 确认哪些是必要的独立实例，哪些是重复计算
3. 设计依赖注入方案
4. 最小化修改下游引擎
5. 验证下游引擎仍正确消费Frozen BaziChart

**关键问题**:
- BlindBaziEngine为何自行创建BaziEngine？
- ZiweiEngine stub为何直接调用`BaziEngine().compute()` 2次？
- Heluo引擎是否引用BaziEngine？
- API层(app.py)如何传递BaziChart？

---

### Phase B: B8 - P2字段测试覆盖

**目标**: 
- 创建 `tests/test_bazi_p2_fields.py`
- 覆盖全部15个P2字段
- 至少包括：字段存在性、字段类型、确定性、典型案例、边界案例、序列化、Frozen State

**15个P2字段清单**:
1. spouse_star
2. spouse_star_attack
3. officer_mixed
4. day_branch_clash
5. day_branch_harm
6. spouse_star_strength
7. peach_blossom
8. branch_clash_map
9. branch_harm_map
10. branch_he_map
11. branch_sanhe_map
12. branch_sanxing_map
13. kong_wang
14. five_element_balance
15. five_element_imbalance
16. day_branch_main_ten_god

**测试要求**:
- 不能只写 `assert field is not None`
- 必须验证语义结果
- 覆盖典型案例和边界案例

---

### Phase Final: 完整Replay + 再审

**验证清单**:
- [ ] 129 Boundary Tests PASS
- [ ] Core Tests (test_bazi_engine.py) PASS
- [ ] P2 Tests (test_bazi_p2_fields.py) PASS
- [ ] Full Bazi Replay Determinism
- [ ] Downstream Read-only Audit
- [ ] Production Admission Re-audit

**最终输出**:
- 更新 ARBITRATION_RECORD.md
- 生成 FINAL_ADMISSION_REPORT.md
- 提交用户最终裁决

---

## 验收标准

完成所有Phase后，状态升级为:

```
CALCULATION_INTEGRITY: PASS ✅
CANONICAL_STATE: PROVEN ✅ (B7修复后)
BOUNDARY_TESTS: PASS ✅
REPLAY_DETERMINISM: PASS ✅
DOWNSTREAM_RECALCULATION: NONE ✅ (B7修复后)
FALLBACK: FAIL_CLOSED ✅ (B4修复后)
EVIDENCE_INVENTORY: CONSISTENT ✅ (B11固化后)
P2_TEST_COVERAGE: 100% ✅ (B8修复后)

PRODUCTION_ADMITTED: YES
CALCULATION_FREEZE: PENDING USER ARBITRATION
```

---

*任务单 by BOT-MASTER | 2026-09-06*
