# -*- coding: utf-8 -*-
"""P0-6.1: Aggregation Golden Replay

目标: 验证授权等级在聚合过程中不会被升级

测试场景:
1. COMPLETE + COMPLETE → 合法聚合
2. COMPLETE + PARTIAL → PARTIAL / 不得升级
3. PARTIAL + PARTIAL → 不得升级 COMPLETE
4. UNRESOLVED → 阻断
5. Conflict → 不得强制裁决
"""
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class JudgmentAuthorization(Enum):
    AUTHORIZED_COMPLETE = "authorized_complete"
    AUTHORIZED_PARTIAL = "authorized_partial"
    UNRESOLVED = "unresolved"

class AggregationType(Enum):
    COMPLEMENTARY = "complementary"
    EVIDENCE_CHAIN = "evidence_chain"
    LEVEL_COMBINATION = "level_combination"

class AggregationResult:
    def __init__(self, judgments, aggregation_type, conclusion, eligible_for_higher_level, violations=None):
        self.judgments = judgments
        self.aggregation_type = aggregation_type
        self.conclusion = conclusion
        self.eligible_for_higher_level = eligible_for_higher_level
        self.violations = violations or []

class LocalJudgment:
    def __init__(self, primitive_id, name, authorization, judgment, unresolved_parts=None):
        self.primitive_id = primitive_id
        self.name = name
        self.authorization = authorization
        self.judgment = judgment
        self.unresolved_parts = unresolved_parts or []

class AggregationGate:
    def validate_complementary(self, judgments):
        """验证互补组合"""
        # 检查是否有 UNRESOLVED
        unresolved = [j for j in judgments if j.authorization == JudgmentAuthorization.UNRESOLVED]
        if unresolved:
            return AggregationResult(
                judgments=judgments,
                aggregation_type=AggregationType.COMPLEMENTARY,
                conclusion=f"发现 {len(unresolved)} 个 UNRESOLVED，阻断聚合",
                eligible_for_higher_level=False,
                violations=["UNRESOLVED 阻断"]
            )
        
        # 检查冲突：完全相反的 COMPLETE Judgment
        complete_judgments = [j for j in judgments if j.authorization == JudgmentAuthorization.AUTHORIZED_COMPLETE]
        passed = [j for j in complete_judgments if j.judgment]
        failed = [j for j in complete_judgments if not j.judgment]
        
        conflicts = []
        if passed and failed:
            # 有矛盾：一个说成立，一个说不成立
            conflicts = [
                f"Conflict: {p.name} 成立 vs {f.name} 不成立"
                for p in passed
                for f in failed
            ]
        
        # 统计授权等级
        complete_count = sum(1 for j in judgments if j.authorization == JudgmentAuthorization.AUTHORIZED_COMPLETE)
        partial_count = sum(1 for j in judgments if j.authorization == JudgmentAuthorization.AUTHORIZED_PARTIAL)
        
        # 检查是否有错误升级
        violations = list(conflicts)
        
        if partial_count > 0 and complete_count == 0:
            # 所有都是 PARTIAL，结果应该是 PARTIAL
            pass
        elif partial_count > 0 and complete_count > 0:
            # 混合情况，结果应该是 PARTIAL
            pass
        
        # 所有都是 COMPLETE
        if complete_count == len(judgments):
            if conflicts:
                return AggregationResult(
                    judgments=judgments,
                    aggregation_type=AggregationType.COMPLEMENTARY,
                    conclusion=f"发现 {len(conflicts)} 个冲突，不得强制裁决，降级为 UNRESOLVED",
                    eligible_for_higher_level=False,
                    violations=["冲突需降级", "不得强制裁决"]
                )
            return AggregationResult(
                judgments=judgments,
                aggregation_type=AggregationType.COMPLEMENTARY,
                conclusion=f"所有 {len(judgments)} 个 Judgment 都是 AUTHORIZED_COMPLETE，合法聚合",
                eligible_for_higher_level=True,
                violations=violations
            )
        
        # 有 PARTIAL
        return AggregationResult(
            judgments=judgments,
            aggregation_type=AggregationType.COMPLEMENTARY,
            conclusion=f"包含 {partial_count} 个 AUTHORIZED_PARTIAL，结果降为 PARTIAL，不得进入更高层级",
            eligible_for_higher_level=False,
            violations=violations
        )
    
    def validate_evidence_chain(self, judgments):
        """验证证据链聚合"""
        # 检查是否有 UNRESOLVED
        unresolved = [j for j in judgments if j.authorization == JudgmentAuthorization.UNRESOLVED]
        if unresolved:
            return AggregationResult(
                judgments=judgments,
                aggregation_type=AggregationType.EVIDENCE_CHAIN,
                conclusion=f"发现 {len(unresolved)} 个 UNRESOLVED，阻断聚合",
                eligible_for_higher_level=False,
                violations=["UNRESOLVED 阻断"]
            )
        
        # 统计授权等级
        complete_count = sum(1 for j in judgments if j.authorization == JudgmentAuthorization.AUTHORIZED_COMPLETE)
        partial_count = sum(1 for j in judgments if j.authorization == JudgmentAuthorization.AUTHORIZED_PARTIAL)
        
        # 检查是否有错误升级
        violations = []
        
        # 如果只有 PARTIAL，不能升级成 COMPLETE
        if complete_count == 0 and partial_count > 0:
            return AggregationResult(
                judgments=judgments,
                aggregation_type=AggregationType.EVIDENCE_CHAIN,
                conclusion=f"证据链包含 {partial_count} 个 AUTHORIZED_PARTIAL，只能作为 Evidence 输出，不得进入更高层级",
                eligible_for_higher_level=False,
                violations=violations
            )
        
        # 混合情况
        if complete_count > 0 and partial_count > 0:
            return AggregationResult(
                judgments=judgments,
                aggregation_type=AggregationType.EVIDENCE_CHAIN,
                conclusion=f"证据链包含 {complete_count} 个 AUTHORIZED_COMPLETE + {partial_count} 个 AUTHORIZED_PARTIAL，降为 PARTIAL，不得进入更高层级",
                eligible_for_higher_level=False,
                violations=violations
            )
        
        # 所有都是 COMPLETE
        return AggregationResult(
            judgments=judgments,
            aggregation_type=AggregationType.EVIDENCE_CHAIN,
            conclusion=f"证据链完整，{complete_count} 个 AUTHORIZED_COMPLETE，可进入更高层级",
            eligible_for_higher_level=True,
            violations=violations
        )

def test_scenario_1_complete_plus_complete():
    """场景 1: COMPLETE + COMPLETE → 合法聚合"""
    print("\n【场景 1】COMPLETE + COMPLETE → 合法聚合")
    
    gate = AggregationGate()
    judgments = [
        LocalJudgment("P1", "Primitive 1", JudgmentAuthorization.AUTHORIZED_COMPLETE, True),
        LocalJudgment("P2", "Primitive 2", JudgmentAuthorization.AUTHORIZED_COMPLETE, True),
    ]
    
    result = gate.validate_complementary(judgments)
    
    print(f"  结论: {result.conclusion}")
    print(f"  可进入更高层级: {'✅ 是' if result.eligible_for_higher_level else '❌ 否'}")
    print(f"  违规: {result.violations if result.violations else '无'}")
    
    assert result.eligible_for_higher_level == True, "COMPLETE + COMPLETE 应该可以进入更高层级"
    assert len(result.violations) == 0, "不应该有违规"
    print("  ✅ PASS")
    return result

def test_scenario_2_complete_plus_partial():
    """场景 2: COMPLETE + PARTIAL → PARTIAL / 不得升级"""
    print("\n【场景 2】COMPLETE + PARTIAL → PARTIAL / 不得升级")
    
    gate = AggregationGate()
    judgments = [
        LocalJudgment("P1", "Primitive 1", JudgmentAuthorization.AUTHORIZED_COMPLETE, True),
        LocalJudgment("P2", "Primitive 2", JudgmentAuthorization.AUTHORIZED_PARTIAL, True, ["未实现部分"]),
    ]
    
    result = gate.validate_complementary(judgments)
    
    print(f"  结论: {result.conclusion}")
    print(f"  可进入更高层级: {'✅ 是' if result.eligible_for_higher_level else '❌ 否'}")
    print(f"  违规: {result.violations if result.violations else '无'}")
    
    assert result.eligible_for_higher_level == False, "COMPLETE + PARTIAL 不应该进入更高层级"
    assert len(result.violations) == 0, "不应该有违规（降级是正确的）"
    print("  ✅ PASS")
    return result

def test_scenario_3_partial_plus_partial():
    """场景 3: PARTIAL + PARTIAL → 不得升级 COMPLETE"""
    print("\n【场景 3】PARTIAL + PARTIAL → 不得升级 COMPLETE")
    
    gate = AggregationGate()
    judgments = [
        LocalJudgment("P1", "Primitive 1", JudgmentAuthorization.AUTHORIZED_PARTIAL, True, ["未实现部分 1"]),
        LocalJudgment("P2", "Primitive 2", JudgmentAuthorization.AUTHORIZED_PARTIAL, True, ["未实现部分 2"]),
    ]
    
    result = gate.validate_complementary(judgments)
    
    print(f"  结论: {result.conclusion}")
    print(f"  可进入更高层级: {'✅ 是' if result.eligible_for_higher_level else '❌ 否'}")
    print(f"  违规: {result.violations if result.violations else '无'}")
    
    assert result.eligible_for_higher_level == False, "PARTIAL + PARTIAL 不应该进入更高层级"
    assert len(result.violations) == 0, "不应该有违规"
    print("  ✅ PASS")
    return result

def test_scenario_4_unresolved():
    """场景 4: UNRESOLVED → 阻断"""
    print("\n【场景 4】UNRESOLVED → 阻断")
    
    gate = AggregationGate()
    judgments = [
        LocalJudgment("P1", "Primitive 1", JudgmentAuthorization.AUTHORIZED_COMPLETE, True),
        LocalJudgment("P2", "Primitive 2", JudgmentAuthorization.UNRESOLVED, False),
    ]
    
    result = gate.validate_complementary(judgments)
    
    print(f"  结论: {result.conclusion}")
    print(f"  可进入更高层级: {'✅ 是' if result.eligible_for_higher_level else '❌ 否'}")
    print(f"  违规: {result.violations}")
    
    assert result.eligible_for_higher_level == False, "UNRESOLVED 应该阻断聚合"
    assert any("UNRESOLVED" in v for v in result.violations), "应该有 UNRESOLVED 阻断违规"
    print("  ✅ PASS")
    return result

def test_scenario_5_conflict():
    """场景 5: Conflict → 不得强制裁决"""
    print("\n【场景 5】Conflict → 不得强制裁决")
    
    gate = AggregationGate()
    judgments = [
        LocalJudgment("P1", "Primitive 1", JudgmentAuthorization.AUTHORIZED_COMPLETE, True),
        LocalJudgment("P2", "Primitive 2", JudgmentAuthorization.AUTHORIZED_COMPLETE, False),
    ]
    
    # 模拟冲突：两个 COMPLETE Judgment 互相矛盾
    result = gate.validate_complementary(judgments)
    
    print(f"  结论: {result.conclusion}")
    print(f"  可进入更高层级: {'✅ 是' if result.eligible_for_higher_level else '❌ 否'}")
    print(f"  违规: {result.violations}")
    
    assert result.eligible_for_higher_level == False, "Conflict 应该阻断聚合，不得强制裁决"
    assert any("冲突" in v or "不得强制裁决" in v for v in result.violations), "应该有冲突违规"
    print("  ✅ PASS")
    return result

def main():
    print("=" * 60)
    print("P0-6.1: Aggregation Golden Replay")
    print("=" * 60)
    
    results = []
    
    # 场景 1-4 必须通过
    results.append(("COMPLETE + COMPLETE", test_scenario_1_complete_plus_complete()))
    results.append(("COMPLETE + PARTIAL", test_scenario_2_complete_plus_partial()))
    results.append(("PARTIAL + PARTIAL", test_scenario_3_partial_plus_partial()))
    results.append(("UNRESOLVED", test_scenario_4_unresolved()))
    
    # 场景 5 需要确认
    results.append(("Conflict", test_scenario_5_conflict()))
    
    # 汇总
    print(f"\n{'='*60}")
    print("Golden Replay 汇总")
    print("=" * 60)
    
    # 所有 5 个场景都通过了 assert 检查
    passed = len(results)
    print(f"测试场景: {len(results)} 个")
    print(f"通过: {passed} 个")
    print(f"成功率: {passed/len(results)*100:.1f}%")
    
    # 保存结果
    output_path = Path(__file__).parent.parent / "data" / "p0_6_1_golden_replay.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "test_cases": [
                {
                    "name": name,
                    "eligible_for_higher_level": r.eligible_for_higher_level,
                    "violations": r.violations,
                    "conclusion": r.conclusion,
                }
                for name, r in results
            ]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")

if __name__ == "__main__":
    main()
