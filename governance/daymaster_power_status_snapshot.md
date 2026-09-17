# 身强身弱工程状态快照（PATCH-160-B V2）

状态：D2 root_class 细分已完成
HEAD：5a1d7ed0
日期：2026-09-17

---

## 零、D2 完成记录（5a1d7ed0）

新增 `engines/common/daymaster_root_class.py`，8 类离散 RootClass：
- HEAVY_LONGSHENG / HEAVY_LU / HEAVY_WANG(刃别名 ren_alias)
- LIGHT_MU_KU / LIGHT_YU_QI
- SPECIAL_LONGSHENG_YIN（阴长生明根，独立级）
- NONE

关键发现：L0 root_facts 用"同字"判断，网络层补两类（非改 L0、非重算）：
1. 阳干帝旺位/墓库位藏阴干同类（甲卯藏乙、甲未藏乙、丙午藏丁）→ 同五行根
2. 阴长生位藏干全无日主五行（乙逢午藏丁己）→ 十二长生位置明根

阴干墓库按库中本气藏干精确判定：乙戌/丁丑/辛辰/癸未=NONE；己丑=有。
阴干不论羊刃，阴帝旺位保守 LIGHT_YU_QI。
刃=帝旺别名，不另建计算。
network D2 新增 root_class_detail（可选参数，默认行为不变）。
Golden 16/16 PASS；全量回归 67 PASS / 0 FAIL。
无数值/权重/求和/STRONG/WEAK。

下一候选：D13 透藏关系 或 T43 时柱位置；待用户拍板。

---

## 一、已落地文件

| 文件 | 状态 | 说明 |
|---|---|---|
| engines/common/daymaster_power_structure.py | 🔒 FROZEN | 160-A 五轴结构 |
| engines/common/daymaster_power_network.py | 🔒 FROZEN | 160-B V2 多维网络 |
| engines/common/daymaster_power_queries.py | 🔒 FROZEN | 160-C v0 三Query |
| governance/daymaster_power_network_direction.md | 🔒 FROZEN | 方向锁死 |
| governance/daymaster_power_matrix_design.md | 🔒 FROZEN | 16维矩阵 |

---

## 二、160-C v0 三 Query 状态

| Query | state | match_type | evidence |
|---|---|---|---|
| CAN_REN_CAIGUAN | SUPPORTED/NOT_SUPPORTED | STRUCTURE_MATCH/NO_MATCH | refs空（原文待定位） |
| DESHI_BUWANG | UNKNOWN | STRUCTURE_MATCH/NO_MATCH | PZZQ-005-005 |
| SHISHI_BURUO | UNKNOWN | STRUCTURE_MATCH/NO_MATCH | PZZQ-005-005 |

---

## 三、D2 root_type 细分开工规格（已校对通过）

### RootClass 枚举
```
HEAVY
├── HEAVY_LONGSHENG  长生
├── HEAVY_LU         禄（临官）
├── HEAVY_WANG       帝旺
└── HEAVY_REN        刃（帝旺别名，不重算）

LIGHT
├── LIGHT_MU_KU_YANG 阳干墓库
└── LIGHT_YU_QI      余气

SPECIAL
└── SPECIAL_LONGSHENG_YIN  阴长生（明根，约余气）

NONE
```

### 阴阳干规则
- 阳干逢库 = 有根（LIGHT_MU_KU_YANG）
- 阴干逢库：按库中本气藏干是否存在精确判定
  - 乙逢戌：戌中无藏木 → NONE
  - 丁逢丑：丑中无藏火 → NONE
- 阴干余气（乙逢辰、丁逢未）= LIGHT_YU_QI
- 阴长生（乙逢午、丁逢酉）= SPECIAL_LONGSHENG_YIN
- 刃不重算：用已有帝旺识别，只加原典语义标签

### 禁止
- 不做 power=1/2/3
- 不做 HEAVY=3/LIGHT=1
- 不做 sum(root_power)
- 不做根越多→越强
- 不做根力→STRONG/WEAK
- 不做 score/weight/threshold

### 验收 Golden
- 阳干长生 PASS
- 阳干禄 PASS
- 阳干帝旺 PASS
- 阳干羊刃 PASS（帝旺别名）
- 阳干墓库 PASS
- 阳干余气 PASS
- 阴干长生 SPECIAL PASS
- 阴干禄 PASS
- 阴干帝旺 PASS
- 阴干墓库 按藏干精确判定
- 阴干余气 PASS
- 普通无根 NONE

---

## 四、51 触发点分层（已校对）

### 🟢 纯结构（D2 这刀覆盖）
T4/T5/T8/T24/T38/T39/T40/T41/T42 共 9 个

### 🟡 半结构
T3（改名 OUT_OF_SEASON_WITH_ROOT）/ T15（已有）/ T43（时柱位置）

### 🔴 HOLD（作用语义）
T6/T7/T11/T12-T14/T30-T37/T44/T45

### ⚫ 特殊路径（不属普通身强弱）
T16-T29/T36/T46-T51

### T1/T2 纠正
- 不做 Query（PZZQ-005-005 原文自己拆了"得时便作旺"）
- 保留为 SEASONAL FACT

---

## 五、永久边界

- 不评分/不权重/不阈值/不计数
- 不汇总 STRONG/WEAK
- 矛盾共存不裁
- 结构匹配 ≠ 命题成立
- evidence_refs 空 ≠ 有证据
- T1/T2 不进 Query
- T3 用中性名 OUT_OF_SEASON_WITH_ROOT
- T39 按藏干精确
- T42 独立 SPECIAL
- REN 不重算
