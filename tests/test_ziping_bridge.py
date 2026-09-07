"""ZIPING 辨层接线测试 — BaziEngine → ZipingBridge → JudgmentFactory

验证:
1. build_context 将 BaziChart 正确转换为 judgment context
2. run_ziping_judgment 端到端产出五大域判断
3. 判断可追溯 (rule_refs/evidence_refs)
4. Fail Closed: 空chart不崩溃
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tongshu.engines.bazi_engine import BaziEngine  # noqa: E402
from tongshu.reasoning.ziping_bridge import (  # noqa: E402
    build_context,
    run_ziping_judgment,
    synthesis_to_dict,
)
from tongshu.reasoning.judgment import JudgmentConclusion  # noqa: E402


def _make_chart(solar_date=(1990, 3, 1, 12), gender="male"):
    engine = BaziEngine()
    return engine.compute(solar_date=solar_date, gender=gender)


def test_build_context_structure():
    """build_context 必须输出 {natal: {pillars: [4], day_master}}。"""
    chart = _make_chart()
    ctx = build_context(chart)
    assert "natal" in ctx
    assert len(ctx["natal"]["pillars"]) == 4
    assert ctx["natal"]["day_master"]
    positions = [p["position"] for p in ctx["natal"]["pillars"]]
    assert positions == ["YEAR", "MONTH", "DAY", "HOUR"]
    # 每柱有干支
    for p in ctx["natal"]["pillars"]:
        assert p["heavenly_stem"]
        assert p["earthly_branch"]


def test_run_ziping_judgment_core_domains():
    """端到端: 判断层必须产出核心三域 (旺衰/格局/用神)。"""
    chart = _make_chart()
    s = run_ziping_judgment(chart)
    # 核心三域必须有结果 (可为 UNKNOWN 但不能是 None)
    assert s.wangshuai is not None
    assert s.geju is not None
    assert s.yongshen is not None
    # 结论是合法枚举值
    assert s.wangshuai.conclusion in JudgmentConclusion


def test_judgment_traceable():
    """判断必须可追溯: rule_refs/evidence_refs 结构存在。"""
    chart = _make_chart()
    s = run_ziping_judgment(chart)
    for domain in (s.wangshuai, s.geju, s.yongshen):
        assert hasattr(domain, "rule_refs")
        assert hasattr(domain, "evidence_refs")
        # reasoning 非空 (有判断依据)
        assert domain.reasoning


def test_deterministic():
    """确定性: 相同 chart → 相同结论。"""
    chart1 = _make_chart()
    chart2 = _make_chart()
    s1 = run_ziping_judgment(chart1)
    s2 = run_ziping_judgment(chart2)
    assert s1.wangshuai.conclusion == s2.wangshuai.conclusion
    assert s1.geju.conclusion == s2.geju.conclusion
    assert s1.yongshen.conclusion == s2.yongshen.conclusion


def test_fail_closed_empty_chart():
    """Fail Closed: 空对象不崩溃，返回 UNKNOWN。"""
    class Empty:
        pass
    s = run_ziping_judgment(Empty())
    assert s.wangshuai is not None
    assert s.wangshuai.conclusion == JudgmentConclusion.UNKNOWN


def test_synthesis_to_dict():
    """序列化: 输出可被解层消费的 dict。"""
    chart = _make_chart()
    s = run_ziping_judgment(chart)
    d = synthesis_to_dict(s)
    assert "wangshuai" in d
    assert "has_core_judgment" in d
    assert isinstance(d, dict)
