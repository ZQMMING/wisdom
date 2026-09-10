# BZ-FNDR-15.20 — ZIPING-P0-1 FINAL CONSTRUCTION MATRIX

> **Audit-only / Code=0 / Evidence=0 / Rule=0 / Algorithm=0 / 单文件审计记录**
>
> 前置：15.17 → 15.17b → 15.18 → 15.18b → 15.19 全部 COMPLETE
> User 2026-09-11 锁定 15.20 目标：**把 P0-1 从 NOT CLOSED 推导出一条明确、最小侵入、可实施的 CLOSED 路径**
>
> 输出形式：**FINAL CONSTRUCTION MATRIX**（问题 → 根因 → 文件 → 性质 → 允许 → 测试 → 验收 → 完成后状态）
>
> 12 项必答 (User 锁定) 全部覆盖。

---

## 0. 元数据

| 项 | 值 |
|---|---|
| 审计 ID | BZ-FNDR-15.20 |
| 前置 | 15.17 / 15.17b / 15.18 / 15.18b / 15.19 |
| 状态 | **AUDIT COMPLETE / PRODUCTION MATRIX READY** |

---

## 1. 12 项必答

### Q1. 21 条 ZiPing rules 的最终 admission 机制是什么？

**实测坐实**：现有 admission 是**双轨制**，互不相通：

| 轨道 | 覆盖范围 | admission 机制 | 字段 |
|---|---|---|---|
| ASR 路径 | 10 条 ASR-PROD-* | verification_scope + verified_by(GPT agent) + credential_hash | `_meta.declared_credential_hash` 验证 |
| RuleLoader 路径 | 136 条 (含 21 ZiPing) | status enum (draft/review/validated/active/deprecated) | `status` 字段 |

**21 条 ZiPing rules 必须在 RuleLoader 路径上获得 admission**——但 status 字段无 agent 审计链路。

**最终 admission 机制（MINIMAL）**：
- **不引入新 admission gate**——这会触发 P2.1-F 链路 + Agent identity 等大量新基础设施
- **建立 ZiPing admission status 表**（RuleLoader 路径上的窄规则）：
  ```
  RuleLoader status enum 维持不变 (draft/active/...)
  + 新增 admission_metadata 块 (verifying_agent + admission_evidence + admission_timestamp)
  + admission_metadata 由 RuleLoader 加载时校验 (类似 _meta.declared_credential_hash)
  + 21 条 ZiPing rules 补 admission_metadata 即视为 PRODUCTION_ADMITTED
  ```
- **G1 不变**——G1 仍只校验 4 项硬门槛（实测已坐实 G1 不是 bug）
- **维护"Loaded ≠ Production-Admitted"红线**——但 admission_metadata 提供审计追溯

### Q2. status=active 与真正 Production Admission 如何定义关系？

**实测坐实**（15.18）：8 条 active + 13 条 draft 都**没有 admission_metadata**。

**最终关系定义**：
```
Production Rule Admission =
    status == 'active'                         (RuleLoader 加载条件)
    AND
    admission_metadata.verifying_agent != None  (Agent 审计追溯)
    AND
    admission_metadata.credential_hash 已注册   (P2.1-F 链路锚定)
```

→ 现有 8 条 active **不满足** Production Rule Admission（缺 admission_metadata）——**这与 15.18 锁定一致，不允许绕过**。

**agent 选择**：参照 production_assertion_rules.json 的 verified_by 模式：
- 优先：人类审计师 (User) 提供 credential_hash
- 第二：Agent-based audit (如 BOT-AUDITOR，需独立 build)
- 不可：BOT-MASTER 自己审核自己（无 authority）

### Q3. GEJU evidence refs 应从哪里正式产生？

**实测坐实**（15.18b）：GEJU judge 函数 L662/670/682/700/703/704/710/715 共 8 处 `rule_refs.append("ZPZ-xxx")`，**没有** `evidence_refs.append(...)`。

**根因**：GEJU 用的是直接 append 模式，**没有用** WANGSHUAI 的 `cits.add("DTS-xxx")` 模式（`cits.add` 自动从 CITATION 表 L123-144 查 rule→evidence 映射并双填）。

**正式产生路径（最小改动）**：
- 在 GEJU judge 函数顶部添加 `cits = _Citations()` 实例
- 把 8 处 `rule_refs.append("ZPZ-xxx")` 替换为 `cits.add("ZPZ-xxx")`
- 在 return 路径用 `evidence_refs=cits.evidence_refs, rule_refs=cits.rule_refs` 替代现有手工 append

**验证**：CITATION 表 L123-144 已含 ZPZ-101/105~111/120 完整 rule→evidence 映射，无需新建。

### Q4. YONGSHEN 8 主流格规则是否真的存在、是否具备证据、是否允许 admission？

**实测**：

| 主流格 | 应有规则 | 实际 | evidence | 允许 admission？ |
|---|---|---|---|---|
| 正官格 | ZPZ-106 | ✓ | E-ZPZ-106-001.json | ✅ |
| 七杀格 | ZPZ-107 | ✓ | E-ZPZ-107-001.json | ✅ |
| 正印格 | ZPZ-108 | ✓ | E-ZPZ-108-001.json | ✅ |
| 偏印格 | ZPZ-?（理论 ZPZ-112）| ✓ ZPZ-112 已存 | E-ZPZ-112-001.json | ✅ |
| 正财格 | ZPZ-109 | ✓ | E-ZPZ-109-001.json | ✅ |
| 偏财格 | ZPZ-?（理论 ZPZ-118）| ✓ ZPZ-118 已存 | E-ZPZ-118-001.json | ✅ |
| 食神格 | ZPZ-?（理论 ZPZ-115）| ✓ ZPZ-115 已存 | E-ZPZ-115-001.json | ✅ |
| 伤官格 | ZPZ-110 | ✓ | E-ZPZ-110-001.json | ✅ |

→ **8 主流格全部存在 + evidence 齐全**——GEJU_RULE_BY_GE 表 L257-280 需补 8 主流格 → (ZPZ-xxx, E-ZPZ-xxx-001) 映射。

**允许 admission**：用户裁决（agent audit 通过后）即可。

### Q5. SHISHEN 是否属于当前 P0-1 必须闭合的范围？

**实测**（15.18b）：SHISHENJudgment STATUS="P1-REVIEW" PRODUCTION_READY=False。Pipeline 未注入 semantic_signals。

**最终裁决**：SHISHEN **不属于 P0-1 必须闭合的范围**。
- 理由：P0-1 = "Chain-B (ZiPing Judgment) → 0 production consumer" 修复；SHISHEN 是 Chain-B 内部的 P1-REVIEW 子任务
- P0-1 闭合后，SHISHEN 仍维持 P1-REVIEW 状态，Pipeline 仍不注入 semantic_signals → Composer 仍 fail-closed → 0 claim
- SHISHEN 单独走 P1-REVIEW → PIPELINE 信号注入 → Stage 3 子任务

**唯一例外**：如果 SHISHEN 被 P0-1 闭合"无意中激活"（Composer 不补空引用，但 YONGSHEN 补全后顺带激活 SHISHEN），则需重新审视。

### Q6. SHIJIAN 后续处理？

**实测**（15.14）：SHIJIAN 6 候选方法全 FAIL，③Method / ④Event Mapping 全 0 命中。

**最终裁决**：SHIJIAN **明确排除** P0-1 闭合范围。
- 理由：User 锁定 15.14 FAIL-CLOSED + 15.18b Composer S4 拦截 SHIJIAN
- Composer `_FC_BLOCKED_DOMAINS = {"SHIJIAN"}` 永远拦截 → 0 SHIJIAN claim
- SHIJIAN 单独走：Method 审计通过 + Event Mapping 建立 → 单独 Stage 任务

### Q7. 10 条 mapping admission 还是新增 ZiPing 专用 mapping？

**实测**（15.19）：mapping_registry L92 强制 status=ACTIVE 过滤；10 条 mapping 全 draft → 0 进生产链。

**最终裁决**：**两步走**，但**不新建** ZiPing 专用 mapping 路径——保持 mapping_registry 单一接口：

```
Step 1: 现有 10 条 mapping (MAP-1001~1010) admission 升 ACTIVE
  - 现有 rule_refs 全是 ZPZ-*
  - 已具备 evidence (rule_refs 100% 命中 production RuleLoader)
  - 升 ACTIVE = 单字段改 status='ACTIVE'

Step 2: 补 WANGSHUAI 域 mappings
  - 当前 mapping rule_refs 全是 ZPZ-* (GEJU/SHISHEN 域)
  - 新增 DTS-* (WANGSHUAI 域) mappings
  - DTS-* mappings 需 evidence + spec_decisions_ref + modern_theme
  - 估算 5-8 条 DTS-* mappings (DTS-101~107)
```

**不新建** ZiPing 专用 mapping path——map 一旦 admission ACTIVE，mapping_registry 自动通过 rule_refs 交集机制覆盖 Composer claims。

### Q8. AC-ZP-* 是否继续复用现有 G1，不修改 G1？

**实测**（15.17b / 15.18）：G1 evidence_gate 只校验 4 项硬门槛，**完全不看 admission_scope / verified_by / claim_id namespace**。

**最终裁决**：AC-ZP-* **继续复用现有 G1**，**不修改 G1**。
- 理由：G1 不是 bug（实测已坐实），G1 校验维度是 rule_refs 非空 + evidence_refs 非空 + source_layers 非空 + claim_id 前缀 AC-
- Composer claims 经修复后，AC-ZP-* 自动通过 G1
- 唯一豁免：Composer 默认 OFF → 实际只有 WANGSHUAI 域能被生产面消费

**红线守备**：G1 维持 LOCKED，**不因 P0-1 闭合而扩展 G1**。

### Q9. Composer ON 后如何保证 T-3 零漂移？

**T-3 零漂移 5 项条件**（15.19 §3.5 修正后 — User 已删 OpenAI claim_id 过滤项）：

```
1. ✅ Composer S4 fail-closed (UNKNOWN/NOT_EXECUTED/FAILED/EVENT_ABSENT/SHIJIAN)
2. ❌ judgment.py 修 GEJU evidence_refs.append + YONGSHEN 主流格映射
3. ❌ 21 条 ZiPing rules admission_metadata 完整
4. ❌ mapping_registry admission: 10 draft → ACTIVE + 补 WANGSHUAI DTS-* mappings
5. ❌ Composer production path 打开 (judgment_composer=self.judgment_composer)
```

→ 4 项施工项 → 见 §3 FINAL CONSTRUCTION MATRIX。

### Q10. 哪些修改属于 P0-1，哪些必须拆成后续 P1？

| 项 | P0-1 | 理由 |
|---|---|---|
| Composer S4 fail-closed | ✅ 已在 Stage 2 落地 | Composer Module + 单元测试 11/11 PASS |
| Composer 默认 OFF | ✅ 已在 Stage 2 落地 | Stage 2 commit 7f1cefa4 |
| judgment.py GEJU evidence refs 修补 | ✅ P0-1 | Composer activation 必填 |
| judgment.py YONGSHEN 主流格映射补全 | ✅ P0-1 | Composer activation 必填 |
| 21 条 ZiPing rules admission_metadata | ✅ P0-1 | Composer activation 必填 |
| mapping_registry 10 → ACTIVE | ✅ P0-1 | WANGSHUAI mapping 必填 |
| mapping_registry 补 WANGSHUAI DTS-* mappings | ✅ P0-1 | WANGSHUAI 域词库覆盖 |
| Composer production path 打开 | ✅ P0-1 | 最终施工步 |
| SHISHEN Pipeline 信号注入 | ❌ P1 | P1-REVIEW, P0-1 闭合后另立任务 |
| SHIJIAN Method Audit | ❌ P1 | 15.14 FAIL, P0-1 闭合后另立任务 |
| OpenAI claim_id 过滤 | ❌ 安全加固 | User 明确指出不属于 P0-1 主闭环 |
| RenderStage 任何修改 | ❌ 禁止 | User 红线 |
| G1 任何修改 | ❌ 禁止 | User 红线 |
| Bazi 任何修改 | ❌ 禁止 | User 红线 |

### Q11. 最小修改集合？

**MINIMAL 改动集合**（4 项）：

1. **`src/tongshu/reasoning/judgment.py`** — GEJU/YONGSHEN 算法修补（不改算法逻辑，只补 evidence_refs）
2. **`src/tongshu/pipeline.py`** — Composer 默认 ON（Stage 2 默认 OFF → P0-1 闭合时默认 ON）
3. **`backend/data/rules/*.json`** — 21 条 ZiPing rules 补 admission_metadata 块（不修改 status 字段语义）
4. **`backend/data/mappings/*.json`** — 10 条 mapping 改 status='ACTIVE' + 新增 5-8 条 DTS-* mappings

**不修改**：
- G1 / RenderStage / Composer module 本身 / Bazi engine / pipeline_stages/* / evidence/*.json

### Q12. 最终需要跑哪些 regression / acceptance gates？

**施工后必须跑（按顺序）**：

| Gate | 范围 | 通过条件 |
|---|---|---|
| 单元测试 | test_g0_1 / test_g0_2 / test_int_01_02_03 / test_int_05 / test_int_06 | 全部 PASS |
| Composer 单元 | test_int_05_judgment_claim_composer | 11/11 PASS（已锁） |
| Pipeline 集成 | test_int_06_pipeline_integration | 5/5 PASS（已锁，OFF default） |
| **T-3 回归** | test_p0_evidence_chain + test_ziping_15_2 + test_audit_gates + test_api | **73/73 PASS**（无漂移） |
| **新增 Composer ON 端到端** | 测试 Composer production ON + 真实 bazi + 真实 judgment 输出 | (1) Composer claims 5 域全产出 (2) validation_passed=True (3) source=llm_renderer (4) ZP claims 含完整 refs (5) ZP claims 全 AC-ZP-* namespace |
| **G1 全解析面** | test_audit_gates.py | Composer ON 后 G1 仍 100% 解析面 |
| **⑮-2 baseline** | test_ziping_15_2_evidence_provenance | 20/20 PASS（Composer ON 不漂移） |
| **⑮-1 SHIJIAN fail-closed** | test_ziping_15_1_shijian_fail_closed | 0 SHIJIAN claim |
| **⑮-3 全链路** | audit_validation | pass + 0 P0 |

**施工前必须先**：15.20 audit 文档被 User 接受 → User 逐项裁决 12 项答复 → 才进入集中施工。

---

## 2. ZIPING-P0-1 FINAL CONSTRUCTION MATRIX

### Matrix 总体结构

```
Step 1: judgment.py 修补 (GEJU + YONGSHEN)
Step 2: 21 条 ZiPing rules admission_metadata
Step 3: mapping_registry admission + 词库扩容
Step 4: Composer production path ON
Step 5: 全量回归 + T-3 验证
```

### Step 1: judgment.py 修补

| 项 | 值 |
|---|---|
| **问题** | GEJU evidence_refs 缺失（8 处 rule_refs.append 无对应 evidence_refs.append） + YONGSHEN 主流格映射缺失（GEJU_RULE_BY_GE 表只 5 特殊格） |
| **根因** | GEJU 用直接 append 模式没用 cits.add；YONGSHEN 用 GEJU_RULE_BY_GE.get(ge_type) 主流格无映射 |
| **必须修改文件** | `src/tongshu/reasoning/judgment.py` |
| **修改性质** | 修改算法数据收集（不改算法逻辑）|
| **是否允许** | ✅ User 已授权 "不要修改算法核心，仅补 provenance 完整性" |
| **精确改动** | (a) GEJU judge 函数顶部 `cits = _Citations()`，8 处 `rule_refs.append(...)` 改 `cits.add(...)`，return 路径用 `cits.evidence_refs / cits.rule_refs` (b) `GEJU_RULE_BY_GE` 表 L257-280 补 8 主流格 (正官/七杀/正印/偏印/正财/偏财/食神/伤官) → (ZPZ-xxx, E-ZPZ-xxx-001) |
| **测试** | (a) 重跑 15.18b 探针，验证 GEJU evidence_refs 非空 + YONGSHEN refs 非空 (b) 新增 `test_judgment_provenance_complete.py` 5 域 evidence_refs 全有断言 |
| **验收门** | judgment.py 改动后所有现有测试不退化 + 5 域实测 evidence_refs 全有 |
| **完成后状态** | 5 域从 1/5 完整 → 5/5 完整（除 SHISHEN/SHIJIAN 域未执行）|

### Step 2: 21 条 ZiPing rules admission_metadata

| 项 | 值 |
|---|---|
| **问题** | 21 条 ZiPing rules 0 admission_scope / 0 verified_by / 0 credential_hash |
| **根因** | RuleLoader 路径无 admission_metadata 字段；与 ASR 路径双轨制 |
| **必须修改文件** | `backend/data/rules/DTS-101.json` ... `YHZP-105.json`（21 个文件） |
| **修改性质** | **新增 admission_metadata 字段**（不改 status 字段，不改 evidence_refs，不改 rule logic） |
| **是否允许** | ✅ User 已授权 "8 条 active ≠ production_admitted, 14 已锁" — 必须建立 admission 链路 |
| **精确改动** | 每个 rule.json 增加：<br>`"admission_metadata": {`<br>`  "verifying_agent": "<agent-id>",`<br>`  "verifying_agent_type": "HUMAN\|AGENT",`<br>`  "admission_evidence_ref": "<audit-doc-id>",`<br>`  "admission_timestamp": "<ISO8601>",`<br>`  "credential_hash": "<P2.1-F hash>"`<br>`}`<br>**注意**：status 字段语义不变 |
| **测试** | (a) 写 `test_ziping_rules_admission.py` 验证 21 条规则 admission_metadata 完整 (b) RuleLoader 加载时**新增 admission_metadata 校验**（_JsonRuleBackend 加载时 schema 校验 admission_metadata 完整性） |
| **验收门** | 21 条 ZiPing rules admission_metadata 全部非空 + RuleLoader 加载时 schema 校验通过 + 不影响 136 条生产规则加载 |
| **完成后状态** | 21 条 ZiPing rules 满足 Production Rule Admission 定义（Q1/Q2）|

### Step 3: mapping_registry admission + 词库扩容

| 项 | 值 |
|---|---|
| **问题** | 10 条 mapping 全 status=draft → apply_to_claims 过滤 0 进生产；WANGSHUAI 域 DTS-* 0 mapping 覆盖 |
| **根因** | mapping status enum 设计；DTS-* mappings 不存在 |
| **必须修改文件** | `backend/data/mappings/MAP-1001.json` ... `MAP-1010.json` (改 status) + **新增** `MAP-1101.json` ... `MAP-1107.json` (WANGSHUAI 域 DTS-*) |
| **修改性质** | (a) 改 status 字段 draft → ACTIVE (b) 新增 mapping 文件 |
| **是否允许** | ⚠️ **待 User 裁决**——User 明确说 "不要修改 RenderStage 来解决 15.19"，但 mapping admission 是 P0-1 闭环所需（Q7 锁定）|
| **精确改动** | (a) 10 条 mapping `status: draft` → `status: ACTIVE` (b) 新增 5-8 条 DTS-* mappings:<br>  MAP-1101: DTS-101/102/104/105/106/107 → "得令/失令判断" modern_theme<br>  MAP-1102: DTS-104 → "得地/十二长生"<br>  MAP-1103: DTS-105 → "党众/印比劫"<br>  MAP-1104: SMTH-101/102 → "十二宫旺位/弱位"<br>  etc. |
| **测试** | (a) 重跑 15.19 §1 测试，验证 mapping 命中 Composer claims (b) 新增 `test_mapping_admission.py` 验证 status=ACTIVE 进 apply_to_claims |
| **验收门** | Composer claims 命中 mapping（mapping_refs 非空）+ modern_theme 非空 + RenderStage 输出含 modern_theme |
| **完成后状态** | mapping_registry 10 + 5-8 条 ACTIVE mappings；WANGSHUAI/GEJU/YONGSHEN 域词库覆盖 |

### Step 4: Composer production path ON

| 项 | 值 |
|---|---|
| **问题** | Stage 2 commit 7f1cefa4 Composer 默认 OFF（T-3 保护）|
| **根因** | 当时 Composer ON 实测 G1 fail → template_fallback（YONGSHEN refs 全空）|
| **必须修改文件** | `src/tongshu/pipeline.py` |
| **修改性质** | 单行改动：`judgment_composer=None` → `judgment_composer=self.judgment_composer` |
| **是否允许** | ⚠️ **Step 1-3 完成后才允许**——这是 P0-1 闭合的最终步 |
| **精确改动** | `src/tongshu/pipeline.py` L370 附近：`judgment_composer=None,  # INT-06 默认 OFF` → `judgment_composer=self.judgment_composer,  # P0-1 CLOSED` |
| **测试** | (a) 跑 15.18b 探针验证 Composer claims 5 域全产出 (b) 跑完整 T-3 regression 验证 0 漂移 |
| **验收门** | (1) Composer claims 5 域全产出 (2) validation_passed=True (3) source=llm_renderer (4) ZP claims 全部 AC-ZP-* namespace (5) ZP claims 全含 mapping_refs + modern_theme |
| **完成后状态** | **P0-1 CLOSED**——Chain-B (ZiPing Judgment) 通过 Composer 进入生产链 |

### Step 5: 全量回归 + T-3 验证

| 项 | 值 |
|---|---|
| **范围** | 同一 commit 一次性集成 Step 1-4 |
| **测试套件** | 全部 117 项回归 + 新增 admission + mapping 测试 |
| **验收门** | (1) 73/73 T-3 PASS (2) 117/117 全回归 PASS (3) Composer ON E2E 测试 PASS (4) G1 全解析面 0 退化 (5) ⑮-1 SHIJIAN fail-closed 维持 (6) ⑮-2 baseline 20/20 维持 (7) ⑮-3 全链路 PASS |
| **完成后状态** | P0-1 = CLOSED，production 路径含 Composer claims，可推 GitHub |

---

## 3. 施工顺序 + 红线

### 严格施工顺序（5 步全部 atomic 单 commit）

```
Step 1 (judgment.py) ─┐
                      ├─→ 同一 commit (Step 1-3) 因互相依赖
Step 2 (admission)   ─┤
                      │
Step 3 (mapping)     ─┘
         ↓
Step 4 (Composer ON) 单独 commit (依赖 Step 1-3)
         ↓
Step 5 (回归验证) 不 commit, 是验收门
```

### 红线（User 已锁定）

```
❌ 不改 G1 (实测非 G1 bug)
❌ 不改 RenderStage (User 红线, 15.19 验证 RenderStage 本身不必改)
❌ 不改 Composer module 本身 (Stage 2 commit 7f1cefa4 已 PASS)
❌ 不改 Bazi engine
❌ 不改 SHIJIAN / SHISHEN 域算法 (P1-REVIEW, 后续 Stage)
❌ 不提升 status 字段语义 (8 条 active 维持 active, 不变 production_admitted)
❌ 不引入新 admission gate (P2.1-F 链路) — admission_metadata 是 RuleLoader 路径窄规则
```

### 可允许的修改（验证后）

```
✅ judgment.py 数据收集（GEJU cits.add / YONGSHEN GEJU_RULE_BY_GE 表）
✅ 21 条 rule.json 加 admission_metadata 字段
✅ mapping 改 status + 新增 DTS-* mappings
✅ pipeline.py 1 行（Composer 默认 ON）
```

---

## 4. P0-1 闭环定义（最终）

**P0-1 CLOSED = 全部 5 项完成**：

```
[1] Composer S4 fail-closed               ✅ Stage 2 commit 7f1cefa4
[2] judgment.py 5 域 evidence_refs 完整  ❌ Step 1 完成后
[3] 21 条 ZiPing rules admission_metadata ❌ Step 2 完成后
[4] mapping_registry ACTIVE mappings     ❌ Step 3 完成后
[5] Composer production path ON + T-3 0 漂移 ❌ Step 4 完成后
```

5/5 全完成时 P0-1 = CLOSED。

---

## 5. 当前门状态

```text
G0-1 Index                       🟢 PASS
G0-2 Provenance                  🟢 PASS
INT-01~03 Stage 1                🟢 CLOSED
INT-05 Composer Module           🟢 MODULE PASS
INT-06 接入点                     🟢 CODE PASS (default OFF)
15.17 Activation Contract        🟢 AUDIT COMPLETE
15.17b Rule ID Investigation     🟢 AUDIT COMPLETE
15.18 Rule Admission Audit       🟢 AUDIT COMPLETE
15.18b Judgment Algorithm Audit  🟢 AUDIT COMPLETE
15.19 RenderStage Mapping Audit  🟢 AUDIT COMPLETE
15.20 FINAL CONSTRUCTION MATRIX  🟢 AUDIT COMPLETE (本次, 5 项施工清单 + 12 项必答)

P0-1 闭环                         🔴 NOT CLOSED (4 项施工待执行)
Step 1 (judgment.py)              ⚪ 未开工
Step 2 (21 admission_metadata)    ⚪ 未开工
Step 3 (mapping admission + DTS-* mappings) ⚪ 未开工
Step 4 (Composer production ON)   ⚪ 未开工
Step 5 (全量回归 + T-3)          ⚪ 验收门

SHIJIAN                           🔴 FAIL / FROZEN (维持)
SHISHEN                           ⚪ P1-REVIEW (维持, 不在 P0-1 范围)
G1 / RenderStage / Composer Module / Bazi 🔒 LOCKED (红线维持)
GitHub push                       🔴 暂不推 (19 commits 本地领先)
```

---

## 6. 待你裁决

### 6.1 12 项必答是否接受？

特别确认：
1. **admission 机制选择**：RuleLoader 路径窄规则（不引入 P2.1-F 新 admission gate）——你之前明确不批"改变生产规则准入面"，所以这条最保守。
2. **GEJU/YONGSHEN 修补**：仅补 evidence_refs 数据收集，不改算法逻辑
3. **mapping admission**：10 条 draft → ACTIVE + 新增 5-8 条 DTS-* mappings（保持 mapping_registry 单一接口）
4. **G1/RenderStage/Composer Module/Bazi**：0 修改
5. **OpenAI claim_id 过滤**：拆出 P0-1，归入安全加固
6. **SHISHEN/SHIJIAN**：排除 P0-1，单独 P1 任务

### 6.2 下一步施工授权

如果 6.1 接受，下一步：

| 选项 | 内容 |
|---|---|
| A | 接受 15.20，授权进入 **集中施工 + 全量回归**（Step 1-5 一次 commit）|
| B | 接受 15.20，先做 Step 1 单独施工 + 测试，验证后再 Step 2/3/4/5 |
| C | 接受 15.20，但先做 Step 2（admission_metadata）或 Step 3（mapping）单独施工 |
| D | 暂缓，先评估 GitHub push 19 commits 决策 |

按你的治理风格（"严格按事实裁决，先验证再汇报"），**B 分步施工**最稳健——每步单 commit，每步独立 regression。但 15.13 Stage 2 任务单已锁定"Step 1-3 同一 commit, Step 4 单独 commit, Step 5 验收门"——所以 C 也可考虑。

我作为 BOT-MASTER 的事实建议（不替你拍板）：**B 分步施工**——每步单 commit，每步独立验证，最大限度保住 T-3 baseline。Step 1-3 不应同一 commit，因为 Step 2/3 改动量较大（21 JSON + 8 JSON），分开便于回滚。

*Generated by BOT-MASTER on 2026-09-11*
*Code Change = 0 / Evidence Change = 0 / Rule Change = 0 / Algorithm Change = 0*
*5 项关键实测取证 (judgment.py 行号 / 8 主流格存在性 / evidence 文件存在 / mapping admission gate)*
*ZIPING-P0-1 FINAL CONSTRUCTION MATRIX 输出: 5 步施工路径 + 12 项必答 + 红线 + 验收门*
