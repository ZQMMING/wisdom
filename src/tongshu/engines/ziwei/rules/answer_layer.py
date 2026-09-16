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
            # SIHUA / 宫位规则
            from .palace_star_verdicts import get_palace_verdict, get_palace_gist
            text = op.get("description", "")
            palace_name = rid.split("-")[-1]
            is_palace = rid.startswith("SANHE-PALACE-")
            if is_palace:
                # 南派宫义做厚：宫义总论 + 各主星落此宫原文断语
                stars = facts.get("stars", [])
                parts = [f"{palace_name}宫：{get_palace_gist(palace_name)}"]
                for st in stars:
                    v = get_palace_verdict(palace_name, st)
                    if v:
                        parts.append(f"【{st}】{v}")
                text = " ".join(parts)
                palace_dim = _PALACE_DIM.get(palace_name, "四化体用")
                items.append(AnswerItem(
                    source="sanhe", rule_id=rid, text=text,
                    qualifier=m.qualifier, _dim_hint=palace_dim,
                ))
                continue
            if not text and op.get("target_palace"):
                # 生年四化入宫：SANHE-SIHUA-{干}-{化}
                parts2 = rid.split("-")
                if len(parts2) >= 4 and parts2[2] in "甲乙丙丁戊己庚辛壬癸":
                    text = f"生年{parts2[2]}干{parts2[3]}入{op.get('target_palace')}宫"
            items.append(AnswerItem(
                source="sanhe", rule_id=rid, text=text,
                qualifier=m.qualifier,
            ))
    return items


# 南派十二宫 → 八维度归位（不与北派四化混）
_PALACE_DIM = {
    "命宫": "性格", "福德": "性格", "父母": "性格",
    "兄弟": "婚姻", "夫妻": "婚姻", "子女": "婚姻",
    "财帛": "财运", "田宅": "财运",
    "疾厄": "健康",
    "官禄": "事业",
    "迁移": "应期", "仆役": "应期",
}


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
        elif rid.startswith("SANHE-PALACE-"):
            sanhe_dims[rid] = _PALACE_DIM.get(rid.split("-")[-1], "四化体用")
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


# ============================================================================
# Z93: 格局/断语释义字典——Assertion → 自然语言解读
# ============================================================================
PATTERN_INTERPRETATION = {
    "WEALTH-01": {"name": "财荫夹印", "interpretation": "武曲天相在官禄宫，梁相夹印，主因职位权力得财。", "dim": "财运"},
    "WEALTH-02": {"name": "日月夹财", "interpretation": "武曲守命或财帛，太阳太阴来夹，财运有贵人助。", "dim": "财运"},
    "WEALTH-03": {"name": "财禄夹马", "interpretation": "天马守命/财帛，武曲+禄存来夹，主动中得财。", "dim": "财运"},
    "WEALTH-04": {"name": "荫印拱身", "interpretation": "天梁+天相拱身/田宅，主有长辈贵人荫庇。", "dim": "财运"},
    "WEALTH-05": {"name": "日月照璧", "interpretation": "太阳太阴临田宅宫，主不动产丰厚、家庭温暖。", "dim": "财运"},
    "WEALTH-06": {"name": "金灿光辉", "interpretation": "太阳单守命在午宫，主光明磊落、名声显赫。", "dim": "事业"},
    "NOB-01": {"name": "日月夹命", "interpretation": "太阳太阴夹命宫，主贵人助力、名声好。", "dim": "事业"},
    "NOB-02": {"name": "日出扶桑", "interpretation": "太阳在卯守命或官禄，主旭日东升、事业早期发达。", "dim": "事业"},
    "NOB-03": {"name": "月朗天门", "interpretation": "太阴在亥守命，主清贵、文才。", "dim": "事业"},
    "NOB-04": {"name": "月生沧海", "interpretation": "太阴在子守田宅，主不动产丰厚、暗财多。", "dim": "财运"},
    "NOB-05": {"name": "辅弼拱主", "interpretation": "紫微守命，左辅右弼来拱，主有辅佐之人。", "dim": "事业"},
    "NOB-06": {"name": "君臣庆会", "interpretation": "紫微+左右同守命，更会相武阴，主大贵。", "dim": "事业"},
    "NOB-07": {"name": "财印夹禄", "interpretation": "禄存守命，梁相来夹，主因财得权、因权得财。", "dim": "财运"},
    "NOB-08": {"name": "禄马佩印", "interpretation": "禄存+天马同宫，主动中得财、异地发展。", "dim": "财运"},
    "NOB-09": {"name": "坐贵向贵", "interpretation": "天魁天钺夹拱命宫，主贵人多、逢凶化吉。", "dim": "事业"},
    "NOB-10": {"name": "马头带剑", "interpretation": "天马+擎羊在午，主武贵、边疆立功。", "dim": "事业"},
    "NOB-11": {"name": "七杀朝斗", "interpretation": "七杀在寅申辰戌守命，主权威、开创。", "dim": "事业"},
    "NOB-12": {"name": "日月并明", "interpretation": "太阳太阴皆入庙，主阴阳调和、声名显赫。", "dim": "事业"},
    "NOB-13": {"name": "明珠出海", "interpretation": "太阴在亥，太阳在卯，主文章盖世。", "dim": "事业"},
    "NOB-14": {"name": "日月同临", "interpretation": "太阳太阴同宫或对照，主多才多艺。", "dim": "事业"},
    "NOB-15": {"name": "刑囚夹印", "interpretation": "廉贞+天刑同临身命，主武勇、军警、司法。", "dim": "事业"},
    "NOB-16": {"name": "科权禄拱", "interpretation": "生年禄权科三方拱命，主三奇加会、大贵。", "dim": "事业"},
    "NOB-17": {"name": "贪火相逢", "interpretation": "贪狼+火星同守命庙旺，主暴发、横发。", "dim": "事业"},
    "NOB-18": {"name": "武曲守垣", "interpretation": "武曲守命在卯宫，主财星得地、理财能力强。", "dim": "财运"},
    "NOB-19": {"name": "府相朝垣", "interpretation": "天府+天相会照，主事业有辅佐、位高权重。", "dim": "事业"},
    "NOB-20": {"name": "紫府朝垣", "interpretation": "紫微+天府同宫或会照，主帝星有库、富贵双全。", "dim": "事业"},
    "NOB-21": {"name": "文星暗拱", "interpretation": "昌曲夹拱命宫，主文才、科名。", "dim": "事业"},
    "NOB-22": {"name": "权禄生逢", "interpretation": "生年化权+化禄同守命庙旺，主财权双得。", "dim": "财运"},
    "NOB-23": {"name": "羊刃入庙", "interpretation": "擎羊守命在辰戌丑未遇吉，主武贵、权威。", "dim": "事业"},
    "NOB-24": {"name": "巨机居卯", "interpretation": "巨门+天机同守卯宫，主口才好、靠技术立足。", "dim": "事业"},
    "NOB-25": {"name": "明禄暗禄", "interpretation": "禄存+化禄明见暗拱，主双禄夹命、财运厚。", "dim": "财运"},
    "NOB-26": {"name": "金舆扶驾", "interpretation": "紫微守命，太阳太阴前后夹，主贵人多。", "dim": "事业"},
    "POV-01": {"name": "生不逢时", "interpretation": "命坐空亡逢廉贞，主怀才不遇。", "dim": "性格"},
    "POV-02": {"name": "禄逢两杀", "interpretation": "禄存坐空亡又逢空劫，主财来财去。", "dim": "财运"},
    "POV-03": {"name": "马落空亡", "interpretation": "天马落空亡，主奔波无功。", "dim": "财运"},
    "POV-04": {"name": "日月藏辉", "interpretation": "日月反背又逢巨暗，主名声不显。", "dim": "事业"},
    "POV-05": {"name": "财与囚仇", "interpretation": "武曲+廉贞同守身命，主因财惹是非。", "dim": "财运"},
    "POV-06": {"name": "一生孤贫", "interpretation": "破军守命星陷地，主一生奔波。", "dim": "性格"},
    "POV-07": {"name": "君子在野", "interpretation": "四杀守身命临陷地，主怀才不遇。", "dim": "事业"},
    "POV-08": {"name": "两重华盖", "interpretation": "禄存化禄坐命遇空劫，主财多耗、宗教缘。", "dim": "财运"},
    "MISC-01": {"name": "风云际会", "interpretation": "身命虽弱，二限逢禄马，主中年后遇机遇。", "dim": "应期"},
    "MISC-02": {"name": "锦上添花", "interpretation": "限破恶星而行吉地，主先难后易。", "dim": "应期"},
    "MISC-03": {"name": "禄衰马困", "interpretation": "限逢七杀禄马空亡，主财运困顿。", "dim": "财运"},
    "MISC-04": {"name": "衣锦还乡", "interpretation": "少年不遂，四十后行墓运，主大器晚成。", "dim": "应期"},
    "MISC-05": {"name": "步数无依", "interpretation": "前限接后限连绵不分，主限运不清。", "dim": "应期"},
    "MISC-06": {"name": "水上驾星", "interpretation": "一年好一年不好，主运势起伏。", "dim": "应期"},
    "MISC-07": {"name": "吉凶相伴", "interpretation": "命有主星，限前则发限衰不发。", "dim": "应期"},
    "MISC-08": {"name": "枯木逢春", "interpretation": "命衰限好，主中年后渐入佳境。", "dim": "应期"},
}

VERDICT_INTERPRETATION = {
    ("夫妻", "破军"): "婚姻多波折，配偶个性强，宜晚婚。",
    ("财帛", "紫微"): "财运靠地位非经商，丰足但不暴富。",
    ("疾厄", "天机"): "幼年多灾，注意神经系统、四肢。",
    ("迁移", "七杀"): "外出奔波多，动中得吉，适合异地。",
    ("仆役", "太阳"): "下属/朋友有力，入庙则发。",
    ("仆役", "天梁"): "下属可靠，有年长得力之人。",
    ("官禄", "武曲"): "事业武职/金融/管理，会科权禄则大富。",
    ("官禄", "天相"): "事业辅佐型，文武皆宜，食禄千钟。",
    ("田宅", "天同"): "田产先少后多，晚年自置。",
    ("田宅", "巨门"): "田产横发但也招非。",
    ("福德", "贪狼"): "精神多欲、劳心，晚年方安。",
    ("父母", "太阴"): "母亲缘深，入庙无克。",
}


def get_interpretation(rule_id: str) -> dict:
    if rule_id in PATTERN_INTERPRETATION:
        return PATTERN_INTERPRETATION[rule_id]
    if rule_id.startswith("PALACE-"):
        parts = rule_id.split("-")
        if len(parts) >= 3:
            palace = parts[1]
            star = parts[2]
            if (palace, star) in VERDICT_INTERPRETATION:
                return {"name": f"{star}在{palace}", "interpretation": VERDICT_INTERPRETATION[(palace, star)], "dim": "性格"}
    return {"name": rule_id, "interpretation": "", "dim": "四化体用"}
