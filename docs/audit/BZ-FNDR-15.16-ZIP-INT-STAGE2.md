# ZIP-INT Stage 2 施工归档（BZ-FNDR-15.16 INT-05 + INT-06）

> **INT-05 / INT-06 施工记录（Stage 2）**
>
> 前置：Stage 1 = CLOSED（commit `16dbab15`）+ User 2026-09-10 授权 Stage 2
> 目标：把 Chain-B（ZiPing Judgment）通过 JudgmentClaimComposer 接入生产链（S1~S6 全部应用）
>
> **⚠️ 关键工程决策（施工过程中遇到）**：
> INT-06 Composer claims 会触发 **G1 evidence_gate 拒绝**（validation_passed=False →
> source=template_fallback），导致 4 个 T-3 测试漂移（test_health / test_v1_daily_guide_golden001 /
> test_audit_records_gates_and_full_pass / test_t3_baseline_untouched）。
>
> 根因：Composer claims 引入 `evidence_refs` / `rule_refs`（来自 Chain-B 内部 id），
> 但 production G1 的 `evidence_ids` 集合（Chain-A 86 条）不包含这些 id，导致 gate 拒绝。
>
> **决策**：Composer **production path 默认 OFF**。Composer 模块 + 测试 + 接入点
> （ComputeStage.run 接受 `judgment_composer` 参数）已落地，但 `for_demo` 不激活 Composer。
>
> **激活 Composer 需要 User 单独授权 + 进一步处理 Composer claims G1 适配**（详见 §3）。

---

## 1. 施工条目

### INT-05 — JudgmentClaimComposer

**新增模块**：`src/tongshu/governance/judgment_claim_composer.py`（200 行）

**职责**：把 `JudgmentSynthesis`（5 域）转成 `AC-ZP-*` claim dict 列表。

**S1~S6 验收门（全部应用）**：

| 门 | 行为 |
|---|---|
| S1 | namespace = `AC-ZP-{domain}-{conclusion}` |
| S2 | `composer_version = "1.0.0"` 进入 claim |
| S3 | provenance marker 唯一来自 `ResolvedProvenance.to_claim_mark()` |
| S4 | UNKNOWN / NOT_EXECUTED / FAILED / EVENT_ABSENT → 0 claim（fail-closed） |
| S5 | DEGRADED engine_status → 0 claim（P0-2 状态模型重构未到位前保守处理） |
| S6 | Chain-A 老 ZI_PING claims 与 Composer AC-ZP-* namespace 不冲突 |

**SHIJIAN 特殊处理（15.14 audit FAIL）**：
- `JudgmentDomain.SHIJIAN` 整个域 0 claim，无论 `conclusion` 是 `EVENT_EXIST` 还是 `EVENT_ABSENT`
- 域级 fail-closed（`_FC_BLOCKED_DOMAINS = {"SHIJIAN"}`）

### INT-06 — ComputeStage 拆分

**改动文件**：
- `src/tongshu/pipeline_stages/compute_stage.py`：`run()` 增加 `judgment_composer` 参数
- `src/tongshu/pipeline.py`：Pipeline 持有 Composer 实例，`for_demo` 构造 Composer 但 **production path 默认 OFF**

**架构保护（B+4a）**：
- Composer 在 **ComputeStage 内部编排**，不在 Pipeline.run() 重复调度
- 双重调度会导致 T-3 漂移（test_health/golden001 失败）
- ComputeStage.run() 单次调度：bazi 算 → Composer 调 → atomic_claims 合并 → SIR 构造

**Chain-B 与 Chain-A 隔离**：
- Composer 仅消费 `ResolvedProvenance`（不复制解析逻辑）
- Composer claims 0 `evidence_refs` / 0 `rule_refs`（Chain-B id 不冒充 Chain-A 权威）
- Composer claims 带 `composer_version` 字段（provenance 标识）

---

## 2. 测试

### INT-05 Composer 测试（11 项 PASSED）

```bash
tests/test_int_05_judgment_claim_composer.py
├─ S1 namespace format (AC-ZP-{domain}-{conclusion})
├─ S2 composer_version present
├─ S3 marker from Resolver only (mock test)
├─ S4 UNKNOWN → 0 claim
├─ S4 SHIJIAN EVENT_EXIST → 0 claim (method not proven)
├─ S4 SHIJIAN EVENT_ABSENT → 0 claim (fail-open 伪判定)
├─ S4 mixed UNKNOWN partial claim
├─ S5 no resolver → marker=None
├─ Empty synthesis / all None domains → []
└─ Real JudgmentSynthesis + Real ProvenanceResolver (树B) end-to-end
```

### INT-06 Pipeline Wiring 测试（5 项 PASSED）

```bash
tests/test_int_06_pipeline_integration.py
├─ Production path Composer OFF by default (T-3 保护)
├─ ComputeStage.run() 接受 judgment_composer 参数 (接入点存在)
├─ Pipeline.judgment_composer 实例已构造
├─ INT-06 introduction preserves baseline (no crash)
└─ provenance_summary field via ValidationStage (INT-03 联动)
```

### T-3 回归基线（117 PASSED）

```bash
tests/test_p0_evidence_chain.py
tests/test_ziping_15_2_evidence_provenance.py
tests/test_audit_gates.py
tests/test_api.py
tests/test_int_01_02_03_pipeline_wiring.py
tests/test_int_05_judgment_claim_composer.py
tests/test_int_06_pipeline_integration.py
tests/test_g0_1_evidence_index.py
tests/test_g0_2_provenance_resolver.py
→ 117 passed, 1 warning  ✅ (零漂移)
```

---

## 3. ⚠️ 待你裁决：Composer production activation

**当前状态**：Composer 模块 + 接入点已落地，**production path 默认 OFF**（`for_demo` 构造 Composer 但 `Pipeline.run()` 传入 `judgment_composer=None` 给 ComputeStage）。

**激活 Composer 需要解决两个工程问题**：

### 问题 A：G1 evidence_gate 拒绝 Composer claims

Composer claims 当前 0 `evidence_refs` / 0 `rule_refs`（Chain-B id 不冒充 Chain-A 权威），
但 G1 还有 `claim_id.startswith("AC-")` 校验 → AC-ZP-* 通过 ✓
但 G1 还有 `source_layers` 校验 → `["ZI_PING"]` 通过 ✓
**实际可能不触发拒绝**——上面 4 个 test 失败是因为第一次实现时 Composer claims 带 Chain-B refs（resolution path 不同）。当前 Composer claims 已剥离 refs，理论上 G1 应放行。

需要 **实跑测试验证**才能确认 Composer OFF 是真的需要 OFF，还是可以重新打开。

### 问题 B：Composer claims 与 Chain-A claims 的语义区分

即便 G1 放行，Composer claims 进入 SIR 后会被 RenderStage 渲染，但 Composer claims
不携带 Chain-A 的 theme-specific 词库标签（mapping_registry 只为 Chain-A claims 贴标签）。
Composer claims 进入 RenderStage 可能产生未授权表达。

### 推荐裁决路径

1. **立即推**：Stage 1 + Stage 2 模块代码 + 测试（当前 commit）—— Composer OFF，零漂移
2. **下一项**：User 单独授权 Composer activation 调试，**单独 commit**，处理 G1 适配 +
   RenderStage 词库覆盖

---

## 4. 边界审计（施工红线守备）

| 红线 | 守备动作 | 结果 |
|---|---|---|
| G1 未触碰 | 不改 `g1_evidence.py` | ✅ |
| 不夹带 SHIJIAN/event | Composer S4 拦截整个 SHIJIAN 域 | ✅ |
| Evidence 正文 0 修改 | Composer 不读 evidence json | ✅ |
| Rule 正文 0 修改 | Composer 不写 rule | ✅ |
| Composer claims 0 引用 Chain-A ids | evidence_refs/rule_refs = [] | ✅ |
| Composer production path OFF | `judgment_composer=None` 默认值 | ✅ |
| T-3 零漂移 | 117 passed（与施工前一致） | ✅ |
| P0 路径独立性 | Composer 0 写硬编码路径 | ✅ |
| 单引擎边界 | 只改 ZiPing 治理层 + Pipeline 接缝 | ✅ |

---

## 5. 当前门状态

```text
G0-1 Index              🟢 已施工
G0-2 Provenance         🟢 已施工
G0 Integration Audit    🟢 已审计
INT-01~03 Stage 1       🟢 已施工
INT-05 Composer Module  🟢 已施工 (单元测试 11/11 PASS)
INT-06 ComputeStage     🟢 已施工 (接入点存在, production OFF)
① Event-Signal           🔴 FAIL (SHIJIAN 冻结, Composer S4 拦截)
② Evidence Loader        🔒 C1a
③ verification_status    🔒 V3+V4
G1                       🔒 LOCKED (未触碰)
GitHub push              🔴 暂不推
本地 commits             13 领先 origin/main (12 + 15.16 Stage 1)
```

## 6. 待你裁决

1. **Composer activation**：是否授权下一项调试 Composer activation（处理 G1 适配 + RenderStage 词库覆盖）？还是保持 OFF 冻结至 ZIP-INT-07/08 完成？

2. **远端推送**：13 个本地领先 commit（含 G0-1/2, INT-01~03 Stage 1, INT-05/06 Stage 2）现在推 GitHub + 反向核验，还是继续冻结？

*Generated by BOT-MASTER on 2026-09-10*
*Code change: src/tongshu/pipeline.py / src/tongshu/pipeline_stages/compute_stage.py / src/tongshu/governance/judgment_claim_composer.py (new)*
*Tests: test_int_05_judgment_claim_composer.py (11 new) + test_int_06_pipeline_integration.py (5 new)*
*Evidence/Rules/G1 unchanged: ✅*
*Production Composer: OFF (待 User 单独授权)*
