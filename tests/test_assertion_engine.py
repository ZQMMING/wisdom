"""AssertionEngine 接口测试。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tongshu.assertion.contract import (
    Assertion,
    AssertionInput,
    AssertionType,
    Confidence,
    Direction,
    StateKind,
)
from tongshu.assertion.engine import AssertionEngine


def _make_producer(subject, assertion=None, raise_exc=False):
    class P:
        pass

    P.subject = subject

    def produce(self, inp, chart, context):
        if raise_exc:
            raise RuntimeError("boom")
        return assertion

    P.produce = produce
    return P()


def test_engine_rejects_duplicate_subject():
    eng = AssertionEngine()
    eng.register(_make_producer("健康"))
    try:
        eng.register(_make_producer("健康"))
        assert False, "duplicate registration should fail"
    except ValueError:
        pass


def test_engine_run_enforces_rule01():
    eng = AssertionEngine()
    try:
        eng.run(AssertionInput(birth_datetime=""), None)
        assert False
    except ValueError as e:
        assert "Rule 01" in str(e)


def test_engine_downgrades_producer_exception():
    """Producer 异常 → 该主题降级 INSUFFICIENT_EVIDENCE, 不影响其他。"""
    ok = Assertion(
        subject="财运",
        assertion_type=AssertionType.STRUCTURAL,
        confidence=Confidence.LIKELY,
        abstain=False,
    )
    eng = AssertionEngine()
    eng.register(_make_producer("健康", raise_exc=True))
    eng.register(_make_producer("财运", assertion=ok))
    results = {a.subject: a for a in eng.run(AssertionInput(birth_datetime="1982-09-27"), None)}
    assert results["健康"].abstain is True
    assert results["健康"].assertion_type == AssertionType.INSUFFICIENT_EVIDENCE
    assert results["财运"] is ok


def test_engine_final_abstention_line():
    """WEAK 置信但未拒断 → 最终防线强制降级。"""
    bad = Assertion(
        subject="婚姻",
        assertion_type=AssertionType.STRUCTURAL,
        confidence=Confidence.WEAK,
        abstain=False,
    )
    eng = AssertionEngine()
    eng.register(_make_producer("婚姻", assertion=bad))
    (a,) = eng.run(AssertionInput(birth_datetime="1982-09-27"), None)
    assert a.abstain is True
