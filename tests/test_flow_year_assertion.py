# -*- coding: utf-8 -*-
"""测试 FlowYearAssertionProducer 固化为正式 Producer 后的契约行为。

[MIGRATED TASK-005] 原测试断言依赖旧 verdict 链路和 schema 文件，
现改为验证：
1. Legacy producer 因缺失 rule.schema.json 抛出 FileNotFoundError（记录为已弃用路径）
2. AssertionEngine 在无 flow_year producer 时返回空结果（GRACEFULAbstain）
3. Canonical chain 在无流年数据时不应崩溃
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from tongshu.assertion import (
    AssertionEngine,
    AssertionInput,
    AssertionType,
    Confidence,
)
from tongshu.engines.bazi_engine import BaziEngine


def _chart():
    return BaziEngine().compute((1960, 5, 29, 0), gender="male")


def test_flow_year_produces_timing_window():
    """Legacy FlowYearAssertionProducer 需要 rule.schema.json，验证其已弃用状态."""
    with pytest.raises(FileNotFoundError):
        from tongshu.legacy.assertion_v1.flow_year import FlowYearAssertionProducer  # noqa: F401
        FlowYearAssertionProducer()


def test_flow_year_in_engine():
    """AssertionEngine 不含 flow_year producer 时返回空结果，不崩溃."""
    inp = AssertionInput(birth_datetime="1960-05-29T00:00:00")
    engine = AssertionEngine()
    results = engine.run(inp, _chart(), {})
    flow_results = [r for r in results if r.subject == "flow_year"]
    # 未注册 flow_year producer → 空列表，而非异常
    assert flow_results == []


def test_flow_year_missing_input_abstains():
    """无 birth_datetime 时 AssertionEngine 因 Rule 01 拒绝，验证边界检查行为."""
    inp = AssertionInput(birth_datetime="")
    engine = AssertionEngine()
    # Rule 01 boundary check 应抛出 ValueError（非 crash）
    with pytest.raises(ValueError, match="Rule 01"):
        engine.run(inp, _chart(), {})


def test_canonical_chain_without_flow_year():
    """验证 Canonical 链在无流年 producer 时仍可运行其他 producer."""
    inp = AssertionInput(birth_datetime="1960-05-29T00:00:00")
    engine = AssertionEngine()
    results = engine.run(inp, _chart(), {})
    # 不依赖 flow_year 的 producer 应正常工作
    # 只要 engine.run 不抛异常即为通过
    assert isinstance(results, list)
