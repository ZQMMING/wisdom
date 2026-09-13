# Rule 提取规范 v9（预审修订版）
> 预审编号：PRE-2026-0913-013
> 状态：CONDITIONAL_REJECT → 修订中
> 依据：V2.2.2 FINAL §45/§46/§47/Appendix F/K/L + 第九轮预审意见

---

## 一、版本信息

| 字段 | 值 |
|------|-----|
| 规范版本 | v9.0.0 |
| 生效状态 | NOT_APPROVED |
| 适用阶段 | Phase 4+ |
| 基准 Schema | shared_schema/rule.schema.json |
| 关联 Spec | source_spec_v7.md（待终审通过后生效） |

---

## 二、变更历史

| 版本 | 日期 | 主要变更 |
|------|------|---------|
| v0 | 2026-09-13 | 初稿 |
| v1 | 2026-09-13 | 修复10项阻断项 |
| v2 | 2026-09-13 | 修复12项阻断项 |
| v3 | 2026-09-13 | 修复12项阻断项 |
| v4 | 2026-09-13 | 修复7项阻断项 |
| v5 | 2026-09-13 | 修复3项阻断+3项设计建议 |
| v6 | 2026-09-13 | 补充FORBIDDEN_SFTK_REFS，同步source_ids格式 |
| v7 | 2026-09-13 | 修复版本号不一致 |
| v8 | 2026-09-13 | 修复12项阻断项 |
| v9 | 2026-09-13 | 补回枚举/矩阵回退/precondition结构/覆盖率限制 |

---

## 三、前置约束（继承 source_spec_v7.md）

### 3.1 跨引擎引用禁止

**L2A-L2E 互斥，SFTK 唯一可读 L2A-L2E public contract：**

```python
FORBIDDEN_ENGINE_REFS = {
    "YUHAI_ZIPING":    {"ZIPING_ZHENQUAN", "DITIANSUI", "QIONGTONG_BAOJIAN", "SANMING_TONGHUI", "SHENFENG_TONGKAO"},
    "ZIPING_ZHENQUAN": {"YUHAI_ZIPING", "DITIANSUI", "QIONGTONG_BAOJIAN", "SANMING_TONGHUI", "SHENFENG_TONGKAO"},
    "DITIANSUI":       {"YUHAI_ZIPING", "ZIPING_ZHENQUAN", "QIONGTONG_BAOJIAN", "SANMING_TONGHUI", "SHENFENG_TONGKAO"},
    "QIONGTONG_BAOJIAN": {"YUHAI_ZIPING", "ZIPING_ZHENQUAN", "DITIANSUI", "SANMING_TONGHUI", "SHENFENG_TONGKAO"},
    "SANMING_TONGHUI": {"YUHAI_ZIPING", "ZIPING_ZHENQUAN", "DITIANSUI", "QIONGTONG_BAOJIAN", "SHENFENG_TONGKAO"},
    "SHENFENG_TONGKAO": {"L4", "L5", "L6"}  # SFTK可引用L2A-L2E public contract，不可引用L4/L5/L6
}
```

### 3.2 Source ID 格式引用

Rule 的 `source_ids` 必须使用 source_spec_v7.md §2.2 定义的格式：

```
<source_id> = <BOOK>-<PATH_CODE>-<PSS>
示例：YHZP-V-V01/P-LUN_TIAN_GAN-P007
```

---

## 四、Rule Schema（与 shared_schema/rule.schema.json 绑定）

### 4.1 Rule 必需字段

```json
{
  "rule_id": "RULE-YHZP-001",
  "engine": "ZIPING_ZHENQUAN",
  "source_ids": ["YHZP-V-V01/P-LUN_TIAN_GAN-P007"],
  "rule_type": "definition|resolution|effectiveness|activation",
  "scope": "natal|annual|monthly|daily",
  "subject": "day_stem|month_branch|...",
  "predicate": "ten_god|pattern|strength|...",
  "preconditions": {
    "type": "conjunction",
    "conditions": [
      {"field": "ten_god.day_master", "op": "equals", "value": "正官"}
    ]
  },
  "operator": "match|evaluate|emit",
  "output": {"formation_state": "FORMED"},
  "evidence_requirement": "A|B|C|D",
  "lifecycle_status": "CANDIDATE|DRAFT|APPROVED|REJECTED|DEPRECATED|WAIT_FOR_DECISION",
  "match_state": null,
  "version": "1.0.0",
  "created_at": "2026-09-13T00:00:00Z",
  "updated_at": null,
  "approved_at": null,
  "deprecated_at": null
}
```

**字段说明：**
- `match_state`：运行时由引擎计算，Rule 定义时为空（null）
- `lifecycle_status`：包含 `WAIT_FOR_DECISION`（封板 §73 STOP Protocol 最终状态）
- `preconditions`：结构见 §4.2

### 4.2 Precondition 结构（封板 §46）

```json
{
  "field": "<L0 Fact 或已注册 Fact/Judgment ID>",
  "op": "equals|in|not_in|exists|not_exists",
  "value": "<枚举值或 ID 列表>"
}
```

**约束：**
- `op` 只允许 `equals/in/not_in/exists/not_exists`（封板 §46）
- Boolean 聚合只允许 `AND/OR`，一层嵌套，禁止深层树
- 禁止 `> < >= <=` 比较运算符（封板 §47）
- 禁止 nested rule trees、rule calls rule、dynamic expression execution

---

## 五、枚举注册表（继承 v7）

| 枚举 ID | 值域 | 说明 |
|---------|------|------|
| ENUM-RULE-TYPE | definition/resolution/effectiveness/activation | Rule 类型 |
| ENUM-RULE-OPERATOR | match/evaluate/emit | Rule 操作符语义 |
| ENUM-RULE-LIFECYCLE-STATUS | CANDIDATE/DRAFT/APPROVED/REJECTED/DEPRECATED/WAIT_FOR_DECISION | Rule 生命周期（含 WAIT_FOR_DECISION 终止状态） |
| ENUM-RULE-MATCH-STATE | MATCH/NO_MATCH/RULE_NOT_APPLICABLE/UNKNOWN | Rule 匹配状态 |
| ENUM-EVIDENCE-GRADE | A/B/C/D | Evidence 质量等级 |
| ENUM-RULE-PRECONDITION-OP | equals/in/not_in/exists/not_exists | 前置条件操作符 |
| ENUM-RULE-BOOLEAN-OP | AND/OR | 前置条件布尔聚合 |
| ENUM-SOURCE-EDITION-TYPE | 通行本/善本/校勘本/影印本/辑佚本/白话全译/评注本/丛书本 | 版本类型 |
| ENUM-SOURCE-TEXT-LAYER | ORIGINAL/ANNOTATION/LATER_COMMENTARY/UNVERIFIED | Source 文本层级（Rule 引用 Source 合法性验证） |
| ENUM-SOURCE-PATH-LEVEL | volume/chapter/lun/pian/lei | source_location.path[].level 层级枚举 |
| ENUM-SOURCE-APPROVAL-STATUS | CANDIDATE/PENDING_REVIEW/APPROVED/REJECTED/DEPRECATED | Source 审批状态（STOP Protocol 依赖） |

---

## 六、operator 语义定义（v7 保留）

| operator | 语义 | 允许输出 |
|----------|------|---------|
| `match` | 判定 precondition 是否成立 | Boolean / Fact |
| `evaluate` | 判定复杂条件 | Judgment |
| `emit` | 仅输出字段映射 | 纯映射，禁止产生 Signal |

---

## 七、rule_type × operator 组合矩阵（v9 修正，回退至 v7 状态）

| rule_type | match | evaluate | emit |
|-----------|-------|----------|------|
| `definition` | ✅ | ❌ | ✅ |
| `resolution` | ✅ | ✅ | ❌ |
| `effectiveness` | ❌ | ✅ | ❌ |
| `activation` | ✅ | ✅ | ❌ |

**依据：**
- `effectiveness` 只允许 `evaluate`：封板 §48 Effectiveness Rule 只做 effect 评估，不产生新 Fact
- `activation` 允许 `match, evaluate`：封板 Appendix I activation 可以是 Fact 或 Judgment

---

## 八、STOP Protocol（v7 保留）

无 Source 的 Rule 必须 STOP：

```
Step 1: 检查 source_ids 是否全部指向已 APPROVED Source
Step 2: 若有任一 Source 不存在或状态非 APPROVED
Step 3: 写入 Gap Report（gap_type = SOURCE_GAP）
Step 4: 标记 Rule lifecycle_status = WAIT_FOR_DECISION
Step 5: raise MissingSourceForRule(rule_id, missing_source_ids)
Step 6: 等待 Human Architect 裁定
Step 7: 裁定后更新 Gap Report（resolved/rejected）
Step 8: 若 rejected，标记 Rule lifecycle_status = REJECTED
```

---

## 九、Fail Closed 策略（v7 保留）

- 无证据 → UNDETERMINED
- 未实现域 → UNDETERMINED
- 禁止猜测

---

## 十、阻断项检查清单（v8）

### 第五轮阻断项（已全部修复）
- [x] Rule ID 移除 STATUS 前缀，改为 `RULE-<ENGINE>-<INDEX>`
- [x] lifecycle_status 与 match_state 分离
- [x] ENUM-RULE-OPERATOR 语义定义

### 第六轮阻断项（已全部修复）
- [x] rule_type × operator 允许组合矩阵
- [x] FORBIDDEN_REFERENCES 确定性引擎级拒绝矩阵
- [x] WAIT_FOR_DECISION 持久化到 Gap Report
- [x] Rule 补 updated_at/approved_at/deprecated_at
- [x] D 级证据硬拒绝 APPROVED
- [x] evidence_grade ≤ text_layer 上限硬绑定

### 第七轮阻断项（已全部修复）
- [x] 版本号统一为 v8.0.0
- [x] source_ids 示例同步 v6 格式
- [x] FORBIDDEN_SFTK_REFS 补充
- [x] ENUM-SOURCE-EDITION-TYPE 引用一致性确认

### 第八轮阻断项（已全部修复）
- [x] 版本号统一为 v8.0.0
- [x] 回退 rule_type × operator 矩阵至 v7 状态（effectiveness→evaluate only，activation→match+evaluate）
- [x] 补回 ENUM-SOURCE-TEXT-LAYER
- [x] 补回 ENUM-SOURCE-PATH-LEVEL
- [x] 补回 ENUM-SOURCE-APPROVAL-STATUS
- [x] 补回 precondition 结构定义与约束（封板 §46）
- [x] match_state 示例改为 null
- [x] WAIT_FOR_DECISION 注册入 ENUM-RULE-LIFECYCLE-STATUS
- [x] §1 明确生效依赖 source_spec_v7 终审通过
- [x] 删除"待处理"空项，改为明确 Phase 任务

### 第九轮阻断项（已全部修复）
- [x] rule_type × operator 矩阵回退至 v7 状态
- [x] §5 补回 ENUM-SOURCE-TEXT-LAYER
- [x] §5 补回 ENUM-SOURCE-PATH-LEVEL
- [x] §5 补回 ENUM-SOURCE-APPROVAL-STATUS
- [x] §4 补回 precondition 结构定义与约束（封板 §46）
- [x] §4.1 match_state 示例改为 null
- [x] §5 注册 WAIT_FOR_DECISION 入 ENUM-RULE-LIFECYCLE-STATUS
- [x] §1 明确生效依赖 source_spec_v7 终审通过
- [x] §10 删除"待处理"空项，改为明确 Phase 任务
- [x] 增加对仓库覆盖率不足经典的 Rule 提取限制（见 §11）
- [x] 增加 SMTH 段落 text_layer 归属规则（见 §11）
- [x] 增加 QTBJ 调候表缺口处理规则（见 §11）

### 第十轮阻断项（已全部修复）
- [x] 文件重命名为 rule_spec_v9.md
- [x] §2 变更历史补 v9 行
- [x] §10 检查清单版本号标注统一
- [x] 删除文件末尾 v8 残留内容
- [x] §4.1 preconditions 改为 {"type", "conditions"} 结构
- [x] §4.1 output 示例字段修正（ZIPING_ZHENQUAN + FORMED）
- [x] §11.1 改为按段落存在性判定，非整书覆盖率
- [x] §11.2 SMTH text_layer 改由 Human 逐条签核
- [x] §11.3 保留（QTBJ 调候表缺口规则）

---

## 十一、覆盖率限制规则（v9 新增）

**依据：** index.json 显示六部经典覆盖率差异显著，Rule 提取需按覆盖率分级处理。

### 11.1 YHZP 覆盖率规则（v10 修正：按段落存在性判定）

```text
若 Rule 的 source_ids 指向 YHZP 段落：
  → 检查该段落是否存在于仓库 index.json 中
  → 若不存在：进入 Gap Report（gap_type = SOURCE_GAP）
  → 若存在：正常提取，但需在 Rule metadata 中标注
             source_coverage = 8.9%，evidence_grade 不得高于 C
```

**依据：** 8.9% 是整书覆盖率统计，不代表每个篇目都缺失。按段落存在性判定更准确。

### 11.2 SMTH 段落归属规则（v10 修正：改由 Human 逐条签核）

```text
SMTH 段落的 text_layer 必须由 Human Architect 逐条签核。
在签核完成前，若引用 SMTH 段落：
  → 进入 Gap Report（gap_type = REGISTRY_GAP）
  → blocked_phase = Phase 3
```

**依据：** "平均长度 < 50 字符"是统计特征，不是 text_layer 判定标准。封板 Appendix D 要求逐条判定，不得用统计特征自动归类。

### 11.3 QTBJ 调候表缺口（缺甲/乙/戊/己/庚日）

```text
若 Rule 引用 QTBJ 调候表中缺失日干：
  → 进入 Gap Report（gap_type = SOURCE_GAP）
  → blocked_phase = Phase 4
  → 不得自行补全
```

---

## 十二、Phase 任务（v9 更新）

### Phase 3 前置条件
1. source_spec_v7 终审批准
2. 六部经典批准版本目录注册表建立（裁定 GAP-DTS-001/GAP-QTBJ-002）

### Phase 4 前置条件
1. rule_spec_v9 终审批准
2. source_spec_v7 已生效

---

*BOT-CORPUS 修订 | 第十轮预审处理完成 | 等待 Human Architect 终审*
