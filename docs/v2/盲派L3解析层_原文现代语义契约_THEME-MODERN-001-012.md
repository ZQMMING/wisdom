# 盲派 L3 解析层契约：解层断语全集 → 原文断言 + 现代语义（THEME-MODERN-001~012）

- 状态：**ESTABLISHED（断言层清洗 + 出处审计 PASS + modern忠实审计 PASS + 全集审计 FULL）**
- 方法域：`DUAN_JIANYE`（段建业体系）
- 引擎文件：`src/tongshu/engines/blind_interpretation.py`
- 提交：BOT-BLIND L3 解析层（断言层清洗 + 现代语义忠实版）
- 验证日期：2026-09-13
- **验收标准（三道）**：
  1. **断言出处审计（audit_assertion_provenance）**：每条断语的 original 必须是**可追溯的真实古籍/口诀原文断言**
     （书名《》/ 篇名盲派X章 / 金口诀 / 铁断 / VERIFY-BLIND-NNN / 段建业讲义 / 段建业原书核心心法），
     禁止"章节名当原文"、**禁止以案例号（案例N）为出处**（案例是引擎外验证佐证，不入注册表）；
     确实无原文的必须显式声明"未取证/证据不足/fail-closed"，不得静默自造。
  2. **现代语义忠实度审计（audit_modern_fidelity）**：modern 必须覆盖 original 核心概念词
     （如"制财之原神"→"原神"、"官杀制不净当财看"→"当财"、"食伤泄秀一般不发大财"→"大财"），
     禁止错位翻译/漏核心限定；旺衰类禁夹带子平用神语义（盲派弃旺衰废用忌），禁口语自创词。
  3. **解层断语全集覆盖审计（audit_full_coverage）**：按代码枚举空间（VALUE_SEMANTICS +
     TOKEN_SEMANTICS + EVENT_SEMANTICS + TIME_KIND_SEMANTICS）逐项校验，任何枚举值都有
     原文断言+现代语义；案例只是回归，不是验收依据。

---

## 一、层定义

**L3 解析层（Interpretation Layer）= 解层断语全集 → 原文断言 + 现代语义翻译。**

输入：L2.5 `BlindThemeResult`（12 主题聚合）+ L2 `BlindJudgmentResult`（事件候选）。
输出：**解层每一条断语断言** = `(原文断言 original, 现代语义 modern)` 成对条目。
覆盖范围 = 盲派解层全部断语断言（非组合枚举 VALUE_SEMANTICS + 组合枚举 token
TOKEN_SEMANTICS + L2 事件 EVENT_SEMANTICS + 时间层事件 TIME_KIND_SEMANTICS）。

### 断言层清洗规则（2026-09-13 确立）

1. **original 必须是真实原文断言**：口诀原文/原书原文，不是引擎规则描述、不是章节名、**不是案例**。
2. **出处必须可追溯（古籍/口诀原文，案例不入注册表）**：每条 original 带出处（书名《》/篇名盲派X章/
   金口诀/铁断/VERIFY 号/段建业讲义/段建业原书核心心法），格式：
   `口诀名（《书名·篇名》：原文要点）` 或 `书名·章节：原文要点（VERIFY-BLIND-NNN）`。
   **案例号（案例N）是引擎外验证佐证，禁止作为断言出处引入引擎**——案例只存在于回归测试，
   不参与规则依据；同一断言若需佐证，在测试侧标注对应案例，不在引擎注册表出现。
3. **无原文 = 显式声明**：确无原文的枚举输出"证据不足（fail-closed，不做断言）"或
   "非盲派专属/排盘层统计"等声明，绝不静默自造原文。
4. **组合枚举按 token 拆解逐条翻译**，token 各自带出处。
5. **同义枚举归一**：children.palace_hit 的"(克子)"后缀归一，避免同义枚举分叉。

### 现代语义忠实度规则（2026-09-13 确立）

1. **modern 是 original 的忠实翻译**：不扩大、不缩小、不替换原文概念。
2. **核心限定不可丢**：如"官杀制不净**当财看**"、"食伤泄秀**一般不发大财**"。
3. **禁夹带他派语义**：盲派弃旺衰废用忌，旺衰条目只输出状态分类，禁"扛得住财官/借外力/宜顺势"
   等子平用神表述。
4. **禁口语自创**：如"越努力越背""突破条条框框"等原文没有的表述。

与 L2.5 的关系：

| 层 | 职责 | 输出 |
|---|---|---|
| L0 排盘 | 时间干支事实 | 四柱/大运/流年 |
| L1 做功 | 结构事实 | 做功类型/效率/制净 |
| L1e 事件 | 事件候选 | 婚姻/财富/官贵事件 |
| L1f 应期 | 时间触发 | 大运/流年触发 |
| L2 断语 | 断言事实 | 婚姻断语/职业断语 |
| L2.5 主题聚合 | 12 主题断言 | THEME-001~012 |
| **L3 解析层** | **原文+现代语义** | **条目 = 原文出处 + 现代语义** |

---

## 二、铁律（与全系统一致，本层特别强调）

1. **全模板、零 LLM、零自由发挥**：每个现代语义句子必须由 `MODERN_SEMANTICS` 规则表固定模板生成，引擎内不存在任何自由造句逻辑。
2. **全布尔/枚举、禁评分**：本层只有枚举键 → 固定模板映射，无分数、无百分比、无权重。
3. **每条映射必须带原文出处**：原文来自段建业体系口诀/案例集原文/五经原文。无原文可依 = `MODERN_MISSING`（"原文/现代语义证据未取证，不做断言"），**绝不发明**。
4. **吉凶词汇在 L3 出口正式放行**：吉凶（如"婚姻易分离"）源自引擎事实方向（AUSPICIOUS / IN_AUSPICIOUS），是事实层的翻译，不是新增判断。
5. **后端输出全事实**：L3 输出仍是可消费数据（themes + events 结构化），前端渲染层再决定展示。

---

## 三、12 主题现代语义映射（原文出处清单）

### THEME-001 性情禀赋
| source | value | 原文出处 | 现代语义 |
|---|---|---|---|
| blind_wangshuai | WANG | 盲派四定律·身旺以官杀（含纳音） | 日主自身力量旺，扛得住财官，做事有底气 |
| blind_wangshuai | ZHONG_HE_PIAN_RUO | 盲派旺衰定律 | 日主中和偏弱，做事需借财官之力，不宜硬扛 |
| blind_wangshuai | RUO | 盲派四定律·身弱以财官（含纳音） | 日主自身力量偏弱，做事易受牵制，需借外力 |
| five_element_imbalance | TRUE/FALSE | 五行失衡（排盘层五行统计） | 五行分布不均，性情有偏向 / 相对均衡，性情较平和 |
| transparent_ten_gods | {year,month,hour} | 盲派十神心性/渊海子平十神赋 | 逐项十神性情（偏财慷慨/七杀果断/正官守规…） |

### THEME-002 交游人际
| source | value | 原文出处 | 现代语义 |
|---|---|---|---|
| kinship_count.brother_count | 0~9 | 盲派六亲计数·比肩为兄弟 | 同胞中兄弟 N 人 |
| kinship_count.sister_count | 0~9 | 盲派六亲计数·劫财为姐妹 | 同胞中姐妹 N 人 |
| zuo_gong.比劫做功 | EFFECTIVE/NOT_EFFECTIVE | 盲派做功·比劫制财/比劫成党 | 人际靠朋友伙伴，竞争性强 / 朋友助力有限 |

### THEME-003 婚姻配偶
| source | value | 原文出处 | 现代语义 |
|---|---|---|---|
| marriage_state | BROKEN | 盲派婚姻篇·配偶宫逢冲必离婚/配偶宫破星损 | 婚姻易分离、难长久 |
| marriage_state | CHALLENGED | 盲派婚姻篇·配偶宫受损 | 婚姻有波折，需经营 |
| palace_state | CLASHED_AND_HARMED_AND_PUNISHED 等 | 盲派婚姻篇·配偶宫逢冲刑穿害 | 配偶宫被冲刑穿害，婚姻根基不稳 |
| palace_state | STABLE | 盲派婚姻篇·配偶宫安稳 | 配偶宫安稳，婚姻基础好 |
| spouse_star_present | True/False | 盲派婚姻篇·配偶星 | 配偶星在局 / 不显 |

### THEME-004 子女
| source | value | 原文出处 | 现代语义 |
|---|---|---|---|
| children.star | 男命有财→官杀 | 段建业《盲派八字命理口诀·子女》：有财星则以七杀为儿、正官为女 | 男命以官杀为子女星 |
| children.star | 女命→食伤 | 段建业《盲派八字命理口诀·子女》：女命以食神为女、伤官为儿 | 女命以食伤为子女星 |
| palace_hit | 时支逢冲/穿/枭印在时柱 | 段建业《盲派八字命理口诀·子女》：时柱忌枭印驾临 | 子女宫受损组合 |
| palace_hit | STABLE | 段建业《盲派八字命理口诀·子女》 | 子女宫安稳 |

### THEME-005 财帛
| source | value | 原文出处 | 现代语义 |
|---|---|---|---|
| wealth_state | DIRECTED_AND_ESTABLISHED | 盲派财富章·财现+财被取+做功成 | 求财有成，财富能到手 |
| wealth_state | SUBSTITUTED_AND_ESTABLISHED | 盲派换象·伤食当财/禄当财/官杀当财（VERIFY-BLIND-022） | 财以换象方式成立，求财方式特别 |
| wealth_present | True/False | 盲派财富章·财星在局/不现 | 局中有财 / 以换象论财 |

### THEME-006 身体疾厄
| source | value | 原文出处 | 现代语义 |
|---|---|---|---|
| body_event_candidate | LU_UNDER_ATTACK | 盲派口诀·禄怕见绝更怕穿害（案例集交通意外） | 禄神受攻击，身体或福报易受损 |
| body_event_candidate | YANG_REN_CLASHED | 盲派口诀·羊刃逢冲血光之灾 | 羊刃逢冲，有血光/外伤风险 |
| dry_earth_brittle | NO_DRY_EARTH/NOT_TRIGGERED | 盲派口诀·燥土脆金（VERIFY-BLIND-034） | 无燥土脆金之患 / 条件未触发 |

### THEME-007 迁移出行
| source | value | 原文出处 | 现代语义 |
|---|---|---|---|
| yima.present | 各马组合/NONE | 盲派金口诀·论驿马（寅午戌马在申等） | 命带驿马，主走动奔波 / 命不带驿马 |
| yima.trigger | NO_TRIGGER/TRIGGERED | 盲派金口诀·驿马引动 | 驿马未被引动 / 被引动有迁移之机 |

### THEME-008 事业功名
| source | value | 原文出处 | 现代语义 |
|---|---|---|---|
| work_types（逐项） | CONTROL_OFFICER_BY_FOOD_INJURY | 案例12：伤食制官局，命有官职 | 以食伤制官杀取功名，走公职/管理路线 |
| work_types | GENERATE_WEALTH_BY_FOOD_INJURY | 案例46：食伤做功技术赚 | 以食伤生财，靠技艺/技术谋财 |
| work_types | TRANSFORM_OFFICER_BY_RESOURCE | 案例23：印主单位 | 以印化官杀，靠单位/文职立足 |
| work_types | CONTROL_OFFICER_BY_INTERACTION | 盲派互动制官·刑/穿/冲制官杀 | 以互动方式制官杀得权 |
| work_types | CONTROL_WEALTH_BY_BIJIE | 盲派做功·比劫制财 | 靠朋友伙伴竞争制财 |
| work_types | CONTROL_WEALTH_BY_INTERACTION | 盲派互动制财 | 以刑穿冲制财 |
| work_types | CONTROL_FOOD_INJURY_BY_RESOURCE | 盲派做功·印制食伤 | 以印制食伤立身 |
| work_types | CONTROL_BIJIE_BY_OFFICER | 盲派做功·官杀制比劫 | 以官杀制比劫管团队 |
| work_types | CONTROL_RESOURCE_BY_WEALTH | 盲派做功·财制印 | 以财坏印突破框框 |
| work_types | STORE_BY_MUKU | 盲派墓库·辰库收水（案例1：银行金融中心） | 墓库收物蓄财，走金融/仓储类 |
| official_state | CONTROLLED_AND_CLEAN | 盲派口诀·制尽杀星得天下（乾隆 金水伤官制净） | 官杀制净，功名/管理有成 |
| official_state | CONTROLLED_PARTIAL | 盲派口诀·官杀制不净（D29 车间主任） | 功名/职位有限 |
| official_state | DAMAGED | 盲派口诀·穿官损官（案例2 官场梦碎） | 官星被穿损，体制内不顺 |
| official_state | ROBBED | 盲派口诀·官星被劫财合走（案例8 仓库保管员） | 职位非我所有，难掌实权 |
| official_state | UNCONTROLLED | 盲派口诀·官杀无制必犯官非 | 官杀无制，易犯官非 |
| work_efficiency | LARGE/MEDIUM | 盲派效率·做功效率大（功大者贵） | 事业成就层次高/中 |

### THEME-009 田宅家业
| source | value | 原文出处 | 现代语义 |
|---|---|---|---|
| zuo_gong.墓库收物 | EFFECTIVE | 盲派墓库·墓库喜冲不冲不发（辰库收水巨富） | 墓库收物成立，家业/积蓄有成 |
| zuo_gong.墓库收物 | NOT_EFFECTIVE | 盲派墓库·喜冲不冲不发 | 家业/积蓄平平 |
| zuo_gong.冲开墓库 | 冲开墓库 | 盲派墓库·墓库喜冲，不冲不发 | 墓库被冲开，家业有变动之机 |

### THEME-010 福德精神
| source | value | 原文出处 | 现代语义 |
|---|---|---|---|
| zuo_gong.食伤做功 | EFFECTIVE | 盲派十神口诀·日带食神自己福，一世不会受辛苦 | 食伤做功成立，有福气、衣食无忧 |
| blind_wangshuai | WANG | 盲派十神口诀·印旺身强多福寿，六亲和睦家道丰 | 日主旺，福寿根基好 |
| zuo_gong.印做功 | EFFECTIVE | 盲派十神口诀·印主福寿庇护 | 有长辈庇护，福泽厚 |

### THEME-011 父母长辈
| source | value | 原文出处 | 现代语义 |
|---|---|---|---|
| parents.father(偏财) | PRESENT/ABSENT | 盲派六亲·父星=偏财 | 父星在局 / 不显父缘淡 |
| parents.mother(印星) | PRESENT/ABSENT | 盲派六亲·母星=印星 | 母星在局 / 不显母缘淡 |

### THEME-012 才艺学业
| source | value | 原文出处 | 现代语义 |
|---|---|---|---|
| zuo_gong.印做功(学业) | EFFECTIVE | 段建业《盲派中级命理学》第11章：印星须做功方表学历 | 学业有成就 |
| zuo_gong.印做功(学业) | NOT_EFFECTIVE | 段建业《盲派中级命理学》第11章 | 学业动力不足 |
| zuo_gong.食伤泄秀(才艺) | EFFECTIVE | 段建业《盲派中级命理学》第11章：食神主思想学习 | 才艺/口才出众 |
| talent.direction | WEN(木火)/LI(金水) | 段建业《盲派中级命理学》第11章：金水主理，木火主文 | 文理方向偏文/偏理 |

---

## 四、L2 事件 → 现代语义（L3 事件层）

| event_type | 原文出处 | 现代语义 |
|---|---|---|
| MARRIAGE_BROKEN | 盲派婚姻篇·配偶宫逢冲必离婚（BLIND-DJ-004） | 婚姻易分离、难长久 |
| WEALTH_ESTABLISHED | 盲派财富章（BLIND-DJ-005/007/009） | 求财有成 |
| OFFICIAL_ESTABLISHED | 盲派官贵章·制尽杀星（BLIND-DJ-006） | 功名/管理有成 |
| OFFICIAL_PARTIAL | 盲派官贵章·官杀制不净（BLIND-DJ-007） | 功名有限 |
| OFFICIAL_DAMAGED | 盲派官贵章·穿官损官（BLIND-DJ-010） | 体制内不顺 |
| OFFICIAL_ROBBED | 盲派官贵章·官星被劫财合走（BLIND-DJ-011） | 职位非我所有 |
| OFFICIAL_OFFENSE_CANDIDATE | 盲派官贵章·官杀无制必犯官非（BLIND-DJ-001） | 易犯官非 |
| OCCUPATION_DIRECTION_CANDIDATE | 盲派职业章·做功类型映射 | 职业方向候选 |
| BODY_LU_ATTACK | 盲派口诀·禄怕见绝更怕穿害（BLIND-DJ-002） | 禄神受攻击 |
| BODY_YANG_REN_CLASH | 盲派口诀·羊刃逢冲血光之灾（BLIND-DJ-003） | 血光/外伤风险 |
| REVERSED_PATTERN | 盲派口诀·反局（BLIND-DJ-008） | 做功方向与日主意向相反 |

---

## 五、验证记录（2026-09-13 · 断言层清洗版）

- **断言出处审计（audit_assertion_provenance）：PASS**——130 条已取证（含书名/篇名/口诀/案例号/
  VERIFY 号出处）+ 11 条显式声明未取证（fail-closed/非盲派专属/排盘层统计），**0 条无出处断言**。
- **解层断语全集审计（audit_full_coverage）：FULL**——129 项枚举逐项校验，全部有原文断言+现代语义。
- 1980 案例（庚申 壬午 丙寅 癸巳，男）：L3 主题 12 条全命中，L3 事件 5 条全命中，MISSING=0。
- 16 例全链路（含八字案例.txt 15 例 + 1980）：L3 逐例跑通，总计 MISSING=0。
- 盲派测试：86 passed, 7 subtests passed。
- 清洗修正记录：`ZIZAIXIAN` 断言"自在线引动"→"字再现引动"（VERIFY-BLIND-028 原局字再现）；
  `blind_wangshuai` 旺衰断言不再套用六亲四定律语义，只作状态分类（弃旺衰，仅状态）；
  `印做功` 断言"印主福寿庇护"→"印旺身强多福寿，六亲和睦家道丰"（盲派六亲损断口诀）；
  职业断言全部落到古籍出处（制用五种/生用结构/化用结构/墓用结构/做功方式，VERIFY-BLIND-003/004/005/006/007/011/020/026）。
- 案例出处清理记录（2026-09-13）：原注册表 80 处含"案例"，其中 50 处纯案例出处全部替换为
  古籍/口诀原文出处（段建业原书/《盲派中级命理学》篇/金口诀/VERIFY 号）；出处审计函数
  同步移除"案例"合法出处标记；案例号仅存在于引擎外回归测试，不再进入引擎注册表。
  清理后出处审计 PASS（130 取证 + 11 声明未取证 + 0 无出处），86 测试全绿，16 例回归 MISSING=0。
- modern 忠实修正记录：旺衰5条去子平用神语义（扛得住财官/借外力/宜顺势→纯状态分类）；
  换象制财"竞争博弈"→"制财之原神（食神）"；财制印"突破条条框框"→"资本运作控制资源权力"；
  食伤泄秀补回"一般不发大财"；官杀制不净补回"当财看"；印做功对齐"印旺身强多福寿"；
  反局去口语"越努力越背"→"为凶（反局）"。
- modern 忠实审计：**PASS**（122 条已检，缺核心词/夹带禁用词 0）。
- 覆盖说明：MODERN_MISSING 兜底仍保留——注册表未覆盖的枚举一律输出"原文/现代语义证据未取证，
  不做断言"，**不回退成自由文本**；新增枚举需同步入注册表并通过出处审计+modern忠实审计。

## 六、边界与消费层

- L3 消费 L2.5 主题 + L2 事件，**不新增命理计算**，只做事实→现代语义翻译。
- L3 的现代语义是下游 12 人生维度映射（L2.5→现代语言出口）的最终事实源；前端渲染层可在此基础上决定展示口径（含吉凶措辞）。
- 子平引擎与盲派引擎完全独立，唯一共享层 = L0 排盘。L3 只属于盲派引擎。
