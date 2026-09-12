# 1980-06-22 10:00 男 广州 — 全链路引擎输出（L0→L2.5，停 L3 前）

> 口径：八字排盘引擎（北京时间口径）→ 盲派引擎（DUAN_JIANYE）→ L2 解层 → L2.5 12主题。引擎原始输出转 MD，无 LLM 断言。

## 一、八字排盘 L0

| 项 | 值 |
|---|---|
| 公历 | 1980-06-22 10:00 | 性别 | 男 |
| 年柱 | 庚申（石榴木） | 月柱 | 壬午（杨柳木） |
| 日柱 | 丙寅（炉中火） | 时柱 | 癸巳（长流水） |
| 日主 | BING | | |

## 二、盲派 L1 做功层

| # | 方法 | 归属 | 明细 |
|---|---|---|---|
| 0 | 食伤生财 | EFFECTIVE | WU(食神)生GENG(偏财), 距0 |
| 1 | 食伤制杀 | EFFECTIVE | WU(食神)制REN(七杀), 距1[主取宾] |
| 2 | 比劫制财 | EFFECTIVE | BING(比肩)制GENG(偏财), 距0 |
| 3 | 官杀制比劫 | EFFECTIVE | GUI(正官)制DING(劫财), 距2 |
| 4 | 伤官制官 | INEFFECTIVE | JI(伤官)制GUI(正官), 距2 |
| 5 | 刑正官 | EFFECTIVE | 地支三刑: YIN(比肩)刑SI(正官), 距1(互动无制) |
| 6 | 刑制偏财 | EFFECTIVE | 地支三刑: YIN(比肩)刑SI(偏财), 距1+五行制 |
| 7 | 印化官杀 | EFFECTIVE | REN(七杀)生JIA(偏印), 距1 |
| 8 | 刑偏财 | EFFECTIVE | 地支三刑: YIN(偏印)刑SI(偏财), 距1(互动无制) |
| 9 | 刑制正官 | EFFECTIVE | 地支三刑: YIN(食神)刑SI(正官), 距1+五行制 |
| 10 | 暗合 | INEFFECTIVE | 暗合: SHEN藏REN(七杀)合WU藏DING(劫财)=暗藏信息 |
| 11 | 印制食伤 | EFFECTIVE | 印制食伤: JIA(偏印)制WU(食神), 距2 |
| 12 | 禄神受穿 | NEGATIVE | 禄神SI被YIN穿害: 禄怕穿害, 身体/福报受损 |

- 效率：LARGE | 制净：CLEAN | 等级：LARGE_NOBLE | 反局：ZHENG | 旺衰：WANG

## 三、L2 解层事件

- **MARRIAGE → MARRIAGE_BROKEN（IN_AUSPICIOUS）**｜spouse_palace=YIN(day)+star_weakened=True+star_into_muku=False
- **WEALTH → WEALTH_ESTABLISHED（AUSPICIOUS）**｜wealth_state=DIRECTED_AND_ESTABLISHED
- **OFFICIAL → OFFICIAL_ESTABLISHED（AUSPICIOUS）**｜official_state=CONTROLLED_AND_CLEAN+completeness=CLEAN
- **OCCUPATION → OCCUPATION_DIRECTION_CANDIDATE（NEUTRAL）**｜work_types=['CONTROL_OFFICER_BY_FOOD_INJURY', 'CONTROL_WEALTH_BY_BIJIE', 'CONTROL_WEALTH_BY_INTERACTION', 'CONTROL_OFFICER_BY_INTERACTION', 'GENERATE_WEALTH_BY_FOOD_INJURY', 'TRANSFORM_OFFICER_BY_RESOURCE', 'CONTROL_FOOD_INJURY_BY_RESOURCE', 'CONTROL_BIJIE_BY_OFFICER']+direction=['TOWARD_WEALTH', 'TOWARD_OFFICIAL']｜职业名：官职/公职、技艺谋财、单位文职
- **BODY → BODY_LU_ATTACK（IN_AUSPICIOUS）**｜lu_present=True+lu_attacked=True（禄怕见绝更怕穿害）

## 四、L2.5 十二主题

| 主题 | 状态 | 条目 |
|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai=WANG; five_element_imbalance=TRUE; transparent_ten_gods={"year": "偏财", "month": "七杀", "hour": "正官"} |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count=0; kinship_count.sister_count=6; zuo_gong.比劫做功=EFFECTIVE |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state=BROKEN; marriage_event_structure.palace_state=CLASHED_AND_HARMED_AND_PUNISHED; marriage_event_structure.spouse_star_present=True |
| THEME-004 子女 | CANDIDATE | children.star=男命有财→官杀为子女星(七杀为儿/正官为女); children.star_present=TRUE; children.palace_hit=时支逢穿 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state=DIRECTED_AND_ESTABLISHED; wealth_event_structure.wealth_present=True |
| THEME-006 身体疾厄 | ESTABLISHED | body_event_candidate.candidate=LU_UNDER_ATTACK; body_event_candidate.lu_attacked=True; dry_earth_brittle=NO_DRY_EARTH |
| THEME-007 迁移出行 | ESTABLISHED | yima.present=SHEN马在YIN_AND_YIN马在SHEN; yima.trigger=NO_TRIGGER |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types=["CONTROL_OFFICER_BY_FOOD_INJURY", "CONTROL_WEALTH_BY_BIJIE", "CONTROL_WEALTH_BY_INTERACTION", "CONTROL_OFFICER_BY_INTERACTION", "GENERATE_WEALTH_BY_FOOD_INJURY", "TRANSFORM_OFFICER_BY_RESOURCE", "CONTROL_FOOD_INJURY_BY_RESOURCE", "CONTROL_BIJIE_BY_OFFICER"]; official_event_structure.official_state=CONTROLLED_AND_CLEAN; work_efficiency=LARGE |
| THEME-009 田宅家业 | UNDETERMINED | zuo_gong.墓库收物=NOT_EFFECTIVE |
| THEME-010 福德精神 | ESTABLISHED | zuo_gong.食伤做功=EFFECTIVE; blind_wangshuai=WANG; zuo_gong.印做功=EFFECTIVE |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财)=PRESENT; parents.mother(印星)=PRESENT |
| THEME-012 才艺学业 | ESTABLISHED | zuo_gong.印做功(学业)=EFFECTIVE; zuo_gong.食伤泄秀(才艺)=NOT_EFFECTIVE; talent.direction=WEN(木火) |
