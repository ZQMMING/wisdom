# X-1 裁决登记 + 实施门锁定记录（BZ-FNDR-15.8）

> **BZ-FNDR-15.8：X-1a 裁决 + G1 不修改 + 三个基础设施待裁项 + 本地远端状态锁定**
> **Code / Evidence / Rule / Algorithm Change = 0**
>
> 本 commit 是 **裁决登记记录（Ruling Record），不是实施，也不是新审计**。
> 记录 2026-09-10 User 三项落槌，锁死实施门；把 ②③ 两个基础设施裁决**不预设、只列事实/代价/依赖**供 User 独立拍板。

---

## 0. 记录元数据

| 项 | 值 |
|---|---|
| 记录 ID | BZ-FNDR-15.8 |
| 前置记录 | 15.6c（`a719bc53`）→ 15.7（`14b0b313`） |
| 本次记录 commit | 本地待归档（Code/Evidence/Rule/Algorithm Change = 0） |
| 执行者 | BOT-MASTER（裁决记录） |
| **Git push** | **暂不推**（User 2026-09-10 口径：本地存在 ≠ GitHub 已验证） |

---

## 1. X-1 裁决：Claim namespace 锁定 = X-1a

**User 落槌（锁定）**：

```text
AC-ZP-{domain}-{conclusion}     ← ZiPing 派生 Claim 的 claim_id 命名空间
不修改 G1
```

**理由（User，锁定）**：15.6c 原则 = G1 作为**唯一生产 Gate**，不为新 ZiPing Claim 反向扩展已冻结的 Gate。

**逐条登记**：

| 项 | 裁决 | 说明 |
|---|---|---|
| `AC-*` | 保持 G1 唯一合法 Claim namespace | G1 L44 `startswith("AC-")` 校验不动 |
| `AC-ZP-{domain}-{conclusion}` | ZiPing 域/来源区分 | 确定性、可回放（H-4） |
| `composer_version` | 负责转换契约版本 | 记录在 claim（15.6c §5③） |
| `ZC-*` | **不采用** | 会与 G1 `AC-*` 硬校验全量 BLOCK（15.7 §5 X-1） |
| X-1b（G1 白名单扩展 AC-*/ZC-*） | **不采用** | G1 是 ⑮-3 冻结面，不反向扩展 |
| 15.6c 正文 | **不推翻** | 仅在 15.7/后续实施记录登记 **namespace correction**（ZC-* → AC-ZP-*） |

### 追加硬规则（User 加码，锁定）

> **`AC-ZP-*` 只是 Claim ID namespace，不是 source authority。**

```text
AC-ZP-WANGSHUAI-xxx  ≠  已具备 Evidence 权威
```

权威仍由下列字段决定，**不随 namespace 自动升级**：

```text
source_layer
rule_refs
evidence_refs
G1
```

即：一条 `AC-ZP-*` claim 若其 `evidence_refs` 指向的 evidence 是 `ENGINEERING-DEFINED`（如 DTS-106）或 `pending_verification`，**不得因它是 ZiPing 派生 claim 就假装经典权威**。权威判定链保持：`evidence_refs → evidence.resource(authority_type/verification_status) → G1`。

---

## 2. 本地 / 远端状态锁定（User 口径）

User 从 GitHub 公开端核验 `a719bc53`、`14b0b313` 均未形成可验证公开记录 → 按治理原则：

```text
本地存在 ≠ GitHub 已验证
```

**锁定**：

```text
a719bc53  (15.6c)   本地
      ↓
14b0b313  (15.7)    本地
      ↓
本 15.8 commit       本地
      ↓
origin/main          暂不推进（不 push）
```

正式进入远端审计链时，**一次性推送 + 立即从 GitHub 反向核验**：

```text
commit SHA → parent → changed files → diff
→ Code/Evidence/Rule/Algorithm Change = 0
→ 15.6c / 15.7 / 15.8 内容完整性
```

---

## 3. 当前状态总表（User 锁定的锁定面）

| 项目 | 状态 |
|---|---|
| 15.6c 架构裁决（D-1~D-7） | 🔒 LOCKED |
| 15.7 前置审查 | 🔒 LOCKED |
| X-1 Claim namespace | 🔒 **X-1a = `AC-ZP-*`，G1 不修改** |
| G1 | 🔒 不修改（唯一生产 Gate） |
| ⑮-1 本体 | 🔒 CLOSED |
| Event-Signal | 🟠 依据未证明，**SHIJIAN fail-closed** |
| ⑮-2 状态语义 | 🟠 条件 REOPEN（仅 Judgment State Semantics） |
| Loader（ZIP-PRE-02） | 🟠 策略待最终实施设计（本文 §4②，**未拍板**） |
| G1 verification_status（ZIP-PRE-04） | 🟠 独立 P1（本文 §4③，**未拍板**） |
| DTS-106 | 🟠 **ENGINEERING-DEFINED**（15.7 §4 S1-S8 登记，不再作为实施门重议） |
| ZIP-INT-01~08 | 🔴 **未授权** |
| GitHub push | 🔴 **暂不允许** |

---

## 4. 三个基础设施实施门（User 未拍板，本文只列事实/代价/依赖，不预设选择）

> ⚠️ 这三项**在锁死前，ZIP-INT-01~08 维持未授权**。
> BOT-MASTER 不替 User 拍板基础设施行为，只做裁决支持（事实 + 代价 + 依赖 + 我的倾向，倾向可被否决）。

### ① ZIP-PRE-01 — Event-Signal

**User 倾向**：暂不创造映射；SHIJIAN fail-closed；待定是否建立独立事件方法证据链。

| 事实 | 15.7 §1 已坐实：生产 `event_types` 恒空；全仓唯一 event_type 生产方 = BLIND 引擎（异引擎，不得挪用）；数据层 0 处支关系→event 映射；⑮-1 未覆盖 event |
|---|---|
| 代价（暂不创造映射） | SHIJIAN 域在 ZiPingJudgmentStage 内 fail-closed（缺 event_signals → 不产 EVENT_EXIST）；V1 事件域基本不可用 |
| 代价（建独立事件证据链） | 需 ⑮-1-EVENT-SIGNAL 依据级方法审计（canonical→event feature→event type→SHIJIAN rule 每跳有依据），新增工作量大 |
| 依赖 | 决定是否给 SHIJIAN 出「降级为事件域 NOT_EXECUTED」还是「保留 EVENT_ABSENT 语义但标注依据缺失」 |
| BOT-MASTER 倾向（可否决） | V1 先 fail-closed + 标注，事件证据链作为独立 P1 里程碑另批 |

### ② ZIP-PRE-02 — Evidence Loader 策略

**User 倾向**：**C（Evidence Index）**；但明确**单独裁决，不顺手塞进 X-1**。

| 方案 | 事实/机制 | 代价 | 依赖/风险 |
|---|---|---|---|
| A. `rglob()` | 直接递归扫全部子目录 | 最小改动；但**把目录结构重新变成事实来源**（结构一变即失效，且 1503 资源全量进 Loader） | 与「稳定 Resource ID / 可迁移」长期审计原则冲突 |
| B. 显式注册清单 | 维护「哪些子目录/evidence 可见」清单 | 可控；但清单本身成新事实来源，需治理 | 清单漂移、遗漏风险 |
| C. **Evidence Index**（User 倾向） | 稳定 Resource ID / Logical URI / 相对路径 / Runtime Resolver / 可迁移索引 | 与顺天既有长期审计原则一致；**改动最大**（索引生成 + resolver + 迁移） | 需与 P0 红线「路径独立性」对齐（无硬编码绝对路径）；工程量在三项中最高 |

> 本文**不替 User 选**。锁定后，Loader 实施才并入 BOT-ZIPING 任务单。

### ③ ZIP-PRE-04 — G1 与 `verification_status`

**User 明确**：不能简单「全部 pending 就 BLOCK」；`verification_status` 体系需先与既有 Evidence provenance contract 对齐，是**独立架构点**。

| 事实 | 15.7 §3 已坐实：G1 全函数 5 校验面 0 读 `verification_status`/`source_layer` → pending 与 verified 生产等价放行 |
|---|---|
| 为什么不能「pending 全 BLOCK」 | 现有 evidence 的 `verification_status` 取值体系（`pending_verification` / `verified` / `UNVERIFIED` 等）尚未与 Evidence provenance contract 统一；直接全 BLOCK 会误伤大量 legitimate 资源 |
| 需先对齐 | `verification_status` 的取值语义 + 与 `authority_type`（CLASSICAL-PROVEN / ENGINEERING-DEFINED / PARTIAL / PROVENANCE-BLOCKED）的映射关系 |
| 可能的 Gate 形态（供裁决，非预设） | (a) pending → 该 claim 标 `PROVENANCE-PENDING` 而非 BLOCK；(b) 仅对 ENGINEERING-DEFINED/PARTIAL 资源做分级放行；(c) 与 ② Loader 策略联动（可见性 + 分级同批） |
| 依赖 | 与 ②（Loader 可见哪些 evidence）强耦合；建议 ②③ 同批裁决 |
| BOT-MASTER 倾向（可否决） | ②③ 合并成一次「Evidence 生产可见性 + 分级 Gate」裁决，避免两次返工 |

---

## 5. 最终实施门（更新）

```text
ZIP-INT-01~08 授权前置条件（全部满足才开工）:
  ☑ X-1 裁决 = X-1a（AC-ZP-*，G1 不修改）        ← 本次锁死
  ☑ DTS-106 = ENGINEERING-DEFINED（S1-S8）          ← 15.7 已登记，不再重议
  ☐ ① Event-Signal：fail-closed 确认 / 是否建事件证据链   ← 待 User
  ☐ ② Loader：A / B / C（User 倾向 C，单独裁决）          ← 待 User
  ☐ ③ G1 verification_status 分级策略（与 ② 联动）        ← 待 User
  ☐ 15.6c 基线（a719bc53）保持未变
⇒ 当前：ZIP-INT-01~08 维持未授权。①②③ 未锁死前，任何 BOT 不得边审边改。
```

---

## 6. 边界记录

```text
✅ 0 代码 / 0 evidence / 0 rule / 0 algorithm 改动
✅ X-1a 只改 claim namespace 命名约定（记录层），G1 / judgment.py / _rule_backends.py 未动
✅ 15.6c / 15.7 正文不回改（namespace correction 以本记录 §1 为注记）
✅ a719bc53 / 14b0b313 / 本 commit 全部保持本地不推（User 口径）
✅ 工作区未提交 ⑮ 整改代码未进入本 commit
```

*Generated by BOT-MASTER on 2026-09-10*
*Code change: 0 | Evidence change: 0 | Rule change: 0 | Algorithm change: 0*
*Files modified: 1 (this ruling record only)*
