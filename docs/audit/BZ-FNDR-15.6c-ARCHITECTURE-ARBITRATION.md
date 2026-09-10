# ⑮-3 P0-1 / P0-2 Remediation Architecture Arbitration Record

> **BZ-FNDR-15.6c：P0-1 / P0-2 接入架构裁决（D-1～D-7 锁定）**
> **Architecture-Only, No Code / Evidence / Rule / Algorithm Change**
>
> 本 commit 是 **Architecture Arbitration Record，不是 Remediation Commit，也不是实施任务单**。
> 不含任何代码修改、Evidence 重挂、Rule ID 变更、算法调整、⑮-0/⑮-1/⑮-2 CLOSED 项回改。
> 本文**锁定 D-1～D-7 架构裁决**，把 P0-1/P0-2 的实施边界写死，并拆解 BOT-ZIPING
> 后续实施任务（**仅登记，禁止执行**），供 User 审阅后再单独下达实施授权。

---

## 0. 审计元数据

| 项 | 值 |
|---|---|
| 审计 ID | BZ-FNDR-15.6c |
| 记录类型 | Remediation Architecture Arbitration（架构裁决，非审计、非实施） |
| 前置记录 | `ab7a9574`（⑮-3 A~H）→ `0e395996`（15.6b 反向一致性审计） |
| 代码取证基线 | `40eeb359` → `48e66f6c` → `ab7a9574` → `0e395996`（均 `git show` 已提交版本） |
| 裁决输入 | User 2026-09-10 对 D-1～D-7 的逐点拍板 |
| 执行者 | BOT-MASTER（调度 + 裁决记录；实施由 BOT-ZIPING 单独授权后执行） |
| **Code Change** | **0** |
| **Evidence Change** | **0** |
| **Rule Change** | **0** |
| **Algorithm Change** | **0** |
| **Git push** | 待 User 审阅后裁决 |

### 架构总原则（永久，本文所有裁决的依据）

```text
算 → 辨 → 解（不得倒置）
Deterministic First（确定性能做的不交 LLM）
AI Is Expression Only（LLM 不得改 Calculation/Signal/Evidence/Rule/Judgment/Mapping）
Fail Closed（缺证据不强行出结论）
先架构、后 BOT 实施；先锁数据契约、再写代码
```

---

## 1. 最终锁定版本（User 拍板）

```text
P0-1 = 采用 B + 4a（独立 ZiPing Judgment Stage + Compute/SIR 拆分定稿）
P0-2 = Judgment State Model 重构（不做局部 is not None 补丁）
D-4  = 8 字段命局 Feature Contract，luck_pillars 独立留给未来大运域
D-5  = 不重开整个 ⑮-1，只新增 ⑮-1-EVENT-SIGNAL 方法审查
D-6  = 有条件重开 ⑮-2，仅重开 Judgment State Semantics 基线
```

### 目标架构（锁定）

```text
BirthInput
   ↓
TimeResolver
   ↓
BaziEngine
   ↓
Frozen CanonicalBaziChart
   ↓
ComputeStage                     [算]
   ├─ Bazi deterministic facts
   └─ Domain-independent signals
   ↓
ZiPingJudgmentStage              [辨]
   ├─ Feature Resolver（域隔离 Feature View）
   ├─ Domain Features
   ├─ Judgment Rules
   └─ JudgmentSynthesis
   ↓
JudgmentClaimComposer            [唯一 Judgment→Claim 转换边界]
   ↓
SIR / CanonicalContent 最终定稿
   ↓
G1 Evidence Gate（唯一生产 Evidence Gate，不新增 G5）
   ↓
RenderStage                      [解]
   ↓
ValidationStage
   ↓
Output
```

**禁止模式（P0-1 根因，自此封死）：**

```text
Compute
 └─ 顺手生成最终 SIR
      ↓
Judgment 再平行跑
```

SIR 是"解层输入的最终事实/判断载体"，**不得在 Judgment 完成前提前定稿**（D-3 4a 锁定的直接理由）。

---

## 2. D-3：Compute / SIR 定稿拆分【LOCKED = 4a】

**锁定 4a：ComputeStage 拆两段，Judgment 完成后再 `compose_sir` 定稿。**

```text
ComputeStage.run_compute()   → 确定性事实 + 域无关 signals + 中间产物
   ↓
ZiPingJudgmentStage.run()    → JudgmentSynthesis
   ↓
JudgmentClaimComposer        → 合并 claims
   ↓
compose_sir(final claims)    → SIR / CanonicalContent 定稿（唯一一次）
```

- **判层输出时序上先于 SIR 定稿**，"算→辨→解"严格成序。
- 代价：4a 拆分 ComputeStage 契约会触碰既有 415 PASS 基线测试（回归成本在实施任务单里评估，不在架构层）。
- **4b（最小改动、辨先于算组尾但阶段糊）已被 User 否决**，永久不采用。

---

## 3. D-4：命局 5 域 Feature Contract【LOCKED = 8 进命局 / luck_pillars 留大运域】

### 命局 5 域 Feature 映射（锁定）

| Canonical Fact | Feature | 消费域 |
|---|---|---|
| `five_element_balance` | 五行分布 | 旺衰 |
| `day_branch_main_ten_god` | 日支主气十神 | 格局 / 旺衰 |
| `branch_clash_map` | 冲 | 事件 |
| `branch_sanxing_map` | 刑 | 事件 |
| `branch_harm_map` | 害 | 事件 |
| `branch_he_map` | 六合 | 事件 / 合局 |
| `branch_sanhe_map` | 三合 | 事件 / 合局 |
| `kong_wang` | 空亡 | 旺衰 / 事件 |
| `luck_pillars` | 大运 | **不进入 V1 命局五域（独立大运域，未来单独裁决）** |

### 硬边界（User 追加，锁定）

> **"进 Feature" 不等于 "所有域都能读取"。**

```text
five_element_balance → WANGSHUAI Feature → WANGSHUAI Rule   ✅
five_element_balance → 所有 Judgment Rule 随便读             ❌ 禁止
```

**Feature Resolver 必须产生「域隔离后的 Feature View」**：每个 Domain Feature 只暴露本域允许读取的 Canonical Fact 子集，各域 Rule 只读自己域的 Feature，**不读 raw 巨型 dict**。这既修 N-2（build_context 缺口），又防止 ZiPing 从 `Bazi→ZiPing` 退化成 `BaziCanonical→巨型 Context→所有规则随便读`。

---

## 4. D-1：PipelineResult 契约【LOCKED】

**PipelineResult 不挂完整 `JudgmentSynthesis`。** 只提供：

```text
ziping:
    engine_status        # CONNECTED | DEGRADED | NOT_CONNECTED | FAILED
    (机器可读状态元数据)
```

**但 User 加码（锁定）**：单有模糊 `engine_status` 不够。内部必须保留 **5 域 Domain Status**：

```text
WANGSHUAI / GEJU / YONGSHEN / SHISHEN / SHIJIAN
```

这些 **属于 ZiPingJudgmentStage 内部结果（随 JudgmentSynthesis 走），不塞进 PipelineResult**。职责分离：

```text
PipelineResult.ziping.engine_status  → 负责生产状态（给 API/用户）
JudgmentSynthesis.domain_statuses     → 负责辨层内部诊断（给审计/回放）
```

**职责不混。** 完整 Synthesis 永不挂 PipelineResult（避免 H-3 双通道再犯），只有轻字段上 API。

---

## 5. D-2：Judgment → AtomicClaim 规范转换契约【LOCKED】

**转换权归属（唯一）**：新建 `JudgmentClaimComposer`，**唯一**可产出 judgment 派生 claims 的模块。**禁止各 Domain 自行 append claim 到 SIR。**

### ① UNKNOWN 不产生确定性 Claim【硬规则，锁定】

```text
EXECUTED + 有明确结论  → 可产生 Claim
UNKNOWN               → 不产生确定性 Claim
NOT_EXECUTED          → 不产生 Claim
FAILED                → 不产生 Claim
```

若未来产品需告知用户"该域资料不足"，这是 **状态信息（进 engine_status/domain_status）**，**不是占位式判断 claim**。杜绝"假判断"。

### ② 链 A 旧 ZI_PING claims 不与 Judgment 重复【锁定】

最终生产架构中：**ZiPing Judgment 是 ZiPing 生产判断的唯一权威来源。** 禁止：

```text
Chain A: ZI_PING claim   +   Chain B: ZiPing Judgment claim   →  两者都进 SIR（双轨 ❌）
```

**后续实施必须审计并处理现有 Chain-A `ZI_PING` claims 的身份**（H 回放已见 3 条 `source_layers=ZI_PING` 的链A授权 claims）。若它们只是旧授权 assertion / 占位信号，**明确降级或移除其作为 ZiPing 最终判断 claim 的身份**。这是 D-2 的强制子任务（列入 §8 实施任务）。

### ③ `composer_version` 必须存在【锁定，审计 provenance】

每个 judgment 派生 claim 携带 `composer_version`：

```text
claim_id（确定性命名空间 ZC-{domain}-{conclusion}，H-4 可回放，禁 uuid）
  + rule_refs / evidence_refs（原样透传 ⑮-2 P0 已实活的 DTS-102/SMTH-102/E-DTS-105-001）
  + source_layers = [ZI_PING]
  + domain 标签
  + composer_version（哪个 Judgment→Claim 映射契约生成）
```

**这是审计 provenance，不是装饰字段。** 理由：Rule / Evidence / Composer 未来都会演进，必须可追溯"这条 claim 由哪版映射契约生成"。

---

## 6. D-5：Event-Signal 来源【LOCKED = 不重开整个 ⑮-1，新增 ⑮-1-EVENT-SIGNAL 方法审查】

**User 修正（锁定）**：event_signals 派生可以做，但**不因此把整个 ⑮-1 打回重审**。

```text
⑮-1 自身方法 → 保持 CLOSED 🔒
新增 ⑮-1-EVENT-SIGNAL 子项 / P1 方法审查 → 专审：
   branch_clash_map / branch_sanxing_map / branch_harm_map /
   branch_he_map / branch_sanhe_map / kong_wang
        ↓
   event_type mapping
        ↓
   SHIJIAN
```

必须先证明每一跳都有依据：

```text
Canonical Fact → Event Feature → Event Type → SHIJIAN Rule
```

**Feature 派生可以确定性实现，但 Event Type 的"命理语义"必须先经独立方法审计。** 在此之前：

- SHIJIAN **不得**因为"有冲/刑/害"就自动生成**未经依据**的事件结论；
- 禁止 BOT 自己创造未经审计的语义映射（例 `冲=婚姻事件 / 刑=官非事件 / 害=小人事件` 一律不得无依据落地）。

> 结论：⑮-1-EVENT-SIGNAL 是 **P1 方法审查项**，不是 ⑮-1 重开。审查通过前，event_signals 可产出 Feature，但 SHIJIAN 域结论 fail-closed。

---

## 7. D-6 / D-7：状态模型与失败语义【LOCKED】

### D-6：有条件重开 ⑮-2 —— 仅重开 Judgment State Semantics 基线

```text
⑮-2 CLOSED → 有条件 REOPEN（不推翻整个 ⑮-2，只重开状态语义）
锁定 JudgmentStatus（域级语义维度）：
   EXECUTED      = 已执行且得到结论
       ├─ ESTABLISHED
       └─ PARTIAL
   UNKNOWN       = 已执行，但无法得出可靠结论
   NOT_EXECUTED  = 根本没有执行
```

### D-6 加码（User 补刀，锁定）：FAILED 首先是 Stage/Engine 执行态，不是 DomainStatus

**两套状态维度，禁止合并成一个枚举：**

```text
EngineStatus（Stage / Engine 执行维度）:
   CONNECTED / DEGRADED / NOT_CONNECTED / FAILED

JudgmentStatus（域级判断语义维度）:
   EXECUTED / UNKNOWN / NOT_EXECUTED
```

两维度正交：一个 Stage 可以 `CONNECTED` 但某域 `UNKNOWN`；一个域可以 `NOT_EXECUTED` 而 Stage 整体 `DEGRADED`。**不得合成单枚举。**

### D-7：EngineStatus 4 态语义【锁定】

```text
CONNECTED     Stage 正常运行 + 核心域 EXECUTED        → 可产生 ZP claims
DEGRADED      Stage 已运行 + 存在 UNKNOWN/NOT_EXECUTED → 只输出"实际 EXECUTED 域"的合法 claims, status = PARTIAL
NOT_CONNECTED Stage 根本没接入                        → 0 ZP claims
FAILED        Stage 执行异常                          → 0 ZP claims
```

**核心硬规则（fail-closed，锁定）：**

```text
只有 CONNECTED / DEGRADED 允许产生 ZiPing Claim；
DEGRADED 只能产生"实际 EXECUTED 域"的 claim；
NOT_CONNECTED / FAILED → 0 ZP claims。
```

**两条禁行（直接关闭 F-7/G-5 语义假成功）：**

```text
SHISHEN = UNKNOWN  →  AI 帮忙补一个结论          ❌ 禁止
NOT_CONNECTED      →  Chain A 有 ZI_PING 标签      ❌ 禁止假装 ZiPing 已执行
                      就声称 ZiPing 已参与
```

输出侧 5 态可辨：`SUCCESS / PARTIAL / INSUFFICIENT / UNKNOWN / ENGINE_NOT_CONNECTED`。

### P0-2 定性（锁定）

P0-2 **不是**局部把 `has_core_judgment` 的 `is not None` 改成 `!= UNKNOWN`。而是随 D-6/D-7 做 **Judgment State Model 重构**：

```text
has_core_judgment → 三核心域（wangshuai/geju/yongshen）全部 == EXECUTED
                   （UNKNOWN 不算完成，NOT_EXECUTED 更不算）
G-1 降级态（异常→仅 wangshuai=UNKNOWN，其余 4 域 None）→ has_core = False（fail-closed，不再误报 True）
```

同时消掉 ⑮-3 P2 "SHISHEN/SHIJIAN None vs UNKNOWN 语义"项：None=NOT_EXECUTED、UNKNOWN=判不出，语义分开。

---

## 8. BOT-ZIPING 实施任务拆解【仅登记，禁止执行；待 User 单独授权】

> ⚠️ 本节是**实施边界清单，不是实施令**。任何 BOT 在 User 授权前**不得**改代码、
> Evidence、Rule ID、⑮-0/⑮-1/⑮-2 CLOSED 项。顺序依赖见 §9。

### A. 前置（架构/契约锁定后、Stage 实施前）

| 任务 ID | 内容 | 归属 | 状态 |
|---|---|---|---|
| ZIP-PRE-01 | ⑮-1-EVENT-SIGNAL 方法审查：branch maps → event_type 映射依据审计（⑮-1 保持 CLOSED，新增 P1 子项） | User 裁决 + BOT-ZIPING 审计 | 登记 / 未执行 |
| ZIP-PRE-02 | ⑮-2-P1-Sub loading boundary（C-2a Loader 递归/可见性：五经子目录对生产 RuleLoader 不可见） | BOT-ZIPING（代码项，契约锁定后） | 登记 / 未执行 |
| ZIP-PRE-03 | DTS-106 PROVENANCE-BLOCKED 裁决（补古典证据 / 撤规则 / 标 ENGINEERING-DEFINED 三选一） | **User 单独裁决** | 登记 / 未裁决 |
| ZIP-PRE-04 | C-2c G1 读 `verification_status`（pending 与 verified 生产等价放行 → 入 G1） | BOT-ZIPING（独立 P1，与 P0-1 解耦） | 登记 / 未执行 |

### B. P0-1 实施（前置完成后）

| 任务 ID | 内容 | 对应决策 | 状态 |
|---|---|---|---|
| ZIP-INT-01 | 新增 ZiPingJudgmentStage（辨层，入口 `require_factory=True`） | D-3/D-1，修 N-1 | 登记 / 未执行 |
| ZIP-INT-02 | Feature Resolver：域隔离 Feature View（命局 8 字段按域切分，luck_pillars 不进 V1） | D-4，修 N-2 | 登记 / 未执行 |
| ZIP-INT-03 | `build_context` 重定义为正式 Feature/Context Contract（不再取 4柱+日主裸 dict） | D-4/N-2 | 登记 / 未执行 |
| ZIP-INT-04 | `signals_by_domain` 接入：event_signals 由 ⑮-1-EVENT-SIGNAL 审计后确定性派生（未审计前 SHIJIAN fail-closed） | D-5，修 C-2 | 登记 / 未执行 |
| ZIP-INT-05 | 唯一 `JudgmentClaimComposer` + `composer_version` + 确定性 `ZC-{domain}-{conclusion}` 命名 | D-2 | 登记 / 未执行 |
| ZIP-INT-06 | 4a 拆分 ComputeStage（`run_compute` + `compose_sir`），SIR 定稿移到 Judgment 之后 | D-3 4a | 登记 / 未执行 |
| ZIP-INT-07 | PipelineResult 增加 `ziping.engine_status`（**不**挂完整 Synthesis；Domain Status 留 Stage 内部） | D-1 | 登记 / 未执行 |
| ZIP-INT-08 | 链 A 旧 `ZI_PING` claims 审计处理（降级/移除其作为 ZiPing 最终判断 claim 身份） | D-2② | 登记 / 未执行 |

### C. P0-2 实施（状态模型，与 P0-1 同批或单独授权）

| 任务 ID | 内容 | 对应决策 | 状态 |
|---|---|---|---|
| ZIP-STATE-01 | `JudgmentStatus`（EXECUTED/UNKNOWN/NOT_EXECUTED）+ `EngineStatus`（4 态）两套正交枚举落地 | D-6 | 登记 / 未执行 |
| ZIP-STATE-02 | `has_core_judgment` 重构为"三核心域全 EXECUTED" | D-6/P0-2 | 登记 / 未执行 |
| ZIP-STATE-03 | D-7 fail-closed 硬规则：仅 CONNECTED/DEGRADED 出 claim；DEGRADED 只出实际 EXECUTED 域；NOT_CONNECTED/FAILED=0 claim | D-7 | 登记 / 未执行 |

---

## 9. 实施顺序（锁定，覆盖 15.6b 上一轮"先修 Loader"判断）

```text
① 本 15.6c 定死 D-1～D-7 契约        ← 现在（架构封版）
② 前置 ZIP-PRE-01~04（⑮-1-EVENT 审计 / ⑮-2 loading / DTS-106 / C-2c）
③ P0-1 实施 ZIP-INT-01~08（enable_ziping_claims 开关；默认 ON 前须 G1 全解析）
④ P0-2 实施 ZIP-STATE-01~03
⑤ E8 确定性回放 → Production Admission
```

**关键（User 纠正，锁定）**：先锁契约（本文件），再动 ⑮-2 Loader；**不得**为当前孤立 Judgment 的引用结构反向改基础设施后再返工。

---

## 10. 冻结项（本架构裁决生效后维持）

```text
Bazi ①–⑭ CLOSED 🔒
Canonical ⑭ FROZEN 🔒
⑮-0 接入契约 CLOSED 🔒
⑮-1 自身方法 CLOSED 🔒（仅新增 ⑮-1-EVENT-SIGNAL P1 子项，⑮-1 本体不回改）
⑮-2 P0 CLOSED 🔒 / ⑮-2 Judgment State Semantics 基线 有条件 REOPEN（仅状态语义，不推翻 ⑮-2 P0）
⑮-2-P1-Sub Audit CLOSED / Provenance OPEN / Admission BLOCKED
⑮-3 A~H + 15.6b 反向审计 CLOSED 🔒
本 15.6c 架构 DRAFT 升 LOCKED（D-1～D-7）
Golden expected values 不动
Basis: 415 PASS 基线 + Dual-Track 44/44
```

---

## 11. 核心结论

> **P0-1 锁定 B + 4a：独立 ZiPingJudgmentStage 负责辨层，SIR 定稿移到 Judgment 之后，唯一 JudgmentClaimComposer 进 SIR，G1 保持唯一生产 Evidence Gate。**
>
> **P0-2 锁定为状态模型重构（非局部 is not None 补丁）：JudgmentStatus / EngineStatus 两套正交维度，has_core_judgment = 三核心域全 EXECUTED。**
>
> **两条硬边界（User 追加）：① Feature View 域隔离，"进 Feature ≠ 全域可读"；② UNKNOWN/NOT_EXECUTED/FAILED 不出确定性 claim，杜绝 AI 补判断与 Chain A ZI_PING 标签冒充 ZiPing 已执行。**
>
> 本记录 **Code/Evidence/Rule/Algorithm Change = 0**。所有实施任务已拆解并**登记为未执行**，**待 User 审阅本 15.6c 后单独下达实施授权**。在此之前，任何 BOT 不得改代码、Evidence、Rule ID 或 ⑮-0/⑮-1/⑮-2 CLOSED 项。

---

*Generated by BOT-MASTER on 2026-09-10*
*Code change: 0 | Evidence change: 0 | Rule change: 0 | Algorithm change: 0*
*Files modified: 1 (this architecture arbitration record only)*
*取证基线：git show 40eeb359 / 48e66f6c / ab7a9574 / 0e395996 已提交版本，非工作区。*
