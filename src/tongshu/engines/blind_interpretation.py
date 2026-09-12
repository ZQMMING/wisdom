# -*- coding: utf-8 -*-
"""L3 解析层（Interpretation Layer）：盲派解层断语全集 → 原文断言 + 现代语义。

输入：L2.5 BlindThemeResult（12 主题聚合） + L2 BlindJudgmentResult（事件候选）
输出：每条解层断语 = { 原文断言(original) + 现代语义(modern) + 引擎事实(value) }。

铁律：
- 解层断语全集注册表（VALUE_SEMANTICS / TOKEN_SEMANTICS / EVENT_SEMANTICS /
  TIME_KIND_SEMANTICS）按**代码枚举空间全覆盖**。
- 组合枚举（palace_state / children.palace_hit / yima.present / yima.trigger /
  冲开墓库）按 "_AND_" 拆 token，逐 token 翻译拼接；STABLE/NONE/NO_TRIGGER 是
  无 token 的完整值，走 VALUE_SEMANTICS。
- 每个现代语义句子必须由注册表固定模板生成：零 LLM、零自由发挥、零评分。
- 每条映射必须带原文断言（盲派口诀/古籍原文）。注册表未覆盖 = MODERN_MISSING
  （"原文证据未取证，不做断言"），绝不发明。
- 吉凶词汇在 L3 出口正式放行（映射层=现代语言出口，吉凶按引擎方向事实化输出）。
- 后端输出全事实。

方法域：DUAN_JIANYE（段建业体系）。
"""

import ast
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

METHOD_SCOPE = "DUAN_JIANYE"

# ────────────────────────────────────────────────────────────
# 一、非组合枚举：原文断言 + 现代语义（解层断语全集）
# 结构：source → value → (原文断言, 现代语义)
# ────────────────────────────────────────────────────────────

# 十神透干 → 性情（传统十神心性通论，渊海子平十神赋系；非盲派专属原文，盲派以做功为主）
TEN_GOD_TEMPER = {
    "偏财": ("十神心性·偏财：慷慨大方，重实际，善经营（传统十神心性通论·渊海子平十神赋系）", "为人慷慨大方，注重实际利益，善于经营谋划"),
    "正财": ("十神心性·正财：勤俭踏实，守本分（传统十神心性通论·渊海子平十神赋系）", "为人勤俭踏实，守本分，重视稳定收入"),
    "七杀": ("十神心性·七杀：果断威权，性急多疑（传统十神心性通论·渊海子平十神赋系）", "做事果断有魄力，性急，疑心较重"),
    "正官": ("十神心性·正官：循规蹈矩，重名誉（传统十神心性通论·渊海子平十神赋系）", "守规矩讲原则，重视名誉，责任心强"),
    "食神": ("十神心性·食神：温和厚道，主福气（传统十神心性通论·渊海子平十神赋系）", "性情温和厚道，有口福，福气较好"),
    "伤官": ("十神心性·伤官：聪明外露，不服管（传统十神心性通论·渊海子平十神赋系）", "聪明外露，才华张扬，不愿受管束"),
    "偏印": ("十神心性·偏印：多思善谋，孤僻（传统十神心性通论·渊海子平十神赋系）", "心思多、善谋略，性格偏孤僻"),
    "正印": ("十神心性·正印：仁慈稳重，重学识（传统十神心性通论·渊海子平十神赋系）", "仁慈稳重，重视学问名声"),
    "比肩": ("十神心性·比肩：自立自强，不服输（传统十神心性通论·渊海子平十神赋系）", "自立心强，不服输，靠自己"),
    "劫财": ("十神心性·劫财：豪爽冲动，好竞争（传统十神心性通论·渊海子平十神赋系）", "为人豪爽但易冲动，好胜心强"),
}

VALUE_SEMANTICS: Dict[str, Dict[str, tuple]] = {
    # ── THEME-001 性情禀赋 ────────────────────────────────
    # 盲派旺衰仅作状态分类（弃旺衰废用忌看做功；旺衰分类据《命理玄机探秘》兄弟四定律界定）
    "blind_wangshuai": {
        "WANG_JI": ("盲派旺衰·旺极（《命理玄机探秘》四定律界定；弃旺衰，仅状态分类）", "日主旺极，气势一面倒（状态分类，不取用神）"),
        "TAI_RUO": ("盲派旺衰·太弱（《命理玄机探秘》四定律界定；弃旺衰，仅状态分类）", "日主太弱，难自立（弱极从势，状态分类）"),
        "WANG": ("盲派旺衰·身旺（《命理玄机探秘》四定律界定；弃旺衰，仅状态分类）", "日主自身力量旺（状态分类，不取用神）"),
        "ZHONG_HE_PIAN_RUO": ("盲派旺衰·中和偏弱（《命理玄机探秘》四定律界定；弃旺衰，仅状态分类）", "日主中和偏弱（状态分类，不取用神）"),
        "RUO": ("盲派旺衰·身弱（《命理玄机探秘》四定律界定；弃旺衰，仅状态分类）", "日主自身力量偏弱（状态分类，不取用神）"),
        "UNDETERMINED": ("盲派旺衰·证据不足（fail-closed，不做断言）", "旺衰判定证据不足，不做断言"),
    },
    "five_element_imbalance": {
        "TRUE": ("五行失衡（八字排盘层五行统计事实，非盲派口诀）", "五行分布不均（排盘层统计事实，性情另由旺衰/透干十神判）"),
        "FALSE": ("五行均衡（八字排盘层五行统计事实，非盲派口诀）", "五行相对均衡，性情较平和"),
    },
    # ── THEME-002 交游人际 ────────────────────────────────
    "zuo_gong.比劫做功": {
        "EFFECTIVE": ("盲派做功·比肩去财（段建业讲义：制用五种之'比肩去财'；有比劫制财局和财制比劫局两种）", "比劫制财做功成立（比肩去财），取财靠伙伴/竞争"),
        "NOT_EFFECTIVE": ("盲派做功·比劫制财未成（段建业原书核心心法：功大者贵，无功者贱）", "比劫做功未成，朋友助力有限"),
    },
    # ── THEME-003 婚姻配偶 ────────────────────────────────
    "marriage_event_structure.palace_state": {
        "STABLE": ("盲派婚姻·配偶宫安稳（《盲派中级命理学·婚姻篇》：妻宫正财坐正位，拱财局为吉）", "配偶宫安稳，婚姻基础好"),
    },
    "marriage_event_structure.marriage_state": {
        "BROKEN": ("盲派口诀·配偶宫逢冲必离婚（《盲派中级命理学·婚姻篇》：日支为配偶宫，逢冲必离婚）", "婚姻上容易出现分离、难长久的问题"),
        "CHALLENGED": ("盲派婚姻·配偶宫受损（《盲派中级命理学·婚姻篇》：配偶宫与配偶星相穿/相刑/相破=婚姻出问题）", "婚姻上容易有波折，需经营"),
        "HARMONIOUS": ("盲派婚姻·配偶宫稳定（《盲派中级命理学·婚姻篇》：配偶宫与配偶星相生/相合/拱合=婚姻好）", "婚姻状态平稳，配偶宫无破"),
        "UNDETERMINED": ("盲派婚姻·证据不足（fail-closed，不做断言）", "婚姻判定证据不足，不做断言"),
    },
    "marriage_event_structure.spouse_star_present": {
        "True": ("盲派婚姻·配偶星在局（《盲派中级命理学·婚姻篇》：男命以财星为妻，女命以官杀为夫）", "配偶星在局中（有婚姻对象之缘）"),
        "False": ("盲派婚姻·配偶星不现（男命以财星为妻，女命以官杀为夫）", "配偶星不在局中（缘分难显）"),
    },
    # ── THEME-004 子女 ────────────────────────────────────
    "children.star": {
        "男命有财→官杀为子女星(七杀为儿/正官为女)": ("段建业《盲派八字命理口诀·子女》：有财星则以七杀为儿、正官为女", "男命以官杀为子女星（七杀主儿子、正官主女儿）"),
        "男命无财→食伤为子女星(食神为儿/伤官为女)": ("段建业《盲派八字命理口诀·子女》：无财星则以食神为儿、伤官为女", "男命以食伤为子女星（食神主儿子、伤官主女儿）"),
        "女命→食伤为子女星(食神为女/伤官为儿)": ("段建业《盲派八字命理口诀·子女》：女命以食神为女、伤官为儿", "女命以食伤为子女星（食神主女儿、伤官主儿子）"),
    },
    "children.star_present": {
        "TRUE": ("段建业《盲派八字命理口诀·子女》：以财/食伤定子女星（原文见上）", "子女星在局中"),
        "FALSE": ("段建业《盲派八字命理口诀·子女》：以财/食伤定子女星（原文见上）", "子女星不显，子女缘晚显或淡"),
    },
    "children.palace_hit": {
        "STABLE": ("段建业《盲派八字命理口诀·子女》：时柱=子女宫，忌冲忌伤忌枭印驾临（皆无=安稳）", "子女宫安稳，无冲穿枭压"),
    },
    # ── THEME-005 财帛 ────────────────────────────────────
    "wealth_event_structure.wealth_state": {
        "DIRECTED_AND_ESTABLISHED": ("盲派财富·有势又有功定是富贵翁（VERIFY-BLIND-024：财官在主位就是我的财官）+ 财现+财被取+做功成（生用结构·食伤生财/制用五种·制财）", "财星被定向取用且做功成立，求财有成"),
        "SUBSTITUTED_AND_ESTABLISHED": ("盲派换象·伤食当财/禄当财/官杀当财（VERIFY-BLIND-022：无财则伤食/禄/官杀当财看）", "财以换象方式成立（伤食/禄/官杀当财），求财方式特别"),
        "DIRECTED_PARTIAL": ("盲派财富·财被取未制净（制用五种·比劫制财；克制未净则效率不高）", "财星有取但未全成，求财有得有失"),
        "SUBSTITUTED_CANDIDATE": ("盲派换象·伤食当财候选（VERIFY-BLIND-022：八字无财，以伤食当财富看）", "财以换象候选，求财方式待定"),
        "PRESENT_UNTAKEN": ("盲派财富·有财未被取（VERIFY-BLIND-024：财官在主位才是我的财官；有财官≠有富贵）", "局中有财但未被取用，财不易到手"),
        "ABSENT_NO_SUBSTITUTION": ("盲派财富·无财亦无换象（盲派核心心法：功大者贵，无功者贱——有势无大功为平常）", "局中无财且无换象，财源薄"),
        "UNDETERMINED": ("盲派财富·证据不足（fail-closed，不做断言）", "财富判定证据不足，不做断言"),
    },
    "wealth_event_structure.wealth_present": {
        "True": ("盲派财富·财星在局（VERIFY-BLIND-024：财官在主位，就是我的财官）", "局中有财星"),
        "False": ("盲派财富·财星不现（VERIFY-BLIND-022：八字无财，以伤食/禄当财富看）", "局中财星不现，以换象论财"),
    },
    # ── THEME-006 身体疾厄 ────────────────────────────────
    "body_event_candidate.candidate": {
        "LU_UNDER_ATTACK": ("盲派口诀·禄怕见绝更怕穿害（盲派身体章：禄神被穿/合克/脆金则受损）", "禄神受攻击（被穿/合克/脆金），身体或福报易受损"),
        "YANG_REN_CLASHED": ("盲派口诀·羊刃逢冲血光之灾（盲派身体章：羊刃逢冲主血光外伤）", "羊刃逢冲，有血光/外伤风险"),
        "UNDETERMINED": ("盲派身体·证据不足（fail-closed，不做断言）", "身体判定证据不足，不做断言"),
    },
    "body_event_candidate.lu_attacked": {
        "True": ("盲派口诀·禄怕见绝更怕穿害（盲派身体章：禄神被穿/合克则受损）", "禄神状态受损（穿/冲/合克）"),
        "False": ("盲派口诀·禄怕见绝更怕穿害（盲派身体章：禄神无穿害则环境正常）", "禄神未被攻击"),
    },
    "dry_earth_brittle": {
        "NO_DRY_EARTH": ("盲派口诀·燥土脆金（VERIFY-BLIND-034《段氏理象学》：燥土不能生金反脆金；无燥土则无此患）", "无燥土脆金之患"),
        "NOT_TRIGGERED": ("盲派口诀·燥土脆金（VERIFY-BLIND-034：如四柱有水，虽见未戌之燥土亦可生金）", "燥土脆金条件未触发"),
        "TRIGGERED": ("盲派口诀·燥土脆金（VERIFY-BLIND-034：如四柱无水，见未戌之燥土定主脆金；未土脆金为最）", "燥土脆金成立，金被燥土所脆"),
    },
    # ── THEME-007 迁移出行 ────────────────────────────────
    "yima.present": {
        "NONE": ("盲派金口诀·论驿马（申子辰马在寅/寅午戌马在申/巳酉丑马在亥/亥卯未马在巳——四柱查无马星）", "命不带驿马，走动少、偏安于一地"),
    },
    "yima.trigger": {
        "NO_TRIGGER": ("盲派金口诀·驿马逢冲/合为引动（驿马主动；无引动则不动）", "驿马未被大运流年冲合引动，暂不迁移"),
    },
    # ── THEME-008 事业功名 ────────────────────────────────
    "occupation_candidate.work_types": {
        "CONTAIN_CONTROL_OFFICER_BY_FOOD_INJURY": ("制用五种·食伤制杀（段建业讲义：食伤制官杀为当官结构；VERIFY-BLIND-026：食神制煞靠技能权谋）", "含以食伤制官杀取功名，走公职/管理路线"),
        "CONTAIN_GENERATE_WEALTH_BY_FOOD_INJURY": ("生用结构·食伤生财（VERIFY-BLIND-005：食伤生财靠技艺技术）", "含以食伤生财，靠技艺/技术谋财"),
        "CONTAIN_TRANSFORM_OFFICER_BY_RESOURCE": ("化用结构·印化官杀（VERIFY-BLIND-004：用印化官杀，大多为当官的；VERIFY-BLIND-026：杀印相生靠贵人或平台）", "含以印化官杀，靠单位/文职立足"),
        "CONTAIN_STORE_BY_MUKU": ("墓用结构·墓库收物（VERIFY-BLIND-007/020：墓用=得到、控制、占据、拥有；辰库主储蓄）", "含墓库收物做功，职业与金融/仓储/管理库藏相关"),
        "CONTAIN_CONTROL_OFFICER_BY_INTERACTION": ("做功方式·冲穿制官（VERIFY-BLIND-011：刑冲克穿合墓都是做功方式）", "含以互动方式制官杀，靠手段/冲突方式得权"),
        "CONTAIN_CONTROL_WEALTH_BY_BIJIE": ("制用五种·比肩去财（VERIFY-BLIND-003：比劫制财局；比劫当财看）", "含靠朋友/伙伴/竞争制财，与人合伙谋财"),
        "CONTAIN_CONTROL_WEALTH_BY_INTERACTION": ("合制做功·制财之原神（VERIFY-BLIND-006/009：合而有制为做功；制净财之原神则财大）", "含以互动方式制财之原神（食神），财富级别大"),
        "CONTAIN_CONTROL_FOOD_INJURY_BY_RESOURCE": ("制用五种·印制食伤（VERIFY-BLIND-003：印制食伤；印=权力、食伤=财富）", "含以印印制食伤，靠约束收敛立身"),
        "CONTAIN_CONTROL_BIJIE_BY_OFFICER": ("盲派做功·官杀制比劫（段建业讲义：制用五种）", "含以官杀制比劫，靠规则/领导约束团队"),
        "CONTAIN_CONTROL_RESOURCE_BY_WEALTH": ("制用五种·财来制印（VERIFY-BLIND-003：财制印为制用之一，主掌财权）", "含以财制印做功，靠资本运作控制资源权力"),
        "CONTAIN_DRAIN_BY_FOOD_INJURY": ("盲派做功·食伤泄秀（VERIFY-BLIND-005：食伤泄秀一般不发大财）", "含以食伤泄秀立身，一般不发大财"),
    },
    "official_event_structure.official_state": {
        "CONTROLLED_AND_CLEAN": ("盲派口诀·制尽杀星得天下（《盲派中级命理学·官贵章》：官杀制净则得天下）", "官杀被制净，功名/管理有成"),
        "CONTROLLED_PARTIAL": ("盲派口诀·官杀制不净当财看（《盲派中级命理学·官贵章》：制不净则当财看；和珅为原书命例）", "官杀有制但制不净，功名/职位有限"),
        "DAMAGED": ("盲派口诀·伤官损官（制用五种·伤官去官：伤官克损官星则官场不顺）", "官星被穿损，官场/体制内不顺"),
        "ROBBED": ("盲派口诀·官星被劫财合走非我所有（《盲派中级命理学·官贵章》：官星被劫财合去则职非我有）", "官星被劫财合走，职位非我所有，难掌实权"),
        "UNCONTROLLED": ("盲派口诀·官杀无制必犯官非（VERIFY-BLIND-025：官杀旺而无制化则成了官灾）", "官杀无制，易犯官非/与官方冲突"),
        "UNDETERMINED": ("盲派官贵·证据不足（fail-closed，不做断言）", "官贵判定证据不足，不做断言"),
    },
    "work_efficiency": {
        "LARGE": ("盲派效率·功大者贵（段建业原书：有势又有功定是富贵翁——功大者贵）", "做功效率大，事业成就层次高"),
        "MEDIUM": ("盲派效率·做功效率中（制用五种：克制未净则效率中平）", "做功效率中等，事业成就有一定层次"),
        "SMALL": ("盲派效率·做功效率小（段建业原书：无功者贱——功小者平常）", "做功效率小，事业成就层次低"),
    },
    # ── THEME-009 田宅家业 ────────────────────────────────
    "zuo_gong.墓库收物": {
        "EFFECTIVE": ("盲派墓库·墓库喜冲，不冲不发（VERIFY-BLIND-020：库不开则财官无用，一冲则发）", "墓库收物成立，家业/积蓄有成"),
        "NOT_EFFECTIVE": ("盲派墓库·墓库喜冲（VERIFY-BLIND-020：库不开则财官无用）", "墓库收物未成立，家业/积蓄平平"),
        "UNDETERMINED": ("盲派墓库·证据不足（fail-closed，不做断言）", "田宅家业判定证据不足，不做断言"),
    },
    "zuo_gong.冲开墓库": {
        "冲开墓库": ("盲派墓库·墓库喜冲，不冲不发（VERIFY-BLIND-020：冲则开库，库开财官可用）", "墓库被冲开，家业/积蓄有变动之机"),
    },
    # ── THEME-010 福德精神 ────────────────────────────────
    "zuo_gong.食伤做功": {
        "EFFECTIVE": ("盲派十神口诀·日带食神自己福，一世不会受辛苦（食神主衣食口福）", "食伤做功成立，有福气、衣食无忧"),
        "NOT_EFFECTIVE": ("盲派十神口诀·日带食神自己福（食神主衣食口福；不做功则福薄）", "食伤做功未成，福气/衣食保障平平"),
    },
    "zuo_gong.印做功": {
        "EFFECTIVE": ("盲派六亲损断·印旺身强多福寿，六亲和睦家道丰", "印做功成立，主福寿、家道和睦（印旺身强多福寿）"),
        "NOT_EFFECTIVE": ("盲派六亲损断·印旺身强多福寿（印不做功则福寿庇护弱）", "印做功未成，福寿/庇护有限"),
    },
    # ── THEME-011 父母长辈 ────────────────────────────────
    "parents.father(偏财)": {
        "PRESENT": ("盲派六亲·父星=偏财（《盲派中级命理学·六亲章》：宫位比十神更准；年柱祖上父母）", "父星（偏财）在局中"),
        "ABSENT": ("盲派六亲·父星=偏财（偏财不显则父缘淡）", "父星（偏财）不显，父缘淡或助力少"),
    },
    "parents.mother(印星)": {
        "PRESENT": ("盲派六亲·母星=印星（《盲派中级命理学·六亲章》：宫位比十神更准；年柱祖上父母）", "母星（印星）在局中"),
        "ABSENT": ("盲派六亲·母星=印星（印星不显则母缘淡）", "母星（印星）不显，母缘淡或助力少"),
    },
    # ── THEME-012 才艺学业 ────────────────────────────────
    "zuo_gong.印做功(学业)": {
        "EFFECTIVE": ("段建业《盲派中级命理学》第11章：印星须做功方表学历", "印星做功成立，学业有成就"),
        "NOT_EFFECTIVE": ("段建业《盲派中级命理学》第11章：印星不做功=懒惰不好学", "印星不做功，学业动力不足"),
    },
    "zuo_gong.食伤泄秀(才艺)": {
        "EFFECTIVE": ("段建业《盲派中级命理学》第11章：食神主思想思考、主学习好", "食伤泄秀成立，主思想思考、学习（食神主学习好）"),
        "NOT_EFFECTIVE": ("段建业《盲派中级命理学》第11章：食神主思想思考（不成立则才艺平平）", "食伤泄秀不成立，思想/学习表现平平"),
    },
    "talent.direction": {
        "WEN(木火)": ("段建业《盲派中级命理学》第11章：金水主理，木火主文", "文理方向偏文（木火）"),
        "LI(金水)": ("段建业《盲派中级命理学》第11章：金水主理，木火主文", "文理方向偏理（金水）"),
        "UNDETERMINED": ("段建业《盲派中级命理学》第11章：证据不足（fail-closed，不做断言）", "文理方向判定证据不足，不做断言"),
    },
}

# ────────────────────────────────────────────────────────────
# 二、组合枚举 token：原文断言 + 现代语义（_AND_ 拆解后逐 token 翻译）
# ────────────────────────────────────────────────────────────
TOKEN_SEMANTICS: Dict[str, Dict[str, tuple]] = {
    "marriage_event_structure.palace_state": {
        "CLASHED": ("盲派婚姻·配偶宫逢冲（《盲派中级命理学·婚姻篇》：日支逢冲必离婚）", "配偶宫（日支）被冲，婚姻根基动摇"),
        "HARMED": ("盲派婚姻·配偶宫逢穿（《盲派中级命理学·婚姻篇》：配偶宫与配偶星相穿=婚姻出问题）", "配偶宫（日支）被穿，暗中受克，婚姻暗损"),
        "PUNISHED": ("盲派婚姻·配偶宫逢刑（《盲派中级命理学·婚姻篇》：配偶宫相刑=婚姻出问题）", "配偶宫（日支）被刑，夫妻易有口舌纠纷"),
        "HE_BANNED": ("盲派婚姻·配偶宫逢合绊（《段氏理象学》：六合之合，只要相邻都有合绊之意）", "配偶宫（日支）被合绊，感情易被他人牵动"),
    },
    "children.palace_hit": {
        "时支逢冲": ("段建业《盲派八字命理口诀·子女》：时柱=子女宫，忌冲", "子女宫（时支）逢冲，子女运不稳"),
        "时支逢穿": ("段建业《盲派八字命理口诀·子女》：时柱=子女宫，忌伤", "子女宫（时支）逢穿，子女运有损"),
        "枭印在时柱(克子)": ("段建业《盲派八字命理口诀·子女》：时柱忌枭印驾临，枭印在时柱克子息", "枭印临子女宫，克子息"),
        "枭印在时柱": ("段建业《盲派八字命理口诀·子女》：时柱忌枭印驾临，枭印在时柱克子息", "枭印临子女宫，克子息"),
    },
    "yima.present": {
        "SHEN马在YIN": ("盲派金口诀·论驿马：申子辰马在寅", "命带驿马（申马在寅），主走动奔波"),
        "YIN马在SHEN": ("盲派金口诀·论驿马：寅午戌马在申", "命带驿马（寅马在申），主走动奔波"),
        "ZI马在YIN": ("盲派金口诀·论驿马：申子辰马在寅", "命带驿马（子马在寅），主走动奔波"),
        "HAI马在SI": ("盲派金口诀·论驿马：亥卯未马在巳", "命带驿马（亥马在巳），主走动奔波"),
        "SI马在HAI": ("盲派金口诀·论驿马：巳酉丑马在亥", "命带驿马（巳马在亥），主走动奔波"),
        "CHOU马在HAI": ("盲派金口诀·论驿马：巳酉丑马在亥", "命带驿马（丑马在亥），主走动奔波"),
        "YOU马在HAI": ("盲派金口诀·论驿马：巳酉丑马在亥", "命带驿马（酉马在亥），主走动奔波"),
        "MAO马在SI": ("盲派金口诀·论驿马：亥卯未马在巳", "命带驿马（卯马在巳），主走动奔波"),
        "WEI马在SI": ("盲派金口诀·论驿马：亥卯未马在巳", "命带驿马（未马在巳），主走动奔波"),
        "WU马在SHEN": ("盲派金口诀·论驿马：寅午戌马在申", "命带驿马（午马在申），主走动奔波"),
        "XU马在SHEN": ("盲派金口诀·论驿马：寅午戌马在申", "命带驿马（戌马在申），主走动奔波"),
        "CHEN马在YIN": ("盲派金口诀·论驿马：申子辰马在寅", "命带驿马（辰马在寅），主走动奔波"),
    },
    "yima.trigger": {
        "驿马": ("盲派金口诀·驿马逢冲/合为引动（驿马主动，迁移奔波）", "驿马被引动，有迁移变动之机"),
    },
    "zuo_gong.冲开墓库": {
        "冲开墓库": ("盲派墓库·墓库喜冲，不冲不发（VERIFY-BLIND-020：库不开则财官无用，一冲则发）", "墓库被冲开，家业/积蓄有变动之机"),
    },
}

# ────────────────────────────────────────────────────────────
# 三、L2 事件断语：原文断言 + 现代语义（EVENT_SEMANTICS）
# ────────────────────────────────────────────────────────────
EVENT_SEMANTICS: Dict[str, tuple] = {
    "MARRIAGE_BROKEN": ("盲派口诀·配偶宫逢冲必离婚（《盲派中级命理学·婚姻篇》婚姻篇，BLIND-DJ-004）", "婚姻容易出现分离、难长久的问题"),
    "MARRIAGE_CHALLENGED": ("盲派婚姻·配偶宫受损（《盲派中级命理学·婚姻篇》：配偶宫与配偶星相穿相刑相破=婚姻出问题，BLIND-DJ-004）", "婚姻有波折，需用心经营"),
    "MARRIAGE_STABLE": ("盲派婚姻·配偶宫安稳（《盲派中级命理学·婚姻篇》：妻宫正财坐正位拱财局→婚姻好，BLIND-DJ-004）", "婚姻状态平稳"),
    "WEALTH_ESTABLISHED": ("盲派财富·有势又有功定是富贵翁（VERIFY-BLIND-024；BLIND-DJ-005/007/009）", "求财有成，财富能到手"),
    "WEALTH_CANDIDATE": ("盲派财富·财被取未全成（制用五种·克制未净则效率不高，BLIND-DJ-005/007）", "求财有得有失，财富待定"),
    "WEALTH_UNTAKEN": ("盲派财富·有财未被取（VERIFY-BLIND-024：财官在主位才是我的财官，BLIND-DJ-005）", "局中有财未取，财不易到手"),
    "WEALTH_ABSENT": ("盲派财富·无财亦无换象（段建业原书：有势无大功为平常）", "无财无换象，财源薄"),
    "OFFICIAL_ESTABLISHED": ("盲派口诀·制尽杀星得天下（《盲派中级命理学·官贵章》，BLIND-DJ-006）", "功名/管理有成，能掌权"),
    "OFFICIAL_PARTIAL": ("盲派口诀·官杀制不净当财看（和珅例，BLIND-DJ-007）", "官杀制不净当财看，功名层次有限"),
    "OFFICIAL_DAMAGED": ("盲派口诀·伤官损官（制用五种·伤官去官：伤官克损官星，BLIND-DJ-010）", "官星被损，官场/体制内不顺"),
    "OFFICIAL_ROBBED": ("盲派口诀·官星被劫财合走非我所有（《盲派中级命理学·官贵章》：官星被劫财合去，BLIND-DJ-011）", "职位非我所有，难掌实权"),
    "OFFICIAL_OFFENSE_CANDIDATE": ("盲派口诀·官杀无制必犯官非（VERIFY-BLIND-025：官杀旺而无制化则成了官灾，BLIND-DJ-001）", "官杀无制，易与官方冲突/犯官非"),
    "OCCUPATION_DIRECTION_CANDIDATE": ("盲派职业·做功类型映射职业候选（VERIFY-BLIND-026：食神制煞靠技能权谋/杀印相生靠贵人平台）", "职业方向候选（见 detail.occupation_name）"),
    "BODY_LU_ATTACK": ("盲派口诀·禄怕见绝更怕穿害（盲派身体章：禄神被穿害则受损，BLIND-DJ-002）", "禄神受攻击，身体或福报易受损"),
    "BODY_YANG_REN_CLASH": ("盲派口诀·羊刃逢冲血光之灾（盲派身体章：羊刃逢冲主血光外伤，BLIND-DJ-003）", "羊刃逢冲，有血光/外伤风险"),
    "REVERSED_PATTERN": ("盲派口诀·反局（《盲派中级命理学》第01章：反局=日柱做功所表达的意思与原局表达的意思相反，为凶；BLIND-DJ-008）", "做功方向与日主意向相反，为凶（反局）"),
}

# 时间层事件 kind → 原文断言 + 现代语义（TIME_<KIND>）
TIME_KIND_SEMANTICS: Dict[str, tuple] = {
    "CHONG": ("盲派应期·逢冲则动（VERIFY-BLIND-010：冲是做功方式之一）", "大运/流年冲引动原局，主变动"),
    "CHUAN": ("盲派应期·穿比冲更狠（盲派口诀：禄怕见绝更怕穿害；穿=背后偷袭暗中受克）", "大运/流年穿引动原局，暗中受损"),
    "SANXING": ("盲派应期·三刑引动（盲派应期章：丑未戌三刑应期）", "大运/流年刑引动原局，主口舌纠纷"),
    "FANYIN": ("盲派应期·反吟：天克地冲（VERIFY-BLIND-027）", "大运/流年反吟（天克地冲）引动原局，主剧烈变动"),
    "FUYIN": ("盲派应期·伏吟：重复引动（VERIFY-BLIND-027：伏吟主原局结构重演）", "大运/流年伏吟引动原局，主原局结构重演/加重"),
    "LIUHE": ("盲派应期·六合引动（VERIFY-BLIND-006：合是做功方式之一；合而引动主牵动）", "大运/流年合引动原局，主合绊/牵动"),
    "SANHE": ("盲派应期·三合引动（盲派应期章：三合成局制用则聚势）", "大运/流年三合引动原局，主成局/聚势"),
    "MUKU_KAI": ("盲派应期·墓库逢冲则开（VERIFY-BLIND-020：冲则开库；BLIND-DJ-005）", "大运/流年冲开墓库，主积蓄变动/库开"),
    "LU": ("盲派应期·禄神引动（盲派身体章：禄神被冲刑则受损；BLIND-DJ-002）", "大运/流年引动禄神，主身体/福报相关变动"),
    "TOUGAN": ("盲派应期·遁藏透干应期（VERIFY-BLIND-028：地支遁藏字在大运/流年天干出现=该字应期）", "大运/流年透干引动原局，主天干层面变动"),
    "ZIXING": ("盲派应期·自刑引动（盲派应期章：未戌自刑应期）", "大运/流年自刑引动原局，主自我消耗/口舌"),
    "ZIZAIXIAN": ("盲派应期·字再现引动（VERIFY-BLIND-028：原局字再现=应期）", "大运/流年原局字再现引动，主原局重现"),
}

MODERN_MISSING = "（原文/现代语义证据未取证，不做断言）"

# 组合枚举 source 清单（按 _AND_ 拆 token 翻译）
DECOMPOSE_SOURCES = {
    "marriage_event_structure.palace_state": TOKEN_SEMANTICS["marriage_event_structure.palace_state"],
    "children.palace_hit": TOKEN_SEMANTICS["children.palace_hit"],
    "yima.present": TOKEN_SEMANTICS["yima.present"],
    "yima.trigger": TOKEN_SEMANTICS["yima.trigger"],
    "zuo_gong.冲开墓库": TOKEN_SEMANTICS["zuo_gong.冲开墓库"],
}

# 主题级现代语义（综合断言模板）
THEME_SUMMARY: Dict[str, str] = {
    "THEME-001": "性情由旺衰+五行+透干十神共同决定，以下为逐项事实",
    "THEME-002": "同胞关系以比劫计数为据",
    "THEME-003": "婚姻以配偶宫（日支）+配偶星状态为据",
    "THEME-004": "子女以子女星+子女宫（时支）状态为据",
    "THEME-005": "财富以财星取用做功状态为据",
    "THEME-006": "身体以禄神/羊刃/燥土状态为据",
    "THEME-007": "迁移以驿马+引动状态为据",
    "THEME-008": "事业以做功类型+官杀制净状态为据",
    "THEME-009": "田宅家业以墓库收物状态为据",
    "THEME-010": "福德以食伤（寿）+印（福）+旺衰为据",
    "THEME-011": "父母以偏财（父）+印星（母）在局与否为据",
    "THEME-012": "才艺学业以印做功+食伤泄秀+文理方向为据",
}
THEME_SUMMARY_SOURCE: Dict[str, str] = {
    "THEME-001": "盲派十神心性",
    "THEME-002": "盲派六亲计数",
    "THEME-003": "盲派婚姻篇",
    "THEME-004": "段建业子女口诀",
    "THEME-005": "盲派财富章",
    "THEME-006": "盲派身体章",
    "THEME-007": "盲派金口诀·论驿马",
    "THEME-008": "盲派职业/官贵章",
    "THEME-009": "盲派墓库章",
    "THEME-010": "盲派十神口诀·福德",
    "THEME-011": "盲派六亲章",
    "THEME-012": "段建业《盲派中级命理学》第11章",
}


@dataclass
class InterpretationEntry:
    """单条现代语义：引擎事实 + 原文断言 + 现代语义。"""
    source: str
    value: str
    original: str = ""
    modern: str = ""

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "value": self.value,
            "original": self.original,
            "modern": self.modern,
        }


@dataclass
class BlindInterpretationResult:
    """L3 解析层结果：解层断语全集 → 原文断言 + 现代语义。"""
    themes: List[Dict] = field(default_factory=list)
    method_scope: str = METHOD_SCOPE
    status: str = "ESTABLISHED"  # ESTABLISHED / PARTIAL / UNDETERMINED

    def to_dict(self) -> dict:
        return {
            "themes": self.themes,
            "method_scope": self.method_scope,
            "status": self.status,
        }


def _norm_value(v) -> str:
    """把 value 规范成查表键（CONTAIN_ 前缀用于 work_types 列表匹配）。"""
    if isinstance(v, list):
        joined = "|".join(str(x) for x in v)
        for key in ("CONTROL_OFFICER_BY_FOOD_INJURY", "GENERATE_WEALTH_BY_FOOD_INJURY",
                    "TRANSFORM_OFFICER_BY_RESOURCE", "STORE_BY_MUKU",
                    "CONTROL_OFFICER_BY_INTERACTION", "CONTROL_WEALTH_BY_BIJIE",
                    "CONTROL_WEALTH_BY_INTERACTION", "CONTROL_FOOD_INJURY_BY_RESOURCE",
                    "CONTROL_BIJIE_BY_OFFICER", "CONTROL_RESOURCE_BY_WEALTH",
                    "DRAIN_BY_FOOD_INJURY"):
            if key in joined:
                return "CONTAIN_" + key
        return joined[:80]
    if isinstance(v, dict):
        # 透干十神 dict：{"year": "偏财", ...} → 规范成 TEN_GOD_TRANSPARENT（逐项由展开逻辑处理）
        return "TEN_GOD_TRANSPARENT"
    if isinstance(v, str) and v[:1] in ("{", "["):
        # 兼容 Python repr（单引号）形式的 list/dict 字符串
        try:
            parsed = ast.literal_eval(v)
            if isinstance(parsed, (list, dict)):
                return _norm_value(parsed)
        except Exception:
            pass
    return str(v).upper() if isinstance(v, bool) else str(v)


def _lookup(source: str, value: str) -> Optional[tuple]:
    """查非组合枚举表；无则 None。"""
    table = VALUE_SEMANTICS.get(source)
    if not table:
        return None
    hit = table.get(value)
    if hit is not None:
        return hit
    # 大小写归一重试
    for k, v in table.items():
        if k.lower() == str(value).lower():
            return v
    return None


def _lookup_decompose(source: str, value: str) -> List[tuple]:
    """组合枚举：_AND_ 拆 token 逐条翻译（无 token 的完整值走 VALUE_SEMANTICS）。"""
    table = DECOMPOSE_SOURCES.get(source)
    if not table:
        return []
    toks = value.split("_AND_") if "_AND_" in value else ([value] if value not in VALUE_SEMANTICS.get(source, {}) else [])
    out = []
    for tok in toks:
        # yima.trigger 动态格式：驿马<支>逢冲(<来源>) / 逢合(<来源>)
        if source == "yima.trigger":
            if "逢冲" in tok or "逢合" in tok:
                out.append(("盲派金口诀·驿马逢冲/合为引动（驿马主动，迁移奔波；逢冲=野马脱缰必远行）", "驿马被引动，有迁移变动之机"))
                continue
            hit = table.get(tok)
            if hit:
                out.append(hit)
            continue
        hit = table.get(tok)
        if hit:
            out.append(hit)
    return out


def interpret_blind(theme_result, judgment_result=None, blind_result=None) -> BlindInterpretationResult:
    """L3 解析：消费 L2.5 主题聚合，输出 原文断言+现代语义 成对条目。"""
    themes_in = getattr(theme_result, "themes", None)
    if themes_in is None:
        themes_in = (theme_result or {}).get("themes", []) if isinstance(theme_result, dict) else []

    out_themes = []
    any_modern = False
    for t in themes_in:
        theme_id = t.get("theme_id", "") if isinstance(t, dict) else getattr(t, "theme_id", "")
        theme_name = t.get("theme_name", "") if isinstance(t, dict) else getattr(t, "theme_name", "")
        state = t.get("state", "UNDETERMINED") if isinstance(t, dict) else getattr(t, "state", "UNDETERMINED")
        entries = t.get("entries", []) if isinstance(t, dict) else getattr(t, "entries", [])

        entry_out = []
        for e in entries:
            src = e.get("source", "") if isinstance(e, dict) else getattr(e, "source", "")
            val_raw = e.get("value", "") if isinstance(e, dict) else getattr(e, "value", "")
            # value 可能是 JSON 字符串化的 dict/list（如 '{"year": "偏财"}'），先还原
            val = val_raw
            if isinstance(val_raw, str) and val_raw[:1] in ("{", "["):
                try:
                    val = json.loads(val_raw)
                except Exception:
                    val = val_raw
            # children.palace_hit 的 "(克子)" 后缀归一（避免同义枚举分叉）
            norm_val = _norm_value(val)
            if src == "children.palace_hit":
                norm_val = norm_val.replace("(克子)", "")

            # work_types 列表 → 逐项现代语义（职业做功类型全映射）
            if src == "occupation_candidate.work_types" and isinstance(val, list):
                WT_MAP = {
                    "CONTROL_OFFICER_BY_FOOD_INJURY": ("制用五种·食伤制杀（段建业讲义：食伤制官杀为当官结构；VERIFY-BLIND-026：食神制煞靠技能权谋）", "以食伤制官杀取功名，走公职/管理路线"),
                    "CONTROL_OFFICER_BY_INTERACTION": ("做功方式·冲穿制官（VERIFY-BLIND-011：刑冲克穿合墓都是做功方式）", "以刑穿冲等互动方式制官杀，靠手段/冲突方式得权"),
                    "CONTROL_WEALTH_BY_BIJIE": ("制用五种·比肩去财（VERIFY-BLIND-003：比劫制财局；比劫当财看）", "靠朋友/伙伴/竞争制财，与人合伙谋财"),
                    "CONTROL_WEALTH_BY_INTERACTION": ("合制做功·制财之原神（VERIFY-BLIND-006/009：合而有制为做功；制净财之原神则财大）", "以互动方式制财之原神（食神），财富级别大"),
                    "CONTROL_FOOD_INJURY_BY_RESOURCE": ("制用五种·印制食伤（VERIFY-BLIND-003：印制食伤；印=权力、食伤=财富）", "以印印制食伤，靠约束收敛立身"),
                    "CONTROL_BIJIE_BY_OFFICER": ("盲派做功·官杀制比劫（段建业讲义：制用五种）", "以官杀制比劫，靠规则/领导约束团队"),
                    "CONTROL_RESOURCE_BY_WEALTH": ("制用五种·财来制印（VERIFY-BLIND-003：财制印为制用之一，主掌财权）", "以财制印做功，靠资本运作控制资源权力"),
                    "GENERATE_WEALTH_BY_FOOD_INJURY": ("生用结构·食伤生财（VERIFY-BLIND-005：食伤生财靠技艺技术）", "以食伤生财，靠技艺/技术谋财"),
                    "TRANSFORM_OFFICER_BY_RESOURCE": ("化用结构·印化官杀（VERIFY-BLIND-004：用印化官杀，大多为当官的；VERIFY-BLIND-026：杀印相生靠贵人或平台）", "以印化官杀，靠单位/文职立足"),
                    "STORE_BY_MUKU": ("墓用结构·墓库收物（VERIFY-BLIND-007/020：墓用=得到、控制、占据、拥有；辰库主储蓄）", "以墓库收物蓄财，走金融/仓储类"),
                    "DRAIN_BY_FOOD_INJURY": ("盲派做功·食伤泄秀（VERIFY-BLIND-005：食伤泄秀一般不发大财）", "以食伤泄秀立身，一般不发大财"),
                }
                for wt in val:
                    wt_hit = WT_MAP.get(wt)
                    if wt_hit:
                        entry_out.append(InterpretationEntry(
                            source=f"occupation_candidate.work_type.{wt}",
                            value=wt,
                            original=wt_hit[0],
                            modern=f"做功类型 {wt}：{wt_hit[1]}",
                        ).to_dict())
                        any_modern = True
                continue

            # 透干十神 dict → 逐项十神性情展开（原文=盲派十神心性）
            if isinstance(val, dict):
                for k2, v2 in val.items():
                    tg_hit = TEN_GOD_TEMPER.get(str(v2))
                    if tg_hit:
                        entry_out.append(InterpretationEntry(
                            source=f"transparent_ten_gods.{k2}",
                            value=str(v2),
                            original=tg_hit[0],
                            modern=f"透干{v2}：{tg_hit[1]}",
                        ).to_dict())
                        any_modern = True
                continue

            # 组合枚举（_AND_ token 拆解）
            decomp = _lookup_decompose(src, str(val))
            if decomp:
                for orig, mod in decomp:
                    entry_out.append(InterpretationEntry(
                        source=src, value=str(val),
                        original=orig, modern=mod,
                    ).to_dict())
                    any_modern = True
                continue

            # 非组合枚举
            hit = _lookup(src, str(val)) if isinstance(val, (str, bool)) else None
            # 数字计数通配
            if hit is None and src in ("kinship_count.brother_count", "kinship_count.sister_count"):
                label = "兄弟" if src.endswith("brother_count") else "姐妹"
                if str(val) in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
                    hit = ("盲派六亲计数·比肩为兄弟/劫财为姐妹", f"同胞中{label} {val} 人")
            if hit is None:
                hit = ("（未收录）", MODERN_MISSING)
            entry_out.append(InterpretationEntry(
                source=src, value=str(val),
                original=hit[0], modern=hit[1],
            ).to_dict())
            if hit[1] != MODERN_MISSING:
                any_modern = True

        out_themes.append({
            "theme_id": theme_id,
            "theme_name": theme_name,
            "state": state,
            "modern_summary_source": THEME_SUMMARY_SOURCE.get(theme_id, "（未定义）"),
            "modern_summary": THEME_SUMMARY.get(theme_id, ""),
            "entries": entry_out,
        })

    status = "ESTABLISHED" if any_modern else "UNDETERMINED"
    return BlindInterpretationResult(themes=out_themes, status=status)


def interpret_blind_events(judgment_result, theme_result=None) -> List[Dict]:
    """L2 事件断语 → 原文断言 + 现代语义。"""
    evts = getattr(judgment_result, "event_candidates", None)
    if evts is None:
        evts = (judgment_result or {}).get("event_candidates", []) if isinstance(judgment_result, dict) else []

    out = []
    for ev in evts:
        et = ev.get("event_type", "") if isinstance(ev, dict) else getattr(ev, "event_type", "")
        dom = ev.get("domain", "") if isinstance(ev, dict) else getattr(ev, "domain", "")
        direction = ev.get("direction", "") if isinstance(ev, dict) else getattr(ev, "direction", "")
        structure = ev.get("structure_ref", "") if isinstance(ev, dict) else getattr(ev, "structure_ref", "")
        evidence = ev.get("evidence_refs", []) if isinstance(ev, dict) else getattr(ev, "evidence_refs", [])
        detail = ev.get("detail", {}) if isinstance(ev, dict) else getattr(ev, "detail", {})
        # TIME_<KIND> 按 kind 查表
        if et.startswith("TIME_"):
            kind = et[len("TIME_"):]
            hit = TIME_KIND_SEMANTICS.get(kind)
            if hit is None:
                hit = ("（未收录）", MODERN_MISSING)
        else:
            hit = EVENT_SEMANTICS.get(et)
            if hit is None:
                hit = ("（未收录）", MODERN_MISSING)
        out.append({
            "domain": dom,
            "event_type": et,
            "direction": direction,
            "original": hit[0],
            "modern": hit[1],
            "structure_ref": structure,
            "evidence_refs": evidence,
            "detail": detail,
        })
    return out


# ────────────────────────────────────────────────────────────
# 四、解层断语全集审计：按代码枚举空间校验注册表覆盖
# ────────────────────────────────────────────────────────────
ENUM_SPACE = {
    "blind_wangshuai": ["WANG_JI", "TAI_RUO", "WANG", "ZHONG_HE_PIAN_RUO", "RUO", "UNDETERMINED"],
    "five_element_imbalance": ["TRUE", "FALSE"],
    "zuo_gong.比劫做功": ["EFFECTIVE", "NOT_EFFECTIVE"],
    "marriage_event_structure.marriage_state": ["BROKEN", "CHALLENGED", "HARMONIOUS", "UNDETERMINED"],
    "marriage_event_structure.palace_state": ["STABLE", "CLASHED", "HARMED", "PUNISHED", "HE_BANNED",
                                               "CLASHED_AND_HARMED", "CLASHED_AND_PUNISHED", "CLASHED_AND_HE_BANNED",
                                               "HARMED_AND_PUNISHED", "HARMED_AND_HE_BANNED", "PUNISHED_AND_HE_BANNED",
                                               "CLASHED_AND_HARMED_AND_PUNISHED", "CLASHED_AND_HARMED_AND_HE_BANNED",
                                               "CLASHED_AND_PUNISHED_AND_HE_BANNED", "HARMED_AND_PUNISHED_AND_HE_BANNED",
                                               "CLASHED_AND_HARMED_AND_PUNISHED_AND_HE_BANNED"],
    "marriage_event_structure.spouse_star_present": ["True", "False"],
    "children.star": ["男命有财→官杀为子女星(七杀为儿/正官为女)",
                      "男命无财→食伤为子女星(食神为儿/伤官为女)",
                      "女命→食伤为子女星(食神为女/伤官为儿)"],
    "children.star_present": ["TRUE", "FALSE"],
    "children.palace_hit": ["STABLE", "时支逢冲", "时支逢穿", "枭印在时柱(克子)",
                            "时支逢冲_AND_枭印在时柱", "时支逢穿_AND_枭印在时柱"],
    "wealth_event_structure.wealth_state": ["DIRECTED_AND_ESTABLISHED", "SUBSTITUTED_AND_ESTABLISHED",
                                            "DIRECTED_PARTIAL", "SUBSTITUTED_CANDIDATE",
                                            "PRESENT_UNTAKEN", "ABSENT_NO_SUBSTITUTION", "UNDETERMINED"],
    "wealth_event_structure.wealth_present": ["True", "False"],
    "body_event_candidate.candidate": ["LU_UNDER_ATTACK", "YANG_REN_CLASHED", "UNDETERMINED"],
    "body_event_candidate.lu_attacked": ["True", "False"],
    "dry_earth_brittle": ["NO_DRY_EARTH", "NOT_TRIGGERED", "TRIGGERED"],
    "yima.present": ["NONE", "SHEN马在YIN", "YIN马在SHEN", "CHOU马在HAI", "HAI马在SI", "SI马在HAI",
                     "SHEN马在YIN_AND_YIN马在SHEN", "CHOU马在HAI_AND_YOU马在HAI", "HAI马在SI_AND_SI马在HAI"],
    "yima.trigger": ["NO_TRIGGER", "驿马SHEN逢冲(大运)", "驿马YIN逢合(流年)", "驿马SHEN逢冲(大运)_AND_驿马YIN逢合(流年)"],
    "official_event_structure.official_state": ["CONTROLLED_AND_CLEAN", "CONTROLLED_PARTIAL",
                                                "DAMAGED", "ROBBED", "UNCONTROLLED", "UNDETERMINED"],
    "work_efficiency": ["LARGE", "MEDIUM", "SMALL"],
    "zuo_gong.墓库收物": ["EFFECTIVE", "NOT_EFFECTIVE", "UNDETERMINED"],
    "zuo_gong.冲开墓库": ["冲开墓库"],
    "zuo_gong.食伤做功": ["EFFECTIVE", "NOT_EFFECTIVE"],
    "zuo_gong.印做功": ["EFFECTIVE", "NOT_EFFECTIVE"],
    "parents.father(偏财)": ["PRESENT", "ABSENT"],
    "parents.mother(印星)": ["PRESENT", "ABSENT"],
    "zuo_gong.印做功(学业)": ["EFFECTIVE", "NOT_EFFECTIVE"],
    "zuo_gong.食伤泄秀(才艺)": ["EFFECTIVE", "NOT_EFFECTIVE"],
    "talent.direction": ["WEN(木火)", "LI(金水)", "UNDETERMINED"],
}

EVENT_SPACE = ["MARRIAGE_BROKEN", "MARRIAGE_CHALLENGED", "MARRIAGE_STABLE",
               "WEALTH_ESTABLISHED", "WEALTH_CANDIDATE", "WEALTH_UNTAKEN", "WEALTH_ABSENT",
               "OFFICIAL_ESTABLISHED", "OFFICIAL_PARTIAL", "OFFICIAL_DAMAGED", "OFFICIAL_ROBBED",
               "OFFICIAL_OFFENSE_CANDIDATE", "OCCUPATION_DIRECTION_CANDIDATE",
               "BODY_LU_ATTACK", "BODY_YANG_REN_CLASH", "REVERSED_PATTERN"]
TIME_KIND_SPACE = ["CHONG", "CHUAN", "SANXING", "FANYIN", "FUYIN", "LIUHE", "SANHE",
                   "MUKU_KAI", "LU", "TOUGAN", "ZIXING", "ZIZAIXIAN"]


def audit_assertion_provenance() -> Dict:
    """断言层出处审计：每条 original 必须含可追溯出处标记，禁止'章节名当原文'。

    规则：
    - 出处标记 = 书名（《》）/ 篇名（盲派X章/金口诀/铁断）/ VERIFY 号（VERIFY-BLIND-NNN）
      / 讲义（段建业讲义）/ 心法（段建业原书核心心法）/ 原书（段氏理象学等）之一。
    - 盲派引擎全域（含注释）禁止出现任何验证样本引用：验证样本仅存在于引擎外验证（tests/），
    - 不是引擎规则依据；断言出处只允许古籍/口诀/VERIFY 号/段建业原书。
    - 已取证的断言（original 含出处标记）计入 provenance_ok。
    - 未取证断言（含'未取证'/'证据不足'/'fail-closed'/'原文见上'/'非盲派专属'）计入 deferred_ok，
      这类是明确声明无原文的兜底，允许存在但必须显式声明。
    - 两者皆非 = provenance_missing（断言既无出处又未声明未取证）→ 审计失败。
    """
    marks = ["《", "盲派", "段建业", "VERIFY", "讲义", "心法", "铁断", "金口诀",
             "渊海子平", "理象学", "命理玄机探秘", "段氏"]
    deferred_marks = ["未取证", "证据不足", "fail-closed", "原文见上", "非盲派专属", "排盘层"]
    bad = []
    n_ok = n_def = 0
    def check(name, tbl):
        nonlocal n_ok, n_def
        items = []
        if isinstance(tbl, dict):
            for k, v in tbl.items():
                if isinstance(v, dict):
                    for k2, (orig, mod) in v.items():
                        items.append((f"{name}.{k2}", orig))
                else:
                    items.append((f"{name}.{k}", v[0]))
        else:
            items.append((name, tbl[0]))
        for key, orig in items:
            if any(m in orig for m in deferred_marks):
                n_def += 1
            elif any(m in orig for m in marks):
                n_ok += 1
            else:
                bad.append((key, orig))
    for src_name, tbl in VALUE_SEMANTICS.items():
        check(f"VALUE.{src_name}", tbl)
    for src_name, tbl in TOKEN_SEMANTICS.items():
        check(f"TOKEN.{src_name}", tbl)
    check("EVENT", EVENT_SEMANTICS)
    check("TIME", TIME_KIND_SEMANTICS)
    check("TEN_GOD", TEN_GOD_TEMPER)
    return {
        "provenance_ok": n_ok,
        "deferred_ok": n_def,
        "provenance_missing": bad,
        "status": "PASS" if not bad else "FAIL",
    }


def audit_modern_fidelity() -> Dict:
    """现代语义忠实度审计：modern 必须覆盖 original 核心概念，禁错位/缩水/夹带。

    - REQUIRE：登记原文字眼 → modern 必须出现（如"制财之原神"→"原神"、"当财看"→"当财"）。
    - FORBIDDEN：modern 禁出现子平用神语义（盲派弃旺衰废用忌）与口语自创词。
    - fail-closed 条目（原文含 证据不足/未取证/fail-closed/非盲派专属/排盘层）自动放行。
    """
    REQUIRE = {
        "CONTAIN_CONTROL_WEALTH_BY_INTERACTION": ["原神"],
        "CONTAIN_DRAIN_BY_FOOD_INJURY": ["大财"],
        "OFFICIAL_PARTIAL": ["当财"],
        "zuo_gong.印做功": ["福寿"],
        "zuo_gong.印做功(学业)": [],
        "zuo_gong.食伤泄秀(才艺)": ["学习", "思想"],
        "blind_wangshuai": ["旺", "弱", "极"],
    }
    FORBIDDEN = ["扛得住", "借外力", "借财官之力", "宜顺势", "越努力越背", "突破条条框框"]
    bad = []
    n_ok = 0
    def check(key, orig, mod):
        nonlocal n_ok
        if any(m in orig for m in ("证据不足", "未取证", "fail-closed", "非盲派专属", "排盘层")):
            return
        matched = None
        for src_name, keys in REQUIRE.items():
            if src_name in key and (matched is None or len(src_name) > len(matched[0])):
                matched = (src_name, keys)
        if matched is not None:
            keys = matched[1]
            if keys and not any(k in mod for k in keys):
                bad.append((key, "缺核心词", orig[:36], mod))
        for f in FORBIDDEN:
            if f in mod:
                bad.append((key, "夹带禁用词", orig[:36], mod))
                break
        else:
            n_ok += 1
    for src_name, tbl in VALUE_SEMANTICS.items():
        for k, v in tbl.items():
            check(f"{src_name}.{k}", v[0], v[1])
    for src_name, tbl in TOKEN_SEMANTICS.items():
        for k, v in tbl.items():
            check(f"{src_name}.{k}", v[0], v[1])
    for k, v in EVENT_SEMANTICS.items():
        check(f"EVENT.{k}", v[0], v[1])
    for k, v in TIME_KIND_SEMANTICS.items():
        check(f"TIME.{k}", v[0], v[1])
    return {
        "checked": n_ok + len(bad),
        "fidelity_ok": n_ok,
        "fidelity_bad": bad,
        "status": "PASS" if not bad else "FAIL",
    }


def audit_full_coverage() -> Dict:
    """全集审计：枚举空间逐项校验，返回未覆盖清单（None=全覆盖）。"""
    missing = []
    for source, values in ENUM_SPACE.items():
        table = VALUE_SEMANTICS.get(source)
        decomp = DECOMPOSE_SOURCES.get(source)
        for v in values:
            if decomp is not None and ("_AND_" in v or v in decomp):
                if "_AND_" in v:
                    toks = v.split("_AND_")
                    bad = [t for t in toks if t not in decomp and not (source == "yima.trigger" and ("逢冲" in t or "逢合" in t))]
                    if bad:
                        missing.append((source, v, "组合token缺"))
                else:
                    if v not in decomp and (table is None or v not in table):
                        missing.append((source, v, "完整值缺"))
                continue
            # yima.trigger 动态格式按前缀/包含匹配
            if source == "yima.trigger" and ("逢冲" in v or "逢合" in v):
                continue
            if table is None or v not in table:
                missing.append((source, v, "枚举缺"))
    for et in EVENT_SPACE:
        if et not in EVENT_SEMANTICS:
            missing.append(("EVENT", et, "事件缺"))
    for k in TIME_KIND_SPACE:
        if k not in TIME_KIND_SEMANTICS:
            missing.append(("TIME", k, "时间层缺"))
    return {
        "total_enums": sum(len(v) for v in ENUM_SPACE.values()) + len(EVENT_SPACE) + len(TIME_KIND_SPACE),
        "missing": missing,
        "coverage": "FULL" if not missing else "PARTIAL",
    }
