# T2 裁决：strength_engine 审计与隔离

**裁决者**: Hermes  
**裁决日期**: 2026-08-30  
**User 授权**: T1 → T2 → T3 顺序执行

---

## 一、审计目标

确认 strength_engine 所有生产调用链，决定隔离策略。

---

## 二、生产调用链清单

| 调用文件 | 行号 | 使用方式 | 风险等级 |
|---------|------|---------|---------|
| `src/tongshu/engines/annual_event_evaluator.py` | 207-209 | `evaluate_strength(chart)` → `verdict` | **高** — 直接参与运势评分 |
| `src/tongshu/engines/judgment_engine.py` | 41, 371 | 类型 `D1StrengthResult`，传入 `judgment()` | **中** — 类型约束 |
| `src/tongshu/reasoning/health_signals.py` | 19, 99 | `evaluate_strength(chart)` → `d1` | **高** — 健康信号判断 |
| `src/tongshu/reasoning/event_topic.py` | 442-445 | `evaluate_strength(chart)` → `d1` | **中** — 事件主题分析 |
| `src/tongshu/legacy/assertion_v1/environmental_fit.py` | 39, 293 | `evaluate_strength(chart)` → 方位适配 | **低** — 已在 legacy 层 |

---

## 三、wang_score 使用情况

### 3.1 定义（第75行）
```python
_WANG_SCORE_THRESHOLD = 2.0
```

### 3.2 计算（第352-353行）
```python
# wang_score = de_ling_weight×1.5 + de_di_weighted×1.0 + de_shi_effective×0.8 + (support-drain)×0.3
wang_score = (
    de_ling_weight * 1.5
    + de_di_weighted * 1.0
    + de_shi_effective * 0.8
    + (support - drain) * 0.3
)
```

### 3.3 阈值判断（第396行）
```python
strong = wang_score >= _WANG_SCORE_THRESHOLD
```

### 3.4 从格条件（第367-393行）
- 从强：`wang_score > 4.0` + 其他条件
- 从弱：`wang_score < 1.5` + 其他条件

---

## 四、隔离策略

### 方案 A：标记 Deprecated + 保留调用（推荐）
- 在 strength_engine.py 添加 `@deprecated` 装饰器
- 所有生产调用继续工作，但输出 WARNING
- 不破坏现有测试流
- 未来逐步迁移到 CanonicalState

### 方案 B：完全隔离
- 将 wang_score 阈值判断移除
- 改用布尔 verdict（身强/身弱）
- 高风险：可能破坏已有命例计算

**裁决：采用方案 A**

---

## 五、实施步骤

1. 添加 `warnings.warn` 标记 deprecated
2. 创建 `CanonicalStrengthEngine` 占位（待 V1.4 迁移）
3. 更新调用方注释，注明迁移方向
4. 保持向后兼容，不破坏现有测试

---

## 六、影响范围

- **不破坏**：现有 1683 passed 测试
- **新增**：运行时 Warning 日志
- **未来**：V1.4 迁移时替换为 CanonicalState

---

**裁决状态**: 🟡 PENDING — 等待 User 确认方案
