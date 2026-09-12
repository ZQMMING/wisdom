
"""
Qintian Judgment Resolver — 钦天门判定层 (P0-7)

严格工程边界：
- 本模块只负责"组合命中 → 判定结论"映射
- 不涉及数据计算（combinations / features 负责）
- 不涉及规则图谱匹配（rule_graph 负责）
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


# Judgment 映射表（与 P0-4/P0-5 同模式）
JUDGMENT_MAPPING: Dict[str, Dict] = {
    "QTN-CMB-001": {
        "judgment_strength": "strong",
        "neutral_facts_template": [
            "来因宫确定一生主题与活动空间",
            "生年干=因果起点",
        ],
    },
    "QTN-CMB-002": {
        "judgment_strength": "strong",
        "neutral_facts_template": [
            "钦天门时空结构完整：体(空间)+用(时间)齐备",
            "自化触发生年四化能量",
        ],
    },
    "QTN-CMB-003": {
        "judgment_strength": "moderate",
        "neutral_facts_template": [
            "12 宫齐全 = 立太极基础",
            "可展开中太极分析（许铨仁立太极）",
        ],
    },
    "QTN-CMB-004": {
        "judgment_strength": "moderate",
        "neutral_facts_template": [
            "向心自化注脚在对宫",
            "事件判断重心在对宫",
        ],
    },
    "QTN-CMB-005": {
        "judgment_strength": "moderate",
        "neutral_facts_template": [
            "化忌入六亲=潜意识亏欠",
            "可能产生弥补行为或溺爱倾向",
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
