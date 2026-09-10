# BZ-FNDR-15.18 — Rule Admission Audit (21 Ziping Rules)

> **Audit-only / Code=0 / Evidence=0 / Rule=0 / Algorithm=0 / 单文件审计记录**
>
> 前置：15.17b commit `6acca0bc` 锁定 Layer 2 修正（21/21 全部命中但全 status=draft）
> User 2026-09-11 授权 15.18：逐条检查 21 条 Ziping rule IDs 的 admission metadata
>
> **12 项审计目标** (User 锁定)：
> rule ID / 经典 / status / layer / rule definition / evidence refs / evidence provenance /
> classical source / verification status / 加载状态 / admission criteria / 独立验证状态

---

## 0. 元数据

| 项 | 值 |
|---|---|
| 审计 ID | BZ-FNDR-15.18 |
| 前置 | 15.17b |
| 探针 | `scripts/audit_15_18_ziping_rules.py` + `.json`（一次性, 探针脚本不入 commit） |
| 状态 | **AUDIT COMPLETE** |

---

## 1. 关键修正（与 15.17b 进一步修正）

15.17b 实测说"21/21 全部 status=draft"——**这是错的**。本审计实测：

```
21 个 Ziping rule IDs status 分布:
  active: 8
  draft:  13
```

### 1.1 8 条 ACTIVE（实测全部 ZIPING-ZHENQUAN book）

```
ZPZ-101  印绶当令 → SUPPORT             (子平真诠·月令司权)
ZPZ-105  官杀当令 → CONSTRAINT          (子平真诠·月令司权)
ZPZ-106  正官格 → CONSTRAINT            (子平真诠·格局判定)
ZPZ-107  七杀格 → CONSTRAINT            (子平真诠·格局判定)
ZPZ-108  正印格 → SUPPORT               (子平真诠·格局判定)
ZPZ-110  伤官格 → OUTPUT                (子平真诠·格局判定)
ZPZ-111  正印当令且主气透干 → SUPPORT   (子平真诠·格局判定)
ZPZ-120  七杀当令且主气透干 → CONSTRAINT(子平真诠·格局判定)
```

**关键观察**：8 条 ACTIVE 全是 `子平真诠` book，分布 **book-by-book 分阶段 admission**——子平真诠已完整 admission，其他 3 本（滴天髓/三命通会/渊海子平）的 13 条仍在 draft。

### 1.2 修正后的真实状态

```text
21 个 Ziping rule IDs 状态分布:
  子平真诠 (ZIPING-ZHENQUAN)  book: 8/8 active ✅ admission 完成
  滴天髓   (DITIANSUI)        book: 7 条 全 draft
  三命通会 (SANMING-TONGHUI)   book: 3 条 全 draft (含 SMTH-101~103)
  渊海子平 (YUANHAI-ZIPING)   book: 3 条 全 draft (含 YHZP-101/104/105)
```

---

## 2. 逐项实测结果（13 个审计面）

### 【1】加载状态 (Production RuleLoader)

```text
21 个 Ziping rule IDs:
  两树都存在 (A & B):      21
  仅 tree A (backend/data):  0
  仅 tree B (data):         0
  Production RuleLoader 可加载: 21/21
```

✅ 21/21 全部被 Production RuleLoader 加载（不依赖 Option A/B 切换）。

### 【2】status 分布（修正 15.17b）

```text
draft:  13 (DTS 系 7 + YHZP 3 + SMTH 3)
active:  8 (ZPZ 全部)
validated: 0
```

**`status` 是 rule 自身的 enum，不等于 admission_scope**（见 §3 重要区分）。

### 【3】applies_to_layers

```text
全部 'BASELINE': 21/21
```

✅ 无 EVENT_TOPIC / DAILY_ACTIVATION——Ziping rules 不参与事件判断（与 SHIJIAN fail-closed 一致）。

### 【4】Book / Passage / Concept / Principle 完整性

```text
缺 book_id:    0 条 ✅
缺 passage_id: 0 条 ✅
缺 concept_id: 0 条 ✅
缺 principle_id: 6 条 → ['SMTH-101', 'SMTH-102', 'SMTH-103', 'YHZP-101', 'YHZP-104', 'YHZP-105']
```

⚠️ **6 条 principle_id 缺失** 全在三命通会 + 渊海子平 系（draft 系），暗示这 6 条 metadata 不完整。

### 【5】book_id 分布（经典归属）

```text
ZIPING-ZHENQUAN: 8  (子平真诠)
DITIANSUI:       7  (滴天髓)
SANMING-TONGHUI: 3  (三命通会)
YUANHAI-ZIPING:  3  (渊海子平)
```

✅ 4 本经典全覆盖。

### 【6】source.work 经典出处

```text
子平真诠: 8
滴天髓:   7
三命通会: 3
渊海子平: 3
```

✅ 21 条全部有完整经典出处。

### 【7】evidence_refs 完整性

```text
无 evidence_refs 的规则: 0 条
21 条全部至少有 1 个 evidence_refs 字段
```

✅ rule 层面 evidence_refs 全有。但**反义复用问题仍存在**：3 个 evidence ID（E-DTS-102-001, E-SMTH-102-001, E-YHZP-105-001）在生产 evidence_ids 集合中不存在（15.17 §1.3 命中 18/21）。

### 【8】spec_decisions_ref（spec 决策引用）

```text
('DECISION-002', 'DECISION-006', 'DECISION-009'): 13  ← DTS/SMTH/YHZP 全 draft 系
('DECISION-002', 'DECISION-006'):                8  ← ZPZ active 系
```

🔍 draft 系多引用 DECISION-009 (推测是 admission gate 决策)，active 系只引用 DECISION-002 + DECISION-006。

### 【9】version

```text
全部 0.2.0: 21 条
```

✅ 版本一致，无版本漂移。

### 【10】created_at

```text
2026-08-17: 8 条 (ZPZ 系 active)
2026-08-19: 11 条 (DTS/SMTH 系 draft)
2026-08-26: 2 条 (YHZP 系 draft, 最晚)
```

🔍 **ZPZ 系最早创建 (8-17)，最先升 active**——印证 book-by-book admission 时序。

### 【11】forbidden_inferences

```text
有 forbidden_inferences 的规则: 0 / 21
```

⚠️ 全部 21 条 Ziping rules **无 forbidden_inferences 字段**。其他 production rules (e.g. CRR/EDU/HH) 通常有非空 forbidden_inferences。**这意味着 Composer claims 引用 Ziping rule_refs 时，无法用 forbidden_inferences 阻止 G2 后续不当推理**。

### 【12】完整 JSON dump

探针已保存到 `scripts/audit_15_18_ziping_rules.json`，21 条规则完整 metadata 可供后续审计调用。

---

## 3. ⚠️ 关键架构发现：两套规则宇宙

实测中发现 production_assertion_rules.json 与 backend/data/rules/*.json **是两条互不相干的规则准入路径**：

### 3.1 production_assertion_rules.json 路径（10 条 ASR-PROD-*）

```json
{
  "rule_id": "ASR-PROD-ZHI_YIN",
  "provenance": {
    "verification_scope": "PRODUCTION_ADMITTED",
    "verified_by": {
      "identity_type": "GPT",
      "identity_id": "gpt-adjudicator-v1",
      "authority_source": "architecture-governance",
      "credential_hash": "schema-v1-arch-gov-2026"
    },
    "verification_version": "2026.09"
  }
}
```

**完整 admission metadata**：verification_scope + verified_by(GPT agent) + credential_hash。
**与 P2.1-F Authority Credentials 链路绑定**（test conftest.py 注入）。

### 3.2 backend/data/rules/*.json 路径（136 条 Ziping + 其它）

DTS-101.json 完整字段：
```json
{
  "rule_id": "DTS-101",
  "status": "draft",           ← rule 自身 enum, 不是 admission_scope
  "evidence_refs": [...],       ← rule 引用 evidence, 不是 verified_by metadata
  "spec_decisions_ref": [...]   ← spec 阶段引用, 不是 admission agent
}
```

⚠️ **0 admission metadata**——没有 verification_scope / verified_by / credential_hash。

### 3.3 两条路径完全分离（实测）

| 维度 | ASR 路径 | 传统 rules 路径 |
|---|---|---|
| 数量 | 10 条 | 136 条（含 Ziping 21） |
| 准入 | verification_scope + verified_by agent | status enum (draft/active) |
| Agent | GPT adjudicator (audit-able) | 无 (self-claimed) |
| Hash 绑定 | credential_hash | 无 |
| 推到 G1 链路 | `_meta.declared_credential_hash` → 加载时验证 | 无验证 |

→ **Ziping rules 不在 P2.1-F Authority 链路上**。即使 status=active，**没有 agent verified_by metadata**，所以 "active" 不能等同于 "production_admitted"。

---

## 4. Rule Admission 实测判据

### 4.1 实测 P2.1 系列 admission 链路（assertion_rule_library.py + admission_registry.py）

```python
class AdmissionScope(str, Enum):
    TEST_FIXTURE = "TEST_FIXTURE"     # 测试夹具
    SOURCE_VERIFIED = "SOURCE_VERIFIED"  # 来源已核实
    PRODUCTION_ADMITTED = "PRODUCTION_ADMITTED"  # 生产已准入

class RuleProvenance:
    @property
    def is_production_admitted(self) -> bool:
        return self.verification_scope == VerificationScope.PRODUCTION_ADMITTED
```

**这些判据只对 `assertion_rule_library` 的 RuleProvenance 生效**——`ProductionRuleLoader` 加载的传统 rules **不进入这条链路**。

### 4.2 现行 Ziping admission 判据（实测 = RuleLoader.status）

```python
# schema/rule.schema.json L120-122
"status": {
  "enum": ["draft", "review", "validated", "active", "deprecated"]
}
```

→ `active` ≠ `PRODUCTION_ADMITTED`。两个不同的枚举，**没有任何代码把 status=active 映射到 admission_scope=PRODUCTION_ADMITTED**。

---

## 5. 核心结论

### 5.1 21 条 Ziping rules 的 admission 现状

```text
已具备生产面形式条件:
  ✅ Production RuleLoader 加载 (21/21)
  ✅ evidence_refs 全有 (21/21)
  ✅ book/passage/concept 全有 (21/21 partial: 6 缺 principle_id)
  ✅ status=active 部分 (8/21 仅 ZPZ 系)
  ✅ applies_to_layers=['BASELINE'] (21/21)

未具备生产面 authority 条件:
  ❌ 0 admission_scope (none has verification_scope field)
  ❌ 0 verified_by (none has verified_by agent)
  ❌ 0 credential_hash (none bound to P2.1-F agent chain)
  ❌ 6 条缺 principle_id (metadata 不全)
  ❌ 0 条有 forbidden_inferences (防护字段缺失)

当前 status=active 的 8 条 ZPZ:
  - "active" 仅表示 spec 已通过 review
  - 不等于 production_admitted
  - 进入 G1 时没有 audit agent 链路背书
```

### 5.2 User 已锁定红线的直接证据

> "G1 PASS ≠ Rule Admission PASS" (User 2026-09-11 锁定)

实测坐实：G1 只校验 4 项硬门槛（rule_refs/evidence_refs/source_layers/claim_id 前缀），
**完全不校验 admission_scope 或 verified_by**。

→ **G1 通过 ≠ production_admitted**——但因为 21 条 Ziping rules 不带 admission metadata，
即便 G1 通过，它们的"生产权威性"也无独立审计追溯。

### 5.3 修正后的 Layer 2 架构结论

```text
Layer 2 (本次修正):
  不是 "两个 authority 世界的合并" (15.17b 误判)
  而是 "传统 rules 路径 0 admission metadata，
        生产 authority 完全依赖 ASR 路径
        Ziping rules 处于 'status=active 但无 admission_scope' 的中间态"

正确表述 (User 锁定的延伸):
  "21 条 ZiPing rules 已被 Production RuleLoader 加载，
   8 条 status=active (ZPZ 系) 但 0 条 verification_scope=PRODUCTION_ADMITTED，
   全部 0 条 verified_by agent，
   → 'Loaded' ≠ 'Production-Admitted'。
   → Rule Admission 必须走 ASR 路径或建立新 admission 路径才能闭合。"
```

---

## 6. 后续步骤（不替 User 拍板）

### 6.1 路径选择空间

```text
路径 X: 把 21 条 Ziping rules 接入 ASR admission 路径
  - 创建 ASR-PROD-ZIPING-* 包装条目
  - 或为每条 Ziping rule 添加 verification_scope + verified_by metadata
  - 但 P2.1-F 链路要求 agent identity (GPT/HUMAN)
  - 谁来 verify? BOT-MASTER 不可 (无 authority)
  - 人类审计师? 需要 User 授权

路径 Y: 扩 RuleLoader admission 检查
  - RuleLoader 加载时强制 status ∈ {validated, active} + admission_scope = PRODUCTION_ADMITTED
  - 当前 RuleLoader 不做此检查
  - 扩展 = 改 RuleLoader, 触发 Stage 1 红线

路径 Z: 把 21 条 Ziping rules 降级为非生产
  - status='deprecated' 或从生产加载列表排除
  - Composer 永远无法引用
  - 但 judgment.py 内部使用 → judgment.py 必须修改
  - 触发 15.18b Judgment Algorithm Audit

路径 W: 维持现状
  - Composer Production 永远 BLOCKED
  - P0-1 永远 NOT CLOSED
  - 但 T-3 稳定 (D 状态)
```

### 6.2 当前事实建议（不替 User 拍板）

```text
事实 1: 21 条 Ziping rules 缺失 admission metadata (0 verification_scope, 0 verified_by)
事实 2: 8 条 active + 13 条 draft 都不等于 production_admitted
事实 3: Composer activation 必须先解决 Ziping rules admission
事实 4: 解决 admission = 路径 X/Y/Z 之一, 每个都触发红线
事实 5: 维持 W (Composer OFF) 是当前最稳

P0-1 真正闭环条件 (修正):
  - Path X 完成 (Ziping rules admission metadata 完整)
  + Path 15.18b 完成 (Judgment 算法 refs 完整性)
  + Path 渲染完成 (mapping_registry 词库覆盖 AC-ZP-*)

这是 3 个独立审计 + 各自决策的组合, 不是单一一项能闭环。
```

---

## 7. 当前门状态

```text
G0-1 Index                       🟢 PASS
G0-2 Provenance                  🟢 PASS
INT-01~03 Stage 1                🟢 CLOSED
INT-05 Composer Module           🟢 MODULE PASS
INT-06 接入点                     🟢 CODE PASS
15.17 Activation Contract        🟢 AUDIT COMPLETE
15.17b Rule ID Investigation     🟢 AUDIT COMPLETE (含 Layer 2 修正)
15.18 Rule Admission Audit       🟢 AUDIT COMPLETE (本次, 21/21 admission metadata 缺失坐实)

Composer Production              🔴 BLOCKED (需 Path X/Y/Z + 15.18b + Render mapping)
P0-1 完整闭环                     🔴 NOT CLOSED (3 个独立路径未闭合)
SHIJIAN Event-Signal             🔴 FAIL / FROZEN
G1                               🔒 LOCKED (实测非 G1 bug)
RenderStage                      🔒 LOCKED
mapping_registry                 🔒 不为 Composer 接入而修改
GitHub push                      🔴 暂不推 (16 commits 本地领先)
```

---

## 8. 待你裁决

### 8.1 15.18 实测结论接受？

特别是：
1. **修正 15.17b**：21/21 不是全 draft，是 **8 active + 13 draft**
2. **新发现**：21 条 Ziping rules **0 admission metadata** (无 verification_scope, 无 verified_by, P2.1-F 链路完全不挂)
3. **G1 PASS ≠ Rule Admission PASS** 红线坐实（G1 不校验 admission）

### 8.2 下一步方向

| 选项 | 内容 | 红线触发 |
|---|---|---|
| A | 维持 W (Composer OFF)，承认 P0-1 NOT CLOSED 为已知架构债 | ✅ 维持 |
| B | 启动 **15.18b Judgment Algorithm Audit**（User 明确建议第二步） | ⚠️ 不直接触发红线但探 judgment.py 算法 |
| C | 启动 **15.19 RenderStage Mapping Audit**（AC-ZP-* 词库覆盖可行性） | ⚠️ 不直接改 RenderStage |
| D | 启动 **15.20 Ziping Admission Architecture Audit**（评估 X/Y/Z 路径） | ⚠️ 决策层 |

我作为 BOT-MASTER 的事实建议是 **B → C → D** 顺序（User 已锁定 B 第二步），逐项关闭阻塞点。

*Generated by BOT-MASTER on 2026-09-11*
*Code Change = 0 / Evidence Change = 0 / Rule Change = 0 / Algorithm Change = 0*
*探针 (scripts/audit_15_18_ziping_rules.py + .json) — 一次性, 不入 commit*
*21 条 Ziping rules admission metadata 完整盘点 + 两套规则宇宙分离坐实*
