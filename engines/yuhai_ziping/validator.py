"""YHZP Input/Output Validator（Phase 1 骨架；Phase 2 以 contract.json 锁定）。

输入：Frozen Canonical Bazi Chart 引用（§3 Downstream Rule：MUST consume /
MUST NOT modify / MUST NOT re-chart）。Phase 1 只做 Gate + 契约骨架校验。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft202012Validator

from shared_types.enums import EngineStatus
from shared_types.fail_closed import FailClosedReason, FailClosedError
from shared_types.gate_result import GateOutcome
from phase0.canonical_gate import CanonicalGate

ENGINES_DIR = Path(__file__).resolve().parent.parent.parent

# §B-2/§K-1 YHZP 允许的 L0 core facts（Phase 2 由 contract.json allowed_fields 锁定）
YHZP_L0_FIELDS = {
    "pillars", "hidden_stems", "shishen", "wuxing", "yinyang",
    "nayin", "xunkong", "changsheng", "relations",
}

# §B-5 YHZP 禁止输出
YHZP_FORBIDDEN_OUTPUT = {
    "global_strength", "global_yongshen", "modern_signal", "modern_conclusion",
    "llm_judgment", "cross_classic_priority",
}


class YHZPInputValidator:
    """输入校验：只接受 Frozen Canonical Bazi Chart（ref/hash 引用）。"""

    def __init__(self) -> None:
        self.gate = CanonicalGate()

    def validate(self, canonical_chart: Dict[str, Any]) -> str:
        """返回 canonical_input ref；Gate 失败 → FAIL_CLOSED。"""
        if not isinstance(canonical_chart, dict):
            raise FailClosedError(FailClosedReason.INPUT_FORBIDDEN, "canonical_chart 非字典")
        ref = canonical_chart.get("canonical_input", {}).get("ref")
        if not ref:
            raise FailClosedError(FailClosedReason.INPUT_FORBIDDEN, "缺少 canonical_input.ref")
        # §3.4：禁止重排盘
        if canonical_chart.get("recalculated") is True:
            raise FailClosedError(FailClosedReason.INPUT_FORBIDDEN, "禁止重新排盘")
        summary = self.gate.run_or_fail(canonical_chart)
        if not summary.all_passed:
            raise FailClosedError(FailClosedReason.CANONICAL_GATE, f"Gate 未全过: {summary.failed_gates}")
        return ref


class YHZPOutputValidator:
    """输出校验：EngineResult 必须符合 §70 结构且无禁用输出（§B-5）。"""

    def __init__(self) -> None:
        schema_path = ENGINES_DIR / "shared_schema" / "engine_result.schema.json"
        self.validator = Draft202012Validator(json.loads(schema_path.read_text(encoding="utf-8")))

    def validate(self, result_dict: Dict[str, Any]) -> None:
        errors = list(self.validator.iter_errors(result_dict))
        if errors:
            raise FailClosedError(FailClosedReason.CONTRACT_INVALID, f"EngineResult 违反 Schema: {errors[0].message}")
        facts = result_dict.get("facts", {})
        for group, items in facts.items():
            for item in items:
                if isinstance(item, dict):
                    bad = [f for f in YHZP_FORBIDDEN_OUTPUT if f in {k.lower() for k in item.keys()}]
                    if bad:
                        raise FailClosedError(FailClosedReason.CONTRACT_INVALID, f"输出含禁用字段: {bad}")
        if result_dict.get("status") not in {s.value for s in EngineStatus}:
            raise FailClosedError(FailClosedReason.CONTRACT_INVALID, f"非法 status: {result_dict.get('status')}")
