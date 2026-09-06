# 引擎迁移完整性审计报告

**审计时间**: 2026-09-06 18:00  
**审计人**: Hermes Agent  
**严重级别**: 🔴 P0 - 可能有数据遗漏

---

## 核心发现

**shuntian-NEW 是退化版本，shuntian 包含了更多的工作。**

但这引发了新的问题：**shuntian-NEW 的"改进"是否遗漏了什么？**

---

## 各引擎对比详情

### 1. 盲派引擎 (blind)

| 指标 | D:/shuntian | D:/shuntian-NEW | 差异 |
|------|-------------|-----------------|------|
| 文件数 | 8 | 1 | ❌ **shuntian-NEW遗漏7个文件** |
| evidence_producer.py | 257行 | 127行 | ❌ **shuntian-NEW少130行** |

**shuntian 独有文件（shuntian-NEW缺失）**：
```
❌ palace.py - 宫位计算
❌ palace_rules.json - 宫位规则配置
❌ rules/graph.py - 规则图
❌ rules/matcher.py - 规则匹配器
❌ rules/models.py - 规则数据模型
❌ workchain.py - 工作链
❌ workgraph.py - 工作图
```

**风险评估**：🔴 **严重** - shuntian-NEW完全缺失盲派的规则图和匹配系统

---

### 2. 河洛引擎 (heluo)

| 指标 | D:/shuntian | D:/shuntian-NEW | 差异 |
|------|-------------|-----------------|------|
| 文件数 | 25 | 22 | shuntian多3个 |
| canonical.py | 495行 | 431行 | +64行 |
| evidence_producer.py | 200行 | 153行 | +47行 |

**shuntian 独有文件**：
```
✅ diagnosis_rule_graph.py - 诊断规则图
✅ frozen_state.py - 冻结状态
✅ guidance.py - 指导系统
✅ hua_gong.py - 化宫计算
✅ jiehhou.py - 节气候
```

**shuntian-NEW 独有文件**：
```
⚠️ hetu_luoshu.py - 河图洛书（可能在shuntian已重构）
⚠️ metrics.py - 指标系统（可能在shuntian已重构为metrics_v2.py）
```

**风险评估**：🟡 **中等** - shuntian-NEW缺少5个功能文件，但河图洛书可能被重构

---

### 3. 紫微引擎 (ziwei)

| 指标 | D:/shuntian | D:/shuntian-NEW | 差异 |
|------|-------------|-----------------|------|
| 文件数 | 5 | 5 | 相同 |
| ziwei_engine.py | 799行 | 907行 | ❌ **shuntian少108行** |
| ziwei_adapter.py | 216行 | 116行 | ✅ **shuntian多100行** |

**分析**：
- ziwei_engine.py在shuntian-NEW中更大（907行 vs 799行）
- 但ziwei_adapter.py在shuntian中更大（216行 vs 116行）
- 这可能是架构调整：将功能从engine移到adapter

**风险评估**：🟡 **中等** - 需要深入比较具体实现

---

### 4. 易经引擎 (yi)

| 指标 | D:/shuntian | D:/shuntian-NEW | 差异 |
|------|-------------|-----------------|------|
| 文件数 | 12 | 11 | shuntian多1个 |
| core.py | 存在 | 不存在 | ❌ shuntian-NEW缺失 |

**shuntian 独有文件**：
```
✅ core.py - 易经核心逻辑
```

**风险评估**：🟡 **低** - 缺失1个文件，但需要确认core.py是否必要

---

### 5. 其他引擎

```
盲派主引擎 (blind_bazi_engine.py):
  shuntian: 618行 vs shuntian-NEW: 650行 (-32行)
  → shuntian-NEW多了32行，需核查

 YingQi (blind_yingqi.py):
  shuntian: 440行 vs shuntian-NEW: 440行 (相同)
  → 无差异

紫微适配器 (ziwei_adapter.py):
  shuntian: 216行 vs shuntian-NEW: 116行 (+100行)
  → shuntian有额外功能
```

---

## 关键问题

### 问题1：shuntian-NEW为什么文件更少？

**可能的解释**：
1. shuntian-NEW是历史快照，当时工作未完成
2. shuntian是主仓库，持续迭代，积累了更多功能
3. **迁移过程中可能遗漏了部分文件**

### 问题2：哪些文件是关键数据文件？

**高风险文件**：
1. `palace_rules.json` - 盲派规则配置（JSON数据文件）
2. `rules/*.py` - 盲派规则图系统
3. `frozen_state.py` - 河洛状态管理
4. `core.py` - 易经核心逻辑

---

## 紧急核查行动

### STEP1: 检查JSON配置文件

```bash
# 检查盲派规则配置文件
find /d/shuntian -name "palace_rules.json" -o -name "*.json" | grep -E "blind|rule"

# 检查河洛配置
find /d/shuntian -name "*.json" | grep heluo
```

### STEP2: 比较Git历史

```bash
# 查看shuntian的关键提交
cd /d/shuntian && git log --all --oneline -- src/tongshu/engines/blind/ | head -20
cd /d/shuntian && git log --all --oneline -- src/tongshu/engines/heluo/ | head -20
```

### STEP3: 运行测试验证

```bash
# 测试盲派引擎
cd /d/shuntian && python -m pytest tests/test_blind*.py -v

# 测试河洛引擎
cd /d/shuntian && python -m pytest tests/test_heluo*.py -v
```

---

## 初步结论

**shuntian-NEW确实遗漏了大量数据**，特别是：
1. 盲派的完整规则图系统（7个文件）
2. 河洛的诊断和状态管理系统（5个文件）
3. 易经的核心逻辑（1个文件）

**这证实了用户的担忧：迁移过程确实存在数据遗漏风险。**

---

## 下一步建议

1. **立即核查**：确认shuntian中的关键文件是否被正确引用
2. **测试验证**：运行所有引擎的测试套件
3. **Git溯源**：追踪每个文件的提交历史
4. **风险评估**：确定哪些遗漏是致命的，哪些是次要的

---

**审计人**: Hermes Agent  
**日期**: 2026-09-06  
**状态**: 🔴 进行中 - 发现重大数据遗漏
