# P1-6: Authority / Semantic Boundary Audit

**日期:** 2026-09-02
**分支:** main
**提交:** 7902d31 (P1-5: Remove dead code legacy_adapter.py)
**目标:** 证明从 Engine 信号到最终 Guidance 之间不存在未经 Authority 授权的语义升级

---

## 执行摘要

| 检查项 | 状态 | 说明 |
|--------|------|------|
| Engine → Signal | 🟢 | 信号仅为计算事实 |
| Signal → Claim | 🟢 | 已切断，Claim 来自 Rule 授权 |
| Signal → Judgment | 🟢 | 无直接路径 |
| Rule → Claim/Judgment | 🟢 | 权威来源明确 |
| Claim → Domain | 🟢 | 经过语义映射 |
| Domain → Guidance | 🟢 | 不重新计算方向 |
| Guidance → LLM | 🟢 | LLM 仅表达，不改变语义 |
| Signal.direction → TemporalConvergence | 🟡 | 内部计算，不输出到 API |
| Signal.direction → Yi Engine | 🟡 | 接口存在但未被调用 |
| TemporalConvergence → API | 🟢 | 不输出 |
| Yi image_reasoning → API | 🟢 | 输出但不含 Signal.direction |

**结论:** Authority Gate 完整，无 bypass 路径。

---

## 1. 数据流追踪

### 1.1 生产路径 (AtomicClaims)

```
BaziEngine → ten_god evidence → SemanticAtom
  → ProductionRuleLibrary.find_rule()
  → CrossDomainOrchestrator.orchestrate()
  → CanonicalAssertion(authorized_rule_id, direction=rule.direction)
  → AtomicClaim(authorized_rule_id, direction=rule_direction)

API 输出:
  /v1/daily-guide → atomic_claims (含 authorized_rule_id + rule_direction) ✅
  /v1/calculate   → atomic_claims (含 authorized_rule_id + rule_direction) ✅
```

**证明:** T22.1 已通过 — 生产源码不含 `sig.direction` 直接赋值到 claim

### 1.2 Signal.direction 流向分析

#### 路径 A: Signal.direction → TemporalConvergence

```python
# src/tongshu/pipeline_stages/compute_stage.py:429
direction = _DIR_MAP.get(sig.direction, "UNKNOWN")

# 创建 TemporalSignal
return TemporalSignal(
    direction=direction,  # ← 来自 Signal.direction
    ...
)
```

**下游使用:**
```python
# src/tongshu/temporal/convergence.py:97
if self._signals[sid].direction != "UNKNOWN"
```

**输出到 API?**
```python
# src/tongshu/api/app.py - 无 temporal_convergence 字段
# src/tongshu/canonical/composer.py - 无 temporal_convergence 字段
```

**结论:** 🟡 TemporalConvergence 使用 `Signal.direction` 进行内部计算，但**结果不输出到 API**。

#### 路径 B: Signal.direction → Yi Engine

```python
# src/tongshu/yi/adapter.py:105-108
if input_data.canonical_signals:
    for sig in input_data.canonical_signals[:3]:
        image_reasoning.append(
            f"{sig.source_engine.value}→{sig.direction}#{sig.signal_id}"
        )
```

**接口存在但未被调用:**
```python
# src/tongshu/pipeline_stages/compute_stage.py:280-285
yi_input = YiAdapterInput(
    heluo_prenatal_hexagram=...,
    heluo_postnatal_hexagram=...,
    heluo_yuantang_index=...,
    heluo_yuantang=...,
    # ← 无 canonical_signals 参数！
)
```

**输出到 API?**
```python
# src/tongshu/api/app.py:280-288
def _yi_block(result) -> dict | None:
    block = {}
    if result.yi_structure is not None:
        block["yi_structure"] = result.yi_structure.to_dict()
    if result.yi_interpretation is not None:
        block["yi_interpretation"] = result.yi_interpretation.to_dict()
    return block or None
```

**结论:** 🟡 Yi Adapter 接口支持 `canonical_signals`，但当前调用**不传递该参数**。`image_reasoning` 为空列表。

---

## 2. 边界证明

### 2.1 无直接 Signal → Claim 路径

```python
# src/tongshu/pipeline_stages/compute_stage.py:502-522
def _build_claims_from_assertions(self, theme: str, assertions: list[dict]) -> list[dict]:
    """direction comes from Rule, not Signal.
    P1.6 boundary: claims from authorized assertions only.
    No signal.direction bypass.
    """
    claims = []
    for auth in assertions:
        claims.append({
            "direction": auth.get("rule_direction", "UNKNOWN"),  # ← 来自 Rule
            # ... 无 signal.direction 引用
        })
```

**证明:** T22.1 已通过 — 生产源码不含 `sig.direction` 直接赋值

### 2.2 无授权 Claim 路径

```python
# src/tongshu/pipeline_stages/compute_stage.py:182-187
if authorized_assertions:
    atomic_claims = self._build_claims_from_assertions(theme, authorized_assertions)
else:
    atomic_claims = []  # ← fail-closed
```

**证明:** T16-06 已通过 — `assertion_library=None` 时 orchestrator=None

### 2.3 Loader 失败阻断

```python
# src/tongshu/pipeline.py:161-176
if not assertion_rules_path.exists():
    raise RuntimeError(...)  # ← fail-closed
try:
    assertion_library = ProductionRuleLoader.load(...)
except Exception as e:
    raise RuntimeError(...)  # ← fail-closed
```

**证明:** T16-10 已通过

---

## 3. 风险矩阵

| 路径 | 泄露字段 | 风险等级 | 说明 |
|------|---------|---------|------|
| Signal → TemporalConvergence | direction | 🟡 低 | 内部计算，不输出 API |
| Signal → Yi Adapter | direction | 🟡 低 | 接口存在但未调用 |
| Yi → API (image_reasoning) | direction | 🟢 无 | 当前为空列表 |
| TemporalConvergence → API | 无 | 🟢 无 | 不输出 |

---

## 4. 结论

### 已证明

1. **Claim 路径安全:** `AtomicClaim.direction` 来自 `ProductionRule`，不来自 `Signal.direction` ✅
2. **Fail-closed 生效:** Loader 失败 → RuntimeError，Pipeline 不启动 ✅
3. **无 bypass 路径:** `_build_claims_from_assertions` 不含 `sig.direction` 引用 ✅
4. **API 边界安全:** `/v1/daily-guide` 不暴露 Signal.direction ✅

### 观察项（非阻塞）

- `TemporalConvergence` 内部使用 `Signal.direction` 进行时序聚合计算
- `YiAdapter` 接口支持 `canonical_signals` 但当前未传递
- 这些路径**不影响最终 Claim/Guidance 的权威性**

---

## 5. 测试覆盖

| 测试 | 状态 |
|------|------|
| T22.1 signal.direction 不在授权路径 | ✅ PASS |
| T16-04 真实 Pipeline → claims > 0 | ✅ PASS |
| T16-05 EngineEvidence → orchestrator | ✅ PASS |
| T16-06 fail-closed (None) | ✅ PASS |
| T16-08 runtime trace | ✅ PASS |
| T16-10 loader failure blocks | ✅ PASS |
| Vertical slice: no legacy signal in chain | ✅ PASS |
| Vertical slice: full traceability | ✅ PASS |

---

## 6. 建议

**P1-6 = CLOSED。**

Authority / Semantic Boundary 已完整建立。`Signal.direction` 在 TemporalConvergence 和 Yi Engine 中的使用属于**内部计算语义**，不构成对 Production Rule 权威性的绕过。

如未来需要清理，建议：
1. 评估 TemporalConvergence 是否仍需 `Signal.direction`
2. 评估 Yi Adapter 的 `canonical_signals` 参数是否需要启用

当前无需修改。
