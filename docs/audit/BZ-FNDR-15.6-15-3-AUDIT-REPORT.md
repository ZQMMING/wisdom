# ⑮-3 ZiPing Remaining Domains Audit Report

> **BZ-FNDR-15.6 / ⑮-3：子平剩余域全链路审计（A~H）**
> **Audit-Only, No Code Change**
>
> 本 commit 是 **Audit Record Commit，不是 Remediation Commit**。
> 不含任何代码修改、Evidence 重挂、Rule ID 变更、算法调整、⑮-2 CLOSED 项回改。

---

## 0. 审计元数据

| 项 | 值 |
|---|---|
| 审计 ID | BZ-FNDR-15.6 |
| 审计阶段 | ⑮-3 ZiPing Remaining Domains |
| 基线 commit | `48e66f6c`（⑮-2-P1-Sub R-A 审计归档） |
| 冻结基线 | Bazi ①~⑭、⑮-0、⑮-1、⑮-2 P0 全部 FROZEN / CLOSED |
| 审计窗口 | 2026-09-10 |
| 执行者 | BOT-MASTER（User 授权综合决策） |
| **Code Change** | **0（本 commit 仅含本文件）** |
| **Git push** | **未推远程** |
| 回放样本 | 公历 1983-11-03 12:00 BJT（立冬前 5 天，与 ⑫ Oracle 同命例） |

### ⑮-3 状态锁定（User 裁决口径）

```text
⑮-3 ZiPing Remaining Domains Audit
AUDIT                  = COMPLETE / CLOSED
CALCULATION_CORE       = VALIDATED
PRODUCTION_INTEGRATION = BLOCKED
PRODUCTION_ADMISSION   = BLOCKED / CONDITIONAL
CODE_REMEDIATION       = NOT STARTED
```

---

## 1. 阶段链

```text
⑮-0 Bazi → ZiPing 接入契约 (BZ-FNDR-15)            → CLOSED 🔒
⑮-1 子平自身方法审计 (BZ-FNDR-15.3)                 → CLOSED 🔒
⑮-2 P0 CITATION 元数据 (BZ-FNDR-15.4)               → CLOSED 🔒
⑮-2-P1-Sub Evidence Provenance (48e66f6c)           → Audit CLOSED / Provenance OPEN
⑮-3 子平剩余域 A~H 全链路                            → 本文
```

⑮-3 审计顺序（User 锁定）：
`A Feature/Resolver → B Judgment→Resolution → C Evidence/Provenance → D 辨层输出契约 → E 解层输入隔离 → F Production Path 终审 → G Fail-closed 终审 → H 全链路回放`

---

## 2. A~H 阶段事实矩阵

### A — Feature / Resolver 完整性（COMPLETE）

- 5 个 Adapter 全部实现 `adapt()`，0 个 NotImplementedError 占位。
- ZiPing 26 Feature，18/19 ZiPingCanonicalBaziChart 字段覆盖（唯一未覆盖 = `birth_datetime` 元数据，合理）。
- 0 个 NOT_AUTHORIZED 字段残留（⑮-0 P1-1 验证）。
- **A-P0-1/2/3**：`run_ziping_judgment` / `ZiPingFeatureAdapter` / `judgment_index_foundation` 在 src/ 生产链路 0 调用；`pipeline.py` 不引用 FeatureRegistry。→ 归并入 P0-1（见 §3）。

### B — Judgment → Resolution 边界（COMPLETE）

| 项 | 判定 |
|---|---|
| B-1 Judgment Boundary | 🟡 P1 OPEN — JudgmentFactory/Index 仅测试消费 |
| B-2 Resolution Boundary | 🟡 P1 OPEN — 解层 = LLM 渲染 SIR，0 消费 JudgmentSynthesis |
| B-3 Provenance Carry-over | 🔴 P0（并入 P0-1）— 链 A 活跃 / 链 B 孤岛，无对齐机制 |
| B-4 Fail-closed | 🟢 PASS — 0 fail-open 残留（UNKNOWN/MISSING 收敛正确） |
| B-5 Deterministic Isolation | 🟢 PASS — judgment 0 LLM；解层 LLM 仅表达式 |
| B-6 Production Call Path | 🔴 P0（并入 P0-1）— 裁定①：生产链路确实断，②假设排除 |

### C — Evidence / Provenance 剩余域（COMPLETE）

| 项 | 判定 |
|---|---|
| C-1 G1 覆盖面 | 🔴 P0（并入 P0-1）— G1 仅覆盖 SIR atomic_claims，Judgment 链全在 G1 之外 |
| C-2a 生产加载边界 | 🔴 P0（新）— 生产 `RuleLoader` 非递归 `glob("*.json")`，五经子目录（yuan_hai_zi_ping / ziping_zhenquan / di_tian_sui / qiong_tong_bao_jian / san_ming_tong_hui）对生产不可见；`E-DTS-106-001` 生产解析 = 根级 paraphrase，classical 原文被遮蔽 |
| C-2b YHZP-105 | 🟠 P1（latent）— 主 evidence 位于子目录，remediation 补挂时 G1 会判 unresolved |
| C-2c verification_status | 🟠 P1 — G1 不读 `source_layer` / `verification_status`；pending_verification 与 verified 生产等价放行 |
| C-3 Assertion V2 | 🟠 P1 — `ZiPingJudgmentType` 0 生产消费（孤立定义） |
| C-4 双链合流 | 🔴 P0（并入 P0-1）— 合流断层三处证据同源确证 |

### D — 辨层输出契约（COMPLETE）

| 项 | 判定 |
|---|---|
| D-1 五域输出结构 | CONTRACT_DEFINED ✅ / 部分 TESTED / CONNECTED ❌ / PRODUCTION_CONSUMED ❌ |
| D-2 UNKNOWN 契约 | 🔴 P0-2（独立）— `has_core_judgment()` 判据 = `is not None`，**全 UNKNOWN 仍报 True**；`EVENT_ABSENT` 枚举残留死值（fail-open 地雷） |
| D-3 Judgment→SIR | 🔴 P0（并入 P0-1）— 正式转换器不存在（composer / compute_stage 0 judgment 引用） |
| D-4 Assertion 双轨 | 🟠 P1 — 旧轨（production_assertion_rules.json，10 条，生产 fail-closed 加载）与 V2 轨（孤立交并）并存，类型映射缺失 |
| D-5 辨层纯净度 | 🟢 PASS — 0 LLM / 0 话术 / 0 解层混入 |
| D-6 确定性回放 | 🟡 P2 — `created_at = now()` 非确定源 |

### E — 解层输入隔离（COMPLETE）

| 项 | 判定 |
|---|---|
| E-1 RenderStage 输入源 | 🟢 PASS — 实收输入仅 `canonical.to_dict()` + 4 meta 字段 |
| E-2 LLM 输入隔离 | 🟢 PASS — 0 BaziChart / 0 Judgment / 0 Evidence 读盘；guardrail = 确定性常量 |
| E-3 解层重算事实 | 🟢 PASS — render/ 全目录 0 处 BaziEngine/sxtwl/ten_god 重算 |
| E-4 LLM 输出边界 | 🟢 PASS — text + claim 回读清单；`self_check` 无机器复核（P2 观察项） |
| E-5 Validation 兜底 | 🟢 PASS — render→validation→替换→output 顺序正确；`enable_validation=False` 分支 = P2 观察项 |
| E-6 fallback 隔离 | 🟡 P2 — 18 条确定性模板，UNKNOWN 未被转成确定性话术；fallback 路径无 evidence 溯源（契约声明项） |
| E-7 数据泄漏边界 | 🟠 P1 — API 响应体全量透传 `atomic_claims`（含内部 rule/evidence ID）+ `audit_entry_id` |

### F — Production Path 终审（COMPLETE）

| 项 | 判定 |
|---|---|
| F-1 全入口清单 | 唯一生产入口族 = `TONGSHUPipeline`（/v1/calculate + /v1/daily-guide + deprecated /api/reading）；ZiPing 无独立入口；services/ 8 模块 0 引用 |
| F-2 真实生产链 | 链 A 全程活跃；ZiPing Feature/Judgment/Synthesis 生产 0 接入 |
| F-3 双入口终验 | 入口①成立；入口②（run_ziping_judgment）**非生产入口**（仅 scripts 基准工具 + tests + reference 异项目） |
| F-4 stored-never-read | `ComputeResult.canonical_bazi_chart` 全仓 0 生产读取（3 处引用全在 tests/） |
| F-5 最终断点 | **B-3 / C-4 / D-3 / F-4 = 同一架构断点的 4 种观测面，P0 计数 = 1** |
| F-6 Admission | Calc Core ✅ / ZiPing logic ✅（可现状）/ 接通 🔴 / Provenance 链 A 闭合链 B 不闭合 |
| F-7 fail-closed | 🟠 P1 — 隐性认知 fail-open：`cross_status` 纯链 A 派生 + 0 处 `ENGINE_NOT_CONNECTED` 类声明，未接事实被正常输出掩盖 |

### G — Fail-closed / Error Boundary 终审（COMPLETE）

| 检查项 | 正常 | 异常 | Fail-closed | Severity | Status |
|---|---|---|---|---|---|
| Judgment | 5 域确定性 | 异常→仅 wangshuai=UNKNOWN，4 域 None；状态粒度丢失 | 半 | P1（并入 D-2） | OPEN |
| Feature | 24 字段直读 | AttributeError 硬上抛（0 静默） | ✅ | — | PASS |
| Evidence | G1 未解析 ID→BLOCK | **pending 与 verified 等价放行；collision 不可检出（静默取根级）** | ❌ | P0（并入 C-2a/C-2c，非 ⑮-3 新增） | OPEN |
| SIR/G1 | 链 A 全过 gate | 绕过路径 = 仅 `enable_validation=False` 开关 | ✅ | P2（E-5） | PASS |
| ZiPing 未接通 | — | "未运行"被 cross_status + atomic_claims 掩盖 | ❌（语义层） | P1（维持 F-7） | OPEN |
| Render/Fallback | LLM 校验通过 | timeout/malformed→模板✅；empty text→脏 audit；unknown theme→空响应 | ✅（落"空/脏"不落"错"） | P2 x2 | OPEN |
| API Output | 3 状态字段可辨 | P0/P1 异常仍出正常 reading；引擎参与状态不可见 | 运行时健全/语义缺失 | P1（同 F-7/G-5） | OPEN |

**G 结论**：异常放大效应全部落在**静默放行与语义冒充**，无"错误结论放行"。P0 增量 = 0（Evidence 行为 C 阶段既有项的异常视角确证）。

### H — 全链路回放（COMPLETE）

真实样本（1983-11-03 午时，male，theme=WORK，StubLLM 确定性注入）实跑 `TONGSHUPipeline.for_demo`：

| 观测点 | 实测 | 结论对应 |
|---|---|---|
| validation_passed | True（L1/L2/L3 + G1-G4 全过） | 链 A 运行时健全 |
| atomic_claims | 3 条，source_layers 全 ZI_PING | 链 A 携带 ZI_PING 标签 |
| PipelineResult 字段全集 | **0 judgment 字段、0 canonical_bazi_chart 属性** | F-4 运行时实锤 |
| 链 B 独立直调 | 5 域 = MODERATE/ESTABLISHED/PRIMARY/None/None；⑮-2 P0 修正的 CITATION 挂载实活（DTS-102/SMTH-102/E-DTS-105-001）但生产 0 消费 | H-3 双链独立、互不校验 |
| 确定性回放 | 断言级一致 ✅；meta 随机 ID（canonical_id 尾 8 + request/trace/document_id）不一致 | E8 回放需剥离 meta 段 |
| P2.1-F bootstrap | fail-closed 实测成立（缺 credential → RuntimeError） | 生产启动边界健全 |

**H 核心命题确认**：「ZiPing 算法/判断代码存在且测试可验证，但生产 Pipeline 0 消费其结果」——运行时证据全部成立，无一例外。

---

## 3. P0 根因去重（最终版）

**⑮-3 全部 P0 归并为唯二：**

### P0-1：Production Integration 单一架构断点

```text
观测面（6 处，同一根因）:
B-3 (provenance 双链断层)
C-4 (双链合流未建)
D-3 (Judgment→SIR 无转换器)
F-4 (canonical_bazi_chart 写而不读)
H-2 (PipelineResult 0 judgment 字段)
H-3 (双链独立、结果互不校验)
        ↓ 同一根因
ZiPing Chain B (Feature → Judgment → JudgmentSynthesis)
        ↓
0 production consumer
        ↓
未进入 SIR / G1 / Resolution / API
```

**定性**：⑮-0 接入契约对象（ZiPingCanonicalBaziChart）在生产链路构造成功（factory provenance 通过）但零消费；ZiPing 辨层整体处于测试自证状态。**不是 6 个 P0，是 1 个 P0 的 6 种观测面。**

**不裁决项**：接通架构（B→A 合流 / 判层下沉 / 独立 G5 / 显式降级标注）留待 **Remediation Architecture Arbitration**，本归档不选。

### P0-2：`has_core_judgment()` UNKNOWN 误报

- `judgment.py` `has_core_judgment()` 判据 = `is not None`（域对象存在），非 `conclusion != UNKNOWN`。
- 全 UNKNOWN 态（含 G-1 异常降级态）→ 误报 True。
- 涉及已 CLOSED 的 ⑮-2 域行为（⑮-1 A1/A2 修改同文件）。
- **不得在本次归档中修复；需 User 单独裁决**（是否重开 ⑮-2 行为基线）。

---

## 4. Remediation Queue（仅登记，不执行）

> ⚠️ **建立 Queue ≠ 已决定接通架构**。下一阶段 = Remediation Architecture Arbitration（先裁决 P0-1 架构，再让 BOT 出实施方案）。
> 任何开发 BOT 不得在本阶段修改代码、Evidence、Rule ID 或 ⑮-2 CLOSED 项。

| 优先级 | 项目 | 状态 |
|--------|------|------|
| **P0** | ZiPing Chain B → Production Chain A 接通（P0-1，架构待裁决） | OPEN |
| **P0** | `has_core_judgment()` UNKNOWN 语义（P0-2，涉 ⑮-2 CLOSED 域） | OPEN / 需单独裁决 |
| P1 | E-7 `atomic_claims` 内部 ID 暴露（泄漏 vs 审计字段，待裁决） | OPEN |
| P1 | F-7/G-5/G-7 未接通状态显式标识（ENGINE_NOT_CONNECTED 类输出语义） | OPEN |
| P1 | Assertion V2 / Legacy 双轨定轨 + 类型映射 | OPEN |
| P1 | ⑮-2-P1-Sub provenance 未闭合项（DTS-106 PROVENANCE-BLOCKED / ZPZ PARTIAL x5 / 调候 / 病药阈值 / 五级顺序 / YHZP-105 绑定） | EXISTING OPEN |
| P2 | Replay 随机 ID / `created_at`（E8 回放前置，meta 段剥离） | OPEN |
| P2 | `enable_validation=False` 开关语义（LLM 未校验直出分支） | OPEN |
| P2 | fallback provenance 契约（模板 0-evidence 输出声明） | OPEN |
| P2 | SHISHEN/SHIJIAN `None` vs `UNKNOWN` 语义（域未执行 ≠ 域不可判） | OPEN |

（C-2a 生产加载边界 / C-2b YHZP-105 latent / C-2c verification_status 不入 G1 — 作为 P1「⑮-2-P1-Sub provenance 未闭合项」的实现前置条件记录于该项。）

---

## 5. 冻结项（本归档生效后维持）

```text
Bazi ①–⑭              CLOSED 🔒
Canonical ⑭            FROZEN 🔒
⑮-0 接入契约            CLOSED 🔒
⑮-1 自身方法           CLOSED 🔒
⑮-2 P0                 CLOSED 🔒
⑮-2-P1-Sub             Audit CLOSED / Provenance OPEN / Admission BLOCKED
⑮-3                    Audit COMPLETE / Integration BLOCKED（本文）
Golden expected values  不动
Basis: 415 PASS 基线 + Dual-Track 44/44
```

---

## 6. ⑮-3 核心结论（最终版）

> **ZiPing 算法/判断层（链 B）内部有效、可测试、⑮-2 P0 修正的 provenance 挂载实活；但生产 Pipeline（链 A）0 消费其结果，双链互不校验。⑮-3 全部 P0 去重后 = 1 个架构断点（Production Integration 未成立，P0-1）+ 1 个 ⑮-2 域行为缺陷（has_core 误报，P0-2）。Production Admission = BLOCKED / CONDITIONAL，现具备运行时实证（H 回放）而非仅静态推断。**
>
> **CALCULATION_CORE = VALIDATED（保持）；ZiPing internal logic 可维持现状；Production Integration 未接通前，不得对 ZiPing 引擎签 BASIC_VALIDATED 之上的任何 lifecycle 状态。**
