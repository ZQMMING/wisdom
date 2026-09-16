# 盲派 Frontend Expression Contract V1

基线 commit: b9c428e6
封板日期: 2026-09-17
状态: 契约定义完成，待Frontend实现

---

## 数据契约：ModernExpressionResult

Frontend只能渲染以下字段，不得自行解释或重新判断：

| 字段 | 类型 | 用途 | 展示要求 |
|---|---|---|---|
| `judgment_id` | str | 唯一标识 | 内部用，不展示给用户 |
| `mapping_id` | str | Mapping标识 | 内部用，不展示给用户 |
| `classical_result` | str | 经典结果枚举 | 可选展示（折叠/详情页） |
| `classical_meaning` | str | 经典含义原文 | 可选展示（折叠/详情页） |
| `modern_semantic` | str | 现代语义 | **用户主显示文本** |
| `modern_domain` | str | 现代域分类 | 用于模块分类/分组 |
| `modern_expression` | str | 现代表达 | **用户主显示文本** |
| `semantic_boundary` | Tuple[str,...] | 语义边界 | **必须展示**（风险提示） |
| `avoid_phrases` | Tuple[str,...] | 禁语 | **不得作为正文展示** |
| `mapping_version` | str | Mapping版本 | 内部用，不展示给用户 |
| `provenance` | str | 溯源链 | 内部用，不展示给用户 |

---

## Frontend 7条铁律

### F-01 只渲染，不解释
Frontend只能把后端返回的ModernExpressionResult渲染成UI，不得：
- 重新解释modern_semantic
- 重新组合多条Judgment成新结论
- 自行生成吉凶判断
- 自行生成Event结论

### F-02 modern_expression是主显示文本
用户看到的主要文字必须是`modern_expression`字段，不得：
- 用classical_result直接当正文
- 用judgment_result枚举直接当正文
- 把avoid_phrases当正文展示

### F-03 semantic_boundary必须展示
每条Judgment的边界提示（如"信号不是事件坐实"）**必须**展示给用户，不得：
- 折叠后隐藏
- 用CSS隐藏
- 省略不显示

### F-04 avoid_phrases不得展示
禁语列表仅供前端内部做文本校验用，**不得**作为正文展示给用户。

### F-05 不得把结构渲染成确定事件
- "结构信号" → 不能渲染成"一定会..."
- "风险信号" → 不能渲染成"会得病/会坐牢"
- "倾向" → 不能渲染成"必然"
- "时间窗口" → 不能渲染成"X年一定会..."

### F-06 不得跨条重新组合
Frontend不得把多条Judgment的modern_semantic自行组合成新的综合结论，综合结论必须由后端提供。

### F-07 不得修改任何字段
Frontend不得：
- 修改modern_semantic
- 修改classical_meaning
- 修改semantic_boundary
- 增删字段

---

## 展示规范

### 单条Judgment展示模板

```
┌─────────────────────────────────┐
│ [modern_domain]                 │  ← 分类标签
│─────────────────────────────────│
│ modern_expression               │  ← 用户主文本
│                                 │
│ ⚠️ semantic_boundary[0]         │  ← 边界提示
│ ⚠️ semantic_boundary[1]         │
│                                 │
│ [展开经典语义]                  │  ← 折叠区
│   classical_meaning             │
└─────────────────────────────────┘
```

### 多Judgment分组展示
按`modern_domain`分组：
- 财富/方向
- 事业/平台
- 婚姻/感情
- 健康/身体
- 六亲/关系
- 子女/性别
- 时间窗口
- 限制/约束

---

## 禁止事项

1. ❌ Frontend重新解释Judgment
2. ❌ Frontend重新计算Rule/Assertion/Judgment
3. ❌ Frontend自行生成吉凶/Event结论
4. ❌ Frontend把risk/tendency/structure渲染成确定事件
5. ❌ Frontend把avoid_phrases当正文展示
6. ❌ Frontend隐藏semantic_boundary
7. ❌ Frontend跨条重新组合结论

---

## 解锁条件

M-09 Frontend Expression Contract签完后，还需：
1. Frontend Render Regression（前端实际渲染验证）
2. 渲染结果与后端数据一致性验证
3. 边界提示是否正确展示验证
4. 禁语是否未泄漏验证

全部PASS后才真正解锁Frontend Expression。
