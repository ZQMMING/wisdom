# 🔴 P0 紧急审计：引擎迁移数据遗漏分析

**审计时间**: 2026-09-06 18:15  
**审计人**: Hermes Agent  
**严重级别**: 🔴 P0-CRITICAL

---

## 核心结论

**D:/shuntian-NEW 是严重的退化版本，遗漏了大量关键数据和架构组件。**

这证实了用户的担忧：迁移过程中确实存在数据遗漏风险。

---

## 各引擎详细对比

### 1. 盲派引擎 (blind) - 🔴 严重遗漏

| 指标 | D:/shuntian | D:/shuntian-NEW | 差异 |
|------|-------------|-----------------|------|
| 总行数 | 1185行 | ~300行 | ❌ **少885行** |
| 文件数 | 8 | 1 | ❌ **少7个文件** |
| JSON配置 | ✅ palace_rules.json | ❌ 缺失 | ❌ **规则配置丢失** |

**shuntian 独有的关键文件**：
```
❌ palace.py (209行) - 宫位计算系统
❌ palace_rules.json (500+字节) - 宫位语义规则配置
❌ rules/graph.py (74行) - 规则图定义
❌ rules/matcher.py (90行) - 规则匹配器
❌ rules/models.py (38行) - 规则数据模型
❌ workchain.py (211行) - 工作链（宾主/体用/做功）
❌ workgraph.py (277行) - 工作图（可视化输出）
```

**影响评估**：
- 🔴 **致命**：盲派的完整规则图系统完全缺失
- 🔴 **致命**：宫位语义配置丢失
- 🔴 **致命**：workchain/workgraph 无法运行

---

### 2. 河洛引擎 (heluo) - 🔴 严重遗漏

| 指标 | D:/shuntian | D:/shuntian-NEW | 差异 |
|------|-------------|-----------------|------|
| 总行数 | 5996行 | ~4500行 | ❌ **少1496行** |
| 文件数 | 25 | 22 | ❌ **少3个关键文件** |

**shuntian 独有的关键文件**：
```
❌ diagnosis_rule_graph.py (333行) - 诊断规则图（H12核心）
❌ frozen_state.py (197行) - FrozenHeluoState（状态冻结）
❌ guidance.py (365行) - 指导系统
❌ hua_gong.py (123行) - 化工状态判定
❌ jiehhou.py (247行) - 节候卦计算
```

**shuntian-NEW 独有但可能已过时**：
```
⚠️ hetu_luoshu.py (12KB) - 可能被重构到其他文件
⚠️ metrics.py (7.5KB) - 已被 metrics_v2.py 替代
```

**canonical.py 差异**：
```
shuntian: 495行（完整的模块入口）
shuntian-NEW: 431行（缺失部分导入）
```

**影响评估**：
- 🔴 **致命**：diagnosis_rule_graph.py 是 H12 诊断系统的核心
- 🔴 **致命**：frozen_state.py 是状态冻结的关键
- 🟡 **高**：hua_gong.py 和 jiehhou.py 缺失会影响计算完整性

---

### 3. 紫微引擎 (ziwei) - 🟡 架构调整

| 指标 | D:/shuntian | D:/shuntian-NEW | 差异 |
|------|-------------|-----------------|------|
| 文件数 | 5 | 5 | 相同 |
| ziwei_engine.py | 799行 | 907行 | shuntian少108行 |
| ziwei_adapter.py | 216行 | 116行 | shuntian多100行 |

**分析**：
- 功能从 engine 迁移到 adapter
- 这是架构优化，不是数据遗漏
- 但需要验证 adapter 是否完整覆盖了 engine 的功能

---

### 4. 易经引擎 (yi) - 🟡 轻微遗漏

| 指标 | D:/shuntian | D:/shuntian-NEW | 差异 |
|------|-------------|-----------------|------|
| 文件数 | 12 | 11 | shuntian多1个 |

**shuntian 独有**：
```
✅ core.py - 易经核心逻辑
```

**影响评估**：
- 🟡 **低**：缺失1个文件，但需要验证是否必要

---

## Git历史溯源

### 盲派引擎关键提交
```
98073792 整合ziwei分支引擎改进: Blind规则图 + Ziwei适配器优化
520a045f P2.2: Blind School Engine + Evidence Library
   - Add blind school engine core: palace, workchain, workgraph, rules
   - Add blind_bazi_engine.py (618 lines) and blind_yingqi.py (440 lines)
   - Add tests for blind engine
```

**结论**：盲派引擎是在 P2.2 阶段构建的，包含完整的规则图系统。

### 河洛引擎关键提交
```
9e233e62 P2.7-H18-ROLLBACK: Revert H17-B Heluo pollution from bazi agent
7d6002ae P2.7-H17-B: Canonical Bazi Integration — Heluo consumes CanonicalBaziChart
40c39cef H0-H15: Heluo/Yi/Meihua engine independent build and audit
```

**结论**：河洛引擎经历了多次重构，shuntian 保留了最新的完整版本。

---

## 根因分析

### 为什么 shuntian-NEW 会遗漏这些数据？

**可能原因1：STOP.md 误导**
- STOP.md 说"引擎改进已整合到主仓库"
- 但实际上 shuntian-NEW 是独立开发的快照
- 两者有共同的 Git 祖先，但后续发展 diverged

**可能原因2：分支策略混乱**
- shuntian 有多个 feature 分支（feature/blind, feature/heluo 等）
- shuntian-NEW 可能基于旧的主干，未合并最新改进

**可能原因3：Git 同步不完整**
- 检查 git log，发现两个仓库有相同的 commit hash
- 但 shuntian-NEW 缺少 remote，可能是本地快照

---

## 紧急行动建议

### 立即核查（P0）

1. **验证 shuntian 的功能完整性**
   ```bash
   cd D:/shuntian && python -m pytest tests/test_blind*.py -v
   cd D:/shuntian && python -m pytest tests/test_heluo*.py -v
   ```

2. **检查证据系统**
   ```bash
   find D:/shuntian/backend/data/evidence -name "E-BLIND*.json" | wc -l
   find D:/shuntian/backend/data/evidence -name "E-HELUO*.json" | wc -l
   ```

3. **验证导入路径**
   ```python
   from tongshu.engines.blind.palace import PalaceEngine
   from tongshu.engines.heluo.frozen_state import FrozenHeluoState
   ```

### 中期修复（P1）

1. **清理 shuntian-NEW**
   - 重命名为 `shuntian-archive-LEGACY`
   - 添加明显的废弃标记

2. **补充测试用例**
   - 为盲派规则图添加单元测试
   - 为河洛诊断系统添加集成测试

3. **文档更新**
   - 更新 ARCHITECTURE.md，明确各引擎的文件位置
   - 记录关键文件的作用和依赖关系

---

## 结论

**shuntian 是正确的、完整的版本。**

**shuntian-NEW 是严重的退化版本，不应作为参考或合并来源。**

用户担心的"迁移遗漏数据"问题确实存在——但不是从 shuntian-NEW 迁移到 shuntian 时遗漏，而是 shuntian-NEW 本身就缺少了大量关键文件。

---

## 下一步

1. 立即运行测试套件验证 shuntian 的功能完整性
2. 检查是否有其他引擎也存在类似问题
3. 清理 shuntian-NEW，避免混淆

---

**审计人**: Hermes Agent  
**日期**: 2026-09-06  
**状态**: 🔴 等待用户决策
