# PATCH-003B：六经典逐章节 Evidence Verification（启动文档）

> 日期：2026-09-16 ｜ Human 批准：APPROVED ｜ 第一准则：V2.22 FINAL + 附录 A–M
> 前置：R1-05 VERIFIED_SCOPE 收官 PASS（commit `da0397da`）

---

## 一、R1-05 冻结边界（Human 2026-09-16 裁决，禁止违反）

```
VERIFIED_SCOPE → 自动生成 RULE        ✗ 禁止
原文 → Scope → Rule Admission → Business Judgment    ✓ 唯一通道
```

### ① 基础五行 / 十神 / 生旺休囚 / 根气 / 党众 —— PASS
- **根气**：`ROOT ≠ DAY_MASTER_ONLY`，对象必须解析：
  `ROOT(object=日主) / ROOT(object=官) / ROOT(object=财) / ROOT(object=杀) / ROOT(object=印)`
- 禁止 `has_root(day_master)` 作为通用强弱开关。

### ② 生扶克泄耗 / 气势 / 调候 / 通关
- **通关**：`DTS_SCOPE_ONLY`。`DTS-019-001` 通关=ORIGINAL/A；其他经典 NOT_FOUND。
  - 禁止：YHZP引化=通关、QTBJ寒暖=通关、SFTK病药=通关。
  - `CONCEPT_SIMILAR ≠ CONCEPT_EQUAL`。
- **调候**：`QTBJ_PRIMARY_SCOPE` + `PZZQ_CONTEXTUAL_SCOPE`（PZZQ-007-003）+ 其他 SOURCE_CHECK_REQUIRED。
  - 禁止生成「统一调候喜忌算法」；必须带 `CLASSICAL_SCOPE=QTBJ`。

### ③ 格局成败 / 相神 / 顺逆
- **相神**：`PZZQ_ONLY`。`PZZQ-007-004`「月令既得用神，則別位亦必有相」；`xiangshen_state` 只能由 PZZQ Rule 注册；禁止「病药救应=相神」。
- **顺逆**：`DTS_PRIMARY`（DTS-025-001 顺其气势）；其他经典引用必须重新验证。

### ④ 干支组合 / 六亲 / 神煞 / 命例
- **神煞**：`EXCLUDED_FROM_RULE`。允许文献检索/参考展示；禁止命局核心裁决、用神判断、吉凶自动输出。
- **命例**：`REFERENCE_ONLY`。允许 Rule 验证/Golden Case/Regression Test；禁止从命例反推规则。

---

## 二、003B 新增两字段（已落库 governance/r1_05_verified_scope.json，25/25 领域）

### classical_usage_type
`FOUNDATIONAL | PRIMARY_RULE | SUPPORTING | CONTEXT_ONLY | REFERENCE_ONLY | EXCLUDED`

关键映射（Human 给定）：
| 概念 | 书 | 类型 |
|---|---|---|
| 用神 | PZZQ | PRIMARY_RULE |
| 病药 | SFTK | PRIMARY_RULE |
| 神煞 | YHZP/SMTH | EXCLUDED |
| 命例 | 六部 | REFERENCE_ONLY |
| 调候 | QTBJ | PRIMARY_RULE |
| 相神 | PZZQ | SUPPORTING（PZZQ_ONLY） |
| 通关 | DTS | SUPPORTING（DTS_SCOPE_ONLY） |

### rule_boundary
```json
{
  "allowed": ["PZZQ用神判断"],
  "forbidden": ["统一八字用神"]
}
```
防止 Agent 扩大解释。

---

## 三、003B 核验流程（目标 = Evidence Verification，不是找关键词）

逐章节检查，每条 source 核验链：

```
Source → Chapter → Text Layer → Attribution → Concept → Scope → Rule Eligibility
```

核验记录 schema（governance/patch_003b_evidence_checklist.json，已生成 130 条）：

```json
{
  "source_id": "DTS-019-001",
  "domains": ["tong_guan"],
  "chapter_verified": null,
  "text_layer_verified": null,
  "attribution_verified": null,
  "evidence_grade_verified": null,
  "usage_type_verified": null,
  "rule_boundary_ok": null,
  "verification_status": "PENDING",
  "note": ""
}
```

### 待核验清单规模（130 条）
| 书 | 条数 |
|---|---|
| YHZP | 24 |
| PZZQ | 17 |
| DTS | 35 |
| QTBJ | 14 |
| SMTH | 15 |
| SFTK | 25 |

> 第一批（f8f85498）9 领域原为早期 dict schema，已统一为 16 字段 cell；缺失字段（text_layer/object_type/semantic_role 等）标 `TO_VERIFY`，全部纳入 003B 核验清单。

---

## 四、执行要求（Human 冻结）

1. 六部逐章节核验（逐条回查原文，确认 text_layer/attribution/chapter/evidence_grade 与 Scope 一致）
2. 修正 Scope 遗漏（发现新证据 → 补入 r1_05_verified_scope.json 对应 cell）
3. 建立 Rule Admission 边界（每条核验通过的 source 输出 usage_type + rule_boundary）
4. **不开发算法**
5. **不生成业务判断**

## 五、003B 完成后才允许进入

```
旺衰 / 强弱 / 用神 / 格局 算法设计
```
该阶段必须依赖 003B 最终边界，禁止把六部经典"融合成一本书"。

---

## 六、核验顺序（按冻结批序反向核验，从最关键概念开始）

1. 用神（PZZQ-007-004 等）→ 病药（SFTK）→ 调候（QTBJ）→ 通关（DTS）
2. 格局成败 → 相神 → 顺逆
3. 旺强衰 → 令时地根 → 势
4. 其余领域顺序核验

## PATCH-003B 第一轮核验结果（commit 待）

### 状态汇总
- 待核验 130 条（YHZP 24 / PZZQ 17 / DTS 35 / QTBJ 14 / SMTH 15 / SFTK 25）
- **VERIFIED 129 条**（原文库存在，text_layer/evidence_grade/attribution 回查一致）
- **RESOLVED_NOT_FOUND 1 条**（SMTH-030-002）

### 关键修正：SMTH-030-002 引用不实
- 第 5 批落档时引用的 SMTH「地支至切，黨盛為強」**原文库不存在**——003B 核验抓出
- SMTH 实际「黨」命中均为神煞/日时断语语境（財黨煞等），无干支组合 A 级总纲
- 按铁律修正：NOT_FOUND/FAIL_CLOSED，excluded_scope 注明「日时断语为条件变量，不得作干支组合总纲」
- 教训：不得凭印象引用，evidence 必须可回查

### 第一批 schema 统一
- 第一批 9 领域原为早期 dict schema → 已统一为 16 字段 cell（49 cell）
- TO_VERIFY 字段从原文回填：text_layer/evidence_grade/attribution/chapter_id（49/49 清零）

### 层级一致性比对
- 158 条（含多领域重复引用）scope 期望 vs 原文实际 = 一致，0 不一致
- 无 A/B 级错标、无 attribution 错配

### 产物
- governance/r1_05_verified_scope.json：25 领域 16 字段 + classical_usage_type + rule_boundary + 回填完成
- governance/patch_003b_evidence_checklist.json：130 条核验记录（VERIFIED/RESOLVED_NOT_FOUND）
