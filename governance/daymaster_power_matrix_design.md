# 身强身弱多维矩阵设计（PATCH-160 整体研究）

状态：研究完成 / 前置设计 / 待执行
基准：ee913740

---

## 一、原著命题全集（六部经典已确认）

### PZZQ（子平真诠）
| 原文 | evidence_id | 语义 | 维度 |
|---|---|---|---|
| 得时为旺，失时为衰 | PZZQ-005-005 | 月令旺衰轴 | SEASONAL |
| 党众为强，助寡为弱 | 待定位 | 同党多少轴 | SUPPORT |
| 得时而不旺（得令但泄太重） | PZZQ-005-005 | 得令+泄太重 | SEASONAL+DRAIN |
| 失时而不弱（失令但比印重叠） | PZZQ-005-005 | 失令+扶重叠 | SEASONAL+SUPPORT |
| 有根便能任财官 | 待定位 | 根→承受力 | ROOT |
| 长生/禄/旺/刃=重根；墓库/余气=轻根 | 待定位 | 根层级 | ROOT |
| 干多不如根重 | 待定位 | 根>干 | ROOT |

### DTS（滴天髓）
| 原文 | evidence_id | 语义 | 维度 |
|---|---|---|---|
| 强众敌寡/强寡敌众 | DTS-027-003 | 两端成势 | TWO_SIDE |
| 通根透癸，冲天奔地 | DTS-008-021 | 通根=有力 | ROOT |
| 不论有根无根，俱要天覆地载 | DTS-010-003 | 根+结构关系 | ROOT+STRUCTURE |

---

## 二、多维矩阵（完整结构）

```
日主多维网络
├─ D1 SEASONAL（得令/失令）
│   ├─ in_season: bool
│   ├─ month_supports: bool
│   └─ 原著: 得时为旺，失时为衰
│
├─ D2 ROOT（根气）
│   ├─ has_root: bool
│   ├─ root_weight_class: HEAVY/LIGHT
│   ├─ root_type: 长生/禄/旺/刃/墓库/余气
│   ├─ per_pillar: 各支根
│   └─ 原著: 有根便能任财官；根分轻重
│
├─ D3 SUPPORT（党众/助寡）
│   ├─ BIJIE: stem_present/root_present
│   ├─ YIN: stem_present/root_present
│   └─ 原著: 党众为强，助寡为弱
│
├─ D4 DRAIN（泄耗）
│   ├─ SHISHANG: stem_present/root_present
│   ├─ CAI: stem_present/root_present
│   └─ 原著: 得时不旺=泄太重
│
├─ D5 CONTROL（克制）
│   ├─ GUANSHA: stem_present/root_present
│   └─ 原著: 官杀克身
│
├─ D6 TWO_SIDE（两端成势）【HOLD】
│   ├─ daymaster_side: D2+D3
│   ├─ opposing_side: D4+D5
│   └─ 原著: 强众敌寡/强寡敌众
│
├─ D7 TRANSMISSION（传递链）【C级，未授权】
│   ├─ SHISHANG→CAI
│   ├─ CAI→GUANSHA
│   └─ GUANSHA→YIN
│
└─ D8 STRUCTURE_RELATION（合冲刑害破）【HOLD】
    ├─ 合：天干五合
    ├─ 冲：六冲
    ├─ 刑：三刑/自刑
    ├─ 害：六害
    └─ 破：六破
```

---

## 三、当前已建 vs 缺失

### 已建（160-A + 160-B V2）
| 维度 | 状态 | 说明 |
|---|---|---|
| D1 SEASONAL | ✅ 已建 | in_season + month_supports |
| D2 ROOT | ✅ 已建 | root_weight_class + per_pillar |
| D3 SUPPORT | ✅ 已建 | BIJIE/YIN stem/root present |
| D4 DRAIN | ✅ 已建 | SHISHANG/CAI stem/root present |
| D5 CONTROL | ✅ 已建 | GUANSHA stem/root present |
| D7 TRANSMISSION | ✅ C级 | 保留节点，不参与强弱 |

### 缺失（当前未建）
| 维度 | 状态 | 原因 |
|---|---|---|
| D2 ROOT root_type 细分 | ⚠️ 未细分 | 当前只有 HEAVY/LIGHT，未按长生/禄/旺/刃/墓库/余气细分 |
| D6 TWO_SIDE 成势判断 | 🔒 HOLD | "成势"带作用语义，未授权 |
| D8 STRUCTURE_RELATION 对根气影响 | 🔒 HOLD | "根动/根拔"带作用语义 |

---

## 四、Query 全集（已建 vs 缺失）

### 已建（160-C v0）
| Query | 原著依据 | 结构条件 | state | match_type |
|---|---|---|---|---|
| CAN_REN_CAIGUAN | 有根便能任财官 | D2.has_root | SUPPORTED/NOT_SUPPORTED | STRUCTURE_MATCH/NO_MATCH |
| DESHI_BUWANG | 得时不旺 | D1.in_season + D4.has_drain | UNKNOWN | STRUCTURE_MATCH/NO_MATCH |
| SHISHI_BURUO | 失时不弱 | NOT D1.in_season + D3.has_support | UNKNOWN | STRUCTURE_MATCH/NO_MATCH |

### 缺失 Query（待研究）
| Query | 原著依据 | 需要维度 | 状态 |
|---|---|---|---|
| 根重 vs 根轻 | 根分轻重 | D2.root_type | ⚠️ 待建 |
| 干多不如根重 | 根>干 | D2 vs D3 | ⚠️ 待建 |
| 天覆地载 | 不论有根无根俱要天覆地载 | D2+D8 | 🔒 HOLD |
| 强众敌寡 | 两端成势 | D6 | 🔒 HOLD |
| 强寡敌众 | 两端成势 | D6 | 🔒 HOLD |
| 通根透癸 | 通根=有力 | D2 | ⚠️ 待建 |

---

## 五、依赖关系（关键！）

```
CAN_REN_CAIGUAN (D2.has_root)
    ↓ 独立，不依赖其他维度

DESHI_BUWANG (D1.in_season + D4.has_drain)
    ↓ 依赖 D1 + D4
    ↓ 不依赖 D2/D3/D5

SHISHI_BURUO (NOT D1.in_season + D3.has_support)
    ↓ 依赖 D1 + D3
    ↓ 不依赖 D2/D4/D5

D6 TWO_SIDE 成势
    ↓ 依赖 D2 + D3 + D4 + D5
    ↓ 但"成势"带作用语义 → HOLD

D8 STRUCTURE_RELATION 影响根气
    ↓ 依赖 D2 + D8
    ↓ 但"根动/根拔"带作用语义 → HOLD
```

---

## 六、执行优先级

### 第一刀：补 D2 ROOT root_type 细分
- 当前：root_weight_class = HEAVY/LIGHT
- 原著：长生/禄/旺/刃=重根；墓库/余气=轻根
- 执行：把 root_type 从 L0 root_facts 接进来，细分 per_pillar
- 风险：低，纯结构

### 第二刀：补 D2 root_type Query
- Query: ROOT_HEAVY vs ROOT_LIGHT
- 原著：根分轻重
- 执行：从 root_type 直接映射

### 第三刀：研究 D6 TWO_SIDE 成势
- 原著：强众敌寡/强寡敌众
- 问题：成势带作用语义
- 执行：只读研究，确认"成势"能不能纯结构机器化
- 风险：高，可能继续 HOLD

### 暂不执行
- D8 STRUCTURE_RELATION 影响根气（根动/根拔）
- 传递链 C 级不参与强弱
- 任何"太强/太弱"数量判断

---

## 七、永久边界

- 不评分/不权重/不阈值/不计数
- 不汇总成 STRONG/WEAK
- 矛盾共存不裁
- 结构匹配 ≠ 命题成立
- evidence_refs 空 ≠ 有证据
- 不强行绑未定位原文
