# 盲派 Judgment Evidence 母表 V1

> **基线**：bce821f5（Rule Evidence FROZEN → Rule Registry PASS → Assertion Engine PASS → Human Gate PASS）
> **本轮目标**：只建 Judgment Evidence 母表，不写 Judgment 代码。
> **核心原则**：Assertion = "有什么结构"；Judgment = "这些结构按经典判断规则推出什么判断"。
> **铁律**：Case → Judgment Rule 禁止。案例只进 Golden/Regression/Counter/Edge。

---

## 字段定义

| 字段 | 要求 |
|---|---|
| JUDGMENT_ID | 唯一 ID |
| JUDGMENT_DOMAIN | J1财富/J2官贵/J3职业/J4婚姻/J5六亲/J6子女/J7健康灾厄/J8应期/J9特殊结构 |
| ASSERTION_INPUTS | 所需 Assertion（必须是已封板29条之一） |
| JUDGMENT_RULE | 经典判断逻辑 |
| CONDITION | 必要条件 |
| EXCLUSION | 禁止推断 |
| EVIDENCE_ID | 原典证据 ID |
| SOURCE | 书名/卷章 |
| SOURCE_LOCATION | 原文定位 |
| EVIDENCE_LEVEL | PRIMARY（原典原文）/ SECONDARY（后人整理） |
| STATUS | ESTABLISHED / IN_PROGRESS / NOT_ESTABLISHED |

---

## Judgment Domains（9个独立域，不揉一个Resolver）

| Domain | 名称 | 范围 |
|---|---|---|
| J1 | 财富/财 | 有财/得财/财来源/财主宾/财制化墓冲/财岁运引动 |
| J2 | 官贵/权力 | 有官/得官/官主宾/官制化/官职大小（不估具体级别） |
| J3 | 职业/事业 | 行业方向/职业象/做功方向对应的行业 |
| J4 | 婚姻 | 婚姻顺逆/配偶特征/结婚应期已封/离婚应期已封 |
| J5 | 六亲 | 父母/兄弟/配偶/子女的存在与关系 |
| J6 | 子女 | 子女有无/贤否/数量（不估精确数） |
| J7 | 健康/灾厄 | 身体风险/牢狱风险/伤灾风险 |
| J8 | 事件应期 | 应期→事件的经典判断规则（现有TIMING是结构引动） |
| J9 | 特殊结构 | 正局/反局/贼捕/从格等特殊结构的实际判断 |

---

## 候选 Judgment Rule 清单（待填证据）

### J1 财富/财

#### J-WEALTH-001 有财无财（结构判断）
- **JUDGMENT_DOMAIN**：J1
- **ASSERTION_INPUTS**：A-BZ-MAINGUEST, A-WEALTH-LUASCASH, A-MUKU-OPENED
- **JUDGMENT_RULE**：待补原文
- **CONDITION**：待补
- **EXCLUSION**：待补
- **EVIDENCE_ID**：EVD-J-WEALTH-001
- **SOURCE**：《盲派中级命理学》第八章财富看法
- **SOURCE_LOCATION**：待补
- **EVIDENCE_LEVEL**：待查
- **STATUS**：IN_PROGRESS

#### J-WEALTH-002 得财条件
- **JUDGMENT_DOMAIN**：J1
- **ASSERTION_INPUTS**：A-BZ-MAINGUEST, A-GF-GONGSHEN, A-WEALTH-LUASCASH
- **JUDGMENT_RULE**：待补原文
- **CONDITION**：待补
- **EXCLUSION**：MUKU_OPENED≠WEALTH_GAIN（已锁死）
- **EVIDENCE_ID**：EVD-J-WEALTH-002
- **SOURCE**：第八章
- **STATUS**：IN_PROGRESS

#### J-WEALTH-003 财主宾（财是我家他家）
- **JUDGMENT_DOMAIN**：J1
- **ASSERTION_INPUTS**：A-BZ-MAINGUEST, root_provenance（已有）
- **JUDGMENT_RULE**：财根在主位=我家财；在宾位=他家财/公家财。年上财=别人的财/国有财；日主合年上官=在国企工作。
- **CONDITION**：财星/财根定位 + 主宾定位
- **EXCLUSION**：不估财富金额
- **EVIDENCE_ID**：EVD-J-WEALTH-003
- **SOURCE**：《盲派中级命理学》第01章
- **SOURCE_LOCATION**："年上的官星被制为国有企业的官；日主合年上的官表示在国企工作"、"主位一党，宾位一党，要制宾"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-WEALTH-004 财被制/化/墓/冲
- **JUDGMENT_DOMAIN**：J1
- **ASSERTION_INPUTS**：A-SX-ZHISYMBOLS, A-MUKU-OPENED
- **JUDGMENT_RULE**：待补原文
- **EVIDENCE_ID**：EVD-J-WEALTH-004
- **STATUS**：IN_PROGRESS

#### J-WEALTH-GRADE 财富等级
- **STATUS**：NOT_ESTABLISHED（禁止：百万/千万/亿级/一层功/二层功）

---

### J2 官贵/权力

#### J-OFFICIAL-001 有官无官
- **JUDGMENT_DOMAIN**：J2
- **ASSERTION_INPUTS**：A-BZ-MAINGUEST, A-TY-TIYONG, root_provenance
- **JUDGMENT_RULE**：待补原文
- **EVIDENCE_ID**：EVD-J-OFFICIAL-001
- **STATUS**：IN_PROGRESS

#### J-OFFICIAL-002 官主宾（官是公家还是自己）
- **JUDGMENT_DOMAIN**：J2
- **ASSERTION_INPUTS**：A-BZ-MAINGUEST, root_provenance
- **JUDGMENT_RULE**：年上官=国企/公家单位；日时官=自己/私企。官表示单位大小，不表示官职大小。
- **CONDITION**：官星定位 + 主宾定位
- **EXCLUSION**：不估官职级别
- **EVIDENCE_ID**：EVD-J-OFFICIAL-002
- **SOURCE**：《盲派中级命理学》第01章
- **SOURCE_LOCATION**："年上的官星被制为国有企业的官；日主合年上的官表示在国企工作，官表示国家的单位、大型的单位，不表示官职"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

---

### J3 职业/事业

#### J-CAREER-001 做功方向→行业
- **JUDGMENT_DOMAIN**：J3
- **ASSERTION_INPUTS**：A-SX-HESYMBOLS, A-SX-HUASYMBOLS, A-SX-MUSYMBOLS, A-SX-ZHISYMBOLS, A-SX-DAISYMBOLS
- **JUDGMENT_RULE**：财原神生财之地=银行；辰拱水=从混浊中提纯=化工/制药；辰也有药的象。
- **CONDITION**：制象/合象/化象/墓象已成立
- **EXCLUSION**：不指定具体职业名，只给行业方向
- **EVIDENCE_ID**：EVD-J-CAREER-001
- **SOURCE**：《盲派中级命理学》第01章
- **SOURCE_LOCATION**："卯为食神为财原神，生财之地，为银行"、"辰是机器，拱了水，辰就成了泥巴，表从混浊中提纯。实际是化工行业，制药企业"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

---

### J4 婚姻

#### J-MARRIAGE-001 婚姻顺逆
- **JUDGMENT_DOMAIN**：J4
- **ASSERTION_INPUTS**：A-BZ-MAINGUEST, A-SX-JIESYMBOLS
- **JUDGMENT_RULE**：待补原文
- **EVIDENCE_ID**：EVD-J-MARRIAGE-001
- **STATUS**：IN_PROGRESS

（注：结婚应期/离婚应期已有 TIMING Assertion，J4 只补"婚姻顺逆"结构判断）

---

### J5 六亲

#### J-KIN-001 父母
- **JUDGMENT_DOMAIN**：J5
- **ASSERTION_INPUTS**：A-BZ-MAINGUEST
- **JUDGMENT_RULE**：待补原文
- **STATUS**：IN_PROGRESS

---

### J6 子女

#### J-CHILD-001 子女有无
- **JUDGMENT_DOMAIN**：J6
- **ASSERTION_INPUTS**：A-BZ-MAINGUEST
- **JUDGMENT_RULE**：待补原文
- **EXCLUSION**：不估精确数量
- **STATUS**：IN_PROGRESS

---

### J7 健康/灾厄

#### J-HEALTH-001 身体风险
- **JUDGMENT_DOMAIN**：J7
- **ASSERTION_INPUTS**：A-BODY-GONGWEI, A-BODY-GAN, A-BODY-ZHI
- **JUDGMENT_RULE**：待补原文（身体象+制化→风险，不是疾病）
- **EXCLUSION**：身体象≠疾病（已锁死）
- **STATUS**：IN_PROGRESS

#### J-DISASTER-001 牢狱风险判断
- **JUDGMENT_DOMAIN**：J7
- **ASSERTION_INPUTS**：A-DISASTER-PRISON
- **JUDGMENT_RULE**：待补原文
- **EXCLUSION**：PRISON_RISK≠必坐牢
- **STATUS**：IN_PROGRESS

---

### J8 事件应期

#### J-TIMING-001 应期→事件判断
- **JUDGMENT_DOMAIN**：J8
- **ASSERTION_INPUTS**：所有 TIMING Assertion
- **JUDGMENT_RULE**：待补原文（"八字讲贵贱，大运讲吉凶，流年看应期"的事件判断规则）
- **EXCLUSION**：TIMING Assertion≠EVENT（已锁死）
- **STATUS**：IN_PROGRESS

---

### J9 特殊结构

#### J-SPECIAL-001 正局/反局→实际判断
- **JUDGMENT_DOMAIN**：J9
- **ASSERTION_INPUTS**：A-PJ-ZHENG, A-PJ-FAN
- **JUDGMENT_RULE**：原局反局原局凶；大运反局大运凶；流年反局流年凶。在哪方面反局哪方面应凶。
- **CONDITION**：局型=反局 + 反局位置（原局/大运/流年）
- **EXCLUSION**：正局不自动推吉；反局只记应凶方向，不记具体事件
- **EVIDENCE_ID**：EVD-J-SPECIAL-001
- **SOURCE**：《盲派中级命理学》第01章
- **SOURCE_LOCATION**："反局分原局反局、大运反局、流年反局三种，原局反局原局凶，大运反局大运凶，流年反局流年凶"、"在哪方面反局哪方面应凶"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-SPECIAL-002 贼捕→实际判断
- **JUDGMENT_DOMAIN**：J9
- **ASSERTION_INPUTS**：A-ZB-ROBBER_CATCHER
- **JUDGMENT_RULE**：待补原文
- **EXCLUSION**：贼捕≠直接大富贵
- **STATUS**：IN_PROGRESS

---

## 统计

| STATUS | 数量 |
|---|---|
| ESTABLISHED | 5（J-WEALTH-003财主宾, J-OFFICIAL-002官主宾, J-CAREER-001行业, J-SPECIAL-001正反局应凶） |
| IN_PROGRESS | 10 |
| NOT_ESTABLISHED | 1（财富等级） |

**已封板5条**（全部 PRIMARY，来自第01章原文）：
1. J-WEALTH-003 财主宾（年上财=公家/国有）
2. J-OFFICIAL-002 官主宾（年上官=国企，不表官职）
3. J-CAREER-001 做功→行业（财原神=银行，辰拱水=化工制药）
4. J-SPECIAL-001 反局应凶方向（原局/大运/流年分层）
5. （J-WEALTH-001/002/004、J-OFFICIAL-001、J-MARRIAGE-001、J-KIN、J-CHILD、J-HEALTH、J-DISASTER、J-TIMING、J-SPECIAL-002 仍 IN_PROGRESS）

**下一步**：继续搜第02~12章判断语句。宁可少而准，不多而假。
