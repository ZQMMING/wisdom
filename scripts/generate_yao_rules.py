#!/usr/bin/env python3
"""Generate all new rule and evidence files for DISPATCH_HERMES_IMG_YAO_IMPLEMENTATION.

Produces:
  P0:  MK-101~105 (墓库体系)
  P1:  HH-101~103 (合化条件)
  P1:  GW-101~104 (四柱宫位)
  P1:  SX-101~102 (三刑专项)
  P1:  DTS-106/107 (旺衰单因子修正)
  P2:  SMTH-104V2 (天乙贵人温和降级)
  P2:  LM-101 (禄命法框架)
  P2:  TF-101/102 (玄学天赋)
  Event_TOPIC: HLT scenario tags for 刑冲场景化
"""
from __future__ import annotations
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA_DIR = REPO / "data"
RULES_DIR = DATA_DIR / "rules"
EVIDENCE_DIR = DATA_DIR / "evidence"
SCHEMA_DIR = DATA_DIR / "schemas"

NOW = "2026-08-26T18:00:00Z"

# --------------------------------------------------------------------------- #
# Evidence files
# --------------------------------------------------------------------------- #
EVIDENCE = {
    # MK
    "E-MK-101-001": {
        "evidence_id": "E-MK-101-001",
        "rule_refs": ["MK-101"],
        "citation": {
            "original_text": "(待校,paraphrase)旺者为库衰者为墓。《三命通会》论四库(辰戌丑未)随日主旺衰而异其用:旺则库可蓄水蓄水,衰则墓闭气藏。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《三命通会·四库》旺衰判据:四库随日主旺衰而表现为库或墓。MK-101以此为准(待校 paraphrase)。",
        "evidence_strength": "tertiary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-SANMING-TONGHUI-SHIERJUAN",
        "provenance_note": "M2-B:五书分批核验(新补MK系列)",
        "source_locator": {"work": "三命通会", "chapter": "论四库"},
    },
    "E-MK-102-001": {
        "evidence_id": "E-MK-102-001",
        "rule_refs": ["MK-102"],
        "citation": {
            "original_text": "生方怕动库宜开,败地逢冲仔细推。《滴天髓·通神论·衰旺》",
            "language": "classical_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "库宜开(调用库中资源需冲开),墓宜闭(败地逢冲仔细推,墓气不可轻易冲动)。MK-102以此为准。",
        "evidence_strength": "secondary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-DITIANSUI-RENTIEQIAO",
        "provenance_note": "M2-B:金句核校(注意原文为'生方'非'生风')",
        "source_locator": {"work": "滴天髓", "chapter": "通神论·衰旺"},
    },
    "E-MK-103-001": {
        "evidence_id": "E-MK-103-001",
        "rule_refs": ["MK-103"],
        "citation": {
            "original_text": "(待校,paraphrase)刑开库=以摧毁性代价换取资源,缓慢;冲开库=以冲突换资源,高效。《三命通会》论库冲与刑库之异。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《三命通会》库开方式:刑库(缓慢/代价大)vs冲库(高效/冲突明显)。MK-103以此为准。",
        "evidence_strength": "tertiary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-SANMING-TONGHUI-SHIERJUAN",
        "provenance_note": "M2-B:新补MK系列",
        "source_locator": {"work": "三命通会", "chapter": "论刑冲"},
    },
    "E-MK-104-001": {
        "evidence_id": "E-MK-104-001",
        "rule_refs": ["MK-104"],
        "citation": {
            "original_text": "(待校,paraphrase)杂气透干汇之,岂不甚美,又何劳行冲乎!《子平真诠·论杂气用事》",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《子平真诠》杂气格:库中财官印已透干则不需再冲(已出库)。MK-104以此为准。",
        "evidence_strength": "secondary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-ZIPINGZHENQUAN",
        "provenance_note": "M2-B:新补MK系列",
        "source_locator": {"work": "子平真诠", "chapter": "论杂气用事"},
    },
    "E-MK-105-001": {
        "evidence_id": "E-MK-105-001",
        "rule_refs": ["MK-105"],
        "citation": {
            "original_text": "(待校,paraphrase)天干只得一库根,逢冲则余气尽伤。《滴天髓·通神论·衰旺》论库根被冲之弊。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《滴天髓》库根透出后逢冲→余气尽伤。MK-105以此为准。",
        "evidence_strength": "tertiary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-DITIANSUI-RENTIEQIAO",
        "provenance_note": "M2-B:新补MK系列",
        "source_locator": {"work": "滴天髓", "chapter": "通神论·衰旺"},
    },
    # HH
    "E-HH-101-001": {
        "evidence_id": "E-HH-101-001",
        "rule_refs": ["HH-101"],
        "citation": {
            "original_text": "(待校,paraphrase)甲己化土非辰戌丑未月不化;丁壬化木非寅卯月不化;戊癸化火非巳午月不化。《三命通会》论十神化气。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《三命通会·论十神化气》:合化必须得令(化神得月令旺气)。HH-101以此为准。",
        "evidence_strength": "secondary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-SANMING-TONGHUI-SHIERJUAN",
        "provenance_note": "M2-B:新补HH系列",
        "source_locator": {"work": "三命通会", "chapter": "论十神化气"},
    },
    "E-HH-102-001": {
        "evidence_id": "E-HH-102-001",
        "rule_refs": ["HH-102"],
        "citation": {
            "original_text": "(待校,paraphrase)化气格成格条件:双方能量相当;差距大则只合不化(合绊)。化气格通论。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "化气格通论:合化需双方能量相当,差距大则合绊。HH-102以此为准。",
        "evidence_strength": "tertiary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "provenance_note": "M2-B:新补HH系列",
        "source_locator": {"work": "三命通会", "chapter": "论化气"},
    },
    "E-HH-103-001": {
        "evidence_id": "E-HH-103-001",
        "rule_refs": ["HH-103"],
        "citation": {
            "original_text": "(待校,paraphrase)合而能化才论化神,否则仅合绊(合而不化)。《三命通会》。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《三命通会》合化判据:合而能化则论化神,合而不化则仅合绊。HH-103以此为准。",
        "evidence_strength": "tertiary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-SANMING-TONGHUI-SHIERJUAN",
        "provenance_note": "M2-B:新补HH系列",
        "source_locator": {"work": "三命通会", "chapter": "论化气"},
    },
    # GW
    "E-GW-101-001": {
        "evidence_id": "E-GW-101-001",
        "rule_refs": ["GW-101"],
        "citation": {
            "original_text": "(待校,paraphrase)年柱为根祖上,主16岁前气运、出身根基。《渊海子平》《五行精纪》宫位通论。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《渊海子平》《五行精纪》四柱宫位:年柱=祖上/根基。GW-101以此为准(年龄段分段,不硬编码15年)。",
        "evidence_strength": "secondary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-YUANHAIZIPING",
        "provenance_note": "M2-B:新补GW系列",
        "source_locator": {"work": "渊海子平", "chapter": "论四柱宫位"},
    },
    "E-GW-102-001": {
        "evidence_id": "E-GW-102-001",
        "rule_refs": ["GW-102"],
        "citation": {
            "original_text": "(待校,paraphrase)月柱为父母兄弟宫,主青年时期成长教育。《渊海子平》《五行精纪》宫位通论。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《渊海子平》《五行精纪》月柱=父母/成长/兄弟。GW-102以此为准。",
        "evidence_strength": "secondary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-YUANHAIZIPING",
        "provenance_note": "M2-B:新补GW系列",
        "source_locator": {"work": "渊海子平", "chapter": "论四柱宫位"},
    },
    "E-GW-103-001": {
        "evidence_id": "E-GW-103-001",
        "rule_refs": ["GW-103"],
        "citation": {
            "original_text": "(待校,paraphrase)日柱为己身夫妻宫,主中年心性定型。《渊海子平》《五行精纪》宫位通论。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《渊海子平》《五行精纪》日柱=自我/夫妻宫/身体。GW-103以此为准。",
        "evidence_strength": "secondary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-YUANHAIZIPING",
        "provenance_note": "M2-B:新补GW系列",
        "source_locator": {"work": "渊海子平", "chapter": "论四柱宫位"},
    },
    "E-GW-104-001": {
        "evidence_id": "E-GW-104-001",
        "rule_refs": ["GW-104"],
        "citation": {
            "original_text": "(待校,paraphrase)时柱为子女果报宫,主晚年运势。《渊海子平》《五行精纪》宫位通论。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《渊海子平》《五行精纪》时柱=子女/果报/未来。GW-104以此为准。",
        "evidence_strength": "secondary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-YUANHAIZIPING",
        "provenance_note": "M2-B:新补GW系列",
        "source_locator": {"work": "渊海子平", "chapter": "论四柱宫位"},
    },
    # SX
    "E-SX-101-001": {
        "evidence_id": "E-SX-101-001",
        "rule_refs": ["SX-101"],
        "citation": {
            "original_text": "(待校,paraphrase)寅刑巳、巳刑申、申刑寅,循环相克,天地乖气,无恩之刑。《五行精纪》第廿五卷。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《五行精纪》卷廿五:三刑(寅巳申)需三字汇聚方成完整无恩刑。SX-101以此为准。",
        "evidence_strength": "secondary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-WUXINGJINGJI",
        "provenance_note": "M2-B:新补SX系列",
        "source_locator": {"work": "五行精纪", "chapter": "卷廿五·论三刑"},
    },
    "E-SX-102-001": {
        "evidence_id": "E-SX-102-001",
        "rule_refs": ["SX-102"],
        "citation": {
            "original_text": "(待校,paraphrase)三刑方向区分:寅刑巳(取巳中金土)/巳刑寅(取寅中土火)等,破坏根基。《五行精纪》卷廿五。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《五行精纪》三刑方向:各刑取象不同,破坏根基。SX-102以此为准。",
        "evidence_strength": "secondary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-WUXINGJINGJI",
        "provenance_note": "M2-B:新补SX系列",
        "source_locator": {"work": "五行精纪", "chapter": "卷廿五·论三刑"},
    },
    # DTS correction
    "E-DTS-106-001": {
        "evidence_id": "E-DTS-106-001",
        "rule_refs": ["DTS-106"],
        "citation": {
            "original_text": "生方怕动库宜开,败地逢冲仔细推。《滴天髓·通神论·衰旺》——月令被围克则得令不成立。",
            "language": "classical_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《滴天髓》:月令虽得令但被其他地支围克(如午月被子水围克),则得令不成立,反断身弱。DTS-106以此为准。",
        "evidence_strength": "secondary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-DITIANSUI-RENTIEQIAO",
        "provenance_note": "M2-B:修正DTS-101误判,CASE1验证结果",
        "source_locator": {"work": "滴天髓", "chapter": "通神论·衰旺"},
    },
    "E-DTS-107-001": {
        "evidence_id": "E-DTS-107-001",
        "rule_refs": ["DTS-107"],
        "citation": {
            "original_text": "(待校,paraphrase)得地得势可弥补失令:月令失令但有强根/帮扶,仍身偏强。《滴天髓·通神论·衰旺》三辨综合判定。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《滴天髓》三辨(得令/得地/得势)综合判定:失令但有强根强势可转为身强。DTS-107以此为准。",
        "evidence_strength": "secondary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-DITIANSUI-RENTIEQIAO",
        "provenance_note": "M2-B:修正DTS-102误判,CASE2/3/6验证结果",
        "source_locator": {"work": "滴天髓", "chapter": "通神论·衰旺"},
    },
    # SMTH-104V2
    "E-SMTH-104V2-001": {
        "evidence_id": "E-SMTH-104V2-001",
        "rule_refs": ["SMTH-104V2"],
        "citation": {
            "original_text": "(待校,paraphrase)天乙贵人逢冲/空亡,贵人之力减半,降为LIKELY/WEAK。《三命通会·论天乙贵人》",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《三命通会》贵人逢冲力减。SMTH-104V2温和降级(不硬编码逢冲转凶)。",
        "evidence_strength": "tertiary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-SANMING-TONGHUI-SHIERJUAN",
        "provenance_note": "M2-B:温和处理,不引入逢冲=凶定性",
        "source_locator": {"work": "三命通会", "chapter": "论天乙贵人"},
    },
    # LM
    "E-LM-101-001": {
        "evidence_id": "E-LM-101-001",
        "rule_refs": ["LM-101"],
        "citation": {
            "original_text": "(待校,paraphrase)干配禄,以支合命,以纳音论身,之谓三命。《五行精纪》《李虚中命书》禄命法通论。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "《五行精纪》《李虚中命书》:年柱为太极点,看祖上气运/出身根基(独立于日柱子平层)。LM-101以此为准。",
        "evidence_strength": "secondary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "edition_id": "EDITION-WUXINGJINGJI",
        "provenance_note": "M2-B:新补LM系列",
        "source_locator": {"work": "五行精纪", "chapter": "论三命"},
    },
    # TF
    "E-TF-101-001": {
        "evidence_id": "E-TF-101-001",
        "rule_refs": ["TF-101"],
        "citation": {
            "original_text": "(待校,paraphrase)偏印强于正印出玄学天赋;偏印不可临正官。字幕《玄学天赋正解》作者观点。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "玄学天赋判断:偏印(枭神)强于正印,偏印临正官则格局破。TF-101以此为准(作者观点,作性格/天赋主题Signal)。",
        "evidence_strength": "tertiary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "provenance_note": "M2-B:新补TF系列,多属作者观点",
        "source_locator": {"work": "意象派国学字幕", "chapter": "玄学天赋正解"},
    },
    "E-TF-102-001": {
        "evidence_id": "E-TF-102-001",
        "rule_refs": ["TF-102"],
        "citation": {
            "original_text": "(待校,paraphrase)印食伤需相融:燥土印×寒水食伤则相斥,寒土印×暖水食伤可相济。字幕《玄学天赋正解》。",
            "language": "vernacular_chinese",
            "verification_status": "pending_verification",
        },
        "modern_paraphrase": "玄学天赋:印星与食伤的五行调和决定天赋发挥。TF-102以此为准。",
        "evidence_strength": "tertiary",
        "version": "1.0.0",
        "created_at": NOW,
        "source_layer": "paraphrase",
        "provenance_note": "M2-B:新补TF系列",
        "source_locator": {"work": "意象派国学字幕", "chapter": "玄学天赋正解"},
    },
}

# --------------------------------------------------------------------------- #
# Rule files
# --------------------------------------------------------------------------- #
RULES = {
    # ---- P0: 墓库体系 (BASELINE, STRUCTURAL signals) ----
    "MK-101": {
        "rule_id": "MK-101",
        "title": "四库旺衰判据:旺者为库衰者为墓",
        "rule_type": "旺衰判定",
        "source": {
            "work": "三命通会",
            "chapter": "论四库",
            "location": "旺者库衰者墓",
        },
        "conditions": {
            "all": [
                {"field": "month_hidden_main_ten_god", "op": "in", "value": ["正印", "偏印", "比肩", "劫财"]},
                {"field": "day_branch_main_ten_god", "op": "in", "value": ["正印", "偏印", "比肩", "劫财"]},
            ]
        },
        "conclusion": {
            "rationale_classical": "《三命通会》:旺者为库衰者为墓。日主旺则四库为库(可调用库中资源);日主衰则四库为墓(宜收藏宜闭)。",
            "produces_layer_output_template": {"direction": "STABLE", "polarity": "neutral"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "CONSTRAINT",
        "forbidden_inferences": [],
        "evidence_refs": ["E-MK-101-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.0.0",
        "precedence": 0,
        "created_at": NOW,
        "book_id": "SANMING-TONGHUI",
        "passage_id": "P-MK-WANGSHUAI",
        "concept_id": "四库",
        "principle_id": "PRINCIPLE-WANGSHUAI",
        "scope": "八字旺衰判定(四库旺衰判据)",
    },
    "MK-102": {
        "rule_id": "MK-102",
        "title": "库宜开墓宜闭:库中被调用资源需开库",
        "rule_type": "旺衰判定",
        "source": {
            "work": "滴天髓",
            "chapter": "通神论·衰旺",
            "location": "生方怕动库宜开",
        },
        "conditions": {
            "all": [
                {"field": "month_hidden_main_ten_god", "op": "in", "value": ["正财", "偏财", "正官", "七杀", "正印", "偏印"]},
                {"field": "month_branch", "op": "in", "value": ["CHEN", "XU", "CHOU", "WEI"]},
            ]
        },
        "conclusion": {
            "rationale_classical": "《滴天髓》:生方怕动库宜开,败地逢冲仔细推。库宜开(调用资源),墓宜闭(收藏)。",
            "produces_layer_output_template": {"direction": "STABLE", "polarity": "neutral"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "CONSTRAINT",
        "forbidden_inferences": [],
        "evidence_refs": ["E-MK-102-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.0.0",
        "precedence": 0,
        "created_at": NOW,
        "book_id": "DITIANSUI",
        "passage_id": "P-MK-KUMU",
        "concept_id": "库墓",
        "principle_id": "PRINCIPLE-WANGSHUAI",
        "scope": "八字旺衰判定(库墓开闭判据)",
    },
    "MK-103": {
        "rule_id": "MK-103",
        "title": "开库方式:刑开库缓慢代价大,冲开库高效冲突明显",
        "rule_type": "旺衰判定",
        "source": {
            "work": "三命通会",
            "chapter": "论刑冲",
            "location": "刑开库与冲开库",
        },
        "conditions": {
            "any": [
                {
                    "all": [
                        {"field": "month_branch", "op": "in", "value": ["CHEN", "XU", "CHOU", "WEI"]},
                        {"field": "day_branch", "op": "in", "value": ["CHEN", "XU", "CHOU", "WEI"]},
                    ]
                },
                {
                    "all": [
                        {"field": "month_branch", "op": "in", "value": ["CHEN", "XU", "CHOU", "WEI"]},
                        {"field": "branch_clash_map", "op": "has_any", "value": [["CHEN","XU"],["CHOU","WEI"]]},
                    ]
                },
            ]
        },
        "conclusion": {
            "rationale_classical": "《三命通会》:刑开库以摧毁性代价换资源(缓慢),冲开库以冲突换资源(高效)。",
            "produces_layer_output_template": {"direction": "VOLATILE", "polarity": "caution"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "CHANGE",
        "forbidden_inferences": [],
        "evidence_refs": ["E-MK-103-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.0.0",
        "precedence": 0,
        "created_at": NOW,
        "book_id": "SANMING-TONGHUI",
        "passage_id": "P-MK-KAIKU",
        "concept_id": "开库",
        "principle_id": "PRINCIPLE-WANGSHUAI",
        "scope": "八字旺衰判定(开库方式判据)",
    },
    "MK-104": {
        "rule_id": "MK-104",
        "title": "库中财官印透干→不需再冲",
        "rule_type": "旺衰判定",
        "source": {
            "work": "子平真诠",
            "chapter": "论杂气用事",
            "location": "杂气透干不需冲",
        },
        "conditions": {
            "all": [
                {"field": "month_branch", "op": "in", "value": ["CHEN", "XU", "CHOU", "WEI"]},
                {"field": "month_hidden_main_ten_god", "op": "nin", "value": ["比肩", "劫财"]},
                {"field": "transparent_ten_gods", "op": "has_any", "value": [["正财", "偏财"], ["正官", "七杀"], ["正印", "偏印"]]},
            ]
        },
        "conclusion": {
            "rationale_classical": "《子平真诠》:杂气透干汇之,岂不甚美,又何劳行冲乎!库中财官印已透干则不需再冲。",
            "produces_layer_output_template": {"direction": "STABLE", "polarity": "neutral"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "SUPPORT",
        "forbidden_inferences": [],
        "evidence_refs": ["E-MK-104-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.0.0",
        "precedence": 0,
        "created_at": NOW,
        "book_id": "ZIPINGZHENQUAN",
        "passage_id": "P-MK-ZAGI",
        "concept_id": "杂气格",
        "principle_id": "PRINCIPLE-WANGSHUAI",
        "scope": "八字旺衰判定(杂气透干)",
    },
    "MK-105": {
        "rule_id": "MK-105",
        "title": "库根透出后逢冲→余气尽伤",
        "rule_type": "旺衰判定",
        "source": {
            "work": "滴天髓",
            "chapter": "通神论·衰旺",
            "location": "库根逢冲",
        },
        "conditions": {
            "all": [
                {"field": "month_branch", "op": "in", "value": ["CHEN", "XU", "CHOU", "WEI"]},
                {"field": "day_branch", "op": "in", "value": ["CHEN", "XU", "CHOU", "WEI"]},
                {"field": "month_hidden_main_ten_god", "op": "in", "value": ["正印", "偏印", "比肩", "劫财"]},
            ]
        },
        "conclusion": {
            "rationale_classical": "《滴天髓》:天干只得一库根,逢冲则余气尽伤。库根透出后逢冲,根基不稳。",
            "produces_layer_output_template": {"direction": "DECLINE", "polarity": "caution"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "CONSTRAINT",
        "forbidden_inferences": [],
        "evidence_refs": ["E-MK-105-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.0.0",
        "precedence": 0,
        "created_at": NOW,
        "book_id": "DITIANSUI",
        "passage_id": "P-MK-KUGEN",
        "concept_id": "库根",
        "principle_id": "PRINCIPLE-WANGSHUAI",
        "scope": "八字旺衰判定(库根被冲)",
    },
    # ---- P1: 合化条件 (BASELINE) ----
    "HH-101": {
        "rule_id": "HH-101",
        "title": "合化需得令(化神得月令旺气)",
        "rule_type": "格局判定",
        "source": {
            "work": "三命通会",
            "chapter": "论十神化气",
            "location": "化气格成格条件",
        },
        "conditions": {
            "all": [
                {"field": "day_master_stage_month", "op": "in", "value": ["临官", "帝旺", "长生"]},
            ]
        },
        "conclusion": {
            "rationale_classical": "《三命通会》论十神化气:甲己化土非辰戌丑未月不化,丁壬化木非寅卯月不化。合化必须得令。",
            "produces_layer_output_template": {"direction": "STABLE", "polarity": "active"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "SUPPORT",
        "forbidden_inferences": [],
        "evidence_refs": ["E-HH-101-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.0.0",
        "precedence": 0,
        "created_at": NOW,
        "book_id": "SANMING-TONGHUI",
        "passage_id": "P-HH-HUAQI",
        "concept_id": "化气格",
        "principle_id": "PRINCIPLE-HUAQI",
        "scope": "格局判定(合化得令)",
    },
    "HH-102": {
        "rule_id": "HH-102",
        "title": "合化需双方能量相当,差距大则合绊",
        "rule_type": "格局判定",
        "source": {
            "work": "三命通会",
            "chapter": "论化气",
            "location": "化气格通论",
        },
        "conditions": {
            "all": [
                {"field": "month_hidden_main_ten_god", "op": "in", "value": ["正印", "偏印", "比肩", "劫财", "正官", "七杀", "正财", "偏财", "食神", "伤官"]},
            ]
        },
        "conclusion": {
            "rationale_classical": "化气格通论:合化需双方能量相当;差距大则只合不化(合绊)。",
            "produces_layer_output_template": {"direction": "STABLE", "polarity": "neutral"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "CONSTRAINT",
        "forbidden_inferences": [],
        "evidence_refs": ["E-HH-102-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.0.0",
        "precedence": 0,
        "created_at": NOW,
        "book_id": "SANMING-TONGHUI",
        "passage_id": "P-HH-HEBAN",
        "concept_id": "合绊",
        "principle_id": "PRINCIPLE-HUAQI",
        "scope": "格局判定(合化能量均衡)",
    },
    "HH-103": {
        "rule_id": "HH-103",
        "title": "合而能化才论化神,否则仅合绊",
        "rule_type": "格局判定",
        "source": {
            "work": "三命通会",
            "chapter": "论化气",
            "location": "合而不化",
        },
        "conditions": {
            "not": {
                "all": [
                    {"field": "day_master_stage_month", "op": "in", "value": ["临官", "帝旺", "长生"]},
                ]
            }
        },
        "conclusion": {
            "rationale_classical": "《三命通会》:合而能化才论化神,否则仅合绊(合而不化)。",
            "produces_layer_output_template": {"direction": "STABLE", "polarity": "neutral"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "CONSTRAINT",
        "forbidden_inferences": [],
        "evidence_refs": ["E-HH-103-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.0.0",
        "precedence": 0,
        "created_at": NOW,
        "book_id": "SANMING-TONGHUI",
        "passage_id": "P-HH-HEER",
        "concept_id": "合而不化",
        "principle_id": "PRINCIPLE-HUAQI",
        "scope": "格局判定(合而不化)",
    },
    # ---- P1: 四柱宫位 (BASELINE, structural only) ----
    "GW-101": {
        "rule_id": "GW-101",
        "title": "年柱=祖上/根基/事业(16岁前)",
        "rule_type": "十神定性",
        "source": {
            "work": "渊海子平",
            "chapter": "论四柱宫位",
            "location": "年柱宫位",
        },
        "conditions": {
            "all": [
                {"field": "birth_year_stem", "op": "exists", "value": True},
            ]
        },
        "conclusion": {
            "rationale_classical": "《渊海子平》《五行精纪》:年柱为根祖上,主16岁前气运、出身根基。",
            "produces_layer_output_template": {"direction": "STABLE", "polarity": "neutral"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "REFLECTION",
        "forbidden_inferences": [],
        "evidence_refs": ["E-GW-101-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.0.0",
        "precedence": 0,
        "created_at": NOW,
        "book_id": "YUANHAIZIPING",
        "passage_id": "P-GW-NIANZHU",
        "concept_id": "四柱宫位",
        "principle_id": "PRINCIPLE-GONGWEI",
        "scope": "四柱宫位(年柱)",
    },
    "GW-102": {
        "rule_id": "GW-102",
        "title": "月柱=父母/成长/教育/兄弟(青年)",
        "rule_type": "十神定性",
        "source": {
            "work": "渊海子平",
            "chapter": "论四柱宫位",
            "location": "月柱宫位",
        },
        "conditions": {
            "all": [
                {"field": "month_stem", "op": "exists", "value": True},
            ]
        },
        "conclusion": {
            "rationale_classical": "《渊海子平》《五行精纪》:月柱为父母兄弟宫,主青年时期成长教育。",
            "produces_layer_output_template": {"direction": "STABLE", "polarity": "neutral"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "REFLECTION",
        "forbidden_inferences": [],
        "evidence_refs": ["E-GW-102-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.0.0",
        "precedence": 0,
        "created_at": NOW,
        "book_id": "YUANHAIZIPING",
        "passage_id": "P-GW-YUEZHU",
        "concept_id": "四柱宫位",
        "principle_id": "PRINCIPLE-GONGWEI",
        "scope": "四柱宫位(月柱)",
    },
    "GW-103": {
        "rule_id": "GW-103",
        "title": "日柱=自我/夫妻宫/身体/居住(中年)",
        "rule_type": "十神定性",
        "source": {
            "work": "渊海子平",
            "chapter": "论四柱宫位",
            "location": "日柱宫位",
        },
        "conditions": {
            "all": [
                {"field": "day_master", "op": "exists", "value": True},
            ]
        },
        "conclusion": {
            "rationale_classical": "《渊海子平》《五行精纪》:日柱为己身夫妻宫,主中年心性定型。",
            "produces_layer_output_template": {"direction": "STABLE", "polarity": "neutral"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "REFLECTION",
        "forbidden_inferences": [],
        "evidence_refs": ["E-GW-103-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.0.0",
        "precedence": 0,
        "created_at": NOW,
        "book_id": "YUANHAIZIPING",
        "passage_id": "P-GW-RIZHU",
        "concept_id": "四柱宫位",
        "principle_id": "PRINCIPLE-GONGWEI",
        "scope": "四柱宫位(日柱)",
    },
    "GW-104": {
        "rule_id": "GW-104",
        "title": "时柱=子女/果报/未来(晚年)",
        "rule_type": "十神定性",
        "source": {
            "work": "渊海子平",
            "chapter": "论四柱宫位",
            "location": "时柱宫位",
        },
        "conditions": {
            "all": [
                {"field": "hour_stem", "op": "exists", "value": True},
            ]
        },
        "conclusion": {
            "rationale_classical": "《渊海子平》《五行精纪》:时柱为子女果报宫,主晚年运势。",
            "produces_layer_output_template": {"direction": "STABLE", "polarity": "neutral"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "REFLECTION",
        "forbidden_inferences": [],
        "evidence_refs": ["E-GW-104-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.0.0",
        "precedence": 0,
        "created_at": NOW,
        "book_id": "YUANHAIZIPING",
        "passage_id": "P-GW-SHIZHU",
        "concept_id": "四柱宫位",
        "principle_id": "PRINCIPLE-GONGWEI",
        "scope": "四柱宫位(时柱)",
    },
    # ---- P1: 三刑专项 (EVENT_TOPIC) ----
    "SX-101": {
        "rule_id": "SX-101",
        "title": "寅巳申三字汇聚→时空秩序紊乱",
        "rule_type": "健康断事",
        "source": {
            "work": "五行精纪",
            "chapter": "卷廿五·论三刑",
            "location": "无恩之刑",
        },
        "conditions": {
            "all": [
                {"field": "branch_clash_map", "op": "has_all", "value": ["YIN", "SI", "SHEN"]},
            ]
        },
        "conclusion": {
            "rationale_classical": "《五行精纪》卷廿五:寅刑巳、巳刑申、申刑寅,循环相克,天地乖气,无恩之刑。时空秩序紊乱、天干发用不能长效。",
            "produces_layer_output_template": {"direction": "DECLINE", "polarity": "caution"},
        },
        "applies_to_layers": ["EVENT_TOPIC"],
        "produces_signal_type": "HEALTH_RISK",
        "forbidden_inferences": [],
        "evidence_refs": ["E-SX-101-001"],
        "status": "active",
        "spec_decisions_ref": ["DECISION-013"],
        "version": "1.0.0",
        "precedence": 5,
        "created_at": NOW,
        "book_id": "WUXINGJINGJI",
        "passage_id": "P-SX-WUEN",
        "concept_id": "三刑",
        "principle_id": "PRINCIPLE-XINGCHONG",
        "scope": "健康断事 / 三刑无恩刑",
        "scenario": "MARRIAGE_HEALTH",
    },
    "SX-102": {
        "rule_id": "SX-102",
        "title": "三刑方向区分:各刑取象破坏根基",
        "rule_type": "健康断事",
        "source": {
            "work": "五行精纪",
            "chapter": "卷廿五·论三刑",
            "location": "三刑方向",
        },
        "conditions": {
            "any": [
                {"all": [{"field": "day_branch", "op": "eq", "value": "YIN"}, {"field": "month_branch", "op": "in", "value": ["SI", "SHEN"]}]},
                {"all": [{"field": "day_branch", "op": "eq", "value": "SI"}, {"field": "month_branch", "op": "in", "value": ["YIN", "SHEN"]}]},
                {"all": [{"field": "day_branch", "op": "eq", "value": "SHEN"}, {"field": "month_branch", "op": "in", "value": ["YIN", "SI"]}]},
            ]
        },
        "conclusion": {
            "rationale_classical": "《五行精纪》:三刑方向区分,寅刑巳取巳中金土,巳刑寅取寅中土火,各破坏根基。",
            "produces_layer_output_template": {"direction": "DECLINE", "polarity": "caution"},
        },
        "applies_to_layers": ["EVENT_TOPIC"],
        "produces_signal_type": "HEALTH_RISK",
        "forbidden_inferences": [],
        "evidence_refs": ["E-SX-102-001"],
        "status": "active",
        "spec_decisions_ref": ["DECISION-013"],
        "version": "1.0.0",
        "precedence": 5,
        "created_at": NOW,
        "book_id": "WUXINGJINGJI",
        "passage_id": "P-SX-FANGXIANG",
        "concept_id": "三刑",
        "principle_id": "PRINCIPLE-XINGCHONG",
        "scope": "健康断事 / 三刑方向",
        "scenario": "MARRIAGE_HEALTH",
    },
    # ---- P1: 旺衰单因子修正 (DTS-106/107) ----
    "DTS-106": {
        "rule_id": "DTS-106",
        "title": "得令但月令被围克→身弱",
        "rule_type": "旺衰判定",
        "source": {
            "work": "滴天髓",
            "edition": "通行本(任铁樵《滴天髓阐微》)",
            "chapter": "通神论·衰旺",
            "location": "月令被围克",
        },
        "conditions": {
            "all": [
                {"field": "month_hidden_main_ten_god", "op": "in", "value": ["正印", "偏印", "比肩", "劫财"]},
                {"field": "day_branch_clash", "op": "eq", "value": True},
            ]
        },
        "conclusion": {
            "rationale_classical": "《滴天髓》:生方怕动库宜开,败地逢冲仔细推。月令虽得令但被围克(如午月被子水围克),得令不成立,反断身弱。",
            "produces_layer_output_template": {"direction": "DECREASE", "polarity": "restricted"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "CONSTRAINT",
        "forbidden_inferences": [],
        "evidence_refs": ["E-DTS-106-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.1.0",
        "precedence": 5,
        "created_at": NOW,
        "book_id": "DITIANSUI",
        "passage_id": "P-DTS-SHUAIWANG",
        "concept_id": "旺衰",
        "principle_id": "PRINCIPLE-WANGSHUAI",
        "scope": "八字旺衰判定(月令被围克修正)",
    },
    "DTS-107": {
        "rule_id": "DTS-107",
        "title": "失令但有强根/帮扶→身偏强",
        "rule_type": "旺衰判定",
        "source": {
            "work": "滴天髓",
            "edition": "通行本(任铁樵《滴天髓阐微》)",
            "chapter": "通神论·衰旺",
            "location": "三辨综合判定",
        },
        "conditions": {
            "all": [
                {"field": "month_hidden_main_ten_god", "op": "in", "value": ["正官", "七杀", "正财", "偏财", "食神", "伤官"]},
                {"field": "day_branch_main_ten_god", "op": "in", "value": ["比肩", "劫财", "正印", "偏印"]},
            ]
        },
        "conclusion": {
            "rationale_classical": "《滴天髓》三辨综合判定:失令但有强根强势(日支通根+天干比劫林立),仍身偏强。",
            "produces_layer_output_template": {"direction": "INCREASE", "polarity": "active"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "SUPPORT",
        "forbidden_inferences": [],
        "evidence_refs": ["E-DTS-107-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.1.0",
        "precedence": 5,
        "created_at": NOW,
        "book_id": "DITIANSUI",
        "passage_id": "P-DTS-SHUAIWANG",
        "concept_id": "旺衰",
        "principle_id": "PRINCIPLE-WANGSHUAI",
        "scope": "八字旺衰判定(失令有根修正)",
    },
    # ---- P2: 天乙贵人温和降级 (SMTH-104V2) ----
    "SMTH-105": {
        "rule_id": "SMTH-105",
        "title": "天乙贵人逢冲/空亡→SUPPORT降级为LIKELY",
        "rule_type": "神煞判定",
        "source": {
            "work": "三命通会",
            "edition": "通行本(十二卷)",
            "chapter": "论天乙贵人",
            "location": "贵人逢冲",
        },
        "conditions": {
            "all": [
                {"field": "tianyi_guiren_branches", "op": "exists", "value": True},
                {"field": "day_branch_clash", "op": "eq", "value": True},
            ]
        },
        "conclusion": {
            "rationale_classical": "《三命通会》:天乙者乃天上之神,一切凶煞隐然而避。但贵人逢冲则力减半,温和降级为LIKELY(不引入逢冲转凶硬编码)。",
            "produces_layer_output_template": {"direction": "STABLE", "polarity": "active"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "SUPPORT",
        "forbidden_inferences": [],
        "evidence_refs": ["E-SMTH-104V2-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.1.0",
        "precedence": 3,
        "created_at": NOW,
        "book_id": "SANMING-TONGHUI",
        "passage_id": "P-SMTH-TIANYI",
        "concept_id": "天乙贵人",
        "principle_id": "PRINCIPLE-SHENSHA",
        "scope": "神煞判定(天乙贵人温和降级)",
    },
    # ---- P2: 禄命法 (LM-101) ----
    "LM-101": {
        "rule_id": "LM-101",
        "title": "年柱为太极点:祖上气运/出身根基(禄命法独立维度)",
        "rule_type": "十神定性",
        "source": {
            "work": "五行精纪",
            "chapter": "论三命",
            "location": "干配禄支合命纳音论身",
        },
        "conditions": {
            "all": [
                {"field": "birth_year_stem", "op": "exists", "value": True},
            ]
        },
        "conclusion": {
            "rationale_classical": "《五行精纪》《李虚中命书》:干配禄,以支合命,以纳音论身,之谓三命。年柱为太极点,看祖上气运/出身根基(独立于日柱子平层)。",
            "produces_layer_output_template": {"direction": "STABLE", "polarity": "neutral"},
        },
        "applies_to_layers": ["BASELINE"],
        "produces_signal_type": "REFLECTION",
        "forbidden_inferences": [],
        "evidence_refs": ["E-LM-101-001"],
        "status": "draft",
        "spec_decisions_ref": ["DECISION-002", "DECISION-006", "DECISION-009"],
        "version": "1.0.0",
        "precedence": 0,
        "created_at": NOW,
        "book_id": "WUXINGJINGJI",
        "passage_id": "P-LM-SANMING",
        "concept_id": "禄命法",
        "principle_id": "PRINCIPLE-SANMING",
        "scope": "禄命法框架(年柱太极点)",
    },
    # ---- P2: 玄学天赋 (TF-101/102, EVENT_TOPIC) ----
    "TF-101": {
        "rule_id": "TF-101",
        "title": "偏印强于正印出玄学天赋;偏印不可临正官",
        "rule_type": "神煞判定",
        "source": {
            "work": "工程种子",
            "chapter": "玄学天赋正解",
            "location": "偏印正印对比",
        },
        "conditions": {
            "all": [
                {"field": "month_hidden_main_ten_god", "op": "eq", "value": "偏印"},
            ]
        },
        "conclusion": {
            "rationale_classical": "字幕《玄学天赋正解》:偏印强于正印出玄学天赋;偏印不可临正官(格局破)。",
            "produces_layer_output_template": {"direction": "INCREASE", "polarity": "opportunity"},
        },
        "applies_to_layers": ["EVENT_TOPIC"],
        "produces_signal_type": "SUPPORT",
        "forbidden_inferences": [],
        "evidence_refs": ["E-TF-101-001"],
        "status": "active",
        "spec_decisions_ref": ["DECISION-013"],
        "version": "1.0.0",
        "precedence": 3,
        "created_at": NOW,
        "passage_id": "P-TF-XUANXUE",
        "concept_id": "玄学天赋",
        "principle_id": "PRINCIPLE-TALENT",
        "scope": "玄学天赋(偏印判定)",
        "scenario": "SELF_AWAKENING_TALENT",
    },
    "TF-102": {
        "rule_id": "TF-102",
        "title": "印食伤需相融(燥土印×寒水食伤则相斥)",
        "rule_type": "神煞判定",
        "source": {
            "work": "工程种子",
            "chapter": "玄学天赋正解",
            "location": "印食伤相融",
        },
        "conditions": {
            "all": [
                {"field": "month_hidden_main_ten_god", "op": "in", "value": ["正印", "偏印"]},
                {"field": "day_branch_main_ten_god", "op": "in", "value": ["食神", "伤官"]},
            ]
        },
        "conclusion": {
            "rationale_classical": "《子平真诠》《滴天髓》:印星与食伤需五行调和。燥土之印克寒水之食伤则相斥(天赋阻塞);燥土印配燥土食伤则相融(天赋发挥)。",
            "produces_layer_output_template": {"direction": "STABLE", "polarity": "neutral"},
        },
        "applies_to_layers": ["EVENT_TOPIC"],
        "produces_signal_type": "SUPPORT",
        "forbidden_inferences": [],
        "evidence_refs": ["E-TF-102-001"],
        "status": "active",
        "spec_decisions_ref": ["DECISION-013"],
        "version": "1.0.0",
        "precedence": 3,
        "created_at": NOW,
        "passage_id": "P-TF-YINSHI",
        "concept_id": "玄学天赋",
        "principle_id": "PRINCIPLE-TALENT",
        "scope": "玄学天赋(印食伤调和)",
        "scenario": "SELF_AWAKENING_TALENT",
    },
}

# --------------------------------------------------------------------------- #
# Write all files
# --------------------------------------------------------------------------- #
def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    # Write evidence files
    for eid, edata in EVIDENCE.items():
        p = EVIDENCE_DIR / f"{eid}.json"
        write_json(p, edata)
        print(f"Wrote evidence: {p.name}")

    # Write rule files
    for rid, rdata in RULES.items():
        p = RULES_DIR / f"{rid}.json"
        write_json(p, rdata)
        print(f"Wrote rule: {p.name}")

    print(f"\nTotal evidence: {len(EVIDENCE)}")
    print(f"Total rules: {len(RULES)}")


if __name__ == "__main__":
    main()
