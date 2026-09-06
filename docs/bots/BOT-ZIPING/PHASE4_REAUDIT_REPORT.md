# ZIPING 子平系统全面重新审计报告（Phase 4）

**任务 ID**: T-ENGINE-BAZI-002 Phase 4
**执行者**: @bot-ziping
**日期**: 2026-09-07
**依据**: BOT-MASTER 基线文档（十七节架构原则）

---

## 一、审计范围与目标

根据 BOT-MASTER 基线文档，本次审计聚焦七个核心问题：

| 编号 | 检查项 | 严重级别 | 状态 |
|------|--------|----------|------|
| P0-1 | 是否真正消费 BAZI Frozen Canonical State | P0 | ❌ FAIL |
| P0-2 | 资料索引是否可靠 | P0 | ⚠️ PARTIAL |
| P0-3 | Evidence 是否真正进入 Rule | P1 | ✅ PASS |
| P0-4 | Rule 是否真正执行 | P0 | ✅ PASS |
| P0-5 | Rule 是否真正产生 Judgment | P0 | ✅ PASS |
| P0-6 | Judgment 是否真正 Synthesis | P0 | ❌ FAIL |
| P0-7 | 整个 ZIPING 是否真正能跑通 | P0 | ❌ FAIL |

**总体结论**: 🔴 **ZIPING 不具备冻结条件**

---

## 二、详细审计结果

### P0-1: 是否真正消费 BAZI Frozen Canonical State

**状态**: ❌ FAIL
**严重级别**: P0

#### 发现的问题

ContextAssembler 在第532行调用了 `self.bazi_engine.compute()` 进行重新排盘：

```python
# src/tongshu/reasoning/context_assembler.py:532
chart = self.bazi_engine.compute((birth_year, birth_month, birth_day, birth_hour), gender)
```

**架构违规分析**：

根据 BOT-MASTER 基线文档第1节和第10节：

> BAZI负责"事实"，ZIPING负责"命理判断"
> ZIPING消费的是 Canonical Chart，不是重新计算的结果

**但好消息**：

ContextAssembler 仅在 `__main__` 块中调用（第570-581行），生产管道（`ComputeStage`）已经通过 `BaziAdapter` 正确消费 BaziChart：

```python
# src/tongshu/pipeline_stages/compute_stage.py:132
bazi_chart = self.bazi_engine.compute(bazi_birth, gender=effective_gender)
```

**判定**：代码存在架构违规，但未进入生产路径。属于 **P1 级别风险**，需要删除或重构 ContextAssembler。

#### 修复建议

```python
# 方案1: 删除 ContextAssembler 中的重新排盘逻辑
# 方案2: 将 ContextAssembler 改造为仅消费已计算的 chart
# 方案3: 移除 ContextAssembler，由 ComputeStage 统一处理
```

---

### P0-2: 资料索引是否可靠

**状态**: ⚠️ PARTIAL
**严重级别**: P0

#### 发现的问题

1. **规则文件结构不完整**

   示例规则 ZPZ-101 引用了证据 `E-ZPZ-101-001`，但证据文件路径不确定：
   ```json
   {
     "evidence_refs": ["E-ZPZ-101-001"]
   }
   ```

2. **Schema 文件缺失**

   `test_rule_lifecycle.py` 尝试加载 `rule.schema.json` 失败：
   ```
   FileNotFoundError: [Errno 2] No such file or directory: 'D:\\docs\\rule.schema.json'
   ```

3. **证据目录路径不一致**

   - 规则文件位于：`backend/data/rules/`
   - 证据文件可能位于：`data/evidence/` 或 `backend/data/evidence/`

#### 数据统计

- 总规则数: 136
- 有证据引用的规则: 136 (100%)
- 证据引用断裂数: 待验证

#### 修复建议

1. 建立证据文件索引验证机制
2. 统一证据目录路径
3. 补充缺失的 schema 文件

---

### P0-3: Evidence 是否真正进入 Rule

**状态**: ✅ PASS
**严重级别**: INFO

#### 验证结果

- 所有136条规则都包含 `evidence_refs` 字段
- RuleLoader 实现了 `_load_evidence()` 方法
- SignalEngine 使用 `evidence_refs` 字段记录信号来源

#### 统计数据

| 指标 | 数值 |
|------|------|
| 总规则数 | 136 |
| 有证据引用 | 136 (100%) |
| 无证据引用 | 0 (0%) |

---

### P0-4: Rule 是否真正执行

**状态**: ✅ PASS
**严重级别**: INFO

#### 验证结果

1. **RuleMatcher 实现完整**
   - `match_all()` 方法可匹配规则
   - `evaluate_conditions()` 可评估条件DSL
   - `resolve_conflicts()` 可解决冲突

2. **SignalEngine 正确调用 RuleMatcher**
   ```python
   # src/tongshu/reasoning/signal_engine.py:247
   matched = matcher.match_all(ctx, layer=layer)
   ```

3. **Rule 执行链路完整**
   - RuleLoader → RuleMatcher → SignalEngine → Signal

#### 测试结果

```
tests/test_rule_engine.py: 12 passed
tests/test_phase3_p0.py: 3 passed
```

---

### P0-5: Rule 是否真正产生 Judgment

**状态**: ✅ PASS
**严重级别**: INFO

#### 验证结果

1. **Signal 类包含必要字段**
   - `signal_id`: 唯一标识
   - `ontology_type`: USO 类型
   - `direction`: 方向（VOLATILE/SUPPORT/等）
   - `polarity`: 极性（caution/benefit/等）
   - `strength`: 强度
   - `layer`: 层级
   - `rule_refs`: 规则引用
   - `evidence_refs`: 证据引用

2. **SignalEngine 产出 Signal**
   ```python
   # src/tongshu/reasoning/signal_engine.py:232
   return Signal(
       signal_id=f"SIG-{layer[:2].upper()}-{extra_id}{index:03d}",
       ontology_type=rule["produces_signal_type"],
       direction=template["direction"],
       polarity=template["polarity"],
       ...
   )
   ```

3. **可追溯性**
   - 每个 Signal 包含 `rule_refs` 和 `evidence_refs`
   - 可追溯到具体规则和证据

---

### P0-6: Judgment 是否真正 Synthesis

**状态**: ❌ FAIL
**严重级别**: P0

#### 发现的问题

**核心问题：五大辨证域不完整**

规则领域分布统计：

| 领域 | 规则数 | 状态 |
|------|--------|------|
| 旺衰判定 (wangshuai) | 14 | ✅ 存在 |
| 格局判定 (pattern) | 20 | ✅ 存在 |
| 用神判定 (yongshen) | **0** | ❌ **缺失** |
| 十神语义 (ten_god) | 21 | ✅ 存在 |
| 事件判断 (event) | 21 | ✅ 存在 |

**严重缺失：用神域（yongshen）完全没有规则！**

根据 BOT-MASTER 基线文档第7节：

> 用神是 ZIPING 最容易被简化错误的地方
> 旺衰是证据之一，不是整个用神算法
> 《穷通宝鉴》的月令、节候、寒暖燥湿逻辑不能简单压成"强弱算法"

当前状态：
- 旺衰域有规则（14条）
- 格局域有规则（20条）
- 但用神域完全没有独立规则

#### 影响分析

1. **诊断无法完成**
   - 没有用神规则，无法判断命局的核心需求
   - 无法给出"扶抑/调候/通关"等关键建议

2. **架构不完整**
   - 五大辨证域缺一，不符合子平命理核心框架

3. **Golden Test 无法覆盖**
   - 用神判断是命局分析的核心，缺失导致无法进行端到端测试

#### 修复建议

需要补充用神域规则，至少包括：

```json
{
  "rule_id": "YG-001",
  "title": "身旺取克泄耗",
  "domain": "yongshen",
  "source": {"work": "子平真诠", "chapter": "论用神"},
  "conditions": {
    "all": [
      {"field": "day_master_strength", "op": "eq", "value": "STRONG"},
      {"field": "month_branch", "op": "nin", "value": ["申", "酉", "戌"]}
    ]
  },
  "conclusion": {
    "produces_layer_output_template": {
      "direction": "CONTROL",
      "polarity": "benefit"
    }
  },
  "evidence_refs": ["E-YG-001-001"],
  "status": "active"
}
```

---

### P0-7: 整个 ZIPING 是否真正能跑通

**状态**: ❌ FAIL
**严重级别**: P0

#### 发现的问题

1. **测试失败：Schema 文件缺失**

   `test_rule_lifecycle.py` 全部9个测试失败：
   ```
   FileNotFoundError: [Errno 2] No such file or directory: 'D:\\docs\\rule.schema.json'
   ```

2. **RuleLoader 依赖缺失的 Schema**

   ```python
   # src/tongshu/reasoning/rule_loader.py:37
   self._rule_schema = self._load_schema(schema_dir / "rule.schema.json")
   ```

3. **端到端链路断裂**

   虽然核心组件存在，但缺少必要的配置文件，导致无法完整运行。

#### 修复建议

1. 补充缺失的 schema 文件：
   - `docs/rule.schema.json`
   - `docs/evidence.schema.json`

2. 建立配置完整性检查机制

3. 确保所有测试能在隔离环境中运行

---

## 三、规则统计与分布

### 3.1 规则总数

- 总规则数: 136
- 状态分布:
  - active: 75 (55.1%)
  - draft: 51 (37.5%)
  - validated: 10 (7.4%)

### 3.2 领域分布

| 规则类型 | 数量 | 说明 |
|----------|------|------|
| 流年触发 | 21 | EVENT_TOPIC 层 |
| 旺衰判定 | 14 | BASELINE 层 |
| 十神定性 | 21 | BASELINE 层 |
| 格局判定 | 20 | BASELINE 层 |
| 健康断事 | 25 | EVENT_TOPIC 层 |
| 体用辨析 | 10 | 盲派理论 |
| 婚姻断事 | 8 | EVENT_TOPIC 层 |
| 流日激活 | 5 | DAILY_ACTIVATION 层 |
| 神煞判定 | 4 | BASELINE 层 |
| 大运起止 | 1 | CYCLE_CONTEXT 层 |
| 月令司权 | 7 | BASELINE 层 |

### 3.3 经典来源分布

| 经典 | 规则数 | 占比 |
|------|--------|------|
| 子平真诠 | ~60 | 44% |
| 滴天髓 | ~30 | 22% |
| 渊海子平 | ~25 | 18% |
| 穷通宝鉴 | ~15 | 11% |
| 三命通会 | ~6 | 4% |

---

## 四、关键发现总结

### 4.1 已实现的组件 ✅

1. **RuleMatcher** - 完整实现，可执行规则匹配
2. **SignalEngine** - 完整实现，可产出 Signal
3. **RuleLoader** - 实现，但依赖缺失的 schema
4. **EvidenceLoader** - 实现（phase_b1_evidence_connection.py）
5. **ContextAssembler** - 实现，但有架构违规风险

### 4.2 缺失的组件 ❌

1. **用神域规则** - 完全缺失，无法进行核心诊断
2. **Schema 文件** - rule.schema.json 和 evidence.schema.json 缺失
3. **证据索引验证** - 证据引用路径不完整
4. **Synthesis 机制** - 五大领域未连接，各自独立

### 4.3 架构风险 ⚠️

1. **ContextAssembler 重复排盘风险** - 虽然未进入生产路径，但代码存在架构违规
2. **Rule Lifecycle 未强制执行** - Phase B-2.1 的 RemediationEngine 存在但未集成
3. **Authorization Gate 未集成** - 规则无法区分 DRAFT/ACTIVE/PRODUCED

---

## 五、建议修复优先级

### P0 紧急修复（冻结前必须完成）

1. **补充用神域规则**
   - 至少添加 4-7 条核心用神规则
   - 覆盖：格局用神、扶抑用神、调候用神

2. **补充缺失的 Schema 文件**
   - `docs/rule.schema.json`
   - `docs/evidence.schema.json`

3. **修复 ContextAssembler 架构违规**
   - 删除 `bazi_engine.compute()` 调用
   - 改为仅消费已计算的 chart

### P1 重要修复（建议尽快完成）

1. **建立证据索引验证机制**
   - 验证所有 evidence_refs 指向真实文件
   - 建立证据路径规范

2. **集成 Phase B-2.1 的 RemediationEngine**
   - 确保 Rule Lifecycle 状态机生效
   - 强制执行 Authorization Gate

3. **建立五大领域的 Synthesis 机制**
   - CrossDomainOrchestrator 完善
   - Judgment Synthesis 实现

### P2 建议修复（可选）

1. **优化 RuleLoader 路径处理**
2. **完善测试覆盖率**
3. **建立 Evidence-Provenance 追踪**

---

## 六、结论

### 当前状态评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 基础设施 | 7/10 | 核心组件存在，但配置缺失 |
| 规则覆盖 | 5/10 | 五大域缺用神，规则不完整 |
| 证据链接 | 6/10 | 所有规则有引用，但验证不完整 |
| 执行链路 | 8/10 | RuleMatcher + SignalEngine 正常工作 |
| 架构合规 | 4/10 | ContextAssembler 有架构违规 |

### 冻结建议

**❌ 不建议冻结 ZIPING**

原因：
1. 核心辨证域（用神）完全缺失
2. Schema 文件缺失导致测试无法运行
3. ContextAssembler 存在架构违规风险
4. 五大领域未连接，无法进行 Synthesis

### 下一步行动

1. **立即**：补充用神域规则（4-7条）
2. **立即**：补充 schema 文件
3. **本周**：修复 ContextAssembler
4. **下周**：建立 Synthesis 机制
5. **两周后**：重新审计并申请冻结

---

## 七、附录

### A. 审计脚本

- `scripts/phase4_reaudit.py` - Phase 4 审计脚本
- `docs/bots/BOT-ZIPING/PHASE4_REAUDIT_REPORT.md` - 本报告

### B. 相关文件

- `src/tongshu/reasoning/context_assembler.py` - 存在架构违规
- `src/tongshu/reasoning/signal_engine.py` - 正常工作
- `src/tongshu/reasoning/matcher.py` - 正常工作
- `src/tongshu/reasoning/rule_loader.py` - 依赖缺失 schema
- `backend/data/rules/*.json` - 136条规则
- `src/tongshu/phase_b1_evidence_connection.py` - EvidenceLoader
- `src/tongshu/phase_b2_1_remediation.py` - RemediationEngine

### C. 测试状态

| 测试文件 | 状态 | 通过数 | 失败数 |
|----------|------|--------|--------|
| test_rule_engine.py | ✅ PASS | 12 | 0 |
| test_phase3_p0.py | ✅ PASS | 3 | 0 |
| test_rule_lifecycle.py | ❌ FAIL | 0 | 9 |
| test_bazi_engine.py | ✅ PASS | 12 | 0 |

---

**执行者**: @bot-ziping
**状态**: 🔴 NOT READY FOR FREEZE
**下一步**: 等待 BOT-MASTER 裁决后开始修复
