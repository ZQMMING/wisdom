# 盲派规则 V1-FINAL · 修订层：做功强弱（做功效率）规则域

> 修订依据：用户指令"查古籍是否有做功强弱，先将规则优化好再执行其他"
> 修订对象：`C:\Users\ming\Desktop\盲派生产规则.txt` 第 38 节「"效率"重新定义」
> 修订方式：§38 升级为完整规则域 `WK-EFFICIENCY-001~005`；其余 93 节 V1-FINAL 原文保持不变
> 状态：RULE_REGISTRY_DRAFT-FOR-VERIFICATION（证据未全部核证，见 §五）

---

## 一、查证结论：古籍确有"做功强弱"，且是盲派层次判断核心指标

### 1.1 古籍原文（证据库已收录，出处均标段建业著作+章节+页码）

| 证据 ID | 出处（source 字段） | 原文核心 |
|---|---|---|
| E-BLIND-WORK_EFFICIENCY-001 | 《盲派初级命理学》段建业·第二章 做功详解·第二节 做功效率·p.20-25 | "做功效率是指做功的效果大小。效率高则富贵层次高，效率低则富贵层次低。做功效率分为：**大效率、中效率、小效率、无效做功**。" |
| E-BLIND-WORK_EFFICIENCY-002 | 《段氏理象学——盲派命理研究》段建业·案例篇·做功效率·p.110-120 | "做功等级分为：**大贵、中贵、小贵、平常、贫贱**。大贵之命做功效率高，结构清晰；中贵之命做功效率中等，结构较清；小贵之命做功效率较低，结构有杂；平常之命做功效率低，结构混乱；贫贱之命无效做功或做功有误。" |
| E-BLIND-WORK_EFFICIENCY-005 | 《盲派初级命理学》段建业 | "做功效率高低的判断：**看做功路径是否直接、看做功力量是否集中、看做功对象是否得力**。" |
| E-BLIND-C-EFFICIENCY_CASE-001 | 《盲派命理-案例资料集》段建业·第五章 做功效率案例·第三节 高效做功案例·p.118-122 | 案例层：高效做功判定 |
| E-BLIND-C-EFFICIENCY_CASE-002 | 《盲派命理-案例资料集》段建业·第三章 做功效率·第二节 效率分级·p.65-70 | 案例层：效率分级 |
| E-BLIND-C-EFFICIENCY_EXAMPLE-001 | 《段氏理象学》段建业·案例篇·做功效率·p.110-120 | "庚申 戊子 壬辰 甲辰……做功在食神泄秀，效率较高，主文采出众。" |

### 1.2 关键性质：古籍的"做功强弱"是结构性表述，无任何数字

- 等级是**枚举**：大效率 / 中效率 / 小效率 / 无效做功
- 做功等级是**枚举**：大贵 / 中贵 / 小贵 / 平常 / 贫贱
- 判据是**布尔判断**：路径是否直接、力量是否集中、对象是否得力
- 外显是**结构状态**：结构清晰 / 较清 / 有杂 / 混乱

→ 结论：规则"不得数字化"方向正确，但 §38 原文仅引"[算准网]"（二手中介，违反本文件 §71-72 来源等级：二手中介只能 RESEARCH_CANDIDATE，不得进核心规则），且缺少古籍原话的三判据、等级枚举、结构外显。必须替换来源并补全规则链。

### 1.3 证据核证状态（当前）

- `source_verification_final_report.json` 对 WORK_EFFICIENCY-001/002、C-EFFICIENCY_CASE-001/002、C-EFFICIENCY_EXAMPLE-001 均判 `DOWNGRADED`，issues = `no_author / no_chapter / no_locator`。
- **原因已定位（数据层，非内容层）**：出处信息（段建业/章节/页码）实际存在，但放在证据 JSON 的 `source` 对象内部字段；核证程序读取的是证据条目**顶层** `author/chapter/locator` 字段（为空），导致误判降级。
- 处置：修复字段映射后重新核证，转 `PRIMARY_TEXT / AUTHOR_TEXT` 后进核心规则。此处置列为 VERIFY-BLIND-031（见 §五）。

---

## 二、规则优化：§38 升级为「做功强弱规则域」

替换原 §38 全文为以下内容：

---

# 38. 做功强弱（做功效率）规则域

## 38.1 来源（替换原"[算准网]"引用）

- 《盲派初级命理学》段建业：第二章·做功详解·第二节·做功效率，p.20-25
- 《段氏理象学——盲派命理研究》段建业：案例篇·做功效率，p.110-120
- 《盲派命理-案例资料集》段建业：第三章·做功效率·效率分级，p.65-70；第五章·做功效率案例·高效做功案例，p.118-122
- 证据：E-BLIND-WORK_EFFICIENCY-001 / -002 / -005、E-BLIND-C-EFFICIENCY_CASE-001 / -002、E-BLIND-C-EFFICIENCY_EXAMPLE-001

## 38.2 核心原则（保持 V1-FINAL 最高裁决不变）

```text
做功强弱 = 结构性枚举状态，绝不数字化
禁止: efficiency = 95% / work_power > target_power / A_count > B_count / 百分比 / 评分 / 权重
允许: 等级枚举 + 布尔判据 + 结构外显状态
```

## 38.3 WK-EFFICIENCY-001 做功强弱定义（布尔结构枚举）

```text
IF
METHOD_SCOPE = DUAN_JIANYE
THEN
WORK_EFFICIENCY ∈ { LARGE, MEDIUM, SMALL, NONE }
```

| 枚举 | 古籍原话对应 | 禁止等价物 |
|---|---|---|
| LARGE | 大效率 | 禁 efficiency=high_score、work_power>阈值 |
| MEDIUM | 中效率 | 禁 efficiency=medium_score |
| SMALL | 小效率 | 禁 efficiency=low_score |
| NONE | 无效做功 | 禁 efficiency=0 分 |

## 38.4 WK-EFFICIENCY-002 做功强弱三判据（布尔规则）

古籍原话：做功效率高低判断 = 做功路径是否直接、做功力量是否集中、做功对象是否得力。

```text
IF
WORK_PATH_DIRECT            # 路径直接：主宾→体用→做功为单一明确作用链，无阻断/无中介绕行
AND
WORK_POWER_CONCENTRATED     # 力量集中：参与做功干支构成单一作用集；禁 actor_count>=3 围制
AND
WORK_TARGET_EFFECTIVE       # 对象得力：功神/做功目标有根（ROOTED）且未被制、未被合绊（BINDING）
THEN
WORK_EFFICIENCY = LARGE
```

```text
IF
WORK_PATH_DIRECT
AND ( WORK_POWER_CONCENTRATED OR WORK_TARGET_EFFECTIVE )
AND NOT ( WORK_PATH_DIRECT AND WORK_POWER_CONCENTRATED AND WORK_TARGET_EFFECTIVE )
THEN
WORK_EFFICIENCY = MEDIUM
```

```text
IF
WORK_PATH_DIRECT
AND NOT WORK_POWER_CONCENTRATED
AND NOT WORK_TARGET_EFFECTIVE
THEN
WORK_EFFICIENCY = SMALL
```

```text
IF
NOT WORK_PATH_DIRECT
OR WORK_ERRORED            # 做功有误：作用方向颠倒、穿倒 OVERTURNED、中链断 FAILED
THEN
WORK_EFFICIENCY = NONE
```

三判据各自的子条件（WORK_PATH_DIRECT / WORK_POWER_CONCENTRATED / WORK_TARGET_EFFECTIVE）必须由 method_scope 内既有结构规则（宾主 BG、体用 BU、做功 WORK、功神 GS、虚实 VR、制 WK-CONTROL）推导，禁止另行定义独立数值来源。

## 38.5 WK-EFFICIENCY-003 结构外显映射（伴生状态）

```text
WORK_EFFICIENCY = LARGE   → STRUCTURE_CLARITY = CLEAR          # 结构清晰
WORK_EFFICIENCY = MEDIUM  → STRUCTURE_CLARITY = PARTIALLY_CLEAR # 结构较清
WORK_EFFICIENCY = SMALL   → STRUCTURE_CLARITY = MIXED          # 结构有杂
WORK_EFFICIENCY = NONE    → STRUCTURE_CLARITY = CHAOTIC        # 结构混乱/做功有误
```

- 结构外显是做功强弱的**推导结果**，不作为独立计数来源。
- 禁反推：禁"结构杂 → 效率低"作为独立判据（必须回到 38.4 三判据）。

## 38.6 WK-EFFICIENCY-004 做功等级（理法-结果层）

```text
WORK_LEVEL ∈ { LARGE_NOBLE, MEDIUM_NOBLE, SMALL_NOBLE, ORDINARY, POOR }
```

由 做功强弱 + 结构外显 共同产生（古籍原文映射）：

| 做功等级 | 做功强弱 | 结构外显 | 古籍原话 |
|---|---|---|---|
| LARGE_NOBLE 大贵 | LARGE | CLEAR | 效率高，结构清晰 |
| MEDIUM_NOBLE 中贵 | MEDIUM | PARTIALLY_CLEAR | 效率中等，结构较清 |
| SMALL_NOBLE 小贵 | SMALL | MIXED | 效率较低，结构有杂 |
| ORDINARY 平常 | SMALL/NONE | CHAOTIC 边缘 | 效率低，结构混乱 |
| POOR 贫贱 | NONE | CHAOTIC | 无效做功或做功有误 |

- 此层属"理法-结果"，为判断层输出，不参与排盘事实层。
- 禁：财富等级公式、百分比效率、数量推断（本文件 §74 禁止吸收内容）。
- method_scope 标注：五档等级映射按传承差异可调整（如 XIA_ZHONGQI 是否细分），冲突时按 §90 规则裁决，不合并。

## 38.7 WK-EFFICIENCY-005 与既有枚举对齐（实现层）

```text
WORK_EFFICIENCY = LARGE  ↔ CONTROL_COMPLETENESS = COMPLETE   # 全部控制路径有效
WORK_EFFICIENCY = NONE   ↔ CONTROL_COMPLETENESS = INCOMPLETE # 无有效做功
                            WORK_BROKEN = BROKEN             # 做功有误/中链断
```

- 盲派语义层枚举（LARGE/MEDIUM/SMALL/NONE）与实现层枚举（EFFECTIVE/PARTIAL/BLOCKED/BROKEN/COMPLETE/INCOMPLETE）并存，语义层由 38.4 推导，实现层由制用/复合做功规则推导，二者通过上表对齐，不得互相替代。

---

## 三、新增核证项：VERIFY-BLIND-031~033

原 VERIFY-BLIND-001~030 不变，追加：

```text
VERIFY-BLIND-031  做功强弱四档（大/中/小/无效做功）
                  → 核证 E-BLIND-WORK_EFFICIENCY-001/-002/-005 原文
                  → 处置：修复 source 字段映射（顶层 author/chapter/locator），
                    重新跑 source_verification，转 PRIMARY_TEXT/AUTHOR_TEXT
VERIFY-BLIND-032  做功三判据（路径直接/力量集中/对象得力）
                  → 核证 E-BLIND-WORK_EFFICIENCY-005 + C-EFFICIENCY_CASE-001/-002
                  → 核证通过前，38.4 中 MEDIUM/SMALL 的精确分支映射保持
                    METHOD_SCOPE_PENDING，不得自行发明
VERIFY-BLIND-033  做功等级五档与结构外显映射
                  → 核证 E-BLIND-WORK_EFFICIENCY-002
                  → 确认大贵→贫贱五档在五部经典/盲派传承内无冲突
```

---

## 四、对其他章节的影响

| 章节 | 影响 | 处置 |
|---|---|---|
| 第 0 节最高裁决 L5/L9 | 无冲突，本修订是 L9 的落地展开 | 保持 |
| BLIND-ARCH-006（L182-186） | 无冲突，本修订给出"结构枚举"的具体形式 | 保持 |
| §37 制尽 | WK-EFFICIENCY-005 与 CONTROL_COMPLETENESS 对齐 | 保持 |
| §39 结构层级 | 做功强弱 ≠ 层功数；禁"一层功/二层功"数字叠加与做功强弱混用 | 保持（新增禁止：做功强弱不得由层功数量推导） |
| BLIND-G16 | 无冲突，"数字化能量/效率/层功清除"是本修订的验收门 | 保持 |
| §71-72 来源等级 | 本修订将 §38 来源从二手中介（算准网）升级为 AUTHOR_TEXT 候选 | 生效 |

---

## 五、状态

```text
ARCHITECTURE_STATUS     = APPROVED
RULE_REGISTRY_STATUS    = DRAFT-FOR-VERIFICATION   # WK-EFFICIENCY-001~005 已锁语义，
                                                    # 证据核证（VERIFY-BLIND-031~033）通过前不施工
IMPLEMENTATION_STATUS   = BLOCKED                  # 与 V1-FINAL 一致：核证先行
EVIDENCE_STATUS         = WORK_EFFICIENCY 6 条证据：DOWNGRADED（字段映射修复后重核证）
```

最高禁令（沿用 V1-FINAL）：事实 + 已验证中间状态 + AND/OR/NOT → 枚举结果；不得自行补全做功强弱判据；核证清单不得当 TODO 跳过。
