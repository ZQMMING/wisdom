# ZIPING P0 Gap 裁决表 — BOT-MASTER 最终裁决

**任务 ID**: T-ENGINE-BAZI-002 Phase 4
**执行者**: @bot-ziping
**日期**: 2026-09-07
**依据**: BOT-MASTER 基线文档 + Phase 4 审计证据

---

## 一、裁决原则（BOT-MASTER 明确）

> **违规的是它参与子平命理最终裁决的语义方式，而不是数学函数本身。**

```
允许:
  - sum() / ratio / count 用于工程统计、覆盖率统计、结构性计数
  - 特征提取（如 heluo_wuxing_imbalance）

禁止:
  - score > threshold → judgment (旺/弱/格局成立/不成立)
  - confidence = weighted_ratio(...) → 命理裁决
  - 投票 / 百分比 / 概率 / 权重平均 / 置信度聚合 / 评分阈值
```

---

## 二、7 个 Gap 最终裁决

| # | Gap | 类别 | 裁决 | 修复 | 测试 | 状态 |
|---|-----|------|------|------|------|------|
| 1 | ContextAssembler 调用 bazi_engine.compute() | ARCHITECTURE_VIOLATION | 🔴 P0 BLOCK | 删除或重构 | 必须 | 待修复 |
| 2 | 硬编码路径依赖 | PATH_DEPENDENCY | 🔴 P0 BLOCK | 改为相对路径 | 必须 | 待修复 |
| 3 | EvidenceRegistry / RuleRegistry 孤立 | MISSING_IMPLEMENTATION | 🟡 P1 | 集成或移除 | 建议 | 待裁决 |
| 4 | RuleMatcher.sum() 计算 specificity | 结构性计数 | 🟢 APPROVED | 无需修改 | N/A | ✅ 通过 |
| 5 | SignalEngine.ratio 判断五行失衡 | 特征提取 | 🟢 APPROVED | 无需修改 | N/A | ✅ 通过 |
| 6 | Signal 类缺少 domain 字段 | MISSING_IMPLEMENTATION | 🟡 P1 | 添加 domain 字段 | 建议 | 待修复 |
| 7 | 无 Domain Judgment 实现 | MISSING_IMPLEMENTATION | 🔴 P0 BLOCK | 建立 Judgment 层 | 必须 | 待修复 |

### 裁决说明

#### Gap 1: 🔴 P0 BLOCK

**事实**: `context_assembler.py:532` 有 `self.bazi_engine.compute()` 调用  
**证据**: 第532行代码 + 第570-581行 `__main__` 测试块  
**影响**: 当前未进入生产路径（仅在 `__main__` 中），但存在架构违规风险  
**根因**: ContextAssembler 设计为独立可运行的排盘+上下文组装组件，与生产路径（ComputeStage）重复  
**修复**: 删除第532行的 compute() 调用，改为消费传入的 chart 参数  
**测试**: 删除后确认 `__main__` 测试块仍能正确运行（需要传入 chart）  

#### Gap 2: 🔴 P0 BLOCK

**事实**: 生产代码中发现硬编码绝对路径  
**证据**: `phase_b1_evidence_connection.py:724` 等  
**影响**: 项目移动后路径失效  
**根因**: Phase B-1/B-2 脚本编写时使用了硬编码路径  
**修复**: 改为 `Path(__file__).resolve().parents[N]`  
**测试**: 移动项目目录后确认仍能正常运行  

#### Gap 3: 🟡 P1 — 待 BOT-MASTER 裁决

**事实**: `phase_b1_evidence_connection.py` 定义了 EvidenceRegistry 和 RuleRegistry，但未被导入  
**证据**: grep 搜索无结果  
**影响**: Rule Lifecycle 状态机未生效，Authorization Gate 仅存在于测试代码  
**选项 A**: 集成 Registry 到生产路径  
**选项 B**: 移除 Phase B-1 的 Registry 代码（保留 phase_b2_1_remediation.py 作为参考）  
**测试**: 根据裁决决定  

#### Gap 4: 🟢 APPROVED — 无需修复

**事实**: `matcher.py:285-295` 使用 `sum()` 计算条件叶子节点数量  
**语义分析**: 
- 用途: 计算 specificity（条件复杂度），作为冲突解决时的参考优先级
- 不涉及命理裁决，不决定旺/弱/格局成立/不成立
- 属于结构性计数，非 aggregation  
**裁决**: ✅ APPROVED — 不属于禁止的"命理裁决聚合"  

#### Gap 5: 🟢 APPROVED — 无需修复

**事实**: `signal_engine.py:101-106` 使用 ratio 判断五行失衡  
**语义分析**:
- 用途: 特征提取，构建 RuleContext 的 `heluo_wuxing_imbalance` 字段
- 不直接决定命理裁决，而是作为规则条件的输入
- 属于结构性特征提取，非 aggregation  
**裁决**: ✅ APPROVED — 不属于禁止的"命理裁决聚合"  

#### Gap 6: 🟡 P1 — 建议修复

**事实**: Signal 类缺少 `domain` 字段  
**影响**: 无法区分 Signal 属于哪个辨证域（旺衰/格局/用神/十神语义/事件判断）  
**修复**: 在 Signal 类中添加 `domain: str` 字段  
**测试**: 确认各域 Signal 能正确标记 domain  

#### Gap 7: 🔴 P0 BLOCK

**事实**: 搜索 `DomainJudgment` / `domain_judgment` / `Judgment.*Synthesis` 无结果  
**影响**: 
- Signal 直接输出，未经过 Domain Judgment 层
- 五大领域无法独立产出 Judgment
- Synthesis 机制不存在  
**根因**: ZIPING 规则引擎架构尚未完整实现，只有 RuleMatcher + SignalEngine，缺少 Judgment 层  
**修复**: 
1. 建立 Domain Judgment 类（旺衰/格局/用神/十神语义/事件判断）
2. 每个域独立消费本域 Signal，产出本域 Judgment
3. 建立 Synthesis 机制，汇总各域 Judgment 为最终语义信号  
**测试**: 端到端测试确认五大领域各自产出 Judgment 并能 Synthesis  

---

## 三、修复顺序（锁死）

```text
P0-1: ContextAssembler 修复 (Gap 1)
    ↓
P0-2: 硬编码路径修复 (Gap 2)
    ↓
P0-3: Evidence → Rule 链路验证 (Gap 3 裁决后)
    ↓
P0-4: Rule 确定性执行验证 (Gap 4/5 已通过)
    ↓
P0-5: Domain Judgment 层建立 (Gap 6/7)
    ↓
P0-6: Judgment Synthesis 建立 (Gap 7)
    ↓
P0-7: 端到端测试 (全部修复后)
    ↓
补充 YG 用神规则 (基础链路稳定后)
    ↓
测试覆盖
    ↓
冻结申请
```

**重要**: 不要先补 YG 规则！必须先稳定基础链路。

---

## 四、可执行修复清单

### Fix-001: 删除 ContextAssembler 中的重复排盘调用

**文件**: `src/tongshu/reasoning/context_assembler.py`  
**行号**: 527-532  
**操作**: 
1. 删除第532行: `chart = self.bazi_engine.compute(...)`
2. 修改 `assemble()` 方法签名，接受已计算的 chart 作为参数
3. 修改 `__main__` 测试块，先调用 BaziEngine.compute()，再传入 assemble()

**预估工作量**: 30 分钟  
**风险**: 低（仅影响测试块）

---

### Fix-002: 修复硬编码路径

**涉及文件**: 
- `src/tongshu/phase_b1_evidence_connection.py` (3处)
- `src/tongshu/phase_b2_1_remediation.py` (2处)
- `src/tongshu/phase_b2_rule_authorization.py` (3处)

**操作**: 将 `Path("D:/shuntian/...")` 改为 `Path(__file__).resolve().parents[N] / "..."`

**预估工作量**: 1 小时  
**风险**: 低

---

### Fix-003: 决策 Gap 3（EvidenceRegistry 集成或移除）

**等待 BOT-MASTER 裁决**:
- 选项 A: 集成 Registry 到生产路径
- 选项 B: 移除 Phase B-1 的 Registry 代码

**预估工作量**: 2-4 小时（取决于裁决）  
**风险**: 中

---

### Fix-004: 添加 Signal.domain 字段

**文件**: `src/tongshu/reasoning/signal_engine.py`  
**操作**: 
1. 在 Signal 数据类中添加 `domain: str` 字段
2. 修改 `_rule_to_signal()` 函数，从规则中读取 domain 信息
3. 更新所有创建 Signal 的地方

**预估工作量**: 1 小时  
**风险**: 中（可能影响现有测试）

---

### Fix-005: 建立 Domain Judgment 层

**新增文件**: `src/tongshu/reasoning/domain_judgment.py`  
**操作**: 
1. 定义 DomainJudgment 数据类
2. 实现五大域的 Judgment 逻辑
3. 每个域独立消费本域 Signal，产出 Judgment

**预估工作量**: 1-2 天  
**风险**: 高（核心架构变更）

---

### Fix-006: 建立 Judgment Synthesis 机制

**新增/修改文件**: `src/tongshu/reasoning/synthesis.py`  
**操作**: 
1. 定义 Synthesis 逻辑
2. 汇总各域 Judgment 为最终语义信号
3. 处理域间冲突

**预估工作量**: 1-2 天  
**风险**: 高（核心架构变更）

---

### Fix-007: 补充缺失的 Schema 文件

**新增文件**: 
- `docs/rule.schema.json`
- `docs/evidence.schema.json`

**操作**: 根据现有规则/证据格式定义 Schema

**预估工作量**: 2 小时  
**风险**: 低

---

### Fix-008: 端到端测试验证

**操作**: 
1. 修复完成后运行所有测试
2. 补充缺失的测试用例
3. 确认 Golden Cases 通过

**预估工作量**: 1 天  
**风险**: 低

---

## 五、状态追踪

| Fix | 状态 | 完成日期 | 测试状态 |
|-----|------|----------|----------|
| Fix-001 | ⏳ 待执行 | - | - |
| Fix-002 | ⏳ 待执行 | - | - |
| Fix-003 | ⏸️ 等待裁决 | - | - |
| Fix-004 | ⏳ 待执行 | - | - |
| Fix-005 | ⏳ 待执行 | - | - |
| Fix-006 | ⏳ 待执行 | - | - |
| Fix-007 | ⏳ 待执行 | - | - |
| Fix-008 | ⏳ 待执行 | - | - |

---

**执行者**: @bot-ziping  
**裁决者**: BOT-MASTER  
**状态**: 等待裁决后开始执行
