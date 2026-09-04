# ZIWEI CURRENT ARCHITECTURE AUDIT

> **审计时间**：2026-09-02
> **审计范围**：`src/tongshu/engines/ziwei/` 及相关依赖
> **审计原则**：只审计，不修改业务逻辑
> **基于 commit**：main 分支最新

---

## 1. 当前谁负责计算？

**答案**：`ZiweiEngine` (ziwei_engine.py) + `iztro` npm 包

### 计算职责分解

| 职责 | 负责模块 | 方法 |
|------|---------|------|
| 阳历→农历转换 | `ZiweiAdapter` | `compute(ctx, gender)` |
| 命宫/身宫定位 | `ZiweiEngine` | `_compute_via_iztro()` |
| 十四主星安布 | `iztro` (npm) | `byLunar()` |
| 十二宫布宫 | `iztro` (npm) | `astrolabe.palaces` |
| 大限方向 | `ShuntianZiweiDependencyAdapter` | `adapt_from_chart()` |
| 四化表 | `ZiweiEngine.GAN_SIHUA` | 硬编码字典 |
| 流月/流日四化 | `ZiweiEngine` | `flow_month_mutagen()`, `flow_day_mutagen()` |
| 三方四正 | `ZiweiEngine` | `get_sanfang_sizheng()`, `sanfang_sizheng()` |
| 宫干自化 | `ZiweiEngine` | `get_zigong_zihua()`, `palace_self_mutagen()` |
| 来因宫 | `ZiweiEngine` | `get_laiyin_gong()` |
| 格局识别 | `ziwei_pattern.py` | `recognize_patterns()`, `recognize_patterns_from_chart()` |

### 计算输出

```text
ZiweiChart (dataclass)
├── soul_palace_main_star: str          # 命宫第一主星(拼音键)
├── soul_palace_main_stars: list        # 命宫全部主星(V2.6双主星)
├── soul_palace_sihua: list             # 命宫四化
├── palace_data: dict                   # 宫位原始数据
│   ├── raw_soul_main_star: str         # 命宫主星(中文)
│   ├── soul_borrowed: bool             # 是否借星
│   ├── soul_earthly_branch: str        # 命宫地支
│   ├── body_earthly_branch: str        # 身宫地支
│   └── decadal/yearly/monthly/daily_mutagen
├── daily_luck_palace: str              # 流日命宫
└── source: str                         # "iztro" | "stub" | "stub_with_error"
```

---

## 2. 当前谁负责排盘？

**答案**：`iztro` npm 包（通过 subprocess 调用）

### 排盘流程

```text
SolarDate (阳历)
    ↓ ZiweiAdapter.compute()
LunarDate (农历)
    ↓ ZiweiEngine._compute_via_iztro()
iztro byLunar() → astrolabe
    ↓ JavaScript 脚本提取
ZiweiChart (Python dataclass)
```

### 关键依赖

| 依赖 | 版本 | 状态 |
|------|------|------|
| `iztro` npm | 2.6.0 | ✅ 可用 |
| `lunar_python` | — | ✅ 可用 |
| `node` | — | ✅ 可用 |

### 已知问题

- **iztro 2.6.0 大限方向 bug**：已用 `ShuntianZiweiDependencyAdapter` 修复
  - 原bug：使用 earthlyBranch yinYang + gender 判断方向
  - 正确：应使用 heavenly stem yinYang + gender
  - 修复状态：✅ 已隔离在 dependency_adapter.py，不影响核心计算

---

## 3. 当前谁负责三方四正？

**答案**：`ZiweiEngine` (两个方法)

### 方法清单

| 方法 | 位置 | 用途 |
|------|------|------|
| `get_sanfang_sizheng(full_chart, palace_name)` | ziwei_engine.py:368 | 返回宫位结构 dict |
| `sanfang_sizheng(palace_name)` | ziwei_engine.py:696 | 返回宫名列表 |

### 实现状态

```text
✅ 本宫 + 对宫(+6) + 三合宫(+4, +8) 逻辑正确
✅ 根据地支索引计算，不依赖宫名
⚠️ 但未形成独立 Fact 对象（SanfangFact 不存在）
```

---

## 4. 当前谁负责四化？

**答案**：`ZiweiEngine.GAN_SIHUA` 硬编码字典

### 四化职责分解

| 职责 | 负责模块 | 状态 |
|------|---------|------|
| 四化表定义 | `GAN_SIHUA` (ziwei_engine.py:80) | ⚠️ 硬编码，未Profile化 |
| 生年四化 | `iztro` npm | ✅ 通过 horoscope() |
| 大限四化 | `flow_decadal_mutagen()` | ✅ 已实现 |
| 流年四化 | `flow_years_mutagen()` | ✅ 已实现 |
| 流月四化 | `flow_month_mutagen()` | ✅ 已实现 |
| 流日四化 | `flow_day_mutagen()` | ✅ 已实现 |
| 宫干自化 | `get_zigong_zihua()`, `palace_self_mutagen()` | ✅ 已实现 |
| 来因宫 | `get_laiyin_gong()` | ✅ 已实现 |

### 关键发现

```text
⚠️ GAN_SIHUA 注释称"中州派/王亭之主流版本"
⚠️ 实际内容为通行版（庚干天同化忌）
⚠️ 与明代《全书》原版有差异（天相化忌）
⚠️ 中州派特殊版本（天府化科）未被采纳
⚠️ 四化表未 Profile化，无法切换流派版本
```

---

## 5. 当前谁负责格局？

**答案**：`ziwei_pattern.py` (硬编码列表)

### 格局识别状态

| 组件 | 状态 | 问题 |
|------|------|------|
| `PATTERNS` 列表（37条） | ⚠️ 硬编码 | 未验证是否全来自《全书》 |
| `recognize_patterns()` | ✅ 实现 | 返回 (格局名, 说明) |
| `recognize_patterns_from_chart()` | ✅ 实现 | 支持空宫借星标注 |
| 格局来源标注 | ❌ 缺失 | 未标注每条格局的出处 |

### 需核实的声明

```text
代码注释声称："仅收录《紫微斗数全书》及主流名家公认的常见格局"
实际状态：37条格局未逐条核对原典出处
```

---

## 6. 当前谁负责解释？

**答案**：混在多个模块中，边界不清

### 解释层现状

| 模块 | 内容 | 问题 |
|------|------|------|
| `ziwei_knowledge.py` | 主星脏腑映射、宫位主题、性格关键词 | ⚠️ 注释称"用于score_ziwei"，属legacy路径 |
| `MAIN_STAR_USO` | 星曜→语义类别映射 | ⚠️ 混入计算层（ziwei_engine.py） |
| `NIHAIXIA_ZWDS_CONSTRAINTS.md` | 17条硬约束 | ✅ RATIFIED，但部分约束来源待核实 |
| `pattern.py` | 格局说明文本 | ⚠️ 硬编码在代码中 |

### 关键问题

```text
❌ 事实与解释未分离
❌ score_ziwei 路径仍存在（legacy）
❌ 无独立 Diagnosis / Judgment 层
```

---

## 7. 当前哪里存在 score？

**答案**：`ziwei_knowledge.py` 及关联路径

### score_ziwei 引用位置

| 文件 | 行号 | 内容 |
|------|------|------|
| `ziwei_knowledge.py` | 5, 42 | 注释明确引用 "score_ziwei" |
| `PROJECT_ISSUE_LOG.md` | 236, 248, 257, 266, 378 | 历史讨论记录 |
| `P0_2_hidden_scoring_scan_raw.json` | 2465, 2470 | 扫描结果 |

### 状态

```text
⚠️ score_ziwei 已被标记为 LEGACY / FORBIDDEN PRODUCTION PATH
⚠️ 但 ziwei_knowledge.py 仍存在且未被删除
⚠️ 代码注释仍引用 score_ziwei
```

---

## 8. 当前哪里存在 LLM？

**答案**：渲染层（非紫微专属）

### LLM 使用位置

| 模块 | 用途 | 是否紫微专属 |
|------|------|-------------|
| `render/renderer.py` | 最终文本渲染 | ❌ 通用 |
| `canonical/composer.py` | SIR 构造 | ❌ 通用 |

### 关键发现

```text
✅ 紫微计算层无 LLM 调用
✅ 信号提取层无 LLM 调用
⚠️ 渲染层使用 LLM，但这是通用架构，非紫微专属问题
```

---

## 9. 当前哪里把事实和解释混在一起？

**答案**：多处

### 混用清单

| 位置 | 事实 | 解释 | 问题 |
|------|------|------|------|
| `ziwei_engine.py:38-53` | MAIN_STAR_USO 映射 | 语义类别（SUPPORT/RESOURCE等） | 混入计算层 |
| `ziwei_pattern.py:12-55` | 格局名 | 格局说明文本 | 硬编码在代码中 |
| `ziwei_knowledge.py` | 主星脏腑映射 | 健康断事结论 | 整文件属legacy |
| `GAN_SIHUA` 注释 | 四化表 | "中州派主流版本" | 声明与实际不符 |

---

## 10. 当前哪里存在派别混用？

**答案**：`GAN_SIHUA` 四化表

### 混用详情

```text
代码声明："中州派/王亭之主流版本"
实际内容：通行版（庚干天同化忌）

中州派实际声明：
- 戊干：太阳/天府化科（非右弼）
- 庚干：天府化科（非太阴）
- 壬干：天府化科（非左辅）

当前代码未采纳中州派特殊版本。
```

---

## 11. 当前哪些代码是真生产路径？

### 生产路径图

```text
API Request
    ↓
ComputeStage
    ├── BaziAdapter.compute() → BaziChart
    ├── ZiweiAdapter.compute() → ZiweiChart  ✅ 生产路径
    │       └── ZiweiEngine.compute()
    │               └── iztro byLunar()
    ├── HuangliEngine.compute() → HuangliDay
    ├── ZiweiEngine.extract_baseline_signal() → Signal  ✅ 生产路径
    ├── CrossDomainOrchestrator  ✅ 生产路径
    └── CanonicalComposer  ✅ 生产路径
        ↓
RenderStage → LLM render / template fallback
    ↓
ValidationStage → Layer1/2/3 + Gates
```

### 真生产路径确认

| 组件 | 状态 | 说明 |
|------|------|------|
| `ZiweiAdapter.compute()` | ✅ 生产路径 | 阳历→农历→iztro |
| `ZiweiEngine.extract_baseline_signal()` | ✅ 生产路径 | 命宫主星→Signal |
| `ZiweiEvidenceProducer.produce()` | ⚠️ 部分生产 | 仅提取事实，未完整接入 |
| `ShuntianZiweiDependencyAdapter` | ✅ 生产路径 | 大限方向修正 |

---

## 12. 哪些是 legacy/dead code？

### Legacy 清单

| 文件/模块 | 状态 | 说明 |
|----------|------|------|
| `ziwei_knowledge.py` | ⚠️ Legacy | 注释明确称"用于score_ziwei"，属废弃路径 |
| `score_ziwei` 引用 | ⚠️ Legacy | 多处引用，但已标记为FORBIDDEN |
| `MAIN_STAR_USO` (计算层) | ⚠️ 需迁移 | 语义映射不应在计算层 |
| `ziwei_pattern.py` | ⚠️ 需重构 | 格局识别应迁移到 Rule Graph |

### Dead Code 确认

```text
❌ 无明确 dead code（所有模块都有引用）
⚠️ 但部分功能已废弃（如 score_ziwei 路径）
```

---

## 13. 哪些代码可以复用？

### 可复用组件

| 组件 | 复用方式 | 说明 |
|------|---------|------|
| `ZiweiChart` | → FrozenZiweiChart | 作为 Frozen Chart 基础 |
| `iztro` 调用逻辑 | → Calculation 层 | 直接复用 |
| `ShuntianDependencyAdapter` | → Calculation 层 | 直接复用 |
| `get_sanfang_sizheng()` | → Fact Layer | 提取为 SanfangFact |
| `palace_self_mutagen()` | → Method Profile | 飞星派 Method Profile |
| `recognize_patterns()` | → Rule Graph | 迁移为规则 |

---

## 14. 哪些代码必须拆分？

### 拆分清单

| 当前状态 | 目标结构 | 理由 |
|---------|---------|------|
| `MAIN_STAR_USO` 在计算层 | → Signal Layer | 语义映射非计算事实 |
| `GAN_SIHUA` 硬编码 | → TransformationProfile | 各派四化表不同 |
| `PATTERNS` 硬编码 | → Rule Graph | 需带 method_id |
| `ziwei_knowledge.py` | → 删除/归档 | Legacy路径 |
| `ZiweiChart` 无来源标注 | → FrozenZiweiChart | 需明确计算政策 |

---

## 15. 哪些代码必须删除？

### 删除清单

| 代码 | 理由 |
|------|------|
| `ziwei_knowledge.py` | Legacy路径，属score_ziwei |
| `MAIN_STAR_USO` 从计算层移除 | 混入语义解释 |
| `GAN_SIHUA` 硬编码（保留接口） | 需改为 Profile 化 |

---

## 16. 依赖关系图

### 完整依赖图

```text
                     API/Service
                          │
              ┌───────────┼───────────┐
              ↓           ↓           ↓
       ComputeStage  RenderStage  ValidationStage
              │
    ┌─────────┼─────────┐
    ↓         ↓         ↓
BaziEngine  ZiweiEngine  HuangliEngine
    │         │           │
    │    ┌────┴────┐      │
    │    ↓         ↓      │
    │ ZiweiAdapter  │      │
    │    │          │      │
    │    ↓          │      │
    │ iztro(npm)    │      │
    │    │          │      │
    │    ↓          │      │
    │ ZiweiChart    │      │
    │    │          │      │
    │    ├→ extract_baseline_signal() → Signal
    │    │
    │    ├→ evidence_producer → EngineEvidence
    │    │
    │    └→ pattern.py → patterns (LEGACY)
    │
    └→ ShuntianDependencyAdapter → Direction修正
```

### 关键依赖

| 依赖 | 类型 | 状态 |
|------|------|------|
| `iztro` npm | 外部包 | ✅ 可用 |
| `lunar_python` | Python包 | ✅ 可用 |
| `node` | 运行时 | ✅ 可用 |
| `ShuntianDependencyAdapter` | 内部 | ✅ 已集成 |

---

## 17. 测试基线

### 当前测试状态

```text
总测试数: 71 passed, 32 subtests passed
耗时: 32.21s
状态: ✅ ALL PASS
```

### 紫微相关测试

| 测试文件 | 测试数 | 状态 |
|---------|--------|------|
| `test_ziwei_engine.py` | — | ✅ PASS |
| `test_ziwei_pattern.py` | — | ✅ PASS |
| `test_ziwei_chart_cross_validate.py` | — | ✅ PASS |
| `test_ziwei_phase_a0_extended.py` | — | ✅ PASS |
| `test_vertical_slice_ziwei.py` | — | ✅ PASS |

---

## 18. Gate Z0 完成检查

### 必答题确认

| 问题 | 答案 | 状态 |
|------|------|------|
| 谁负责计算？ | ZiweiEngine + iztro | ✅ 明确 |
| 谁负责排盘？ | iztro npm | ✅ 明确 |
| 谁负责三方四正？ | ZiweiEngine | ✅ 明确 |
| 谁负责四化？ | GAN_SIHUA 硬编码 | ⚠️ 需重构 |
| 谁负责格局？ | ziwei_pattern.py | ⚠️ 需迁移 |
| 谁负责解释？ | 多处混用 | ❌ 边界不清 |
| 哪里存在 score？ | ziwei_knowledge.py | ⚠️ Legacy |
| 哪里存在 LLM？ | 渲染层 | ✅ 非紫微专属 |
| 事实解释混用？ | 多处 | ❌ 需分离 |
| 派别混用？ | GAN_SIHUA | ❌ 需Profile化 |
| 真生产路径？ | Adapter→Engine→iztro | ✅ 明确 |
| Legacy code？ | knowledge.py, USO | ⚠️ 需清理 |
| 可复用？ | Chart, Adapter, 三方四正 | ✅ 明确 |
| 需拆分？ | 四化表、格局、USO | ⚠️ 明确 |
| 需删除？ | knowledge.py | ⚠️ 明确 |

---

## 19. 生产路径确认

### 当前生产路径

```text
API
  ↓
ComputeStage
  ↓
ZiweiAdapter.compute(ctx, gender)
  ↓
ZiweiEngine._compute_via_iztro()
  ↓
iztro byLunar()
  ↓
ZiweiChart
  ↓
extract_baseline_signal() → Signal
  ↓
CrossDomainOrchestrator → CanonicalContent
  ↓
RenderStage → LLM / Template
  ↓
ValidationStage → Gates
```

### 禁止路径（需fail-closed）

```text
❌ API → LLM → Judgment（无Fact/Rule层）
❌ API → score_ziwei → Judgment（legacy路径）
❌ Signal → Judgment（无Rule匹配）
❌ 三合Judgment → 飞星Judgment（跨派依赖）
```

---

## 20. 下一步行动

### Phase A1: Frozen Chart 契约

- [ ] 定义 `FrozenZiweiChart` 数据结构
- [ ] 从现有 `ZiweiChart` 提取计算事实
- [ ] 明确计算政策（历法、时间、四化版本）

### Phase A2: Fact Layer 构建

- [ ] 派生 `PalaceFact`, `StarPlacementFact`, `SanfangFact`
- [ ] 派生 `TransformationFact`, `SelfTransformationFact`
- [ ] 每个 Fact 只回答"是什么、在哪里、来自哪里"

### Phase A3: Method Profile 构建

- [ ] 定义 `ZiweiMethodProfile` 接口
- [ ] 实现 `SANHE` Method Profile
- [ ] 实现 `FEIXING` Method Profile（接口先行）
- [ ] 实现 `ZHONGZHOU` Method Profile（证据确认后）

---

*Z0 审计完成。测试基线：71 passed, 32 subtests passed.*
