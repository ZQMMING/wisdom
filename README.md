# 顺天 / EXIS / Wisdom

基于五部经典（《渊海子平》《子平真诠》《滴天髓》《穷通宝鉴》《三命通会》）的八字命理计算引擎 + 断言资产治理系统。

## 核心架构

```
算 (Calculation) → 辨 (State/Signal) → 解 (Assertion/Interpretation)
     ↓                  ↓                      ↓
Canonical State    Semantic Signals      Assertion Assets
     ↓                  ↓                      ↓
确定性计算          状态/关系              断事规则
```

## 核心治理原则

> **原典授权 ≠ 条件成立 ≠ 断事结论授权**

三者永久分离：
- `EVIDENCE_STATUS`（原典证据是否充分）
- `MATCH_STATUS`（前置条件是否匹配）
- `CONCLUSION_STATUS`（断事结论是否获得原典授权）

## 项目结构

| 目录 | 说明 |
|------|------|
| `src/tongshu/engines/` | 计算引擎（八字、紫微、河洛、黄历等） |
| `src/tongshu/canonical/` | Canonical State 相关 |
| `src/tongshu/assertion_v2/` | 断言引擎 v2 |
| `src/tongshu/governance/` | 治理相关 |
| `data/` | 数据文件和审计结果 |
| `docs/` | 项目文档和审计报告 |
| `scripts/` | 脚本和工具 |

## 核心引擎

| 文件 | 功能 |
|------|------|
| `bazi_engine.py` | 核心八字计算引擎 |
| `bazi_l1_facts.py` | L1 事实数据（十二长生、藏干） |
| `strength_engine.py` | 强弱计算引擎 |
| `time_resolver.py` | 时间解析器 |

## 当前项目状态

| 阶段 | 状态 |
|------|------|
| P6.1 Canonical State | 🔒 FROZEN |
| P6.2 Assertion Admission | 🔒 FROZEN |
| P6.3 Cross-Domain Integration | 🔒 FROZEN |
| P6.4 Asset Production Protocol | 🔒 FROZEN |
| P6.5 Batch Production | 🟡 进行中 |
| P6-CALC Calculation Integrity | 🔵 当前施工区 |

## 审计指南

请先阅读 [AUDIT_GUIDE.md](./AUDIT_GUIDE.md)，了解项目结构、核心治理原则和审计重点。

## 重要文档

- [项目状态快照](./docs/PROJECT_STATUS_SNAPSHOT.md)
- [五部经典资料索引](./docs/五部经典资料索引_Canonical_Source_Registry.md)
- [计算 Golden Dataset](./data/calc_golden_dataset_001.json)

## Implementation Source

当前计算引擎的十二长生表和藏干表数据来源：`freddylamlc/bazi-patterns (GitHub)`

**状态**：`NOT_CANONICAL_SOURCE`（实现参考，不是授权来源）
