"""
P0-8 MultiMethodSignal — 紫微三派 RuleGraph 集成器

严格工程边界 (P0-8-A):
  ❌ 不改 BaseZiweiRuleGraph
  ❌ 不改 FrozenZiweiChart / ZiweiChart
  ❌ 不改各派 RuleGraph 子类 (Zhongzhou/Feixing/Qintian)
  ❌ 不写"判断/解释/强旺衰" - 那是"解"层的事
  ✅ 仅做"派别独立 compute + 适配器翻译 + 合并 + 命名空间隔离"

架构:
  chart (FrozenZiweiChart) → MultiMethodSignal.compute(chart)
                            ├→ ZhongzhouRuleGraph.compute(chart, resolver) → MethodBundle
                            ├→ FeixingRuleGraph.compute(chart)            → MethodBundle
                            └→ QintianRuleGraph.compute(chart)            → MethodBundle
                          ↓
                          MultiMethodSignal (3-4 MethodBundles + 三派聚合 grade=1 命中)

派别 API 差异适配 (P0-8-A 严格派):
  - ZhongzhouRuleGraph:
      * match_all(chart, resolver) - 需 resolver
      * 无 graph_id() method → 用 graph_id 硬编码
      * ZhongzhouRuleMatch = combo + judgment + evidence
      * ZhongzhouRuleGraphResult 无 unmatched_production_rules / draft_detected → 推导
  - FeixingRuleGraph:
      * match_all(chart) - 无 resolver
      * 有 graph_id() method
      * FeixingRuleMatch = combo + judgment + evidence_grade + rule_id
      * FeixingRuleGraphResult 无 unmatched/draft → 推导
  - QintianRuleGraph:
      * match_all(chart) - 无 resolver
      * 有 graph_id() method
      * QintianRuleMatch = rule_id + evidence_grade + semantic_summary + judgment_strength
      * QintianRuleGraphResult 有 unmatched_production_rules + draft_detected
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .zhongzhou import make_zhongzhou_rule_graph
from .feixing import make_feixing_rule_graph
from .qintian import make_qintian_rule_graph


@dataclass
class MethodMatch:
    """单条派别内规则匹配 (派别无关通用结构)"""
    rule_id: str
    evidence_grade: int
    semantic_summary: str
    facts: Dict[str, Any] = field(default_factory=dict)
    judgment_strength: str = "neutral"  # "strong" / "moderate" / "weak" / "neutral"
    judgment_text: str = ""  # 古典断语原文（来自证据表 / judgment.raw_text）


@dataclass
class MethodBundle:
    """单派别 RuleGraph 计算结果 (命名空间隔离)"""
    method_id: str                 # "ZHONGZHOU" / "FEIXING" / "QINTIAN"
    graph_id: str                  # "ZHONGZHOU-P0-4-A" 等
    profile: str                   # PROFILE 字串
    implementation_status: str     # "PRODUCTION" / "PARTIAL" / "DRAFT" / "SCAFFOLD" / "FAIL"
    matched_rules: List[MethodMatch] = field(default_factory=list)
    unmatched_production_rules: List[str] = field(default_factory=list)
    draft_detected: List[str] = field(default_factory=list)
    rule_count: int = 0
    evidence_bindings: Dict[str, Dict] = field(default_factory=dict)
    compute_error: Optional[str] = None


@dataclass
class MultiMethodSignal:
    """多派别聚合信号 - 上游"辨"层的输入"""
    chart_id: str
    bundles: Dict[str, MethodBundle] = field(default_factory=dict)
    cross_method_consensus: List[str] = field(default_factory=list)
    total_matched_rules: int = 0
    total_unmatched_production: int = 0
    compute_status: str = "OK"


# ----- 派别适配器 -----

def _wrap_zhongzhou(graph, chart) -> MethodBundle:
    """中州 RuleGraph → MethodBundle (P0-8-A 适配层)"""
    graph_id = "ZHONGZHOU-P0-4-A"
    profile = "ZHONGZHOU-Production-A"
    try:
        from ...ziwei_palace_resolution import ZiweiPalaceResolver
        from ...ziwei_method_profile import MethodId
        resolver = ZiweiPalaceResolver(chart, MethodId.ZHONGZHOU)
        result = graph.match_all(chart, resolver)

        # 适配 ZhongzhouRuleMatch (combo + judgment + evidence)
        matches: List[MethodMatch] = []
        for zm in result.matched_rules:
            combo = zm.combo
            judgment = zm.judgment
            matches.append(MethodMatch(
                rule_id=combo.combo_id,  # Zhongzhou 用 combo_id 代替 rule_id
                evidence_grade=int(combo.evidence_grade) if combo.evidence_grade != "1.5" else 1,
                semantic_summary=f"{combo.feature_id} (witness={sorted(combo.witness_palaces)})",
                facts={
                    "feature_id": combo.feature_id,
                    "witness_palaces": sorted(combo.witness_palaces),
                },
                judgment_strength=getattr(judgment, "strength", "moderate"),
                judgment_text=getattr(judgment, "description", "") if judgment else "",
            ))

        # 推导 unmatched (rule_count - matched_count)
        all_prod_ids = {f"ZHZ-CMB-{i:03d}" for i in range(1, result.rule_count + 1)}
        matched_ids = {m.rule_id for m in matches}
        unmatched = sorted(all_prod_ids - matched_ids)

        # 中州 evidence bindings (P0-4 用 EVIDENCE_TABLE dict)
        from .zhongzhou import evidence as _zhz_ev_mod
        _zhz_table = getattr(_zhz_ev_mod, "EVIDENCE_BINDINGS", None) or getattr(_zhz_ev_mod, "EVIDENCE_TABLE", None) or {}
        ev_bindings = {
            rid: {"name": rid, "grade": ev.evidence_grade}
            for rid, ev in (_zhz_table.items() if hasattr(_zhz_table, "items") else [])
        }

        return MethodBundle(
            method_id="ZHONGZHOU",
            graph_id=graph_id,
            profile=profile,
            implementation_status=result.implementation_status,
            matched_rules=matches,
            unmatched_production_rules=unmatched,
            draft_detected=[],
            rule_count=result.rule_count,
            evidence_bindings=ev_bindings,
        )
    except Exception as e:
        return MethodBundle(
            method_id="ZHONGZHOU",
            graph_id=graph_id,
            profile=profile,
            implementation_status="FAIL",
            compute_error=f"{type(e).__name__}: {e}",
        )


def _wrap_feixing(graph, chart) -> MethodBundle:
    """飞星 RuleGraph → MethodBundle (P0-8-A 适配层)"""
    try:
        result = graph.match_all(chart)

        # 适配 FeixingRuleMatch (combo + judgment + evidence_grade + rule_id)
        matches: List[MethodMatch] = []
        for fm in result.matched_rules:
            combo = fm.combo
            matches.append(MethodMatch(
                rule_id=fm.rule_id,
                evidence_grade=fm.evidence_grade,
                semantic_summary=combo.semantic_summary if hasattr(combo, "semantic_summary") else "",
                facts=dict(combo.facts) if hasattr(combo, "facts") else {},
                judgment_strength=getattr(fm.judgment, "strength", "moderate") if fm.judgment else "neutral",
                judgment_text=fm.judgment.raw_text if fm.judgment else "",
            ))

        # 推导 unmatched
        all_prod_ids = {f"FEX-CMB-{i:03d}" for i in range(1, result.rule_count + 1)}
        matched_ids = {m.rule_id for m in matches}
        unmatched = sorted(all_prod_ids - matched_ids)

        # Feixing evidence bindings (P0-5 用 EVIDENCE_TABLE tuple)
        from .feixing import evidence as _fex_ev_mod
        _fex_table = getattr(_fex_ev_mod, "EVIDENCE_BINDINGS", None) or getattr(_fex_ev_mod, "EVIDENCE_TABLE", None) or ()
        ev_bindings = {}
        for ev in (_fex_table if isinstance(_fex_table, (tuple, list)) else _fex_table.values()):
            ev_bindings[ev.rule_id] = {"name": ev.rule_id, "grade": ev.grade}

        return MethodBundle(
            method_id="FEIXING",
            graph_id=graph.graph_id(),
            profile=getattr(graph, "PROFILE", "FEIXING-P0-5-A"),
            implementation_status=result.implementation_status,
            matched_rules=matches,
            unmatched_production_rules=unmatched,
            draft_detected=[],
            rule_count=result.rule_count,
            evidence_bindings=ev_bindings,
        )
    except Exception as e:
        return MethodBundle(
            method_id="FEIXING",
            graph_id=getattr(graph, "graph_id", lambda: "FEIXING-UNKNOWN")(),
            profile=getattr(graph, "PROFILE", "UNKNOWN"),
            implementation_status="FAIL",
            compute_error=f"{type(e).__name__}: {e}",
        )


def _wrap_qintian(graph, chart) -> MethodBundle:
    """钦天 RuleGraph → MethodBundle (钦天 API 最完整, 几乎无需适配)"""
    try:
        result = graph.match_all(chart)

        matches: List[MethodMatch] = []
        for qm in result.matched_rules:
            matches.append(MethodMatch(
                rule_id=qm.rule_id,
                evidence_grade=qm.evidence_grade,
                semantic_summary=qm.semantic_summary,
                facts=dict(qm.facts),
                judgment_strength=qm.judgment_strength,
            ))

        # Qintian evidence bindings
        from .qintian.evidence import EVIDENCE_BINDINGS as QTN_BINDINGS
        ev_bindings = {
            rid: {"name": getattr(ev, "title", getattr(ev, "name", rid)), "grade": ev.grade}
            for rid, ev in QTN_BINDINGS.items()
        }

        return MethodBundle(
            method_id="QINTIAN",
            graph_id=graph.graph_id(),
            profile=getattr(graph, "PROFILE", "QINTIAN-QINTIAN_SIHA-PRODUCTION-A"),
            implementation_status=result.implementation_status,
            matched_rules=matches,
            unmatched_production_rules=list(result.unmatched_production_rules),
            draft_detected=list(result.draft_detected),
            rule_count=graph.rule_count(),
            evidence_bindings=ev_bindings,
        )
    except Exception as e:
        return MethodBundle(
            method_id="QINTIAN",
            graph_id=getattr(graph, "graph_id", lambda: "QINTIAN-UNKNOWN")(),
            profile=getattr(graph, "PROFILE", "UNKNOWN"),
            implementation_status="FAIL",
            compute_error=f"{type(e).__name__}: {e}",
        )


def _wrap_sanhe(graph, chart) -> MethodBundle:
    """三合 SCAFFOLD → MethodBundle (P0-2 SCAFFOLD, 无 production)"""
    return MethodBundle(
        method_id="SANHE",
        graph_id="SANHE-SCAFFOLD",
        profile="SANHE-NONE",
        implementation_status="SCAFFOLD",
        matched_rules=[],
        unmatched_production_rules=[],
        draft_detected=[],
        rule_count=0,
        evidence_bindings={},
    )


# ----- 主入口 -----

def compute_multi_method_signals(
    chart,
    *,
    include_sanhe: bool = True,
) -> MultiMethodSignal:
    """三派并行 compute + 适配 + 聚合

    Args:
        chart: FrozenZiweiChart / ZiweiChart / 任意 duck-typed chart
            需有 .palaces (dict, 飞星要), .palace_stems (钦天要), .flying_transforms (飞星/钦天要), .birth_year
        include_sanhe: 是否包含三合 SCAFFOLD

    Returns:
        MultiMethodSignal with 3-4 MethodBundles
    """
    chart_id = f"chart-{getattr(chart, 'birth_year', 'unknown')}-{id(chart) & 0xFFFF:04x}"

    bundles: Dict[str, MethodBundle] = {}

    # 三派并行
    bundles["ZHONGZHOU"] = _wrap_zhongzhou(make_zhongzhou_rule_graph(), chart)
    bundles["FEIXING"] = _wrap_feixing(make_feixing_rule_graph(), chart)
    bundles["QINTIAN"] = _wrap_qintian(make_qintian_rule_graph(), chart)

    # 三合 SCAFFOLD
    if include_sanhe:
        bundles["SANHE"] = _wrap_sanhe(None, chart)

    # 跨派别共识检测
    consensus = _detect_cross_method_consensus(bundles)

    # 聚合
    total_matched = sum(len(b.matched_rules) for b in bundles.values())
    total_unmatched = sum(len(b.unmatched_production_rules) for b in bundles.values())

    fail_count = sum(1 for b in bundles.values() if b.implementation_status == "FAIL")
    if fail_count == 0:
        compute_status = "OK"
    elif fail_count == len(bundles):
        compute_status = "FAIL"
    else:
        compute_status = "PARTIAL"

    return MultiMethodSignal(
        chart_id=chart_id,
        bundles=bundles,
        cross_method_consensus=consensus,
        total_matched_rules=total_matched,
        total_unmatched_production=total_unmatched,
        compute_status=compute_status,
    )


def _detect_cross_method_consensus(bundles: Dict[str, MethodBundle]) -> List[str]:
    """检测跨派别共识: 同一 fact 字段在 ≥2 派命中且值一致"""
    consensus = []
    fact_key_values_by_method: Dict[str, Dict[str, set]] = {}
    for mid, b in bundles.items():
        fact_key_values_by_method[mid] = {}
        for m in b.matched_rules:
            for k, v in m.facts.items():
                fact_key_values_by_method[mid].setdefault(k, set()).add(str(v))

    all_keys = set()
    for fkv in fact_key_values_by_method.values():
        all_keys.update(fkv.keys())

    for k in sorted(all_keys):
        methods_with_k = [mid for mid, fkv in fact_key_values_by_method.items() if k in fkv]
        if len(methods_with_k) >= 2:
            common = set.intersection(*[fact_key_values_by_method[m][k] for m in methods_with_k])
            if common:
                for v in common:
                    consensus.append(f"{k}={v} (共识于 {', '.join(sorted(methods_with_k))})")

    return consensus
