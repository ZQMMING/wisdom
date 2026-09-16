# -*- coding: utf-8 -*-
"""盲派 Rule Registry V3.2 验证测试
验证: 29条ESTABLISHED Rule全覆盖 + 反例边界 + 禁止规则
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tongshu.engines.blind_rule_registry import RULE_REGISTRY, FORBIDDEN_RULES, COUNTER_EXAMPLES, get_registry_stats
from tongshu.engines.blind_rule_matcher import coverage_report


def test_registry_28_established():
    """29条ESTABLISHED Rule全部在Registry"""
    stats = get_registry_stats()
    assert stats["total"] == 29, f"Registry应28条, 实际{stats['total']}"
    assert stats["established"] == 29, f"ESTABLISHED应28, 实际{stats['established']}"
    print(f"✓ Registry: {stats['total']}条 Rule, 全部ESTABLISHED")


def test_rule_ids_complete():
    """所有Rule_ID符合命名规范"""
    expected_prefixes = ["R-PJ", "R-ZB", "R-GF", "R-BZ", "R-TY",
                         "R-SX", "R-WEALTH", "R-MARRIAGE", "R-BODY",
                         "R-DISASTER", "R-SHEN", "R-MUKU"]
    for rid in RULE_REGISTRY:
        assert any(rid.startswith(p) for p in expected_prefixes), f"Rule_ID命名异常: {rid}"
    print(f"✓ Rule_ID命名规范: {len(RULE_REGISTRY)}条")


def test_forbidden_rules_no_leak():
    """禁止规则不得出现在Registry"""
    for forbidden in FORBIDDEN_RULES:
        for rid in RULE_REGISTRY:
            assert forbidden not in rid, f"禁止规则{forbidden}泄漏到{rid}"
    print(f"✓ 禁止规则0泄漏: {len(FORBIDDEN_RULES)}条禁止规则")


def test_counter_examples_defined():
    """反例测试清单已定义"""
    assert len(COUNTER_EXAMPLES) >= 8, f"反例应≥8条, 实际{len(COUNTER_EXAMPLES)}"
    for name, rule in COUNTER_EXAMPLES:
        assert name and rule, f"反例缺描述: {name}"
    print(f"✓ 反例清单: {len(COUNTER_EXAMPLES)}条")


def test_muku_boundary():
    """MUKU边界: MUKU_OPENED≠WEALTH_GAIN"""
    muku_002 = RULE_REGISTRY["R-MUKU-002"]
    assert "MUKU_OPENED≠WEALTH_GAIN" in muku_002.exclusions, \
        "R-MUKU-002必须写明 MUKU_OPENED≠WEALTH_GAIN"
    assert "合库=闭库" in muku_002.exclusions, "必须写明合库=闭库"
    print("✓ MUKU边界: MUKU_OPENED≠WEALTH_GAIN 已锁死")


def test_no_scoring_in_rules():
    """所有Rule不得含评分/百分比/概率"""
    forbidden_words = ["评分", "score", "百分比", "概率", "probability", "0.", "分>"]
    for rid, rule in RULE_REGISTRY.items():
        text = f"{rule.rule_logic} {rule.assertion} {rule.description}"
        for fw in forbidden_words:
            assert fw not in text, f"{rid} 含禁止词'{fw}'"
    print("✓ 无评分/百分比/概率泄漏")


def test_evidence_provenance():
    """所有Rule都有Evidence_ID"""
    for rid, rule in RULE_REGISTRY.items():
        assert rule.evidence_id.startswith("EVD-"), f"{rid} 缺Evidence_ID"
        assert rule.status == "ESTABLISHED", f"{rid} 状态不是ESTABLISHED"
    print("✓ 28条Rule全部有Evidence provenance")


def test_coverage_report():
    """覆盖率报告可生成"""
    rep = coverage_report()
    assert rep["registry_total"] == 29
    assert len(rep["rule_ids"]) == 29
    print(f"✓ 覆盖率报告: {rep['registry_total']}条Rule")


if __name__ == "__main__":
    test_registry_28_established()
    test_rule_ids_complete()
    test_forbidden_rules_no_leak()
    test_counter_examples_defined()
    test_muku_boundary()
    test_no_scoring_in_rules()
    test_evidence_provenance()
    test_coverage_report()
    print("\n=== 全部通过 ===")

