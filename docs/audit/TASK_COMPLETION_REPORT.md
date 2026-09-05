# 紫微大限方向下一阶段完成报告

## 执行时间
2026-09-02

## 任务状态

| # | 任务 | 状态 |
|---|------|------|
| 1 | 准备 upstream issue 报告 | ✅ 完成 |
| 2 | 设计 Shuntian Ziwei Dependency Adapter 架构 | ✅ 完成 |
| 3 | 实现 Adapter（仅隔离 decadal direction discrepancy） | ✅ 完成 |
| 4 | 重新做最高等级 Harness（三层比较） | ✅ 完成 |
| 5 | 修正文档命名（decimal → cadal） | ✅ 完成 |

---

## 修改文件清单

### 新增文件

| 文件 | 说明 |
|------|------|
| `src/tongshu/engines/ziwei_dependency_adapter.py` | Adapter 层实现 |
| `scripts/ziwei_runtime_output_audit_v5.py` | 三层验证 Harness v5 |
| `docs/audit/upstream-issue-template.md` | upstream issue 报告 |
| `docs/audit/TASK_COMPLETION_REPORT.md` | 本完成报告 |

### 重命名文件

- `docs/audit/iztro-decimal-direction-forensic-v2.md` → `iztro-decadal-direction-forensic-v2.md`

### 未修改文件

- ✅ `ziwei_engine.py`（wrapper，保持原样）
- ✅ `node_modules/iztro`（不 patch）
- ✅ 其他计算逻辑（未触碰）

---

## Adapter 架构

```
┌─────────────────────────────────────────────────────────────┐
│  iztro 2.6.0 (raw output)                                   │
│  palace.js:163 → GENDER === branch.yinYang ? forward        │
│  ↓ 错误方向                                                  │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ShuntianZiweiDependencyAdapter                              │
│  - 独立计算 expected (年干阴阳 + 性别)                        │
│  - 比较 iztro raw vs expected                                │
│  - 返回 corrected direction                                  │
│  - 记录审计日志                                              │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Signal Layer (canonical direction)                          │
│  - 用于后续四化、宫位分析                                     │
└─────────────────────────────────────────────────────────────┘
```

### 关键设计原则

1. **隔离性**：Adapter 在 wrapper 层调用 iztro，然后应用修正
2. **可审计性**：每个修正都有完整 audit trail
3. **可关闭性**：iztro 修复后，只需移除 adapter 调用

---

## Harness v5 测试结果

```
======================================================================
ZIWEI RUNTIME VERIFICATION HARNESS — P-A1 Post-Cleanup (v5)
======================================================================

[1] DECADAL DIRECTION VERIFICATION (Three-Layer)

毛泽东:
  Layer 1 (iztro raw):     forward  ← 已知 bug
  Layer 2 (adapter):       reverse  ← 修正
  Layer 3 (expected):      reverse  ← 传统规则
  Discrepancy detected:    YES
  Corrected:               YES
  ✓ Adapter matches expected

阳女测试:
  Layer 1 (iztro raw):     forward
  Layer 2 (adapter):       reverse
  Layer 3 (expected):      reverse
  Discrepancy detected:    YES
  Corrected:               YES
  ✓ Adapter matches expected

阴男测试:
  Layer 1 (iztro raw):     forward
  Layer 2 (adapter):       reverse
  Layer 3 (expected):      reverse
  Discrepancy detected:    YES
  Corrected:               YES
  ✓ Adapter matches expected

阴女测试:
  Layer 1 (iztro raw):     reverse
  Layer 2 (adapter):       forward
  Layer 3 (expected):      forward
  Discrepancy detected:    YES
  Corrected:               YES
  ✓ Adapter matches expected

[2] STRUCTURAL CHECKS
  ✓ 五行局、命宫全部正确

[3] GAN_SIHUA INTEGRITY
  ✓ 10干四化全部正确

[4] TEMPORAL MUTATION CHECKS
  ✓ 流年四化全部正确（来自年干GAN_SIHUA oracle）

[5] FORBIDDEN METHODS CHECK
  ✓ 全部已删除

======================================================================
SUMMARY
======================================================================
  Passed:   31
  Warnings: 0
  Failed:   0

  Iztro discrepancies found: 4/4
  Adapter corrections applied: 4/4

  STATUS: ✅ PASSED
======================================================================
```

---

## Ad-hoc 验证结果

```
TEST 1: Adapter canonical cases          ✅ PASS
TEST 2: Adapter audit trail              ✅ PASS
TEST 3: Harness v5 execution             ✅ PASS (exit code: 0)
TEST 4: Code isolation check             ✅ PASS

OVERALL: ✅ ALL TESTS PASSED
```

---

## Upstream Issue 内容摘要

**Issue Title**: `[Bug] Decadal direction computation uses wrong yin-yang comparison`

**Key Points**:
- Location: `lib/astro/palace.js:163`
- Current: `GENDER[gender] === earthlyBranch.yinYang ? forward : reverse`
- Expected: Based on `heavenlyStem.yinYang + gender`
- Impact: All 4 combinations reversed
- Canonical cases: 甲辰阳男、甲辰阳女、乙巳阴男、乙巳阴女

完整报告见：`docs/audit/upstream-issue-template.md`

---

## 后续行动

1. 提交 commit（含 adapter + harness + 文档）
2. 向 upstream 提交 issue
3. 等待上游反馈（不影响当前使用）

---

**完成时间**: 2026-09-02  
**Git 状态**: 待提交
