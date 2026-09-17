# 身强身弱多维矩阵设计（PATCH-160 整体研究 v2）

状态：研究扩展完成 / 前置设计 / 待执行
基准：93a3426d

---

## 一、六部经典身强身弱相关原文（深度搜索后）

### PZZQ（子平真诠）
| 原文 | evidence_id | 语义 | 维度 |
|---|---|---|---|
| 得时为旺，失时为衰 | PZZQ-005-005 | 月令旺衰 | D1 SEASONAL |
| 党众为强，助寡为弱 | 待定位 | 同党多少 | D3 SUPPORT |
| 得时而不旺（得令但泄太重） | PZZQ-005-005 | 得令+泄太重 | D1+D4 |
| 失时而不弱（失令但比印重叠） | PZZQ-005-005 | 失令+扶重叠 | D1+D3 |
| 有根便能任财官 | 待定位 | 根→承受力 | D2 ROOT |
| 长生/禄/旺/刃=重根；墓库/余气=轻根 | 待定位 | 根层级 | D2 ROOT |
| 干多不如根重 | 待定位 | 根>干 | D2 vs D3 |
| 透干会支，别取财官煞食为用 | PZZQ-007-033 | 透藏关系 | D13 TOU_CANG |
| 有情无情、有力无力之间 | PZZQ-007-001 | 格局高低（非身强弱） | — |

### DTS（滴天髓）
| 原文 | evidence_id | 语义 | 维度 |
|---|---|---|---|
| 强众敌寡/强寡敌众 | DTS-027-003 | 两端成势 | D6 TWO_SIDE |
| 通根透癸，冲天奔地 | DTS-008-021 | 通根=有力 | D2 ROOT |
| 不论有根无根，俱要天覆地载 | DTS-010-003 | 根+结构 | D2+D12 |
| 五阳从气不从势，五阴从势无情义 | DTS-008-003 | 从化 | D10 CONG_HUA |
| 何知章：何处起根源，流到何方住 | DTS-018-001 | 源流/通关 | D15 GUAN_TONG |

### QTBJ（穷通宝鉴）
| 原文 | evidence_id | 语义 | 维度 |
|---|---|---|---|
| 正月甲木/二月甲木... | QTBJ-003-001等 | 调候 | D9 TIAO_HOU |
| 寒暖燥湿 | 全书 | 调候 | D9 TIAO_HOU |

---

## 二、完整多维矩阵（16 维）

```
日主多维网络（16 维）
│
├─ D1 SEASONAL（得令/失令）✅ 已建
│   ├─ in_season
│   ├─ month_supports
│   └─ 原著: 得时为旺，失时为衰
│
├─ D2 ROOT（根气）✅ 已建（待细分 root_type）
│   ├─ has_root
│   ├─ root_weight_class: HEAVY/LIGHT
│   ├─ root_type: 长生/禄/旺/刃/墓库/余气（待接）
│   └─ per_pillar
│
├─ D3 SUPPORT（党众/助寡）✅ 已建
│   ├─ BIJIE: stem/root present
│   └─ YIN: stem/root present
│
├─ D4 DRAIN（泄耗）✅ 已建
│   ├─ SHISHANG: stem/root present
│   └─ CAI: stem/root present
│
├─ D5 CONTROL（克制）✅ 已建
│   └─ GUANSHA: stem/root present
│
├─ D6 TWO_SIDE（两端成势）🔒 HOLD
│   ├─ daymaster_side: D2+D3
│   ├─ opposing_side: D4+D5
│   └─ 原著: 强众敌寡/强寡敌众
│
├─ D7 TRANSMISSION（传递链）✅ C级
│   ├─ SHISHANG→CAI
│   ├─ CAI→GUANSHA
│   └─ GUANSHA→YIN
│
├─ D8 STRUCTURE（合冲刑害破）🔒 HOLD
│   ├─ 合/冲/刑/害/破
│   └─ 对根气影响（根动/根拔）
│
├─ D9 TIAO_HOU（调候）🔒 未建
│   ├─ 寒暖燥湿
│   ├─ 月令调候需求
│   └─ 原著: QTBJ 全书
│
├─ D10 CONG_HUA（从化）🔒 未建
│   ├─ 从格（从财/从杀/从儿/从势）
│   ├─ 化格
│   └─ 原著: DTS 五阳从气不从势
│
├─ D11 XI_WANG_XIU_QIU（旺相休囚）⚠️ 待建
│   ├─ 日主在月令的旺相休囚
│   └─ 原著: PZZQ/QTBJ
│
├─ D12 TIAN_FU_DI_ZAI（天覆地载）🔒 HOLD
│   ├─ 不论有根无根俱要天覆地载
│   ├─ 根动/根拔
│   └─ 原著: DTS
│
├─ D13 TOU_CANG（透藏关系）⚠️ 待建
│   ├─ 透干会支
│   ├─ 天干透 vs 地支藏
│   └─ 原著: PZZQ 透干会支取财官煞食
│
├─ D14 GE_JU_GAO_DI（格局高低）— 非身强弱
│   ├─ 有情无情/有力无力/清浊真假
│   └─ 注意: 这是格局层，不属身强弱矩阵
│
├─ D15 GUAN_TONG（通关/源流）✅ C级
│   ├─ 生克路线
│   ├─ 通关
│   └─ 原著: DTS 源流论
│
└─ D16 SUI_YUN（岁运）🔒 冻结（215）
    ├─ 运支×命局刑破害
    ├─ 运干×命局合冲
    └─ 之前已冻结
```

---

## 三、已建 vs 缺失（扩展后）

### 已建
| 维度 | 状态 |
|---|---|
| D1 SEASONAL | ✅ |
| D2 ROOT | ✅（待细分 root_type） |
| D3 SUPPORT | ✅ |
| D4 DRAIN | ✅ |
| D5 CONTROL | ✅ |
| D7 TRANSMISSION | ✅ C级 |
| D15 GUAN_TONG | ✅ C级 |

### 缺失（未建）
| 维度 | 状态 | 原因 |
|---|---|---|
| D6 TWO_SIDE 成势 | 🔒 HOLD | 成势带作用语义 |
| D8 STRUCTURE 影响根气 | 🔒 HOLD | 根动/根拔带作用语义 |
| D9 TIAO_HOU 调候 | 🔒 未建 | QTBJ 体系，独立于身强弱 |
| D10 CONG_HUA 从化 | 🔒 未建 | 从格化格，特殊路径 |
| D11 XI_WANG_XIU_QIU | ⚠️ 待建 | 旺相休囚，与 D1 有重叠 |
| D12 TIAN_FU_DI_ZAI | 🔒 HOLD | 天覆地载带结构关系 |
| D13 TOU_CANG 透藏 | ⚠️ 待建 | 透干会支，结构关系 |
| D14 GE_JU_GAO_DI | — | 格局层，不属身强弱 |
| D16 SUI_YUN | 🔒 冻结 | 215 已冻结 |

---

## 四、Query 全集（扩展后）

### 已建
| Query | 原著依据 | 维度 |
|---|---|---|
| CAN_REN_CAIGUAN | 有根便能任财官 | D2 |
| DESHI_BUWANG | 得时不旺 | D1+D4 |
| SHISHI_BURUO | 失时不弱 | D1+D3 |

### 缺失 Query（待研究）
| Query | 原著依据 | 维度 | 状态 |
|---|---|---|---|
| 根重 vs 根轻 | 根分轻重 | D2 | ⚠️ 待建 |
| 干多不如根重 | 根>干 | D2 vs D3 | ⚠️ 待建 |
| 通根透癸 | 通根=有力 | D2 | ⚠️ 待建 |
| 天覆地载 | 不论有根无根俱要 | D2+D12 | 🔒 HOLD |
| 强众敌寡 | 两端成势 | D6 | 🔒 HOLD |
| 强寡敌众 | 两端成势 | D6 | 🔒 HOLD |
| 透干会支取财官 | 透藏 | D13 | ⚠️ 待建 |
| 寒暖燥湿调候 | QTBJ | D9 | 🔒 独立体系 |
| 从化成立 | 从格化格 | D10 | 🔒 特殊路径 |

---

## 五、依赖关系（关键）

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

D8 STRUCTURE 影响根气
    ↓ 依赖 D2 + D8
    ↓ 但"根动/根拔"带作用语义 → HOLD

D9 TIAO_HOU 调候
    ↓ 独立体系，不与身强弱混算

D10 CONG_HUA 从化
    ↓ 特殊路径，不与普通身强弱混算

D13 TOU_CANG 透藏
    ↓ 依赖 D1 + 天干透/地支藏
    ↓ 纯结构，可建
```

---

## 六、执行优先级（扩展后）

### 第一刀：补 D2 ROOT root_type 细分
- 当前：HEAVY/LIGHT
- 原著：长生/禄/旺/刃=重根；墓库/余气=轻根
- 纯结构，低风险

### 第二刀：补 D13 TOU_CANG 透藏关系
- 透干会支
- 纯结构，中风险

### 第三刀：补 D11 XI_WANG_XIU_QIU
- 旺相休囚
- 与 D1 有重叠，需区分

### 第四刀：研究 D9 TIAO_HOU 调候能否纯结构
- QTBJ 体系独立
- 可能 HOLD

### 第五刀：研究 D10 CONG_HUA 从化
- 从格化格
- 特殊路径，可能 HOLD

### 暂不执行
- D6 TWO_SIDE 成势（作用语义）
- D8 STRUCTURE 影响根气（作用语义）
- D12 天覆地载（结构关系）
- D14 格局高低（非身强弱）
- D16 岁运（已冻结）

---

## 七、永久边界

- 不评分/不权重/不阈值/不计数
- 不汇总成 STRONG/WEAK
- 矛盾共存不裁
- 结构匹配 ≠ 命题成立
- evidence_refs 空 ≠ 有证据
- 格局层（D14）不混入身强弱矩阵
- 调候（D9）独立体系，不与身强弱混算
