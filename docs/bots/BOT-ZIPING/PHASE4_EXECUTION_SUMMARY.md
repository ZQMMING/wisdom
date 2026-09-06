# ZIPING 子平系统 Phase 4 重新审计摘要

## 执行摘要

根据 BOT-MASTER 基线文档，对 ZIPING 子平系统进行全面重新审计，聚焦七个核心问题（P0-1 至 P0-7）。

## 审计结果

| 检查项 | 状态 | 严重级别 | 关键发现 |
|--------|------|----------|----------|
| P0-1: BAZI Frozen State Consumption | ❌ FAIL | P0 | ContextAssembler 有重复排盘风险（未进入生产路径） |
| P0-2: Evidence Index Reliability | ⚠️ PARTIAL | P0 | Schema 文件缺失，证据引用路径不完整 |
| P0-3: Evidence to Rule Flow | ✅ PASS | INFO | 136条规则全部有证据引用 |
| P0-4: Rule Execution | ✅ PASS | INFO | RuleMatcher + SignalEngine 正常工作 |
| P0-5: Rule to Judgment | ✅ PASS | INFO | Signal 产出包含 direction/polarity |
| P0-6: Judgment Synthesis | ❌ FAIL | P0 | **用神域（yongshen）完全缺失规则** |
| P0-7: End-to-End Runnable | ❌ FAIL | P0 | test_rule_lifecycle.py 全部失败（Schema 缺失） |

## 核心发现

### 🔴 致命问题

**用神域规则完全缺失**

- 五大辨证域中，用神域（yongshen）规则数为 **0**
- 这是子平命理的核心，无法判断命局的关键需求
- 根据 BOT-MASTER 基线文档第7节，用神算法是"最容易被简化错误的地方"

### 🟡 重要问题

1. **ContextAssembler 架构违规风险**
   - 第532行调用 `bazi_engine.compute()` 重新排盘
   - 虽未进入生产路径，但代码存在架构风险
   - 违反"ZIPING 消费 Canonical State，不重新排盘"的原则

2. **Schema 文件缺失**
   - `rule.schema.json` 和 `evidence.schema.json` 不存在
   - 导致 RuleLoader 无法验证规则结构
   - test_rule_lifecycle.py 全部失败

3. **证据引用路径不完整**
   - 规则引用证据 ID（如 E-ZPZ-101-001）
   - 但证据文件路径不明确
   - 需要建立索引验证机制

### 🟢 正常部分

1. **RuleMatcher 工作正常**
   - match_all() 可正确匹配规则
   - evaluate_conditions() 可评估 DSL 条件
   - resolve_conflicts() 可解决冲突

2. **SignalEngine 产出正确**
   - 每个 Signal 包含完整的 direction/polarity/strength
   - rule_refs 和 evidence_refs 可追溯

3. **证据引用完整性**
   - 136条规则全部有 evidence_refs
   - 无孤立规则

## 规则统计

- 总规则数：136
- 状态分布：active (75), draft (51), validated (10)
- 领域分布：
  - 旺衰判定：14
  - 格局判定：20
  - 用神判定：**0** ⚠️
  - 十神语义：21
  - 事件判断：21

## 测试状态

| 测试文件 | 状态 | 通过数 |
|----------|------|--------|
| test_rule_engine.py | ✅ PASS | 12 |
| test_phase3_p0.py | ✅ PASS | 3 |
| test_bazi_engine.py | ✅ PASS | 12 |
| test_rule_lifecycle.py | ❌ FAIL | 0 |

## 结论

**❌ ZIPING 不具备冻结条件**

### 必须修复的问题（冻结前）

1. **补充用神域规则**（至少 4-7 条核心规则）
2. **补充 Schema 文件**（rule.schema.json, evidence.schema.json）
3. **修复 ContextAssembler 架构违规**

### 建议修复的问题（近期）

1. 建立证据索引验证机制
2. 集成 Phase B-2.1 的 RemediationEngine
3. 建立五大领域的 Synthesis 机制

## 下一步

1. 等待 BOT-MASTER 裁决
2. 根据裁决开始修复
3. 修复完成后重新审计
4. 申请 ZIPING 冻结

---

**执行者**: @bot-ziping  
**日期**: 2026-09-07  
**状态**: 待裁决
