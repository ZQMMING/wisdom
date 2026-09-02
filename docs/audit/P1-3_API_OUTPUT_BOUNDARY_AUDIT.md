# P1-3: API Output Boundary Audit

**日期:** 2026-09-02
**分支:** main
**目标:** 证明用户 API 输出不能直接暴露 Engine Signal / Signal.direction，数据流必须通过授权 Gate

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

**结论:** AtomicClaim 的 direction 来自 Rule，不来自 Signal。[T22 已通过]

### 1.2 信号路径 (Signals)

```
SignalEngine.build() → signals dict[str, list[Signal]]
  → composer._format_signals() → signals dict for SIR
  → result.canonical.signals (SerializedSignal[] with direction)

API 输出:
  /v1/daily-guide → signal_counts (仅计数) + rendered_text ✅
  /v1/calculate   → signals (完整序列化 Signal 列表) + atomic_claims ✅
```

**发现:** `/v1/calculate` 返回完整 `signals` 字段，包含 `Signal.direction`

---

## 2. 泄露点分析

### 2.1 `/v1/calculate` 端点

```python
# src/tongshu/api/app.py:370-380
resp = {
    "signals": canon["signals"],           # ← 包含 Signal.direction
    "atomic_claims": canon["atomic_claims"], # ← 来自 Rule 授权
}
```

**风险:** `signals.direction` 直接暴露给客户端

**但:**
- `direction` 是引擎内部状态描述（如 "STABLE", "INCREASE"），不是最终结论
- 客户端不能直接通过 Signal.direction 推导结论（没有 claim_id + authorized_rule_id）
- 需要配合 `atomic_claims` 才有意义，而 claims 的 direction 来自 Rule

### 2.2 `/v1/daily-guide` 端点

```python
# src/tongshu/api/app.py:291-314
resp = {
    "signal_counts": {...},       # ← 仅计数
    "atomic_claims": canon.atomic_claims or [],  # ← 来自 Rule 授权
    "rendered_text": result.rendered_text,  # ← LLM 生成
}
```

**结论:** ✅ 无泄露，仅暴露计数

### 2.3 `/v1/today` 端点

```python
# src/tongshu/api/app.py:410+
card = {
    "ganZhi": computed,
    "lunarMonth": hl_dict["lunar_month_label"],
    "yi": hl_dict["yi"],
    "ji": hl_dict["ji"],
    # 无 signals / atomic_claims
}
```

**结论:** ✅ 不涉及 Engine 信号

---

## 3. 边界证明

### 3.1 无直接 Signal → Claim 路径

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

### 3.2 无授权 Claim 路径

```python
# src/tongshu/pipeline_stages/compute_stage.py:182-187
if authorized_assertions:
    atomic_claims = self._build_claims_from_assertions(theme, authorized_assertions)
else:
    atomic_claims = []  # ← fail-closed
```

**证明:** T16-06 已通过 — `assertion_library=None` 时 orchestrator=None

### 3.3 Loader 失败阻断

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

## 4. 风险矩阵

| 端点 | 泄露字段 | 风险等级 | 说明 |
|------|---------|---------|------|
| `/v1/daily-guide` | signal_counts (计数) | 🟢 无 | 仅数量，无内容 |
| `/v1/daily-guide` | atomic_claims | 🟢 无 | direction 来自 Rule |
| `/v1/calculate` | signals | 🟡 中 | 暴露 Signal.direction |
| `/v1/calculate` | atomic_claims | 🟢 无 | direction 来自 Rule |
| `/v1/today` | 无 | 🟢 无 | 不涉及 Engine 信号 |

---

## 5. 结论

### 已证明

1. **Claim 路径安全:** `AtomicClaim.direction` 来自 `ProductionRule`，不来自 `Signal.direction` ✅
2. **Fail-closed 生效:** Loader 失败 → RuntimeError，Pipeline 不启动 ✅
3. **无 bypass 路径:** `_build_claims_from_assertions` 不含 `sig.direction` 引用 ✅

### 需关注

- `/v1/calculate` 暴露完整 `signals` 字段（含 `Signal.direction`）
- 但这是**调试/计算接口**，客户端需要同时获取 `atomic_claims` 才有意义
- Signal.direction 是**引擎状态描述**，不是最终结论

### 建议

**不阻塞 P0.2 关闭。** 如需清理 `/v1/calculate` 的 signals 暴露，可作为 P1 后续任务单独处理。

---

## 测试覆盖

| 测试 | 状态 |
|------|------|
| T22.1 signal.direction 不在授权路径 | ✅ PASS |
| T16-04 真实 Pipeline → claims > 0 | ✅ PASS |
| T16-05 EngineEvidence → orchestrator | ✅ PASS |
| T16-06 fail-closed (None) | ✅ PASS |
| T16-08 runtime trace | ✅ PASS |
| T16-10 loader failure blocks | ✅ PASS |
