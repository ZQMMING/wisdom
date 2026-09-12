
"""
Qintian Evidence Bindings — 钦天门证据等级与一手源 (P0-7)

严格工程边界：
- 每条规则绑定 grade=1 一手源（许铨仁 / 四余独步钦天四化讲义）
- grade=3+ 后人整理只作 DRAFT/CANDIDATE 不进 production
- 所有 5 条 production 规则必须有 verbatim 原文出处
- 来源 URL 用作 evidence trace

5 条 production (grade=1):
  - QTN-CMB-001 来因宫 = 生年干所在宫位（许铨仁 A02 四化象）
  - QTN-CMB-002 生年四化宫=空间 / 自化=时间（钦天核心时空观）
  - QTN-CMB-003 立太极 (Xuanji)
  - QTN-CMB-004 向心自化注脚在对宫
  - QTN-CMB-005 忌入六亲宫=亏欠

5 条 DRAFT (grade=3+):
  - 串联自化 (四余独步)
  - 离心自化十二地支分布
  - 十二宫生年四化逐宫详释
  - 子/丑不做来因宫例外
  - 化忌多变动推论

所有 production 规则只接受 grade<=2 进 evidence_grade 字段。
"""

from __future__ import annotations

from typing import Dict, NamedTuple
from dataclasses import dataclass


class QintianEvidence(NamedTuple):
    """钦天门证据 binding (NamedTuple 保持 immutable)"""
    rule_id: str
    title: str
    verbatim_quote: str
    source: str
    source_url: str
    grade: int  # 1=许铨仁/四余独步原文 2=陆斌兆/王亭之传承 3=后人整理 4=推演
    evidence_type: str  # PRIMARY_TRADITION / SYSTEMATIZED / CANDIDATE


# ============================================================
# 5 条 production (grade=1) — 钦天门一手原文证据
# ============================================================

EVIDENCE_BINDINGS: Dict[str, QintianEvidence] = {
    "QTN-CMB-001": QintianEvidence(
        rule_id="QTN-CMB-001",
        title="来因宫 = 生年干所在宫位",
        verbatim_quote="来因宫就是生年干所在的宫位",
        source="许铨仁《钦天四化紫微斗数命理学》A02 四化象",
        source_url="https://m.douban.com/group/topic/116690133",
        grade=1,
        evidence_type="PRIMARY_TRADITION",
    ),
    "QTN-CMB-002": QintianEvidence(
        rule_id="QTN-CMB-002",
        title="生年四化=空间(体) / 自化=时间(用)",
        verbatim_quote="拿到一个盘，先看来因+生年四化宫，这决定了我们的生存空间。而自化是决定事情的发生时间。前者是空间，后者是时空。",
        source="四余独步《钦天四化紫微斗数讲义》第一课",
        source_url="https://www.ziweicn.com/yiyuxinshu/book/4186.html",
        grade=1,
        evidence_type="PRIMARY_TRADITION",
    ),
    "QTN-CMB-003": QintianEvidence(
        rule_id="QTN-CMB-003",
        title="立太极(中太极)：每宫可立新命宫",
        verbatim_quote="以夫妻宫立太极，财帛宫是夫妻宫的夫妻宫。这个中太极里面有命宫、兄弟宫还有化禄象。",
        source="许铨仁《钦天四化紫微斗数命理学》A03 化禄象基本含义",
        source_url="https://m.douban.com/group/topic/116690133",
        grade=1,
        evidence_type="PRIMARY_TRADITION",
    ),
    "QTN-CMB-004": QintianEvidence(
        rule_id="QTN-CMB-004",
        title="向心自化注脚在对宫",
        verbatim_quote="箭头由本宫发射到对宫，是向心自化，向心自化重点注脚在对宫，比如福德向心到财帛，注脚在财帛宫，命宫向心到迁移，注脚在迁移宫。",
        source="四余独步《钦天四化紫微斗数讲义》第一课",
        source_url="https://www.ziweicn.com/yiyuxinshu/book/4186.html",
        grade=1,
        evidence_type="PRIMARY_TRADITION",
    ),
    "QTN-CMB-005": QintianEvidence(
        rule_id="QTN-CMB-005",
        title="化忌入六亲宫 = 潜意识亏欠",
        verbatim_quote="化忌入六亲宫主亏欠。若生年化忌落在兄弟代表我本人对兄弟姐妹潜意识有亏欠的感觉。",
        source="许铨仁《钦天四化紫微斗数命理学》A06-07 化忌象基本含义",
        source_url="https://m.douban.com/group/topic/116690133",
        grade=1,
        evidence_type="PRIMARY_TRADITION",
    ),
}


# ============================================================
# 5 条 DRAFT (grade=3+) — 不进 production, 占位拒绝
# ============================================================

DRAFT_BINDINGS: Dict[str, QintianEvidence] = {
    "QTN-CMB-006-DRAFT": QintianEvidence(
        rule_id="QTN-CMB-006-DRAFT",
        title="串联自化 (DRAFT)",
        verbatim_quote="颜色一样的同向自化叫串联。比如这个盘，官禄的太阴B和交友的贪狼A都自化B，叫串联。",
        source="四余独步《钦天四化紫微斗数讲义》",
        source_url="https://www.ziweicn.com/yiyuxinshu/book/4186.html",
        grade=3,
        evidence_type="CANDIDATE",
    ),
    "QTN-CMB-007-DRAFT": QintianEvidence(
        rule_id="QTN-CMB-007-DRAFT",
        title="离心自化十二地支分布 (DRAFT)",
        verbatim_quote="箭头向外是离心自化，比如午、未、申、酉、戌都有离心。",
        source="四余独步《钦天四化紫微斗数讲义》",
        source_url="https://www.ziweicn.com/yiyuxinshu/book/4186.html",
        grade=3,
        evidence_type="CANDIDATE",
    ),
    "QTN-CMB-008-DRAFT": QintianEvidence(
        rule_id="QTN-CMB-008-DRAFT",
        title="十二宫生年四化逐宫详释 (DRAFT)",
        verbatim_quote="（许铨仁 A03-A07 各宫详释 48 例）",
        source="许铨仁《钦天四化紫微斗数命理学》",
        source_url="https://m.douban.com/group/topic/116690133",
        grade=3,
        evidence_type="CANDIDATE",
    ),
    "QTN-CMB-009-DRAFT": QintianEvidence(
        rule_id="QTN-CMB-009-DRAFT",
        title="子/丑不做来因宫例外 (DRAFT)",
        verbatim_quote="（备注：子，丑位不做来因宫）",
        source="四余独步《钦天四化紫微斗数讲义》",
        source_url="https://www.ziweicn.com/yiyuxinshu/book/4186.html",
        grade=3,
        evidence_type="CANDIDATE",
    ),
    "QTN-CMB-010-DRAFT": QintianEvidence(
        rule_id="QTN-CMB-010-DRAFT",
        title="化忌多变动推论 (DRAFT)",
        verbatim_quote="化忌主多变动、多变迁又含有动荡不安",
        source="许铨仁《钦天四化紫微斗数命理学》",
        source_url="https://m.douban.com/group/topic/116690133",
        grade=3,
        evidence_type="CANDIDATE",
    ),
}


def get_evidence(rule_id: str) -> QintianEvidence | None:
    """根据 rule_id 获取 evidence binding (production only)"""
    return EVIDENCE_BINDINGS.get(rule_id)


def is_production_rule(rule_id: str) -> bool:
    """判断 rule_id 是否为钦天 production 规则"""
    return rule_id in EVIDENCE_BINDINGS
