# 盲派 L2.5 维度断言（15 例，引擎原始输出转 MD，零加工）

| 例 | 四柱 |
|---|---|
| #1 | 壬子 辛亥 壬辰 丙午 |
| #2 | 丁未 癸卯 庚子 丁丑 |
| #3 | 戊申 己未 庚申 辛巳 |
| #4 | 甲寅 丙子 己亥 戊辰 |
| #5 | 丁亥 癸丑 己未 癸酉 |
| #6 | 庚寅 戊寅 己亥 丙寅 |
| #7 | 戊申 己未 癸巳 己未 |
| #8 | 乙巳 甲申 辛酉 乙未 |
| #9 | 癸丑 乙卯 戊戌 癸亥 |
| #10 | 戊申 壬戌 甲子 丙寅 |
| #11 | 庚寅 乙酉 戊午 丁巳 |
| #12 | 丁亥 甲辰 己巳 丙寅 |
| #13 | 甲辰 庚午 甲辰 戊辰 |
| #14 | 乙丑 辛巳 辛酉 己亥 |
| #15 | 乙未 乙酉 庚子 丁丑 |

## 例 #1  壬子 辛亥 壬辰 丙午

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = WANG<br>five_element_imbalance = TRUE<br>transparent_ten_gods = {"year": "比肩", "month": "正印", "hour": "偏财"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 0<br>kinship_count.sister_count = 4<br>zuo_gong.比劫做功 = EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = CHALLENGED<br>marriage_event_structure.palace_state = STABLE<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | CANDIDATE | children.star = 男命有财→官杀为子女星(七杀为儿/正官为女)<br>children.star_present = TRUE<br>children.palace_hit = 时支逢冲 | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = DIRECTED_AND_ESTABLISHED<br>wealth_event_structure.wealth_present = True | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | ESTABLISHED | body_event_candidate.candidate = YANG_REN_CLASHED<br>body_event_candidate.lu_attacked = False<br>dry_earth_brittle = NO_DRY_EARTH | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | UNDETERMINED | yima.present = NONE<br>yima.trigger = NO_TRIGGER | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["CONTROL_OFFICER_BY_FOOD_INJURY", "CONTROL_RESOURCE_BY_WEALTH", "CONTROL_BIJIE_BY_OFFICER", "STORE_BY_MUKU"]<br>official_event_structure.official_state = CONTROLLED_AND_CLEAN<br>work_efficiency = LARGE | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | ESTABLISHED | zuo_gong.墓库收物 = EFFECTIVE | THEME-009 |
| THEME-010 福德精神 | ESTABLISHED | zuo_gong.食伤做功 = NOT_EFFECTIVE<br>blind_wangshuai = WANG<br>zuo_gong.印做功 = EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = PRESENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | ESTABLISHED | zuo_gong.印做功(学业) = EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = NOT_EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |

## 例 #2  丁未 癸卯 庚子 丁丑

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = ZHONG_HE_PIAN_RUO<br>five_element_imbalance = FALSE<br>transparent_ten_gods = {"year": "正官", "month": "伤官", "hour": "正官"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 1<br>kinship_count.sister_count = 4<br>zuo_gong.比劫做功 = EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = BROKEN<br>marriage_event_structure.palace_state = HARMED_AND_PUNISHED_AND_HE_BANNED<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | CANDIDATE | children.star = 女命→食伤为子女星(食神为女/伤官为儿)<br>children.star_present = TRUE<br>children.palace_hit = 时支逢冲 | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = DIRECTED_AND_ESTABLISHED<br>wealth_event_structure.wealth_present = True | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | UNDETERMINED | body_event_candidate.candidate = UNDETERMINED<br>body_event_candidate.lu_attacked = False<br>dry_earth_brittle = NOT_TRIGGERED | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | UNDETERMINED | yima.present = NONE<br>yima.trigger = NO_TRIGGER | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["CONTROL_WEALTH_BY_BIJIE", "CONTROL_WEALTH_BY_INTERACTION", "CONTROL_OFFICER_BY_INTERACTION", "CONTROL_FOOD_INJURY_BY_RESOURCE", "CONTROL_BIJIE_BY_OFFICER", "DRAIN_BY_FOOD_INJURY", "STORE_BY_MUKU"]<br>official_event_structure.official_state = CONTROLLED_AND_CLEAN<br>work_efficiency = LARGE | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | ESTABLISHED | zuo_gong.墓库收物 = EFFECTIVE<br>zuo_gong.冲开墓库 = 冲开墓库 | THEME-009 |
| THEME-010 福德精神 | ESTABLISHED | zuo_gong.食伤做功 = EFFECTIVE<br>blind_wangshuai = ZHONG_HE_PIAN_RUO<br>zuo_gong.印做功 = EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = ABSENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | ESTABLISHED | zuo_gong.印做功(学业) = EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |

## 例 #3  戊申 己未 庚申 辛巳

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = WANG<br>five_element_imbalance = TRUE<br>transparent_ten_gods = {"year": "偏印", "month": "正印", "hour": "劫财"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 0<br>kinship_count.sister_count = 5<br>zuo_gong.比劫做功 = NOT_EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = CHALLENGED<br>marriage_event_structure.palace_state = PUNISHED_AND_HE_BANNED<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | CANDIDATE | children.star = 男命有财→官杀为子女星(七杀为儿/正官为女)<br>children.star_present = TRUE<br>children.palace_hit = 枭印在时柱(克子) | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = PRESENT_UNTAKEN<br>wealth_event_structure.wealth_present = True | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | UNDETERMINED | body_event_candidate.candidate = UNDETERMINED<br>body_event_candidate.lu_attacked = False<br>dry_earth_brittle = NOT_TRIGGERED | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | UNDETERMINED | yima.present = NONE<br>yima.trigger = NO_TRIGGER | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["CONTROL_OFFICER_BY_INTERACTION", "CONTROL_FOOD_INJURY_BY_RESOURCE"]<br>official_event_structure.official_state = CONTROLLED_PARTIAL<br>work_efficiency = MEDIUM | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | UNDETERMINED | zuo_gong.墓库收物 = NOT_EFFECTIVE | THEME-009 |
| THEME-010 福德精神 | ESTABLISHED | zuo_gong.食伤做功 = EFFECTIVE<br>blind_wangshuai = WANG<br>zuo_gong.印做功 = EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = ABSENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | ESTABLISHED | zuo_gong.印做功(学业) = EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = NOT_EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |

## 例 #4  甲寅 丙子 己亥 戊辰

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = WANG<br>five_element_imbalance = TRUE<br>transparent_ten_gods = {"year": "正官", "month": "正印", "hour": "劫财"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 0<br>kinship_count.sister_count = 8<br>zuo_gong.比劫做功 = NOT_EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = HARMONIOUS<br>marriage_event_structure.palace_state = STABLE<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | UNDETERMINED | children.star = 女命→食伤为子女星(食神为女/伤官为儿)<br>children.star_present = FALSE<br>children.palace_hit = STABLE | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = PRESENT_UNTAKEN<br>wealth_event_structure.wealth_present = True | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | UNDETERMINED | body_event_candidate.candidate = UNDETERMINED<br>body_event_candidate.lu_attacked = True<br>dry_earth_brittle = NO_DRY_EARTH | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | UNDETERMINED | yima.present = NONE<br>yima.trigger = NO_TRIGGER | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["STORE_BY_MUKU"]<br>official_event_structure.official_state = CONTROLLED_PARTIAL<br>work_efficiency = LARGE | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | ESTABLISHED | zuo_gong.墓库收物 = EFFECTIVE | THEME-009 |
| THEME-010 福德精神 | CANDIDATE | zuo_gong.食伤做功 = NOT_EFFECTIVE<br>blind_wangshuai = WANG<br>zuo_gong.印做功 = NOT_EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = PRESENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | CANDIDATE | zuo_gong.印做功(学业) = NOT_EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = NOT_EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |

## 例 #5  丁亥 癸丑 己未 癸酉

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = WANG<br>five_element_imbalance = TRUE<br>transparent_ten_gods = {"year": "偏印", "month": "偏财", "hour": "偏财"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 0<br>kinship_count.sister_count = 5<br>zuo_gong.比劫做功 = NOT_EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = BROKEN<br>marriage_event_structure.palace_state = CLASHED_AND_PUNISHED<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | ESTABLISHED | children.star = 男命有财→官杀为子女星(七杀为儿/正官为女)<br>children.star_present = TRUE<br>children.palace_hit = STABLE | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = DIRECTED_AND_ESTABLISHED<br>wealth_event_structure.wealth_present = True | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | UNDETERMINED | body_event_candidate.candidate = UNDETERMINED<br>body_event_candidate.lu_attacked = True<br>dry_earth_brittle = NOT_TRIGGERED | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | UNDETERMINED | yima.present = NONE<br>yima.trigger = NO_TRIGGER | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["CONTROL_OFFICER_BY_FOOD_INJURY", "CONTROL_FOOD_INJURY_BY_RESOURCE", "STORE_BY_MUKU"]<br>official_event_structure.official_state = CONTROLLED_AND_CLEAN<br>work_efficiency = LARGE | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | ESTABLISHED | zuo_gong.墓库收物 = EFFECTIVE<br>zuo_gong.冲开墓库 = 冲开墓库 | THEME-009 |
| THEME-010 福德精神 | ESTABLISHED | zuo_gong.食伤做功 = EFFECTIVE<br>blind_wangshuai = WANG<br>zuo_gong.印做功 = EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = PRESENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | ESTABLISHED | zuo_gong.印做功(学业) = EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = NOT_EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |

## 例 #6  庚寅 戊寅 己亥 丙寅

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = WANG<br>five_element_imbalance = FALSE<br>transparent_ten_gods = {"year": "伤官", "month": "劫财", "hour": "正印"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 0<br>kinship_count.sister_count = 8<br>zuo_gong.比劫做功 = EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = CHALLENGED<br>marriage_event_structure.palace_state = HE_BANNED<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | ESTABLISHED | children.star = 男命有财→官杀为子女星(七杀为儿/正官为女)<br>children.star_present = TRUE<br>children.palace_hit = STABLE | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = DIRECTED_AND_ESTABLISHED<br>wealth_event_structure.wealth_present = True | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | UNDETERMINED | body_event_candidate.candidate = UNDETERMINED<br>body_event_candidate.lu_attacked = False<br>dry_earth_brittle = NO_DRY_EARTH | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | UNDETERMINED | yima.present = NONE<br>yima.trigger = NO_TRIGGER | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["CONTROL_WEALTH_BY_BIJIE"]<br>official_event_structure.official_state = UNCONTROLLED<br>work_efficiency = LARGE | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | UNDETERMINED | zuo_gong.墓库收物 = NOT_EFFECTIVE | THEME-009 |
| THEME-010 福德精神 | CANDIDATE | zuo_gong.食伤做功 = NOT_EFFECTIVE<br>blind_wangshuai = WANG<br>zuo_gong.印做功 = NOT_EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = ABSENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | CANDIDATE | zuo_gong.印做功(学业) = NOT_EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = NOT_EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |

## 例 #7  戊申 己未 癸巳 己未

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = ZHONG_HE_PIAN_RUO<br>five_element_imbalance = TRUE<br>transparent_ten_gods = {"year": "正官", "month": "七杀", "hour": "七杀"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 1<br>kinship_count.sister_count = 4<br>zuo_gong.比劫做功 = NOT_EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = CHALLENGED<br>marriage_event_structure.palace_state = PUNISHED<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | ESTABLISHED | children.star = 男命有财→官杀为子女星(七杀为儿/正官为女)<br>children.star_present = TRUE<br>children.palace_hit = STABLE | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = PRESENT_UNTAKEN<br>wealth_event_structure.wealth_present = True | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | UNDETERMINED | body_event_candidate.candidate = UNDETERMINED<br>body_event_candidate.lu_attacked = True<br>dry_earth_brittle = NOT_TRIGGERED | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | UNDETERMINED | yima.present = NONE<br>yima.trigger = NO_TRIGGER | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["CONTROL_FOOD_INJURY_BY_RESOURCE"]<br>official_event_structure.official_state = UNCONTROLLED<br>work_efficiency = MEDIUM | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | UNDETERMINED | zuo_gong.墓库收物 = NOT_EFFECTIVE | THEME-009 |
| THEME-010 福德精神 | ESTABLISHED | zuo_gong.食伤做功 = EFFECTIVE<br>blind_wangshuai = ZHONG_HE_PIAN_RUO<br>zuo_gong.印做功 = EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = PRESENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | ESTABLISHED | zuo_gong.印做功(学业) = EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = NOT_EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |

## 例 #8  乙巳 甲申 辛酉 乙未

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = WANG<br>five_element_imbalance = TRUE<br>transparent_ten_gods = {"year": "偏财", "month": "正财", "hour": "偏财"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 0<br>kinship_count.sister_count = 5<br>zuo_gong.比劫做功 = NOT_EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = HARMONIOUS<br>marriage_event_structure.palace_state = STABLE<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | CANDIDATE | children.star = 男命有财→官杀为子女星(七杀为儿/正官为女)<br>children.star_present = TRUE<br>children.palace_hit = 枭印在时柱(克子) | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = PRESENT_UNTAKEN<br>wealth_event_structure.wealth_present = True | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | UNDETERMINED | body_event_candidate.candidate = UNDETERMINED<br>body_event_candidate.lu_attacked = False<br>dry_earth_brittle = NOT_TRIGGERED | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | UNDETERMINED | yima.present = NONE<br>yima.trigger = NO_TRIGGER | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["CONTROL_FOOD_INJURY_BY_RESOURCE"]<br>official_event_structure.official_state = UNCONTROLLED<br>work_efficiency = MEDIUM | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | UNDETERMINED | zuo_gong.墓库收物 = NOT_EFFECTIVE | THEME-009 |
| THEME-010 福德精神 | ESTABLISHED | zuo_gong.食伤做功 = EFFECTIVE<br>blind_wangshuai = WANG<br>zuo_gong.印做功 = EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = PRESENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | ESTABLISHED | zuo_gong.印做功(学业) = EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = NOT_EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |

## 例 #9  癸丑 乙卯 戊戌 癸亥

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = WANG<br>five_element_imbalance = TRUE<br>transparent_ten_gods = {"year": "正财", "month": "正官", "hour": "正财"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 0<br>kinship_count.sister_count = 6<br>zuo_gong.比劫做功 = NOT_EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = CHALLENGED<br>marriage_event_structure.palace_state = PUNISHED_AND_HE_BANNED<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | ESTABLISHED | children.star = 男命有财→官杀为子女星(七杀为儿/正官为女)<br>children.star_present = TRUE<br>children.palace_hit = STABLE | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = DIRECTED_AND_ESTABLISHED<br>wealth_event_structure.wealth_present = True | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | UNDETERMINED | body_event_candidate.candidate = UNDETERMINED<br>body_event_candidate.lu_attacked = True<br>dry_earth_brittle = NOT_TRIGGERED | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | ESTABLISHED | yima.present = CHOU马在HAI<br>yima.trigger = NO_TRIGGER | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["CONTROL_OFFICER_BY_FOOD_INJURY", "CONTROL_WEALTH_BY_INTERACTION", "CONTROL_OFFICER_BY_INTERACTION", "CONTROL_RESOURCE_BY_WEALTH", "TRANSFORM_OFFICER_BY_RESOURCE", "CONTROL_FOOD_INJURY_BY_RESOURCE"]<br>official_event_structure.official_state = CONTROLLED_PARTIAL<br>work_efficiency = MEDIUM | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | UNDETERMINED | zuo_gong.墓库收物 = NOT_EFFECTIVE | THEME-009 |
| THEME-010 福德精神 | ESTABLISHED | zuo_gong.食伤做功 = EFFECTIVE<br>blind_wangshuai = WANG<br>zuo_gong.印做功 = EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = PRESENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | ESTABLISHED | zuo_gong.印做功(学业) = EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = NOT_EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |

## 例 #10  戊申 壬戌 甲子 丙寅

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = WANG<br>five_element_imbalance = FALSE<br>transparent_ten_gods = {"year": "偏财", "month": "偏印", "hour": "食神"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 0<br>kinship_count.sister_count = 5<br>zuo_gong.比劫做功 = EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = CHALLENGED<br>marriage_event_structure.palace_state = STABLE<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | CANDIDATE | children.star = 女命→食伤为子女星(食神为女/伤官为儿)<br>children.star_present = TRUE<br>children.palace_hit = 时支逢冲 | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = DIRECTED_AND_ESTABLISHED<br>wealth_event_structure.wealth_present = True | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | ESTABLISHED | body_event_candidate.candidate = LU_UNDER_ATTACK<br>body_event_candidate.lu_attacked = True<br>dry_earth_brittle = NOT_TRIGGERED | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | ESTABLISHED | yima.present = SHEN马在YIN_AND_ZI马在YIN<br>yima.trigger = NO_TRIGGER | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["CONTROL_WEALTH_BY_BIJIE", "CONTROL_FOOD_INJURY_BY_RESOURCE", "CONTROL_BIJIE_BY_OFFICER", "DRAIN_BY_FOOD_INJURY"]<br>official_event_structure.official_state = UNCONTROLLED<br>work_efficiency = MEDIUM | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | UNDETERMINED | zuo_gong.墓库收物 = NOT_EFFECTIVE | THEME-009 |
| THEME-010 福德精神 | ESTABLISHED | zuo_gong.食伤做功 = EFFECTIVE<br>blind_wangshuai = WANG<br>zuo_gong.印做功 = EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = PRESENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | ESTABLISHED | zuo_gong.印做功(学业) = EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |

## 例 #11  庚寅 乙酉 戊午 丁巳

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = WANG<br>five_element_imbalance = TRUE<br>transparent_ten_gods = {"year": "食神", "month": "正官", "hour": "正印"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 0<br>kinship_count.sister_count = 4<br>zuo_gong.比劫做功 = NOT_EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = CHALLENGED<br>marriage_event_structure.palace_state = STABLE<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | CANDIDATE | children.star = 女命→食伤为子女星(食神为女/伤官为儿)<br>children.star_present = TRUE<br>children.palace_hit = 时支逢穿_AND_枭印在时柱(克子) | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = SUBSTITUTED_AND_ESTABLISHED<br>wealth_event_structure.wealth_present = False | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | ESTABLISHED | body_event_candidate.candidate = LU_UNDER_ATTACK<br>body_event_candidate.lu_attacked = True<br>dry_earth_brittle = NO_DRY_EARTH | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | UNDETERMINED | yima.present = NONE<br>yima.trigger = NO_TRIGGER | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["CONTROL_FOOD_INJURY_BY_RESOURCE"]<br>official_event_structure.official_state = UNCONTROLLED<br>work_efficiency = MEDIUM | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | UNDETERMINED | zuo_gong.墓库收物 = NOT_EFFECTIVE | THEME-009 |
| THEME-010 福德精神 | ESTABLISHED | zuo_gong.食伤做功 = EFFECTIVE<br>blind_wangshuai = WANG<br>zuo_gong.印做功 = EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = ABSENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | ESTABLISHED | zuo_gong.印做功(学业) = EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = NOT_EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |

## 例 #12  丁亥 甲辰 己巳 丙寅

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = WANG<br>five_element_imbalance = TRUE<br>transparent_ten_gods = {"year": "偏印", "month": "正官", "hour": "正印"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 0<br>kinship_count.sister_count = 7<br>zuo_gong.比劫做功 = NOT_EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = BROKEN<br>marriage_event_structure.palace_state = CLASHED_AND_HARMED_AND_PUNISHED<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | CANDIDATE | children.star = 女命→食伤为子女星(食神为女/伤官为儿)<br>children.star_present = TRUE<br>children.palace_hit = 时支逢穿 | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = DIRECTED_AND_ESTABLISHED<br>wealth_event_structure.wealth_present = True | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | UNDETERMINED | body_event_candidate.candidate = UNDETERMINED<br>body_event_candidate.lu_attacked = False<br>dry_earth_brittle = NO_DRY_EARTH | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | CANDIDATE | yima.present = HAI马在SI_AND_SI马在HAI<br>yima.trigger = 驿马HAI逢冲(大限day) | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["CONTROL_OFFICER_BY_FOOD_INJURY", "CONTROL_OFFICER_BY_INTERACTION", "GENERATE_WEALTH_BY_FOOD_INJURY", "CONTROL_FOOD_INJURY_BY_RESOURCE"]<br>official_event_structure.official_state = CONTROLLED_AND_CLEAN<br>work_efficiency = LARGE | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | UNDETERMINED | zuo_gong.墓库收物 = NOT_EFFECTIVE | THEME-009 |
| THEME-010 福德精神 | ESTABLISHED | zuo_gong.食伤做功 = EFFECTIVE<br>blind_wangshuai = WANG<br>zuo_gong.印做功 = EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = PRESENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | ESTABLISHED | zuo_gong.印做功(学业) = EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = NOT_EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |

## 例 #13  甲辰 庚午 甲辰 戊辰

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = WANG<br>five_element_imbalance = TRUE<br>transparent_ten_gods = {"year": "比肩", "month": "七杀", "hour": "偏财"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 0<br>kinship_count.sister_count = 4<br>zuo_gong.比劫做功 = NOT_EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = HARMONIOUS<br>marriage_event_structure.palace_state = STABLE<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | ESTABLISHED | children.star = 女命→食伤为子女星(食神为女/伤官为儿)<br>children.star_present = TRUE<br>children.palace_hit = STABLE | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = PRESENT_UNTAKEN<br>wealth_event_structure.wealth_present = True | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | UNDETERMINED | body_event_candidate.candidate = UNDETERMINED<br>body_event_candidate.lu_attacked = False<br>dry_earth_brittle = NO_DRY_EARTH | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | UNDETERMINED | yima.present = NONE<br>yima.trigger = NO_TRIGGER | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["CONTROL_FOOD_INJURY_BY_RESOURCE"]<br>official_event_structure.official_state = UNCONTROLLED<br>work_efficiency = LARGE | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | UNDETERMINED | zuo_gong.墓库收物 = NOT_EFFECTIVE | THEME-009 |
| THEME-010 福德精神 | ESTABLISHED | zuo_gong.食伤做功 = EFFECTIVE<br>blind_wangshuai = WANG<br>zuo_gong.印做功 = EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = PRESENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | ESTABLISHED | zuo_gong.印做功(学业) = EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = NOT_EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |

## 例 #14  乙丑 辛巳 辛酉 己亥

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = WANG<br>five_element_imbalance = FALSE<br>transparent_ten_gods = {"year": "偏财", "month": "比肩", "hour": "偏印"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 0<br>kinship_count.sister_count = 4<br>zuo_gong.比劫做功 = NOT_EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = CHALLENGED<br>marriage_event_structure.palace_state = STABLE<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | CANDIDATE | children.star = 女命→食伤为子女星(食神为女/伤官为儿)<br>children.star_present = TRUE<br>children.palace_hit = 时支逢冲_AND_枭印在时柱(克子) | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = PRESENT_UNTAKEN<br>wealth_event_structure.wealth_present = True | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | UNDETERMINED | body_event_candidate.candidate = UNDETERMINED<br>body_event_candidate.lu_attacked = False<br>dry_earth_brittle = NO_DRY_EARTH | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | ESTABLISHED | yima.present = CHOU马在HAI_AND_YOU马在HAI<br>yima.trigger = NO_TRIGGER | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["CONTROL_FOOD_INJURY_BY_RESOURCE"]<br>official_event_structure.official_state = UNCONTROLLED<br>work_efficiency = MEDIUM | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | UNDETERMINED | zuo_gong.墓库收物 = NOT_EFFECTIVE | THEME-009 |
| THEME-010 福德精神 | ESTABLISHED | zuo_gong.食伤做功 = EFFECTIVE<br>blind_wangshuai = WANG<br>zuo_gong.印做功 = EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = PRESENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | ESTABLISHED | zuo_gong.印做功(学业) = EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = NOT_EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |

## 例 #15  乙未 乙酉 庚子 丁丑

| 主题 | 状态 | 断言条目 | 规则 |
|---|---|---|---|
| THEME-001 性情禀赋 | ESTABLISHED | blind_wangshuai = WANG<br>five_element_imbalance = FALSE<br>transparent_ten_gods = {"year": "正财", "month": "正财", "hour": "正官"} | THEME-001 |
| THEME-002 交游人际 | ESTABLISHED | kinship_count.brother_count = 0<br>kinship_count.sister_count = 5<br>zuo_gong.比劫做功 = NOT_EFFECTIVE | THEME-002 |
| THEME-003 婚姻配偶 | ESTABLISHED | marriage_event_structure.marriage_state = BROKEN<br>marriage_event_structure.palace_state = HARMED_AND_HE_BANNED<br>marriage_event_structure.spouse_star_present = True | THEME-003, JDG-MARRIAGE-001 |
| THEME-004 子女 | CANDIDATE | children.star = 女命→食伤为子女星(食神为女/伤官为儿)<br>children.star_present = TRUE<br>children.palace_hit = 时支逢冲 | THEME-004, BLIND-CHILD-001 |
| THEME-005 财帛 | ESTABLISHED | wealth_event_structure.wealth_state = DIRECTED_AND_ESTABLISHED<br>wealth_event_structure.wealth_present = True | THEME-005, JDG-WEALTH-001 |
| THEME-006 身体疾厄 | UNDETERMINED | body_event_candidate.candidate = UNDETERMINED<br>body_event_candidate.lu_attacked = False<br>dry_earth_brittle = NOT_TRIGGERED | THEME-006, JDG-BODY-001 |
| THEME-007 迁移出行 | UNDETERMINED | yima.present = NONE<br>yima.trigger = NO_TRIGGER | THEME-007, BLIND-YIMA-001 |
| THEME-008 事业功名 | ESTABLISHED | occupation_candidate.work_types = ["CONTROL_OFFICER_BY_FOOD_INJURY", "CONTROL_WEALTH_BY_INTERACTION", "CONTROL_OFFICER_BY_INTERACTION", "GENERATE_WEALTH_BY_FOOD_INJURY", "CONTROL_FOOD_INJURY_BY_RESOURCE", "STORE_BY_MUKU"]<br>official_event_structure.official_state = CONTROLLED_AND_CLEAN<br>work_efficiency = LARGE | THEME-008, JDG-OFFICIAL-001, JDG-OCCUPATION-001 |
| THEME-009 田宅家业 | ESTABLISHED | zuo_gong.墓库收物 = EFFECTIVE<br>zuo_gong.冲开墓库 = 冲开墓库 | THEME-009 |
| THEME-010 福德精神 | ESTABLISHED | zuo_gong.食伤做功 = EFFECTIVE<br>blind_wangshuai = WANG<br>zuo_gong.印做功 = EFFECTIVE | THEME-010, BLIND-FUDE-001 |
| THEME-011 父母长辈 | ESTABLISHED | parents.father(偏财) = ABSENT<br>parents.mother(印星) = PRESENT | THEME-011 |
| THEME-012 才艺学业 | ESTABLISHED | zuo_gong.印做功(学业) = EFFECTIVE<br>zuo_gong.食伤泄秀(才艺) = NOT_EFFECTIVE<br>talent.direction = WEN(木火) | THEME-012, BLIND-XUELI-001 |
