# -*- coding: utf-8 -*-
"""ZIPING V3.1 顶层入口 — 一个 BaziChart 跑完 已实现子集, 产出 §28 统一输出.

已实现域 (P0~P4, 确定性结构判定, 无阈值):
    LING      月令/得令        (§4)
    GROWTH    十二长生结构态   (§5/§72)
    STRENGTH  身强弱六态       (§14, 依赖 LING+根+党众)
    CLIMATE   气候/调候需求    (§19/§38, 调候表 pluggable)
    QING      清浊             (§17)
    TONGGUAN  通关             (§21)
    DISEASE   病药             (§20/§61, 需主格; 未实现主格 → fail-closed)
    QI        气势             (§12, 依赖 LING+党众)
    YONG      用神分方法       (§23/§57, 各方法独立输出不合并)

未实现域 (pattern 建格/清浊成败/喜忌/时间层/特殊格/真假/相神/病药五件套补全):
    → 保持 fail-closed (UNDETERMINED + 分因 §77), 不臆测 (§0.3/§82 BLOCKER).

架构: 各域 已实现 则 出判断, 未实现 或 缺前置 则 UNDETERMINED;
      域间 按 §79 依赖边 串接, 互不阻塞.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .engine import EngineContext
from .facts_adapter import chart_to_context
from .judgment import judge_ling, judge_growth, derive_effective_root, \
    derive_party_structure, judge_strength
from .judgment_ext import (
    judge_climate, judge_qing, judge_tongguan,
    judge_disease, judge_qi, judge_yong,
)
from .reference import build_derived_facts
from .types import (
    MethodScope, UndeterminedReason, ZiPingDerivedFact, ZiPingJudgment,
    synthesize_output,
)


def _und(domain: str, detail: str) -> ZiPingJudgment:
    """未实现域 / 缺前置 → UNDETERMINED (携带分因, §77 禁止裸 UNDETERMINED)."""
    return ZiPingJudgment(
        domain=domain, state="UNDETERMINED",
        matched_rule_ids=[], evidence_refs=[],
        method_scope=[MethodScope.DISPUTED],
        reason=UndeterminedReason.RULE_MISSING,
        reason_detail=detail,
    )


def run_ziping(
    chart: Any,
    month_command: Optional[Dict[str, Any]] = None,
    climate_table: Optional[Dict[str, Any]] = None,
    temporal_inputs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """BaziChart → §28 统一输出 (已实现域判断 + 未实现域 fail-closed 清单).

    Args:
        chart: BaziEngine.compute() 产出 (排盘层事实).
        month_command: 月令司令表数据 (pluggable); 缺 → 透干/调候 fail-closed.
        climate_table: 调候用神表数据 (pluggable, 子代理核证产出); 缺 → 调候 fail-closed.
        temporal_inputs: 流年/流月/流日 (调用方注入; §25 子平只 overlay).

    Returns:
        §28 契约 dict: engine/version/judgments/undetermined/status.
    """
    fact, available, ti = chart_to_context(chart, temporal_inputs)
    derived = build_derived_facts(fact, month_command)
    ctx = EngineContext(fact, available, ti)

    judgments: List[ZiPingJudgment] = []

    # ---- 基础域: 月令 + 长生 (无上游依赖) ----
    ling = judge_ling(ctx, derived)
    growth = judge_growth(ctx, derived)
    judgments += [ling, growth]

    # ---- 根 + 党众 (依赖 四柱/藏干/长生) ----
    eff_root = derive_effective_root(ctx, derived)
    de_ling = ling.state == "DE_LING"
    party = derive_party_structure(ctx, derived, de_ling=de_ling)

    # ---- 身强弱 (依赖 月令+根+党众) ----
    strength = judge_strength(ctx, derived, ling, eff_root, party,
                              special_valid=False)
    judgments.append(strength)

    # ---- 独立诊断域: 气候/清浊/通关 (透干十神, 无主格依赖) ----
    climate = judge_climate(ctx, derived, climate_table)
    qing = judge_qing(ctx, derived)
    tongguan = judge_tongguan(ctx, derived)
    judgments += [climate, qing, tongguan]

    # ---- 气势 (依赖 月令+党众) ----
    qi = judge_qi(ctx, derived, ling, party)
    judgments.append(qi)

    # ---- 病药 (需主格; 主格未实现 → fail-closed) ----
    disease = judge_disease(ctx, derived, pattern_judgment=None)
    judgments.append(disease)

    # ---- 用神分方法 (§57 隔离, 不合并; 各方法按上游 fail-closed) ----
    yong = judge_yong(ctx, derived,
                      pattern=None,        # 主格未实现 → YONG-PATTERN fail-closed
                      climate=climate,
                      disease=disease,
                      tongguan=tongguan,
                      climate_table=climate_table)
    judgments += list(yong.values())

    # ---- 未实现域 显式登记 fail-closed (§82 BLOCKER: 不得宣称完成) ----
    judgments += [
        _und("PATTERN", "建格八格十项未实现 (REV-PATTERN, 需主格核证 附录B/E)"),
        _und("PATTERN_QUALITY", "格局高低未实现 (§33, 需清浊+成败+有情有力)"),
        _und("TRUE", "真假十项未实现 (§68 REV-TRUE)"),
        _und("SPECIAL", "特殊格/从格未实现 (§22/§63, 需主导定义核证)"),
        _und("XIANG", "相神六态未实现 (§32/§56)"),
        _und("XIJI", "喜忌七输入未实现 (§58 REV-XIJI, 需 七域齐备)"),
        _und("TEMPORAL", "时间层 overlay 未实现 (§25/§73, 需 caller 注入 流年/流月/流日)"),
    ]

    undet = [(j.domain, UndeterminedReason(j.reason or "RULE_MISSING"),
              j.reason_detail or "")
             for j in judgments if j.state == "UNDETERMINED"]

    result = synthesize_output(judgments, undet)
    # ---- 解层: §28 枚举 → 五经断语触发 (全量 15 维) ----
    from .interpretation import build_interpretation
    interpretation = build_interpretation(judgments)
    result["interpretations"] = {
        "ling": [d.__dict__ for d in getattr(interpretation, 'ling', [])],
        "growth": [d.__dict__ for d in getattr(interpretation, 'growth', [])],
        "root": [d.__dict__ for d in getattr(interpretation, 'root', [])],
        "party": [d.__dict__ for d in getattr(interpretation, 'party', [])],
        "strength": [d.__dict__ for d in getattr(interpretation, 'strength', [])],
        "qing": [d.__dict__ for d in getattr(interpretation, 'qing', [])],
        "climate": [d.__dict__ for d in getattr(interpretation, 'climate', [])],
        "tongguan": [d.__dict__ for d in getattr(interpretation, 'tongguan', [])],
        "disease": [d.__dict__ for d in getattr(interpretation, 'disease', [])],
        "qi": [d.__dict__ for d in getattr(interpretation, 'qi', [])],
        "pattern": [d.__dict__ for d in getattr(interpretation, 'pattern', [])],
        "pattern_quality": [d.__dict__ for d in getattr(interpretation, 'pattern_quality', [])],
        "true": [d.__dict__ for d in getattr(interpretation, 'true', [])],
        "special": [d.__dict__ for d in getattr(interpretation, 'special', [])],
        "yong": [d.__dict__ for d in getattr(interpretation, 'yong', [])],
        "xiang": [d.__dict__ for d in getattr(interpretation, 'xiang', [])],
        "xiji": [d.__dict__ for d in getattr(interpretation, 'xiji', [])],
        "temporal": [d.__dict__ for d in getattr(interpretation, 'temporal', [])],
        # 人生维度
        "wealth": [d.__dict__ for d in getattr(interpretation, 'wealth', [])],
        "career": [d.__dict__ for d in getattr(interpretation, 'career', [])],
        "marriage": [d.__dict__ for d in getattr(interpretation, 'marriage', [])],
        "health": [d.__dict__ for d in getattr(interpretation, 'health', [])],
        "longevity": [d.__dict__ for d in getattr(interpretation, 'longevity', [])],
        "family": [d.__dict__ for d in getattr(interpretation, 'family', [])],
        "children": [d.__dict__ for d in getattr(interpretation, 'children', [])],
        "fortune": [d.__dict__ for d in getattr(interpretation, 'fortune', [])],
        "undetermined_domains": getattr(interpretation, 'undetermined_domains', []),
    }
    # ---- 喜用神裁定 ----
    from .yongshen import YongShenEngine, LiuNianEngine
    yong_engine = YongShenEngine()
    chart_info = {
        "month_branch": derived.states.get("month_branch", ""),
        "day_master": derived.states.get("day_master", ""),
        "four_stems": [p.heavenly_stem for p in [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]],
        "four_branches": [p.earthly_branch for p in [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]],
        "has_root_for_yong": derived.states.get("root_strength", {}).get("growth_available", False),
    }
    yong_verdict = yong_engine.verdict(judgments, chart_info)
    result["yongshen"] = YongShenEngine.to_dict(yong_verdict)

    # ---- 大运 (从八字引擎获取) ----
    if hasattr(chart, 'luck_pillars') and chart.luck_pillars:
        luck_data = []
        start_age = getattr(chart, 'start_age', 5)
        for i, lp in enumerate(chart.luck_pillars):
            age_start = round(start_age + i * 10)
            age_end = age_start + 9
            luck_data.append({
                "index": i + 1,
                "age_range": f"{age_start}-{age_end}",
                "stem": lp.heavenly_stem,
                "branch": lp.earthly_branch,
                "ten_god": lp.stem_ten_god,
            })
        result["dayun"] = luck_data

    # ---- 流年判定 (2024-2035) ----
    liunian_engine = LiuNianEngine()
    liunian_results = []
    # 流年干支使用拼音格式 (2字符天干+2字符地支)
    for year_gz in ["JIA chen", "YI si", "BING wu", "DING wei", "WU shen", "JI you",
                    "GENG xu", "XIN hai", "REN zi", "GUI chou", "JIA yin", "YI mao"]:
        lv = liunian_engine.verdict(year_gz, chart_info, yong_verdict)
        liunian_results.append(LiuNianEngine.to_dict(lv))
    result["liunian"] = liunian_results
    # 附加 派生事实 快照 (便于 消费方 追溯 判据依据)
    result["derived"] = derived.states
    return result
