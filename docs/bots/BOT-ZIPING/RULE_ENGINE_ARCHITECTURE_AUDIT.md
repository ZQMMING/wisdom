# ZIPING Rule Engine Architecture Audit

**任务 ID**: T-ENGINE-BAZI-002 Phase 2 Architecture Audit  
**执行者**: @bot-ziping  
**日期**: 2026-09-06  
**状态**: 🔄 IN PROGRESS - Architecture Design Phase

---

## 执行摘要

根据 BOT-MASTER 裁决，停止直接实现 P0-1～P0-5。
转入 **Rule Engine Architecture & Authority Audit** 阶段。

**核心任务**: 基于现有五经 Evidence 数据库，建立完整规则链设计。

---

## 一、现状盘点

### 1.1 BAZI 层状态 🟢 FROZEN

| 组件 | 状态 | 说明 |
|------|------|------|
| BaziEngine | ✅ | 四柱、节气、真太阳时计算完成 |
| BaziChart | ✅ | 数据结构完整，含 P2 extension |
| TenGods | ✅ | 单一权威源，无重复实现 |
| HiddenStems | ✅ | BRANCH_HIDDEN_STEMS 统一 |
| TwelveGrowths | ✅ | 阳顺阴逆，戊己随丙丁 |
| DayMasterStrength | 🔴→✅ | fail-closed 已实现 |

### 1.2 ZIPING Context 层状态 🟢 CONNECTED

| 组件 | 状态 | 说明 |
|------|------|------|
| NatalContext | ✅ | 四柱、十神、地支关系完整 |
| DaYunContext | ✅ | 大运推算、交运期检测 |
| YearContext | ✅ | 流年、三层交互 |
| DerivedSignals | ✅ | 带 provenance 的信号生成 |
| ContractValidator | ✅ | 完整性验证 |

### 1.3 Evidence 层状态 ⚠️ PARTIAL

| 经典 | 文件数 | 结构化程度 | 可用性 |
|------|--------|------------|--------|
| 渊海子平 | 117 | ✅ 高 | ⚠️ 未连接 |
| 子平真诠 | 10 | ⚠️ 中 | ⚠️ 未连接 |
| 滴天髓 | 44 | ⚠️ 中 | ⚠️ 未连接 |
| 穷通宝鉴 | 1233 | ✅ 高 | ⚠️ 未连接 |
| 三命通会 | 10 | ❌ 低 | ❌ 未连接 |
| **总计** | **~1414** | | **全部未连接** |

> **注意**: 子平真诠实际只有 10 条结构化证据（原计划 ~130），三命通会仅 10 条。证据数量≠证据质量。详见 `references/evidence-coverage-analysis.md`。

### 1.4 Bian Agent 层状态 🔴 EMPTY

| Agent | 状态 | `_load_classic_entries()` |
|-------|------|---------------------------|
| YHZPBianAgent | 🔴 | `return []` |
| PZZQBianAgent | 🔴 | `return []` |
| DTSSBianAgent | 🔴 | `return []` |
| QTBJBianAgent | 🔴 | `return []` |
| SMTHBianAgent | 🔴 | `return []` |

**结论**: 五个辨证代理全部为空实现，证据数据库与推理层完全脱节。

### 1.5 Rule Engine 层状态 🔴 MISSING

| 模块 | 应有状态 | 实际状态 |
|------|----------|----------|
| 旺衰引擎 | Rule → Feature → Judgment | 🔴 完全缺失 |
| 格局引擎 | Rule → Condition → Pattern | 🔴 完全缺失 |
| 用神系统 | Rule → Priority → Yongshen | 🔴 完全缺失 |
| 十神语义 | Evidence → SemanticMap | ⚠️ 数据结构存在，无应用 |
| 事件判断 | Signal → Event → Assertion | 🔴 完全缺失 |

---

## 二、架构缺口分析

### 2.1 断裂的规则链

```
应有链路:
Classic Evidence → Evidence Extraction → Canonical Rule → 
Rule Condition → Feature/Signal → Judgment → Priority → Assertion

实际链路:
Classic Evidence ✅ (证据数据库存在)
    ↓
Evidence Extraction ❌ (代理空实现，无法加载)
    ↓
Canonical Rule ❌ (无规则定义)
    ↓
Rule Condition ❌ (无条件判断)
    ↓
Feature/Signal ⚠️ (数据结构存在，无规则应用)
    ↓
Judgment ❌ (无判定逻辑)
    ↓
Priority ❌ (无优先级定义)
    ↓
Assertion ❌ (无断言输出)
```

### 2.2 核心问题：有书无规则

> **"有书，但是没有把书变成可执行的子平规则。"**

证据数据库是"静态资料"，不是"动态规则"。需要建立转化层：

```
静态证据 (JSON files)
    ↓ 转化层 (Rule Extraction)
动态规则 (Rule Schema)
    ↓ 应用层 (Rule Engine)
辨证结果 (Judgment/Assertion)
```

---

## 三、Rule Engine Architecture 设计

### 3.1 完整规则链设计

```
┌─────────────────────────────────────────────────────────────────┐
│                    ZIPING Rule Engine Architecture               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 1: Evidence Layer                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Classic Evidence (JSON files in data/evidence/)         │   │
│  │   - E-YHZP-XXX-XXX.json                                 │   │
│  │   - E-PZZQ-XXX-XXX.json                                 │   │
│  │   - E-DTS-XXX-XXX.json                                  │   │
│  │   - E-QTBJ-XXX-XXX.json                                 │   │
│  │   - E-SMTH-XXX-XXX.json                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  Layer 2: Evidence Loader (连接层)                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ EvidenceLoader                                          │   │
│  │   - _load_classic_entries() ← 实现此方法                 │   │
│  │   - _build_passage_index()                              │   │
│  │   - search_by_keyword()                                 │   │
│  │   - filter_by_authorization()                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  Layer 3: Rule Definition (规则定义层)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Rule Schema                                             │   │
│  │   - rule_id: ZIPING-RULE-XXXX                           │   │
│  │   - source: [Evidence IDs]                              │   │
│  │   - condition: Callable[CanonicalState] -> bool         │   │
│  │   - output: str  (Judgment value)                       │   │
│  │   - priority: int                                       │   │
│  │   - authorization_level: AuthorizationLevel             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  Layer 4: Rule Engine (规则引擎层)                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ RuleEngine                                              │   │
│  │   - evaluate_rule(rule, state) -> Judgment              │   │
│  │   - apply_priority(rules, judgments) -> Final           │   │
│  │   - detect_conflicts(rules) -> List[Conflict]           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  Layer 5: Judgment Layer (判断层)                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ JudgmentSchema                                            │   │
│  │   - judgment_id: ZIPING-JUDG-XXXX                       │   │
│  │   - domain: str  (wangshuai/pattern/yongshen/...)       │   │
│  │   - value: str  (STRONG/WEAK/MODERATE/...)              │   │
│  │   - confidence: float  (0.0-1.0)                        │   │
│  │   - rule_refs: List[str]                                │   │
│  │   - evidence_refs: List[str]                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  Layer 6: Assertion Layer (断言层)                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ AssertionSchema                                           │   │
│  │   - assertion_id: ZIPING-ASSERT-XXXX                    │   │
│  │   - subject: str                                        │   │
│  │   - predicate: str                                      │   │
│  │   - object: str                                         │   │
│  │   - provenance: RuleChain                               │   │
│  │   - production_status: CANDIDATE/APPROVED/REJECTED      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Rule Schema 定义

```python
@dataclass(frozen=True)
class RuleCondition:
    """规则触发条件"""
    monthly_command: Optional[str] = None      # 月令条件
    root_present: Optional[bool] = None        # 通根条件
    peer_support: Optional[int] = None         # 比劫数量条件
    resource_support: Optional[int] = None     # 印星数量条件
    control_stems: Optional[List[str]] = None  # 克泄耗天干
    # ... 更多条件

@dataclass(frozen=True)
class Rule:
    """子平规则定义"""
    rule_id: str                              # ZIPING-RULE-WS-001
    name: str                                 # 得令条件
    domain: str                               # wangshuai/pattern/yongshen
    source_evidence_ids: List[str]            # 来源证据ID
    condition: RuleCondition                  # 触发条件
    output: str                               # 输出值
    priority: int                             # 优先级
    authorization_level: AuthorizationLevel   # 授权级别
    classic_reference: str                    # 经典出处
    notes: str = ""
    
    def evaluate(self, canonical_state: CanonicalState) -> bool:
        """评估规则是否触发"""
        # 由子类实现
        raise NotImplementedError
```

### 3.3 Evidence → Rule Provenance Contract

```python
@dataclass(frozen=True)
class EvidenceRuleProvenance:
    """证据→规则追溯链"""
    evidence_id: str                          # E-YHZP-001-001
    evidence_text: str                        # 原文
    rule_id: str                              # ZIPING-RULE-WS-001
    extraction_method: str                    # 如何从证据提取规则
    confidence: float                         # 提取置信度
    verification_status: VerificationStatus   # 核验状态
    notes: str = ""
```

---

## 四、五大辨证域规则设计

### 4.1 P0-1 旺衰引擎规则设计

#### 规则链

```
月令条件 → 得令判定
    ↓
通根条件 → 得地判定
    ↓
生扶条件 → 得势判定
    ↓
综合判定 → 强弱结论
```

#### 规则定义

| Rule ID | 规则名 | 条件 | 输出 | 优先级 | 证据来源 |
|---------|--------|------|------|--------|----------|
| ZIPING-RULE-WS-001 | 得令判定 | 月支五行生/同日主 | SUPPORT | 1 | DTS-WS-001 |
| ZIPING-RULE-WS-002 | 失令判定 | 月支五行克/被日主克 | CONSTRAINT | 1 | DTS-WS-002 |
| ZIPING-RULE-WS-003 | 通根判定 | 地支藏干含日主 | SUPPORT | 2 | YHZP-003 |
| ZIPING-RULE-WS-004 | 无根判定 | 四柱无一地支藏干含日主 | CONSTRAINT | 2 | DTS-004 |
| ZIPING-RULE-WS-005 | 比劫帮身 | 天干比劫≥2 | SUPPORT | 3 | YHZP-005 |
| ZIPING-RULE-WS-006 | 印星生身 | 天干印星≥1 | SUPPORT | 3 | DTS-006 |
| ZIPING-RULE-WS-007 | 官杀攻身 | 天干官杀≥2 | CONSTRAINT | 3 | PZZQ-007 |
| ZIPING-RULE-WS-008 | 食伤泄身 | 天干食伤≥2 | CONSTRAINT | 3 | DTS-008 |
| ZIPING-RULE-WS-009 | 综合强判定 | 得令+通根+生扶≥2 | STRONG | 4 | 多经综合 |
| ZIPING-RULE-WS-010 | 综合弱判定 | 失令+无根+克泄耗≥2 | WEAK | 4 | 多经综合 |
| ZIPING-RULE-WS-011 | 综合中和 | 以上都不满足 | MODERATE | 4 | 默认 |

#### 权重体系（禁止评分，但需明确条件）

```python
# 禁止：strength_score = w1*得令 + w2*通根 + ...
# 允许：条件触发制（符合子平原典）

WANGSHUAI_RULES = {
    "STRONG": ["ZIPING-RULE-WS-001", "ZIPING-RULE-WS-003", "ZIPING-RULE-WS-005"],
    "WEAK": ["ZIPING-RULE-WS-002", "ZIPING-RULE-WS-004", "ZIPING-RULE-WS-007"],
    "MODERATE": ["default"]
}
```

---

### 4.2 P0-2 格局引擎规则设计

#### 规则链

```
月令定格 → 透干成格 → 生克制化 → 成格/破格 → 特殊格局检查
```

#### 规则定义

| Rule ID | 规则名 | 条件 | 输出 | 优先级 | 证据来源 |
|---------|--------|------|------|--------|----------|
| ZIPING-RULE-PT-001 | 正官格 | 月令正官+透干 | ZHENGGUAN_PATTERN | 1 | PZZQ-001 |
| ZIPING-RULE-PT-002 | 七杀格 | 月令七杀+透干 | QISHA_PATTERN | 1 | PZZQ-002 |
| ZIPING-RULE-PT-003 | 财格 | 月令财星+透干 | CAI_PATTERN | 1 | PZZQ-003 |
| ZIPING-RULE-PT-004 | 印格 | 月令印星+透干 | YIN_PATTERN | 1 | PZZQ-004 |
| ZIPING-RULE-PT-005 | 食神格 | 月令食神+透干 | SHISHEN_PATTERN | 1 | PZZQ-005 |
| ZIPING-RULE-PT-006 | 伤官格 | 月令伤官+透干 | SHANGGUAN_PATTERN | 1 | PZZQ-006 |
| ZIPING-RULE-PT-007 | 建禄格 | 月支=日主禄位 | JIANLU_PATTERN | 2 | SMTH-001 |
| ZIPING-RULE-PT-008 | 阳刃格 | 月支=日主帝旺 | YANGREN_PATTERN | 2 | YHZP-002 |
| ZIPING-RULE-PT-009 | 从格判定 | 日主无根无帮扶 | CONGRUENT_PATTERN | 0 | PZZQ-009 |
| ZIPING-RULE-PT-010 | 化格判定 | 天干五合化气成功 | TRANSFORMATION_PATTERN | 0 | DTS-010 |

#### 格局优先级

```python
PATTERN_PRIORITY = [
    ("CONGRUENT_PATTERN", 0),      # 从格最高
    ("TRANSFORMATION_PATTERN", 1), # 化格次之
    ("JIANLU_PATTERN", 2),         # 建禄
    ("YANGREN_PATTERN", 3),        # 阳刃
    ("ZHENGGUAN_PATTERN", 4),      # 正官
    ("QISHA_PATTERN", 5),          # 七杀
    ("CAI_PATTERN", 6),            # 财格
    ("YIN_PATTERN", 7),            # 印格
    ("SHISHEN_PATTERN", 8),        # 食神
    ("SHANGGUAN_PATTERN", 9),      # 伤官
]
```

---

### 4.3 P0-3 用神系统规则设计

#### 概念拆分（禁止合并）

```python
# 禁止：useful_element = "metal" (模糊)
# 允许：分开定义

USEFUL_GOD_DOMAINS = {
    "pattern": "格局用神 - 成格要求",      # 《子平真诠》
    "climate": "调候用神 - 寒暖燥湿",      # 《穷通宝鉴》
    "support": "扶抑用神 - 旺衰平衡",      # 《滴天髓》
    "regulation": "制化用神 - 病药平衡",   # 《子平真诠》
}
```

#### 优先级链（原典依据）

```python
# 《子平真诠》: 格局优先
# 《穷通宝鉴》: 调候次之
# 《滴天髓》: 扶抑再次

USEFUL_GOD_PRIORITY = [
    "pattern",      # 格局用神（特殊格局 > 正格）
    "climate",      # 调候用神
    "support",      # 扶抑用神
    "regulation",   # 制化用神
]
```

#### 规则定义

| Rule ID | 规则名 | 条件 | 输出 | 优先级 | 证据来源 |
|---------|--------|------|------|--------|----------|
| ZIPING-RULE-YG-001 | 格局用神 | 根据格局类型 | PATTERN_YONGSHEN | 1 | PZZQ |
| ZIPING-RULE-YG-002 | 调候用神 | 日主+月令 | CLIMATE_YONGSHEN | 2 | QTBJ |
| ZIPING-RULE-YG-003 | 扶抑用神 | 旺衰判断 | SUPPORT_YONGSHEN | 3 | DTS |
| ZIPING-RULE-YG-004 | 制化用神 | 病药分析 | REGULATION_YONGSHEN | 4 | PZZQ |

---

### 4.4 P0-4 十神语义规则设计

#### BAZI → ZIPING 边界

```
BAZI层: 甲日主 + 庚干 → 七杀 (计算，已完成)
ZIPING层: 七杀在这个命局中如何成立、如何作用 (辨证，待实现)
```

#### 语义映射表

| 十神 | 正面语义 | 负面语义 | 条件 |
|------|----------|----------|------|
| 正官 | 贵气、事业、纪律 | 压力、束缚 | 无破损为贵 |
| 七杀 | 权威、魄力、冒险 | 凶暴、疾病 | 有制为权 |
| 正财 | 稳定、务实、勤俭 | 吝啬、保守 | 身强为宜 |
| 偏财 | 灵活、慷慨、投机 | 浮荡、挥霍 | 身强为宜 |
| 正印 | 学历、名声、仁慈 | 依赖、懒惰 | 生身有力 |
| 偏印 | Special、研究、孤独 | 偏执、孤僻 | 特殊格局用 |
| 食神 | 才华、享受、温和 | 消极、依赖 | 生财为吉 |
| 伤官 | 才华、创新、反叛 | 傲气、是非 | 配印为贵 |
| 比肩 | 独立、自信、竞争 | 固执、争夺 | 帮身有力 |
| 劫财 | 果断、行动、争夺 | 破财、冲动 | 特殊情况用 |

#### 规则定义

| Rule ID | 规则名 | 条件 | 输出 | 优先级 | 证据来源 |
|---------|--------|------|------|--------|----------|
| ZIPING-RULE-TG-001 | 十神正面语义 | 十神得位+有生扶 | POSITIVE_SEMANTIC | 1 | YHZP |
| ZIPING-RULE-TG-002 | 十神负面语义 | 十神受损+无制化 | NEGATIVE_SEMANTIC | 1 | YHZP |
| ZIPING-RULE-TG-003 | 十神组合语义 | 两个十神相邻 | COMBINED_SEMANTIC | 2 | PZZQ |

---

### 4.5 P0-5 事件判断规则设计

#### 规则链

```
本命判断 → 大运作用 → 流年引动 → 作用关系 → 事件信号 → 事件断言
```

#### 事件类型

| 事件类型 | 判定条件 | 证据来源 |
|----------|----------|----------|
| 财运 | 财星+身强/从格 | PZZQ-财篇 |
| 事业 | 官杀+格局成 | PZZQ-官篇 |
| 婚姻 | 配偶星+配偶宫 | YHZP-六亲篇 |
| 健康 | 五行失衡+刑冲 | DTS-疾厄篇 |

#### 规则定义

| Rule ID | 规则名 | 条件 | 输出 | 优先级 | 证据来源 |
|---------|--------|------|------|--------|----------|
| ZIPING-RULE-EV-001 | 财运信号 | 财星透干+身强 | WEALTH_SIGNAL | 1 | PZZQ |
| ZIPING-RULE-EV-002 | 事业信号 | 官杀透干+格局成 | CAREER_SIGNAL | 1 | PZZQ |
| ZIPING-RULE-EV-003 | 婚姻信号 | 配偶星+宫位稳 | MARRIAGE_SIGNAL | 1 | YHZP |
| ZIPING-RULE-EV-004 | 健康信号 | 五行偏枯+刑冲 | HEALTH_SIGNAL | 1 | DTS |

---

## 五、Rule Authority 体系设计

### 5.1 权威等级

```python
class RuleAuthorityLevel(str, Enum):
    """规则权威等级"""
    EXPLICIT = "EXPLICIT"              # 原典明确（如《子平真诠》直接论述）
    IMPLICIT = "IMPLICIT"              # 原典隐含（需推论）
    HYPOTHESIS = "HYPOTHESIS"          # 合理假说（后世发展）
    ENGINEERING = "ENGINEERING"        # 工程推导（现代整理）
    UNVERIFIED = "UNVERIFIED"          # 未核验
    NOT_AUTHORIZED = "NOT_AUTHORIZED"  # 未授权
```

### 5.2 经典冲突处理

```python
CLASSIC_AUTHORITY = {
    "ziping_zhenquan": 1,    # 格局权威
    "yuan_hai_zi_ping": 2,   # 基础权威
    "di_tian_sui": 3,        # 旺衰权威
    "qiong_tong_bao_jian": 4, # 调候权威
    "san_ming_tong_hui": 5,  # 杂项权威
}

def resolve_conflict(rules: List[Rule]) -> Rule:
    """解决经典冲突"""
    # 1. 同域规则冲突：取高权威经典
    # 2. 不同域规则：都保留，标注冲突
    # 3. 无冲突：正常应用
    pass
```

---

## 六、实施计划

### Phase A: Architecture Design (当前阶段)
- [ ] 完成 Rule Schema 定义
- [ ] 完成 Evidence → Rule Provenance Contract
- [ ] 完成五大辨证域规则设计
- [ ] 完成 Rule Authority 体系

### Phase B: Evidence Connection
- [ ] 实现五个 Bian Agent 的 `_load_classic_entries()`
- [ ] 连接证据数据库到辨证代理
- [ ] 验证证据加载正确性

### Phase C: Rule Engine Implementation
- [ ] 实现 RuleEngine 类
- [ ] 实现 Rule Evaluation 逻辑
- [ ] 实现 Rule Priority 应用

### Phase D: Domain Implementation
- [ ] P0-1: 旺衰规则实现
- [ ] P0-2: 格局规则实现
- [ ] P0-3: 用神规则实现
- [ ] P0-4: 十神语义规则实现
- [ ] P0-5: 事件判断规则实现

### Phase E: Validation
- [ ] Golden Cases 验证
- [ ] Rule-level Provenance 追溯测试
- [ ] 冲突检测与裁决

---

## 七、指标体系

### 7.1 新指标（替代证据数量）

| 指标 | 定义 | 目标 |
|------|------|------|
| RuleProvenanceRate | 有完整溯源的规则比例 | ≥90% |
| RuleCompleteness | 条件定义完整的规则比例 | ≥80% |
| RuleConflictRate | 存在冲突的规则比例 | ≤10% |
| PriorityDefined | 已定义优先级的规则比例 | 100% |
| ExecutionCoverage | 已被执行的规则比例 | ≥70% |
| GoldenCaseAccuracy | Golden Cases 判断准确率 | ≥85% |

### 7.2 旧指标（降级为辅助）

| 指标 | 意义 | 当前值 |
|------|------|--------|
| EvidenceCount | 资料规模 | ~1534 |
| EvidenceCoverage | 哪些规则有原典依据 | 待统计 |
| EvidenceQuality | 证据质量分布 | 待统计 |

---

## 八、当前状态总结

```
BAZI
🟢 FROZEN

        ↓ Canonical Chart

ZIPING
🟡 CONNECTED
🟢 INPUT CONTRACT PASS
🟢 NO BAZI RECALCULATION
🟢 BASIC DERIVED FACTS PASS

        ↓

ZIPING RULE ENGINE
🔴 NOT IMPLEMENTED

旺衰       🔴
格局       🔴
用神       🔴
十神语义   🔴
事件判断   🔴

        ↓

ZIPING FREEZE
🔴 NOT READY
```

---

## 九、下一步行动

**立即停止**: 直接实现 P0-1～P0-5 代码

**开始执行**: ZIPING Rule Engine Architecture Audit

**交付物**: 
1. Rule Schema 规范文档
2. Evidence → Rule Provenance Contract
3. 五大辨证域规则设计文档
4. Rule Authority 体系文档
5. P0 Implementation Plan

---

**执行者**: @bot-ziping  
**状态**: 🔄 IN PROGRESS - Architecture Design Phase  
**预计完成**: 2-4 小时
