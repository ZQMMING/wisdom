# Phase B-0: Rule Authorization Audit

**任务 ID**: T-ENGINE-BAZI-002 Phase B-0  
**执行者**: @bot-ziping  
**日期**: 2026-09-06  
**状态**: 🔄 IN PROGRESS - Per-Rule Provenance Audit

---

## 执行摘要

根据 BOT-MASTER 裁决，执行 **Phase B-0: Rule Authorization Audit**。

**核心原则**:
- 所有 32 条规则标记为 `CANDIDATE`（草稿状态）
- 禁止进入生产执行
- 每条规则必须绑定具体 Evidence ID
- 禁止使用全局权威排名，改用域特定权威

---

## 一、Rule State Machine

### 1.1 规则状态流转

```
DRAFT → EVIDENCE_VERIFIED → ADJUDICATED → AUTHORIZED → PRODUCTION
  ↑         ↓                    ↓            ↓
  └─────────┴────────────────────┴────────────┘
              REJECTED / REVISION NEEDED
```

| 状态 | 说明 | 是否允许执行 |
|------|------|--------------|
| DRAFT | 草稿，未验证 | ❌ |
| EVIDENCE_VERIFIED | 已验证证据来源 | ❌ |
| ADJUDICATED | 已通过冲突裁决 | ❌ |
| AUTHORIZED | 授权生产使用 | ⚠️ 需 BOT-MASTER 裁决 |
| PRODUCTION | 实际执行中 | ✅ |
| REJECTED | 被否决 | ❌ |

### 1.2 当前状态

**全部 32 条规则**: `DRAFT` (待证据验证)

---

## 二、权威体系重构

### 2.1 废弃全局权威排名

**原因**: "互补不比较"架构原则，不同经典在不同语义域承担不同职责。

**废弃设计**:
```python
# ❌ 废弃：全局排名
CLASSIC_AUTHORITY = {
    "ziping_zhenquan": 1,
    "yuan_hai_zi_ping": 2,
    ...
}
```

### 2.2 采用域特定权威

**新设计**:
```python
DOMAIN_AUTHORITY = {
    "wangshuai": {
        "di_tian_sui": "PRIMARY",           # 旺衰权威
        "yuan_hai_zi_ping": "SUPPORTING",   # 基础支持
        "ziping_zhenquan": "REFERENCE",     # 参考
    },
    "pattern": {
        "ziping_zhenquan": "PRIMARY",       # 格局权威
        "yuan_hai_zi_ping": "SUPPORTING",   # 基础支持
        "san_ming_tong_hui": "REFERENCE",   # 补充参考
    },
    "yongshen": {
        "qiong_tong_bao_jian": "PRIMARY",   # 调候权威
        "ziping_zhenquan": "PRIMARY",       # 格局用神
        "di_tian_sui": "SUPPORTING",        # 扶抑参考
    },
    "ten_god_semantics": {
        "yuan_hai_zi_ping": "PRIMARY",      # 十神基础
        "ziping_zhenquan": "SUPPORTING",    # 格局关联
    },
    "event": {
        "ziping_zhenquan": "PRIMARY",       # 事件判断
        "yuan_hai_zi_ping": "SUPPORTING",   # 基础支持
    },
}
```

### 2.3 优先级拆分

**废弃单字段 priority**:
```python
# ❌ 废弃：单字段
priority: int  # 1, 2, 3...
```

**新设计：多维度优先级**:
```python
@dataclass(frozen=True)
class RulePriority:
    """规则优先级维度"""
    execution_order: int           # 执行顺序（数字越小越先执行）
    conflict_precedence: int       # 冲突裁决优先级（数字越小越高）
    authority_level: str           # 权威等级：PRIMARY/SUPPORTING/REFERENCE
    specificity: int               # 特异性（越具体优先级越高）
    
    def __lt__(self, other):
        # 执行顺序优先，冲突裁决次之
        if self.execution_order != other.execution_order:
            return self.execution_order < other.execution_order
        return self.conflict_precedence < other.conflict_precedence
```

---

## 三、32 条候选规则逐条审计

### 3.1 旺衰域规则（11条）

#### ZIPING-RULE-WS-001: 得令判定

```yaml
rule_id: ZIPING-RULE-WS-001
name: 得令判定
domain: wangshuai
status: DRAFT
source_evidence:
  - evidence_id: E-DTS-101-001
    classic: di_tian_sui
    chapter: 任氏曰
    text: "干为天元，支为地元，支中所藏为人元..."
    extraction: "三元本体论 → 月令得气"
    confidence: 0.6  # 间接引用，非直接论述
condition:
  monthly_command: "得令"  # 月支五行生助或同于日主
output: SUPPORT
priority:
  execution_order: 1
  conflict_precedence: 1
  authority_level: SUPPORTING  # 滴天髓在旺衰域是PRIMARY，但此条为间接引用
  specificity: 1
classic_reference: 滴天髓·通神论
notes: "原文未直接论述'得令'概念，需从三元理论推论"
adjudication: PENDING
conflicts:
  - potential_conflict_with: "失令判定(WS-002)"
    resolution: "互斥条件"
```

#### ZIPING-RULE-WS-002: 失令判定

```yaml
rule_id: ZIPING-RULE-WS-002
name: 失令判定
domain: wangshuai
status: DRAFT
source_evidence:
  - evidence_id: E-DTS-101-001
    classic: di_tian_sui
    extraction: "三元理论推论"
    confidence: 0.5  # 间接引用
condition:
  monthly_command: "失令"  # 月支五行克或被日主克
output: CONSTRAINT
priority:
  execution_order: 1
  conflict_precedence: 1
  authority_level: SUPPORTING
  specificity: 1
classic_reference: 滴天髓·通神论（推论）
notes: "与WS-001互斥，覆盖所有月令情况"
adjudication: PENDING
```

#### ZIPING-RULE-WS-003: 通根判定

```yaml
rule_id: ZIPING-RULE-WS-003
name: 通根判定
domain: wangshuai
status: DRAFT
source_evidence:
  - evidence_id: E-YHZP-003-001
    classic: yuan_hai_zi_ping
    chapter: 论根气
    text: "根者，柱中之支也..."
    extraction: "地支藏干含日主 = 有根"
    confidence: 0.85
condition:
  root_present: true
  root_type: "any"  # 主气/中气/余气均可
output: SUPPORT
priority:
  execution_order: 2
  conflict_precedence: 2
  authority_level: SUPPORTING  # 渊海在旺衰域是SUPPORTING
  specificity: 2
classic_reference: 渊海子平·论根气
notes: "需明确'根'的定义：主气根 > 中气根 > 余气根"
adjudication: PENDING
```

#### ZIPING-RULE-WS-004: 无根判定

```yaml
rule_id: ZIPING-RULE-WS-004
name: 无根判定
domain: wangshuai
status: DRAFT
source_evidence: []  # 无直接证据，需推导
confidence: 0.3
condition:
  root_present: false
output: CONSTRAINT
priority:
  execution_order: 2
  conflict_precedence: 2
  authority_level: REFERENCE
  specificity: 2
classic_reference: 待定
notes: "从'通根判定'反向推导，需原典验证"
adjudication: PENDING
```

#### ZIPING-RULE-WS-005: 比劫帮身

```yaml
rule_id: ZIPING-RULE-WS-005
name: 比劫帮身
domain: wangshuai
status: DRAFT
source_evidence:
  - evidence_id: E-YHZP-005-001
    classic: yuan_hai_zi_ping
    extraction: "同类之阴阳 = 比劫"
    confidence: 0.75
condition:
  peer_count: ">= 2"  # 天干比劫数量
output: SUPPORT
priority:
  execution_order: 3
  conflict_precedence: 3
  authority_level: SUPPORTING
  specificity: 3
classic_reference: 渊海子平·论比肩
notes: "需明确'帮身'的定义：同五行同阴阳=比肩，不同阴阳=劫财"
adjudication: PENDING
```

#### ZIPING-RULE-WS-006: 印星生身

```yaml
rule_id: ZIPING-RULE-WS-006
name: 印星生身
domain: wangshuai
status: DRAFT
source_evidence:
  - evidence_id: E-YHZP-006-001
    classic: yuan_hai_zi_ping
    extraction: "生气之阴阳 = 印绶"
    confidence: 0.75
condition:
  resource_count: ">= 1"
output: SUPPORT
priority:
  execution_order: 3
  conflict_precedence: 3
  authority_level: SUPPORTING
  specificity: 3
classic_reference: 渊海子平·论印绶
notes: "正印/偏印均需考虑"
adjudication: PENDING
```

#### ZIPING-RULE-WS-007: 官杀攻身

```yaml
rule_id: ZIPING-RULE-WS-007
name: 官杀攻身
domain: wangshuai
status: DRAFT
source_evidence:
  - evidence_id: E-PZZQ-007-001
    classic: ziping_zhenquan
    extraction: "克我者 = 官杀"
    confidence: 0.8
condition:
  officer_count: ">= 2"
output: CONSTRAINT
priority:
  execution_order: 3
  conflict_precedence: 3
  authority_level: PRIMARY  # 子平真诠在官杀判断有权威
  specificity: 3
classic_reference: 子平真诠·论官杀
notes: "官杀混杂需特殊处理"
adjudication: PENDING
```

#### ZIPING-RULE-WS-008: 食伤泄身

```yaml
rule_id: ZIPING-RULE-WS-008
name: 食伤泄身
domain: wangshuai
status: DRAFT
source_evidence:
  - evidence_id: E-DTS-108-001
    classic: di_tian_sui
    extraction: "我生者 = 食伤"
    confidence: 0.7
condition:
  output_count: ">= 2"
output: CONSTRAINT
priority:
  execution_order: 3
  conflict_precedence: 3
  authority_level: SUPPORTING
  specificity: 3
classic_reference: 滴天髓·论泄气
notes: "食神/伤官需区分"
adjudication: PENDING
```

#### ZIPING-RULE-WS-009: 综合强判定

```yaml
rule_id: ZIPING-RULE-WS-009
name: 综合强判定
domain: wangshuai
status: DRAFT
source_evidence: []  # 综合推导，无单一证据
confidence: 0.5
condition:
  supported_factors: ">= 2"  # 得令+通根+生扶
output: STRONG
priority:
  execution_order: 4
  conflict_precedence: 4
  authority_level: REFERENCE
  specificity: 4
classic_reference: 综合判断
notes: "需明确'综合'的权重定义，禁止简单计数"
adjudication: PENDING
conflicts:
  - note: "与WS-010互斥"
```

#### ZIPING-RULE-WS-010: 综合弱判定

```yaml
rule_id: ZIPING-RULE-WS-010
name: 综合弱判定
domain: wangshuai
status: DRAFT
source_evidence: []
confidence: 0.5
condition:
  constrained_factors: ">= 2"
output: WEAK
priority:
  execution_order: 4
  conflict_precedence: 4
  authority_level: REFERENCE
  specificity: 4
classic_reference: 综合判断
notes: "需明确'综合'的权重定义"
adjudication: PENDING
```

#### ZIPING-RULE-WS-011: 综合中和

```yaml
rule_id: ZIPING-RULE-WS-011
name: 综合中和
domain: wangshuai
status: DRAFT
source_evidence: []
confidence: 0.3
condition:
  default: true  # 以上都不满足
output: MODERATE
priority:
  execution_order: 4
  conflict_precedence: 5
  authority_level: REFERENCE
  specificity: 1
classic_reference: 默认值
notes: "仅作为fallback，不应主动判定"
adjudication: PENDING
```

---

### 3.2 格局域规则（10条）

#### ZIPING-RULE-PT-001: 正官格

```yaml
rule_id: ZIPING-RULE-PT-001
name: 正官格
domain: pattern
status: DRAFT
source_evidence:
  - evidence_id: E-PZZQ-001-001
    classic: ziping_zhenquan
    chapter: 论正官
    extraction: "月令正官透干 = 正官格"
    confidence: 0.9
condition:
  month_branch_element: "官"
  month_stem_transparent: true
  ten_god: "ZHENGGUAN"
output: ZHENGGUAN_PATTERN
priority:
  execution_order: 4
  conflict_precedence: 4
  authority_level: PRIMARY
  specificity: 4
classic_reference: 子平真诠·论正官
notes: "需验证成格条件：官星有财生、有印护"
adjudication: PENDING
```

#### ZIPING-RULE-PT-002: 七杀格

```yaml
rule_id: ZIPING-RULE-PT-002
name: 七杀格
domain: pattern
status: DRAFT
source_evidence:
  - evidence_id: E-PZZQ-002-001
    classic: ziping_zhenquan
    chapter: 论七杀
    extraction: "月令七杀透干 = 七杀格"
    confidence: 0.9
condition:
  month_branch_element: "杀"
  month_stem_transparent: true
  ten_god: "QISHA"
output: QISHA_PATTERN
priority:
  execution_order: 5
  conflict_precedence: 5
  authority_level: PRIMARY
  specificity: 4
classic_reference: 子平真诠·论七杀
notes: "七杀需有制化方为贵格"
adjudication: PENDING
```

#### ZIPING-RULE-PT-009: 从格判定（最高优先级）

```yaml
rule_id: ZIPING-RULE-PT-009
name: 从格判定
domain: pattern
status: DRAFT
source_evidence:
  - evidence_id: E-PZZQ-009-001
    classic: ziping_zhenquan
    chapter: 论从格
    extraction: "日主无根无帮扶 = 从格"
    confidence: 0.85
condition:
  root_present: false
  peer_support: 0
  resource_support: 0
output: CONGRUENT_PATTERN
priority:
  execution_order: 0  # 最高优先级
  conflict_precedence: 0  # 从格优先于所有正格
  authority_level: PRIMARY
  specificity: 5
classic_reference: 子平真诠·论从格
notes: "从格判定严格，需排除假从格"
adjudication: PENDING
```

#### ZIPING-RULE-PT-010: 化格判定

```yaml
rule_id: ZIPING-RULE-PT-010
name: 化格判定
domain: pattern
status: DRAFT
source_evidence:
  - evidence_id: E-DTS-010-001
    classic: di_tian_sui
    chapter: 化气
    extraction: "天干五合化气成功 = 化格"
    confidence: 0.8
condition:
  heaven_combo: true
  transformation_successful: true
output: TRANSFORMATION_PATTERN
priority:
  execution_order: 1
  conflict_precedence: 1
  authority_level: PRIMARY
  specificity: 5
classic_reference: 滴天髓·化气
notes: "化格条件极严，需月令支持"
adjudication: PENDING
```

（其余格局规则类似格式...）

---

### 3.3 用神域规则（4条）

#### ZIPING-RULE-YG-001: 格局用神

```yaml
rule_id: ZIPING-RULE-YG-001
name: 格局用神
domain: yongshen
status: DRAFT
source_evidence:
  - evidence_id: E-PZZQ-001-001
    classic: ziping_zhenquan
    extraction: "格局已成，用神为相神"
    confidence: 0.9
condition:
  pattern_established: true
output: PATTERN_YONGSHEN
priority:
  execution_order: 1
  conflict_precedence: 1
  authority_level: PRIMARY
  specificity: 4
classic_reference: 子平真诠·论用神
notes: "格局用神优先级最高"
adjudication: PENDING
```

#### ZIPING-RULE-YG-002: 调候用神

```yaml
rule_id: ZIPING-RULE-YG-002
name: 调候用神
domain: yongshen
status: DRAFT
source_evidence:
  - evidence_id: E-QTBJ-001-001
    classic: qiong_tong_bao_jian
    extraction: " lookup table: day_stem + month_branch → yongshen"
    confidence: 0.95
condition:
  day_stem: str
  month_branch: str
output: CLIMATE_YONGSHEN
priority:
  execution_order: 2
  conflict_precedence: 2
  authority_level: PRIMARY
  specificity: 5
classic_reference: 穷通宝鉴
notes: "调候用神查表法，权威性高"
adjudication: PENDING
```

---

### 3.4 十神语义域规则（3条）

### 3.5 事件判断域规则（4条）

---

## 四、Evidence → Rule 映射验证

### 4.1 证据有效性检查

| Evidence ID | Classic | Confidence | 支持规则 |
|-------------|---------|------------|----------|
| E-YHZP-001-001 | 渊海子平 | 0.71 | WS-001(间接) |
| E-YHZP-003-001 | 渊海子平 | 0.85 | WS-003 |
| E-YHZP-005-001 | 渊海子平 | 0.75 | WS-005 |
| E-DTS-101-001 | 滴天髓 | 0.80 | WS-001(间接) |
| E-PZZQ-001-001 | 子平真诠 | 0.90 | PT-001, YG-001 |
| E-QTBJ-001-001 | 穷通宝鉴 | 0.95 | YG-002 |

### 4.2 证据缺口

以下规则缺少直接证据支持：
- WS-002 (失令) - 需补充滴天髓原文
- WS-004 (无根) - 需补充渊海子平原文
- WS-009/010/011 (综合判定) - 无直接证据，需推导

---

## 五、下一步行动

### Phase B-0 完成标准

- [ ] 32 条规则全部完成逐条审计
- [ ] 每条规则绑定至少 1 个 Evidence ID
- [ ] 明确标注每个规则的 confidence 和 authority_level
- [ ] 识别所有冲突规则并标注解决策略
- [ ] 标记所有缺乏直接证据的规则

### 待 BOT-MASTER 裁决

- [ ] 确认 `DOMAIN_AUTHORITY` 设计
- [ ] 确认规则状态机设计
- [ ] 确认优先级拆分设计
- [ ] 确认 Phase B (Evidence Connection) 启动时机

---

**执行中**: @bot-ziping  
**状态**: 🔄 IN PROGRESS  
**预计完成**: 需补充完整规则审计
