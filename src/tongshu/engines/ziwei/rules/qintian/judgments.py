# -*- coding: utf-8 -*-
"""
Qintian Judgment Resolver — 钦天门判定层（Z44 蔡明宏主源版）

严格工程边界：
- 本模块只负责"组合命中 → 判定结论"映射
- 不涉及数据计算（combinations / features 负责）
- 不做最终用户判断（结论文字给"辨"层用）
- judgment_strength 仅作 raw 输出（"强弱"由"辨"层综合计算）
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
from .combinations import QintianCombination


@dataclass
class QintianJudgment:
    rule_id: str
    evidence_grade: int
    judgment_strength: str  # "strong" / "moderate" / "weak" / "neutral"
    neutral_facts: List[str]


# Judgment 映射表（8 条 production，蔡明宏体系）
JUDGMENT_MAPPING: Dict[str, Dict] = {
    "QTN-CMB-001": {
        "judgment_strength": "strong",
        "neutral_facts_template": [
            "来因宫即命盘太极，确定一生主题与活动空间",
            "生年干=因果起点",
        ],
    },
    "QTN-CMB-002": {
        "judgment_strength": "strong",
        "neutral_facts_template": [
            "钦天时空结构完整：体(生年四化/空间) + 用(自化/时间)齐备",
            "自化触发生年四化能量（体用合一）",
        ],
    },
    "QTN-CMB-004": {
        "judgment_strength": "moderate",
        "neutral_facts_template": [
            "向心自化主物质的凝聚",
            "箭头向内，能量回收于本宫",
        ],
    },
    "QTN-CMB-006": {
        "judgment_strength": "moderate",
        "neutral_facts_template": [
            "串联自化：同向自化跨多宫联动",
            "事件由单点变多点连锁",
        ],
    },
    "QTN-CMB-007": {
        "judgment_strength": "moderate",
        "neutral_facts_template": [
            "离心自化主物质的分散",
            "把已有的事物现象变成没有或改变另一种模式",
        ],
    },
    "QTN-CMB-011": {
        "judgment_strength": "moderate",
        "neutral_facts_template": [
            "自化五分类：生年四化 × 自化 的有无组合",
            "分类决定自化论命的切入层次",
        ],
    },
    "QTN-CMB-012": {
        "judgment_strength": "weak",
        "neutral_facts_template": [
            "出入视角：入=自化面对生年四化，出=自化背离生年四化",
            "用于判断事件面向（向内收敛/向外发散）",
        ],
    },
    "QTN-CMB-013": {
        "judgment_strength": "moderate",
        "neutral_facts_template": [
            "法象：自化之象对照生年四化宫位",
            "依两宫位互动产生吉凶征兆",
        ],
    },
    "QTN-CMB-014": {
        "judgment_strength": "moderate",
        "neutral_facts_template": [
            "命为体身为用：身宫=此生追求/执念/果报落点",
            "35岁后身宫权重放大，首看生年四化/宫内自化/三方四正",
        ],
    },
    "QTN-CMB-019": {
        "judgment_strength": "strong",
        "neutral_facts_template": [
            "生年斗君在某宫，一生课题集中该宫与其对待宫",
            "十二宫以六宫论：命宫100%|迁移70%，兄弟100%|交友70%，夫妻100%|官禄70%，子女100%|田宅70%，财帛100%|福德70%，疾厄100%|父母70%",
        ],
    },
    "QTN-CMB-018": {
        "judgment_strength": "strong",
        "neutral_facts_template": [
            "取意托乎随心而化乃名自化（自化之解）",
            "自化有反其意之作用：本好可变坏，本坏可变好，逢自化不可拘泥原本之意",
        ],
    },
    "QTN-CMB-017": {
        "judgment_strength": "strong",
        "neutral_facts_template": [
            "大限应用一律与本命息息相关，宫位为飞化定点时与生年四化发生关系",
            "大限四化以本命盘宫干为用（本命为天、大限为地、流年为人）",
            "大限化禄逢生年忌成双忌论（书例）",
        ],
    },
    "QTN-CMB-016": {
        "judgment_strength": "strong",
        "neutral_facts_template": [
            "流年四化以本命盘原始宫干为主（飞星秘仪），不用流年干",
            "若用流年干：四化为定象不可再转化，忌冲为凶；不与生年四化对待",
        ],
    },
    "QTN-CMB-015": {
        "judgment_strength": "strong",
        "neutral_facts_template": [
            "生年四化落宫单象解义：以落宫断该宫位的人生课题基调",
            "生年四化本身无吉凶（静象），吉凶须待后天飞化碰撞（动象）",
        ],
    },
}


def resolve_judgment(combo: QintianCombination) -> QintianJudgment:
    """根据组合命中返回判定结论 (raw, 无最终解释)"""
    if combo.rule_id not in JUDGMENT_MAPPING:
        # fail-closed: 未知规则返回 neutral
        return QintianJudgment(
            rule_id=combo.rule_id,
            evidence_grade=combo.evidence_grade,
            judgment_strength="neutral",
            neutral_facts=[],
        )

    m = JUDGMENT_MAPPING[combo.rule_id]
    return QintianJudgment(
        rule_id=combo.rule_id,
        evidence_grade=combo.evidence_grade,
        judgment_strength=m["judgment_strength"],
        neutral_facts=list(m["neutral_facts_template"]),
    )
