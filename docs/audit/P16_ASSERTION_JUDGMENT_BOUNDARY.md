# P1.6 Assertion → Judgment Boundary Audit + Implementation

**Date**: 2026-09-02
**Status**: 🟡 AUDIT COMPLETE — Implementation needed before P1.6 approval
**Baseline**: 272 spec tests PASS

---

## 审计目标

验证 P1.6 八大边界规则在生产路径上的满足情况，识别 Assertion/Judgment 边界泄漏。

### 八大边界规则（User 裁决）
1. Assertion 与 Judgment 职责边界不可混淆
2. Assertion 不得偷偷携带未经授权的 Judgment 结论
3. Judgment 只能消费已经授权的 Assertion / Signal
4. 不允许通过 fallback/默认值/legacy 字段/旁路重新产生 Judgment
5. Judgment 层不能反向改变 Assertion 的事实语义
6. PRODUCTION_ADMITTED 之前的资产不能进入生产 Judgment
7. 所有 Production Judgment 路径最终都必须经过统一授权边界
8. 测试必须覆盖正向 + 负向 + bypass

---

## 三重取证

### ① 调用图取证

| 符号 | src/ 生产代码引用数 | tests/ 引用数 | 结论 |
|------|---------------------|---------------|------|
| `CrossDomainOrchestrator` | 0 | 25 (test_cross_domain) | ⚠️ **孤儿代码** — 仅测试使用 |
| `AssertionRuleLibrary` | 0 | 多处 | ⚠️ **孤儿代码** — 仅测试使用 |
| `ProductionRuleLoader` | 0 | 多处 | ⚠️ **孤儿代码** — 仅测试使用 |
| `JudgmentRuleLibrary` | 0 | 0 | 🔴 **零引用** — 完全未实现 |
| `CanonicalAssertion` | 0 | 测试中 | ⚠️ **孤儿代码** — 仅测试使用 |

**结论**：P1.3/P1.5 新架构全部未接入生产管道。

### ② 生产入口链取证

```
pipeline.py
  └── compute_stage.py
        ├── SignalEngine.build() → signals (含 direction via _DIRECTION_MAP)
        ├── _build_atomic_claims(theme, signals)
        │     └── claim["direction"] = sig.direction  ← 从 Signal 直接取，无 Rule 授权
        ├── CanonicalComposer.compose(atomic_claims=...)
        └── RenderStage.run(compute, ...)
              └── Renderer.render(payload) → text
```

```
grep "CrossDomainOrchestrator\|AssertionRuleLibrary\|JudgmentRule" src/tongshu/pipeline.py src/tongshu/pipeline_stages/
→ 0 matches (仅注释提及)
```

**确认**：生产管道完全走旧 Signal → Claim 路径，不经过任何 Assertion 授权 Gate。

### ③ 方向（direction）溯源

```
src/tongshu/reasoning/signal_engine.py:
  _DIRECTION_MAP = {
      "INCREASE": "POSITIVE",
      "DECLINE": "NEGATIVE",
      "STABLE": "NEUTRAL",
      "VOLATILE": "CHANGE",
  }
  direction = _DIRECTION_MAP.get(signal.direction, "UNKNOWN")

src/tongshu/pipeline_stages/compute_stage.py:
  claims.append({"direction": sig.direction, ...})  # 直接用 signal 的 direction
```

**问题**：direction 来自 `_DIRECTION_MAP`（信号映射），不是来自 `AssertionRule.find_rule()`（规则授权）。

---

## 审计发现

### F1: 生产方向未经 Assertion Rule 授权 🔴

**现状**：
```python
# compute_stage.py:286-294
direction=sig.direction,  # ← 来自 SignalEngine._DIRECTION_MAP
...
"direction": sig.direction,
```

**应有**：
```python
rule = assertion_lib.find_rule(atom, context)
if rule is None:
    continue  # NO_ASSERTION
direction = rule.direction  # ← 来自 Authorized Assertion Rule
```

**违反规则**：#2 (Assertion 不得携带未经授权的方向)

### F2: CrossDomainOrchestrator 未接入生产 🔴

**现状**：`compute_stage.py:144` 注释写着 "replaced by CrossDomainOrchestrator"，但代码中**没有实际调用**。

**应有**：生产路径应经过 `CrossDomainOrchestrator.orchestrate()` 产出 `CrossDomainResult`。

**违反规则**：#7 (所有生产路径须经统一授权边界)

### F3: JudgmentRuleLibrary 零引用 🔴

**现状**：`judgment_rule_library.py` 存在但生产管道零引用，`find_judgment()` 从未被调用。

**应有**：生产管道应通过 `JudgmentRuleLibrary` 产生 Judgment。

**违反规则**：#3 (Judgment 只能消费已授权的 Assertion)

### F4: atomic_claims 携带 direction 绕过授权边界 🔴

**现状**：
```python
claims.append({
    "direction": sig.direction,  # ← 直接来自 signal，未经 Rule 授权
    ...
})
```

**风险**：方向从 Signal 直接传递到 Render，绕过了 `AssertionRuleLibrary.find_rule()`。

**违反规则**：#2, #4, #7

### F5: P1.3/P1.5 组件均为孤儿代码 🔴

`CrossDomainOrchestrator`, `AssertionRuleLibrary`, `CanonicalAssertion`, `ProductionRuleLoader` 在 `src/tongshu/` 中零生产调用方。只有测试文件引用它们。

**违反规则**：#7

### F6: cross_result=None 硬编码 ⚠️

```python
return ComputeResult(
    ...
    cross_result=None,  # ← 硬编码 None
    ...
)
```

P1.4 注释说 "replaced by CrossDomainOrchestrator"，但 `cross_result` 始终为 None。

### F7: 测试未覆盖生产路径 ✅

现有 272 tests 全在 spec/ 层测试新组件，但**没有测试证明生产管道走了新链路**。

---

## 修复方案

### Step 1: 生产管道集成 CrossDomainOrchestrator

在 `compute_stage.py` 中：
1. 接受 `assertion_library: AssertionRuleLibrary` 参数（通过 `ProductionRuleLoader.load()` 加载）
2. 在 `_build_atomic_claims()` 之前，先通过 `CrossDomainOrchestrator.orchestrate()` 编排
3. `atomic_claims` 的 direction 来自 `assertion.rule.direction`（非 `sig.direction`）
4. `cross_result` 字段从 None 改为实际 Orchestrator 输出

### Step 2: 添加 P1.6 边界测试

新增 `tests/spec/test_p16_assertion_judgment_boundary.py`：
- T16: 生产管道必须使用 CrossDomainOrchestrator
- T17: atomic_claim direction 必须来自 Rule（非 Signal）
- T18: 无授权 Rule → NO_ASSERTION（不产出 claim）
- T19: cross_result 不能为 None
- T20: JudgmentRuleLibrary 必须被生产路径调用

### Step 3: 更新文档

`docs/audit/P16_ASSERTION_JUDGMENT_BOUNDARY.md`

---

## 当前 P1 状态

```
P0   🔒 FROZEN
P1.2 🔒 FROZEN
P1.3 ✅ IMPLEMENTED (代码存在，未接入生产)
P1.4 ✅ CLOSED
P1.5 ✅ VERIFIED
────────────────
P1.6 🔴 BOUNDARY VIOLATION DETECTED
     生产管道未接 CrossDomainOrchestrator
     方向未经 Assertion Rule 授权
     待修复后重审
```
