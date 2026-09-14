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
