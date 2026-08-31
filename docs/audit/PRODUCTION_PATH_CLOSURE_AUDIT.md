# Production Path Closure Audit

**审计日期**: 2026-08-31  
**审计者**: Claude (独立审计)  
**方法**: 三重取证（调用图 + 生产入口链 + 测试对象核对）  
**范围**: 全仓库所有可产生"命理结论"的路径

---

## 执行摘要

| 检查项 | 结果 | 严重度 |
|--------|------|--------|
| Strength Engine 生产回流 | ✅ 无证据 | — |
| infer_verdict() 生产调用 | ✅ 零调用方 | — |
| health_signals 生产调用 | ✅ 零调用方 | — |
| event_topic.EventTopicEngine 生产调用 | ✅ 零调用方 | — |
| judgment_engine 生产调用 | ✅ 零调用方 | — |
| annual_event_evaluator 生产调用 | ✅ 仅 legacy 引用 | — |
| Admin Router 生产可达性 | ⚠️ Feature Flag 保护中 | P1 |
| Legacy Assertion 生产接入 | ⚠️ Shim 存在但 Pipeline 未使用 | P2 |
| judgment_production.py Pipeline 接入 | 🔴 未接入主链路 | P1 |
| 唯一生产路径确认 | ✅ 已通过 | — |

**核心结论**: 主干 Golden Path 已收敛为唯一生产路径。但存在两处 **P1 架构债务**需处理：(1) `infer_verdict()` 死代码风险；(2) `judgment_production.py` 未接入主链路。

---

## 一、唯一生产路径验证

### 1.1 生产入口链（三重取证）

```
HTTP/API (app.py)
  └→ TONGSHUPipeline.run() (pipeline.py:154)
       └→ ComputeStage.run() (compute_stage.py:94)
            ├→ BaziEngine.compute() → BaziChart (L1 Facts)
            ├→ ZiweiEngine.compute() → ZiweiChart
            ├→ HuangliEngine.get_day()
            ├→ SignalEngine.build() → Semantic Signals
            ├→ CrossAnalyzer.analyze() → CrossResult
            ├→ RuleLoader + RuleMatcher → matched rules
            └→ CanonicalComposer.compose() → CanonicalContent (SIR)
       └→ RenderStage.run() → Rendered text
       └→ ValidationStage.run() → ValidationResult
```

**取证结论**: 以上路径为**唯一**进入生产结论的路径。所有其他模块均不通过此链触发。

### 1.2 RuleMatcher 与 JudgmentProduction 的关系

- `RuleMatcher` 加载 `data/rules/*.json` (136条规则)，直接匹配 `RuleContext`
- `judgment_production.JudgmentProducer` 是独立引擎，**未被 pipeline 导入或调用**
- 当前生产结论由 RuleMatcher 基于 JSON 规则产生，而非 JudgmentProducer

---

## 二、Legacy 模块调用图取证

### 2.1 evaluate_strength / infer_verdict 调用追踪

```python
# 调用方统计 (grep 全仓库):
src/tongshu/engines/annual_event_evaluator.py:37   ← DEPRECATED stub调用
src/tongshu/reasoning/health_signals.py:19          ← DEPRECATED stub调用
src/tongshu/reasoning/event_topic.py:443            ← DEPRECATED stub调用
src/tongshu/legacy/assertion_v1/engine_adapters.py:51← LEGACY目录
src/tongshu/legacy/assertion_v1/environmental_fit.py:45 ← LEGACY目录
src/tongshu/legacy/assertion_v1/systems.py:652      ← LEGACY目录

# 生产代码（非legacy）对 strength_engine 的 import:
src/tongshu/engines/judgment_engine.py:41           ← 仅 import D1StrengthResult (类型注解)
```

**结论**:
- `evaluate_strength()` 在生产代码中已退回 UNRESOLVED stub，所有调用方均感知为空 verdict
- `infer_verdict()` **零生产调用方**，为死代码

### 2.2 health_signals 调用追踪

```python
# 全仓库 import health_signals:
# (无任何生产代码导入)
```

**结论**: `health_signals.py` 完全孤立，不参与生产。

### 2.3 event_topic.EventTopicEngine 调用追踪

```python
# 全仓库 import EventTopicEngine:
# (无任何生产代码导入，仅 matcher.py 注释引用)
```

**结论**: `EventTopicEngine` 为未来规划代码，未接入生产。

### 2.4 judgment_engine 调用追踪

```python
# 全仓库 import judgment_engine:
# (零调用方)
```

**结论**: `judgment_engine.py` 完全孤立。

### 2.5 annual_event_evaluator 调用追踪

```python
# 全仓库 import annual_event_evaluator:
src/tongshu/legacy/assertion_v1/flow_year.py:32  ← LEGACY目录
```

**结论**: 仅被 legacy 代码引用。

---

## 三、Admin Router 可达性分析

### 3.1 当前状态 (B-03 Fix)

```python
# src/tongshu/api/app.py:586-593
# B-03 FIX: 添加 feature flag 保护 /admin 路由（默认关闭）
import os
if os.getenv("TONGSHU_ADMIN_ROUTER_ENABLED", "false").lower() in ("true", "1", "yes"):
    from ..admin import admin_router as _admin_router
    app.include_router(_admin_router)
```

**状态**: ✅ 默认关闭。需要显式设置环境变量才会激活。

### 3.2 Admin Router 内部链路

```
POST /admin/cases
  └→ compute_case_snapshot() (admin/service.py:56)
       └→ produce_all_evidence() (assertion/engine_adapters.py:558)
            └→ evaluate_strength() [LEGACY, returns UNRESOLVED stub]
```

**风险**: 当 `TONGSHU_ADMIN_ROUTER_ENABLED=true` 时，admin 端点可访问 legacy 路径。但 `evaluate_strength` 返回 UNRESOLVED，不会产生错误结论。

**建议**: 保留 feature flag 作为安全阀，但增加日志警告。

---

## 四、Legacy Shim 分析

### 4.1 assertion/__init__.py Shim 层

```python
# 重导出 legacy/assertion_v1/* 模块
# 目的: 向后兼容 API
```

**生产消费方**: 仅 `legacy/assertion_v1/` 内部互相引用。Pipeline 不使用此 shim。

**结论**: ✅ 无害 shim，不产生生产结论。

---

## 五、发现的技术债

### TD-002: `infer_verdict()` 死代码风险 【P1】

**位置**: `src/tongshu/engines/strength_engine.py:406-450`

**问题**: 该函数包含完整的旧式身强/身弱判定逻辑，虽未被调用，但新开发者可能误用。

```python
def infer_verdict(features: D1FeatureResult) -> str:
    """从 D1FeatureResult 推导 verdict（原典条件组合，不依赖 wang_score）。
    ...
    """
```

**建议 Action**:
1. 添加 `# noqa: S107` + `DEPRECATED_INFER_VERDICT_REMOVED` 大段声明
2. 或彻底删除此函数（保留在历史 commit 中可追溯）
3. 在 `strength_engine.py` 头部增加"禁止调用 infer_verdict"警告

### TD-003: `judgment_production.py` 未接入主链路 【P1】

**问题**: `JudgmentProducer` 已实现（4条 APPROVED Judgment），但 pipeline 使用 `RuleMatcher + data/rules/*.json` 而非 `JudgmentProducer`。

**影响**: 当前生产结论来自 JSON 规则匹配，不是来自 Judgment Authority 授权路径。两条路径并行但未统一。

**建议 Action**:
1. 评估是否将 `JudgmentProducer` 接入 pipeline
2. 或将 `data/rules/*.json` 明确标注为 Judgment Producer 的输出物
3. 建立统一视图：所有生产结论必须经过 `Authority Ledger`

### TD-004: Admin Router 安全加固 【P2】

**建议**: 即使 feature flag 关闭，admin router 的 include 仍应带审计日志。

---

## 六、最终结论

### 生产路径收敛度评分

| 层级 | 状态 | 评分 |
|------|------|------|
| Bazi/Canonical 计算层 | ✅ 唯一入口，无分流 | 🟢 |
| Semantic Signal 层 | ✅ SignalEngine 唯一入口 | 🟢 |
| Rule Matcher 层 | ✅ RuleLoader 唯一规则源 | 🟢 |
| Canonical Composer 层 | ✅ 唯一 SIR 组装点 | 🟢 |
| Render/Validation 层 | ✅ 唯一输出点 | 🟢 |
| Legacy Strength Engine | ✅ 零生产回流（stub） | 🟢 |
| Legacy Assertion v1 | ✅ 仅 shim + legacy 内部引用 | 🟢 |
| Judgment Production | ⚠️ 未接入主链路 | 🟡 |
| Admin Router | ⚠️ Feature Flag 保护 | 🟡 |
| `infer_verdict()` | 🔴 死代码存在风险 | 🟡 |

### 总体判断

**Golden Path 已收敛为唯一生产路径**。旧系统残留代码虽然存在，但通过以下机制确保不产生生产结论：
1. `evaluate_strength()` 已退回 UNRESOLVED stub
2. `infer_verdict()` 零调用方
3. Legacy 模块仅被 legacy 自身引用
4. Admin router 有 feature flag 保护

**下一步优先级**:
1. [P1] TD-002: 清理 `infer_verdict()` 死代码
2. [P1] TD-003: 统一 Judgment Production 与 Rule Matcher 的架构关系
3. [P2] TD-004: Admin Router 安全加固日志
