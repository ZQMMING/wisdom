# ZIPING Rule Engine Architecture - Final Status Report

**任务 ID**: T-ENGINE-BAZI-002  
**执行者**: @bot-ziping  
**日期**: 2026-09-06  
**状态**: 🔴 ARCHITECTURE DESIGN COMPLETE - AWAITING ARBITRATION

---

## 最终状态总结

### BAZI 层

```
🟢 FROZEN
```

- 四柱计算 ✅
- 节气判断 ✅
- 真太阳时 ✅
- 十神计算 ✅（单一权威源）
- 藏干表 ✅（统一）
- 十二长生 ✅
- fail-closed ✅（day_master_strength）

---

### ZIPING Context 层

```
🟢 CONNECTED
```

- NatalContext ✅
- DaYunContext ✅
- YearContext ✅
- DerivedSignals ✅
- ContractValidator ✅

---

### ZIPING Rule Engine 层

```
🔴 NOT IMPLEMENTED
```

| 模块 | 状态 | 说明 |
|------|------|------|
| Evidence Loader | 🔴 | 空实现 |
| Rule Definition | 🟡 | 32条候选规则设计完成 |
| Rule Engine | 🔴 | 未实现 |
| Judgment Layer | 🔴 | 未实现 |
| Assertion Layer | 🔴 | 未实现 |

---

### 32 条候选规则状态

```
🟡 CANDIDATE（全部）
```

| 域 | 规则数 | 状态 | 证据覆盖 |
|----|--------|------|----------|
| 旺衰 | 11 | CANDIDATE | ⚠️ 部分缺证据 |
| 格局 | 10 | CANDIDATE | ✅ 较好 |
| 用神 | 4 | CANDIDATE | ✅ 完整 |
| 十神语义 | 3 | CANDIDATE | ⚠️ 需补充 |
| 事件判断 | 4 | CANDIDATE | ❌ 完全缺失 |

---

## 架构裁决要点

### 已通过

| 项目 | 裁决 |
|------|------|
| BAZI → ZIPING Contract | ✅ PASS |
| ZIPING 不重算 BAZI | ✅ PASS |
| Evidence → Rule → Judgment 架构方向 | ✅ PASS |
| Rule Schema（设计层） | ✅ PASS |
| EvidenceRuleLink | ✅ PASS |
| 五大辨证域划分 | ✅ PASS |
| Provenance 作为核心指标 | ✅ PASS |
| ZIPING Freeze | ❌ **继续禁止** |

### 需要修正

| 项目 | 原设计 | 修正方案 |
|------|--------|----------|
| 权威体系 | 全局排名 1-5 | 域特定权威 DOMAIN_AUTHORITY |
| 规则状态 | 无状态机 | DRAFT → EVIDENCE_VERIFIED → ADJUDICATED → AUTHORIZED → PRODUCTION |
| 优先级 | 单字段 priority | 拆分为 execution_order / conflict_precedence / authority_level / specificity |

---

## 关键发现

### 1. 证据数据库 ≠ 辨证引擎

```
证据数据库: ~1534 文件 ✅
辨证代理: 5个空实现 ❌
规则引擎: 完全缺失 ❌
```

### 2. 有书无规则

> **"有书，但是没有把书变成可执行的子平规则。"**

证据是静态资料，需要建立转化层：
```
静态证据 (JSON) → 规则提取 → 动态规则 → 规则引擎 → 辨证结果
```

### 3. 32条规则全是候选

所有规则标记为 `CANDIDATE`，未经 BOT-MASTER 裁决不得进入生产。

---

## 新指标体系

| 指标 | 定义 | 目标 |
|------|------|------|
| RuleProvenanceRate | 有完整溯源的规则比例 | ≥90% |
| RuleCompleteness | 条件定义完整的规则比例 | ≥80% |
| RuleConflictRate | 存在冲突的规则比例 | ≤10% |
| PriorityDefined | 已定义优先级的规则比例 | 100% |
| ExecutionCoverage | 已被执行的规则比例 | ≥70% |
| GoldenCaseAccuracy | Golden Cases 判断准确率 | ≥85% |

**旧指标（降级）**:
- EvidenceCount（仅表示资料规模，不代表正确性）

---

## 最终架构图

```
                    顺天
                     │
             ┌───────┴───────┐
             ▼               ▼
          CALC 算          DIAG 辨
             │               │
           BAZI           ZIPING
             │               │
          🟢 FROZEN       🟡 ARCHITECTURE
                             │
                       Rule Engine
                             │
                         🔴 未实现
                             │
                       32 Candidate Rules
                             │
                         🟡 待裁决
                             │
                       Evidence DB (~1534 files)
                             │
                         🔴 未连接
```

---

## 下一阶段

### Phase B-0: Rule Authorization Audit（当前阶段）

**目标**: 对32条候选规则逐条审计

**交付物**:
1. 每条规则的完整 provenance
2. 明确的条件定义
3. 冲突识别与裁决策略
4. 权威等级标注

**完成标准**: 所有规则标记为 `EVIDENCE_VERIFIED` 或 `REJECTED`

### Phase B: Evidence Connection（待授权）

**前提**: Phase B-0 通过 BOT-MASTER 裁决

**目标**: 连接证据数据库到辨证代理

**步骤**:
1. 实现 EvidenceLoader
2. 修改五个 Bian Agent 的 `_load_classic_entries()`
3. 验证证据加载正确性

### Phase C: Rule Engine Implementation（待授权）

**前提**: Phase B 通过

**目标**: 实现规则引擎核心类

---

## 交付物清单

| 文件 | 路径 | 状态 |
|------|------|------|
| Phase 2 深度审计报告 | `docs/bots/BOT-ZIPING/PHASE2_DEEP_AUDIT_REPORT.md` | ✅ |
| 最终裁决报告 | `docs/bots/BOT-ZIPING/FINAL_RULING_REPORT.md` | ✅ |
| Architecture Audit | `docs/bots/BOT-ZIPING/RULE_ENGINE_ARCHITECTURE_AUDIT.md` | ✅ |
| Implementation Plan | `docs/bots/BOT-ZIPING/RULE_ENGINE_IMPLEMENTATION_PLAN.md` | ✅ |
| B-0 规则授权审计 | `docs/bots/BOT-ZIPING/PHASE_B0_RULE_AUTHORIZATION_AUDIT.md` | 🔄 |
| 本状态报告 | `docs/bots/BOT-ZIPING/FINAL_STATUS_REPORT.md` | ✅ |

---

**最终裁决**: @bot-ziping  
**状态**: 🔴 ARCHITECTURE DESIGN COMPLETE - AWAITING ARBITRATION  
**下一步**: 等待 BOT-MASTER 对 Phase B-0 的裁决
