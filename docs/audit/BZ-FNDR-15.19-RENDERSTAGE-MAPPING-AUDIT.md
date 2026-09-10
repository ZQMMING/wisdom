# BZ-FNDR-15.19 — RenderStage Mapping Audit

> **Audit-only / Code=0 / Evidence=0 / Rule=0 / Algorithm=0 / 单文件审计记录**
>
> 前置：15.18b commit `b24445e1` 锁定 5 域实测结论（③ WANGSHUAI / ② GEJU+YONGSHEN / ① SHISHEN+SHIJIAN）
> User 2026-09-11 授权 15.19：RenderStage 是否"缺词库"还是"更深输出契约限制"

---

## 0. 元数据

| 项 | 值 |
|---|---|
| 审计 ID | BZ-FNDR-15.19 |
| 前置 | 15.18b |
| 探针 | `scripts/audit_15_19_render.py`（一次性, 探针已删） |
| 状态 | **AUDIT COMPLETE** |

---

## 1. 12 项实测答案（直接回应 User 锁定）

### 1.1 AC-ZP-* namespace 是否被 registry 识别？**❌ 不识别**

实测：
```
mapping_registry.apply_to_claims([{
    "claim_id": "AC-ZP-wangshuai-strong",
    "rule_refs": ["DTS-101", "DTS-104", "DTS-105"],
    ...
}])
→ mapping_refs: <NONE>, modern_theme: <NONE>
```

**实测机制**（mapping_registry.py L79-109）：
- `apply_to_claims` **完全通过 rule_refs 交集** 找 mappings
- **不读取 claim_id 字段，不识别 namespace**
- AC-ZP-* / AC-* / ZC-* 对 mapping_registry 透明

### 1.2 5 Domain conclusions 合法 mapping？**❌ 全部无覆盖**

10 条 mappings rule_refs 全是 ZPZ-*（十神语义），且全部 status=draft：

| mapping_id | status | rule_refs | source_term | 覆盖 ZiPing 域 |
|---|---|---|---|---|
| MAP-1001 | **draft** | ZPZ-101/108/111/121/122 | 正印 | GEJU/SHISHEN |
| MAP-1002 | **draft** | ZPZ-101/112/122 | 偏印 | GEJU/SHISHEN |
| MAP-1003 | **draft** | ZPZ-109/117/127 | 正财 | GEJU/SHISHEN |
| MAP-1004 | **draft** | ZPZ-104/118/128 | 偏财 | GEJU/SHISHEN |
| MAP-1005 | **draft** | ZPZ-103/115/125 | 食神 | GEJU/SHISHEN |
| MAP-1006 | **draft** | ZPZ-103/110/116/126 | 伤官 | GEJU/SHISHEN |
| MAP-1007 | **draft** | ZPZ-105/106/119/129 | 正官 | GEJU/SHISHEN |
| MAP-1008 | **draft** | ZPZ-105/107/120/130 | 七杀 | GEJU/SHISHEN |
| MAP-1009 | **draft** | ZPZ-102/113/123 | 比肩 | GEJU/SHISHEN |
| MAP-1010 | **draft** | ZPZ-102/114/124 | 劫财 | GEJU/SHISHEN |

**WANGSHUAI 域的 rule_refs (DTS-*) 0 命中**——所有 10 条 mappings 是十神/格局域，不含 DTS-*。
**GEJU 域 (ZPZ-111/106/110) 命中 MAP-1006/1007**——但 status=draft 被过滤。
**YONGSHEN 不命中**（refs 全空）。

### 1.3 UNKNOWN / NOT_EXECUTED / FAILED fail-closed？**✅ Composer S4 拦截**

实测 Composer S4 黑名单（`_FC_BLOCKED_CONCLUSIONS`）= {UNKNOWN, NOT_EXECUTED, FAILED, EVENT_ABSENT}。
**Composer 不产这些结论的 claim → 0 进 mapping 链**。

### 1.4 5 域真实 conclusions mapping 覆盖？**❌ 全部无覆盖**

实测 mapping 匹配情况：
```
WANGSHUAI-WEAK (DTS-102/106/105): 0 mapping (DTS-* 不在 10 条 MAP-1001~1010 任何 rule_refs)
GEJU-BROKEN (ZPZ-111/106/110 + DTS-106): 0 mapping (status=draft 被过滤, ACTIVE=0)
YONGSHEN-PRIMARY: 0 rule_refs → 0 mapping
SHISHEN-None: Composer 拦截 → 0 claim
SHIJIAN-None: Composer 拦截 → 0 claim
```

### 1.5 SHISHEN 未执行状态被错误渲染？**❌ 不会**

实测 Composer S4 黑名单 + `_FC_BLOCKED_DOMAINS = {"SHIJIAN"}`（当前未含 SHISHEN 但 SHISHEN STATUS=P1-REVIEW 不进生产）。
即便 SHISHEN 域被填充，Composer 仍走 S4 fail-closed。

### 1.6 SHIJIAN 因 mapping 存在被错误解出？**❌ 不可能**

实测所有 mappings rule_refs 是 **ZPZ-***（十神/格局），**0 含 EVENT / SHIJIAN 关键字**。即便 Composer 误产 SHIJIAN claim（已 S4 拦截），mapping 链无 EVENT-related entry → 不会通过 mapping 给 SHISHEN/SHIJIAN 贴词库标签。

### 1.7 mapping 是否把工程 conclusion 直接暴露给用户？**⚠️ 部分暴露（user_payload 层）**

实测 `_sir_to_user_payload`（renderer.py L317-319）:
```python
def _sir_to_user_payload(sir: dict) -> str:
    return json.dumps(sir, ensure_ascii=False)  # ← 全 SIR 序列化
```

SIR 含 atomic_claims 完整 dict（含 claim_id, rule_refs, evidence_refs, source_layers）。
Renderer 把 user_payload JSON 传给 LLM client。
**LLM 看到 claim_id 但 system_prompt 禁止 "Rule DB ID / Evidence ID" 引用**（L306）。

实测 Stub 渲染输出（Composer ON 后）：
```text
rendered_text: '今日【WORK】主题方向清晰。基于你的命盘结构，宜在熟悉的领域推进既定方向。请结合实际情境把握节拍。今日的主题落在执行层面...'
rendered_text 含 'AC-ZP': False
rendered_text 含 'AC-': False
rendered_text 含 'ZPZ-': False
rendered_text 含 'DTS-': False
```

**Stub 不暴露 claim_id / rule_id**——但 OpenAI client 通过 `json.dumps(sir)` 把原始 claim_id 喂给 LLM。
**User 必须信任 LLM 遵守 system_prompt "不引用 Rule DB ID"**。

→ AC-ZP-* namespace 实际**不会暴露给用户**（Stub），但 OpenAI client **理论上可能暴露**（依赖 LLM 守约）。

### 1.8 旧 ZI_PING Chain-A mapping vs AC-ZP-* authority 重复？**✅ 不重复**

实测：
- 10 条 mappings rule_refs 全是 ZPZ-*（ZiPing 规则）
- Composer claim namespace = AC-ZP-*
- Chain-A claims (from `_build_claims_from_assertions`) namespace = `AC-{assertion_id}`，**不通过 mapping_registry rule_refs 交集机制**

→ Composer claims 与 Chain-A claims **在 mapping 维度不冲突**（两套 claim 各走各的 mapping 路径）。

### 1.9 RenderStage 是否有硬编码 namespace 白名单？**❌ 0 硬编码**

实测 `src/tongshu/render/renderer.py` grep:
```
AC-ZP: 0 次
AC-: 0 次 (LLM prompt 内除外)
claim_id: 19 次 (全部是动态读取, 无 startswith 检查)
namespace: 0 次
whitelist: 0 次
allowed: 0 次
claim_id 前缀检查模式: 0 次
```

**Renderer 不对 claim_id 做合法性检查**——接受任意 namespace。

### 1.10 加入合法 AC-ZP-* 后能否保持 T-3 零漂移？**❌ 不能（实测坐实）**

实测 Composer ON + Ziping refs 注入：
```
validation_passed: False
source: template_fallback
rendered_text: '今日【WORK】主题方向清晰...' ← TemplateFallback 输出, 不是 Renderer 输出
```

Composer ON + YONGSHEN refs=[] → G1 L31/L34 fail → validation_passed=False → source=template_fallback → RenderStage 输出被覆盖。

**即便补 YONGSHEN refs 让 G1 通过**：mapping 仍是 0（status=draft 过滤），用户看到的"Composer claims"是裸的 engineering conclusion text（"日主BING判身弱"等），没有 modern_theme 标签。

### 1.11 mapping 的 evidence/rule provenance 是否完整保留？**✅ rule_refs 完整保留**

实测 mapping entry 字段：
```json
{
  "mapping_id": "MAP-1001",
  "rule_refs": ["ZPZ-101", "ZPZ-108", "ZPZ-111", "ZPZ-121", "ZPZ-122"],
  "modern_theme": "滋养与根基支撑",
  "ontology_type": "SUPPORT",
  "version": "1.0.0",
  "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"]
}
```

**mapping 不带 evidence_refs**——mapping 本身只标 rule → modern_theme 映射，不带 evidence provenance。这是 schema 设计（`docs/mapping.schema.json` 只要求 `mapping_id` + `rule_refs`），不是 bug。

### 1.12 修改 RenderStage 必要性？**⚠️ RenderStage 本身不需要改，但需补 mapping_registry + Composer claim shape**

实测 RenderStage 行为：
- ✅ 接受任意 namespace claim（不硬编码白名单）
- ✅ 不暴露 claim_id（Stub）；OpenAI 客户端依赖 LLM 守约
- ❌ 缺词库标签（mapping_registry 0 ACTIVE ZPZ-* mapping）
- ❌ mapping_registry 完全不识别 AC-ZP-* namespace

**必要修改矩阵**：

| 修改项 | 必要性 | 红线 |
|---|---|---|
| 1. mapping_registry 10 条 draft → ACTIVE | 必要（mapping 才进生产链） | ⚠️ 触及 mapping admission gate |
| 2. mapping_registry 补 WANGSHUAI domain mappings (DTS-*) | 必要（覆盖 5 域） | ⚠️ 触及 mapping admission |
| 3. Composer claim shape 改用 `claim_id` 索引 (不 rule_refs) | 不必要 (现有机制 work) | ⚠️ 触及 mapping 改 |
| 4. RenderStage 加 namespace 白名单 | 不必要 (现有 0 硬编码) | ❌ User 红线 "不因 Composer 接入而改 RenderStage" |
| 5. mapping schema 加 `claim_id_namespace` 字段 | 可选 (扩展合法输出能力) | ⚠️ 触及 schema 改 |
| 6. OpenAI client 在 user_payload 中过滤 AC-ZP-* claim_id | 不必要 (user_payload 是 LLM 输入) | ❌ 强侵入 |

---

## 2. 核心架构发现（User 锁定的核心问题）

### 2.1 RenderStage 是"缺词库"还是"更深输出契约限制"？

**实测答案：两者皆是，且更深层问题在 mapping_registry**。

### 2.2 三层结构性缺失（按因果链）

```
[Layer 1] mapping_registry 当前 10 条全是 draft
   ↓ apply_to_claims L92 过滤
[Layer 2] Composer claims 进 SIR 后 0 mapping_refs / 0 modern_theme
   ↓ Renderer 拿到裸 claim text
[Layer 3] RenderStage 渲染用户看到的 engineering conclusion text
   ↓ 但 validation_passed=False 触发 template_fallback 覆盖
[Layer 4] 用户实际看不到 Renderer 输出（被 TemplateFallback 替代）
```

### 2.3 RenderStage 本身不是 bottleneck

实测：
- RenderStage **接受任意 namespace**（无硬编码）
- RenderStage **不暴露 claim_id**（Stub 实测）
- RenderStage **依赖 user_payload 透传** SIR 给 LLM → OpenAI client 是潜在 namespace 暴露点

**真正 bottleneck = mapping_registry + G1 fail-closed 链**。

### 2.4 "更深输出契约限制" 实测坐实

mapping_registry 设计：
- 通过 `rule_refs 交集` 找 mapping（不通过 claim_id / namespace）
- apply_to_claims 强制 status=ACTIVE 过滤（10 条 draft 全 0 进生产）
- schema 只要求 `mapping_id` + `rule_refs`（不要求 namespace 字段）

→ **mapping_registry 是"工程层数据",不是"namespace 识别层"**。
→ Composer claims 走不进 mapping_registry 是 **数据缺失 + 字段缺失**，不是 RenderStage 拒绝。

---

## 3. T-3 真正零漂移条件（实测更新）

### 3.1 当前 Composer OFF 状态（Baseline）
```
G1 evidence_gate: 73/73 PASS
validation_passed: True
source: llm_renderer
T-3 稳定 ✅
```

### 3.2 Composer ON + 不修复任何层（实测）
```
validation_passed: False (YONGSHEN refs=[] → G1 L31/L34)
source: template_fallback
rendered_text: TemplateFallback 输出, 无 AC-ZP 信息
T-3 漂移 ❌
```

### 3.3 Composer ON + 修 YONGSHEN 算法 (15.18b Step 3)
```
validation_passed: True (YONGSHEN refs 完整)
source: llm_renderer
rendered_text: 含 AC-ZP-* + 无词库标签的 engineering text
T-3 漂移 ❌ (用户看到 naked engineering conclusion)
```

### 3.4 Composer ON + 修 YONGSHEN + mapping admission
```
validation_passed: True
source: llm_renderer
rendered_text: 含 AC-ZP-* + ZPZ-* 词库标签
T-3 漂移 ❌ (mapping 仍只覆盖 SHISHEN/GEJU, WANGSHUAI 仍裸)
```

### 3.5 Composer ON + 修 YONGSHEN + mapping admission + WANGSHUAI mapping 扩容
```
validation_passed: True
source: llm_renderer
rendered_text: 含 AC-ZP-* + 全 5 域 mapping
但 openai_compat.py 仍把 raw claim_id 通过 json.dumps(sir) 传给 LLM
→ LLM 守约 system_prompt 才不会暴露 claim_id
T-3 漂移 ❌ (LLM 守约是软约束)
```

**真正的零漂移条件**（5 项全部满足）：
1. ✅ Composer S4 fail-closed（UNKNOWN/NOT_EXECUTED/FAILED/SHIJIAN 不产 claim）
2. ❌ judgment.py 修补 GEJU evidence_refs.append + YONGSHEN 主流格映射（15.18b 算法）
3. ❌ 21 条 Ziping rules admission metadata 完整（15.18 Path X）
4. ❌ mapping_registry admission 把 10 条 draft → ACTIVE + 补 WANGSHUAI DTS-* mappings（mapping admission gate）
5. ⚠️ OpenAI client 处理 user_payload 时主动过滤 claim_id 等 ID 字段（不依赖 LLM 守约）

**5 项中 1 已完成, 4 项未完成**——这与 15.18b §6 Composer activation 真正阻碍图完全一致。

---

## 4. 关键架构结论

### 4.1 三个"看起来独立但实际耦合"的层级

```text
1. Judgment Algorithm (judgment.py)
   - WANGSHUAI ✅ 完整
   - GEJU ⚠️ 缺 evidence_refs.append
   - YONGSHEN ❌ 缺主流格映射
   - SHISHEN/SHIJIAN 🔒 P1-REVIEW

2. Rule Admission (RuleLoader + ASR Path)
   - 21 条 ZiPing rules 0 admission_scope / 0 verified_by
   - 但 RuleLoader 已加载, G1 不校验 admission

3. MappingRegistry Admission (MappingRegistry)
   - 10 条 mappings 全 status=draft → apply_to_claims 过滤
   - rule_refs 覆盖 ZPZ-*（十神/格局），不覆盖 DTS-*（旺衰）
   - schema 不含 namespace 字段
   - Composer claims rule_refs 与 mapping rule_refs 部分交集（仅 ZPZ-* 部分）
```

### 4.2 12 项实测答案总览

| # | 问题 | 答案 |
|---|---|---|
| 1 | AC-ZP-* namespace 识别？ | ❌ 不识别（mapping_registry 通过 rule_refs 交集，不是 namespace） |
| 2 | 5 域 conclusions 合法 mapping？ | ❌ 全部无覆盖（10 条 mapping 全 draft 过滤） |
| 3 | UNKNOWN/NOT_EXECUTED/FAILED fail-closed？ | ✅ Composer S4 拦截 |
| 4 | 5 域真实 conclusions mapping？ | ❌ WANGSHUAI 0 + GEJU 0 (draft 过滤) + YONGSHEN 0 (refs 空) |
| 5 | SHISHEN 未执行错误渲染？ | ❌ 不会（域 STATUS=P1-REVIEW 不进生产） |
| 6 | SHIJIAN 因 mapping 错误解出？ | ❌ 不可能（mapping 无 EVENT-related） |
| 7 | mapping 把工程结论暴露用户？ | ⚠️ Stub 不暴露，OpenAI 依赖 LLM 守约 |
| 8 | 旧 ZI_PING vs AC-ZP-* authority 重复？ | ✅ 不重复（不同 namespace 各自映射） |
| 9 | RenderStage namespace 白名单？ | ❌ 0 硬编码（接受任意 namespace） |
| 10 | AC-ZP-* 后 T-3 零漂移？ | ❌ 不能（mapping 缺失 + G1 fail 触发 fallback） |
| 11 | mapping evidence/rule provenance 保留？ | ✅ rule_refs 完整保留（mapping 本身不带 evidence） |
| 12 | RenderStage 修改必要？ | ⚠️ RenderStage 不必改，需补 mapping admission + Composer claim shape |

---

## 5. 当前门状态

```text
G0-1 Index                       🟢 PASS
G0-2 Provenance                  🟢 PASS
INT-01~03 Stage 1                🟢 CLOSED
INT-05 Composer Module           🟢 MODULE PASS
INT-06 接入点                     🟢 CODE PASS
15.17 Activation Contract        🟢 AUDIT COMPLETE
15.17b Rule ID Investigation     🟢 COMPLETE
15.18 Rule Admission Audit       🟢 COMPLETE
15.18b Judgment Algorithm Audit  🟢 COMPLETE
15.19 RenderStage Mapping Audit  🟢 COMPLETE (本次, 5 项零漂移条件精确)

Composer Production              🔴 BLOCKED (5 项未完成)
P0-1 完整闭环                     🔴 NOT CLOSED
SHIJIAN Event-Signal             🔴 FAIL / FROZEN
G1                               🔒 LOCKED (实测非 G1 bug)
RenderStage                      🔒 不必修改 (User 红线 "不因 Composer 接入而改")
mapping_registry                 ⚠️ 需 admission + 词库扩容 (待 User 决策)
GitHub push                      🔴 暂不推 (18 commits 本地领先)
```

---

## 6. 待你裁决

### 6.1 15.19 实测结论接受？

特别确认：
1. **mapping_registry 10 条全 draft** —— 当前 0 条 mapping 进生产链
2. **AC-ZP-* namespace 完全不识别** —— mapping_registry 是 rule_ref 交集机制
3. **RenderStage 本身不必修改**（User 红线维持）
4. **5 项零漂移条件中 1 已完成**（Composer S4），4 项需后续 Stage

### 6.2 下一步（按 B → C → D 顺序）

按 User 已锁定顺序，最后一项 = **15.20 Admission Architecture Audit**——
评估 5 项零漂移条件的施工路径（X/Y/Z 与 mapping admission gate），形成最终 P0-1 闭环裁决。

继续启动 **15.20 Admission Architecture Audit**？

*Generated by BOT-MASTER on 2026-09-11*
*Code Change = 0 / Evidence Change = 0 / Rule Change = 0 / Algorithm Change = 0*
*探针脚本 (scripts/audit_15_19_render.py) 已删除*
*12 项实测（mapping_registry + RenderStage + G1 + Composer 联动）*
