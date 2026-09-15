# -*- coding: utf-8 -*-
"""
Qintian Combinations — 钦天门组合 detect 函数（Z44 蔡明宏主源版）

严格工程边界：
- 8 条 production detect 函数 (grade=1 蔡明宏《悟我十八年》原文支持)
- detect 返回 QintianCombination-style dataclass
- 所有 detect 失败/缺失返回 None (fail-closed)
- Z44 主源切换：许铨仁/四余独步规则清除，主源=蔡明宏《悟我十八年》

规则清单（全部蔡明宏原文）：
  - QTN-CMB-001 来因宫 = 生年干所在宫位
  - QTN-CMB-002 生年四化=空间(体) / 自化=时间(用)
  - QTN-CMB-004 向心自化（箭头向内，物质的凝聚）
  - QTN-CMB-006 串联自化（同向自化串联）
  - QTN-CMB-007 离心自化（箭头向外，物质的分散）
  - QTN-CMB-011 自化五分类（生年有/无自化 × 飞宫遇/不遇）
  - QTN-CMB-012 出与入（自化面对生年四化的出入）
  - QTN-CMB-013 法象（自化之象对照生年四化宫位）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from ..feixing_rule_graph import FlyingTransformFact, PalaceStemFact
from .features import (
    get_laiyin_palace, get_self_mutagen, get_xiangxin_mutagen, get_lixin_mutagen,
)


@dataclass
class QintianCombination:
    """钦天门单条组合 detect 结果"""
    rule_id: str
    detected: bool
    evidence_grade: int
    facts: Dict[str, Any] = field(default_factory=dict)
    semantic_summary: str = ""


# ============================================================
# 8 条 production detect (grade=1)
# ============================================================

def detect_qtn_cmb_001_laiyin(chart) -> Optional[QintianCombination]:
    """QTN-CMB-001: 来因宫 = 生年干所在宫位（蔡明宏：太极即来因宫）"""
    palace_stems = chart.palace_stems
    if not palace_stems:
        return None

    laiyin = get_laiyin_palace(chart.birth_year, palace_stems)
    if not laiyin:
        return None

    return QintianCombination(
        rule_id="QTN-CMB-001",
        detected=True,
        evidence_grade=1,
        facts={
            "laiyin_palace": laiyin,
            "birth_year": chart.birth_year,
            "trigger_pattern": "来因宫 = 生年干所在宫位",
        },
        semantic_summary=(
            f"生年{chart.birth_year}年来因宫落{laiyin}，"
            f"此宫即命盘之「太极」，看四化之所用（蔡明宏《悟我十八年》）。"
        ),
    )


def detect_qtn_cmb_002_space_time(chart) -> Optional[QintianCombination]:
    """QTN-CMB-002: 生年四化=空间(体) / 自化=时间(用)

    蔡明宏：生年的象是空间性的（物的存在论）；自化的象是时间性的。
    两要素齐备（来因宫 + 至少1处自化）构成完整时空结构。
    """
    palace_stems = chart.palace_stems
    if not palace_stems:
        return None

    laiyin = get_laiyin_palace(chart.birth_year, palace_stems)
    if not laiyin:
        return None

    self_mutagens = get_self_mutagen(chart)
    if not self_mutagens:
        return None

    return QintianCombination(
        rule_id="QTN-CMB-002",
        detected=True,
        evidence_grade=1,
        facts={
            "laiyin_palace": laiyin,
            "self_mutagen_count": len(self_mutagens),
            "self_mutagens": [
                f"{ft.source_palace}/{ft.transformation}" for ft in self_mutagens
            ],
            "trigger_pattern": "来因宫 + 自化 双要素齐备（体+用）",
        },
        semantic_summary=(
            f"来因宫{laiyin}（体/空间）+ {len(self_mutagens)} 处自化（用/时间），"
            f"构成钦天完整时空结构（蔡明宏：生年四化体用合一）。"
        ),
    )


def detect_qtn_cmb_004_xiangxin(chart) -> Optional[QintianCombination]:
    """QTN-CMB-004: 向心自化（箭头向内，物质的凝聚）"""
    xiangxin = get_xiangxin_mutagen(chart)
    if not xiangxin:
        return None

    return QintianCombination(
        rule_id="QTN-CMB-004",
        detected=True,
        evidence_grade=1,
        facts={
            "xiangxin_count": len(xiangxin),
            "xiangxin_list": [
                f"{ft.source_palace}→{ft.target_palace}/{ft.transformation}"
                for ft in xiangxin
            ],
            "trigger_pattern": "至少 1 个向心自化（箭头向内）",
        },
        semantic_summary=(
            f"发现{len(xiangxin)}处向心自化，"
            f"主物质的凝聚（蔡明宏：箭头向内→向心力→物质的凝聚）。"
        ),
    )


def detect_qtn_cmb_006_chuanlian(chart) -> Optional[QintianCombination]:
    """QTN-CMB-006: 串联自化

    蔡明宏：自化的游戏规则（3）串联与不串联；飞宫不遇生年四化但有自化者（并串联）。
    检测: 同一种四化的自化出现在 >=2 个不同宫位即串联。
    """
    self_mutagens = get_self_mutagen(chart)
    if not self_mutagens:
        return None

    by_transform: dict = {}
    for ft in self_mutagens:
        by_transform.setdefault(ft.transformation, []).append(ft)

    chuanlian = []
    for transform, fts in by_transform.items():
        palaces = sorted({ft.source_palace for ft in fts})
        if len(palaces) >= 2:
            chuanlian.append({
                "transformation": transform,
                "palaces": palaces,
                "stars": sorted({ft.target_star for ft in fts}),
                "count": len(fts),
            })

    if not chuanlian:
        return None

    return QintianCombination(
        rule_id="QTN-CMB-006",
        detected=True,
        evidence_grade=1,
        facts={
            "chuanlian_count": len(chuanlian),
            "chuanlian_list": chuanlian,
            "trigger_pattern": "同向自化（同四化）串联 >=2 宫",
        },
        semantic_summary=(
            f"发现{len(chuanlian)}组串联自化："
            + "、".join(f"{c['transformation']}@{'+'.join(c['palaces'])}" for c in chuanlian)
            + "（蔡明宏：串联与不串联）。"
        ),
    )


def detect_qtn_cmb_007_lixin(chart) -> Optional[QintianCombination]:
    """QTN-CMB-007: 离心自化（箭头向外，物质的分散）"""
    lixin = get_lixin_mutagen(chart)
    if not lixin:
        return None

    branch_dist: dict = {}
    palace_to_branch = {pf.palace_name: pf.branch for pf in chart.palace_stems}
    for ft in lixin:
        branch = palace_to_branch.get(ft.source_palace)
        if branch:
            branch_dist.setdefault(branch, 0)
            branch_dist[branch] += 1

    return QintianCombination(
        rule_id="QTN-CMB-007",
        detected=True,
        evidence_grade=1,
        facts={
            "lixin_count": len(lixin),
            "branch_distribution": branch_dist,
            "lixin_list": [
                f"{ft.source_palace}{ft.target_star}{ft.transformation}"
                for ft in lixin
            ],
            "trigger_pattern": "离心自化（箭头向外）",
        },
        semantic_summary=(
            f"发现{len(lixin)}处离心自化，"
            f"主物质的分散——把已有的事物现象变成没有或改变另一种模式（蔡明宏）。"
        ),
    )


def detect_qtn_cmb_011_wufenlei(chart) -> Optional[QintianCombination]:
    """QTN-CMB-011: 自化五分类

    蔡明宏原文：
    （一）生年四化，有自化者。（包括来因宫本身自己有自化者）
    （二）生年四化，没有自化者。
    （三）无生年四化，有自化者。
    （四）飞宫遇生年四化，又有自化者。
    （五）飞宫不遇生年四化，但有自化者。（并串联）
    """
    self_mutagens = get_self_mutagen(chart)
    # 生年四化（年干四化）落宫
    from ....ziwei_engine import GAN_SIHUA
    birth_stem_idx = (chart.birth_year - 4) % 10
    stems_10 = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    birth_stem = stems_10[birth_stem_idx]
    birth_sihua = GAN_SIHUA.get(birth_stem, ())

    # 生年四化星所在宫（main stars 含该星）
    sheng_nian_palaces = []
    for pf in chart.palace_stems:
        if any(s in pf.major_stars for s in birth_sihua):
            sheng_nian_palaces.append(pf.palace_name)

    has_sheng_nian = len(sheng_nian_palaces) > 0
    has_self = len(self_mutagens) > 0

    # 飞宫 = 宫干四化（flying_transforms 中非生年干来源者）
    flying_transforms = [ft for ft in chart.flying_transforms]
    # 串联合并判定
    chuanlian = 0
    by_transform: dict = {}
    for ft in self_mutagens:
        by_transform.setdefault(ft.transformation, []).append(ft)
    for transform, fts in by_transform.items():
        if len({ft.source_palace for ft in fts}) >= 2:
            chuanlian += 1

    # 归类
    if has_sheng_nian and has_self:
        cat = "（一）生年四化有自化者（含来因宫自化）"
    elif has_sheng_nian and not has_self:
        cat = "（二）生年四化没有自化者"
    elif not has_sheng_nian and has_self:
        cat = "（三）无生年四化有自化者"
    else:
        cat = "（四）无生年四化且无自化者（盘面无自化）"

    note = f"，并串联{chuanlian}组" if chuanlian else ""

    return QintianCombination(
        rule_id="QTN-CMB-011",
        detected=True,
        evidence_grade=1,
        facts={
            "category": cat,
            "sheng_nian_palaces": sheng_nian_palaces,
            "sheng_nian_sihua": list(birth_sihua),
            "self_mutagen_count": len(self_mutagens),
            "chuanlian_count": chuanlian,
            "flying_transform_count": len(flying_transforms),
            "trigger_pattern": "自化五分类判定",
        },
        semantic_summary=(
            f"本盘归类：{cat}（蔡明宏自化五分类）{note}。"
        ),
    )


def detect_qtn_cmb_012_churu(chart) -> Optional[QintianCombination]:
    """QTN-CMB-012: 出与入

    蔡明宏原文：站在太阴化禄的流年（酉宫）去面对巨门的自化禄是'入'。
    站在巨门的自化禄去面对太阴的化禄是'出'。

    检测：生年四化宫 与 自化宫 的相对视角（入=生年四化面对自化；出=自化面对生年四化）。
    """
    self_mutagens = get_self_mutagen(chart)
    if not self_mutagens:
        return None

    from ....ziwei_engine import GAN_SIHUA
    birth_stem_idx = (chart.birth_year - 4) % 10
    stems_10 = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    birth_stem = stems_10[birth_stem_idx]
    birth_sihua = GAN_SIHUA.get(birth_stem, ())

    # 生年四化宫
    sheng_nian_palaces = []
    for pf in chart.palace_stems:
        if any(s in pf.major_stars for s in birth_sihua):
            sheng_nian_palaces.append(pf.palace_name)

    if not sheng_nian_palaces:
        return None

    # 与生年四化同宫的自化 = 入（生年四化面对自化）；异宫自化 = 出
    churu = []
    for ft in self_mutagens:
        if ft.source_palace in sheng_nian_palaces:
            churu.append(f"{ft.source_palace}{ft.transformation}（入）")
        else:
            churu.append(f"{ft.source_palace}{ft.transformation}（出）")

    return QintianCombination(
        rule_id="QTN-CMB-012",
        detected=True,
        evidence_grade=1,
        facts={
            "churu_list": churu,
            "sheng_nian_palaces": sheng_nian_palaces,
            "trigger_pattern": "自化相对生年四化的出入视角",
        },
        semantic_summary=(
            "出入判定（蔡明宏）：" + "；".join(churu[:8])
            + "（入=自化面对生年四化；出=自化背离生年四化）。"
        ),
    )


def detect_qtn_cmb_013_faxiang(chart) -> Optional[QintianCombination]:
    """QTN-CMB-013: 法象（自化之象对照生年四化宫位）

    蔡明宏原文：把自化的'象'（看是禄、权、科、忌的那一种），再去对照生年四化的宫位，
    然后依两宫位互动，就产生了现象与物相及吉或凶的征兆。
    """
    self_mutagens = get_self_mutagen(chart)
    if not self_mutagens:
        return None

    from ....ziwei_engine import GAN_SIHUA
    birth_stem_idx = (chart.birth_year - 4) % 10
    stems_10 = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    birth_stem = stems_10[birth_stem_idx]
    birth_sihua = GAN_SIHUA.get(birth_stem, ())

    # 生年四化：星→宫 映射
    sheng_nian_map = {}  # star -> palace
    for pf in chart.palace_stems:
        for s in pf.major_stars:
            if s in birth_sihua:
                sheng_nian_map[s] = pf.palace_name

    # 法象：自化（象）→ 对照生年四化宫位
    faxiang = []
    for ft in self_mutagens:
        sn = sheng_nian_map.get(ft.target_star)
        if sn:
            faxiang.append({
                "self": f"{ft.source_palace}{ft.target_star}{ft.transformation}",
                "faxiang_to": sn,
            })

    return QintianCombination(
        rule_id="QTN-CMB-013",
        detected=True,
        evidence_grade=1,
        facts={
            "faxiang_list": faxiang,
            "self_mutagen_count": len(self_mutagens),
            "trigger_pattern": "自化之象法象到生年四化宫位",
        },
        semantic_summary=(
            f"法象判定（蔡明宏）：{len(faxiang)} 处自化法象到生年四化宫位"
            + ("：" + "；".join(f"{f['self']}→{f['faxiang_to']}" for f in faxiang[:6]) if faxiang else "（无同星生年四化可法象）")
            + "。"
        ),
    )


def detect_qtn_cmb_014_shengong(chart) -> Optional[QintianCombination]:
    """QTN-CMB-014: 北派身宫论断（命为体身为用，身宫=此生执念/果报落点）

    蔡明宏体系（derived_commentary，grade=3）：
    身宫六寄宫：子午=命 辰戌=财帛 寅申=官禄 卯酉=迁移 丑未=福德 巳亥=夫妻
    看身宫首看生年四化、宫内自化，次看三方四正，不可单以星曜断吉凶。
    """
    from ..shengong_wuxing_data import (
        get_qintian_shengong_total,
        get_qintian_shengong_assertion,
        SHENGONG_PALACE_DISPLAY,
    )

    soul_br = chart.body_earthly_branch  # 身宫地支（Z45fix：body 才是身宫）
    if not soul_br:
        return None
    shen_name = ""
    for _pn, _pd in chart.palaces.items():
        if _pd.get("branch") == soul_br:
            shen_name = _pn
            break
    if not shen_name:
        return None

    total = get_qintian_shengong_total()
    data = get_qintian_shengong_assertion(shen_name)
    if not data:
        # 身宫落非六寄宫（兄弟/子女/田宅/疾厄/仆役/父母）：只出总诀
        return QintianCombination(
            rule_id="QTN-CMB-014",
            detected=True,
            evidence_grade=3,
            facts={
                "shen_palace": shen_name,
                "shen_branch": soul_br,
                "total_assertion": total["text"],
                "has_palace_assertion": False,
                "trigger_pattern": "北派身宫论断（总诀）",
            },
            semantic_summary=(
                f"身宫落{shen_name}（非六寄宫），北派只出总诀：命为体身为用，"
                f"身宫=此生追求/执念/果报落点（蔡明宏体系 derived）。"
            ),
        )

    display = SHENGONG_PALACE_DISPLAY.get(shen_name, shen_name + "宫")
    return QintianCombination(
        rule_id="QTN-CMB-014",
        detected=True,
        evidence_grade=3,
        facts={
            "shen_palace": shen_name,
            "shen_branch": soul_br,
            "total_assertion": total["text"],
            "palace_assertion": data["text"],
            "palace_features": data["features"],
            "palace_display": display,
            "has_palace_assertion": True,
            "trigger_pattern": "北派身宫论断（六寄宫）",
        },
        semantic_summary=(
            f"北派身宫落{display}：{data['text'][:60]}..."
        ),
    )



def detect_qtn_cmb_015_sheng_nian_jieyi(chart) -> Optional[QintianCombination]:
    """QTN-CMB-015: 生年四化在十二宫之解义

    蔡明宏《紫微斗數飛星秘儀》「生年四化在十二宮之解義」：
    生年四化（依据出生年干）落于某宫，即以此宫之四化单象解义论断。
    全以单象而解（双象组合不在此卷范围）；生年四化本身无吉凶，只是「象」。
    """
    palace_stems = chart.palace_stems
    if not palace_stems:
        return None

    from ....ziwei_engine import GAN_SIHUA
    birth_stem_idx = (chart.birth_year - 4) % 10
    stems_10 = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    birth_stem = stems_10[birth_stem_idx]
    birth_sihua = GAN_SIHUA.get(birth_stem, ())
    if len(birth_sihua) < 4:
        return None

    # 生年四化：星→四化 映射（化禄/化权/化科/化忌）
    star_to_sihua = {
        birth_sihua[0]: "化禄",
        birth_sihua[1]: "化权",
        birth_sihua[2]: "化科",
        birth_sihua[3]: "化忌",
    }

    from .qintian_sheng_nian_data import get_sheng_nian_jieyi, PALACE_DISPLAY

    jieyi_list = []
    for pf in palace_stems:
        for star in pf.major_stars:
            sihua = star_to_sihua.get(star)
            if not sihua:
                continue
            palace_norm = pf.palace_name.rstrip('宫')
            text = get_sheng_nian_jieyi(palace_norm, sihua)
            if text is None:
                # 原书该宫无此四化条目（如疾厄无化忌），跳过而非报错
                continue
            jieyi_list.append({
                "palace": pf.palace_name,
                "palace_display": PALACE_DISPLAY.get(palace_norm, pf.palace_name),
                "star": star,
                "sihua": sihua,
                "jieyi": text,
            })

    if not jieyi_list:
        return None

    return QintianCombination(
        rule_id="QTN-CMB-015",
        detected=True,
        evidence_grade=1,
        facts={
            "birth_stem": birth_stem,
            "birth_sihua": list(birth_sihua),
            "jieyi_count": len(jieyi_list),
            "jieyi_list": jieyi_list,
            "trigger_pattern": "生年四化星落宫 → 十二宫单象解义",
        },
        semantic_summary=(
            f"生年{birth_stem}四化落宫解义（《飞星秘仪》单象解）："
            + ";".join(
                f"{j['palace']}{j['star']}{j['sihua']}={j['jieyi'][:18]}"
                for j in jieyi_list
            )
            + "。"
        ),
    )



def detect_qtn_cmb_016_liunian(chart) -> Optional[QintianCombination]:
    """QTN-CMB-016: 流年四化应用（以本命盘原始宫干为主，不以流年干）

    蔡明宏《飞星秘仪》流年四化应用：
    - 流年者即太岁也，每逢一年顺行一宫，四化运用不以小限为主。
    - 太岁使用分两种：(一)以本命盘原始宫干为主 (二)以流年干为主。
      唯飞星秘仪记载用本命盘之宫干为主。
    - 例：原命盘地支丑位为癸丑，则流年用「癸」一飞化，不以今年流年乙丑之「乙」为飞化。
      若用乙，则每个人今年均太阴化忌。
    - 若用流年干：四化为定象不可再转化，以忌冲为凶论；流年四化与大限对待，
      不与本命盘生年四化对待，不可三合而一使用。

    入参：chart.flow_year（流年年份），无则 fail-closed 返回 None。
    """
    flow_year = getattr(chart, 'flow_year', None)
    if not flow_year:
        return None
    palace_stems = chart.palace_stems
    if not palace_stems:
        return None

    from ....ziwei_engine import GAN_SIHUA
    stems_10 = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    branches_12 = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # 流年干（仅作对比说明用）与流年支
    flow_stem_nian = stems_10[(flow_year - 4) % 10]
    flow_branch = branches_12[(flow_year - 4) % 12]

    # 流年支所在宫（太岁位 = 流年命宫），取本命盘原始宫干
    flow_palace = None
    flow_stem_used = None
    for pf in palace_stems:
        if pf.branch == flow_branch:
            flow_palace = pf.palace_name
            flow_stem_used = pf.stem
            break
    if not flow_palace or not flow_stem_used:
        return None

    # 用本命盘原始宫干飞化（飞星秘仪主法）
    flow_sihua = GAN_SIHUA.get(flow_stem_used, ())
    if len(flow_sihua) < 4:
        return None

    # 若改用流年干（对比说明）
    nian_sihua = GAN_SIHUA.get(flow_stem_nian, ())

    # 四化落星宫位
    sihua_keys = ["化禄", "化权", "化科", "化忌"]
    sihua_palaces = []
    for pf in palace_stems:
        for star in pf.major_stars:
            for k, s in zip(sihua_keys, flow_sihua):
                if star == s:
                    sihua_palaces.append(f"{pf.palace_name}{star}{k}")

    diff_note = ""
    if nian_sihua and tuple(nian_sihua) != tuple(flow_sihua):
        diff_note = (
            "若改用流年干" + flow_stem_nian + "飞化则为：" + "".join(nian_sihua)
            + "（定象不可再转化，忌冲为凶）"
        )

    return QintianCombination(
        rule_id="QTN-CMB-016",
        detected=True,
        evidence_grade=1,
        facts={
            "flow_year": flow_year,
            "flow_branch": flow_branch,
            "flow_palace": flow_palace,
            "flow_stem_nian": flow_stem_nian,
            "flow_stem_used": flow_stem_used,
            "flow_sihua": list(flow_sihua),
            "sihua_palaces": sihua_palaces,
            "trigger_pattern": "流年四化以本命盘原始宫干为主（飞星秘仪）",
        },
        semantic_summary=(
            f"{flow_year}{flow_branch}年（{flow_stem_nian}干）：流年太岁位落{flow_palace}，"
            f"飞星秘仪以本命盘原始宫干{flow_stem_used}飞化（不用流年干{flow_stem_nian}）"
            + "，四化=" + "、".join(flow_sihua) + "。" + diff_note
        ),
    )



def detect_qtn_cmb_017_daixian(chart) -> Optional[QintianCombination]:
    """QTN-CMB-017: 大限四化应用（一律与本命息息相关，本命盘宫干为用）

    蔡明宏《飞星秘仪》大限四化应用：
    - 大限的應用，一律與本命息息相關。
    - 當任何宮位為飛化定點時，均與生年四化發生關係。
    - 例：用大限財帛言，則用命盤之「丙」干飛化；化祿照大限官祿，
      可是逢到生年忌，則構成祿忌，成為雙忌論。
    - 大限即以本命盤的宮干為大限之宮干（本命為天、大限為地、流年為人）。

    入参：chart.decadal_palace（大限命宫名，如"命宫"），无则 fail-closed 返回 None。
    """
    dec_palace = getattr(chart, 'decadal_palace', None)
    if not dec_palace:
        return None
    palace_stems = chart.palace_stems
    if not palace_stems:
        return None
    from ....ziwei_engine import GAN_SIHUA

    # 找大限命宫的本命盘原始宫干
    dec = None
    for pf in palace_stems:
        if pf.palace_name == dec_palace:
            dec = pf
            break
    if dec is None:
        return None
    dec_stem = dec.stem
    dec_sihua = GAN_SIHUA.get(dec_stem, ())
    if len(dec_sihua) < 4:
        return None

    # 大限三方（命财官，各隔四宫）：用宫序数组推算
    branches_12 = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    dec_idx = branches_12.index(dec.branch)
    tri_idx = [(dec_idx + 4 * k) % 12 for k in (0, 1, 2)]  # 命→财→官
    tri_branches = [branches_12[i] for i in tri_idx]

    tri_palaces = []
    for tb in tri_branches:
        for pf in palace_stems:
            if pf.branch == tb:
                tri_palaces.append({
                    "palace": pf.palace_name,
                    "branch": pf.branch,
                    "stem": pf.stem,
                })
                break

    # 生年四化（用生年干，非命宫宫干；对照碰撞用）
    stems_10 = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    birth_year = getattr(chart, 'birth_year', None)
    sheng_nian_sihua = ()
    if birth_year:
        sheng_stem = stems_10[(birth_year - 4) % 10]
        sheng_nian_sihua = GAN_SIHUA.get(sheng_stem, ())

    # 碰撞说明（书例：化禄照大限官禄，逢生年忌成双忌论）
    collision_notes = []
    sheng_nian_ji_palace = None
    if sheng_nian_sihua:
        ji_star = sheng_nian_sihua[3]  # 生年化忌星
        for pf in palace_stems:
            if ji_star in pf.major_stars:
                sheng_nian_ji_palace = pf.palace_name
                break
        if sheng_nian_ji_palace:
            lu_star = dec_sihua[0]  # 大限化禄星
            for pf2 in palace_stems:
                if lu_star in pf2.major_stars and pf2.palace_name == sheng_nian_ji_palace:
                    collision_notes.append(
                        f"大限化禄{lu_star}落{sheng_nian_ji_palace}宫，逢生年忌成双忌论"
                    )
                    break
            if ji_star in dec_sihua:
                collision_notes.append(
                    f"大限四化含生年忌星{ji_star}，飞化与生年四化对待"
                )

    return QintianCombination(
        rule_id="QTN-CMB-017",
        detected=True,
        evidence_grade=1,
        facts={
            "decadal_palace": dec_palace,
            "decadal_branch": dec.branch,
            "decadal_stem": dec_stem,
            "decadal_sihua": list(dec_sihua),
            "decadal_triangle": tri_palaces,
            "sheng_nian_ji_palace": sheng_nian_ji_palace if sheng_nian_sihua else None,
            "collision_notes": collision_notes,
            "trigger_pattern": "大限四化以本命盘宫干为用（飞星秘仪）",
        },
        semantic_summary=(
            f"大限命宫落{dec_palace}({dec.branch})，飞星秘仪以本命盘宫干{dec_stem}为用，"
            + "四化=" + "、".join(dec_sihua)
            + "；大限三合变迁：" + "、".join(f"{p['palace']}{p['branch']}({p['stem']})" for p in tri_palaces)
            + "。大限应用一律与本命息息相关，宫位为飞化定点时均与生年四化发生关系。"
        ),
    )




def detect_qtn_cmb_018_zihua(chart) -> Optional[QintianCombination]:
    """QTN-CMB-018: 自化浅解（取意托乎随心而化乃名自化；自化反其意）

    蔡明宏《飞星秘仪》自化浅解：
    - 自化是易之「本易」。本易者，本义也。斗数上自化，有「不化」，亦有「有化」。
    - 秘仪有载：「取意托乎，随心而化，乃名自化」，为自化之解。
    - 自化定义：某宫宫干飞化之四化星恰在本宫（如夫妻宫干丙、天机化权在夫妻本宫 → 自化权）。
    - (B) 自化有反其「意」之作用：本为不好，也许因自化而好；本为不好，因自化而恶化；
      本是好的，因自化而更好；本是好的，因自化而变坏。
    - (F) 凡在四化中，不论四化如何飞化，或与生年四化碰撞产生的各种情况，
      若逢该宫自化时，其意则全变，不可拘泥于原本之意。
    - 书例：夫妻宫坐机梁、宫干丙，天机化权在夫妻本宫，谓之自化（夫妻有才干自立）；
      命宫坐戊天机化忌入夫妻，但化忌入夫妻及夫妻自化权，则其意完全变化，
      变成本身才华不及对方才干；女命多劳而荫夫。
    """
    palace_stems = chart.palace_stems
    if not palace_stems:
        return None
    from ....ziwei_engine import GAN_SIHUA

    sihua_keys = ["化禄", "化权", "化科", "化忌"]
    zihua_list = []
    for pf in palace_stems:
        if not pf.stem or not pf.major_stars:
            continue
        sihua = GAN_SIHUA.get(pf.stem, ())
        if len(sihua) < 4:
            continue
        for k, star in zip(sihua_keys, sihua):
            if star in pf.major_stars:
                zihua_list.append({
                    "palace": pf.palace_name,
                    "branch": pf.branch,
                    "stem": pf.stem,
                    "sihua": k,
                    "star": star,
                })
    if not zihua_list:
        return None

    # 反意提示：逢自化其意全变，不可拘泥原本之意（书 F/B 条）
    # 若任一自化宫同时有他宫化忌入 → 其意完全变化（书例夫妻宫）
    reverse_notes = [
        f"{z['palace']}宫自化{z['sihua']}（{z['star']}），逢自化其意全变，不可拘泥原本之意"
        for z in zihua_list
    ]

    return QintianCombination(
        rule_id="QTN-CMB-018",
        detected=True,
        evidence_grade=1,
        facts={
            "zihua_list": zihua_list,
            "zihua_count": len(zihua_list),
            "reverse_notes": reverse_notes,
            "trigger_pattern": "自化浅解：取意托乎随心而化乃名自化（飞星秘仪）",
        },
        semantic_summary=(
            "自化浅解："
            + "、".join(f"{z['palace']}宫干{z['stem']}使{z['star']}{z['sihua']}在本宫" for z in zihua_list)
            + "。取意托乎随心而化乃名自化；自化有反其意之作用，逢自化其意全变，不可拘泥原本之意。"
        ),
    )



def detect_qtn_cmb_019_doujun(chart) -> Optional[QintianCombination]:
    """QTN-CMB-019: 生年斗君入十二宫解（十二宫以六宫论）

    蔡明宏《飞星秘仪》生年斗君入十二宫解：
    - 生年斗君落十二宫各有解义（言行/兄弟交友/夫妻官禄/子女田宅…）
    - 十二宫以六宫论：命宫100%|迁移70%、兄弟100%|交友70%、
      夫妻100%|官禄70%、子女100%|田宅70%、财帛100%|福德70%、疾厄100%|父母70%
    - 生年斗君在某宫，一生课题集中该宫与其对待宫
    入参：chart.doujun_palace（生年斗君所在宫名），无则 fail-closed 返回 None。
    """
    doujun = getattr(chart, 'doujun_palace', None)
    if not doujun:
        return None
    from .qintian_doujun_data import get_doujun_jieyi, get_doujun_weight

    jieyi = get_doujun_jieyi(doujun)
    if not jieyi:
        return None
    weight = get_doujun_weight(doujun)

    return QintianCombination(
        rule_id="QTN-CMB-019",
        detected=True,
        evidence_grade=1,
        facts={
            "doujun_palace": doujun,
            "jieyi": jieyi,
            "weight_palace": weight["palace"] if weight else None,
            "weight_pct": weight["weight"] if weight else None,
            "trigger_pattern": "生年斗君入十二宫解（飞星秘仪）",
        },
        semantic_summary=(
            f"生年斗君在{doujun}宫：" + jieyi
            + (f"十二宫以六宫论：{doujun}宫为100%，{weight['palace']}宫为70%。" if weight else "")
        ),
    )


# ============================================================
# Detect All 函数
# ============================================================



PRODUCTION_DETECTORS = [
    detect_qtn_cmb_001_laiyin,
    detect_qtn_cmb_002_space_time,
    detect_qtn_cmb_004_xiangxin,
    detect_qtn_cmb_006_chuanlian,
    detect_qtn_cmb_007_lixin,
    detect_qtn_cmb_011_wufenlei,
    detect_qtn_cmb_012_churu,
    detect_qtn_cmb_013_faxiang,
    detect_qtn_cmb_014_shengong,
    detect_qtn_cmb_015_sheng_nian_jieyi,
    detect_qtn_cmb_016_liunian,
    detect_qtn_cmb_017_daixian,
    detect_qtn_cmb_018_zihua,
    detect_qtn_cmb_019_doujun,
]

DRAFT_DETECTORS: List = []


def detect_all_production(chart) -> List[QintianCombination]:
    """运行所有 production detect 函数"""
    results = []
    for detect_fn in PRODUCTION_DETECTORS:
        try:
            r = detect_fn(chart)
            if r is not None:
                results.append(r)
        except Exception:
            # fail-closed: 错误不传播, 该规则静默失败
            pass
    return results


def detect_all_draft(chart) -> List[QintianCombination]:
    """运行所有 DRAFT detect (应全返回 None)"""
    results = []
    for detect_fn in DRAFT_DETECTORS:
        try:
            r = detect_fn(chart)
            if r is not None:
                results.append(r)
        except Exception:
            pass
    return results
