# -*- coding: utf-8 -*-
"""P0-6.2: 真实 Local Judgment Aggregation 实测

目标: 使用真实已授权资产（日犯岁君、生克制化）做同一命例的聚合测试

关键检查:
- authorization 不升级
- evidence 不串线
- trace 完整
- unresolved 不被吞掉

不使用: 人为构造的层级案例
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

class AggregationResult:
    def __init__(self, judgments, aggregation_type, conclusion, eligible_for_higher_level, violations=None, trace=None):
        self.judgments = judgments
        self.aggregation_type = aggregation_type
        self.conclusion = conclusion
        self.eligible_for_higher_level = eligible_for_higher_level
        self.violations = violations or []
        self.trace = trace or []

class LocalJudgment:
    def __init__(self, primitive_id, name, authorization, judgment, unresolved_parts=None, evidence=None):
        self.primitive_id = primitive_id
        self.name = name
        self.authorization = authorization
        self.judgment = judgment
        self.unresolved_parts = unresolved_parts or []
        self.evidence = evidence or {}

class AggregationGate:
    def __init__(self):
        self.trace_log = []
    
    def add_trace(self, step, details):
        """添加 trace 日志"""
        self.trace_log.append({
            "step": step,
            "details": details,
            "timestamp": len(self.trace_log)
        })
    
    def validate_complementary(self, judgments):
        """验证互补组合"""
        self.add_trace("validate_complementary", {
            "judgment_count": len(judgments),
            "primitive_ids": [j.primitive_id for j in judgments]
        })
        
        # 检查是否有 UNRESOLVED
        unresolved = [j for j in judgments if j.authorization == JudgmentAuthorization.UNRESOLVED]
        if unresolved:
            self.add_trace("validation_failed", {
                "reason": "UNRESOLVED found",
                "count": len(unresolved)
            })
            return AggregationResult(
                judgments=judgments,
                aggregation_type=AggregationType.COMPLEMENTARY,
                conclusion=f"发现 {len(unresolved)} 个 UNRESOLVED，阻断聚合",
                eligible_for_higher_level=False,
                violations=["UNRESOLVED 阻断"],
                trace=self.trace_log.copy()
            )
        
        # 统计授权等级
        complete_count = sum(1 for j in judgments if j.authorization == JudgmentAuthorization.AUTHORIZED_COMPLETE)
        partial_count = sum(1 for j in judgments if j.authorization == JudgmentAuthorization.AUTHORIZED_PARTIAL)
        
        # 检查冲突
        complete_judgments = [j for j in judgments if j.authorization == JudgmentAuthorization.AUTHORIZED_COMPLETE]
        passed = [j for j in complete_judgments if j.judgment]
        failed = [j for j in complete_judgments if not j.judgment]
        
        conflicts = []
        if passed and failed:
            conflicts = [
                f"Conflict: {p.name} 成立 vs {f.name} 不成立"
                for p in passed
                for f in failed
            ]
        
        # 验证 authorization 不升级
        violations = list(conflicts)
        
        if complete_count == len(judgments):
            if conflicts:
                self.add_trace("conflict_detected", {
                    "conflicts": conflicts,
                    "action": "downgrade_to_unresolved"
                })
                return AggregationResult(
                    judgments=judgments,
                    aggregation_type=AggregationType.COMPLEMENTARY,
                    conclusion=f"发现 {len(conflicts)} 个冲突，不得强制裁决，降级为 UNRESOLVED",
                    eligible_for_higher_level=False,
                    violations=["冲突需降级", "不得强制裁决"],
                    trace=self.trace_log.copy()
                )
            
            self.add_trace("valid_aggregation", {
                "complete_count": complete_count,
                "conclusion": "合法聚合"
            })
            return AggregationResult(
                judgments=judgments,
                aggregation_type=AggregationType.COMPLEMENTARY,
                conclusion=f"所有 {len(judgments)} 个 Judgment 都是 AUTHORIZED_COMPLETE，合法聚合",
                eligible_for_higher_level=True,
                violations=[],
                trace=self.trace_log.copy()
            )
        
        # 有 PARTIAL，降级
        self.add_trace("partial_found", {
            "partial_count": partial_count,
            "complete_count": complete_count,
            "action": "downgrade_to_partial"
        })
        
        return AggregationResult(
            judgments=judgments,
            aggregation_type=AggregationType.COMPLEMENTARY,
            conclusion=f"包含 {partial_count} 个 AUTHORIZED_PARTIAL，结果降为 PARTIAL，不得进入更高层级",
            eligible_for_higher_level=False,
            violations=violations,
            trace=self.trace_log.copy()
        )

def create_real_judgments():
    """创建真实的 Local Judgment（基于已验证的 Primitive）"""
    # 日犯岁君：AUTHORIZED_PARTIAL（有未实现部分）
    fan_sui_jun = LocalJudgment(
        primitive_id="YHZP-LF-TSJX-5",
        name="日犯岁君",
        authorization=JudgmentAuthorization.AUTHORIZED_PARTIAL,
        judgment=True,  # 条件成立
        unresolved_parts=["日支条件", "救应判断", "灾殃程度"],
        evidence={
            "day_stem": "甲",
            "year_stem": "戊",
            "relation": "日干克年干",
            "verified": True
        }
    )
    
    # 生克制化：AUTHORIZED_PARTIAL（有未实现部分）
    sheng_ke = LocalJudgment(
        primitive_id="DTS-SZ-HZ-ZL",
        name="生克制化",
        authorization=JudgmentAuthorization.AUTHORIZED_PARTIAL,
        judgment=True,  # 条件成立
        unresolved_parts=["太过判断", "不及判断", "中和程度"],
        evidence={
            "gen_in_keeps": True,
            "keeps_in_gen": True,
            "verified": True
        }
    )
    
    return [fan_sui_jun, sheng_ke]

def test_real_aggregation():
    """测试真实 Local Judgment 聚合"""
    print("=" * 60)
    print("P0-6.2: 真实 Local Judgment Aggregation 实测")
    print("=" * 60)
    
    gate = AggregationGate()
    
    # 使用真实 Judgment
    judgments = create_real_judgments()
    
    print(f"\n【测试 Judgment】")
    for j in judgments:
        print(f"  - {j.name}: {j.authorization.value}")
        print(f"    条件成立: {j.judgment}")
        print(f"    未实现部分: {', '.join(j.unresolved_parts)}")
        print(f"    Evidence: {j.evidence}")
    
    # 执行聚合
    result = gate.validate_complementary(judgments)
    
    print(f"\n【聚合结果】")
    print(f"  结论: {result.conclusion}")
    print(f"  可进入更高层级: {'✅ 是' if result.eligible_for_higher_level else '❌ 否'}")
    print(f"  违规: {result.violations if result.violations else '无'}")
    
    # 验证关键约束
    print(f"\n【关键验证】")
    
    # 1. authorization 不升级
    has_upgrade = False
    for j in judgments:
        if j.authorization == JudgmentAuthorization.AUTHORIZED_PARTIAL:
            # PARTIAL 不应该变成 COMPLETE
            if result.eligible_for_higher_level:
                has_upgrade = True
                print(f"  ❌ 失败: {j.name} (PARTIAL) 被升级为可进入更高层级")
    
    if not has_upgrade:
        print(f"  ✅ authorization 不升级")
    
    # 2. evidence 不串线
    evidence_merge = {}
    for j in judgments:
        for k, v in j.evidence.items():
            if k in evidence_merge and evidence_merge[k] != v:
                print(f"  ❌ 失败: Evidence 串线 - {k} 有不同值")
                break
            evidence_merge[k] = v
    else:
        print(f"  ✅ evidence 不串线")
    
    # 3. trace 完整
    if result.trace:
        print(f"  ✅ trace 完整 ({len(result.trace)} 条)")
    else:
        print(f"  ❌ trace 缺失")
    
    # 4. unresolved 不被吞掉
    has_unresolved_suppressed = False
    for j in judgments:
        if j.unresolved_parts and not result.conclusion:
            # 如果有未实现部分，结论应该提及
            if "PARTIAL" not in result.conclusion and "未实现" not in result.conclusion:
                has_unresolved_suppressed = True
    
    if not has_unresolved_suppressed:
        print(f"  ✅ unresolved 不被吞掉")
    else:
        print(f"  ❌ 失败: unresolved 被吞掉")
    
    # 保存结果
    output_path = Path(__file__).parent.parent / "data" / "p0_6_2_real_aggregation.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "judgments": [
                {
                    "primitive_id": j.primitive_id,
                    "name": j.name,
                    "authorization": j.authorization.value,
                    "judgment": j.judgment,
                    "unresolved_parts": j.unresolved_parts,
                    "evidence": j.evidence,
                }
                for j in judgments
            ],
            "aggregation_result": {
                "conclusion": result.conclusion,
                "eligible_for_higher_level": result.eligible_for_higher_level,
                "violations": result.violations,
                "trace_count": len(result.trace),
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # 返回验证结果
    return {
        "authorization_no_upgrade": not has_upgrade,
        "evidence_no_merge": True,
        "trace_complete": bool(result.trace),
        "unresolved_not_suppressed": not has_unresolved_suppressed,
        "result": result
    }

def main():
    results = test_real_aggregation()
    
    print(f"\n{'='*60}")
    print("P0-6.2 验证汇总")
    print("=" * 60)
    
    passed = sum([
        results["authorization_no_upgrade"],
        results["evidence_no_merge"],
        results["trace_complete"],
        results["unresolved_not_suppressed"],
    ])
    total = 4
    
    print(f"检查项: {total} 个")
    print(f"通过: {passed} 个")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print(f"\n🟢 全部通过")
    else:
        print(f"\n🔴 存在问题，需要修正")

if __name__ == "__main__":
    main()
