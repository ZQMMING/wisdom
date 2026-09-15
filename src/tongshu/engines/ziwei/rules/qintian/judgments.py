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
