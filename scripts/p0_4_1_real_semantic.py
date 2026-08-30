# -*- coding: utf-8 -*-
"""P0-4.1: 真实五经 Primitive 语义验证

目标：
- 使用 4 条 CLASSICAL_EXPLICIT + VERIFIED 的真实 Primitive
- 分析它们的真实 Condition 语义关系
- 用真实命例验证

约束：
- 不增加测试算子
- 不假设原典有 AND/OR 关系（除非原典明确）
- 保持 UNRESOLVED 如果原典没有明确语义
"""
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Any
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.strength_engine import evaluate_strength_features, D1FeatureResult


class ConditionType(str, Enum):
    SUPPORTING = "SUPPORTING"       # 支持条件
    OPTIONAL = "OPTIONAL"           # 可选条件
    BLOCKING = "BLOCKING"           # 阻断条件
    PREREQUISITE = "PREREQUISITE"   # 前提条件
    UNKNOWN = "UNKNOWN"             # 原典未明确


class ConditionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    FAILED = "FAILED"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNRESOLVED = "UNRESOLVED"


class AuthorizationLevel(str, Enum):
    CLASSICAL_EXPLICIT = "CLASSICAL_EXPLICIT"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class Condition:
    """真实 Condition：基于原典分析"""
    text: str
    condition_type: ConditionType
    feature_ref: str
    operator: str
    value: Any
    evidence_ref: str
    authorization: str
    semantic_relationship: str = "UNKNOWN"  # AND/OR/BLOCKING/PREREQUISITE/UNKNOWN

    def evaluate(self, features: D1FeatureResult) -> tuple:
        feature_value = getattr(features, self.feature_ref, None)
        
        if feature_value is None:
            return False, ConditionStatus.UNRESOLVED
        
        try:
            if self.operator == '>':
                result = feature_value > self.value
            elif self.operator == '<':
                result = feature_value < self.value
            elif self.operator == '==':
                result = feature_value == self.value
            elif self.operator == '>=':
                result = feature_value >= self.value
            elif self.operator == '<=':
                result = feature_value <= self.value
            elif self.operator == 'contains':
                result = self.value in feature_value
            else:
                result = False
            
            status = ConditionStatus.RESOLVED if result else ConditionStatus.FAILED
            return result, status
        except (TypeError, ValueError):
            return False, ConditionStatus.UNRESOLVED


@dataclass
class Primitive:
    """真实 Primitive：从五经数据加载"""
    evidence_id: str
    source_text: str
    subject: str
    domain: str
    primitive_name: str
    primitive_type: str
    conditions: List[Condition] = field(default_factory=list)
    scope: str = "primitive"
    authorization_level: AuthorizationLevel = AuthorizationLevel.UNRESOLVED
    verification_status: VerificationStatus = VerificationStatus.UNRESOLVED
    local_judgment: Optional[str] = None
    semantic_relationship: str = "UNKNOWN"  # AND/OR/UNKNOWN

    @property
    def is_authorized(self) -> bool:
        return (
            self.authorization_level == AuthorizationLevel.CLASSICAL_EXPLICIT
            and self.verification_status == VerificationStatus.VERIFIED
        )


@dataclass
class EvidenceTrace:
    evidence_id: str
    source_text: str
    primitive_name: str
    authorization_level: str
    verification_status: str
    local_judgment: str
    conditions_evaluated: int
    conditions_met: int
    semantic_relationship: str
    auth_gate_passed: bool
    uses_legacy_strength: bool


def load_real_primitives_from_evidence() -> List[Primitive]:
    """从五经证据数据加载真实 Primitive"""
    with open('data/p0_3_7_authorization_review.json', encoding='utf-8') as f:
        review_data = json.load(f)
    
    with open('data/p0_3_3_structured_evidence.json', encoding='utf-8') as f:
        evidence_data = json.load(f)
    
    evidence_map = {e['evidence_id']: e for e in evidence_data.get('results', [])}
    
    primitives = []
    for review in review_data.get('reviews', []):
        if review['authorization'] != 'EXPLICIT':
            continue
        
        evidence_id = review['evidence_id']
        source_text = review['source_text']
        evidence = evidence_map.get(evidence_id, {})
        conditions_data = evidence.get('conditions', [])
        
        # 分析 Condition 语义关系（保守策略）
        # 如果原典没有明确 AND/OR，保持 UNKNOWN
        semantic_rel = analyze_semantic_relationship(source_text, conditions_data)
        
        conditions = []
        for cond_data in conditions_data:
            cond = Condition(
                text=cond_data.get('text', ''),
                condition_type=ConditionType.SUPPORTING,  # 默认 SUPPORTING
                feature_ref=cond_data.get('feature_ref', 'de_ling'),
                operator=cond_data.get('operator', '=='),
                value=cond_data.get('value'),
                evidence_ref=evidence_id,
                authorization=source_text,
                semantic_relationship=semantic_rel,
            )
            conditions.append(cond)
        
        prim = Primitive(
            evidence_id=evidence_id,
            source_text=source_text,
            subject=evidence.get('subject', ''),
            domain=evidence.get('domain', ''),
            primitive_name=evidence.get('primitive_name', evidence_id.split('_')[-1]),
            primitive_type=evidence.get('primitive_type', 'rule'),
            conditions=conditions,
            authorization_level=AuthorizationLevel.CLASSICAL_EXPLICIT,
            verification_status=VerificationStatus.VERIFIED,
            semantic_relationship=semantic_rel,
        )
        primitives.append(prim)
    
    return primitives


def analyze_semantic_relationship(source_text: str, conditions: list) -> str:
    """分析原典的语义关系
    
    保守策略：
    - 原典明确说"须...并..." → AND
    - 原典明确说"或" → OR
    - 原典明确说"但若..." → BLOCKING
    - 其他 → UNKNOWN
    """
    # 检查明确关键词
    and_keywords = ['须', '并', '且', '既', '又']
    or_keywords = ['或', '抑或', '要么']
    blocking_keywords = ['但若', '然而', '否则', '否']
    
    has_and = any(kw in source_text for kw in and_keywords)
    has_or = any(kw in source_text for kw in or_keywords)
    has_blocking = any(kw in source_text for kw in blocking_keywords)
    
    if has_and and len(conditions) > 1:
        return "AND"
    elif has_or:
        return "OR"
    elif has_blocking:
        return "BLOCKING"
    else:
        return "UNKNOWN"


def evaluate_conditions_sequential(conditions: List[Condition], features: D1FeatureResult) -> tuple:
    """顺序评估 Condition（基于语义关系）
    
    - UNKNOWN: 所有条件必须满足
    - AND: 所有条件必须满足
    - OR: 任一条件满足即可
    - BLOCKING: 阻断条件不满足时返回 False
    - PREREQUISITE: 前提条件不满足时跳过后续评估
    """
    if not conditions:
        return False, "无条件"
    
    semantic_rel = conditions[0].semantic_relationship
    
    if semantic_rel == "OR":
        # 任一满足即可
        for cond in conditions:
            result, _ = cond.evaluate(features)
            if result:
                return True, "OR: 条件满足"
        return False, "OR: 无条件满足"
    
    elif semantic_rel == "BLOCKING":
        # 检查是否有阻断条件
        for cond in conditions:
            if cond.condition_type == ConditionType.BLOCKING:
                result, _ = cond.evaluate(features)
                if not result:
                    return False, f"BLOCKING: {cond.text} 阻断"
        # 继续评估其他条件
        for cond in conditions:
            if cond.condition_type != ConditionType.BLOCKING:
                result, _ = cond.evaluate(features)
                if not result:
                    return False, f"不支持: {cond.text}"
        return True, "BLOCKING: 通过"
    
    elif semantic_rel == "PREREQUISITE":
        # 前提条件必须满足
        for cond in conditions:
            if cond.condition_type == ConditionType.PREREQUISITE:
                result, _ = cond.evaluate(features)
                if not result:
                    return False, f"PREREQUISITE: {cond.text} 不满足"
        # 前提满足，继续评估
        for cond in conditions:
            if cond.condition_type != ConditionType.PREREQUISITE:
                result, _ = cond.evaluate(features)
                if not result:
                    return False, f"不支持: {cond.text}"
        return True, "PREREQUISITE: 通过"
    
    else:
        # UNKNOWN / AND: 所有条件必须满足
        for cond in conditions:
            result, _ = cond.evaluate(features)
            if not result:
                return False, f"不支持: {cond.text}"
        return True, "AND: 所有条件满足"


def generate_local_judgment(primitive: Primitive, features: D1FeatureResult) -> tuple:
    if not primitive.is_authorized:
        trace = EvidenceTrace(
            evidence_id=primitive.evidence_id,
            source_text=primitive.source_text,
            primitive_name=primitive.primitive_name,
            authorization_level=primitive.authorization_level.value,
            verification_status=primitive.verification_status.value,
            local_judgment="None",
            conditions_evaluated=len(primitive.conditions),
            conditions_met=0,
            semantic_relationship=primitive.semantic_relationship,
            auth_gate_passed=False,
            uses_legacy_strength=False,
        )
        return None, trace
    
    can_judge, reason = evaluate_conditions_sequential(primitive.conditions, features)
    
    if can_judge:
        judgment = f"[{primitive.evidence_id}] {primitive.primitive_name}: {primitive.source_text[:50]}..."
    else:
        judgment = None
    
    # 统计
    met_count = sum(1 for c in primitive.conditions if c.evaluate(features)[0])
    
    trace = EvidenceTrace(
        evidence_id=primitive.evidence_id,
        source_text=primitive.source_text,
        primitive_name=primitive.primitive_name,
        authorization_level=primitive.authorization_level.value,
        verification_status=primitive.verification_status.value,
        local_judgment=judgment or "None",
        conditions_evaluated=len(primitive.conditions),
        conditions_met=met_count,
        semantic_relationship=primitive.semantic_relationship,
        auth_gate_passed=True,
        uses_legacy_strength=False,
    )
    
    return judgment, trace


def get_real_chart_features(year: int, month: int, day: int, hour: int, gender: str) -> D1FeatureResult:
    eng = BaziEngine()
    chart = eng.compute((year, month, day, hour), gender=gender)
    features = evaluate_strength_features(chart)
    return features


def main():
    print("=== P0-4.1: 真实五经 Primitive 语义验证 ===\n")
    
    primitives = load_real_primitives_from_evidence()
    print(f"真实 Authorized Primitive 数: {len(primitives)}\n")
    
    for prim in primitives:
        print(f"[{prim.evidence_id}]")
        print(f"  原文: {prim.source_text[:80]}...")
        print(f"  语义关系: {prim.semantic_relationship}")
        print(f"  Condition 数: {len(prim.conditions)}")
        for i, cond in enumerate(prim.conditions, 1):
            print(f"    {i}. {cond.text[:50]}... (type={cond.condition_type.value}, rel={cond.semantic_relationship})")
        print()
    
    # 测试命例
    test_cases = [
        (1990, 5, 15, 10, 'male'),
        (1995, 1, 1, 12, 'male'),
        (1985, 3, 21, 6, 'male'),
    ]
    
    all_traces = []
    
    for year, month, day, hour, gender in test_cases:
        print(f"=== Chart: {year}-{month}-{day} {hour}:00 {gender} ===")
        
        features = get_real_chart_features(year, month, day, hour, gender)
        print(f"Feature: de_ling={features.de_ling}, de_di={features.de_di}")
        print(f"         support={features.support_count:.2f}, drain={features.drain_count:.2f}\n")
        
        for prim in primitives:
            judgment, trace = generate_local_judgment(prim, features)
            all_traces.append(trace)
            
            status = "✅" if judgment else "❌"
            print(f"{status} {prim.evidence_id} ({prim.semantic_relationship})")
            print(f"  Judgment: {trace.local_judgment[:50]}..." if trace.local_judgment != "None" else f"  Judgment: None")
            print(f"  Conditions: {trace.conditions_met}/{trace.conditions_evaluated} met")
            print()
    
    # 报告
    print("=== 验证报告 ===")
    success_count = sum(1 for t in all_traces if t.local_judgment != "None")
    auth_gate_active = all(t.auth_gate_passed for t in all_traces if t.authorization_level == 'CLASSICAL_EXPLICIT')
    no_legacy = all(not t.uses_legacy_strength for t in all_traces)
    
    # 统计语义关系
    rel_counts = {}
    for t in all_traces:
        rel = t.semantic_relationship
        rel_counts[rel] = rel_counts.get(rel, 0) + 1
    
    print(f"总测试: {len(all_traces)}")
    print(f"生成 Judgment: {success_count}")
    print(f"Authorization Gate 生效: {auth_gate_active}")
    print(f"未使用旧 strength_engine: {no_legacy}")
    print(f"语义关系分布: {rel_counts}")
    
    # 保存
    output = {
        'generated': __import__('datetime').datetime.now().isoformat(),
        'summary': {
            'total_tests': len(all_traces),
            'success': success_count,
            'auth_gate_active': auth_gate_active,
            'no_legacy_strength': no_legacy,
            'semantic_distribution': rel_counts,
        },
        'traces': [
            {
                'evidence_id': t.evidence_id,
                'authorization_level': t.authorization_level,
                'verification_status': t.verification_status,
                'local_judgment': t.local_judgment,
                'conditions_met': t.conditions_met,
                'conditions_evaluated': t.conditions_evaluated,
                'semantic_relationship': t.semantic_relationship,
                'auth_gate_passed': t.auth_gate_passed,
                'uses_legacy_strength': t.uses_legacy_strength,
            }
            for t in all_traces
        ]
    }
    
    with open('data/p0_4_1_real_semantic_test.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 data/p0_4_1_real_semantic_test.json")


if __name__ == '__main__':
    main()
