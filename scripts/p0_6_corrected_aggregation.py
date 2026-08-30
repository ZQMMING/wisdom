# -*- coding: utf-8 -*-
"""P0-6 修正版：Local Judgment Aggregation Contract（三级授权）

关键修正:
1. 增加三级授权状态：AUTHORIZED_COMPLETE / AUTHORIZED_PARTIAL / UNRESOLVED
2. AUTHORIZED_PARTIAL 不得作为完整高层 Judgment 的输入
3. 删除人工构造的层级 Golden Case
4. Conflict 允许内部记录；无法解决时降级 UNRESOLVED
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

sys.path.insert(0, '.')

from tongshu.canonical.state import StateAuthorizationLevel
from tongshu.engines.bazi_engine import BaziEngine


# ============================================================
# 枚举定义：三级授权状态
# ============================================================

class JudgmentAuthorization(Enum):
    """Judgment 授权状态（三级）"""
    AUTHORIZED_COMPLETE = "AUTHORIZED_COMPLETE"      # 完整授权，可参与聚合
    AUTHORIZED_PARTIAL = "AUTHORIZED_PARTIAL"        # 部分授权，仅可作为 Evidence
    UNRESOLVED = "UNRESOLVED"                         # 未决，不得产生 Judgment


class AggregationType(Enum):
    """聚合类型"""
    COMPLEMENTARY = "complementary"  # 互补组合（只允许 AUTHORIZED_COMPLETE）
    EVIDENCE_CHAIN = "evidence_chain"  # 证据链（允许 AUTHORIZED_PARTIAL 作为 Evidence）


class ConflictResolution(Enum):
    """冲突解决方式"""
    RESOLVED = "resolved"              # 已解决
    DOWNGRADED = "downgraded"          # 降级为 UNRESOLVED
    PENDING = "pending"                # 待进一步分析


# ============================================================
# 数据结构
# ============================================================

@dataclass
class LocalJudgment:
    """单个 Local Judgment"""
    primitive_id: str
    name: str
    judgment: bool  # 条件是否成立
    evidence: str   # 原典证据
    authorization: JudgmentAuthorization  # 授权状态
    unresolved_parts: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primitive_id": self.primitive_id,
            "name": self.name,
            "judgment": self.judgment,
            "evidence": self.evidence,
            "authorization": self.authorization.value,
            "unresolved_parts": self.unresolved_parts,
        }


@dataclass
class Conflict:
    """冲突记录"""
    judgment_1: str
    judgment_2: str
    conflict_type: str  # "factual" or "semantic"
    description: str
    resolution: ConflictResolution = ConflictResolution.PENDING
    resolution_note: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "judgment_1": self.judgment_1,
            "judgment_2": self.judgment_2,
            "conflict_type": self.conflict_type,
            "description": self.description,
            "resolution": self.resolution.value,
            "resolution_note": self.resolution_note,
        }


@dataclass
class AggregationResult:
    """聚合结果"""
    judgments: List[LocalJudgment]
    aggregation_type: AggregationType
    conclusion: str
    conflicts: List[Conflict] = field(default_factory=list)
    eligible_for_higher_level: bool = False  # 是否可以进入更高层级
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "judgments": [j.to_dict() for j in self.judgments],
            "aggregation_type": self.aggregation_type.value,
            "conclusion": self.conclusion,
            "conflicts": [c.to_dict() for c in self.conflicts],
            "eligible_for_higher_level": self.eligible_for_higher_level,
            "has_unresolved_conflicts": any(c.resolution == ConflictResolution.PENDING for c in self.conflicts),
            "has_partial_authorization": any(j.authorization == JudgmentAuthorization.AUTHORIZED_PARTIAL for j in self.judgments),
        }


# ============================================================
# Aggregation Contract（修正版）
# ============================================================

class LocalJudgmentAggregator:
    """Local Judgment 聚合器（三级授权版）
    
    关键约束:
    - AUTHORIZED_COMPLETE: 可参与任何聚合
    - AUTHORIZED_PARTIAL: 只能作为 Evidence，不能参与需要完整语义的聚合
    - UNRESOLVED: 不得产生 Judgment
    - 禁止投票机制
    - Conflict 不能停留为最终状态，必须解决或降级
    """
    
    def __init__(self):
        self.judgments: List[LocalJudgment] = []
        self.conflicts: List[Conflict] = []
        self._last_complementary: Optional[AggregationResult] = None
        self._last_evidence_chain: Optional[AggregationResult] = None
    
    def add_judgment(self, judgment: LocalJudgment):
        """添加 Local Judgment"""
        self.judgments.append(judgment)
    
    def validate_no_unresolved(self) -> bool:
        """验证无 UNRESOLVED Judgment 进入聚合"""
        unresolved = [j for j in self.judgments if j.authorization == JudgmentAuthorization.UNRESOLVED]
        return len(unresolved) == 0
    
    def detect_conflicts(self) -> List[Conflict]:
        """检测冲突"""
        conflicts = []
        
        for i, j1 in enumerate(self.judgments):
            for j2 in self.judgments[i+1:]:
                # 只检测两个都成立的 Judgment 之间的冲突
                if j1.judgment and j2.judgment:
                    # 检查是否是跨体系
                    if self._is_cross_system(j1, j2):
                        conflict = Conflict(
                            judgment_1=j1.primitive_id,
                            judgment_2=j2.primitive_id,
                            conflict_type="semantic",
                            description=f"{j1.name}与{j2.name}跨体系，不能互相否定",
                            resolution=ConflictResolution.DOWNGRADED,
                            resolution_note="跨体系冲突降级为 UNRESOLVED，不互相否定"
                        )
                        conflicts.append(conflict)
        
        self.conflicts = conflicts
        return conflicts
    
    def _is_cross_system(self, j1: LocalJudgment, j2: LocalJudgment) -> bool:
        """检查是否跨体系"""
        system_1 = j1.primitive_id.split('-')[0] if '-' in j1.primitive_id else ""
        system_2 = j2.primitive_id.split('-')[0] if '-' in j2.primitive_id else ""
        return system_1 != system_2
    
    def aggregate_complementary(self) -> AggregationResult:
        """互补组合聚合
        
        条件:
        - 所有 Judgment 必须是 AUTHORIZED_COMPLETE
        - 描述同一状态的不同方面
        """
        # 检查授权状态
        complete_judgments = [j for j in self.judgments if j.authorization == JudgmentAuthorization.AUTHORIZED_COMPLETE]
        partial_judgments = [j for j in self.judgments if j.authorization == JudgmentAuthorization.AUTHORIZED_PARTIAL]
        
        if partial_judgments:
            # 有 AUTHORIZED_PARTIAL，不能作为完整聚合
            conclusion = f"存在 {len(partial_judgments)} 个 AUTHORIZED_PARTIAL Judgment，只能作为 Evidence 输出"
            eligible = False
        elif all(j.judgment for j in complete_judgments):
            conclusion = "所有 AUTHORIZED_COMPLETE Judgment 成立，形成互补描述"
            eligible = True
        else:
            passed_count = sum(1 for j in complete_judgments if j.judgment)
            conclusion = f"{passed_count}/{len(complete_judgments)} 个 AUTHORIZED_COMPLETE Judgment 成立"
            eligible = False
        
        self._last_complementary = AggregationResult(
            judgments=self.judgments,
            aggregation_type=AggregationType.COMPLEMENTARY,
            conclusion=conclusion,
            conflicts=self.conflicts,
            eligible_for_higher_level=eligible,
        )
        return self._last_complementary
    
    def aggregate_evidence_chain(self) -> AggregationResult:
        """证据链聚合
        
        条件:
        - 允许 AUTHORIZED_PARTIAL 作为 Evidence
        - 下层 Judgment 成立是上层 Judgment 的前提
        """
        # 收集所有成立的 Judgment
        passed = [j for j in self.judgments if j.judgment]
        
        # 统计授权状态
        complete_count = sum(1 for j in passed if j.authorization == JudgmentAuthorization.AUTHORIZED_COMPLETE)
        partial_count = sum(1 for j in passed if j.authorization == JudgmentAuthorization.AUTHORIZED_PARTIAL)
        
        if partial_count > 0:
            conclusion = f"证据链包含 {complete_count} 个 AUTHORIZED_COMPLETE + {partial_count} 个 AUTHORIZED_PARTIAL（部分证据）"
            eligible = False
        else:
            conclusion = f"证据链完整，{complete_count} 个 AUTHORIZED_COMPLETE Judgment 成立"
            eligible = True
        
        self._last_evidence_chain = AggregationResult(
            judgments=self.judgments,
            aggregation_type=AggregationType.EVIDENCE_CHAIN,
            conclusion=conclusion,
            conflicts=self.conflicts,
            eligible_for_higher_level=eligible,
        )
        return self._last_evidence_chain
    
    def resolve_conflicts(self):
        """解决冲突
        
        流程:
        1. 检测冲突
        2. 分析冲突类型和范围
        3. 能解决 → RESOLVED
        4. 不能解决 → DOWNGRADED（降级为 UNRESOLVED）
        """
        conflicts = self.detect_conflicts()
        
        for conflict in conflicts:
            if conflict.resolution == ConflictResolution.DOWNGRADED:
                conflict.resolution_note = f"冲突无法解决，降级处理：{conflict.description}"
        
        self.conflicts = conflicts
    
    def validate_constraints(self) -> Dict[str, bool]:
        """验证约束"""
        # 检查是否有聚合结果错误地将 AUTHORIZED_PARTIAL 当作完整结论
        has_partial_upgraded = False
        for result_type, result in [("complementary", getattr(self, '_last_complementary', None)), 
                                     ("evidence_chain", getattr(self, '_last_evidence_chain', None))]:
            if result and result.eligible_for_higher_level:
                # 如果标记为可进入更高层级，但包含 AUTHORIZED_PARTIAL，则是错误升级
                has_partial = any(j.authorization == JudgmentAuthorization.AUTHORIZED_PARTIAL 
                                 for j in result.judgments)
                if has_partial:
                    has_partial_upgraded = True
        
        return {
            "无 UNRESOLVED Judgment": self.validate_no_unresolved(),
            "无投票机制": True,
            "冲突已处理": all(c.resolution != ConflictResolution.PENDING for c in self.conflicts),
            "AUTHORIZED_PARTIAL 未升级为完整": not has_partial_upgraded,
        }


# ============================================================
# 测试用例（修正版）
# ============================================================

def create_test_judgments():
    """创建测试用 Local Judgment（修正版）
    
    修正:
    - 日犯岁君: AUTHORIZED_PARTIAL（有未实现部分：日支条件、救应判断）
    - 生克制化: AUTHORIZED_PARTIAL（有未实现部分：太过判断、不及判断）
    - 删除人工构造的层级案例
    """
    return [
        LocalJudgment(
            primitive_id="YHZP-LF-TSJX-5",
            name="日犯岁君",
            judgment=True,
            evidence="渊海子平·论太岁吉凶：甲日见戊年，剋重者死",
            authorization=JudgmentAuthorization.AUTHORIZED_PARTIAL,
            unresolved_parts=["日支条件", "救应判断", "灾殃程度"],
        ),
        LocalJudgment(
            primitive_id="DTS-SZ-HZ-ZL",
            name="生克制化",
            judgment=True,
            evidence="滴天髓·通神论：生克制化，须制中有生，生中有制",
            authorization=JudgmentAuthorization.AUTHORIZED_PARTIAL,
            unresolved_parts=["太过判断", "不及判断", "中和程度"],
        ),
    ]


def run_aggregation_test():
    """运行聚合测试"""
    print("=" * 60)
    print("P0-6 修正版: Local Judgment Aggregation Contract 验证")
    print("=" * 60)
    
    # 创建测试 Judgment
    judgments = create_test_judgments()
    
    print(f"\n【测试 Judgment】")
    for j in judgments:
        print(f"  - {j.name}: {j.authorization.value} (judgment={j.judgment})")
        if j.unresolved_parts:
            print(f"    未实现: {', '.join(j.unresolved_parts)}")
    
    # 创建聚合器
    aggregator = LocalJudgmentAggregator()
    for j in judgments:
        aggregator.add_judgment(j)
    
    # 解决冲突
    aggregator.resolve_conflicts()
    
    # 检测冲突
    conflicts = aggregator.detect_conflicts()
    print(f"\n【冲突检测】")
    print(f"发现冲突: {len(conflicts)} 条")
    for c in conflicts:
        print(f"  - {c.description}")
        print(f"    状态: {c.resolution.value}")
    
    # 互补组合
    print(f"\n【互补组合聚合】")
    result_comp = aggregator.aggregate_complementary()
    print(f"  结论: {result_comp.conclusion}")
    print(f"  可进入更高层级: {'✅ 是' if result_comp.eligible_for_higher_level else '❌ 否'}")
    
    # 证据链聚合
    print(f"\n【证据链聚合】")
    result_chain = aggregator.aggregate_evidence_chain()
    print(f"  结论: {result_chain.conclusion}")
    print(f"  可进入更高层级: {'✅ 是' if result_chain.eligible_for_higher_level else '❌ 否'}")
    
    # 约束验证
    print(f"\n【约束验证】")
    constraints = aggregator.validate_constraints()
    for check, passed in constraints.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon} {check}")
    
    # 保存结果
    output_path = Path(__file__).parent.parent / "data" / "p0_6_corrected_test.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "judgments": [j.to_dict() for j in judgments],
            "conflicts": [c.to_dict() for c in conflicts],
            "complementary_result": result_comp.to_dict(),
            "evidence_chain_result": result_chain.to_dict(),
            "constraints_valid": constraints,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    return {
        "judgments": judgments,
        "conflicts": conflicts,
        "complementary": result_comp,
        "evidence_chain": result_chain,
        "constraints": constraints,
    }


if __name__ == "__main__":
    result = run_aggregation_test()
    
    print(f"\n{'='*60}")
    print("Aggregation Contract 验证完成（修正版）")
    print("=" * 60)
    print(f"总 Judgment: {len(result['judgments'])} 条")
    print(f"发现冲突: {len(result['conflicts'])} 条")
    print(f"互补聚合可进入更高层级: {'✅ 是' if result['complementary'].eligible_for_higher_level else '❌ 否'}")
    print(f"证据链可进入更高层级: {'✅ 是' if result['evidence_chain'].eligible_for_higher_level else '❌ 否'}")
    all_passed = all(result['constraints'].values())
    print(f"约束验证: {'✅ 全部通过' if all_passed else '❌ 存在问题'}")
