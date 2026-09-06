# 🔴 P0-1-C 发现：day_master_strength 缺失

**发现者**: @bot-ziping
**日期**: 2026-09-07
**严重性**: P0 BLOCK

---

## 问题描述

执行完整链路测试时发现：

```python
chart = canonical_bazi_engine.compute((1983, 11, 3, 12), 'male')
ctx = assembler.assemble('TEST-001', chart, 'male', 2026)
# ❌ ValueError: day_master_strength 未计算
```

### 错误位置

`src/tongshu/reasoning/context_assembler.py:195-201`

```python
_dm_strength = getattr(chart, 'day_master_strength', None)
if _dm_strength is None:
    raise ValueError(
        f"day_master_strength 未计算。"
        f"日主强度是辨证核心，必须在 BaziEngine 中计算或明确标记为 MISSING。"
        f"当前日主: {chart.day_master}"
    )
```

### 当前状态

| 检查项 | 结果 |
|--------|------|
| BaziChart 是否有 day_master_strength？ | ❌ 否 |
| BaziEngine.compute() 是否计算？ | ❌ 否 |
| Phase 3 P0 修复是否要求存在？ | ✅ 是（fail-closed） |

---

## 冲突分析

### Phase 3 P0 修复（已完成）
- **commit**: `2f9c2878` (或相关)
- **内容**: 添加 `day_master_strength` fail-closed 检查
- **目的**: 确保 BAZI Frozen State 包含日主强度
- **代码**: `temporal_context_contract.py:154` default="MISSING"

### 当前矛盾
1. Phase 3 修复要求 `day_master_strength` 必须存在
2. BaziChart 类定义中没有此字段
3. BaziEngine 不计算此字段
4. 导致 assemble() 必然失败

---

## 可能的解决方案

### 方案 A：BaziEngine 计算 day_master_strength
```python
# bazi_engine.py compute() 返回时添加
chart.day_master_strength = self._compute_strength(chart)
```
**问题**: 违反 BAZI 冻结原则

### 方案 B：ContextAssembler 不要求 day_master_strength
```python
_dm_strength = getattr(chart, 'day_master_strength', 'MISSING')
# 允许 MISSING，不抛异常
```
**问题**: 违反 Phase 3 P0 修复

### 方案 C：从 Chart 外部注入
```python
# ComputeStage 或外部调用方注入
chart.day_master_strength = compute_from_evidence(chart)
```
**问题**: 需要定义注入位置和逻辑

### 方案 D：修正 Phase 3 P0 修复
- 将 fail-closed 改为 fail-soft
- 允许 MISSING，后续 Judgment 层处理

---

## 需要 BOT-MASTER 裁决

**核心问题**: 
> Phase 3 P0 修复要求 `day_master_strength` 必须存在，但 BAZI 冻结不计算它。如何解决这个矛盾？

**建议方向**:
1. 如果 BAZI 确实需要计算，需要重新评估冻结边界
2. 如果 BAZI 不计算，Phase 3 P0 修复需要调整（fail-soft 而非 fail-closed）
3. 或者定义外部注入机制

---

## 当前状态

```
P0-1-A 架构修复          ✅ PASS
P0-1-B birth_year 修复   ✅ PASS
P0-1-C day_master_strength  ❌ BLOCK（需要裁决）
```

**ZIPING Phase 4 不能继续，等待 BOT-MASTER 对 P0-1-C 的裁决。**
