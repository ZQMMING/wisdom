# P0-8.10 M3 工作计划 - 生产标准化与扩展

**Commit**: （待确认）  
**阶段**: M3 - 生产标准化与扩展  
**日期**: 2026-08-31

---

## M2总结

### 验证结果
- 总裁决: 16条
- COMPLETE: 15条（93.75%）
- REJECT: 1条（6.25%）- PZZQ-GEJU-004-A（主体错位）

### 已建立
- Atomic Definition冻结
- 七步验证流程固化
- 一致性审计机制
- 15条COMPLETE资产入库

---

## M3目标

### 核心目标
**建立可复制、可持续的生产能力**

### 具体目标

#### 1. 生产标准化（P0-8.10-M3-PROD）
- [ ] 建立Assertion生产SOP（标准作业程序）
- [ ] 定义完整的七步验证 checklist
- [ ] 创建模板化的Evidence Span格式
- [ ] 建立主体核对检查点（十神名称、格局名称）
- [ ] 制定REJECT标准操作流程

#### 2. 资产扩展（P0-8.10-M3-EXPAND）
- [ ] 从QTBJ（穷通宝鉴）提取调候条件
- [ ] 从SMTH（三命通会）提取格局条件
- [ ] 从DTS（滴天髓）提取中和论断
- [ ] 目标：新增20-30条候选命题
- [ ] 目标：至少8条COMPLETE

#### 3. 质量指标监控（P0-8.10-M3-QA）
- [ ] semantic_overreach_rate = 0%
- [ ] unsupported_condition_rate = 0%
- [ ] multi_conclusion_rate = 0%
- [ ] source_traceability_rate = 100%
- [ ] consistency_check_rate = 100%

---

## M3执行计划

### Phase 1: 生产标准化（第1-2天）

#### Step 1: 建立SOP文档
```
文件：docs/P0_8_10_M3_PRODUCTION_SOP.md

内容：
1. Assertion生产流程
2. 七步验证详细步骤
3. Evidence Span提取规范
4. 主体核对检查点
5. REJECT判定标准
6. 质量控制checklist
```

#### Step 2: 建立模板
```
文件：templates/assertion_production_template.md

模板字段：
- Passage ID
- 书名/章节/行号
- Evidence Span（原文）
- 最小命题
- Semantic Relation类型
- Condition
- Primitive
- 四问裁决结果
- 最终裁决（COMPLETE/REJECT）
```

#### Step 3: 建立checklist
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
□ 四问裁决全部通过
```

---

### Phase 2: 资产扩展（第3-5天）

#### Step 1: 从QTBJ提取调候条件

**来源**: 《穷通宝鉴》调候篇目

**目标候选**:
1. 甲木生于正月，丙火为先，戊土次之
2. 甲木生于二月，庚金为首，丙火次之
3. ...（需逐条定位原典）

**验证标准**:
- 必须是调候条件命题
- 必须明确条件-结论关系
- 必须是原典原文

**预估数量**: 10-15条候选
**目标COMPLETE**: 5-8条

---

#### Step 2: 从SMTH提取格局条件

**来源**: 《三命通会》格局篇目

**目标候选**:
1. 六阳趋艮格
2. 六阴趋乾格
3. ...（需逐条定位原典）

**验证标准**:
- 必须是成格/败格条件
- 必须明确条件组合
- 必须是原典原文

**预估数量**: 10-15条候选
**目标COMPLETE**: 5-8条

---

#### Step 3: 从DTS提取中和论断

**来源**: 《滴天髓》中和章

**目标候选**:
1. 中和为贵，偏枯为贱
2. ...（需判断是否属于理论原则）

**验证标准**:
- 必须是成格/败格条件
- 如果是理论原则，直接REJECT（SEMANTIC_ONLY）

**预估数量**: 5-10条候选
**目标COMPLETE**: 2-3条（预计多为理论原则）

---

### Phase 3: 质量控制（第6-7天）

#### Step 1: 执行一致性审计
- 对所有新COMPLETE进行主体核对
- 记录审计结果
- 修正发现的问题

#### Step 2: 建立质量报告
```
文件：docs/P0_8_10_M3_QUALITY_REPORT.md

内容：
- 新增资产统计
- 质量指标达成情况
- 发现的问题及修正
- 生产流程改进建议
```

#### Step 3: 流程迭代
- 根据审计结果优化SOP
- 更新模板和checklist
- 记录最佳实践

---

## M3 Success Criterion

### 核心标准
```
A. 生产流程完全标准化
   - SOP文档完整
   - 模板可用
   - checklist可执行

B. 质量指标达标
   - semantic_overreach_rate = 0%
   - unsupported_condition_rate = 0%
   - consistency_check_rate = 100%
   - source_traceability_rate = 100%

C. 资产扩展有效
   - 新增COMPLETE ≥ 8条
   - 新增REJECT ≥ 5条（过滤掉不合格候选）
   - 总COMPLETE ≥ 20条

D. 流程可复制
   - 独立生产3条新COMPLETE无需外部干预
   - 生产时间可预测（单条<30分钟）
   - 错误率可接受（<10%）
```

### 数量标准（观察指标，非门槛）
```
目标：新增15-20条候选
预期：8-10条COMPLETE
可接受：5条COMPLETE（只要质量达标）
```

---

## 风险与缓解

### 风险1: 新候选过多理论原则
- **影响**: COMPLETE率低
- **缓解**: 建立快速过滤机制（Step 2语义类型判定）
- **预期**: 20%候选通过理论原则过滤

### 风险2: 原典证据不明确
- **影响**: REJECT率高
- **缓解**: 提前标注"需语境确认"候选
- **预期**: 15%候选因证据不足REJECT

### 风险3: 生产速度不达标
- **影响**: 无法按时交付
- **缓解**: 标准化SOP后提速
- **预期**: 单条Production时间逐步降低

---

## 交付物

1. `docs/P0_8_10_M3_PRODUCTION_SOP.md` - 生产标准化SOP
2. `templates/assertion_production_template.md` - Assertion生产模板
3. `checklists/consistency_checklist.md` - 一致性检查清单
4. `docs/P0_8_10_M3_QUALITY_REPORT.md` - M3质量报告
5. 新增资产库：≥8条COMPLETE

---

## 下一步

### 立即行动
1. 创建M3生产SOP文档
2. 建立Assertion生产模板
3. 制定一致性检查清单

### 等待裁决
- 是否批准M3计划？
- 是否有优先级调整？
- 是否需要先完成其他任务？

---

**状态**: M3计划已制定，等待GPT裁决后开始执行
