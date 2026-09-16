"""Z80b: 时间层 Evidence/Rule——《紫微斗数全书》时间层解释。

Fact 来自 temporal_facts.py，本文件只接解释。
不做成"流曜=吉凶"，保留传统条件结构：
  流曜 + 落宫 + 本宫星曜 + 庙旺 + 化吉化忌 → Rule → Assertion

来源：《紫微斗数全书》卷二/卷三
- 论太岁小限星辰庙陷遇十二宫中吉凶第九十六
- 安斗君诀第四十三
- 安流禄流羊流陀诀第五十七
"""
from __future__ import annotations

SRC = "紫微斗数全书·卷二"

# ============================================================
# 小限 / 太岁 Rule
# ============================================================
# 原典第九十六：太岁+小限到某宫，看本宫星曜庙旺化吉化忌
# 不逐宫录48条（太长），先录核心原则+代表宫位

TAISUI_XIAOXIAN_RULES = [
    {
        "rule_id": "TMPL-01",
        "name": "太岁小限到子宫",
        "school": "CLASSICAL_SOURCE",
        "source": SRC,
        "source_section": "论太岁小限星辰庙陷遇十二宫中吉凶第九十六",
        "verbatim": "子年太岁并小限到子宫入庙化吉：七杀破军在子宫守岁限癸庚己生人发福；巨门天机乙癸生人发福；天府天相天梁丁己庚人财旺遂心；天同丙丁生人财官双美。",
        "condition": "太岁宫=子 且 小限宫=子",
        "good_stars": ["七杀","破军","巨门","天机","天府","天相","天梁","天同"],
        "bad_stars": ["紫微"],
    },
    {
        "rule_id": "TMPL-02",
        "name": "太岁小限到子宫化凶",
        "school": "CLASSICAL_SOURCE",
        "source": SRC,
        "source_section": "论太岁小限星辰庙陷遇十二宫中吉凶第九十六",
        "verbatim": "子年太岁并小限到子宫不入庙化凶：紫微在子宫守命及岁限丙戊生人悔吝，破财灾殃。",
        "condition": "太岁宫=子 且 小限宫=子 且 落陷化凶",
        "bad_stars": ["紫微"],
    },
    {
        "rule_id": "TMPL-03",
        "name": "太岁所值吉凶星总则",
        "school": "CLASSICAL_SOURCE",
        "source": SRC,
        "source_section": "论太岁小限星辰庙陷遇十二宫中吉凶第九十六",
        "verbatim": "子年太岁所值吉凶星：禄存天机天同太阴昌曲辅弼破军天相廉真武曲天府巨门七杀，可断其年人财两美事事遂心。若遇贪狼紫微天梁忌星太阳擎羊，便断人财耗散孝服，本身灾晦不宁，减半论之。",
        "condition": "太岁宫星曜吉凶分类",
        "good_stars": ["禄存","天机","天同","太阴","文昌","文曲","左辅","右弼","破军","天相","廉贞","武曲","天府","巨门","七杀"],
        "bad_stars": ["贪狼","紫微","天梁","化忌","太阳","擎羊"],
    },
]

# ============================================================
# 斗君 Rule
# ============================================================
DOUJUN_RULES = [
    {
        "rule_id": "TDJ-01",
        "name": "斗君=月将星",
        "school": "CLASSICAL_SOURCE",
        "source": SRC,
        "source_section": "安斗君诀第四十三",
        "verbatim": "即月将星是也。于流年太岁宫起正月逆至本生月，又从本生月起子顺数至本生时安斗君。",
        "condition": "斗君宫位=月将，定流月吉凶",
        "note": "Fact层已算，本Rule只作概念定义，不作吉凶断",
    },
]

# ============================================================
# 流禄/流羊/流陀 Rule
# ============================================================
LIUYAO_RULES = [
    {
        "rule_id": "TLY-01",
        "name": "流禄=流年干禄存",
        "school": "CLASSICAL_SOURCE",
        "source": SRC,
        "source_section": "安流禄流羊流陀诀第五十七",
        "verbatim": "论流年太岁。假如己丑流年流禄在午、流羊在未、流陀在巳。",
        "condition": "流禄=流年干禄存所在地支",
        "note": "流禄主年吉庆，落宫看本宫星曜",
    },
    {
        "rule_id": "TLY-02",
        "name": "流羊=流年干擎羊",
        "school": "CLASSICAL_SOURCE",
        "source": SRC,
        "source_section": "安流禄流羊流陀诀第五十七",
        "verbatim": "流羊在未（己丑年）。",
        "condition": "流羊=流年干擎羊所在地支",
        "note": "流羊主年刑伤，落宫看本宫星曜",
    },
    {
        "rule_id": "TLY-03",
        "name": "流陀=流年干陀罗",
        "school": "CLASSICAL_SOURCE",
        "source": SRC,
        "source_section": "安流禄流羊流陀诀第五十七",
        "verbatim": "流陀在巳（己丑年）。",
        "condition": "流陀=流年干陀罗所在地支",
        "note": "流陀主年拖延暗损，落宫看本宫星曜",
    },
]

# 汇总
ALL_TEMPORAL_RULES = TAISUI_XIAOXIAN_RULES + DOUJUN_RULES + LIUYAO_RULES


def count() -> dict:
    return {
        "taisui_xiaoxian": len(TAISUI_XIAOXIAN_RULES),
        "doujun": len(DOUJUN_RULES),
        "liuyao": len(LIUYAO_RULES),
        "total": len(ALL_TEMPORAL_RULES),
    }
