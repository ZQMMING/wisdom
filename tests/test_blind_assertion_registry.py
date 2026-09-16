# -*- coding: utf-8 -*-
"""盲派 Assertion Registry V3.2 验证测试
Gate: 29 Rule全部有Assertion映射 + Judgment 0泄漏 + 跨层0推断
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tongshu.engines.blind_rule_registry import RULE_REGISTRY
from tongshu.engines.blind_assertion_registry import ASSERTION_REGISTRY, FORBIDDEN_ASSERTIONS, get_assertion_stats


def test_assertion_coverage():
    """29 Rule 全部有合法 Assertion 映射"""
    rule_ids = set(RULE_REGISTRY.keys())
    assertion_rule_ids = set(a.rule_id for a in ASSERTION_REGISTRY.values())
    missing = rule_ids - assertion_rule_ids
    assert not missing, f"以下Rule缺Assertion映射: {missing}"
    print(f"✓ Assertion Coverage: {len(rule_ids)}/{len(assertion_rule_ids)} Rule全覆盖")


def test_assertion_count_match():
    """Assertion 数量 = Rule 数量（一对一）"""
    stats = get_assertion_stats()
    assert stats["total"] == len(RULE_REGISTRY), \
        f"Assertion数{stats['total']}≠Rule数{len(RULE_REGISTRY)}"
    print(f"✓ Assertion数={stats['total']} Rule数={len(RULE_REGISTRY)} 一对一")


def test_provenance_chain():
    """每条Assertion→Rule→Evidence 100%可追溯"""
    for aid, a in ASSERTION_REGISTRY.items():
        assert a.rule_id in RULE_REGISTRY, f"{aid} rule_id={a.rule_id}不在Registry"
        assert a.evidence_id.startswith("EVD-"), f"{aid} 缺Evidence_ID"
        assert a.provenance.startswith(a.rule_id), f"{aid} provenance链不完整"
    print("✓ Assertion→Rule→Evidence 100%可追溯")


def test_no_judgment_leakage():
    """禁止的Judgment Assertion不得出现在Registry"""
    forbidden_words = ["WEALTH_GAIN", "WEALTH_LEVEL", "MARRIED", "DIVORCED",
                       "DISEASE", "DEFINITE_PRISON", "发财", "必结婚", "必离婚"]
    for aid, a in ASSERTION_REGISTRY.items():
        text = f"{a.assertion_id} {a.relation} {a.object} {a.conditions}"
        for fw in forbidden_words:
            assert fw not in text, f"{aid} 含Judgment泄漏词'{fw}'"
    print("✓ Judgment Leakage: 0")


def test_no_cross_layer_inference():
    """MUKU_OPENED不得自动产生WEALTH_GAIN"""
    a_muku = ASSERTION_REGISTRY["A-MUKU-OPENED"]
    assert "WEALTH" not in a_muku.object, "MUKU_OPENED泄漏到财富层"
    assert "GAIN" not in a_muku.relation, "MUKU_OPENED泄漏到发财"
    print("✓ 跨层推断: 0 (MUKU_OPENED≠WEALTH_GAIN)")


def test_forbidden_assertions_defined():
    """禁止Assertion清单已定义"""
    assert len(FORBIDDEN_ASSERTIONS) >= 5
    for fid, desc in FORBIDDEN_ASSERTIONS.items():
        assert fid not in ASSERTION_REGISTRY, f"禁止Assertion {fid}泄漏到Registry"
    print(f"✓ 禁止Assertion: {len(FORBIDDEN_ASSERTIONS)}条全禁")


def test_no_score_or_probability():
    """Assertion不得含评分/概率"""
    forbidden = ["评分", "score", "概率", "probability", "0.", "分>"]
    for aid, a in ASSERTION_REGISTRY.items():
        text = f"{a.relation} {a.object} {a.conditions}"
        for fw in forbidden:
            assert fw not in text, f"{aid} 含禁止词'{fw}'"
    print("✓ 无评分/概率泄漏")


def test_assertion_types():
    """Assertion类型分三类"""
    stats = get_assertion_stats()
    assert stats["structural"] > 0
    assert stats["timing"] > 0
    assert stats["relation"] > 0
    print(f"✓ Assertion类型: 结构{stats['structural']} 时{stats['timing']} 关系{stats['relation']}")


def test_marriage_timing_not_event():
    """结婚/离婚应期≠已发生事件"""
    a_m = ASSERTION_REGISTRY["A-MARRIAGE-TIMING"]
    assert "CANDIDATE" in a_m.object, "结婚应期必须是候选不是已发生"
    a_d = ASSERTION_REGISTRY["A-DIVORCE-TIMING"]
    assert "CANDIDATE" in a_d.object, "离婚应期必须是候选不是已发生"
    print("✓ 应期=候选窗口，不是事件坐实")


if __name__ == "__main__":
    test_assertion_coverage()
    test_assertion_count_match()
    test_provenance_chain()
    test_no_judgment_leakage()
    test_no_cross_layer_inference()
    test_forbidden_assertions_defined()
    test_no_score_or_probability()
    test_assertion_types()
    test_marriage_timing_not_event()
    print("\n=== Assertion Registry 全部通过 ===")
