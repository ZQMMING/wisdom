# P0-8.10 M3 工作计划（修订版）

**Commit**: 3fa3f61（有条件PASS）  
**修订日期**: 2026-08-31

---

## 核心原则变更

### 原计划（错误）
```
目标：新增COMPLETE ≥ 8条
压力：必须凑够数量
风险：可能降低质量标准
```

### 新计划（正确）
```
核心原则：质量 > 数量
目标：证明流程可复制
门槛：≥1条COMPLETE即可证明
数量：观察指标，非硬KPI
过滤：证据不足直接REJECT
```

### 关键边界
```
✅ 正确流程：
Evidence → Primitive → Condition → Local Judgment → 执行验证

❌ 禁止跳步：
Evidence → 直接认定为最终断言资产
```

---

## M3执行原则（永久冻结）

### 原则1: 质量优先
- 不追求数量
- 证据不足直接REJECT
- 宁可0条入库，不拿低质量充数

### 原则2: 完整验证链
每条Assertion必须经过：
1. 原典Evidence定位
2. Primitive提取
3. Condition推导
4. **真实Canonical State执行验证** ← 关键新增
5. Local Judgment生成

### 原则3: SEMANTIC_ONLY过滤
理论原则、评价性命题直接REJECT，不进入生产。

### 原则4: 渐进扩展
- 先验证1-2条完整链路
- 证明可复制后再扩展
- 不一次性生产大量候选

---

## Phase 1: 生产标准化（立即执行）

### Step 1: 建立SOP文档
```
文件：docs/P0_8_10_M3_PRODUCTION_SOP.md
内容：
1. Assertion生产完整流程（六步）
2. Evidence提取规范
3. Primitive/Condition推导规则
4. 真实执行验证方法
5. REJECT判定标准
6. 质量控制checklist
```

### Step 2: 建立模板
```
文件：templates/assertion_production_template.md
字段：
- Passage ID
- 书名/章节/行号
- Evidence Span（原文）
- 最小命题
- Semantic Relation类型
- Condition
- Primitive
- 执行验证结果
- 四问裁决
- 最终裁决（COMPLETE/REJECT）
```

### Step 3: 建立checklist
```
文件：checklists/consistency_checklist.md
检查项：
□ Evidence来自原典原文（非表格/非现代解释）
□ 证据源正确（书名/章节/行号匹配）
□ 主体一致（十神名称无替换）
□ 条件一致（无遗漏/无添加）
□ 结论一致（格局名称无替换）
□ 最小命题不可再分
□ 语义关系明确（成格/败格/理论原则）
□ Condition不超出Evidence范围
□ Primitive忠实于Condition
□ 执行验证通过
□ 四问裁决全部通过
```

---

## Phase 2: 小样本验证（第2-3天）

### 目标
**不追求数量，只证明流程可复制**

### 执行
1. 从QTBJ提取2-3条调候条件
2. 对每条执行完整六步验证
3. 记录验证结果
4. 如果全部COMPLETE，证明流程可复制
5. 如果有REJECT，分析原因并修正流程

### 成功标准
```
✅ 流程可复制：能独立生产1条COMPLETE
❌ 不追求：一次生产10条COMPLETE
```

---

## Phase 3: 渐进扩展（第4-7天）

### 条件
只有在Phase 2证明流程可复制后，才进入扩展。

### 扩展策略
```
第1批：QTBJ调候条件（5-8条候选）
第2批：SMTH格局条件（5-8条候选）
第3批：DTS中和论断（2-3条候选，预计多为SEMANTIC_ONLY）
```

### 每批验证标准
- 每条独立验证
- 证据不足直接REJECT
- 理论原则直接REJECT
- 不为了数量降低标准

### 预期结果
```
总候选：15-20条
预期COMPLETE：5-8条（观察指标）
预期REJECT：10-15条（正常过滤）
```

---

## M3 Success Criterion（修订版）

### 核心标准
```
A. 生产流程完全标准化
   - SOP文档完整 ✅
   - 模板可用 ✅
   - checklist可执行 ✅

B. 质量指标达标
   - semantic_overreach_rate = 0% ✅
   - unsupported_condition_rate = 0% ✅
   - consistency_check_rate = 100% ✅
   - source_traceability_rate = 100% ✅
   - execution_verification_rate = 100% ✅

C. 流程可复制证明
   - 能独立生产至少1条新COMPLETE ✅
   - 生产时间可预测（单条<30分钟）✅
   - 错误率可接受（<10%）✅

D. 渐进扩展验证
   - 第1批验证完成 ✅
   - 第2批验证完成 ✅
   - 第3批验证完成（如执行）✅
```

### 数量标准（降级为观察指标）
```
目标：新增5-10条候选
预期：2-5条COMPLETE
可接受：1条COMPLETE（只要质量达标）
```

---

## 风险控制

### 风险1: 新候选证据不足
- **缓解**: 提前标注"需语境确认"
- **预期**: 20%候选因证据不足REJECT

### 风险2: 理论原则过多
- **缓解**: Step 2快速过滤
- **预期**: DTS中50%+候选为理论原则

### 风险3: 执行验证复杂
- **缓解**: 先验证Simple Case，再处理Complex Case
- **预期**: 执行验证失败率<10%

---

## 交付物

1. `docs/P0_8_10_M3_PRODUCTION_SOP.md` - 生产标准化SOP
2. `templates/assertion_production_template.md` - Assertion生产模板
3. `checklists/consistency_checklist.md` - 一致性检查清单
4. `docs/P0_8_10_M3_QUALITY_REPORT.md` - M3质量报告
5. 新增资产库：≥1条COMPLETE（证明可复制）

---

## 立即行动

### Step 1: 创建SOP文档
开始编写Phase 1的SOP文档

### Step 2: 建立模板和checklist
创建标准化的生产工具

### Step 3: 验证第一条QTBJ候选
执行完整六步验证，证明流程可复制

---

**状态**: M3计划已修订，立即启动Phase 1
