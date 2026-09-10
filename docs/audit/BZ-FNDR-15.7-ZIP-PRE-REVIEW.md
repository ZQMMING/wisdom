# ZIP-PRE 前置审查记录（BZ-FNDR-15.7）

> **BZ-FNDR-15.7：ZIP-PRE-01 / 02 / 04 / 03(DTS-106) 前置审查 —— 审计与登记，不施工**
> **Code / Evidence / Rule / Algorithm Change = 0**
>
> 本 commit 是 **前置审查记录（Pre-Implementation Review Record），不是实施任务单，更不是实施**。
> 执行者：BOT-MASTER（User 2026-09-10 授权"替代 BOT-ZIPING 完成 ZIP-PRE 前置审查"）。
> 审查对象：`a719bc53`（15.6c 架构裁决记录）§8 登记的 ZIP-PRE 任务。
> 取证基线：`git show HEAD(<ab7a9574 链>0e395996 a719bc53):<path>` 已提交版本 + 数据资源文件，非工作区。
> **顺序（User 锁定）**：ZIP-PRE-01 → ZIP-PRE-02 → ZIP-PRE-04 → DTS-106 工程登记 → **之后才授权 ZIP-INT-01~08（当前未授权）**。

---

## 0. 审查元数据

| 项 | 值 |
|---|---|
| 审查 ID | BZ-FNDR-15.7 |
| 前置记录 | 15.6c（`a719bc53`，D-1~D-7 LOCKED，本地未推 GitHub） |
| Code / Evidence / Rule / Algorithm Change | **0 / 0 / 0 / 0** |
| 结论性质 | 4 项前置全部完成事实审查与登记；**0 项施工** |
| 新发现 | 1 项实施级冲突（X-1，见 §5），需 User 裁决 |
| Git push | 本记录**随 a719bc53 一并保持不推**（User 治理口径：本地已归档 ≠ 远端已验证） |

---

## 1. ZIP-PRE-01 — ⑮-1-EVENT-SIGNAL 方法审查（登记，未施工）

**任务**：证明 `branch_*_map / kong_wang → event_type → SHIJIAN Rule` 每一跳都有依据；无依据则 SHIJIAN fail-closed。

**取证（HEAD 已提交版）**：

| 检查点 | 事实 | 证据 |
|---|---|---|
| 生产链 event_types 生产方 | **恒空**：`signal_engine.py` L358 `event_types=[]`（信号工厂默认值，全 src 无第二生产点） | `git show HEAD:src/tongshu/reasoning/signal_engine.py` |
| SHIJIAN 域消费 | `judgment.py` L998 `event_signals = [s for s in signals if s.get("event_types")]` → 生产路径 0 event_signals → **恒产 `EVENT_ABSENT`**（与 15.6b C-2 一致） | `git show HEAD:src/tongshu/reasoning/judgment.py` L993-1011 |
| 全仓能产 event_type 的模块 | 仅 **BLIND 引擎**（`blind_bazi_engine.py` L506-592，WEALTH_GAIN/MARRIAGE_CHALLENGE 等 8 类）——异引擎，**非 ZiPing 方法**，不得作为 ZiPing 语义依据 | grep src/ --include=*.py |
| 数据层 ZiPing 支关系→事件映射 | **0 命中**：`data/rules/` 含 event 字样的规则（CRR-10x 流年 / EDU / HL 河洛健康）均非 ZiPing 支关系映射；五经 evidence 无 branch map→event_type 映射资源 | 数据层 grep + 逐目录核对 |
| ⑮-1 审计覆盖 | ⑮-1（BZ-FNDR-15.3，已 CLOSED）**审计范围不含 event-signal 派生**（档案 0 命中 event） | 15.3 档案 grep |

**审查结论（登记）**：

```text
⑮-1-EVENT-SIGNAL = AUDIT-COMPLETE / MAPPING-UNPROVEN（P1，未闭合）
   - Canonical Fact → Event Feature：Feature Resolver 可确定性实现（属于 15.6c D-4/D-5 的 ZIP-INT-02/04 范围）
   - Event Feature → event_type 命理语义：**0 依据**，五经资源中不存在"冲=婚姻事件 / 刑=官非事件"类映射
   - BLIND 引擎 8 类 event_type 属异引擎方法，不得挪用为 ZiPing 依据
   - ⑮-1 本体保持 CLOSED 🔒（User 裁决），本项为新增 P1 子项
⇒ 实施红线（登记）：event_type 映射未获独立方法审计（用户或 BOT-ZIPING 出具依据级审查）之前，
   SHIJIAN 域在 ZiPingJudgmentStage 内必须 fail-closed（不产 EVENT_EXIST；缺 event_signals 时
   依 15.6c D-6/D-7 归为 UNKNOWN/NOT_EXECUTED 语义，不得冒充"判了没事件"）。
```

---

## 2. ZIP-PRE-02 — ⑮-2-P1-Sub loading boundary（登记，未施工）

**任务**：生产 RuleLoader 可见性审计（C-2a：五经子目录对生产不可见）。

**取证（HEAD 已提交版 `_rule_backends.py`）**：

| 检查点 | 事实 | 证据 |
|---|---|---|
| 加载方式 | `glob("*.json")` **非递归**（rules 同）：`L57 rules_dir.glob("*.json")` / `L74 evidence_dir.glob("*.json")` | `git show HEAD:src/tongshu/reasoning/_rule_backends.py` |
| 生产可见 | 仅 `backend/data/evidence/` **根级** json | 同上 |
| 生产不可见规模（实测目录） | `qiong_tong_bao_jian 1233 / yuan_hai_zi_ping 119 / di_tian_sui 45 / blind_seg 86 / ziping_zhenquan 11 / san_ming_tong_hui 9` = **1503 个 evidence 资源对生产 RuleLoader 不可见**（blind_seg 86 属 BLIND 引擎，非 ZiPing 项） | `ls backend/data/evidence/*/` |
| 后果 | ⑮-2 已挂载的 YHZP/ZPZ/DTS-子目录 证据，**生产侧 G1 若解析 evidence_refs 将判 unresolved → BLOCK**（与 ⑮-3 C-2a/C-2b 一致，本次坐实规模数字） | 目录实测 + G1 源码 |

**审查结论（登记）**：

```text
ZIP-PRE-02 = AUDIT-COMPLETE / REMEDIATION-DEFINED-EXECUTION-PENDING
   - 事实：非递归 glob → 1503 个子目录证据生产不可见
   - 实施归属（15.6c §9 顺序②）：BOT-ZIPING 代码项 —— Loader 可见性策略
     （递归 rglob / 注册子目录清单 / evidence index）三选一由 User 裁决后出任务单
   - 红线（User 锁定）：契约（15.6c）锁定在先，Loader 实施在后；不得反向为孤立 Judgment 改基础设施
```

---

## 3. ZIP-PRE-04 — G1 verification_status 不入 Gate（登记，未施工）

**取证（HEAD 已提交版 `g1_evidence.py` L23-45 全函数）**：

G1 `evidence_gate()` 实际校验 5 项，逐项登记：

```text
① claims 非空
② 每 claim: rule_refs 非空
③ 每 claim: evidence_refs 非空 且 (传 evidence_ids 时) 全部可解析
④ 每 claim: source_layers 非空
⑤ 每 claim: claim_id 必须 startswith("AC-")   ← 本次新发现，见 §5 X-1
```

| 检查点 | 事实 |
|---|---|
| G1 是否读 `verification_status` | **0 命中**（全函数无 `verification` 字样） |
| G1 是否读 `source_layer`（资源层 classical_original/paraphrase） | **0 命中**（④ 读的是 claim 的 `source_layers` 枚举标签，非 evidence 资源的层） |
| 后果 | `pending_verification` 与 `verified`、`paraphrase` 与 `classical_original` 在 G1 **生产等价放行**（与 ⑮-3 C-2c 一致，本次坐实 G1 全函数校验面） |

**审查结论（登记）**：

```text
ZIP-PRE-04 = AUDIT-COMPLETE / REMEDIATION-DEFINED-EXECUTION-PENDING（独立 P1，与 P0-1 解耦，15.6c §8）
   - 实施形态（供 User 裁决，不预设）：G1 增加 verification_status 分档策略
     （pending → 该 claim 标记 PROVENANCE-PENDING 而非 BLOCK / 或按 15.6c 与 ⑮-2 基线对齐）
   - 与 DTS-106 登记的联动：DTS-106 的根级资源 verification_status=pending_verification，
     G1 现状下会静默放行 → X-2 登记项
```

---

## 4. DTS-106 ENGINEERING-DEFINED 工程规则登记（User 裁决③，登记，未施工）

**User 裁决原文要点（2026-09-10，本记录执行）**：
- DTS-106"月令被冲/围克→身弱"未达 CLASSICAL-PROVEN 门槛 → **正式登记为 `ENGINEERING-DEFINED`**；
- **不是**"找不到证据所以随便标"，而是"规则语义与经典证据不直接对应，保留规则但降权登记"；
- 不选①（补古文）：根级 paraphrase 与 di_tian_sui 资源均不直接支持该语义，且存在同 ID collision，补"看起来差不多"的证据会掩盖"证据不直接支持规则"的问题；
- 不选②（撤规则）："证据不足" ≠ "规则不存在"，工程规则保留待独立规则审查；
- 当前 **Code Change = 0**；真正实施时由 BOT-ZIPING 按 ENGINEERING-DEFINED 正式契约处理。

**取证（数据资源 + HEAD 代码挂载点，实施边界据此写死）**：

### 4.1 collision 双资源全文核对（实读）

```text
资源A  backend/data/evidence/E-DTS-106-001.json（根级，生产可见）
  source_layer = paraphrase / evidence_strength = secondary
  verification_status = pending_verification
  original_text = "生方怕动库宜开,败地逢冲仔细推。《滴天髓·通神论·衰旺》——月令被围克则得令不成立。"
  rule_refs = ["DTS-106"]
  → 该引文是否直接支撑"月令被冲→格有破损/身弱"：不直接（"败地逢冲仔细推"仅为谨慎性表述）

资源B  backend/data/evidence/di_tian_sui/E-DTS-106-001.json（子目录，生产不可见）
  source_layer = classical_original / passage_id = DTS_0010（任氏曰）
  verification_status = UNVERIFIED / authorization_level = PARTIAL
  原文主题 = "进退之机"（旺相休囚、进气退气论述）
  rule_refs = ["DTS-DTS"]          ← 资源自身绑定的是 DTS-DTS，不是 DTS-106
  原文 0 处出现 "月令被冲 / 围克" 语义
  → 双不匹配：(1) 不直接支持 DTS-106 语义；(2) 资源自身 rule_refs 与规则 DTS-106 不对应
```

### 4.2 规则文件现状（`data/rules/DTS-106.json` + `backend/data/rules/DTS-106.json`，双份同文）

```text
rule_id = DTS-106 / title = "得令但月令被围克→身弱" / status = draft / version = 0.2.0
conditions: month_hidden_main_ten_god in [正印,偏印,比肩,劫财] AND day_branch_clash == true
conclusion.rationale_classical = "《滴天髓》:生方怕动库宜开,败地逢冲仔细推..."  ← classical 框架（与裁决冲突点①）
evidence_refs = ["E-DTS-106-001"]
无 authority_type 字段                                              ← 与裁决冲突点②（需显式补标）
```

### 4.3 代码挂载点（HEAD 已提交版 `judgment.py`，4 处）

```text
L128  CITATION_MAP: "DTS-106" → ("DTS-106", "E-DTS-106-001")   # ⑮-2 P0 CITATION 挂载
L355  旺衰评分文档: 得令但月令被局中支所冲(围克) → 附加 -2  [DTS-106]
L423  cits.add("DTS-106")
L715  rule_refs.append("DTS-106")
```

### 4.4 登记后的实施契约（**登记，未执行**；实施 = 未来 BOT-ZIPING 任务单）

```text
DTS-106 实施契约（ENGINEERING-DEFINED，User 裁决③落地版）:
  S1. rule_id = DTS-106 保留（"证据不足" ≠ "规则不存在"）
  S2. 规则文件显式补 authority_type = "ENGINEERING-DEFINED"（双份 data/ + backend/data/ 同步）
  S3. conclusion.rationale_classical 更名/加注为工程规则 rationale（不得继续以《滴天髓》经典框架表述）
  S4. 不得引用资源A 的 paraphrase 引文当"经典直接证明"；资源B（di_tian_sui DTS_0010）不作为 DTS-106 证据
     （其 rule_refs=DTS-DTS，语义不直接对应）
  S5. collision 处置：两资源同 evidence_id 不同资源 —— 随 ZIP-PRE-02 Loader 策略一并裁决
     （根级保留 + 子目录去重/改名），不得静默取根级
  S6. G1 不得因 DTS-106 是工程规则就假装已有经典证据：
     claim 层暴露 authority_type（与 ZIP-PRE-04 联动），最终 Claim 可辨识为工程规则判断
  S7. judgment.py 4 挂载点（L128/355/423/715）随 DTS-106 实施任务单一次性修订，不提前单独动
  S8. 本登记 ≠ 修改：data/rules/DTS-106.json、judgment.py、evidence 资源 0 改动
```

**登记状态**：

```text
ZIP-PRE-03(DTS-106) = RULING-RECORDED / ENGINEERING-DEFINED 登记完成 / 实施 0 执行
   - 规则保留 + 降权登记 + collision 随 Loader 策略裁决 + G1/claim 层可辨识
   - "证据不足" 与 "规则不存在" 的语义区分正式记录在案
```

---

## 5. 新发现（实施级，需 User 裁决，不动代码）

### X-1 — 15.6c D-2 提案的 `ZC-*` claim_id 与 G1 硬校验冲突【P1，实施前必须裁决】

```text
15.6c §5③ 提案: judgment 派生 claim 命名空间 = ZC-{domain}-{conclusion}（确定性, H-4 可回放）
G1 源码实锤 (HEAD g1_evidence.py L44):  if not str(cid).startswith("AC-"):
                                          reasons.append(f"{cid}: claim_id not AC-* (Traceability)")
⇒ 按 ZC-* 实施的 claim 会在 G1 全量 BLOCK（与 15.6c "G1 唯一生产 Gate" 目标直接矛盾）
```

**候选处理（登记，待裁决，不预设）**：

| 选项 | 内容 | 代价 |
|---|---|---|
| X-1a | 命名空间改为 `AC-ZP-{domain}-{conclusion}`（兼容 G1 既有 AC-* 校验） | 0 改 G1；ZP claims 与链A claims 同前缀，靠 composer_version + domain 标签区分 |
| X-1b | G1 扩展 claim_id 校验白名单（AC-* / ZC-*） | 改 G1（G1 是 ⑮-3 冻结面，需 User 授权）；15.6c 命名保持 |
| X-1c | 15.6c D-2 修订（amend 记录级）：把 `ZC-*` 改为 `AC-ZP-*` 并注记 | 记录层修订，随本 15.7 或后续 15.6d 出 |

> 我（BOT-MASTER）倾向 **X-1a + X-1c**：AC-ZP-* 前缀既保 G1 唯一 Gate 不动，又保确定性回放；15.6c 正文不动（User 认可版），以 15.7 本记录 §5 为修订注记。请 User 定。

### X-2 — G1 静默放行 pending_verification（与 ZIP-PRE-04 同根因，单独标注 DTS-106 相关面）

DTS-106 根级资源 `verification_status=pending_verification`，G1 现状 0 读该字段 → 工程规则登记的 claim 会以"证据已挂"外观放行。此面并入 ZIP-PRE-04 实施任务，本项不另立编号。

---

## 6. 前置审查总结与实施门（Gate）

```text
ZIP-PRE-01  ⑮-1-EVENT-SIGNAL   = AUDIT-COMPLETE / MAPPING-UNPROVEN → P1 未闭合
                                                  （SHIJIAN fail-closed 红线已登记）
ZIP-PRE-02  ⑮-2 loading boundary = AUDIT-COMPLETE / 1503 子目录资源生产不可见 → 实施待 Loader 策略裁决
ZIP-PRE-04  G1 verification_status = AUDIT-COMPLETE / 静默放行坐实（全函数 5 校验面登记）→ 独立 P1
ZIP-PRE-03  DTS-106 工程登记     = RULING-RECORDED / ENGINEERING-DEFINED 8 条实施契约登记 → 0 执行
X-1         G1 AC-* 硬校验冲突   = 需 User 裁决（倾向 X-1a+X-1c）
X-2         并入 ZIP-PRE-04
```

**实施门（与 15.6c §9 顺序③衔接）**：

```text
ZIP-INT-01~08 授权前置条件（全部满足才开工）:
  ☐ X-1 裁决完成（claim_id 命名空间定死）
  ☐ ZIP-PRE-01: event_type 映射获依据级审查 或 SHIJIAN fail-closed 降级方案被认可
  ☐ ZIP-PRE-02: Loader 可见性策略三选一被 User 裁决
  ☐ ZIP-PRE-04: G1 verification_status 分档策略被 User 裁决
  ☐ DTS-106 实施契约（§4.4 S1-S8）并入 BOT-ZIPING 任务单
  ☐ 15.6c 架构基线（a719bc53）保持未变
⇒ 当前：ZIP-INT-01~08 维持未授权（User 锁定），任何 BOT 不得边审边改。
```

---

## 7. 冻结与边界记录

```text
✅ 0 代码改动（judgment.py / g1_evidence.py / _rule_backends.py / compute_stage.py 全未动）
✅ 0 evidence 改动（E-DTS-106-001 双资源原样）
✅ 0 rule 改动（DTS-106.json 双份原样, status=draft 维持）
✅ ⑮-0 / ⑮-1 / ⑮-2 P0 基线未回改（⑮-1 仅新增 EVENT-SIGNAL P1 子项登记）
✅ a719bc53（15.6c）与本地链保持不推 GitHub（User 治理口径）
✅ 工作区未提交 ⑮ 整改代码未进入本 commit
```

*Generated by BOT-MASTER on 2026-09-10（替代 BOT-ZIPING 完成 ZIP-PRE 前置审查，User 授权）*
*Code change: 0 | Evidence change: 0 | Rule change: 0 | Algorithm change: 0*
*Files modified: 1 (this pre-review record only)*
*取证基线：git show HEAD(=a719bc53) 已提交版本 + backend/data 资源实读，非工作区。*
