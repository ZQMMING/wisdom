# 顺天 / EXIS / Wisdom — 项目审计指南

> 本文件用于帮助 AI 审计者（GPT / Claude 等）快速理解项目结构、核心治理原则和审计重点。
> 最后更新：2026-08-29

---

## 一、项目概述

**项目名称**：顺天（EXIS / Wisdom）

**项目定位**：基于五部经典（《渊海子平》《子平真诠》《滴天髓》《穷通宝鉴》《三命通会》）的八字命理计算引擎 + 断言资产治理系统。

**核心架构**：

```
算 (Calculation) → 辨 (State/Signal) → 解 (Assertion/Interpretation)
     ↓                  ↓                      ↓
Canonical State    Semantic Signals      Assertion Assets
     ↓                  ↓                      ↓
确定性计算          状态/关系              断事规则
```

**核心治理原则**：

> **原典授权 ≠ 条件成立 ≠ 断事结论授权**

三者永久分离：
- `EVIDENCE_STATUS`（原典证据是否充分）
- `MATCH_STATUS`（前置条件是否匹配）
- `CONCLUSION_STATUS`（断事结论是否获得原典授权）

---

## 二、项目结构

### 2.1 顶层目录

| 目录 | 说明 |
|------|------|
| `src/tongshu/` | 核心源代码 |
| `engines/` | 计算引擎（八字、紫微、河洛、黄历等） |
| `data/` | 数据文件和审计结果 |
| `docs/` | 项目文档和审计报告 |
| `scripts/` | 脚本和工具 |
| `tests/` | 测试 |
| `audit/` | 审计日志 |
| `examples/` | 示例 |
| `deploy/` | 部署配置 |

### 2.2 核心引擎（`src/tongshu/engines/`）

| 文件 | 功能 | 审计优先级 |
|------|------|-----------|
| `bazi_engine.py` | 核心八字计算引擎，BaziChart 数据结构，固定数据表 | 🔴 高 |
| `bazi_l1_facts.py` | L1 事实数据：十二长生表、完整藏干表 | 🔴 高 |
| `strength_engine.py` | 强弱计算引擎 | 🔴 高 |
| `time_resolver.py` | 时间解析器（公历/农历/真太阳时/节气） | 🔴 高 |
| `bazi_adapter.py` | 八字适配器 | 🟡 中 |
| `tiaohou_loader.py` | 调候用神加载器 | 🟡 中 |
| `judgment_engine.py` | 判断引擎 | 🟡 中 |
| `ziwei_engine.py` | 紫微斗数引擎 | 🟢 低（当前非重点） |
| `heluo_yi_flow.py` | 河洛易数引擎 | 🟢 低 |
| `huangli_engine.py` | 黄历引擎 | 🟢 低 |

### 2.3 核心模块（`src/tongshu/`）

| 目录 | 功能 |
|------|------|
| `canonical/` | Canonical State 相关 |
| `assertion_v2/` | 断言引擎 v2 |
| `governance/` | 治理相关 |
| `validation/` | 验证相关 |
| `audit/` | 审计相关 |
| `golden/` | Golden Dataset |
| `reasoning/` | 推理相关 |
| `signal/` | 信号相关 |
| `evaluation/` | 评估相关 |

---

## 三、当前项目状态（2026-08-29）

### 3.1 阶段状态

| 阶段 | 状态 | 说明 |
|------|------|------|
| P6.1 Canonical State | 🔒 FROZEN | 事实层、关系层、组合层、修正层已完成 |
| P6.1.1 Semantic State Hardening | 🔒 FROZEN | 状态语义硬化 |
| P6.2 Assertion Admission | 🔒 FROZEN | 断言准入 7 层 Gate |
| P6.3 Cross-Domain Integration | 🔒 FROZEN | 跨领域集成 8/8 PASS |
| P6.3-B-R Mutation Regression | 🔒 FROZEN | 变异/语义回归测试 |
| P6.4 Asset Production Protocol | 🔒 FROZEN | 断言资产生产协议 |
| P6.5 Batch Production | 🟡 进行中 | 第一批 100 条已处理，P6.5-C BLOCKED |
| P6-CALC Calculation Integrity | 🔵 当前施工区 | 计算层完整性审计 |

### 3.2 当前最高优先级

**P6-CALC — Calculation Integrity Audit（计算层完整性审计）**

原因：之前发现过严重的计算层 Bug（Evaluation Runner 错误读取 `chart.year_branch` 导致 88% 案例 Day Master 错误，89.5% Ten-God 被污染）。

> **FROZEN ≠ PROVEN CORRECT**：冻结不等于已证明正确。

### 3.3 Assertion Library 当前状态

| 状态 | 数量 | 说明 |
|------|------|------|
| AUTHORIZED_WITH_QUALIFIER | 4 | ASSERT-002/003/004/005 |
| AUTHORIZED（正式入库） | 6 | P6.5-B-R6 后正式入库的 6 条 |
| CANDIDATE | 1 | ASSERT-006（食神生财，Effect 未授权） |
| POSTERIOR | 1 | ASSERT-001（财星透干逢流年合，结论未授权） |

---

## 四、核心治理原则（审计时必须遵守）

### 4.1 原典才是 Canonical Authority

- GitHub / JSON / 开源库 = **implementation source / candidate index**，不是授权来源
- 候选关系必须经过：候选索引 → 原典定位 → 原文核验 → Evidence Contract → 才能进入引擎
- **不为提高通过率强行授权**

### 4.2 允许的证据状态

| 状态 | 说明 |
|------|------|
| `SOURCE_SUPPORTED` | 原典明确表达 |
| `SOURCE_SUPPORTED_WITH_QUALIFIER` | 原典支持，但必须带前提 |
| `SOURCE_MAPPED_NON_PROOF` | 有相关语义，但没有授权因果链 |
| `INSUFFICIENT_SOURCE` | 找不到足够依据（完全合法且重要） |
| `SOURCE_CONTESTED` | 原典之间有争议 |

### 4.3 绝对禁止项

| 禁止项 | 说明 |
|--------|------|
| ❌ 五行计分 → 强弱 | 不能用五行数量计算强弱 |
| ❌ `strength_score` / `root_score` | 禁止任何评分机制 |
| ❌ 长生状态自动制造通根 | 十二长生 ≠ 根 |
| ❌ 合 = 合化 | 五合 ≠ 合化 |
| ❌ 水多木漂直接改强弱 | 只能作为 qualifier |
| ❌ 调候 → 强弱 | 调候是独立维度 |
| ❌ 未授权组合规则 → 最终强弱 | C4 是 INSUFFICIENT_SOURCE |
| ❌ 关键词 → 特殊格局 | 不能关键词触发从格等 |
| ❌ MATCHED → 自动授权结论 | 条件匹配 ≠ 断事授权 |
| ❌ Assertion 反推 Canonical State | 解不能反过来改算 |

### 4.4 关系与结论彻底分开

例如：

```
乙木
 ↓
亥中藏甲
 ↓
这是 L1 事实
 ↓
经典是否称其为"通根"？
 ↓
YES / NO / 条件性
 ↓
经典是否进一步称为"根深"？
 ↓
YES / NO / 未授权
 ↓
是否因此能推出"身强"？
 ↓
另行审计
```

**不能**：

```
亥 = 乙木长生
→ 长生
→ 强根
→ 身强
```

---

## 五、审计重点

### 5.1 计算层审计（当前最高优先级）

#### C0 输入层
- 公历/农历转换是否正确
- 出生时间、地点、时区处理
- DST（夏令时）处理
- 真太阳时计算
- 换日规则（子初换日 vs 子正换日）

#### C1 四柱计算
- 年柱（立春切换）
- 月柱（节气切换）
- 日柱（计算是否正确）
- 时柱（五鼠遁）

#### C2 日主与藏干
- Day Master 提取
- 十二长生表（阳顺阴逆，火土同生）
- 完整藏干表（本气/中气/余气）
- 通根检查（日主对应天干，不是同类五行）

#### C3 十神计算
- 天干十神
- 藏干十神
- 十神分布统计

#### C4 关系计算
- 天干五合
- 地支六合、三合、三会
- 冲、刑、害、破
- 空亡
- 组合关系的优先级

#### C5 时间展开
- 大运（起运、交运）
- 流年、流月、流日
- 节气边界

### 5.2 断言层审计

#### 断言准入 7 层 Gate

1. **Evidence Gate**：原典证据是否充分
2. **Assertion-Type Gate**：断言类型是否可执行（CASE_COMMENTARY / THEORY_OVERVIEW 等不得进入）
3. **Semantic Relation Gate**：关系词（见/生/合/制/化/逢）是否经过语义审核
4. **Precondition Gate**：前置条件是否完整
5. **Matcher Gate**：Matcher 是否能表达全部前置条件
6. **Effect Provenance Gate**：Effect 是否有原典 provenance
7. **Reverse / Qualifier Gate**：反向条件和限定条件是否完整

#### 断言类型分类

| 类型 | 说明 | 能否进入 Admission |
|------|------|-------------------|
| `EXECUTABLE_ASSERTION` | 可执行断言 | ✅ 可以 |
| `STRUCTURAL_ASSERTION` | 结构断言（格局定义等） | ❌ 进入 Structural Library |
| `PRESCRIPTIVE_ASSERTION` | 建议性断言 | ❌ NON_EXECUTABLE |
| `THEORY_OVERVIEW` | 理论概述 | ❌ REJECTED |
| `CASE_COMMENTARY` | 案例批注 | ❌ REJECTED |
| `DESCRIPTIVE` | 描述性文本 | ❌ REJECTED |

#### Effect 类型分类

| 类型 | 说明 | 能否通过 Effect Gate |
|------|------|---------------------|
| `ASSERTION_EFFECT` | 断事效果 | ✅ 可以 |
| `INTERMEDIATE_REASONING` | 中间推理 | ❌ FAIL |
| `RELATION` | 关系描述 | ❌ FAIL |
| `QUALIFIER` | 限定条件 | ❌ FAIL |
| `PRESCRIPTION` | 建议用法 | ❌ FAIL |
| `CASE_RESULT` | 案例结果 | ❌ FAIL |

### 5.3 治理层审计

- 是否有 `score → authorization` 的隐式路径
- 是否有关键词触发的规则
- 是否有 Assertion 反推 Canonical State 的情况
- 原始状态与验证后状态是否可追溯
- Provenance 是否完整（classic → source_file → chapter/section → source_span → source_text）

---

## 六、已知风险和问题

### 6.1 计算层风险（最高优先级）

- **历史 Bug**：Evaluation Runner 曾错误读取 `chart.year_branch`，导致 88% 案例 Day Master 错误
- **FROZEN ≠ PROVEN CORRECT**：P6.1 已冻结，但计算正确性尚未独立证明
- **边界案例**：子初前后、节气前后、立春前后、真太阳时跨时辰等尚未系统测试

### 6.2 断言层风险

- **批量生产语义退化**：P6.5-A-R 发现 32 条原始授权中有 18 条需要调整（56%）
- **Effect 提取错误**：把条件当效果、案例批注误判为通用断言
- **关系词简化**：`has_shangguan AND has_officer` 退化为关键词匹配
- **STRUCTURAL ≠ EXECUTABLE**：格局定义不能伪装成断事效果

### 6.3 治理层风险

- **数量目标反向影响授权率**：不能为了提高授权率而放宽标准
- **机器 Gate 通过 ≠ 人工审核通过**：所有 AUTHORIZED 断言必须经过人工抽样复核
- **Hermes / 采集代理无权授权**：知识采集和命理规则授权必须隔离

---

## 七、1983 命例 Golden Reference

**命例**：癸亥 壬戌 乙未 壬午（1983年）

**当前 Canonical State**：

| 状态 | 值 | 说明 |
|------|-----|------|
| `wangshuai` | 衰 | 戌月木囚，失时 |
| `qiangruo` | UNRESOLVED | 强弱未解析（C4 INSUFFICIENT_SOURCE） |
| `root_state` | ROOT_LIGHT / 部分 UNRESOLVED | 未中乙 = ROOT_LIGHT，亥中甲 = CANDIDATE |
| `dangzhong` | QUALIFIED | 党众条件部分满足 |
| `seasonal_remedy` | 独立维度 | 调候不影响强弱 |

**关键检查点**：
- 乙木 × 未中乙 = 同干，通根 = TRUE
- 乙木 × 亥中甲 = 同五行异天干，通根 = CANDIDATE（不能按同类五行直接处理）
- 乙木 × 午 = 十二长生为长生，但午中无乙，不能凭长生制造藏干根
- 水多木漂只能作为 qualifier，不能直接改 qiangruo
- qiangruo = UNRESOLVED 时，ASSERT-002/003/004 必须正确进入 UNRESOLVED

---

## 八、审计输出要求

审计完成后，请按以下格式输出：

### 8.1 发现的问题

| 严重程度 | 模块 | 问题描述 | 位置 | 建议修复 |
|----------|------|----------|------|----------|
| 🔴 高 | | | | |
| 🟡 中 | | | | |
| 🟢 低 | | | | |

### 8.2 验证通过的部分

| 模块 | 验证内容 | 结果 |
|------|----------|------|
| | | ✅ PASS / ⚠️ 有条件通过 / ❌ FAIL |

### 8.3 建议的下一步

按优先级列出建议的后续工作。

---

## 九、重要文档索引

| 文档 | 位置 | 说明 |
|------|------|------|
| 项目状态快照 | `docs/PROJECT_STATUS_SNAPSHOT.md` | 当前项目完整状态 |
| 五部经典资料索引 | `docs/五部经典资料索引_Canonical_Source_Registry.md` | 原典资料索引 |
| P6.2-B ASSERT-001 溯源 | `docs/P6.2-B_ASSERT-001_原典精确溯源审计报告.md` | 断言溯源示例 |
| 计算 Golden Dataset | `data/calc_golden_dataset_001.json` | 1983 命例计算记录 |
| P6.5 审计结果 | `data/p6_5_*.json` | 批量断言审计结果 |
| 架构文档 | `docs/ARCHITECTURE_V1.1.md` | 系统架构 |

---

## 十、Implementation Source 声明

当前计算引擎的十二长生表和藏干表数据来源：

- **来源**：`freddylamlc/bazi-patterns (GitHub)`
- **状态**：`NOT_CANONICAL_SOURCE`（实现参考，不是授权来源）
- **十二长生体系**：阳干顺行，阴干逆行，戊己与丙丁同论（火土同生）
- **藏干体系**：传统主流藏干表（本气/中气/余气三层）

**注意**：不同命理流派可能有不同排法，后续 Semantic Mapping 需明确采用哪套体系。

---

*本文件是项目审计的入口指南，具体代码和数据请参考相应目录和文件。*

---

## 十一、审计裁决工作流（重要）

> 本项目的角色分工约定：
> - **工程执行者（豆包/Claude 等）**：负责实现代码、验证、生成文档，并将成果推送到 GitHub。**不做裁决。**
> - **AI 审计者（GPT 等）**：负责审阅 GitHub 上的 commit，作出裁决。**裁决必须以实际代码审阅为基础。**

### 11.1 提交规范

工程执行者完成工作后，按以下规范提交：

1. 在 `docs/` 下生成**工程执行完成报告**（命名如 `P0_X_X_任务名.md`），内容只含：
   - 做了什么（事实）
   - 验证结果（事实，含测试输出）
   - 待审计者裁决的问题清单
   - **不含裁决结论**（如 PASS/FAIL、🟢/🔴）
2. commit message 只描述事实，不含裁决性表述
3. 推送到 GitHub，将 commit 链接提供给审计者

### 11.2 裁决规范

AI 审计者收到 commit 链接后，按以下步骤裁决：

1. **直接审阅 commit 的实际代码**，不只看 commit message
2. 核对工程执行报告中的"验证结果"与代码实际行为是否一致
3. 逐条回答执行报告中的"待裁决问题"
4. 给出裁决：
   - 🟢 PASS（可继续）
   - 🟡 CONDITIONAL PASS（需修正特定问题）
   - 🔴 FAIL（需返工）
5. 明确裁决范围（如"仅针对 P0-3.0 阶段1-3"），避免过度推广

### 11.3 当前待裁决项

| Commit | 主题 | 待审文件 | 状态 |
|--------|------|----------|------|
| `2584e6a` | P0-3.0 五经 Corpus 工程（Adapter+Audit+Retrieval） | `docs/P0_3_0_FIVE_CLASSICS_CORPUS_ENGINEERING_VERDICT.md` | ⏳ 待审计者裁决 |

### 11.4 审计原则核对清单

审计者裁决前应核对：

- [ ] 是否直接审阅了实际代码？
- [ ] 是否区分了"事实"与"解释"？
- [ ] 是否遵守了"原典授权≠条件成立≠断事结论授权"？
- [ ] 是否遵守了"候选证据≠原典授权"？
- [ ] 是否遵守了"FROZEN≠PROVEN CORRECT"？
- [ ] 是否遵守了"合理≠原典证明"？
- [ ] 是否遵守了"P6-CALC 仍是最高优先级"？

---

*本文件是项目审计的入口指南，具体代码和数据请参考相应目录和文件。*
