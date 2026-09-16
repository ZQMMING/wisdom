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

### 第01章大运反局节新取证（追加）

#### J-TIMING-002 大运体用动静
- **JUDGMENT_DOMAIN**：J8
- **ASSERTION_INPUTS**：A-PJ-FANJULU, 大运干支
- **JUDGMENT_RULE**：走干运=支为体(静)干为用(动)；走支运=支为用(动)干为体(静)。体静用动，体指挥用。
- **CONDITION**：大运干支分看
- **EXCLUSION**：此"体用"与第02章体用根本不同，不可混用
- **EVIDENCE_ID**：EVD-J-TIMING-002
- **SOURCE**：《盲派中级命理学》第01章大运反局节
- **SOURCE_LOCATION**："走干运是支为体，干为用；走支运是支为用，干为体。体为静，用为动"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-DISASTER-002 辰=牢狱/无自由
- **JUDGMENT_DOMAIN**：J7
- **ASSERTION_INPUTS**：A-DISASTER-PRISON, 辰字出现
- **JUDGMENT_RULE**：辰为伤官库，伤官入库无自由；辰有牢狱之意。原局反局+辰=牢狱应期。
- **CONDITION**：原局反局 AND 岁运见辰
- **EXCLUSION**：辰单独出现不等于牢狱；必须叠加反局/官灾结构
- **EVIDENCE_ID**：EVD-J-DISASTER-002
- **SOURCE**：《盲派中级命理学》第01章大运反局节
- **SOURCE_LOCATION**："辰为伤官库，伤官入库无自由"、"辰有牢狱之意"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-OFFICIAL-003 官星高透克身=当官有灾
- **JUDGMENT_DOMAIN**：J2
- **ASSERTION_INPUTS**：A-TY-TIYONG, 官星克身
- **JUDGMENT_RULE**：官星高透克身，不能当官，当官就会有灾。
- **CONDITION**：官星透干 AND 官星克日主 AND 无制化
- **EXCLUSION**：不做官级别判断
- **EVIDENCE_ID**：EVD-J-OFFICIAL-003
- **SOURCE**：《盲派中级命理学》第01章
- **SOURCE_LOCATION**："因官星高透克身，故不能当官，当官就会有灾"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-HEALTH-002 穿子女宫=膀胱/直肠
- **JUDGMENT_DOMAIN**：J7
- **ASSERTION_INPUTS**：A-BODY-GONGWEI, 时柱穿动
- **JUDGMENT_RULE**：穿了子女宫(时柱)，对应膀胱、直肠部位问题。
- **CONDITION**：时柱被穿 AND 岁运引动
- **EXCLUSION**：是身体风险信号，不是确诊疾病
- **EVIDENCE_ID**：EVD-J-HEALTH-002
- **SOURCE**：《盲派中级命理学》第01章周恩来造例
- **SOURCE_LOCATION**："穿了子女宫，所以是膀胱、直肠部分有问题"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-WEALTH-005 财星反局=财大凶
- **JUDGMENT_DOMAIN**：J1
- **ASSERTION_INPUTS**：A-PJ-FAN, 财星反局位置
- **JUDGMENT_RULE**：财星反局，财大凶，主贫穷。
- **CONDITION**：反局在财星/财宫位置
- **EXCLUSION**：不估具体金额
- **EVIDENCE_ID**：EVD-J-WEALTH-005
- **SOURCE**：《盲派中级命理学》第01章
- **SOURCE_LOCATION**："财星反局财大凶，故此人非常穷"、"在哪方面反局哪方面应凶"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

---

### 第04章神煞类象节新取证

#### J-WEALTH-006 禄印相随=享受/福气
- **JUDGMENT_DOMAIN**：J1
- **ASSERTION_INPUTS**：A-WEALTH-LUASCASH, A-SHEN-LU, 印星
- **JUDGMENT_RULE**：禄不配印=辛苦；禄配印(禄印相随)=享受/福气/做事不辛苦。
- **CONDITION**：禄存在 AND 印星生禄
- **EXCLUSION**：不估财富金额；合到印不算桃花
- **EVIDENCE_ID**：EVD-J-WEALTH-006
- **SOURCE**：《盲派中级命理学》第04章神煞类象
- **SOURCE_LOCATION**："禄不配印为辛苦，禄配印为表示享受之意"、"禄印相随，表享受"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-OFFICIAL-004 羊刃制服=正业；无制服=偏业
- **JUDGMENT_DOMAIN**：J2/J3
- **ASSERTION_INPUTS**：A-SHEN-YANGREN, 羊刃被制
- **JUDGMENT_RULE**：羊刃喜制服，制之得用正→军人/警察/执法/外科/运动员/武人；无制服则用偏→匪徒/赌徒/打架/非法谋营。
- **CONDITION**：羊刃存在 AND 有/无制服
- **EXCLUSION**：不直接断职业名，只给正/偏业方向
- **EVIDENCE_ID**：EVD-J-OFFICIAL-004
- **SOURCE**：《盲派中级命理学》第04章
- **SOURCE_LOCATION**："羊刃喜制服，制之得用正……无制服，则用偏"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-CAREER-002 墓库象→行业机构
- **JUDGMENT_DOMAIN**：J3
- **ASSERTION_INPUTS**：A-MUKU-IDENTIFIED, A-SX-MUSYMBOLS
- **JUDGMENT_RULE**：羊刃库=军队/警察；伤官食神库=寺庙/学校；财库=银行；官杀库=组织部/权力中心。
- **CONDITION**：墓库已识别 AND 按藏干定类型
- **EXCLUSION**：只给机构方向，不指定具体单位名
- **EVIDENCE_ID**：EVD-J-CAREER-002
- **SOURCE**：《盲派中级命理学》第04章
- **SOURCE_LOCATION**："羊刃库或理解成军团或营地；伤官、食神库可理解成寺庙或学校；财库可理解成银行；官杀库可理解成权力中心或组织部门"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-TIMING-003 驿马逢合=停留不动
- **JUDGMENT_DOMAIN**：J8
- **ASSERTION_INPUTS**：A-SHEN-YIMA, 驿马被合
- **JUDGMENT_RULE**：驿马主走动/外出/迁移；驿马逢合=停留、不动。
- **CONDITION**：驿马存在 AND 被合
- **EXCLUSION**：驿马≠必然搬家/出国/换工作；只是象
- **EVIDENCE_ID**：EVD-J-TIMING-003
- **SOURCE**：《盲派中级命理学》第04章
- **SOURCE_LOCATION**："驿马在命中表示走动、外出、远行、游走、迁移、奔忙等意"、"驿马逢合，则表示停留、不动之意"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-KIN-002 空亡分宫位
- **JUDGMENT_DOMAIN**：J5
- **ASSERTION_INPUTS**：A-SHEN-KONGWANG, 空亡所在宫位
- **JUDGMENT_RULE**：年支空亡祖业空；月支空亡兄弟无靠；日支空亡夫妻缘薄；时支空亡子女迟育。凶星空亡凶减半，吉神空亡福不全。
- **CONDITION**：空亡存在 AND 按宫位定六亲
- **EXCLUSION**：空亡≠必然事件；只表缘薄/迟/空
- **EVIDENCE_ID**：EVD-J-KIN-002
- **SOURCE**：《盲派中级命理学》第04章
- **SOURCE_LOCATION**："年支空亡祖业空；月支空亡兄弟无靠或有伤损；日支空亡……夫妻之缘薄；时支空亡子女迟育"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-MARRIAGE-002 禄绊桃花
- **JUDGMENT_DOMAIN**：J4
- **ASSERTION_INPUTS**：A-SHEN-LU, 禄合伤官/官杀/财
- **JUDGMENT_RULE**：女人禄=身体，禄合到伤官/官杀/财=禄绊桃花；合到夫妻宫不为桃花。
- **CONDITION**：女命 AND 禄被合 AND 合向伤官/官杀/财
- **EXCLUSION**：合到夫妻宫不算桃花
- **EVIDENCE_ID**：EVD-J-MARRIAGE-002
- **SOURCE**：《盲派中级命理学》第04章
- **SOURCE_LOCATION**："女人的禄也是身体，合到伤官，官杀，财为禄绊桃花；合到夫妻宫不为桃花"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

---

## 统计

| STATUS | 数量 |
|---|---|
| ESTABLISHED | 16 |
| IN_PROGRESS | 4 |
| NOT_ESTABLISHED | 1（财富等级） |

**已封板 16 条 PRIMARY**：
- 第01章（9条）：J-WEALTH-003/005, J-OFFICIAL-002/003, J-CAREER-001, J-SPECIAL-001, J-TIMING-002, J-DISASTER-002, J-HEALTH-002
- 第04章（6条）：J-WEALTH-006(禄印相随), J-OFFICIAL-004(羊刃制服), J-CAREER-002(墓库象→机构), J-TIMING-003(驿马逢合), J-KIN-002(空亡分宫), J-MARRIAGE-002(禄绊桃花)

**关键边界守住**：
- 驿马≠必然搬家，只是象
- 空亡≠必然事件，只是缘薄/迟/空
- 羊刃制服只给正/偏业方向，不指定职业名
- 墓库象只给机构方向，不指定单位名
- 禄绊桃花有排除条件（合到夫妻宫不算）

**IN_PROGRESS 4 条**：J-WEALTH-001/002/004、J-OFFICIAL-001、J-MARRIAGE-001、J-KIN-001、J-CHILD、J-HEALTH-001、J-DISASTER-001、J-TIMING-001、J-SPECIAL-002
