# -*- coding: utf-8 -*-
"""L3 解析层（Interpretation Layer）：原文 + 现代语义。

输入：L2.5 BlindThemeResult（12 主题聚合） + L2 BlindJudgmentResult（事件候选）
输出：12 主题现代语义条目。每条 = { 原文出处(original) + 现代语义(modern) + 引擎事实(value) }。

铁律：
- 每个现代语义句子必须由本文件的规则表固定模板生成：零 LLM、零自由发挥、零评分。
- 每条映射必须带原文出处（盲派原文/案例原文）。无原文可依 = MODERN_MISSING（不发明）。
- 吉凶词汇在 L3 出口正式允许（映射层是现代语言出口，吉凶在此层按引擎方向事实化输出）。
- 全布尔/枚举，禁评分、禁百分比、禁权重。

方法域：DUAN_JIANYE（段建业体系）。
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

METHOD_SCOPE = "DUAN_JIANYE"

# ────────────────────────────────────────────────────────────
# 现代语义规则表（唯一事实源：原文 → 现代语义固定模板）
# 结构：THEME_ID → {(source, value): (原文出处, 现代语义模板)}
# 原则：现代语义模板只翻译原文事实，不新增判断。
# ────────────────────────────────────────────────────────────

# 十神透干 → 性情现代语义（原文：盲派十神心性口诀/渊海子平十神赋）
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

MODERN_SEMANTICS: Dict[str, Dict[tuple, tuple]] = {
    # ── THEME-001 性情禀赋 ────────────────────────────────
    "THEME-001": {
        ("blind_wangshuai", "WANG"): ("盲派四定律·身旺以官杀（含纳音）", "日主自身力量旺，扛得住财官，做事有底气"),
        ("blind_wangshuai", "RUO"): ("盲派四定律·身弱以财官（含纳音）", "日主自身力量偏弱，做事易受牵制，需借外力"),
        ("blind_wangshuai", "UNDETERMINED"): ("盲派旺衰定律", "旺衰判定证据不足，不做断言"),
        ("blind_wangshuai", "ZHONG_HE_PIAN_RUO"): ("盲派旺衰定律", "日主中和偏弱，做事需借财官之力，不宜硬扛"),
        ("five_element_imbalance", "True"): ("五行失衡（排盘层五行统计）", "五行分布不均，性情有偏向，某方面特质突出"),
        ("five_element_imbalance", "False"): ("五行失衡（排盘层五行统计）", "五行相对均衡，性情较平和"),
        ("five_element_imbalance", "TRUE"): ("五行失衡（排盘层五行统计）", "五行分布不均，性情有偏向，某方面特质突出"),
        ("five_element_imbalance", "FALSE"): ("五行失衡（排盘层五行统计）", "五行相对均衡，性情较平和"),
        ("transparent_ten_gods", "TEN_GOD_TRANSPARENT"): ("盲派十神心性（透干十神）", "见逐项十神性情（entry 内扩展）"),
    },
    # ── THEME-002 交游人际 ────────────────────────────────
    "THEME-002": {
        ("kinship_count.brother_count", "0"): ("盲派六亲计数·比肩为兄弟", "同胞中兄弟少（0）"),
        ("kinship_count.sister_count", "6"): ("盲派六亲计数·劫财为姐妹", "同胞中姐妹多（6）"),
        ("zuo_gong.比劫做功", "EFFECTIVE"): ("盲派做功·比劫制财/比劫成党", "比劫做功有效，人际靠朋友/伙伴，竞争性强"),
        ("zuo_gong.比劫做功", "NOT_EFFECTIVE"): ("盲派做功·比劫制财", "比劫做功未成，朋友助力有限"),
    },
    # ── THEME-003 婚姻配偶 ────────────────────────────────
    "THEME-003": {
        ("marriage_event_structure.marriage_state", "BROKEN"): ("盲派婚姻篇·配偶宫逢冲必离婚/配偶宫破星损", "婚姻上容易出现分离、难长久的问题"),
        ("marriage_event_structure.marriage_state", "CHALLENGED"): ("盲派婚姻篇·配偶宫受损", "婚姻上容易有波折，需经营"),
        ("marriage_event_structure.marriage_state", "HARMONIOUS"): ("盲派婚姻篇·配偶宫稳定", "婚姻状态平稳，配偶宫无破"),
        ("marriage_event_structure.marriage_state", "UNDETERMINED"): ("盲派婚姻篇", "婚姻判定证据不足，不做断言"),
        ("marriage_event_structure.palace_state", "CLASHED_AND_HARMED_AND_PUNISHED"): ("盲派婚姻篇·配偶宫逢冲刑穿害", "配偶宫（日支）被冲/刑/穿/害，婚姻根基不稳"),
        ("marriage_event_structure.palace_state", "HARMED_AND_PUNISHED_AND_HE_BANNED"): ("盲派婚姻篇·配偶宫逢穿刑合绊", "配偶宫（日支）逢穿刑合绊，婚姻易生变数"),
        ("marriage_event_structure.palace_state", "PUNISHED_AND_HE_BANNED"): ("盲派婚姻篇·配偶宫逢刑合绊", "配偶宫（日支）逢刑合绊，感情易有纠纷"),
        ("marriage_event_structure.palace_state", "PUNISHED"): ("盲派婚姻篇·配偶宫逢刑", "配偶宫（日支）逢刑，夫妻易有口舌"),
        ("marriage_event_structure.palace_state", "STABLE"): ("盲派婚姻篇·配偶宫安稳", "配偶宫安稳，婚姻基础好"),
        ("marriage_event_structure.palace_state", "CLASHED_AND_PUNISHED"): ("盲派婚姻篇·配偶宫逢冲刑", "配偶宫（日支）逢冲刑，婚姻易起波澜"),
        ("marriage_event_structure.palace_state", "HARMED_AND_HE_BANNED"): ("盲派婚姻篇·配偶宫逢穿合绊", "配偶宫（日支）逢穿合绊，感情易被牵绊"),
        ("marriage_event_structure.palace_state", "HE_BANNED"): ("盲派婚姻篇·配偶宫逢合绊", "配偶宫（日支）逢合绊，感情易被他人牵动"),
        ("marriage_event_structure.spouse_star_present", "True"): ("盲派婚姻篇·配偶星", "配偶星在局中（有婚姻对象之缘）"),
        ("marriage_event_structure.spouse_star_present", "False"): ("盲派婚姻篇·配偶星", "配偶星不在局中（缘分难显）"),
    },
    # ── THEME-004 子女 ────────────────────────────────────
    "THEME-004": {
        ("children.star", "男命有财→官杀为子女星(七杀为儿/正官为女)"): ("段建业《盲派八字命理口诀·子女》：有财星则以七杀为儿、正官为女", "男命以官杀为子女星（七杀主儿子、正官主女儿）"),
        ("children.star", "男命无财→食伤为子女星(食神为儿/伤官为女)"): ("段建业《盲派八字命理口诀·子女》：无财星则以食神为儿、伤官为女", "男命以食伤为子女星（食神主儿子、伤官主女儿）"),
        ("children.star", "女命→食伤为子女星(食神为女/伤官为儿)"): ("段建业《盲派八字命理口诀·子女》：女命以食神为女、伤官为儿", "女命以食伤为子女星（食神主女儿、伤官主儿子）"),
        ("children.star_present", "TRUE"): ("段建业《盲派八字命理口诀·子女》", "子女星在局中"),
        ("children.star_present", "FALSE"): ("段建业《盲派八字命理口诀·子女》", "子女星不显，子女缘晚显或淡"),
        ("children.palace_hit", "时支逢穿"): ("段建业《盲派八字命理口诀·子女》：时柱忌枭印驾临，子女宫忌伤", "子女宫（时支）逢穿，子女运有损"),
        ("children.palace_hit", "时支逢冲"): ("段建业《盲派八字命理口诀·子女》", "子女宫（时支）逢冲，子女运不稳"),
        ("children.palace_hit", "枭印在时柱"): ("段建业《盲派八字命理口诀·子女》：枭印在时柱克子息", "枭印临子女宫，克子息"),
        ("children.palace_hit", "STABLE"): ("段建业《盲派八字命理口诀·子女》", "子女宫安稳，无冲穿枭压"),
        ("children.palace_hit", "时支逢冲_AND_枭印在时柱"): ("段建业《盲派八字命理口诀·子女》：时柱忌枭印驾临", "子女宫逢冲且枭印临宫，子女运双重受损"),
        ("children.palace_hit", "时支逢穿_AND_枭印在时柱"): ("段建业《盲派八字命理口诀·子女》：时柱忌枭印驾临", "子女宫逢穿且枭印临宫，子女运双重受损"),
        ("children.star_present", "FALSE"): ("段建业《盲派八字命理口诀·子女》", "子女星不显，子女缘晚显或淡"),
    },
    # ── THEME-005 财帛 ────────────────────────────────────
    "THEME-005": {
        ("wealth_event_structure.wealth_state", "DIRECTED_AND_ESTABLISHED"): ("盲派财富章·财现+财被取+做功成（案例集：食伤生财/制财做功）", "财星被定向取用且做功成立，求财有成"),
        ("wealth_event_structure.wealth_state", "SUBSTITUTED_AND_ESTABLISHED"): ("盲派换象·伤食当财/禄当财/官杀当财（VERIFY-BLIND-022）", "财以换象方式成立（伤食/禄/官杀当财），求财方式特别"),
        ("wealth_event_structure.wealth_state", "PRESENT_UNTAKEN"): ("盲派财富章·有财未被取", "局中有财但未被取用，财不易到手"),
        ("wealth_event_structure.wealth_state", "UNDETERMINED"): ("盲派财富章", "财富判定证据不足，不做断言"),
        ("wealth_event_structure.wealth_present", "True"): ("盲派财富章·财星在局", "局中有财星"),
        ("wealth_event_structure.wealth_present", "False"): ("盲派财富章·财星不现", "局中财星不现，以换象论财"),
        ("wealth_event_structure.wealth_present", "FALSE"): ("盲派财富章·财星不现", "局中财星不现，以换象论财"),
    },
    # ── THEME-006 身体疾厄 ────────────────────────────────
    "THEME-006": {
        ("body_event_candidate.candidate", "LU_UNDER_ATTACK"): ("盲派口诀·禄怕见绝更怕穿害（案例集戊申己未庚申辛巳交通意外）", "禄神受攻击（被穿/合克/脆金），身体或福报易受损"),
        ("body_event_candidate.candidate", "YANG_REN_CLASHED"): ("盲派口诀·羊刃逢冲血光之灾（庚午辛未壬申癸酉）", "羊刃逢冲，有血光/外伤风险"),
        ("body_event_candidate.candidate", "UNDETERMINED"): ("盲派身体章", "身体判定证据不足，不做断言"),
        ("body_event_candidate.lu_attacked", "True"): ("盲派口诀·禄怕见绝更怕穿害", "禄神状态受损（穿/冲/合克）"),
        ("body_event_candidate.lu_attacked", "False"): ("盲派口诀·禄怕见绝更怕穿害", "禄神未被攻击"),
        ("dry_earth_brittle", "NO_DRY_EARTH"): ("盲派口诀·燥土脆金（VERIFY-BLIND-034）", "无燥土脆金之患"),
        ("dry_earth_brittle", "NOT_TRIGGERED"): ("盲派口诀·燥土脆金（VERIFY-BLIND-034）", "燥土脆金条件未触发"),
    },
    # ── THEME-007 迁移出行 ────────────────────────────────
    "THEME-007": {
        ("yima.present", "SHEN马在YIN_AND_YIN马在SHEN"): ("盲派金口诀·论驿马：寅午戌马在申、申子辰马在寅", "命带驿马（申马在寅、寅马在申），主走动奔波"),
        ("yima.trigger", "NO_TRIGGER"): ("盲派金口诀·驿马引动", "驿马未被大运流年冲合引动，暂不迁移"),
        ("yima.trigger", "TRIGGERED"): ("盲派金口诀·驿马逢冲/合为引动", "驿马被引动，有迁移变动之机"),
        ("yima.present", "NONE"): ("盲派金口诀·论驿马", "命不带驿马，走动少、偏安于一地"),
        ("yima.present", "CHOU马在HAI"): ("盲派金口诀·论驿马：巳酉丑马在亥", "命带驿马（丑马在亥），主走动奔波"),
        ("yima.present", "CHOU马在HAI_AND_YOU马在HAI"): ("盲派金口诀·论驿马：巳酉丑马在亥", "命带驿马（丑马、酉马同在亥），走动信息强"),
        ("yima.present", "HAI马在SI_AND_SI马在HAI"): ("盲派金口诀·论驿马：亥卯未马在巳、巳酉丑马在亥", "命带驿马（亥马在巳、巳马在亥），走动信息强"),
        ("yima.present", "SHEN马在YIN_AND_ZI马在YIN"): ("盲派金口诀·论驿马：申子辰马在寅", "命带驿马（申马、子马同在寅），走动信息强"),
    },
    # ── THEME-008 事业功名 ────────────────────────────────
    "THEME-008": {
        ("occupation_candidate.work_types", "CONTAIN_CONTROL_OFFICER_BY_FOOD_INJURY"): ("案例12：伤食制官局，命有官职", "以食伤制官杀取功名，走公职/管理路线"),
        ("occupation_candidate.work_types", "CONTAIN_GENERATE_WEALTH_BY_FOOD_INJURY"): ("案例46：食伤做功技术赚", "以食伤生财，靠技艺/技术谋财"),
        ("occupation_candidate.work_types", "CONTAIN_TRANSFORM_OFFICER_BY_RESOURCE"): ("案例23：印主单位", "以印化官杀，靠单位/文职立足"),
        ("official_event_structure.official_state", "CONTROLLED_AND_CLEAN"): ("盲派口诀·制尽杀星得天下（乾隆 金水伤官制净）", "官杀被制净，功名/管理有成"),
        ("official_event_structure.official_state", "CONTROLLED_PARTIAL"): ("盲派口诀·官杀制不净（D29 车间主任）", "官杀有制但制不净，功名/职位有限"),
        ("official_event_structure.official_state", "DAMAGED"): ("盲派口诀·穿官损官，官根受损（案例2 官场梦碎）", "官星被穿损，官场/体制内不顺"),
        ("official_event_structure.official_state", "ROBBED"): ("盲派口诀·官星被劫财合走，非我所有（案例8 仓库保管员）", "官星被劫财合走，职位非我所有，难掌实权"),
        ("official_event_structure.official_state", "UNCONTROLLED"): ("盲派口诀·官杀无制必犯官非（庚午辛未壬申癸酉）", "官杀无制，易犯官非/与官方冲突"),
        ("occupation_candidate.work_types", "CONTAIN_STORE_BY_MUKU"): ("盲派墓库·辰库收水（案例1：银行金融中心）", "含墓库收物做功，职业与金融/仓储/管理库藏相关"),
        ("work_efficiency", "LARGE"): ("盲派效率·做功效率大（功大者贵）", "做功效率大，事业成就层次高"),
        ("work_efficiency", "MEDIUM"): ("盲派效率·做功效率中", "做功效率中等，事业成就有一定层次"),
    },
    # ── THEME-009 田宅家业 ────────────────────────────────
    "THEME-009": {
        ("zuo_gong.墓库收物", "EFFECTIVE"): ("盲派墓库·墓库喜冲不冲不发（辰库收水巨富）", "墓库收物成立，家业/积蓄有成"),
        ("zuo_gong.墓库收物", "NOT_EFFECTIVE"): ("盲派墓库·喜冲不冲不发", "墓库收物未成立，家业/积蓄平平"),
        ("zuo_gong.墓库收物", "UNDETERMINED"): ("盲派墓库", "田宅家业判定证据不足，不做断言"),
        ("zuo_gong.冲开墓库", "冲开墓库"): ("盲派墓库·墓库喜冲，不冲不发", "墓库被冲开，家业/积蓄有变动之机"),
    },
    # ── THEME-010 福德精神 ────────────────────────────────
    "THEME-010": {
        ("zuo_gong.食伤做功", "EFFECTIVE"): ("盲派十神口诀·日带食神自己福，一世不会受辛苦；食神主衣食口福", "食伤做功成立，有福气、衣食无忧"),
        ("blind_wangshuai", "WANG"): ("盲派十神口诀·印旺身强多福寿，六亲和睦家道丰", "日主旺，福寿根基好"),
        ("blind_wangshuai", "ZHONG_HE_PIAN_RUO"): ("盲派十神口诀·身旺方论福寿", "日主中和偏弱，福寿根基一般，需后天保养"),
        ("zuo_gong.印做功", "EFFECTIVE"): ("盲派十神口诀·印主福寿庇护", "印做功成立，有长辈庇护，福泽厚"),
        ("zuo_gong.食伤做功", "NOT_EFFECTIVE"): ("盲派十神口诀·食神主衣食口福", "食伤做功未成，福气/衣食保障平平"),
    },
    # ── THEME-011 父母长辈 ────────────────────────────────
    "THEME-011": {
        ("parents.father(偏财)", "PRESENT"): ("盲派六亲·父星=偏财", "父星（偏财）在局中"),
        ("parents.father(偏财)", "ABSENT"): ("盲派六亲·父星=偏财", "父星（偏财）不显，父缘淡或助力少"),
        ("parents.mother(印星)", "PRESENT"): ("盲派六亲·母星=印星", "母星（印星）在局中"),
        ("parents.mother(印星)", "ABSENT"): ("盲派六亲·母星=印星", "母星（印星）不显，母缘淡或助力少"),
    },
    # ── THEME-012 才艺学业 ────────────────────────────────
    "THEME-012": {
        ("zuo_gong.印做功(学业)", "EFFECTIVE"): ("段建业《盲派中级命理学》第11章：印星须做功方表学历", "印星做功成立，学业有成就"),
        ("zuo_gong.印做功(学业)", "NOT_EFFECTIVE"): ("段建业《盲派中级命理学》第11章：印星不做功=懒惰不好学", "印星不做功，学业动力不足"),
        ("zuo_gong.食伤泄秀(才艺)", "EFFECTIVE"): ("段建业《盲派中级命理学》第11章：食神主思想思考、主学习好", "食伤泄秀成立，才艺/口才出众"),
        ("zuo_gong.食伤泄秀(才艺)", "NOT_EFFECTIVE"): ("段建业《盲派中级命理学》第11章", "食伤泄秀不成立，才艺表现平平"),
        ("talent.direction", "WEN(木火)"): ("段建业《盲派中级命理学》第11章：金水主理，木火主文", "文理方向偏文（木火）"),
        ("talent.direction", "LI(金水)"): ("段建业《盲派中级命理学》第11章：金水主理，木火主文", "文理方向偏理（金水）"),
    },
}

# 主题级现代语义模板（综合断言：由 entries 状态拼接，仍全模板）
THEME_SUMMARY: Dict[str, Dict[str, str]] = {
    "THEME-001": ("盲派十神心性", "性情由旺衰+五行+透干十神共同决定，以下为逐项事实"),
    "THEME-002": ("盲派六亲计数", "同胞关系以比劫计数为据"),
    "THEME-003": ("盲派婚姻篇", "婚姻以配偶宫（日支）+配偶星状态为据"),
    "THEME-004": ("段建业子女口诀", "子女以子女星+子女宫（时支）状态为据"),
    "THEME-005": ("盲派财富章", "财富以财星取用做功状态为据"),
    "THEME-006": ("盲派身体章", "身体以禄神/羊刃/燥土状态为据"),
    "THEME-007": ("盲派金口诀·论驿马", "迁移以驿马+引动状态为据"),
    "THEME-008": ("盲派职业/官贵章", "事业以做功类型+官杀制净状态为据"),
    "THEME-009": ("盲派墓库章", "田宅家业以墓库收物状态为据"),
    "THEME-010": ("盲派十神口诀·福德", "福德以食伤（寿）+印（福）+旺衰为据"),
    "THEME-011": ("盲派六亲章", "父母以偏财（父）+印星（母）在局与否为据"),
    "THEME-012": ("段建业《盲派中级命理学》第11章", "才艺学业以印做功+食伤泄秀+文理方向为据"),
}

MODERN_MISSING = "（原文/现代语义证据未取证，不做断言）"


@dataclass
class InterpretationEntry:
    """单条现代语义：引擎事实 + 原文出处 + 现代语义。"""
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
    """L3 解析层结果：12 主题现代语义（原文+现代语义成对）。"""
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
                    "CONTROL_OFFICER_BY_INTERACTION", "CONTROL_WEALTH_BY_BIJIE"):
            if key in joined:
                return "CONTAIN_" + key
        return joined[:80]
    if isinstance(v, dict):
        # 透干十神 dict：{"year": "偏财", ...} → 规范成 TEN_GOD_TRANSPARENT（逐项由展开逻辑处理）
        return "TEN_GOD_TRANSPARENT"
    if isinstance(v, str) and v[:1] in ("{", "["):
        # 兼容 Python repr（单引号）形式的 list/dict 字符串
        try:
            import ast
            parsed = ast.literal_eval(v)
            if isinstance(parsed, (list, dict)):
                return _norm_value(parsed)
        except Exception:
            pass
    return str(v).upper() if isinstance(v, bool) else str(v)


def interpret_blind(theme_result, judgment_result=None, blind_result=None) -> BlindInterpretationResult:
    """L3 解析：消费 L2.5 主题聚合，输出 原文+现代语义 成对条目。

    参数兼容 BlindThemeResult / dict（theme_result.to_dict() 或 theme_result 本身）。
    """
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
        table = MODERN_SEMANTICS.get(theme_id, {})
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
            key = (src, norm_val)
            hit = table.get(key)
            if hit is None and src in ("kinship_count.brother_count", "kinship_count.sister_count"):
                # 数字计数通配：兄弟=比肩数、姐妹=劫财数（盲派六亲计数）
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

        summary_src, summary_txt = THEME_SUMMARY.get(theme_id, ("（未定义）", ""))
        out_themes.append({
            "theme_id": theme_id,
            "theme_name": theme_name,
            "state": state,
            "modern_summary_source": summary_src,
            "modern_summary": summary_txt,
            "entries": entry_out,
        })

    status = "ESTABLISHED" if any_modern else "UNDETERMINED"
    return BlindInterpretationResult(themes=out_themes, status=status)


def interpret_blind_events(judgment_result, theme_result=None) -> List[Dict]:
    """L2 事件层现代语义（L3 补充：把 L2 事件候选翻译成 原文+现代语义 成对）。

    消费 judgment_result.event_candidates（dict 列表），逐条映射。
    """
    evts = getattr(judgment_result, "event_candidates", None)
    if evts is None:
        evts = (judgment_result or {}).get("event_candidates", []) if isinstance(judgment_result, dict) else []

    # L2 事件 → 现代语义映射（原文出自 EVIDENCE 字典 BLIND-DJ-xxx）
    EVENT_MODERN = {
        "MARRIAGE_BROKEN": ("盲派婚姻篇·配偶宫逢冲必离婚/配偶宫破星损（BLIND-DJ-004）", "婚姻容易出现分离、难长久的问题"),
        "MARRIAGE_CHALLENGED": ("盲派婚姻篇·配偶宫受损（BLIND-DJ-004）", "婚姻有波折，需用心经营"),
        "MARRIAGE_STABLE": ("盲派婚姻篇·配偶宫安稳", "婚姻状态平稳"),
        "WEALTH_ESTABLISHED": ("盲派财富章·财现+财被取+做功成（BLIND-DJ-005/007/009）", "求财有成，财富能到手"),
        "OFFICIAL_ESTABLISHED": ("盲派官贵章·制尽杀星得天下（BLIND-DJ-006）", "功名/管理有成，能掌权"),
        "OFFICIAL_PARTIAL": ("盲派官贵章·官杀制不净（BLIND-DJ-007）", "功名有限，职位层次不高"),
        "OFFICIAL_DAMAGED": ("盲派官贵章·穿官损官（BLIND-DJ-010）", "官星被损，官场/体制内不顺"),
        "OFFICIAL_ROBBED": ("盲派官贵章·官星被劫财合走（BLIND-DJ-011）", "职位非我所有，难掌实权"),
        "OFFICIAL_OFFENSE_CANDIDATE": ("盲派官贵章·官杀无制必犯官非（BLIND-DJ-001）", "官杀无制，易与官方冲突/犯官非"),
        "OCCUPATION_DIRECTION_CANDIDATE": ("盲派职业章·做功类型映射职业候选", "职业方向候选（见 occupation_name）"),
        "BODY_LU_ATTACK": ("盲派口诀·禄怕见绝更怕穿害（BLIND-DJ-002）", "禄神受攻击，身体或福报易受损"),
        "BODY_YANG_REN_CLASH": ("盲派口诀·羊刃逢冲血光之灾（BLIND-DJ-003）", "羊刃逢冲，有血光/外伤风险"),
        "REVERSED_PATTERN": ("盲派口诀·反局：做功方向与日主意向相反（BLIND-DJ-008）", "做功方向与日主意向相反，越努力越背（反局）"),
    }

    out = []
    for ev in evts:
        et = ev.get("event_type", "") if isinstance(ev, dict) else getattr(ev, "event_type", "")
        dom = ev.get("domain", "") if isinstance(ev, dict) else getattr(ev, "domain", "")
        direction = ev.get("direction", "") if isinstance(ev, dict) else getattr(ev, "direction", "")
        structure = ev.get("structure_ref", "") if isinstance(ev, dict) else getattr(ev, "structure_ref", "")
        evidence = ev.get("evidence_refs", []) if isinstance(ev, dict) else getattr(ev, "evidence_refs", [])
        detail = ev.get("detail", {}) if isinstance(ev, dict) else getattr(ev, "detail", {})
        hit = EVENT_MODERN.get(et)
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
