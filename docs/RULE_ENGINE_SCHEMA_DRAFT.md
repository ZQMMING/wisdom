# 五经辨证 Rule Engine Schema 设计草案

**版本**: v0.1 Draft  
**日期**: 2026-08-31  
**阶段**: P0-8.10 M3 Phase 2

---

## 设计目标

基于M2/M3的15条COMPLETE资产和统计分析，设计可扩展、可验证的五经辨证Rule Engine Schema。

---

## 核心组件

### 1. Primitive Registry（Primitive注册表）

#### 功能
- 存储所有经过验证的稳定Primitive
- 提供Primitive查询和匹配接口
- 维护Primitive的Evidence来源

#### 数据结构
```json
{
  "primitive_id": "PRIM_001",
  "primitive": "印格喜煞",
  "semantic_type": "成格条件",
  "evidence_count": 3,
  "supporting_assertions": ["PZZQ-GEJU-005-A", "PZZQ-GEJU-005-B", "PZZQ-GEJU-005-C"],
  "stability": "HIGH",
  "created_at": "2026-08-31",
  "source": "PZZQ"
}
```

#### 当前稳定Primitive（来自M2资产）
```
HIGH稳定性:
- 印格喜煞（3条支持）
- 印格喜官印（3条支持）
- 印格喜食伤泄气（3条支持）
- 岁君关系凶（4条支持）
- 建禄月劫格喜官（3条支持）
- 建禄月劫格喜财（3条支持）
- 建禄月劫格喜煞（3条支持）

MEDIUM稳定性:
- 食神格喜印绶（带旺衰条件）（1条支持）
```

---

### 2. Condition Mapper（Condition映射器）

#### 功能
- 标准化Condition表达
- 处理Condition的重复和合并
- 建立Condition到Primitive的映射

#### 标准化规则
```
【同义合并】
"日犯岁君" ≈ "犯岁君者"
→ 统一为"日犯岁君"

【复合分解】
"阳刃透官煞而露财印，不见伤官"
→ 分解为：
  - 阳刃透官煞（独立条件）
  - 露财印（独立条件）
  - 不见伤官（独立条件）
→ 但保持复合Assertion结构（不拆分Primitive）

【模糊处理】
"伤官旺" → 定义可计算标准
"印有根" → 定义根气标准
"身强" → 定义力量阈值
```

#### 当前Condition映射表
| 原始Expression | 标准化Condition | 对应Primitive | 可计算性 |
|----------------|-----------------|---------------|----------|
| 印轻逢煞 | 印星力量 < 煞星力量 | 印格喜煞 | ✅ 可计算 |
| 官印双全 | 官星透出 + 印星透出 | 印格喜官印 | ✅ 可计算 |
| 身印两旺而用食伤泄气 | 日主力量旺 + 印星力量旺 + 食伤透出 | 印格喜食伤泄气 | ⚠️ 需定义阈值 |
| 阳刃透官煞而露财印，不见伤官 | 阳刃在月令 + 官煞透出 + 财印透出 + 伤官不透 | 阳刃格喜官煞财印 | ✅ 可计算 |

---

### 3. Judgment Composite（复合Judgment处理器）

#### 功能
- 处理需要多个Primitive联合的Judgment
- 实现AND/OR逻辑组合
- 管理Judgment的优先级和冲突

#### 组合逻辑
```
【OR组合】
建禄月劫格成 = 
  (透官而逢财印) ∨ 
  (透财而逢食伤) ∨ 
  (透煞而遇制伏)

【AND组合】
岁君关系救应 = 
  日犯岁君 ∧ 五行有救 → 反必为财

【序列组合】
印格成 = 
  条件1（印轻逢煞）∨ 
  条件2（官印双全）∨ 
  条件3（身印两旺而用食伤泄气）
```

#### 当前Composite Judgment列表
```
【建禄月劫格】
- 复合结构: OR组合
- 路径数: 3
- Primitive依赖: 3个

【岁君关系】
- 复合结构: AND + 条件分支
- 基础Judgment: 日犯岁君 → 凶
- 分支Judgment: 日犯岁君 + 五行有救 → 财

【印格】
- 复合结构: OR组合（三条成格路径）
- 路径数: 3
- Primitive依赖: 3个
```

---

### 4. Semantic Type Filter（语义类型过滤器）

#### 功能
- 过滤SEMANTIC_ONLY内容
- 区分成格条件 vs 调候规则 vs 理论原则
- 防止不同类型内容混入资产库

#### 语义类型分类
```
【CLASSICAL_EXPLICIT】→ 可授权
- 成格条件（如：印轻逢煞 → 印格成）
- 败格条件（如：食神逢枭 → 食神格败）

【CLASSICAL_IMPLICIT】→ 研究用途
- 隐含的成格条件
- 需要进一步验证的命题

【SEMANTIC_ONLY】→ REJECT
- 理论原则（如：命贵中和，偏枯终于有损）
- 调候规则（如：甲木生于正月，丙火为先）
- 评价性命题（如：要以中和为贵）

【ENGINEERED_THRESHOLD】→ 研究用途
- 工程定义的阈值
- 需要独立验证的规则

【UNRESOLVED】→ HOLD
- 证据不足
- 语义不确定
```

#### M3验证结果（QTBJ调候规则）
```
候选: 甲木生于正月，丙火为先，戊土次之
类型: SEMANTIC_ONLY（调候规则）
裁决: REJECT
原因: 不属于成格/败格条件，不能授权为断言
```

---

## Schema应用场景

### 场景1: 新Assertion生产
```
输入: 原典Evidence
↓
Step 1: Semantic Type Filter判定类型
  - CLASSICAL_EXPLICIT → 继续生产
  - SEMANTIC_ONLY → REJECT
↓
Step 2: Condition Mapper标准化
  - 同义合并
  - 复合分解
  - 模糊处理
↓
Step 3: Primitive Registry查询
  - 已有稳定Primitive → 复用
  - 新Primitive → 创建并验证
↓
Step 4: Judgment Composite处理
  - 判断是否需要复合
  - 实现AND/OR逻辑
↓
Step 5: 输出最终Assertion
```

### 场景2: Canonical State执行验证
```
输入: BaziChart（Canonical State）
↓
Step 1: 提取十神分布
  - 官煞星位置
  - 印星位置
  - 食伤位置
  - 财星位置
↓
Step 2: 匹配Condition Mapper
  - 检查是否有匹配的Condition
↓
Step 3: 执行Primitive逻辑
  - 应用Primitive Registry中的规则
↓
Step 4: 生成Local Judgment
  - 单条Primitive → 单一Judgment
  - 多条Primitive → 触发Judgment Composite
↓
Step 5: 输出综合判断
```

### 场景3: 多Primitive冲突处理
```
输入: 多个Primitive产生冲突Judgment
↓
Step 1: 识别冲突
  - Primitive A → Judgment X
  - Primitive B → Judgment Y
  - X ≠ Y
↓
Step 2: 检查优先级
  - 原典明确优先级？
  - 经验法则优先级？
↓
Step 3: 应用Judgment Composite
  - OR组合 → 取满足路径
  - AND组合 → 需同时满足
  - 序列组合 → 按序执行
↓
Step 4: 输出最终Judgment
  - 记录冲突和解决方式
```

---

## 当前Schema覆盖度评估

### Primitive覆盖率
```
✅ 印格相关Primitive: 3条（稳定）
✅ 建禄月劫格相关Primitive: 3条（稳定）
✅ 岁君关系Primitive: 4条（稳定）
⚠️ 食神格Primitive: 1条（待扩展）
❌ 财格Primitive: 2条（待验证）
❌ 官格Primitive: 0条（未验证）
❌ 煞格Primitive: 0条（未验证）
❌ 阳刃格Primitive: 1条（待验证）
```

### Condition计算性评估
```
✅ 完全可计算: 8条Condition
⚠️ 需定义阈值: 4条Condition
❌ 不可计算: 3条Condition（理论原则/调候规则）
```

### Judgment复合度评估
```
✅ 单一Primitive Judgment: 10条
⚠️ 复合Judgment（OR）: 3条（印格、建禄月劫、岁君）
❌ 未验证复合Judgment: 2条（财格、官格）
```

---

## 后续开发路线图

### Phase 1: Schema基础（当前）
- [x] Primitive Registry设计
- [x] Condition Mapper设计
- [x] Judgment Composite设计
- [x] Semantic Type Filter设计
- [ ] 实现Schema核心类
- [ ] 实现验证流程

### Phase 2: 扩展验证（M3继续）
- [ ] 从SMTH提取格局条件（目标5-8条COMPLETE）
- [ ] 验证Rule Engine对现有15条资产的处理
- [ ] 优化Condition Mapper的标准化规则
- [ ] 完善Judgment Composite的冲突处理

### Phase 3: 生产标准化（M3后期）
- [ ] 批量生产新的COMPLETE Assertion
- [ ] 建立自动化验证流程
- [ ] 实现Schema的性能优化
- [ ] 编写用户文档

---

## 关键设计原则

### 原则1: Evidence Source Purity
- 所有Primitive/Condition必须追溯到原典Evidence
- 禁止无Evidence的Primitive
- 禁止跨体系投票决定真伪

### 原则2: Semantic Type Isolation
- SEMANTIC_ONLY内容必须REJECT
- 成格条件 ≠ 调候规则 ≠ 理论原则
- 不同类型内容不能混用

### 原则3: Condition Computability
- 尽量将Condition转化为可计算逻辑
- 无法计算的Condition必须标注"需人工裁决"
- 禁止把不可计算的条件伪装成确定性规则

### 原则4: Judgment Transparency
- 每个Judgment必须可追溯
- 复合Judgment必须明确组合逻辑
- 冲突Judgment必须记录处理方式

---

## 风险与缓解

### 风险1: Primitive冲突
- **影响**: 产生矛盾Judgment
- **缓解**: Judgment Composite处理冲突，记录决策过程
- **预期**: <5%的Assertion产生冲突

### 风险2: Condition不可计算
- **影响**: 无法自动化验证
- **缓解**: 标注为"需人工裁决"，进入HOLD队列
- **预期**: 20-30%的Condition需要人工裁决

### 风险3: 新来源证据不足
- **影响**: REJECT率高
- **缓解**: 严格SEMANTIC_TYPE Filter，证据不足直接REJECT
- **预期**: 50%+新候选因证据不足REJECT

---

**状态**: Schema设计草案v0.1，等待GPT裁决后开始实现
