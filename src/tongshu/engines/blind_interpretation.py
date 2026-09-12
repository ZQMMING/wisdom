# -*- coding: utf-8 -*-
"""L3 解析层（Interpretation Layer）：盲派解层断语全集 → 原文断言 + 现代语义。

输入：L2.5 BlindThemeResult（12 主题聚合） + L2 BlindJudgmentResult（事件候选）
输出：每条解层断语 = { 原文断言(original) + 现代语义(modern) + 引擎事实(value) }。

铁律：
- 解层断语全集注册表（VALUE_SEMANTICS / TOKEN_SEMANTICS / EVENT_SEMANTICS /
  TIME_KIND_SEMANTICS）按**代码枚举空间全覆盖**——不是按案例覆盖。
- 组合枚举（palace_state / children.palace_hit / yima.present / yima.trigger /
  冲开墓库）按 "_AND_" 拆 token，逐 token 翻译拼接；STABLE/NONE/NO_TRIGGER 是
  无 token 的完整值，走 VALUE_SEMANTICS。
- 每个现代语义句子必须由注册表固定模板生成：零 LLM、零自由发挥、零评分。
- 每条映射必须带原文断言（盲派口诀/案例原文）。注册表未覆盖 = MODERN_MISSING
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

# 十神透干 → 性情（原文：盲派十神心性/渊海子平十神赋）
TEN_GOD_TEMPER = {
    "偏财": ("十神心性·偏财：慷慨大方，重实际，善经营", "为人慷慨大方，注重实际利益，善于经营谋划"),
    "正财": ("十神心性·正财：勤俭踏实，守本分", "为人勤俭踏实，守本分，重视稳定收入"),
    "七杀": ("十神心性·七杀：果断威权，性急多疑", "做事果断有魄力，性急，疑心较重"),
    "正官": ("十神心性·正官：循规蹈矩，重名誉", "守规矩讲原则，重视名誉，责任心强"),
    "食神": ("十神心性·食神：温和厚道，主福气", "性情温和厚道，有口福，福气较好"),
    "伤官": ("十神心性·伤官：聪明外露，不服管", "聪明外露，才华张扬，不愿受管束"),
    "偏印": ("十神心性·偏印：多思善谋，孤僻", "心思多、善谋略，性格偏孤僻"),
    "正印": ("十神心性·正印：仁慈稳重，重学识", "仁慈稳重，重视学问名声"),
    "比肩": ("十神心性·比肩：自立自强，不服输", "自立心强，不服输，靠自己"),
    "劫财": ("十神心性·劫财：豪爽冲动，好竞争", "为人豪爽但易冲动，好胜心强"),
}

VALUE_SEMANTICS: Dict[str, Dict[str, tuple]] = {
    # ── THEME-001 性情禀赋 ────────────────────────────────
    "blind_wangshuai": {
        "WANG_JI": ("盲派旺衰·旺极：旺极无制则反", "日主旺极，气势一面倒，宜顺势不可逆"),
        "TAI_RUO": ("盲派旺衰·太弱：弱极则从", "日主太弱，难以自立，宜从势而行"),
        "WANG": ("盲派四定律·身旺以官杀（含纳音）", "日主自身力量旺，扛得住财官，做事有底气"),
        "ZHONG_HE_PIAN_RUO": ("盲派旺衰·中和偏弱", "日主中和偏弱，做事需借财官之力，不宜硬扛"),
        "RUO": ("盲派四定律·身弱以财官（含纳音）", "日主自身力量偏弱，做事易受牵制，需借外力"),
        "UNDETERMINED": ("盲派旺衰定律", "旺衰判定证据不足，不做断言"),
    },
    "five_element_imbalance": {
        "TRUE": ("五行失衡（排盘层五行统计）", "五行分布不均，性情有偏向，某方面特质突出"),
        "FALSE": ("五行失衡（排盘层五行统计）", "五行相对均衡，性情较平和"),
    },
    # ── THEME-002 交游人际 ────────────────────────────────
    "zuo_gong.比劫做功": {
        "EFFECTIVE": ("盲派做功·比劫制财/比劫成党", "比劫做功有效，人际靠朋友/伙伴，竞争性强"),
        "NOT_EFFECTIVE": ("盲派做功·比劫制财", "比劫做功未成，朋友助力有限"),
    },
    # ── THEME-003 婚姻配偶 ────────────────────────────────
    "marriage_event_structure.palace_state": {
        "STABLE": ("盲派婚姻篇·配偶宫安稳", "配偶宫安稳，婚姻基础好"),
    },
    "marriage_event_structure.marriage_state": {
        "BROKEN": ("盲派婚姻篇·配偶宫逢冲必离婚/配偶宫破星损", "婚姻上容易出现分离、难长久的问题"),
        "CHALLENGED": ("盲派婚姻篇·配偶宫受损", "婚姻上容易有波折，需经营"),
        "HARMONIOUS": ("盲派婚姻篇·配偶宫稳定", "婚姻状态平稳，配偶宫无破"),
        "UNDETERMINED": ("盲派婚姻篇", "婚姻判定证据不足，不做断言"),
    },
    "marriage_event_structure.spouse_star_present": {
        "True": ("盲派婚姻篇·配偶星", "配偶星在局中（有婚姻对象之缘）"),
        "False": ("盲派婚姻篇·配偶星", "配偶星不在局中（缘分难显）"),
    },
    # ── THEME-004 子女 ────────────────────────────────────
    "children.star": {
        "男命有财→官杀为子女星(七杀为儿/正官为女)": ("段建业《盲派八字命理口诀·子女》：有财星则以七杀为儿、正官为女", "男命以官杀为子女星（七杀主儿子、正官主女儿）"),
        "男命无财→食伤为子女星(食神为儿/伤官为女)": ("段建业《盲派八字命理口诀·子女》：无财星则以食神为儿、伤官为女", "男命以食伤为子女星（食神主儿子、伤官主女儿）"),
        "女命→食伤为子女星(食神为女/伤官为儿)": ("段建业《盲派八字命理口诀·子女》：女命以食神为女、伤官为儿", "女命以食伤为子女星（食神主女儿、伤官主儿子）"),
    },
    "children.star_present": {
        "TRUE": ("段建业《盲派八字命理口诀·子女》", "子女星在局中"),
        "FALSE": ("段建业《盲派八字命理口诀·子女》", "子女星不显，子女缘晚显或淡"),
    },
    "children.palace_hit": {
        "STABLE": ("段建业《盲派八字命理口诀·子女》", "子女宫安稳，无冲穿枭压"),
    },
    # ── THEME-005 财帛 ────────────────────────────────────
    "wealth_event_structure.wealth_state": {
        "DIRECTED_AND_ESTABLISHED": ("盲派财富章·财现+财被取+做功成（案例集：食伤生财/制财做功）", "财星被定向取用且做功成立，求财有成"),
        "SUBSTITUTED_AND_ESTABLISHED": ("盲派换象·伤食当财/禄当财/官杀当财（VERIFY-BLIND-022）", "财以换象方式成立（伤食/禄/官杀当财），求财方式特别"),
        "DIRECTED_PARTIAL": ("盲派财富章·财被取但未制净", "财星有取但未全成，求财有得有失"),
        "SUBSTITUTED_CANDIDATE": ("盲派换象·伤食当财候选", "财以换象候选，求财方式待定"),
        "PRESENT_UNTAKEN": ("盲派财富章·有财未被取", "局中有财但未被取用，财不易到手"),
        "ABSENT_NO_SUBSTITUTION": ("盲派财富章·无财亦无换象", "局中无财且无换象，财源薄"),
        "UNDETERMINED": ("盲派财富章", "财富判定证据不足，不做断言"),
    },
    "wealth_event_structure.wealth_present": {
        "True": ("盲派财富章·财星在局", "局中有财星"),
        "False": ("盲派财富章·财星不现", "局中财星不现，以换象论财"),
    },
    # ── THEME-006 身体疾厄 ────────────────────────────────
    "body_event_candidate.candidate": {
        "LU_UNDER_ATTACK": ("盲派口诀·禄怕见绝更怕穿害（案例集戊申己未庚申辛巳交通意外）", "禄神受攻击（被穿/合克/脆金），身体或福报易受损"),
        "YANG_REN_CLASHED": ("盲派口诀·羊刃逢冲血光之灾（庚午辛未壬申癸酉）", "羊刃逢冲，有血光/外伤风险"),
        "UNDETERMINED": ("盲派身体章", "身体判定证据不足，不做断言"),
    },
    "body_event_candidate.lu_attacked": {
        "True": ("盲派口诀·禄怕见绝更怕穿害", "禄神状态受损（穿/冲/合克）"),
        "False": ("盲派口诀·禄怕见绝更怕穿害", "禄神未被攻击"),
    },
    "dry_earth_brittle": {
        "NO_DRY_EARTH": ("盲派口诀·燥土脆金（VERIFY-BLIND-034）", "无燥土脆金之患"),
        "NOT_TRIGGERED": ("盲派口诀·燥土脆金（VERIFY-BLIND-034）", "燥土脆金条件未触发"),
        "TRIGGERED": ("盲派口诀·燥土脆金（VERIFY-BLIND-034）", "燥土脆金成立，金被燥土所脆"),
    },
    # ── THEME-007 迁移出行 ────────────────────────────────
    "yima.present": {
        "NONE": ("盲派金口诀·论驿马", "命不带驿马，走动少、偏安于一地"),
    },
    "yima.trigger": {
        "NO_TRIGGER": ("盲派金口诀·驿马引动", "驿马未被大运流年冲合引动，暂不迁移"),
    },
    # ── THEME-008 事业功名 ────────────────────────────────
    "occupation_candidate.work_types": {
        "CONTAIN_CONTROL_OFFICER_BY_FOOD_INJURY": ("案例12：伤食制官局，命有官职", "含以食伤制官杀取功名，走公职/管理路线"),
        "CONTAIN_GENERATE_WEALTH_BY_FOOD_INJURY": ("案例46：食伤做功技术赚", "含以食伤生财，靠技艺/技术谋财"),
        "CONTAIN_TRANSFORM_OFFICER_BY_RESOURCE": ("案例23：印主单位", "含以印化官杀，靠单位/文职立足"),
        "CONTAIN_STORE_BY_MUKU": ("盲派墓库·辰库收水（案例1：银行金融中心）", "含墓库收物做功，职业与金融/仓储/管理库藏相关"),
        "CONTAIN_CONTROL_OFFICER_BY_INTERACTION": ("盲派互动制官·刑/穿/冲制官杀（案例取证）", "含以互动方式制官杀，靠手段/冲突方式得权"),
        "CONTAIN_CONTROL_WEALTH_BY_BIJIE": ("盲派做功·比劫制财", "含靠朋友/伙伴/竞争制财，与人合伙谋财"),
        "CONTAIN_CONTROL_WEALTH_BY_INTERACTION": ("盲派互动制财·刑穿冲制财", "含以互动方式（刑穿冲）制财，财来自竞争博弈"),
        "CONTAIN_CONTROL_FOOD_INJURY_BY_RESOURCE": ("盲派做功·印制食伤", "含以印印制食伤，靠约束收敛立身"),
        "CONTAIN_CONTROL_BIJIE_BY_OFFICER": ("盲派做功·官杀制比劫", "含以官杀制比劫，靠规则/领导约束团队"),
        "CONTAIN_CONTROL_RESOURCE_BY_WEALTH": ("盲派做功·财制印", "含以财坏印，靠现实利益突破条条框框"),
        "CONTAIN_DRAIN_BY_FOOD_INJURY": ("盲派做功·食伤泄秀", "含以食伤泄秀，靠才华表达立身"),
    },
    "official_event_structure.official_state": {
        "CONTROLLED_AND_CLEAN": ("盲派口诀·制尽杀星得天下（乾隆 金水伤官制净）", "官杀被制净，功名/管理有成"),
        "CONTROLLED_PARTIAL": ("盲派口诀·官杀制不净（D29 车间主任）", "官杀有制但制不净，功名/职位有限"),
        "DAMAGED": ("盲派口诀·穿官损官，官根受损（案例2 官场梦碎）", "官星被穿损，官场/体制内不顺"),
        "ROBBED": ("盲派口诀·官星被劫财合走，非我所有（案例8 仓库保管员）", "官星被劫财合走，职位非我所有，难掌实权"),
        "UNCONTROLLED": ("盲派口诀·官杀无制必犯官非（庚午辛未壬申癸酉）", "官杀无制，易犯官非/与官方冲突"),
        "UNDETERMINED": ("盲派官贵章", "官贵判定证据不足，不做断言"),
    },
    "work_efficiency": {
        "LARGE": ("盲派效率·做功效率大（功大者贵）", "做功效率大，事业成就层次高"),
        "MEDIUM": ("盲派效率·做功效率中", "做功效率中等，事业成就有一定层次"),
        "SMALL": ("盲派效率·做功效率小（功小者贱/平常）", "做功效率小，事业成就层次低"),
    },
    # ── THEME-009 田宅家业 ────────────────────────────────
    "zuo_gong.墓库收物": {
        "EFFECTIVE": ("盲派墓库·墓库喜冲不冲不发（辰库收水巨富）", "墓库收物成立，家业/积蓄有成"),
        "NOT_EFFECTIVE": ("盲派墓库·喜冲不冲不发", "墓库收物未成立，家业/积蓄平平"),
        "UNDETERMINED": ("盲派墓库", "田宅家业判定证据不足，不做断言"),
    },
    "zuo_gong.冲开墓库": {
        "冲开墓库": ("盲派墓库·墓库喜冲，不冲不发", "墓库被冲开，家业/积蓄有变动之机"),
    },
    # ── THEME-010 福德精神 ────────────────────────────────
    "zuo_gong.食伤做功": {
        "EFFECTIVE": ("盲派十神口诀·日带食神自己福，一世不会受辛苦；食神主衣食口福", "食伤做功成立，有福气、衣食无忧"),
        "NOT_EFFECTIVE": ("盲派十神口诀·食神主衣食口福", "食伤做功未成，福气/衣食保障平平"),
    },
    "zuo_gong.印做功": {
        "EFFECTIVE": ("盲派十神口诀·印主福寿庇护", "印做功成立，有长辈庇护，福泽厚"),
        "NOT_EFFECTIVE": ("盲派十神口诀·印主福寿庇护", "印做功未成，长辈庇护有限"),
    },
    # ── THEME-011 父母长辈 ────────────────────────────────
    "parents.father(偏财)": {
        "PRESENT": ("盲派六亲·父星=偏财", "父星（偏财）在局中"),
        "ABSENT": ("盲派六亲·父星=偏财", "父星（偏财）不显，父缘淡或助力少"),
    },
    "parents.mother(印星)": {
        "PRESENT": ("盲派六亲·母星=印星", "母星（印星）在局中"),
        "ABSENT": ("盲派六亲·母星=印星", "母星（印星）不显，母缘淡或助力少"),
    },
    # ── THEME-012 才艺学业 ────────────────────────────────
    "zuo_gong.印做功(学业)": {
        "EFFECTIVE": ("段建业《盲派中级命理学》第11章：印星须做功方表学历", "印星做功成立，学业有成就"),
        "NOT_EFFECTIVE": ("段建业《盲派中级命理学》第11章：印星不做功=懒惰不好学", "印星不做功，学业动力不足"),
    },
    "zuo_gong.食伤泄秀(才艺)": {
        "EFFECTIVE": ("段建业《盲派中级命理学》第11章：食神主思想思考、主学习好", "食伤泄秀成立，才艺/口才出众"),
        "NOT_EFFECTIVE": ("段建业《盲派中级命理学》第11章", "食伤泄秀不成立，才艺表现平平"),
    },
    "talent.direction": {
        "WEN(木火)": ("段建业《盲派中级命理学》第11章：金水主理，木火主文", "文理方向偏文（木火）"),
        "LI(金水)": ("段建业《盲派中级命理学》第11章：金水主理，木火主文", "文理方向偏理（金水）"),
        "UNDETERMINED": ("段建业《盲派中级命理学》第11章", "文理方向判定证据不足，不做断言"),
    },
}

# ────────────────────────────────────────────────────────────
# 二、组合枚举 token：原文断言 + 现代语义（_AND_ 拆解后逐 token 翻译）
# ────────────────────────────────────────────────────────────
TOKEN_SEMANTICS: Dict[str, Dict[str, tuple]] = {
    "marriage_event_structure.palace_state": {
        "CLASHED": ("盲派婚姻篇·配偶宫逢冲", "配偶宫（日支）被冲，婚姻根基动摇"),
        "HARMED": ("盲派婚姻篇·配偶宫逢穿", "配偶宫（日支）被穿，暗中受克，婚姻暗损"),
        "PUNISHED": ("盲派婚姻篇·配偶宫逢刑", "配偶宫（日支）被刑，夫妻易有口舌纠纷"),
        "HE_BANNED": ("盲派婚姻篇·配偶宫逢合绊", "配偶宫（日支）被合绊，感情易被他人牵动"),
    },
    "children.palace_hit": {
        "时支逢冲": ("段建业《盲派八字命理口诀·子女》：子女宫忌冲", "子女宫（时支）逢冲，子女运不稳"),
        "时支逢穿": ("段建业《盲派八字命理口诀·子女》：子女宫忌伤", "子女宫（时支）逢穿，子女运有损"),
        "枭印在时柱(克子)": ("段建业《盲派八字命理口诀·子女》：枭印在时柱克子息", "枭印临子女宫，克子息"),
        "枭印在时柱": ("段建业《盲派八字命理口诀·子女》：枭印在时柱克子息", "枭印临子女宫，克子息"),
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
        "驿马": ("盲派金口诀·驿马逢冲/合为引动", "驿马被引动，有迁移变动之机"),
    },
    "zuo_gong.冲开墓库": {
        "冲开墓库": ("盲派墓库·墓库喜冲，不冲不发", "墓库被冲开，家业/积蓄有变动之机"),
    },
}

# ────────────────────────────────────────────────────────────
# 三、L2 事件断语：原文断言 + 现代语义（EVENT_SEMANTICS）
# ────────────────────────────────────────────────────────────
EVENT_SEMANTICS: Dict[str, tuple] = {
    "MARRIAGE_BROKEN": ("盲派婚姻篇·配偶宫逢冲必离婚/配偶宫破星损（BLIND-DJ-004）", "婚姻容易出现分离、难长久的问题"),
    "MARRIAGE_CHALLENGED": ("盲派婚姻篇·配偶宫受损（BLIND-DJ-004）", "婚姻有波折，需用心经营"),
    "MARRIAGE_STABLE": ("盲派婚姻篇·配偶宫安稳（BLIND-DJ-004）", "婚姻状态平稳"),
    "WEALTH_ESTABLISHED": ("盲派财富章·财现+财被取+做功成（BLIND-DJ-005/007/009）", "求财有成，财富能到手"),
    "WEALTH_CANDIDATE": ("盲派财富章·财被取未全成", "求财有得有失，财富待定"),
    "WEALTH_UNTAKEN": ("盲派财富章·有财未被取（BLIND-DJ-005）", "局中有财未取，财不易到手"),
    "WEALTH_ABSENT": ("盲派财富章·无财亦无换象", "无财无换象，财源薄"),
    "OFFICIAL_ESTABLISHED": ("盲派官贵章·制尽杀星得天下（BLIND-DJ-006）", "功名/管理有成，能掌权"),
    "OFFICIAL_PARTIAL": ("盲派官贵章·官杀制不净（BLIND-DJ-007）", "功名有限，职位层次不高"),
    "OFFICIAL_DAMAGED": ("盲派官贵章·穿官损官（BLIND-DJ-010）", "官星被损，官场/体制内不顺"),
    "OFFICIAL_ROBBED": ("盲派官贵章·官星被劫财合走（BLIND-DJ-011）", "职位非我所有，难掌实权"),
    "OFFICIAL_OFFENSE_CANDIDATE": ("盲派官贵章·官杀无制必犯官非（BLIND-DJ-001）", "官杀无制，易与官方冲突/犯官非"),
    "OCCUPATION_DIRECTION_CANDIDATE": ("盲派职业章·做功类型映射职业候选", "职业方向候选（见 detail.occupation_name）"),
    "BODY_LU_ATTACK": ("盲派口诀·禄怕见绝更怕穿害（BLIND-DJ-002）", "禄神受攻击，身体或福报易受损"),
    "BODY_YANG_REN_CLASH": ("盲派口诀·羊刃逢冲血光之灾（BLIND-DJ-003）", "羊刃逢冲，有血光/外伤风险"),
    "REVERSED_PATTERN": ("盲派口诀·反局：做功方向与日主意向相反（BLIND-DJ-008）", "做功方向与日主意向相反，越努力越背（反局）"),
}

# 时间层事件 kind → 原文断言 + 现代语义（TIME_<KIND>）
TIME_KIND_SEMANTICS: Dict[str, tuple] = {
    "CHONG": ("盲派应期·逢冲则动，冲主位凶（庚午辛未壬申癸酉）", "大运/流年冲引动原局，主变动"),
    "CHUAN": ("盲派应期·穿比冲更狠，暗中受克（戊申己未庚申辛巳）", "大运/流年穿引动原局，暗中受损"),
    "SANXING": ("盲派应期·三刑引动", "大运/流年刑引动原局，主口舌纠纷"),
    "FANYIN": ("盲派应期·反吟：天克地冲", "大运/流年反吟（天克地冲）引动原局，主剧烈变动"),
    "FUYIN": ("盲派应期·伏吟：重复引动", "大运/流年伏吟引动原局，主原局结构重演/加重"),
    "LIUHE": ("盲派应期·六合引动", "大运/流年合引动原局，主合绊/牵动"),
    "SANHE": ("盲派应期·三合引动", "大运/流年三合引动原局，主成局/聚势"),
    "MUKU_KAI": ("盲派应期·墓库逢冲则开（BLIND-DJ-005）", "大运/流年冲开墓库，主积蓄变动/库开"),
    "LU": ("盲派应期·禄神引动（BLIND-DJ-002）", "大运/流年引动禄神，主身体/福报相关变动"),
    "TOUGAN": ("盲派应期·透干引动", "大运/流年透干引动原局，主天干层面变动"),
    "ZIXING": ("盲派应期·自刑引动", "大运/流年自刑引动原局，主自我消耗/口舌"),
    "ZIZAIXIAN": ("盲派应期·自在线引动", "大运/流年自在线引动原局，主原局重现"),
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
                out.append(("盲派金口诀·驿马逢冲/合为引动", "驿马被引动，有迁移变动之机"))
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
                    "CONTROL_OFFICER_BY_FOOD_INJURY": ("案例12：伤食制官局，命有官职", "以食伤制官杀取功名，走公职/管理路线"),
                    "CONTROL_OFFICER_BY_INTERACTION": ("盲派互动制官·刑/穿/冲制官杀（案例取证）", "以刑穿冲等互动方式制官杀，靠手段/冲突方式得权"),
                    "CONTROL_WEALTH_BY_BIJIE": ("盲派做功·比劫制财", "靠朋友/伙伴/竞争制财，与人合伙谋财"),
                    "CONTROL_WEALTH_BY_INTERACTION": ("盲派互动制财·刑穿冲制财", "以互动方式（刑穿冲）制财，财来自竞争博弈"),
                    "CONTROL_FOOD_INJURY_BY_RESOURCE": ("盲派做功·印制食伤", "以印印制食伤，靠约束收敛立身"),
                    "CONTROL_BIJIE_BY_OFFICER": ("盲派做功·官杀制比劫", "以官杀制比劫，靠规则/领导约束团队"),
                    "CONTROL_RESOURCE_BY_WEALTH": ("盲派做功·财制印", "以财坏印，靠现实利益突破条条框框"),
                    "GENERATE_WEALTH_BY_FOOD_INJURY": ("案例46：食伤做功技术赚", "以食伤生财，靠技艺/技术谋财"),
                    "TRANSFORM_OFFICER_BY_RESOURCE": ("案例23：印主单位", "以印化官杀，靠单位/文职立足"),
                    "STORE_BY_MUKU": ("盲派墓库·辰库收水（案例1）", "以墓库收物蓄财，走金融/仓储类"),
                    "DRAIN_BY_FOOD_INJURY": ("盲派做功·食伤泄秀", "以食伤泄秀，靠才华表达立身"),
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
# 四、解层断语全集审计：按代码枚举空间校验注册表覆盖（非案例覆盖）
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
