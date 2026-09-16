# 盲派 Judgment Engine V1.1 Semantic Gate 验收矩阵

基线 commit: ab619820
验收日期: 2026-09-17
验收人: 人工 + 机器

## 验收标准

每条Judgment三种状态：
- **PASS**: 正例触发 / 反例不触发 / Exclusion命中阻断 = 完全一致
- **BOUNDARY/V2**: 语义未完整，明确记录待V2
- **FAIL**: 机器行为与原典不一致，需修

## 验收矩阵

### J-WEALTH-003 财主宾定位

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 财根在主位 | assertions={A-BZ-MAINGUEST}, features={FEAT_ROOT_IN_MAIN} | TRIGGER | 待验 | 待验 |
| C2 财根在宾位 | assertions={A-BZ-MAINGUEST}, features={FEAT_ROOT_IN_GUEST} | TRIGGER | 待验 | 待验 |
| C3 年上财 | assertions={A-BZ-MAINGUEST}, features={FEAT_WEALTH_AT_YEAR} | TRIGGER | 待验 | 待验 |
| Exclusion 不估金额 | assertions={A-BZ-MAINGUEST}, features={FEAT_WEALTH_LEVEL} | BLOCK | 待验 | 待验 |

### J-WEALTH-005 财星反局

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 反局在财位 | assertions={A-PJ-FAN}, features={FEAT_FANJU_AT_WEALTH} | TRIGGER | 待验 | 待验 |
| Exclusion 不估金额 | assertions={A-PJ-FAN}, features={FEAT_WEALTH_AMOUNT} | BLOCK | 待验 | 待验 |

### J-OFFICIAL-002 官主宾定位

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 年上官=国企 | assertions={A-BZ-MAINGUEST}, features={FEAT_OFFICIAL_AT_YEAR} | TRIGGER | 待验 | 待验 |
| C2 日时官=私企 | assertions={A-BZ-MAINGUEST}, features={FEAT_OFFICIAL_AT_DAY_HOUR} | TRIGGER | 待验 | 待验 |
| Exclusion 不估级别 | assertions={A-BZ-MAINGUEST}, features={FEAT_OFFICIAL_RANK} | BLOCK | 待验 | 待验 |

### J-OFFICIAL-003 官透克身

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 官透克身无制 | assertions={A-TY-TIYONG}, features={FEAT_OFFICIAL_TRANSPARENT_ATTACK} | TRIGGER | 待验 | 待验 |
| Exclusion 不做官级别 | assertions={A-TY-TIYONG}, features={FEAT_OFFICIAL_RANK} | BLOCK | 待验 | 待验 |

### J-CAREER-001 财原神→银行

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 财原神=银行 | assertions={A-SX-HESYMBOLS,...}, features={FEAT_WEALTH_SOURCE_AT_BANK} | TRIGGER | 待验 | 待验 |
| C2 辰拱水=化工 | assertions={A-SX-HESYMBOLS,...}, features={FEAT_CHEN_GONG_WATER} | TRIGGER | 待验 | 待验 |
| Exclusion 不指定职业名 | assertions={...}, features={FEAT_SPECIFIC_JOB_NAME} | BLOCK | 待验 | 待验 |

### J-SPECIAL-001 反局三层

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 原局反局 | assertions={A-PJ-ZHENG, A-PJ-FAN}, features={FEAT_NATAL_FANJU} | TRIGGER | 待验 | 待验 |
| C2 大运反局 | assertions={...}, features={FEAT_LUCK_FANJU} | TRIGGER | 待验 | 待验 |
| C3 流年反局 | assertions={...}, features={FEAT_YEAR_FANJU} | TRIGGER | 待验 | 待验 |
| Exclusion 正局不自动推吉 | assertions={...}, features={FEAT_ZHENG_AUTO_AUSPICIOUS} | BLOCK | 待验 | 待验 |

### J-TIMING-002 大运体用动静

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 走干运支为体 | assertions={A-PJ-FANJULU}, features={FEAT_STEM_LUCK_BRANCH_TI} | TRIGGER | 待验 | 待验 |
| C2 走支运干为体 | assertions={...}, features={FEAT_BRANCH_LUCK_STEM_TI} | TRIGGER | 待验 | 待验 |
| Exclusion 体用不混淆 | assertions={...}, features={FEAT_TIYONG_CONFUSION} | BLOCK | 待验 | 待验 |

### J-DISASTER-002 反局+辰=牢狱风险

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 原局反局+辰 | assertions={A-DISASTER-PRISON}, features={FEAT_NATAL_FANJU_CHEN} | TRIGGER | 待验 | 待验 |
| Exclusion 辰单独不等于牢狱 | assertions={...}, features={FEAT_CHEN_ALONE_PRISON} | BLOCK | 待验 | 待验 |

### J-HEALTH-002 时柱被穿=膀胱直肠风险

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 时柱被穿+岁运引动 | assertions={A-BODY-GONGWEI}, features={FEAT_HOUR_PILLAR_CHUAN} | TRIGGER | 待验 | 待验 |
| Exclusion 风险≠确诊 | assertions={...}, features={FEAT_MEDICAL_DIAGNOSIS} | BLOCK | 待验 | 待验 |

### J-DISASTER-003 丑酉阴中阴=犯罪结构

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 丑酉同现阴干入墓 | assertions={A-DISASTER-PRISON}, features={FEAT_CHOU_YOU_YIN_RUMU} | TRIGGER | 待验 | 待验 |
| Exclusion 辛丑不成立 | assertions={...}, features={FEAT_XINCHOU_CLEAR} | BLOCK | 待验 | 待验 |

### J-CAREER-003 文理分科

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 木火=文 | assertions={A-SX-STEMBRANCH}, features={FEAT_WOOD_FIRE_WEN} | TRIGGER | 待验 | 待验 |
| C2 金水=理 | assertions={...}, features={FEAT_METAL_WATER_LI} | TRIGGER | 待验 | 待验 |
| C3 戌亥=数学 | assertions={...}, features={FEAT_XU_HAI_MATH} | TRIGGER | 待验 | 待验 |
| C4 丑=玄学 | assertions={...}, features={FEAT_CHOU_XUANXUE} | TRIGGER | 待验 | 待验 |
| C5 申金融酉法律 | assertions={...}, features={FEAT_SHEN_FINANCE_YOU_LAW} | TRIGGER | 待验 | 待验 |
| Exclusion 不指定具体专业 | assertions={...}, features={FEAT_SPECIFIC_MAJOR} | BLOCK | 待验 | 待验 |

### J-CAREER-004 干支→行业

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 阳木遇火=家具 | assertions={A-SX-STEMBRANCH}, features={FEAT_YANG_WOOD_FIRE_FURNITURE} | TRIGGER | 待验 | 待验 |
| C2 阴木遇火=纺织 | assertions={...}, features={FEAT_YIN_WOOD_FIRE_TEXTILE} | TRIGGER | 待验 | 待验 |
| C3 辛金取财=五金 | assertions={...}, features={FEAT_XIN_METAL_WEALTH_HARDWARE} | TRIGGER | 待验 | 待验 |
| C4 火克金=冶炼 | assertions={...}, features={FEAT_FIRE_ATTACK_METAL_SMELTING} | TRIGGER | 待验 | 待验 |
| Exclusion 不指定具体单位 | assertions={...}, features={FEAT_SPECIFIC_COMPANY} | BLOCK | 待验 | 待验 |

### J-HEALTH-003 甲丁=头发/面损

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 甲丁同现=头发稀 | assertions={A-BODY-STEM}, features={FEAT_JIA_DING_HAIR_THIN} | TRIGGER | 待验 | 待验 |
| C2 甲头丁面癸克=面损 | assertions={...}, features={FEAT_JIA_HEAD_DING_FACE_GUI_ATTACK} | TRIGGER | 待验 | 待验 |
| Exclusion 风险≠确诊 | assertions={...}, features={FEAT_MEDICAL_DIAGNOSIS} | BLOCK | 待验 | 待验 |

### J-WEALTH-006 禄印相随

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 禄不配印=辛苦 | assertions={A-WEALTH-LUASCASH, A-SHEN-LU}, features={FEAT_LU_NO_YIN_HARD} | TRIGGER | 待验 | 待验 |
| C2 禄配印=享受 | assertions={...}, features={FEAT_LU_WITH_YIN_EASE} | TRIGGER | 待验 | 待验 |
| Exclusion 不得演化成财富等级 | assertions={...}, features={FEAT_WEALTH_LEVEL} | BLOCK | 待验 | 待验 |

### J-OFFICIAL-004 羊刃正/偏业

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 羊刃有制=正业 | assertions={A-SHEN-YANGREN}, features={FEAT_YANGREN_CONTROLLED_ORTHODOX} | TRIGGER | 待验 | 待验 |
| C2 羊刃无制=偏业 | assertions={...}, features={FEAT_YANGREN_UNCONTROLLED_UNORTHODOX} | TRIGGER | 待验 | 待验 |
| Exclusion 只给方向 | assertions={...}, features={FEAT_DIRECT_JOB_LABEL} | BLOCK | 待验 | 待验 |

### J-CAREER-002 墓库→机构

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 羊刃库=军队 | assertions={A-MUKU-IDENTIFIED, A-SX-MUSYMBOLS}, features={FEAT_YANGREN_MUKU_MILITARY} | TRIGGER | 待验 | 待验 |
| C2 伤食库=学校 | assertions={...}, features={FEAT_SHANGSHI_MUKU_SCHOOL} | TRIGGER | 待验 | 待验 |
| C3 财库=银行 | assertions={...}, features={FEAT_WEALTH_MUKU_BANK} | TRIGGER | 待验 | 待验 |
| C4 官杀库=组织 | assertions={...}, features={FEAT_GUANSHA_MUKU_ORG} | TRIGGER | 待验 | 待验 |
| Exclusion 只给方向 | assertions={...}, features={FEAT_SPECIFIC_INSTITUTION} | BLOCK | 待验 | 待验 |

### J-TIMING-003 驿马走动/停留

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 驿马存在=走动 | assertions={A-SHEN-YIMA}, features={FEAT_YIMA_PRESENT} | TRIGGER | 待验 | 待验 |
| C2 驿马被合=停留 | assertions={...}, features={FEAT_YIMA_HE_STATIONARY} | TRIGGER | 待验 | 待验 |
| Exclusion 驿马≠搬家 | assertions={...}, features={FEAT_YIMA_MOVE_GUARANTEE} | BLOCK | 待验 | 待验 |

### J-KIN-002 空亡分宫

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 年空亡=祖业空 | assertions={A-SHEN-KONGWANG}, features={FEAT_YEAR_KONGWANG_ZUYE} | TRIGGER | 待验 | 待验 |
| C2 月空亡=兄弟无靠 | assertions={...}, features={FEAT_MONTH_KONGWANG_BROTHER} | TRIGGER | 待验 | 待验 |
| C3 日空亡=夫妻缘薄 | assertions={...}, features={FEAT_DAY_KONGWANG_SPOUSE} | TRIGGER | 待验 | 待验 |
| C4 时空亡=子女迟育 | assertions={...}, features={FEAT_HOUR_KONGWANG_CHILDREN} | TRIGGER | 待验 | 待验 |
| Exclusion 空亡≠必然 | assertions={...}, features={FEAT_KONGWANG_DEFINITE_EVENT} | BLOCK | 待验 | 待验 |

### J-MARRIAGE-002 禄绊桃花

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 女命禄合桃花 | assertions={A-SHEN-LU}, features={FEAT_FEMALE_LU_HE_TAOHUA} | TRIGGER | 待验 | 待验 |
| Exclusion 合夫妻宫不算桃花 | assertions={...}, features={FEAT_HE_SPOUSE_PALACE_TAOHUA} | BLOCK | 待验 | 待验 |

### J-WEALTH-007 时支=车

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 时支被生=买车 | assertions={A-BODY-GONGWEI}, features={FEAT_HOUR_BRANCH_SHENG_CAR} | TRIGGER | 待验 | 待验 |
| C2 时支被破=车损 | assertions={...}, features={FEAT_HOUR_BRANCH_BREAK_CAR_RISK} | TRIGGER | 待验 | 待验 |
| Exclusion 信号≠事件 | assertions={...}, features={FEAT_CAR_EVENT_GUARANTEE} | BLOCK | 待验 | 待验 |

### J-HEALTH-005 年支被破=腿足残疾

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 年被主位比劫破 | assertions={A-BODY-GONGWEI}, features={FEAT_YEAR_BREAK_BY_MAIN_BIJIE} | TRIGGER | 待验 | 待验 |
| Exclusion 主位破宾位 | assertions={...}, features={FEAT_MAIN_BREAK_GUEST_REQUIRED} | BLOCK | 待验 | 待验 |

### J-KIN-003 丈母娘在年

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 年与妻宫关联 | assertions={A-BODY-GONGWEI}, features={FEAT_YEAR_RELATED_SPOUSE_PALACE} | TRIGGER | 待验 | 待验 |
| Exclusion 与妻宫无关 | assertions={...}, features={FEAT_NO_SPOUSE_PALACE_RELATION} | BLOCK | 待验 | 待验 |

### J-MARRIAGE-003 夫妻象在月=同学

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 夫妻象在月柱 | assertions={A-BODY-GONGWEI}, features={FEAT_SPOUSE_AT_MONTH_SCHOOLMATE} | TRIGGER | 待验 | 待验 |
| Exclusion 不必然 | assertions={...}, features={FEAT_SPOUSE_SOURCE_GUARANTEE} | BLOCK | 待验 | 待验 |

### J-WEALTH-008 财多心乱=早辍学

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 年月财旺女命 | assertions={A-TY-TIYONG}, features={FEAT_WEALTH_STRONG_YEAR_MONTH_FEMALE} | TRIGGER | 待验 | 待验 |
| Exclusion 只是倾向 | assertions={...}, features={FEAT_DROPOUT_GUARANTEE} | BLOCK | 待验 | 待验 |

### J-WEALTH-009 财虚透=才华

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 财虚透天干 | assertions={A-TY-TIYONG}, features={FEAT_WEALTH_TRANSPARENT_TALENT} | TRIGGER | 待验 | 待验 |
| C2 财虚透时上=时尚 | assertions={...}, features={FEAT_WEALTH_TRANSPARENT_AT_HOUR_FASHION} | TRIGGER | 待验 | 待验 |
| Exclusion 是象不必然 | assertions={...}, features={FEAT_WEALTH_SYMBOL_GUARANTEE} | BLOCK | 待验 | 待验 |

### J-CHILD-001 子女性别倾向

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 男杀有财=儿 | assertions={A-TY-TIYONG}, features={FEAT_MALE_SHA_WITH_WEALTH_SON} | TRIGGER | 待验 | 待验 |
| C2 男杀无财=女 | assertions={...}, features={FEAT_MALE_SHA_NO_WEALTH_DAUGHTER} | TRIGGER | 待验 | 待验 |
| C3 穿财=生女 | assertions={...}, features={FEAT_CHUAN_WEALTH_DAUGHTER} | TRIGGER | 待验 | 待验 |
| C4 伤官运=生儿 | assertions={...}, features={FEAT_HURT_OFFICIAL_LUCK_SON} | TRIGGER | 待验 | 待验 |
| Exclusion 只是倾向 | assertions={...}, features={FEAT_CHILD_GENDER_GUARANTEE} | BLOCK | 待验 | 待验 |

### J-KIN-004 食神被穿=母早死风险

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 食神被穿无救 | assertions={A-TY-TIYONG}, features={FEAT_SHISHEN_CHUAN_NO_SALVATION} | TRIGGER | 待验 | 待验 |
| Exclusion 风险≠必然 | assertions={...}, features={FEAT_MOTHER_DEATH_GUARANTEE} | BLOCK | 待验 | 待验 |

### J-WEALTH-010 穿门口=车被盗风险

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 时柱被穿 | assertions={A-BODY-GONGWEI}, features={FEAT_HOUR_PILLAR_CHUAN_CAR_THEFT} | TRIGGER | 待验 | 待验 |
| Exclusion 风险≠必然 | assertions={...}, features={FEAT_CAR_THEFT_GUARANTEE} | BLOCK | 待验 | 待验 |

### J-OFFICIAL-005 阳制阴=公安

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 阳字制阴字 | assertions={A-SX-HESYMBOLS}, features={FEAT_YANG_ATTACK_YIN_POLICE} | TRIGGER | 待验 | 待验 |
| Exclusion 只给方向 | assertions={...}, features={FEAT_DEPARTMENT_RANK} | BLOCK | 待验 | 待验 |

### J-WEALTH-011 带象四法

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 财带官帽=公家 | assertions={A-SX-DAISYMBOLS}, features={FEAT_WEALTH_WITH_OFFICIAL_CAP_PUBLIC} | TRIGGER | 待验 | 待验 |
| C2 官带财帽=管理 | assertions={...}, features={FEAT_OFFICIAL_WITH_WEALTH_CAP_MANAGER} | TRIGGER | 待验 | 待验 |
| C3 印带官帽=权力 | assertions={...}, features={FEAT_YIN_WITH_OFFICIAL_CAP_POWER} | TRIGGER | 待验 | 待验 |
| C4 印带财帽=薪水 | assertions={...}, features={FEAT_YIN_WITH_WEALTH_CAP_SALARY} | TRIGGER | 待验 | 待验 |
| Exclusion 是象不必然 | assertions={...}, features={FEAT_WEALTH_NATURE_GUARANTEE} | BLOCK | 待验 | 待验 |

### J-OFFICIAL-006 杀入羊刃墓=军队

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 七杀入羊刃墓 | assertions={A-MUKU-IDENTIFIED}, features={FEAT_SHA_INTO_YANGREN_MUKU_MILITARY} | TRIGGER | 待验 | 待验 |
| Exclusion 不推级别 | assertions={...}, features={FEAT_SPECIFIC_RANK} | BLOCK | 待验 | 待验 |

### J-CAREER-005 辰子=化工制药

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 辰子同现 | assertions={A-SX-HUASYMBOLS}, features={FEAT_CHEN_ZI_CHEMICAL_PHARMA} | TRIGGER | 待验 | 待验 |
| Exclusion 只给行业 | assertions={...}, features={FEAT_SPECIFIC_INDUSTRY} | BLOCK | 待验 | 待验 |

### J-WEALTH-012 丑未冲=资本运营

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 丑未冲财库 | assertions={A-MUKU-IDENTIFIED}, features={FEAT_CHOU_WEI_CHONG_CAPITAL} | TRIGGER | 待验 | 待验 |
| Exclusion 不估金额 | assertions={...}, features={FEAT_WEALTH_AMOUNT} | BLOCK | 待验 | 待验 |

### J-WEALTH-013 禄神当财

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 禄当财条件 | assertions={A-WEALTH-LUASCASH}, features={FEAT_LU_AS_WEALTH_CONDITION} | TRIGGER | 待验 | 待验 |
| C2 印生禄 | assertions={...}, features={FEAT_LU_AS_WEALTH_YIN_SHENG} | TRIGGER | 待验 | 待验 |
| C3 禄取财辛苦 | assertions={...}, features={FEAT_LU_WEALTH_HARD} | TRIGGER | 待验 | 待验 |
| C4 禄见劫财破财 | assertions={...}, features={FEAT_LU_JIECAI_BROKEN} | TRIGGER | 待验 | 待验 |
| Exclusion 不估金额 | assertions={...}, features={FEAT_WEALTH_AMOUNT} | BLOCK | 待验 | 待验 |

### J-WEALTH-014 伤食当财

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 无财伤食当财 | assertions={A-WEALTH-LUASCASH}, features={FEAT_NO_WEALTH_SHANGSHI_AS_WEALTH} | TRIGGER | 待验 | 待验 |
| C2 伤食财性质 | assertions={...}, features={FEAT_SHANGSHI_WEALTH_NATURE} | TRIGGER | 待验 | 待验 |
| C3 食干支性质 | assertions={...}, features={FEAT_SHISHEN_STEM_BRANCH_NATURE} | TRIGGER | 待验 | 待验 |
| Exclusion 有财时伤食是原神 | assertions={...}, features={FEAT_HAS_WEALTH_SHANGSHI_YUANSHEN} | BLOCK | 待验 | 待验 |

### J-WEALTH-015 官杀当财

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 官统财/财统官 | assertions={A-WEALTH-LUASCASH}, features={FEAT_GUAN_WEALTH_UNIFIED} | TRIGGER | 待验 | 待验 |
| C2 官杀制不净 | assertions={...}, features={FEAT_GUANSHA_NOT_CONTROLLED_PURE} | TRIGGER | 待验 | 待验 |
| Exclusion 只论原局 | assertions={...}, features={FEAT_LUCK_APPEARANCE} | BLOCK | 待验 | 待验 |

### J-CAREER-006 内食神=企业

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 内食神做功 | assertions={A-SX-HUASYMBOLS}, features={FEAT_INNER_SHISHEN_BUSINESS} | TRIGGER | 待验 | 待验 |
| C2 食带官=经理人 | assertions={...}, features={FEAT_SHISHEN_WITH_OFFICIAL_MANAGER} | TRIGGER | 待验 | 待验 |
| Exclusion 不指定行业 | assertions={...}, features={FEAT_SPECIFIC_INDUSTRY} | BLOCK | 待验 | 待验 |

### J-WEALTH-016 财在年=远方贸易

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 财在年+远方+水 | assertions={A-BODY-GONGWEI}, features={FEAT_WEALTH_AT_YEAR_REMOTE_TRADE} | TRIGGER | 待验 | 待验 |
| Exclusion 不单独推海外 | assertions={...}, features={FEAT_SINGLE_OVERSEAS_TRADE} | BLOCK | 待验 | 待验 |

### J-MARRIAGE-004 好婚姻结构

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 夫妻宫安静制星 | assertions={A-MARRIAGE-MAINGUEST}, features={FEAT_SPOUSE_PALACE_QUIET_CONTROL} | TRIGGER | 待验 | 待验 |
| Exclusion 制之不住 | assertions={...}, features={FEAT_CONTROL_INSUFFICIENT} | BLOCK | 待验 | 待验 |

### J-MARRIAGE-005 差婚姻结构

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 夫妻宫被破坏 | assertions={A-MARRIAGE-MAINGUEST}, features={FEAT_SPOUSE_PALACE_DAMAGED} | TRIGGER | 待验 | 待验 |
| C2 破坏轻不离婚 | assertions={...}, features={FEAT_DAMAGE_LIGHT_NO_DIVORCE} | TRIGGER | 待验 | 待验 |
| C3 破坏重必离异 | assertions={...}, features={FEAT_DAMAGE_HEAVY_DIVORCE} | TRIGGER | 待验 | 待验 |
| C4 比劫争配偶 | assertions={...}, features={FEAT_BIJIE_COMPETE_SPOUSE} | TRIGGER | 待验 | 待验 |
| Exclusion 不必然离婚 | assertions={...}, features={FEAT_DIVORCE_GUARANTEE} | BLOCK | 待验 | 待验 |

### J-MARRIAGE-006 结婚应期窗口

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 冲合婚期 | assertions={A-MARRIAGE-MAINGUEST}, features={FEAT_SPOUSE_HE_CHONG_MARRIAGE_TIMING} | TRIGGER | 待验 | 待验 |
| C2 冲墓婚期 | assertions={...}, features={FEAT_SPOUSE_RUMU_CHONG_MARRIAGE_TIMING} | TRIGGER | 待验 | 待验 |
| Exclusion 窗口≠坐实 | assertions={...}, features={FEAT_MARRIAGE_EVENT_GUARANTEE} | BLOCK | 待验 | 待验 |

### J-MARRIAGE-007 比劫争夫

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 比劫与夫星关系 | assertions={A-TY-TIYONG}, features={FEAT_BIJIE_WITH_HUSBAND_STAR_COMPETE} | TRIGGER | 待验 | 待验 |
| Exclusion 只是可能 | assertions={...}, features={FEAT_COMPETE_GUARANTEE} | BLOCK | 待验 | 待验 |

### J-DISASTER-004 牢狱五结构（Clause A~E）

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| A 丑辰亥坏阳用 | assertions={A-DISASTER-PRISON}, features={FEAT_CHOU_CHEN_HAI_DAMAGE_YANG_USEFUL} | TRIGGER | 待验 | 待验 |
| B 水多金沉 | assertions={...}, features={FEAT_WATER_METAL_SINK_PRISON} | TRIGGER | 待验 | 待验 |
| C 枭神夺食 | assertions={...}, features={FEAT_XIAO_SHEN_DUO_SHISHEN_FREEDOM} | TRIGGER | 待验 | 待验 |
| D 劫财伤官抗官杀 | assertions={...}, features={FEAT_JIECAISHANGSHI_ATTACK_OFFICIAL_PRISON} | TRIGGER | 待验 | 待验 |
| E 反局+丑辰多数牢狱 | assertions={...}, features={FEAT_FANJU_WITH_CHOU_CHEN_MOST_PRISON} | TRIGGER | 待验 | 待验 |
| Exclusion 阳制阴不算 | assertions={...}, features={FEAT_YANG_CONTROL_YIN} | BLOCK | 待验 | 待验 |

### J-DISASTER-005 出狱应期

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 日主得禄出狱 | assertions={A-DISASTER-PRISON}, features={FEAT_DAY_MASTER_LU_RELEASE} | TRIGGER | 待验 | 待验 |
| C2 日主合冲出狱 | assertions={...}, features={FEAT_DAY_MASTER_HE_CHONG_RELEASE} | TRIGGER | 待验 | 待验 |
| C3 冲穿库出狱 | assertions={...}, features={FEAT_PRISON_MUKU_CHUAN_RELEASE} | TRIGGER | 待验 | 待验 |
| Exclusion 窗口≠坐实 | assertions={...}, features={FEAT_RELEASE_EVENT_GUARANTEE} | BLOCK | 待验 | 待验 |

### J-WEALTH-017 劫财官在主=小偷

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 劫财官在主位 | assertions={A-TY-TIYONG}, features={FEAT_JIECAI_OFFICIAL_AT_MAIN_THIEF} | TRIGGER | 待验 | 待验 |
| Exclusion 结构≠犯罪 | assertions={...}, features={FEAT_CRIME_GUARANTEE} | BLOCK | 待验 | 待验 |

### J-DISASTER-006 伤食入墓=失自由

| Clause | 正例输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| C1 食伤入墓 | assertions={A-MUKU-IDENTIFIED}, features={FEAT_SHANGSHI_RUMU_FREEDOM_LOSS} | TRIGGER | 待验 | 待验 |
| Exclusion 结构≠坐牢 | assertions={...}, features={FEAT_PRISON_GUARANTEE} | BLOCK | 待验 | 待验 |

---

## 验收总结

| 状态 | 数量 |
|---|---|
| PASS | 待填 |
| BOUNDARY/V2 | 待填 |
| FAIL | 待填 |
| 总计 | 46 Judgment |
