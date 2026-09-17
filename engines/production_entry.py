# -*- coding: utf-8 -*-
"""Production Entry Gate (PATCH-ProdGate)
唯一生产入口: production_entry(chart: FrozenCanonicalBaziChart) -> EngineResult.
Gate 只验证身份/contract, 不排盘, 不重算; 失败 fail-closed, 不进入主链.
l0_fact_builder.build() 是内部计算 primitive, 不由外部直接调用作生产入口.
"""
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True)
class FrozenCanonicalBaziChart:
    """Canonical/Frozen Bazi 身份对象.
    外部生产方必须构造此对象进入 gate; 普通 pillars dict / BaziChart / BirthInput 一律拒绝.
    本类不排盘, 只携带已冻结的 canonical pillars 与身份标记."""
    pillars: Dict[str, list]
    canonical: bool = True
    frozen: bool = True
    source: str = "canonical_frozen"


def _fail_closed(reason: str, gate: str) -> Dict[str, Any]:
    return {
        "engine_result": None,
        "gate_passed": False,
        "gate": gate,
        "reason": reason,
        "boundary_note": "Gate 失败 fail-closed, 未执行任何 Rule/Judgment",
    }


def _validate_contract(pillars: Dict[str, list]) -> str:
    """验证 canonical contract 完整性. 返回 '' 表示通过, 否则错误原因."""
    required = ("year", "month", "day", "hour")
    if not isinstance(pillars, dict):
        return "pillars 不是 dict"
    for k in required:
        if k not in pillars:
            return f"缺 {k}"
        v = pillars[k]
        if not isinstance(v, (list, tuple)) or len(v) != 2:
            return f"{k} 不是 [干, 支]"
    return ""


def production_entry(chart: Any) -> Dict[str, Any]:
    """唯一生产入口.
    G-P01 类型 = FrozenCanonicalBaziChart
    G-P02 canonical/frozen 身份有效
    G-P03 必要 canonical contract 完整
    G-P04 通过 Gate 后才进入主链
    G-P05 失败 fail-closed, 不执行任何 Rule/Judgment
    """
    # G-P01
    if not isinstance(chart, FrozenCanonicalBaziChart):
        return _fail_closed(
            "输入不是 FrozenCanonicalBaziChart; 普通 dict/BaziChart/BirthInput 不得作为生产入口",
            "G-P01")
    # G-P02
    if not (getattr(chart, "canonical", False) and getattr(chart, "frozen", False)):
        return _fail_closed("缺 canonical/frozen 身份标记", "G-P02")
    # G-P03
    err = _validate_contract(chart.pillars)
    if err:
        return _fail_closed(f"canonical contract 不完整: {err}", "G-P03")

    # G-P04 通过 Gate, 进入主链 (内部 primitive build)
    from engines.common.l0_fact_builder import build
    facts = build(chart.pillars)
    return {
        "engine_result": facts,
        "gate_passed": True,
        "gate": "PASSED",
        "reason": "canonical/frozen 身份有效, contract 完整",
        "source": chart.source,
        "boundary_note": "facts 仅为 L0 结构事实; 不判身强/用神/吉凶; Judgment 仍走 fail-closed gate",
    }
