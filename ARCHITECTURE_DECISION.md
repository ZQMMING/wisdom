# 顺天 / EXIS 项目架构裁决书

> **文档目的**：基于对项目代码的全面深度审核，列出需要裁决的核心架构决策点，供独立审计者（GPT / 专家）做出最终裁决。
>
> **创建时间**：2026-08-29
>
> **仓库地址**：https://github.com/ZQMMING/wisdom
>
> **裁决原则**：原典授权优先、确定性计算优先、不可逆边界优先、不强行授权、允许 UNRESOLVED

---

## 一、项目背景

### 1.1 项目定位

顺天 / EXIS 是一个基于五部经典（《渊海子平》《子平真诠》《滴天髓》《穷通宝鉴》《三命通会》）的八字命理计算引擎 + 断言资产治理系统。

### 1.2 核心架构（目标状态）

```
算 (Calculation) → 辨 (State/Signal) → 解 (Assertion)
     ↓                  ↓                      ↓
Canonical State    Semantic Signals      Assertion Assets
  (wangshuai,       (从 Canonical        (7层Gate准入,
   qiangruo,         State 提取)          Evidence Contract,
   root_state,                            Provenance)
   dangzhong...)
```

### 1.3 核心治理原则（已冻结）

1. **原典才是 Canonical Authority**：GitHub / JSON / 开源库 = implementation source，不是授权来源
2. **原典授权 ≠ 条件成立 ≠ 断事结论授权**：三者永久分离
3. **禁止评分/阈值/权重**：禁止五行计分→强弱，禁止 strength_score / root_score，禁止关键词→结论
4. **FROZEN ≠ PROVEN CORRECT**：冻结不等于已证明正确
5. **解不能反推算**：Assertion 不能反向修改 Canonical State，禁止自证循环

---

## 二、深度审核发现的核心问题

### 2.1 算层问题

| 问题 | 严重程度 | 说明 |
|------|----------|------|
| `strength_engine.py` 使用加权评分系统 | 🔴 高 | 违反 P6.1 冻结原则，使用了 `_ROOT_QUALITY`、`_PILLAR_YIN_FACTOR`、`_CLASH_ACTIVATE_FACTOR`、`_CLIMATE_FACTOR`、`_WANG_SCORE_THRESHOLD = 2.0` 等评分/阈值/权重 |
| 3 套并行数据源 | 🔴 高 | 十二长生表、藏干表、十神计算各有 3 套实现，可能不一致 |
| `bazi_l1_facts.py` 未被核心统一使用 | 🟡 中 | P6.1-A 的成果可能未被核心引擎引用 |
| 缺乏 CALCULATION_GOLDEN_DATASET | 🟡 中 | Step 1 已完成（1983 命例），但不足以验证计算正确性 |
| 缺乏 Boundary Cases 测试 | 🟡 中 | 子初前后、节气前后等边界案例未系统测试 |

### 2.2 辨层问题

| 问题 | 严重程度 | 说明 |
|------|----------|------|
| `canonical/` 目录只有 3 个文件 | 🔴 高 | Canonical State 未真正实现，`canonical_validator.py` + `composer.py` + `__init__.py` 非常薄 |
| `wangshuai/qiangruo/root_state/dangzhong` 只在文档中 | 🔴 高 | P6.1 定义的核心状态字段在核心代码中不存在，仅在 `legacy/assertion_v1/systems.py` 中有雏形 |
| 3 套 signal engine 职责不清 | 🟡 中 | `signal_engine.py`、`semantic_signal.py`、`p3_signal_engine.py` 并行，职责重叠 |
| 辨层消费的是旧评分结果 | 🔴 高 | Signal 引擎可能消费 `strength_engine.py` 的评分结果，不是 Canonical State |

### 2.3 解层问题（当前非重点，但需了解）

| 问题 | 严重程度 | 说明 |
|------|----------|------|
| 两套断言引擎并行 | 🟡 中 | `reasoning/assertion.py` 新版 + `legacy/assertion_v1/` 旧版（16个文件） |
| 治理机制主要在文档中 | 🟡 中 | P6.2-P6.5 的 7 层 Gate、Evidence Contract、Provenance 等主要存在于文档和 data/ 审计结果 |

---

## 三、需要裁决的核心决策点

### 🔴 决策点 1：`strength_engine.py` 的处理方式

**背景**：
`strength_engine.py`（391行）是当前的强弱计算引擎，但它使用了加权评分系统（`_ROOT_QUALITY`、`_PILLAR_YIN_FACTOR`、`_CLASH_ACTIVATE_FACTOR`、`_CLIMATE_FACTOR`、`_WANG_SCORE_THRESHOLD = 2.0`），这与 P6.1 冻结的"禁止评分、禁止阈值、禁止权重"原则直接冲突。

同时，P6.1 定义的 Canonical State（`wangshuai/qiangruo/root_state/dangzhong`）在核心代码中并没有实现。

**需要裁决的问题**：
如何处理 `strength_engine.py`？是修改它移除评分系统，还是新建一个 `canonical_state_engine.py` 逐步替换？

**选项 A：原地修改 `strength_engine.py`**
- 做法：保留文件，移除所有评分/阈值/权重代码，改为 P6.1 的非评分式 Canonical State
- 优点：
  - 不增加新文件，调用方不需要改 import
  - 迁移成本低
- 缺点：
  - 改动量大，可能引入新 bug
  - 旧的评分逻辑被删除后，如果有问题难以回滚
  - 文件职责从"强弱评分"变为"Canonical State 计算"，语义变化大

**选项 B：新建 `canonical_state_engine.py`，逐步替换**
- 做法：在 `canonical/` 目录下新建 `canonical_state_engine.py`，实现 P6.1 的非评分式 Canonical State；`strength_engine.py` 标记为 deprecated，逐步迁移调用方
- 优点：
  - 新旧并存，可以逐步迁移，风险可控
  - 新引擎可以严格按照 P6.1 原则设计，不受旧代码约束
  - 旧引擎保留作为参考和回滚
- 缺点：
  - 两套引擎并存期间，需要明确哪套是权威
  - 调用方需要逐步改 import
  - 维护成本暂时增加

**选项 C：废弃 `strength_engine.py`，完全重写**
- 做法：直接删除 `strength_engine.py`，在 `canonical/` 目录下完全重写
- 优点：
  - 最干净，没有历史包袱
- 缺点：
  - 风险最高，所有调用方立即失效
  - 不建议在没有完整测试覆盖的情况下采用

**裁决标准**：
1. 是否符合 P6.1 冻结原则（禁止评分/阈值/权重）
2. 迁移风险是否可控
3. 是否便于逐步验证和回滚
4. 是否符合"确定性计算优先"原则

**建议**：选项 B（新建 `canonical_state_engine.py`，逐步替换）

---

### 🔴 决策点 2：数据源统一 — 以哪套为权威？

**背景**：
项目中存在 3 套并行的核心数据源：

| 数据 | 位置 1 | 位置 2 | 位置 3 |
|------|--------|--------|--------|
| 十二长生表 | `bazi_l1_facts.py` `TIAN_GAN_TWELVE_GROWTH` | `reasoning/bazi_fixed_tables.py` `LONGHU_STAGE` | - |
| 藏干表 | `bazi_l1_facts.py` `BRANCH_HIDDEN_STEMS`（完整三层） | `reasoning/bazi_ten_gods.py` `BRANCH_HIDDEN_STEMS` | `bazi_engine.py` `_BRANCH_HIDDEN_MAIN`（只有主气） |
| 十神计算 | `bazi_engine.py` `_ten_god` | `reasoning/bazi_ten_gods.py` `ten_god` | - |

其中 `bazi_l1_facts.py` 是 P6.1-A 的专门成果，明确标注了 Implementation Source（`freddylamlc/bazi-patterns`）和体系声明（阳顺阴逆，火土同生）。

**需要裁决的问题**：
以哪套数据源作为唯一权威？其他套如何处理？

**选项 A：以 `bazi_l1_facts.py` 为唯一权威**
- 做法：所有模块统一引用 `bazi_l1_facts.py` 的数据表；其他位置的表标记为 deprecated 或删除
- 优点：
  - `bazi_l1_facts.py` 是 P6.1-A 的专门成果，有明确的 Implementation Source 声明和体系声明
  - 数据最完整（藏干表有完整三层）
  - 符合"单一权威来源"原则
- 缺点：
  - 需要检查 `reasoning/` 下的表是否与 `bazi_l1_facts.py` 一致，如果不一致需要人工确认
  - 调用方需要改 import

**选项 B：以 `reasoning/bazi_ten_gods.py` + `reasoning/bazi_fixed_tables.py` 为权威**
- 做法：以 reasoning 目录下的表为权威，`bazi_l1_facts.py` 标记为参考
- 优点：
  - reasoning 目录下的表可能被更多模块引用
- 缺点：
  - 缺乏明确的 Implementation Source 声明
  - 藏干表可能不完整
  - 与 P6.1-A 的成果冲突

**选项 C：先对比，再决定**
- 做法：先完整对比 3 套数据源的差异，输出差异报告，人工确认哪套正确后再统一
- 优点：
  - 最稳妥，不会因为假设一致而引入错误
- 缺点：
  - 需要额外的对比工作

**裁决标准**：
1. 哪套数据有明确的 Implementation Source 声明和体系声明
2. 哪套数据最完整
3. 三套数据是否一致，如果不一致哪套更符合传统主流体系
4. 是否符合"单一权威来源"原则

**建议**：选项 C → 选项 A（先对比确认一致，然后以 `bazi_l1_facts.py` 为权威）

---

### 🔴 决策点 3：Canonical State 的实现路径

**背景**：
P6.1 文档中定义了完整的 Canonical State 结构：

```python
wangshuai: 旺 / 衰 / UNRESOLVED
qiangruo: 强 / 弱 / UNRESOLVED
root_state: ROOT_HEAVY / ROOT_LIGHT / ROOT_PRESENT / ROOT_NONE / ROOT_UNRESOLVED
dangzhong: CONFIRMED / QUALIFIED / CANDIDATE / NOT_ESTABLISHED / UNRESOLVED
seasonal_remedy: 独立调候状态
special_pattern: candidate / confirmed / rejected / unresolved
qualifiers: [...]
unresolved_reasons: [...]
```

但在核心代码中，这些状态字段**完全不存在**。`canonical/` 目录只有 3 个文件（`canonical_validator.py`、`composer.py`、`__init__.py`），非常薄。

**需要裁决的问题**：
Canonical State 应该在哪里实现？如何实现？

**选项 A：在 `canonical/` 目录下新建 `canonical_state.py` + `canonical_state_engine.py`**
- 做法：
  - `canonical_state.py`：定义 CanonicalState 数据结构（封闭枚举）
  - `canonical_state_engine.py`：实现从 BaziChart 到 CanonicalState 的确定性计算
- 优点：
  - 职责清晰，canonical 目录专门负责 Canonical State
  - 与 P6.1 文档结构对应
  - 便于独立测试和验证
- 缺点：
  - 需要新建文件
  - 调用方需要改 import

**选项 B：改造 `bazi_engine.py` 的 BaziChart，增加 Canonical State 字段**
- 做法：在 BaziChart 数据类中增加 `wangshuai`、`qiangruo`、`root_state` 等字段
- 优点：
  - 不增加新文件，调用方不需要改 import
- 缺点：
  - BaziChart 会变得非常臃肿（当前已经有 30+ 字段）
  - 确定性计算与原始数据混在一起，职责不清
  - 不符合"算→辨→解"三层分离的架构

**选项 C：在 `reasoning/` 目录下实现**
- 做法：在 reasoning 目录下新建 Canonical State 相关模块
- 优点：
  - reasoning 目录已经有 signal_engine 等，可以就近
- 缺点：
  - reasoning 目录职责已经很多（assertion、matcher、rule_resolver 等）
  - Canonical State 是"辨"层的核心，应该有独立的位置

**裁决标准**：
1. 是否符合"算→辨→解"三层分离架构
2. 职责是否清晰
3. 是否便于独立测试和验证
4. 是否符合 P6.1 文档定义

**建议**：选项 A（在 `canonical/` 目录下新建 `canonical_state.py` + `canonical_state_engine.py`）

---

### 🟡 决策点 4：Signal 引擎整合 — 3 套如何处理？

**背景**：
`reasoning/` 目录下存在 3 套 signal 相关引擎：
- `signal_engine.py`
- `semantic_signal.py`
- `p3_signal_engine.py`

三者职责不清，可能存在重复计算。

**需要裁决的问题**：
3 套 signal engine 如何整合？

**选项 A：整合为一套 `signal_engine.py`**
- 做法：梳理 3 套的职责，合并为一套，删除重复
- 优点：
  - 最干净，没有重复
- 缺点：
  - 需要详细梳理 3 套的职责和差异
  - 改动量大

**选项 B：明确分工，保留 3 套**
- 做法：明确 3 套各自的职责边界，在文档中说明，不合并
- 优点：
  - 改动小
- 缺点：
  - 仍然存在重复计算的可能
  - 新开发者难以理解为什么有 3 套

**选项 C：先梳理职责，再决定是否合并**
- 做法：先详细梳理 3 套 signal engine 的职责、输入、输出、调用方，输出梳理报告，再决定是否合并
- 优点：
  - 基于事实决策，不会误删有用的功能
- 缺点：
  - 需要额外的梳理工作

**裁决标准**：
1. 3 套是否真的职责不同，还是重复
2. 是否符合"辨"层的定位（从 CanonicalState 提取语义信号，不修改 CanonicalState）
3. 维护成本

**建议**：选项 C（先梳理职责，再决定）

---

### 🟡 决策点 5：旧系统的迁移策略

**背景**：
项目中存在多套旧系统：
- `strength_engine.py`：旧的评分式强弱计算引擎
- `legacy/assertion_v1/`：旧版断言引擎（16 个文件）
- `reasoning/` 下的旧模块：可能与新架构冲突

**需要裁决的问题**：
旧系统如何处理？是立即删除，还是标记 deprecated 逐步迁移？

**选项 A：标记 deprecated，逐步迁移**
- 做法：旧系统保留，标记为 deprecated，新代码使用新架构，逐步迁移调用方，全部迁移完成后删除
- 优点：
  - 风险可控，不会立即破坏现有功能
  - 可以逐步验证新架构的正确性
- 缺点：
  - 新旧并存期间维护成本高
  - 可能有人继续使用旧系统

**选项 B：立即删除旧系统**
- 做法：直接删除所有旧系统，全部使用新架构
- 优点：
  - 最干净
- 缺点：
  - 风险最高，可能破坏现有功能
  - 不建议在没有完整测试覆盖的情况下采用

**选项 C：隔离旧系统，不删除也不迁移**
- 做法：旧系统保留在 legacy 目录，不主动迁移，新功能全部使用新架构
- 优点：
  - 风险最低
- 缺点：
  - 旧系统永远存在，技术债务累积

**裁决标准**：
1. 迁移风险是否可控
2. 是否有完整的测试覆盖
3. 维护成本

**建议**：选项 A（标记 deprecated，逐步迁移），但 `strength_engine.py` 的评分部分应该尽快被新的 Canonical State 引擎替代

---

## 四、裁决输出要求

请独立审计者（GPT / 专家）基于以上决策点，输出以下内容：

### 4.1 每个决策点的裁决

对于每个决策点（1-5），输出：
- **裁决结果**：选择哪个选项（A / B / C / 其他）
- **裁决理由**：为什么选择这个选项，基于什么标准
- **风险评估**：选择这个选项的主要风险是什么
- **实施建议**：具体应该如何实施，分几步

### 4.2 整体架构建议

- 算层（Calculation）的最终架构应该是什么样
- 辨层（State/Signal）的最终架构应该是什么样
- 算→辨→解 三层之间的接口应该如何定义
- 不可逆边界应该如何保证

### 4.3 实施优先级

- 哪些工作应该立即做（P0）
- 哪些工作应该近期做（P1）
- 哪些工作可以后续做（P2）
- 哪些工作不应该做（禁止项）

### 4.4 验证标准

- 如何验证算层的正确性
- 如何验证辨层的正确性
- 如何验证算→辨→解 三层的闭环
- CALCULATION_GOLDEN_DATASET 应该包含什么

---

## 五、参考资料

### 5.1 核心代码文件

| 文件 | 行数 | 说明 |
|------|------|------|
| `src/tongshu/engines/bazi_engine.py` | 728 | 核心八字计算引擎，BaziChart 数据结构，固定数据表 |
| `src/tongshu/engines/bazi_l1_facts.py` | 518 | P6.1-A 成果，L1 事实数据（十二长生、藏干） |
| `src/tongshu/engines/strength_engine.py` | 391 | 旧评分式强弱计算引擎（违反 P6.1 原则） |
| `src/tongshu/engines/time_resolver.py` | 62 | 时间解析器 |
| `src/tongshu/canonical/canonical_validator.py` | - | Canonical 验证器（很薄） |
| `src/tongshu/canonical/composer.py` | - | 组合器（很薄） |
| `src/tongshu/reasoning/bazi_ten_gods.py` | - | 十神计算，藏干表 |
| `src/tongshu/reasoning/bazi_fixed_tables.py` | - | 固定数据表（十二长生等） |
| `src/tongshu/reasoning/signal_engine.py` | - | 信号引擎 |
| `src/tongshu/reasoning/semantic_signal.py` | - | 语义信号 |
| `src/tongshu/reasoning/p3_signal_engine.py` | - | P3 信号引擎 |

### 5.2 项目文档

| 文档 | 位置 | 说明 |
|------|------|------|
| AUDIT_GUIDE.md | 仓库根目录 | 项目审计指南 |
| README.md | 仓库根目录 | 项目说明 |
| PROJECT_STATUS_SNAPSHOT.md | docs/ | 项目状态快照 |
| 五部经典资料索引_Canonical_Source_Registry.md | docs/ | 原典资料索引 |
| calc_golden_dataset_001.json | data/ | 1983 命例计算记录（Step 1） |

### 5.3 P6.1 冻结的核心原则

1. 禁止五行计分→强弱
2. 禁止 strength_score / root_score
3. 禁止长生状态自动制造通根
4. 禁止合=合化
5. 禁止水多木漂直接改强弱
6. 禁止调候→强弱
7. 禁止未授权组合规则→最终强弱
8. 禁止关键词→特殊格局
9. 禁止 MATCHED→自动授权结论
10. 禁止 Assertion 反推 Canonical State

---

## 六、裁决者注意事项

1. **不要假设文档与实现一致**：本项目存在严重的文档与实现脱节问题，P6.1-P6.5 的治理成果主要存在于文档中，核心代码并没有真正实现。请以实际代码为准。

2. **不要强行授权**：如果某个决策点的信息不足，请明确标记为 UNRESOLVED，不要为了给出完整答案而强行决策。

3. **优先考虑确定性和可验证性**：命理计算的核心是确定性，任何引入不确定性、黑箱、评分的方案都应该谨慎。

4. **允许 UNRESOLVED**：对于无法裁决的问题，明确标记为 UNRESOLVED 并说明原因，比强行给出错误答案更有价值。

5. **原典授权优先**：任何涉及命理规则的决策，都应该以五部经典的原典授权为优先，而不是以实现方便为优先。

---

*本裁决书基于 2026-08-29 对项目代码的全面深度审核，列出了当前最核心的架构决策点。请独立审计者基于实际代码和原典依据做出裁决。*
