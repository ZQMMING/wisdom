# 盲派 Rule Evidence 母表 V3（生产规则唯一准入来源）

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
| Status | ESTABLISHED / NOT_ESTABLISHED / IN_PROGRESS |

---

## L1 STRUCTURE（结构层）

### R-PJ-001 正局判定 ✅
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
- **Status**：ESTABLISHED

### R-PJ-002 反局判定 ✅
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
- **Status**：ESTABLISHED

### R-PJ-003 冲合反局（岁运层）✅
- **Source**：《盲派中级命理学》
- **Chapter**：第01章 岁运冲合反局
- **Passage**：原局有明确的制的时候，怕大运、流年合。如无明确的制，则不怕。天干合地支冲可以，不为反局；怕地支上又冲又合。
- **Rule_Type**：TIMING
- **Preconditions**：原局已有明确做功方式（冲/合/穿/刑）
- **Inputs**：original_work_method, luck_year_method
- **Operators**：CONFLICT
- **Rule**：IF original_work_method == CHONG AND luck_year_method == HE THEN FAN_JU_ACTIVE
- **Assertion**：岁运反局 = TRUE/FALSE
- **Scope**：大运/流年
- **Exclusions**：天干合地支冲不反；原局无明确制不反
- **Status**：ESTABLISHED

### R-ZB-001 贼神捕神结构 ✅
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
- **Status**：ESTABLISHED

### R-GF-001 功神/废神划分 ✅
- **Source**：《盲派八字体系》
- **Chapter**：第三章 功神废神
- **Passage**：参与做功的神=功神，不参与做功的=废神。
- **Rule_Type**：STRUCTURE
- **Preconditions**：做功方向已识别
- **Inputs**：working_branches, target_branches
- **Operators**：SET_MEMBERSHIP
- **Rule**：IF branch IN working_branches OR branch IN target_branches THEN GONG_SHEN ELSE FEI_SHEN
- **Assertion**：每字=功神/废神
- **Status**：ESTABLISHED

### R-BZ-001 宾主定位 ✅
- **Source**：《盲派八字体系》
- **Chapter**：第一章 宾主
- **Passage**：日柱=主，他柱=宾；日时=主，年月=宾。
- **Rule_Type**：STRUCTURE
- **Preconditions**：四柱已排
- **Inputs**：pillar_position
- **Operators**：ENUM
- **Rule**：day/hour = MAIN; year/month = GUEST
- **Assertion**：每柱=MAIN/GUEST
- **Status**：ESTABLISHED

### R-TY-001 体用定位 ✅
- **Source**：《盲派八字体系》
- **Chapter**：第二章 体用
- **Passage**：体=日主/印/禄/比劫；用=财/官杀。食伤中性。
- **Rule_Type**：STRUCTURE
- **Preconditions**：十神已排
- **Inputs**：ten_god
- **Operators**：ENUM
- **Rule**：DM/印/禄/比劫 = TI；财/官杀 = YONG；食伤 = NEUTRAL
- **Assertion**：每十神=TI/YONG/NEUTRAL
- **Status**：ESTABLISHED

---

## L2 SYMBOL（象法层）

### R-SX-001 共象原则 ✅
- **Source**：《象的应用原则》
- **Chapter**：一、共象
- **Passage**：某一字有干支象+宫位象+十神象，两类以上表示同一事物=共象成立。
- **Rule_Type**：SYMBOL
- **Rule**：IF COUNT(overlapping_xiang) >= 2 THEN 共象成立
- **Assertion**：该字象 = intersection_meaning
- **Status**：ESTABLISHED

### R-SX-002 合象原则 ✅
- **Source**：《象的应用原则》
- **Chapter**：二、合象
- **Passage**：天干五合/地支六合，相合双方互取象。一方定义另一方性质。
- **Rule_Type**：SYMBOL
- **Rule**：IF 合绊成立 THEN both_sides_borrow_each_other_xiang
- **Assertion**：合绊双方象 = A+B 复合象
- **Status**：ESTABLISHED

### R-SX-003 化象原则 ✅
- **Source**：《象的应用原则》
- **Chapter**：三、化象
- **Passage**：阴木生火=纺织；阳木生火=家具；辰配子=化工制药。
- **Rule_Type**：SYMBOL
- **Rule**：IF 阴木→火 THEN 纺织; IF 阳木→火 THEN 家具; IF 辰→子 THEN 化工
- **Assertion**：转化象
- **Status**：ESTABLISHED

### R-SX-004 墓象原则 ✅
- **Source**：《象的应用原则》
- **Chapter**：四、墓象
- **Passage**：墓=收藏控制。七杀入羊刃墓=军队；食伤库=学校工厂；财星墓=建筑地产。
- **Rule_Type**：SYMBOL
- **Rule**：IF 七杀入羊刃墓 THEN 军队; IF 食伤入墓 THEN 学校; IF 财入墓 THEN 地产
- **Assertion**：墓象
- **Status**：ESTABLISHED

### R-SX-005 制象原则 ✅
- **Source**：《象的应用原则》
- **Chapter**：五、制象
- **Passage**：合制/克制/冲制/刑制/穿制，制法取复合象推断行业。
- **Rule_Type**：SYMBOL
- **Rule**：IF 财库制劫财印库 THEN 资本运作; IF 丑未冲制印库 THEN 地产
- **Assertion**：制象
- **Status**：ESTABLISHED

### R-SX-006 带象原则 ✅
- **Source**：《象的应用原则》
- **Chapter**：六、带象
- **Passage**：一柱干支以干统支。财带官帽=公家财；官带财帽=管财官；印带官帽=权力；印带财帽=薪水。
- **Rule_Type**：SYMBOL
- **Rule**：IF 财+官同柱 THEN 公家财; IF 官+财同柱 THEN 管财官; IF 印+官同柱 THEN 权力; IF 印+财同柱 THEN 薪水
- **Assertion**：带象
- **Status**：ESTABLISHED

### R-SX-007 借象原则 ✅（本轮封板）
- **Source**：《盲派中级命理学》
- **Chapter**：第七章 象的应用
- **Passage**：八字中字有一些重要的关系可以互通其象，称借象。天干通禄神可借象；同五行阴阳不同也可借象。
- **Rule_Type**：SYMBOL
- **Preconditions**：A为天干，B为其通禄神 OR A/B同五行阴阳不同
- **Inputs**：gan_A, gan_B, tonglu_relation, same_element_diff_yinyang
- **Operators**：EITHER
- **Rule**：IF (A_tiangan → B_tonglu) OR (A/B同五行 AND 阴阳不同) THEN 借象关系成立
- **Assertion**：A↔B symbol_reference = BORROWED
- **Scope**：象法关系，不直接推职业/婚姻
- **Exclusions**：借象后仍需宫位/十神/做功关系才能定具体象
- **Status**：ESTABLISHED

---

## L3 WEALTH（财富层）

### R-WEALTH-001 禄神当财 ✅（本轮封板）
- **Source**：《盲派命理论坛》/第八章财富看法
- **Chapter**：财富看法→禄神当财
- **Passage**：命中占禄，无伤食泄时，或八字无财时，禄可以当财看。禄是现成之福，条件是印生禄。喜印，忌伤食劫财。
- **Rule_Type**：STRUCTURE
- **Preconditions**：命局有禄
- **Inputs**：lu_present, food_injury_present, wealth_star_present, resource_generates_lu
- **Operators**：AND, OR
- **Rule**：
  - 001A: IF lu_present AND NOT food_injury_present THEN 禄可当财
  - 001B: IF NOT wealth_star_present AND lu_present THEN 禄作财富取象
  - 001C: IF resource_generates_lu THEN 禄=现成之福/享用
  - 001D: IF 禄取财 AND 禄受伤 THEN 财富结构受损
- **Assertion**：禄神=财富候选；禄伤=财富受损
- **Scope**：财富结构
- **Exclusions**：喜印忌伤食劫财是结构关系，不得变 fortune_score
- **Status**：ESTABLISHED

### R-WEALTH-002 财库/开库 ⚠️（继续取证）
- **Source**：第八章财富看法
- **Chapter**：财库
- **Passage**：待补原文
- **Rule_Type**：STRUCTURE
- **Rule**：待拆：财库是什么/什么叫开/什么叫入/什么叫收/什么叫制/什么情况下冲库反而坏
- **Assertion**：待补
- **Status**：IN_PROGRESS

### R-WEALTH-003 财富层次 ❌（暂不准入）
- **Source**：第八章目录
- **Chapter**：财富看法/取财方法
- **Passage**：目录为：禄神当财/伤食当财/官杀当财；经营/风险/智力/体力/工薪。无"富/大富/巨富"独立等级判定章节。
- **Rule_Type**：—
- **Rule**：—
- **Assertion**：NOT_ESTABLISHED
- **Exclusions**：案例中"千万/上亿"不得反向生成等级 Rule
- **Status**：NOT_ESTABLISHED

---

## L4 MARRIAGE（婚姻层）

### R-MARRIAGE-001 结婚应期 ✅（本轮封板）
- **Source**：《盲派中高级命理学讲义》
- **Chapter**：第十章第四节 结婚应期
- **Passage**：结婚应期三类：①配偶星地支三合/六合合入配偶宫；②配偶星逢天干五合；③配偶宫与配偶星逢刑冲。
- **Rule_Type**：TIMING
- **Preconditions**：配偶宫/配偶星已定位
- **Inputs**：spouse_palace, spouse_star, relations
- **Operators**：IN_LIST
- **Rule**：
  - 001A: IF 配偶星三合/六合合入配偶宫 THEN 婚期候选
  - 001B: IF 配偶星天干五合 THEN 婚期候选
  - 001C: IF 配偶宫↔配偶星发生刑/冲 THEN 婚期候选
- **Assertion**：DIVORCE=NO; MARRIAGE_TIMING_CANDIDATE
- **Scope**：大运/流年
- **Exclusions**：多信号同时出现由 Assertion Resolver 处理，不直接推结婚
- **Status**：ESTABLISHED

### R-MARRIAGE-002 离婚应期 ✅（本轮封板）
- **Source**：《盲派中级命理学》
- **Chapter**：第十章 离婚应期
- **Passage**：许多离婚的流年应期，是宫星发生对抗。宫来制星，当出现宫无法制星而对抗时，便是离婚应期；对抗出现平衡时就离婚。
- **Rule_Type**：TIMING
- **Preconditions**：原局已有宫星作用结构
- **Inputs**：palace_controls_star, star_vs_palace_opposition, opposition_balance
- **Operators**：OVERRIDE, BALANCE
- **Rule**：IF 原局宫→星作用结构 AND 岁运导致宫星对抗形成 AND 对抗达到平衡 THEN
- **Assertion**：DIVORCE_TIMING_CANDIDATE
- **Scope**：大运/流年
- **Exclusions**：冲≠离婚充分条件；必须是宫星对抗+平衡
- **Status**：ESTABLISHED

---

## L5 BODY/DISASTER（身体/灾厄层，拆规则）

### R-BODY-001 宫位→身体部位 ✅（本轮封板）
- **Source**：《盲派中级命理学》
- **Chapter**：第三章 干支类象
- **Passage**：年柱=腿足四肢；月柱=躯干（脊肩背）；日支=五脏六腑心脑髓；时柱=头面手眼耳鼻生殖排泄。
- **Rule_Type**：SYMBOL
- **Rule**：年→腿足; 月→躯干; 日支→内脏; 时→头面
- **Assertion**：宫位→身体部位映射
- **Status**：ESTABLISHED

### R-BODY-002 十干→身体类象 ✅（本轮封板）
- **Source**：《盲派中级命理学》
- **Chapter**：第三章 十干类象
- **Passage**：甲=头/头面/头发/眉/臂/肢体/肝胆/经脉/神经；乙=颈/脊柱/手腕/脚腕/胆/头发/经脉；丙=眼睛/神经/大脑/血压/小肠/肩；丁=眼睛/心脏/血管/神经；戊=鼻/胃/皮肤/肌肉。
- **Rule_Type**：SYMBOL
- **Preconditions**：—
- **Inputs**：stem
- **Operators**：LOOKUP
- **Rule**：
  - 002-A: 甲 → {头,头面,头发,眉,臂,肢体,肝胆,经脉,神经}
  - 002-B: 乙 → {颈,脊柱,手腕,脚腕,胆,头发,经脉}
  - 002-C: 丙 → {眼睛,神经,大脑,血压,小肠,肩}
  - 002-D: 丁 → {眼睛,心脏,血管,神经}
  - 002-E: 戊 → {鼻,胃,皮肤,肌肉}
  - 002-F~J: 己庚辛壬癸 → 待补原文
- **Assertion**：十干→身体部位象集合
- **Exclusions**：十干→身体部位是 Symbol Assertion，不是疾病 Assertion。甲→肝胆 ≠ 甲→肝病；疾病需另外结构规则
- **Status**：ESTABLISHED（己庚辛壬癸待补）

### R-BODY-003 十二支→身体类象 ✅（本轮封板）
- **Source**：《盲派中级命理学》
- **Chapter**：第三章 十二支类象
- **Passage**：子=肾/耳/膀胱/泌尿/血液/精/腰/喉咙；丑=腹/脾胃/肾/子宫/肌肉/肿块；午=心/小肠/眼/舌/血液/神经/精力；申=肺/大肠/骨/脊椎/气管/食道/牙齿/骨钙/经络；酉=肺/肋/小肠/耳朵/牙齿/骨骼/臂膀/精血；戌=心/心包/命门/背/胃/鼻/肌肉/腿/踝足；亥=头/肾/膀胱/尿道/血脉/经血。
- **Rule_Type**：SYMBOL
- **Preconditions**：—
- **Inputs**：branch
- **Operators**：LOOKUP
- **Rule**：
  - 003-ZI: 子 → {肾,耳,膀胱,泌尿,血液,精,腰,喉咙}
  - 003-CHO: 丑 → {腹,脾胃,肾,子宫,肌肉,肿块}
  - 003-WU: 午 → {心,小肠,眼,舌,血液,神经,精力}
  - 003-SHEN: 申 → {肺,大肠,骨,脊椎,气管,食道,牙齿,骨钙,经络}
  - 003-YOU: 酉 → {肺,肋,小肠,耳朵,牙齿,骨骼,臂膀,精血}
  - 003-XU: 戌 → {心,心包,命门,背,胃,鼻,肌肉,腿,踝足}
  - 003-HAI: 亥 → {头,肾,膀胱,尿道,血脉,经血}
  - 003-YIN/MAO/CHEN/SI/WEI: 待补原文
- **Assertion**：十二支→身体部位象集合
- **Exclusions**：只出象，不出病种。象≠病
- **Status**：ESTABLISHED（寅卯辰巳待补）

### R-DISASTER-001 牢狱/灾厄结构 ✅（本轮封板，拆5条）
- **Source**：《盲派命理论坛》/第十二章 牢狱专辑
- **Chapter**：牢狱之灾的看法
- **Passage**：①亥丑辰有牢狱象，阳性有用之物被坏→牢狱；②水多金沉→牢狱；③枭神夺食→失去自由/坐牢；④劫财+伤官+与官杀对抗→牢狱；⑤反局+辰丑→多数应牢狱。
- **Rule_Type**：STRUCTURE
- **Preconditions**：原局结构已识别
- **Inputs**：harmful_branches, water_level, metal_sinks, indirect_resource_overcomes_food, rob_wealth+hurting_officer, officer_opposition, reverse_structure
- **Operators**：INTERSECTION, AND, MOSTLY
- **Rule**：
  - 001A: IF {亥,丑,辰}∩harmful_structure AND 阳性有用之物被坏 THEN PRISON_RISK
  - 001B: IF water_excessive AND metal_sinks THEN PRISON_STRUCTURE
  - 001C: IF 枭神夺食 THEN FREEDOM_LOSS
  - 001D: IF 劫财 AND 伤官 AND 与官杀对抗 THEN PRISON_STRUCTURE
  - 001E: IF reverse_structure AND {辰,丑} present THEN PRISON_RISK (CONDITIONAL, 原文"多数应牢狱")
- **Assertion**：PRISON_RISK / FREEDOM_LOSS
- **Exclusions**：001E 是 CONDITIONAL 不是充分条件；assertion_strength=STRONG/CONDITIONAL，不得 TRUE=必然牢狱
- **Status**：ESTABLISHED

---

## L6 SHENCHA（神煞类象层，拆五类）

### R-SHEN-001 禄神 ✅（本轮封板）
- **Source**：《盲派中级命理学》第四章
- **Chapter**：神煞类象
- **Passage**：禄神严格说不属于神煞，是十干本气，象丰富单独列出。
- **Rule_Type**：SYMBOL
- **Rule**：禄=十干临官之地
- **Assertion**：禄象
- **Status**：ESTABLISHED

### R-SHEN-002 羊刃 ✅（本轮封板）
- **Source**：第四章
- **Passage**：羊刃=十干帝旺之地
- **Rule_Type**：SYMBOL
- **Assertion**：刃象
- **Status**：ESTABLISHED

### R-SHEN-003 墓库 ✅（本轮封板）
- **Source**：第四章
- **Passage**：墓库=辰戌丑未，收藏控制
- **Rule_Type**：SYMBOL
- **Assertion**：墓库象
- **Status**：ESTABLISHED

### R-SHEN-004 驿马 ✅（本轮封板）
- **Source**：第四章
- **Passage**：申子辰→寅午戌；寅午戌→申子辰；巳酉丑→亥卯未；亥卯未→巳酉丑。象=走动/外出/远行/迁移/奔忙。
- **Rule_Type**：SYMBOL
- **Rule**：IF 日支三合局 THEN 驿马支=对宫三合首字
- **Assertion**：驿马象=迁移/奔波
- **Status**：ESTABLISHED

### R-SHEN-005 空亡 ✅（本轮封板）
- **Source**：第四章
- **Passage**：六甲旬空。象=有气无形/有名无实/挂名/形式/影子/减半/不全。
- **Rule_Type**：SYMBOL
- **Rule**：IF 日柱旬空 THEN 空亡成立
- **Assertion**：空亡象=虚/不实/减半
- **Status**：ESTABLISHED

---

## L7 TIMING（应期层，已有）
冲/合/刑/穿/墓/透干/字再现/见禄/空亡填实/开库/合待冲冲待合 ✅

---

## V3 汇总

| 状态 | 数量 | 规则 |
|---|---|---|
| ESTABLISHED | 25 | R-PJ-001/002/003, R-ZB-001, R-GF-001, R-BZ-001, R-TY-001, R-SX-001~007, R-WEALTH-001, R-MARRIAGE-001/002, R-BODY-001/002/003, R-DISASTER-001(A~E), R-SHEN-001~005 |
| IN_PROGRESS | 1 | R-WEALTH-002(财库开启) |
| NOT_ESTABLISHED | 1 | R-WEALTH-003(财富等级) |
| 待补原文 | 5干+5支 | 己庚辛壬癸身体象；寅卯辰巳未身体象 |

**下一步**：只剩 R-WEALTH-002 财库开启需重点深挖。十干/十二支身体象、灾厄结构已封板。财富等级保持 NOT_ESTABLISHED，不硬造。
