"""Z77: 辅曜/煞曜/杂曜断语层。

对齐 palace_star_verdicts.py 结构，但遵守"无原文不入规则"：
- 有原典出处的：填原文 + source
- 无原典出处的：标 EVIDENCE_GAP，不硬填

星曜类别：
- 辅曜：左辅、右弼、文昌、文曲、天魁、天钺、禄存、天马
- 煞曜：擎羊、陀罗、火星、铃星、地空、地劫
- 杂曜：天刑、天姚、天伤、天使、天哭、天虚、红鸾、天喜、龙池、凤阁、台辅、封诰、三台、八座

来源：《紫微斗数全书·诸星问答论》（待逐星录入原文）
"""
from __future__ import annotations

# EVIDENCE_GAP: 原典原文未录入，不硬填断语
# 每条结构：(star, palace, verbatim, source, status)
# status: "VERIFIED" | "EVIDENCE_GAP"

# 辅曜
AUX_STAR_VERDICTS = [
    # 左辅右弼——《全书》有论，待逐宫原文录入
    {"star": "左辅", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
    {"star": "右弼", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
    # 文昌文曲
    {"star": "文昌", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
    {"star": "文曲", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
    # 天魁天钺
    {"star": "天魁", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
    {"star": "天钺", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
    # 禄存天马
    {"star": "禄存", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
    {"star": "天马", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
]

# 煞曜
SHA_STAR_VERDICTS = [
    {"star": "擎羊", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
    {"star": "陀罗", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
    {"star": "火星", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
    {"star": "铃星", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
    {"star": "地空", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
    {"star": "地劫", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
]

# 杂曜
MISC_STAR_VERDICTS = [
    {"star": "天刑", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
    {"star": "天姚", "palace": "命宫", "verbatim": "", "source": "紫微斗数全书·诸星问答论", "status": "EVIDENCE_GAP"},
]

# 汇总
ALL_AUX_STARS = list({x["star"] for x in AUX_STAR_VERDICTS})
ALL_SHA_STARS = list({x["star"] for x in SHA_STAR_VERDICTS})
ALL_MISC_STARS = list({x["star"] for x in MISC_STAR_VERDICTS})


def count_verified() -> int:
    return sum(1 for x in AUX_STAR_VERDICTS + SHA_STAR_VERDICTS + MISC_STAR_VERDICTS if x["status"] == "VERIFIED")


def count_gap() -> int:
    return sum(1 for x in AUX_STAR_VERDICTS + SHA_STAR_VERDICTS + MISC_STAR_VERDICTS if x["status"] == "EVIDENCE_GAP")
