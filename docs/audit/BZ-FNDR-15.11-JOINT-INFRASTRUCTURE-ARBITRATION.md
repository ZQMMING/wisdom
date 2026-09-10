# ②③ 联合基础设施裁决记录（BZ-FNDR-15.11）

> **BZ-FNDR-15.11：②-C / C1a + ③ V3+V4 联合 Evidence Infrastructure 锁定**
> **Audit / Ruling Record Only — Code = 0 / Evidence = 0 / Rule = 0 / Algorithm = 0**
>
> 本记录是 **联合裁决登记（Joint Arbitration Record）**，不是实施。
> 依据：15.10 双树对账（`f89b2166`）+ User 2026-09-10 两次落槌（③ V3+V4 → ②-C1a）。
> 执行：BOT-MASTER（User 授权接管 BOT-ZIPING 前置任务）。

---

## 0. 记录元数据

| 项 | 值 |
|---|---|
| 记录 ID | BZ-FNDR-15.11 |
| 前置 | 15.9（`7928e1e8`）/ 15.10（`f89b2166`） |
| ② 裁决 | **②-C（Evidence Index）+ ②-C1c（双树对账先行）→ C1a（树B 为 Corpus Base）** |
| ③ 裁决 | **V3（分级放行 + provenance 标记）+ V4（与 Loader/Index 联动）** |
| 否决项 | ②-A（rglob 树A）/ ②-B（注册清单）/ ②-C1b（双树并行）/ ③-V1（现状）/ ③-V2（全 BLOCK pending） |
| G1 | **不修改**（唯一生产 Gate 原则不变） |
| ZIP-INT-01~08 | 🔴 未授权 |
| 本地 commits | 5 ahead origin/main（a719bc53 / 14b0b313 / a6933e9b / 7928e1e8 / f89b2166）**不推**，本记录为第 6 个 |

---

## 1. ② 正式架构锁定（C1a）

### 1.1 语料基准树

```text
data/evidence/          ← Evidence Corpus Base（唯一语料事实来源）
       ↓
Evidence Index（Stable Resource ID + Logical URI + 相对路径 + Runtime Resolver）
       ↓
Production Resolver → G1
```

```text
backend/data/evidence/  → 降级为 Legacy / Production Visibility Snapshot
                         不再是 Evidence Corpus 的事实来源
```

### 1.2 C1a 裁决依据（15.10 对账数据，User 复核认可）

| 判断项 | 结果 | 裁决 |
|---|---|---|
| 语料完整性 | B-only 4106（合规率 99.85%） | B 明显更完整 |
| 共有 ID | 1562，0 冲突 | 稳定 |
| 同 ID drift | 72，**全部为 B 侧 blind_seg 核验信息单向增量**（0 条 A→B 改写） | 无"错误覆盖"证据 |
| A 独有 | 仅 1（E-DTS-145-001） | 见 §4 Q2 |
| Schema 合规 | B 4240 vs A 141 | B 明显占优 |
| Provenance | 共有项 vs_top/vs_cit/路径 0 差异 | 可治理 |
| 时间 | B 末改 09-09 > A 09-06 | B 更新 |

### 1.3 禁止项（永久性边界）

```text
❌ backend/data/evidence → rglob → 生产 Evidence Truth
❌ 目录扫描本身作为证据事实来源
❌ 以"树B 更新"为由跳过 Q1/Q2 直接覆盖
```

### 1.4 Index 契约（实施设计阶段执行，本记录只锁方向）

```text
Stable Resource ID
  + Logical URI
  + Project-relative Path
  + Runtime Resolver
  + Provenance Resolution
        →  生产 Loader 只消费 Index，不消费目录结构
```

**硬边界：`Stable Resource ID ≠ 文件系统路径`** —— 换机器/换 OS/仓库迁移/目录重定位，Resource Identity 不变。

---

## 2. ③ 正式规则锁定（V3 + V4）

### 2.1 分级放行表

| 状态 | G1 行为 | Claim 行为 |
|---|---|---|
| `verified` | ✅ PASS | 正常证据权威 |
| `cross_verified` | ✅ PASS | 正常证据权威 + 保留交叉核验标识 |
| `pending_verification` | ✅ 放行 | **必须携带 `PROVENANCE-PENDING`** |
| `UNVERIFIED` | ✅ 放行 | **必须携带 `PROVENANCE-PENDING`** |
| 缺失 | ⚠️ 放行但必须显式标记 | **不得伪装成已核验** |
| `not_applicable` | ✅ 放行 | 标记相应非核验/工程语义 |
| `disputed` | ❌ BLOCK | 不得产生生产 Claim |
| 未知/非法值 | ❌ BLOCK | 不得产生生产 Claim |

### 2.2 核心架构限制（User 原文锁定）

> **"可放行" ≠ "证据已证明"。**
> G1 允许 provenance 不完整的资源参与生产链，但 Claim 必须携带对应 provenance 状态；
> **不能因为 Claim 最终通过 G1，就把 `pending` 自动升级成 `verified`。**

### 2.3 两套字段不合并（15.9 §④ 坐实的分层原则）

```text
顶层 verification_status        ≠  citation.verification_status

后续在 Evidence Index / Resolver 中建立:
raw_extraction_status
+ citation_verification_status
+ authority_type
+ source_layer
        ↓
Resolved Provenance

⇒ 原始状态保留，解析后的生产状态另行计算。
   旧批次的 UNVERIFIED 不得污染正式核验语义。
```

### 2.4 DTS-106 联动链（与 15.7 §4 ENGINEERING-DEFINED 一致）

```text
DTS-106
  → authority_type = ENGINEERING_DEFINED
  → verification_status = pending
  → Claim（AC-ZP-*）
  → PROVENANCE-PENDING + ENGINEERING-DEFINED
  → G1

Claim 的 namespace 仍然是 AC-ZP-*，绝不改变 authority。与 X-1a 完全一致。
```

### 2.5 大小写归一（15.9 §⑦ 登记的实施前置）

```text
PENDING_VERIFICATION ≡ pending_verification
SOURCE_VERIFICATION_REQUIRED / CASE_SOURCE_VERIFICATION_REQUIRED → 归入 PENDING 系
（归一化发生在 Resolved Provenance 计算层，不改原始资源文件 —— Evidence Change = 0）
```

---

## 3. 联合 Evidence Infrastructure 目标结构（②③ 同一契约）

```text
                  ┌──────────────────────┐
                  │  Evidence Corpus B   │
                  │  data/evidence/      │
                  └──────────┬───────────┘
                             ↓
                    Evidence Index
                             ↓
             ┌───────────────┴──────────────┐
             │                              │
       Resource Identity              Provenance
       Stable ID                      authority_type
       Logical URI                    verification_status
       Relative Path                  source_layer
             │                              │
             └───────────────┬──────────────┘
                             ↓
                    Runtime Resolver
                             ↓
                   JudgmentClaimComposer
                             ↓
                         AC-ZP-*
                             ↓
                           G1
```

**分工边界（三者不互相冒充）：**

- **②** 解决"什么资源是真正可见的、身份是什么、从哪里解析"；
- **③** 解决"这个资源的核验状态和权威性质是什么"；
- **G1** 负责最终 Claim Gate。

### 3.1 六大锁定原则（User 原文，永久边界）

```text
1. Corpus ≠ Production admissibility
2. Resource ID ≠ filesystem path
3. Resource visibility ≠ authority
4. verification_status ≠ authority_type
5. G1 PASS ≠ classical proof
6. pending ≠ verified
```

---

## 4. Q1 / Q2 / Q3 处理边界（本记录逐项锁死）

### Q1 — 12 组同 ID 多文件（Evidence Identity Contract）

```text
裁决: 暂不修改证据 ID。
Index 必须表达:
  Resource ID + Logical URI → 唯一资源实例
  （same evidence_id ≠ same resource instance）
⇒ 进入后续 Index 实施设计（属于 ②-C 契约的一部分，非独立授权）。
```

**子项 Q1-i（ID declaration integrity，较严重）**：

```text
COMPLEX_WORK-002 文件内 evidence_id 字段 = WORK_METHOD-004（ID 错配）
  ❌ 禁止在 Loader/Index 实施阶段"偷偷修正"
  ✅ 进入 Evidence Identity Audit / remediation 清单
  ✅ 由证据变更门单独授权后处理
```

### Q2 — E-DTS-145-001（唯一 A-only）

```text
裁决: 暂不授权补入树B。
理由: 架构裁决阶段不为"Corpus Base 看起来完整"夹带 Evidence Change。
处置: 进入 Evidence Change 待授权项。
      未来若确认它是 Corpus Base 必须保留的唯一 A-only canonical resource，
      再单独授权一次 Evidence Change（1 条资源，独立 commit）。
```

### Q3 — 1440 条 schema 不合规

```text
裁决: 不因 C1a 强行修。
处置: 进入 Schema / Provenance remediation（另行治理）。
      禁止路径: schema 不合规 → 删除资源。
      原则依据: Corpus completeness ≠ production admissibility
      （与 ③ V3 分级放行 + 显式标记 对齐）。
```

---

## 5. 当前门状态（本记录封档时点）

```text
① Event-Signal           ☐ 最后一项待裁决
② Evidence Loader        🔒 ②-C + C1c ✅ + C1a
③ verification_status    🔒 V3 + V4
────────────────────────────
G1                       🔒 不修改
ZIP-INT-01~08            🔴 未授权（①裁完后三门全封口，再出实施任务单）
本地 commits              5 ahead + 本记录 = 6 ahead，全部不推
```

---

## 6. 边界与冻结

```text
✅ 本记录 0 代码 / 0 evidence / 0 rule / 0 algorithm 改动
✅ 未开始 Evidence Index 实施（User 指令：先本记录，后 ①，三门封口后才授权施工）
✅ 15.6c / 15.7 / 15.8 / 15.9 / 15.10 不回改
✅ 数字引用以 15.9（verification_status 盘）+ 15.10（双树对账）为准
✅ a719bc53 / 14b0b313 / a6933e9b / 7928e1e8 / f89b2166 / 本 commit 全部本地不推
```

*Generated by BOT-MASTER on 2026-09-10*
*Code: 0 | Evidence: 0 | Rule: 0 | Algorithm: 0 — single-file joint arbitration record*
