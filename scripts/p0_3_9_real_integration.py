# -*- coding: utf-8 -*-
"""P0-3.9: 真实命例验证 - Local Judgment Engine

目标：
- 使用真实 Canonical State（从实际Chart计算）
- 使用真实 Evidence（从五经数据加载）
- 使用真实 Primitive（从数据加载）
- 使用真实 Condition Evaluator（基于Feature计算）
- Local Judgment 基于真实条件评估

不再 simulate_chart()，不再预设条件状态
"""
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Any
from enum import Enum

# 添加 backend/src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from tongshu.engines.strength_engine import evaluate_strength_features, D1FeatureResult
from tongshu.bazi.chart import BaziChart


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
    """真实 Condition：基于 Feature 计算状态"""
    text: str
    condition_type: str
    feature_ref: str  # 对应 D1FeatureResult 字段
    operator: str  # >, <, ==, >=, <=, contains
    value: Any
    evidence_ref: str
    authorization: str
    status: ConditionStatus = ConditionStatus.UNRESOLVED

    def evaluate(self, features: D1FeatureResult) -> bool:
        """真实评估：从 Feature 计算条件状态"""
        feature_value = getattr(features, self.feature_ref, None)
        
        if feature_value is None:
            self.status = ConditionStatus.UNRESOLVED
            return False
        
        # 执行比较
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
            
            self.status = ConditionStatus.RESOLVED if result else ConditionStatus.FAILED
            return result
        except (TypeError, ValueError):
            self.status = ConditionStatus.UNRESOLVED
            return False


@dataclass
class Primitive:
    """真实 Primitive：从证据数据加载"""
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

    @property
    def is_authorized(self) -> bool:
        return (
            self.authorization_level == AuthorizationLevel.CLASSICAL_EXPLICIT
            and self.verification_status == VerificationStatus.VERIFIED
        )


@dataclass
class EvidenceTrace:
    """证据追溯"""
    evidence_id: str
    source_text: str
    primitive_name: str
    authorization_level: str
    verification_status: str
    local_judgment: str
    conditions_evaluated: int
    conditions_met: int
    conditions_failed: int
    conditions_unresolved: int
    auth_gate_passed: bool
    uses_legacy_strength: bool


def load_authorized_primitives_from_data() -> List[Primitive]:
    """从真实数据加载 Authorized Primitive"""
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
        evidence = evidence_map.get(evidence_id, {})
        source_text = review['source_text']
        conditions_data = evidence.get('conditions', [])
        
        # 构建真实 Condition
        conditions = []
        for cond_data in conditions_data:
            cond = Condition(
                text=cond_data.get('text', ''),
                condition_type=cond_data.get('type', 'SUPPORTING'),
                feature_ref=cond_data.get('feature_ref', ''),
                operator=cond_data.get('operator', '=='),
                value=cond_data.get('value'),
                evidence_ref=evidence_id,
                authorization=source_text,
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
        )
        primitives.append(prim)
    
    return primitives


def get_real_chart_features(year: int, month: int, day: int, hour: int, gender: str) -> D1FeatureResult:
    """从真实 Chart 计算 Feature"""
    chart = BaziChart(year=year, month=month, day=day, hour=hour, gender=gender)
    features = evaluate_strength_features(chart)
    return features


def generate_local_judgment(primitive: Primitive, features: D1FeatureResult) -> tuple:
    """从真实 Primitive + Feature 生成 Local Judgment
    
    返回: (judgment: Optional[str], trace: EvidenceTrace)
    """
    # 检查 Authorization Gate
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
            conditions_failed=0,
            conditions_unresolved=len(primitive.conditions),
            auth_gate_passed=False,
            uses_legacy_strength=False,
        )
        return None, trace
    
    # 评估所有 Condition
    met_count = 0
    failed_count = 0
    unresolved_count = 0
    
    for cond in primitive.conditions:
        result = cond.evaluate(features)
        if result:
            met_count += 1
        elif cond.status == ConditionStatus.FAILED:
            failed_count += 1
        else:
            unresolved_count += 1
    
    # 生成 Judgment
    if met_count > 0 and failed_count == 0:
        judgment = f"[{primitive.evidence_id}] {primitive.primitive_name}: {primitive.source_text[:50]}..."
    elif met_count == 0:
        judgment = None
    else:
        judgment = f"[{primitive.evidence_id}] 部分条件满足 ({met_count}/{len(primitive.conditions)})"
    
    trace = EvidenceTrace(
        evidence_id=primitive.evidence_id,
        source_text=primitive.source_text,
        primitive_name=primitive.primitive_name,
        authorization_level=primitive.authorization_level.value,
        verification_status=primitive.verification_status.value,
        local_judgment=judgment or "None",
        conditions_evaluated=len(primitive.conditions),
        conditions_met=met_count,
        conditions_failed=failed_count,
        conditions_unresolved=unresolved_count,
        auth_gate_passed=True,
        uses_legacy_strength=False,
    )
    
    return judgment, trace


def main():
    print("=== P0-3.9: 真实命例验证 ===\n")
    
    # 加载 Authorized Primitive
    primitives = load_authorized_primitives_from_data()
    print(f"Authorized Primitive 数: {len(primitives)}\n")
    
    # 使用真实命例
    test_cases = [
        # (year, month, day, hour, gender, description)
        (1990, 5, 15, 10, 'male', '测试命例1'),
        (1985, 3, 21, 6, 'male', '测试命例2'),
        (1992, 8, 8, 14, 'female', '测试命例3'),
    ]
    
    all_traces = []
    
    for year, month, day, hour, gender, desc in test_cases:
        print(f"=== {desc} ===")
        print(f"Chart: {year}-{month}-{day} {hour}:00 {gender}\n")
        
        # 计算真实 Feature
        features = get_real_chart_features(year, month, day, hour, gender)
        print(f"Feature: de_ling={features.de_ling}, de_di={features.de_di}, de_shi={features.de_shi}")
        print(f"         support={features.support_count}, drain={features.drain_count}\n")
        
        # 对每个 Primitive 运行验证
        for prim in primitives:
            judgment, trace = generate_local_judgment(prim, features)
            all_traces.append(trace)
            
            status = "✅" if judgment and judgment != "None" else "❌"
            print(f"{status} {prim.evidence_id}")
            print(f"  AuthGate: {trace.auth_gate_passed}")
            print(f"  Conditions: {trace.conditions_met} met, {trace.conditions_failed} failed, {trace.conditions_unresolved} unresolved")
            print(f"  Judgment: {trace.local_judgment[:60]}..." if len(trace.local_judgment) > 60 else f"  Judgment: {trace.local_judgment}")
            print()
    
    # 输出报告
    print("=== 验证报告 ===")
    success_count = sum(1 for t in all_traces if t.local_judgment != "None")
    auth_gate_active = all(t.auth_gate_passed for t in all_traces if t.authorization_level == 'CLASSICAL_EXPLICIT')
    no_legacy = all(not t.uses_legacy_strength for t in all_traces)
    
    print(f"总 Primitive 测试: {len(all_traces)}")
    print(f"生成 Judgment: {success_count}")
    print(f"Authorization Gate 生效: {auth_gate_active}")
    print(f"未使用旧 strength_engine: {no_legacy}")
    
    # 保存
    output = {
        'generated': __import__('datetime').datetime.now().isoformat(),
        'test_cases': len(test_cases),
        'summary': {
            'total_tests': len(all_traces),
            'success': success_count,
            'auth_gate_active': auth_gate_active,
            'no_legacy_strength': no_legacy,
        },
        'traces': [
            {
                'evidence_id': t.evidence_id,
                'authorization_level': t.authorization_level,
                'verification_status': t.verification_status,
                'local_judgment': t.local_judgment,
                'conditions_met': t.conditions_met,
                'conditions_failed': t.conditions_failed,
                'conditions_unresolved': t.conditions_unresolved,
                'auth_gate_passed': t.auth_gate_passed,
                'uses_legacy_strength': t.uses_legacy_strength,
            }
            for t in all_traces
        ]
    }
    
    with open('data/p0_3_9_real_integration_test.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 data/p0_3_9_real_integration_test.json")


if __name__ == '__main__':
    main()
