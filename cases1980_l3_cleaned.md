# 1980-06-22 10:00 男 广州 · 盲派 L3（根因A-E修复+日主得气校准版，引擎原始输出）

> 本轮新增：日主得气校准（文献《盲派命理-案例资料集》'有财官≠有富贵, 关键在于谁在做功、是否为我所用'；
> '非日主得气→终身仓库保管员'）——有效功无一日主亲自/禄身→效率压一档；
> 包局 actor_dim 修复（包群含日支/日主禄=LU_SELF, 含主位=TOOL_ASSISTED, 全宾位=OTHER）。

## [THEME-001] 性情禀赋 · ESTABLISHED
- 现代总括：性情由旺衰+五行+透干十神共同决定，以下为逐项事实
- 事实 blind_wangshuai=WANG
  原文断言：盲派旺衰·身旺（《命理玄机探秘》四定律界定；弃旺衰，仅状态分类）
  现代语义：日主自身力量旺（状态分类，不取用神）
- 事实 five_element_imbalance=TRUE
  原文断言：五行失衡（八字排盘层五行统计事实，非盲派口诀）
  现代语义：五行分布不均（排盘层统计事实，性情另由旺衰/透干十神判）
- 事实 transparent_ten_gods.year=偏财
  原文断言：十神心性·偏财：慷慨大方，重实际，善经营（传统十神心性通论·渊海子平十神赋系）
  现代语义：透干偏财：为人慷慨大方，注重实际利益，善于经营谋划
- 事实 transparent_ten_gods.month=七杀
  原文断言：十神心性·七杀：果断威权，性急多疑（传统十神心性通论·渊海子平十神赋系）
  现代语义：透干七杀：做事果断有魄力，性急，疑心较重
- 事实 transparent_ten_gods.hour=正官
  原文断言：十神心性·正官：循规蹈矩，重名誉（传统十神心性通论·渊海子平十神赋系）
  现代语义：透干正官：守规矩讲原则，重视名誉，责任心强

## [THEME-002] 交游人际 · ESTABLISHED
- 现代总括：同胞关系以比劫计数为据
- 事实 kinship_count.brother_count=0
  原文断言：盲派六亲计数·比肩为兄弟/劫财为姐妹
  现代语义：同胞中兄弟 0 人
- 事实 kinship_count.sister_count=6
  原文断言：盲派六亲计数·比肩为兄弟/劫财为姐妹
  现代语义：同胞中姐妹 6 人
- 事实 zuo_gong.比劫做功=EFFECTIVE
  原文断言：盲派做功·比肩去财（段建业讲义：制用五种之'比肩去财'；有比劫制财局和财制比劫局两种）
  现代语义：比劫制财做功成立（比肩去财），取财靠伙伴/竞争

## [THEME-003] 婚姻配偶 · ESTABLISHED
- 现代总括：婚姻以配偶宫（日支）+配偶星状态为据
- 事实 marriage_event_structure.marriage_state=BROKEN
  原文断言：盲派口诀·配偶宫逢冲必离婚（《盲派中级命理学·婚姻篇》：日支为配偶宫，逢冲必离婚）
  现代语义：婚姻上容易出现分离、难长久的问题
- 事实 marriage_event_structure.palace_state=CLASHED_AND_PUNISHED
  原文断言：盲派婚姻·配偶宫逢冲（《盲派中级命理学·婚姻篇》：日支逢冲必离婚）
  现代语义：配偶宫（日支）被冲，婚姻根基动摇
- 事实 marriage_event_structure.palace_state=CLASHED_AND_PUNISHED
  原文断言：盲派婚姻·配偶宫逢刑（《盲派中级命理学·婚姻篇》：配偶宫相刑=婚姻出问题）
  现代语义：配偶宫（日支）被刑，夫妻易有口舌纠纷
- 事实 marriage_event_structure.spouse_star_present=True
  原文断言：盲派婚姻·配偶星在局（《盲派中级命理学·婚姻篇》：男命以财星为妻，女命以官杀为夫）
  现代语义：配偶星在局中（有婚姻对象之缘）

## [THEME-004] 子女 · CANDIDATE
- 现代总括：子女以子女星+子女宫（时支）状态为据
- 事实 children.star=男命有财→官杀为子女星(七杀为儿/正官为女)
  原文断言：段建业《盲派八字命理口诀·子女》：有财星则以七杀为儿、正官为女
  现代语义：男命以官杀为子女星（七杀主儿子、正官主女儿）
- 事实 children.star_present=TRUE
  原文断言：段建业《盲派八字命理口诀·子女》：以财/食伤定子女星（原文见上）
  现代语义：子女星在局中
- 事实 children.palace_hit=时支逢穿
  原文断言：段建业《盲派八字命理口诀·子女》：时柱=子女宫，忌伤
  现代语义：子女宫（时支）逢穿，子女运有损

## [THEME-005] 财帛 · ESTABLISHED
- 现代总括：财富以财星取用做功状态为据
- 事实 wealth_event_structure.wealth_state=DIRECTED_AND_ESTABLISHED
  原文断言：盲派财富·有势又有功定是富贵翁（VERIFY-BLIND-024：财官在主位就是我的财官）+ 财现+财被取+做功成（生用结构·食伤生财/制用五种·制财）
  现代语义：财星被定向取用且做功成立，求财有成
- 事实 wealth_event_structure.wealth_present=True
  原文断言：盲派财富·财星在局（VERIFY-BLIND-024：财官在主位，就是我的财官）
  现代语义：局中有财星

## [THEME-006] 身体疾厄 · ESTABLISHED
- 现代总括：身体以禄神/羊刃/燥土状态为据
- 事实 body_event_candidate.candidate=LU_UNDER_ATTACK
  原文断言：盲派口诀·禄怕见绝更怕穿害（盲派身体章：禄神被穿/合克/脆金则受损）
  现代语义：禄神受攻击（被穿/合克/脆金），身体或福报易受损
- 事实 body_event_candidate.lu_attacked=True
  原文断言：盲派口诀·禄怕见绝更怕穿害（盲派身体章：禄神被穿/合克则受损）
  现代语义：禄神状态受损（穿/冲/合克）
- 事实 dry_earth_brittle=NO_DRY_EARTH
  原文断言：盲派口诀·燥土脆金（VERIFY-BLIND-034《段氏理象学》：燥土不能生金反脆金；无燥土则无此患）
  现代语义：无燥土脆金之患

## [THEME-007] 迁移出行 · ESTABLISHED
- 现代总括：迁移以驿马+引动状态为据
- 事实 yima.present=SHEN马在YIN_AND_YIN马在SHEN
  原文断言：盲派金口诀·论驿马：申子辰马在寅
  现代语义：命带驿马（申马在寅），主走动奔波
- 事实 yima.present=SHEN马在YIN_AND_YIN马在SHEN
  原文断言：盲派金口诀·论驿马：寅午戌马在申
  现代语义：命带驿马（寅马在申），主走动奔波
- 事实 yima.trigger=NO_TRIGGER
  原文断言：盲派金口诀·驿马逢冲/合为引动（驿马主动；无引动则不动）
  现代语义：驿马未被大运流年冲合引动，暂不迁移

## [THEME-008] 事业功名 · ESTABLISHED
- 现代总括：事业以做功类型+官杀制净状态为据
- 事实 occupation_candidate.work_type.CONTROL_OFFICER_BY_FOOD_INJURY=CONTROL_OFFICER_BY_FOOD_INJURY
  原文断言：制用五种·食伤制杀（段建业讲义：食伤制官杀为当官结构；VERIFY-BLIND-026：食神制煞靠技能权谋）
  现代语义：做功类型 CONTROL_OFFICER_BY_FOOD_INJURY：以食伤制官杀取功名，走公职/管理路线
- 事实 occupation_candidate.work_type.CONTROL_WEALTH_BY_BIJIE=CONTROL_WEALTH_BY_BIJIE
  原文断言：制用五种·比肩去财（VERIFY-BLIND-003：比劫制财局；比劫当财看）
  现代语义：做功类型 CONTROL_WEALTH_BY_BIJIE：靠朋友/伙伴/竞争制财，与人合伙谋财
- 事实 occupation_candidate.work_type.CONTROL_WEALTH_BY_INTERACTION=CONTROL_WEALTH_BY_INTERACTION
  原文断言：合制做功·制财之原神（VERIFY-BLIND-006/009：合而有制为做功；制净财之原神则财大）
  现代语义：做功类型 CONTROL_WEALTH_BY_INTERACTION：以互动方式制财之原神（食神），财富级别大
- 事实 occupation_candidate.work_type.GENERATE_WEALTH_BY_FOOD_INJURY=GENERATE_WEALTH_BY_FOOD_INJURY
  原文断言：生用结构·食伤生财（VERIFY-BLIND-005：食伤生财靠技艺技术）
  现代语义：做功类型 GENERATE_WEALTH_BY_FOOD_INJURY：以食伤生财，靠技艺/技术谋财
- 事实 occupation_candidate.work_type.CONTROL_RESOURCE_BY_WEALTH=CONTROL_RESOURCE_BY_WEALTH
  原文断言：制用五种·财来制印（VERIFY-BLIND-003：财制印为制用之一，主掌财权）
  现代语义：做功类型 CONTROL_RESOURCE_BY_WEALTH：以财制印做功，靠资本运作控制资源权力
- 事实 occupation_candidate.work_type.TRANSFORM_OFFICER_BY_RESOURCE=TRANSFORM_OFFICER_BY_RESOURCE
  原文断言：化用结构·印化官杀（VERIFY-BLIND-004：用印化官杀，大多为当官的；VERIFY-BLIND-026：杀印相生靠贵人或平台）
  现代语义：做功类型 TRANSFORM_OFFICER_BY_RESOURCE：以印化官杀，靠单位/文职立足
- 事实 occupation_candidate.work_type.CONTROL_FOOD_INJURY_BY_RESOURCE=CONTROL_FOOD_INJURY_BY_RESOURCE
  原文断言：制用五种·印制食伤（VERIFY-BLIND-003：印制食伤；印=权力、食伤=财富）
  现代语义：做功类型 CONTROL_FOOD_INJURY_BY_RESOURCE：以印印制食伤，靠约束收敛立身
- 事实 occupation_candidate.work_type.CONTROL_BIJIE_BY_OFFICER=CONTROL_BIJIE_BY_OFFICER
  原文断言：盲派做功·官杀制比劫（段建业讲义：制用五种）
  现代语义：做功类型 CONTROL_BIJIE_BY_OFFICER：以官杀制比劫，靠规则/领导约束团队
- 事实 official_event_structure.official_state=CONTROLLED_AND_CLEAN
  原文断言：盲派口诀·制尽杀星得天下（《盲派中级命理学·官贵章》：官杀制净则得天下）
  现代语义：官杀被制净，功名/管理有成
- 事实 work_efficiency=MEDIUM
  原文断言：盲派效率·做功效率中（制用五种：克制未净则效率中平）
  现代语义：做功效率中等，事业成就有一定层次

## [THEME-009] 田宅家业 · ESTABLISHED
- 现代总括：田宅家业以墓库收物状态为据
- 事实 zuo_gong.墓库收物=NOT_EFFECTIVE
  原文断言：盲派墓库·墓库喜冲（VERIFY-BLIND-020：库不开则财官无用）
  现代语义：墓库收物未成立，家业/积蓄平平

## [THEME-010] 福德精神 · ESTABLISHED
- 现代总括：福德以食伤（寿）+印（福）+旺衰为据
- 事实 zuo_gong.食伤做功=EFFECTIVE
  原文断言：盲派十神口诀·日带食神自己福，一世不会受辛苦（食神主衣食口福）
  现代语义：食伤做功成立，有福气、衣食无忧
- 事实 blind_wangshuai=WANG
  原文断言：盲派旺衰·身旺（《命理玄机探秘》四定律界定；弃旺衰，仅状态分类）
  现代语义：日主自身力量旺（状态分类，不取用神）
- 事实 zuo_gong.印做功=EFFECTIVE
  原文断言：盲派六亲损断·印旺身强多福寿，六亲和睦家道丰
  现代语义：印做功成立，主福寿、家道和睦（印旺身强多福寿）

## [THEME-011] 父母长辈 · ESTABLISHED
- 现代总括：父母以偏财（父）+印星（母）在局与否为据
- 事实 parents.father(偏财)=PRESENT
  原文断言：盲派六亲·父星=偏财（《盲派中级命理学·六亲章》：宫位比十神更准；年柱祖上父母）
  现代语义：父星（偏财）在局中
- 事实 parents.mother(印星)=PRESENT
  原文断言：盲派六亲·母星=印星（《盲派中级命理学·六亲章》：宫位比十神更准；年柱祖上父母）
  现代语义：母星（印星）在局中

## [THEME-012] 才艺学业 · ESTABLISHED
- 现代总括：才艺学业以印做功+食伤泄秀+文理方向为据
- 事实 zuo_gong.印做功(学业)=EFFECTIVE
  原文断言：段建业《盲派中级命理学》第11章：印星须做功方表学历
  现代语义：印星做功成立，学业有成就
- 事实 zuo_gong.食伤泄秀(才艺)=NOT_EFFECTIVE
  原文断言：段建业《盲派中级命理学》第11章：食神主思想思考（不成立则才艺平平）
  现代语义：食伤泄秀不成立，思想/学习表现平平
- 事实 talent.direction=WEN(木火)
  原文断言：段建业《盲派中级命理学》第11章：金水主理，木火主文
  现代语义：文理方向偏文（木火）
