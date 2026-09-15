# -*- coding: utf-8 -*-
"""
Qintian Evidence Bindings — 钦天门证据等级与一手源（Z44 蔡明宏主源版）

严格工程边界：
- 每条规则绑定 grade=1 一手源（蔡明宏《悟我十八年》OCR 原文）
- 铁律：原著古书原文为准，不采今人推测口径
- Z44 主源切换：许铨仁/四余独步规则全部清除（书不在 D 盘，无法溯源），
  唯一北派主源 = 蔡明宏《悟我十八年》（正文完整 + PDF 原件在）

8 条 production（grade=1，全部蔡明宏原文）：
  - QTN-CMB-001 来因宫 = 生年干所在宫位（"太极引用在斗数上即来因宫"）
  - QTN-CMB-002 生年四化=空间(体) / 自化=时间(用)
  - QTN-CMB-004 向心自化（箭头向内，物质的凝聚）
  - QTN-CMB-006 串联自化（同向自化串联）
  - QTN-CMB-007 离心自化（箭头向外，物质的分散）
  - QTN-CMB-011 自化五分类（生年有/无自化 × 飞宫遇/不遇）
  - QTN-CMB-012 出与入（自化面对生年四化的出入）
  - QTN-CMB-013 法象（自化之象对照生年四化宫位）

已清除（许铨仁/四余独步，蔡明宏书无）：
  - 003 立太极（蔡明宏"太极"=来因宫，非每宫立新命宫）
  - 005 忌入六亲=亏欠（书无"亏欠"表述）
  - 008 十二宫逐宫详释（结构不同）
  - 009 子/丑不做来因宫（蔡明宏"每个人于命盘都有来因宫"直接矛盾）
  - 010 化忌多变动（书无此表述）

所有 production 规则 evidence_grade=1（一手原文）。
"""

from __future__ import annotations

from typing import Dict, NamedTuple


class QintianEvidence(NamedTuple):
    """钦天门证据 binding (NamedTuple 保持 immutable)"""
    rule_id: str
    title: str
    verbatim_quote: str
    source: str
    source_url: str
    grade: int  # 1=蔡明宏《悟我十八年》原文 2=传承整理 3=后人整理 4=推演
    evidence_type: str  # PRIMARY_TRADITION / SYSTEMATIZED / CANDIDATE


EVIDENCE_BINDINGS: Dict[str, QintianEvidence] = {
    "QTN-CMB-001": QintianEvidence(
        rule_id="QTN-CMB-001",
        title="来因宫 = 生年干所在宫位",
        verbatim_quote="太极若引用在斗数上，所指的就是来因宫。（即宫位与出生的天干相同的宫位）。例 甲年生，甲在命盘的田宅宫，则田宅宫叫做来因宫。所以每个人于命盘都有来因宫，都有他自己的「太极」。",
        source="蔡明宏《悟我十八年》第四章 自化篇·单元二 导读（理）",
        source_url="D:\\顺天系统资料\\豆包资料\\六部经典校对版\\紫薇体系\\OCR转录版本\\蔡明宏_紫微斗数_悟我十八年_OCR_最终版.txt",
        grade=1,
        evidence_type="PRIMARY_TRADITION",
    ),
    "QTN-CMB-002": QintianEvidence(
        rule_id="QTN-CMB-002",
        title="生年四化=空间(体) / 自化=时间(用)",
        verbatim_quote="生年的象，是空间性的，叫做物的存在论。自化的象，是时间性的，叫做物的存在论。生年四化，就先有物（体）；生年四化又自化，是在已有之物后（体），再产生另一种变化（用），体用合一。",
        source="蔡明宏《悟我十八年》第四章 自化篇·单元一 引言 / 单元二 导读（气）",
        source_url="D:\\顺天系统资料\\豆包资料\\六部经典校对版\\紫薇体系\\OCR转录版本\\蔡明宏_紫微斗数_悟我十八年_OCR_最终版.txt",
        grade=1,
        evidence_type="PRIMARY_TRADITION",
    ),
    "QTN-CMB-004": QintianEvidence(
        rule_id="QTN-CMB-004",
        title="向心自化（箭头向内，物质的凝聚）",
        verbatim_quote="自化的游戏规则：向心力与离心力两种。箭头向内（向心力）。向心力→物质的凝聚。",
        source="蔡明宏《悟我十八年》第四章 自化篇·单元一 引言（自化的游戏规则）",
        source_url="D:\\顺天系统资料\\豆包资料\\六部经典校对版\\紫薇体系\\OCR转录版本\\蔡明宏_紫微斗数_悟我十八年_OCR_最终版.txt",
        grade=1,
        evidence_type="PRIMARY_TRADITION",
    ),
    "QTN-CMB-006": QintianEvidence(
        rule_id="QTN-CMB-006",
        title="串联自化",
        verbatim_quote="自化的游戏规则：（3）串联与不串联。飞宫不遇生年四化，但有自化者（并串联）。",
        source="蔡明宏《悟我十八年》第四章 自化篇·单元一 引言 / 单元三 应用篇",
        source_url="D:\\顺天系统资料\\豆包资料\\六部经典校对版\\紫薇体系\\OCR转录版本\\蔡明宏_紫微斗数_悟我十八年_OCR_最终版.txt",
        grade=1,
        evidence_type="PRIMARY_TRADITION",
    ),
    "QTN-CMB-007": QintianEvidence(
        rule_id="QTN-CMB-007",
        title="离心自化（箭头向外，物质的分散）",
        verbatim_quote="自化的游戏规则：向心力与离心力两种。箭头向外（离心力）。离心力→物质的分散。把已有的事物现象变成没有 或改变另一种模式。",
        source="蔡明宏《悟我十八年》第四章 自化篇·单元一 引言（自化的游戏规则）",
        source_url="D:\\顺天系统资料\\豆包资料\\六部经典校对版\\紫薇体系\\OCR转录版本\\蔡明宏_紫微斗数_悟我十八年_OCR_最终版.txt",
        grade=1,
        evidence_type="PRIMARY_TRADITION",
    ),
    "QTN-CMB-011": QintianEvidence(
        rule_id="QTN-CMB-011",
        title="自化五分类",
        verbatim_quote="（一）生年四化，有自化者。（包括来因宫本身自己有自化者）（二）生年四化，没有自化者。（三）无生年四化，有自化者。（四）飞宫遇生年四化，又有自化者。（五）飞宫不遇生年四化，但有自化者。（六）飞宫不遇生年四化，但有自化者。（并串联）。以上是现象的组合性。",
        source="蔡明宏《悟我十八年》第四章 自化篇·单元一 引言",
        source_url="D:\\顺天系统资料\\豆包资料\\六部经典校对版\\紫薇体系\\OCR转录版本\\蔡明宏_紫微斗数_悟我十八年_OCR_最终版.txt",
        grade=1,
        evidence_type="PRIMARY_TRADITION",
    ),
    "QTN-CMB-012": QintianEvidence(
        rule_id="QTN-CMB-012",
        title="出与入",
        verbatim_quote="站在太阴化禄的流年（酉宫）去面对巨门的自化禄是'入'。站在巨门的自化禄去面对太阴的化禄是'出'。",
        source="蔡明宏《悟我十八年》第四章 自化篇·单元一 引言（出与入的区分）",
        source_url="D:\\顺天系统资料\\豆包资料\\六部经典校对版\\紫薇体系\\OCR转录版本\\蔡明宏_紫微斗数_悟我十八年_OCR_最终版.txt",
        grade=1,
        evidence_type="PRIMARY_TRADITION",
    ),
    "QTN-CMB-013": QintianEvidence(
        rule_id="QTN-CMB-013",
        title="法象（自化之象对照生年四化）",
        verbatim_quote="何谓「法象」，就是把自化的'象'（看是禄、权、科、忌的那一种），再去对照生年四化的宫位，然后依两宫位互动，就产生了现象与物相及吉或凶的征兆。",
        source="蔡明宏《悟我十八年》第四章 自化篇·单元三 应用篇（法象）",
        source_url="D:\\顺天系统资料\\豆包资料\\六部经典校对版\\紫薇体系\\OCR转录版本\\蔡明宏_紫微斗数_悟我十八年_OCR_最终版.txt",
        grade=1,
        evidence_type="PRIMARY_TRADITION",
    ),
    "QTN-CMB-014": QintianEvidence(
        rule_id="QTN-CMB-014",
        title="北派身宫论断（命为体身为用）",
        verbatim_quote="命为体，身为用。命是先天带来之根，身是此生要去完成的果。身宫，是你这一辈子「放不下、不断追求」的那一宫。",
        source="北派钦天体系延伸（蔡明宏《悟我十八年》体系，derived_commentary）",
        source_url="D:\\顺天系统资料\\豆包资料\\六部经典校对版\\紫薇体系\\OCR转录版本\\蔡明宏_紫微斗数_悟我十八年_OCR_最终版.txt",
        grade=3,
        evidence_type="SYSTEMATIZED",
    ),
}

DRAFT_BINDINGS: Dict[str, QintianEvidence] = {}


def get_evidence(rule_id: str) -> QintianEvidence | None:
    """根据 rule_id 获取 evidence binding (production only)"""
    return EVIDENCE_BINDINGS.get(rule_id)


def is_production_rule(rule_id: str) -> bool:
    """判断 rule_id 是否为钦天 production 规则"""
    return rule_id in EVIDENCE_BINDINGS
