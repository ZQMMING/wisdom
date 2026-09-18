# 盲派 Rule Evidence 母表 V2（生产规则唯一准入来源）

> **工程禁令**：CASE MUST NEVER BE A RULE SOURCE.
> 任何从案例中发现的规律，必须重新追溯至具名原典规则并取得 Rule Evidence 后，方可进入 Rule Registry。
> 案例另存《Case Golden 母表》，只做 Golden/Regression/Edge/Counter 测试。

---

## 字段定义

| 字段 | 内容 |
|---|---|
| Evidence_ID | 唯一 ID |
| Source | 书名 |
| Chapter | 章节 |
| Passage | 原文 |
| Rule_Type | STRUCTURE / SYMBOL / TIMING |
| Preconditions | 前置条件 |
| Inputs | 输入事实 |
| Operators | 布尔 / 枚举 / 关系 |
| Rule | 机器规则 |
| Assertion | 输出断言 |
| Scope | 适用范围 |
| Exclusions | 禁止推导 |
| Provenance | 原典定位 |

---

## L1 STRUCTURE（结构层）

### R-PJ-001 正局判定
- **Source**：《盲派中级命理学》
- **Chapter**：第01章 正局、反局
- **Passage**：正局：日柱做功，所表达的意思与原局表达的意思一致。八字无势，日主能做功也称为正局。
- **Rule_Type**：STRUCTURE
- **Preconditions**：日主做功或日支做功已识别
- **Inputs**：day_master_work_direction, day_branch_work_direction, original_structure_direction
- **Operators**：EQUAL
- **Rule**：IF (day_master_work_direction == original_structure_direction) OR (day_branch_work_direction == original_structure_direction) THEN
- **Assertion**：局型 = ZHENG
- **Scope**：原局
- **Exclusions**：不自动推吉；正局≠富贵，只记结构事实
- **Provenance**：第01章原文定义

### R-PJ-002 反局判定
- **Source**：《盲派中级命理学》
- **Chapter**：第01章
- **Passage**：反局：日柱做功所表达的意思与原局表达的意思相反，为凶。反局分原局反局、大运反局、流年反局三种。
- **Rule_Type**：STRUCTURE
- **Preconditions**：日主做功方向 vs 日支做功方向 vs 八字之势方向
- **Inputs**：day_master_work_direction, day_branch_work_direction, original_structure_direction
- **Operators**：NOT_EQUAL
- **Rule**：IF (day_master_work_direction != original_structure_direction) OR (day_branch_work_direction != original_structure_direction) OR (day_master_work_direction != day_branch_work_direction AND both_act) THEN
- **Assertion**：局型 = FAN
- **Scope**：原局/大运/流年三层
- **Exclusions**：不自动推凶事；反局只记结构事实，应期层再引动
- **Provenance**：第01章原文定义 + R1-R4 判断条件

### R-PJ-003 冲合反局（岁运层）
- **Source**：《盲派中级命理学》
- **Chapter**：第01章 岁运冲合反局
- **Passage**：原局有明确的制的时候，怕大运、流年合。如无明确的制，则不怕。天干合地支冲可以，不为反局；怕地支上又冲又合。
- **Rule_Type**：TIMING
- **Preconditions**：原局已有明确做功方式（冲/合/穿/刑）
- **Inputs**：original_work_method, luck_year_method, luck_branch
- **Operators**：CONFLICT
- **Rule**：IF original_work_method == CHONG AND luck_year_method == HE THEN FAN_JU_ACTIVE
- **Assertion**：岁运反局 = TRUE/FALSE
- **Scope**：大运/流年
- **Exclusions**：天干合地支冲不反；原局无明确制不反
- **Provenance**：第01章岁运反局节

### R-ZB-001 贼神捕神结构
- **Source**：《盲派八字体系》
- **Chapter**：第五章 贼神捕神
- **Passage**：主或者体比较旺，宾或者用相对弱，主制宾=贼捕。捕神=制者，贼神=被制者。
- **Rule_Type**：STRUCTURE
- **Preconditions**：宾主体用已识别
- **Inputs**：main_strength, guest_strength, main_kills_guest, guest_rootless
- **Operators**：GT, EQ
- **Rule**：IF main_strength > guest_strength AND main_kills_guest AND guest_rootless THEN
- **Assertion**：robber_catcher = TRUE, catcher = main_side, robber = guest_side
- **Scope**：原局
- **Exclusions**：贼捕≠直接大富贵；需叠加其他 Rule 才进财富层
- **Provenance**：第五章原文

### R-GF-001 功神/废神划分
- **Source**：《盲派八字体系》
- **Chapter**：第三章 功神废神
- **Passage**：参与做功的神=功神，不参与做功的=废神。功神耗散能量产生效率；废神不产生效率。
- **Rule_Type**：STRUCTURE
- **Preconditions**：做功方向已识别
- **Inputs**：working_branches, target_branches
- **Operators**：SET_MEMBERSHIP
- **Rule**：IF branch IN working_branches OR branch IN target_branches THEN GONG_SHEN ELSE FEI_SHEN
- **Assertion**：每字=功神/废神
- **Scope**：原局
- **Exclusions**：不直接推富贵
- **Provenance**：第三章原文

### R-BZ-001 宾主定位
- **Source**：《盲派八字体系》
- **Chapter**：第一章 宾主
- **Passage**：日柱=主，他柱=宾；日时=主，年月=宾；八字=主，大运流年=宾。
- **Rule_Type**：STRUCTURE
- **Preconditions**：四柱已排
- **Inputs**：pillar_position
- **Operators**：ENUM
- **Rule**：day/hour = MAIN; year/month = GUEST
- **Assertion**：每柱=MAIN/GUEST
- **Scope**：全局
- **Exclusions**：—
- **Provenance**：第一章原文

### R-TY-001 体用定位
- **Source**：《盲派八字体系》
- **Chapter**：第二章 体用
- **Passage**：体=日主/印/禄/比劫；用=财/官杀。食伤中性（食偏体，伤偏用）。
- **Rule_Type**：STRUCTURE
- **Preconditions**：十神已排
- **Inputs**：ten_god
- **Operators**：ENUM
- **Rule**：DM/印/禄/比劫 = TI；财/官杀 = YONG；食伤 = NEUTRAL
- **Assertion**：每十神=TI/YONG/NEUTRAL
- **Scope**：全局
- **Exclusions**：不替代旺衰
- **Provenance**：第二章原文

---

## L2 SYMBOL（象法层）

### R-SX-001 共象原则
- **Source**：《象的应用原则》
- **Chapter**：一、共象
- **Passage**：某一字有干支象+宫位象+十神象，两类以上表示同一事物=共象成立。
- **Rule_Type**：SYMBOL
- **Preconditions**：干支象/宫位象/十神象/神煞象已提取
- **Inputs**：gan_xiang, zhi_xiang, gongwei_xiang, tenshen_xiang, shensha_xiang
- **Operators**：INTERSECTION
- **Rule**：IF COUNT(overlapping_xiang) >= 2 THEN
- **Assertion**：该字象 = intersection_meaning
- **Scope**：单字取象
- **Exclusions**：只有一类象=不立
- **Provenance**：第一章原文

### R-SX-002 合象原则
- **Source**：《象的应用原则》
- **Chapter**：二、合象
- **Passage**：天干五合/地支六合，相合双方互取象。一方定义另一方性质。
- **Rule_Type**：SYMBOL
- **Preconditions**：原局有合
- **Inputs**：he_pair[0], he_pair[1]
- **Operators**：MUTUAL_BORROW
- **Rule**：IF 合绊成立 THEN both_sides_borrow_each_other_xiang
- **Assertion**：合绊双方象 = A+B 复合象
- **Scope**：原局合绊
- **Exclusions**：无根之合不立
- **Provenance**：第二章原文

### R-SX-003 化象原则
- **Source**：《象的应用原则》
- **Chapter**：三、化象
- **Passage**：两象通过会合生化转化新象。阴木生火=纺织；阳木生火=家具；辰配子=化工制药。
- **Rule_Type**：SYMBOL
- **Preconditions**：有生/三合/半合
- **Inputs**：source_element, target_element
- **Operators**：TRANSFORM
- **Rule**：IF 阴木→火 THEN 象=纺织/服装; IF 阳木→火 THEN 象=家具/装潢; IF 辰→子 THEN 象=化工/制药
- **Assertion**：转化象
- **Scope**：原局生化
- **Exclusions**：—
- **Provenance**：第三章原文

### R-SX-004 墓象原则
- **Source**：《象的应用原则》
- **Chapter**：四、墓象
- **Passage**：墓=收藏控制。所墓之神决定象。七杀入羊刃墓=军队；食伤库=学校工厂；财星墓=建筑地产。
- **Rule_Type**：SYMBOL
- **Preconditions**：有墓库
- **Inputs**：mu_god, mu_branch
- **Operators**：PATTERN
- **Rule**：IF 七杀入羊刃墓 THEN 象=军队; IF 食伤入墓 THEN 象=学校/工厂; IF 财入墓 THEN 象=建筑/地产
- **Assertion**：墓象
- **Scope**：原局墓库
- **Exclusions**：空库/实库另分
- **Provenance**：第四章原文

### R-SX-005 制象原则
- **Source**：《象的应用原则》
- **Chapter**：五、制象
- **Passage**：合制/克制/冲制/刑制/穿制，制法取复合象推断行业。
- **Rule_Type**：SYMBOL
- **Preconditions**：有制
- **Inputs**：controller, controlled, method
- **Operators**：COMPOSITE
- **Rule**：IF 财库制劫财印库 THEN 象=资本运作; IF 丑未冲制印库 THEN 象=地产实业
- **Assertion**：制象
- **Scope**：原局制法
- **Exclusions**：—
- **Provenance**：第五章原文

### R-SX-006 带象原则
- **Source**：《象的应用原则》
- **Chapter**：六、带象
- **Passage**：一柱干支以干统支，干决定支象特点。财带官帽=公家之财；官带财帽=管财的官；印带官帽=权力；印带财帽=薪水。
- **Rule_Type**：SYMBOL
- **Preconditions**：一柱干支同看
- **Inputs**：upper_gan_ten_god, lower_zhi_ten_god
- **Operators**：OVERLAY
- **Rule**：IF 财+官同柱 THEN 公家财; IF 官+财同柱 THEN 管财官; IF 印+官同柱 THEN 权力; IF 印+财同柱 THEN 薪水
- **Assertion**：带象
- **Scope**：单柱
- **Exclusions**：—
- **Provenance**：第六章原文

### R-SX-007 借象原则 ⚠️ 待补原文
- **Source**：待补
- **Chapter**：待补
- **Passage**：待补
- **Rule_Type**：SYMBOL
- **Preconditions**：待补
- **Inputs**：待补
- **Operators**：BORROW
- **Rule**：待补
- **Assertion**：待补
- **Scope**：待补
- **Exclusions**：待补
- **Provenance**：待补

---

## L3 TIMING（应期层，已有）

R-YQ-001~010：冲/合/刑/穿/墓/透干/字再现/见禄/空亡填实/开库
- 现状：引擎已有，对应段建业第02章

---

## 待补 Rule Evidence 清单

| ID | 规则 | 待补原文 |
|---|---|---|
| R-SX-007 | 借象原则 | 章+原文 |
| R-WH-001 | 禄神当财 | 第八章财命专辑 |
| R-WH-002 | 财库开启条件 | 第八章 |
| R-WH-003 | 财富等级分级 | 第八章 |
| R-MY-001 | 结婚应期 | 婚姻章 |
| R-MY-002 | 离婚应期 | 婚姻章 |
| R-JK-001 | 健康灾厄 | 健康章 |
| R-SH-001 | 神煞类象 | 神煞章 |
