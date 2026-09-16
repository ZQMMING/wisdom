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

## 统计（实测）

| STATUS | 数量 |
|---|---|
| ESTABLISHED | 20 |
| IN_PROGRESS | 11 |
| NOT_ESTABLISHED | 1（财富等级） |

**已封板 20 条 PRIMARY**：
- 第01章（9条）：J-WEALTH-003/005, J-OFFICIAL-002/003, J-CAREER-001, J-SPECIAL-001, J-TIMING-002, J-DISASTER-002, J-HEALTH-002
- 第03章（5条）：J-DISASTER-003(丑酉阴中阴), J-CAREER-003(文理分科), J-CAREER-004(干支→行业), J-HEALTH-003(甲遇丁), J-HEALTH-004(丙配癸)
- 第04章（6条）：J-WEALTH-006, J-OFFICIAL-004, J-CAREER-002, J-TIMING-003, J-KIN-002, J-MARRIAGE-002

**第03章关键边界**：纯十干/十二支类象表（甲=肝、子=肾等）不进Judgment，只作Symbol。只有带结构条件的组合判断才封板。

---

### 第03章干支类象节新取证（严格筛选：只收"结构→判断"，纯类象表不进）

#### J-DISASTER-003 丑酉阴中阴=牢狱/黑社会
- **JUDGMENT_DOMAIN**：J7
- **ASSERTION_INPUTS**：A-DISASTER-PRISON, 丑酉组合
- **JUDGMENT_RULE**：丑酉为阴中之阴，多数与犯罪、黑社会、牢狱、坟墓、玄学、淫邪有关。辛酉日主见丑时=阴见阴又入墓=黑社会；辛丑日主不是（浊中见清）。戌为阳乱（歌厅），丑为阴乱。
- **CONDITION**：丑酉同现 AND 阴干见阴支入墓
- **EXCLUSION**：辛丑日主不成立（浊中见清）；不直接断"必犯罪"
- **EVIDENCE_ID**：EVD-J-DISASTER-003
- **SOURCE**：《盲派中级命理学》第03章
- **SOURCE_LOCATION**："丑酉为阴中之阴，太多数丑酉与犯罪、黑社会有关，主牢狱、黑社会、坟墓、玄学、淫邪"、"辛酉日主见丑时为黑社会……辛丑日主不是黑社会，因为浊中见清"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-CAREER-003 文理分科
- **JUDGMENT_DOMAIN**：J3
- **ASSERTION_INPUTS**：A-SX-STEMBRANCH, 木火/金水组合
- **JUDGMENT_RULE**：木火主文，金水主理。戌亥=计算/数学（入乾门）；丑=玄学；辰见子=化学；申=金融，酉=法律（酉不代表金融）。
- **CONDITION**：干支组合方向
- **EXCLUSION**：只给学科方向，不指定具体专业名
- **EVIDENCE_ID**：EVD-J-CAREER-003
- **SOURCE**：《盲派中级命理学》第03章
- **SOURCE_LOCATION**："木火主文，金水主理"、"戌亥为计算、运算的意思，表数学"、"申酉为法律，申还代表金融，酉不代表金融"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-CAREER-004 干支组合→行业
- **JUDGMENT_DOMAIN**：J3
- **ASSERTION_INPUTS**：A-SX-STEMBRANCH, 阳木/阴木遇火
- **JUDGMENT_RULE**：阳木遇火=家具；阴木遇火=纺织；辛金取财=五金行业；火克金=冶炼行业。
- **CONDITION**：干支组合成立
- **EXCLUSION**：只给行业方向，不指定具体单位
- **EVIDENCE_ID**：EVD-J-CAREER-004
- **SOURCE**：《盲派中级命理学》第03章
- **SOURCE_LOCATION**："阳木遇火为家具，阴木遇火为纺织"、"辛金取财为五金行业，火克金为冶炼行业"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-HEALTH-003 甲遇丁=头发/面
- **JUDGMENT_DOMAIN**：J7
- **ASSERTION_INPUTS**：A-BODY-STEM, 甲遇丁
- **JUDGMENT_RULE**：甲遇丁火=头发稀；甲为头，丁为脸，两癸冲克丁=面/脸受损（毁容类信号）。
- **CONDITION**：甲丁同现 AND 丁被冲克
- **EXCLUSION**：是身体风险信号，不是确诊
- **EVIDENCE_ID**：EVD-J-HEALTH-003
- **SOURCE**：《盲派中级命理学》第03章
- **SOURCE_LOCATION**："甲遇丁火头发稀"、"甲为头，丁为脸，两癸冲克，谓干头反复，主凶"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-HEALTH-004 丙配癸=眼
- **JUDGMENT_DOMAIN**：J7
- **ASSERTION_INPUTS**：A-BODY-STEM, 丙癸同现
- **JUDGMENT_RULE**：【CASE-DERIVED，暂不封】丙为眼眶，癸为黑/眼珠；癸水被烤干=眼盲风险信号。
- **CONDITION**：丙癸同现 AND 癸被火烤干
- **EXCLUSION**：原典仅在郝金阳先生案例中出现，非章节正文普遍规则陈述。按铁律 CASE MUST NEVER BE A RULE SOURCE，降级为 CASE-DERIVED，需另找普遍规则陈述后再升 PRIMARY。
- **EVIDENCE_ID**：EVD-J-HEALTH-004
- **SOURCE**：《盲派中级命理学》第03章郝金阳先生例（案例位置）
- **SOURCE_LOCATION**："丙为眼框，癸为黑，为眼珠，癸水烤干了，眼盲"
- **EVIDENCE_LEVEL**：CASE-DERIVED
- **STATUS**：IN_PROGRESS

---

### 第05章宫位类象节新取证

#### J-WEALTH-007 时支=车
- **JUDGMENT_DOMAIN**：J1/J8
- **ASSERTION_INPUTS**：A-BODY-GONGWEI, 时支
- **JUDGMENT_RULE**：时支=车/门户/代步工具。时支被生=买车；时支被破/冲=车有问题/车祸风险。
- **CONDITION**：时支存在 AND 被生/被破
- **EXCLUSION**：是物品/应期信号，不是必然事件
- **EVIDENCE_ID**：EVD-J-WEALTH-007
- **SOURCE**：《盲派中级命理学》第05章
- **SOURCE_LOCATION**："时支表示车，如买车、车祸均看时支"、"卯财在时上表车，癸卯运为花钱买车……原局子卯破表车有问题"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-HEALTH-005 破到年上=腿足残疾
- **JUDGMENT_DOMAIN**：J7
- **ASSERTION_INPUTS**：A-BODY-GONGWEI, 年支被破
- **JUDGMENT_RULE**：比劫破到年上（主位破宾位），年柱=腿足四肢，表腿足残疾风险。阴=右，阳=左。
- **CONDITION**：年支被主位破 AND 比劫破年
- **EXCLUSION**：必须是主位破宾位，否则不成立；是风险信号不是确诊
- **EVIDENCE_ID**：EVD-J-HEALTH-005
- **SOURCE**：《盲派中级命理学》第05章
- **SOURCE_LOCATION**："火旺了，比劫破到年上卯，阴为右，阳为左，表右腿有残疾"、"必须是主位和他破，这才能表示自己控制不住他的意思"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-KIN-003 丈母娘在年上找
- **JUDGMENT_DOMAIN**：J5
- **ASSERTION_INPUTS**：A-BODY-GONGWEI, 年柱与妻宫关联
- **JUDGMENT_RULE**：丈母娘在年上找（年=外戚），与妻宫关联的印/伤食=丈母娘。伤=无感情，食=重感情。
- **CONDITION**：年柱 AND 与妻宫关联 AND 印/伤食
- **EXCLUSION**：与妻宫无关则伤可能是奶奶
- **EVIDENCE_ID**：EVD-J-KIN-003
- **SOURCE**：《盲派中级命理学》第05章
- **SOURCE_LOCATION**："丈母娘在年上找，因年上表外戚，和妻宫发生了关联的印伤食都是丈母娘。伤无感情，食重感情"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-MARRIAGE-003 夫妻象在月上=同学
- **JUDGMENT_DOMAIN**：J4
- **ASSERTION_INPUTS**：A-BODY-GONGWEI, 夫妻象在月柱
- **JUDGMENT_RULE**：月柱=同学/同事；夫妻象在月上=配偶是同学/同事。
- **CONDITION**：夫妻星/宫在月柱
- **EXCLUSION**：只给来源方向，不必然
- **EVIDENCE_ID**：EVD-J-MARRIAGE-003
- **SOURCE**：《盲派中级命理学》第05章
- **SOURCE_LOCATION**："月柱表同学、同事，若夫妻象现在月上可能是同学"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

---

### 第06章十神类象节新取证

#### J-WEALTH-008 财多心乱=早辍学
- **JUDGMENT_DOMAIN**：J1/J3
- **ASSERTION_INPUTS**：A-TY-TIYONG, 年月财旺
- **JUDGMENT_RULE**：年月财旺（尤其女命）=财多心乱，主早辍学。
- **CONDITION**：年月柱财星旺 AND 女命优先
- **EXCLUSION**：不必然，只是倾向
- **EVIDENCE_ID**：EVD-J-WEALTH-008
- **SOURCE**：《盲派中级命理学》第06章
- **SOURCE_LOCATION**："年月逢旺的人，尤其是女的，一定很早辍学，诀：财多心乱"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-WEALTH-009 财虚透=才华/爱打扮
- **JUDGMENT_DOMAIN**：J1/J3
- **ASSERTION_INPUTS**：A-TY-TIYONG, 财星虚透
- **JUDGMENT_RULE**：财虚透=才华，表会来事/会交往/会说话。财星虚透在时上=爱打扮/时尚/穿金带银。
- **CONDITION**：财星虚透天干
- **EXCLUSION**：是象，不必然
- **EVIDENCE_ID**：EVD-J-WEALTH-009
- **SOURCE**：《盲派中级命理学》第06章
- **SOURCE_LOCATION**："财虚透是指才华，表会来事、会交往、会说话"、"财星虚透在时上为爱打扮，时尚，穿金带银"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-CHILD-001 杀+财=儿，杀无财=女
- **JUDGMENT_DOMAIN**：J6
- **ASSERTION_INPUTS**：A-TY-TIYONG, 男命七杀
- **JUDGMENT_RULE**：男命以杀为儿官为女。杀+财=儿；杀无财=女。穿倒财=生女。行伤官大运=生儿。
- **CONDITION**：男命 AND 七杀有/无财
- **EXCLUSION**：只是倾向，不是必然
- **EVIDENCE_ID**：EVD-J-CHILD-001
- **SOURCE**：《盲派中级命理学》第06章
- **SOURCE_LOCATION**："男命以杀为儿，官为女……杀＋财＝儿，杀无财为女。穿倒财生女"、"行伤大运，则生儿"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-KIN-004 穿倒食神=母早死
- **JUDGMENT_DOMAIN**：J5
- **ASSERTION_INPUTS**：A-TY-TIYONG, 食神被穿
- **JUDGMENT_RULE**：食/伤/禄为母。穿倒食神=母早死风险信号。
- **CONDITION**：食神被穿 AND 无救应
- **EXCLUSION**：是风险信号，不是必然
- **EVIDENCE_ID**：EVD-J-KIN-004
- **SOURCE**：《盲派中级命理学》第06章
- **SOURCE_LOCATION**："穿倒了食神……母早死"、"食、伤、禄为母"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-WEALTH-010 穿门口=车被盗
- **JUDGMENT_DOMAIN**：J1/J8
- **ASSERTION_INPUTS**：A-BODY-GONGWEI, 时柱被穿
- **JUDGMENT_RULE**：时柱=门口/车。穿了门口=车被盗风险信号。
- **CONDITION**：时柱被穿
- **EXCLUSION**：是风险信号，不是必然
- **EVIDENCE_ID**：EVD-J-WEALTH-010
- **SOURCE**：《盲派中级命理学》第06章末
- **SOURCE_LOCATION**："穿了门口注意车被盗"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

---

### 第07章象的应用节新取证

#### J-OFFICIAL-005 阳制阴=公安/刑警
- **JUDGMENT_DOMAIN**：J2
- **ASSERTION_INPUTS**：A-SX-HESYMBOLS, 阳干/支制阴
- **JUDGMENT_RULE**：阳制阴（阳干/阳支穿制阴）=公安/刑警组合。寅=劫财带枪。
- **CONDITION**：阳字制阴字 AND 丑/辰/申等阴字
- **EXCLUSION**：只给部门方向，不指定级别
- **EVIDENCE_ID**：EVD-J-OFFICIAL-005
- **SOURCE**：《盲派中级命理学》第07章
- **SOURCE_LOCATION**："申辰丑为阴，寅为阳，以阳制阴，公安处长"、"卯穿了辰阴，为公安！刑警！"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-WEALTH-011 带象：财带官帽/官带财帽/印带官帽/印带财帽
- **JUDGMENT_DOMAIN**：J1/J2
- **ASSERTION_INPUTS**：A-SX-DAISYMBOLS, 带象结构
- **JUDGMENT_RULE**：财带官帽=公家之财；官带财帽=管理财的官；印带官帽=权力；印带财帽=薪水/上班领工资。
- **CONDITION**：一柱干支带象结构成立
- **EXCLUSION**：是象，不必然
- **EVIDENCE_ID**：EVD-J-WEALTH-011
- **SOURCE**：《盲派中级命理学》第07章带象原则
- **SOURCE_LOCATION**："财带官帽：公家之财。官带财帽：管理财的官。印带官帽：权力。印带财帽：表薪水，即上班领工资"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-OFFICIAL-006 七杀入羊刃墓=军队/军官
- **JUDGMENT_DOMAIN**：J2
- **ASSERTION_INPUTS**：A-MUKU-IDENTIFIED, 七杀入羊刃墓
- **JUDGMENT_RULE**：七杀入羊刃墓=军队/军团/军官。
- **CONDITION**：七杀入羊刃墓 AND 墓库识别
- **EXCLUSION**：不指定级别
- **EVIDENCE_ID**：EVD-J-OFFICIAL-006
- **SOURCE**：《盲派中级命理学》第07章墓象原则
- **SOURCE_LOCATION**："七杀入了羊刃墓，表军队，军团"、"未为七杀之墓……是个军官。实际是一少将"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-CAREER-005 辰配子=化工/制药
- **JUDGMENT_DOMAIN**：J3
- **ASSERTION_INPUTS**：A-SX-HUASYMBOLS, 辰子组合
- **JUDGMENT_RULE**：辰配子=化工/制药/提纯。
- **CONDITION**：辰子同现
- **EXCLUSION**：只给行业方向
- **EVIDENCE_ID**：EVD-J-CAREER-005
- **SOURCE**：《盲派中级命理学》第07章化象原则
- **SOURCE_LOCATION**："辰---子，化工，制药，提纯"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-WEALTH-012 丑未冲=资本运营
- **JUDGMENT_DOMAIN**：J1
- **ASSERTION_INPUTS**：A-MUKU-IDENTIFIED, 丑未冲
- **JUDGMENT_RULE**：丑未冲=财库制劫财与印库，取财手段=资本运营/资金运作。
- **CONDITION**：丑未冲 AND 丑为财库
- **EXCLUSION**：不估金额
- **EVIDENCE_ID**：EVD-J-WEALTH-012
- **SOURCE**：《盲派中级命理学》第07章制象原则
- **SOURCE_LOCATION**："丑是财库，财库制劫财与印库……他取财的手段与方式是资本运营"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-KIN-005 卯戌合=母
- **JUDGMENT_DOMAIN**：J5
- **ASSERTION_INPUTS**：A-SX-HEXISYMBOLS, 卯戌合
- **JUDGMENT_RULE**：卯戌合=母的状态。破坏此合=母有变故风险信号。
- **CONDITION**：卯戌合成立 AND 岁运破坏此合
- **EXCLUSION**：是风险信号，不是必然
- **EVIDENCE_ID**：EVD-J-KIN-005
- **SOURCE**：《盲派中级命理学》第07章制象原则
- **SOURCE_LOCATION**："卯戌合的象也是母……辰运母死，辰破坏了卯戌合的状态，卯就不是母了"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

---

### 第08章财命专集节新取证

#### J-WEALTH-013 禄神当财条件
- **JUDGMENT_DOMAIN**：J1
- **ASSERTION_INPUTS**：A-WEALTH-LUASCASH, 禄神
- **JUDGMENT_RULE**：命中占禄 AND 无伤食泄 OR 八字无财 → 禄可当财看。禄当财条件=印生禄（现成之福）。以禄取财=辛苦求财。喜印，忌伤食劫财。禄作用神最怕见劫财（分禄）。
- **CONDITION**：禄存在 AND (无伤食泄 OR 无财)
- **EXCLUSION**：不估金额；见劫财=分禄破财
- **EVIDENCE_ID**：EVD-J-WEALTH-013
- **SOURCE**：《盲派中级命理学》第08章禄神当财节
- **SOURCE_LOCATION**："命中占禄，无伤食泄时，或八字无财时，禄可以当财看"、"禄是现成之福，其条件是印生禄"、"以禄当财，喜印，忌伤食劫财"、"禄作用神最怕见劫财，劫财有分禄之意"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-WEALTH-014 伤食当财
- **JUDGMENT_DOMAIN**：J1
- **ASSERTION_INPUTS**：A-WEALTH-LUASCASH, 伤食
- **JUDGMENT_RULE**：八字无财星 AND 有伤食 → 伤食当财富看。伤官=谋为/经营之财；食神=思想/脑力之财。天干食=思想，地支食=企业。
- **CONDITION**：八字无财 AND 有伤食
- **EXCLUSION**：有财时伤食是原神/投资财
- **EVIDENCE_ID**：EVD-J-WEALTH-014
- **SOURCE**：《盲派中级命理学》第08章伤食当财节
- **SOURCE_LOCATION**："八字无财星，却有伤食星，以伤食当财富看"、"伤官为谋为、经营之财；食神为思想、脑力之财。天干的食表思想，地支的食表企业"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-WEALTH-015 官杀当财
- **JUDGMENT_DOMAIN**：J1
- **ASSERTION_INPUTS**：A-WEALTH-LUASCASH, 官杀
- **JUDGMENT_RULE**：两种情况官杀当财：①官统财/财统官（官多财少或财多官少，且相连）；②官杀有制但制不净。官杀当财时财富级别高。
- **CONDITION**：官杀财相连 AND 官多财少 OR 财多官少 OR 官杀制不净
- **EXCLUSION**：只论原局，大运出现不算；不估具体金额
- **EVIDENCE_ID**：EVD-J-WEALTH-015
- **SOURCE**：《盲派中级命理学》第08章官杀当财节
- **SOURCE_LOCATION**："官统财或财统官，官杀当财富看"、"官杀有制，但制服不太好，官杀可以当财富看。官杀当财富看时，其财富级别会很高"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-CAREER-006 内食神格=做企业
- **JUDGMENT_DOMAIN**：J3
- **ASSERTION_INPUTS**：A-SX-HUASYMBOLS, 内食神格
- **JUDGMENT_RULE**：内食神格（地支食神做功）=适合做企业经营。食神带官象=不是本人企业=企业经理人。
- **CONDITION**：地支食神做功 AND 食神生财
- **EXCLUSION**：不指定具体行业
- **EVIDENCE_ID**：EVD-J-CAREER-006
- **SOURCE**：《盲派中级命理学》第08章经营取财节
- **SOURCE_LOCATION**："内食神格（地支食神做功者）适合于做企业经营"、"食神带官象说明不是他本人的企业，应是企业经理人"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-WEALTH-016 财在年上=远方求财
- **JUDGMENT_DOMAIN**：J1
- **ASSERTION_INPUTS**：A-BODY-GONGWEI, 财在年上
- **JUDGMENT_RULE**：财在年上做功=远方求财/海外贸易。
- **CONDITION**：财星在年柱 AND 做功
- **EXCLUSION**：只给方向，不指定具体
- **EVIDENCE_ID**：EVD-J-WEALTH-016
- **SOURCE**：《盲派中级命理学》第08章经营取财节
- **SOURCE_LOCATION**："财在年上，局有火土成势，意在制财……年主远方，水主海运，故是做海外贸易的"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

---

### 第10章婚姻专集节新取证

#### J-MARRIAGE-004 好婚姻组合
- **JUDGMENT_DOMAIN**：J4
- **ASSERTION_INPUTS**：A-MARRIAGE-MAINGUEST, 夫妻宫
- **JUDGMENT_RULE**：好婚姻=夫妻宫安静（无刑冲克穿合他星）AND 夫妻宫制夫妻星（制得住）。
- **CONDITION**：夫妻宫无破坏 AND 宫制星成立
- **EXCLUSION**：制之不住=反为坏婚姻
- **EVIDENCE_ID**：EVD-J-MARRIAGE-004
- **SOURCE**：《盲派中级命理学》第10章好婚姻节
- **SOURCE_LOCATION**："夫妻宫位要安静……不能被刑坏、冲破、穿倒"、"夫妻宫的宫位制去夫妻星的字为好婚姻……如制之不住，反为坏婚姻"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-MARRIAGE-005 差婚姻组合
- **JUDGMENT_DOMAIN**：J4
- **ASSERTION_INPUTS**：A-MARRIAGE-MAINGUEST, 夫妻宫被破坏
- **JUDGMENT_RULE**：夫妻宫被刑冲破穿=婚姻不好。破坏较轻=婚姻不好不一定离婚；破坏太重=必离异。比劫争夫/争妻=第三者问题。
- **CONDITION**：夫妻宫被破坏 AND 破坏程度
- **EXCLUSION**：不必然离婚，看破坏程度
- **EVIDENCE_ID**：EVD-J-MARRIAGE-005
- **SOURCE**：《盲派中级命理学》第10章差婚姻节
- **SOURCE_LOCATION**："夫妻宫位有用，却被刑、冲、破、穿……不好到什么程度，能否离婚，却要看夫妻宫破坏到什么程度"、"比劫争夫……轻者有第三者问题，重者必离婚"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-MARRIAGE-006 结婚应期：合处逢冲/冲墓
- **JUDGMENT_DOMAIN**：J4/J8
- **ASSERTION_INPUTS**：A-MARRIAGE-MAINGUEST, 配偶宫星被合/入墓
- **JUDGMENT_RULE**：结婚应期两种：①配偶宫或星原有合，冲其合为婚期；②配偶星或宫入墓，刑冲其墓流年为婚期。
- **CONDITION**：原局配偶宫星被合 OR 入墓
- **EXCLUSION**：是应期窗口，不是事件坐实
- **EVIDENCE_ID**：EVD-J-MARRIAGE-006
- **SOURCE**：《盲派中级命理学》第10章结婚应期节
- **SOURCE_LOCATION**："配偶宫或配偶星原有合……应在冲其合为结婚应期"、"配偶星或配偶宫入墓时，应刑冲其墓的流年而结婚"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-MARRIAGE-007 比劫争夫的几种可能
- **JUDGMENT_DOMAIN**：J4
- **ASSERTION_INPUTS**：A-TY-TIYONG, 比劫争夫
- **JUDGMENT_RULE**：比劫争夫的几种可能：①老公是离过婚的；②老公有外遇；③自己当小的/被包；④离婚；⑤曾经的对象。
- **CONDITION**：比劫与夫星有关系
- **EXCLUSION**：只是可能，不是必然
- **EVIDENCE_ID**：EVD-J-MARRIAGE-007
- **SOURCE**：《盲派中级命理学》第10章差婚姻节
- **SOURCE_LOCATION**："比肩争夫的几种可能：1、找的老公是离过婚的。2、老公有外遇。3、自己当小的或被包。4、离婚。5、曾经的对象"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

---

### 第12章牢狱专集节新取证

#### J-DISASTER-004 牢狱五种结构
- **JUDGMENT_DOMAIN**：J7
- **ASSERTION_INPUTS**：A-DISASTER-PRISON, 亥丑辰/水多金沉/枭神夺食/劫财伤官抗官杀/反局+辰丑
- **JUDGMENT_RULE**：牢狱五种结构：①亥/丑/辰牢狱字坏阳性有用之物（阳制阴不算）；②水多金沉；③枭神夺食=失去自由；④劫财+伤官+与官杀对抗；⑤反局+辰/丑=多数应牢狱。
- **CONDITION**：五种结构任一成立
- **EXCLUSION**：阳制阴不算；⑤是"多数"不是必然
- **EVIDENCE_ID**：EVD-J-DISASTER-004
- **SOURCE**：《盲派中级命理学》第12章
- **SOURCE_LOCATION**："亥水、丑土、辰土……有牢狱象。如果八字中有阳性的有用的东西，被这些坏了，可能会有牢狱。如是阳制阴不为牢狱"、"水多金沉为牢狱"、"枭神夺食为牢狱……失去自由，坐牢"、"劫财、伤官的组合……再与官杀对抗必为牢狱"、"凡出现反局的情况，有辰、丑等字在局中，多数应牢狱"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-DISASTER-005 出狱看法
- **JUDGMENT_DOMAIN**：J7/J8
- **ASSERTION_INPUTS**：A-DISASTER-PRISON, 日主得禄/合出/冲出
- **JUDGMENT_RULE**：出狱=日主得禄之年 OR 日主合出/冲出日主之年。如牢狱为库，冲穿坏了库为出狱。
- **CONDITION**：已有牢狱结构 AND 岁运出现上述
- **EXCLUSION**：是应期窗口，不是事件坐实
- **EVIDENCE_ID**：EVD-J-DISASTER-005
- **SOURCE**：《盲派中级命理学》第12章出狱节
- **SOURCE_LOCATION**："当日主得禄之年或日主合出、冲出日主之年出狱；如牢狱为库，冲、穿坏了库为出狱"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-WEALTH-017 劫财+官在主位=小偷
- **JUDGMENT_DOMAIN**：J1/J7
- **ASSERTION_INPUTS**：A-TY-TIYONG, 劫财+官在主位
- **JUDGMENT_RULE**：劫财为手，官为盗贼，劫财和官在主位组合=小偷结构。
- **CONDITION**：劫财+官杀在主位
- **EXCLUSION**：是结构象，不是必然犯罪
- **EVIDENCE_ID**：EVD-J-WEALTH-017
- **SOURCE**：《盲派中级命理学》第12章
- **SOURCE_LOCATION**："劫财为手，官为盗贼，劫财和官在主位组合时为小偷"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED

#### J-DISASTER-006 食伤入墓=失去自由
- **JUDGMENT_DOMAIN**：J7
- **ASSERTION_INPUTS**：A-MUKU-IDENTIFIED, 食伤入墓
- **JUDGMENT_RULE**：食伤表示自由/思想/表达，食伤入墓=失去自由/不能和外界联系。
- **CONDITION**：食伤入墓
- **EXCLUSION**：是结构象，不是必然坐牢
- **EVIDENCE_ID**：EVD-J-DISASTER-006
- **SOURCE**：《盲派中级命理学》第12章
- **SOURCE_LOCATION**："食伤也表示自由，入墓为失去自由，不能和外界联系"
- **EVIDENCE_LEVEL**：PRIMARY
- **STATUS**：ESTABLISHED
