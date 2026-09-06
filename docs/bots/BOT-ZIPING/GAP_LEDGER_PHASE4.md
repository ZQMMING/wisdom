# ZIPING Gap Ledger — Phase 4 P0 深挖阶段

**任务 ID**: T-ENGINE-BAZI-002 Phase 4 P0 Deep Dive
**执行者**: @bot-ziping
**日期**: 2026-09-07
**状态**: 证据追踪完成，等待 BOT-MASTER 裁决

---

## 执行摘要

本次审计共发现 **400 个 P0 问题**、5 个 P1 问题、7 个 INFO。

但大部分 P0 来自 P0-2 路径扫描（脚本中的硬编码路径）。核心架构问题聚焦在以下 **7 个关键 Gap**：

| # | 类别 | 问题 | 严重性 | Git 状态 |
|---|------|------|--------|----------|
| 1 | ARCHITECTURE_VIOLATION | ContextAssembler 调用 bazi_engine.compute() | P0 | 现存代码 |
| 2 | PATH_DEPENDENCY | 大量硬编码路径 | P0 | 遗留问题 |
| 3 | MISSING_IMPLEMENTATION | EvidenceRegistry / RuleRegistry 孤立 | P1 | 设计存在未集成 |
| 4 | ARCHITECTURE_VIOLATION | RuleMatcher 使用 sum() 计算 specificity | P0 | 设计争议 |
| 5 | ARCHITECTURE_VIOLATION | SignalEngine 使用 ratio/confidence | P0 | 需审查 |
| 6 | MISSING_IMPLEMENTATION | Signal 类缺少 domain 字段 | P1 | 设计缺失 |
| 7 | MISSING_IMPLEMENTATION | 无 Domain Judgment 实现 | P0 | 架构缺口 |

---

## Gap 1: ContextAssembler 重复排盘风险

### 问题描述
`context_assembler.py:532` 调用 `self.bazi_engine.compute()` 重新排盘：

```python
chart = self.bazi_engine.compute((birth_year, birth_month, birth_day, birth_hour), gender)
```

### 证据
- 文件位置: `src/tongshu/reasoning/context_assembler.py:532`
- 调用点: 仅在 `__main__` 块（第570-581行），未进入生产路径
- 生产路径: `ComputeStage` 通过 `BaziAdapter.compute()` 正确调用

### Git 历史
- ContextAssembler 共有 2 次提交
- 需要进一步检查是否曾有主动删除的 commit

### 影响
- 当前不影响生产，但代码存在架构违规风险
- 如果未来有人误用 ContextAssembler.assemble()，会导致重复排盘

### 裁决建议
**P0 BLOCK**: 必须删除或重构此调用，改为仅消费已计算的 chart

---

## Gap 2: 硬编码路径依赖

### 问题描述
扫描发现大量硬编码路径，主要集中在：
- `scripts/*.py` (50+)
- `tests/*.py` (10+)
- `src/tongshu/phase_b*.py` (5+)

### 证据示例
```python
# scripts/phase_b1_evidence_connection.py:724
loader = EvidenceLoader(Path("D:/shuntian/data/evidence"))

# scripts/phase_b2_1_remediation.py:667
output_path = Path("D:/shuntian/docs/bots/BOT-ZIPING/PHASE_B2_1_REMEDIATION_AUDIT.md")
```

### 分类
- **Scripts 目录**: 临时脚本，路径硬编码可接受（不影响生产）
- **Production 代码**: 需要改为 `Path(__file__).resolve().parents[N]`

### 影响
- 项目移动后，脚本和测试会失败
- 生产代码中的硬编码路径会导致运行时错误

### 裁决建议
**P0 BLOCK**: 生产代码中的硬编码路径必须修复

---

## Gap 3: EvidenceRegistry / RuleRegistry 孤立

### 问题描述
`phase_b1_evidence_connection.py` 定义了 `EvidenceRegistry` 和 `RuleRegistry` 类，但未被任何生产代码导入。

### 证据
```python
# grep 搜索无结果
# src/tongshu/phase_b1_evidence_connection.py 存在但未导入
```

### 影响
- Phase B-1 的 Registry 设计未进入生产路径
- Rule Lifecycle 状态机（DRAFT→EVIDENCE_VERIFIED→ADJUDICATED→AUTHORIZED→PRODUCTION）未生效
- Authorization Gate 仅存在于测试代码中

### Git 历史
- 需要检查是否有 merge 后被删除的 commit

### 裁决建议
**P1**: 需要决定是集成还是移除 Phase B-1 的 Registry 代码

---

## Gap 4: RuleMatcher 使用 sum() 计算 Specificity

### 问题描述
`matcher.py:285-295` 使用 `sum()` 计算条件的叶子节点数量作为 specificity：

```python
def count_conditions(conditions: dict | None) -> int:
    if not conditions:
        return 0
    if not isinstance(conditions, dict):
        raise ValueError(...)
    if "all" in conditions:
        return sum(count_conditions(c) for c in conditions["all"])
    if "any" in conditions:
        return sum(count_conditions(c) for c in conditions["any"])
    if "not" in conditions:
        return count_conditions(conditions["not"])
    return 1  # leaf
```

### 分析
- 这里的 `sum()` 是**结构性计数**，不是命理裁决
- 用于计算条件的复杂度（specificity），作为冲突解决时的参考
- BOT-MASTER 禁止的是 `score/weight/vote` 作为**命理裁决机制**

### 裁决建议
**P1**（需 BOT-MASTER 裁决）: 此用法是否属于"aggregation"？

---

## Gap 5: SignalEngine 使用 ratio 计算五行失衡

### 问题描述
`signal_engine.py:101-106` 使用 ratio 判断五行失衡：

```python
if ratio > _WUXING_OVER_THRESHOLD:
    out["heluo_wuxing_imbalance"] = "over"
elif ratio < _WUXING_UNDER_THRESHOLD:
    out["heluo_wuxing_imbalance"] = "under"
else:
    out["heluo_wuxing_imbalance"] = "none"
```

### 分析
- ratio 是**结构性特征提取**，不是命理裁决
- 用于构建 RuleContext，供规则条件判断使用
- 与 score/weight/vote 不同，这里没有"聚合裁决"的含义

### 裁决建议
**P1**（需 BOT-MASTER 裁决）: 此用法是否属于"aggregation"？

---

## Gap 6: Signal 类缺少 domain 字段

### 问题描述
`Signal` 类（`signal_engine.py:117-131`）定义：

```python
@dataclass(frozen=True)
class Signal:
    signal_id: str
    ontology_type: str
    direction: str
    polarity: str
    strength: str
    layer: str
    rule_refs: list
    evidence_refs: list
```

缺少 `domain` 字段，无法区分 Signal 属于哪个辨证域。

### 影响
- 无法进行 Domain-specific Judgment Synthesis
- 五大领域的 Signal 混在一起，无法归类

### 裁决建议
**P1**: 需要在 Signal 类中添加 domain 字段

---

## Gap 7: 无 Domain Judgment 实现

### 问题描述
搜索 `DomainJudgment`、`domain_judgment`、`Judgment.*Synthesis` 无结果。

### 影响
- Signal 直接输出，没有经过 Domain Judgment 层
- 五大领域（旺衰/格局/用神/十神语义/事件判断）无法独立产出 Judgment
- Synthesis 机制不存在

### 裁决建议
**P0 BLOCK**: 必须建立 Domain Judgment 层和 Synthesis 机制

---

## 额外发现

### 其他重复排盘入口
发现以下文件也有 `bazi_engine.compute()` 调用：
- `src/tongshu/api/app.py:398` — API 层直接调用（可能合法）
- `src/tongshu/engines/blind_bazi_engine.py:149,618` — 盲派引擎（可能合法）
- `src/tongshu/engines/ziwei_engine.py:768,774` — 紫微引擎依赖 BAZI（可能合法）
- `src/tongshu/judgment_architecture/judgment_index_foundation.py:324` —  judgment 架构（需审查）

### 测试失败
`test_rule_lifecycle.py` 全部 9 个测试失败，原因：
```
FileNotFoundError: rule.schema.json 不存在
```

---

## 建议修复优先级

### P0 紧急修复（冻结前必须完成）
1. **修复 Gap 1**: 删除 ContextAssembler 中的 `bazi_engine.compute()` 调用
2. **修复 Gap 7**: 建立 Domain Judgment 层和 Synthesis 机制
3. **修复硬编码路径**: 生产代码中的绝对路径改为相对路径

### P1 重要修复（建议尽快完成）
1. **修复 Gap 3**: 集成或移除 Phase B-1 的 Registry 代码
2. **修复 Gap 6**: 在 Signal 类中添加 domain 字段
3. **BOT-MASTER 裁决**: Gap 4 和 Gap 5 的 sum()/ratio 用法是否违规

### P2 建议修复（可选）
1. 补充 Schema 文件（rule.schema.json, evidence.schema.json）
2. 完善测试覆盖率

---

## 结论

### 当前状态评估

| 维度 | 评分 | 说明 |
|------|------|------|
| BAZI Frozen State 保护 | 4/10 | ContextAssembler 有违规风险，但生产路径正常 |
| 索引路径独立性 | 5/10 | 生产代码基本正常，脚本有大量硬编码 |
| Evidence → Rule 链路 | 6/10 | 引用完整但 Registry 未集成 |
| Rule 执行 | 8/10 | RuleMatcher 工作正常 |
| Rule → Judgment | 3/10 | Signal 产出但缺少 Domain Judgment |
| Judgment Synthesis | 2/10 | 完全缺失 |
| 端到端运行 | 5/10 | 部分测试失败（Schema 缺失） |

### 冻结建议

**❌ 禁止冻结 ZIPING**

#### 必须修复的问题（冻结前）

1. **删除 ContextAssembler 中的 bazi_engine.compute() 调用**
   - 文件: `src/tongshu/reasoning/context_assembler.py`
   - 行号: 532
   - 修复方案: 改为消费传入的 chart 参数

2. **建立 Domain Judgment 层**
   - 需要在 SignalEngine 之上增加 Judgment 层
   - 五大领域各自独立产出 Judgment
   - 建立 Synthesis 机制汇总各域 Judgment

3. **修复硬编码路径**
   - 生产代码中的绝对路径改为相对路径
   - 确保项目移动后仍能正常运行

#### 需要 BOT-MASTER 裁决的问题

1. **RuleMatcher.sum() 和 SignalEngine.ratio 是否违规？**
   - 结构性计数 vs 命理裁决聚合
   - 需要明确定义边界

2. **Phase B-1 Registry 是否集成？**
   - 集成则需修复调用链
   - 不集成则需清理代码

---

## 下一步

1. 等待 BOT-MASTER 裁决 Gap 4 和 Gap 5 的违规判定
2. 根据裁决开始修复 P0 问题
3. 修复完成后重新审计
4. 申请 ZIPING 冻结

---

**执行者**: @bot-ziping  
**状态**: 等待裁决  
**报告文件**: `docs/bots/BOT-ZIPING/PHASE4_P0_DEEP_DIVE_REPORT.md`
