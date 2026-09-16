# -*- coding: utf-8 -*-
"""Z74d: 答案层组装——两派规则命中 → 分维度平行答案。

用户流程：输入层（八字排盘）→ 紫微斗数 → 排盘（内部算层）→ 答案层
→ 映射到各维度 → 解析层。

本模块实现「答案层→维度映射」：
- 输入：SanheRuleGraph.match_all（南派）+ detect_all_production（北派）
- 输出：八维度平行答案（性格/格局/事业/婚姻/财运/健康/应期/四化体用）
- 两派各自归位，不投票不融合，南北平行输出
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

DIMENSIONS = ["性格", "格局", "事业", "婚姻", "财运", "健康", "应期", "四化体用"]

# ============================================================================
# 北派（QINTIAN）规则 → 维度映射（按规则语义归位）
# ============================================================================
QTN_DIMENSION = {
    # 四化体用（来因/自化/双象/出入/次序——钦天核心结构）
    "QTN-CMB-001": "四化体用", "QTN-CMB-002": "四化体用", "QTN-CMB-003": "四化体用",
    "QTN-CMB-004": "四化体用", "QTN-CMB-005": "四化体用", "QTN-CMB-006": "四化体用",
    "QTN-CMB-007": "四化体用", "QTN-CMB-008": "四化体用", "QTN-CMB-009": "四化体用",
    "QTN-CMB-010": "四化体用", "QTN-CMB-011": "四化体用", "QTN-CMB-012": "四化体用",
    "QTN-CMB-013": "四化体用", "QTN-CMB-021": "四化体用", "QTN-CMB-022": "四化体用",
    "QTN-CMB-025": "四化体用", "QTN-CMB-026": "四化体用", "QTN-CMB-031": "四化体用",
    "QTN-CMB-044": "四化体用",
    # 性格（身宫/来因宫体性）
    "QTN-CMB-014": "性格", "QTN-CMB-020": "性格", "QTN-CMB-027": "性格",
    # 事业（官禄飞化/命宫飞化/武职/白手起家）
    "QTN-CMB-023": "事业", "QTN-CMB-033": "事业", "QTN-CMB-046": "事业",
    "QTN-CMB-045": "事业",
    # 婚姻（夫妻宫四化/结婚限）
    "QTN-CMB-038": "婚姻", "QTN-CMB-039": "婚姻", "QTN-CMB-047": "婚姻",
    "QTN-CMB-049": "婚姻", "QTN-CMB-050": "婚姻",
    # 财运（财帛飞化/来因宫贵格）
    "QTN-CMB-032": "财运", "QTN-CMB-036": "财运", "QTN-CMB-037": "财运",
    # 健康（疾厄宫/血光）
    "QTN-CMB-041": "健康",
    # 应期（大限/流年/流月/官非/结婚限应期）
    "QTN-CMB-016": "应期", "QTN-CMB-017": "应期", "QTN-CMB-024": "应期",
    "QTN-CMB-028": "应期", "QTN-CMB-029": "应期", "QTN-CMB-030": "应期",
    "QTN-CMB-040": "应期", "QTN-CMB-042": "应期", "QTN-CMB-043": "应期",
    "QTN-CMB-048": "应期", "QTN-CMB-051": "应期", "QTN-CMB-052": "应期",
    "QTN-CMB-053": "应期", "QTN-CMB-054": "应期", "QTN-CMB-055": "应期",
    "QTN-CMB-059": "应期", "QTN-CMB-060": "应期",
    # 五行局（共用根基）
    "QTN-CMB-034": "性格", "QTN-CMB-035": "性格",
    # 其他（身宫/忌星等，归四化体用兜底）
    "QTN-CMB-015": "四化体用", "QTN-CMB-018": "四化体用", "QTN-CMB-019": "四化体用",
}

# 南派格局 trend → 维度（格局断语按吉凶向归位）
SANHE_TREND_DIMENSION = {
    "贵": "事业", "武权": "事业", "吏/安": "事业", "晚发贵": "事业",
    "财": "财运", "富/寿": "财运", "库/稳": "财运", "富/柔": "财运",
    "财印": "财运", "财官": "财运",
    "福": "性格", "福/寿": "健康", "荫/寿": "健康", "桃花/祸福": "婚姻",
    "桃花/权": "婚姻", "桃花/凶": "婚姻", "淫欲/凶": "婚姻", "暗/口舌": "性格",
    "权/囚": "事业", "威权": "事业", "权": "事业", "成败/凶": "事业",
    "大起大落": "事业", "变革": "事业", "变革/凶": "事业", "耗/变革": "事业",
    "破荡": "事业", "积富/刑": "财运", "贵/荫": "事业", "贵/口才": "事业",
    "贵/富": "事业", "荣": "事业", "福/印": "性格", "智": "性格",
    "福/印": "性格",
}


@dataclass
class AnswerItem:
    """单条维度答案。"""
    source: str          # sanhe / qintian
    rule_id: str
    text: str
    trend: str = ""
    qualifier: str = ""
    evidence_grade: int = 1
    _dim_hint: str = ""  # 显式维度提示（三方会照格局归「格局」）

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "rule_id": self.rule_id,
            "text": self.text,
            "trend": self.trend,
            "qualifier": self.qualifier,
            "evidence_grade": self.evidence_grade,
        }


def _build_sanhe_items(sanhe_result) -> list[AnswerItem]:
    items: list[AnswerItem] = []
    for m in sanhe_result.matched_rules:
        rid = m.rule_spec.rule_id
        op = m.rule_spec.operation
        facts = m.facts
        if "JUDG" in rid:
            # 坐命星断语：按星曜特质归维度
            star = facts.get("judgment_star", "")
            trend = facts.get("trend", "")
            dim = SANHE_TREND_DIMENSION.get(trend, "性格")
            items.append(AnswerItem(
                source="sanhe", rule_id=rid, text=op.get("description", ""),
                trend=trend, qualifier=m.qualifier,
            ))
        elif "PATTERN" in rid:
            scope = facts.get("scope", "坐命")
            pj = facts.get("pattern_judgment", {})
            trend = pj.get("trend", "")
            text = pj.get("judgment", "") or op.get("description", "")
            if scope == "三方会照":
                # 三方会照格局不判本命坐格：归「格局」维度并标注，不进主维度
                text = "（三方会照）" + text
                items.append(AnswerItem(
                    source="sanhe", rule_id=rid, text=text,
                    trend=trend, qualifier=m.qualifier,
                    _dim_hint="格局",
                ))
            else:
                dim = SANHE_TREND_DIMENSION.get(trend, "格局")
                items.append(AnswerItem(
                    source="sanhe", rule_id=rid, text=text,
                    trend=trend, qualifier=m.qualifier,
                    _dim_hint=dim,
                ))
        else:
            # SIHUA / 宫位规则 → 四化体用
            text = op.get("description", "")
            if not text and op.get("target_palace"):
                # 生年四化入宫：SANHE-SIHUA-{干}-{化}
                parts = rid.split("-")
                if len(parts) >= 4 and parts[2] in "甲乙丙丁戊己庚辛壬癸":
                    text = f"生年{parts[2]}干{parts[3]}入{op.get('target_palace')}宫"
            if not text and op.get("theme"):
                palace = rid.split("-")[-1]
                stars = "、".join(facts.get("stars", []))
                text = f"{palace}宫（{op.get('theme')}）：主星{stars}"
            items.append(AnswerItem(
                source="sanhe", rule_id=rid, text=text,
                qualifier=m.qualifier,
            ))
    return items


def _build_qtn_items(qtn_hits: list) -> list[AnswerItem]:
    items: list[AnswerItem] = []
    for c in qtn_hits:
        dim = QTN_DIMENSION.get(c.rule_id, "四化体用")
        items.append(AnswerItem(
            source="qintian", rule_id=c.rule_id,
            text=c.semantic_summary,
            evidence_grade=getattr(c, "evidence_grade", 1),
        ))
    return items


def build_answer(chart) -> dict:
    """两派平行组装 → 八维度答案（不投票不融合）。"""
    from .method_graphs import SanheRuleGraph
    from .qintian.combinations import detect_all_production

    sanhe_result = SanheRuleGraph().match_all(chart)
    qtn_hits = detect_all_production(chart)

    # 南派：rule_id → 维度
    sanhe_dims: dict[str, str] = {}
    for m in sanhe_result.matched_rules:
        rid = m.rule_spec.rule_id
        if "JUDG" in rid:
            sanhe_dims[rid] = SANHE_TREND_DIMENSION.get(m.facts.get("trend", ""), "性格")
        elif "PATTERN" in rid:
            sanhe_dims[rid] = SANHE_TREND_DIMENSION.get(
                m.facts.get("pattern_judgment", {}).get("trend", ""), "格局")
        else:
            sanhe_dims[rid] = "四化体用"

    items = _build_sanhe_items(sanhe_result) + _build_qtn_items(qtn_hits)
    answer: dict = {dim: [] for dim in DIMENSIONS}
    for it in items:
        dim = it._dim_hint or sanhe_dims.get(it.rule_id, QTN_DIMENSION.get(it.rule_id, "四化体用"))
        answer[dim].append(it.to_dict())

    return {
        "dimensions": DIMENSIONS,
        "answer": answer,
        "summary": {
            "sanhe_total": len(sanhe_result.matched_rules),
            "qintian_total": len(qtn_hits),
            "dimension_counts": {d: len(answer[d]) for d in DIMENSIONS},
        },
    }
