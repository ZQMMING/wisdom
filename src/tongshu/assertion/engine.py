"""AssertionEngine 接口 (DISPATCH_HERMES_ASSERTION_CONTRACT.md Sprint A.2)。

所有主题 Producer 实现同一输出格式(Assertion)。
引擎负责: Producer 注册、输入边界校验、Abstention 汇总、置信裁定。
"""
from __future__ import annotations

from typing import Callable, Protocol

from tongshu.assertion.contract import (
    Assertion,
    AssertionInput,
    Confidence,
    insufficient_evidence,
)


class AssertionProducer(Protocol):
    """P3 Producer 协议: 输入合法 AssertionInput + 计算上下文 → Assertion。"""

    subject: str

    def produce(self, inp: AssertionInput, chart, context: dict) -> Assertion: ...


class AssertionEngine:
    """断言引擎: 统一入口, 强制契约。"""

    def __init__(self) -> None:
        self._producers: dict[str, AssertionProducer] = {}

    def register(self, producer: AssertionProducer) -> None:
        """注册 Producer; subject 重复即拒绝(单一职责)。"""
        if producer.subject in self._producers:
            raise ValueError(f"producer for '{producer.subject}' already registered")
        self._producers[producer.subject] = producer

    @property
    def subjects(self) -> list[str]:
        return sorted(self._producers)

    def run(self, inp: AssertionInput, chart, context: dict | None = None) -> list[Assertion]:
        """跑全部 Producer。

        - 先校验输入边界(Rule 01)
        - 单个 Producer 异常 → 该主题降级为 INSUFFICIENT_EVIDENCE(Rule 04),
          不影响其他 Producer
        """
        errs = inp.validate()
        if errs:
            raise ValueError(f"Rule 01 violation: {errs}")
        context = context or {}

        results: list[Assertion] = []
        for subject in self.subjects:
            producer = self._producers[subject]
            try:
                a = producer.produce(inp, chart, context)
            except Exception as exc:  # noqa: BLE001 — 契约要求降级不炸全局
                results.append(
                    insufficient_evidence(subject, f"producer error: {exc}")
                )
                continue
            results.append(self._enforce_abstention(a))
        return results

    @staticmethod
    def _enforce_abstention(a: Assertion) -> Assertion:
        """最终防线: INSUFFICIENT_EVIDENCE/WEAK 必须拒断(Rule 04)。"""
        if a.confidence in (Confidence.WEAK, Confidence.INSUFFICIENT_EVIDENCE) and not a.abstain:
            return insufficient_evidence(a.subject, f"downgraded: confidence={a.confidence.value}")
        return a


__all__ = ["AssertionEngine", "AssertionProducer"]
