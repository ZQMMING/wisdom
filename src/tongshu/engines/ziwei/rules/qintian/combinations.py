
"""
Qintian Combinations — 钦天门组合 detect 函数 (P0-7)

严格工程边界：
- 5 条 production detect 函数 (grade=1 许铨仁/四余独步原文支持)
- 5 条 DRAFT/CANDIDATE detect_*_draft 强制返回 None (不进生产)
- detect 返回 QintianCombination-style dataclass (与 P0-4/P0-5 模式对齐)
- 所有 detect 失败/缺失返回 None (fail-closed)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from ..feixing_rule_graph import FlyingTransformFact, PalaceStemFact
from .features import (
    get_laiyin_palace, get_self_mutagen, get_xiangxin_mutagen,
    SIX_RELATIVES,
)


@dataclass
class QintianCombination:
    """钦天门单条组合 detect 结果 (与 P0-4/P0-5 同模式)"""
    rule_id: str
    detected: bool
    evidence_grade: int
    facts: Dict[str, Any] = field(default_factory=dict)
    semantic_summary: str = ""


# ============================================================
# 5 条 production detect (grade=1)
# ============================================================

def detect_qtn_cmb_001_laiyin(chart) -> Optional[QintianCombination]:
    """QTN-CMB-001: 来因宫 = 生年干所在宫位"""
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
            f"一生主题与活动空间围绕{laiyin}展开（钦天门核心时空观）。"
        ),
    )


def detect_qtn_cmb_002_space_time(chart) -> Optional[QintianCombination]:
    """QTN-CMB-002: 生年四化=空间(体) / 自化=时间(用)

    钦天门时空观核心: 两个条件必须同时满足:
      - 来因宫存在 (空间基础)
      - 至少 1 个自化 (时间触发器)
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
            "trigger_pattern": "来因宫 + 自化 双要素齐备",
        },
        semantic_summary=(
            f"来因宫{laiyin}+ {len(self_mutagens)} 处自化，"
            f"构成钦天门完整时空结构（体+用）。"
        ),
    )


def detect_qtn_cmb_003_xuanji(chart) -> Optional[QintianCombination]:
    """QTN-CMB-003: 立太极 — 任何宫可立新命宫

    P0-7-A 严格派: 仅检测"可立太极"标志, 不展开 144 种映射
    """
    # 12 宫存在 = 可立太极
    if len(chart.palace_stems) < 12:
        return None

    return QintianCombination(
        rule_id="QTN-CMB-003",
        detected=True,
        evidence_grade=1,
        facts={
            "palace_count": len(chart.palace_stems),
            "trigger_pattern": "12 宫齐全，可立太极（中太极）",
        },
        semantic_summary=(
            "12 宫齐全，钦天门允许任何宫立太极形成中太极分析（许铨仁立太极基础）。"
        ),
    )


def detect_qtn_cmb_004_xiangxin(chart) -> Optional[QintianCombination]:
    """QTN-CMB-004: 向心自化注脚在对宫"""
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
            "trigger_pattern": "至少 1 个向心自化（对宫发射）",
        },
        semantic_summary=(
            f"发现{len(xiangxin)}处向心自化，注脚在对宫。"
        ),
    )


def detect_qtn_cmb_005_ji_six_relatives(chart) -> Optional[QintianCombination]:
    """QTN-CMB-005: 化忌入六亲宫 = 潜意识亏欠"""
    # 找所有飞化忌落入六亲宫
    ji_into_six_relatives = []
    for ft in chart.flying_transforms:
        if ft.transformation == "化忌":
            target_norm = (ft.target_palace or "").rstrip("宫")
            # 接受 "兄弟"/"兄弟宫" 两种命名
            if target_norm in {sr.rstrip("宫") for sr in SIX_RELATIVES}:
                ji_into_six_relatives.append(ft)

    if not ji_into_six_relatives:
        return None

    return QintianCombination(
        rule_id="QTN-CMB-005",
        detected=True,
        evidence_grade=1,
        facts={
            "ji_into_six_relatives_count": len(ji_into_six_relatives),
            "ji_list": [
                f"{ft.source_palace}→{ft.target_palace}" for ft in ji_into_six_relatives
            ],
            "six_relatives_set": sorted(SIX_RELATIVES),
            "trigger_pattern": "化忌入六亲宫",
        },
        semantic_summary=(
            f"发现{len(ji_into_six_relatives)}处化忌入六亲宫，"
            f"主对该六亲有潜意识亏欠感（许铨仁 A06-07）。"
        ),
    )


# ============================================================
# 5 条 DRAFT detect (grade=3+ 强制返回 None)
# ============================================================

def detect_qtn_cmb_006_chuanlian_draft(chart) -> Optional[QintianCombination]:
    """QTN-CMB-006 DRAFT: 串联自化 (四余独步)"""
    return None  # DRAFT, not implemented in P0-7-A


def detect_qtn_cmb_007_lixin_draft(chart) -> Optional[QintianCombination]:
    """QTN-CMB-007 DRAFT: 离心自化十二地支分布 (四余独步)"""
    return None


def detect_qtn_cmb_008_12palace_draft(chart) -> Optional[QintianCombination]:
    """QTN-CMB-008 DRAFT: 十二宫生年四化逐宫详释 (许铨仁 A03-A07)"""
    return None


def detect_qtn_cmb_009_zi_chou_draft(chart) -> Optional[QintianCombination]:
    """QTN-CMB-009 DRAFT: 子/丑不做来因宫例外 (四余独步)"""
    return None


def detect_qtn_cmb_010_ji_dynamic_draft(chart) -> Optional[QintianCombination]:
    """QTN-CMB-010 DRAFT: 化忌多变动推论"""
    return None


# ============================================================
# Detect All 函数
# ============================================================

PRODUCTION_DETECTORS = [
    detect_qtn_cmb_001_laiyin,
    detect_qtn_cmb_002_space_time,
    detect_qtn_cmb_003_xuanji,
    detect_qtn_cmb_004_xiangxin,
    detect_qtn_cmb_005_ji_six_relatives,
]

DRAFT_DETECTORS = [
    detect_qtn_cmb_006_chuanlian_draft,
    detect_qtn_cmb_007_lixin_draft,
    detect_qtn_cmb_008_12palace_draft,
    detect_qtn_cmb_009_zi_chou_draft,
    detect_qtn_cmb_010_ji_dynamic_draft,
]


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
