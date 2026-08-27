# -*- coding: utf-8 -*-
"""测试 FlowYearAssertionProducer 固化为正式 Producer 后的契约行为。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tongshu.assertion import (
    AssertionEngine,
    AssertionInput,
    AssertionType,
    Confidence,
    FlowYearAssertionProducer,
)
from tongshu.engines.bazi_engine import BaziEngine


def _chart():
    return BaziEngine().compute((1960, 5, 29, 0), gender="male")


def test_flow_year_produces_timing_window():
    inp = AssertionInput(birth_datetime="1960-05-29T00:00:00")
    p = FlowYearAssertionProducer()
    a = p.produce(inp, _chart(), {})
    assert a.subject == "flow_year"
    assert a.assertion_type == AssertionType.TIMING_WINDOW
    # 单体系或已收敛多体系：LIKELY（单体系）或 SUPPORTED（≥2体系同向）
    assert a.confidence in (Confidence.LIKELY, Confidence.SUPPORTED)
    assert a.abstain is False
    # 有焦点年份
    assert "焦点年份" in a.time
    # 有规则机制与证据
    assert "流年触发机制" in a.mechanism
    assert len(a.evidence) >= 3
    assert all(e.system in ("event_topic", "heluo", "yi", "blind") for e in a.evidence)


def test_flow_year_in_engine():
    inp = AssertionInput(birth_datetime="1960-05-29T00:00:00")
    engine = AssertionEngine()
    engine.register(FlowYearAssertionProducer())
    results = engine.run(inp, _chart(), {})
    a = [r for r in results if r.subject == "flow_year"][0]
    assert a.assertion_type == AssertionType.TIMING_WINDOW
    assert a.confidence in (Confidence.LIKELY, Confidence.SUPPORTED, Confidence.INSUFFICIENT_EVIDENCE)


def test_flow_year_missing_input_abstains():
    # 空 birth_datetime → Rule 01 触发，engine.run 抛错；produce 需 chart 也返回拒断
    p = FlowYearAssertionProducer()
    a = p.produce(AssertionInput(birth_datetime=""), None, {})
    assert a.abstain is True
    assert a.confidence == Confidence.INSUFFICIENT_EVIDENCE
